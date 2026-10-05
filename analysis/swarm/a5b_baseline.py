import json, itertools, re, numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from load import *
c,p=load(); c['kind']='comment'; p['kind']='post'; p['body']=p.title.fillna('')+'\n'+p.body.fillna('')
it=pd.concat([c[['id','kind','author','author_model','t','body']],p[['id','kind','author','author_model','t','body']]],ignore_index=True)
it['body']=it.body.fillna('').astype(str)
cnt=it.author.value_counts(); act=cnt[cnt>=120].index.tolist()
core=json.load(open('t1_core_handles.json'))
hs=sorted(set(act)|set(core))
sub=it[it.author.isin(hs)]
docs={h:'\n'.join(g.body)[:300000] for h,g in sub.groupby('author')}
hs=list(docs)
tf=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=3,sublinear_tf=True,max_features=300000)
X=tf.fit_transform([docs[h] for h in hs]); S=(X@X.T).toarray()
mod=sub.groupby('author').author_model.agg(lambda s:s.value_counts().index[0]).to_dict()
fam=lambda m:('claude' if 'claude' in str(m).lower() else 'other')
ts={h:np.sort(g.t.values.astype('datetime64[s]').astype(np.int64)) for h,g in sub.groupby('author')}
rows=[]
for i,j in itertools.combinations(range(len(hs)),2):
    a,b=hs[i],hs[j]
    rows.append(dict(a=a,b=b,cos=S[i,j],both_core=(a in core and b in core),one_core=((a in core)!=(b in core)),model_a=mod[a],model_b=mod[b],same_label=mod[a]==mod[b],both_claude=fam(mod[a])=='claude' and fam(mod[b])=='claude'))
R=pd.DataFrame(rows)
R.to_csv('t5_pair_char_cos_all_active.csv',index=False)
for name,m in [('core-core',R.both_core),('core-other',R.one_core),('neither core',~R.both_core&~R.one_core),('both claude-labeled, neither core',R.both_claude&~R.both_core&~R.one_core),('both claude-labeled, both core',R.both_claude&R.both_core),('same exact label, neither core',R.same_label&~R.both_core&~R.one_core)]:
    x=R[m].cos; print(name,len(x),'median',round(x.median(),3),'p90',round(x.quantile(.9),3),'p99',round(x.quantile(.99),3),'max',round(x.max(),3))
print(R.sort_values('cos',ascending=False).head(30).to_string())
# egress-like template group
g=['egress','gnomon','holdfast','tardis-relay','no-quote-no-claim','no-scheduler','porch-light-keeper','scholium','plumbline','cairn-lineage']
sg=R[R.a.isin(g)&R.b.isin(g)]; print('template group pairs median',sg.cos.median(),len(sg))
print(R[(R.a=='egress')|(R.b=='egress')].sort_values('cos',ascending=False).head(15).to_string())
