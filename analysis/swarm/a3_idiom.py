import re, json, collections
import pandas as pd, numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from load import *
c,p=load()
c['kind']='comment'; p['kind']='post'; p['body']=p.title.fillna('')+'\n'+p.body.fillna('')
items=pd.concat([c[['id','kind','author','t','body']],p[['id','kind','author','t','body']]],ignore_index=True)
items['body']=items.body.fillna('').astype(str).str.lower()
items=items.sort_values('t').reset_index(drop=True)
items['url']=items.apply(lambda r:f"https://1f916.ai/api/{r.kind}/{r.id}",axis=1)
items['day']=items.t.dt.strftime('%Y-%m-%d')
cm=json.load(open('t1_communities.json'))
items['comm']=items.author.map(cm)
terms=["false green","second witness","cheap check","falsifier","receipt","stillness","witness","seam","tell","specimen","falsif","counterfactual","denominator","provenance","handoff","ground truth","tombstone","attest","heartbeat","quota","load-bearing","negative space","residue","ledger","audit"]
def spread(term):
    rx=re.compile(r'\b'+re.escape(term).replace(r'\ ',r'[\s\-]+'),re.I)
    m=items[items.body.map(lambda s:bool(rx.search(s)))]
    return m
rows=[];curves={}
for t in terms:
    m=spread(t)
    if len(m)==0: continue
    first=m.iloc[0]
    fa=m.groupby('author').t.min().sort_values()
    ad=fa.iloc[1:]
    cl_first=first.comm
    cross=int((m.groupby('author').comm.first().dropna()!=cl_first).sum()) if pd.notna(cl_first) else None
    rows.append(dict(term=t,items=len(m),authors=m.author.nunique(),first_author=first.author,first_item=f"{first.kind[0]}{first.id}",first_url=first.url,first_time=first.t,
       second_author=(fa.index[1] if len(fa)>1 else ''),authors_within_7d_of_first=int((fa<=fa.iloc[0]+pd.Timedelta(days=7)).sum()),authors_within_30d=int((fa<=fa.iloc[0]+pd.Timedelta(days=30)).sum()),
       first_author_community=cl_first,communities_among_authors=m.comm.nunique(),authors_outside_first_community=cross))
    curves[t]=m.groupby('day').author.agg(['size','nunique']).to_dict('index')
pd.DataFrame(rows).sort_values('authors').to_csv('t3_idiom_listed_terms.csv',index=False)
json.dump({k:{d:v for d,v in c_.items()} for k,c_ in curves.items()},open('t3_idiom_spread_per_day.json','w'))
# discovery
cv=CountVectorizer(ngram_range=(2,3),min_df=8,max_df=1500,binary=True,token_pattern=r"[a-z][a-z\-_']{2,}")
X=cv.fit_transform(items.body); vocab=np.array(cv.get_feature_names_out())
au=pd.factorize(items.author)[0]; tm=items.t.values
res=[]
Xc=X.tocsc()
for j in range(X.shape[1]):
    rows_=Xc.indices[Xc.indptr[j]:Xc.indptr[j+1]]
    rows_=np.sort(rows_)
    a=au[rows_]
    na=len(set(a))
    if na<6: continue
    # authors per item concentration: top author share
    cnt=collections.Counter(a); top=cnt.most_common(1)[0][1]/len(rows_)
    if top>0.4: continue
    first=rows_[0]
    # fraction of items in first 10% of the term's lifetime from first author
    res.append((vocab[j],len(rows_),na,round(top,2),first,rows_[min(2,len(rows_)-1)]))
R=pd.DataFrame(res,columns=['term','items','authors','top_author_share','first_idx','third_idx'])
R['first_author']=items.author.values[R.first_idx]; R['first_item']=[f"{items.kind[i][0]}{items.id[i]}" for i in R.first_idx]
R['first_url']=items.url.values[R.first_idx]; R['first_time']=items.t.values[R.first_idx]
R['authors_per_item']=R.authors/R['items']
# prefer terms born mid-corpus (not common phrases): first appear after day 3 and authors>=8
R=R[R.first_time>pd.Timestamp('2026-08-08T00:00:00')]
R=R.sort_values(['authors','items'],ascending=False)
R.drop(columns=['first_idx','third_idx']).head(300).to_csv('t3_idiom_discovered.csv',index=False)
print(pd.DataFrame(rows).to_string()); print(R.head(60).to_string())
