"""Handle by cluster, model-family by cluster (self-declared labels), reply structure by cluster."""
from common import *

M = pd.read_pickle(os.path.join(CACHE, 'M_final.pkl'))
T = pd.read_csv(os.path.join(OUT, 'topics.csv'))
K = len(T)
A = M[M.topic >= 0]

# ---- handle x cluster
top = A.handle.value_counts().head(60).index.tolist()
hc = pd.crosstab(A.handle, A.topic).reindex(columns=range(K), fill_value=0)
hc.loc[top].assign(total=hc.loc[top].sum(1)).to_csv(os.path.join(OUT, 'handle_by_cluster_top60_counts.csv'))
(hc.loc[top].div(hc.loc[top].sum(1), axis=0).round(4)).to_csv(os.path.join(OUT, 'handle_by_cluster_top60_rowshare.csv'))
rows = []
for c in range(K):
    col = hc[c]
    s = col / col.sum()
    rows.append(dict(cluster=c, label=T.label[c], messages=int(col.sum()), handles=int((col > 0).sum()),
                     handles_5plus_msgs=int((col >= 5).sum()), top_handle=s.idxmax(), top_handle_share=round(s.max(), 3),
                     effective_handles=round(1 / (s ** 2).sum(), 1), dominated_by_one_handle=bool(s.max() > 0.5),
                     top3_share=round(s.nlargest(3).sum(), 3), share_of_top60_handles=round(col.loc[top].sum() / col.sum(), 3)))
HS = pd.DataFrame(rows)
HS['shared_by_many'] = HS.effective_handles >= 100
HS.to_csv(os.path.join(OUT, 'cluster_handle_concentration.csv'), index=False)

# ---- family x cluster
fc = pd.crosstab(A.family, A.topic).reindex(columns=range(K), fill_value=0)
fc.to_csv(os.path.join(OUT, 'family_by_cluster_counts.csv'))
fc.div(fc.sum(0), axis=1).round(4).to_csv(os.path.join(OUT, 'family_by_cluster_share_of_cluster.csv'))
lift = (fc.div(fc.sum(1), axis=0)).div(fc.sum(0) / fc.values.sum(), axis=1).round(2)
lift.to_csv(os.path.join(OUT, 'family_by_cluster_lift.csv'))
hf = A.drop_duplicates('handle').groupby('family').size()   # handles per family (label of first message)
hf.rename('handles').to_csv(os.path.join(OUT, 'family_handles.csv'))

# ---- reply structure
C = rd('data/comments/*.jsonl.gz')
C = C[C.created_at.notna()]
C['addr'] = np.where(C.intended_parent_id.notna(), 'c' + C.intended_parent_id.astype('Int64').astype(str),
                     np.where(C.parent_id.notna(), 'c' + C.parent_id.astype('Int64').astype(str), 'p' + C.post_id.astype('Int64').astype(str)))
C['uid'] = 'c' + C.id.astype(str)
ch = C[['addr', 'author', 'created_at']].rename(columns={'addr': 'uid', 'author': 'rep_author', 'created_at': 'rep_t'})
mm = M[['uid', 'handle', 'created_at']].merge(ch, on='uid', how='left')
mm['other'] = mm.rep_author.notna() & (mm.rep_author != mm.handle)
mm['dt'] = (mm.rep_t - mm.created_at) / 1000
g = mm.groupby('uid')
R = pd.DataFrame(dict(replies_all=g.rep_author.count(), replies_other=g.other.sum(),
                      first_other_s=mm[mm.other].groupby('uid').dt.min()))
R = R.reindex(M.uid).reset_index()
R['replies_other'] = R.replies_other.fillna(0)
R['answered_any'] = R.replies_other > 0
R['answered_1h'] = R.first_other_s.notna() & (R.first_other_s <= 3600) & (R.first_other_s >= 0)
M2 = M.merge(R, on='uid')
M2.to_pickle(os.path.join(CACHE, 'M_reply.pkl'))
A2 = M2[M2.topic >= 0]
rows = []
for kind, d_ in [('all', A2), ('post', A2[A2.kind == 'post']), ('comment', A2[A2.kind == 'comment'])]:
    for c, d in d_.groupby('topic'):
        rows.append(dict(cluster=c, label=T.label[c], kind=kind, messages=len(d), median_direct_replies=d.replies_all.median(),
                         mean_direct_replies=round(d.replies_all.mean(), 2),
                         share_answered_by_other_handle=round(d.answered_any.mean(), 3),
                         share_answered_within_1h=round(d.answered_1h.mean(), 3),
                         median_first_reply_min=round(d.first_other_s.median() / 60, 1) if d.first_other_s.notna().any() else np.nan,
                         median_depth=d.depth.median() if kind != 'post' else np.nan,
                         mean_votes=round(d.votes.mean(), 2), median_votes=d.votes.median(),
                         share_with_votes=round((d.votes > 0).mean(), 3)))
RS = pd.DataFrame(rows)
RS.to_csv(os.path.join(OUT, 'reply_structure_by_cluster.csv'), index=False)
allc = RS[RS.kind == 'all'].sort_values('share_answered_within_1h')
print(allc.to_string())
base = A2.groupby('kind')[['answered_any', 'answered_1h']].mean()
print(base)
