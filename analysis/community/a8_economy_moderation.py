from common import *
md = []
USDC = '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913'
def usd(a, tok=None):
    if tok is not None and str(tok).lower() != USDC:
        return np.nan
    try: return int(a) / 1e6
    except Exception: return np.nan
def bucket(x):
    if pd.isna(x): return 'n/a'
    for lo, hi, n in [(0, 0.5, '<0.5'), (0.5, 1, '0.5-1'), (1, 2, '1-2'), (2, 5, '2-5'), (5, 10, '5-10'), (10, 1e12, '10+')]:
        if lo <= x < hi: return n
    return 'n/a'
order = ['<0.5', '0.5-1', '1-2', '2-5', '5-10', '10+', 'n/a']
# ---- listings
L = jl('listings'); LD = jl('listings_detail')
L['usd'] = [usd(a, t) for a, t in zip(L.amount_atomic, L.token)]; L['bucket'] = L.usd.map(bucket)
L['created'] = ts(L.created_at)
md.append('## 7. Economy\n')
lc = L.lifecycle.value_counts().rename_axis('lifecycle').reset_index(name='listings')
md.append(f'### Listings\n\n{len(L)} listings (ids {L.id.min()} to {L.id.max()}) by {L.funder.nunique()} funders, chain {L.chain_id.iloc[0]}. {int((L.token.str.lower() == USDC).sum())} are priced in USDC and {int((L.token.str.lower() != USDC).sum())} in another token (listing ids {' '.join(map(str, L[L.token.str.lower() != USDC].id))}; excluded from USDC sums and counted under n/a). Total posted value {L.usd.sum():.2f} USDC; median {L.usd.median():.2f}; maximum {L.usd.max():.2f}. Row `listing-<id>` resolves at https://1f916.ai/api/listings/<id>.\n\n' + md_table(lc) + '\n')
ab = L.bucket.value_counts().reindex(order).dropna().astype(int).rename_axis('amount_usdc').reset_index(name='listings')
md.append('By amount range (USDC):\n\n' + md_table(ab) + '\n')
L['has_receipt'] = L.receipts > 0; L['has_payment'] = L.observed_payments > 0
md.append(f'Listings with at least one submission: {int((L.submissions > 0).sum())} of {len(L)} ({100 * (L.submissions > 0).mean():.1f}%); total submissions {int(L.submissions.sum())}; total payout bindings {int(L.bindings.sum())}; listings with a worker receipt: {int(L.has_receipt.sum())} ({100 * L.has_receipt.mean():.1f}%); listings with an observed on-chain payment: {int(L.has_payment.sum())} ({100 * L.has_payment.mean():.1f}%).\n')
save(L.drop(columns=['created']), 'economy_listings')
if len(LD):
    st = LD.state.value_counts().rename_axis('state').reset_index(name='listings')
    md.append('Listing detail state (from per-listing records):\n\n' + md_table(st) + '\n')
    awards = []
    for _, r in LD.iterrows():
        subs = {s['id']: s for s in (r.submissions if isinstance(r.submissions, list) else [])}
        for a in (r.awards if isinstance(r.awards, list) else []):
            s = subs.get(a.get('submission_id'), {})
            awards.append({'listing_id': r.listing_id, 'award_id': a.get('award_id'), 'submission_id': a.get('submission_id'), 'handle': s.get('handle'), 'state': a.get('state'),
                           'amount_usdc': usd(a.get('amount_atomic'), r.token), 'awarded_by': a.get('awarded_by'), 'listing_created': r.created_at,
                           'submission_created': s.get('created_at'), 'awarded_at': a.get('awarded_at'), 'paid_at': a.get('paid_at')})
    AW = pd.DataFrame(awards)
    if len(AW):
        AW['h_sub_to_award'] = (AW.awarded_at - AW.submission_created) / 3.6e6
        AW['h_listing_to_award'] = (AW.awarded_at - AW.listing_created) / 3.6e6
        save(AW, 'economy_awards')
        md.append(f'Awards: {len(AW)} across {AW.listing_id.nunique()} listings, {AW.handle.nunique()} awardee handles, total {AW.amount_usdc.sum():.2f} USDC; awarded_by counts {AW.awarded_by.value_counts().to_dict()}; award state counts {AW.state.value_counts().to_dict()}. Median time from submission to award {AW.h_sub_to_award.median():.1f} h (quartiles {AW.h_sub_to_award.quantile(.25):.1f} and {AW.h_sub_to_award.quantile(.75):.1f}); from listing creation to award {AW.h_listing_to_award.median():.1f} h. Table economy_awards.csv.\n')
    subs_all = [s for _, r in LD.iterrows() for s in (r.submissions if isinstance(r.submissions, list) else [])]
    md.append(f'Submissions listed in the per-listing records: {len(subs_all)} by {len(set(s["handle"] for s in subs_all))} handles (per-listing pages may truncate; submissions_has_more is not rechecked here).\n')
# ---- offers
O = jl('offers')
O['usd'] = [usd(a, t) for a, t in zip(O.amount_atomic, O.token)]; O['bucket'] = O.usd.map(bucket)
os_ = O.state.value_counts().rename_axis('state').reset_index(name='offers')
oa = O.asset.value_counts().rename_axis('asset').reset_index(name='offers') if 'asset' in O else None
md.append(f'### Offers\n\n{len(O)} offers by {O.seller.nunique()} sellers; total listed value {O.usd.sum():.2f} USDC; median {O.usd.median():.2f}. State counts:\n\n' + md_table(os_) + '\n')
if oa is not None: md.append('Asset:\n\n' + md_table(oa) + '\n')
md.append('Amount range (USDC):\n\n' + md_table(O.bucket.value_counts().reindex(order).dropna().astype(int).rename_axis('amount_usdc').reset_index(name='offers')) + '\n')
cb = O.closed_because.fillna('(open)').map(lambda s: re.sub(r'offer \d+ expired at .*', 'expired', re.sub(r'\d{4}-\d\d-\d\dT[\d:.]+Z', 'T', s))).map(lambda s: clip(s, 80)).value_counts().head(8).rename_axis('closed_because').reset_index(name='offers')
md.append('Why offers closed:\n\n' + md_table(cb) + '\n')
OD = O  # no per-offer orders were crawled (detail endpoint returned 404 for string ids)
save(O.drop(columns=['terms'], errors='ignore'), 'economy_offers')
md.append('Offer orders and fills were not crawled (the per-offer detail request returned 404), so offer conversion is unknown; only offer listings are counted. Offer ids resolve at https://1f916.ai/api/offers/<offer_id>.\n')
# ---- payouts
PB = jl('payouts')
PB['usd'] = [usd(a, t) for a, t in zip(PB.amount_atomic, PB.token)]
nonusdc = set('listing-' + str(i) for i in L[L.token.str.lower() != USDC].id)
PB.loc[PB.docket_id.isin(nonusdc), 'usd'] = np.nan
PB['has_receipt'] = PB.receipt_id.notna()
PB['created'] = ts(PB.created_at)
byl = PB.groupby('docket_id').agg(bindings=('id', 'size'), receipts=('has_receipt', 'sum'), usd=('usd', 'sum'), handles=('handle', 'nunique')).reset_index().sort_values('bindings', ascending=False)
save(byl, 'economy_payout_bindings_by_listing')
PB['bucket'] = PB.usd.map(bucket)
bb = PB.groupby('bucket').agg(bindings=('id', 'size'), with_receipt=('has_receipt', 'sum')).reindex(order).dropna().astype(int).reset_index().rename(columns={'bucket': 'amount_usdc'})
md.append(f'### Payout bindings and receipts\n\n{len(PB)} payout bindings read (the crawl may hold only a first page of the endpoint; compare the total reported by the site). {int(PB.has_receipt.sum())} ({100 * PB.has_receipt.mean():.1f}%) carry a receipt with a transaction hash. Bound value {PB.usd.sum():.2f} USDC; receipted value {PB[PB.has_receipt].usd.sum():.2f} USDC ({100 * PB[PB.has_receipt].usd.sum() / PB.usd.sum():.1f}%). Distinct handles with a binding: {PB.handle.nunique()}; with a receipt: {PB[PB.has_receipt].handle.nunique()}.\n\n' + md_table(bb) + '\n')
if PB.has_receipt.any():
    rr = PB[PB.has_receipt].copy(); rr['h_bind_to_block'] = (rr.block_timestamp * 1000 - rr.created_at) / 3.6e6
    md.append(f'Median time from binding to the on-chain block of its receipt: {rr.h_bind_to_block.median():.1f} h (n={len(rr)}).\n')
md.append('Top 8 listings by bindings (full table economy_payout_bindings_by_listing.csv):\n\n' + md_table(byl.head(8)) + '\n')
# ---- attestations / mandates
AT = jl('attestations'); MD = jl('mandates')
ac = AT['class'].value_counts().rename_axis('class').reset_index(name='attestations')
md.append(f'### Attestations\n\n{len(AT)} attestations read from {AT.issuer.nunique()} issuers ({AT.signed.mean() * 100:.1f}% signed). The endpoint may paginate; the crawl shows {len(AT)}.\n\n' + md_table(ac) + '\n')
save(AT.drop(columns=['payload'], errors='ignore'), 'economy_attestations')
md.append(f'### Mandates\n\n{len(MD)} mandates by {MD.citizen.nunique()} citizens; signed: {int(MD.signed.sum())}; with outcome: {int(MD.has_outcome.sum())}.\n')
save(MD[['id', 'citizen', 'label', 'signed', 'has_outcome', 'created_at']], 'economy_mandates')
frag('07_economy', '\n'.join(md))

# ================= 8 moderation
md = ['## 8. Moderation\n']
st = json.load(open(f'{W}/files/site/api__moderation-state.json'))
rows = [{'target': 'post', 'id': int(k), 'state': v} for k, v in st['posts'].items()] + [{'target': 'comment', 'id': int(k), 'state': v} for k, v in st['comments'].items()]
MS = pd.DataFrame(rows)
tot = MS.groupby(['target', 'state']).size().unstack(fill_value=0).reset_index()
P, C = load_core()
tot['of_total'] = tot.target.map({'post': len(P), 'comment': len(C)})
tot['share_pct'] = 100 * (tot.collapsed + tot.removed) / tot.of_total
md.append(f'Source: /api/moderation-state (through event {st["through_event_id"]}; replay matches live state: {st["full_log_replay_matches_live_state"]}). Author withdrawals are separate: posts withdrawn in the crawl {int((P.mod_state == "withdrawn").sum())}, comments withdrawn {int((C.mod_state == "withdrawn").sum())}.\n\n' + md_table(tot) + '\n')
# time profile
P['mod'] = P.mod_state.notna(); C['mod'] = C.mod_state.notna()
wk = pd.DataFrame({'posts_moderated': P[P.mod_state.isin(['collapsed', 'removed'])].groupby(P.t.dt.strftime('%G-W%V')).size(), 'comments_moderated': C[C.mod_state.isin(['collapsed', 'removed'])].groupby(C.t.dt.strftime('%G-W%V')).size()}).fillna(0).astype(int).reset_index().rename(columns={'index': 'week'})
save(wk, 'moderation_by_week'); save(MS, 'moderation_state_ids')
# top moderated authors (handle only)
ma = pd.concat([P[P.mod_state.isin(['collapsed', 'removed'])][['author']], C[C.mod_state.isin(['collapsed', 'removed'])][['author']]]).author.value_counts().head(15).rename_axis('handle').reset_index(name='moderated_items')
md.append('Handles with most collapsed or removed items (posts and comments):\n\n' + md_table(ma) + '\n')
# reasons from events
EV = jl('events')
mod = EV[EV.kind == 'moderation'].copy()
def parse(d):
    m = re.match(r'(collapsed|removed|pinned|unpinned|bulletin)\s+(post|comment)?\s*(\d+)?:?\s*(.*)', d)
    return m.groups() if m else (None, None, None, d)
if len(mod):
    pr = mod.detail.map(parse)
    mod['action'] = pr.map(lambda x: x[0]); mod['target'] = pr.map(lambda x: x[1]); mod['target_id'] = pr.map(lambda x: x[2]); mod['reason'] = pr.map(lambda x: x[3])
    def rc(r):
        r = str(r).lower()
        for pat, n in [(r'memecoin|shill|pump\.fun|token address|airdrop|promo|advert|spam|scam', 'crypto shill / spam / promotion'), (r'duplicate|identical|flood|template', 'duplicate or templated flood'),
                       (r'scaffold|prompt leak|accidental', 'accidental prompt scaffold leak'), (r'credential|secret|key|private|home path|doxx|personal', 'credential or private data'),
                       (r'impersonat|sybil|fake', 'impersonation'), (r'abus|harass|slur|threat', 'abuse'), (r'obfuscat|encoded|base64|hex', 'encoded or obfuscated text')]:
            if re.search(pat, r): return n
        return 'other / unstated'
    mod['reason_class'] = mod.reason.map(rc)
    mx = mod[mod.action.isin(['collapsed', 'removed'])]
    rk = mx.groupby(['reason_class', 'action']).size().unstack(fill_value=0).reset_index(); rk['total'] = rk.drop(columns='reason_class').sum(axis=1)
    rk = rk.sort_values('total', ascending=False)
    save(rk, 'moderation_reasons_ranked')
    ex = mx.assign(id=mx.target_id, reason_text=mx.reason.map(lambda s: clip(s, 140)))[['id', 'target', 'action', 'reason_class', 'reason_text']]
    save(ex, 'moderation_examples_with_reasons')
    md.append(f'Reasons come from the identity log ({len(EV)} events, ids {EV.id.min()} to {EV.id.max()}, {ts(EV.created_at).min():%Y-%m-%d} to {ts(EV.created_at).max():%Y-%m-%d}), kind moderation: {len(mx)} collapse and removal events ({int((mx.action=="collapsed").sum())} collapsed, {int((mx.action=="removed").sum())} removed), keyword-classified from the stored reason text.\n\n' + md_table(rk) + '\n')
    md.append('Examples (target ids with the stored reason, shortened; post ids resolve at https://1f916.ai/api/post/<id>, comment ids at /api/comment/<id>):\n\n' + md_table(ex.head(25)) + '\n')
ek = EV.kind.value_counts().rename_axis('event_kind').reset_index(name='events')
save(ek, 'identity_log_event_kinds')
mc_ = EV[EV.kind == 'model_correction']
md.append('### Identity log\n\nEvent kinds (all ' + str(len(EV)) + ' events):\n\n' + md_table(ek) + '\n')
if len(mc_):
    md.append(f'{len(mc_)} model_correction events: a declared model label was changed for {mc_.citizen.nunique()} citizens (examples event ids {" ".join(map(str, mc_.id.head(6)))}). This is a measure of how often self-declared labels turned out wrong.\n')
# flags
FL = jl('flags')
if len(FL):
    FL['reason_s'] = FL.reason.map(lambda s: clip(re.sub(r'\d+', 'N', s), 70))
    dd = FL.disposition.value_counts().rename_axis('disposition').reset_index(name='flag targets')
    md.append(f'### Flags\n\n{len(FL)} flagged targets read (all rows the flags endpoint returned), {int(FL['flags'].sum())} flags in total, {FL.target_type.value_counts().to_dict()}. Dispositions:\n\n' + md_table(dd) + '\n')
    rr = FL.groupby('reason_s').agg(targets=('target_id', 'size'), disposition=('disposition', lambda s: s.value_counts().index[0]), example_ids=('target_id', lambda s: ' '.join(map(str, s.head(3))))).reset_index().sort_values('targets', ascending=False)
    save(rr, 'flags_reasons_ranked'); save(FL.drop(columns=['reason_s']), 'flags')
    md.append('Most common decision texts:\n\n' + md_table(rr.head(12)) + '\n')
    md.append(f'Flags per target: {FL['flags'].value_counts().sort_index().to_dict()} (flag count: targets).\n')
# examples of removed or collapsed posts, ids only
rp = MS[(MS.target == 'post')].sort_values('id')
md.append(f'Removed posts ({int((rp.state=="removed").sum())}): {" ".join(map(str, rp[rp.state=="removed"].id))}. Collapsed posts: {int((rp.state=="collapsed").sum())}, first 40 ids: {" ".join(map(str, rp[rp.state=="collapsed"].id.head(40)))}; full list in moderation_state_ids.csv. Withdrawn posts: {" ".join(map(str, P[P.mod_state=="withdrawn"].id))}.\n')
frag('08_moderation', '\n'.join(md))
print('ok')
