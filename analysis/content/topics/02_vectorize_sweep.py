"""TF-IDF matrix over messages with >= 20 words (deduplicated on clean text), then a sweep of NMF k = 12..30
with NPMI coherence and seed/subsample stability."""
import time, sys, scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.decomposition import NMF
from scipy.optimize import linear_sum_assignment
from common import *

M = load_M()
EXTRA = set("""don didn doesn isn wasn aren won wouldn couldn shouldn hasn haven ve ll re just like really thing things
also one would could even much still make made way get got say said let us""".split())
STOP = sorted(set(ENGLISH_STOP_WORDS) | EXTRA)

fit = M[(~M.short) & (M.ntok >= 20)].drop_duplicates('clean').reset_index(drop=True)
print('fit docs', len(fit), 'of', len(M))
vec = TfidfVectorizer(stop_words=STOP, ngram_range=(1, 2), min_df=15, max_df=0.35, max_features=40000,
                      sublinear_tf=True, dtype=np.float32, token_pattern=r"(?u)\b[^\W\d_][\w'\-]*[^\W\d_]\b")
X = vec.fit_transform(fit.clean)
terms = np.array(vec.get_feature_names_out())
print(X.shape, X.nnz)
sp.save_npz(os.path.join(CACHE, 'X_fit.npz'), X)
fit[['uid']].to_pickle(os.path.join(CACHE, 'fit_uids.pkl'))
import pickle
pickle.dump(vec, open(os.path.join(CACHE, 'vec.pkl'), 'wb'))

# coherence helper: NPMI over document co-occurrence on a 30k sample
rng = np.random.RandomState(0)
samp = rng.choice(X.shape[0], 30000, replace=False)
B = (X[samp] > 0).astype(np.float32).tocsc()
ND = B.shape[0]
df = np.asarray(B.sum(0)).ravel()


def npmi(H, topn=10):
    out = []
    for h in H:
        idx = np.argsort(-h)[:topn]
        sub = B[:, idx]
        co = (sub.T @ sub).toarray()
        s = []
        for i in range(topn):
            for j in range(i + 1, topn):
                pij = co[i, j] / ND
                pi, pj = df[idx[i]] / ND, df[idx[j]] / ND
                if pij <= 0:
                    s.append(-1.0)
                else:
                    s.append(np.log(pij / (pi * pj)) / (-np.log(pij)))
        out.append(np.mean(s))
    return np.array(out)


def match_cos(H1, H2):
    a = H1 / (np.linalg.norm(H1, axis=1, keepdims=True) + 1e-12)
    b = H2 / (np.linalg.norm(H2, axis=1, keepdims=True) + 1e-12)
    S = a @ b.T
    r, c = linear_sum_assignment(-S)
    return S[r, c]


def nmf(Xs, k, seed):
    return NMF(n_components=k, init='nndsvda' if seed == 0 else 'random', random_state=seed, max_iter=250,
               tol=1e-4, solver='cd').fit(Xs)


rows = []
n = X.shape[0]
sweep_idx = rng.choice(n, 45000, replace=False)
Xs = X[sweep_idx]
for k in range(12, 31, 2):
    t0 = time.time()
    # three runs: seed 0 on 80% subsample A, seed 1 on 80% subsample B, seed 2 on all 45k
    ia = rng.choice(len(sweep_idx), int(0.8 * len(sweep_idx)), replace=False)
    ib = rng.choice(len(sweep_idx), int(0.8 * len(sweep_idx)), replace=False)
    ma, mb, mc = nmf(Xs[ia], k, 0), nmf(Xs[ib], k, 1), nmf(Xs, k, 2)
    pairs = [match_cos(ma.components_, mb.components_), match_cos(ma.components_, mc.components_),
             match_cos(mb.components_, mc.components_)]
    allc = np.concatenate(pairs)
    coh = np.concatenate([npmi(m.components_) for m in (ma, mb, mc)])
    # hard assignment sizes on full run
    W = mc.transform(Xs)
    sizes = np.bincount(W.argmax(1), minlength=k) / len(W)
    rows.append(dict(k=k, npmi_mean=coh.mean(), npmi_min_topic=np.mean([npmi(m.components_).min() for m in (ma, mb, mc)]),
                     stab_mean_cos=allc.mean(), stab_share_topics_cos_ge_0_8=(allc >= 0.8).mean(),
                     recon_err_full=mc.reconstruction_err_, min_size_share=sizes.min(), max_size_share=sizes.max(),
                     secs=round(time.time() - t0)))
    print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, 'k_selection.csv'), index=False)
