"""Apply a rules module to all posts and comments. Usage: python apply_rules.py [rules_module] [out_stem]
Uses multiprocessing (fork). Output: <stem>.csv.gz without body text."""
import sys, importlib, time
import numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, '.')
from load import load_messages, HERE, _read

modname = sys.argv[1] if len(sys.argv) > 1 else 'rules'
stem = sys.argv[2] if len(sys.argv) > 2 else 'types_all'
mod = importlib.import_module(modname)

M = load_messages()
C = _read('comments/*.jsonl.gz')[['id', 'amends']]
amends = dict(zip(C.id, C.amends))
auth = {('post', i): a for i, a in zip(M[M.kind == 'post'].id, M[M.kind == 'post'].author)}
auth.update({('comment', i): a for i, a in zip(M[M.kind == 'comment'].id, M[M.kind == 'comment'].author)})
rows = [dict(id=int(a), kind=b, author=c, t=(d.strftime('%Y-%m-%dT%H:%M:%SZ') if pd.notna(d) else None), text=e, post_id=f, parent_id=g) for a, b, c, d, e, f, g in zip(M.id, M.kind, M.author, M.t, M.text, M.post_id, M.parent_id)]


def work(r):
    from types import SimpleNamespace as NS
    r = NS(**r)
    ctx = {}
    pa = None
    if r.kind == 'comment':
        pid = r.parent_id
        pa = auth.get(('comment', int(pid))) if pd.notna(pid) else (auth.get(('post', int(r.post_id))) if pd.notna(r.post_id) else None)
        pa = pa if isinstance(pa, str) else None
        ctx['parent_author'] = pa
        ctx['reply_to_self'] = (pa == r.author)
        ctx['addressed'] = bool(pa) and pa != r.author and (pa.lower() in (r.text or '').lower()[:400])
        am = amends.get(r.id)
        if isinstance(am, list) and am:
            ctx['amends_self'] = any(auth.get(('comment', int(a))) == r.author for a in am)
    if r.t is None and not (r.text or '').strip():
        return {'id': r.id, 'kind': r.kind, 'handle': r.author, 'date_utc': None, 'length': 0, 'primary': 'no_content', 'secondary': '', 'rule_hits': 'no_content:empty_row_without_timestamp', 'parent_author': pa, 'has_hash': False, 'has_table': False, 'has_code': False, 'n_mentions': 0, 'n_q': 0}
    res = mod.classify(r.text, r.kind, ctx)
    f = res['features']
    return {'id': r.id, 'kind': r.kind, 'handle': r.author, 'date_utc': r.t,
            'length': f['len'], 'primary': res['primary'], 'score': round(res['scores'][res['primary']],2), 'secondary': ';'.join(res['secondary']),
            'rule_hits': ';'.join(res['hits']), 'parent_author': pa,
            'has_hash': f['hash'], 'has_table': f['table'], 'has_code': f['code'], 'n_mentions': f['mentions'],
            'n_q': f['q']}


if __name__ == '__main__':
    t0 = time.time()
    with Pool(8) as p:
        recs = p.map(work, rows, chunksize=500)
    D = pd.DataFrame(recs)
    D.to_csv(f'{HERE}/{stem}.csv.gz', index=False, compression='gzip')
    print('seconds', time.time() - t0)
    print(D.primary.value_counts())
    print(D.groupby(['kind', 'primary']).size().unstack(0))
