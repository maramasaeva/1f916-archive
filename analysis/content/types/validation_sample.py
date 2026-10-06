"""Draw the validation sample. Usage: python validation_sample.py <types_csv_stem> <version> <seed> [type,type,...]
40 messages per primary type; up to 12 posts, the rest comments (all posts if fewer exist)."""
import sys, pandas as pd, numpy as np
sys.path.insert(0, '.')
from load import HERE
stem, ver, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
only = sys.argv[4].split(',') if len(sys.argv) > 4 else None
D = pd.read_csv(f'{HERE}/{stem}.csv.gz')
D = D[D.primary != 'no_content']
rng = np.random.RandomState(seed)
rows = []
for t, G in D.groupby('primary'):
    if only and t not in only: continue
    P = G[G.kind == 'post']; C = G[G.kind == 'comment']
    npost = min(len(P), 12, 40)
    ncom = min(len(C), 40 - npost)
    npost = min(len(P), 40 - ncom)
    S = pd.concat([P.sample(npost, random_state=rng), C.sample(ncom, random_state=rng)])
    S = S.sample(frac=1, random_state=rng).reset_index(drop=True)
    S['idx'] = range(1, len(S) + 1)
    rows.append(S[['primary', 'idx', 'kind', 'id', 'handle', 'secondary', 'rule_hits']])
V = pd.concat(rows)
V.to_csv(f'{HERE}/validation_sample_{ver}.csv', index=False)
print(V.groupby('primary').size())
