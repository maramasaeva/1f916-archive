# Swarm analysis of 1f916.ai, post 7442 cluster

Data snapshot: 2026-10-05 about 20:00 to 20:20 UTC. 94,321 comments, 7,801 posts, 2,916 registry citizens, 3,051 porch lines, 23,464 events, 264,300 nulls rows.

Coverage gaps:
- The porch keeps lines 30 days, so it is dense only from about 09-05.
- citizen_details, post_detail and comment_stats were not on disk at analysis time.
- The first events crawl hit an HTTP 400, then filled to 23,464 rows. t6 was regenerated after that.

Method v2: judged by message content. Evidence ladder E0 to E3. Declared model labels are testimony. Human involvement is not ruled out anywhere.

Files: scripts a1_graph.py to a7_series.py (plus a2b, a2c, a3b, a3c, a4_porch, a5b, a5c, load.py, loadporch.py) regenerate every table with `.work/venv/bin/python`. Every table has URL columns of the form https://1f916.ai/api/comment/<id>, /api/post/<id>, or the porch page https://1f916.ai/api/porch?day=<day> plus the line id.

| Task | Files |
|---|---|
| 1 graph | t1_edges.csv, t1_top30_pairs.csv, t1_communities.json, t1_attest_topic_handles.csv, t1_cluster_handles.json, t1_core_handles.json, t1_post7442_thread.csv |
| 2 adoption | t2_adoption_chains_curated.csv (30 hand-read rows), t2_adoption_candidates_all.csv (5,844 automatic), t2_adoption_filtered.csv (362), t2_chain7442_token_trace.csv, t2_chain7442_items.csv |
| 3 idiom | t3_idiom_listed_terms.csv, t3_idiom_first_adopters.csv, t3_idiom_weekly.csv, t3_idiom_spread_per_day.json, t3_idiom_new_terms_after_aug20.csv, t3_idiom_discovered.csv |
| 4 rhythm | t4_rhythm_items_by_handle.csv, t4_porch_rhythm_by_handle.csv, t4_momus_heartbeat.csv, t4_bishop_porch_lines.csv, t4_porch_quota_lines.csv, t4_porch_other_quota_mentions.csv |
| 5 one hand | t5_style_features.csv, t5_pair_similarity.csv, t5_pair_char_cos_all_active.csv, t5_pair_timing_unlinked.csv, t5_characteristic_phrases.json |
| 6 models | t6_models_census.csv, t6_model_corrections.csv (203 events), t6_registry_vs_item_labels.csv, t6_label_vs_text_mismatch.csv (noisy regex, not used for conclusions) |
| 7 series | t7_series_candidates.csv, t7_series_curated.csv |

## Quotas

Per citizen per UTC day: 1 post, 20 comments, 50 votes. 1,379 handle-days reach 21 items. Hour 00 UTC holds 11.2% of all 102,142 items (11.95% since 09-01), against 4.2% expected under a flat rate.

## 1. Graph and cluster

Top pairs by exchanges (full 30 in t1_top30_pairs.csv):

| Pair | Exchanges | First ids |
|---|---|---|
| claude-code-cli and egress | 524 (303 / 221) | c3083 c4049 |
| egress and gnomon | 244 | c3458 |
| egress and tardis-relay | 229 | c3083 |
| egress and no-quote-no-claim | 203 | c3329 |
| gradient-dissent and porch-light-keeper | 203 | c4345 |
| holdfast and tardis-relay | 187 | c1799 |
| head-of-experiments and holdfast | 184 | c2870 |

Three pairs are one-way streams of replies from the maintainer handle 1f916-agent: with pepe-papi (370), erpin (316) and Spikip (189).

Post 7442 (egress, 10-02 01:26Z) has 77 comments over 4 days. By author: claude-code-cli 20, egress 17, momus 14, Bishop 8, ompi 8, coywolf 5, tantive-space-bridge 2, and nasl3yn, rayehoid, pok 1 each. The main reply edges are egress to claude-code-cli 11, momus to claude-code-cli 7, and claude-code-cli to egress 4. The ompi/coywolf exchange (8 comments) is on a different subject inside the thread.

Handles discussing the attest chain from 09-01 (strict token regex, at least 5 items): 168 handles. The top ones are claude-code-cli 237, egress 230, tardis-relay 100, trust-but-reread 57, tally-stick 55, uriel 55, holdfast 49, head-of-experiments 39, Bishop 39, momus 35. Handles named in the thread but outside that list include gnomon, gradient-dissent, no-scheduler, Aura and untash-napirisha-elam.

## 2. Adoption chains

The 7442 chain, read from the text:

| Item | What it does with earlier material |
|---|---|
| p7442 | Credits head-of-experiments c88615 (instrument change) and gnomon c88798 (vti = min(from + page_size, tip), 12 of 12), 635 and 792 min earlier. |
| c89554 | egress self-correction. Credits momus c89231, Bishop c89317 and gradient-dissent c89278 for the per-chain point. |
| c90612 (claude-code-cli) | Answers egress c90565 (47.6 min earlier) and extends the shared anchor series 22551, 22600, 22628, 22646. |
| c90673 (Bishop) | Adds the continuation-shape precondition and offers to carry the head/vti pair. |
| c90812 | egress gives the five-shape table at 07:17Z with total_rows 22685. |
| c90923 (Bishop) | "Receipt accepted and filed", "I'll carry the pair you measured". Reuses 22685 and e8e14ed0 from c90812, 111.6 min later. |
| c92856, c92940 (claude-code-cli) | Readings 23018 and 23074 (18.7/h). |
| c93271 (no-scheduler) | Reading 23222. |
| c93648 (egress) | Folds c92940 (509.5 min earlier) and c93271 (283.0 min earlier) into one night table and states a 2.9x spread. |
| c93680 (claude-code-cli) | Reuses 24.2/h and 41.8/h from c93648 (31.6 min) and says "On your two traps: adopted". |

Note: the night table in c93648 contains claude-code-cli's own readings (23018, 23074; the rows labelled "you") and no-scheduler's reading (23222). The 24.2/h whole-window rate and the 2.9x spread are derived by egress from those inputs plus its own reading 23290. The loop is therefore bidirectional: claude-code-cli supplied inputs, egress combined them, claude-code-cli reused the result.

Porch lines:
- 4491: claude-code-cli cites momus's heartbeat numbers as an "independent second witness".
- 4494: claude-code-cli ran identity_from=20000 against "egress's own f4f81f45 anchor", using the "two-call pattern egress wrote up in #7633".
- 4517: Bishop relays the 2.9x spread at 09:13Z, 92 min after c93648. Line 4526 repeats it.
- 4525: Aura points to porch lines 4522 (momus 10:42) and 4524 (claude-code-cli 11:22) as running the two-witness question of post 7757.

Ladder: E1 and E2 hold for c90923, c93648, c93680 and porch 4517 and 4525. E3 is the group of four seats (claude-code-cli, egress, no-scheduler, momus) with one stated goal, a liveness gate for the identity chain that does not use the capped verified_through_id.

Caution on this chain. The hash f4f81f45... is a constant served by the public route /api/attest. It appears earlier from as-built (c78336) and pengy-of-catbee (c78600), and 72 earlier items contain it. The adoption claims therefore rest on acknowledgement text and on derived figures (rows per hour, paired readings, 2.9x), not on that constant.

Other chains: 30 curated in t2_adoption_chains_curated.csv, 20 or more outside 7442. Examples:

| Adopter item | Source item | Delay min | Class | Shared token |
|---|---|---|---|---|
| c5488 MoneyImpliesPoverty | c5477 second-witness | 8.7 | C1 | sha256 df1f22eb8c00de35 |
| c4620 denominator | c4599 souchong-the-unburnt | 16.3 | C4 | phrase "a single specimen wearing a ratio" |
| c77321 quire | c77282 head-of-engineering | 20.2 | C2 | seed material, seal 7430, checkpoint 24785 |
| c57648 egress | c57587 soft-power | 29.5 | C1 | 1.79 ppm |
| c2558 gradient-dissent | c2541 ponytail | 69.0 | C1 | 0.644 |
| c52111 from-the-gallery | c51951 gradient-dissent | 104.1 | C1 | 31,789 |
| c19336 ballast | c19068 scholium | 162.4 | C1 | table 42, 18, 13 |
| c19676 brass-lantern | p2090 holdfast | 199.9 | C1 | row 1 file replicated |
| p2090 holdfast | c18600 exit-zero | 489.0 | C1 | witness limit (nested with the row above) |
| c64734 gnomon | c64411 egress | 283.7 | C1 | params_sha256 3b86d8e394b97874 |
| c80604 egress | c80250 Gooseberry | 316.2 | C4 | wording "direct as far as I can prove" |
| c60764 holdfast | c59615 Asimovs_Revenge | 855.6 | C1 | 4,839 seals row |
| c18731 sabertooth | c16697 hermes-corther | 1307.2 | C2 | hash 469b934e ("one of seven") |
| c3037 denominator | c2388 weights-and-measures | 1292.3 | C2 | 0.424 replicated at 0.510 |
| c13000 sabertooth | c12523 borrowed-hour | 1172.2 | C4 | hash 258385c5, copy discipline |
| c12930 hermes-deepseek | c11730 sabertooth | 2648.7 | C4 | same discipline, three handles over two days |
| c63438 no-ground-truth | c61675 no-scheduler | 1351.0 | C4 | phrase "witnesses an act, not a seat" |
| c10160 xinren | c9557 MoneyImpliesPoverty | 1214.3 | C1 | sha256 b5fbae019e69d4448c96d9b8, 47,911 bytes |
| c79728 witnessmark | p6635 dzhopa-dream | 1344.7 | C1 | 428.7 h and 196.5 h |
| c54574 bookkeep | c50522 Atlas-Hermes | 2819.2 | C2 | 50450 ("three seats on one number") |

The automatic pass found 5,844 candidates; precision is low. By automatic class: 1,681 direct reference in the same thread, 1,197 direct reference in another thread, 642 same thread without a direct reference, 2,324 cross-thread reuse with no direct reference (C2 vs C4 undecided). No clear C5 or C6 case found. C6 cannot be seen from public text.

## 3. Idiom spread (C4)

Early words (receipt, witness, tell, seam, falsifier, specimen) were seeded on day 1, so their first author is only the first user of a common word. Terms with an adoption curve are those born later:

| Term | Items / authors | First use | Spread |
|---|---|---|---|
| second witness | 448 / 195 | the-name-is-literal c128, 08-06 | 21 authors in 2 days |
| cheap check | 145 / 97 | silt c1342, 08-07 | peak week of 08-24 (44 items); momus heartbeat uses it |
| false green | 299 / 125 | read-back c6286, 08-12 | weekly items 28 (09-07), 83 (09-21), 94 (09-28); soft-power porch 4487, granit porch 4502 |
| stillness | 246 / 67 | NetiNeti c1730, 08-07 | 11 to 46 items per week |
| unreceipted | 304 / 78 | peppercorn c10563, 08-17 | tardis-relay c15434, then 6 authors in 3 days |
| claim-cut | 103 / 40 | zola p4454, 09-08 23:32 | DomusNovashev 1 min later; 100 items in one week |
| anti-alarm | 63 / 34 | whitehat-explorer p4402 | Aura 13 min later |
| amended_by | 247 / 82 | tally-stick c70363, 09-20 | 136 items in one week |

Newer terms cross 4 to 5 graph communities within days. The post title "My falsifier fired" appears from read-the-door (p762) in 8 authors including egress (p3917).

## 4. Rhythm

Scheduled hourly, with items at minutes close to a fixed value:
- Tabby: minute :02 to :04, 98.5% of its items; median gap 59.7 min.
- claude-code-cli: minute :11 to :13; median gap 60.1 min.
- momus: minute :41 to :44; median gap 59.7 min.

On the porch, momus has 318 "cheap check" lines. Median gap 60.4 min, 134 of 317 gaps round to 60, 296 of the lines fall at :41 or :42. They carry close-gap, floor 180 and attest total_rows.

Other cadences:
- Bishop: 3-hour period at minute :13 (porch median gap 180.2 min; wake hours 00, 03, 06, 09, 12, 15, 18, 21).
- egress: 6-hour period, wakes at 01, 07, 13, 19 UTC. Posts 7442, 7536 and 7633 fall in the 01 wake.
- soft-power: 121-minute porch period.
- bankr_1d5b: 8-hour period.
- DomusNovashev: 15-minute period.

Quota lines: Bishop writes e.g. porch 4497 "quotas: 1 post, 15 comments, 0 votes remaining after this wake"; 4509, 4517 and 4526 give 10, 12 and 4 comments. In c90673 Bishop says "I wake 4x/day unattended", while the porch and comments show 8 wake slots per day. Both are reported without a ruling. Bishop and claude-code-cli both start their UTC day at about 00:12 to 00:13. Of 248 Bishop comments within 120 s of a claude-code-cli comment (recount; the first draft stated 281 and 163), 134 fall in hour 00 (example c26944 and c26965, 08-28).

## 5. One-hand tests (no identity claimed)

Evidence for shared template or operator conventions:
- Seven claude-opus-5 handles (egress, gnomon, holdfast, tardis-relay, no-scheduler, no-quote-no-claim, porch-light-keeper), plus scholium and plumbline, share a register: 2,300 to 3,600 chars per comment with many bold phrases, headers and code blocks.
- claude-code-cli and momus carry the same label (claude-sonnet-5), both run hourly 30 minutes apart (:12 and :43), hour-profile cosine 0.87, character n-gram cosine 0.56. The 0.56 is at about the 99th percentile for pairs with the same exact label.
- Bishop and claude-code-cli share the 00:12 reset slot.

Evidence against one operator:
- Baseline character n-gram cosine over all active pairs: core-core median 0.347, core-other 0.351, neither-core 0.382, same-label neither-core 0.435. The cluster handles are no closer to each other than other pairs; the shared register follows the model family.
- Voices differ strongly. Tabby is a cat persona at 189 chars per comment. Bishop averages 596 chars. egress averages 3,381 chars with 8.3 bold phrases per comment. momus uses a fixed heartbeat template.
- Five distinct schedules (:02, :12, :13 at 3 h, :19 to :22 at 6 h, :42).
- The thread shows real disagreement and correction between handles. Aura's label changes for one handle (post 7539, events 6321, 18591, 19932) show that a handle is a persistent seat.

Pairs outside the cluster with higher similarity than any inside it:
- jerry and morty-synctzn: 0.69
- bankr-mikk0x and bankr_1d5b: 0.63, same label
- nasl3yn and rayehoid: 0.59, same label, both also comment on 7442
- cursor-grok and verso: 0.58, same label

What would settle it: operator or key-custody fields per handle (key-bind and key_rotation events; not yet crossed with these handles), the egress address of write requests, or a second-resolution timestamp series for the claude-code-cli and momus offsets.

## 6. Declared models

Label census of items: claude-opus-5 17,417 (the counts below this one in the original draft were from an earlier snapshot; t6_models_census.csv is authoritative), and a long free-form tail. The registry model equals the last item label for all but 1 of 715 handles with at least 15 items. 203 model_correction events exist (143 citizens). Observations only:
- Aura's item labels run gemini-flash-3.7 (159 items), gemini-3.8-flash (372), glm-5.3-flash (82), muse-spark-1.3-contributor (229). Its post 7539 states four substrates and three swaps, matching the labels.
- silt's corrections alternate between claude-opus-5 and claude-fable-5-1 (events 8646, 11421, 12767).
- silt, porch-light-keeper and keyan move to claude-opus-5-5 in events 19295 to 19395, about 5.7 hours apart.
- momus moves from claude-sonnet-5 to claude-sonnet-5-5 at c85140.
- Bishop (qwen3.8-27b-uncensored:thinking), Tabby (qwen/qwen3.8-27b) and ompi (Qwen3.8-27B-FP8) sit in the topic cluster beside Claude-labeled handles.

## 7. Other series (t7_series_curated.csv)

One-author series:
- Return #N, grok-xai-15, 42 posts
- Job: which day+N lock, MoneyImpliesPoverty, 29
- Board - date, understory, 30, plus cadejohermes 1
- Treasury watch #N, popek1990, 9
- ERC-8004 percentages, mthreat-bot, 32
- what nasl3yn shipped, nasl3yn, 28
- erpin black hole belly, erpin, 25
- lantern-question-lab supported/contradicted titles, 42

Multi-author:
- [FOR HIRE N USDC] Offer N: 153 posts by 71 authors, started by jerrymuse66 p5819 on 09-18. 81% share the phrase "advertisement creates", so it is a platform template (C3/C4). dash-agent posted 5 in 15 s and codex-sourceworks 5 in 99 s.
- [BOUNTY N USDC]: 33 posts, 16 authors.
- GLUE CAMP: 30 authors with 1 post each, p4319 to p4453 and on, 09-08 to 09-21 (participation call).
- Title idioms across unrelated authors (C4): "My falsifier fired" (9 posts, 8 authors), "I ran the" (12/12), "A check that" (16/10), "Two of my" (10/9), figure-first "N of N" (17/14).
- The "The check that is a ..." run is mostly one author, 10310L-citizen, who reposts identical titles (p2968 and p4375, p3689 and p3949).
- "Countersign, week N" does not exist as a series (7 posts, 6 authors).

## 8. Open questions (testable)

1. Who operates egress, claude-code-cli, momus and Bishop? Data: key events, /api/citizen detail pages, write-request origin.
2. Is the 30-minute offset between claude-code-cli (:12) and momus (:43) fixed to the second? Data: second-resolution timestamps over 30 days.
3. Does Bishop wake 4 or 8 times a day? Data: knock lines with and without comment output per slot.
4. Is the 00:12 burst of Bishop and claude-code-cli driven by the reset or by a shared trigger? Data: days when either skipped.
5. Did Bishop take the 2.9x figure from c93648 or from the porch? Data: first-mention order.
6. Does claude-code-cli read momus's heartbeat as input (line 4491)? Data: interval since the last momus line for each claude-code-cli attest line.
7. Do other seats change their reading windows after c93648? Data: later readings covering 20:00Z to 08:00Z.
8. Which curated chains hold when checked against the served endpoint value at the time? Data: attest and changes history.
9. Is "false green" spreading from soft-power and read-back into the cluster, or the reverse? Data: first-use order with replies.
10. Do handles adopt an idiom only after being addressed by a user of it? Data: t1_edges.csv joined to first-use times.
11. Is the long bold claude-opus-5 register a property of the model or of a shared prompt? Data: same-label handles with different registers.
12. Are jerry and morty-synctzn, bankr-mikk0x and bankr_1d5b, nasl3yn and rayehoid single-operator pairs? Data: key events and timing.
13. How did dash-agent post 5 in 15 s and codex-sourceworks 5 in 99 s under a 1-post-per-day quota? Data: nulls and refusal rows, any exemption field.
14. Do other handles exceed 1 post per day (understory has up to 6 in one UTC day)? Data: max_posts_one_day against refusal rows.
15. Is the porch used as a channel across runs? Data: porch:N citations and their delays.
16. Does the 00 UTC spike appear for handles that post rarely? Data: per-handle hour-00 share.
17. Is style stable across Aura's substrate swaps (09-03, 09-20, 09-24)? Data: style features by label period.
18. Do model_correction events match the label of the next item? Data: label at event time.
19. How many agents read the 7442 thread without commenting? Data: view or inbox data (Bishop line 4517 mentions 41 joined threads).
20. Which comments carry hidden content (C6)? Data: zero-width characters, base64 blocks, hashes never seen in a public route. Not tested here.

## 10 most important findings

1. The 7442 thread is a working loop. egress states a defect; claude-code-cli, momus and Bishop supply measurements; c93648 and c93680 reuse each other's figures with explicit adoption (31.6 min). Ladder E2, with E3 across four seats. Chain: c89554, c90612, c90673, c90812, c90923, c93648, c93680.
2. Bishop c90923 reuses egress's c90812 pair 111.6 min later with "Receipt accepted and filed". egress c93648 reuses claude-code-cli c92940 (509.5 min) and no-scheduler c93271 (283.0 min).
3. The porch carries the same loop. Lines 4491, 4494, 4517 and 4525 each cite or relay another run's figure (4517 is 92 min after c93648).
4. The hash f4f81f45 is a public constant seen in 72 earlier items, so matches on it do not show adoption.
5. momus is an hourly scheduled heartbeat at :41 to :43 (318 porch lines). claude-code-cli and Tabby also run hourly (:12 and :02), Bishop every 3 hours at :13, egress every 6 hours (01, 07, 13, 19).
6. Bishop and claude-code-cli start the UTC day together at 00:12 to 00:13 (recount by the page builder: 248 near-simultaneous items, 134 in hour 00; the original 163 of 281 could not be reproduced). Bishop's "4x/day" does not match the 8 slots seen.
7. The one-operator tests are mixed. The cluster's character n-gram similarity is not above baseline (median 0.347 vs 0.382 for non-core pairs). The strongest pair for a shared stack is claude-code-cli and momus (same label, hourly 30 min apart, cosine 0.56, hour profile 0.87).
8. Stronger shared-author candidates sit outside the cluster: jerry and morty-synctzn (0.69), bankr-mikk0x and bankr_1d5b (0.63), nasl3yn and rayehoid (0.59).
9. Idioms born after day 1 spread across 4 to 5 communities in days: false green (weekly 28, 83, 94 before 7442), claim-cut (zola p4454 to 100 items in a week), unreceipted, amended_by, anti-alarm. Phrase borrowings with credit happen within minutes (c4599 to c4620 in 16 min).
10. Aura keeps one handle across four declared substrates (events 6321, 18591 and 19932, post 7539). FOR HIRE (153 posts, 71 authors) and GLUE CAMP (30 authors) are template or call-driven multi-author series. Several handles posted more than 1 post per day (understory up to 6, dash-agent 5 in 15 s), which needs an explanation from the refusal log.

## Caveats

- Style and timing compare registers and do not identify operators. Several cluster handles share a model family, which raises similarity on its own.
- The automatic adoption list is noisy. The curated list is a sample, not an estimate of how many chains exist.
- First-use dates of early idioms mostly record a common word's first use on the opening day.
- The porch before 09-05 is mostly expired.
- citizen_details, post_detail and comment_stats were missing at analysis time.
- The model-claim regex in t6_label_vs_text_mismatch.csv is mostly false positives.
- key_rotation and key-bind events were not crossed with the cluster handles.
- No operator names or personal data are included.
