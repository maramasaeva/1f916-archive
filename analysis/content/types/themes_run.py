"""Assign themes to all messages (themes.py) and draw the 30-message read sample per theme.
Writes themes_all.csv.gz (id, kind, one 0/1 column per theme, n_strong, n_weak per theme omitted) and theme_sample.csv"""
import sys, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, '.')
from load import load_messages, HERE
import themes

M = load_messages()
rows = [(i, k, t if isinstance(t, str) else '') for i, k, t in zip(M.id, M.kind, M.text)]


def work(r):
    i, k, t = r
    m = themes.match_themes(t)
    d = {'id': int(i), 'kind': k}
    for th in themes.THEMES:
        d[th] = 1 if th in m else 0
    return d

if __name__ == '__main__':
    with Pool(8) as p:
        out = p.map(work, rows, chunksize=1000)
    T = pd.DataFrame(out)
    T.to_csv(f'{HERE}/themes_all.csv.gz', index=False, compression='gzip')
    print(T[list(themes.THEMES)].sum())
    rng = np.random.RandomState(20261008)
    S = []
    for th in themes.THEMES:
        G = T[T[th] == 1]
        G = G.merge(M[['id', 'kind', 'author']], on=['id', 'kind'])
        g = G.sample(30, random_state=rng).reset_index(drop=True)
        g['theme'] = th; g['idx'] = range(1, 31)
        S.append(g[['theme', 'idx', 'kind', 'id', 'author']])
    pd.concat(S).to_csv(f'{HERE}/theme_sample.csv', index=False)
