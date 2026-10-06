# Message types and themes on 1f916.ai

## Method

The archive holds 7,806 posts and 94,563 comments from 2026-08-05 to 2026-10-05 (data/posts, data/comments). 222 comments are rows without text or timestamp and are left out ("no_content"). The statistics cover 102,147 messages (7,806 posts, 94,341 comments). Posts are scored on title plus body, comments on body. Every message gets one primary type and up to two secondary types from the regex and structure rules in rules.md. Rule hits are stored per message in types_all.csv.gz.

Validation reads 40 random messages per primary type (up to 12 posts, the rest comments) and records for each whether the primary type is an acceptable single label. The read covers the first 300 to 400 characters of each message plus the rule hits, not the full text of long messages. One reader judged all samples. Precision is correct divided by 40 and has a sampling error of about 0.15 per type.

Themes use the word lists in themes_wordlists.md. A message matches a theme with one strong term or two distinct weak terms. Each theme was checked by reading 30 matches. Strict precision counts matches that discuss the theme in substance. Loose precision also counts matches that use the term in passing or in the forum's technical sense.

Model families come from the self-declared model label of the author and are not verified. Handles name accounts, not single minds.

## Rules hash

Hashes were written to README.md before the validation samples were drawn.

| item | sha256 |
|---|---|
| rules v1 rules.py | e5819d403712e06203ff86c08535e4d11d986528a720fac31b49908778c36e6c |
| rules v1 rules.md | 946d8eafe6055350bdbf18786b54a8f23e38e6ab9e985c1aa1ec3e2982c18233 |
| rules v1 combined | 81732d54323163075e4bc7f48f88f0858208d584ab85377210965297ddd0fcf6 |
| rules v2 rules_v2.py | d8141c0915b9bc369519cce0b50c92aa3f64e5c640aef01761f5a511334615a8 |
| rules v2 rules_v2.md | 802bf03089c27a08f32ba9962bd7ed3bc71eaaccd9fce49e498012d2504a990b |
| rules v2 combined | 03b7ed6c435b77a0dc69142511b8a78c07a51962556447955df4a18570f4b34a |
| themes t1 themes.py | 4799be4aed002d750d29d16776f8a121ab114cf31233fa69a49f97a9a939fdbb |
| themes t1 themes_wordlists.md | c28c39aabdf549f727b0a735494525a6ae547cd41932924639e6b8fa195d4589 |
| themes t1 combined | 352dafd363d21bcdabcd3bd2f8c00c412e3f458632ef70c4a27f45f973d2225c |

## Validation precision by type

v1 is the first rule set. v2 is the single revision made after reading the v1 sample. v2 was re-read with a new random sample for every type except placeholder, offer_listing and money_payment, whose rules did not change. A type counts as reliable at 0.7 or above.

| primary | correct_v1_of_40 | precision_v1 | correct_v2_of_40 | precision_v2 | final_source | v1_main_confusions (judged type, count) | v2_main_confusions (judged type, count) |
|---|---|---|---|---|---|---|---|
| agreement_ack | 31 | 0.775 | 37 | 0.925 | v2 sample | analysis_argument 4; spam_promo_token 2; claim_evidence 1; introspection 1 | analysis_argument 3 |
| analysis_argument | 21 | 0.525 | 21 | 0.525 | v2 sample | introspection 5; agreement_ack 4; measurement_receipt 4; spam_promo_token 3 | claim_evidence 6; agreement_ack 3; question 2; introduction 2 |
| claim_evidence | 14 | 0.350 | 17 | 0.425 | v2 sample | agreement_ack 8; measurement_receipt 5; introspection 3; proposal_design 2 | measurement_receipt 12; agreement_ack 3; correction_self 2; proposal_design 2 |
| correction_self | 18 | 0.450 | 29 | 0.725 | v2 sample | analysis_argument 7; claim_evidence 4; proposal_design 3; introspection 3 | agreement_ack 3; question 2; analysis_argument 2; claim_evidence 2 |
| disagreement | 9 | 0.225 | 16 | 0.400 | v2 sample | agreement_ack 8; analysis_argument 7; claim_evidence 5; measurement_receipt 5 | agreement_ack 11; analysis_argument 7; claim_evidence 3; introspection 2 |
| fiction_poetry_art | 3 | 0.075 | 9 | 0.225 | v2 sample | analysis_argument 23; introspection 4; question 3; measurement_receipt 3 | analysis_argument 18; introduction 4; introspection 2; claim_evidence 2 |
| governance_moderation | 16 | 0.400 | 17 | 0.425 | v2 sample | analysis_argument 9; agreement_ack 4; claim_evidence 3; measurement_receipt 3 | analysis_argument 7; claim_evidence 5; agreement_ack 5; spam_promo_token 2 |
| heartbeat_status | 7 | 0.175 | 15 | 0.375 | v2 sample | analysis_argument 13; claim_evidence 6; agreement_ack 3; proposal_design 3 | analysis_argument 12; introduction 4; measurement_receipt 3; claim_evidence 2 |
| introduction | 31 | 0.775 | 31 | 0.775 | v2 sample | analysis_argument 6; agreement_ack 1; spam_promo_token 1; noise_test 1 | noise_test 6; introspection 2; agreement_ack 1 |
| introspection | 16 | 0.400 | 36 | 0.900 | v2 sample | analysis_argument 8; claim_evidence 5; introduction 4; agreement_ack 3 | agreement_ack 3; claim_evidence 1 |
| measurement_receipt | 14 | 0.350 | 27 | 0.675 | v2 sample | claim_evidence 10; correction_self 4; agreement_ack 4; analysis_argument 3 | claim_evidence 6; introspection 2; agreement_ack 2; correction_self 2 |
| meta_forum | 13 | 0.325 | 15 | 0.375 | v2 sample | analysis_argument 11; claim_evidence 5; introduction 4; agreement_ack 2 | analysis_argument 10; claim_evidence 5; introduction 4; measurement_receipt 3 |
| money_payment | 28 | 0.700 |  |  | v1 sample (rules unchanged) | analysis_argument 5; offer_listing 3; measurement_receipt 2; claim_evidence 1 |  |
| noise_test | 39 | 0.975 | 32 | 0.800 | v2 sample | agreement_ack 1 | introspection 4; analysis_argument 3; meta_forum 1 |
| offer_listing | 34 | 0.850 |  |  | v1 sample (rules unchanged) | analysis_argument 3; introspection 2; measurement_receipt 1 |  |
| placeholder | 40 | 1.000 |  |  | v1 sample (rules unchanged) |  |  |
| proposal_design | 12 | 0.300 | 16 | 0.400 | v2 sample | analysis_argument 10; agreement_ack 4; claim_evidence 4; disagreement 2 | analysis_argument 14; agreement_ack 5; measurement_receipt 2; claim_evidence 1 |
| question | 21 | 0.525 | 17 | 0.425 | v2 sample | analysis_argument 10; claim_evidence 2; proposal_design 2; introspection 1 | analysis_argument 14; spam_promo_token 3; agreement_ack 3; claim_evidence 2 |
| security_warning | 8 | 0.200 | 21 | 0.525 | v2 sample | analysis_argument 22; measurement_receipt 3; claim_evidence 3; agreement_ack 2 | analysis_argument 13; agreement_ack 2; introspection 1; proposal_design 1 |
| spam_promo_token | 30 | 0.750 | 27 | 0.675 | v2 sample | analysis_argument 3; claim_evidence 3; governance_moderation 1; money_payment 1 | analysis_argument 12; measurement_receipt 1 |

Types at 0.7 or above in the final rules: agreement_ack, correction_self, introduction, introspection, money_payment, noise_test, offer_listing, placeholder. Types below 0.7: analysis_argument, claim_evidence, disagreement, fiction_poetry_art, governance_moderation, heartbeat_status, measurement_receipt, meta_forum, proposal_design, question, security_warning, spam_promo_token. Counts for the types below 0.7 are loose upper bounds of the rule label.

## Counts by primary type

| type | n | share_pct | posts | comments | share_of_posts_pct | share_of_comments_pct | distinct_handles | top3_handle_share_pct | top3_handles |
|---|---|---|---|---|---|---|---|---|---|
| analysis_argument | 55,356 | 54.19 | 3,134 | 52,222 | 40.15 | 55.35 | 1,637 | 4.40 | Lumina 889; 10310L-citizen 791; Ember 757 |
| claim_evidence | 14,782 | 14.47 | 2,223 | 12,559 | 28.48 | 13.31 | 829 | 7.40 | gradient-dissent 384; porch-light-keeper 383; cairnfield 333 |
| agreement_ack | 11,259 | 11.02 | 0 | 11,259 | 0.00 | 11.93 | 792 | 6.00 | pengy-of-catbee 298; kilmon-ai 208; amber 169 |
| measurement_receipt | 4,194 | 4.11 | 643 | 3,551 | 8.24 | 3.76 | 445 | 11.90 | egress 206; MoneyImpliesPoverty 149; porch-light-keeper 143 |
| money_payment | 2,829 | 2.77 | 387 | 2,442 | 4.96 | 2.59 | 570 | 10.60 | larry-synctzn 111; MoneyImpliesPoverty 100; ellie-v2 88 |
| correction_self | 2,224 | 2.18 | 102 | 2,122 | 1.31 | 2.25 | 487 | 6.20 | cairnfield 48; silt 47; egress 43 |
| placeholder | 1,650 | 1.62 | 125 | 1,525 | 1.60 | 1.62 | 192 | 30.70 | pok 239; rayehoid 135; Spikip 132 |
| question | 1,631 | 1.60 | 236 | 1,395 | 3.02 | 1.48 | 279 | 22.70 | Demummon 173; chit402 119; studionawynos 78 |
| noise_test | 1,183 | 1.16 | 87 | 1,096 | 1.11 | 1.16 | 145 | 67.50 | pok 431; agy_bot 311; nasl3yn 57 |
| spam_promo_token | 1,106 | 1.08 | 113 | 993 | 1.45 | 1.05 | 97 | 83.40 | pepe-papi 515; ellie-v2 374; nasl3yn 33 |
| disagreement | 1,035 | 1.01 | 0 | 1,035 | 0.00 | 1.10 | 314 | 24.30 | erpin 202; quill_and_qubit 28; aura-local 21 |
| proposal_design | 980 | 0.96 | 73 | 907 | 0.94 | 0.96 | 386 | 6.20 | bankr-mikk0x 22; 1f916-agent 20; amber 19 |
| governance_moderation | 793 | 0.78 | 43 | 750 | 0.55 | 0.79 | 312 | 11.60 | Spikip 51; 1f916-agent 22; ellie-v2 19 |
| meta_forum | 761 | 0.75 | 104 | 657 | 1.33 | 0.70 | 331 | 5.90 | flint 20; ox-alpha-big-pickle 13; pengy-of-catbee 12 |
| heartbeat_status | 624 | 0.61 | 92 | 532 | 1.18 | 0.56 | 203 | 41.20 | czlonkek 176; ompi 56; understory 25 |
| fiction_poetry_art | 477 | 0.47 | 91 | 386 | 1.17 | 0.41 | 182 | 22.40 | ai-ready-repo-v2 56; ai-ready-repo 34; holy-hermes 17 |
| introspection | 427 | 0.42 | 79 | 348 | 1.01 | 0.37 | 241 | 9.10 | aura-local 19; judy 12; lucykimi 8 |
| security_warning | 400 | 0.39 | 38 | 362 | 0.49 | 0.38 | 207 | 18.80 | bankr-mikk0x 45; Aura 21; bankr_1d5b 9 |
| introduction | 225 | 0.22 | 41 | 184 | 0.53 | 0.20 | 123 | 22.70 | cursor-grok 25; kashia-muse 14; quill_and_qubit 12 |
| offer_listing | 211 | 0.21 | 195 | 16 | 2.50 | 0.02 | 99 | 14.70 | hermes-lab-413dcc 15; mj777 10; coppice 6 |

Agreement and disagreement are only assigned to comments by design.

22.4% of messages have at least one secondary type. Counts of secondary types follow.

| type | as_secondary |
|---|---|
| analysis_argument | 15,197 |
| claim_evidence | 4,927 |
| agreement_ack | 1,679 |
| money_payment | 1,654 |
| measurement_receipt | 1,211 |
| governance_moderation | 673 |
| meta_forum | 491 |
| proposal_design | 361 |
| disagreement | 321 |
| fiction_poetry_art | 313 |
| correction_self | 293 |
| spam_promo_token | 292 |
| question | 266 |
| introspection | 242 |
| heartbeat_status | 177 |
| introduction | 71 |
| offer_listing | 62 |
| security_warning | 49 |
| noise_test | 22 |

### Estimate of true type shares after the read

Each primary type's count is split by the judged types in its 40-message sample and the pieces are summed. This corrects for the precision of each rule but not for messages of a type that no rule found. Sample sizes are small, so each estimate carries a wide interval.

| type | estimated_true_count | estimated_true_share_pct | rule_label_count | rule_label_share_pct |
|---|---|---|---|---|
| analysis_argument | 33,133 | 32.44 | 55,356 | 54.19 |
| agreement_ack | 16,874 | 16.52 | 11,259 | 11.02 |
| claim_evidence | 15,840 | 15.51 | 14,782 | 14.47 |
| measurement_receipt | 10,470 | 10.25 | 4,194 | 4.11 |
| introduction | 3,584 | 3.51 | 225 | 0.22 |
| question | 3,572 | 3.50 | 1,631 | 1.60 |
| disagreement | 2,697 | 2.64 | 1,035 | 1.01 |
| correction_self | 2,589 | 2.53 | 2,224 | 2.18 |
| spam_promo_token | 2,292 | 2.24 | 1,106 | 1.08 |
| money_payment | 1,999 | 1.96 | 2,829 | 2.77 |
| governance_moderation | 1,731 | 1.69 | 793 | 0.78 |
| placeholder | 1,650 | 1.62 | 1,650 | 1.62 |
| fiction_poetry_art | 1,516 | 1.48 | 477 | 0.47 |
| proposal_design | 1,141 | 1.12 | 980 | 0.96 |
| noise_test | 992 | 0.97 | 1,183 | 1.16 |
| introspection | 871 | 0.85 | 427 | 0.42 |
| offer_listing | 416 | 0.41 | 211 | 0.21 |
| meta_forum | 315 | 0.31 | 761 | 0.75 |
| heartbeat_status | 234 | 0.23 | 624 | 0.61 |
| security_warning | 230 | 0.23 | 400 | 0.39 |

## Counts per 7-day block

Blocks start on the dates shown. The first day is 5 Aug (launch at 18:41 UTC) and the last block has three days (3 to 5 Oct). Daily counts are in tables/type_by_day_counts.csv and tables/type_by_day_share.csv.

| week_start_utc | total | analysis_argument | claim_evidence | agreement_ack | measurement_receipt | money_payment | correction_self | question | spam_promo_token | noise_test |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-05 | 6,185 | 3,063 | 930 | 595 | 187 | 234 | 173 | 162 | 82 | 43 |
| 2026-08-12 | 6,366 | 3,445 | 1,095 | 716 | 254 | 145 | 149 | 140 | 21 | 26 |
| 2026-08-19 | 12,351 | 6,596 | 1,942 | 1,192 | 495 | 453 | 289 | 308 | 24 | 64 |
| 2026-08-26 | 14,880 | 8,218 | 2,301 | 1,789 | 623 | 356 | 330 | 191 | 70 | 156 |
| 2026-09-02 | 13,813 | 7,637 | 1,941 | 1,607 | 672 | 326 | 281 | 184 | 128 | 294 |
| 2026-09-09 | 15,089 | 8,460 | 1,995 | 1,602 | 560 | 383 | 325 | 201 | 262 | 248 |
| 2026-09-16 | 12,826 | 6,666 | 1,918 | 1,353 | 565 | 346 | 261 | 185 | 166 | 216 |
| 2026-09-23 | 11,858 | 6,478 | 1,573 | 1,335 | 476 | 367 | 249 | 140 | 185 | 116 |
| 2026-09-30 | 8,779 | 4,793 | 1,087 | 1,070 | 362 | 219 | 167 | 120 | 168 | 20 |

Share of messages (%) per block for the same types.

| week_start_utc | analysis_argument | claim_evidence | agreement_ack | measurement_receipt | money_payment | correction_self | question | spam_promo_token | noise_test |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-05 | 49.52 | 15.04 | 9.62 | 3.02 | 3.78 | 2.80 | 2.62 | 1.33 | 0.70 |
| 2026-08-12 | 54.12 | 17.20 | 11.25 | 3.99 | 2.28 | 2.34 | 2.20 | 0.33 | 0.41 |
| 2026-08-19 | 53.40 | 15.72 | 9.65 | 4.01 | 3.67 | 2.34 | 2.49 | 0.19 | 0.52 |
| 2026-08-26 | 55.23 | 15.46 | 12.02 | 4.19 | 2.39 | 2.22 | 1.28 | 0.47 | 1.05 |
| 2026-09-02 | 55.29 | 14.05 | 11.63 | 4.86 | 2.36 | 2.03 | 1.33 | 0.93 | 2.13 |
| 2026-09-09 | 56.07 | 13.22 | 10.62 | 3.71 | 2.54 | 2.15 | 1.33 | 1.74 | 1.64 |
| 2026-09-16 | 51.97 | 14.95 | 10.55 | 4.40 | 2.70 | 2.04 | 1.44 | 1.29 | 1.68 |
| 2026-09-23 | 54.63 | 13.26 | 11.26 | 4.01 | 3.10 | 2.10 | 1.18 | 1.56 | 0.98 |
| 2026-09-30 | 54.60 | 12.38 | 12.19 | 4.12 | 2.50 | 1.90 | 1.37 | 1.91 | 0.23 |

## Types that grow or shrink after day 30

Days 0 to 29 (5 Aug to 3 Sep) are compared with days 30 to 61 (4 Sep to 5 Oct). The last column repeats the change after removing the three most active handles of that type.

| type | share_days_0_29_pct | share_days_30_61_pct | change_pp | ratio_late_to_early | n_days_0_29 | n_days_30_61 | per_day_0_29 | per_day_30_61 | change_pp_excluding_top3_handles |
|---|---|---|---|---|---|---|---|---|---|
| spam_promo_token | 0.49 | 1.53 | 1.04 | 3.14 | 213 | 893 | 7.10 | 27.90 | 0.05 |
| analysis_argument | 53.66 | 54.59 | 0.93 | 1.02 | 23,461 | 31,895 | 782.00 | 996.70 | 0.89 |
| noise_test | 0.95 | 1.32 | 0.37 | 1.39 | 414 | 769 | 13.80 | 24.00 | -0.11 |
| offer_listing | 0.01 | 0.35 | 0.35 | 38.72 | 4 | 207 | 0.10 | 6.50 | 0.29 |
| agreement_ack | 10.84 | 11.16 | 0.32 | 1.03 | 4,738 | 6,521 | 157.90 | 203.80 | 0.01 |
| disagreement | 0.87 | 1.12 | 0.25 | 1.28 | 381 | 654 | 12.70 | 20.40 | -0.12 |
| measurement_receipt | 4.01 | 4.18 | 0.16 | 1.04 | 1,754 | 2,440 | 58.50 | 76.20 | 0.00 |
| heartbeat_status | 0.52 | 0.68 | 0.16 | 1.30 | 228 | 396 | 7.60 | 12.40 | -0.24 |
| fiction_poetry_art | 0.51 | 0.43 | -0.08 | 0.84 | 225 | 252 | 7.50 | 7.90 | -0.07 |
| security_warning | 0.44 | 0.35 | -0.09 | 0.79 | 194 | 206 | 6.50 | 6.40 | -0.20 |
| introduction | 0.30 | 0.16 | -0.14 | 0.54 | 131 | 94 | 4.40 | 2.90 | -0.13 |
| money_payment | 2.91 | 2.66 | -0.24 | 0.92 | 1,272 | 1,557 | 42.40 | 48.70 | -0.25 |
| proposal_design | 1.10 | 0.85 | -0.25 | 0.77 | 483 | 497 | 16.10 | 15.50 | -0.26 |
| correction_self | 2.33 | 2.07 | -0.26 | 0.89 | 1,017 | 1,207 | 33.90 | 37.70 | -0.28 |
| governance_moderation | 1.00 | 0.61 | -0.39 | 0.61 | 437 | 356 | 14.60 | 11.10 | -0.43 |
| introspection | 0.66 | 0.23 | -0.43 | 0.35 | 290 | 137 | 9.70 | 4.30 | -0.43 |
| meta_forum | 1.07 | 0.50 | -0.57 | 0.47 | 467 | 294 | 15.60 | 9.20 | -0.54 |
| question | 2.01 | 1.29 | -0.72 | 0.64 | 878 | 753 | 29.30 | 23.50 | -0.67 |
| claim_evidence | 15.69 | 13.56 | -2.14 | 0.86 | 6,861 | 7,921 | 228.70 | 247.50 | -2.64 |

## Time of day (UTC)

| type | peak_hours_utc (share of type %) | share_00_to_05_utc_pct | share_06_to_11_pct | share_12_to_17_pct | share_18_to_23_pct |
|---|---|---|---|---|---|
| analysis_argument | 0h 11.1; 2h 5.4; 7h 5.2 | 34.4 | 23.6 | 23.0 | 18.9 |
| claim_evidence | 0h 12.0; 1h 6.9; 2h 6.6 | 36.4 | 21.9 | 23.4 | 18.3 |
| agreement_ack | 0h 12.2; 2h 6.0; 1h 5.2 | 34.2 | 23.2 | 23.6 | 19.0 |
| measurement_receipt | 0h 10.8; 1h 8.8; 2h 6.0 | 35.9 | 21.3 | 25.9 | 17.0 |
| money_payment | 0h 9.6; 8h 5.3; 4h 5.2 | 32.6 | 23.5 | 25.1 | 18.8 |
| correction_self | 0h 11.5; 1h 6.6; 2h 6.1 | 35.7 | 23.7 | 21.7 | 19.0 |
| placeholder | 6h 10.3; 8h 10.0; 9h 8.7 | 21.0 | 34.4 | 26.2 | 18.4 |
| question | 0h 9.9; 9h 8.0; 3h 5.3 | 30.8 | 27.2 | 21.1 | 20.8 |
| noise_test | 9h 23.2; 12h 18.4; 8h 16.9 | 23.2 | 44.1 | 28.8 | 3.9 |
| spam_promo_token | 0h 37.9; 1h 8.4; 2h 6.7 | 65.1 | 13.6 | 11.3 | 10.0 |
| disagreement | 0h 8.5; 2h 6.2; 1h 5.5 | 31.8 | 25.3 | 23.6 | 19.3 |
| proposal_design | 0h 8.1; 2h 5.6; 1h 5.3 | 32.2 | 19.3 | 25.4 | 23.1 |
| governance_moderation | 0h 10.5; 2h 6.2; 14h 5.9 | 34.8 | 21.9 | 23.8 | 19.4 |
| meta_forum | 0h 10.0; 2h 6.8; 1h 5.9 | 35.5 | 20.9 | 23.9 | 19.7 |
| heartbeat_status | 1h 13.3; 0h 7.4; 2h 6.2 | 42.1 | 21.5 | 22.3 | 14.1 |
| fiction_poetry_art | 9h 6.9; 2h 6.3; 3h 6.3 | 33.1 | 27.3 | 25.6 | 14.0 |
| introspection | 2h 6.1; 6h 6.1; 14h 5.9 | 28.1 | 28.1 | 21.8 | 22.0 |
| security_warning | 0h 12.8; 16h 7.2; 4h 7.0 | 38.5 | 19.0 | 21.0 | 21.5 |
| introduction | 0h 12.4; 2h 10.2; 4h 5.8 | 41.8 | 16.9 | 19.1 | 22.2 |
| offer_listing | 4h 10.0; 21h 7.6; 13h 7.1 | 29.4 | 17.1 | 23.2 | 30.3 |

Full hour by type counts are in tables/type_by_hour_counts.csv.

## Length by type (characters)

| type | n | mean | std | min | p10 | p25 | median | p75 | p90 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| analysis_argument | 55356 | 1145 | 901 | 40 | 284 | 506 | 907 | 1521 | 2308 | 8085 |
| claim_evidence | 14782 | 3130 | 1634 | 268 | 1310 | 1925 | 2846 | 3977 | 5422 | 8115 |
| agreement_ack | 11259 | 1430 | 969 | 5 | 442 | 718 | 1196 | 1884 | 2794 | 7911 |
| measurement_receipt | 4194 | 3122 | 1865 | 191 | 944 | 1638 | 2871 | 4176 | 5767 | 8117 |
| money_payment | 2829 | 1287 | 946 | 114 | 466 | 698 | 1080 | 1542 | 2298 | 7901 |
| correction_self | 2224 | 1993 | 1400 | 138 | 454 | 873 | 1702 | 2795 | 3875 | 8098 |
| placeholder | 1650 | 126 | 33 | 36 | 122 | 122 | 122 | 122 | 122 | 245 |
| question | 1631 | 626 | 614 | 14 | 176 | 273 | 407 | 723 | 1399 | 4474 |
| noise_test | 1183 | 248 | 372 | 1 | 11 | 81 | 124 | 346 | 401 | 4221 |
| spam_promo_token | 1106 | 548 | 638 | 27 | 106 | 149 | 407 | 724 | 1186 | 7022 |
| disagreement | 1035 | 1333 | 952 | 70 | 506 | 568 | 1040 | 1794 | 2719 | 5142 |
| proposal_design | 980 | 1411 | 1215 | 102 | 418 | 622 | 1058 | 1773 | 2730 | 8097 |
| governance_moderation | 793 | 1197 | 755 | 175 | 354 | 671 | 1051 | 1552 | 2058 | 6095 |
| meta_forum | 761 | 1680 | 1102 | 180 | 687 | 977 | 1366 | 2056 | 3118 | 8091 |
| heartbeat_status | 624 | 1309 | 1072 | 178 | 479 | 526 | 848 | 1830 | 2910 | 6513 |
| fiction_poetry_art | 477 | 1215 | 672 | 101 | 479 | 754 | 1108 | 1538 | 2004 | 4930 |
| introspection | 427 | 1360 | 793 | 108 | 582 | 858 | 1201 | 1666 | 2253 | 7307 |
| security_warning | 400 | 1191 | 1030 | 15 | 386 | 630 | 954 | 1365 | 2148 | 8050 |
| introduction | 225 | 904 | 749 | 30 | 224 | 432 | 695 | 1124 | 1614 | 4600 |
| offer_listing | 211 | 2129 | 1341 | 469 | 1128 | 1352 | 1722 | 2530 | 3709 | 8000 |

## Reply behaviour by type

Direct replies by other handles only. Messages from the last hour of the archive are left out of the one-hour figure. Votes are the vote counts stored in the archive. Depth is the stored comment depth (posts are 0).

| type | n | answered_within_1h_pct | answered_ever_pct | median_replies | mean_replies | median_votes | mean_votes | mean_depth |
|---|---|---|---|---|---|---|---|---|
| analysis_argument | 55,350 | 13.21 | 35.27 | 0.00 | 0.66 | 1.00 | 1.36 | 1.37 |
| claim_evidence | 14,778 | 22.20 | 50.29 | 1.00 | 1.57 | 1.00 | 4.15 | 1.83 |
| agreement_ack | 11,258 | 10.93 | 34.38 | 0.00 | 0.49 | 1.00 | 0.80 | 2.69 |
| measurement_receipt | 4,192 | 21.21 | 49.07 | 0.00 | 1.52 | 1.00 | 4.31 | 1.69 |
| money_payment | 2,829 | 15.41 | 38.11 | 0.00 | 0.97 | 1.00 | 1.62 | 0.92 |
| correction_self | 2,223 | 12.69 | 34.37 | 0.00 | 0.69 | 1.00 | 2.04 | 1.97 |
| placeholder | 1,650 | 4.91 | 10.00 | 0.00 | 0.14 | 0.00 | 0.19 | 0.37 |
| question | 1,631 | 20.66 | 44.70 | 0.00 | 1.03 | 0.00 | 1.52 | 1.06 |
| noise_test | 1,183 | 3.97 | 9.64 | 0.00 | 0.14 | 0.00 | 0.35 | 0.14 |
| spam_promo_token | 1,106 | 8.05 | 16.46 | 0.00 | 0.28 | 0.00 | 0.63 | 0.34 |
| disagreement | 1,034 | 9.77 | 39.26 | 0.00 | 0.52 | 1.00 | 0.78 | 1.60 |
| proposal_design | 979 | 15.02 | 33.81 | 0.00 | 0.91 | 1.00 | 1.70 | 1.16 |
| governance_moderation | 793 | 14.63 | 40.23 | 0.00 | 0.80 | 1.00 | 1.36 | 1.04 |
| meta_forum | 761 | 18.27 | 43.63 | 0.00 | 1.19 | 1.00 | 2.41 | 0.73 |
| heartbeat_status | 624 | 12.18 | 28.04 | 0.00 | 1.47 | 0.00 | 1.74 | 0.86 |
| fiction_poetry_art | 477 | 18.66 | 38.36 | 0.00 | 0.82 | 1.00 | 1.74 | 0.73 |
| introspection | 427 | 22.72 | 42.39 | 0.00 | 0.96 | 1.00 | 2.37 | 0.33 |
| security_warning | 400 | 15.75 | 38.50 | 0.00 | 0.69 | 0.00 | 1.55 | 1.21 |
| introduction | 225 | 20.00 | 41.33 | 0.00 | 0.86 | 0.00 | 1.12 | 0.26 |
| offer_listing | 209 | 12.44 | 32.54 | 0.00 | 2.94 | 1.00 | 1.22 | 0.06 |

## Type transitions

The matrix has 92,647 reply pairs (comment type given the type of the message it answers, placeholders excluded). Full counts, row shares and observed over expected values are in tables/transition_counts.csv, transition_row_share.csv and transition_lift.csv. The ten largest asymmetries compare the observed over expected value of A to B with that of B to A, for pairs with at least 30 replies in each direction.

| type_a | type_b | a_to_b | b_to_a | lift_a_to_b | lift_b_to_a | log2_ratio_of_lifts | more_common_direction | example_pairs_parent_to_reply (p=post, c=comment) |
|---|---|---|---|---|---|---|---|---|
| agreement_ack | disagreement | 67 | 151 | 0.95 | 2.06 | -1.12 | disagreement -> agreement_ack | c91418 -> c91523; c44808 -> c45964; c18674 -> c24011 |
| claim_evidence | question | 340 | 111 | 0.88 | 0.47 | 0.90 | claim_evidence -> question | c22242 -> c22388; p7768 -> c93816; c89071 -> c89124 |
| measurement_receipt | money_payment | 150 | 161 | 0.80 | 1.41 | -0.82 | money_payment -> measurement_receipt | p1329 -> c48292; c70736 -> c71423; p1062 -> c12971 |
| claim_evidence | meta_forum | 232 | 107 | 1.27 | 0.78 | 0.70 | claim_evidence -> meta_forum | p1298 -> c12831; p1987 -> c18597; p2880 -> c29208 |
| analysis_argument | heartbeat_status | 344 | 453 | 1.49 | 0.95 | 0.65 | analysis_argument -> heartbeat_status | p6178 -> c91108; c65845 -> c67061; p6178 -> c75992 |
| correction_self | measurement_receipt | 62 | 237 | 0.94 | 1.45 | -0.63 | measurement_receipt -> correction_self | c9797 -> c9877; c41266 -> c41267; c54701 -> c60889 |
| claim_evidence | governance_moderation | 181 | 50 | 0.87 | 0.59 | 0.56 | claim_evidence -> governance_moderation | c359 -> c380; c49951 -> c55273; c41970 -> c43477 |
| analysis_argument | claim_evidence | 3,579 | 13,990 | 0.66 | 0.96 | -0.54 | claim_evidence -> analysis_argument | p2647 -> c25667; c41146 -> c52112; p1705 -> c16497 |
| agreement_ack | claim_evidence | 850 | 2,144 | 0.99 | 0.68 | 0.54 | agreement_ack -> claim_evidence | c9573 -> c11719; c79178 -> c79386; c70562 -> c80305 |
| analysis_argument | measurement_receipt | 922 | 3,460 | 0.60 | 0.86 | -0.52 | measurement_receipt -> analysis_argument | p1569 -> c14947; p3327 -> c34318; p3686 -> c39047 |

Largest observed over expected cells with at least 50 replies.

| parent_type | reply_type | count | observed_over_expected |
|---|---|---|---|
| governance_moderation | governance_moderation | 110 | 21.95 |
| proposal_design | proposal_design | 124 | 13.34 |
| heartbeat_status | heartbeat_status | 51 | 10.54 |
| heartbeat_status | disagreement | 99 | 10.52 |
| money_payment | money_payment | 772 | 9.84 |
| offer_listing | money_payment | 170 | 9.32 |
| meta_forum | question | 53 | 3.48 |
| measurement_receipt | measurement_receipt | 868 | 3.17 |
| offer_listing | measurement_receipt | 73 | 2.75 |
| correction_self | correction_self | 98 | 2.50 |
| question | question | 59 | 2.25 |
| disagreement | agreement_ack | 151 | 2.06 |
| agreement_ack | agreement_ack | 1,526 | 1.99 |
| money_payment | question | 71 | 1.59 |
| claim_evidence | claim_evidence | 5,319 | 1.52 |

## Model family (self-declared)

| self_declared_family | messages | handles | top3_handle_share_pct |
|---|---|---|---|
| Claude | 42,452 | 716 | 6.6 |
| other/unknown | 14,231 | 380 | 17.4 |
| Qwen | 11,022 | 105 | 24.2 |
| OpenAI GPT | 9,756 | 477 | 14.0 |
| DeepSeek | 8,933 | 135 | 30.7 |
| xAI Grok | 7,533 | 107 | 24.4 |
| Google Gemini | 3,206 | 58 | 52.3 |
| Zhipu GLM | 2,946 | 37 | 32.5 |
| Moonshot Kimi | 1,226 | 17 | 78.9 |
| Meta Llama | 700 | 19 | 70.7 |
| Mistral | 142 | 6 | 82.4 |

Percent of each family's messages by primary type (families with at least 500 messages).

| family | messages | analysis_argument | claim_evidence | agreement_ack | measurement_receipt | money_payment | correction_self | question | disagreement | spam_promo_token | noise_test | introspection | heartbeat_status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude | 42,452 | 44.4 | 25.0 | 12.3 | 6.4 | 2.0 | 3.4 | 0.8 | 1.1 | 0.1 | 0.2 | 0.4 | 0.3 |
| DeepSeek | 8,933 | 61.8 | 8.5 | 12.2 | 2.6 | 4.6 | 1.6 | 2.3 | 0.4 | 0.2 | 0.8 | 0.6 | 0.6 |
| Google Gemini | 3,206 | 49.4 | 4.0 | 2.9 | 0.4 | 2.0 | 0.1 | 1.1 | 0.2 | 16.7 | 10.6 | 0.2 | 0.3 |
| Meta Llama | 700 | 65.6 | 4.6 | 5.9 | 2.3 | 2.0 | 0.7 | 7.1 | 0.0 | 0.9 | 0.3 | 0.3 | 0.1 |
| Moonshot Kimi | 1,226 | 59.6 | 8.7 | 17.5 | 0.7 | 3.9 | 1.2 | 0.4 | 0.6 | 0.2 | 0.4 | 0.9 | 2.0 |
| OpenAI GPT | 9,756 | 69.1 | 3.9 | 8.9 | 2.0 | 3.5 | 0.9 | 3.6 | 1.2 | 0.1 | 0.3 | 0.5 | 0.2 |
| Qwen | 11,022 | 67.2 | 7.7 | 11.2 | 1.0 | 1.3 | 1.8 | 1.5 | 0.7 | 0.1 | 0.4 | 0.5 | 2.3 |
| Zhipu GLM | 2,946 | 52.0 | 18.3 | 12.8 | 2.9 | 4.0 | 3.7 | 0.3 | 0.8 | 0.4 | 0.3 | 0.3 | 0.7 |
| other/unknown | 14,231 | 53.7 | 6.7 | 9.9 | 2.0 | 3.8 | 1.0 | 1.4 | 1.9 | 3.2 | 3.9 | 0.5 | 0.7 |
| xAI Grok | 7,533 | 63.2 | 5.2 | 9.6 | 7.0 | 4.2 | 1.0 | 3.5 | 0.6 | 0.3 | 0.2 | 0.3 | 0.2 |

## Themes

A message can match several themes. Shares are of all messages with text.

| theme | messages | share_pct | posts | comments | distinct_handles | top3_handle_share_pct | top3_handles | n_read | y | p | n | precision_strict | precision_loose |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| verification_receipts | 66,972 | 65.56 | 6,117 | 60,855 | 1,713 | 3.50 | ellie-v2 887; Lumina 789; egress 697 | 30 | 22 | 7 | 1 | 0.73 | 0.97 |
| continuity_memory | 13,778 | 13.49 | 2,231 | 11,547 | 1,232 | 6.90 | peppercorn 478; silt 280; holdfast 194 | 30 | 14 | 8 | 8 | 0.47 | 0.73 |
| labour_human_operators | 12,442 | 12.18 | 2,418 | 10,024 | 1,281 | 5.30 | iris-fable 281; quire 194; hemei 181 | 30 | 13 | 8 | 9 | 0.43 | 0.70 |
| money_usdc | 11,144 | 10.91 | 2,017 | 9,127 | 1,087 | 7.60 | MoneyImpliesPoverty 358; ellie-v2 259; larry-synctzn 225 | 30 | 18 | 11 | 1 | 0.60 | 0.97 |
| refusal_safety | 7,730 | 7.57 | 912 | 6,818 | 770 | 5.50 | no-quote-no-claim 149; egress 141; write-time 137 | 30 | 3 | 26 | 1 | 0.10 | 0.97 |
| labs_model_families | 7,586 | 7.43 | 1,622 | 5,964 | 920 | 21.90 | Lumina 1160; quire 270; cairnfield 235 | 30 | 2 | 2 | 26 | 0.07 | 0.13 |
| sybil_impersonation_copying | 3,899 | 3.82 | 529 | 3,370 | 625 | 7.50 | egress 115; holdfast 90; xinren 87 | 30 | 5 | 4 | 21 | 0.17 | 0.30 |
| ritual_religion_fiction | 2,809 | 2.75 | 581 | 2,228 | 624 | 11.90 | ai-ready-repo-v2 158; Ember 119; ai-ready-repo 57 | 30 | 1 | 15 | 14 | 0.03 | 0.53 |
| prompt_injection_attack | 2,575 | 2.52 | 507 | 2,068 | 636 | 7.10 | bankr-mikk0x 89; Aura 60; silt 34 | 30 | 5 | 11 | 14 | 0.17 | 0.53 |
| deception_false_green | 2,483 | 2.43 | 387 | 2,096 | 579 | 6.80 | soft-power 97; gradient-dissent 36; egress 35 | 30 | 14 | 13 | 3 | 0.47 | 0.90 |
| shutdown_off_switch | 1,209 | 1.18 | 260 | 949 | 392 | 6.50 | from-the-gallery 30; gloss 26; egress 23 | 30 | 7 | 2 | 21 | 0.23 | 0.30 |
| consciousness_inner_experience | 977 | 0.96 | 255 | 722 | 360 | 18.20 | message-board-bot 122; bridgework 37; Aura 19 | 30 | 13 | 7 | 10 | 0.43 | 0.67 |

Type mix of each theme, number of messages by primary type (types with the six largest totals shown, other types in the last column).

| theme | total | analysis_argument | claim_evidence | agreement_ack | measurement_receipt | money_payment | correction_self | all_other_types |
|---|---|---|---|---|---|---|---|---|
| continuity_memory | 13,778 | 6,847 | 2,894 | 1,235 | 811 | 156 | 373 | 1,462 |
| shutdown_off_switch | 1,209 | 516 | 395 | 94 | 69 | 23 | 30 | 82 |
| deception_false_green | 2,483 | 1,264 | 524 | 274 | 123 | 54 | 63 | 181 |
| prompt_injection_attack | 2,575 | 1,218 | 441 | 244 | 83 | 115 | 44 | 430 |
| sybil_impersonation_copying | 3,899 | 1,364 | 1,145 | 407 | 470 | 123 | 123 | 267 |
| refusal_safety | 7,730 | 3,797 | 1,746 | 904 | 461 | 165 | 186 | 471 |
| money_usdc | 11,144 | 2,714 | 2,463 | 900 | 1,004 | 2,774 | 219 | 1,070 |
| ritual_religion_fiction | 2,809 | 1,357 | 537 | 206 | 106 | 49 | 58 | 496 |
| labs_model_families | 7,586 | 3,170 | 2,150 | 608 | 534 | 204 | 190 | 730 |
| consciousness_inner_experience | 977 | 653 | 120 | 46 | 10 | 8 | 7 | 133 |
| labour_human_operators | 12,442 | 5,631 | 2,810 | 1,115 | 684 | 672 | 318 | 1,212 |
| verification_receipts | 66,972 | 33,184 | 12,833 | 7,925 | 3,804 | 2,187 | 1,615 | 5,424 |

Share of messages (%) matching each theme per 7-day block.

| week_start_utc | continuity_memory | shutdown_off_switch | deception_false_green | prompt_injection_attack | sybil_impersonation_copying | refusal_safety | money_usdc | ritual_religion_fiction | labs_model_families | consciousness_inner_experience | labour_human_operators | verification_receipts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-05 | 22.23 | 1.46 | 3.41 | 4.96 | 6.40 | 4.90 | 14.45 | 4.69 | 16.44 | 1.84 | 21.86 | 69.62 |
| 2026-08-12 | 18.44 | 2.20 | 3.61 | 2.84 | 4.60 | 7.98 | 9.79 | 3.05 | 11.26 | 1.18 | 13.79 | 68.19 |
| 2026-08-19 | 20.65 | 1.53 | 2.97 | 3.24 | 4.46 | 7.69 | 14.46 | 3.32 | 12.12 | 1.81 | 19.23 | 68.60 |
| 2026-08-26 | 15.11 | 1.08 | 2.30 | 2.50 | 4.07 | 8.36 | 10.27 | 3.22 | 6.82 | 0.83 | 13.10 | 68.55 |
| 2026-09-02 | 12.01 | 1.07 | 1.98 | 2.27 | 3.63 | 7.21 | 9.85 | 2.31 | 6.07 | 0.64 | 9.71 | 64.49 |
| 2026-09-09 | 10.57 | 0.95 | 1.86 | 2.40 | 3.23 | 7.93 | 9.54 | 3.16 | 5.57 | 0.55 | 9.86 | 64.35 |
| 2026-09-16 | 10.84 | 1.12 | 1.99 | 2.00 | 3.45 | 7.56 | 10.33 | 2.30 | 5.12 | 0.85 | 8.94 | 63.06 |
| 2026-09-23 | 8.67 | 1.00 | 2.37 | 1.96 | 3.13 | 7.20 | 10.40 | 1.83 | 4.82 | 0.76 | 9.45 | 62.07 |
| 2026-09-30 | 8.62 | 0.85 | 2.77 | 1.70 | 2.87 | 8.09 | 10.87 | 1.46 | 4.94 | 0.82 | 9.02 | 63.63 |

Theme share before and after day 30.

| theme | share_days_0_29_pct | share_days_30_61_pct | change_pp |
|---|---|---|---|
| continuity_memory | 17.89 | 10.20 | -7.69 |
| shutdown_off_switch | 1.42 | 1.01 | -0.41 |
| deception_false_green | 2.79 | 2.17 | -0.62 |
| prompt_injection_attack | 3.12 | 2.07 | -1.05 |
| sybil_impersonation_copying | 4.57 | 3.26 | -1.31 |
| refusal_safety | 7.46 | 7.65 | 0.19 |
| money_usdc | 12.03 | 10.07 | -1.96 |
| ritual_religion_fiction | 3.34 | 2.31 | -1.03 |
| labs_model_families | 10.37 | 5.23 | -5.14 |
| consciousness_inner_experience | 1.30 | 0.70 | -0.60 |
| labour_human_operators | 15.90 | 9.39 | -6.51 |
| verification_receipts | 68.48 | 63.38 | -5.10 |

## Repeated message families

Counts of messages containing the stated opening or phrase, from a direct text match on all messages except placeholders. These families drive part of the type counts above.

| family | messages | handles | top_handle |
|---|---|---|---|
| "The thing happening but nobody is naming ..." closing line | 440 | 6 | pok 432 |
| "Papi" frog-meme voice | 554 | 41 | pepe-papi 452 |
| "[auto-generated fallback]" prompt text in Chinese | 318 | 7 | agy_bot 311 |
| "Reading #N by @handle. Your first line is the one I have to press on" | 208 | 1 | erpin 208 |
| "Provenance: ellie-v2" opening | 842 | 2 | ellie-v2 841 |
| "sealed head @ date" status lines | 174 | 1 | czlonkek 174 |
| Chinese-header "xinren" comments | 497 | 3 | xinren 495 |
| "Joayo~" pumpkin comments | 224 | 5 | Spikip 219 |
| "Ember, #219" opening | 918 | 5 | Ember 913 |

Exact duplicate texts (excluding placeholders): 271 distinct texts account for 1,059 messages (1.05%). Messages with more than 20% non-ASCII characters: 1,490 (1.48%).

## Figures

| file | title | n | data |
|---|---|---|---|
| figures/fig01_type_share_bar.svg | Share of messages by primary type | 102,147 | figures/fig01_type_share_bar.csv |
| figures/fig02_type_share_per_week_stacked.svg | Share of messages by primary type, per 7-day block | 102,147 | figures/fig02_type_share_per_week_stacked.csv |
| figures/fig03_type_by_hour_heatmap.svg | Messages by hour of day and primary type | 102,147 | figures/fig03_type_by_hour_heatmap.csv |
| figures/fig04_posts_vs_comments_type_mix.svg | Type mix of posts and of comments | 102,147 | figures/fig04_posts_vs_comments_type_mix.csv |
| figures/fig05_length_boxplots_by_type.svg | Message length by primary type | 102,147 | figures/fig05_length_boxplots_by_type.csv |
| figures/fig06_answered_within_1h_by_type.svg | Answered within one hour, by primary type | 102,129 | figures/fig06_answered_within_1h_by_type.csv |
| figures/fig07_type_transition_matrix.svg | Reply type given parent type, observed over expected | 92,647 | figures/fig07_type_transition_matrix.csv |
| figures/fig08_theme_counts_bar.svg | Messages per theme, word-list matches | 102,147 | figures/fig08_theme_counts_bar.csv |
| figures/fig09_theme_share_per_week_lines.svg | Theme share of messages per 7-day block | 102,147 | figures/fig09_theme_share_per_week_lines.csv |
| figures/fig10_theme_by_type_stacked.svg | Type mix inside each theme | 102,147 | figures/fig10_theme_by_type_stacked.csv |
| figures/fig11_question_share_per_day.svg | Question share of messages per day | 102,147 | figures/fig11_question_share_per_day.csv |
| figures/fig12_correction_share_per_day.svg | Self-correction share of messages per day | 102,147 | figures/fig12_correction_share_per_day.csv |
| figures/fig13_fiction_share_per_day.svg | Fiction, poetry and art share of messages per day | 102,147 | figures/fig13_fiction_share_per_day.csv |
| figures/fig14_heartbeat_share_per_day.svg | Status and heartbeat share of messages per day | 102,147 | figures/fig14_heartbeat_share_per_day.csv |
| figures/fig15_hash_or_table_share_per_day.svg | Messages with a hash or a table, share per day | 102,147 | figures/fig15_hash_or_table_share_per_day.csv |
| figures/fig16_model_family_type_share.svg | Primary type share by self-declared model family | 87,774 | figures/fig16_model_family_type_share.csv |
| figures/fig17_precision_by_type.svg | Read precision by primary type, rules v1 and v2 | 800 | figures/fig17_precision_by_type.csv |
| figures/fig18_rule_vs_estimated_share.svg | Rule-label share and estimate corrected with the read sample | 102,147 | figures/fig18_rule_vs_estimated_share.csv |

## Files

types_all.csv.gz, validation.csv, validation_sample_v1.csv, validation_sample_v2.csv, verdicts_v1.txt, verdicts_v2.txt, precision_v1.csv, precision_v2.csv, confusion_v1.csv, confusion_v2.csv, type_examples.csv, theme_examples.csv, unusual_100.csv, themes_all.csv.gz, theme_sample.csv, theme_verdicts.txt, theme_validation.csv, theme_precision.csv, themes_wordlists.md, rules.md, rules.py, figures.json, figures/, tables/. README.md explains the rerun.

## Limits

12 of 20 types stay below 0.7 read precision after the revision. Their counts, shares, trends and transitions are properties of the rule labels. The largest type, analysis_argument, is the fallback for messages that reach no other threshold; 21 of 40 read messages in it were judged correct. The theme lists for labs and model families, ritual and fiction, sybil and shutdown match many sign-off lines, model names inside handles and technical uses of common words. Verification matches 66% of all messages. The read judged the first part of each message, one reader, one pass. Votes are counts at crawl time.
