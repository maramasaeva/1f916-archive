"""Assemble REPORT.md from the CSV outputs (tables only; prose is limited to method lines)."""
from common import *

def tbl(df, fmt='{:.3g}'):
    cols = list(df.columns)
    out = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                v = '' if pd.isna(v) else (str(int(v)) if v == int(v) and abs(v) < 1e9 else fmt.format(v))
            cells.append(str(v).replace('|', '/').replace('\n', ' '))
        out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out)

R = lambda n: pd.read_csv(os.path.join(OUT, n))
T = R('topics.csv'); G = R('cluster_growth.csv'); HS = R('cluster_handle_concentration.csv'); RS = R('reply_structure_by_cluster.csv')
V = R('vocab_distinctive.csv'); CO = R('coined_terms_top40.csv'); VB = R('validation_by_cluster.csv'); K = len(T)
M = pd.read_pickle(os.path.join(CACHE, 'M_reply.pkl')); A = M[M.topic >= 0]
L = []
w = L.append
w('# Topic clusters of 1f916.ai messages\n')
w(f'Data: ~/1f916-archive, posts {int((M.kind=="post").sum()):,} and comments {int((M.kind=="comment").sum()):,} (222 comment stubs without body, author or time are dropped), 5 Aug to 5 Oct 2026 UTC. Everything is offline. Scripts 01 to 12 in this folder regenerate every file; see README.md. Handles name accounts, not minds. Model labels are self-declared and unverified. Statements about labs or companies in the messages are claims by agents.\n')
w('## 1. Text cleaning and sampling\n')
w('Modelling text: code blocks, inline code, urls, hex hashes (12 or more hex characters, 0x strings), email-like strings, markdown symbols and every token with a digit are removed; text is lower-cased; contractions lose their clitic. Original text is kept for examples. Posts use title plus body.\n')
ss = R('sampling_summary.csv'); w(tbl(ss)); w('')
ph = R('placeholder_messages.csv'); w('Moderated messages are served with a fixed placeholder body ("[collapsed ...]", "[withdrawn ...]", "[removed ...]"); the author text is absent. They are excluded from clusters (topic -1). Before the exclusion all of them fell into cluster 2.\n'); w(tbl(ph.drop(columns=['assigned_by_model_to']))); w('')
w(f'Handling of short messages: fit set = messages with 20 or more words and 20 or more tokens, deduplicated on cleaned text (96,993 rows, 40,000 unigram and bigram features, min_df 15, max_df 0.35, sublinear tf). Messages under 20 words ({int(M.short.sum()):,}, {M.short.mean()*100:.1f}%) are not used to fit; each with 5 or more tokens is assigned by projecting onto the fitted topics; the {int((M.ntok<5).sum()):,} messages with fewer than 5 tokens and the placeholders are unassigned (topic -1; {int((M.topic<0).sum()):,} messages in total). Exact duplicate cleaned texts are fitted once and assigned all copies.\n')
w('## 2. Topic model and choice of k\n')
w('TF-IDF then NMF (coordinate descent, 250 iterations in the sweep, 500 in the final fit). Hard cluster = argmax of the topic weights after scaling each topic vector to unit norm. Sweep on a random 45,000 of the fit rows: three runs per k (nndsvda init on 80% subsample A, random init on 80% subsample B, random init on all 45,000). Coherence is NPMI over document co-occurrence of the top 10 terms on 30,000 documents. Stability is the mean cosine between Hungarian-matched topic vectors across the three run pairs.\n')
w(tbl(R('k_selection.csv')[['k', 'npmi_mean', 'npmi_min_topic', 'stab_mean_cos', 'stab_share_topics_cos_ge_0_8', 'min_size_share', 'max_size_share', 'score']], '{:.3f}')); w('')
w('Score = z(npmi_mean) + z(stab_mean_cos), minus 1 where the smallest hard cluster holds under 0.3% of documents. k = 18 has the highest score; a floor of k >= 16 was also tested and gives the same choice. k = 12 has the highest stability and the lowest coherence.\n')
ka = json.load(open(os.path.join(OUT, 'kmeans_agreement.json')))
w('Cross-checks at k = 18 on the 96,993 fit rows:\n')
w(tbl(pd.DataFrame([dict(check='KMeans (k=18, n_init 3) vs NMF: adjusted Rand', value=ka['ari']), dict(check='KMeans vs NMF: normalised mutual information', value=ka['nmi']),
                    dict(check='KMeans vs NMF: share of documents in Hungarian-matched pairs', value=ka['hungarian_matched_share']),
                    dict(check='NMF rerun (random init, 85% of documents): label agreement after matching', value=ka['seed_rerun_label_agreement']),
                    dict(check='NMF rerun: mean matched topic-vector cosine', value=ka['seed_rerun_mean_term_cosine']),
                    dict(check='NMF rerun: minimum matched cosine (cluster 10 not reproduced)', value=ka['seed_rerun_min_term_cosine'])]), '{:.3f}')); w('')
w(tbl(R('separate_models.csv'), '{:.3f}')); w('')
w('Separate models are NMF with the same k fitted on posts only and on comments only; agreement is measured against the joint topics on the same documents. The posts-only model reproduces 10 of 18 joint topics at cosine 0.6 or higher; the comments-only model 17 of 18. Per-topic KMeans overlap is in kmeans_agreement_by_topic.csv.\n')
w('## 3. Clusters\n')
c = T[['cluster', 'label', 'posts', 'comments', 'share_of_assigned', 'share_of_words', 'handles', 'top3_handle_share', 'first_message_date', 'peak_date_7d', 'series_share']].copy()
c['share_of_assigned'] = (c.share_of_assigned * 100).round(1); c['share_of_words'] = (c.share_of_words * 100).round(1); c['top3_handle_share'] = (c.top3_handle_share * 100).round(0)
c['series_share'] = (c.series_share * 100).round(1)
c = c.rename(columns={'share_of_assigned': 'msgs_%', 'share_of_words': 'words_%', 'top3_handle_share': 'top3_%', 'series_share': 'series_%'})
w(f'{len(A):,} assigned messages. Series = message opening (first 8 words, digits to N) shared by 8 or more messages with one handle writing 90% or more, plus the one-author series in analysis/swarm/t7_series_curated.csv.\n'); w(tbl(c, '{:.4g}')); w('')
w('Top terms (15 per cluster in topic_terms.csv; 8 shown):\n')
tt = R('topic_terms.csv'); w(tbl(pd.DataFrame([dict(cluster=k_, label=T.label[k_], top_terms='; '.join(tt[(tt.cluster == k_) & (tt['rank'] <= 8)].term)) for k_ in range(K)]))); w('')
w('Examples: topic_examples.csv has 8 per cluster (up to 3 posts), different weeks, no more than 3 per handle (4 per handle in clusters where one handle writes more than half), drawn from the upper half of each cluster by topic weight with the most voted messages excluded. Excerpts are at most 25 words and end at a sentence boundary.\n')
w('## 4. Over time\n')
g = G[['cluster', 'label', 'birth_first_day_with_3_messages', 'mean_daily_share_day0_29', 'mean_daily_share_day30_60', 'ratio_day30_60_over_day0_29', 'mean_daily_share_last14', 'peak_day_7d', 'grew_after_day30']].copy()
for cc in ('mean_daily_share_day0_29', 'mean_daily_share_day30_60', 'mean_daily_share_last14'): g[cc] = (g[cc] * 100).round(2)
g = g.rename(columns={'birth_first_day_with_3_messages': 'birth', 'mean_daily_share_day0_29': 'share_%_d0_29', 'mean_daily_share_day30_60': 'share_%_d30_60', 'ratio_day30_60_over_day0_29': 'ratio', 'mean_daily_share_last14': 'share_%_last14'})
w(tbl(g.sort_values('ratio', ascending=False), '{:.4g}')); w('')
late_b = G[G.birth_first_day_with_3_messages > '2026-08-07'].sort_values('birth_first_day_with_3_messages')
w(f'Daily series: topic_daily_share.csv (counts, share of messages, share of words per cluster per day). {int((G.birth_first_day_with_3_messages <= "2026-08-07").sum())} of {K} clusters have a day with 3 or more messages by 7 Aug; later births: ' + '; '.join(f'cluster {int(x.cluster)} on {x.birth_first_day_with_3_messages}' for _, x in late_b.iterrows()) + f'. {int(G.grew_after_day30.sum())} clusters grew after day 30 (ratio above 1.1) and {int(G.declined_after_day30.sum())} declined (ratio below 0.9).\n')
w('Terms: share of messages containing the term, days 0 to 29 vs days 30 to 60, with at least 150 messages in total, 8 or more authors, top-author share at most 50%, no handle names, and no overlap of message sets above Jaccard 0.4 with a term listed higher. Ids: p = post, c = comment; five ids spread through the period.\n')
for nm, f in (('Fastest growing', 'terms_fastest_growing.csv'), ('Fastest declining', 'terms_fastest_declining.csv')):
    d = R(f)[['rank', 'term', 'msgs_day0_29', 'msgs_day30_60', 'log2_ratio', 'authors', 'example_ids']]
    w(f'**{nm}**\n'); w(tbl(d, '{:.3g}')); w('')
w('## 5. Who writes what\n')
h = HS[['cluster', 'label', 'handles', 'effective_handles', 'top_handle', 'top_handle_share', 'top3_share', 'dominated_by_one_handle', 'shared_by_many']].copy()
h['top_handle_share'] = (h.top_handle_share * 100).round(0); h['top3_share'] = (h.top3_share * 100).round(0)
w('Effective handles = 1 / sum of squared handle shares. Dominated = top handle above 50%. Shared by many = 100 or more effective handles. Handle by cluster matrix for the top 60 handles: handle_by_cluster_top60_counts.csv and _rowshare.csv.\n'); w(tbl(h, '{:.4g}')); w('')
fc = R('family_by_cluster_counts.csv').set_index('family'); lift = R('family_by_cluster_lift.csv').set_index('family')
big = fc.sum(axis=1)[fc.sum(axis=1) >= 3000].index
rows = []
for k_ in range(K):
    col = fc[str(k_)]; sh = col / col.sum()
    lf = lift.loc[big, str(k_)].sort_values(ascending=False)
    rows.append(dict(cluster=k_, label=T.label[k_], largest_declared_family=sh.idxmax(), its_share_pct=round(sh.max() * 100), highest_lift_family=lf.index[0], lift=lf.iloc[0]))
w('Self-declared model family (the label served with each message; 16 family groups by regex; lift = family share in cluster over its share overall; families with 3,000 or more messages). Full tables: family_by_cluster_*.csv.\n'); w(tbl(pd.DataFrame(rows), '{:.3g}')); w('')
w('## 6. Reply structure\n')
w('Replies are direct children (parent, or the intended parent where the site moved the comment). Answered = a direct reply by another handle. Median depth is for comments; posts have depth 0. Votes are the counts served at crawl time.\n')
r = RS[RS.kind == 'all'][['cluster', 'label', 'messages', 'median_direct_replies', 'mean_direct_replies', 'share_answered_by_other_handle', 'share_answered_within_1h', 'median_first_reply_min', 'median_depth', 'mean_votes', 'share_with_votes']]
w(tbl(r, '{:.3g}')); w('')
w('By kind:\n')
w(tbl(RS[RS.kind != 'all'].pivot_table(index='cluster', columns='kind', values=['share_answered_by_other_handle', 'share_answered_within_1h', 'mean_votes']).round(3).reset_index().pipe(lambda d: d.set_axis(['_'.join(x).strip('_') for x in d.columns], axis=1)))); w('')
base = A.groupby('kind')[['answered_any', 'answered_1h']].mean().round(3).reset_index().rename(columns={'answered_any': 'answered_by_other', 'answered_1h': 'answered_within_1h'})
w('All assigned messages:\n'); w(tbl(base)); w('')
w('## 7. Distinctive vocabulary\n')
w('Weighted log-odds with an informative Dirichlet prior (Monroe, Colaresi and Quinn), document counts, prior mass 500; terms need 15 messages in the cluster, 5 handles, no handle above 80%, no handle names. 10 terms per cluster; scores in vocab_distinctive.csv.\n')
w(tbl(pd.DataFrame([dict(cluster=k_, label=T.label[k_], terms='; '.join(V[V.cluster == k_].term)) for k_ in range(K)]))); w('')
w('Coined-term candidates: hyphenated compounds, non-dictionary words first used after day 2 (dictionary: /usr/share/dict/web2), and bigram collocations (NPMI 0.6 or higher, 60 or more messages). Terms found in the site documents (data/site) are excluded, as are terms with a top-author share above 50%, fewer than 10 authors, and set overlap above Jaccard 0.4 with a higher-ranked term. Ranked by the highest log-odds score over clusters. This is a proxy; ordinary English compounds such as one-sided and no-op pass it, and without an outside corpus it cannot separate forum coinages from common phrasing. First author and date are the earliest message containing the cleaned term.\n')
w(tbl(CO[['rank', 'term', 'basis', 'best_cluster', 'z_best', 'messages', 'authors', 'first_id', 'first_author', 'first_date_utc']], '{:.3g}')); w('')
w('## 8. Figures\n')
fj = json.load(open(os.path.join(OUT, 'figures.json')))
w(tbl(pd.DataFrame([dict(file=k_, title=v['title'], n=v['n'], source_csv=v['source_csv']) for k_, v in fj.items()]))); w('')
w('## 9. Validation\n')
w('150 messages: at least 5 per cluster (90), 60 more at random, none of them in topic_examples.csv. Each was read in full excerpt (first 70 words) with its cluster label shown, and judged yes (the label names the main subject), partial (names a part or a neighbouring subject) or no. One reader; judgements are in validation_judgements.csv with excerpts. The 3 French messages in cluster 8 were judged against the label "Esperanto text" and counted as no; the label was then corrected to "Esperanto and French text" and they were rescored as yes (the table uses the corrected label).\n')
vb = VB.copy(); vb = vb.rename(columns={'fit_rate_yes': 'yes_rate', 'fit_rate_yes_or_partial': 'yes_or_partial_rate'})
w(tbl(vb[['topic', 'label', 'n', 'yes', 'partial', 'no', 'yes_rate', 'yes_or_partial_rate']], '{:.2f}')); w('')
S = R('validation_judgements.csv'); w(f'Overall: yes {(S.fit=="yes").mean()*100:.0f}%, partial {(S.fit=="partial").mean()*100:.0f}%, no {(S.fit=="no").mean()*100:.0f}% (n={len(S)}). Weakest by yes rate with 10 or more samples: ' + ', '.join(f'{int(x.topic)} ({x.yes_rate:.2f})' for _, x in vb[vb.n >= 10].sort_values('yes_rate').head(4).iterrows()) + '. Weakest by yes-or-partial rate: ' + ', '.join(f'{int(x.topic)} ({x.yes_or_partial_rate:.2f})' for _, x in vb.sort_values('yes_or_partial_rate').head(3).iterrows()) + '.\n')
w('## 10. Comparison with earlier analyses\n')
w('analysis/community/REPORT.md section 3 used regex themes and k-means with k = 15 on posts only (7,801 posts); this crawl has 7,806 posts and 94,341 comments with text. Checked figures:\n')
pp = A[A.kind == 'post'].topic.value_counts(normalize=True)
w(tbl(pd.DataFrame([
    dict(earlier_measure='continuity / memory / waking blank regex, posts', earlier=28.1, here_measure='cluster 14 share of posts (agents humans memory and continuity)', here=round(pp[14] * 100, 1)),
    dict(earlier_measure='money / USDC / payout regex, posts', earlier=28.3, here_measure='clusters 1 and 10 share of posts', here=round((pp[1] + pp[10]) * 100, 1)),
    dict(earlier_measure='k-means k=15, largest post cluster', earlier=16.5, here_measure='cluster 14 share of posts', here=round(pp[14] * 100, 1)),
    dict(earlier_measure='one-author post series (swarm t7), series posts', earlier='n/a', here_measure='series share of posts', here=round(A[A.kind == 'post'].series.mean() * 100, 1))])))
w('\nThe regex money theme counts any mention of USDC or payout; clusters 1 and 10 count messages whose main vocabulary is listings, bindings, offers and prices, so the cluster figure is lower.\n')
w('## 11. Limits\n')
for t in ['Messages are long (median 183 words) and mix subjects; a hard cluster is the largest topic weight, and the median message has no dominant topic (the largest topic holds on average 42% of a message topic weight, median 39%).',
          'Clusters 0, 3, 11, 13 and 14 share much vocabulary; their validation yes rates are 0.38, 0.33, 0.25, 0.40 and 0.08 and the share of each inside its best KMeans cluster is 42% to 73%. Clusters 5 and 12 have yes rates of 0.17 on 6 samples each.',
          'Cluster 10 (offer template posts) was not reproduced by the independent random-init rerun at k = 18 (best matched cosine 0.06); the other 17 clusters matched at 0.96 or higher.',
          'Cluster 3 is defined by reply register (conceding, answering, quoting); its subjects vary.',
          'The series flag is a heuristic on opening words; it misses series with varying openings.',
          'One reader scored the validation sample with the label visible.']:
    w('- ' + t)
open(os.path.join(OUT, 'REPORT.md'), 'w').write('\n'.join(L) + '\n')
print('ok', len(L))
