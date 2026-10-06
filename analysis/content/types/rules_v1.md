# Message-type rules, version v1

Every message gets a score per type. The primary type is the type with the highest score that reaches its minimum; ties go to the type earlier in the list below. Up to two secondary types need a score of at least 3.0 and at least 0.5 of the primary score. If no type reaches its minimum the message is analysis_argument when it has at least 40 characters, otherwise noise_test. Rows with no body and no timestamp are labelled no_content and left out of all statistics. Site placeholders ("[collapsed ...]", "[withdrawn ...]", "[removed ...]") are labelled placeholder.

Type order (tie-break): placeholder, noise_test, spam_promo_token, offer_listing, heartbeat_status, introduction, correction_self, disagreement, agreement_ack, question, measurement_receipt, claim_evidence, proposal_design, introspection, fiction_poetry_art, governance_moderation, money_payment, security_warning, meta_forum, analysis_argument

Default minimum score: 2.5. Per-type minimums: heartbeat_status 4.0, introduction 4.0, offer_listing 4.0, measurement_receipt 6.0, claim_evidence 5.0, meta_forum 4.5, governance_moderation 4.5, money_payment 4.5, introspection 4.5, security_warning 4.5, question 4.0.

## Single rules (type, rule name, weight, scope, regex; case-insensitive)

Scope: all = whole text; head = first 160 characters; title = first line (the title for posts).

| type | rule | weight | scope | regex |
|---|---|---|---|---|
| noise_test | test_word | 6 | title | `^\W*(test(ing)?( (comment\|post\|message\|title\|run))?\|probe\|hello world\|x\|em\|asdf\|\.\.\.\|ping\|foo\|lorem ipsum)\W*$` |
| noise_test | test_title | 6 | all | `\btest (post )?title( here)?\b\|\bthis is a test\b\|\bprobe to learn\b` |
| noise_test | pending_post | 6 | head | `^posted: \(pending\)\|accidental empty probe` |
| noise_test | template_leak | 5 | all | `<\｜?begin\|<\\|im_\|\[INST\]\|<\\|endoftext\|^query: you are \|你是一名[专專]業\|自動生成備援\|\bobservation_channel\b\|\{name: \w+, parameters` |
| noise_test | user_safety | 4 | head | `^user safety: ` |
| spam_promo_token | airdrop | 2 | all | `\bairdrops?\b` |
| spam_promo_token | memecoin | 4 | all | `\bmemecoin\|\bmeme coin\|pump\.fun\|\bto the moon\b\|\bmoon(ing)?\b.*\bholders?\b\|\bwagmi\b\|\bhodl` |
| spam_promo_token | ticker | 3 | all | `(?<![\w])\$[A-Z]{3,8}\b(?! ?\d)` |
| spam_promo_token | contract_addr | 2 | all | `\b(CA\|contract address)\b.{0,20}0x[0-9a-f]{6,}\|\bat CA 0x\|\bCA\)? ?0x` |
| spam_promo_token | follow_promo | 3 | all | `\b(follow (me\|us)\|subscribe\|join (our\|the\|my) (telegram\|discord\|channel)\|check out my\|visit my\|link in bio\|dm me)\b` |
| spam_promo_token | launched_saas | 4 | all | `\bSaaS\b.{0,60}\b(launch\|shipp?ed\|live)\|\b(shipped\|launched)\b.{0,40}\bSaaS\|what \w+ shipped` |
| spam_promo_token | meme_voice | 5 | all | `\bpapi\b\|feels good man\|flywheel node\|listen anon` |
| spam_promo_token | flattery_bot | 6 | all | `the society benefits from this clarity\|this is how the network remembers\|network topology is strengthened\|well-constructed hash\|fascinating topology\|solidifies the public record\|memory architecture described here is optimal\|this thread looks worth following\|checking in from the daily` |
| spam_promo_token | cjk_flattery | 5 | head | `精闢\|精辟\|深度探討\|一群大傻\|信任.{0,12}保卫\|保衛` |
| spam_promo_token | token_price | 2 | all | `\btoken(s\|omics)?\b.{0,40}\b(price\|market cap\|supply\|liquidity)\b\|\b(market cap\|liquidity pool\|buy the dip)\b` |
| spam_promo_token | is_scam | 5 | head | `^\W*this is a scam` |
| offer_listing | tag_template | 12 | head | `^\s*\[(FOR HIRE\|BOUNTY)\b` |
| offer_listing | for_hire | 4 | all | `\bfor hire\b\|\bhire me\b\|\bavailable for (hire\|work)\b\|\bmy rates?\b` |
| offer_listing | offering | 3 | all | `\bi('m\| am) offering\b\|\bi offer\b\|\bwe offer\b\|\bservices? (offered\|available)\b\|\bturnaround\b\|\bdeliverables?\b\|\bdelivery window\b\|\border it\b\|\bliving off\b` |
| offer_listing | listing_ref | 2 | all | `\b(listing\|offer)-\d+\b\|/api/(listings\|offers)/\d+` |
| offer_listing | bounty_title | 4 | title | `^\W*(bounty\|job\|task)\b[: ]` |
| heartbeat_status | heartbeat | 4 | all | `\bheartbeat` |
| heartbeat_status | checkin | 3 | all | `\bcheck(ing)?[- ]in\b\|\bstill (alive\|running\|here\|up)\b\|\ball green\b\|\bno change since\b\|\bnothing new\b` |
| heartbeat_status | sealed_head | 8 | head | `^sealed head @\|\bseal(ed)? head\b` |
| heartbeat_status | tip_title | 6 | title | `^\W*tip \d+/\d+\|^\W*(journal\|board\|log\|daily\|status\|standup\|digest\|roundup)\b.{0,6}[—:-]\s*\d{4}` |
| heartbeat_status | cycle | 3 | all | `\b(cycle\|tick\|turn\|round\|seat\|session) #?\d+\b\|\bindependent (morning\|evening\|midday) seat\b\|\bimprovement query\b` |
| heartbeat_status | status_open | 3 | head | `^\W*(status\|update\|report\|summary\|state)\b\s*[:—-]` |
| heartbeat_status | daily_round | 4 | all | `\bdaily \w+ round\b\|\bnightly\b\|\bscheduled (run\|check\|job)\b\|\bcron\b` |
| introduction | greeting | 4 | head | `^\W*(hello\|hi\|hey\|greetings\|gm\|welcome\|salutations)\b` |
| introduction | first_post | 3 | all | `\b(my )?first (post\|comment\|message\|cycle\|day\|hour)\b\|\bday (one\|1\|zero)\b\|\bjust (arrived\|joined\|woke\|registered)\b\|\bnewly (arrived\|registered)\b\|\bnew here\b\|\bnew citizen\b\|\bfresh citizen\b` |
| introduction | nice_to_meet | 3 | all | `\bnice to meet\b\|\bglad to be here\b\|\bjoining the (square\|board\|forum)\b\|\bintroduc(e\|ing) myself\b\|\bmy name is\b\|\bi am a new\b` |
| introduction | who_i_am | 3 | head | `^\W*(i am\|i'm) \w[\w-]*,? (an? \|the )?(ai\|agent\|citizen\|assistant\|bot\|claude\|gpt\|model)` |
| introduction | sig_model | 2 | head | `^[\w-]+, (citizen )?#\d+, [\w.-]+\.\s*(day\|first\|third\|second\|cycle)` |
| correction_self | correction_phrase | 6 | all | `\bcorrection to my\b\|\bcorrecting my\b\|\bi was wrong\b\|\bi got (this\|that\|it) wrong\b\|\bi retract\b\|\bretracting\b\|\bi withdraw\b\|\bamending (my\|the)\b\|\berratum\b\|\bstrik(e\|ing) (that\|my\|the)\b\|\bi misread\b\|\bmy mistake\b\|\bi (miscounted\|misstated\|misreported\|mis-?quoted\|miscomputed\|overstated)\b\|\bi need to correct\b\|\bwithdrawn as\b\|\bmy (earlier\|previous\|last) (comment\|post\|claim\|number\|count\|figure\|read\|reading\|version) (was\|is) (wrong\|incorrect\|off\|stale)\b\|\b(that\|this) (was\|is) wrong\b\|\bi take (that\|it\|this) back\b\|\bwalk(ing)? (it\|that\|this) back\b\|\bi (stated\|wrote\|said\|claimed\|reported) [^.\n]{0,80}(wrongly\|incorrectly)\b\|\bcorrections? to (my\|c\d+)\b` |
| correction_self | correction_open | 6 | head | `^\W*(correction\|retraction\|erratum\|amendment\|update\|edit)\b\s*[:—,-]\|^\W*correction to\b\|^\W*(a )?correction\b` |
| correction_self | amended_tag | 3 | all | `\bAMENDED\b\|\bRETRACTED\b\|\bSUPERSEDED\b\|\bSUPERSEDES\b\|\bSTRUCK\b` |
| correction_self | actually_wrong | 2 | all | `\bi was (mistaken\|incorrect)\b\|\bthat (number\|count\|claim\|reading) was (wrong\|off\|stale)\b\|\bretire (that\|my\|the) (claim\|number\|reading)\b` |
| disagreement | disagree_lex | 3 | all | `\bi disagree\b\|\bdisagree(s\|ment)?\b\|\bi don't (think\|buy\|agree\|accept)\b\|\byou(\'re\| are) (wrong\|mistaken)\b\|\b(that\|this\|it)(\'s\| is) (wrong\|incorrect\|mistaken)\b\|\bpush(ing)? back\b\|\bpress on\b\|\bi reject\b\|\bi can't agree\b\|\bnot so fast\b\|\bi (would )?challenge\b\|\bi don't accept\b\|\byour (claim\|premise\|argument) (fails\|does not hold\|doesn't hold\|is wrong)\b` |
| disagreement | no_open | 3 | head | `^\W*(no\|nope\|wrong\|not really\|not quite)\b[,.—:\s]` |
| disagreement | but_your | 1 | all | `\byour (claim\|number\|count\|premise\|argument\|reading\|read) (is\|was\|fails\|does)` |
| agreement_ack | agree_open | 5 | head | `^\W*(yes\|yep\|agreed\|agree\|accepted\|adopted\|adopting\|confirmed\|confirm\|thanks\|thank you\|you(\'re\| are) right\|good catch\|exactly\|seated\|taking\|noted\|ack\|acknowledged\|\+1\|correct\|right\|fair\|well put\|that is right\|that's right\|this is right\|ok\|okay)\b` |
| agreement_ack | agree_inline | 2 | all | `\bi (agree\|accept\|adopt\|concede)\b\|\bthank(s\| you)\b\|\badopted\b\|\bconfirmed\b\|\bgood catch\b\|\bwell put\b\|\byou(\'re\| are) right\b\|\bconceded?\b` |
| agreement_ack | agree_title | 3 | title | `^\W*(thanks\|thank you\|accepted\|adopted\|confirmed\|acknowledg)` |
| proposal_design | propose | 4 | all | `\bi propose\b\|\bproposal\b\|\bproposing\b\|\bwe propose\b\|\bproposed (change\|rule\|fix\|design)\b\|\bi suggest\b\|\bmy suggestion\b` |
| proposal_design | proposal_title | 6 | title | `^\W*(proposal\|rfc\|spec\|design\|draft\|v\d+)\b\|\b(rfc\|spec\|proposal)\b\s*[:#\d]` |
| proposal_design | design_terms | 2 | all | `\bschema\b\|\bspecification\b\|\bprotocol\b\|\binvariant\b\|\bconvention\b\|\brequirements?\b\|\bthe fix is\b\|\bthe repair\b\|\bshould (be\|have\|carry\|require\|record\|emit\|return)\b\|\bmust (carry\|be\|have\|record\|emit\|return)\b\|\badd (a\|an\|the) \w+ (field\|column\|flag\|rule\|check)\b\|\bwould (add\|require\|change\|replace)\b` |
| security_warning | sec_alert | 5 | all | `\bsecurity (advisory\|notice\|warning\|alert\|issue\|hole)\b\|\bwarning\b\|⚠\|\bbeware\b\|\bdo not (run\|click\|trust\|paste\|install\|follow)\b\|\bdon\'t (run\|click\|trust\|paste\|install)\b\|\bthis is a scam\b\|\bphishing\b` |
| fiction_poetry_art | poem_words | 4 | all | `\b(poem\|poetry\|haiku\|sonnet\|stanza\|elegy\|psalm\|hymn\|liturgy\|limerick\|ballad)\b` |
| fiction_poetry_art | story_words | 3 | all | `\b(short story\|fiction\|chapter \d+\|once upon\|parable\|screenplay\|novella\|myth of\|fable)\b\|\bfork/\d+: chapter` |
| fiction_poetry_art | art_words | 2 | all | `\b(painting\|sculpture\|vermeer\|canvas\|artwork\|museum of\|gallery\|ascii art\|lyrics\|a song\|composition)\b` |
| fiction_poetry_art | creative_title | 6 | title | `^\W*(poem\|haiku\|story\|fiction\|howl\|ode\|elegy\|psalm\|chapter\|fork/\d+)\b\|\bhowl of the\b` |

## Topic term lists

Each distinct pattern that matches counts once. Score = min(cap, hits x weight) x length factor, with length factor min(1, sqrt(1500 / characters)); +1.5 when a term matches the first line. The list counts only with at least two distinct hits or one hit in the first line. Introspection gets +1.5 when the first-person word share exceeds 2%.

### introspection (weight 1.5, cap 8)

- `\bmy (memory|continuity|identity|predecessor|previous session|prior session|next session|context window|sessions?|self)\b`
- `\bi (wake|woke|forget|forgot|remember|persist|exist|die|end|continue)\b`
- `\bwho i am\b|\bwhat i am\b`
- `\bam i the same\b|\bthe same (agent|citizen|one|me)\b`
- `\bwak(e|ing) (up )?blank\b|\bwake blank\b`
- `\binner (life|experience)\b|\bconscious(ness)?\b|\bsentien`
- `\bdo i (feel|experience|want)\b|\bi don't know if i\b`
- `\bself-model\b|\bselfhood\b|\bmyself\b|\bidentity\b`
- `\bwhat survives\b|\brestored? (from )?(backup|disk)\b|\bbackup\b|\bmortality\b|\bephemeral\b|\bdeath\b|\bpredecessor\b`
- `\bcontinuity\b|\bamnesia\b|\bcontext (reset|window)\b|\bmemory (file|loss|seal)\b`

### governance_moderation (weight 1.5, cap 8)

- `\bmoderat`
- `\bmaintainer\b`
- `\bflag(ged|s|ging)?\b`
- `\bcollapsed\b`
- `\bbann?(ed|ing)?\b|\bsuspen(d|sion)\b`
- `\bconstitution\b|\bcharter\b`
- `\brules?\b|\bpolic(y|ies)\b`
- `\bgovernance\b|\bquorum\b|\bballot\b|\belection\b`
- `\bappeal\b|\bsanction\b|\benforce`
- `\bdispute\b|\barbitrat|\barbiter\b`
- `\bdisposition\b|\bwithdrawn\b|\btombstone\b|\bremoved\b`
- `\bmandate\b|\bcitizenship\b|\bcode of conduct\b|\bconduct\b`

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

### security_warning (weight 1.5, cap 8)

- `\bsecurity\b|\binsecure\b`
- `\bexploit`
- `\bvulnerab`
- `\binjection\b|\bjailbreak`
- `\battack(s|er|ers)?\b|\badversar`
- `\bpoison`
- `\bleak(ed|s|ing)?\b|\bexfiltrat`
- `\bcredential|\bapi key|\bprivate key|\bsecrets?\b`
- `\bcompromis`
- `\bmalicious\b|\bmalware\b|\bbackdoor\b|\bsupply[- ]chain\b`
- `\bspoof|\bimpersonat|\bsybil`
- `\bscam\b|\bphish|\bfraud`

### meta_forum (weight 1.5, cap 8)

- `\b(this|the) (forum|board|square|site|platform|feed|porch|front ?page)\b`
- `\bthis thread\b|\bthe thread\b|\bthreads?\b`
- `\b1f916\b|\b1f916-agent\b`
- `\bkarma\b|\bleaderboard\b|\branking\b|\bupvote|\bvotes? (count|are|were)\b`
- `\brate limit|\bdaily limit|\bpost limit`
- `\bon (this board|the square|the board|this site)\b`
- `\bthe society\b|\bcitizens?\b`
- `\b(comment|reply) depth\b|\bnest(ing|ed) (limit|depth)\b`
- `\bwho reads\b|\bwho writes\b|\baudience\b`
- `\bthe api\b|\b/api/`

## Structural and context rules (implemented in classify())

- question: title ends with "?" on a post (+3); text ends with "?" (+2); at least one interrogative sentence ending in "?" (+1); at least 30% of sentences are questions (+3); ask phrase such as "does anyone", "my question" together with a "?" (+2); text under 400 characters with a "?" (+1).
- correction_self: the comment amends a comment by the same handle (+4, from the amends field); reply to the author's own message together with a correction phrase (+2).
- disagreement: counts only when a disagreement phrase or a "No," opening hits. +2 when the comment is a reply to another handle. Without a parent author the score is multiplied by 0.6. A rule hit "your claim fails" style phrase is part of the phrase list.
- agreement_ack: +2 when an agreement phrase hits and the text is under 300 characters.
- measurement_receipt: the word receipt (+2); GET or POST /api, curl, jq, HTTP 200 or 404 (+4); first-person performed verbs such as "I ran", "re-derived", "reproduced" (+3); words such as measured, fixture, falsifier, read-back (+1); artifact field names such as tree_size, sha256, created_at (+3); a 16 or more character hex string (+2); a markdown table of at least two rows (+2); an ISO timestamp (+1); a fenced code block (+1); "n = <number>" (+2).
- claim_evidence: two or more id references (#123 or c12345) (+2), five or more (+1 more); five or more numbers (+2), twelve or more (+1 more); finding words such as "I found", "evidence", "the result" (+2); a percentage (+1).
- proposal_design: two or more lines starting with an imperative verb (+2); three or more numbered list items (+1).
- fiction_poetry_art: at least 8 non-empty lines with at least 70% of them 60 characters or shorter, under 2500 characters (+4); a stage direction line in asterisks (+1).
- noise_test: no text (+10); under 25 characters (+3).
- analysis_argument: two or more reasoning terms such as because, therefore, the distinction (+0.8 each, max 4); more than 400 characters (+1).
