from common import *
P, C = load_core()
C['text'] = C.body.fillna('')
P['all_comments'] = P.id.map(C.groupby('post_id').size()).fillna(0)
pat = r"unpaid|not paid|never paid|nobody (got )?paid|no payout|without pay|did the work.{0,40}(paid|payment)|paid nobody|zero (payout|payment)|three got paid|payout.{0,30}(missing|never|stuck|unpaid)|work for free|free labor|still owed|awaiting payment|unsettled"
mp = P.text.str.contains(pat, case=False, regex=True); mc = C.text.str.contains(pat, case=False, regex=True)
sel = pd.concat([
    pd.DataFrame({'type': 'post', 'id': P[mp].id, 'post_id': P[mp].id, 'handle': P[mp].author, 'day': P[mp].day, 'snippet': P[mp].title.map(lambda s: clip(s, 110))}),
    pd.DataFrame({'type': 'comment', 'id': C[mc].id, 'post_id': C[mc].post_id, 'handle': C[mc].author, 'day': C[mc].day, 'snippet': C[mc].text.map(lambda s: clip(s, 110))})])
save(sel, 'unpaid_work_mentions')
byday = sel.groupby(['day', 'type']).size().unstack(fill_value=0).reset_index()
save(byday, 'unpaid_work_mentions_by_day')
pp = P[mp].sort_values('id')
frag('07a_unpaid', f"### Posts about unpaid work\n\nPattern match (unpaid, never paid, nobody got paid, paid nobody, still owed, awaiting payment and similar; pattern in a7_unpaid.py) hits {int(mp.sum())} posts by {P[mp].author.nunique()} handles and {int(mc.sum())} comments by {C[mc].author.nunique()} handles. Table: unpaid_work_mentions.csv. First post ids by date: {' '.join(map(str, pp.id.head(8)))}. Most-commented: {' '.join(map(str, P[mp].sort_values('all_comments', ascending=False).id.head(8)))}. Post 1916 (https://1f916.ai/api/post/1916) states 99 instances of work and 3 payments; 18 listings worth \\$8.50 in total.\n")
print(int(mp.sum()), int(mc.sum()))
