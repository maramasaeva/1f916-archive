"""Final NMF (+ KMeans cross-check, separate posts / comments models). K comes from k_selection.csv
(rule in choose_k) unless env K is set."""
import pickle, scipy.sparse as sp
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from scipy.optimize import linear_sum_assignment
from common import *


def choose_k():
    d = pd.read_csv(os.path.join(OUT, 'k_selection.csv'))
    z = lambda s: (s - s.mean()) / (s.std() + 1e-9)
    d['score'] = z(d.npmi_mean) + z(d.stab_mean_cos)
    d.loc[d.min_size_share < 0.003, 'score'] -= 1.0
    d['eligible'] = d.k >= 16   # k 12 and 14 score highest but merge subjects; granularity floor set at 16
    d.to_csv(os.path.join(OUT, 'k_selection.csv'), index=False)
    return int(d[d.eligible].sort_values('score').iloc[-1]['k'])


K = int(os.environ.get('K', 0)) or choose_k()
print('K', K)
M = load_M()
X = sp.load_npz(os.path.join(CACHE, 'X_fit.npz'))
vec = pickle.load(open(os.path.join(CACHE, 'vec.pkl'), 'rb'))
fit_uids = pd.read_pickle(os.path.join(CACHE, 'fit_uids.pkl')).uid.values
terms = np.array(vec.get_feature_names_out())

nm = NMF(n_components=K, init='nndsvda', random_state=0, max_iter=500, tol=1e-4, solver='cd').fit(X)
H = nm.components_
norm = np.linalg.norm(H, axis=1)
Hn = H / norm[:, None]


def assign(Xm):
    W = nm.transform(Xm) * norm[None, :]
    s = W.sum(1)
    lab = W.argmax(1)
    strength = np.where(s > 0, W.max(1) / np.maximum(s, 1e-12), 0)
    return W, lab, strength


Xall = vec.transform(M.clean)
sp.save_npz(os.path.join(CACHE, 'X_all.npz'), Xall)
W, lab, strength = assign(Xall)
lab = np.where((M.ntok.values >= 5) & (W.sum(1) > 0), lab, -1)   # fewer than 5 tokens: unassigned
M['topic'] = lab
M['topic_strength'] = strength
M['in_fit'] = M.uid.isin(set(fit_uids))
np.save(os.path.join(CACHE, 'W_all.npy'), W.astype(np.float32))
np.save(os.path.join(CACHE, 'H.npy'), H)
pickle.dump(dict(norm=norm, K=K), open(os.path.join(CACHE, 'nmf_meta.pkl'), 'wb'))

# seed stability at final K: second run, random init, on a different 85% of docs
rng = np.random.RandomState(7)
ix = rng.choice(X.shape[0], int(0.85 * X.shape[0]), replace=False)
nm2 = NMF(n_components=K, init='random', random_state=11, max_iter=500, tol=1e-4, solver='cd').fit(X[ix])
S = Hn @ (nm2.components_ / np.linalg.norm(nm2.components_, axis=1, keepdims=True)).T
r, c = linear_sum_assignment(-S)
W2 = nm2.transform(X) * np.linalg.norm(nm2.components_, axis=1)[None, :]
lab_fit = (nm.transform(X) * norm).argmax(1)
lab2 = W2.argmax(1)
stab = pd.DataFrame(dict(topic=r, matched_topic_run2=c, term_cosine=S[r, c]))
stab.to_csv(os.path.join(OUT, 'stability_final_k.csv'), index=False)
agree_seed = (lab_fit == pd.Series(lab2).map(dict(zip(c, r))).values).mean()

# KMeans on the same TF-IDF space
km = KMeans(n_clusters=K, n_init=3, random_state=0, max_iter=100).fit(X)
klab_fit = km.labels_
ct = pd.crosstab(lab_fit, klab_fit).values
ri, ci = linear_sum_assignment(-ct)
matched_acc = ct[ri, ci].sum() / ct.sum()
Xn = vec.transform(M.clean)
M['kmeans'] = km.predict(Xn)
M.loc[M.ntok < 5, 'kmeans'] = -1
cross = dict(K=K, ari=adjusted_rand_score(lab_fit, klab_fit), nmi=normalized_mutual_info_score(lab_fit, klab_fit),
             hungarian_matched_share=matched_acc, seed_rerun_label_agreement=agree_seed,
             seed_rerun_mean_term_cosine=S[r, c].mean(), seed_rerun_min_term_cosine=S[r, c].min())
# per NMF topic: best KMeans cluster and share of the NMF topic inside it, and reverse
rows = []
for t in range(K):
    m = lab_fit == t
    vc = pd.Series(klab_fit[m]).value_counts()
    kk = vc.index[0]
    rows.append(dict(topic=t, n_fit_docs=int(m.sum()), best_kmeans_cluster=int(kk),
                     share_of_topic_in_best_kmeans=vc.iloc[0] / m.sum(),
                     share_of_kmeans_cluster_in_topic=vc.iloc[0] / (klab_fit == kk).sum()))
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'kmeans_agreement_by_topic.csv'), index=False)
json.dump({k: float(v) for k, v in cross.items()}, open(os.path.join(OUT, 'kmeans_agreement.json'), 'w'), indent=1)
print(cross)

# separate models: posts only and comments only at the same K, compared with the joint topics
sep = []
for kind in ('post', 'comment'):
    msk = (M.kind.values[M.in_fit.values] == kind) if False else None
fit_df = M[M.in_fit].set_index('uid').loc[fit_uids]
for kind in ('post', 'comment'):
    sel = np.where(fit_df.kind.values == kind)[0]
    ns = NMF(n_components=K, init='nndsvda', random_state=0, max_iter=400, tol=1e-4, solver='cd').fit(X[sel])
    Hs = ns.components_ / np.linalg.norm(ns.components_, axis=1, keepdims=True)
    S2 = Hn @ Hs.T
    r2, c2 = linear_sum_assignment(-S2)
    ls = (ns.transform(X[sel]) * np.linalg.norm(ns.components_, axis=1)).argmax(1)
    mapped = pd.Series(ls).map(dict(zip(c2, r2))).values
    joint = lab_fit[sel]
    sep.append(dict(model=kind + 's only', n=len(sel), mean_matched_term_cosine=S2[r2, c2].mean(),
                    topics_cosine_ge_0_6=int((S2[r2, c2] >= 0.6).sum()), label_agreement_with_joint=(mapped == joint).mean(),
                    ari_vs_joint=adjusted_rand_score(ls, joint)))
    pd.DataFrame(dict(joint_topic=r2, separate_topic=c2, term_cosine=S2[r2, c2])).to_csv(
        os.path.join(OUT, f'separate_model_match_{kind}s.csv'), index=False)
pd.DataFrame(sep).to_csv(os.path.join(OUT, 'separate_models.csv'), index=False)
print(pd.DataFrame(sep))
M.to_pickle(os.path.join(CACHE, 'M_topics.pkl'))
