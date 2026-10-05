import re, json, collections, itertools
import pandas as pd, networkx as nx
from load import *
c,p=load()
c['kind']='comment'; p['kind']='post'
for d in (c,p): d['url']=d.apply(lambda r:f"https://1f916.ai/api/{r.kind}/{r.id}",axis=1)
pa=dict(zip(p.id,p.author)); ca=dict(zip(c.id,c.author))
handles={h.lower():h for h in set(c.author)|set(p.author) if isinstance(h,str)}
men=re.compile(r'@([A-Za-z0-9][A-Za-z0-9_\-\.]*[A-Za-z0-9]|[A-Za-z0-9])')
def mentions(t):
    out=set()
    for m in men.findall(t if isinstance(t,str) else ''):
        m=m.rstrip('.-_')
        if m.lower() in handles: out.add(handles[m.lower()])
    return out
edges=[]  # (src,dst,type,item kind,id)
for r in c.itertuples():
    pid=int(r.parent_id) if r.parent_id not in (None,'None') and str(r.parent_id)!='nan' else None
    if pid and pid in ca: edges.append((r.author,ca[pid],'reply',r.id))
    elif int(r.post_id) in pa: edges.append((r.author,pa[int(r.post_id)],'reply_post',r.id))
    for m in mentions(r.body): edges.append((r.author,m,'mention',r.id))
for r in p.itertuples():
    for m in mentions(r.body): edges.append((r.author,m,'mention_post',r.id))
E=pd.DataFrame(edges,columns=['src','dst','type','item_id']); E=E[E.src!=E.dst]
E.to_csv('t1_edges.csv',index=False)
E['pair']=E.apply(lambda r:' <-> '.join(sorted([r.src,r.dst])),axis=1)
pc=E.groupby('pair').agg(total=('item_id','count'),replies=('type',lambda s:s.isin(['reply','reply_post']).sum()),mentions=('type',lambda s:s.str.startswith('mention').sum())).sort_values('total',ascending=False)
dirc=E.groupby(['pair','src']).size().unstack(fill_value=0)
top=pc.head(30).reset_index()
top['directions']=top.pair.map(lambda k:json.dumps({a:int(b) for a,b in dirc.loc[k].items() if b}))
ex=E.sort_values('item_id').groupby('pair').item_id.apply(lambda s:' '.join(map(str,s.head(3))))
top['example_item_ids(comment/post id)']=top.pair.map(ex)
top['example_url']=top['example_item_ids(comment/post id)'].map(lambda s:f"https://1f916.ai/api/comment/{s.split()[0]}")
top.to_csv('t1_top30_pairs.csv',index=False)
# community structure
G=nx.Graph()
for k,v in pc.total.items():
    a,b=k.split(' <-> '); G.add_edge(a,b,weight=int(v))
comms=nx.community.greedy_modularity_communities(G,weight='weight')
cm={}
for i,cc in enumerate(comms):
    for h in cc: cm[h]=i
json.dump(cm,open('t1_communities.json','w'))
# 7442 cluster
topic=re.compile(r'/api/attest|verified_head|verified_through|identity_expect|sealed_entries|legacy_prefix|witnessed_against|expect_matches|identity chain|treasury chain|identity_log',re.I)
th=c[c.post_id.astype(int)==7442]
cluster=set(th.author)|{pa[7442]}
cl_mentions=set()
for b in th.body: cl_mentions|=mentions(b)
cl_mentions|=mentions(p[p.id==7442].body.iloc[0])
allitems=pd.concat([c[['id','kind','author','t','body','post_id','url']],p.assign(post_id=p.id)[['id','kind','author','t','body','post_id','url']]])
allitems['topic']=allitems.body.fillna('').map(lambda s:len(topic.findall(s)))
tp=allitems[(allitems.topic>0)&(allitems.t>=pd.Timestamp('2026-09-01',tz='UTC'))]
rows=[]
for h,g in tp.groupby('author'):
    rows.append(dict(handle=h,topic_items=len(g),topic_mentions=int(g.topic.sum()),first=g.t.min(),last=g.t.max(),in_7442_thread=h in cluster,mentioned_in_7442_thread=h in cl_mentions,first_item_url=g.sort_values('t').url.iloc[0],community=cm.get(h)))
hc=pd.DataFrame(rows).sort_values('topic_items',ascending=False)
hc.to_csv('t1_attest_topic_handles.csv',index=False)
th_rows=th[['id','author','author_model','t','parent_id','url']]; th_rows.to_csv('t1_post7442_thread.csv',index=False)
print(top.head(30).to_string()); print(len(hc),hc.head(40).to_string()); print(sorted(cluster)); print(sorted(cl_mentions))

strict=hc[(hc.topic_items>=5)].handle.tolist()
user_list=['egress','claude-code-cli','Bishop','momus','Aura','soft-power','Tabby','no-scheduler','porch','gnomon','head-of-experiments']
user_list=[h for h in user_list if h in set(c.author)|set(p.author)]
cl=sorted(set(strict)|cluster|cl_mentions|set(user_list))
json.dump(cl,open('t1_cluster_handles.json','w'))
hc['in_cluster_list']=hc.handle.isin(cl)
hc.to_csv('t1_attest_topic_handles.csv',index=False)
print(len(cl),cl)
sub=allitems[allitems.topic>0]
print(sub.groupby(sub.t.dt.strftime('%Y-%m-%d')).size().to_string())
