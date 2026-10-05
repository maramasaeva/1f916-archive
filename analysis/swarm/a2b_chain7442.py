import re, pandas as pd
from load import *
c,p=load()
c['kind']='comment'; p['kind']='post'; p['body']=p.title.fillna('')+'\n'+p.body.fillna(''); p['parent_id']=None; p['post_id']=p.id
it=pd.concat([c[['id','kind','author','t','body','parent_id','post_id']],p[['id','kind','author','t','body','parent_id','post_id']]],ignore_index=True).sort_values('t').reset_index(drop=True)
it['body']=it.body.fillna('').astype(str)
chain=[89554,90612,90673,90923,93648,93680]
tok=re.compile(r'\b[0-9a-f]{8,64}\b|\b\d{5,}\b|\b\d+\.\d+/h\b')
rows=[]
for cid in chain:
    r=it[(it.kind=='comment')&(it.id==cid)].iloc[0]
    ts=set()
    for m in tok.findall(r.body):
        if re.fullmatch(r'[0-9a-f]{8,64}',m) and not re.search(r'\d',m) : continue
        ts.add(m[:16] if len(m)>=16 else m)
    for m in sorted(ts):
        e=it[(it.t<r.t)&it.body.str.contains(m,regex=False)]
        if len(e)==0: first=None
        else: first=e.iloc[0]
        rows.append(dict(item=f"c{cid}",author=r.author,time=r.t,token=m,earlier_items=len(e),first_source=(f"{first.kind[0]}{first.id}" if first is not None else ''),first_author=(first.author if first is not None else ''),first_time=(first.t if first is not None else ''),
          delay_min=(round((r.t-first.t).total_seconds()/60,1) if first is not None else ''),first_url=(f"https://1f916.ai/api/{first.kind}/{first.id}" if first is not None else ''),
          first_other_author=(lambda e2:(f"{e2.iloc[0].kind[0]}{e2.iloc[0].id} {e2.iloc[0].author}" if len(e2) else ''))(e[e.author!=r.author]) if first is not None else ''))
R=pd.DataFrame(rows); R.to_csv('t2_chain7442_token_trace.csv',index=False)
pd.set_option('display.width',250); print(R.to_string())
# explicit c-references inside chain items
for cid in chain:
    b=it[(it.kind=='comment')&(it.id==cid)].body.iloc[0]
    print(cid, sorted(set(re.findall(r'\bc(\d{4,6})\b',b))), sorted(set(re.findall(r'#(\d{3,5})\b',b))), sorted(set(re.findall(r'@([\w\-]+)',b))))
