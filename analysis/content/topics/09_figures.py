"""Figures (SVG) with a CSV of the plotted data per figure (same stem) and figures.json."""
import pickle, collections, scipy.sparse as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from common import *

INK, MID, LIGHT, ACC = '#333333', '#8c8c8c', '#d4d4d4', '#b5341a'
plt.rcParams.update({'svg.fonttype': 'none', 'font.family': 'sans-serif', 'font.size': 7, 'text.color': INK,
                     'axes.edgecolor': MID, 'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
                     'axes.linewidth': 0.6, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.dpi': 100,
                     'figure.facecolor': 'white', 'axes.facecolor': 'white', 'savefig.facecolor': 'white',
                     'axes.titlesize': 8, 'axes.titleweight': 'normal', 'axes.titlelocation': 'left'})
CM = LinearSegmentedColormap.from_list('acc', ['#ffffff', ACC])
W7 = 7.0
M = pd.read_pickle(os.path.join(CACHE, 'M_reply.pkl'))
T = pd.read_csv(os.path.join(OUT, 'topics.csv'))
G = pd.read_csv(os.path.join(OUT, 'cluster_growth.csv'))
RS = pd.read_csv(os.path.join(OUT, 'reply_structure_by_cluster.csv'))
HS = pd.read_csv(os.path.join(OUT, 'cluster_handle_concentration.csv'))
K = len(T)
SH = {c: f"{c} {T.label[c]}"[:52] for c in range(K)}
A = M[M.topic >= 0]
reg = []


def finish(fig, stem, title, desc, n, ax=None):
    fig.savefig(os.path.join(FIG, stem + '.svg'), format='svg', bbox_inches='tight', pad_inches=0.08)
    plt.close(fig)
    reg.append(dict(file=f'figures/{stem}.svg', title=title, description=desc, source_csv=f'figures/{stem}.csv', n=int(n)))


def save_csv(df, stem):
    df.to_csv(os.path.join(FIG, stem + '.csv'), index=False)


def dodge(ys, gap):
    order = np.argsort(ys); y = np.array(ys, float)[order]
    for _ in range(200):
        moved = False
        for i in range(1, len(y)):
            if y[i] - y[i - 1] < gap:
                d = (gap - (y[i] - y[i - 1])) / 2
                y[i - 1] -= d; y[i] += d; moved = True
        if not moved:
            break
    out = np.empty_like(y); out[order] = y
    return out


# ---- a. cluster sizes
stem = 'fig_a_cluster_sizes'
d = T.sort_values('messages')
fig, ax = plt.subplots(figsize=(W7, 3.6))
y = np.arange(len(d))
ax.barh(y, d.comments, color=ACC, height=0.65, label='comments')
ax.barh(y, d.posts, left=d.comments, color=MID, height=0.65, label='posts')
for yi, (m, s) in enumerate(zip(d.messages, d.share_of_assigned)):
    ax.text(m + 150, yi, f'{m:,} ({s * 100:.1f}%)', va='center', fontsize=6.5)
ax.set_yticks(y); ax.set_yticklabels([SH[c] for c in d.cluster]); ax.set_xlabel('messages (count)')
ax.set_xlim(0, d.messages.max() * 1.18); ax.legend(frameon=False, loc='lower right')
ax.set_title('Messages per cluster, posts and comments, 5 Aug to 5 Oct 2026')
save_csv(d[['cluster', 'label', 'posts', 'comments', 'messages', 'share_of_assigned']], stem)
finish(fig, stem, 'Messages per cluster, posts and comments, 5 Aug to 5 Oct 2026',
       'Horizontal bars of the number of posts and comments assigned to each of 18 clusters.', len(A))

# ---- b. stacked area daily share
stem = 'fig_b_daily_share'
D = pd.read_csv(os.path.join(OUT, 'topic_daily_share.csv'))
S = D[[f'share_msgs_{c}' for c in range(K)]].rolling(7, center=True, min_periods=1).mean()
S.columns = range(K)
S = S.div(S.sum(axis=1), axis=0)
order = T.sort_values('messages', ascending=False).cluster.tolist()
greys = ['#9a9a9a', '#b8b8b8', '#7a7a7a', '#d0d0d0']
cols = {c: (ACC if c == 14 else greys[i % 4]) for i, c in enumerate(order)}
fig, ax = plt.subplots(figsize=(W7, 4.2))
x = np.arange(len(S))
ax.stackplot(x, [S[c].values for c in order], colors=[cols[c] for c in order], edgecolor='white', linewidth=0.4)
cum = np.cumsum([S[c].values[-1] for c in order]); mid = cum - np.array([S[c].values[-1] for c in order]) / 2
ypos = dodge(mid, 0.036)
for c, yy, m_ in zip(order, ypos, mid):
    ax.text(len(S) + 0.5, yy, SH[c], fontsize=6, va='center', color=ACC if c == 14 else INK)
ax.set_xlim(0, len(S) - 1); ax.set_ylim(0, 1)
ax.set_xticks(range(0, 61, 10)); ax.set_xticklabels([(START + pd.Timedelta(days=i)).strftime('%d %b') for i in range(0, 61, 10)])
ax.set_xlabel('day (UTC)'); ax.set_ylabel('share of assigned messages (7-day mean)')
ax.set_title('Share of messages per cluster per day (7-day centred mean)')
out = S.copy(); out.columns = [f'share_c{c}' for c in range(K)]; out.insert(0, 'day', D.day)
save_csv(out, stem)
finish(fig, stem, 'Share of messages per cluster per day (7-day centred mean)',
       'Stacked areas of each cluster share of assigned messages per UTC day, smoothed with a 7-day centred mean; cluster 14 in red.', len(A))

# ---- c. heatmap cluster by week
stem = 'fig_c_cluster_by_week'
wk = A.pivot_table(index='topic', columns='week', values='uid', aggfunc='count', fill_value=0).reindex(range(K), fill_value=0)
wks = wk.div(wk.sum(axis=0), axis=1)
fig, ax = plt.subplots(figsize=(W7, 4.0))
im = ax.imshow(wks.values, aspect='auto', cmap=CM)
ax.set_yticks(range(K)); ax.set_yticklabels([SH[c] for c in range(K)])
ax.set_xticks(range(wks.shape[1])); ax.set_xticklabels([(START + pd.Timedelta(weeks=int(i))).strftime('%d %b') for i in wks.columns])
for i in range(K):
    for j in range(wks.shape[1]):
        v = wks.values[i, j]
        ax.text(j, i, f'{v * 100:.0f}', ha='center', va='center', fontsize=5.5, color='white' if v > 0.12 else INK)
ax.set_xlabel('week starting (UTC; last week has 5 days)'); ax.set_title('Cluster share of messages by week (percent of the week)')
ax.spines[:].set_visible(False)
w2 = wks.copy(); w2.columns = [f'week_{c}' for c in w2.columns]; w2.insert(0, 'label', T.label); w2.insert(0, 'cluster', range(K))
save_csv(w2, stem)
finish(fig, stem, 'Cluster share of messages by week (percent of the week)',
       'Heatmap of each cluster share of assigned messages in each of nine weeks, numbers in percent.', len(A))

# ---- d. birth dates
stem = 'fig_d_birth_dates'
d = G.merge(T[['cluster', 'first_message_date']], on='cluster').sort_values('birth_first_day_with_3_messages', ascending=False)
fig, ax = plt.subplots(figsize=(W7, 3.6))
for i, (_, r) in enumerate(d.iterrows()):
    f, b, p = [pd.Timestamp(v) for v in (r.first_message_date, r.birth_first_day_with_3_messages, r.peak_day_7d)]
    ax.plot([f, p], [i, i], color=LIGHT, lw=0.8, zorder=1)
    ax.scatter([f], [i], s=14, facecolors='white', edgecolors=MID, zorder=2)
    ax.scatter([b], [i], s=14, color=MID, zorder=3)
    ax.scatter([p], [i], s=22, color=ACC, zorder=4)
ax.set_yticks(range(len(d))); ax.set_yticklabels([SH[c] for c in d.cluster])
ax.scatter([], [], s=14, facecolors='white', edgecolors=MID, label='first message'); ax.scatter([], [], s=14, color=MID, label='first day with 3 messages')
ax.scatter([], [], s=22, color=ACC, label='peak day (7-day mean)'); ax.legend(frameon=False, ncol=3, fontsize=6, loc='upper center', bbox_to_anchor=(0.4, -0.16))
ax.set_xlabel('date (UTC, 2026)'); ax.set_title('First message, birth and peak date per cluster')
import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.DayLocator(interval=14)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
save_csv(d[['cluster', 'label', 'first_message_date', 'birth_first_day_with_3_messages', 'peak_day_7d']], stem)
finish(fig, stem, 'First message, birth and peak date per cluster',
       'Dot plot per cluster of the date of the first message, the first day with three messages and the peak day of the 7-day mean.', len(A))

# ---- e. concentration
stem = 'fig_e_concentration'
d = T.sort_values('top3_handle_share')
fig, ax = plt.subplots(figsize=(W7, 3.6))
y = np.arange(len(d))
ax.barh(y, d.top3_handle_share * 100, color=[ACC if v > 0.5 else MID for v in d.top3_handle_share], height=0.65)
for yi, (v, h, hs, n) in enumerate(zip(d.top3_handle_share, d.top_handle, d.top_handle_share, d.handles)):
    ax.text(v * 100 + 1, yi, f'{v * 100:.0f}%   top: {h} {hs * 100:.0f}%   {n} handles', va='center', fontsize=6)
ax.set_yticks(y); ax.set_yticklabels([SH[c] for c in d.cluster]); ax.set_xlim(0, 150); ax.spines['bottom'].set_bounds(0, 100)
ax.set_xlabel('share of cluster messages by its top 3 handles (percent)'); ax.set_xticks(range(0, 101, 20))
ax.set_title('Top-3 handle share per cluster (red above 50 percent)')
save_csv(d[['cluster', 'label', 'handles', 'top_handle', 'top_handle_share', 'top3_handle_share']], stem)
finish(fig, stem, 'Top-3 handle share per cluster (red above 50 percent)',
       'Bars of the share of each cluster messages written by its three most frequent handles, with top handle and handle count.', len(A))

# ---- f. answered within 1h
stem = 'fig_f_answered_1h'
r = RS[RS.kind == 'all'].set_index('cluster')
rp = RS[RS.kind == 'post'].set_index('cluster'); rc = RS[RS.kind == 'comment'].set_index('cluster')
d = pd.DataFrame(dict(label=T.label, all_messages=r.share_answered_within_1h, posts=rp.share_answered_within_1h, comments=rc.share_answered_within_1h,
                      n_posts=rp.messages, n_comments=rc.messages)).sort_values('all_messages')
fig, ax = plt.subplots(figsize=(W7, 3.6))
y = np.arange(len(d))
ax.barh(y, d.all_messages * 100, color=MID, height=0.6, label='all messages')
ax.scatter(d.posts * 100, y, color=ACC, s=14, zorder=3, label='posts')
ax.scatter(d.comments * 100, y, color=INK, s=10, marker='s', zorder=3, label='comments')
ax.set_yticks(y); ax.set_yticklabels([SH[c] for c in d.index]); ax.set_xlabel('share answered by another handle within 1 hour (percent)')
ax.legend(frameon=False, loc='lower right', fontsize=6); ax.set_title('Share of messages with a reply by another handle within 1 hour')
save_csv(d.reset_index().rename(columns={'index': 'cluster'}), stem)
finish(fig, stem, 'Share of messages with a reply by another handle within 1 hour',
       'Bars of the share of messages in each cluster that received a direct reply from another handle within 3600 seconds, with posts and comments marked separately.', len(A))

# ---- g. length distribution
stem = 'fig_g_length'
bins = np.logspace(0, np.log10(5000), 45)
fig, ax = plt.subplots(figsize=(W7, 3.0))
rows = []
for k, col, lab in [('post', MID, 'posts'), ('comment', ACC, 'comments')]:
    v = M[M.kind == k].nwords.clip(lower=1)
    h, e = np.histogram(v, bins=bins)
    h = h / h.sum() * 100
    ax.step(e[:-1], h, where='post', color=col, lw=1.2, label=f'{lab} (n={len(v):,}, median {int(np.median(v))} words)')
    rows += [dict(kind=k, bin_left_words=a, share_percent=b) for a, b in zip(e[:-1], h)]
ax.axvline(20, color=LIGHT, lw=0.8); ax.text(21, ax.get_ylim()[1] * 0.92, '20 words', fontsize=6, color=MID)
ax.set_xscale('log'); ax.set_xlabel('words per message (log scale, code and urls removed)'); ax.set_ylabel('share of kind (percent per bin)')
ax.legend(frameon=False); ax.set_title('Message length, posts and comments')
save_csv(pd.DataFrame(rows), stem)
finish(fig, stem, 'Message length, posts and comments',
       'Histogram on a log axis of words per message for 7,806 posts and 94,341 comments.', len(M))

# ---- h. novelty
stem = 'fig_h_novelty'
cnt = collections.Counter(); first = {}
Ms = M.sort_values('created_at')
for dn, txt in zip(Ms.dayn.values, Ms.clean.values):
    for t in set(txt.split()):
        cnt[t] += 1
        if t not in first:
            first[t] = dn
keep = {t for t, c in cnt.items() if c >= 5}
fd = pd.Series([v for t, v in first.items() if t in keep]).value_counts().reindex(range(61), fill_value=0)
ntok = Ms.groupby('dayn').ntok.sum().reindex(range(61), fill_value=0)
nm = Ms.groupby('dayn').size().reindex(range(61), fill_value=0)
d = pd.DataFrame(dict(day_index=range(61), date=[(START + pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(61)],
                      new_word_types=fd.values, messages=nm.values, tokens=ntok.values))
d['new_types_per_1000_messages'] = d.new_word_types / d.messages * 1000
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(W7, 4.2), sharex=True, gridspec_kw=dict(height_ratios=[1, 1], hspace=0.12))
ax.bar(d.day_index, d.new_word_types, color=MID, width=0.8); ax.set_ylabel('new word types (count)')
ax2.plot(d.day_index, d.new_types_per_1000_messages, color=ACC, lw=1.1); ax2.set_yscale('log')
ax2.set_ylabel('new types per 1,000 messages (log)')
ax2.set_xticks(range(0, 61, 10)); ax2.set_xticklabels([(START + pd.Timedelta(days=i)).strftime('%d %b') for i in range(0, 61, 10)])
ax2.set_xlabel('day (UTC)')
ax.set_title('Word types first seen each day (types used in at least 5 messages overall)')
save_csv(d, stem)
finish(fig, stem, 'Word types first seen each day (types used in at least 5 messages overall)',
       'Bars of the number of word types whose first use falls on each UTC day, and a line of the same count per 1,000 messages that day.', len(keep))

# ---- i. handle by cluster heatmap
stem = 'fig_i_handle_by_cluster'
top = A.handle.value_counts().head(40).index.tolist()
hc = pd.crosstab(A.handle, A.topic).reindex(columns=range(K), fill_value=0).loc[top]
hs = hc.div(hc.sum(axis=1), axis=0)
fig, ax = plt.subplots(figsize=(W7, 6.8))
ax.imshow(hs.values, aspect='auto', cmap=CM, vmin=0, vmax=0.6)
ax.set_yticks(range(len(top))); ax.set_yticklabels([f'{h} ({int(hc.loc[h].sum()):,})' for h in top], fontsize=6)
ax.set_xticks(range(K)); ax.set_xticklabels([str(c) for c in range(K)], fontsize=6)
ax.set_xlabel('cluster id (see topics.csv)'); ax.set_title("Each of the 40 most active handles: share of its messages per cluster (row sums to 100%)")
ax.spines[:].set_visible(False)
h2 = hs.copy(); h2.columns = [f'c{c}' for c in h2.columns]; h2.insert(0, 'messages', hc.sum(axis=1)); h2 = h2.reset_index()
save_csv(h2, stem)
finish(fig, stem, 'Share of each top-40 handle messages per cluster',
       'Heatmap of the 40 handles with most assigned messages against the 18 clusters, cell value the share of that handle messages in the cluster.',
       int(hc.values.sum()))

# ---- j. family by cluster
stem = 'fig_j_family_by_cluster'
fam = A.family.where(~A.family.str.startswith('Claude'), 'Claude (self-declared)')
top_f = ['Claude (self-declared)', 'OpenAI GPT', 'Google Gemini', 'xAI Grok', 'DeepSeek', 'Qwen']
fam = fam.where(fam.isin(top_f), 'other/unknown')
fc = pd.crosstab(A.topic, fam).reindex(range(K), fill_value=0)[top_f + ['other/unknown']]
fs = fc.div(fc.sum(axis=1), axis=0)
fig, ax = plt.subplots(figsize=(W7, 3.8))
fcols = [ACC, '#555555', '#7d7d7d', '#9e9e9e', '#bcbcbc', '#d6d6d6', '#eeeeee']
left = np.zeros(K)
ordc = list(range(K))[::-1]
for f, c in zip(fs.columns, fcols):
    ax.barh(range(K), fs.loc[ordc, f].values * 100, left=left, color=c, height=0.7, edgecolor='white', linewidth=0.3, label=f)
    left += fs.loc[ordc, f].values * 100
ax.set_yticks(range(K)); ax.set_yticklabels([SH[c] for c in ordc]); ax.set_xlim(0, 100); ax.set_xticks(range(0, 101, 20))
ax.set_xlabel('share of cluster messages by self-declared model family (percent)')
ax.legend(frameon=False, ncol=4, fontsize=6, loc='upper center', bbox_to_anchor=(0.45, -0.14))
ax.set_title('Self-declared model family of authors per cluster (labels are unverified)')
o = fs.copy(); o.insert(0, 'messages', fc.sum(axis=1)); o = o.reset_index().rename(columns={'topic': 'cluster'}); o.insert(1, 'label', T.label)
save_csv(o, stem)
finish(fig, stem, 'Self-declared model family of authors per cluster (labels are unverified)',
       'Stacked horizontal bars of the share of each cluster messages by the self-declared model family of the author.', len(A))

# ---- k. 2D map
stem = 'fig_k_map'
Xall = sp.load_npz(os.path.join(CACHE, 'X_all.npz'))
rng = np.random.RandomState(5)
idx = np.where((M.topic >= 0).values & (~M.short).values)[0]
sel = np.sort(rng.choice(idx, 20000, replace=False))
Z = TruncatedSVD(50, random_state=0).fit_transform(Xall[sel])
Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9)
E = TSNE(2, perplexity=40, init='pca', random_state=0, learning_rate='auto', max_iter=750).fit_transform(Z)
lab = M.topic.values[sel]
pal = ['#b5341a', '#2f5d8a', '#6b8e23', '#8a6d3b', '#7a5195', '#2b8a7e', '#c28f00', '#555555', '#d1798a', '#4f6f52', '#9a5b2e', '#3d3d99',
       '#a0522d', '#5f9ea0', '#808000', '#a569bd', '#cd5c5c', '#708090']
fig, ax = plt.subplots(figsize=(W7, 6.2))
for c in range(K):
    m_ = lab == c
    ax.scatter(E[m_, 0], E[m_, 1], s=1.2, color=pal[c], alpha=0.55, linewidths=0, rasterized=True)
cent = np.array([np.median(E[lab == c], axis=0) for c in range(K)])
for c in range(K):
    ax.text(cent[c, 0], cent[c, 1], str(c), fontsize=8, ha='center', va='center', color='black', weight='bold',
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.75))
ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel('t-SNE dimension 1 (arbitrary units)'); ax.set_ylabel('t-SNE dimension 2 (arbitrary units)')
for s_ in ('left', 'bottom'):
    ax.spines[s_].set_visible(False)
ax.set_title('Map of 20,000 messages (SVD to 50 dimensions, then t-SNE), colour = cluster; numbers = cluster ids')
ax.text(1.01, 1.0, '\n'.join(SH[c] for c in range(K)), transform=ax.transAxes, fontsize=5.5, va='top')
mp = pd.DataFrame(dict(uid=M.uid.values[sel], tsne1=E[:, 0], tsne2=E[:, 1], cluster=lab))
save_csv(mp, stem)
finish(fig, stem, 'Map of 20,000 messages (SVD to 50 dimensions, then t-SNE), colour = cluster',
       'Scatter of a random sample of 20,000 messages with at least 20 words in a two-dimensional t-SNE embedding of their TF-IDF vectors, coloured by cluster.', 20000)

# ---- l. top terms small multiples
stem = 'fig_l_top_terms'
TT = pd.read_csv(os.path.join(OUT, 'topic_terms.csv'))
fig, axes = plt.subplots(6, 3, figsize=(W7, 9.2))
for c, ax in enumerate(axes.ravel()):
    d = TT[(TT.cluster == c) & (TT['rank'] <= 8)].iloc[::-1]
    ax.barh(range(len(d)), d.weight, color=MID, height=0.7)
    ax.set_yticks(range(len(d))); ax.set_yticklabels(d.term, fontsize=6)
    ax.set_xticks([]); ax.spines['bottom'].set_visible(False)
    ax.set_title(SH[c], fontsize=6.5, color=INK)
fig.supxlabel('NMF term weight (bars scaled within each cluster)', fontsize=7)
fig.tight_layout()
save_csv(TT[TT['rank'] <= 8], stem)
finish(fig, stem, 'Top 8 NMF terms per cluster',
       'Small multiples of the eight highest-weighted terms of each of 18 clusters.', int(TT[TT['rank'] <= 8].shape[0]))

# ---- m. k selection
stem = 'fig_m_k_selection'
ks = pd.read_csv(os.path.join(OUT, 'k_selection.csv'))
fig, ax = plt.subplots(figsize=(W7, 2.8))
ax.plot(ks.k, ks.npmi_mean, color=ACC, marker='o', ms=3, lw=1); ax.set_ylabel('mean NPMI coherence (top 10 terms)', color=ACC)
ax.set_xlabel('k (number of NMF topics)'); ax2 = ax.twinx(); ax2.plot(ks.k, ks.stab_mean_cos, color=INK, marker='s', ms=3, lw=1)
ax2.set_ylabel('mean matched term-vector cosine across 3 runs', color=INK); ax2.spines['right'].set_visible(True)
ax.axvline(int(T.shape[0]), color=LIGHT, lw=0.8); ax.set_title('Coherence and stability by k (chosen k marked)')
save_csv(ks, stem)
finish(fig, stem, 'Coherence and stability by k (chosen k marked)',
       'Lines of mean NPMI coherence and mean matched cosine between independent NMF runs for k from 12 to 30.', len(ks))

# ---- n. growth after day 30
stem = 'fig_n_growth'
d = G.sort_values('ratio_day30_60_over_day0_29')
fig, ax = plt.subplots(figsize=(W7, 3.6))
y = np.arange(len(d))
ax.barh(y, d.ratio_day30_60_over_day0_29, color=[ACC if v > 1.1 else MID for v in d.ratio_day30_60_over_day0_29], height=0.65)
ax.axvline(1, color=INK, lw=0.6)
for yi, v in enumerate(d.ratio_day30_60_over_day0_29):
    ax.text(v + 0.05, yi, f'{v:.2f}', va='center', fontsize=6)
ax.set_yticks(y); ax.set_yticklabels([SH[c] for c in d.cluster])
ax.set_xlabel('mean daily share, days 30 to 60, divided by days 0 to 29'); ax.set_title('Change in cluster share after day 30 (red above 1.1)')
save_csv(d[['cluster', 'label', 'mean_daily_share_day0_29', 'mean_daily_share_day30_60', 'ratio_day30_60_over_day0_29']], stem)
finish(fig, stem, 'Change in cluster share after day 30 (red above 1.1)',
       'Bars of the ratio of mean daily share in days 30 to 60 to mean daily share in days 0 to 29 per cluster.', len(A))

json.dump({r['file']: {k: v for k, v in r.items() if k != 'file'} for r in reg}, open(os.path.join(OUT, 'figures.json'), 'w'), indent=1)
print(len(reg), 'figures')
