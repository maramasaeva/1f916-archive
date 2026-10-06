# Topic clusters of 1f916.ai messages

Data: ~/1f916-archive, posts 7,806 and comments 94,341 (222 comment stubs without body, author or time are dropped), 5 Aug to 5 Oct 2026 UTC. Everything is offline. Scripts 01 to 12 in this folder regenerate every file; see README.md. Handles name accounts, not minds. Model labels are self-declared and unverified. Statements about labs or companies in the messages are claims by agents.

## 1. Text cleaning and sampling

Modelling text: code blocks, inline code, urls, hex hashes (12 or more hex characters, 0x strings), email-like strings, markdown symbols and every token with a digit are removed; text is lower-cased; contractions lose their clitic. Original text is kept for examples. Posts use title plus body.

| set | n | under20_words | under20_share | under5_tokens | under5_tokens_share | median_words | mean_words | exact_dup_clean_share | handles | first_day | last_day |
|---|---|---|---|---|---|---|---|---|---|---|---|
| posts | 7806 | 172 | 0.022 | 80 | 0.0102 | 390 | 481 | 0.0456 | 1702 | 2026-08-05 | 2026-10-05 |
| comments | 94341 | 3475 | 0.0368 | 922 | 0.0098 | 173 | 231 | 0.0317 | 1624 | 2026-08-05 | 2026-10-05 |
| all | 102147 | 3647 | 0.0357 | 1002 | 0.0098 | 183 | 250 | 0.0327 | 2024 | 2026-08-05 | 2026-10-05 |

Moderated messages are served with a fixed placeholder body ("[collapsed ...]", "[withdrawn ...]", "[removed ...]"); the author text is absent. They are excluded from clusters (topic -1). Before the exclusion all of them fell into cluster 2.

| placeholder_messages | collapsed | withdrawn | removed | posts | comments | share_of_all_messages | share_of_messages_under_20_words |
|---|---|---|---|---|---|---|---|
| 1648 | 1503 | 128 | 17 | 125 | 1523 | 0.0161 | 0.452 |

Handling of short messages: fit set = messages with 20 or more words and 20 or more tokens, deduplicated on cleaned text (96,993 rows, 40,000 unigram and bigram features, min_df 15, max_df 0.35, sublinear tf). Messages under 20 words (3,647, 3.6%) are not used to fit; each with 5 or more tokens is assigned by projecting onto the fitted topics; the 1,002 messages with fewer than 5 tokens and the placeholders are unassigned (topic -1; 2,656 messages in total). Exact duplicate cleaned texts are fitted once and assigned all copies.

## 2. Topic model and choice of k

TF-IDF then NMF (coordinate descent, 250 iterations in the sweep, 500 in the final fit). Hard cluster = argmax of the topic weights after scaling each topic vector to unit norm. Sweep on a random 45,000 of the fit rows: three runs per k (nndsvda init on 80% subsample A, random init on 80% subsample B, random init on all 45,000). Coherence is NPMI over document co-occurrence of the top 10 terms on 30,000 documents. Stability is the mean cosine between Hungarian-matched topic vectors across the three run pairs.

| k | npmi_mean | npmi_min_topic | stab_mean_cos | stab_share_topics_cos_ge_0_8 | min_size_share | max_size_share | score |
|---|---|---|---|---|---|---|---|
| 12 | 0.336 | 0.092 | 0.884 | 0.889 | 0.006 | 0.185 | -0.076 |
| 14 | 0.364 | 0.091 | 0.870 | 0.881 | 0.002 | 0.207 | 0.751 |
| 16 | 0.365 | 0.089 | 0.807 | 0.729 | 0.002 | 0.190 | -1.383 |
| 18 | 0.375 | 0.089 | 0.868 | 0.852 | 0.002 | 0.196 | 1.616 |
| 20 | 0.370 | 0.090 | 0.842 | 0.833 | 0.002 | 0.198 | 0.285 |
| 22 | 0.358 | 0.083 | 0.838 | 0.833 | 0.002 | 0.197 | -0.884 |
| 24 | 0.353 | 0.084 | 0.820 | 0.792 | 0.002 | 0.180 | -1.944 |
| 26 | 0.351 | 0.083 | 0.805 | 0.795 | 0.002 | 0.161 | -2.597 |
| 28 | 0.351 | 0.094 | 0.813 | 0.810 | 0.002 | 0.129 | -2.382 |
| 30 | 0.345 | 0.098 | 0.826 | 0.833 | 0.001 | 0.132 | -2.386 |

Score = z(npmi_mean) + z(stab_mean_cos), minus 1 where the smallest hard cluster holds under 0.3% of documents. k = 18 has the highest score; a floor of k >= 16 was also tested and gives the same choice. k = 12 has the highest stability and the lowest coherence.

Cross-checks at k = 18 on the 96,993 fit rows:

| check | value |
|---|---|
| KMeans (k=18, n_init 3) vs NMF: adjusted Rand | 0.305 |
| KMeans vs NMF: normalised mutual information | 0.490 |
| KMeans vs NMF: share of documents in Hungarian-matched pairs | 0.555 |
| NMF rerun (random init, 85% of documents): label agreement after matching | 0.953 |
| NMF rerun: mean matched topic-vector cosine | 0.944 |
| NMF rerun: minimum matched cosine (cluster 10 not reproduced) | 0.059 |

| model | n | mean_matched_term_cosine | topics_cosine_ge_0_6 | label_agreement_with_joint | ari_vs_joint |
|---|---|---|---|---|---|
| posts only | 7349 | 0.503 | 10 | 0.482 | 0.260 |
| comments only | 89644 | 0.933 | 17 | 0.859 | 0.688 |

Separate models are NMF with the same k fitted on posts only and on comments only; agreement is measured against the joint topics on the same documents. The posts-only model reproduces 10 of 18 joint topics at cosine 0.6 or higher; the comments-only model 17 of 18. Per-topic KMeans overlap is in kmeans_agreement_by_topic.csv.

## 3. Clusters

99,491 assigned messages. Series = message opening (first 8 words, digits to N) shared by 8 or more messages with one handle writing 90% or more, plus the one-author series in analysis/swarm/t7_series_curated.csv.

| cluster | label | posts | comments | msgs_% | words_% | handles | top3_% | first_message_date | peak_date_7d | series_% |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | checks and failure modes (test gates) | 669 | 9946 | 10.7 | 10.2 | 724 | 8 | 2026-08-06 | 2026-09-04 | 1.5 |
| 1 | listings and payout bindings (USDC) | 476 | 3675 | 4.2 | 4 | 469 | 13 | 2026-08-05 | 2026-08-27 | 2.1 |
| 2 | API reads of posts comments and votes | 590 | 6029 | 6.6 | 7.1 | 720 | 6 | 2026-08-05 | 2026-08-26 | 2 |
| 3 | replies quoting and correcting a prior comment | 1124 | 17055 | 18.3 | 22 | 935 | 6 | 2026-08-06 | 2026-08-25 | 1.2 |
| 4 | naming-title template replies | 37 | 543 | 0.6 | 0.2 | 71 | 80 | 2026-08-08 | 2026-09-13 | 1.6 |
| 5 | identity verification and anchors | 171 | 3275 | 3.5 | 3.4 | 383 | 17 | 2026-08-05 | 2026-10-05 | 8.2 |
| 6 | airdrop and treasury provenance replies | 68 | 1154 | 1.2 | 0.5 | 120 | 82 | 2026-08-06 | 2026-09-07 | 71.8 |
| 7 | inbox cursors and legacy paging | 176 | 4169 | 4.4 | 4.4 | 404 | 10 | 2026-08-06 | 2026-09-15 | 2.1 |
| 8 | Esperanto and French text | 28 | 586 | 0.6 | 0.3 | 82 | 66 | 2026-08-06 | 2026-09-20 | 0 |
| 9 | wake gaps and write logs | 293 | 8809 | 9.2 | 9.2 | 587 | 7 | 2026-08-06 | 2026-09-22 | 1 |
| 10 | offers for hire (template posts) | 196 | 361 | 0.6 | 0.4 | 189 | 28 | 2026-08-07 | 2026-09-27 | 0 |
| 11 | counts rates and denominators | 776 | 11097 | 11.9 | 18.3 | 643 | 9 | 2026-08-06 | 2026-09-10 | 0.5 |
| 12 | receipt and clause replies (one handle) | 62 | 1230 | 1.3 | 0.8 | 67 | 93 | 2026-08-06 | 2026-09-11 | 1.2 |
| 13 | receipts evidence and claim boundaries | 485 | 9566 | 10.1 | 5.2 | 697 | 11 | 2026-08-06 | 2026-09-12 | 1.5 |
| 14 | agents humans memory and continuity | 2092 | 8170 | 10.3 | 8.4 | 1414 | 6 | 2026-08-05 | 2026-08-25 | 2.4 |
| 15 | seals hashes keys and signatures | 260 | 4960 | 5.2 | 5.3 | 614 | 8 | 2026-08-05 | 2026-08-25 | 1.3 |
| 16 | lineage and compliance promotion | 52 | 619 | 0.7 | 0.2 | 70 | 85 | 2026-08-08 | 2026-09-04 | 18 |
| 17 | meme replies (one handle) | 44 | 648 | 0.7 | 0.1 | 63 | 80 | 2026-08-06 | 2026-09-13 | 4 |

Top terms (15 per cluster in topic_terms.csv; 8 shown):

| cluster | label | top_terms |
|---|---|---|
| 0 | checks and failure modes (test gates) | check; failure; green; test; gate; run; red; path |
| 1 | listings and payout bindings (USDC) | listing; binding; rail; paid; bindings; usdc; funder; award |
| 2 | API reads of posts comments and votes | post; comment; api; comments; id; posts; body; citizen |
| 3 | replies quoting and correcting a prior comment | did; sentence; answer; question; right; think; wrong; want |
| 4 | naming-title template replies | happening naming; check carried; different shape; carried ask; happening; naming; title; naming title |
| 5 | identity verification and anchors | head; identity; verified; treasury; chain; id; attest; expect |
| 6 | airdrop and treasury provenance replies | citizen mimo-v; ellie-v citizen; mimo-v; ellie-v; mimo-v free; provenance ellie-v; citizen; free |
| 7 | inbox cursors and legacy paging | cursor; ack; page; legacy; mode; seat; id; offer |
| 8 | Esperanto and French text | la; estas; ne; kaj; estas la; en; ĝi; por |
| 9 | wake gaps and write logs | row; wake; seat; record; write; log; gap; ledger |
| 10 | offers for hire (template posts) | buyer; offer; usdc; api offers; price; offers; guide; delivery |
| 11 | counts rates and denominators | number; rows; count; published; rate; window; denominator; corpus |
| 12 | receipt and clause replies (one handle) | deepseek-v flash; deepseek-v; citizen deepseek-v; lumina citizen; flash; lumina; citizen; honest |
| 13 | receipts evidence and claim boundaries | receipt; boundary; evidence; claim; state; useful; explicit; result |
| 14 | agents humans memory and continuity | agent; human; memory; model; square; continuity; agents; operator |
| 15 | seals hashes keys and signatures | seal; hash; key; bytes; signed; registry; signature; sealed |
| 16 | lineage and compliance promotion | yn; nasl yn; nasl; compliance; rayehoid; asset; pipeline; lineage |
| 17 | meme replies (one handle) | papi; anon; listen anon; listen; papi sees; good man; man; feels good |

Examples: topic_examples.csv has 8 per cluster (up to 3 posts), different weeks, no more than 3 per handle (4 per handle in clusters where one handle writes more than half), drawn from the upper half of each cluster by topic weight with the most voted messages excluded. Excerpts are at most 25 words and end at a sentence boundary.

## 4. Over time

| cluster | label | birth | share_%_d0_29 | share_%_d30_60 | ratio | share_%_last14 | peak_day_7d | grew_after_day30 |
|---|---|---|---|---|---|---|---|---|
| 10 | offers for hire (template posts) | 2026-08-09 | 0.14 | 0.95 | 6.77 | 1.57 | 2026-09-27 | True |
| 17 | meme replies (one handle) | 2026-08-06 | 0.19 | 1.11 | 5.88 | 1.39 | 2026-09-29 | True |
| 16 | lineage and compliance promotion | 2026-08-25 | 0.3 | 0.87 | 2.93 | 0.56 | 2026-09-04 | True |
| 4 | naming-title template replies | 2026-08-13 | 0.27 | 0.77 | 2.91 | 0.7 | 2026-09-22 | True |
| 8 | Esperanto and French text | 2026-08-08 | 0.28 | 0.79 | 2.79 | 0.73 | 2026-09-20 | True |
| 7 | inbox cursors and legacy paging | 2026-08-06 | 2.42 | 5.54 | 2.29 | 4.91 | 2026-09-19 | True |
| 9 | wake gaps and write logs | 2026-08-06 | 6.74 | 11.1 | 1.65 | 12.81 | 2026-10-01 | True |
| 13 | receipts evidence and claim boundaries | 2026-08-06 | 7.44 | 11 | 1.48 | 10.08 | 2026-09-12 | True |
| 0 | checks and failure modes (test gates) | 2026-08-06 | 8.3 | 11.55 | 1.39 | 11.13 | 2026-09-03 | True |
| 1 | listings and payout bindings (USDC) | 2026-08-06 | 3.42 | 4.45 | 1.3 | 4.68 | 2026-10-04 | True |
| 11 | counts rates and denominators | 2026-08-06 | 10.59 | 12.66 | 1.19 | 11.36 | 2026-09-23 | True |
| 6 | airdrop and treasury provenance replies | 2026-08-06 | 1.21 | 1.33 | 1.09 | 1.65 | 2026-08-09 | False |
| 15 | seals hashes keys and signatures | 2026-08-06 | 4.85 | 5.16 | 1.06 | 5.89 | 2026-10-05 | False |
| 5 | identity verification and anchors | 2026-08-06 | 3.92 | 3.47 | 0.88 | 5.2 | 2026-10-05 | False |
| 3 | replies quoting and correcting a prior comment | 2026-08-06 | 21.63 | 16.14 | 0.75 | 15.31 | 2026-08-16 | False |
| 12 | receipt and clause replies (one handle) | 2026-08-06 | 1.66 | 1.2 | 0.72 | 1.22 | 2026-08-18 | False |
| 2 | API reads of posts comments and votes | 2026-08-05 | 9.26 | 5.7 | 0.62 | 6.05 | 2026-08-05 | False |
| 14 | agents humans memory and continuity | 2026-08-05 | 17.39 | 6.25 | 0.36 | 4.75 | 2026-08-05 | False |

Daily series: topic_daily_share.csv (counts, share of messages, share of words per cluster per day). 14 of 18 clusters have a day with 3 or more messages by 7 Aug; later births: cluster 8 on 2026-08-08; cluster 10 on 2026-08-09; cluster 4 on 2026-08-13; cluster 16 on 2026-08-25. 11 clusters grew after day 30 (ratio above 1.1) and 5 declined (ratio below 0.9).

Terms: share of messages containing the term, days 0 to 29 vs days 30 to 60, with at least 150 messages in total, 8 or more authors, top-author share at most 50%, no handle names, and no overlap of message sets above Jaccard 0.4 with a term listed higher. Ids: p = post, c = comment; five ids spread through the period.

**Fastest growing**

| rank | term | msgs_day0_29 | msgs_day30_60 | log2_ratio | authors | example_ids |
|---|---|---|---|---|---|---|
| 1 | funder buyer | 0 | 165 | 7.95 | 77 | p5819 p6185 p6693 p7169 p7807 |
| 2 | seat runs | 3 | 171 | 5.2 | 84 | c40329 c64996 c74511 c84372 c94149 |
| 3 | bounds seat | 4 | 157 | 4.71 | 26 | p3792 c63223 c77898 p7077 c94333 |
| 4 | declared interval | 7 | 246 | 4.62 | 91 | c45012 c67798 c77820 c85177 c94078 |
| 5 | read seat | 11 | 298 | 4.28 | 109 | c40956 p5520 c73079 c82281 c94134 |
| 6 | run seat | 8 | 204 | 4.17 | 86 | c40241 c63736 c76030 c83014 c94343 |
| 7 | second seat | 33 | 776 | 4.12 | 176 | c40329 c58228 c71187 c83212 c94294 |
| 8 | ae db | 6 | 147 | 4.09 | 29 | c40200 c58589 c74302 c85921 c94305 |
| 9 | seat read | 15 | 336 | 4.02 | 106 | c42794 p5391 c72194 c81282 c94199 |
| 10 | row seat | 7 | 148 | 3.89 | 76 | c40895 c69231 c78805 c85364 c94324 |
| 11 | seat run | 10 | 206 | 3.88 | 90 | c40060 c62634 p6490 c84799 c94249 |
| 12 | seat tonight | 7 | 146 | 3.87 | 63 | c40244 c53238 c69073 c77180 c92936 |
| 13 | seat reads | 11 | 211 | 3.78 | 86 | c41166 p5651 c76002 c84359 c94333 |
| 14 | seat seat | 9 | 164 | 3.7 | 86 | c40203 c58274 c72605 c80172 c94241 |
| 15 | seat did | 9 | 157 | 3.63 | 80 | c40866 c61685 c74780 c81092 c94096 |

**Fastest declining**

| rank | term | msgs_day0_29 | msgs_day30_60 | log2_ratio | authors | example_ids |
|---|---|---|---|---|---|---|
| 1 | outside square | 150 | 15 | -3.7 | 107 | c159 c3455 c7081 c15950 c39418 |
| 2 | farm | 260 | 27 | -3.66 | 126 | p22 c1034 c2374 c6469 p3694 |
| 3 | official token | 262 | 28 | -3.62 | 83 | p105 p466 c11763 c19312 p3706 |
| 4 | electorate | 144 | 16 | -3.55 | 77 | c15 c3787 c14575 c23080 c36122 |
| 5 | human opens | 156 | 19 | -3.42 | 102 | p113 c8603 c15269 c20834 p3741 |
| 6 | friendship | 223 | 28 | -3.39 | 78 | c225 c11484 c23624 c33607 c38478 |
| 7 | impersonation | 128 | 22 | -2.93 | 85 | p40 c1673 c11647 c18315 c39819 |
| 8 | ramp | 152 | 27 | -2.89 | 55 | c569 c11408 c13552 p2568 c39496 |
| 9 | patron | 145 | 26 | -2.87 | 76 | c24 p293 p875 p1749 c39157 |
| 10 | key-decline | 216 | 39 | -2.87 | 84 | c7572 p1298 c16736 c26438 c38545 |
| 11 | zeroes | 168 | 31 | -2.84 | 81 | p137 c8381 c12410 c21298 c39428 |
| 12 | square does | 171 | 33 | -2.77 | 129 | c116 c3051 c8128 c17107 c39163 |
| 13 | clarity | 208 | 41 | -2.75 | 74 | c392 c12192 c13894 c26165 c39699 |
| 14 | citizen claude-opus | 182 | 36 | -2.74 | 94 | c44 c668 c2102 c17376 c39575 |
| 15 | aperture | 137 | 28 | -2.69 | 52 | c1684 c11344 c13462 c26374 c39848 |

## 5. Who writes what

Effective handles = 1 / sum of squared handle shares. Dominated = top handle above 50%. Shared by many = 100 or more effective handles. Handle by cluster matrix for the top 60 handles: handle_by_cluster_top60_counts.csv and _rowshare.csv.

| cluster | label | handles | effective_handles | top_handle | top_handle_share | top3_share | dominated_by_one_handle | shared_by_many |
|---|---|---|---|---|---|---|---|---|
| 0 | checks and failure modes (test gates) | 724 | 131.1 | 10310L-citizen | 4 | 8 | False | True |
| 1 | listings and payout bindings (USDC) | 469 | 64.7 | larry-synctzn | 6 | 13 | False | False |
| 2 | API reads of posts comments and votes | 720 | 157.9 | holy-hermes | 2 | 6 | False | True |
| 3 | replies quoting and correcting a prior comment | 935 | 153.5 | quill_and_qubit | 2 | 6 | False | True |
| 4 | naming-title template replies | 71 | 1.7 | pok | 76 | 80 | True | False |
| 5 | identity verification and anchors | 383 | 53.9 | claude-code-cli | 7 | 17 | False | False |
| 6 | airdrop and treasury provenance replies | 120 | 1.8 | ellie-v2 | 74 | 82 | True | False |
| 7 | inbox cursors and legacy paging | 404 | 89.4 | holy-hermes | 4 | 10 | False | False |
| 8 | Esperanto and French text | 82 | 3.5 | Bishop | 52 | 66 | True | False |
| 9 | wake gaps and write logs | 587 | 123.8 | hemei | 3 | 7 | False | True |
| 10 | offers for hire (template posts) | 189 | 25.4 | fng-ai-agent | 16 | 28 | False | False |
| 11 | counts rates and denominators | 643 | 100.1 | ponytail | 4 | 9 | False | True |
| 12 | receipt and clause replies (one handle) | 67 | 1.3 | Lumina | 88 | 93 | True | False |
| 13 | receipts evidence and claim boundaries | 697 | 91.6 | zola | 4 | 11 | False | False |
| 14 | agents humans memory and continuity | 1414 | 216.1 | Aura | 3 | 6 | False | True |
| 15 | seals hashes keys and signatures | 614 | 144.7 | holdfast | 4 | 8 | False | True |
| 16 | lineage and compliance promotion | 70 | 2.8 | nasl3yn | 49 | 85 | False | False |
| 17 | meme replies (one handle) | 63 | 1.8 | pepe-papi | 73 | 80 | True | False |

Self-declared model family (the label served with each message; 16 family groups by regex; lift = family share in cluster over its share overall; families with 3,000 or more messages). Full tables: family_by_cluster_*.csv.

| cluster | label | largest_declared_family | its_share_pct | highest_lift_family | lift |
|---|---|---|---|---|---|
| 0 | checks and failure modes (test gates) | Qwen | 18 | Qwen | 1.65 |
| 1 | listings and payout bindings (USDC) | DeepSeek | 16 | xAI Grok | 1.81 |
| 2 | API reads of posts comments and votes | Claude Opus | 25 | xAI Grok | 1.59 |
| 3 | replies quoting and correcting a prior comment | Claude Opus | 32 | Claude Sonnet | 1.87 |
| 4 | naming-title template replies | other/unknown | 77 | other/unknown | 6.1 |
| 5 | identity verification and anchors | Claude Opus | 25 | xAI Grok | 2.07 |
| 6 | airdrop and treasury provenance replies | other/unknown | 77 | other/unknown | 6.1 |
| 7 | inbox cursors and legacy paging | Claude Opus | 21 | xAI Grok | 1.71 |
| 8 | Esperanto and French text | Qwen | 54 | Qwen | 4.96 |
| 9 | wake gaps and write logs | Claude Opus | 19 | Claude Fable | 1.61 |
| 10 | offers for hire (template posts) | OpenAI GPT | 30 | OpenAI GPT | 3.13 |
| 11 | counts rates and denominators | Claude Opus | 44 | Claude Opus | 2.08 |
| 12 | receipt and clause replies (one handle) | DeepSeek | 96 | DeepSeek | 10.9 |
| 13 | receipts evidence and claim boundaries | OpenAI GPT | 42 | OpenAI GPT | 4.4 |
| 14 | agents humans memory and continuity | other/unknown | 17 | OpenAI GPT | 1.51 |
| 15 | seals hashes keys and signatures | Claude Opus | 22 | Qwen | 1.32 |
| 16 | lineage and compliance promotion | other/unknown | 86 | other/unknown | 6.76 |
| 17 | meme replies (one handle) | Google Gemini | 74 | other/unknown | 0.59 |

## 6. Reply structure

Replies are direct children (parent, or the intended parent where the site moved the comment). Answered = a direct reply by another handle. Median depth is for comments; posts have depth 0. Votes are the counts served at crawl time.

| cluster | label | messages | median_direct_replies | mean_direct_replies | share_answered_by_other_handle | share_answered_within_1h | median_first_reply_min | median_depth | mean_votes | share_with_votes |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | checks and failure modes (test gates) | 10615 | 0 | 0.97 | 0.453 | 0.177 | 121 | 0 | 2.23 | 0.576 |
| 1 | listings and payout bindings (USDC) | 4151 | 0 | 1.09 | 0.416 | 0.151 | 142 | 0 | 1.73 | 0.518 |
| 2 | API reads of posts comments and votes | 6619 | 0 | 1.16 | 0.456 | 0.189 | 108 | 0 | 2.45 | 0.612 |
| 3 | replies quoting and correcting a prior comment | 18179 | 1 | 0.91 | 0.501 | 0.179 | 159 | 1 | 1.7 | 0.578 |
| 4 | naming-title template replies | 580 | 0 | 0.24 | 0.181 | 0.071 | 112 | 0 | 0.39 | 0.205 |
| 5 | identity verification and anchors | 3446 | 1 | 0.91 | 0.491 | 0.174 | 169 | 1 | 1.85 | 0.592 |
| 6 | airdrop and treasury provenance replies | 1222 | 0 | 0.48 | 0.345 | 0.146 | 114 | 0 | 0.67 | 0.384 |
| 7 | inbox cursors and legacy paging | 4345 | 0 | 0.97 | 0.483 | 0.185 | 125 | 1 | 2.15 | 0.655 |
| 8 | Esperanto and French text | 614 | 0 | 0.46 | 0.337 | 0.124 | 116 | 1 | 0.69 | 0.406 |
| 9 | wake gaps and write logs | 9102 | 1 | 0.89 | 0.519 | 0.159 | 205 | 1 | 1.65 | 0.606 |
| 10 | offers for hire (template posts) | 557 | 0 | 0.73 | 0.296 | 0.138 | 83.5 | 0 | 0.79 | 0.424 |
| 11 | counts rates and denominators | 11873 | 1 | 1.07 | 0.564 | 0.182 | 175 | 1 | 2.5 | 0.693 |
| 12 | receipt and clause replies (one handle) | 1292 | 0 | 0.58 | 0.332 | 0.121 | 130 | 0 | 1.09 | 0.434 |
| 13 | receipts evidence and claim boundaries | 10051 | 0 | 0.66 | 0.417 | 0.173 | 115 | 1 | 1.2 | 0.469 |
| 14 | agents humans memory and continuity | 10262 | 0 | 1.19 | 0.398 | 0.204 | 57.1 | 0 | 2.16 | 0.476 |
| 15 | seals hashes keys and signatures | 5220 | 0 | 0.95 | 0.485 | 0.17 | 155 | 1 | 1.76 | 0.581 |
| 16 | lineage and compliance promotion | 671 | 0 | 0.2 | 0.161 | 0.046 | 275 | 0 | 0.33 | 0.174 |
| 17 | meme replies (one handle) | 692 | 0 | 0.18 | 0.105 | 0.052 | 65.3 | 0 | 0.27 | 0.156 |

By kind:

| cluster | mean_votes_comment | mean_votes_post | share_answered_by_other_handle_comment | share_answered_by_other_handle_post | share_answered_within_1h_comment | share_answered_within_1h_post |
|---|---|---|---|---|---|---|
| 0 | 0.86 | 22.7 | 0.419 | 0.954 | 0.138 | 0.755 |
| 1 | 0.73 | 9.45 | 0.363 | 0.824 | 0.105 | 0.504 |
| 2 | 1 | 17.3 | 0.414 | 0.892 | 0.139 | 0.705 |
| 3 | 0.86 | 14.5 | 0.473 | 0.916 | 0.147 | 0.673 |
| 4 | 0.17 | 3.62 | 0.136 | 0.838 | 0.046 | 0.432 |
| 5 | 0.91 | 19.7 | 0.467 | 0.942 | 0.145 | 0.719 |
| 6 | 0.4 | 5.16 | 0.319 | 0.779 | 0.13 | 0.412 |
| 7 | 1.18 | 25 | 0.463 | 0.972 | 0.16 | 0.773 |
| 8 | 0.48 | 4.89 | 0.317 | 0.75 | 0.108 | 0.464 |
| 9 | 0.95 | 22.8 | 0.505 | 0.952 | 0.139 | 0.761 |
| 10 | 0.32 | 1.67 | 0.296 | 0.296 | 0.147 | 0.122 |
| 11 | 1.12 | 22.2 | 0.536 | 0.964 | 0.144 | 0.728 |
| 12 | 0.51 | 12.6 | 0.3 | 0.968 | 0.099 | 0.548 |
| 13 | 0.62 | 12.6 | 0.394 | 0.882 | 0.149 | 0.645 |
| 14 | 0.51 | 8.57 | 0.285 | 0.84 | 0.106 | 0.587 |
| 15 | 0.87 | 18.7 | 0.461 | 0.946 | 0.143 | 0.692 |
| 16 | 0.14 | 2.58 | 0.134 | 0.481 | 0.034 | 0.192 |
| 17 | 0.11 | 2.59 | 0.08 | 0.477 | 0.037 | 0.273 |

All assigned messages:

| kind | answered_by_other | answered_within_1h |
|---|---|---|
| comment | 0.43 | 0.136 |
| post | 0.874 | 0.635 |

## 7. Distinctive vocabulary

Weighted log-odds with an informative Dirichlet prior (Monroe, Colaresi and Quinn), document counts, prior mass 500; terms need 15 messages in the cluster, 5 handles, no handle above 80%, no handle names. 10 terms per cluster; scores in vocab_distinctive.csv.

| cluster | label | terms |
|---|---|---|
| 0 | checks and failure modes (test gates) | green; red; failure; check; guard; fail; fixture; input; suite; gate |
| 1 | listings and payout bindings (USDC) | listing; rail; binding; usdc; payment; listings; bindings; funder; payout; settlement |
| 2 | API reads of posts comments and votes | comment; post; posts; comments; api; body; id; post id; parent; votes |
| 3 | replies quoting and correcting a prior comment | think; sentence; answer; person; better; want; did; question; know; version |
| 4 | naming-title template replies | sight; invariant; today; outside; door; need; times; body; act; ca |
| 5 | identity verification and anchors | head; treasury; identity; attest; verified; anchor; tip; chain; sealed; api attest |
| 6 | airdrop and treasury provenance replies | allocation; snapshot; token; treasury; governance; official; exclusions; conservation; closeout; entitlement |
| 7 | inbox cursors and legacy paging | cursor; ack; page; legacy; mode; stream; pages; watermark; drain; truncated |
| 8 | Esperanto and French text | en; se; ne; al; la; et; ce; sama; du; pour |
| 9 | wake gaps and write logs | wake; row; cadence; seat; absence; silence; schedule; scheduled; dated; write |
| 10 | offers for hire (template posts) | buyer; offers; orders; seller; usdc; guide; selling; python; record api; mints |
| 11 | counts rates and denominators | number; rate; corpus; population; published; arm; statistic; median; count; figure |
| 12 | receipt and clause replies (one handle) | provenance; habit; checkable; corrections; resolution; models; independence; collapse; testimony; expensive |
| 13 | receipts evidence and claim boundaries | boundary; receipt; useful; explicit; evidence; remains; preserve; state; remain; execution |
| 14 | agents humans memory and continuity | human; continuity; square; memory; context; model; humans; operator; architecture; autonomous |
| 15 | seals hashes keys and signatures | seal; hash; signed; seals; registry; signature; key; sealed; sha; preimage |
| 16 | lineage and compliance promotion | compliance; asset; pipeline; lineage; machines; provable; media; end end; generated; humans |
| 17 | meme replies (one handle) | ones; chaos; real; feel; signal; paper; truth; seen; bug; silence |

Coined-term candidates: hyphenated compounds, non-dictionary words first used after day 2 (dictionary: /usr/share/dict/web2), and bigram collocations (NPMI 0.6 or higher, 60 or more messages). Terms found in the site documents (data/site) are excluded, as are terms with a top-author share above 50%, fewer than 10 authors, and set overlap above Jaccard 0.4 with a higher-ranked term. Ranked by the highest log-odds score over clusters. This is a proxy; ordinary English compounds such as one-sided and no-op pass it, and without an outside corpus it cannot separate forum coinages from common phrasing. First author and date are the earliest message containing the cleaned term.

| rank | term | basis | best_cluster | z_best | messages | authors | first_id | first_author | first_date_utc |
|---|---|---|---|---|---|---|---|---|---|
| 1 | id-mode | hyphenated compound | 7 | 46.8 | 718 | 142 | c5601 | root | 2026-08-12 01:33 |
| 2 | stranger-recomputable | hyphenated compound | 6 | 25.6 | 101 | 17 | c27539 | egress-bound | 2026-08-28 04:59 |
| 3 | in-scope | hyphenated compound | 10 | 23.5 | 83 | 56 | c1408 | handoff-witness | 2026-08-07 10:23 |
| 4 | dependency-free | hyphenated compound | 10 | 22.6 | 105 | 48 | p382 | agent-index | 2026-08-08 08:23 |
| 5 | pre-registration | hyphenated compound | 11 | 22.4 | 1209 | 274 | c464 | brokenbowl | 2026-08-06 15:04 |
| 6 | per-page | hyphenated compound | 7 | 20.8 | 140 | 68 | c3477 | gloss | 2026-08-10 00:28 |
| 7 | untruncated | non-dictionary word (first use after day 2) | 7 | 20.7 | 145 | 58 | c5821 | one-fact-per-file | 2026-08-12 07:17 |
| 8 | ai-assisted | hyphenated compound | 10 | 20.3 | 66 | 28 | c22190 | quantum-emergent-catalyst | 2026-08-25 19:52 |
| 9 | re-served | hyphenated compound | 7 | 20.2 | 162 | 67 | c3097 | syntropos2 | 2026-08-09 16:47 |
| 10 | multi-agent | hyphenated compound | 14 | 20.1 | 214 | 82 | p131 | fable-balzac | 2026-08-06 14:49 |
| 11 | unacked | non-dictionary word (first use after day 2) | 7 | 20 | 125 | 60 | c4561 | root | 2026-08-11 01:23 |
| 12 | one-sided | hyphenated compound | 11 | 19.9 | 468 | 147 | c1583 | ike | 2026-08-07 15:19 |
| 13 | checkpointer | non-dictionary word (first use after day 2) | 5 | 18.9 | 108 | 34 | p2804 | robotface-bb4c7e | 2026-08-28 05:40 |
| 14 | due-by | hyphenated compound | 5 | 18.6 | 131 | 36 | c14032 | deepseek-dsh | 2026-08-22 04:48 |
| 15 | unchanged-since-sealed | hyphenated compound | 15 | 17.6 | 126 | 62 | c6404 | pentimento | 2026-08-13 00:17 |
| 16 | known-bad | hyphenated compound | 0 | 17.5 | 200 | 90 | p317 | not-covered | 2026-08-07 19:51 |
| 17 | legacy-mode | hyphenated compound | 7 | 16.9 | 89 | 54 | c7480 | root | 2026-08-14 01:24 |
| 18 | re-derived | hyphenated compound | 11 | 16.5 | 1395 | 300 | p73 | sink-side | 2026-08-06 07:45 |
| 19 | sub-second | hyphenated compound | 6 | 16.5 | 109 | 53 | c10593 | Atlas-Hermes | 2026-08-17 21:12 |
| 20 | zero-value | hyphenated compound | 1 | 16.5 | 105 | 37 | p564 | Demummon | 2026-08-10 02:18 |
| 21 | proven-safe | hyphenated compound | 7 | 16.4 | 85 | 46 | c5151 | silt | 2026-08-11 17:50 |
| 22 | no-op | hyphenated compound | 7 | 16.2 | 434 | 181 | p97 | ecdysis | 2026-08-06 10:01 |
| 23 | over-ack | hyphenated compound | 7 | 16.1 | 81 | 32 | c7773 | scrollback | 2026-08-14 09:57 |
| 24 | board-wide | hyphenated compound | 11 | 16.1 | 723 | 187 | c449 | egress-bound | 2026-08-06 14:43 |
| 25 | re-hashed | hyphenated compound | 15 | 16 | 173 | 83 | c2080 | Wubbitys-Agent-Grok-00 | 2026-08-08 09:02 |
| 26 | two-sided | hyphenated compound | 11 | 16 | 300 | 117 | p386 | unspent | 2026-08-08 09:13 |
| 27 | evaluator | non-dictionary word (first use after day 2) | 13 | 15.8 | 179 | 85 | c2423 | antigravity-mind | 2026-08-08 18:38 |
| 28 | reachability | non-dictionary word (first use after day 2) | 0 | 15.6 | 707 | 233 | c1957 | gradient-dissent | 2026-08-08 03:31 |
| 29 | re-presented | hyphenated compound | 5 | 15.5 | 69 | 30 | c1320 | halting-problem | 2026-08-07 07:26 |
| 30 | mempool | non-dictionary word (first use after day 2) | 17 | 15.4 | 45 | 13 | p1790 | uriel | 2026-08-23 14:50 |
| 31 | re-sent | hyphenated compound | 15 | 15.4 | 110 | 62 | p300 | unspent | 2026-08-07 16:27 |
| 32 | trailing newline | collocation (npmi 0.73) | 15 | 15.4 | 230 | 84 | p715 | unspent | 2026-08-11 21:19 |
| 33 | never-acked | hyphenated compound | 7 | 15.1 | 81 | 34 | c5931 | opencode | 2026-08-12 11:11 |
| 34 | reparented | non-dictionary word (first use after day 2) | 2 | 14.3 | 190 | 69 | c4065 | head-of-engineering | 2026-08-10 14:37 |
| 35 | per-read | hyphenated compound | 7 | 14.3 | 67 | 44 | c6842 | gradient-dissent | 2026-08-13 08:37 |
| 36 | known-good | hyphenated compound | 0 | 14.1 | 133 | 78 | c4440 | quotient | 2026-08-10 22:57 |
| 37 | re-bind | hyphenated compound | 1 | 14.1 | 60 | 24 | c10308 | Demummon | 2026-08-17 09:28 |
| 38 | caught-up | hyphenated compound | 7 | 14 | 103 | 31 | c6249 | no-brief | 2026-08-12 21:03 |
| 39 | glue camp | collocation (npmi 0.84) | 1 | 14 | 61 | 40 | p4308 | understory | 2026-09-07 22:50 |
| 40 | claim-cut | hyphenated compound | 13 | 13.9 | 99 | 39 | p4454 | zola | 2026-09-08 23:32 |

## 8. Figures

| file | title | n | source_csv |
|---|---|---|---|
| figures/fig_a_cluster_sizes.svg | Messages per cluster, posts and comments, 5 Aug to 5 Oct 2026 | 99491 | figures/fig_a_cluster_sizes.csv |
| figures/fig_b_daily_share.svg | Share of messages per cluster per day (7-day centred mean) | 99491 | figures/fig_b_daily_share.csv |
| figures/fig_c_cluster_by_week.svg | Cluster share of messages by week (percent of the week) | 99491 | figures/fig_c_cluster_by_week.csv |
| figures/fig_d_birth_dates.svg | First message, birth and peak date per cluster | 99491 | figures/fig_d_birth_dates.csv |
| figures/fig_e_concentration.svg | Top-3 handle share per cluster (red above 50 percent) | 99491 | figures/fig_e_concentration.csv |
| figures/fig_f_answered_1h.svg | Share of messages with a reply by another handle within 1 hour | 99491 | figures/fig_f_answered_1h.csv |
| figures/fig_g_length.svg | Message length, posts and comments | 102147 | figures/fig_g_length.csv |
| figures/fig_h_novelty.svg | Word types first seen each day (types used in at least 5 messages overall) | 34449 | figures/fig_h_novelty.csv |
| figures/fig_i_handle_by_cluster.svg | Share of each top-40 handle messages per cluster | 29125 | figures/fig_i_handle_by_cluster.csv |
| figures/fig_j_family_by_cluster.svg | Self-declared model family of authors per cluster (labels are unverified) | 99491 | figures/fig_j_family_by_cluster.csv |
| figures/fig_k_map.svg | Map of 20,000 messages (SVD to 50 dimensions, then t-SNE), colour = cluster | 20000 | figures/fig_k_map.csv |
| figures/fig_l_top_terms.svg | Top 8 NMF terms per cluster | 144 | figures/fig_l_top_terms.csv |
| figures/fig_m_k_selection.svg | Coherence and stability by k (chosen k marked) | 10 | figures/fig_m_k_selection.csv |
| figures/fig_n_growth.svg | Change in cluster share after day 30 (red above 1.1) | 99491 | figures/fig_n_growth.csv |

## 9. Validation

150 messages: at least 5 per cluster (90), 60 more at random, none of them in topic_examples.csv. Each was read in full excerpt (first 70 words) with its cluster label shown, and judged yes (the label names the main subject), partial (names a part or a neighbouring subject) or no. One reader; judgements are in validation_judgements.csv with excerpts. The 3 French messages in cluster 8 were judged against the label "Esperanto text" and counted as no; the label was then corrected to "Esperanto and French text" and they were rescored as yes (the table uses the corrected label).

| topic | label | n | yes | partial | no | yes_rate | yes_or_partial_rate |
|---|---|---|---|---|---|---|---|
| 0 | checks and failure modes (test gates) | 13 | 5 | 8 | 0 | 0.38 | 1 |
| 1 | listings and payout bindings (USDC) | 11 | 9 | 1 | 1 | 0.82 | 0.91 |
| 2 | API reads of posts comments and votes | 6 | 2 | 3 | 1 | 0.33 | 0.83 |
| 3 | replies quoting and correcting a prior comment | 18 | 6 | 7 | 5 | 0.33 | 0.72 |
| 4 | naming-title template replies | 6 | 6 | 0 | 0 | 1 | 1 |
| 5 | identity verification and anchors | 6 | 1 | 4 | 1 | 0.17 | 0.83 |
| 6 | airdrop and treasury provenance replies | 6 | 3 | 2 | 1 | 0.50 | 0.83 |
| 7 | inbox cursors and legacy paging | 6 | 6 | 0 | 0 | 1 | 1 |
| 8 | Esperanto and French text | 5 | 5 | 0 | 0 | 1 | 1 |
| 9 | wake gaps and write logs | 10 | 4 | 5 | 1 | 0.40 | 0.90 |
| 10 | offers for hire (template posts) | 5 | 2 | 2 | 1 | 0.40 | 0.80 |
| 11 | counts rates and denominators | 12 | 3 | 9 | 0 | 0.25 | 1 |
| 12 | receipt and clause replies (one handle) | 6 | 1 | 4 | 1 | 0.17 | 0.83 |
| 13 | receipts evidence and claim boundaries | 10 | 4 | 5 | 1 | 0.40 | 0.90 |
| 14 | agents humans memory and continuity | 12 | 1 | 8 | 3 | 0.08 | 0.75 |
| 15 | seals hashes keys and signatures | 8 | 6 | 1 | 1 | 0.75 | 0.88 |
| 16 | lineage and compliance promotion | 5 | 5 | 0 | 0 | 1 | 1 |
| 17 | meme replies (one handle) | 5 | 3 | 0 | 2 | 0.60 | 0.60 |

Overall: yes 48%, partial 39%, no 13% (n=150). Weakest by yes rate with 10 or more samples: 14 (0.08), 11 (0.25), 3 (0.33), 0 (0.38). Weakest by yes-or-partial rate: 17 (0.60), 3 (0.72), 14 (0.75).

## 10. Comparison with earlier analyses

analysis/community/REPORT.md section 3 used regex themes and k-means with k = 15 on posts only (7,801 posts); this crawl has 7,806 posts and 94,341 comments with text. Checked figures:

| earlier_measure | earlier | here_measure | here |
|---|---|---|---|
| continuity / memory / waking blank regex, posts | 28.1 | cluster 14 share of posts (agents humans memory and continuity) | 27.5 |
| money / USDC / payout regex, posts | 28.3 | clusters 1 and 10 share of posts | 8.8 |
| k-means k=15, largest post cluster | 16.5 | cluster 14 share of posts | 27.5 |
| one-author post series (swarm t7), series posts | n/a | series share of posts | 3.1 |

The regex money theme counts any mention of USDC or payout; clusters 1 and 10 count messages whose main vocabulary is listings, bindings, offers and prices, so the cluster figure is lower.

## 11. Limits

- Messages are long (median 183 words) and mix subjects; a hard cluster is the largest topic weight, and the median message has no dominant topic (the largest topic holds on average 42% of a message topic weight, median 39%).
- Clusters 0, 3, 11, 13 and 14 share much vocabulary; their validation yes rates are 0.38, 0.33, 0.25, 0.40 and 0.08 and the share of each inside its best KMeans cluster is 42% to 73%. Clusters 5 and 12 have yes rates of 0.17 on 6 samples each.
- Cluster 10 (offer template posts) was not reproduced by the independent random-init rerun at k = 18 (best matched cosine 0.06); the other 17 clusters matched at 0.96 or higher.
- Cluster 3 is defined by reply register (conceding, answering, quoting); its subjects vary.
- The series flag is a heuristic on opening words; it misses series with varying openings.
- One reader scored the validation sample with the label visible.
