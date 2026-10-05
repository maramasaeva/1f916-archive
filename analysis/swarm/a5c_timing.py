import json, itertools, numpy as np, pandas as pd
from load import *
c,p=load(); c['kind']='comment'; p['kind']='post'; p['post_id']=p.id; p['parent_id']=None
core=json.load(open('t1_core_handles.json'))
it=pd.concat([c[['id','kind','author','t','post_id','parent_id','body']],p[['id','kind','author','t','post_id','parent_id','body']]],ignore_index=True)
it['body']=it.body.fillna('').astype(str)
s=it[it.author.isin(core)].sort_values('t').reset_index(drop=True)
s['ts']=(s.t-pd.Timestamp('1970-01-01',tz='UTC')).dt.total_seconds().astype('int64')
rows=[]
a_idx=s.groupby('author').indices
cid_author=dict(zip(c.id,c.author))
for a,b in itertools.combinations(core,2):
    A=s.iloc[a_idx[a]] if a in a_idx else None; B=s.iloc[a_idx[b]] if b in a_idx else None
    if A is None or B is None: continue
    ta=A.ts.values; n=0; unl=0; ex=[]
    for r in B.itertuples():
        k=np.searchsorted(ta,r.ts)
        for kk in (k-1,k):
            if 0<=kk<len(ta) and abs(ta[kk]-r.ts)<=120:
                ra=A.iloc[kk]; n+=1
                linked = (r.parent_id is not None and str(r.parent_id)!='nan' and cid_author.get(int(r.parent_id))==a) or (ra.parent_id is not None and str(ra.parent_id)!='nan' and cid_author.get(int(ra.parent_id))==b) or (f'@{a}' in r.body) or (f'@{b}' in ra.body) or int(ra.post_id)==int(r.post_id)
                if not linked:
                    unl+=1
                    if len(ex)<3: ex.append(f"{ra.kind[0]}{ra.id}/{r.kind[0]}{r.id}")
                break
    rows.append(dict(a=a,b=b,items_a=len(A),items_b=len(B),pairs_within_120s=n,unlinked_pairs_within_120s=unl,unlinked_share_of_smaller=round(unl/min(len(A),len(B)),4),examples=' '.join(ex)))
R=pd.DataFrame(rows).sort_values('unlinked_pairs_within_120s',ascending=False); R.to_csv('t5_pair_timing_unlinked.csv',index=False)
print(R.head(20).to_string())
