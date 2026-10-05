import re, collections, bisect, json
import pandas as pd
from load import *
c,p=load()
c['kind']='comment'; p['kind']='post'
p['post_id']=p.id; p['parent_id']=None
p['body']=p.title.fillna('')+'\n'+p.body.fillna('')
items=pd.concat([c[['id','kind','author','t','body','post_id','parent_id']],p[['id','kind','author','t','body','post_id','parent_id']]],ignore_index=True)
items['body']=items.body.fillna('').astype(str)
items=items.sort_values('t').reset_index(drop=True)
items['key']=items.kind.str[0]+items.id.astype(str)
items['url']=items.apply(lambda r:f"https://1f916.ai/api/{r.kind}/{r.id}",axis=1)
ack=re.compile(r"\b(adopt(?:ed|ing|s)?|using your|per your|as @[\w\-\.]+ (?:measured|computed|found|derived|reported|fitted|showed|posted)|second witness|replicat(?:ed|es|ing)|independently (?:confirm|reproduc|verif)\w*|confirm(?:s|ed|ing) (?:your|@[\w\-\.]+)|reproduc(?:ed|es|ing) (?:your|@)|taking (?:your|@[\w\-\.]+'s)|borrow(?:ed|ing) (?:your|@)|cross-?checked (?:against|with) (?:your|@)|your (?:number|figure|hash|measurement|count|fit|term)|picked up (?:your|from @))",re.I)
hexre=re.compile(r'\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,64}\b')
numre=re.compile(r'(?<![\w.])\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\w.,])\d+\.\d{2,}(?![\w.])|(?<![\w.,])\d{4,}(?![\w.:\-])')
tickre=re.compile(r'`([^`\n]{4,48})`')
bolre=re.compile(r'\*\*([^*\n]{4,40})\*\*')
cidre=re.compile(r'\bc(\d{3,6})\b')
def toks(t):
    s=set()
    for m in hexre.findall(t): s.add(('hash',m[:16]))
    for m in numre.findall(t): s.add(('num',m))
    for m in tickre.findall(t):
        m=m.strip()
        if len(m)>=4 and not re.fullmatch(r'[\d\W]+',m): s.add(('term',m.lower()))
    for m in bolre.findall(t): s.add(('term',m.strip().lower()))
    return s
items['toks']=items.body.map(toks)
idx=collections.defaultdict(list)
for i,r in enumerate(items.itertuples()):
    for tk in r.toks: idx[tk].append(i)
mentre=re.compile(r'@([\w\-\.]+)')
rows=[]
cid_to_idx={ (r.kind,r.id):i for i,r in enumerate(items.itertuples())}
for j,r in enumerate(items.itertuples()):
    if r.kind!='comment' and r.kind!='post': continue
    am=ack.search(r.body)
    if not am: continue
    tl=r.toks
    cands=[]
    for tk in tl:
        L=idx[tk]
        if len(L)>40 or len(L)<2: continue
        for i in L:
            if i>=j: break
            a=items.iloc[i]
            if a.author==r.author: continue
            dt=(r.t-a.t).total_seconds()/60
            if 0<dt<=7*24*60: cands.append((i,tk,dt,len(L)))
    if not cands: continue
    # prefer earliest source per token; then choose source mentioned or referenced
    best=collections.defaultdict(list)
    for i,tk,dt,n in cands: best[i].append((tk,dt,n))
    ms={m.lower() for m in mentre.findall(r.body)}
    cref={int(x) for x in cidre.findall(r.body)}
    sc=[]
    for i,l in best.items():
        a=items.iloc[i]
        s=len(l)+(3 if a.author.lower() in ms else 0)+(3 if (a.kind=='comment' and a.id in cref) else 0)
        sc.append((s,i,l))
    sc.sort(key=lambda x:(-x[0],x[1]))
    s,i,l=sc[0]
    a=items.iloc[i]
    ex=ack.search(r.body); ctx=r.body[max(0,ex.start()-80):ex.end()+120].replace('\n',' ')
    tk=sorted(l,key=lambda x:x[2])[0]
    direct = a.author.lower() in ms or (a.kind=='comment' and a.id in cref)
    rows.append(dict(adopter_item=r.key,adopter=r.author,adopter_url=r.url,adopter_time=r.t,source_item=a.key,source_author=a.author,source_url=a.url,source_time=a.t,
      delay_min=round((r.t-a.t).total_seconds()/60,1),shared_token_kind=tk[0][0],shared_token=tk[0][1],n_shared_tokens=len(l),token_item_freq=tk[2],
      same_post=int(r.post_id)==int(a.post_id),direct_reference=direct,ack_phrase=ex.group(0),context=ctx,score=s))
D=pd.DataFrame(rows).sort_values('score',ascending=False)
D.to_csv('t2_adoption_candidates_all.csv',index=False)
def cls(r):
    if r.direct_reference and r.same_post: return 'C1 message (direct reference, same thread)'
    if r.direct_reference: return 'C1 message (direct reference, other thread)'
    if r.same_post: return 'C3 shared channel (same thread, no direct reference)'
    return 'C4/C2 undecided (cross-thread reuse, no direct reference)'
D['class_auto']=D.apply(cls,axis=1)
D.to_csv('t2_adoption_candidates_all.csv',index=False)
print(len(D)); print(D.class_auto.value_counts())
# 7442 chain check
chain=[89554,90612,90673,90923,93648,93680]
cc=items[(items.kind=='comment')&items.id.isin(chain)][['id','author','t','url','body']]
cc.to_csv('t2_chain7442_items.csv',index=False)
print(cc.drop(columns='body').to_string())
