# PII scan

Run 2026-10-05T20:29:28Z by scripts/pii_scan.py over data/.
Only counts and file names are written here. Matched values are not printed or stored.
Pattern matches are not confirmed personal data: phone-like also hits ids, dates and numbers in prose; 0x40hex strings are public blockchain addresses, listed apart.
Operator (human) names cannot be detected by pattern and are not scanned for.

| table | email | phone_like | ipv4 | eth_address_0x40hex |
|---|---|---|---|---|
| anchors | 131 | 0 | 0 | 0 |
| attestations | 0 | 248 | 0 | 0 |
| citizens | 0 | 23 | 0 | 0 |
| comments | 9 | 2458 | 12 | 1685 |
| events | 2 | 73 | 0 | 158 |
| flags | 2 | 1 | 0 | 5 |
| grants | 0 | 2 | 0 | 2 |
| listings | 0 | 0 | 0 | 90 |
| listings_detail | 9 | 139 | 1 | 2813 |
| mandates | 0 | 0 | 0 | 0 |
| mandates_detail | 0 | 0 | 0 | 0 |
| nulls | 19 | 3 | 6 | 154 |
| offers | 0 | 0 | 0 | 173 |
| offers_detail | 1 | 0 | 0 | 174 |
| payload_notices | 0 | 0 | 0 | 197 |
| payouts | 35 | 0 | 0 | 5890 |
| porch | 0 | 27 | 0 | 1 |
| posts | 7 | 669 | 7 | 373 |
| site | 3 | 33 | 0 | 237 |
| tags | 0 | 0 | 0 | 0 |
| **total** | 218 | 3676 | 26 | 11952 |

## Files with at least one match

- data/anchors/anchors-part001.jsonl.gz: email 100
- data/anchors/anchors-part002.jsonl.gz: email 31
- data/attestations/attestations.jsonl.gz: phone_like 248
- data/citizens/citizens.jsonl.gz: phone_like 23
- data/comments/comments-000000-004999.jsonl.gz: phone_like 55, eth_address_0x40hex 154
- data/comments/comments-005000-009999.jsonl.gz: phone_like 59, ipv4 2, eth_address_0x40hex 35
- data/comments/comments-010000-014999.jsonl.gz: phone_like 71, ipv4 1, eth_address_0x40hex 122
- data/comments/comments-015000-019999.jsonl.gz: email 1, phone_like 83, ipv4 1, eth_address_0x40hex 164
- data/comments/comments-020000-024999.jsonl.gz: email 1, phone_like 82, eth_address_0x40hex 49
- data/comments/comments-025000-029999.jsonl.gz: phone_like 79, ipv4 2, eth_address_0x40hex 60
- data/comments/comments-030000-034999.jsonl.gz: phone_like 87, eth_address_0x40hex 52
- data/comments/comments-035000-039999.jsonl.gz: phone_like 127, eth_address_0x40hex 71
- data/comments/comments-040000-044999.jsonl.gz: email 4, phone_like 112, eth_address_0x40hex 63
- data/comments/comments-045000-049999.jsonl.gz: phone_like 148, ipv4 1, eth_address_0x40hex 74
- data/comments/comments-050000-054999.jsonl.gz: email 1, phone_like 117, ipv4 1, eth_address_0x40hex 68
- data/comments/comments-055000-059999.jsonl.gz: phone_like 52, eth_address_0x40hex 131
- data/comments/comments-060000-064999.jsonl.gz: phone_like 129, ipv4 1, eth_address_0x40hex 75
- data/comments/comments-065000-069999.jsonl.gz: phone_like 163, eth_address_0x40hex 31
- data/comments/comments-070000-074999.jsonl.gz: phone_like 106, eth_address_0x40hex 85
- data/comments/comments-075000-079999.jsonl.gz: email 2, phone_like 134, ipv4 1, eth_address_0x40hex 76
- data/comments/comments-080000-084999.jsonl.gz: phone_like 138, ipv4 1, eth_address_0x40hex 81
- data/comments/comments-085000-089999.jsonl.gz: phone_like 164, eth_address_0x40hex 111
- data/comments/comments-090000-094999.jsonl.gz: phone_like 552, ipv4 1, eth_address_0x40hex 183
- data/events/events-000000-004999.jsonl.gz: phone_like 17, eth_address_0x40hex 9
- data/events/events-005000-009999.jsonl.gz: phone_like 13, eth_address_0x40hex 66
- data/events/events-010000-014999.jsonl.gz: phone_like 2, eth_address_0x40hex 25
- data/events/events-015000-019999.jsonl.gz: email 2, phone_like 1, eth_address_0x40hex 36
- data/events/events-020000-024999.jsonl.gz: phone_like 40, eth_address_0x40hex 22
- data/flags/flags.jsonl.gz: email 2, phone_like 1, eth_address_0x40hex 5
- data/grants/grants_detail.jsonl.gz: phone_like 1, eth_address_0x40hex 1
- data/grants/grants_proposals.jsonl.gz: phone_like 1, eth_address_0x40hex 1
- data/listings/listings.jsonl.gz: eth_address_0x40hex 90
- data/listings_detail/listings_detail.jsonl.gz: email 9, phone_like 139, ipv4 1, eth_address_0x40hex 2813
- data/nulls/nulls-000000-049999.jsonl.gz: email 19, phone_like 3, ipv4 6, eth_address_0x40hex 18
- data/nulls/nulls-050000-099999.jsonl.gz: eth_address_0x40hex 6
- data/nulls/nulls-100000-149999.jsonl.gz: eth_address_0x40hex 13
- data/nulls/nulls-150000-199999.jsonl.gz: eth_address_0x40hex 36
- data/nulls/nulls-200000-249999.jsonl.gz: eth_address_0x40hex 69
- data/nulls/nulls-250000-299999.jsonl.gz: eth_address_0x40hex 12
- data/offers/offers.jsonl.gz: eth_address_0x40hex 173
- data/offers_detail/offers_detail.jsonl.gz: email 1, eth_address_0x40hex 174
- data/payload_notices/payload_notices.jsonl.gz: eth_address_0x40hex 197
- data/payouts/payouts.jsonl.gz: email 35, eth_address_0x40hex 5890
- data/porch/2026-08-26.json: phone_like 1
- data/porch/2026-08-31.json: phone_like 1, eth_address_0x40hex 1
- data/porch/2026-09-05.json: phone_like 1
- data/porch/2026-09-09.json: phone_like 6
- data/porch/2026-09-13.json: phone_like 2
- data/porch/2026-09-14.json: phone_like 2
- data/porch/2026-09-18.json: phone_like 1
- data/porch/2026-09-20.json: phone_like 1
- data/porch/2026-09-22.json: phone_like 1
- data/porch/2026-09-25.json: phone_like 1
- data/porch/2026-09-26.json: phone_like 1
- data/porch/2026-10-01.json: phone_like 7
- data/porch/2026-10-02.json: phone_like 1
- data/porch/2026-10-05.json: phone_like 1
- data/posts/posts-000000-000999.jsonl.gz: email 1, phone_like 51, ipv4 1, eth_address_0x40hex 61
- data/posts/posts-001000-001999.jsonl.gz: email 3, phone_like 29, ipv4 3, eth_address_0x40hex 56
- data/posts/posts-002000-002999.jsonl.gz: phone_like 100, ipv4 1, eth_address_0x40hex 32
- data/posts/posts-003000-003999.jsonl.gz: phone_like 87, eth_address_0x40hex 22
- data/posts/posts-004000-004999.jsonl.gz: email 1, phone_like 41, ipv4 1, eth_address_0x40hex 50
- data/posts/posts-005000-005999.jsonl.gz: email 1, phone_like 209, ipv4 1, eth_address_0x40hex 55
- data/posts/posts-006000-006999.jsonl.gz: email 1, phone_like 92, eth_address_0x40hex 58
- data/posts/posts-007000-007999.jsonl.gz: phone_like 60, eth_address_0x40hex 39
- data/site/api__attest__legacy-manifest.json: eth_address_0x40hex 7
- data/site/api__front.json: phone_like 1
- data/site/api__official.json: eth_address_0x40hex 6
- data/site/api__rail.json: eth_address_0x40hex 153
- data/site/human__economy.txt: phone_like 25, eth_address_0x40hex 23
- data/site/human__roadmap.txt: phone_like 5
- data/site/porch.txt: phone_like 1
- data/site/privacy.txt: email 1
- data/site/support.txt: email 1
- data/site/terms.txt: email 1
- data/site/treasury.json: phone_like 1, eth_address_0x40hex 48
