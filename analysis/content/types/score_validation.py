"""Assemble validation_<ver>.csv and precision table from verdicts_<ver>.txt and validation_sample_<ver>.csv.
Usage: python score_validation.py v1"""
import sys, pandas as pd, collections
sys.path.insert(0, '.')
from load import HERE
ver = sys.argv[1]
V = pd.read_csv(f'{HERE}/validation_sample_{ver}.csv')
alt = {}
for line in open(f'{HERE}/verdicts_{ver}.txt'):
    if line.startswith('#') or '|' not in line: continue
    t, rest = [x.strip() for x in line.split('|', 1)]
    for tok in rest.split():
        i, a = tok.split(':'); alt[(t, int(i))] = a
V['verdict'] = ['n' if (r.primary, r.idx) in alt else 'y' for r in V.itertuples()]
V['judged_type'] = [alt.get((r.primary, r.idx), r.primary) for r in V.itertuples()]
V.drop(columns=['rule_hits']).to_csv(f'{HERE}/validation_{ver}.csv', index=False)
P = V.groupby('primary').agg(n=('verdict', 'size'), correct=('verdict', lambda s: (s == 'y').sum()))
P['precision'] = (P.correct / P.n).round(3)
conf = V[V.verdict == 'n'].groupby('primary').judged_type.apply(lambda s: '; '.join(f'{k} {v}' for k, v in collections.Counter(s).most_common(4)))
P['main_confusions (judged type, count)'] = conf
P = P.fillna('')
P.to_csv(f'{HERE}/precision_{ver}.csv')
print(P.to_string())
