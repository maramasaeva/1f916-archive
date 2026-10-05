import json,glob,pandas as pd,os
def porch():
    rows=[]
    for f in sorted(glob.glob(os.path.expanduser('~/1f916-archive/.work/files/porch/*.json'))):
        d=json.load(open(f))
        for l in d['lines']: rows.append(l)
    P=pd.DataFrame(rows).drop_duplicates('id').sort_values('id')
    P['t']=pd.to_datetime(P.created_at,unit='ms',utc=True)
    P['url']=P.id.map(lambda i:f"https://1f916.ai/api/porch?day=")+P.day+f"#line"  # placeholder
    P['url']="https://1f916.ai/api/porch?day="+P.day.astype(str)
    return P
