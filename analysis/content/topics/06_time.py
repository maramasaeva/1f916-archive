"""Daily cluster share (messages, words), birth/decline, growth after day 30, fastest growing and declining terms."""
import pickle, scipy.sparse as sp
from common import *

M = pd.read_pickle(os.path.join(CACHE, 'M_final.pkl'))
T = pd.read_csv(os.path.join(OUT, 'topics.csv'))
vec = pickle.load(open(os.path.join(CACHE, 'vec.pkl'), 'rb'))
terms = np.array(vec.get_feature_names_out())
K = len(T)
A = M[M.topic >= 0]
days = pd.date_range('2026-08-05', '2026-10-05').strftime('%Y-%m-%d')
cm = A.pivot_table(index='day', columns='topic', values='uid', aggfunc='count', fill_value=0).reindex(days, fill_value=0)
cw = A.pivot_table(index='day', columns='topic', values='nwords', aggfunc='sum', fill_value=0).reindex(days, fill_value=0)
for c in range(K):
    for d_ in (cm, cw):
        if c not in d_.columns:
            d_[c] = 0
cm, cw = cm[range(K)], cw[range(K)]
sm = cm.div(cm.sum(axis=1), axis=0); sw = cw.div(cw.sum(axis=1), axis=0)
out = pd.concat([cm.add_prefix('n_'), sm.add_prefix('share_msgs_'), sw.add_prefix('share_words_')], axis=1)
out.insert(0, 'day_index', range(len(days)))
out.index.name = 'day'
out.to_csv(os.path.join(OUT, 'topic_daily_share.csv'))
# weekly
A = A.assign(wk=A.week)
wk = A.pivot_table(index='wk', columns='topic', values='uid', aggfunc='count', fill_value=0)
wk.div(wk.sum(axis=1), axis=0).to_csv(os.path.join(OUT, 'topic_weekly_share.csv'))

rows = []
for c in range(K):
    n = cm[c].values
    s = sm[c].values
    nz = np.where(n >= 3)[0]
    birth = days[nz[0]] if len(nz) else ''
    first30, d3160, last14 = s[:30].mean(), s[30:61].mean(), s[-14:].mean()
    peakd = int(pd.Series(s).rolling(7, center=True, min_periods=4).mean().values.argmax())
    slope = np.polyfit(np.arange(30, 62), s[30:62], 1)[0] if s[30:62].std() > 0 else 0
    rows.append(dict(cluster=c, label=T.label[c], birth_first_day_with_3_messages=birth,
                     mean_daily_share_day0_29=round(first30, 4), mean_daily_share_day30_60=round(d3160, 4),
                     ratio_day30_60_over_day0_29=round(d3160 / first30, 2) if first30 else np.nan,
                     mean_daily_share_last14=round(last14, 4), peak_day_7d=days[peakd], peak_day_index=peakd,
                     slope_share_per_day_after_day30=slope,
                     grew_after_day30=bool(d3160 > first30 * 1.1),
                     declined_after_day30=bool(d3160 < first30 * 0.9),
                     msgs_total=int(n.sum()), msgs_day0_29=int(n[:30].sum()), msgs_day30_60=int(n[30:].sum())))
G = pd.DataFrame(rows)
G.to_csv(os.path.join(OUT, 'cluster_growth.csv'), index=False)

# terms: document frequency (share of messages containing the term) day 0-29 vs day 30-60
Xall = sp.load_npz(os.path.join(CACHE, 'X_all.npz'))
B = (Xall > 0).tocsc()
early = (M.dayn < 30).values & (M.ntok >= 5).values
late = (M.dayn >= 30).values & (M.ntok >= 5).values
de = np.asarray(B[early].sum(0)).ravel(); dl = np.asarray(B[late].sum(0)).ravel()
ne, nl = early.sum(), late.sum()
pe, pl = (de + 0.5) / (ne + 1), (dl + 0.5) / (nl + 1)
lr = np.log2(pl / pe)
ok = (de + dl) >= 150
tdf = pd.DataFrame(dict(term=terms, msgs_day0_29=de, msgs_day30_60=dl, per1000_day0_29=1000 * de / ne,
                        per1000_day30_60=1000 * dl / nl, log2_ratio=lr))[ok]
idsM = M.uid.values


def ex_ids(term, period):
    j = list(terms).index(term)
    col = B[:, j].toarray().ravel() > 0
    sel = np.where(col & (early if period == 'early' else late))[0]
    if len(sel) == 0:
        return ''
    pick = sel[np.linspace(0, len(sel) - 1, min(5, len(sel))).astype(int)]
    return ' '.join(idsM[pick])


# author concentration per candidate term, and handle-name filter
codes = pd.factorize(M.handle)[0]
pos = {t: i for i, t in enumerate(terms)}
Bc = B.tocsc()
topsh, nauth = [], []
for t in tdf.term:
    rows_ = Bc.indices[Bc.indptr[pos[t]]:Bc.indptr[pos[t] + 1]]
    bc = np.bincount(codes[rows_])
    topsh.append(bc.max() / bc.sum()); nauth.append(int((bc > 0).sum()))
tdf['top_author_share'] = np.round(topsh, 3); tdf['authors'] = nauth
words = set(w.strip().lower() for w in open('/usr/share/dict/web2'))
hpieces = set()
for h in M.handle.unique():
    h = h.lower()
    hpieces.add(h)
    for p in re.split(r'[-_.\d]+', h):
        if len(p) >= 4 and p not in words:
            hpieces.add(p)
big = M.handle.value_counts(); big = set(h.lower() for h in big[big >= 100].index)
bigpieces = {p for h in big for p in re.split(r'[-_.\d]+', h) if len(p) >= 4}
bigpieces |= big                                   # unigram terms equal to a piece of a frequent handle (names, e.g. chit, souchong)
tdf['handle_token'] = [any(w in hpieces for w in re.split(r'[\s\-_]+', t)) or (len(t.split()) == 1 and (t in hpieces or t in bigpieces or len(t) <= 3 or any(h.startswith(t) for h in big)))
                       for t in tdf.term]
tdf['content_term'] = (~tdf.handle_token) & (tdf.top_author_share <= 0.5) & (tdf.authors >= 8)
cand = tdf[tdf.content_term]
def pick(df, n=15, jmax=0.4):
    # greedy: skip a term whose message set overlaps an accepted term by Jaccard >= jmax (template phrases collapse to one row)
    out, sets = [], []
    for t in df.term:
        st = set(Bc.indices[Bc.indptr[pos[t]]:Bc.indptr[pos[t] + 1]])
        if all(len(st & q) / len(st | q) < jmax for q in sets):
            out.append(t); sets.append(st)
        if len(out) == n:
            break
    return df.set_index('term').loc[out].reset_index()


up = pick(cand.sort_values('log2_ratio', ascending=False))
dn = pick(cand.sort_values('log2_ratio'))
up['example_ids'] = [ex_ids(t, 'late') for t in up.term]
dn['example_ids'] = [ex_ids(t, 'early') for t in dn.term]
up.insert(0, 'rank', range(1, 16)); dn.insert(0, 'rank', range(1, 16))
up.round(3).to_csv(os.path.join(OUT, 'terms_fastest_growing.csv'), index=False)
dn.round(3).to_csv(os.path.join(OUT, 'terms_fastest_declining.csv'), index=False)
# id prefix p = post, c = comment
tdf.round(3).to_csv(os.path.join(OUT, 'terms_growth_all.csv'), index=False)
print(G.to_string())
print(up[['term', 'msgs_day0_29', 'msgs_day30_60', 'log2_ratio', 'authors']]); print(dn[['term', 'msgs_day0_29', 'msgs_day30_60', 'log2_ratio', 'authors']])
