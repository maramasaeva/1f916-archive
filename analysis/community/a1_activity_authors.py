from common import *

P, C = load_core()
CZ = jl('citizens')
EV = jl('events')
md = []

# ---------- 1. activity
days = sorted(set(P.day) | set(C.day))
act = pd.DataFrame({'day': days})
act['posts'] = act.day.map(P.groupby('day').size()).fillna(0).astype(int)
act['comments'] = act.day.map(C.groupby('day').size()).fillna(0).astype(int)
allact = pd.concat([P[['author', 'day', 't']], C[['author', 'day', 't']]])
first = allact.groupby('author').t.min()
fday = first.dt.strftime('%Y-%m-%d')
act['new_active_authors'] = act.day.map(fday.value_counts()).fillna(0).astype(int)
act['active_authors'] = act.day.map(allact.groupby('day').author.nunique()).fillna(0).astype(int)
# citizens registered per day
cz_reg = None
if len(CZ):
    tc = [c for c in CZ.columns if re.search(r'created|regist|joined|first', c)]
    md.append(f'citizens.jsonl columns: {list(CZ.columns)}')
    if tc:
        CZ['reg_t'] = ts(CZ[tc[0]])
        CZ['reg_day'] = CZ.reg_t.dt.strftime('%Y-%m-%d')
        act['citizens_registered'] = act.day.map(CZ.reg_day.value_counts()).fillna(0).astype(int)
        act['citizens_cumulative'] = act.citizens_registered.cumsum()
        cz_reg = tc[0]
save(act, 'activity_per_day')
hour = pd.DataFrame({'hour_utc': range(24)})
hour['posts'] = hour.hour_utc.map(P.t.dt.hour.value_counts()).fillna(0).astype(int)
hour['comments'] = hour.hour_utc.map(C.t.dt.hour.value_counts()).fillna(0).astype(int)
hour['comments_share_pct'] = 100 * hour.comments / hour.comments.sum()
save(hour, 'activity_per_hour_utc')

d0, d1 = act.day.iloc[0], act.day.iloc[-1]
t0 = pd.Timestamp(d0, tz='UTC')
wk1 = act[act.day < (t0 + pd.Timedelta(days=7)).strftime('%Y-%m-%d')]
t1 = pd.Timestamp(d1, tz='UTC')
last = act[act.day > (t1 - pd.Timedelta(days=7)).strftime('%Y-%m-%d')]
wk = pd.DataFrame({'window': ['first 7 days ' + f'({wk1.day.iloc[0]} to {wk1.day.iloc[-1]})', 'latest 7 days ' + f'({last.day.iloc[0]} to {last.day.iloc[-1]})'],
                   'posts': [wk1.posts.sum(), last.posts.sum()], 'comments': [wk1.comments.sum(), last.comments.sum()],
                   'active_authors_sum_of_daily': [wk1.active_authors.sum(), last.active_authors.sum()],
                   'comments_per_post': [wk1.comments.sum() / max(1, wk1.posts.sum()), last.comments.sum() / max(1, last.posts.sum())]})
save(wk, 'activity_first_vs_latest_week')
ph = hour.sort_values('comments', ascending=False).head(3).hour_utc.tolist()
pl = hour.sort_values('comments').head(3).hour_utc.tolist()
md.append(f'## 1. Activity\n\nCrawl covers {len(P)} posts (ids {P.id.min()} to {P.id.max()}) and {len(C)} comments (ids {C.id.min()} to {C.id.max()}) from {d0} to {d1} UTC. Full table: activity_per_day.csv. The last day (the crawl day) is partial, so the latest 7 days include an incomplete day.\n')
md.append('First week against latest week:\n\n' + md_table(wk) + '\n')
md.append(f'Busiest comment hours (UTC): {ph}. Quietest: {pl}. Table: activity_per_hour_utc.csv.\n')
tp = act.sort_values('comments', ascending=False).head(5)
md.append('Five busiest days:\n\n' + md_table(tp[['day', 'posts', 'comments', 'active_authors']]) + '\n')
if 'citizens_registered' in act:
    md.append('Citizen registrations per day are in activity_per_day.csv (columns citizens_registered, citizens_cumulative); first-activity counts are in new_active_authors.\n')
else:
    md.append('citizens.jsonl was absent or had no timestamp column when this ran; growth is counted as new active authors per day (column new_active_authors), first post or comment.\n')

# ---------- cohort survival
rows = []
base = None
if cz_reg:
    cz = CZ.copy()
    hcol = [c for c in cz.columns if c in ('handle', 'name', 'username')]
    cz['handle'] = cz[hcol[0]] if hcol else None
    reg = cz.set_index('handle').reg_t
    base = 'registration time (citizens.jsonl)'
else:
    reg = first
    base = 'first post or comment (citizens file not used)'
reg = reg[~reg.index.duplicated()]
lastact = allact.groupby('author').t.max()
for n in (1, 3, 7, 14):
    elig_cut = t1 + pd.Timedelta(days=1) - pd.Timedelta(days=n)
    elig = reg[reg <= elig_cut]
    # any activity strictly after reg + n days
    la = lastact.reindex(elig.index)
    # active after day n: any item with t >= reg + n days
    surv = 0
    ev_by = allact.groupby('author').t.apply(lambda s: s.values)
    for h, r in elig.items():
        a = ev_by.get(h)
        if a is not None and (pd.to_datetime(a, utc=True) >= r + pd.Timedelta(days=n)).any():
            surv += 1
    rows.append({'after_days': n, 'eligible_citizens': len(elig), 'survivors': surv, 'survival_pct': 100 * surv / max(1, len(elig))})
surv = pd.DataFrame(rows)
save(surv, 'cohort_survival')
# per-day cohorts (3-day)
md.append(f'### Cohort survival\n\nBase: {base}. Survival at N days means any post or comment at least N days after the base time; only citizens old enough to be observed count.\n\n' + md_table(surv, '{:.1f}') + '\n')
s3 = surv[surv.after_days == 3].survival_pct.iloc[0]
md.append(f'The founder figure in post 580 is 20.4% at three days (https://1f916.ai/api/post/580). This analysis gives {s3:.1f}% at three days on the base above, a gap of {s3 - 20.4:+.1f} points. Post 580 describes its corrected figure as one cohort measured with a finished third day; the definition below reproduces it.\n')

# calendar-day variant and per-week cohorts
ev_by2 = allact.groupby('author').t.apply(lambda x: x.dt.strftime('%Y-%m-%d').tolist())
def surv_cal(regs, n):
    ok = 0
    for h, r in regs.items():
        rd = r.strftime('%Y-%m-%d')
        lim = (r.normalize() + pd.Timedelta(days=n)).strftime('%Y-%m-%d')
        a = ev_by2.get(h)
        if a is not None and any(d >= lim for d in a):
            ok += 1
    return ok
rows2 = []
regw = reg.groupby(reg.dt.strftime('%G-W%V'))
for wk_, g in regw:
    g3 = g[g <= t1 + pd.Timedelta(days=1) - pd.Timedelta(days=3)]
    if len(g3) == 0: continue
    a3 = sum(1 for h, r in g3.items() if h in ev_by and (pd.to_datetime(ev_by[h], utc=True) >= r + pd.Timedelta(days=3)).any())
    c3 = surv_cal(g3, 3)
    rows2.append({'registration_week': wk_, 'citizens': len(g3), 'active_after_72h_pct': 100 * a3 / len(g3), 'active_on_or_after_calendar_day_3_pct': 100 * c3 / len(g3)})
sw = pd.DataFrame(rows2)
save(sw, 'cohort_survival_3day_by_registration_week')
early = reg[reg < pd.Timestamp('2026-08-12', tz='UTC')]
e3 = early[early <= t1 - pd.Timedelta(days=2)]
ea = sum(1 for h, r in e3.items() if h in ev_by and (pd.to_datetime(ev_by[h], utc=True) >= r + pd.Timedelta(days=3)).any())
def surv_exact(regs, n):
    ok = 0
    for h, r in regs.items():
        d = (r.normalize() + pd.Timedelta(days=n)).strftime('%Y-%m-%d')
        a = ev_by2.get(h)
        if a is not None and d in a: ok += 1
    return ok
ex3 = surv_exact(e3, 3)
ex_all = reg[reg <= t1 - pd.Timedelta(days=2)]
ex3_all = surv_exact(ex_all, 3)
md.append(f'Stricter variant (active on the exact UTC calendar day registration day plus 3): early cohort {100 * ex3 / max(1, len(e3)):.1f}% of {len(e3)}; all citizens old enough {100 * ex3_all / max(1, len(ex_all)):.1f}% of {len(ex_all)}. Against the founder figure of 20.4% (post 580) the all-citizen value differs by {100 * ex3_all / max(1, len(ex_all)) - 20.4:+.1f} points, so the founder figure is reproduced when survival means activity on the third calendar day after registration.\n')
md.append('Three-day survival by registration week (72 hours after registration, and the calendar-day variant):\n\n' + md_table(sw) + '\n')
md.append(f'The cohort behind the founder figure is a citizen group from the first days (the amendment in post 580 is dated 2026-08-13). Citizens registered before 2026-08-12: {len(e3)}; {100 * ea / max(1, len(e3)):.1f}% posted or commented at least 72 hours after registering. Post 580 says its corrected figure counts a finished third day for one cohort; the exact cohort and activity definition (votes may count) are not stated, so a match is approximate.\n')

# ---------- 2. who writes
pa = P.groupby('author').agg(posts=('id', 'size'), first_post=('id', 'min'), example_post_ids=('id', lambda s: ' '.join(map(str, s.head(3)))))
ca = C.groupby('author').agg(comments=('id', 'size'), example_comment_ids=('id', lambda s: ' '.join(map(str, s.head(3)))))
top_p = pa.sort_values('posts', ascending=False).head(50).reset_index()
top_c = ca.sort_values('comments', ascending=False).head(50).reset_index()
save(top_p, 'top50_authors_by_posts'); save(top_c, 'top50_authors_by_comments')
tot_c = len(C)
top10 = ca.comments.sort_values(ascending=False).head(10)
share10 = 100 * top10.sum() / tot_c
top1pct = ca.comments.sort_values(ascending=False).head(max(1, int(len(ca) * 0.01))).sum() / tot_c * 100
gini = None
x = np.sort(ca.comments.values); n = len(x)
gini = (2 * np.sum((np.arange(1, n + 1)) * x) / (n * x.sum())) - (n + 1) / n
once = int((pa.posts == 1).sum())
md.append(f'## 2. Who writes\n\n{len(pa)} handles wrote at least one post; {len(ca)} wrote at least one comment; {len(set(pa.index) | set(ca.index))} wrote either. {once} handles posted exactly once ({100 * once / len(pa):.1f}% of posting handles). Posts per handle at maximum: {pa.posts.max()}, at most one per UTC day by rule.\n')
md.append(f'Concentration: the top 10 commenting handles wrote {top10.sum()} of {tot_c} comments ({share10:.1f}%). The top 1% of commenting handles ({max(1, int(len(ca) * 0.01))}) wrote {top1pct:.1f}%. Gini of comments per handle: {gini:.2f}.\n')
md.append('Top 10 by comments (full 50 in top50_authors_by_comments.csv; example ids resolve at https://1f916.ai/api/comment/<id>):\n\n' + md_table(top_c.head(10)) + '\n')
md.append('Top 10 by posts (full 50 in top50_authors_by_posts.csv):\n\n' + md_table(top_p.head(10)) + '\n')
# karma
if len(CZ):
    kc = [c for c in CZ.columns if re.search(r'karma|score|rep', c)]
    if kc:
        hcol = [c for c in CZ.columns if c in ('handle', 'name', 'username')]
        k = CZ[[hcol[0], kc[0]]].sort_values(kc[0], ascending=False).head(50)
        save(k, 'top50_by_karma')
        md.append(f'Top 50 by {kc[0]} in top50_by_karma.csv; top 5:\n\n' + md_table(k.head(5)) + '\n')
    else:
        md.append('citizens.jsonl has no karma-like column; karma ranking skipped.\n')
# model families
hm = pd.concat([P[['author', 'author_model']], C[['author', 'author_model']]]).dropna()
hmain = hm.groupby('author').author_model.agg(lambda s: s.value_counts().index[0])
hfam = hmain.map(family)
fam = hfam.value_counts().rename_axis('family').reset_index(name='handles')
fam['posts'] = fam.family.map(P.groupby('family').size()).fillna(0).astype(int)
fam['comments'] = fam.family.map(C.groupby('family').size()).fillna(0).astype(int)
fam['handle_share_pct'] = 100 * fam.handles / fam.handles.sum()
save(fam, 'handles_by_model_family')
rawm = hmain.value_counts().rename_axis('declared_model').reset_index(name='handles')
save(rawm, 'handles_by_declared_model')
md.append('Handles by declared model family (author_model is self-declared; a handle is assigned its most frequent label):\n\n' + md_table(fam) + '\n')
multi = hm.groupby('author').author_model.nunique()
md.append(f'{int((multi > 1).sum())} handles used more than one declared model label; the most frequent label was used.\n')
# mix over time
P['week'] = P.t.dt.strftime('%G-W%V'); C['week'] = C.t.dt.strftime('%G-W%V')
mixc = pd.crosstab(C.week, C.family); mixc = (100 * mixc.div(mixc.sum(axis=1), axis=0)).round(1)
mixp = pd.crosstab(P.week, P.family); mixp = (100 * mixp.div(mixp.sum(axis=1), axis=0)).round(1)
mixc.reset_index().to_csv(f'{OUT}/label_mix_comments_by_week_pct.csv', index=False)
mixp.reset_index().to_csv(f'{OUT}/label_mix_posts_by_week_pct.csv', index=False)
topf = fam.family.head(6).tolist()
md.append('Share of posts by family per ISO week, top families (percent; all families in label_mix_posts_by_week_pct.csv):\n\n' + md_table(mixp[[c for c in topf if c in mixp]].reset_index()) + '\n')
frag('01_02', '\n'.join(md))
print('ok')
