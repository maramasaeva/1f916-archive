import re, json, itertools, collections, os
import pandas as pd, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from load import *
c,p=load()
c['kind']='comment'; p['kind']='post'; p['body']=p.title.fillna('')+'\n'+p.body.fillna('')
it=pd.concat([c[['id','kind','author','author_model','t','body']],p[['id','kind','author','author_model','t','body']]],ignore_index=True)
it['body']=it.body.fillna('').astype(str)
cluster=json.load(open('t1_core_handles.json'))
sub=it[it.author.isin(cluster)].copy()
emo=re.compile('[\U0001F300-\U0001FAFF☀-➿]')
def feat(g):
    txt='\n'.join(g.body); n=len(txt)+1
    sents=[s for s in re.split(r'(?<=[.!?])\s+|\n+',re.sub(r'```.*?```','',txt,flags=re.S)) if len(s.split())>1]
    return dict(items=len(g),chars_per_item=round(n/len(g)),avg_sentence_words=round(np.mean([len(s.split()) for s in sents]),1) if sents else 0,
      semicolons_per_1k=round(1000*txt.count(';')/n,2),hashes_per_item=round(len(re.findall(r'\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{8,64}\b',txt))/len(g),2),
      code_blocks_per_item=round(txt.count('```')/2/len(g),2),emoji_per_item=round(len(emo.findall(txt))/len(g),2),headers_per_item=round(len(re.findall(r'^#{1,4} ',txt,flags=re.M))/len(g),2),
      bold_per_item=round(txt.count('**')/2/len(g),2),backticks_per_1k=round(1000*txt.count('`')/n,2),emdash_per_1k=round(1000*(txt.count('—')+txt.count('–'))/n,2),
      commaperiod=round(1000*txt.count(',')/n,2),parens_per_1k=round(1000*txt.count('(')/n,2),first_person_I_per_1k=round(1000*len(re.findall(r'\bI\b',txt))/n,2),
      models='; '.join(f"{k}:{v}" for k,v in g.author_model.value_counts().items()),first=g.t.min(),last=g.t.max())
F=pd.DataFrame({h:feat(g) for h,g in sub.groupby('author')}).T
F.to_csv('t5_style_features.csv')
# hour profiles and pair timing
sub['h']=sub.t.dt.hour; sub['min']=sub.t.dt.minute
H=sub.groupby(['author','h']).size().unstack(fill_value=0)
Hn=H.div(H.sum(1),axis=0)
M=sub.groupby(['author','min']).size().unstack(fill_value=0)
def cos(a,b): return float(a@b/np.linalg.norm(a)/np.linalg.norm(b))
tf=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2,sublinear_tf=True,max_features=200000)
docs={h:'\n'.join(g.body)[:300000] for h,g in sub.groupby('author')}
Xt=tf.fit_transform(list(docs.values())); hs=list(docs)
S=(Xt@Xt.T).toarray()
wt=TfidfVectorizer(ngram_range=(2,3),min_df=2,sublinear_tf=True,max_features=200000)
Xw=wt.fit_transform(list(docs.values())); SW=(Xw@Xw.T).toarray()
ts={h:np.sort(g.t.values.astype('datetime64[s]').astype(np.int64)) for h,g in sub.groupby('author')}
rows=[]
for i,j in itertools.combinations(range(len(hs)),2):
    a,b=hs[i],hs[j]
    ta,tb=ts[a],ts[b]
    # items of b within 120 s of any a item
    k=np.searchsorted(ta,tb); d=np.minimum(np.abs(tb-ta[np.clip(k,0,len(ta)-1)]),np.abs(tb-ta[np.clip(k-1,0,len(ta)-1)]))
    near=int((d<=120).sum()); near600=int((d<=600).sum())
    rows.append(dict(a=a,b=b,items_a=len(ta),items_b=len(tb),char_ngram_cos=round(S[i,j],3),word_ngram_cos=round(SW[i,j],3),hour_profile_cos=round(cos(Hn.loc[a].values,Hn.loc[b].values),3),
       minute_profile_cos=round(cos(M.loc[a].values.astype(float),M.loc[b].values.astype(float)),3),b_within_120s_of_a=near,b_within_600s_of_a=near600,share_b_within_120s=round(near/len(tb),3)))
P=pd.DataFrame(rows).sort_values('char_ngram_cos',ascending=False)
P.to_csv('t5_pair_similarity.csv',index=False)
# distinctive phrases per handle
vec=TfidfVectorizer(ngram_range=(2,3),min_df=3,sublinear_tf=True); 
allh={h:'\n'.join(g.body)[:300000] for h,g in it.groupby('author') if len(g)>=5}
V=vec.fit_transform(list(allh.values())); ha=list(allh); fn=np.array(vec.get_feature_names_out())
ph={}
for h in cluster:
    if h in allh:
        r=V[ha.index(h)].toarray()[0]; ph[h]=list(fn[np.argsort(-r)[:12]])
json.dump(ph,open('t5_characteristic_phrases.json','w'),indent=1)
print(F.to_string()); print(P.head(25).to_string())
