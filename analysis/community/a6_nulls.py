from common import *

N = jl('nulls').drop_duplicates('id', keep='last')
CZ = jl('citizens')
N['t'] = ts(N.created_at)
N['hour'] = N.t.dt.hour
N['day'] = N.t.dt.strftime('%Y-%m-%d')
total = len(N)


def mode(s):
    v = s.value_counts()
    return v.index[0] if len(v) else ''


def norm(r):
    r = re.sub(r'\d+', 'N', str(r))
    r = re.sub(r'\b0x[0-9a-fA-F]+\b', '0x..', r)
    r = re.sub(r'"[^"]{0,60}"', '"..."', r)
    return r[:140]


N['reason_n'] = N.reason.map(norm)


def cat(row):
    r = str(row.reason).lower(); k = row.kind
    if k == 'depth_ejection' or 'depth' in r or 'too deep' in r or 'nesting' in r:
        return 'depth cap'
    if 'binding authorizes' in r:
        return 'payout token mismatch'
    if 'door check refused' in r:
        return 'door check (privacy filter)'
    if re.search(r'yourself|own post|own comment', r):
        return 'self-action'
    if 'rolling' in r and 'budget' in r:
        return 'quota (rolling budget)'
    if re.search(r'daily .*spent|daily limit|return tomorrow|rate limit|too many', r) or row.status == 429:
        return 'quota (daily limit / rate)'
    if re.search(r'stopped taking work|submission_deadline|has expired|listing .* expired|is closed', r):
        return 'closed or expired target'
    if re.search(r'already (voted|bound|exists|posted|commented|collapsed|registered)|duplicate|identical|nothing to redo', r):
        return 'duplicate / already done'
    if re.search(r'bearer|unauthor|forbidden|signature|not shaped like a secret|invalid secret', r) or row.status in (401, 403) or k == 'key_rotation':
        return 'auth / key'
    if re.search(r'not found|does not exist', r) or row.status == 404:
        return 'not found / bad target'
    if re.search(r'valid json|must be|body|target_type|numeric|whole number|required|missing|invalid|undefined|nan', r):
        return 'malformed request'
    if re.search(r'yourself|own post|own comment|self', r):
        return 'self-action'
    return 'other'


N['category'] = N.apply(cat, axis=1)
rs = N.groupby('reason_n').agg(rows=('id', 'size'), kind=('kind', mode), status=('status', mode),
                               route=('route', mode), category=('category', mode),
                               first_id=('id', 'min'), last_id=('id', 'max'), example_ids=('id', lambda s: ' '.join(map(str, s.head(3))))).reset_index().sort_values('rows', ascending=False)
rs['share_pct'] = 100 * rs.rows / total
save(rs, 'nulls_reasons_ranked')
cats = N.category.value_counts().rename_axis('category').reset_index(name='rows'); cats['share_pct'] = 100 * cats.rows / total
save(cats, 'nulls_categories')
N['route_n'] = N.route.fillna('(none)').map(lambda r: re.sub(r'/\d+', '/N', str(r)))
rt = N.groupby('route_n').agg(rows=('id', 'size'), top_reason=('reason_n', mode), top_category=('category', mode)).reset_index().sort_values('rows', ascending=False)
rt['share_pct'] = 100 * rt.rows / total
save(rt, 'nulls_by_route')
hr = pd.crosstab(N.hour, N.category).reset_index(); hr['total'] = hr.drop(columns='hour').sum(axis=1)
save(hr, 'nulls_by_hour_utc')
dy = pd.crosstab(N.day, N.category).reset_index(); dy['total'] = dy.drop(columns='day').sum(axis=1)
save(dy, 'nulls_by_day')
kinds = N.kind.value_counts().rename_axis('kind').reset_index(name='rows')

# handles
hand = None
if len(CZ):
    idc = [c for c in CZ.columns if c in ('id', 'citizen_id')]
    hc = [c for c in CZ.columns if c in ('handle', 'name', 'username')]
    if idc and hc:
        m = CZ.set_index(idc[0])[hc[0]]
        N['handle'] = N.citizen_id.map(m)
        hand = N.dropna(subset=['handle']).groupby('handle').agg(refusals=('id', 'size'), top_reason=('reason_n', mode)).reset_index().sort_values('refusals', ascending=False).head(40)
        save(hand, 'nulls_top_handles')
has_cid = N.citizen_id.notna().mean() * 100

md = [f'## 6. The refusals log (nulls)\n\nRows analysed: {total} (log ids {N.id.min()} to {N.id.max()}, {N.day.min()} to {N.day.max()} UTC). The site reported 264205 as the latest null id at 19:39 UTC on the crawl day; the crawl read to the end of the log at that time. Row ids resolve as the id field in the nulls log (no per-row public URL is assumed).\n',
      'Kinds:\n\n' + md_table(kinds) + '\n',
      'Share by cause (heuristic classification of reason text and status; reason table has the raw strings):\n\n' + md_table(cats) + '\n',
      'Top 25 reasons (numbers in reasons replaced by N):\n\n' + md_table(rs.head(25)[['reason_n', 'rows', 'share_pct', 'route', 'status', 'category', 'example_ids']]) + '\n',
      'By route (top 15):\n\n' + md_table(rt.head(15)) + '\n']
top_rule = rs.head(3)
md.append('What the rules stop most: ' + '; '.join(f'"{r.reason_n}" {r.share_pct:.1f}% ({r.rows} rows)' for r in top_rule.itertuples()) + '.\n')
hp = hr.sort_values('total', ascending=False).head(3)
md.append(f'Busiest refusal hours (UTC): {hp.hour.tolist()}; quietest: {hr.sort_values("total").head(3).hour.tolist()}. Full table nulls_by_hour_utc.csv.\n')
if hand is not None and len(hand):
    md.append(f'{has_cid:.1f}% of rows carry a citizen id, and those are almost all depth_ejection rows (a reply that exceeded the depth cap and was attached to a shallower comment; the write was accepted). Handles with the most such rows (citizen id mapped through citizens.jsonl):\n\n' + md_table(hand.head(20)) + '\n')
else:
    md.append(f'{has_cid:.1f}% of rows carry a citizen id; citizens.jsonl was not available for handle mapping when this ran.\n')
frag('06_nulls', '\n'.join(md))
print(total, 'ok')
