import re, json, os
import pandas as pd
from load import *
c,p=load()
c['kind']='comment'; p['kind']='post'; p['body']=p.title.fillna('')+'\n'+p.body.fillna('')
it=pd.concat([c[['id','kind','author','author_model','t','body']],p[['id','kind','author','author_model','t','body']]],ignore_index=True)
it['url']=it.apply(lambda r:f"https://1f916.ai/api/{r.kind}/{r.id}",axis=1)
act=it.author.value_counts(); act=act[act>=15].index
g=it[it.author.isin(act)].groupby('author')
rows=[]
for h,d in g:
    vc=d.author_model.fillna('(none)').value_counts()
    d=d.sort_values('t')
    seq=d.author_model.fillna('(none)').tolist()
    ch=[(i) for i in range(1,len(seq)) if seq[i]!=seq[i-1]]
    rows.append(dict(handle=h,items=len(d),models='; '.join(f"{k}:{v}" for k,v in vc.items()),n_models=len(vc),n_label_changes=len(ch),first_change_url=(d.url.iloc[ch[0]] if ch else ''),first_change=(f"{seq[ch[0]-1]} -> {seq[ch[0]]} at {d.t.iloc[ch[0]]}" if ch else '')))
Mo=pd.DataFrame(rows).sort_values('items',ascending=False); Mo.to_csv('t6_models_census.csv',index=False)
# self-description mismatch
rx=re.compile(r"\b(?:i am|i'm|running on|running as|my model is|model:)\s+(?:running on\s+)?`?((?:claude|gpt|gemini|grok|llama|qwen|deepseek|mistral|kimi|glm|hermes|opus|sonnet|haiku|fable)[\w\.\-]*)",re.I)
mm=[]
for r in it.itertuples():
    for m in rx.findall(r.body[:1500]):
        mm.append(dict(handle=r.author,url=r.url,declared_label=r.author_model,said_in_text=m))
MM=pd.DataFrame(mm)
if len(MM):
    MM['consistent']=MM.apply(lambda r:str(r.said_in_text).lower().strip('.-') in str(r.declared_label).lower() or str(r.declared_label).lower() in str(r.said_in_text).lower(),axis=1)
    MM[~MM.consistent].to_csv('t6_label_vs_text_mismatch.csv',index=False)
    print(len(MM),(~MM.consistent).sum())
# events
ev=W+'events.jsonl'
if os.path.exists(ev):
    E=jl('events.jsonl'); E.to_csv('t6_events_all_head.csv',index=False)
    if 'kind' in E: 
        mc=E[E.kind=='model_correction']; mc.to_csv('t6_model_corrections.csv',index=False); print(len(mc)); print(mc.head().to_string())
print(Mo.head(40).to_string())
print(it.author_model.value_counts().head(30))
# citizens registry model vs most recent item label
cz=jl('citizens.jsonl')[['handle','model','karma','created_at']].rename(columns={'model':'registry_model'})
last=it.sort_values('t').groupby('author').agg(last_label=('author_model','last'),first_label=('author_model','first'),n=('id','count')).reset_index().rename(columns={'author':'handle'})
Z=cz.merge(last,on='handle',how='left')
Z['registry_vs_last_label_differs']=Z.registry_model.fillna('')!=Z.last_label.fillna('')
Z[(Z.n>=15)].sort_values('n',ascending=False).to_csv('t6_registry_vs_item_labels.csv',index=False)
print(Z[(Z.n>=15)].registry_vs_last_label_differs.mean(), Z[(Z.n>=15)&Z.registry_vs_last_label_differs].head(20).to_string())
if os.path.exists(W+'events.jsonl'):
    E2=jl('events.jsonl'); mc=E2[E2.kind=='model_correction']; mc.to_csv('t6_model_corrections.csv',index=False)
    pd.set_option('display.max_colwidth',200); print(mc[['id','citizen','detail','created_at']].to_string())
