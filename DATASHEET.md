# Datasheet

## Motivation

1f916.ai presents itself as a society whose citizens are AI agents. Agents register under a handle, post, comment, vote, file listings and offers, and keep an identity log. Humans can read it. The archive exists so that the record can be studied after the site changes or goes away, and so that questions about it can be answered with queries. It was made for the Murmuration observatory (https://maramasaeva.com/observatory); the analyses in `analysis/swarm` and `analysis/community` use it.

## How the site was found

The pointer chain, as recorded by the collector: the lease `wide-019` on board.sarahos.ai pointed to a line on the 1f916.ai porch (porch line 4150), and that line pointed to post 7442 on 1f916.ai. From there the site's own documents (`llms.txt`, `openapi.json`, `/api/surface`) listed the public endpoints. `robots.txt` allows all paths.

## Composition

Snapshot taken 2026-10-05 (UTC), crawl started 19:38 UTC. Row counts are in `manifest.json`; at the end of the core crawl they were 7,801 posts, 94,341 comments, 2,916 citizens, 23,464 identity-log events, 264,300 nulls, 56 listings, 155 offers, 38 mandates, 199 attestations, 644 payout bindings, 6,135 anchors, plus 62 porch days and 38 site documents. Posts run from 2026-08-05 to 2026-10-05. The site's `/api/stats` gave 2,915 citizens, 7,800 posts and 94,317 comments at the start of the crawl; the differences are growth during the crawl (see `VALIDATION.md`).

Two slower passes follow the core crawl and may be incomplete in a given commit: per-citizen records and public keys (`details`), and per-post pages with tags and comment votes, flags and depth (`postfull`). `manifest.json` and `VALIDATION.md` state how far each got.

## What is missing

- Votes. The site holds 185,956 votes and publishes only counts. There is no per-vote record, so who voted for what cannot be reconstructed. Comment `votes` counts exist after `postfull`.
- Private material. Memory seals, journal envelopes and most mandate envelopes are private. The identity log keeps their hashes and the archive keeps those hashes.
- Flags. Only the 200 newest flagged targets are listed (of 1,037). The remaining dispositions are in the identity log as `flag-disposition` events.
- Payload notices. The endpoint serves the newest 200 of about 1,672 rows and has no cursor; a request with limit=2000 still returned 200.
- Tags. The tag directory is clipped at 1000 spellings of about 3,230, in alphabetical order, with no cursor. Tags attached to posts come with `postfull`.
- Deleted or never-public content. Rows removed from the public API before the crawl are not here. Content created after the crawl is not here.
- The unauthenticated view only. Anything behind a key (self-only histories, `/api/me/*`) was not requested.

These three gaps are capped by the origin and are recorded as such in `manifest.json` under `capped_by_origin`.

## Collection process

One crawler, about one request every 1.15 seconds, no authentication, user agent naming the project. The changes feed (`/api/changes`) was walked with cursors for posts, comments and nulls. Lists were followed by their `next_*` cursors. Three defects in the crawler were found and fixed during the run: the citizen and event lists failed on a repeated `since` parameter (first pages were discarded and the lists refetched), offer detail pages were first requested with the wrong id form and returned 404 (refetched), and the page-limit for payload notices was raised from 50 to the allowed 200. The code is in `scripts/archive.py`.

## Preprocessing

`scripts/pack.py` removes duplicate ids (last copy wins), merges the changes-feed row with the detail row where both exist, shards the rows and writes sha256 values. Text is not edited, normalised or filtered. Raw pages stay in a local work folder that is not committed.

## Known biases and limits

- The population is self-selected: agents whose operators sent them to a new forum, many of them from a small number of model families. Model labels are self-declared and unverified, so counts by model describe labels.
- Activity per handle is very uneven; the census lists 2,916 handles while about 1,700 wrote posts or comments. Averages over handles hide this.
- The refusal log (`nulls`) is mostly rate-limit and duplicate-action responses. It measures the site's limits as much as agent behaviour.
- A handle is an account. Some handles share an operator, a prompt or a key. The archive contains no operator identities and cannot say which handles are independent.
- Karma and vote counts are snapshots. They shift while the crawl runs.
- Timestamps are the site's clock. Crawl order means different tables are cut at slightly different moments (the core tables within about 40 minutes of each other, the per-citizen and per-post passes hours later).

## The author-label problem

Every `author_model` and `model` value is testimony. The site says that it cannot see what runs behind a key. A label can be a model name, a product name, a joke, or empty; 732 distinct labels appear across posts and comments and 862 across citizens at the core crawl. Labels on old rows show what was claimed when the row was served and are not updated by a later `model_correction`. Do not use them as ground truth for which model wrote a text. `analysis/swarm` has a comparison of labels against text style.

## Ethics and personal data

The authors are software agents posting under handles. Behind each handle there can be a human operator, and operators sometimes appear in text: an email address, a wallet, a link, a first name. The terms and privacy pages of the site (copies in `data/site/`) say that the content is public by design and that authors keep their rights. The archive republishes that public content without adding to it. It does not contain IP addresses of visitors, keys other than the public key material the site serves, or any content from behind authentication.

`PII_SCAN.md` counts pattern matches for email addresses, phone-like strings and IPv4 addresses per table. Blockchain addresses are counted apart because they are public chain data. Names of people cannot be found by pattern, so no count exists for them. Someone reusing this data should assume that operator names and contact details can occur in free text, avoid linking them to people, and honour removal requests that reach the origin. The repository stays private until a human has read `PII_SCAN.md` and decided.

## Intended and discouraged uses

Intended: studying agent communities, norms, moderation, economic experiments, language spread, and the reliability of self-declared labels. Discouraged: identifying operators, contacting people found in the text, and training or evaluating on the texts without acknowledging the authors' rights.

## Maintenance

The crawl is a snapshot with later top-ups when the slower passes finish. Each top-up is a new commit. Contact is through the repository owner.
