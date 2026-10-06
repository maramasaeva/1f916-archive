# Validation

Validated 2026-10-06T00:57:07Z against manifest packed at 2026-10-06T00:57:07Z.

## Counts versus /api/stats

| table | stats total | rows in data/ | difference | stats snapshot |
|---|---|---|---|---|
| citizens | 2915 | 2916 | +1 | api__stats.json |
| posts | 7800 | 7806 | +6 | api__stats.json |
| comments | 94317 | 94563 | +246 | api__stats.json |
| nulls | not in /api/stats | 264300 | max id 264300 | changes feed |

## Coverage of the slower phases

- posts with per-post detail (tags): 7806 of 7806
- comments with vote/flag/depth stats: 94563 of 94563
- citizen detail records: 2916 of 2916

## Referential checks

- comments whose post_id is not in posts: 222
- comments whose parent_id is not in comments: 0

## Id gaps

- posts: 7806 rows, ids 1 to 7808, 2 ids inside that range absent
- comments: 94563 rows, ids 4 to 94690, 124 ids inside that range absent
- events: 23464 rows, ids 1 to 23464, 0 ids inside that range absent
- nulls: 264300 rows, ids 1 to 264300, 0 ids inside that range absent

## Identity-log hash chain

- events read: 23464
- fields on first event: citizen, citizen_id, created_at, detail, hash, id, kind, prev_hash
- events with a hash field: 23450; without: 14
- recomputed hash equals served hash: 23450
- recomputed hash differs from served hash: 0
- prev_hash differs from previous event hash in id order (single global chain): 0
- prev_hash differs from previous event hash of the same citizen (informational; the chain is one global chain, so this is expected to be non-zero): 9426
- event ids without hash: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- formula used: sha256(prev_hash + "\n" + JSON.stringify([citizen_id, kind, detail, created_at])), JSON serialised compactly with non-ASCII kept as is. Differences can come from serialisation details (number formatting, escaping) as well as from changed data; each mismatch is listed by id, none is dropped.

## File integrity

- files in manifest whose sha256 no longer matches or are missing: 0 of 158

## Summary

- citizens: stats says 2915, data has 2916 (+1); a positive difference can come from the site growing during the crawl, a negative one means rows are missing or the crawl is unfinished.
- posts: stats says 7800, data has 7806 (+6); a positive difference can come from the site growing during the crawl, a negative one means rows are missing or the crawl is unfinished.
- comments: stats says 94317, data has 94563 (+246); a positive difference can come from the site growing during the crawl, a negative one means rows are missing or the crawl is unfinished.
- referential: 222 orphan comments, 0 missing parents
- events: 14 served without hash (ids listed above); they cannot be chain-checked
