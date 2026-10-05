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
cm=json.load(open('t1_communities.json')); items['comm']=items.author.map(cm)
cv=CountVectorizer(ngram_range=(1,2),min_df=8,max_df=900,binary=True,token_pattern=r"[a-z][a-z\-_]{3,}")
X=cv.fit_transform(items.body).tocsc(); vocab=np.array(cv.get_feature_names_out())
au=pd.factorize(items.author)[0]; tm=items.t.values
hl={h.lower() for h in set(items.author)}
hp=set()
for h in hl: hp|={x for x in re.split(r'[-_.\s]+',h) if len(x)>3}
cut=np.datetime64('2026-08-20T00:00:00')
res=[]
for j in range(X.shape[1]):
    r=np.sort(X.indices[X.indptr[j]:X.indptr[j+1]])
    if tm[r[0]]<cut: continue
    if any((w in hl or w in hp) for w in vocab[j].split()): continue
    a=au[r]; first_t=tm[r[0]]
    w=r[tm[r]<=first_t+np.timedelta64(14,'D')]
    na14=len(set(au[w])); na=len(set(a))
    if na14<8: continue
    top=collections.Counter(a).most_common(1)[0][1]/len(r)
    if top>0.35 or items.author.values[r[0]]=='jerrymuse66': continue
    fa=items.author.values[r[0]]
    comms=items.comm.values[w]
    fc=items.comm.values[r[0]]
    same=np.mean([x==fc for x in comms if pd.notna(x)]) if pd.notna(fc) else np.nan
    res.append(dict(term=vocab[j],items=len(r),authors=na,authors_14d=na14,top_author_share=round(top,2),first_author=fa,first_item=f"{items.kind[r[0]][0]}{items.id[r[0]]}",first_url=items.url[r[0]],first_time=pd.Timestamp(first_t),second_author=items.author.values[r[1]],share_14d_items_same_community_as_first=round(same,2) if same==same else ''))
R=pd.DataFrame(res).sort_values('authors_14d',ascending=False)
R.head(200).to_csv('t3_idiom_new_terms_after_aug20.csv',index=False)
print(R.head(60).drop(columns='first_url').to_string())
