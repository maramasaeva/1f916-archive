"""Counts, trends, concentration, reply behaviour, transitions, model families, themes by type.
Reads types_all.csv.gz (final rules) and themes_all.csv.gz. Writes CSV tables into tables/."""
import sys, json, collections
import numpy as np, pandas as pd
sys.path.insert(0, '.')
from load import load_messages, HERE
import themes as TH

TY = f'{HERE}/types_all.csv.gz'
OUT = f'{HERE}/tables'
M = load_messages()
D = pd.read_csv(TY)
D = D[D.primary != 'no_content'].copy()
X = D.merge(M[['id', 'kind', 'author_model', 'created_at', 'votes', 'depth', 'post_id', 'parent_id', 'family']], on=['id', 'kind'])
X['t'] = pd.to_datetime(X.created_at, unit='ms', utc=True)
T0 = pd.Timestamp('2026-08-05', tz='UTC')
X['day'] = ((X.t - T0).dt.total_seconds() // 86400).astype(int)
X['week'] = X.day // 7
X['hour'] = X.t.dt.hour
X['date'] = X.t.dt.strftime('%Y-%m-%d')
TYPES = [t for t in X.primary.unique()]
order = X.primary.value_counts().index.tolist()
N = len(X)

# 1. counts overall, posts vs comments, concentration
rows = []
for t in order:
    G = X[X.primary == t]
    hc = G.handle.value_counts()
    rows.append({'type': t, 'n': len(G), 'share_pct': round(100 * len(G) / N, 2),
                 'posts': int((G.kind == 'post').sum()), 'comments': int((G.kind == 'comment').sum()),
                 'share_of_posts_pct': round(100 * (G.kind == 'post').sum() / (X.kind == 'post').sum(), 2),
                 'share_of_comments_pct': round(100 * (G.kind == 'comment').sum() / (X.kind == 'comment').sum(), 2),
                 'distinct_handles': int(hc.size), 'top3_handle_share_pct': round(100 * hc.head(3).sum() / len(G), 1),
                 'top3_handles': '; '.join(f'{h} {c}' for h, c in hc.head(3).items())})
C = pd.DataFrame(rows)
C.to_csv(f'{OUT}/type_counts.csv', index=False)

# secondary types
sec = X.secondary.fillna('').str.split(';').explode()
sec = sec[sec != '']
sc = sec.value_counts().rename_axis('type').reset_index(name='as_secondary')
sc['messages_with_any_secondary'] = (X.secondary.fillna('') != '').sum()
sc.to_csv(f'{OUT}/secondary_counts.csv', index=False)

# 2. per day and per week
byday = X.groupby(['date', 'primary']).size().unstack(fill_value=0)
byday['total'] = byday.sum(axis=1)
byday.to_csv(f'{OUT}/type_by_day_counts.csv')
share_day = byday.drop(columns='total').div(byday.total, axis=0).round(5)
share_day.to_csv(f'{OUT}/type_by_day_share.csv')
byweek = X.groupby(['week', 'primary']).size().unstack(fill_value=0)
byweek['total'] = byweek.sum(axis=1)
byweek.insert(0, 'week_start_utc', [(T0 + pd.Timedelta(days=7 * w)).strftime('%Y-%m-%d') for w in byweek.index])
byweek.to_csv(f'{OUT}/type_by_week_counts.csv')
wshare = byweek.drop(columns=['week_start_utc', 'total']).div(byweek.total, axis=0).round(5)
wshare.insert(0, 'week_start_utc', byweek.week_start_utc)
wshare.to_csv(f'{OUT}/type_by_week_share.csv')

# 3. growth after day 30 (days 0-29 vs 30-61), also posts only / comments only and excluding top 3 handles of the type
rows = []
early = X[X.day < 30]; late = X[X.day >= 30]
for t in order:
    if t == 'placeholder': continue
    se = 100 * (early.primary == t).mean(); sl = 100 * (late.primary == t).mean()
    top3 = X[X.primary == t].handle.value_counts().head(3).index
    e2 = early[~early.handle.isin(top3)]; l2 = late[~late.handle.isin(top3)]
    rows.append({'type': t, 'share_days_0_29_pct': round(se, 2), 'share_days_30_61_pct': round(sl, 2),
                 'change_pp': round(sl - se, 2), 'ratio_late_to_early': round(sl / se, 2) if se else np.nan,
                 'n_days_0_29': int((early.primary == t).sum()), 'n_days_30_61': int((late.primary == t).sum()),
                 'per_day_0_29': round((early.primary == t).sum() / 30, 1), 'per_day_30_61': round((late.primary == t).sum() / late.day.nunique(), 1),
                 'change_pp_excluding_top3_handles': round(100 * (l2.primary == t).mean() - 100 * (e2.primary == t).mean(), 2)})
G30 = pd.DataFrame(rows).sort_values('change_pp', ascending=False)
G30.to_csv(f'{OUT}/trend_after_day30.csv', index=False)
pd.DataFrame({'period': ['days 0-29', 'days 30-61'], 'messages': [len(early), len(late)], 'days': [early.day.nunique(), late.day.nunique()]}).to_csv(f'{OUT}/trend_periods.csv', index=False)

# 4. time of day
H = X.groupby(['primary', 'hour']).size().unstack(fill_value=0)
H.to_csv(f'{OUT}/type_by_hour_counts.csv')
H.div(H.sum(axis=1), axis=0).round(5).to_csv(f'{OUT}/type_by_hour_share_within_type.csv')
(H.sum(axis=0) / H.sum().sum()).round(5).rename('all_messages_share').to_csv(f'{OUT}/hour_share_all.csv')

# 5. length distribution
L = X.groupby('primary').length.describe(percentiles=[.1, .25, .5, .75, .9]).round(0)
L.columns = ['n', 'mean', 'std', 'min', 'p10', 'p25', 'median', 'p75', 'p90', 'max']
L = L.loc[order]
L.to_csv(f'{OUT}/length_by_type.csv')

# 6. reply behaviour. direct replies: comments whose parent is this message (top-level comments for a post)
Cm = X[X.kind == 'comment'][['id', 'handle', 'created_at', 'post_id', 'parent_id']].copy()
Cm['pk'] = np.where(Cm.parent_id.notna(), 'comment', 'post')
Cm['pid'] = np.where(Cm.parent_id.notna(), Cm.parent_id, Cm.post_id).astype('int64')
par = X[['kind', 'id', 'handle', 'created_at']].rename(columns={'kind': 'pk', 'id': 'pid', 'handle': 'p_handle', 'created_at': 'p_created'})
J = Cm.merge(par, on=['pk', 'pid'], how='inner')
J = J[J.handle != J.p_handle]
J['delay_s'] = (J.created_at - J.p_created) / 1000
g = J.groupby(['pk', 'pid']).agg(n_replies=('id', 'size'), first_delay_s=('delay_s', 'min')).reset_index().rename(columns={'pk': 'kind', 'pid': 'id'})
X = X.merge(g, on=['kind', 'id'], how='left')
X['n_replies'] = X.n_replies.fillna(0)
end = X.created_at.max()
X['observable_1h'] = X.created_at <= end - 3600 * 1000
X['answered_1h'] = (X.first_delay_s <= 3600)
X['answered_any'] = X.n_replies > 0
R = X[X.observable_1h].groupby('primary').agg(n=('id', 'size'), answered_within_1h_pct=('answered_1h', lambda s: 100 * s.mean()),
                                              answered_ever_pct=('answered_any', lambda s: 100 * s.mean()),
                                              median_replies=('n_replies', 'median'), mean_replies=('n_replies', 'mean'),
                                              median_votes=('votes', 'median'), mean_votes=('votes', 'mean'),
                                              mean_depth=('depth', 'mean')).round(2)
R = R.loc[[t for t in order if t in R.index]]
R.to_csv(f'{OUT}/reply_behaviour_by_type.csv')
# same split by kind
for k in ('post', 'comment'):
    Rk = X[(X.observable_1h) & (X.kind == k)].groupby('primary').agg(n=('id', 'size'), answered_within_1h_pct=('answered_1h', lambda s: 100 * s.mean()),
                                              median_replies=('n_replies', 'median'), median_votes=('votes', 'median')).round(2)
    Rk.to_csv(f'{OUT}/reply_behaviour_by_type_{k}s.csv')
X.drop(columns=['author_model']).to_pickle(f'{HERE}/.X.pkl')

# 7. transitions: parent type -> reply type (comments only)
ptype = X[['kind', 'id', 'primary']].rename(columns={'kind': 'pk', 'id': 'pid', 'primary': 'parent_type'})
Tm = Cm.merge(ptype, on=['pk', 'pid'], how='inner').merge(X[X.kind == 'comment'][['id', 'primary']].rename(columns={'primary': 'reply_type'}), on='id')
Tm = Tm[~Tm.parent_type.isin(['placeholder']) & ~Tm.reply_type.isin(['placeholder'])]
mat = pd.crosstab(Tm.parent_type, Tm.reply_type)
mat.to_csv(f'{OUT}/transition_counts.csv')
rown = mat.div(mat.sum(axis=1), axis=0).round(4)
rown.to_csv(f'{OUT}/transition_row_share.csv')
exp = np.outer(mat.sum(axis=1), mat.sum(axis=0)) / mat.values.sum()
lift = pd.DataFrame(mat.values / exp, index=mat.index, columns=mat.columns).round(2)
lift.to_csv(f'{OUT}/transition_lift.csv')
rng = np.random.RandomState(7)
asym = []
ts = list(mat.index)
for a in ts:
    for b in ts:
        if a >= b or a not in mat.columns or b not in mat.columns: continue
        ab = int(mat.loc[a, b]); ba = int(mat.loc[b, a])
        if ab >= 30 and ba >= 30 and ab + ba >= 200:
            lab = lift.loc[a, b]; lba = lift.loc[b, a]
            asym.append({'type_a': a, 'type_b': b, 'a_to_b': ab, 'b_to_a': ba, 'lift_a_to_b': lab, 'lift_b_to_a': lba,
                         'log2_ratio_of_lifts': round(float(np.log2(lab / lba)), 2)})
A = pd.DataFrame(asym)
A['log2_ratio_of_shares'] = A.log2_ratio_of_lifts
A['abs'] = A.log2_ratio_of_shares.abs()
A = A.sort_values('abs', ascending=False).head(10).drop(columns='abs').reset_index(drop=True)
exrows = []
for r in A.itertuples():
    hi_a, hi_b = (r.type_a, r.type_b) if r.log2_ratio_of_shares > 0 else (r.type_b, r.type_a)  # direction hi_a -> hi_b is the more common
    S = Tm[(Tm.parent_type == hi_a) & (Tm.reply_type == hi_b)]
    pick = S.sample(min(3, len(S)), random_state=rng)
    exrows.append('; '.join(f'{p[0]}{int(i)} -> c{int(c)}' for p, i, c in zip(pick.pk, pick.pid, pick.id)))
A['more_common_direction'] = ['%s -> %s' % ((r.type_a, r.type_b) if r.log2_ratio_of_shares > 0 else (r.type_b, r.type_a)) for r in A.itertuples()]
A['example_pairs_parent_to_reply (p=post, c=comment)'] = exrows
A.to_csv(f'{OUT}/transition_asymmetries.csv', index=False)

# 8. model family (self-declared)
F = X.groupby('family').size().sort_values(ascending=False)
keepf = F[F >= 500].index
FT = X[X.family.isin(keepf)].groupby(['family', 'primary']).size().unstack(fill_value=0)
FT['messages'] = FT.sum(axis=1)
FT.to_csv(f'{OUT}/family_type_counts.csv')
FS = FT.drop(columns='messages').div(FT.messages, axis=0).round(4)
FS.insert(0, 'messages', FT.messages)
FS.to_csv(f'{OUT}/family_type_share.csv')
fh = X.groupby('family').agg(messages=('id', 'size'), handles=('handle', 'nunique'))
fh['top3_handle_share_pct'] = [round(100 * X[X.family == f].handle.value_counts().head(3).sum() / (X.family == f).sum(), 1) for f in fh.index]
fh.sort_values('messages', ascending=False).to_csv(f'{OUT}/family_overview.csv')

# 9. daily series of specific shares
X['hash_or_table'] = X.has_hash | X.has_table
day = X.groupby('date').agg(messages=('id', 'size'), hash_or_table=('hash_or_table', 'mean'), hash=('has_hash', 'mean'), table=('has_table', 'mean'))
for t in ['question', 'correction_self', 'fiction_poetry_art', 'heartbeat_status']:
    day[t] = X.groupby('date').primary.apply(lambda s, t=t: (s == t).mean())
day.round(5).to_csv(f'{OUT}/daily_series.csv')

# 10. validation-corrected estimate of true shares from the judged sample (v2 where revalidated, v1 otherwise)
v1 = pd.read_csv(f'{HERE}/validation_v1.csv'); v2 = pd.read_csv(f'{HERE}/validation_v2.csv')
use = pd.concat([v2, v1[v1.primary.isin(['placeholder', 'offer_listing', 'money_payment'])]])
pred = X.primary.value_counts()
est = collections.Counter()
for p, G in use.groupby('primary'):
    for jt, c in G.judged_type.value_counts().items():
        est[jt] += pred.get(p, 0) * c / len(G)
E = pd.DataFrame({'type': list(est.keys()), 'estimated_true_count': [round(v) for v in est.values()]})
E['estimated_true_share_pct'] = (100 * E.estimated_true_count / E.estimated_true_count.sum()).round(2)
E = E.merge(C[['type', 'n', 'share_pct']].rename(columns={'n': 'rule_label_count', 'share_pct': 'rule_label_share_pct'}), on='type', how='left').sort_values('estimated_true_count', ascending=False)
E.to_csv(f'{OUT}/estimated_true_share.csv', index=False)

# 11. themes
Tt = pd.read_csv(f'{HERE}/themes_all.csv.gz')
Y = X.merge(Tt, on=['id', 'kind'])
names = list(TH.THEMES)
rows = []
for th in names:
    G = Y[Y[th] == 1]
    hc = G.handle.value_counts()
    rows.append({'theme': th, 'messages': len(G), 'share_pct': round(100 * len(G) / len(Y), 2), 'posts': int((G.kind == 'post').sum()),
                 'comments': int((G.kind == 'comment').sum()), 'distinct_handles': int(hc.size),
                 'top3_handle_share_pct': round(100 * hc.head(3).sum() / len(G), 1), 'top3_handles': '; '.join(f'{h} {c}' for h, c in hc.head(3).items())})
pd.DataFrame(rows).sort_values('messages', ascending=False).to_csv(f'{OUT}/theme_counts.csv', index=False)
tt = pd.DataFrame({th: Y[Y[th] == 1].primary.value_counts() for th in names}).fillna(0).astype(int).T
tt = tt[[c for c in order if c in tt.columns]]
tt.to_csv(f'{OUT}/theme_by_type_counts.csv')
tt.div(tt.sum(axis=1), axis=0).round(4).to_csv(f'{OUT}/theme_by_type_share.csv')
tw = pd.DataFrame({th: Y[Y[th] == 1].groupby('week').size() for th in names}).fillna(0).astype(int)
tw.insert(0, 'week_start_utc', [(T0 + pd.Timedelta(days=7 * w)).strftime('%Y-%m-%d') for w in tw.index])
tw['messages_in_week'] = Y.groupby('week').size()
tw.to_csv(f'{OUT}/theme_by_week_counts.csv')
twd = tw.drop(columns=['week_start_utc', 'messages_in_week'])
twd.div(tw.messages_in_week, axis=0).round(5).assign(week_start_utc=tw.week_start_utc).to_csv(f'{OUT}/theme_by_week_share.csv')
# theme x kind and trend
rows = []
for th in names:
    e = Y[(Y.day < 30)]; l = Y[Y.day >= 30]
    rows.append({'theme': th, 'share_days_0_29_pct': round(100 * e[th].mean(), 2), 'share_days_30_61_pct': round(100 * l[th].mean(), 2)})
pd.DataFrame(rows).assign(change_pp=lambda d: (d.share_days_30_61_pct - d.share_days_0_29_pct).round(2)).to_csv(f'{OUT}/theme_trend_after_day30.csv', index=False)
print(C.to_string()); print(G30.to_string()); print(R.to_string()); print(A.to_string()); print(E.to_string())
