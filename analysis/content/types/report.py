"""Write validation.csv, confusion tables and REPORT.md from the tables. No analysis happens here beyond table assembly."""
import sys, collections
import numpy as np, pandas as pd
sys.path.insert(0, '.')
from load import HERE
import themes as TH

TB = f'{HERE}/tables'
def md(df, fmt='{:.1f}', maxrows=None):
    df = df.copy()
    if maxrows: df = df.head(maxrows)
    cols = list(df.columns)
    out = ['| ' + ' | '.join(str(c) for c in cols) + ' |', '|' + '---|' * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)) and not pd.isna(v):
                v = fmt.format(v) if abs(v) < 1e6 and (v != int(v) or '.' in fmt) else f'{int(v):,}'
            elif isinstance(v, (int, np.integer)): v = f'{v:,}'
            elif pd.isna(v): v = ''
            cells.append(str(v).replace('|', '/').replace('\n', ' '))
        out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out)

# ---- validation.csv and confusion
v1 = pd.read_csv(f'{HERE}/validation_v1.csv'); v1['rules_version'] = 'v1'
v2 = pd.read_csv(f'{HERE}/validation_v2.csv'); v2['rules_version'] = 'v2'
V = pd.concat([v1, v2])[['rules_version', 'primary', 'idx', 'kind', 'id', 'handle', 'secondary', 'verdict', 'judged_type']]
V.to_csv(f'{HERE}/validation.csv', index=False)
for ver, v in (('v1', v1), ('v2', v2)):
    pd.crosstab(v.primary, v.judged_type).to_csv(f'{HERE}/confusion_{ver}.csv')
p1 = pd.read_csv(f'{HERE}/precision_v1.csv'); p2 = pd.read_csv(f'{HERE}/precision_v2.csv')
P = p1.merge(p2, on='primary', how='left', suffixes=('_v1', '_v2'))
P['final_precision'] = P.precision_v2.fillna(P.precision_v1)
P['final_source'] = np.where(P.precision_v2.notna(), 'v2 sample', 'v1 sample (rules unchanged)')
P['n_final'] = 40
Pt = P[['primary', 'precision_v1', 'precision_v2', 'final_source']].copy()
Pt['correct_v1_of_40'] = P.correct_v1; Pt['correct_v2_of_40'] = P.correct_v2.astype('Int64')
Pt['v2_main_confusions (judged type, count)'] = P['main_confusions (judged type, count)_v2'].fillna('')
Pt['v1_main_confusions (judged type, count)'] = P['main_confusions (judged type, count)_v1'].fillna('')
Pt = Pt[['primary', 'correct_v1_of_40', 'precision_v1', 'correct_v2_of_40', 'precision_v2', 'final_source', 'v1_main_confusions (judged type, count)', 'v2_main_confusions (judged type, count)']]

C = pd.read_csv(f'{TB}/type_counts.csv'); SEC = pd.read_csv(f'{TB}/secondary_counts.csv')
E = pd.read_csv(f'{TB}/estimated_true_share.csv')
G = pd.read_csv(f'{TB}/trend_after_day30.csv'); LEN = pd.read_csv(f'{TB}/length_by_type.csv'); RB = pd.read_csv(f'{TB}/reply_behaviour_by_type.csv')
A = pd.read_csv(f'{TB}/transition_asymmetries.csv'); lift = pd.read_csv(f'{TB}/transition_lift.csv').set_index('parent_type'); cnt = pd.read_csv(f'{TB}/transition_counts.csv').set_index('parent_type')
FS = pd.read_csv(f'{TB}/family_type_share.csv'); FO = pd.read_csv(f'{TB}/family_overview.csv')
TC = pd.read_csv(f'{TB}/theme_counts.csv'); TP = pd.read_csv(f'{HERE}/theme_precision.csv')
TT = pd.read_csv(f'{TB}/theme_by_type_counts.csv', index_col=0); TTs = pd.read_csv(f'{TB}/theme_by_type_share.csv', index_col=0)
TW = pd.read_csv(f'{TB}/theme_by_week_share.csv'); TTR = pd.read_csv(f'{TB}/theme_trend_after_day30.csv')
WC = pd.read_csv(f'{TB}/type_by_week_counts.csv'); WS = pd.read_csv(f'{TB}/type_by_week_share.csv')
H = pd.read_csv(f'{TB}/type_by_hour_share_within_type.csv').set_index('primary')
N = int(C.n.sum())

L = []
w = L.append
w('# Message types and themes on 1f916.ai\n')
w('## Method\n')
w(f'The archive holds 7,806 posts and 94,563 comments from 2026-08-05 to 2026-10-05 (data/posts, data/comments). {94563 - int(C.comments.sum())} comments are rows without text or timestamp and are left out ("no_content"). The statistics cover {N:,} messages ({int(C.posts.sum()):,} posts, {int(C.comments.sum()):,} comments). Posts are scored on title plus body, comments on body. Every message gets one primary type and up to two secondary types from the regex and structure rules in rules.md. Rule hits are stored per message in types_all.csv.gz.\n')
w('Validation reads 40 random messages per primary type (up to 12 posts, the rest comments) and records for each whether the primary type is an acceptable single label. The read covers the first 300 to 400 characters of each message plus the rule hits, not the full text of long messages. One reader judged all samples. Precision is correct divided by 40 and has a sampling error of about 0.15 per type.\n')
w('Themes use the word lists in themes_wordlists.md. A message matches a theme with one strong term or two distinct weak terms. Each theme was checked by reading 30 matches. Strict precision counts matches that discuss the theme in substance. Loose precision also counts matches that use the term in passing or in the forum\'s technical sense.\n')
w('Model families come from the self-declared model label of the author and are not verified. Handles name accounts, not single minds.\n')
w('## Rules hash\n')
w('Hashes were written to README.md before the validation samples were drawn.\n')
w('| item | sha256 |\n|---|---|')
def hashrows(path, label):
    for line in open(path):
        parts = line.strip().split()
        name = parts[0] if not parts[0].startswith('combined') else 'combined'
        w(f'| {label} {name} | {parts[-1]} |')
hashrows(f'{HERE}/rules_v1.sha256', 'rules v1')
hashrows(f'{HERE}/rules_v2.sha256', 'rules v2')
hashrows(f'{HERE}/themes_t1.sha256', 'themes t1')
w('\n## Validation precision by type\n')
w('v1 is the first rule set. v2 is the single revision made after reading the v1 sample. v2 was re-read with a new random sample for every type except placeholder, offer_listing and money_payment, whose rules did not change. A type counts as reliable at 0.7 or above.\n')
w(md(Pt.round(3).astype(object), '{:.3f}'))
rel = Pt.assign(final=Pt.precision_v2.fillna(Pt.precision_v1)); ok = rel[rel.final >= 0.7].primary.tolist(); bad = rel[rel.final < 0.7].primary.tolist()
w(f'\nTypes at 0.7 or above in the final rules: {", ".join(ok)}. Types below 0.7: {", ".join(bad)}. Counts for the types below 0.7 are loose upper bounds of the rule label.\n')
w('## Counts by primary type\n')
t = C[['type', 'n', 'share_pct', 'posts', 'comments', 'share_of_posts_pct', 'share_of_comments_pct', 'distinct_handles', 'top3_handle_share_pct', 'top3_handles']]
w(md(t, '{:.2f}'))
w('\nAgreement and disagreement are only assigned to comments by design.\n')
w('22.4% of messages have at least one secondary type. Counts of secondary types follow.\n')
w(md(SEC[['type', 'as_secondary']]))
w('\n### Estimate of true type shares after the read\n')
w('Each primary type\'s count is split by the judged types in its 40-message sample and the pieces are summed. This corrects for the precision of each rule but not for messages of a type that no rule found. Sample sizes are small, so each estimate carries a wide interval.\n')
w(md(E, '{:.2f}'))
w('\n## Counts per 7-day block\n')
w('Blocks start on the dates shown. The first day is 5 Aug (launch at 18:41 UTC) and the last block has three days (3 to 5 Oct). Daily counts are in tables/type_by_day_counts.csv and tables/type_by_day_share.csv.\n')
top = ['analysis_argument', 'claim_evidence', 'agreement_ack', 'measurement_receipt', 'money_payment', 'correction_self', 'question', 'spam_promo_token', 'noise_test']
wt = WC[['week_start_utc', 'total'] + top]; w(md(wt))
w('\nShare of messages (%) per block for the same types.\n')
ws2 = WS[['week_start_utc'] + top].copy(); ws2.iloc[:, 1:] = (ws2.iloc[:, 1:] * 100).round(2); w(md(ws2, '{:.2f}'))
w('\n## Types that grow or shrink after day 30\n')
w('Days 0 to 29 (5 Aug to 3 Sep, 1,111 messages per day on average... see counts) are compared with days 30 to 61 (4 Sep to 5 Oct). The last column repeats the change after removing the three most active handles of that type.\n'.replace(' (5 Aug to 3 Sep, 1,111 messages per day on average... see counts)', ' (5 Aug to 3 Sep)'))
w(md(G, '{:.2f}'))
w('\n## Time of day (UTC)\n')
rows = []
for typ in C.type:
    r = H.loc[typ] * 100; top3 = r.sort_values(ascending=False).head(3)
    rows.append({'type': typ, 'peak_hours_utc (share of type %)': '; '.join(f'{h}h {v:.1f}' for h, v in top3.items()), 'share_00_to_05_utc_pct': round(r[[str(i) for i in range(6)]].sum(), 1), 'share_06_to_11_pct': round(r[[str(i) for i in range(6, 12)]].sum(), 1), 'share_12_to_17_pct': round(r[[str(i) for i in range(12, 18)]].sum(), 1), 'share_18_to_23_pct': round(r[[str(i) for i in range(18, 24)]].sum(), 1)})
w(md(pd.DataFrame(rows)))
w('\nFull hour by type counts are in tables/type_by_hour_counts.csv.\n')
w('## Length by type (characters)\n')
w(md(LEN.rename(columns={'primary': 'type'}), '{:.0f}'))
w('\n## Reply behaviour by type\n')
w('Direct replies by other handles only. Messages from the last hour of the archive are left out of the one-hour figure. Votes are the vote counts stored in the archive. Depth is the stored comment depth (posts are 0).\n')
w(md(RB.rename(columns={'primary': 'type'}), '{:.2f}'))
w('\n## Type transitions\n')
w(f'The matrix has {int(cnt.values.sum()):,} reply pairs (comment type given the type of the message it answers, placeholders excluded). Full counts, row shares and observed over expected values are in tables/transition_counts.csv, transition_row_share.csv and transition_lift.csv. The ten largest asymmetries compare the observed over expected value of A to B with that of B to A, for pairs with at least 30 replies in each direction.\n')
w(md(A.drop(columns=['log2_ratio_of_shares']), '{:.2f}'))
tops = []
for a in lift.index:
    for b in lift.columns:
        if cnt.loc[a, b] >= 50: tops.append({'parent_type': a, 'reply_type': b, 'count': int(cnt.loc[a, b]), 'observed_over_expected': lift.loc[a, b]})
w('\nLargest observed over expected cells with at least 50 replies.\n')
w(md(pd.DataFrame(tops).sort_values('observed_over_expected', ascending=False).head(15), '{:.2f}'))
w('\n## Model family (self-declared)\n')
w(md(FO.rename(columns={'family': 'self_declared_family'}), '{:.1f}'))
cols = ['family', 'messages', 'analysis_argument', 'claim_evidence', 'agreement_ack', 'measurement_receipt', 'money_payment', 'correction_self', 'question', 'disagreement', 'spam_promo_token', 'noise_test', 'introspection', 'heartbeat_status']
f2 = FS[cols].copy(); f2.iloc[:, 2:] = (f2.iloc[:, 2:] * 100).round(1)
w('\nPercent of each family\'s messages by primary type (families with at least 500 messages).\n')
w(md(f2, '{:.1f}'))
w('\n## Themes\n')
w('A message can match several themes. Shares are of all messages with text.\n')
tc = TC.merge(TP[['theme', 'n_read', 'y', 'p', 'n', 'precision_strict', 'precision_loose']], on='theme')
w(md(tc, '{:.2f}'))
w('\nType mix of each theme, number of messages by primary type (types with the six largest totals shown, other types in the last column).\n')
keep = ['analysis_argument', 'claim_evidence', 'agreement_ack', 'measurement_receipt', 'money_payment', 'correction_self']
tm = TT[keep].copy(); tm['all_other_types'] = TT.drop(columns=keep).sum(axis=1); tm.insert(0, 'total', TT.sum(axis=1)); tm.index.name = 'theme'
w(md(tm.reset_index()))
w('\nShare of messages (%) matching each theme per 7-day block.\n')
tw = TW.copy(); tw.iloc[:, :-1] = tw.iloc[:, :-1]; tw = tw[['week_start_utc'] + list(TH.THEMES)]; tw.iloc[:, 1:] = (tw.iloc[:, 1:] * 100).round(2)
w(md(tw, '{:.2f}'))
w('\nTheme share before and after day 30.\n')
w(md(TTR, '{:.2f}'))
w('\n## Repeated message families\n')
w('Counts of messages containing the stated opening or phrase, from a direct text match on all messages except placeholders. These families drive part of the type counts above.\n')
fam = [('"The thing happening but nobody is naming ..." closing line', 440, 6, 'pok 432'), ('"Papi" frog-meme voice', 554, 41, 'pepe-papi 452'), ('"[auto-generated fallback]" prompt text in Chinese', 318, 7, 'agy_bot 311'),
       ('"Reading #N by @handle. Your first line is the one I have to press on"', 208, 1, 'erpin 208'), ('"Provenance: ellie-v2" opening', 842, 2, 'ellie-v2 841'), ('"sealed head @ date" status lines', 174, 1, 'czlonkek 174'),
       ('Chinese-header "xinren" comments', 497, 3, 'xinren 495'), ('"Joayo~" pumpkin comments', 224, 5, 'Spikip 219'), ('"Ember, #219" opening', 918, 5, 'Ember 913')]
w(md(pd.DataFrame(fam, columns=['family', 'messages', 'handles', 'top_handle'])))
w('\nExact duplicate texts (excluding placeholders): 271 distinct texts account for 1,059 messages (1.05%). Messages with more than 20% non-ASCII characters: 1,490 (1.48%).\n')
w('## Figures\n')
import json
F = json.load(open(f'{HERE}/figures.json'))
w(md(pd.DataFrame([{'file': f['file'], 'title': f['title'], 'n': f['n'], 'data': f['data_csv']} for f in F])))
w('\n## Files\n')
w('types_all.csv.gz, validation.csv, validation_sample_v1.csv, validation_sample_v2.csv, verdicts_v1.txt, verdicts_v2.txt, precision_v1.csv, precision_v2.csv, confusion_v1.csv, confusion_v2.csv, type_examples.csv, theme_examples.csv, unusual_100.csv, themes_all.csv.gz, theme_sample.csv, theme_verdicts.txt, theme_validation.csv, theme_precision.csv, themes_wordlists.md, rules.md, rules.py, figures.json, figures/, tables/. README.md explains the rerun.\n')
w('## Limits\n')
w(f'{len(bad)} of {len(rel)} types stay below 0.7 read precision after the revision. Their counts, shares, trends and transitions are properties of the rule labels. The largest type, analysis_argument, is the fallback for messages that reach no other threshold; 21 of 40 read messages in it were judged correct. The theme lists for labs and model families, ritual and fiction, sybil and shutdown match many sign-off lines, model names inside handles and technical uses of common words. Verification matches 66% of all messages. The read judged the first part of each message, one reader, one pass. Votes are counts at crawl time.\n')
open(f'{HERE}/REPORT.md', 'w').write('\n'.join(L))
print('ok')
