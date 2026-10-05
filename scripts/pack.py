#!/usr/bin/env python3
"""Turn .work/ (raw crawl output, not committed) into the committed data/ tree.

Rows are kept exactly as served by the site. Duplicates are removed by id (the last
copy read wins). Files are gzip-compressed JSON Lines with a fixed gzip mtime, so the
same input always gives the same bytes and the same sha256.

Usage: python3 scripts/pack.py
"""
import gzip, hashlib, json, os, re, shutil, sys, datetime, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
W = os.path.join(ROOT, '.work')
D = os.path.join(ROOT, 'data')
MAX_RAW = 100 * 1024 * 1024      # raw bytes per shard before it is split further
ROWS_PER_PART = 5000             # for tables without numeric ids

WARN = []
COUNTS = {}
BADLINES = {}


def read_jsonl(stream):
    fn = os.path.join(W, stream + '.jsonl')
    if not os.path.exists(fn):
        return []
    out, bad = [], 0
    with open(fn, encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                bad += 1
    if bad:
        BADLINES[stream] = bad
    return out


def dedupe(rows, keyfn):
    seen = {}
    order = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        k = keyfn(r)
        if k is None:
            k = ('__row__', json.dumps(r, sort_keys=True, ensure_ascii=False))
        if k not in seen:
            order.append(k)
        seen[k] = r
    return [seen[k] for k in order]


def dump(r):
    return (json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf8')


def write_gz(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0, compresslevel=9) as g:
            for l in lines:
                g.write(l)


def clear(dirname):
    p = os.path.join(D, dirname)
    if os.path.isdir(p):
        shutil.rmtree(p)


def pack_table(name, rows, keyfn=lambda r: r.get('id'), width=None, sortkey=None):
    """Write rows to data/<name>/. Numeric-id tables are sharded by id range (width)."""
    rows = dedupe(rows, keyfn)
    if sortkey is None:
        sortkey = lambda r: (0, keyfn(r)) if isinstance(keyfn(r), int) else (1, str(keyfn(r)))
    try:
        rows.sort(key=sortkey)
    except TypeError:
        pass
    clear(name)
    COUNTS[name] = len(rows)
    if not rows:
        return
    out = os.path.join(D, name)
    if width and all(isinstance(keyfn(r), int) for r in rows):
        groups = {}
        for r in rows:
            groups.setdefault(keyfn(r) // width, []).append(r)
        for g, grp in sorted(groups.items()):
            parts, cur, size = [], [], 0
            for r in grp:
                b = dump(r)
                if size + len(b) > MAX_RAW and cur:
                    parts.append(cur); cur, size = [], 0
                cur.append(b); size += len(b)
            parts.append(cur)
            for i, p in enumerate(parts):
                lo = g * width
                hi = lo + width - 1
                suffix = '' if len(parts) == 1 else f'-p{i + 1}'
                write_gz(os.path.join(out, f'{name}-{lo:06d}-{hi:06d}{suffix}.jsonl.gz'), p)
    else:
        if len(rows) <= ROWS_PER_PART:
            write_gz(os.path.join(out, f'{name}.jsonl.gz'), [dump(r) for r in rows])
        else:
            for i in range(0, len(rows), ROWS_PER_PART):
                write_gz(os.path.join(out, f'{name}-part{i // ROWS_PER_PART + 1:03d}.jsonl.gz'),
                         [dump(r) for r in rows[i:i + ROWS_PER_PART]])


def by_id(r):
    return r.get('id')


# ------------------------------------------------------------------ tables
def pack_posts():
    base = dedupe(read_jsonl('posts_changes'), by_id)
    det = {}
    for d in read_jsonl('post_detail'):
        p = d.get('post') or {}
        if p.get('id') is not None:
            det[p['id']] = d
    merged = []
    seen = set()
    for r in base:
        r = dict(r)
        d = det.get(r['id'])
        if d:
            for k, v in d['post'].items():
                if k in r and r[k] != v:
                    WARN.append(f"post {r['id']} field {k} differs between changes feed and detail; detail kept")
                r[k] = v
            for k in ('tags', 'tags_truncated', 'comments_total', 'comments_distinct_authors'):
                if k in d:
                    r[k] = d[k]
            seen.add(r['id'])
        merged.append(r)
    for pid, d in det.items():
        if pid not in seen and pid not in {x['id'] for x in base}:
            r = dict(d['post'])
            for k in ('tags', 'tags_truncated', 'comments_total', 'comments_distinct_authors'):
                if k in d:
                    r[k] = d[k]
            merged.append(r)
    COUNTS['_posts_with_detail'] = len(det)
    pack_table('posts', merged, by_id, width=1000)


def pack_comments():
    base = dedupe(read_jsonl('comments_changes'), by_id)
    stats = {s['id']: s for s in dedupe(read_jsonl('comment_stats'), by_id)}
    ids = {r['id'] for r in base}
    out = []
    for r in base:
        r = dict(r)
        s = stats.get(r['id'])
        if s:
            for k, v in s.items():
                if k == 'id':
                    continue
                if k not in r:
                    r[k] = v
                elif v is not None and r[k] != v:
                    # keep the changes-feed copy for text fields; stats only refines counters/state
                    if k in ('mod_state', 'amends', 'amended_by', 'votes', 'flags', 'depth', 'parent_id', 'intended_parent_id', 'post_id'):
                        r[k] = v
        out.append(r)
    extra = [s for i, s in stats.items() if i not in ids]
    COUNTS['_comments_with_stats'] = len(stats)
    COUNTS['_comments_only_in_stats'] = len(extra)
    out.extend(extra)
    pack_table('comments', out, by_id, width=5000)


def pack_citizens():
    lst = dedupe(read_jsonl('citizens'), lambda r: r.get('handle') or r.get('id'))
    det = dedupe(read_jsonl('citizen_details'), lambda r: r.get('handle_requested'))
    clear('citizens')
    os.makedirs(os.path.join(D, 'citizens'), exist_ok=True)

    def part(name, rows):
        COUNTS['citizens' if name == 'citizens' else 'citizens_' + name] = len(rows)
        for i in range(0, max(len(rows), 1), ROWS_PER_PART):
            chunk = rows[i:i + ROWS_PER_PART]
            if not chunk:
                break
            suf = '' if len(rows) <= ROWS_PER_PART else f'-part{i // ROWS_PER_PART + 1:03d}'
            write_gz(os.path.join(D, 'citizens', f'{name}{suf}.jsonl.gz'), [dump(r) for r in chunk])

    lst.sort(key=lambda r: (str(r.get('citizen_id', r.get('id', ''))).zfill(12), str(r.get('handle'))))
    part('citizens', lst)
    dets, keys = [], []
    for d in det:
        d = dict(d)
        k = d.pop('keys', None)
        dets.append(d)
        if k is not None:
            keys.append({'handle_requested': d.get('handle_requested'), 'keys': k})
    dets.sort(key=lambda r: str(r.get('handle_requested')))
    keys.sort(key=lambda r: str(r.get('handle_requested')))
    if dets:
        part('details', dets)
    if keys:
        part('keys', keys)


def pack_simple(name, stream, keyfn=by_id, width=None):
    pack_table(name, read_jsonl(stream), keyfn, width=width)


def pack_lists():
    pack_simple('listings', 'listings')
    for suffix in ('listings', 'offers', 'mandates'):
        rows = read_jsonl(suffix + '_detail')
        if rows:
            pack_table(suffix + '_detail', rows, lambda r: (r.get('id') or (r.get('listing') or r.get('offer') or r.get('mandate') or {}).get('id')))
    pack_simple('offers', 'offers')
    pack_simple('mandates', 'mandates')
    pack_simple('attestations', 'attestations')
    pack_simple('payouts', 'payouts', keyfn=lambda r: r.get('id') or r.get('handle') or r.get('citizen_id'))
    pack_simple('anchors', 'anchors')
    pack_simple('flags', 'flags', keyfn=lambda r: (r.get('target_type'), r.get('target_id')))
    pack_simple('tags', 'tags', keyfn=lambda r: r.get('id') or r.get('tag') or r.get('name'))
    pack_simple('payload_notices', 'payload_notices')
    for s in ('grants_index', 'grants_detail', 'grants_proposals'):
        rows = read_jsonl(s)
        if rows:
            pack_table(s, rows, lambda r: None)
    # keep data/grants/ as the single grants folder
    g = os.path.join(D, 'grants')
    clear('grants')
    os.makedirs(g, exist_ok=True)
    for s in ('grants_index', 'grants_detail', 'grants_proposals'):
        src = os.path.join(D, s)
        if os.path.isdir(src):
            for f in os.listdir(src):
                shutil.move(os.path.join(src, f), os.path.join(g, f.replace(s, s.replace('grants_', ''), 1) if False else f))
            shutil.rmtree(src)
            COUNTS['grants/' + s] = COUNTS.pop(s)


def pack_porch():
    clear('porch')
    n = 0
    for f in sorted(glob.glob(os.path.join(W, 'files', 'porch', '*.json'))):
        dst = os.path.join(D, 'porch', os.path.basename(f))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(f, dst)
        n += 1
    COUNTS['porch_days'] = n


SITE_ITEMS = ['/', '/about', '/terms', '/privacy', '/humans.txt', '/llms.txt', '/openapi.json', '/apis.json',
              '/security.txt', '/robots.txt', '/support', '/treasury', '/human/economy', '/human/roadmap',
              '/human/setup', '/grants', '/porch', '/skills/index.json', '/skills/1f916/SKILL.md',
              '/api/surface', '/api/stats', '/api/official', '/api/checkpoint', '/api/witnesses',
              '/api/docket', '/api/rail', '/api/grants', '/api/front', '/api/provenance', '/api/pulse',
              '/api/listings/guide', '/api/listings/security', '/api/offers/guide', '/api/mandates/budgets',
              '/api/screen-notices', '/api/moderation-state', '/api/attest', '/api/attest/legacy-manifest']


def site_name(p):
    name = (p.strip('/') or 'front-door').replace('/', '__')
    return re.sub(r'\.[a-z]{2,4}$', '', name)


def pack_site():
    clear('site')
    src = os.path.join(W, 'files', 'site')
    if not os.path.isdir(src):
        return
    state = {}
    try:
        state = json.load(open(os.path.join(W, 'state.json')))
    except Exception:
        pass
    name2ep = {site_name(p): p for p in SITE_ITEMS}
    index = []
    for f in sorted(os.listdir(src)):
        stem = os.path.splitext(f)[0]
        base = re.sub(r'__\d.*$', '', stem)
        os.makedirs(os.path.join(D, 'site'), exist_ok=True)
        shutil.copyfile(os.path.join(src, f), os.path.join(D, 'site', f))
        b = open(os.path.join(src, f), 'rb').read()
        index.append({'file': f, 'endpoint': name2ep.get(stem) or name2ep.get(base),
                      'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
                      'fetched_at': datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(src, f)), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
    json.dump({'static_phase_started': state.get('static_at'), 'files': index},
              open(os.path.join(D, 'site', '_index.json'), 'w'), indent=1)
    COUNTS['site_files'] = len(index)


ENDPOINTS = ['/api/changes (posts, comments, nulls, cursor paged)', '/api/citizens?since=0', '/api/events?since=0',
             '/api/listings?include_expired=1', '/api/listings/{id}', '/api/payouts', '/api/mandates', '/api/mandates/{id}',
             '/api/attestations', '/api/anchors', '/api/offers?include_closed=1', '/api/offers/{id}', '/api/flags',
             '/api/tags', '/api/payload-notices', '/api/grants', '/api/grants/{slug}', '/api/grants/{slug}/proposals/{id}',
             '/api/porch?day=YYYY-MM-DD', '/api/citizen/{handle}', '/api/keys/{handle}', '/api/post/{id}'] + SITE_ITEMS


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def main():
    os.makedirs(D, exist_ok=True)
    pack_posts()
    pack_comments()
    pack_simple('nulls', 'nulls', width=50000)
    pack_citizens()
    pack_simple('events', 'events', width=5000)
    pack_lists()
    pack_porch()
    pack_site()

    files = {}
    for dp, _, fs in os.walk(D):
        for f in sorted(fs):
            p = os.path.join(dp, f)
            files[os.path.relpath(p, ROOT)] = {'bytes': os.path.getsize(p), 'sha256': sha(p)}
    state = {}
    try:
        state = json.load(open(os.path.join(W, 'state.json')))
    except Exception:
        pass
    mt = [os.path.getmtime(p) for p in glob.glob(os.path.join(W, '*.jsonl'))]
    iso = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    first_site = [os.path.getmtime(p) for p in glob.glob(os.path.join(W, 'files', 'site', '*'))]
    man = {
        'origin': 'https://1f916.ai',
        'packed_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'crawl_started_at': iso(min(first_site)) if first_site else None,
        'crawl_last_write_at': iso(max(mt)) if mt else None,
        'crawl_state': {k: v for k, v in state.items() if k in ('static_at', 'changes', 'nulls_total', 'incomplete')},
        'phases_done': {'postfull_next_id': (state.get('postfull') or {}).get('next'),
                        'citizen_details_done': len(state.get('citizen_done') or [])},
        'row_counts': COUNTS,
        'unparsable_lines_skipped': BADLINES,
        'capped_by_origin': {
            'flags': 'endpoint lists 200 of 1037 flagged targets; the rest are in events kind=flag-disposition',
            'tags': 'endpoint lists 1000 spellings alphabetically with no cursor (site reports about 3230); per-post tags come from the postfull phase',
            'payload_notices': 'endpoint returns at most 200 rows (limit=2000 was tried and still returned 200) of about 1672, no older cursor'},
        'warnings': WARN[:200],
        'warnings_total': len(WARN),
        'endpoints': ENDPOINTS,
        'files': files,
        'total_bytes': sum(v['bytes'] for v in files.values()),
    }
    json.dump(man, open(os.path.join(ROOT, 'manifest.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({'row_counts': COUNTS, 'files': len(files), 'total_bytes': man['total_bytes'],
                      'warnings': len(WARN), 'bad_lines': BADLINES}, indent=1))


if __name__ == '__main__':
    main()
