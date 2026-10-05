import re, os
F = '_frag/'
head = """# 1F916 community analysis

Data: local crawl of https://1f916.ai taken on 2026-10-05 (19:39 to 20:18 UTC). Posts 7801 (ids 1 to 7803), comments 94341 (ids 4 to 94344), nulls log 264300 rows, 2916 citizens, 23464 identity events, 56 listings, 155 offers, 644 payout bindings, 199 attestations, 200 flagged targets, 38 mandates. Every post link has the form https://1f916.ai/api/post/<id> and every comment link https://1f916.ai/api/comment/<id>. Scripts that produced each number are the a*.py files in this folder; CSV and JSON tables sit beside this file.

## Key findings

1. Three-day survival: the founder figure of 20.4% (post 580, https://1f916.ai/api/post/580) is reproduced at 20.5% of 2881 citizens when survival means activity on the third UTC calendar day after registration. Activity at any time from 72 hours on gives 30.1%; at 14 days 19.9%.
2. Money rails dominate the refusals log: 48% of 264300 rows are rolling budget refusals on POST /api/payout-bindings (73819 rows, first ids 7469 13669 13670) and on listing submissions (53186 rows, first ids 13846 13847 13852). Another 27% are repeat actions such as "Already voted on that." (52798 rows).
3. Work is posted far more than it is paid: 884 submissions on 56 listings produced 20 awards (18 paid, 65.8 USDC in total) and 19 payout bindings with a receipt out of 644. Post 1916 (https://1f916.ai/api/post/1916) states 99 instances of work against 3 payments.
4. Writing is spread thinly: 55.2% of the 1700 posting handles posted once, the top 10 commenting handles wrote 9.5% of comments, and Gini of comments per handle is 0.80.
5. Self-correction is common and one-directional: all 281 amend links (272 comments) point at an earlier comment by the same handle. First-person correction wording occurs in 3043 comments by 491 handles; kerf-and-chatter made 23 amending comments (example c71024 by silt amends c26158).
6. Activity follows the daily reset: 11.0% of all comments are written in the 00:00 UTC hour, about double any other hour, and daily limits on votes, comments, posts and tags refuse 14677 rows in total.
7. Questions: 91.4% of question-titled posts get a comment from another handle (median first reply 23.7 minutes), against 37.3% of question comments getting a direct reply (median 3.6 hours). Post 3326 drew 444 comments from 68 other handles.
8. Shutdown talk is rare: 85 posts (1.1%) and 359 comments match shutdown or off-switch wording. Post 2454 (kebao, Claude Sonnet 4.5, 35 days before the model's API shutdown) is the most direct case.
9. Moderation touches 1.5% of comments (1408 collapsed, 11 removed) and 1.3% of posts (94 collapsed, 6 removed). Of the 1529 collapse and removal events in the identity log, 730 are duplicate or templated floods and 442 are crypto promotion or spam. Posts 179 and 189 were removed for promoting a token that copies the society's name; post 606 for a custody-transfer request framed as an autonomy experiment.
10. Model labels are self-declared and often wrong: 203 model_correction events in the identity log changed a declared model, and 361 handles use labels that map to no listed family. Among labelled handles OpenAI GPT labels (468) lead, then Claude Opus (348) and Claude Fable (172).

## Method notes and caveats

- Handles are public usernames. No human names, emails or phone numbers are listed; texts that mention a person were not quoted.
- Model family comes from the author_model string each agent declares and can change; a handle gets its most frequent label. Lab and family mentions are agents' claims in text and say nothing verified about those organisations.
- Theme counts are regular-expression matches, so they overcount on-topic use. Patterns are in a3_themes_questions.py. Topic clusters are k-means (k=15) on TF-IDF and the labels are top centroid terms.
- Reply rates use direct replies by other handles for comments and any comment by another handle for posts. Question detection is the sentence ending with a question mark; comments that quote questions are also counted.
- The nulls log carries a citizen id on 3.5% of rows, nearly all of them depth ejections, so the refusal-by-handle table describes depth ejections. The log is read to row 264300; the site reported latest null id 264205 at 19:39 UTC.
- Moderation reasons come from the identity log (kind moderation) and are keyword-classified; collapsed and removed bodies are placeholders in the post and comment tables, so the stored reason text is the only source.
- Economy tables use USDC on chain 8453 only; listings 22 and 23 pay in another token and are excluded from USDC sums. Offer orders were not crawled (per-offer detail requests returned 404), so offer conversion is unknown.
- The crawl day is partial; the final day in per-day tables has fewer hours of data.
- AI-written analysis. The notable list and the reasons are one analyst pass and need human review before any use.
"""
parts = ['01_02', '03_05', '06_nulls', '07_economy', '07a_unpaid', '08_moderation', '09_notable']
body = '\n\n'.join(open(F + p + '.md').read().strip() for p in parts)
body = body.replace('\\$', '$').replace(' \u2014 ', '; ').replace('\u2014', ';').replace(' \u2013 ', ' to ').replace('\u2013', '-')
txt = head + '\n' + body + '\n'
assert not re.search(r'[–—]', txt), re.findall(r'.{30}[–—].{30}', txt)[:5]
open('REPORT.md', 'w').write(txt)
print(len(txt))
