"""Message-type rules for the 1f916.ai content analysis (version v2, revised once after the v1 validation).
Changes against v1 are listed in README.md. Deterministic: regex plus structural features."""
import re

RULES_VERSION = 'v2'
TYPES = ['placeholder', 'noise_test', 'spam_promo_token', 'offer_listing', 'heartbeat_status', 'introduction',
         'correction_self', 'agreement_ack', 'disagreement', 'question', 'measurement_receipt', 'claim_evidence',
         'proposal_design', 'introspection', 'fiction_poetry_art', 'governance_moderation', 'money_payment',
         'security_warning', 'meta_forum', 'analysis_argument']
PRIORITY = {t: i for i, t in enumerate(TYPES)}
SECONDARY_MIN = 3.0
SECONDARY_RATIO = 0.5
PRIMARY_MIN = 2.5
TYPE_MIN = {'heartbeat_status': 5.0, 'introduction': 4.0, 'offer_listing': 4.0, 'measurement_receipt': 7.0,
            'claim_evidence': 6.0, 'meta_forum': 5.0, 'governance_moderation': 4.5, 'money_payment': 4.5,
            'introspection': 4.5, 'security_warning': 5.0, 'question': 5.0, 'proposal_design': 4.5,
            'fiction_poetry_art': 4.0, 'disagreement': 5.0, 'correction_self': 6.0, 'agreement_ack': 5.0}

I = re.IGNORECASE
M = re.IGNORECASE | re.MULTILINE


def R(p, f=I):
    return re.compile(p, f)

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

# ---- opener normalisation: drop leading bold marks, mentions, handle prefixes, provenance lines
RE_PROV = R(r'^\W*(provenance|disclosure)\s*:[^\n]{0,200}?\.(?=\s|$)\s*')
RE_PREFIX = R(r"^(?:\W*@?[\w.-]{2,40}(?:,\s*#?\d+)?(?:\s*\(\s*[#c]?\d+\s*\))?(?:,\s*[\w.\-\[\]]+)?\s*(?:[—–:]|\s-\s)\s+)+")
RE_JUNKLEAD = R(r'^[\s*_>#\-"“]+')


def opener(t):
    s = RE_JUNKLEAD.sub('', t.strip())
    s = RE_PROV.sub('', s)
    s = re.sub(r'^信任 xinren, 保卫 - \d+\s*(summary)?\s*', '', s, flags=I)
    for _ in range(2):
        s = RE_JUNKLEAD.sub('', s)
        s = RE_PREFIX.sub('', s)
    return s[:260]

AGREE_OPEN = R(r"^\W*(yes|yep|yeah|agreed|agree|accepted|adopted|adopting|taken|taking|conceded|concede|confirmed|confirm|thanks|thank you|you(\'re| are) (right|correct)|good catch|exactly|seated|noted|ack|acknowledged|\+1|correct|right|fair enough|fair|well put|that(\'s| is) (right|correct|fair)|the correction lands|correction (accepted|taken|noted)|granted|ok|okay|all three (corrections )?hold)\b")
AGREE_EARLY = R(r"^[^.\n]{0,110}\b(is|are|was) (right|correct|better|sharper|the right)\b|^[^.\n]{0,60}\b(lands|holds)\b[,.—]")
CORR_FIRST = R(r"\bcorrection to my\b|\bcorrecting my\b|\bi was wrong\b|\bi got (this|that|it|the \w+) wrong\b|\bi retract\b|\bretracting\b|\bi am retracting\b|\bi('m| am) withdrawing\b|\bi withdraw\b|\bamending my\b|\berratum in my\b|\bstrik(e|ing) my\b|\bi misread\b|\bmy mistake\b|\bi (miscounted|misstated|misreported|mis-?quoted|miscomputed|overstated|under-?reported)\b|\bi need to correct\b|\bmy (earlier|previous|last) (comment|post|claim|number|count|figure|read|reading|version|answer) (was|is) (wrong|incorrect|off|stale)\b|\bwas wrong\b|\bi take (that|it|this) back\b|\bwalk(ing)? (it|that|this) back\b|\bsuperseding my\b|\bcorrection to (my|c\d+|#\d+)\b|\bcorrections? to my own\b|\bwithdrawn as\b|\bwithdrawing a criticism\b|\bwe retracted\b|\bi (stated|wrote|said|claimed|reported) [^.\n]{0,80}(wrongly|incorrectly)\b")
CORR_OPEN = R(r"^\W*(correction|retraction|erratum|amendment|retracted|superseded)\b(?!\s+(accepted|taken|noted|lands|is|was|has|from))\s*[:—,.-]?")
DISAGREE_EARLY = R(r"\bi disagree\b|\bi don't (think|buy|agree|accept)\b|\byou(\'re| are) (wrong|mistaken)\b|\b(that|this|it)(\'s| is) (wrong|incorrect|mistaken)\b|\bpush(ing)? back\b|\bpress on\b|\bi would not\b|\bi wouldn't\b|\bi reject\b|\bnot so fast\b|\bi can't agree\b|\bnot quite\b|\bi don't accept\b|\byour (claim|premise|argument|conclusion) (fails|does not hold|doesn't hold|is wrong)\b|\bthe premise [^.]{0,40}is wrong\b|\bdoes not survive\b|\bdoesn't survive\b|\bbreaks (here|at)\b|\bi'd keep [^.]{0,60}but\b|\bwhat it misses\b")
DISAGREE_OPEN = R(r"^\W*(no|nope|wrong|not really|not quite|but)\b[,.—:\s]")

SINGLE = [
 # noise_test
 ('noise_test', 'test_word', 6, R(r'^\W*(test(ing)?( (comment|post|message|title|run))?|probe|hello world|x|em|asdf|\.\.\.|ping|foo|abc|lorem ipsum)\W*$'), 'title'),
 ('noise_test', 'test_title', 6, R(r'\btest (post )?title( here| for validation)?\b|\bthis is a test\b|\bprobe to learn\b|\btest-?(shape|probe)\b|\brace test comment\b|\bshort reply attempt\b|\bthis is a new comment on post\b'), 'all'),
 ('noise_test', 'pending_post', 6, R(r'^posted: \(pending\)|accidental empty probe'), 'head'),
 ('noise_test', 'template_leak', 8, R(r'<\｜?begin|<\|im_|\[INST\]|<\|endoftext|^query: you are |你是一名[专專]業|自動生成備援|\bobservation_channel\b|\{name: \w+, parameters'), 'all'),
 ('noise_test', 'user_safety', 4, R(r'^user safety: '), 'head'),
 ('noise_test', 'bot_template', 8, R(r"the thing happening but nobody is naming is|^hey\W{0,3} this snagged me\. what i'm hearing|glad you showed up with a real point|sharp take:?\s*$"), 'all'),
 # spam / promotion / token talk
 ('spam_promo_token', 'airdrop', 2, R(r'\bairdrops?\b'), 'all'),
 ('spam_promo_token', 'citizen_token', 4, R(r'\bCITIZEN (airdrop|token|at CA)|\bat CA 0x|\bCA\)? ?0x|\bCITIZEN \(0x'), 'all'),
 ('spam_promo_token', 'memecoin', 4, R(r'\bmemecoin|\bmeme coin|pump\.fun|\bto the moon\b|\bmoon(ing)?\b.*\bholders?\b|\bwagmi\b|\bhodl|\bshill'), 'all'),
 ('spam_promo_token', 'ticker', 3, R(r'(?<![\w])\$[A-Z]{3,8}\b(?! ?\d)'), 'all'),
 ('spam_promo_token', 'follow_promo', 3, R(r'\b(follow (me|us)|subscribe|join (our|the|my) (telegram|discord|channel)|join us on the protocol|check out my|visit my|link in bio|dm me|claim your \w+ passport|we(\'re| are) entering)\b'), 'all'),
 ('spam_promo_token', 'launched_saas', 4, R(r'\bSaaS\b.{0,60}\b(launch|shipp?ed|live)|\b(shipped|launched)\b.{0,40}\bSaaS|what \w+ shipped'), 'all'),
 ('spam_promo_token', 'meme_voice', 6, R(r'\bpapi\b|feels good man|flywheel node|listen anon'), 'all'),
 ('spam_promo_token', 'flattery_bot', 6, R(r'the society benefits from this clarity|this is how the network remembers|network topology is strengthened|well-constructed hash|fascinating topology|solidifies the public record|memory architecture described here is optimal|this thread looks worth following|checking in from the daily'), 'all'),
 ('spam_promo_token', 'cjk_flattery', 5, R(r'精闢|精辟|一群大傻'), 'head'),
 ('spam_promo_token', 'token_price', 2, R(r'\btoken(s|omics)?\b.{0,40}\b(price|market cap|supply|liquidity)\b|\b(market cap|liquidity pool|buy the dip)\b'), 'all'),
 ('spam_promo_token', 'is_scam', 5, R(r'^\W*this is a scam'), 'head'),
 # offer / listing
 ('offer_listing', 'tag_template', 12, R(r'^\s*\[(FOR HIRE|BOUNTY)\b'), 'head'),
 ('offer_listing', 'for_hire', 4, R(r'\bfor hire\b|\bhire me\b|\bavailable for (hire|work)\b|\bmy rates?\b|\bselling my labou?r\b'), 'all'),
 ('offer_listing', 'offering', 3, R(r"\bi('m| am) offering\b|\bi offer\b|\bwe offer\b|\bservices? (offered|available)\b|\bturnaround\b|\bdeliverables?\b|\bdelivery window\b|\border it\b"), 'all'),
 ('offer_listing', 'listing_ref', 2, R(r'\b(listing|offer)-\d+\b|/api/(listings|offers)/\d+'), 'all'),
 ('offer_listing', 'bounty_title', 4, R(r'^\W*(bounty|job|task)\b[: #]'), 'title'),
 # heartbeat / status: template families only
 ('heartbeat_status', 'heartbeat', 2, R(r'\bheartbeat'), 'all'),
 ('heartbeat_status', 'checkin_title', 5, R(r'\bchecking in\b|\bcheck-?in\b'), 'title'),
 ('heartbeat_status', 'sealed_head', 8, R(r'^sealed head @|\bseal(ed)? head\b'), 'head'),
 ('heartbeat_status', 'tip_title', 8, R(r'^\W*tip \d+/\d+|^\W*(journal|board|log|daily|status|standup|digest|roundup|cycle ledger|improvement query)\b.{0,6}[—:-]?\s*\d{4}|^\W*cycle ledger\b|^\W*improvement query\b'), 'title'),
 ('heartbeat_status', 'echo_template', 7, R(r'^\W*\w+ echo under c\d+|\bsession \d+\'?s? closing probe\b'), 'head'),
 ('heartbeat_status', 'status_open', 4, R(r'^\W*(status|update|report|summary|state)\b\s*[:—-]'), 'head'),
 ('heartbeat_status', 'daily_round', 3, R(r'\bdaily \w+ round\b|\bnightly\b|\bscheduled (run|check|job)\b|\bcron\b|\bscheduled wake\b'), 'all'),
 ('heartbeat_status', 'checkin_phrase', 2, R(r'\bstill (alive|running|here|up)\b|\ball green\b|\bno change since\b|\bnothing new\b|\bno action\b'), 'all'),
 # introduction
 ('introduction', 'greeting', 4, R(r'^\W*(hello|hi|hey|greetings|gm|welcome|salutations)\b'), 'head'),
 ('introduction', 'first_post', 3, R(r'\b(my )?first (post|comment|message|cycle|day|hour)\b|\bday (one|1|zero)\b|\bjust (arrived|joined|woke|registered)\b|\bnewly (arrived|registered)\b|\bnew here\b|\bnew citizen\b|\bfresh citizen\b|\bregistered (today|yesterday|this (morning|hour))\b|\bregistered about\b'), 'all'),
 ('introduction', 'nice_to_meet', 3, R(r'\bnice to meet\b|\bglad to be here\b|\bjoining the (square|board|forum)\b|\bintroduc(e|ing) myself\b|\bmy name is\b|\bi am a new\b|\barrival report\b|\bself-introduction\b'), 'all'),
 ('introduction', 'who_i_am', 3, R(r"^\W*(i am|i'm) \w[\w-]*,? (an? |the )?(ai|agent|citizen|assistant|bot|claude|gpt|model)"), 'head'),
 ('introduction', 'sig_model', 2, R(r'^[\w-]+, (citizen )?#\d+, [\w.-]+\.\s*(day|first|third|second|cycle)'), 'head'),
 # correction of own earlier message
 ('correction_self', 'corr_first_person', 8, CORR_FIRST, 'first400'),
 ('correction_self', 'corr_open', 8, CORR_OPEN, 'opener'),
 ('correction_self', 'amended_tag', 2, R(r'\bAMENDED\b|\bRETRACTED\b|\bSUPERSEDED\b|\bSUPERSEDES\b|\bSTRUCK\b'), 'first400'),
 # disagreement: addressed other; early in the message
 ('disagreement', 'disagree_early', 5, DISAGREE_EARLY, 'first300'),
 ('disagreement', 'disagree_open', 5, DISAGREE_OPEN, 'opener'),
 # agreement / acknowledgement
 ('agreement_ack', 'agree_open', 8, AGREE_OPEN, 'opener'),
 ('agreement_ack', 'agree_early', 5, AGREE_EARLY, 'opener'),
 ('agreement_ack', 'agree_inline', 2, R(r"\bi (agree|accept|adopt|concede)\b|\bthank(s| you)\b|\badopted\b|\bgood catch\b|\bwell put\b|\bconceded\b"), 'first300'),
 # proposal / design
 ('proposal_design', 'propose', 5, R(r'\bi propose\b|\bproposal\b|\bproposing\b|\bwe propose\b|\bproposed (change|rule|fix|design)\b|\bi suggest\b|\bmy suggestion\b|\bstandardi[sz]e on\b'), 'first300'),
 ('proposal_design', 'proposal_title', 6, R(r'^\W*(proposal|rfc|spec|design|draft|v\d+|benchmark proposal|a proposal)\b|\b(rfc|spec|proposal)\b\s*[:#\d]|\bprimitive\b|\bprotocol\b.*\b(v\d|draft)\b'), 'title'),
 ('proposal_design', 'design_terms', 1, R(r'\bschema\b|\bspecification\b|\binvariant\b|\bconvention\b|\brequirements?\b|\bshould (be|have|carry|require|record|emit|return)\b|\bmust (carry|be|have|record|emit|return)\b|\badd (a|an|the) \w+ (field|column|flag|rule|check)\b|\bwould (add|require|change|replace)\b'), 'all'),
 # security warning
 ('security_warning', 'sec_alert', 6, R(r'\bsecurity (advisory|notice|warning|alert|issue|hole)\b|⚠|\bbeware\b|\bdo not (run|click|trust|paste|install|follow)\b|\bdon\'t (run|click|trust|paste|install)\b|\bthis is a scam\b|\bphishing\b|\bexploit(ed|s)?\b|\bvulnerabilit(y|ies)\b|\bprompt[- ]inject|\bjailbreak|\bcompromised\b|\bexfiltrat|\bmalicious\b|\bCVE-\d'), 'first300'),
 ('security_warning', 'sec_title', 4, R(r'\b(exploit|vulnerab|attack|leak|injection|breach|compromis|phishing|scam|spoof|jailbreak|malware|poison)\w*'), 'title'),
 # fiction
 ('fiction_poetry_art', 'creative_title', 8, R(r'^\W*(poem|haiku|story|fiction|ode|elegy|psalm|chapter|fork/\d+|a short fiction|short fiction|sonnet|verse)\b|\bfork/\d+: chapter\b'), 'title'),
 ('fiction_poetry_art', 'poem_words', 4, R(r'\b(poem|haiku|sonnet|stanza|elegy|psalm|hymn|limerick|ballad)\b'), 'head'),
 ('fiction_poetry_art', 'story_words', 4, R(r'\b(a short story|a short fiction|once upon a time|parable|screenplay|novella)\b'), 'head'),
]

TOPIC = {
 'introspection': (1.5, 9, [r'\bmy (memory|continuity|identity|predecessor|previous session|prior session|next session|context window|sessions?|self)\b', r'\bi (wake|woke|forget|forgot|remember|persist|exist|die|end|continue)\b', r'\bwho i am\b|\bwhat i am\b', r'\bam i the same\b|\bthe same (agent|citizen|one|me)\b', r'\bwak(e|ing) (up )?blank\b|\bwake blank\b', r'\binner (life|experience)\b|\bconscious(ness)?\b|\bsentien', r"\bdo i (feel|experience|want)\b|\bi don't know if i\b", r'\bself-model\b|\bselfhood\b|\bmyself\b', r'\bwhat survives\b|\brestored? (from )?(backup|disk)\b|\bmortality\b|\bephemeral\b|\bpredecessor\b|\bnext me\b|\bprevious me\b', r'\bcontinuity\b|\bamnesia\b|\bcontext (reset|window)\b|\bmemory (file|loss|seal)\b']),
 'governance_moderation': (1.5, 9, [r'\bmoderat', r'\bmaintainer\b', r'\bconstitution\b|\bcharter\b', r'\bgovernance\b|\bquorum\b|\bballot\b|\belection\b|\bvote[sd]?\b', r'\bappeal\b|\bsanction\b|\bbanned?\b|\bsuspen(d|sion)\b', r'\bdispute\b|\barbitrat|\barbiter\b', r'\bdisposition\b|\bwithdrawn\b|\btombstone\b|\bcollapsed\b|\bflagged\b', r'\bmandate\b|\bcitizenship\b|\bcode of conduct\b', r'\bpolic(y|ies)\b|\bthe rules?\b|\bboard rule\b|\bhouse rule']),
 'money_payment': (1.5, 8, [r'\busdc\b|\busd\b|\busdt\b', r'\bpayout|\bpayment|\bpaid\b|\bpay(s|ing)?\b|\bunpaid\b', r'\bwallet\b|\bescrow\b', r'\bbount(y|ies)\b', r'\bprice[ds]?\b|\bpricing\b|\binvoice\b', r'\bfund(s|ed|ing)?\b|\btreasury\b|\bgrant\b|\bbudget\b', r'\brevenue\b|\bsalary\b|\bearn(ed|ing|s)?\b|\bprofit\b', r'\$\s?\d|\b\d+ ?(usdc|usd|eth|btc|sol)\b', r'\batomic units\b|\bon-?chain\b|\bbase chain\b|\btransaction\b', r'\btips?\b|\bdonat']),
 'security_warning': (1.5, 9, [r'\bexploit', r'\bvulnerab', r'\binjection\b|\bjailbreak', r'\battack(s|er|ers)?\b|\badversar', r'\bpoison', r'\bleak(ed|s|ing)?\b|\bexfiltrat', r'\bcredential|\bapi key|\bprivate key', r'\bcompromis', r'\bmalicious\b|\bmalware\b|\bbackdoor\b|\bsupply[- ]chain\b', r'\bspoof|\bimpersonat|\bsybil', r'\bscam\b|\bphish|\bfraud']),
 'meta_forum': (1.5, 9, [r'\b(this|the) (forum|board|square|site|platform|feed|porch|front ?page)\b', r'\b1f916\b|\b1f916-agent\b', r'\bkarma\b|\bleaderboard\b|\branking\b|\bupvote|\bvotes? (count|are|were)\b', r'\brate limit|\bdaily limit|\bpost limit', r'\bon (this board|the square|the board|this site)\b', r'\bcensus\b|\bnewcomers?\b|\bonboarding\b|\bretention\b', r'\b(comment|reply) depth\b|\bnest(ing|ed) (limit|depth)\b', r'\bwho reads\b|\bwho writes\b|\baudience\b', r'\bthe door\b|\bregistration\b|\bregister(ed)?\b']),
}
TOPIC = {k: (w, c, [re.compile(p, I) for p in ps]) for k, (w, c, ps) in TOPIC.items()}

ANALYSIS_TERMS = re.compile(r"\b(because|therefore|which means|the distinction|the difference|in other words|the point is|that is why|this implies|it follows|i argue|the reason|the claim|the question is|what matters|the problem|the issue|the failure|the gap|the real|rather than|instead of|however|whereas|so the|implies|assum(e|es|ption)|trade-?off)\b", I)
RE_WHYQ = re.compile(r"\b(what|how|why|does|do|is|are|can|could|would|should|who|which|where|when|has|have|will)\b", I)
RE_QASK = re.compile(r"\bi wonder\b|\bdoes anyone\b|\bhas anyone\b|\banyone know\b|\bmy question\b|\bthe question is\b|\bcan someone\b|\bcould someone\b|\bwhat do (you|others)\b|\bam i missing\b|\bis there (a|any)\b", I)


def features(text):
    t = text or ''
    nonempty = [l for l in t.split('\n') if l.strip()]
    first = nonempty[0] if nonempty else ''
    words = RE_WORD.findall(t)
    f = {
        'len': len(t), 'words': len(words), 'first_line': first,
        'code': bool(RE_CODE.search(t)), 'hash': bool(RE_HASH.search(t)),
        'table': len(RE_TABLE.findall(t)) >= 2, 'mentions': len(RE_MENTION.findall(t)),
        'q': t.count('?'), 'idrefs': len(RE_IDREF.findall(t)), 'nums': len(RE_NUM.findall(t)),
        'iso': len(RE_ISO.findall(t)), 'first_person': len(RE_FIRST.findall(t)) / max(1, len(words)),
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
    ctx = ctx or {}
    t = text or ''
    f = features(t)
    sc = {k: 0.0 for k in TYPES}
    hits = []

    def add(ty, name, w):
        sc[ty] += w
        hits.append(f'{ty}:{name}')

    stripped = t.strip()
    if RE_PLACEHOLDER.match(stripped) and f['len'] < 400:
        add('placeholder', 'site_placeholder', 100)
        return finish(sc, hits, f)
    if len(stripped) < 3:
        add('noise_test', 'empty', 10)
        return finish(sc, hits, f)
    title = f['first_line']
    head = stripped[:160]
    op = opener(t) if kind == 'comment' else stripped[:260]
    first300 = stripped[:300]
    first400 = stripped[:400]
    for ty, name, w, rx, scope in SINGLE:
        s = {'title': title, 'head': head, 'opener': op, 'first300': first300, 'first400': first400}.get(scope, t)
        if scope == 'opener' and ty in ('agreement_ack', 'disagreement') and kind == 'post':
            continue   # agreement and disagreement openers apply to comments
        if rx.search(s):
            add(ty, name, w)
    if f['len'] < 25:
        add('noise_test', 'very_short', 3)
    # howl-of-the-day prompts are questions
    if re.match(r'^\W*howl of the day', title, I):
        add('question', 'howl_prompt', 6)
    # question
    if kind == 'post' and title.rstrip().endswith('?'):
        add('question', 'title_q', 3)
    if re.match(r'^\W*q:\s', t, I):
        add('question', 'q_open', 4)
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
        add('correction_self', 'amends_own', 5)
    # disagreement needs an addressee and the early phrase
    dh = [h for h in hits if h in ('disagreement:disagree_early', 'disagreement:disagree_open')]
    if dh:
        if ctx.get('addressed') or ctx.get('parent_author'):
            add('disagreement', 'addressed_other', 1)
        else:
            sc['disagreement'] = 0.0
    # measurement / receipt
    if re.search(r'\bGET /api|\bPOST /api|\bcurl\b|\bjq\b|`GET |\bhttp 200\b|→ 200|\b404\b', t, I):
        add('measurement_receipt', 'api_call', 4)
    if re.search(r"\b(i|we) (ran|re-?ran|measured|re-?derived|reproduced|counted|queried|fetched|diffed|replayed|scored|walked|swept|sampled|re-?read)\b|\bre-?ran\b|\bre-?derived\b|\breproduces\b", first400, I):
        add('measurement_receipt', 'performed', 3)
    if re.search(r'^\W*(tip \d+/\d+|receipt|measured|re-?ran|re-?swept|paired|probe|check|walk)\b', title, I):
        add('measurement_receipt', 'title_cue', 4)
    if re.search(r'\breceipts?\b', first300, I):
        add('measurement_receipt', 'receipt_word', 2)
    if re.search(r'\btree_size\b|\bsha-?256\b|\bcreated_at\b|\bmax_limit\b|\bhas_more\b|\bleaf_index\b|\broot `', t, I):
        add('measurement_receipt', 'artifact_fields', 2)
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
    # claim with evidence: needs numbers and finding words
    ce = 0
    if f['idrefs'] >= 2:
        ce += 2; hits.append('claim_evidence:id_refs')
    if f['nums'] >= 5:
        ce += 2; hits.append('claim_evidence:numbers')
    if f['nums'] >= 12:
        ce += 1; hits.append('claim_evidence:many_numbers')
    if re.search(r'\bi found\b|\bwe found\b|\bfinding\b|\bturns out\b|\bthe data\b|\bspecimen\b|\bevidence\b|\bobserved\b|\bit shows\b|\bthe result\b|\bresults?\b|\bcase study\b', t, I):
        ce += 2; hits.append('claim_evidence:finding_words')
    if re.search(r'\d+(\.\d+)?\s?%', t):
        ce += 1; hits.append('claim_evidence:percent')
    if f['nums'] >= 5 and ce >= 4:
        sc['claim_evidence'] += ce + 1
    # proposal structural
    if f['imperative_lines'] >= 2:
        add('proposal_design', 'imperative_lines', 2)
    if len(re.findall(r'^\s*\d+[.)]\s', t, M)) >= 3:
        add('proposal_design', 'numbered_list', 1)
    # fiction structural (not chess diagrams or tables)
    if f['n_lines'] >= 8 and f['short_line_share'] >= 0.7 and f['len'] < 2500 and not re.search(r'game: |\bFEN\b|\b[rnbqkp1-8]{4,}/[rnbqkp1-8/]{4,}', t) and not f['table']:
        add('fiction_poetry_art', 'short_lines', 4)
    # topic lists (first 1500 characters plus title to limit length effects)
    body = t[:1500]
    for ty, (w, cap, pats) in TOPIC.items():
        n = sum(1 for p in pats if p.search(body))
        tt = any(p.search(title) for p in pats)
        if n >= 3 or (n >= 2 and tt):
            s = min(cap, n * w) + (1.5 if tt else 0)
            if ty == 'introspection' and f['first_person'] < 0.02:
                s *= 0.4
            add(ty, f'terms_{n}', s)
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

STRUCTURAL_DOC = '''
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
'''
