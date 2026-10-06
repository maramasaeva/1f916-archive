"""Score the hand-entered judgements (validation_judgements_by_uid.csv: uid, yes/partial/no, note)."""
from common import *
S = pd.read_csv(os.path.join(OUT, 'validation_sample.csv'))
J = pd.read_csv(os.path.join(OUT, 'validation_judgements_by_uid.csv')).set_index('uid')   # hand-entered after reading each message
S['fit'] = S.uid.map(J.fit)
S['note'] = S.uid.map(J.note).fillna('')
assert S.fit.notna().all()
S[['uid', 'kind', 'handle', 'topic', 'label', 'fit', 'note', 'excerpt']].to_csv(os.path.join(OUT, 'validation_judgements.csv'), index=False)
g = S.groupby(['topic', 'label']).fit.agg(n='size', yes=lambda x: (x == 'yes').sum(), partial=lambda x: (x == 'partial').sum(),
                                          no=lambda x: (x == 'no').sum()).reset_index()
g['fit_rate_yes'] = (g.yes / g.n).round(2)
g['fit_rate_yes_or_partial'] = ((g.yes + g.partial) / g.n).round(2)
g.to_csv(os.path.join(OUT, 'validation_by_cluster.csv'), index=False)
print(g.to_string())
print('overall', (S.fit == 'yes').mean(), (S.fit != 'no').mean(), len(S))
