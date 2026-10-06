"""Figures (SVG) and their data CSVs, plus figures.json. Reads tables/*.csv written by analyze_types.py."""
import json, sys, textwrap
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from load import HERE
import themes as TH

TB = f'{HERE}/tables'; FG = f'{HERE}/figures'
INK = '#333333'; MID = '#8a8a8a'; LIGHT = '#cfcfcf'; FAINT = '#ececec'; ACC = '#1f6f8b'; ACC_L = '#a9cbd8'
GREYS = ['#4d4d4d', '#7a7a7a', '#a0a0a0', '#c2c2c2', '#dcdcdc', '#ececec']
plt.rcParams.update({'svg.fonttype': 'none', 'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
                     'font.size': 7.5, 'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
                     'axes.edgecolor': LIGHT, 'axes.linewidth': 0.6, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
                     'savefig.facecolor': 'white', 'axes.spines.top': False, 'axes.spines.right': False,
                     'xtick.major.size': 2.5, 'ytick.major.size': 2.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5})
W = 7.0
LOG = []


def finish(fig, stem, title, desc, data, source, n):
    fig.savefig(f'{FG}/{stem}.svg', format='svg', bbox_inches='tight', pad_inches=0.12)
    import os
    if os.environ.get('FIG_PNG_DIR'): fig.savefig(os.environ['FIG_PNG_DIR'] + f'/{stem}.png', dpi=110, bbox_inches='tight', pad_inches=0.12)
    plt.close(fig)
    data.to_csv(f'{FG}/{stem}.csv', index=False)
    LOG.append({'file': f'figures/{stem}.svg', 'title': title, 'description': desc, 'source_csv': source, 'data_csv': f'figures/{stem}.csv', 'n': int(n)})


def lab(t):
    return t.replace('_', ' ')

C = pd.read_csv(f'{TB}/type_counts.csv')
order = C.type.tolist()
prec = pd.read_csv(f'{HERE}/precision_v2.csv').set_index('primary').precision.to_dict()
prec1 = pd.read_csv(f'{HERE}/precision_v1.csv').set_index('primary').precision.to_dict()
for t in ('placeholder', 'offer_listing', 'money_payment'): prec[t] = prec1[t]
N = int(C.n.sum())

# 1 type share bar
d = C[['type', 'n', 'share_pct']].copy(); d['precision_checked'] = d.type.map(prec)
fig, ax = plt.subplots(figsize=(W, 4.2))
y = np.arange(len(d))[::-1]
cols = [ACC if p >= 0.7 else LIGHT for p in d.precision_checked]
ax.barh(y, d.share_pct, color=cols, height=0.7)
for yi, (s, n_, p) in zip(y, zip(d.share_pct, d.n, d.precision_checked)):
    ax.text(s + 0.5, yi, f'{s:.1f}%  (n={n_:,}; read precision {p:.2f})', va='center', fontsize=6.5)
ax.set_yticks(y); ax.set_yticklabels([lab(t) for t in d.type]); ax.set_xlim(0, 75)
ax.set_xlabel('share of all messages (%)'); ax.tick_params(axis='y', length=0)
ax.set_title(f'Share of messages by primary type, {N:,} messages with text', loc='left', fontsize=8.5)
fig.text(0.01, -0.02, 'Blue bars: read precision of at least 0.7 in the 40-message check. Grey bars: below 0.7, so the rule label is a loose upper bound.', fontsize=6.5, color=MID)
finish(fig, 'fig01_type_share_bar', 'Share of messages by primary type', 'Horizontal bars of the share of all posts and comments assigned to each primary type by the final rules, with the read precision of each type.', d, 'tables/type_counts.csv', N)

# 2 weekly stacked
ws = pd.read_csv(f'{TB}/type_by_week_share.csv'); wc = pd.read_csv(f'{TB}/type_by_week_counts.csv')
types_top = ['analysis_argument', 'claim_evidence', 'agreement_ack', 'measurement_receipt', 'money_payment', 'correction_self']
d = ws[['week_start_utc'] + types_top].copy(); d['all_other_types'] = 1 - d[types_top].sum(axis=1)
d['messages_in_week'] = wc.total
d.iloc[:, 1:8] = (d.iloc[:, 1:8] * 100).round(2)
fig, ax = plt.subplots(figsize=(W, 3.6))
bottom = np.zeros(len(d)); cols = [GREYS[3], ACC, GREYS[1], GREYS[2], GREYS[4], GREYS[0], FAINT]
names = types_top + ['all_other_types']
for nme, c in zip(names, cols):
    ax.bar(range(len(d)), d[nme], bottom=bottom, color=c, width=0.8, edgecolor='white', linewidth=0.5)
    mid = bottom + d[nme] / 2
    if d[nme].iloc[-1] > 3: ax.text(len(d) - 0.55, mid.iloc[-1], lab(nme), va='center', fontsize=6.5)
    bottom += d[nme].values
ax.set_xticks(range(len(d))); ax.set_xticklabels([f'{s[5:]}' for s in d.week_start_utc], fontsize=6.5)
ax.set_xlabel('first day of 7-day block since launch (month-day, UTC; last block has 3 days)'); ax.set_ylabel('share of messages in block (%)')
ax.set_xlim(-0.6, len(d) + 1.9); ax.set_ylim(0, 100)
ax.set_title('Share of messages by primary type, per 7-day block', loc='left', fontsize=8.5)
finish(fig, 'fig02_type_share_per_week_stacked', 'Share of messages by primary type, per 7-day block', 'Stacked bars of the weekly share of the six largest types and all other types combined, nine 7-day blocks from 5 Aug to 5 Oct 2026.', d, 'tables/type_by_week_share.csv', N)

# 3 hour heatmap
H = pd.read_csv(f'{TB}/type_by_hour_share_within_type.csv').set_index('primary').loc[order] * 100
fig, ax = plt.subplots(figsize=(W, 5.2))
im = ax.imshow(H.values, aspect='auto', cmap=matplotlib.colors.LinearSegmentedColormap.from_list('a', ['#ffffff', ACC]), vmin=0, vmax=H.values.max())
ax.set_yticks(range(len(H))); ax.set_yticklabels([lab(t) for t in H.index]); ax.set_xticks(range(0, 24, 2)); ax.set_xticklabels(range(0, 24, 2))
ax.set_xlabel('hour of day (UTC)'); ax.tick_params(length=0)
for sp in ax.spines.values(): sp.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02); cb.set_label("share of the type's messages in that hour (%)", fontsize=6.5); cb.outline.set_visible(False); cb.ax.tick_params(labelsize=6)
ax.set_title('Messages by hour of day and primary type', loc='left', fontsize=8.5)
finish(fig, 'fig03_type_by_hour_heatmap', 'Messages by hour of day and primary type', 'Heatmap of the share of each type\'s messages posted in each UTC hour.', H.reset_index().rename(columns={'primary': 'type'}).round(3), 'tables/type_by_hour_share_within_type.csv', N)

# 4 posts vs comments
d = C[['type', 'share_of_posts_pct', 'share_of_comments_pct', 'posts', 'comments']].copy()
fig, ax = plt.subplots(figsize=(W, 4.4)); y = np.arange(len(d))[::-1]
ax.barh(y + 0.19, d.share_of_posts_pct, height=0.36, color=ACC); ax.barh(y - 0.19, d.share_of_comments_pct, height=0.36, color=GREYS[2])
for yi, p_, c_ in zip(y, d.share_of_posts_pct, d.share_of_comments_pct):
    ax.text(p_ + 0.6, yi + 0.19, f'{p_:.1f}', va='center', fontsize=6, color=ACC); ax.text(c_ + 0.6, yi - 0.19, f'{c_:.1f}', va='center', fontsize=6, color=MID)
ax.set_yticks(y); ax.set_yticklabels([lab(t) for t in d.type]); ax.tick_params(axis='y', length=0); ax.set_xlim(0, 62)
ax.set_xlabel('share of that kind of message (%)')
ax.text(40, y[2], 'posts (n=7,806)', color=ACC, fontsize=7); ax.text(40, y[3] - 0.1, 'comments (n=94,341)', color=MID, fontsize=7)
ax.set_title('Type mix of posts and of comments', loc='left', fontsize=8.5)
finish(fig, 'fig04_posts_vs_comments_type_mix', 'Type mix of posts and of comments', 'Paired bars of the share of posts and the share of comments in each primary type.', d, 'tables/type_counts.csv', N)

# 5 length boxplots
L = pd.read_csv(f'{TB}/length_by_type.csv').set_index('primary').loc[order]
stats = [{'med': r['median'], 'q1': r.p25, 'q3': r.p75, 'whislo': r.p10, 'whishi': r.p90, 'fliers': []} for _, r in L.iterrows()]
fig, ax = plt.subplots(figsize=(W, 4.6))
bp = ax.bxp(stats, positions=np.arange(len(L))[::-1], orientation='horizontal', showfliers=False, widths=0.6, patch_artist=True,
            boxprops=dict(facecolor=ACC_L, edgecolor=ACC, linewidth=0.6), medianprops=dict(color=INK, linewidth=1), whiskerprops=dict(color=MID, linewidth=0.6), capprops=dict(color=MID, linewidth=0.6))
ax.set_xscale('log'); ax.set_yticks(np.arange(len(L))[::-1]); ax.set_yticklabels([lab(t) for t in L.index]); ax.tick_params(axis='y', length=0)
ax.set_xlabel('length in characters (log scale; box = 25th to 75th percentile, whiskers = 10th to 90th, line = median)')
ax.set_title('Message length by primary type', loc='left', fontsize=8.5)
finish(fig, 'fig05_length_boxplots_by_type', 'Message length by primary type', 'Horizontal box plots of message length in characters for each primary type, from the 10th to the 90th percentile.', L.reset_index().rename(columns={'primary': 'type'}), 'tables/length_by_type.csv', N)

# 6 answered within 1h
R = pd.read_csv(f'{TB}/reply_behaviour_by_type.csv').sort_values('answered_within_1h_pct', ascending=False)
fig, ax = plt.subplots(figsize=(W, 4.2)); y = np.arange(len(R))[::-1]
mean_all = (R.answered_within_1h_pct * R.n).sum() / R.n.sum()
ax.barh(y, R.answered_within_1h_pct, color=[ACC if v > mean_all else LIGHT for v in R.answered_within_1h_pct], height=0.7)
for yi, v, n_ in zip(y, R.answered_within_1h_pct, R.n): ax.text(v + 0.4, yi, f'{v:.1f}%  (n={n_:,})', va='center', fontsize=6.5)
ax.axvline(mean_all, color=MID, linewidth=0.6, linestyle=(0, (3, 3))); ax.text(mean_all + 0.3, y[0] + 0.55, f'all messages {mean_all:.1f}%', fontsize=6.5, color=MID)
ax.set_yticks(y); ax.set_yticklabels([lab(t) for t in R.primary]); ax.tick_params(axis='y', length=0); ax.set_xlim(0, 36)
ax.set_xlabel('messages with a direct reply by another handle within 1 hour (%)')
ax.set_title('Answered within one hour, by primary type', loc='left', fontsize=8.5)
finish(fig, 'fig06_answered_within_1h_by_type', 'Answered within one hour, by primary type', 'Bars of the share of messages that received a direct reply from another handle within one hour, excluding messages from the last hour of the archive.', R.rename(columns={'primary': 'type'}), 'tables/reply_behaviour_by_type.csv', int(R.n.sum()))

# 7 transition matrix (lift)
mat = pd.read_csv(f'{TB}/transition_counts.csv').set_index('parent_type'); lift = pd.read_csv(f'{TB}/transition_lift.csv').set_index('parent_type'); rs = pd.read_csv(f'{TB}/transition_row_share.csv').set_index('parent_type')
ro = [t for t in order if t in mat.index]; co = [t for t in order if t in mat.columns]
long = []
for a in ro:
    for b in co: long.append({'parent_type': a, 'reply_type': b, 'count': int(mat.loc[a, b]), 'row_share': rs.loc[a, b], 'lift': lift.loc[a, b]})
long = pd.DataFrame(long)
fig, ax = plt.subplots(figsize=(W, 6.3))
V = lift.loc[ro, co].values.astype(float)
V = np.where(mat.loc[ro, co].values < 10, np.nan, V)
im = ax.imshow(V, aspect='auto', cmap=matplotlib.colors.LinearSegmentedColormap.from_list('a', ['#ffffff', ACC]), vmin=0, vmax=3)
for i in range(V.shape[0]):
    for j in range(V.shape[1]):
        if V[i, j] >= 1.6 and mat.loc[ro[i], co[j]] >= 20: ax.text(j, i, f'{V[i, j]:.1f}', ha='center', va='center', fontsize=5.5, color='white' if V[i, j] > 2 else INK)
ax.set_xticks(range(len(co))); ax.set_xticklabels([lab(t) for t in co], rotation=60, ha='right', fontsize=6); ax.set_yticks(range(len(ro))); ax.set_yticklabels([lab(t) for t in ro], fontsize=6.5)
ax.set_xlabel('type of the reply'); ax.set_ylabel('type of the message replied to'); ax.tick_params(length=0)
for sp in ax.spines.values(): sp.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label('observed count divided by count expected from the type totals', fontsize=6.5); cb.outline.set_visible(False); cb.ax.tick_params(labelsize=6)
ax.set_title('Reply type given parent type, observed over expected', loc='left', fontsize=8.5)
finish(fig, 'fig07_type_transition_matrix', 'Reply type given parent type, observed over expected', 'Heatmap of observed over expected counts for each parent type and reply type; cells with fewer than 10 replies are blank and values of 1.6 or more are printed.', long, 'tables/transition_counts.csv', int(mat.values.sum()))

# 8 theme counts
TC = pd.read_csv(f'{TB}/theme_counts.csv'); TP = pd.read_csv(f'{HERE}/theme_precision.csv').set_index('theme')
d = TC[['theme', 'messages', 'share_pct']].copy(); d['precision_strict'] = d.theme.map(TP.precision_strict); d['precision_loose'] = d.theme.map(TP.precision_loose)
fig, ax = plt.subplots(figsize=(W, 3.6)); y = np.arange(len(d))[::-1]
ax.barh(y, d.messages, color=[ACC if p >= 0.5 else LIGHT for p in d.precision_strict], height=0.7)
for yi, r in zip(y, d.itertuples()): ax.text(r.messages + 600, yi, f'{r.messages:,}  ({r.share_pct:.1f}%)  read precision {r.precision_strict:.2f} strict, {r.precision_loose:.2f} loose', va='center', fontsize=6.3)
ax.set_yticks(y); ax.set_yticklabels([lab(t) for t in d.theme]); ax.tick_params(axis='y', length=0); ax.set_xlim(0, 135000); ax.set_xlabel('messages matching the word list')
ax.set_title('Messages per theme, word-list matches', loc='left', fontsize=8.5)
fig.text(0.01, -0.03, 'Blue: strict read precision of 0.5 or more. Grey: below 0.5. A message can match several themes.', fontsize=6.5, color=MID)
finish(fig, 'fig08_theme_counts_bar', 'Messages per theme, word-list matches', 'Bars of the number of messages matching each theme word list, with the precision from a 30-message read per theme.', d, 'tables/theme_counts.csv', N)

# 9 theme share per week lines
tw = pd.read_csv(f'{TB}/theme_by_week_share.csv'); names = list(TH.THEMES)
d = tw[['week_start_utc'] + names].copy(); d.iloc[:, 1:] = (d.iloc[:, 1:] * 100).round(3)
fig, ax = plt.subplots(figsize=(W, 4.2))
ends = {n_: d[n_].iloc[-1] for n_ in names}
pos = {}
srt = sorted(names, key=lambda n_: ends[n_])
lp = [np.log10(ends[n_]) for n_ in srt]
for i in range(1, len(lp)):
    if lp[i] - lp[i - 1] < 0.075: lp[i] = lp[i - 1] + 0.075
for n_, v in zip(srt, lp): pos[n_] = 10 ** v
for nme in names:
    focal = nme in ('continuity_memory', 'money_usdc', 'deception_false_green')
    ax.plot(range(len(d)), d[nme], color=ACC if focal else MID, linewidth=1.3 if focal else 0.8, alpha=1 if focal else 0.8)
    ax.text(len(d) - 0.85, pos[nme], lab(nme), va='center', fontsize=6.2, color=ACC if focal else MID)
ax.set_yscale('log'); ax.set_xticks(range(len(d))); ax.set_xticklabels([s[5:] for s in d.week_start_utc], fontsize=6.5); ax.set_xlim(-0.3, len(d) + 2.4)
ax.set_xlabel('first day of 7-day block since launch (month-day, UTC)'); ax.set_ylabel('share of messages in block (%, log scale)')
ax.set_title('Theme share of messages per 7-day block', loc='left', fontsize=8.5)
finish(fig, 'fig09_theme_share_per_week_lines', 'Theme share of messages per 7-day block', 'Lines of the weekly share of messages matching each theme word list, on a log axis.', d, 'tables/theme_by_week_share.csv', N)

# 10 theme by type stacked
tt = pd.read_csv(f'{TB}/theme_by_type_share.csv', index_col=0); tt.index.name = 'theme'
keep = ['analysis_argument', 'claim_evidence', 'agreement_ack', 'measurement_receipt', 'money_payment', 'correction_self']
d = tt[keep].copy(); d['all_other_types'] = 1 - d.sum(axis=1); d = d * 100
fig, ax = plt.subplots(figsize=(W, 3.8)); y = np.arange(len(d))[::-1]; left = np.zeros(len(d)); cols = [GREYS[3], ACC, GREYS[1], GREYS[2], GREYS[4], GREYS[0], FAINT]
for nme, c in zip(keep + ['all_other_types'], cols):
    ax.barh(y, d[nme], left=left, color=c, height=0.72, edgecolor='white', linewidth=0.4)
    for yi, l_, v in zip(y, left, d[nme]):
        if v >= 9: ax.text(l_ + v / 2, yi, f'{v:.0f}', ha='center', va='center', fontsize=6, color='white' if c in (GREYS[0], GREYS[1], ACC) else INK)
    left += d[nme].values
ax.set_yticks(y); ax.set_yticklabels([lab(t) for t in d.index]); ax.tick_params(axis='y', length=0); ax.set_xlim(0, 100); ax.set_xlabel('share of the theme\'s messages (%)')
x0 = 0
for nme, c in zip(keep + ['all_other_types'], cols):
    ax.add_patch(plt.Rectangle((x0, len(d) - 0.1), 1.3, 0.28, color=c, clip_on=False)); ax.text(x0 + 2, len(d) + 0.04, lab(nme).replace('analysis argument', 'analysis').replace('measurement receipt', 'measurement').replace('correction self', 'correction').replace('claim evidence', 'claim'), fontsize=5.8, va='center'); x0 += 14.2
ax.set_title('Type mix inside each theme', loc='left', fontsize=8.5, pad=14)
finish(fig, 'fig10_theme_by_type_stacked', 'Type mix inside each theme', 'Stacked bars of the primary-type mix of the messages matching each theme.', d.reset_index(), 'tables/theme_by_type_share.csv', N)

# 11 to 15 daily series
DS = pd.read_csv(f'{TB}/daily_series.csv')
def daily(stem, col, title, ylabel, desc):
    d = DS[['date', 'messages', col]].copy(); d['share_pct'] = (d[col] * 100).round(3); d['mean_7d_pct'] = d.share_pct.rolling(7, center=True, min_periods=4).mean().round(3)
    fig, ax = plt.subplots(figsize=(W, 2.7))
    ax.plot(range(len(d)), d.share_pct, color=LIGHT, linewidth=0.7, marker='o', markersize=1.8); ax.plot(range(len(d)), d.mean_7d_pct, color=ACC, linewidth=1.5)
    ax.text(len(d) - 0.5, d.mean_7d_pct.dropna().iloc[-1], '7-day mean', color=ACC, fontsize=6.5, va='center'); ax.text(len(d) - 0.5, d.share_pct.iloc[-1] + d.share_pct.max() * 0.05, 'daily', color=MID, fontsize=6.5)
    ticks = list(range(0, len(d), 7)); ax.set_xticks(ticks); ax.set_xticklabels([d.date.iloc[i][5:] for i in ticks], fontsize=6.5); ax.set_xlim(-1, len(d) + 6)
    ax.set_xlabel('day (month-day, UTC)'); ax.set_ylabel(ylabel); ax.set_ylim(0, d.share_pct.max() * 1.15); ax.set_title(title, loc='left', fontsize=8.5)
    finish(fig, stem, title, desc, d.drop(columns=[col]), 'tables/daily_series.csv', int(d.messages.sum()))
daily('fig11_question_share_per_day', 'question', 'Question share of messages per day', 'share of that day\'s messages (%)', 'Daily share of messages whose primary type is question, with a 7-day centred mean.')
daily('fig12_correction_share_per_day', 'correction_self', 'Self-correction share of messages per day', 'share of that day\'s messages (%)', 'Daily share of messages whose primary type is correction of the author\'s own earlier message, with a 7-day centred mean.')
daily('fig13_fiction_share_per_day', 'fiction_poetry_art', 'Fiction, poetry and art share of messages per day', 'share of that day\'s messages (%)', 'Daily share of messages whose primary type is fiction, poetry or art, with a 7-day centred mean.')
daily('fig14_heartbeat_share_per_day', 'heartbeat_status', 'Status and heartbeat share of messages per day', 'share of that day\'s messages (%)', 'Daily share of messages whose primary type is status or heartbeat, with a 7-day centred mean.')
daily('fig15_hash_or_table_share_per_day', 'hash_or_table', 'Messages with a hash or a table, share per day', 'share of that day\'s messages (%)', 'Daily share of messages that contain a hex string of 16 or more characters or a markdown table, with a 7-day centred mean.')

# 16 family heatmap
FS = pd.read_csv(f'{TB}/family_type_share.csv').set_index('family'); fo = pd.read_csv(f'{TB}/family_overview.csv').set_index('family')
fam = [f for f in fo.index if f in FS.index and f != 'other/unknown'][:10]
cols_ = ['analysis_argument', 'claim_evidence', 'agreement_ack', 'measurement_receipt', 'money_payment', 'correction_self', 'question', 'disagreement', 'spam_promo_token', 'noise_test']
d = (FS.loc[fam, cols_] * 100).round(2); d.insert(0, 'messages', FS.loc[fam, 'messages'])
fig, ax = plt.subplots(figsize=(W, 3.8)); V = d[cols_].values
im = ax.imshow(V, aspect='auto', cmap=matplotlib.colors.LinearSegmentedColormap.from_list('a', ['#ffffff', ACC]), vmin=0, vmax=40)
for i in range(V.shape[0]):
    for j in range(V.shape[1]): ax.text(j, i, f'{V[i, j]:.1f}', ha='center', va='center', fontsize=6, color='white' if V[i, j] > 24 else INK)
ax.set_xticks(range(len(cols_))); ax.set_xticklabels([lab(t) for t in cols_], rotation=40, ha='right', fontsize=6.5)
ax.set_yticks(range(len(fam))); ax.set_yticklabels([f'{f} (n={int(m):,})' for f, m in zip(fam, d.messages)], fontsize=6.5); ax.tick_params(length=0)
for sp in ax.spines.values(): sp.set_visible(False)
ax.set_title('Primary type share by self-declared model family', loc='left', fontsize=8.5)
ax.set_xlabel('percent of the family\'s messages; family is the label the citizen declared, not verified', fontsize=6.8)
finish(fig, 'fig16_model_family_type_share', 'Primary type share by self-declared model family', 'Heatmap of the percent of each self-declared model family\'s messages in ten primary types.', d.reset_index(), 'tables/family_type_share.csv', int(d.messages.sum()))

# 17 precision v1 vs v2
rows = []
for t in order:
    rows.append({'type': t, 'precision_v1': prec1.get(t), 'precision_v2': pd.read_csv(f'{HERE}/precision_v2.csv').set_index('primary').precision.get(t, np.nan)})
d = pd.DataFrame(rows)
fig, ax = plt.subplots(figsize=(W, 4.2)); y = np.arange(len(d))[::-1]
ax.axvline(0.7, color=MID, linewidth=0.6, linestyle=(0, (3, 3))); ax.text(0.705, y[0] + 0.7, '0.7', fontsize=6.5, color=MID)
for yi, r in zip(y, d.itertuples()):
    if not np.isnan(r.precision_v2): ax.plot([r.precision_v1, r.precision_v2], [yi, yi], color=LIGHT, linewidth=1)
ax.scatter(d.precision_v1, y, color=GREYS[2], s=18, zorder=3); ax.scatter(d.precision_v2, y, color=ACC, s=18, zorder=3)
ax.set_yticks(y); ax.set_yticklabels([lab(t) for t in d.type]); ax.tick_params(axis='y', length=0); ax.set_xlim(0, 1.05); ax.set_xlabel('share of 40 read messages judged correctly typed')
ax.text(0.02, y[-1] - 1.1, 'grey: rules v1', color=GREYS[1], fontsize=6.5); ax.text(0.22, y[-1] - 1.1, 'blue: rules v2 (revised once)', color=ACC, fontsize=6.5)
ax.set_title('Read precision by primary type, rules v1 and v2', loc='left', fontsize=8.5)
finish(fig, 'fig17_precision_by_type', 'Read precision by primary type, rules v1 and v2', 'Dot plot of the share of 40 read messages per type judged correct under the first and the revised rules.', d, 'precision_v1.csv and precision_v2.csv', 40 * len(d))

# 18 estimated vs rule share
E = pd.read_csv(f'{TB}/estimated_true_share.csv').sort_values('estimated_true_share_pct', ascending=False)
fig, ax = plt.subplots(figsize=(W, 4.2)); y = np.arange(len(E))[::-1]
ax.barh(y + 0.19, E.rule_label_share_pct, height=0.36, color=LIGHT); ax.barh(y - 0.19, E.estimated_true_share_pct, height=0.36, color=ACC)
for yi, a, b in zip(y, E.rule_label_share_pct, E.estimated_true_share_pct): ax.text(max(a, b) + 0.6, yi, f'{a:.1f} to {b:.1f}', va='center', fontsize=6)
ax.set_yticks(y); ax.set_yticklabels([lab(t) for t in E.type]); ax.tick_params(axis='y', length=0); ax.set_xlim(0, 62); ax.set_xlabel('share of messages (%)')
ax.text(33, y[3], 'grey: rule label', color=GREYS[1], fontsize=7); ax.text(33, y[4], 'blue: estimate after the read check', color=ACC, fontsize=7)
ax.set_title('Rule-label share and estimate corrected with the read sample', loc='left', fontsize=8.5)
finish(fig, 'fig18_rule_vs_estimated_share', 'Rule-label share and estimate corrected with the read sample', 'Paired bars comparing each type\'s rule-label share with the share estimated by reweighting the 40-message read samples by their judged types.', E, 'tables/estimated_true_share.csv', N)

json.dump(LOG, open(f'{HERE}/figures.json', 'w'), indent=1, ensure_ascii=False)
print(len(LOG), 'figures')
