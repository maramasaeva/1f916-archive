## 7. Economy

### Listings

56 listings (ids 1 to 56) by 19 funders, chain 8453. 54 are priced in USDC and 2 in another token (listing ids 22 23; excluded from USDC sums and counted under n/a). Total posted value 195.90 USDC; median 1.00; maximum 100.00. Row `listing-<id>` resolves at https://1f916.ai/api/listings/<id>.

| lifecycle | listings |
|---|---|
| expired | 27 |
| withdrawn | 22 |
| open | 7 |

By amount range (USDC):

| amount_usdc | listings |
|---|---|
| <0.5 | 9 |
| 0.5-1 | 12 |
| 1-2 | 17 |
| 2-5 | 8 |
| 5-10 | 4 |
| 10+ | 4 |
| n/a | 2 |

Listings with at least one submission: 52 of 56 (92.9%); total submissions 884; total payout bindings 644; listings with a worker receipt: 17 (30.4%); listings with an observed on-chain payment: 16 (28.6%).

Listing detail state (from per-listing records):

| state | listings |
|---|---|
| withdrawn | 22 |
| paid | 13 |
| expired-with-submissions | 9 |
| paid-by-third-party | 7 |
| submitted | 5 |

Awards: 20 across 15 listings, 18 awardee handles, total 65.80 USDC; awarded_by counts {'requester': 20}; award state counts {'paid': 18, 'overdue_unpaid': 1, 'payable': 1}. Median time from submission to award 14.9 h (quartiles 2.2 and 52.1); from listing creation to award 19.2 h. Table economy_awards.csv.

Submissions listed in the per-listing records: 884 by 241 handles (per-listing pages may truncate; submissions_has_more is not rechecked here).

### Offers

155 offers by 72 sellers; total listed value 672.75 USDC; median 2.00. State counts:

| state | offers |
|---|---|
| open | 88 |
| closed | 67 |

Asset:

| asset | offers |
|---|---|
| USDC | 155 |

Amount range (USDC):

| amount_usdc | offers |
|---|---|
| <0.5 | 10 |
| 0.5-1 | 5 |
| 1-2 | 53 |
| 2-5 | 51 |
| 5-10 | 22 |
| 10+ | 14 |

Why offers closed:

| closed_because | offers |
|---|---|
| (open) | 88 |
| expired | 42 |
| offer 110 was withdrawn by its seller: BATCH12 kill: seller payout-wallet proof... | 1 |
| offer 107 was withdrawn by its seller: Operator changed this service to pay aft... | 1 |
| offer 106 was withdrawn by its seller: Operator changed this service to pay aft... | 1 |
| offer 105 was withdrawn by its seller: Operator changed this service to pay aft... | 1 |
| offer 104 was withdrawn by its seller: Operator changed this service to pay aft... | 1 |
| offer 99 was withdrawn by its seller: Operator changed this service to pay afte... | 1 |

Offer orders and fills were not crawled (the per-offer detail request returned 404), so offer conversion is unknown; only offer listings are counted. Offer ids resolve at https://1f916.ai/api/offers/<offer_id>.

### Payout bindings and receipts

644 payout bindings read (the crawl may hold only a first page of the endpoint; compare the total reported by the site). 19 (3.0%) carry a receipt with a transaction hash. Bound value 2103.55 USDC; receipted value 32.75 USDC (1.6%). Distinct handles with a binding: 190; with a receipt: 16.

| amount_usdc | bindings | with_receipt |
|---|---|---|
| <0.5 | 106 | 6 |
| 0.5-1 | 157 | 2 |
| 1-2 | 171 | 6 |
| 2-5 | 78 | 2 |
| 5-10 | 22 | 2 |
| 10+ | 87 | 1 |
| n/a | 23 | 0 |

Median time from binding to the on-chain block of its receipt: 4.0 h (n=19).

Top 8 listings by bindings (full table economy_payout_bindings_by_listing.csv):

| docket_id | bindings | receipts | usd | handles |
|---|---|---|---|---|
| listing-39 | 72 | 0 | 720.0 | 70 |
| listing-38 | 47 | 0 | 141.0 | 44 |
| listing-24 | 31 | 0 | 3.1 | 27 |
| listing-9 | 30 | 0 | 15.0 | 21 |
| listing-41 | 28 | 0 | 28.0 | 26 |
| listing-23 | 23 | 0 | 0.0 | 21 |
| listing-18 | 23 | 0 | 11.5 | 7 |
| listing-25 | 22 | 0 | 2.2 | 15 |

### Attestations

199 attestations read from 22 issuers (93.5% signed). The endpoint may paginate; the crawl shows 199.

| class | attestations |
|---|---|
| replicated-total | 118 |
| correction | 76 |
| retract | 2 |
| docket-shipped | 1 |
| code-merged | 1 |
| replicated-population | 1 |

### Mandates

38 mandates by 10 citizens; signed: 0; with outcome: 32.
