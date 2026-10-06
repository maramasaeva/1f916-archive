"""Theme read precision: strict = y share of 30; loose = (y + p) share. Writes theme_precision.csv and theme_validation.csv"""
import sys, pandas as pd
sys.path.insert(0, '.')
from load import HERE
S = pd.read_csv(f'{HERE}/theme_sample.csv')
v = {}
for line in open(f'{HERE}/theme_verdicts.txt'):
    if line.startswith('#') or '|' not in line: continue
    th, rest = [x.strip() for x in line.split('|', 1)]
    for tok in rest.split():
        i, a = tok.split(':'); v[(th, int(i))] = a
S['verdict'] = [v.get((r.theme, r.idx), 'y') for r in S.itertuples()]
S.to_csv(f'{HERE}/theme_validation.csv', index=False)
P = S.groupby('theme').verdict.value_counts().unstack(fill_value=0)
for c in 'ypn':
    if c not in P: P[c] = 0
P['n_read'] = P[['y', 'p', 'n']].sum(axis=1)
P['precision_strict'] = (P.y / P.n_read).round(3)
P['precision_loose'] = ((P.y + P.p) / P.n_read).round(3)
P = P[['n_read', 'y', 'p', 'n', 'precision_strict', 'precision_loose']]
P.to_csv(f'{HERE}/theme_precision.csv')
print(P)
