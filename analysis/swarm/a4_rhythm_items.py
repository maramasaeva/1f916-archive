import json, numpy as np, pandas as pd
from load import *
c,p=load()
c['kind']='comment'; p['kind']='post'
it=pd.concat([c[['id','kind','author','t']],p[['id','kind','author','t']]],ignore_index=True).sort_values('t')
core=json.load(open('t1_core_handles.json'))
act=it.author.value_counts(); act=act[act>=100].index
rows=[]
for h in act:
    g=it[it.author==h].sort_values('t'); n=len(g)
    d=g.t.diff().dt.total_seconds().dropna()/60
    mins=g.t.dt.minute.values; mb=np.bincount(mins,minlength=60)
    sec=g.t.dt.hour.values*60+g.t.dt.minute.values
    after0=((sec<10)).mean()
    hr=np.bincount(g.t.dt.hour.values,minlength=24)
    day=g.groupby(g.t.dt.strftime('%Y-%m-%d')).size()
    pday=g[g.kind=='post'].groupby(g.t.dt.strftime('%Y-%m-%d')).size()
    top3=np.sort(mb)[::-1][:3].sum()/n
    r60=d[(d>=55)&(d<=65)].shape[0]/max(len(d),1)
    rows.append(dict(handle=h,in_core=h in core,items=n,posts=int((g.kind=='post').sum()),days_active=len(day),items_per_active_day_median=float(day.median()),max_items_one_day=int(day.max()),max_posts_one_day=int(pday.max()) if len(pday) else 0,
      first=g.t.min(),last=g.t.max(),gap_min_median=round(d.median(),1),gap_min_p10=round(d.quantile(.1),1),gap_min_p90=round(d.quantile(.9),1),share_gaps_55_65min=round(r60,3),
      top3_minute_bins_share=round(top3,3),modal_minute=int(mb.argmax()),share_in_first_10min_utc_day=round(after0,3),peak_hour_utc=int(hr.argmax()),peak_hour_share=round(hr.max()/n,3),
      active_hours=int((hr>0.02*n).sum())))
R=pd.DataFrame(rows).sort_values('items',ascending=False); R.to_csv('t4_rhythm_items_by_handle.csv',index=False)
pd.set_option('display.width',280); print(R[R.in_core].to_string())
# 00:00 UTC window overall
it['h']=it.t.dt.hour; print(it.groupby('h').size().to_string())
