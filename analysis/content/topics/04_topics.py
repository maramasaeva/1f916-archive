"""topics.csv, topic_terms.csv, series flags. Needs labels.csv (topic,label) written after reading terms and examples."""
import pickle
from common import *

M = pd.read_pickle(os.path.join(CACHE, 'M_topics.pkl'))
H = np.load(os.path.join(CACHE, 'H.npy'))
vec = pickle.load(open(os.path.join(CACHE, 'vec.pkl'), 'rb'))
terms = np.array(vec.get_feature_names_out())
K = H.shape[0]
lp = os.path.join(OUT, 'labels.csv')
labels = dict(pd.read_csv(lp).values) if os.path.exists(lp) else {}
# moderated messages are served as a fixed placeholder body, not the author's text; they are not clustered
M['placeholder'] = M.disp.str.match(r'^\[(collapsed|withdrawn|removed)')
ph = M[M.placeholder]
pd.DataFrame([dict(placeholder_messages=len(ph), collapsed=int((ph.mod_state == 'collapsed').sum()), withdrawn=int((ph.mod_state == 'withdrawn').sum()),
                   removed=int((ph.mod_state == 'removed').sum()), posts=int((ph.kind == 'post').sum()), comments=int((ph.kind == 'comment').sum()),
                   share_of_all_messages=round(len(ph) / len(M), 4), share_of_messages_under_20_words=round(len(ph) / M.short.sum(), 3),
                   assigned_by_model_to=str(ph.topic.value_counts().to_dict()))]).to_csv(os.path.join(OUT, 'placeholder_messages.csv'), index=False)
M.loc[M.placeholder, 'topic'] = -1
M['label'] = M.topic.map(lambda t: labels.get(t, f'topic {t}') if t >= 0 else 'unassigned')

# one-author series: message whose opening skeleton (digits to N, first 8 words) is shared by >= 8 messages
# of which one handle wrote >= 90 percent. Posts use the title, comments the first words of the body.
def skel(r):
    s = r.title if r.kind == 'post' and isinstance(r.title, str) else r.disp
    s = re.sub(r'\d+', 'N', str(s).lower())
    return ' '.join(re.findall(r"[a-zà-ɏN']+", s)[:8])
M['skel'] = M.apply(skel, axis=1)
g = M[M.skel.str.split().str.len() >= 3].groupby('skel').handle.agg(['size', lambda x: x.value_counts().iloc[0] / len(x)])
g.columns = ['n', 'top_share']
ser = set(g[(g.n >= 8) & (g.top_share >= 0.9)].index)
M['series'] = M.skel.isin(ser)
# add curated one-author post series from the swarm analysis
t7 = pd.read_csv(os.path.join(ROOT, 'analysis/swarm/t7_series_curated.csv'))
ids = set()
for _, r in t7[t7.type == 'one author'].iterrows():
    ids |= {'p' + x for x in str(r.post_ids).split()}
M.loc[M.uid.isin(ids), 'series'] = True
pd.DataFrame(dict(skeleton=sorted(ser))).merge(g.reset_index(), left_on='skeleton', right_on='skel').drop(columns='skel') \
    .sort_values('n', ascending=False).to_csv(os.path.join(OUT, 'series_skeletons.csv'), index=False)
M.to_pickle(os.path.join(CACHE, 'M_final.pkl'))

tot = len(M[M.topic >= 0])
rows = []
for t in range(K):
    d = M[M.topic == t]
    daily = d.groupby('day').size()
    vc = d.handle.value_counts()
    # peak: 7-day centred rolling max of daily count
    full = pd.Series(0, index=pd.date_range('2026-08-05', '2026-10-05').strftime('%Y-%m-%d'))
    full.loc[daily.index] = daily.values
    peak = full.rolling(7, center=True, min_periods=4).mean().idxmax()
    rows.append(dict(cluster=t, label=labels.get(t, f'topic {t}'), posts=int((d.kind == 'post').sum()),
                     comments=int((d.kind == 'comment').sum()), messages=len(d), share_of_assigned=round(len(d) / tot, 4),
                     share_of_words=round(d.nwords.sum() / M[M.topic >= 0].nwords.sum(), 4),
                     handles=d.handle.nunique(), top_handle=vc.index[0], top_handle_share=round(vc.iloc[0] / len(d), 3),
                     top3_handle_share=round(vc.head(3).sum() / len(d), 3),
                     first_message_date=d.t.min().strftime('%Y-%m-%d'), peak_date_7d=peak,
                     series_share=round(d.series.mean(), 3), median_words=float(d.nwords.median()),
                     short_share=round(d.short.mean(), 3)))
T = pd.DataFrame(rows)
T['top_terms_15'] = ['; '.join(terms[np.argsort(-H[t])[:15]]) for t in range(K)]
T.to_csv(os.path.join(OUT, 'topics.csv'), index=False)
tr = []
for t in range(K):
    idx = np.argsort(-H[t])[:15]
    for r, i in enumerate(idx, 1):
        tr.append(dict(cluster=t, label=labels.get(t, f'topic {t}'), rank=r, term=terms[i], weight=round(float(H[t, i]), 4)))
pd.DataFrame(tr).to_csv(os.path.join(OUT, 'topic_terms.csv'), index=False)
print(T.drop(columns=['top_handle']).to_string())
print('unassigned', (M.topic < 0).sum(), 'series share overall', M.series.mean())
