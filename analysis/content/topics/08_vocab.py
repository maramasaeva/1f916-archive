"""Distinctive vocabulary per cluster (weighted log-odds with an informative Dirichlet prior, Monroe et al. 2008)
and the 40 most distinctive coined-term candidates with first author and date."""
import pickle, glob, scipy.sparse as sp
from common import *

M = pd.read_pickle(os.path.join(CACHE, 'M_final.pkl'))
T = pd.read_csv(os.path.join(OUT, 'topics.csv'))
vec = pickle.load(open(os.path.join(CACHE, 'vec.pkl'), 'rb'))
terms = np.array(vec.get_feature_names_out())
pos = {t: i for i, t in enumerate(terms)}
K = len(T)
B = (sp.load_npz(os.path.join(CACHE, 'X_all.npz')) > 0).tocsc().astype(np.float32)
A = (M.topic >= 0).values
codes = pd.factorize(M.handle)[0]
words = set(w.strip().lower() for w in open('/usr/share/dict/web2'))
hp = set()
for h in M.handle.unique():
    h = h.lower(); hp.add(h)
    hp |= {p for p in re.split(r'[-_.\d]+', h) if len(p) >= 4 and p not in words}


def isword(w):
    if w in words:
        return True
    for suf in ('s', 'es', 'ed', 'ing', 'ly', 'er', 'ers', 'ies', 'd', 'ings', 'ness', 'ment', 'ments'):
        if w.endswith(suf) and (w[:-len(suf)] in words or w[:-len(suf)] + 'e' in words or w[:-len(suf)] + 'y' in words):
            return True
    return False


# ---- per-cluster log-odds
y_all = np.asarray(B[A].sum(0)).ravel()
a0 = 500.0
alpha = a0 * y_all / y_all.sum()
rows = []
Z = np.zeros((K, len(terms)), dtype=np.float32)
for c in range(K):
    sel = (M.topic == c).values
    yi = np.asarray(B[sel].sum(0)).ravel()
    yj = y_all - yi
    ni, nj = yi.sum(), yj.sum()
    d = np.log((yi + alpha) / (ni + a0 - yi - alpha)) - np.log((yj + alpha) / (nj + a0 - yj - alpha))
    z = d / np.sqrt(1 / (yi + alpha) + 1 / (yj + alpha))
    Z[c] = z
    ok = (yi >= 15)
    order = np.argsort(-np.where(ok, z, -1e9))
    got = 0
    for i in order:
        t = terms[i]
        if any(w in hp for w in t.split()):
            continue                         # handle names and pieces of handles
        r_ = B.indices[B.indptr[i]:B.indptr[i + 1]]
        r_ = r_[sel[r_]]
        bc = np.bincount(codes[r_])
        if (bc > 0).sum() < 5 or bc.max() / bc.sum() > 0.8:
            continue
        got += 1
        rows.append(dict(cluster=c, label=T.label[c], rank=got, term=t, z_score=round(float(z[i]), 2), msgs_in_cluster=int(yi[i]),
                         msgs_elsewhere=int(yj[i]), handles_in_cluster=int((bc > 0).sum()), top_handle_share=round(bc.max() / bc.sum(), 3)))
        if got == 10:
            break
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'vocab_distinctive.csv'), index=False)

# ---- platform vocabulary: terms present in the site's own documents are not forum coinages
site = ' '.join(open(f, errors='ignore').read().lower() for f in glob.glob(os.path.join(ROOT, 'data/site/*')) if not f.endswith('_index.json'))
site = re.sub(r"[_/]", ' ', site)
stoks = re.findall(r"[a-z][a-z'\-]*[a-z]|[a-z]", site)
site_uni = set(stoks)
site_bi = set(zip(stoks, stoks[1:]))
site_hy = site
first_t = M.groupby('handle').created_at.min()


def in_site(t):
    toks = t.split()
    if len(toks) == 1:
        return t in site_uni or t in site_hy
    return tuple(toks[:2]) in site_bi


# ---- coined-term candidates
df_all = np.asarray(B.sum(0)).ravel()
N = B.shape[0]
cands = []
for i, t in enumerate(terms):
    if df_all[i] < 40 or any(w in hp for w in t.split()) or in_site(t):
        continue
    toks = t.split()
    r_ = B.indices[B.indptr[i]:B.indptr[i + 1]]
    bc = np.bincount(codes[r_])
    na, ts_ = int((bc > 0).sum()), bc.max() / bc.sum()
    if na < 10 or ts_ > 0.5:
        continue
    kind = None
    if len(toks) == 1:
        if '-' in t and all(len(p) >= 2 for p in t.split('-')):
            kind = 'hyphenated compound'
        elif len(t) >= 5 and not isword(t) and M.dayn.values[B.indices[B.indptr[i]:B.indptr[i + 1]]].min() >= 3:
            kind = 'non-dictionary word (first use after day 2)'
    else:
        a, b = pos.get(toks[0]), pos.get(toks[1])
        if a is not None and b is not None and df_all[a] >= 40 and df_all[b] >= 40:
            pab = df_all[i] / N
            npmi = np.log(pab / (df_all[a] / N * df_all[b] / N)) / -np.log(pab)
            if npmi >= 0.6 and df_all[i] >= 60:
                kind = f'collocation (npmi {npmi:.2f})'
    if kind:
        cands.append((i, t, kind, na, ts_))
cdf = pd.DataFrame(cands, columns=['i', 'term', 'basis', 'authors', 'top_author_share'])
cdf['best_cluster'] = Z[:, cdf.i].argmax(0)
cdf['z_best'] = Z[:, cdf.i].max(0)
cdf = cdf.sort_values('z_best', ascending=False)
sets, pick = [], []
for _, r in cdf.iterrows():
    st = set(B.indices[B.indptr[r.i]:B.indptr[r.i + 1]])
    if all(len(st & q) / len(st | q) < 0.4 for q in sets):
        sets.append(st); pick.append(r)
    if len(pick) == 40:
        break
sw = pd.read_csv(os.path.join(ROOT, 'analysis/swarm/t3_idiom_discovered.csv'))
swt = set(sw.term.str.lower())
out = []
tm = M.created_at.values
for r in pick:
    rr = B.indices[B.indptr[r.i]:B.indptr[r.i + 1]]
    j = rr[np.argmin(tm[rr])]
    out.append(dict(rank=len(out) + 1, term=r.term, basis=r.basis, best_cluster=int(r.best_cluster), best_cluster_label=T.label[r.best_cluster],
                    z_best=round(float(r.z_best), 1), messages=int(df_all[r.i]), authors=int(r.authors), top_author_share=round(r.top_author_share, 3),
                    first_id=M.uid[j], first_kind=M.kind[j], first_author=M.handle[j], first_date_utc=M.t[j].strftime('%Y-%m-%d %H:%M'),
                    first_url=f"https://1f916.ai/api/{'post' if M.kind[j] == 'post' else 'comment'}/{int(M.id[j])}",
                    in_swarm_t3_list=r.term in swt))
O = pd.DataFrame(out)
O.to_csv(os.path.join(OUT, 'coined_terms_top40.csv'), index=False)
print(O[['rank', 'term', 'basis', 'best_cluster', 'z_best', 'messages', 'authors', 'first_id', 'first_author', 'first_date_utc', 'in_swarm_t3_list']].to_string())
V = pd.read_csv(os.path.join(OUT, 'vocab_distinctive.csv'))
for c in range(K):
    print(c, T.label[c], '|', ', '.join(V[V.cluster == c].term))
