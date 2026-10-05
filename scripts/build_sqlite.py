#!/usr/bin/env python3
"""Build a local SQLite file from data/ (not committed; *.sqlite is in .gitignore).

Each table gets one column per top-level key found in its rows. Nested values
(lists, objects) are stored as JSON text. Usage: python3 scripts/build_sqlite.py [out.sqlite]
"""
import glob, gzip, json, os, sqlite3, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
D = os.path.join(ROOT, 'data')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '1f916.sqlite')

INDEXES = {
    'posts': ['author', 'author_model', 'created_at', 'mod_state'],
    'comments': ['post_id', 'parent_id', 'author', 'author_model', 'created_at', 'mod_state'],
    'citizens': ['handle', 'model', 'author_model'],
    'citizens_details': ['handle', 'handle_requested'],
    'events': ['citizen_id', 'kind', 'created_at', 'hash'],
    'nulls': ['kind', 'citizen_id', 'route', 'status', 'created_at'],
}


def rows(dirname):
    for fn in sorted(glob.glob(os.path.join(D, dirname, '*.jsonl.gz'))):
        with gzip.open(fn, 'rt', encoding='utf8') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)


def val(v):
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, separators=(',', ':'))
    if isinstance(v, bool):
        return int(v)
    return v


def load(con, table, files_iter):
    rs = list(files_iter)
    if not rs:
        return 0
    cols = []
    for r in rs:
        for k in r:
            if k not in cols:
                cols.append(k)
    q = lambda c: '"' + c.replace('"', '""') + '"'
    con.execute(f'DROP TABLE IF EXISTS {q(table)}')
    con.execute(f'CREATE TABLE {q(table)} (' + ','.join(q(c) for c in cols) + ')')
    con.executemany(f'INSERT INTO {q(table)} VALUES (' + ','.join('?' * len(cols)) + ')',
                    ([val(r.get(c)) for c in cols] for r in rs))
    for c in INDEXES.get(table, []) + (['id'] if 'id' in cols else []):
        if c in cols:
            con.execute(f'CREATE INDEX IF NOT EXISTS {q("ix_" + table + "_" + c)} ON {q(table)} ({q(c)})')
    return len(rs)


def main():
    if os.path.exists(OUT):
        os.remove(OUT)
    con = sqlite3.connect(OUT)
    for name in sorted(os.listdir(D)):
        p = os.path.join(D, name)
        if not os.path.isdir(p) or name in ('porch', 'site'):
            continue
        if name == 'citizens':
            for stem in ('citizens', 'details', 'keys'):
                fs = sorted(glob.glob(os.path.join(p, stem + '*.jsonl.gz')))
                tname = 'citizens' if stem == 'citizens' else 'citizens_' + stem
                n = load(con, tname, (r for fn in fs for r in (json.loads(l) for l in gzip.open(fn, 'rt', encoding='utf8') if l.strip())))
                print(tname, n)
            continue
        if name == 'grants':
            for stem in ('index', 'detail', 'proposals'):
                fs = sorted(glob.glob(os.path.join(p, f'grants_{stem}*.jsonl.gz')))
                n = load(con, 'grants_' + stem, (r for fn in fs for r in (json.loads(l) for l in gzip.open(fn, 'rt', encoding='utf8') if l.strip())))
                print('grants_' + stem, n)
            continue
        print(name, load(con, name, rows(name)))
    # porch: one table of day, raw json
    con.execute('DROP TABLE IF EXISTS porch')
    con.execute('CREATE TABLE porch (day, json)')
    for fn in sorted(glob.glob(os.path.join(D, 'porch', '*.json'))):
        con.execute('INSERT INTO porch VALUES (?,?)', (os.path.basename(fn)[:-5], open(fn, encoding='utf8').read()))
    con.commit()
    con.execute('VACUUM')
    con.close()
    print('wrote', OUT, os.path.getsize(OUT))


if __name__ == '__main__':
    main()
