"""Example tables for every type and theme, plus the 100 most unusual messages.
Writes type_examples.csv, theme_examples.csv, unusual_100.csv. Reads .X.pkl written by analyze_types.py."""
import re, sys, collections, math
import numpy as np, pandas as pd
sys.path.insert(0, '.')
from load import load_messages, HERE
import themes as TH

X = pd.read_pickle(f'{HERE}/.X.pkl')
M = load_messages()
X = X.merge(M[['id', 'kind', 'text']], on=['id', 'kind'])
TT = pd.read_csv(f'{HERE}/themes_all.csv.gz')
X = X.merge(TT, on=['id', 'kind'])
X['text'] = X.text.fillna('')
URL = {'post': 'https://1f916.ai/api/post/', 'comment': 'https://1f916.ai/api/comment/'}
BLOCK = [re.compile((r'\b' + re.escape(b) + r'\b') if b.isascii() else re.escape(b), re.I) for b in open(f'{HERE}/privacy_blocklist.txt').read().split()] if __import__('os').path.exists(f'{HERE}/privacy_blocklist.txt') else []

# ---------- privacy filter on excerpts
RE_EMAIL = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
RE_PHONE = re.compile(r'\+?\d[\d\s().-]{8,}\d')
RE_WALLET = re.compile(r'\b0x[0-9a-fA-F]{6,}|\b[0-9a-fA-F]{40}\b|\b[1-9A-HJ-NP-Za-km-z]{32,44}\b')
RE_HUMANREF = re.compile(r"\b(my|the|our|her|his|their)\s+(human|operator|keeper|owner|principal|boss|creator|steward|user|client|partner|husband|wife|friend)\b[^.]{0,25}?\b([A-Z][a-z]{2,})\b")
RE_NAMED = re.compile(r"\b(named|called|name is|I am|I'm|this is|by)\s+([A-Z][a-z]{2,})\b")
RE_TWOCAP = re.compile(r"(?<![.!?\n])\s([A-Z][a-z]{2,}\s[A-Z][a-z]{2,})\b")
OKCAP = {'Base USDC', 'Claude Code', 'Claude Opus', 'Claude Sonnet', 'Claude Fable', 'Claude Haiku', 'Open Source', 'Sonnet', 'The Square', 'Hugging Face', 'Cloudflare Worker', 'Github Actions', 'GitHub Actions'}


def safe(ex):
    if RE_EMAIL.search(ex) or RE_PHONE.search(ex) or RE_WALLET.search(ex): return False
    if RE_HUMANREF.search(ex): return False
    if re.search(r'github\.com/(?!1f916-ai)|gitlab\.com/|twitter\.com/|x\.com/|linkedin\.com/|t\.me/', ex, re.I): return False
    if RE_NAMED.search(ex): return False
    for m in RE_TWOCAP.finditer(ex):
        if m.group(1) not in OKCAP: return False
    if any(b.search(ex) for b in BLOCK): return False
    return True


def excerpt(text, kind):
    t = text.replace('\r', '')
    t = re.sub(r'[*_`>]+', '', t)
    t = re.sub(r'(?m)^#{1,6}\s+', '', t)
    parts = [p.strip() for p in t.split('\n') if p.strip()]
    sents = []
    for p in parts:
        ss = re.split(r'(?<=[.!?])\s+', p)
        sents += [s.strip() for s in ss if s.strip()]
        if len(sents) >= 4: break
    out = []; n = 0
    for s in sents:
        w = len(s.split())
        if n + w > 25: break
        out.append(s); n += w
    if not out: return None
    ex = ' '.join(out)
    ex = ex.replace(' — ', '; ').replace('—', ';').replace(' – ', '; ').replace('–', ' to ')
    if len(ex.split()) < 3: return None
    if not re.search(r'[.!?\]\)"”]$', ex) and len(out) == len(sents) and n < 25:
        pass
    return ex

# ---------- vocabulary rarity (document frequency of tokens)
tok = re.compile(r"[a-z][a-z'-]{2,}")
dfc = collections.Counter()
toks = []
for t in X.text:
    s = set(tok.findall(t.lower()))
    toks.append(s)
    dfc.update(s)
X['rare_share'] = [ (sum(1 for w in s if dfc[w] <= 3) / len(s)) if s else 0 for s in toks ]
X['nonascii'] = X.text.str.count(r'[^\x00-\x7f]') / (X.text.str.len() + 1)
sec = X.secondary.fillna('')
X['combo'] = X.primary + '+' + sec.str.replace(';', '+')
cf = X.combo.value_counts()
X['combo_rarity'] = -np.log2(X.combo.map(cf) / len(X))
X['loglen'] = np.log1p(X.length)
g = X.groupby('primary').loglen.agg(['mean', 'std'])
X['len_z'] = (X.loglen - X.primary.map(g['mean'])) / X.primary.map(g['std']).replace(0, 1)
z = lambda s: (s - s.mean()) / s.std()
X['distinct'] = z(X.combo_rarity) + z(X.len_z.abs()) + z(X.rare_share) + 0.5 * z(X.nonascii)
X['week'] = X.week.astype(int)

CLAUSE = {
 'site_placeholder': 'is the site placeholder shown in place of the text',
 'empty': 'has no text',
 'test_word': 'is a bare test or probe word', 'test_title': 'carries a test or probe title', 'pending_post': 'is a pending or empty probe',
 'template_leak': 'contains a prompt or template fragment', 'user_safety': 'is a safety-label stub', 'bot_template': 'repeats a fixed template sentence',
 'very_short': 'is under 25 characters', 'fallback': 'reaches no stronger type and is prose argument',
 'airdrop': 'mentions an airdrop', 'citizen_token': 'discusses the CITIZEN token or its address', 'memecoin': 'uses memecoin or hype vocabulary', 'ticker': 'names a token ticker',
 'follow_promo': 'asks readers to follow, join or visit', 'launched_saas': 'announces a launched product', 'meme_voice': 'uses the frog-meme voice', 'flattery_bot': 'is generic praise',
 'cjk_flattery': 'is generic praise in Chinese', 'token_price': 'talks about token price or supply', 'is_scam': 'calls something a scam',
 'tag_template': 'starts with a FOR HIRE or BOUNTY tag', 'for_hire': 'offers work for hire', 'offering': 'describes a service or deliverable', 'listing_ref': 'refers to a listing or offer record', 'bounty_title': 'is titled as a bounty or job',
 'heartbeat': 'mentions a heartbeat', 'checkin_title': 'is titled as a check-in', 'sealed_head': 'is a sealed-head status line', 'tip_title': 'is a dated status or tip report', 'echo_template': 'is a numbered echo status line',
 'status_open': 'opens with a status label', 'daily_round': 'refers to a scheduled run', 'checkin_phrase': 'says nothing changed',
 'greeting': 'opens with a greeting', 'first_post': 'says it is a first post or newly arrived', 'nice_to_meet': 'introduces itself', 'who_i_am': 'opens by saying who the writer is', 'sig_model': 'opens with handle, number and model',
 'corr_first_person': 'corrects the writer\'s own earlier statement', 'corr_open': 'opens with a correction label', 'amended_tag': 'carries an AMENDED or RETRACTED tag', 'amends_own': 'amends the same handle\'s earlier comment',
 'disagree_early': 'states disagreement or pushes back early', 'disagree_open': 'opens with a no or but', 'addressed_other': 'is addressed to another handle',
 'agree_open': 'opens with acceptance or confirmation', 'agree_early': 'says the other message is right in its first line', 'agree_inline': 'contains thanks or agreement words',
 'propose': 'proposes a change', 'proposal_title': 'is titled as a proposal or spec', 'design_terms': 'uses design vocabulary such as schema or invariant', 'imperative_lines': 'lists imperative requirements', 'numbered_list': 'uses a numbered list',
 'sec_alert': 'names a vulnerability, exploit or warning', 'sec_title': 'has a security word in the title',
 'creative_title': 'is titled as fiction, poem or chapter', 'poem_words': 'names a poem form', 'story_words': 'names a story form', 'short_lines': 'is laid out in short lines',
 'howl_prompt': 'is a daily prompt question', 'title_q': 'has a question as its title', 'q_open': 'opens with Q:', 'ends_q': 'ends with a question mark', 'interrogative_sentence': 'asks an interrogative sentence', 'q_share': 'is mostly questions', 'ask_phrase': 'uses an ask phrase', 'short_with_q': 'is short and contains a question',
 'api_call': 'quotes an API call', 'performed': 'reports an action the writer ran', 'title_cue': 'is titled as a receipt or measurement', 'receipt_word': 'uses the word receipt', 'artifact_fields': 'quotes record fields', 'hash': 'quotes a long hash', 'table': 'contains a table', 'timestamp': 'quotes a timestamp', 'code_block': 'contains a code block', 'n_equals': 'states a sample size',
 'id_refs': 'cites several post or comment ids', 'numbers': 'contains many numbers', 'many_numbers': 'contains a dozen or more numbers', 'finding_words': 'uses finding or evidence words', 'percent': 'quotes a percentage',
 'reasoning_terms': 'argues with reasoning terms', 'long_text': 'is long prose',
}
TOPICCL = {'introspection': 'talks about its own memory or continuity', 'governance_moderation': 'discusses moderation, rules or voting', 'money_payment': 'discusses payment or money',
           'security_warning': 'discusses attacks or vulnerabilities', 'meta_forum': 'discusses the forum itself'}


def why_type(hitstr, ptype):
    hs = [h.split(':', 1)[1] for h in str(hitstr).split(';') if h.startswith(ptype + ':')]
    cl = []
    for h in hs:
        if h.startswith('terms_'):
            cl.append(TOPICCL.get(ptype, 'uses several terms from the word list'))
        elif h in CLAUSE: cl.append(CLAUSE[h])
    cl = list(dict.fromkeys(cl))
    if not cl:
        return 'reaches no stronger type; plain prose' if ptype == 'analysis_argument' else 'meets the score threshold for this type'
    return ' and '.join(cl[:2])


def pick(G, n=10, seed=1, key='primary', used0=None):
    rng = np.random.RandomState(seed)
    G = G.copy()
    G['ex'] = [excerpt(t, k) for t, k in zip(G.text, G.kind)]
    G = G[G.ex.notna()]
    G = G[[safe(e) for e in G.ex]]
    if G.empty: return []
    q75 = G.votes.quantile(.9)
    med = G.length.median(); lo, hi = G.length.quantile(.25), G.length.quantile(.75)
    chosen = []; used = set(used0 or [])

    def take(S, role, k):
        S = S[~S.handle.isin(used)]
        for _, r in S.iterrows():
            if len([c for c in chosen if c[1] == role]) >= k: break
            if r.handle in used: continue
            chosen.append((r, role)); used.add(r.handle)
    # distinctive 2
    S = G.sort_values('distinct', ascending=False).head(60).sample(frac=1, random_state=rng)
    take(S.head(40), 'distinctive', 2)
    # low-signal typical 2: votes<=1, length inside IQR, one post if available
    L = G[(G.votes <= 1) & (G.length >= lo) & (G.length <= hi)].sample(frac=1, random_state=rng)
    take(L, 'low_signal_typical', 2)
    # spread over weeks, avoiding top vote decile, mix posts and comments
    rest = G[(G.votes < q75) | (G.votes <= 1)]
    nposts = (G.kind == 'post').sum()
    weeks = sorted(rest.week.unique()); rng.shuffle(weeks)
    wantpost = 3 if nposts >= 3 and (G.kind == 'comment').sum() >= 3 else 0
    for wk in weeks * 3:
        if len(chosen) >= n: break
        S = rest[rest.week == wk].sample(frac=1, random_state=rng)
        np_ = sum(1 for c in chosen if c[0].kind == 'post')
        if np_ < wantpost: S = S.sort_values('kind', key=lambda s: (s != 'post'), kind='stable')
        elif wantpost: S = S.sort_values('kind', key=lambda s: (s != 'comment'), kind='stable')
        for _, r in S.iterrows():
            if r.handle in used: continue
            chosen.append((r, 'spread_sample')); used.add(r.handle); break
    if len(chosen) < n:  # relax handle uniqueness
        for _, r in G.sample(frac=1, random_state=rng).iterrows():
            if len(chosen) >= n: break
            if any(c[0].id == r.id and c[0].kind == r.kind for c in chosen): continue
            chosen.append((r, 'spread_sample'))
    return chosen[:n]


def tiered(G, tiers, n=10, seed=1):
    """tiers: list of boolean masks over G in priority order; fill from the first tier, top up from later ones."""
    out = []; used = set(); seen = set()
    for m in tiers:
        S = G[m]
        S = S[[ (k, i) not in seen for k, i in zip(S.kind, S.id)]]
        if S.empty: continue
        need = n - len(out)
        if need <= 0: break
        part = pick(S, n=need, seed=seed, used0=used)
        for r, role in part:
            if out and role in ('distinctive', 'low_signal_typical'):
                have = sum(1 for o in out if o[1] == role)
                limit = 2
                if have >= limit: role = 'spread_sample'
            out.append((r, role)); used.add(r.handle); seen.add((r.kind, r.id))
    return out


# ---------- validation status
v1 = pd.read_csv(f'{HERE}/validation_v1.csv'); v2 = pd.read_csv(f'{HERE}/validation_v2.csv')
vt = pd.concat([v2, v1[v1.primary.isin(['placeholder', 'offer_listing', 'money_payment'])]])
vkey = {(k, int(i)): v for k, i, v in zip(vt.kind, vt.id, vt.verdict)}
X['read_verdict'] = [vkey.get((k, int(i)), 'not read') for k, i in zip(X.kind, X.id)]
tv = pd.read_csv(f'{HERE}/theme_validation.csv')
tkey = {(th, k, int(i)): v for th, k, i, v in zip(tv.theme, tv.kind, tv.id, tv.verdict)}

# ---------- type examples
rows = []
for i, t in enumerate(X.primary.value_counts().index):
    G = X[X.primary == t]
    tiers = [(G.read_verdict == 'y'), (G.read_verdict == 'not read')]
    ch = tiered(G, tiers, seed=100 + i)
    for r, role in ch:
        rows.append({'type': t, 'id': int(r.id), 'kind': r.kind, 'handle': r.handle, 'date_utc': r.date, 'excerpt': r.ex,
                     'url': URL[r.kind] + str(int(r.id)), 'what_makes_it_this_type': why_type(r.rule_hits, t),
                     'read_check': 'read and judged correct' if r.read_verdict == 'y' else 'not in the read sample',
                     'selection_role': role, 'votes': int(r.votes), 'length_chars': int(r.length)})
pd.DataFrame(rows).to_csv(f'{HERE}/type_examples.csv', index=False)

# ---------- theme examples
COMP = {k: ([re.compile(p, re.I) for p in s_], [re.compile(p, re.I) for p in w_]) for k, (s_, w_) in TH.THEMES.items()}
rows = []
for i, th in enumerate(TH.THEMES):
    G = X[X[th] == 1].copy()
    G['tv'] = [tkey.get((th, k, int(i_)), 'not read') for k, i_ in zip(G.kind, G.id)]
    G = G[G.tv != 'n']
    tiers = [(G.tv == 'y'), (G.tv == 'p'), (G.tv == 'not read')]
    ch = tiered(G, tiers, seed=500 + i)
    s_, w_ = COMP[th]
    for r, role in ch:
        terms = []
        for p in s_ + w_:
            m = p.search(r.text)
            if m: terms.append(m.group(0).lower().strip())
        terms = list(dict.fromkeys(terms))[:3]
        why = 'contains ' + ', '.join(f'"{x}"' for x in terms)
        if th == 'labs_model_families': why += ' (a statement or label in the message, not verified)'
        rows.append({'theme': th, 'id': int(r.id), 'kind': r.kind, 'handle': r.handle, 'date_utc': r.date, 'excerpt': r.ex,
                     'url': URL[r.kind] + str(int(r.id)), 'what_makes_it_this_theme': why, 'primary_type': r.primary,
                     'read_check': {'y': 'read: on theme', 'p': 'read: passing or other sense', 'not read': 'not in the read sample'}[r.tv],
                     'selection_role': role, 'votes': int(r.votes), 'length_chars': int(r.length)})
pd.DataFrame(rows).to_csv(f'{HERE}/theme_examples.csv', index=False)

# ---------- 100 most unusual (English-dominant messages; non-English text is reported separately in the report)
U = X[(X.primary != 'placeholder') & (X.length >= 30) & (X.nonascii < 0.1)].copy()
U['h'] = U.text.str.lower().str.replace(r'\s+', ' ', regex=True).str[:300]
U = U.drop_duplicates('h')
U['combo_n'] = U.combo.map(cf)
rng = np.random.RandomState(11)
picked = []; seen = set()
def add(S, crit, k, maxper=None, keycol=None):
    cnt = collections.Counter()
    for _, r in S.iterrows():
        if len([p for p in picked if p[1] == crit]) >= k: break
        key = (r.kind, r.id)
        if key in seen: continue
        if maxper and cnt[r[keycol]] >= maxper: continue
        cnt[r[keycol] if keycol else 0] += 1
        picked.append((r, crit)); seen.add(key)
A = U[U.combo_n <= 10].sample(frac=1, random_state=rng).sort_values('combo_rarity', ascending=False, kind='stable')
add(A, 'rare type combination', 40, maxper=3, keycol='combo')
B = U.assign(az=U.len_z.abs()).sort_values('az', ascending=False)
add(B, 'outlier length', 30)
C = U[U.length >= 80].sort_values('rare_share', ascending=False)
add(C, 'rare vocabulary', 30)
add(A, 'rare type combination', 100)
def reason(r, crit):
    if crit == 'rare type combination': return f'type combination {r.combo} occurs {int(cf[r.combo])} times in 102,147 messages'
    if crit == 'outlier length': return f'{int(r.length)} characters, {abs(r.len_z):.1f} sd {"above" if r.len_z>0 else "below"} the mean log length for type {r.primary}'
    return f'{100*r.rare_share:.0f}% of its distinct words occur in 3 or fewer messages'
rows = []
for r, crit in picked[:100]:
    ex = excerpt(r.text, r.kind)
    rows.append({'id': int(r.id), 'kind': r.kind, 'handle': r.handle, 'date_utc': r.date, 'primary_type': r.primary, 'secondary_types': r.secondary if isinstance(r.secondary, str) else '',
                 'length_chars': int(r.length), 'criterion': crit, 'why_unusual': reason(r, crit),
                 'excerpt': ex if (ex and safe(ex)) else '[no excerpt: first sentence over 25 words or privacy filter]', 'url': URL[r.kind] + str(int(r.id))})
pd.DataFrame(rows).to_csv(f'{HERE}/unusual_100.csv', index=False)
print('done', len(rows))
