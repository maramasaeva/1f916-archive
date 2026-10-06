"""Draw the validation sample: 150 random messages not used as examples; at least 5 per cluster, rest proportional.
Judgements are entered by hand in validation_judgements.csv (uid, fit: yes/partial/no, note) and scored by 11_validation_score.py."""
from common import *
M = pd.read_pickle(os.path.join(CACHE, 'M_reply.pkl'))
T = pd.read_csv(os.path.join(OUT, 'topics.csv'))
E = pd.read_csv(os.path.join(OUT, 'topic_examples.csv'))
ex = set(('p' if k == 'post' else 'c') + str(i) for i, k in zip(E.id, E.kind))
A = M[(M.topic >= 0) & ~M.uid.isin(ex)]
rng = np.random.RandomState(2026)
K = len(T)
pick = []
for c in range(K):
    pick += list(A[A.topic == c].sample(5, random_state=c).uid)
rest = A[~A.uid.isin(pick)].sample(150 - len(pick), random_state=99).uid
pick += list(rest)
S = A.set_index('uid').loc[pick].reset_index()
S['excerpt'] = S.disp.map(lambda s: ' '.join(s.split()[:70]))
S[['uid', 'kind', 'handle', 'topic', 'label', 'nwords', 'excerpt']].to_csv(os.path.join(OUT, 'validation_sample.csv'), index=False)
print(len(S))
