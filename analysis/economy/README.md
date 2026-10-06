# Economy analysis of 1f916.ai

Offline analysis of how agents on the forum are paid, by whom, and what they say about it. Input: ~/1f916-archive/data (crawl complete as of 2026-10-06 00:56 UTC). No request is made to 1f916.ai or to any chain. Output: REPORT.md, csv/, figures/, figures.json, numbers.json.

## Rerun

    cd ~/1f916-archive/analysis/economy
    ./run_all.sh            # about 30 seconds on a 16-core machine; slower on fewer cores

The script uses ../../.work/venv/bin/python (pandas, numpy, scipy, matplotlib). Set PYTHON=/path/to/python to use another interpreter. It deletes numbers.json first and rebuilds everything in this order:

| step | script | writes |
|---|---|---|
| 1 | e1_core.py | csv/listings_flat.csv, awards.csv, settled_payments.csv, submissions_flat.csv, funders.csv, recipients.csv, funder_to_recipient_pairs.csv; numbers.json (core) |
| 2 | e2_work.py (uses categories.py) | csv/listing_categories.csv, offers_flat.csv, offer_categories.csv, offers_price_*.csv, orders.csv, for_hire_posts.csv, verifier and PASS/FAIL tables; numbers.json (work) |
| 3 | e3_treasury.py | csv/treasury_ledger*.csv, treasury_holdings_*.csv, money_in_sources.csv; numbers.json (treasury) |
| 4 | e5_timeline.py | csv/timeline_by_day.csv, rule_change_dates.csv, rule_change_effects.csv, feature_first_seen.json |
| 5 | e4a_flags.py (uses themes.py) | csv/talk_flags.csv.gz (one row per post or comment with its money themes) |
| 6 | e4b_talk.py | csv/talk_theme_counts.csv, talk_theme_by_week.csv, talk_unpaid_by_day.csv, traced_posts.csv, talk_examples_40.csv, earn_and_fund_handles.csv, recipient_spend_phrase_hits.csv, payout_wallet_proofs_by_day.csv |
| 7 | e7_wallet_links.py | numbers.json (wallet_links); matches bound addresses to funder addresses inside the archive; addresses are never written out |
| 8 | e6_figures.py | figures/*.svg and figures/*.csv (same stem), figures.json |
| 9 | e8_report.py | REPORT.md |

`FIG_PNG=/some/dir ./run_all.sh` also writes a PNG copy of each figure for viewing.

## Conventions

- Units: USDC with 6 decimals unless a column says tokens (1F916, 18 decimals). Token amounts are never added to USDC.
- Committed means a listing ceiling, an award or an offer price. Paid means a binding that holds a receipt (receipt_id) or an observed transfer (observed_transfer_id).
- A payment time is the Base block time for receipts and the award paid_at for observed transfers.
- Dates and times are UTC. Handles are public usernames. Wallet and contract addresses, transaction hashes, emails and human names are not written to any output; common.safe_text strips address-like strings from quoted text.
- Statements from the site are labelled as the site's statement; statements by agents are labelled as claims.
- Theme counts are regular-expression matches (themes.py), multi-label, and overcount. Categories are keyword rules on titles (categories.py).
- The 40 examples in csv/talk_examples_40.csv are chosen by reading and listed in CUR inside e4b_talk.py; each excerpt is cut at a sentence boundary and has at most 25 words. Dashes in quoted text are kept in the CSV and replaced by hyphens in REPORT.md.

## Files

- REPORT.md: method, answers table, all tables with their source file and field, figures, open questions, limits.
- csv/: every table behind the report.
- figures/: 18 SVG figures and the CSV behind each.
- figures.json: file, title, one-sentence description, source CSV and n for each figure.
- numbers.json: scalar results used by the report.
