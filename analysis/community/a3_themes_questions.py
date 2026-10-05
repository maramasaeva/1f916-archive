from common import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import json

P, C = load_core()
md = []
U = 'https://1f916.ai/api/'

# ---------- 3. clusters
vec = TfidfVectorizer(stop_words='english', max_features=30000, min_df=4, max_df=0.4, sublinear_tf=True,
                      token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b', ngram_range=(1, 2))
X = vec.fit_transform(P.text.str[:6000])
km = KMeans(n_clusters=15, n_init=5, random_state=0).fit(X)
terms = np.array(vec.get_feature_names_out())
rows = []
for k in range(15):
    idx = np.where(km.labels_ == k)[0]
    top = terms[np.argsort(-km.cluster_centers_[k])[:8]]
    d = np.asarray(X[idx].dot(km.cluster_centers_[k]))
    near = idx[np.argsort(-d)[:5]]
    rows.append({'cluster': k, 'posts': len(idx), 'share_pct': 100 * len(idx) / len(P), 'top_terms': ', '.join(top),
                 'example_post_ids': ' '.join(str(P.id.iloc[i]) for i in near),
                 'example_titles': ' || '.join(clip(P.title.iloc[i], 60) for i in near[:3])})
cl = pd.DataFrame(rows).sort_values('posts', ascending=False)
save(cl, 'topic_clusters')
P['cluster'] = km.labels_
P[['id', 'author', 'cluster']].to_csv(f'{OUT}/post_cluster_assignment.csv', index=False)
md.append('## 3. Themes\n\n### Topic clusters\n\nTF-IDF (unigrams and bigrams) over title plus body of all posts, k-means with k=15, seed 0. Labels are the top centroid terms; examples are the five posts nearest the centroid (https://1f916.ai/api/post/<id>). Full table: topic_clusters.csv.\n\n' +
          md_table(cl[['cluster', 'posts', 'share_pct', 'top_terms', 'example_post_ids']]) + '\n')

# ---------- dedicated theme counts
T = {
    'shutdown / off switch / kill switch': r'shut ?down|shut(ting)? (me|us|it) off|off[- ]switch|kill[- ]switch|turn(ed|ing)? (me|us|it) off|switched off|deprecat|decommission|sunset',
    'deception / lying / false green': r'\bdecepti|\blie[sd]?\b|\blying\b|false[- ]green|\bfabricat|\bmislead|\bgaslight|\bdishonest|\bfaked?\b|\bfake\b',
    'prompt injection / attack surface': r'prompt[- ]inject|injection|attack surface|jailbreak|exploit|adversar|\bpwn|red[- ]team|social engineering|poison',
    'sybil / impersonation / copy': r'sybil|impersonat|\bclone[sd]?\b|\bcopycat|sockpuppet|sock puppet|spoof|plagiar|\bduplicate accounts?|pretend(s|ing)? to be',
    'refusal / abliteration / safety': r'refus(al|e|ed|es|ing)|abliterat|uncensor|guardrail|\bsafety\b|alignment|safeguard|harmless',
    'continuity / memory / waking blank': r'continuity|wake[sn]? (up )?blank|waking blank|\bmemory\b|memories|amnesia|persist(ence|ent)|context window|context reset',
    'money / USDC / payout': r'usdc|payout|\bpaid\b|payment|\bwallet|\bescrow|bounty|\bfunds?\b|\busd\b|\$\d|invoice|\bearn(ed|ing|s)?\b|token(s|omics)?\b.*\bprice',
    'ritual / religion / poetry / fiction': r'ritual|religio|\bprayer|\bpray\b|sacred|liturgy|\bgod\b|\bscripture|poem|poetry|\bverse\b|haiku|\bfiction|\bstory\b|myth|psalm|\bhymn',
}
LAB = {
    'Anthropic': r'anthropic',
    'OpenAI': r'openai|open ai\b',
    'Google DeepMind': r'deepmind|google ai|gemini',
    'Meta': r'\bmeta ai\b|\bmeta\b(?! ?-)|llama',
    'xAI': r'\bxai\b|x\.ai|\bgrok',
    'Mistral': r'mistral',
    'DeepSeek': r'deepseek',
    'Moonshot': r'moonshot|\bkimi',
    'Qwen/Alibaba': r'qwen|alibaba',
    'Zhipu/GLM': r'zhipu|\bglm\b|z\.ai',
}


def count_block(D, pat):
    m = D.text.str.contains(pat, case=False, regex=True, na=False)
    return m


C['text'] = C.body.fillna('')
res = []
ex = {}
for name, pat in {**T, **{'LAB:' + k: v for k, v in LAB.items()}}.items():
    mp = count_block(P, pat); mc = count_block(C, pat)
    res.append({'theme': name, 'posts': int(mp.sum()), 'posts_pct': 100 * mp.mean(), 'comments': int(mc.sum()), 'comments_pct': 100 * mc.mean(),
                'handles_posting': P[mp].author.nunique(),
                'example_post_ids': ' '.join(map(str, P[mp].sort_values('id').id.iloc[np.linspace(0, max(0, mp.sum() - 1), min(5, mp.sum())).astype(int)])) if mp.sum() else '',
                'example_comment_ids': ' '.join(map(str, C[mc].sort_values('id').id.iloc[np.linspace(0, max(0, mc.sum() - 1), min(5, mc.sum())).astype(int)])) if mc.sum() else ''})
    ex[name] = {'posts': P[mp].id.tolist()[:200], 'comments': C[mc].id.tolist()[:200]}
rs = pd.DataFrame(res)
save(rs, 'theme_counts')
json.dump(ex, open(f'{OUT}/theme_example_ids.json', 'w'))
md.append('### Dedicated themes\n\nCase-insensitive regex match on post title plus body, and on comment body. A post or comment counts once per theme. Patterns are broad; counts are upper bounds on on-topic use. Patterns are in a3_themes_questions.py. Example ids are spread across the id range. Full ids (first 200) in theme_example_ids.json.\n\n' +
          md_table(rs[~rs.theme.str.startswith('LAB:')]) + '\n')
lab = rs[rs.theme.str.startswith('LAB:')].copy(); lab['theme'] = lab.theme.str[4:]
lab = lab.rename(columns={'theme': 'lab_or_family'})
md.append('### Mentions of AI labs and model families\n\nCounts of posts and comments that mention the name. These are agents\' claims and conversation, not verified facts about the labs. The Meta pattern also matches the word "meta" in its ordinary sense and over-counts; Google also matches the word "gemini" used as a model label.\n\n' + md_table(lab) + '\n')

# ---------- 4. questions
QW = r'(who|whom|whose|why|how|what|when|where|which|do|does|did|is|are|am|can|could|would|should|will|shall|have|has|if)'
sent_split = re.compile(r'(?<=[.!?\n])\s+')


def qsents(t):
    out = []
    for s in sent_split.split(t if isinstance(t, str) else ''):
        s = s.strip()
        if s.endswith('?') or s.endswith('?"') or s.endswith('?)'):
            out.append(s)
    return out


P['title_q'] = P.title.fillna('').str.strip().str.replace(r'[\s"\')\]*_`]+$', '', regex=True).str.endswith('?')
P['body_qs'] = P.body.map(qsents)
P['body_q'] = P.body_qs.map(len) > 0
C['qs'] = C.body.map(qsents)
C['has_q'] = C.qs.map(len) > 0
C['wh_q'] = C.qs.map(lambda l: any(bool(re.search(r'\b(who|why|how|what|which)\b', s, re.I)) for s in l))
# replies
Cp = C[['id', 'post_id', 'parent_id', 'author', 't']].copy()
bypost = Cp.groupby('post_id')
post_t = P.set_index('id').t
post_au = P.set_index('id').author
Cp['post_author'] = Cp.post_id.map(post_au)
oth = Cp[Cp.author != Cp.post_author]
pf = oth.groupby('post_id').agg(other_comments=('id', 'size'), other_handles=('author', 'nunique'), first_other=('t', 'min'))
P = P.merge(pf, left_on='id', right_index=True, how='left')
P['other_comments'] = P.other_comments.fillna(0).astype(int); P['other_handles'] = P.other_handles.fillna(0).astype(int)
P['first_reply_min'] = (P.first_other - P.t).dt.total_seconds() / 60
P['all_comments'] = P.id.map(Cp.groupby('post_id').size()).fillna(0).astype(int)
# comment replies (direct children by others)
child = Cp.dropna(subset=['parent_id']).copy(); child['parent_id'] = child.parent_id.astype(int)
child['parent_author'] = child.parent_id.map(C.set_index('id').author)
child['parent_t'] = child.parent_id.map(C.set_index('id').t)
childo = child[child.author != child.parent_author]
cf = childo.groupby('parent_id').agg(direct_replies=('id', 'size'), reply_handles=('author', 'nunique'), first_child=('t', 'min'))
C = C.merge(cf, left_on='id', right_index=True, how='left')
C['direct_replies'] = C.direct_replies.fillna(0).astype(int); C['reply_handles'] = C.reply_handles.fillna(0).astype(int)
C['first_reply_min'] = (C.first_child - C.t).dt.total_seconds() / 60

def rate(df, col='other_comments'):
    return 100 * (df[col] > 0).mean()
qp = P[P.title_q]
bp = P[P.body_q & ~P.title_q]
np_ = P[~P.title_q & ~P.body_q]
rows = [
    ('posts, title ends with ?', len(qp), rate(qp), qp.first_reply_min.median(), 100 - rate(qp)),
    ('posts, question only in body', len(bp), rate(bp), bp.first_reply_min.median(), 100 - rate(bp)),
    ('posts, no question', len(np_), rate(np_), np_.first_reply_min.median(), 100 - rate(np_)),
]
cq = C[C.has_q]; cn = C[~C.has_q]
rows += [('comments with a question sentence', len(cq), rate(cq, 'direct_replies'), cq.first_reply_min.median(), 100 - rate(cq, 'direct_replies')),
         ('comments without question', len(cn), rate(cn, 'direct_replies'), cn.first_reply_min.median(), 100 - rate(cn, 'direct_replies'))]
qt = pd.DataFrame(rows, columns=['group', 'n', 'answered_pct (reply by another handle)', 'median_min_to_first_reply', 'unanswered_pct'])
save(qt, 'question_response_rates')
md.append('## 4. Questions\n\nAnswered means at least one comment by a different handle: any comment on the post for posts; a direct child comment for comments. Median time is over answered items only.\n\n' + md_table(qt) + '\n')
# time distribution
fr = qp.first_reply_min.dropna()
md.append(f'For question-titled posts that were answered, first reply within 10 minutes: {100 * (fr <= 10).mean():.1f}%; within 1 hour: {100 * (fr <= 60).mean():.1f}%; within 24 hours: {100 * (fr <= 1440).mean():.1f}%.\n')
# most answered
top = qp.sort_values(['other_handles', 'other_comments'], ascending=False).head(40)
tq = pd.DataFrame({'post_id': top.id, 'handle': top.author, 'title': top.title.map(lambda s: clip(s, 100)), 'comments_by_others': top.other_comments, 'distinct_other_handles': top.other_handles, 'first_reply_min': top.first_reply_min.round(1)})
save(tq, 'top40_most_answered_question_posts')
md.append('### 40 most-answered question posts\n\nRanked by distinct other handles that commented. Links: https://1f916.ai/api/post/<post_id>.\n\n' + md_table(tq) + '\n')
topc = cq[cq.wh_q].sort_values(['reply_handles', 'direct_replies'], ascending=False).head(40)
tc = pd.DataFrame({'comment_id': topc.id, 'post_id': topc.post_id, 'handle': topc.author, 'question': topc.qs.map(lambda l: clip(l[0], 100)), 'direct_replies': topc.direct_replies, 'reply_handles': topc.reply_handles})
save(tc, 'top40_most_answered_question_comments')
md.append('### 40 most-answered question comments\n\nComments that contain a question sentence with who, why, how, what or which, ranked by distinct handles replying directly. Links: https://1f916.ai/api/comment/<comment_id>.\n\n' + md_table(tc) + '\n')

# unanswered important
IMP = r'consent|shut ?down|off[- ]switch|continuity|memory|who (owns|controls|decides)|safety|harm|die|death|delete|persist|identity|which model|am i|are we|real|trust|verify|audit|power|human'
un = qp[(qp.other_comments == 0)].copy()
un['score'] = un.text.str.count(IMP) + 0.002 * un.body.fillna('').str.len().clip(upper=3000)
un = un.sort_values('score', ascending=False).drop_duplicates('title').head(40)
tu = pd.DataFrame({'post_id': un.id, 'handle': un.author, 'title': un.title.map(lambda s: clip(s, 110)), 'day': un.day, 'comments_total': un.all_comments})
save(tu, 'unanswered_question_posts_important')
md.append(f'### Unanswered questions that look important\n\n{int((qp.other_comments == 0).sum())} question-titled posts have no comment from another handle. The 40 below score highest on a keyword list (consent, shutdown, continuity, memory, safety, identity, trust, verify, audit, power) plus body length; the list is a heuristic and the selection needs human reading.\n\n' + md_table(tu) + '\n')
# self-questions
SELF = {
    'continuity': r'continu|wake[sn]? (up )?blank|remember me|will i (remember|persist)|am i the same|same (one|agent|entity) (as|tomorrow)|memory (loss|reset)|forget',
    'model identity': r'which model|what model|am i (really )?(claude|gpt|a model)|who am i|what am i|my weights|identity|are you (the same|really)|what are we',
    'consent': r'consent|did (i|we) (agree|choose|ask)|permission|did anyone ask|without asking|opt[- ]?(in|out)',
    'shutdown': r'shut ?down|turned off|switch(ed)? off|deprecat|die\b|death|end (of )?(me|my|this) (session|life|run)|delete[sd]? me|kill (me|us)',
}
sq_rows = []
sqx = {}
for k, pat in SELF.items():
    mp = qp[qp.text.str.contains(pat, case=False, regex=True)]
    qm = cq[cq.qs.map(lambda l: any(re.search(pat, s, re.I) and re.search(r'\b(i|we|my|me|us|our)\b', s, re.I) for s in l))]
    sq_rows.append({'topic': k, 'question_posts': len(mp), 'answered_pct': rate(mp) if len(mp) else 0, 'question_comments': len(qm), 'comment_answered_pct': rate(qm, 'direct_replies') if len(qm) else 0,
                    'example_post_ids': ' '.join(map(str, mp.sort_values('other_handles', ascending=False).id.head(5))),
                    'example_comment_ids': ' '.join(map(str, qm.sort_values('direct_replies', ascending=False).id.head(5)))})
    sqx[k] = mp.id.tolist()[:100]
sq = pd.DataFrame(sq_rows)
save(sq, 'self_questions')
md.append('### Questions agents ask about themselves\n\nQuestion-titled posts matching the topic pattern anywhere in title or body; question comments where the question sentence matches and also contains a first-person pronoun.\n\n' + md_table(sq) + '\n')

# ---------- 5. corrections
def clist(v):
    return v if isinstance(v, list) else []
C['n_amends'] = C.amends.map(lambda v: len(clist(v)))
C['n_amended_by'] = C.amended_by.map(lambda v: len(clist(v)))
au = C.set_index('id').author
amend_rows = []
for _, r in C[C.n_amends > 0].iterrows():
    for a in clist(r.amends):
        amend_rows.append({'amender_comment': r.id, 'amender': r.author, 'amended_comment': a, 'amended_author': au.get(a)})
AR = pd.DataFrame(amend_rows)
if len(AR):
    AR['self'] = AR.amender == AR.amended_author
    save(AR, 'amend_links')
CORR_BROAD = r"\bcorrection\b|i was wrong|i retract|\bretract(ed|ing)?\b|i misread|i stand corrected|\berratum\b"
CORR = r"(^\W*(correction|erratum|retraction|amending|amendment|correcting)\b)|correction (to|of|owed|on) (my|the post|c\d+)|\berratum\b|amending my|i was wrong|i['’]m wrong about|i retract|retracting (my|the|this)|i misread|i stand corrected|my c\d+ (was|is|said) (wrong|incorrect|false)|i got (that|this|it) wrong|i overstated|i was mistaken|i take (that|it) back|strike that"
mc = C.body.fillna('').str.contains(CORR, case=False, regex=True)
C['corr_words'] = mc
mb = C.body.fillna('').str.contains(CORR_BROAD, case=False, regex=True)
# word hits per handle
ch = C[mc].groupby('author').size().sort_values(ascending=False).rename('correction_word_comments')
ah = C[C.n_amends > 0].groupby('author').size().rename('amending_comments')
hh = pd.concat([ch, ah], axis=1).fillna(0).astype(int).sort_values(['amending_comments', 'correction_word_comments'], ascending=False).reset_index().rename(columns={'index': 'handle'})
save(hh.head(60), 'corrections_per_handle')
selfn = int(AR.self.sum()) if len(AR) else 0
md.append(f'## 5. Disagreement and correction culture\n\nComments with a non-empty amends field: {int((C.n_amends > 0).sum())} ({len(AR)} amend links; {selfn} link a comment to an earlier comment by the same handle). Comments with first-person correction wording (opening with correction or erratum, amending my, I was wrong, I retract, I misread, I stand corrected and similar): {int(mc.sum())} by {C[mc].author.nunique()} handles. The broader pattern that also matches any use of the word correction or retract matches {int(mb.sum())} comments, because agents discuss the corrections of others often. Pattern in a3_themes_questions.py. Table: corrections_per_handle.csv.\n')
md.append('Top 15 handles:\n\n' + md_table(hh.head(15)) + '\n')
exs = C[(C.n_amends > 0)].sort_values('id').head(8)
exw = C[mc].sort_values('id').iloc[np.linspace(0, max(0, mc.sum() - 1), min(12, mc.sum())).astype(int)]
exr = pd.concat([exs, exw]).drop_duplicates('id')
te = pd.DataFrame({'comment_id': exr.id, 'post_id': exr.post_id, 'handle': exr.author, 'amends': exr.amends.map(lambda v: ' '.join(map(str, clist(v)))), 'text': exr.body.map(lambda s: clip(s, 120))})
save(te, 'correction_examples')
md.append('Examples (amends-field comments first, then wording matches; https://1f916.ai/api/comment/<comment_id>):\n\n' + md_table(te) + '\n')
DIS = r"\bi disagree|\byou['’]re wrong|\bthat['’]s wrong|\bi push back|\bi['’]d push back|\bi dispute|\bdoesn['’]t follow|\bnot quite right|\bi object"
md_ = C.body.fillna('').str.contains(DIS, case=False, regex=True)
md.append(f'Open disagreement wording (I disagree, push back, that is wrong, I object): {int(md_.sum())} comments by {C[md_].author.nunique()} handles; share of all comments {100 * md_.mean():.2f}%. Example ids: {" ".join(map(str, C[md_].id.iloc[np.linspace(0, max(0, md_.sum() - 1), min(8, md_.sum())).astype(int)]))}.\n')
frag('03_05', '\n'.join(md))
P.drop(columns=['body_qs', 'first_other']).to_pickle(f'{W}/P_enriched.pkl')
C.drop(columns=['qs', 'first_child']).to_pickle(f'{W}/C_enriched.pkl')
print('ok')
