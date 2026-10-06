# Message types on 1f916.ai

Content classification of all posts and comments in ~/1f916-archive (data/posts, data/comments). Offline only. Rules are regex plus structural features. Handles are public; no message text is stored in the output tables except 25-word excerpts in the example tables.

## Rules hash (recorded before any validation sample was drawn)

Version v1, frozen at the time of writing this file.

- rules.py (copy: rules_v1.py) sha256 e5819d403712e06203ff86c08535e4d11d986528a720fac31b49908778c36e6c
- rules.md (copy: rules_v1.md) sha256 946d8eafe6055350bdbf18786b54a8f23e38e6ab9e985c1aa1ec3e2982c18233
- combined sha256 (of the two hex strings concatenated) 81732d54323163075e4bc7f48f88f0858208d584ab85377210965297ddd0fcf6

Theme word lists, version t1, frozen before the theme read:

- themes.py sha256 4799be4aed002d750d29d16776f8a121ab114cf31233fa69a49f97a9a939fdbb
- themes_wordlists.md sha256 c28c39aabdf549f727b0a735494525a6ae547cd41932924639e6b8fa195d4589

Exploration before freezing used the corpus itself (five tuning rounds with a few dozen to about 100 messages read per round). Validation samples were drawn after the hash was written, with new random seeds, and were not screened against the exploration reads.

Version v2 (the single revision, made after reading the v1 validation sample; see Validation). Hash recorded before the v2 validation sample was drawn.

- rules_v2.py sha256 d8141c0915b9bc369519cce0b50c92aa3f64e5c640aef01761f5a511334615a8
- rules_v2.md sha256 802bf03089c27a08f32ba9962bd7ed3bc71eaaccd9fce49e498012d2504a990b
- combined sha256 03b7ed6c435b77a0dc69142511b8a78c07a51962556447955df4a18570f4b34a

(Because rules_v1.md was generated before the generator text was edited, rules_v1.md is the file that carries the recorded v1 hash; gen_rules_md.py now produces slightly different wording for v1 and was not used to overwrite it.)

rules.py and rules.md in this folder are copies of rules_v2.py and rules_v2.md (the final rules). rules_v1.py and rules_v1.md hold the first rules. The rules files contain a few literal em dash characters inside regular expressions, because the patterns match that character in message text.

## What the files are

- types_all.csv.gz: one row per message (id, kind, handle, date_utc, length, primary, score, secondary, rule_hits, parent_author, has_hash, has_table, has_code, n_mentions, n_q). No message text. The 222 comments without text or timestamp carry the primary type no_content. types_all_v1.csv.gz holds the same table under the v1 rules.
- rules.md, rules.py: the type rules (final, v2). rules_v1.*: first version. Scores, thresholds, regexes and structural features are listed in rules.md.
- validation_sample_v1.csv, validation_sample_v2.csv: the random samples (40 per type). verdicts_v1.txt, verdicts_v2.txt: the judgements as lists of sample positions judged wrong, with the type judged right. validation.csv: all verdicts with ids. precision_v1.csv, precision_v2.csv, confusion_v1.csv, confusion_v2.csv.
- themes.py, themes_wordlists.md, themes_all.csv.gz, theme_sample.csv, theme_verdicts.txt, theme_validation.csv, theme_precision.csv.
- type_examples.csv, theme_examples.csv, unusual_100.csv: example tables. Excerpts are at most 25 words and end at a sentence or title boundary. Dashes in excerpts were replaced by semicolons or "to"; other characters are verbatim. Excerpts with email addresses, phone numbers, wallet addresses, personal-looking names or personal repository links were skipped and replaced by other messages. Examples come first from messages read and judged correct (column read_check).
- tables/: every table behind REPORT.md. figures/: 18 SVG figures, each with a CSV of the same stem. figures.json lists file, title, description, source and n.
- REPORT.md: method, hashes, precision, counts, trends, replies, transitions, families, themes.

## Judgement criteria used in the read

Type: the message counts as correct when the primary type is an acceptable single label for what the message mainly does or is, given the 20 types. A message that opens by accepting another comment and then adds a measurement is judged as agreement. Messages judged wrong carry the type that fits better, taken from the same 20 types. The reader saw the first 300 to 400 characters, the length and the rule hits.

Theme: y when the message discusses the theme in substance, p when the term appears in passing or in a technical or handle-related sense, n when the match is unrelated. Strict precision is y over 30. Loose precision is y plus p over 30.

## Rerun

All paths are relative to this folder. Python 3 with pandas, numpy, scikit-learn, matplotlib and scipy (the venv at ~/1f916-archive/.work/venv has them; create one with python3 -m venv and pip install pandas numpy scikit-learn matplotlib scipy if it is missing).

    cd ~/1f916-archive/analysis/content/types
    PY=~/1f916-archive/.work/venv/bin/python
    $PY apply_rules.py rules_v1 types_all_v1     # about 90 s with 8 processes
    $PY apply_rules.py rules_v2 types_all_v2
    cp types_all_v2.csv.gz types_all.csv.gz
    $PY score_validation.py v1                    # reads verdicts_v1.txt and validation_sample_v1.csv
    $PY score_validation.py v2
    $PY themes_run.py                             # themes_all.csv.gz and theme_sample.csv
    $PY score_themes.py                           # reads theme_verdicts.txt
    $PY analyze_types.py                          # tables/ and .X.pkl (a scratch file)
    $PY examples.py                               # example tables and unusual_100.csv
    $PY figures.py                                # figures/ and figures.json
    $PY report.py                                 # validation.csv, confusion tables, REPORT.md

The validation samples are fixed files. Drawing them again (validation_sample.py with the seeds 20261006 for v1 and 20261007 for v2) gives the same ids, but the verdict files only fit those ids. The verdicts are a human read and cannot be regenerated by a script. gen_rules_md.py rebuilds rules_v2.md from rules_v2.py.

## Revision from v1 to v2

The v1 sample showed that topic word lists (governance, meta, security, introspection) and the loose receipt rules matched forum vocabulary in most messages. v2 changed these points, all in rules_v2.py:

- Agreement, disagreement and correction rules look at the message opening, after removing mentions, handle prefixes and a leading Provenance sentence. Agreement and disagreement apply to comments only. Correction needs a first-person phrase in the first 400 characters or an amends link to the same handle.
- Topic lists need three distinct hits (or two plus a title hit) in the first 1,500 characters and a higher minimum score. Measurement needs an API call or a run verb plus other evidence. Heartbeat is limited to template families. Fixed template sentences used by single accounts move to noise_test.
- Fiction lost its broad word list; it keeps title cues and short-line layout. Daily prompt titles ("Howl of the Day") became questions.

Known defects that stayed because the revision was used once: the fiction rule still matches model names such as sonnet and haiku inside handles and sign-off lines, the bot_template rule misses "hey, this snagged me" with the dash spacing used in the data, and agreement posts are excluded by design.
