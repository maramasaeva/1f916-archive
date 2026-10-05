import re, json, pandas as pd
from load import *
c,p=load(); c['kind']='comment'; p['kind']='post'; p['body']=p.title.fillna('')+'\n'+p.body.fillna('')
it=pd.concat([c[['id','kind','author','t','body']],p[['id','kind','author','t','body']]],ignore_index=True)
it['body']=it.body.fillna('').astype(str); it=it.sort_values('t').reset_index(drop=True)
it['url']=it.apply(lambda r:f"https://1f916.ai/api/{r.kind}/{r.id}",axis=1)
core=set(json.load(open('t1_core_handles.json'))); cm=json.load(open('t1_communities.json'))
it['wk']=it.t.dt.to_period('W-SUN').dt.start_time.dt.strftime('%m-%d')
terms=['false green','second witness','cheap check','falsifier','receipt','stillness','witness','seam','specimen','negative control','unreceipted','claim-cut','anti-alarm','amended_by','witnesses an act','single specimen wearing','dead if','falsifier:','tell']
rows=[];first=[]
for t in terms:
    rx=re.compile(r'(?<![\w])'+re.escape(t).replace(r'\ ',r'[\s\-]+')+(r'' if t.endswith(':') else r'(?![\w])'),re.I)
    m=it[it.body.map(lambda s:bool(rx.search(s)))]
    if not len(m): continue
    w=m.groupby('wk').agg(items=('id','count'),authors=('author','nunique'))
    for k,v in w.iterrows(): rows.append(dict(term=t,week_start=k,items=v['items'],authors=v['authors']))
    fa=m.drop_duplicates('author').head(8)
    first.append(dict(term=t,total_items=len(m),total_authors=m.author.nunique(),core_authors_using=len(set(m.author)&core),
        first_8_authors=' > '.join(f"{r.author}({r.kind[0]}{r.id} {r.t:%m-%d %H:%M})" for r in fa.itertuples()),first_url=fa.url.iloc[0],
        communities_of_first_20_authors=len({cm.get(a) for a in m.drop_duplicates('author').head(20).author if a in cm}) ))
pd.DataFrame(rows).to_csv('t3_idiom_weekly.csv',index=False); F=pd.DataFrame(first); F.to_csv('t3_idiom_first_adopters.csv',index=False)
pd.set_option('display.width',300); pd.set_option('display.max_colwidth',400)
print(F.drop(columns='first_url').to_string())
print(pd.DataFrame(rows).pivot(index='week_start',columns='term',values='items').fillna(0).astype(int).to_string())
