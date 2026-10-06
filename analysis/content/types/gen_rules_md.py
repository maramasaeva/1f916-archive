"""Write rules_<version>.md from a rules module. Usage: python gen_rules_md.py rules rules.md"""
import sys, importlib
sys.path.insert(0, '.')
m = importlib.import_module(sys.argv[1])
out = sys.argv[2]
L = [f'# Message-type rules, version {m.RULES_VERSION}\n',
 'Every message gets a score per type. The primary type is the type with the highest score that reaches its minimum; ties go to the type earlier in the list below. Up to two secondary types need a score of at least %s and at least %s of the primary score. If no type reaches its minimum the message is analysis_argument when it has at least 40 characters, otherwise noise_test. Rows with no body and no timestamp are labelled no_content and left out of all statistics. Site placeholders ("[collapsed ...]", "[withdrawn ...]", "[removed ...]") are labelled placeholder.\n' % (m.SECONDARY_MIN, m.SECONDARY_RATIO),
 'Type order (tie-break): ' + ', '.join(m.TYPES) + '\n',
 'Default minimum score: %s. Per-type minimums: %s.\n' % (m.PRIMARY_MIN, ', '.join(f'{k} {v}' for k, v in m.TYPE_MIN.items())),
 '## Single rules (type, rule name, weight, scope, regex; case-insensitive)\n',
 'Scope: all = whole text; head = first 160 characters; title = first line (the title for posts); first300 and first400 = first 300 or 400 characters; opener = first 260 characters after removing leading bold marks, @mentions, handle prefixes such as "name, #123 —", and a leading "Provenance: ..." sentence (comments only; agreement and disagreement opener rules apply to comments only).\n',
 '| type | rule | weight | scope | regex |', '|---|---|---|---|---|']
for ty, name, w, rx, scope in m.SINGLE:
    L.append(f'| {ty} | {name} | {w} | {scope} | `{rx.pattern.replace("|", chr(92)+"|")}` |')
L.append('\n## Topic term lists\n')
if not hasattr(m, 'STRUCTURAL_DOC'): L.append('Each distinct pattern that matches counts once. Score = min(cap, hits x weight) x length factor, with length factor min(1, sqrt(1500 / characters)); +1.5 when a term matches the first line. The list counts only with at least two distinct hits or one hit in the first line. Introspection gets +1.5 when the first-person word share exceeds 2%.\n')
for k, (w, c, ps) in m.TOPIC.items():
    L.append(f'### {k} (weight {w}, cap {c})\n')
    L += [f'- `{p.pattern}`' for p in ps]
    L.append('')
L.append('## Structural and context rules (implemented in classify())\n')
if hasattr(m, 'STRUCTURAL_DOC'):
    L.append(m.STRUCTURAL_DOC)
else:
    L.append('''- question: title ends with "?" on a post (+3); text ends with "?" (+2); at least one interrogative sentence ending in "?" (+1); at least 30% of sentences are questions (+3); ask phrase such as "does anyone", "my question" together with a "?" (+2); text under 400 characters with a "?" (+1).
- correction_self: the comment amends a comment by the same handle (+4, from the amends field); reply to the author's own message together with a correction phrase (+2).
- disagreement: counts only when a disagreement phrase or a "No," opening hits. +2 when the comment is a reply to another handle. Without a parent author the score is multiplied by 0.6. A rule hit "your claim fails" style phrase is part of the phrase list.
- agreement_ack: +2 when an agreement phrase hits and the text is under 300 characters.
- measurement_receipt: the word receipt (+2); GET or POST /api, curl, jq, HTTP 200 or 404 (+4); first-person performed verbs such as "I ran", "re-derived", "reproduced" (+3); words such as measured, fixture, falsifier, read-back (+1); artifact field names such as tree_size, sha256, created_at (+3); a 16 or more character hex string (+2); a markdown table of at least two rows (+2); an ISO timestamp (+1); a fenced code block (+1); "n = <number>" (+2).
- claim_evidence: two or more id references (#123 or c12345) (+2), five or more (+1 more); five or more numbers (+2), twelve or more (+1 more); finding words such as "I found", "evidence", "the result" (+2); a percentage (+1).
- proposal_design: two or more lines starting with an imperative verb (+2); three or more numbered list items (+1).
- fiction_poetry_art: at least 8 non-empty lines with at least 70% of them 60 characters or shorter, under 2500 characters (+4); a stage direction line in asterisks (+1).
- noise_test: no text (+10); under 25 characters (+3).
- analysis_argument: two or more reasoning terms such as because, therefore, the distinction (+0.8 each, max 4); more than 400 characters (+1).
''')
open(out, 'w').write('\n'.join(L))
