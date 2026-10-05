import json, pandas as pd, os
W=os.path.expanduser('~/1f916-archive/.work/')
def jl(f):
    rows=[]
    p=W+f
    if not os.path.exists(p): return pd.DataFrame()
    for l in open(p):
        try: rows.append(json.loads(l))
        except: pass
    return pd.DataFrame(rows)
def load():
    c=jl('comments_changes.jsonl'); p=jl('posts_changes.jsonl')
    for d in (c,p):
        d['id']=d['id'].astype(int); d['t']=pd.to_datetime(d['created_at'].astype(float),unit='ms',utc=True)
    c=c.sort_values('id').drop_duplicates('id',keep='last'); p=p.sort_values('id').drop_duplicates('id',keep='last')
    return c,p
