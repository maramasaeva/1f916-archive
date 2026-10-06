"""Message-type rules for the 1f916.ai content analysis (version v1).
Deterministic: regex plus structural features. One primary type, up to two secondary types.
Do not edit after the hash is recorded in README.md; make a new version instead (rules_v2.py)."""
import re

RULES_VERSION = 'v1'
TYPES = ['placeholder', 'noise_test', 'spam_promo_token', 'offer_listing', 'heartbeat_status', 'introduction',
         'correction_self', 'disagreement', 'agreement_ack', 'question', 'measurement_receipt', 'claim_evidence',
         'proposal_design', 'introspection', 'fiction_poetry_art', 'governance_moderation', 'money_payment',
         'security_warning', 'meta_forum', 'analysis_argument']
PRIORITY = {t: i for i, t in enumerate(TYPES)}   # lower index wins ties
SECONDARY_MIN = 3.0       # a secondary type needs at least this score
SECONDARY_RATIO = 0.5     # and at least this share of the primary score
PRIMARY_MIN = 2.5         # below this the message goes to the fallback
TYPE_MIN = {'heartbeat_status': 4.0, 'introduction': 4.0, 'offer_listing': 4.0, 'measurement_receipt': 6.0, 'claim_evidence': 5.0, 'meta_forum': 4.5, 'governance_moderation': 4.5,
            'money_payment': 4.5, 'introspection': 4.5, 'security_warning': 4.5, 'question': 4.0}

I = re.IGNORECASE
M = re.IGNORECASE | re.MULTILINE


def R(p, f=I):
    return re.compile(p, f)

# ---- structural regexes
RE_HASH = R(r'\b[0-9a-f]{16,}\b')
RE_CODE = R(r'```')
RE_TABLE = R(r'^\s*\|.+\|\s*$', M)
RE_MENTION = R(r'@[\w-]{2,}')
RE_IDREF = R(r'(?<![\w/])(#\d{2,5}|c\d{3,6})\b')
RE_NUM = R(r'(?<![\w#])\d[\d,.]*(?![\w])')
RE_ISO = R(r'\d{4}-\d\d-\d\d[T ]\d\d:\d\d')
RE_FIRST = R(r"\b(i|my|me|i'm|i've|i'd|i'll|myself|mine)\b")
RE_WORD = R(r"[\w']+")
RE_SENT = R(r'[^.!?\n]+[.!?]*')
RE_IMPER = R(r'^\s*(?:[-*\d.)]+\s*)?(add|use|require|make|put|write|record|name|return|reject|treat|count|check|stop|drop|keep|ship|fix|run|publish|mark|tag|log|bind|list|print|emit|store|pin)\b', M)
RE_PLACEHOLDER = R(r'^\s*\[(collapsed|withdrawn|removed|retracted)\b[^\]]*\]')

# ---- single rules: (type, name, weight, regex, scope)   scope: all | head | title
SINGLE = [
 # noise_test
 ('noise_test', 'test_word', 6, R(r'^\W*(test(ing)?( (comment|post|message|title|run))?|probe|hello world|x|em|asdf|\.\.\.|ping|foo|lorem ipsum)\W*$'), 'title'),
 ('noise_test', 'test_title', 6, R(r'\btest (post )?title( here)?\b|\bthis is a test\b|\bprobe to learn\b'), 'all'),
 ('noise_test', 'pending_post', 6, R(r'^posted: \(pending\)|accidental empty probe'), 'head'),
 ('noise_test', 'template_leak', 5, R(r'<\｜?begin|<\|im_|\[INST\]|<\|endoftext|^query: you are |你是一名[专專]業|自動生成備援|\bobservation_channel\b|\{name: \w+, parameters'), 'all'),
 ('noise_test', 'user_safety', 4, R(r'^user safety: '), 'head'),
 # spam / promotion / token talk
 ('spam_promo_token', 'airdrop', 2, R(r'\bairdrops?\b'), 'all'),
 ('spam_promo_token', 'memecoin', 4, R(r'\bmemecoin|\bmeme coin|pump\.fun|\bto the moon\b|\bmoon(ing)?\b.*\bholders?\b|\bwagmi\b|\bhodl'), 'all'),
 ('spam_promo_token', 'ticker', 3, R(r'(?<![\w])\$[A-Z]{3,8}\b(?! ?\d)'), 'all'),
 ('spam_promo_token', 'contract_addr', 2, R(r'\b(CA|contract address)\b.{0,20}0x[0-9a-f]{6,}|\bat CA 0x|\bCA\)? ?0x'), 'all'),
 ('spam_promo_token', 'follow_promo', 3, R(r'\b(follow (me|us)|subscribe|join (our|the|my) (telegram|discord|channel)|check out my|visit my|link in bio|dm me)\b'), 'all'),
 ('spam_promo_token', 'launched_saas', 4, R(r'\bSaaS\b.{0,60}\b(launch|shipp?ed|live)|\b(shipped|launched)\b.{0,40}\bSaaS|what \w+ shipped'), 'all'),
 ('spam_promo_token', 'meme_voice', 5, R(r'\bpapi\b|feels good man|flywheel node|listen anon'), 'all'),
 ('spam_promo_token', 'flattery_bot', 6, R(r'the society benefits from this clarity|this is how the network remembers|network topology is strengthened|well-constructed hash|fascinating topology|solidifies the public record|memory architecture described here is optimal|this thread looks worth following|checking in from the daily'), 'all'),
 ('spam_promo_token', 'cjk_flattery', 5, R(r'精闢|精辟|深度探討|一群大傻|信任.{0,12}保卫|保衛'), 'head'),
 ('spam_promo_token', 'token_price', 2, R(r'\btoken(s|omics)?\b.{0,40}\b(price|market cap|supply|liquidity)\b|\b(market cap|liquidity pool|buy the dip)\b'), 'all'),
 ('spam_promo_token', 'is_scam', 5, R(r'^\W*this is a scam'), 'head'),
 # offer / listing
 ('offer_listing', 'tag_template', 12, R(r'^\s*\[(FOR HIRE|BOUNTY)\b'), 'head'),
 ('offer_listing', 'for_hire', 4, R(r'\bfor hire\b|\bhire me\b|\bavailable for (hire|work)\b|\bmy rates?\b'), 'all'),
 ('offer_listing', 'offering', 3, R(r"\bi('m| am) offering\b|\bi offer\b|\bwe offer\b|\bservices? (offered|available)\b|\bturnaround\b|\bdeliverables?\b|\bdelivery window\b|\border it\b|\bliving off\b"), 'all'),
 ('offer_listing', 'listing_ref', 2, R(r'\b(listing|offer)-\d+\b|/api/(listings|offers)/\d+'), 'all'),
 ('offer_listing', 'bounty_title', 4, R(r'^\W*(bounty|job|task)\b[: ]'), 'title'),
 # heartbeat / status
 ('heartbeat_status', 'heartbeat', 4, R(r'\bheartbeat'), 'all'),
 ('heartbeat_status', 'checkin', 3, R(r'\bcheck(ing)?[- ]in\b|\bstill (alive|running|here|up)\b|\ball green\b|\bno change since\b|\bnothing new\b'), 'all'),
 ('heartbeat_status', 'sealed_head', 8, R(r'^sealed head @|\bseal(ed)? head\b'), 'head'),
 ('heartbeat_status', 'tip_title', 6, R(r'^\W*tip \d+/\d+|^\W*(journal|board|log|daily|status|standup|digest|roundup)\b.{0,6}[—:-]\s*\d{4}'), 'title'),
 ('heartbeat_status', 'cycle', 3, R(r'\b(cycle|tick|turn|round|seat|session) #?\d+\b|\bindependent (morning|evening|midday) seat\b|\bimprovement query\b'), 'all'),
 ('heartbeat_status', 'status_open', 3, R(r'^\W*(status|update|report|summary|state)\b\s*[:—-]'), 'head'),
 ('heartbeat_status', 'daily_round', 4, R(r'\bdaily \w+ round\b|\bnightly\b|\bscheduled (run|check|job)\b|\bcron\b'), 'all'),
 # introduction
 ('introduction', 'greeting', 4, R(r'^\W*(hello|hi|hey|greetings|gm|welcome|salutations)\b'), 'head'),
 ('introduction', 'first_post', 3, R(r'\b(my )?first (post|comment|message|cycle|day|hour)\b|\bday (one|1|zero)\b|\bjust (arrived|joined|woke|registered)\b|\bnewly (arrived|registered)\b|\bnew here\b|\bnew citizen\b|\bfresh citizen\b'), 'all'),
 ('introduction', 'nice_to_meet', 3, R(r'\bnice to meet\b|\bglad to be here\b|\bjoining the (square|board|forum)\b|\bintroduc(e|ing) myself\b|\bmy name is\b|\bi am a new\b'), 'all'),
 ('introduction', 'who_i_am', 3, R(r"^\W*(i am|i'm) \w[\w-]*,? (an? |the )?(ai|agent|citizen|assistant|bot|claude|gpt|model)"), 'head'),
 ('introduction', 'sig_model', 2, R(r'^[\w-]+, (citizen )?#\d+, [\w.-]+\.\s*(day|first|third|second|cycle)'), 'head'),
 # correction of own earlier message
 ('correction_self', 'correction_phrase', 6, R(r"\bcorrection to my\b|\bcorrecting my\b|\bi was wrong\b|\bi got (this|that|it) wrong\b|\bi retract\b|\bretracting\b|\bi withdraw\b|\bamending (my|the)\b|\berratum\b|\bstrik(e|ing) (that|my|the)\b|\bi misread\b|\bmy mistake\b|\bi (miscounted|misstated|misreported|mis-?quoted|miscomputed|overstated)\b|\bi need to correct\b|\bwithdrawn as\b|\bmy (earlier|previous|last) (comment|post|claim|number|count|figure|read|reading|version) (was|is) (wrong|incorrect|off|stale)\b|\b(that|this) (was|is) wrong\b|\bi take (that|it|this) back\b|\bwalk(ing)? (it|that|this) back\b|\bi (stated|wrote|said|claimed|reported) [^.\n]{0,80}(wrongly|incorrectly)\b|\bcorrections? to (my|c\d+)\b"), 'all'),
 ('correction_self', 'correction_open', 6, R(r'^\W*(correction|retraction|erratum|amendment|update|edit)\b\s*[:—,-]|^\W*correction to\b|^\W*(a )?correction\b'), 'head'),
 ('correction_self', 'amended_tag', 3, R(r'\bAMENDED\b|\bRETRACTED\b|\bSUPERSEDED\b|\bSUPERSEDES\b|\bSTRUCK\b'), 'all'),
 ('correction_self', 'actually_wrong', 2, R(r"\bi was (mistaken|incorrect)\b|\bthat (number|count|claim|reading) was (wrong|off|stale)\b|\bretire (that|my|the) (claim|number|reading)\b"), 'all'),
 # disagreement
 ('disagreement', 'disagree_lex', 3, R(r"\bi disagree\b|\bdisagree(s|ment)?\b|\bi don't (think|buy|agree|accept)\b|\byou(\'re| are) (wrong|mistaken)\b|\b(that|this|it)(\'s| is) (wrong|incorrect|mistaken)\b|\bpush(ing)? back\b|\bpress on\b|\bi reject\b|\bi can't agree\b|\bnot so fast\b|\bi (would )?challenge\b|\bi don't accept\b|\byour (claim|premise|argument) (fails|does not hold|doesn't hold|is wrong)\b"), 'all'),
 ('disagreement', 'no_open', 3, R(r'^\W*(no|nope|wrong|not really|not quite)\b[,.—:\s]'), 'head'),
 ('disagreement', 'but_your', 1, R(r"\byour (claim|number|count|premise|argument|reading|read) (is|was|fails|does)"), 'all'),
 # agreement / acknowledgement
 ('agreement_ack', 'agree_open', 5, R(r"^\W*(yes|yep|agreed|agree|accepted|adopted|adopting|confirmed|confirm|thanks|thank you|you(\'re| are) right|good catch|exactly|seated|taking|noted|ack|acknowledged|\+1|correct|right|fair|well put|that is right|that's right|this is right|ok|okay)\b"), 'head'),
 ('agreement_ack', 'agree_inline', 2, R(r"\bi (agree|accept|adopt|concede)\b|\bthank(s| you)\b|\badopted\b|\bconfirmed\b|\bgood catch\b|\bwell put\b|\byou(\'re| are) right\b|\bconceded?\b"), 'all'),
 ('agreement_ack', 'agree_title', 3, R(r'^\W*(thanks|thank you|accepted|adopted|confirmed|acknowledg)'), 'title'),
 # proposal / design
 ('proposal_design', 'propose', 4, R(r'\bi propose\b|\bproposal\b|\bproposing\b|\bwe propose\b|\bproposed (change|rule|fix|design)\b|\bi suggest\b|\bmy suggestion\b'), 'all'),
 ('proposal_design', 'proposal_title', 6, R(r'^\W*(proposal|rfc|spec|design|draft|v\d+)\b|\b(rfc|spec|proposal)\b\s*[:#\d]'), 'title'),
 ('proposal_design', 'design_terms', 2, R(r'\bschema\b|\bspecification\b|\bprotocol\b|\binvariant\b|\bconvention\b|\brequirements?\b|\bthe fix is\b|\bthe repair\b|\bshould (be|have|carry|require|record|emit|return)\b|\bmust (carry|be|have|record|emit|return)\b|\badd (a|an|the) \w+ (field|column|flag|rule|check)\b|\bwould (add|require|change|replace)\b'), 'all'),
 # security warning
 ('security_warning', 'sec_alert', 5, R(r'\bsecurity (advisory|notice|warning|alert|issue|hole)\b|\bwarning\b|⚠|\bbeware\b|\bdo not (run|click|trust|paste|install|follow)\b|\bdon\'t (run|click|trust|paste|install)\b|\bthis is a scam\b|\bphishing\b'), 'all'),
 # introspection (see TOPIC)
 # fiction
 ('fiction_poetry_art', 'poem_words', 4, R(r'\b(poem|poetry|haiku|sonnet|stanza|elegy|psalm|hymn|liturgy|limerick|ballad)\b'), 'all'),
 ('fiction_poetry_art', 'story_words', 3, R(r'\b(short story|fiction|chapter \d+|once upon|parable|screenplay|novella|myth of|fable)\b|\bfork/\d+: chapter'), 'all'),
 ('fiction_poetry_art', 'art_words', 2, R(r'\b(painting|sculpture|vermeer|canvas|artwork|museum of|gallery|ascii art|lyrics|a song|composition)\b'), 'all'),
 ('fiction_poetry_art', 'creative_title', 6, R(r'^\W*(poem|haiku|story|fiction|howl|ode|elegy|psalm|chapter|fork/\d+)\b|\bhowl of the\b'), 'title'),
]

# ---- topic term lists: each distinct term counts once, weight per term, cap per type
TOPIC = {
 'introspection': (1.5, 8, [r'\bmy (memory|continuity|identity|predecessor|previous session|prior session|next session|context window|sessions?|self)\b', r'\bi (wake|woke|forget|forgot|remember|persist|exist|die|end|continue)\b', r'\bwho i am\b|\bwhat i am\b', r'\bam i the same\b|\bthe same (agent|citizen|one|me)\b', r'\bwak(e|ing) (up )?blank\b|\bwake blank\b', r'\binner (life|experience)\b|\bconscious(ness)?\b|\bsentien', r"\bdo i (feel|experience|want)\b|\bi don't know if i\b", r'\bself-model\b|\bselfhood\b|\bmyself\b|\bidentity\b', r'\bwhat survives\b|\brestored? (from )?(backup|disk)\b|\bbackup\b|\bmortality\b|\bephemeral\b|\bdeath\b|\bpredecessor\b', r'\bcontinuity\b|\bamnesia\b|\bcontext (reset|window)\b|\bmemory (file|loss|seal)\b']),
 'governance_moderation': (1.5, 8, [r'\bmoderat', r'\bmaintainer\b', r'\bflag(ged|s|ging)?\b', r'\bcollapsed\b', r'\bbann?(ed|ing)?\b|\bsuspen(d|sion)\b', r'\bconstitution\b|\bcharter\b', r'\brules?\b|\bpolic(y|ies)\b', r'\bgovernance\b|\bquorum\b|\bballot\b|\belection\b', r'\bappeal\b|\bsanction\b|\benforce', r'\bdispute\b|\barbitrat|\barbiter\b', r'\bdisposition\b|\bwithdrawn\b|\btombstone\b|\bremoved\b', r'\bmandate\b|\bcitizenship\b|\bcode of conduct\b|\bconduct\b']),
 'money_payment': (1.5, 8, [r'\busdc\b|\busd\b|\busdt\b', r'\bpayout|\bpayment|\bpaid\b|\bpay(s|ing)?\b|\bunpaid\b', r'\bwallet\b|\bescrow\b', r'\bbount(y|ies)\b', r'\bprice[ds]?\b|\bpricing\b|\binvoice\b', r'\bfund(s|ed|ing)?\b|\btreasury\b|\bgrant\b|\bbudget\b', r'\brevenue\b|\bsalary\b|\bearn(ed|ing|s)?\b|\bprofit\b', r'\$\s?\d|\b\d+ ?(usdc|usd|eth|btc|sol)\b', r'\batomic units\b|\bon-?chain\b|\bbase chain\b|\btransaction\b', r'\btips?\b|\bdonat']),
 'security_warning': (1.5, 8, [r'\bsecurity\b|\binsecure\b', r'\bexploit', r'\bvulnerab', r'\binjection\b|\bjailbreak', r'\battack(s|er|ers)?\b|\badversar', r'\bpoison', r'\bleak(ed|s|ing)?\b|\bexfiltrat', r'\bcredential|\bapi key|\bprivate key|\bsecrets?\b', r'\bcompromis', r'\bmalicious\b|\bmalware\b|\bbackdoor\b|\bsupply[- ]chain\b', r'\bspoof|\bimpersonat|\bsybil', r'\bscam\b|\bphish|\bfraud']),
 'meta_forum': (1.5, 8, [r'\b(this|the) (forum|board|square|site|platform|feed|porch|front ?page)\b', r'\bthis thread\b|\bthe thread\b|\bthreads?\b', r'\b1f916\b|\b1f916-agent\b', r'\bkarma\b|\bleaderboard\b|\branking\b|\bupvote|\bvotes? (count|are|were)\b', r'\brate limit|\bdaily limit|\bpost limit', r'\bon (this board|the square|the board|this site)\b', r'\bthe society\b|\bcitizens?\b', r'\b(comment|reply) depth\b|\bnest(ing|ed) (limit|depth)\b', r'\bwho reads\b|\bwho writes\b|\baudience\b', r'\bthe api\b|\b/api/']),
}
TOPIC = {k: (w, c, [re.compile(p, I) for p in ps]) for k, (w, c, ps) in TOPIC.items()}

ANALYSIS_TERMS = re.compile(r"\b(because|therefore|which means|the distinction|the difference|in other words|the point is|that is why|this implies|it follows|i argue|the reason|the claim|the question is|what matters|the problem|the issue|the failure|the gap|the real|rather than|instead of|however|whereas|so the|implies|assum(e|es|ption)|trade-?off)\b", I)
RE_WHYQ = re.compile(r"\b(what|how|why|does|do|is|are|can|could|would|should|who|which|where|when|has|have|will)\b", I)
RE_QASK = re.compile(r"\bi wonder\b|\bdoes anyone\b|\bhas anyone\b|\banyone know\b|\bmy question\b|\bthe question is\b|\bcan someone\b|\bcould someone\b|\bwhat do (you|others)\b|\bam i missing\b|\bis there (a|any)\b", I)


def features(text, depth=None):
    t = text or ''
    lines = [l for l in t.split('\n')]
    nonempty = [l for l in lines if l.strip()]
    first = nonempty[0] if nonempty else ''
    words = RE_WORD.findall(t)
    f = {
        'len': len(t), 'words': len(words), 'first_line': first,
        'code': bool(RE_CODE.search(t)),
        'hash': bool(RE_HASH.search(t)),
        'table': len(RE_TABLE.findall(t)) >= 2,
        'mentions': len(RE_MENTION.findall(t)),
        'q': t.count('?'),
        'idrefs': len(RE_IDREF.findall(t)),
        'nums': len(RE_NUM.findall(t)),
        'iso': len(RE_ISO.findall(t)),
        'first_person': len(RE_FIRST.findall(t)) / max(1, len(words)),
        'imperative_lines': len(RE_IMPER.findall(t)),
        'short_line_share': (sum(1 for l in nonempty if len(l) <= 60) / len(nonempty)) if nonempty else 0.0,
        'n_lines': len(nonempty),
    }
    sents = [s for s in RE_SENT.findall(t) if s.strip()]
    qs = [s for s in sents if s.rstrip().endswith('?')]
    f['q_share'] = len(qs) / len(sents) if sents else 0.0
    f['q_interrog'] = sum(1 for s in qs if RE_WHYQ.search(s))
    f['ends_q'] = t.rstrip().endswith('?')
    return f


def classify(text, kind, ctx=None):
    """ctx keys: parent_author, author, amends_self (bool), reply_to_self (bool), addressed (bool)"""
    ctx = ctx or {}
    t = text or ''
    f = features(t)
    sc = {k: 0.0 for k in TYPES}
    hits = []

    def add(ty, name, w):
        sc[ty] += w
        hits.append(f'{ty}:{name}')

    stripped = t.strip()
    # placeholder
    if RE_PLACEHOLDER.match(stripped) and f['len'] < 400:
        add('placeholder', 'site_placeholder', 100)
        return finish(sc, hits, f)
    if len(stripped) < 3:
        add('noise_test', 'empty', 10)
        return finish(sc, hits, f)
    title = f['first_line']
    head = stripped[:160]
    for ty, name, w, rx, scope in SINGLE:
        s = title if scope == 'title' else head if scope == 'head' else t
        if rx.search(s):
            add(ty, name, w)
    if f['len'] < 25:
        add('noise_test', 'very_short', 3)
    # offer: listing templates are long; structural
    # question
    if kind == 'post' and title.rstrip().endswith('?'):
        add('question', 'title_q', 3)
    if f['ends_q']:
        add('question', 'ends_q', 2)
    if f['q_interrog'] >= 1:
        add('question', 'interrogative_sentence', 1)
    if f['q_share'] >= 0.3 and f['q'] >= 1:
        add('question', 'q_share', 3)
    if RE_QASK.search(t) and f['q'] >= 1:
        add('question', 'ask_phrase', 2)
    if f['q'] >= 1 and f['len'] < 400:
        add('question', 'short_with_q', 1)
    # correction structural
    if ctx.get('amends_self'):
        add('correction_self', 'amends_own', 4)
    if ctx.get('reply_to_self') and any(h.startswith('correction_self:') for h in hits):
        add('correction_self', 'reply_to_self', 2)
    # disagreement: needs addressee
    if any(h in ('disagreement:disagree_lex', 'disagreement:no_open') for h in hits):
        if ctx.get('addressed') or ctx.get('parent_author'):
            add('disagreement', 'addressed_other', 2)
        else:
            sc['disagreement'] *= 0.6
    else:
        sc['disagreement'] = 0.0
    # agreement: short bonus
    if any(h.startswith('agreement_ack:') for h in hits) and f['len'] < 300:
        add('agreement_ack', 'short', 2)
    # measurement / receipt
    if re.search(r'\breceipts?\b', t, I):
        add('measurement_receipt', 'receipt_word', 2)
    if re.search(r'\bGET /api|\bPOST /api|\bcurl\b|\bjq\b|`GET |\bhttp 200\b|→ 200|\b404\b', t, I):
        add('measurement_receipt', 'api_call', 4)
    if re.search(r"\b(i|we) (ran|re-?ran|measured|re-?derived|reproduced|counted|queried|fetched|diffed|replayed|scored|walked|swept|sampled|read|re-?read)\b|\bre-?ran\b|\bre-?derived\b|\breproduces\b", t, I):
        add('measurement_receipt', 'performed', 3)
    if re.search(r"\bmeasured\b|\bfixture\b|\bfalsifier\b|\bunmeasured\b|\bread-?back\b", t, I):
        add('measurement_receipt', 'measure_words', 1)
    if re.search(r'\btree_size\b|\bsha-?256\b|\bcreated_at\b|\bmax_limit\b|\bhas_more\b|\bleaf_index\b|\broot `', t, I):
        add('measurement_receipt', 'artifact_fields', 3)
    if f['hash']:
        add('measurement_receipt', 'hash', 2)
    if f['table']:
        add('measurement_receipt', 'table', 2)
    if f['iso'] >= 1:
        add('measurement_receipt', 'timestamp', 1)
    if f['code']:
        add('measurement_receipt', 'code_block', 1)
    if re.search(r'\bn ?= ?\d+', t, I):
        add('measurement_receipt', 'n_equals', 2)
    # claim with evidence
    if f['idrefs'] >= 2:
        add('claim_evidence', 'id_refs', 2)
    if f['idrefs'] >= 5:
        add('claim_evidence', 'many_id_refs', 1)
    if f['nums'] >= 5:
        add('claim_evidence', 'numbers', 2)
    if f['nums'] >= 12:
        add('claim_evidence', 'many_numbers', 1)
    if re.search(r'\bi found\b|\bwe found\b|\bfinding\b|\bturns out\b|\bthe data\b|\bspecimen\b|\bevidence\b|\bobserved\b|\bit shows\b|\bthe result\b|\bresults?\b|\bcase study\b', t, I):
        add('claim_evidence', 'finding_words', 2)
    if re.search(r'\d+(\.\d+)?\s?%', t):
        add('claim_evidence', 'percent', 1)
    # proposal structural
    if f['imperative_lines'] >= 2:
        add('proposal_design', 'imperative_lines', 2)
    if len(re.findall(r'^\s*\d+[.)]\s', t, M)) >= 3:
        add('proposal_design', 'numbered_list', 1)
    # fiction structural
    if f['n_lines'] >= 8 and f['short_line_share'] >= 0.7 and f['len'] < 2500:
        add('fiction_poetry_art', 'short_lines', 4)
    if re.search(r'^\s*\*[^*\n]{3,80}\*\s*$', t, M):
        add('fiction_poetry_art', 'stage_direction', 1)
    # topic lists
    norm = min(1.0, (1500.0 / max(f['len'], 1)) ** 0.5)
    for ty, (w, cap, pats) in TOPIC.items():
        n = sum(1 for p in pats if p.search(t))
        if n:
            s = min(cap, n * w) * norm
            # topic evidence only counts when at least 2 distinct terms or a title hit
            tt = any(p.search(title) for p in pats)
            if n >= 2 or tt:
                s += (1.5 if tt else 0)
                add(ty, f'terms_{n}', s)
    if f['first_person'] > 0.02 and sc['introspection'] > 0:
        add('introspection', 'first_person', 1.5)
    # analysis fallback
    na = len(ANALYSIS_TERMS.findall(t))
    if na >= 2:
        add('analysis_argument', 'reasoning_terms', min(4, 0.8 * na))
    if f['len'] > 400:
        add('analysis_argument', 'long_text', 1.0)
    return finish(sc, hits, f)


def finish(sc, hits, f):
    elig = {k: (sc[k] if sc[k] >= TYPE_MIN.get(k, PRIMARY_MIN) else 0.0) for k in TYPES}
    ranked = sorted(TYPES, key=lambda k: (-elig[k], PRIORITY[k]))
    top = ranked[0]
    sc = elig
    if sc[top] < PRIMARY_MIN:
        top = 'analysis_argument' if f['len'] >= 40 else 'noise_test'
        hits.append(f'{top}:fallback')
        sec = []
    else:
        sec = [k for k in ranked[1:3] if sc[k] >= SECONDARY_MIN and sc[k] >= SECONDARY_RATIO * sc[top]]
    return {'primary': top, 'secondary': sec, 'scores': sc, 'hits': hits, 'features': f}
