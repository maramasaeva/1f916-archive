#!/usr/bin/env python3
"""Check the packed data/ tree against the site's own totals and hash chain.

Writes VALIDATION.md and prints a summary. Mismatches are reported, never hidden.
Usage: python3 scripts/validate.py
"""
import glob, gzip, hashlib, json, os, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
D = os.path.join(ROOT, 'data')
W = os.path.join(ROOT, '.work')


def rows(table):
    for fn in sorted(glob.glob(os.path.join(D, table, '*.jsonl.gz'))):
        with gzip.open(fn, 'rt', encoding='utf8') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)


def js_stringify(v):
    return json.dumps(v, ensure_ascii=False, separators=(',', ':'))


def chain_hash(prev, e, detail_variant):
    detail = e.get('detail')
    if detail_variant == 'as_served':
        d = detail
    elif detail_variant == 'string_to_json':
        d = detail
    payload = js_stringify([e.get('citizen_id'), e.get('kind'), d, e.get('created_at')])
    return hashlib.sha256(((prev or '') + '\n' + payload).encode('utf8')).hexdigest()


def main():
    out, problems = [], []
    man = json.load(open(os.path.join(ROOT, 'manifest.json')))
    counts = man['row_counts']
    out.append(f"Validated {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} against manifest packed at {man['packed_at']}.\n")

    # 1. counts vs /api/stats snapshot(s)
    out.append('## Counts versus /api/stats\n')
    out.append('| table | stats total | rows in data/ | difference | stats snapshot |')
    out.append('|---|---|---|---|---|')
    for fn in sorted(glob.glob(os.path.join(W, 'files', 'site', 'api__stats*.json'))):
        s = json.load(open(fn)).get('society') or {}
        snap = os.path.basename(fn)
        for key, table in (('citizens', 'citizens'), ('posts', 'posts'), ('comments', 'comments')):
            if key in s:
                have = counts.get(table, 0)
                diff = have - s[key]
                out.append(f'| {table} | {s[key]} | {have} | {diff:+d} | {snap} |')
                if diff:
                    problems.append(f'{table}: stats says {s[key]}, data has {have} ({diff:+d}); a positive difference can come from the site growing during the crawl, a negative one means rows are missing or the crawl is unfinished.')
        st = json.load(open(fn))
    nul = [r['id'] for r in rows('nulls')]
    out.append(f"| nulls | not in /api/stats | {len(nul)} | max id {max(nul) if nul else 0} | changes feed |")
    out.append('')

    # 2. detail coverage
    out.append('## Coverage of the slower phases\n')
    out.append(f"- posts with per-post detail (tags): {counts.get('_posts_with_detail', 0)} of {counts.get('posts', 0)}")
    out.append(f"- comments with vote/flag/depth stats: {counts.get('_comments_with_stats', 0)} of {counts.get('comments', 0)}")
    out.append(f"- citizen detail records: {counts.get('citizens_details', 0)} of {counts.get('citizens', 0)}")
    out.append('')

    # 3. referential checks
    post_ids = {p['id'] for p in rows('posts')}
    orphan = missing_parent = 0
    cids = set()
    for c in rows('comments'):
        cids.add(c['id'])
    for c in rows('comments'):
        if c.get('post_id') not in post_ids:
            orphan += 1
        if c.get('parent_id') is not None and c['parent_id'] not in cids:
            missing_parent += 1
    out.append('## Referential checks\n')
    out.append(f'- comments whose post_id is not in posts: {orphan}')
    out.append(f'- comments whose parent_id is not in comments: {missing_parent}')
    out.append('')
    if orphan or missing_parent:
        problems.append(f'referential: {orphan} orphan comments, {missing_parent} missing parents')

    out.append('## Id gaps\n')
    for t in ('posts', 'comments', 'events', 'nulls'):
        ids = sorted(r['id'] for r in rows(t))
        gaps = (ids[-1] - ids[0] + 1 - len(ids)) if ids else 0
        out.append(f'- {t}: {len(ids)} rows, ids {ids[0] if ids else None} to {ids[-1] if ids else None}, {gaps} ids inside that range absent')
    out.append('')

    # 4. identity-log hash chain
    out.append('## Identity-log hash chain\n')
    ev = sorted(rows('events'), key=lambda e: e.get('id', 0))
    out.append(f'- events read: {len(ev)}')
    if ev:
        out.append(f'- fields on first event: {", ".join(sorted(ev[0].keys()))}')
    bad_hash, bad_link_global, bad_link_cit, nohash, ok = [], 0, 0, 0, 0
    last_by_cit = {}
    prev_global = None
    prev_global_set = False
    for e in ev:
        h = e.get('hash')
        if not h:
            nohash += 1
            continue
        # prev_hash as stored; if absent fall back to the previous event in the same stream
        prev = e.get('prev_hash')
        calc = chain_hash(prev, e, 'as_served')
        if calc == h:
            ok += 1
        else:
            bad_hash.append(e.get('id'))
        if prev_global_set and prev != prev_global:
            bad_link_global += 1
        cid = e.get('citizen_id')
        if cid in last_by_cit and prev != last_by_cit[cid]:
            bad_link_cit += 1
        prev_global, prev_global_set = h, True
        last_by_cit[cid] = h
    out.append(f'- events with a hash field: {len(ev) - nohash}; without: {nohash}')
    out.append(f'- recomputed hash equals served hash: {ok}')
    out.append(f'- recomputed hash differs from served hash: {len(bad_hash)}')
    if bad_hash:
        out.append(f'- first mismatching event ids: {bad_hash[:50]}')
    out.append(f'- prev_hash differs from previous event hash in id order (single global chain): {bad_link_global}')
    out.append(f'- prev_hash differs from previous event hash of the same citizen (informational; the chain is one global chain, so this is expected to be non-zero): {bad_link_cit}')
    unhashed = [e['id'] for e in ev if not e.get('hash')]
    if unhashed:
        out.append(f'- event ids without hash: {unhashed[:50]}')
    out.append('- formula used: sha256(prev_hash + "\\n" + JSON.stringify([citizen_id, kind, detail, created_at])), JSON serialised compactly with non-ASCII kept as is. Differences can come from serialisation details (number formatting, escaping) as well as from changed data; each mismatch is listed by id, none is dropped.')
    out.append('')
    if bad_hash:
        problems.append(f'events: {len(bad_hash)} hash mismatches')
    if nohash and ev:
        problems.append(f'events: {nohash} served without hash (ids listed above); they cannot be chain-checked')

    # 5. file integrity
    out.append('## File integrity\n')
    bad = 0
    for rel, meta in man['files'].items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            bad += 1
            continue
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        if h != meta['sha256']:
            bad += 1
    out.append(f'- files in manifest whose sha256 no longer matches or are missing: {bad} of {len(man["files"])}')
    if bad:
        problems.append(f'{bad} files differ from manifest (run pack.py again)')
    out.append('')
    out.append('## Summary\n')
    out.extend(f'- {p}' for p in problems) if problems else out.append('- no problems found')
    txt = '# Validation\n\n' + '\n'.join(out) + '\n'
    open(os.path.join(ROOT, 'VALIDATION.md'), 'w').write(txt)
    print(txt)


if __name__ == '__main__':
    main()
