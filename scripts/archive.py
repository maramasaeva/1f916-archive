#!/usr/bin/env python3
"""Polite, resumable crawler for the public records served by https://1f916.ai.

Everything it fetches is published by that origin without a key. The site asks for
no more than 10 requests per 10 seconds per IP, so this script keeps to ~1/s.

Usage:  python3 scripts/archive.py PHASE [PHASE ...]
Phases: static changes citizens events lists porch details postfull
State and raw pages live in .work/ (not committed). Run `scripts/pack.py` to
turn .work/ into the committed data/ tree.
"""
import json, os, sys, time, re, datetime, urllib.request, urllib.error, urllib.parse

BASE = 'https://1f916.ai'
UA = 'murmuration-archive/1.0 (public-record research; <=1 request/s)'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
W = os.path.join(ROOT, '.work')
os.makedirs(W, exist_ok=True)
MIN_GAP = 1.15
_last = [0.0]
STATE_F = os.path.join(W, 'state.json')
STATE = json.load(open(STATE_F)) if os.path.exists(STATE_F) else {}


def save_state():
    tmp = STATE_F + '.tmp'
    json.dump(STATE, open(tmp, 'w'))
    os.replace(tmp, STATE_F)


def log(*a):
    print(datetime.datetime.utcnow().strftime('%H:%M:%S'), *a, flush=True)


def get(path, raw=False, accept='application/json'):
    for attempt in range(14):
        wait = MIN_GAP - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            req = urllib.request.Request(BASE + path, headers={'User-Agent': UA, 'Accept': accept})
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
                ctype = r.headers.get('Content-Type', '')
            if raw:
                return body, ctype
            return json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ra = e.headers.get('Retry-After')
                time.sleep(float(ra) if ra and ra.replace('.', '', 1).isdigit() else 15)
                continue
            if e.code >= 500:
                time.sleep(10 * (attempt + 1))
                continue
            body = e.read()[:300].decode('utf8', 'replace')
            return ({'_http': e.code, '_body': body}, '') if raw else {'_http': e.code, '_body': body}
        except Exception as e:  # network hiccup
            time.sleep(5 * (attempt + 1))
    raise RuntimeError('giving up on ' + path)


def append(stream, rows):
    with open(os.path.join(W, stream + '.jsonl'), 'a') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n')


def write(relpath, data: bytes):
    p = os.path.join(W, 'files', relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(data)


# ---------------------------------------------------------------- phases
def phase_static():
    items = ['/', '/about', '/terms', '/privacy', '/humans.txt', '/llms.txt', '/openapi.json', '/apis.json',
             '/security.txt', '/robots.txt', '/support', '/treasury', '/human/economy', '/human/roadmap',
             '/human/setup', '/grants', '/porch', '/skills/index.json', '/skills/1f916/SKILL.md',
             '/api/surface', '/api/stats', '/api/official', '/api/checkpoint', '/api/witnesses',
             '/api/docket', '/api/rail', '/api/grants', '/api/front', '/api/provenance', '/api/pulse',
             '/api/listings/guide', '/api/listings/security', '/api/offers/guide', '/api/mandates/budgets',
             '/api/screen-notices', '/api/moderation-state', '/api/attest', '/api/attest/legacy-manifest']
    stamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    for p in items:
        body, ct = get(p, raw=True, accept='*/*' if not p.startswith('/api') else 'application/json')
        if isinstance(body, dict):
            log('skip', p, body)
            continue
        ext = 'json' if 'json' in ct else ('png' if 'png' in ct else ('svg' if 'svg' in ct else 'txt'))
        name = (p.strip('/') or 'front-door').replace('/', '__')
        if re.search(r'\.[a-z]{2,4}$', name):
            name = re.sub(r'\.[a-z]{2,4}$', '', name)
        write(f'site/{name}.{ext}', body)
        log('static', p, len(body))
    STATE['static_at'] = stamp
    save_state()


def phase_changes():
    cur = STATE.get('changes', {'posts': 0, 'comments': 0, 'nulls': 0})
    pages = 0
    while True:
        d = get(f"/api/changes?posts_since={cur['posts']}&comments_since={cur['comments']}&nulls_since={cur['nulls']}")
        if '_http' in d:
            raise RuntimeError(f'changes: {d}')
        np_, nc, nn = d.get('posts') or [], d.get('comments') or [], d.get('nulls') or []
        append('posts_changes', np_)
        append('comments_changes', nc)
        append('nulls', nn)
        for key, k2 in (('posts', 'next_posts_since'), ('comments', 'next_comments_since'), ('nulls', 'next_nulls_since')):
            v = d.get(k2)
            if v is not None:
                cur[key] = v
        STATE['changes'] = cur
        STATE['nulls_total'] = d.get('nulls_total')
        save_state()
        pages += 1
        if pages % 20 == 0:
            log('changes page', pages, 'rows', len(np_), len(nc), len(nn), 'cursors', cur)
        if not d.get('has_more'):
            break
        if not (np_ or nc or nn):
            break
    log('changes done', pages, 'pages', cur)


def paged_list(stream, path, rows_key, extra='', cap_pages=100000):
    """Generic: follow next_<param> keys while has_more. The cursor replaces a same-named fixed param."""
    st = STATE.setdefault('lists', {})
    s = st.get(stream, {'qs': '', 'done': False})
    if s.get('done'):
        return
    base, _, fixed_qs = path.partition('?')
    fixed = dict(urllib.parse.parse_qsl(fixed_qs))
    fixed.update(dict(urllib.parse.parse_qsl(extra)))
    cursor = dict(urllib.parse.parse_qsl(s['qs'])) if s.get('qs') else {}
    n = 0
    while True:
        params = {**fixed, **cursor}
        url = base + (('?' + urllib.parse.urlencode(params)) if params else '')
        d = get(url)
        if '_http' in d:
            log('error', stream, d)
            break
        rows = d.get(rows_key) or []
        append(stream, rows)
        nxt = [(k, d[k]) for k in d if k.startswith('next_') and d[k] not in (None, '', 0) and not isinstance(d[k], (list, dict))]
        n += 1
        if d.get('has_more') and nxt:
            k, v = nxt[0]
            cursor = {k[5:]: str(v)}
            s['qs'] = urllib.parse.urlencode(cursor)
            st[stream] = s
            save_state()
            if n % 10 == 0:
                log(stream, 'page', n)
        else:
            if d.get('has_more') and not nxt:
                log('WARNING', stream, 'has_more but no next_ key; keys=', [k for k in d if not isinstance(d[k], (list, dict))][:12])
                STATE.setdefault('incomplete', []).append(stream)
            s['done'] = True
            st[stream] = s
            save_state()
            break
        if n > cap_pages:
            break
    log(stream, 'done', n, 'pages')


def phase_citizens():
    paged_list('citizens', '/api/citizens?since=0', 'citizens')


def phase_events():
    paged_list('events', '/api/events?since=0', 'events')


def phase_lists():
    paged_list('listings', '/api/listings?include_expired=1', 'listings')
    paged_list('payouts', '/api/payouts', 'bindings')
    paged_list('mandates', '/api/mandates', 'mandates')
    paged_list('attestations', '/api/attestations', 'attestations')
    paged_list('anchors', '/api/anchors', 'anchors')
    paged_list('offers', '/api/offers?include_closed=1', 'offers')
    paged_list('flags', '/api/flags', 'queue')
    paged_list('tags', '/api/tags', 'tags')
    paged_list('payload_notices', '/api/payload-notices?limit=200', 'notices')
    # detail pages for small registries
    for stream, route, key in (('listings', '/api/listings/', 'id'), ('offers', '/api/offers/', 'offer_id'), ('mandates', '/api/mandates/', 'id')):
        done = STATE.setdefault('detail_done', {}).setdefault(stream, [])
        ids = []
        fn = os.path.join(W, stream + '.jsonl')
        if os.path.exists(fn):
            for line in open(fn):
                try:
                    ids.append(json.loads(line).get(key))
                except Exception:
                    pass
        for i in sorted({x for x in ids if x is not None}):
            if i in done:
                continue
            d = get(f'{route}{i}')
            append(stream + '_detail', [d])
            done.append(i)
            save_state()
        log(stream, 'detail done', len(done))
    # grants and proposals
    g = get('/api/grants')
    append('grants_index', [g])
    for gr in g.get('grants') or []:
        slug = gr.get('slug')
        if not slug or slug in STATE.setdefault('grants_done', []):
            continue
        d = get(f'/api/grants/{slug}')
        append('grants_detail', [d])
        for p in (d.get('proposals') or []):
            pid = p.get('id')
            if pid is not None:
                append('grants_proposals', [get(f'/api/grants/{slug}/proposals/{pid}')])
        STATE['grants_done'].append(slug)
        save_state()


def phase_porch():
    start = datetime.date(2026, 8, 5)
    end = datetime.datetime.utcnow().date()
    done = STATE.setdefault('porch_done', [])
    day = start
    while day <= end:
        ds = day.isoformat()
        if ds not in done or day == end:
            d = get(f'/api/porch?day={ds}')
            if '_http' not in d:
                write(f'porch/{ds}.json', json.dumps(d, ensure_ascii=False, indent=0).encode())
            if day != end and ds not in done:
                done.append(ds)
                save_state()
        day += datetime.timedelta(days=1)
    log('porch done')


def phase_details():
    cits = []
    fn = os.path.join(W, 'citizens.jsonl')
    for line in open(fn):
        cits.append(json.loads(line)['handle'])
    done = set(STATE.setdefault('citizen_done', []))
    n = 0
    for h in cits:
        if h in done:
            continue
        d = get('/api/citizen/' + urllib.parse.quote(h, safe=''))
        slim = {k: v for k, v in d.items() if k not in ('posts', 'comments', 'model_provenance', 'untrusted_content', 'now', 'now_utc')}
        slim['handle_requested'] = h
        k = get('/api/keys/' + urllib.parse.quote(h, safe=''))
        slim['keys'] = {kk: vv for kk, vv in k.items() if kk not in ('now', 'now_utc', 'model_provenance', 'untrusted_content')}
        append('citizen_details', [slim])
        STATE['citizen_done'].append(h)
        n += 1
        if n % 25 == 0:
            save_state()
            log('citizen details', len(STATE['citizen_done']), '/', len(cits))
    save_state()
    log('citizen details done')


def phase_postfull():
    top = 0
    for line in open(os.path.join(W, 'posts_changes.jsonl')):
        top = max(top, json.loads(line)['id'])
    st = STATE.setdefault('postfull', {'next': 1})
    i = st['next']
    n = 0
    while i <= top + 5:
        d = get(f'/api/post/{i}')
        if '_http' not in d and d.get('post'):
            post = d['post']
            tags = d.get('tags') or []
            comments = d.get('comments') or []
            nxt = d.get('next_since')
            guard = 0
            while d.get('has_more') and nxt and guard < 20:
                d = get(f'/api/post/{i}?since={nxt}')
                if '_http' in d:
                    break
                comments += d.get('comments') or []
                nxt = d.get('next_since')
                guard += 1
            append('post_detail', [{'post': post, 'tags': tags, 'tags_truncated': d.get('tags_truncated'), 'comments_total': d.get('comments_total'), 'comments_distinct_authors': d.get('comments_distinct_authors')}])
            append('comment_stats', [{k: c.get(k) for k in ('id', 'post_id', 'parent_id', 'intended_parent_id', 'depth', 'mod_state', 'votes', 'flags', 'amends', 'amended_by')} for c in comments])
        st['next'] = i + 1
        i += 1
        n += 1
        if n % 50 == 0:
            save_state()
            log('postfull', i, '/', top)
    save_state()
    log('postfull done')


PHASES = {'static': phase_static, 'changes': phase_changes, 'citizens': phase_citizens, 'events': phase_events,
          'lists': phase_lists, 'porch': phase_porch, 'details': phase_details, 'postfull': phase_postfull}

if __name__ == '__main__':
    for name in sys.argv[1:]:
        log('== phase', name)
        PHASES[name]()
    log('all requested phases finished')
