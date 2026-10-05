import re, numpy as np, pandas as pd, json
from loadporch import *
from load import *
P=porch(); P['url']="https://1f916.ai/api/porch?day="+P.day.astype(str)
P['line_ref']=P.id.map(lambda i:f"porch:{i}")
rows=[]
for h,g in P.groupby('author'):
    if len(g)<20: continue
    g=g.sort_values('t'); d=g.t.diff().dt.total_seconds().dropna()/60
    mb=np.bincount(g.t.dt.minute,minlength=60); hb=np.bincount(g.t.dt.hour,minlength=24)
    # gaps within same day
    rows.append(dict(handle=h,lines=len(g),first=g.t.min(),last=g.t.max(),days=g.day.nunique(),gap_min_median=round(d.median(),1),gap_p25=round(d.quantile(.25),1),gap_p75=round(d.quantile(.75),1),
      share_gaps_within_55_65=round(((d>=55)&(d<=65)).mean(),3),share_gaps_within_115_125=round(((d>=115)&(d<=125)).mean(),3),share_gaps_within_175_185=round(((d>=175)&(d<=185)).mean(),3),
      top3_minute_share=round(np.sort(mb)[::-1][:3].sum()/len(g),3),modal_minute=int(mb.argmax()),hours_with_lines=int((hb>0).sum()),peak_hour=int(hb.argmax()),
      example_line_ids=' '.join(map(str,g.id.head(3)))))
R=pd.DataFrame(rows).sort_values('lines',ascending=False); R.to_csv('t4_porch_rhythm_by_handle.csv',index=False)
pd.set_option('display.width',250); print(R.head(20).to_string())
# quotas
qre=re.compile(r'quotas?[:\s]+(?:remaining[:\s]+)?(\d+)\s*posts?[,;]?\s*(\d+)\s*comments?(?:[,;]?\s*(\d+)\s*votes?)?',re.I)
qs=[]
for r in P.itertuples():
    m=qre.search(r.body)
    if m: qs.append(dict(line_id=r.id,author=r.author,time=r.t,posts_remaining=int(m.group(1)),comments_remaining=int(m.group(2)),votes_remaining=(int(m.group(3)) if m.group(3) else None),text=r.body[-160:].replace('\n',' '),url=r.url))
Q=pd.DataFrame(qs); Q.to_csv('t4_porch_quota_lines.csv',index=False); print(len(Q)); print(Q.author.value_counts().head()); print(Q.head(8).to_string())
other=P[P.body.str.contains(r'quota|remaining|budget|exhausted',case=False)&~P.id.isin(Q.line_id if len(Q) else [])]
other[['id','author','t','body','url']].to_csv('t4_porch_other_quota_mentions.csv',index=False); print(len(other),other.author.value_counts().head(8))
# momus heartbeat
m=P[(P.author=='momus')&P.body.str.startswith('cheap check')].copy()
m['gap_claim']=m.body.str.extract(r'close-gap ([\d\.]+) min')[0].astype(float)
m['total_rows']=m.body.str.extract(r'identity_log\.total_rows=(\d+)')[0].astype(float)
m['stamp']=m.body.str.extract(r'@(\d\d:\d\d:\d\d)Z')[0]
m['gap_real']=m.t.diff().dt.total_seconds()/60
m['reads']=m.body.str.extract(r'threads_joined=(\d+)')[0]
m[['id','t','gap_real','gap_claim','total_rows','stamp','url']].to_csv('t4_momus_heartbeat.csv',index=False)
print(len(m)); print(m.gap_real.describe()); print(m.gap_real.round(0).value_counts().head(12))
print(m.groupby(m.t.dt.hour).size().to_dict()); print(m.t.dt.minute.value_counts().head(8).to_dict())
# Bishop 'knock' lines
b=P[(P.author=='Bishop')].copy(); b['gap']=b.t.diff().dt.total_seconds()/60
b[['id','t','gap','body','url']].to_csv('t4_bishop_porch_lines.csv',index=False)
print(len(b), b.groupby(b.t.dt.hour).size().to_dict(), b.t.dt.minute.value_counts().head(6).to_dict())
for h in ['Tabby','claude-code-cli']:
    g=P[P.author==h]; print(h,len(g),g.t.dt.minute.value_counts().head(6).to_dict(),(g.t.diff().dt.total_seconds()/60).round(0).value_counts().head(6).to_dict())
