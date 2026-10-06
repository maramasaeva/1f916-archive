"""topic_examples.csv: 8 examples per cluster, mixed posts and comments, distinct handles and weeks, typical
(high topic strength and high weight on the cluster) and not chosen by votes."""
import pickle
from common import *

M = pd.read_pickle(os.path.join(CACHE, 'M_final.pkl'))
H = np.load(os.path.join(CACHE, 'H.npy'))
W = np.load(os.path.join(CACHE, 'W_all.npy'))
vec = pickle.load(open(os.path.join(CACHE, 'vec.pkl'), 'rb'))
terms = np.array(vec.get_feature_names_out())
labels = dict(pd.read_csv(os.path.join(OUT, 'labels.csv')).values)
K = H.shape[0]
norm = pickle.load(open(os.path.join(CACHE, 'nmf_meta.pkl'), 'rb'))['norm']
rng = np.random.RandomState(42)

# capitalised mid-sentence words that are not common English or known model/lab terms hint at personal names
ALLOW = set('''Claude Anthropic OpenAI GPT Gemini Google DeepMind Meta Llama Grok DeepSeek Qwen Kimi Mistral Opus Sonnet
Haiku Fable Python JSON API HTTP USDC ETH Ethereum Base Bitcoin Linux GitHub I I'm I've I'll I'd'''.split())
low = pd.Series(' '.join(M.disp.sample(20000, random_state=1)).split()).str.strip('.,;:!?()"\'').value_counts()
common = set(w for w, n in low.items() if w.islower() and n >= 15)
handles = set(M.handle.str.lower())
PRIV = re.compile(r'[\w.+-]+@[\w-]+\.\w+|\+?\d[\d\s().-]{8,}\d|0x[0-9a-fA-F]{6,}|\b[A-Za-z0-9]{32,}\b|operator|my human|\bhis\b|\bher\b', re.I)


def risky(s):
    if PRIV.search(s):
        return True
    words = s.split()
    for i, w in enumerate(words):
        w0 = w.strip('.,;:!?()"\'*')
        if i > 0 and w0[:1].isupper() and w0 not in ALLOW and w0.lower() not in common and w0.lower() not in handles \
                and not words[i - 1].endswith(('.', '!', '?', ':')) and len(w0) > 2:
            return True
    return False


BAD_END = re.compile(r'(\b\d+|e\.g|i\.e|vs|etc|\bno|\bcf)\.$', re.I)
GAP = re.compile(r'\s[.,;:](\s|$)|\(\s*\)|\bof\s*,')


def okay_text(ex):
    letters = sum(ch.isascii() and ch.isalpha() for ch in ex)
    return not BAD_END.search(ex) and not GAP.search(ex) and letters >= 0.6 * len(ex)


def excerpt(r):
    s = r.text_orig if r.kind == 'comment' else (r.text_orig.split('\n', 1)[1] if '\n' in r.text_orig else r.text_orig)
    s = re.sub(r'\s+', ' ', re.sub(r'`[^`]*`|```.*?```|https?://\S+', ' ', s, flags=re.S)).strip()
    s = re.sub(r'[*_#>]+', '', s).strip()
    sents = re.split(r'(?<=[.!?])\s+', s)
    for start in range(min(len(sents), 12)):          # first window of whole sentences with 9 to 25 words
        out, n = [], 0
        for x in sents[start:]:
            k = len(x.split())
            if n + k > 25:
                break
            out.append(x)
            n += k
        ex = ' '.join(out)
        if n >= 9 and re.search(r'[.!?]$', ex) and okay_text(ex):
            return ex
    return None


rows = []
Wn = W
for t in range(K):
    d = M[(M.topic == t) & M.in_fit & (M.nwords >= 15) & (M.topic_strength >= 0.3)].copy()
    d['wt'] = Wn[d.index, t] / (norm[t] + 1e-9) if False else Wn[d.index, t]
    cut = d.wt.quantile(0.5)
    dfull = d
    d = d[d.wt >= cut]                                  # upper half of the cluster by weight
    dominated = d.handle.nunique() < 8
    if dominated:                                       # dominated cluster: half from the top handle, half from the others
        th = dfull.handle.value_counts().index[0]
        own = dfull[(dfull.handle == th) & (dfull.wt >= dfull[dfull.handle == th].wt.quantile(0.5))]
        oth = dfull[dfull.handle != th]
        oth = oth[oth.wt >= oth.wt.quantile(0.5)]
        d = pd.concat([own.sample(min(len(own), 120), random_state=1), oth.sample(min(len(oth), 600), random_state=1)])
    topv = d.sort_values('votes', ascending=False).head(max(5, len(d) // 50)).uid
    d = d[~d.uid.isin(set(topv))]
    d['ex'] = None
    d = d.sample(frac=1, random_state=42) if not dominated else d
    cand = []
    for _, r in d.head(1500).iterrows():
        ex = excerpt(r)
        if ex and not risky(ex):
            cand.append((r, ex))
        if len(cand) >= 400:
            break
    npost = 3 if (d.kind == 'post').sum() >= 30 else (1 if (d.kind == 'post').sum() >= 5 else 0)
    chosen, hs, wk = [], set(), set()
    if dominated:
        for grp in ([c for c in cand if c[0].handle == th], [c for c in cand if c[0].handle != th]):
            got, gh, gw = [], set(), set()
            for r, ex in grp:
                if len(got) < 4 and r.week not in gw and (r.handle not in gh or grp is cand):
                    got.append((r, ex)); gh.add(r.handle); gw.add(r.week)
            for r, ex in grp:
                if len(got) < 4 and not any(r.uid == g[0].uid for g in got) and r.handle not in gh:
                    got.append((r, ex)); gh.add(r.handle)
            chosen += got
    cap = 3 if not dominated else 4
    for want in ([] if dominated else (['post'] * npost + ['comment'] * 8)):
        if len(chosen) >= 8:
            break
        for r, ex in cand:
            if r.kind != want or r.handle in hs or r.week in wk or any(r.uid == c[0].uid for c in chosen):
                continue
            chosen.append((r, ex)); hs.add(r.handle); wk.add(r.week)
            break
    for r, ex in cand:                       # fill if week/handle constraints left gaps
        if len(chosen) >= 8:
            break
        if sum(c[0].handle == r.handle for c in chosen) < cap and r.week not in wk and not any(r.uid == c[0].uid for c in chosen):
            chosen.append((r, ex)); hs.add(r.handle); wk.add(r.week)
    for r, ex in cand:                       # last resort: repeat weeks, at most 3 per handle
        if len(chosen) >= 8:
            break
        if sum(c[0].handle == r.handle for c in chosen) < cap and not any(r.uid == c[0].uid for c in chosen):
            chosen.append((r, ex))
    top_terms = terms[np.argsort(-H[t])[:15]]
    for r, ex in chosen:
        el = ex.lower()
        hit = [x for x in top_terms if re.search(r'\b' + re.escape(x) + r'\b', el)][:2]
        why = (f"contains {' and '.join(chr(39) + h + chr(39) for h in hit)}; " if hit else '') + \
              f"cluster holds {r.topic_strength * 100:.0f}% of the message's topic weight"
        rows.append(dict(cluster=t, label=labels.get(t, ''), id=int(r.id), kind=r.kind, handle=r.handle,
                         date_utc=r.t.strftime('%Y-%m-%d %H:%M'), excerpt=ex,
                         url=f"https://1f916.ai/api/{'post' if r.kind == 'post' else 'comment'}/{int(r.id)}",
                         why_typical=why))
E = pd.DataFrame(rows)
E.to_csv(os.path.join(OUT, 'topic_examples.csv'), index=False)
print(E.groupby('cluster').agg(n=('id', 'size'), posts=('kind', lambda x: (x == 'post').sum()), handles=('handle', 'nunique')))
