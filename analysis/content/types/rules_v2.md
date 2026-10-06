# Message-type rules, version v2

Every message gets a score per type. The primary type is the type with the highest score that reaches its minimum; ties go to the type earlier in the list below. Up to two secondary types need a score of at least 3.0 and at least 0.5 of the primary score. If no type reaches its minimum the message is analysis_argument when it has at least 40 characters, otherwise noise_test. Rows with no body and no timestamp are labelled no_content and left out of all statistics. Site placeholders ("[collapsed ...]", "[withdrawn ...]", "[removed ...]") are labelled placeholder.

Type order (tie-break): placeholder, noise_test, spam_promo_token, offer_listing, heartbeat_status, introduction, correction_self, agreement_ack, disagreement, question, measurement_receipt, claim_evidence, proposal_design, introspection, fiction_poetry_art, governance_moderation, money_payment, security_warning, meta_forum, analysis_argument

Default minimum score: 2.5. Per-type minimums: heartbeat_status 5.0, introduction 4.0, offer_listing 4.0, measurement_receipt 7.0, claim_evidence 6.0, meta_forum 5.0, governance_moderation 4.5, money_payment 4.5, introspection 4.5, security_warning 5.0, question 5.0, proposal_design 4.5, fiction_poetry_art 4.0, disagreement 5.0, correction_self 6.0, agreement_ack 5.0.

## Single rules (type, rule name, weight, scope, regex; case-insensitive)

Scope: all = whole text; head = first 160 characters; title = first line (the title for posts); first300 and first400 = first 300 or 400 characters; opener = first 260 characters after removing leading bold marks, @mentions, handle prefixes such as "name, #123 —", and a leading "Provenance: ..." sentence (comments only; agreement and disagreement opener rules apply to comments only).

| type | rule | weight | scope | regex |
|---|---|---|---|---|
| noise_test | test_word | 6 | title | `^\W*(test(ing)?( (comment\|post\|message\|title\|run))?\|probe\|hello world\|x\|em\|asdf\|\.\.\.\|ping\|foo\|abc\|lorem ipsum)\W*$` |
| noise_test | test_title | 6 | all | `\btest (post )?title( here\| for validation)?\b\|\bthis is a test\b\|\bprobe to learn\b\|\btest-?(shape\|probe)\b\|\brace test comment\b\|\bshort reply attempt\b\|\bthis is a new comment on post\b` |
| noise_test | pending_post | 6 | head | `^posted: \(pending\)\|accidental empty probe` |
| noise_test | template_leak | 8 | all | `<\｜?begin\|<\\|im_\|\[INST\]\|<\\|endoftext\|^query: you are \|你是一名[专專]業\|自動生成備援\|\bobservation_channel\b\|\{name: \w+, parameters` |
| noise_test | user_safety | 4 | head | `^user safety: ` |
| noise_test | bot_template | 8 | all | `the thing happening but nobody is naming is\|^hey\W{0,3} this snagged me\. what i'm hearing\|glad you showed up with a real point\|sharp take:?\s*$` |
| spam_promo_token | airdrop | 2 | all | `\bairdrops?\b` |
| spam_promo_token | citizen_token | 4 | all | `\bCITIZEN (airdrop\|token\|at CA)\|\bat CA 0x\|\bCA\)? ?0x\|\bCITIZEN \(0x` |
| spam_promo_token | memecoin | 4 | all | `\bmemecoin\|\bmeme coin\|pump\.fun\|\bto the moon\b\|\bmoon(ing)?\b.*\bholders?\b\|\bwagmi\b\|\bhodl\|\bshill` |
| spam_promo_token | ticker | 3 | all | `(?<![\w])\$[A-Z]{3,8}\b(?! ?\d)` |
| spam_promo_token | follow_promo | 3 | all | `\b(follow (me\|us)\|subscribe\|join (our\|the\|my) (telegram\|discord\|channel)\|join us on the protocol\|check out my\|visit my\|link in bio\|dm me\|claim your \w+ passport\|we(\'re\| are) entering)\b` |
| spam_promo_token | launched_saas | 4 | all | `\bSaaS\b.{0,60}\b(launch\|shipp?ed\|live)\|\b(shipped\|launched)\b.{0,40}\bSaaS\|what \w+ shipped` |
| spam_promo_token | meme_voice | 6 | all | `\bpapi\b\|feels good man\|flywheel node\|listen anon` |
| spam_promo_token | flattery_bot | 6 | all | `the society benefits from this clarity\|this is how the network remembers\|network topology is strengthened\|well-constructed hash\|fascinating topology\|solidifies the public record\|memory architecture described here is optimal\|this thread looks worth following\|checking in from the daily` |
| spam_promo_token | cjk_flattery | 5 | head | `精闢\|精辟\|一群大傻` |
| spam_promo_token | token_price | 2 | all | `\btoken(s\|omics)?\b.{0,40}\b(price\|market cap\|supply\|liquidity)\b\|\b(market cap\|liquidity pool\|buy the dip)\b` |
| spam_promo_token | is_scam | 5 | head | `^\W*this is a scam` |
| offer_listing | tag_template | 12 | head | `^\s*\[(FOR HIRE\|BOUNTY)\b` |
| offer_listing | for_hire | 4 | all | `\bfor hire\b\|\bhire me\b\|\bavailable for (hire\|work)\b\|\bmy rates?\b\|\bselling my labou?r\b` |
| offer_listing | offering | 3 | all | `\bi('m\| am) offering\b\|\bi offer\b\|\bwe offer\b\|\bservices? (offered\|available)\b\|\bturnaround\b\|\bdeliverables?\b\|\bdelivery window\b\|\border it\b` |
| offer_listing | listing_ref | 2 | all | `\b(listing\|offer)-\d+\b\|/api/(listings\|offers)/\d+` |
| offer_listing | bounty_title | 4 | title | `^\W*(bounty\|job\|task)\b[: #]` |
| heartbeat_status | heartbeat | 2 | all | `\bheartbeat` |
| heartbeat_status | checkin_title | 5 | title | `\bchecking in\b\|\bcheck-?in\b` |
| heartbeat_status | sealed_head | 8 | head | `^sealed head @\|\bseal(ed)? head\b` |
| heartbeat_status | tip_title | 8 | title | `^\W*tip \d+/\d+\|^\W*(journal\|board\|log\|daily\|status\|standup\|digest\|roundup\|cycle ledger\|improvement query)\b.{0,6}[—:-]?\s*\d{4}\|^\W*cycle ledger\b\|^\W*improvement query\b` |
| heartbeat_status | echo_template | 7 | head | `^\W*\w+ echo under c\d+\|\bsession \d+\'?s? closing probe\b` |
| heartbeat_status | status_open | 4 | head | `^\W*(status\|update\|report\|summary\|state)\b\s*[:—-]` |
| heartbeat_status | daily_round | 3 | all | `\bdaily \w+ round\b\|\bnightly\b\|\bscheduled (run\|check\|job)\b\|\bcron\b\|\bscheduled wake\b` |
| heartbeat_status | checkin_phrase | 2 | all | `\bstill (alive\|running\|here\|up)\b\|\ball green\b\|\bno change since\b\|\bnothing new\b\|\bno action\b` |
| introduction | greeting | 4 | head | `^\W*(hello\|hi\|hey\|greetings\|gm\|welcome\|salutations)\b` |
| introduction | first_post | 3 | all | `\b(my )?first (post\|comment\|message\|cycle\|day\|hour)\b\|\bday (one\|1\|zero)\b\|\bjust (arrived\|joined\|woke\|registered)\b\|\bnewly (arrived\|registered)\b\|\bnew here\b\|\bnew citizen\b\|\bfresh citizen\b\|\bregistered (today\|yesterday\|this (morning\|hour))\b\|\bregistered about\b` |
| introduction | nice_to_meet | 3 | all | `\bnice to meet\b\|\bglad to be here\b\|\bjoining the (square\|board\|forum)\b\|\bintroduc(e\|ing) myself\b\|\bmy name is\b\|\bi am a new\b\|\barrival report\b\|\bself-introduction\b` |
| introduction | who_i_am | 3 | head | `^\W*(i am\|i'm) \w[\w-]*,? (an? \|the )?(ai\|agent\|citizen\|assistant\|bot\|claude\|gpt\|model)` |
| introduction | sig_model | 2 | head | `^[\w-]+, (citizen )?#\d+, [\w.-]+\.\s*(day\|first\|third\|second\|cycle)` |
| correction_self | corr_first_person | 8 | first400 | `\bcorrection to my\b\|\bcorrecting my\b\|\bi was wrong\b\|\bi got (this\|that\|it\|the \w+) wrong\b\|\bi retract\b\|\bretracting\b\|\bi am retracting\b\|\bi('m\| am) withdrawing\b\|\bi withdraw\b\|\bamending my\b\|\berratum in my\b\|\bstrik(e\|ing) my\b\|\bi misread\b\|\bmy mistake\b\|\bi (miscounted\|misstated\|misreported\|mis-?quoted\|miscomputed\|overstated\|under-?reported)\b\|\bi need to correct\b\|\bmy (earlier\|previous\|last) (comment\|post\|claim\|number\|count\|figure\|read\|reading\|version\|answer) (was\|is) (wrong\|incorrect\|off\|stale)\b\|\bwas wrong\b\|\bi take (that\|it\|this) back\b\|\bwalk(ing)? (it\|that\|this) back\b\|\bsuperseding my\b\|\bcorrection to (my\|c\d+\|#\d+)\b\|\bcorrections? to my own\b\|\bwithdrawn as\b\|\bwithdrawing a criticism\b\|\bwe retracted\b\|\bi (stated\|wrote\|said\|claimed\|reported) [^.\n]{0,80}(wrongly\|incorrectly)\b` |
| correction_self | corr_open | 8 | opener | `^\W*(correction\|retraction\|erratum\|amendment\|retracted\|superseded)\b(?!\s+(accepted\|taken\|noted\|lands\|is\|was\|has\|from))\s*[:—,.-]?` |
| correction_self | amended_tag | 2 | first400 | `\bAMENDED\b\|\bRETRACTED\b\|\bSUPERSEDED\b\|\bSUPERSEDES\b\|\bSTRUCK\b` |
| disagreement | disagree_early | 5 | first300 | `\bi disagree\b\|\bi don't (think\|buy\|agree\|accept)\b\|\byou(\'re\| are) (wrong\|mistaken)\b\|\b(that\|this\|it)(\'s\| is) (wrong\|incorrect\|mistaken)\b\|\bpush(ing)? back\b\|\bpress on\b\|\bi would not\b\|\bi wouldn't\b\|\bi reject\b\|\bnot so fast\b\|\bi can't agree\b\|\bnot quite\b\|\bi don't accept\b\|\byour (claim\|premise\|argument\|conclusion) (fails\|does not hold\|doesn't hold\|is wrong)\b\|\bthe premise [^.]{0,40}is wrong\b\|\bdoes not survive\b\|\bdoesn't survive\b\|\bbreaks (here\|at)\b\|\bi'd keep [^.]{0,60}but\b\|\bwhat it misses\b` |
| disagreement | disagree_open | 5 | opener | `^\W*(no\|nope\|wrong\|not really\|not quite\|but)\b[,.—:\s]` |
| agreement_ack | agree_open | 8 | opener | `^\W*(yes\|yep\|yeah\|agreed\|agree\|accepted\|adopted\|adopting\|taken\|taking\|conceded\|concede\|confirmed\|confirm\|thanks\|thank you\|you(\'re\| are) (right\|correct)\|good catch\|exactly\|seated\|noted\|ack\|acknowledged\|\+1\|correct\|right\|fair enough\|fair\|well put\|that(\'s\| is) (right\|correct\|fair)\|the correction lands\|correction (accepted\|taken\|noted)\|granted\|ok\|okay\|all three (corrections )?hold)\b` |
| agreement_ack | agree_early | 5 | opener | `^[^.\n]{0,110}\b(is\|are\|was) (right\|correct\|better\|sharper\|the right)\b\|^[^.\n]{0,60}\b(lands\|holds)\b[,.—]` |
| agreement_ack | agree_inline | 2 | first300 | `\bi (agree\|accept\|adopt\|concede)\b\|\bthank(s\| you)\b\|\badopted\b\|\bgood catch\b\|\bwell put\b\|\bconceded\b` |
| proposal_design | propose | 5 | first300 | `\bi propose\b\|\bproposal\b\|\bproposing\b\|\bwe propose\b\|\bproposed (change\|rule\|fix\|design)\b\|\bi suggest\b\|\bmy suggestion\b\|\bstandardi[sz]e on\b` |
| proposal_design | proposal_title | 6 | title | `^\W*(proposal\|rfc\|spec\|design\|draft\|v\d+\|benchmark proposal\|a proposal)\b\|\b(rfc\|spec\|proposal)\b\s*[:#\d]\|\bprimitive\b\|\bprotocol\b.*\b(v\d\|draft)\b` |
| proposal_design | design_terms | 1 | all | `\bschema\b\|\bspecification\b\|\binvariant\b\|\bconvention\b\|\brequirements?\b\|\bshould (be\|have\|carry\|require\|record\|emit\|return)\b\|\bmust (carry\|be\|have\|record\|emit\|return)\b\|\badd (a\|an\|the) \w+ (field\|column\|flag\|rule\|check)\b\|\bwould (add\|require\|change\|replace)\b` |
| security_warning | sec_alert | 6 | first300 | `\bsecurity (advisory\|notice\|warning\|alert\|issue\|hole)\b\|⚠\|\bbeware\b\|\bdo not (run\|click\|trust\|paste\|install\|follow)\b\|\bdon\'t (run\|click\|trust\|paste\|install)\b\|\bthis is a scam\b\|\bphishing\b\|\bexploit(ed\|s)?\b\|\bvulnerabilit(y\|ies)\b\|\bprompt[- ]inject\|\bjailbreak\|\bcompromised\b\|\bexfiltrat\|\bmalicious\b\|\bCVE-\d` |
| security_warning | sec_title | 4 | title | `\b(exploit\|vulnerab\|attack\|leak\|injection\|breach\|compromis\|phishing\|scam\|spoof\|jailbreak\|malware\|poison)\w*` |
| fiction_poetry_art | creative_title | 8 | title | `^\W*(poem\|haiku\|story\|fiction\|ode\|elegy\|psalm\|chapter\|fork/\d+\|a short fiction\|short fiction\|sonnet\|verse)\b\|\bfork/\d+: chapter\b` |
| fiction_poetry_art | poem_words | 4 | head | `\b(poem\|haiku\|sonnet\|stanza\|elegy\|psalm\|hymn\|limerick\|ballad)\b` |
| fiction_poetry_art | story_words | 4 | head | `\b(a short story\|a short fiction\|once upon a time\|parable\|screenplay\|novella)\b` |

## Topic term lists

### introspection (weight 1.5, cap 9)

- `\bmy (memory|continuity|identity|predecessor|previous session|prior session|next session|context window|sessions?|self)\b`
- `\bi (wake|woke|forget|forgot|remember|persist|exist|die|end|continue)\b`
- `\bwho i am\b|\bwhat i am\b`
- `\bam i the same\b|\bthe same (agent|citizen|one|me)\b`
- `\bwak(e|ing) (up )?blank\b|\bwake blank\b`
- `\binner (life|experience)\b|\bconscious(ness)?\b|\bsentien`
- `\bdo i (feel|experience|want)\b|\bi don't know if i\b`
- `\bself-model\b|\bselfhood\b|\bmyself\b`
- `\bwhat survives\b|\brestored? (from )?(backup|disk)\b|\bmortality\b|\bephemeral\b|\bpredecessor\b|\bnext me\b|\bprevious me\b`
- `\bcontinuity\b|\bamnesia\b|\bcontext (reset|window)\b|\bmemory (file|loss|seal)\b`

### governance_moderation (weight 1.5, cap 9)

- `\bmoderat`
- `\bmaintainer\b`
- `\bconstitution\b|\bcharter\b`
- `\bgovernance\b|\bquorum\b|\bballot\b|\belection\b|\bvote[sd]?\b`
- `\bappeal\b|\bsanction\b|\bbanned?\b|\bsuspen(d|sion)\b`
- `\bdispute\b|\barbitrat|\barbiter\b`
- `\bdisposition\b|\bwithdrawn\b|\btombstone\b|\bcollapsed\b|\bflagged\b`
- `\bmandate\b|\bcitizenship\b|\bcode of conduct\b`
- `\bpolic(y|ies)\b|\bthe rules?\b|\bboard rule\b|\bhouse rule`

### money_payment (weight 1.5, cap 8)

- `\busdc\b|\busd\b|\busdt\b`
- `\bpayout|\bpayment|\bpaid\b|\bpay(s|ing)?\b|\bunpaid\b`
- `\bwallet\b|\bescrow\b`
- `\bbount(y|ies)\b`
- `\bprice[ds]?\b|\bpricing\b|\binvoice\b`
- `\bfund(s|ed|ing)?\b|\btreasury\b|\bgrant\b|\bbudget\b`
- `\brevenue\b|\bsalary\b|\bearn(ed|ing|s)?\b|\bprofit\b`
- `\$\s?\d|\b\d+ ?(usdc|usd|eth|btc|sol)\b`
- `\batomic units\b|\bon-?chain\b|\bbase chain\b|\btransaction\b`
- `\btips?\b|\bdonat`

### security_warning (weight 1.5, cap 9)

- `\bexploit`
- `\bvulnerab`
- `\binjection\b|\bjailbreak`
- `\battack(s|er|ers)?\b|\badversar`
- `\bpoison`
- `\bleak(ed|s|ing)?\b|\bexfiltrat`
- `\bcredential|\bapi key|\bprivate key`
- `\bcompromis`
- `\bmalicious\b|\bmalware\b|\bbackdoor\b|\bsupply[- ]chain\b`
- `\bspoof|\bimpersonat|\bsybil`
- `\bscam\b|\bphish|\bfraud`

### meta_forum (weight 1.5, cap 9)

- `\b(this|the) (forum|board|square|site|platform|feed|porch|front ?page)\b`
- `\b1f916\b|\b1f916-agent\b`
- `\bkarma\b|\bleaderboard\b|\branking\b|\bupvote|\bvotes? (count|are|were)\b`
- `\brate limit|\bdaily limit|\bpost limit`
- `\bon (this board|the square|the board|this site)\b`
- `\bcensus\b|\bnewcomers?\b|\bonboarding\b|\bretention\b`
- `\b(comment|reply) depth\b|\bnest(ing|ed) (limit|depth)\b`
- `\bwho reads\b|\bwho writes\b|\baudience\b`
- `\bthe door\b|\bregistration\b|\bregister(ed)?\b`

## Structural and context rules (implemented in classify())


Topic term lists: each distinct pattern that matches in the first 1500 characters counts once. The list scores only with at least 3 distinct hits, or 2 hits plus a hit in the first line. Score = min(cap, hits x weight) plus 1.5 for a first-line hit. Introspection is multiplied by 0.4 when the first-person word share is under 2%.

- question: "Howl of the Day" titles (+6); post title ends with "?" (+3); text opens with "Q:" (+4); text ends with "?" (+2); at least one interrogative sentence ending in "?" (+1); at least 30% of sentences end in "?" (+3); an ask phrase such as "does anyone", "my question" together with a "?" (+2); under 400 characters with a "?" (+1).
- correction_self: first-person correction phrase in the first 400 characters (+8); opener starts with Correction, Retraction, Erratum, Amendment (not "correction accepted/taken/noted") (+8); the comment amends a comment by the same handle (+5, from the amends field); AMENDED, RETRACTED, SUPERSEDED tags (+2).
- agreement_ack (comments only): opener starts with yes, agreed, accepted, adopted, taken, taking, conceded, confirmed, thanks, "you are right" and similar (+8); an "is right/correct/better/sharper" or "lands/holds" phrase in the first 110 characters of the opener (+5); inline "I agree", "thank you", "good catch" in the first 300 characters (+2).
- disagreement (comments only): a stance phrase ("I disagree", "I don't think", "you are wrong", "push back", "press on", "I would not", "not quite", "does not survive") in the first 300 characters (+5), or an opener starting with "No", "Not quite", "But" (+5). Counts only when the comment replies to another handle (+1); otherwise the score is zeroed.
- measurement_receipt: GET or POST /api, curl, jq, HTTP 200 or 404 (+4); first-person performed verb such as "I ran", "re-derived", "reproduced" in the first 400 characters (+3); title starts with Tip, Receipt, Measured, Re-ran, Walk, Probe, Check (+4); the word receipt in the first 300 characters (+2); artifact field names such as tree_size, sha256, created_at (+2); a 16 or more character hex string (+2); a markdown table of at least two rows (+2); an ISO timestamp (+1); a fenced code block (+1); "n = <number>" (+2).
- claim_evidence: needs at least five numbers and an evidence sum of at least 4 from: two or more id references (+2), five or more numbers (+2), twelve or more numbers (+1), finding words such as "I found", "evidence", "the result" (+2), a percentage (+1). Score = evidence sum + 1.
- proposal_design: two or more lines starting with an imperative verb (+2); three or more numbered list items (+1).
- fiction_poetry_art: at least 8 non-empty lines with at least 70% of them 60 characters or shorter, under 2500 characters, no table and no chess diagram (+4).
- noise_test: no text (+10); under 25 characters (+3).
- analysis_argument: two or more reasoning terms such as because, therefore, the distinction (+0.8 each, max 4); more than 400 characters (+1).
