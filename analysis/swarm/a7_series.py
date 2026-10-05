import re, pandas as pd, collections
from load import *
c,p=load()
p['url']=p.id.map(lambda i:f"https://1f916.ai/api/post/{i}")
def skel(t):
    t=str(t).lower()
    t=re.sub(r'\d{4}-\d{2}-\d{2}','D',t); t=re.sub(r'\d+(?:[.,]\d+)*','N',t)
    t=re.sub(r'\b(mon|tue|wed|thu|fri|sat|sun)[a-z]*\b','W',t)
    t=re.sub(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b','M',t)
    return re.sub(r'\s+',' ',t).strip()
p['skel']=p.title.map(skel)
p['prefix3']=p.title.map(lambda t:' '.join(skel(t).split()[:3]))
out=[]
for key,col in (('full','skel'),('prefix3','prefix3')):
    for s,g in p.groupby(col):
        if len(g)<4 or len(s)<4 or s in ('N','n'): continue
        if col=='prefix3' and len(s.split())<2: continue
        a=g.author.value_counts()
        out.append(dict(match=key,skeleton=s,posts=len(g),authors=len(a),top_author=a.index[0],top_author_posts=int(a.iloc[0]),authors_list='; '.join(f"{k}:{v}" for k,v in a.head(12).items()),
          first=g.t.min(),last=g.t.max(),series_type=('one author' if len(a)==1 else ('one author dominant (>=80%)' if a.iloc[0]/len(g)>=.8 else 'multi-author')),
          post_ids=' '.join(map(str,sorted(g.id)[:25])),example_url=g.sort_values('id').url.iloc[0],example_title=g.title.iloc[0]))
O=pd.DataFrame(out).sort_values(['match','posts'],ascending=[True,False])
O.to_csv('t7_series_candidates.csv',index=False)
print(O[O.match=='full'].head(50)[['skeleton','posts','authors','series_type','top_author']].to_string())
print(O[(O.match=='prefix3')&(O.series_type=='multi-author')].head(40)[['skeleton','posts','authors','top_author']].to_string())
