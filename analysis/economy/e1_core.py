"""Core money tables: listings, awards, settled payments, funders, recipients.
Every figure in USDC unless a column says token. 'committed' = award ledger or declared ceiling; 'paid' = receipt or observed transfer.
Outputs csv/*.csv and numbers.json (key core_*)."""
from common import *

L = rd("listings_detail")
LI = {l["listing_id"]: l for l in L}
PAY = rd("payouts")
USDC_TOKEN = site("api__official.json")["payout_assets"]["accepted"][0]["token_contract"].lower()
TREASURY_HANDLE = site("api__official.json")["maintainer"]["handle"]

# submissions index
subs = []
for l in L:
    for s in l["submissions"]:
        subs.append(dict(listing_id=l["listing_id"], submission_id=s["id"], handle=s["handle"], created_at=s["created_at"],
                         economic_state=s["economic_state"], award_id=s["award_id"], paid=s["paid"], paid_by_third_party=s["paid_by_third_party"],
                         key_bound=(s["payee_status"] or {}).get("key_bound") if isinstance(s["payee_status"], dict) else None))
S = pd.DataFrame(subs)
SUBH = {(r.listing_id, r.submission_id): r.handle for r in S.itertuples()}
SUBT = {(r.listing_id, r.submission_id): r.created_at for r in S.itertuples()}

# awards
aw = []
for l in L:
    for a in l["awards"]:
        aw.append(dict(listing_id=l["listing_id"], award_id=a["award_id"], submission_id=a["submission_id"],
                       handle=SUBH.get((l["listing_id"], a["submission_id"])), funder=l["funder"],
                       amount_usdc=usdc(a["amount_atomic"]) if l["token"].lower() == USDC_TOKEN else None,
                       state=a["state"], awarded_by=a["awarded_by"], settled_by=a["settled_by"], settlement_block=a["settlement_block"],
                       awarded_at=a["awarded_at"], paid_at=a["paid_at"], submission_at=SUBT.get((l["listing_id"], a["submission_id"])),
                       receipt_id=a["receipt_id"], observed_transfer_id=a["observed_transfer_id"]))
A = pd.DataFrame(aw)
A["h_sub_to_award"] = (A.awarded_at - A.submission_at) / 3.6e6
A["h_award_to_paid"] = (A.paid_at - A.awarded_at) / 3.6e6
A["awarded_day"] = A.awarded_at.map(day); A["paid_day"] = A.paid_at.map(day)
save_csv(A, "awards.csv")

# settled payments (receipt or observed transfer). tx hashes and addresses are dropped.
awd = {(r.listing_id, r.receipt_id): r for r in A.itertuples() if pd.notna(r.receipt_id)}
awo = {(r.listing_id, r.observed_transfer_id): r for r in A.itertuples() if pd.notna(r.observed_transfer_id)}
pm = []
for p in PAY:
    if not (p["receipt_id"] or p["observed_transfer_id"]):
        continue
    dk = p["docket_id"]; role = "verifier" if dk.endswith("-verifier") else "worker"
    lid = int(re.search(r"listing-(\d+)", dk).group(1)); l = LI[lid]
    kind = "receipt" if p["receipt_id"] else "observed_transfer"
    paid_ms = p["block_timestamp"] * 1000 if p["block_timestamp"] else None
    if paid_ms is None:
        a = awo.get((lid, p["observed_transfer_id"]))
        paid_ms = a.paid_at if a is not None else None
    pm.append(dict(binding_id=p["id"], listing_id=lid, role=role, handle=p["handle"], funder=l["funder"], kind=kind,
                   amount_usdc=usdc(p["amount_atomic"]) if p["token"].lower() == USDC_TOKEN else None,
                   funding_relationship=p["funding_relationship"], settlement_version=l["settlement_version"],
                   in_award_ledger=bool((lid, p["receipt_id"]) in awd or (lid, p["observed_transfer_id"]) in awo),
                   bound_at=p["created_at"], paid_at=paid_ms, paid_day=day(paid_ms)))
PM = pd.DataFrame(pm)
PM["h_bind_to_paid"] = (PM.paid_at - PM.bound_at) / 3.6e6
save_csv(PM, "settled_payments.csv")

# listings
rows = []
treas = lambda f: f == TREASURY_HANDLE
for l in L:
    lid = l["listing_id"]; tok = "USDC" if l["token"].lower() == USDC_TOKEN else "1F916"
    ls = S[S.listing_id == lid]; la = A[A.listing_id == lid] if len(A) else A; lp = PM[(PM.listing_id == lid) & (PM.role == "worker")]
    posted = usdc(l["amount_atomic"]) if tok == "USDC" else None
    v2 = l["settlement_version"] >= 2
    ceiling = (posted * l["max_awards"]) if (tok == "USDC" and v2 and l["max_awards"]) else posted
    first_sub = ls.created_at.min() if len(ls) else None
    first_aw = la.awarded_at.min() if len(la) else None
    first_paid = lp.paid_at.min() if len(lp) and lp.paid_at.notna().any() else None
    rows.append(dict(listing_id=lid, funder=l["funder"], treasury_funded=treas(l["funder"]), title=safe_text(l["title"]), asset=tok,
                     price_usdc=posted, max_awards=l["max_awards"], ceiling_usdc=ceiling, settlement_version=l["settlement_version"],
                     funding_mode=l["funding_mode"], state=l["state"], created_at=l["created_at"], created_day=day(l["created_at"]),
                     expiry_at=l["expiry"] * 1000, withdrawn_at=l["withdrawn_at"], submissions=len(ls), distinct_submitters=ls.handle.nunique(),
                     bindings=l["bindings_total"], awards=len(la), awards_paid=int((la.state == "paid").sum()) if len(la) else 0,
                     committed_usdc=(la.amount_usdc.sum() if len(la) and tok == "USDC" else 0.0),
                     paid_worker_payments=len(lp), paid_usdc=(lp.amount_usdc.sum() if tok == "USDC" else 0.0),
                     first_submission_at=first_sub, first_award_at=first_aw, first_paid_at=first_paid,
                     h_to_first_submission=(first_sub - l["created_at"]) / 3.6e6 if first_sub else None,
                     h_to_first_award=(first_aw - l["created_at"]) / 3.6e6 if first_aw else None,
                     h_to_first_paid=(first_paid - l["created_at"]) / 3.6e6 if first_paid else None,
                     verifier_price_usdc=usdc(l["verifier_price_atomic"]), max_verifiers=l["max_verifiers"],
                     funds_seen_usdc=usdc(l["funds_seen_atomic"]) if tok == "USDC" else None,
                     condition_chars=len(l["condition"] or ""), post_id=l["post_id"]))
LT = pd.DataFrame(rows)
LT["any_payment"] = LT.paid_worker_payments > 0
save_csv(LT, "listings_flat.csv")

# funders
usd = LT[LT.asset == "USDC"]
f = usd.groupby("funder").agg(listings=("listing_id", "count"), posted_price_sum_usdc=("price_usdc", "sum"), ceiling_usdc=("ceiling_usdc", "sum"),
                              awards=("awards", "sum"), committed_usdc=("committed_usdc", "sum"), paid_usdc=("paid_usdc", "sum"),
                              listings_with_payment=("any_payment", "sum"), submissions=("submissions", "sum")).reset_index()
f["verifier_paid_usdc"] = f.funder.map(PM[PM.role == "verifier"].groupby("funder").amount_usdc.sum()).fillna(0.0)
f["total_paid_usdc"] = f.paid_usdc + f.verifier_paid_usdc
tok_l = LT[LT.asset == "1F916"].groupby("funder").listing_id.count()
f["token_listings"] = f.funder.map(tok_l).fillna(0).astype(int)
for fu, n in tok_l.items():
    if fu not in set(f.funder): f.loc[len(f)] = dict(funder=fu, listings=0, token_listings=n)
od = pd.DataFrame()
f["overdue_unpaid_usdc"] = f.funder.map(A[A.state == "overdue_unpaid"].groupby("funder").amount_usdc.sum()).fillna(0.0)
f["unpaid_awarded_usdc"] = f.funder.map(A[A.state.isin(["overdue_unpaid", "payable"])].groupby("funder").amount_usdc.sum()).fillna(0.0)
f["is_treasury"] = f.funder == TREASURY_HANDLE
f = f.sort_values(["total_paid_usdc", "ceiling_usdc"], ascending=False)
save_csv(f, "funders.csv")

# recipients
R = PM.groupby("handle").agg(payments=("binding_id", "count"), paid_usdc=("amount_usdc", "sum"), listings=("listing_id", "nunique"),
                             worker_payments=("role", lambda x: (x == "worker").sum()), verifier_payments=("role", lambda x: (x == "verifier").sum()),
                             first_paid_at=("paid_at", "min")).reset_index().sort_values("paid_usdc", ascending=False)
R["committed_award_usdc"] = R.handle.map(A.groupby("handle").amount_usdc.sum()).fillna(0.0)
R["funds_listings"] = R.handle.isin(set(LT.funder))
save_csv(R, "recipients.csv")

# distribution and concentration
amt = A.amount_usdc.dropna()
pay_amt = PM.amount_usdc.dropna()
def dist(x):
    x = np.asarray(x, float)
    return dict(n=int(len(x)), total=float(x.sum()), min=float(x.min()), median=float(np.median(x)), mean=float(x.mean()), max=float(x.max()), **deciles(x))
bind = pd.DataFrame(PAY)
bind["amount"] = bind.apply(lambda p: usdc(p["amount_atomic"]) if (p["token"].lower() == USDC_TOKEN and int(p["amount_atomic"]) < 10**9 * USDC_ATOMIC) else None, axis=1)
agree = pd.Series([(b["asset_agreement"] or {}).get("state") for l in L for b in l["bindings"]]).value_counts().to_dict()
bind["settled"] = bind.receipt_id.notna() | bind.observed_transfer_id.notna()
bind["role"] = np.where(bind.docket_id.str.endswith("-verifier"), "verifier", "worker")
bw = bind[bind.role == "worker"]
N = {}
N["listings_total"] = len(LT); N["listings_usdc"] = int((LT.asset == "USDC").sum()); N["listings_token"] = int((LT.asset == "1F916").sum())
N["funders_total"] = int(LT.funder.nunique()); N["funders_usdc"] = int(usd.funder.nunique())
N["posted_price_sum_usdc"] = float(usd.price_usdc.sum()); N["posted_ceiling_sum_usdc"] = float(usd.ceiling_usdc.sum())
N["posted_price_median_usdc"] = float(usd.price_usdc.median()); N["posted_price_max_usdc"] = float(usd.price_usdc.max())
N["awards_n"] = len(A); N["awards_paid_n"] = int((A.state == "paid").sum()); N["awards_by_state"] = A.state.value_counts().to_dict()
N["awards_committed_usdc"] = float(A.amount_usdc.sum()); N["awards_paid_usdc"] = float(A[A.state == "paid"].amount_usdc.sum())
N["awards_unpaid_usdc"] = float(A[A.state != "paid"].amount_usdc.sum())
N["award_amount_dist"] = dist(amt); N["award_distinct_listings"] = int(A.listing_id.nunique()); N["award_distinct_handles"] = int(A.handle.nunique())
N["payments_settled_n"] = len(PM); N["payments_settled_usdc"] = float(PM.amount_usdc.sum())
N["payments_by_kind"] = PM.groupby("kind").agg(n=("binding_id", "count"), usdc=("amount_usdc", "sum")).round(3).to_dict("index")
N["payments_by_role"] = PM.groupby("role").agg(n=("binding_id", "count"), usdc=("amount_usdc", "sum")).round(3).to_dict("index")
N["payments_in_award_ledger_usdc"] = float(PM[PM.in_award_ledger].amount_usdc.sum()); N["payments_outside_ledger_usdc"] = float(PM[~PM.in_award_ledger].amount_usdc.sum())
N["payments_outside_ledger_n"] = int((~PM.in_award_ledger).sum())
N["payment_amount_dist"] = dist(pay_amt)
N["receipts_n"] = int((PM.kind == "receipt").sum()); N["receipts_usdc"] = float(PM[PM.kind == "receipt"].amount_usdc.sum())
N["observed_n"] = int((PM.kind == "observed_transfer").sum()); N["observed_usdc"] = float(PM[PM.kind == "observed_transfer"].amount_usdc.sum())
N["treasury_funded_paid_usdc"] = float(PM[PM.funder == TREASURY_HANDLE].amount_usdc.sum()); N["treasury_funded_paid_n"] = int((PM.funder == TREASURY_HANDLE).sum())
N["external_paid_usdc"] = float(PM[PM.funder != TREASURY_HANDLE].amount_usdc.sum()); N["external_paid_n"] = int((PM.funder != TREASURY_HANDLE).sum())
N["recipients_n"] = len(R); N["recipients_top3_share"] = topk_share(R.paid_usdc); N["recipients_gini"] = gini(R.paid_usdc)
N["recipients_top3"] = R.head(3)[["handle", "paid_usdc", "payments"]].to_dict("records")
N["recipients_median_usdc"] = float(R.paid_usdc.median()); N["recipients_mean_usdc"] = float(R.paid_usdc.mean())
N["recipients_multi_payment"] = int((R.payments > 1).sum())
fp = f[f.listings > 0]
N["funders_paying_n"] = int((fp.total_paid_usdc > 0).sum())
N["funders_paid_top3_share"] = topk_share(fp.total_paid_usdc); N["funders_paid_gini_all_usdc_funders"] = gini(fp.total_paid_usdc)
N["funders_posted_top3_share"] = topk_share(fp.ceiling_usdc); N["funders_posted_gini"] = gini(fp.ceiling_usdc)
N["funders_listings_top3_share"] = topk_share(fp.listings); N["funders_listings_gini"] = gini(fp.listings)
N["funders_top3_paid"] = f.head(3)[["funder", "total_paid_usdc"]].to_dict("records")
# bindings
N["bindings_n"] = len(bind); N["bindings_worker_n"] = len(bw); N["bindings_verifier_n"] = int((bind.role == "verifier").sum())
N["bindings_settled_n"] = int(bind.settled.sum()); N["bindings_receipt_n"] = int(bind.receipt_id.notna().sum()); N["bindings_observed_n"] = int(bind.observed_transfer_id.notna().sum())
N["bindings_conversion_pct"] = float(100 * bind.settled.mean()); N["bindings_receipt_conversion_pct"] = float(100 * bind.receipt_id.notna().mean())
N["bindings_handles"] = int(bind.handle.nunique()); N["bindings_handles_settled"] = int(bind[bind.settled].handle.nunique())
N["asset_agreement_states"] = agree
N["bound_value_usdc_all"] = float(bind.amount.sum())
N["rail_totals_lapsed_bindings"] = site("api__rail.json")["totals"]["lapsed_bindings"]
# shares of listings
N["listings_zero_awards_pct_all"] = float(100 * (LT.awards == 0).mean()); N["listings_zero_awards_n"] = int((LT.awards == 0).sum())
v2 = LT[LT.settlement_version >= 2]
N["v2_listings"] = len(v2); N["v2_zero_awards_n"] = int((v2.awards == 0).sum()); N["v2_zero_awards_pct"] = float(100 * (v2.awards == 0).mean())
N["listings_no_payment_n"] = int((~LT.any_payment).sum()); N["listings_no_payment_pct"] = float(100 * (~LT.any_payment).mean())
N["listings_with_submission_n"] = int((LT.submissions > 0).sum()); N["listings_with_payment_n"] = int(LT.any_payment.sum())
N["listings_with_award_n"] = int((LT.awards > 0).sum())
N["state_counts"] = LT.state.value_counts().to_dict()
N["withdrawn_n"] = int(LT.withdrawn_at.notna().sum())
now = CRAWL_END.timestamp() * 1000
N["expired_n"] = int(((LT.expiry_at < now) & LT.withdrawn_at.isna()).sum()); N["open_n"] = int(((LT.expiry_at >= now) & LT.withdrawn_at.isna()).sum())
N["submissions_n"] = len(S); N["submitters_n"] = int(S.handle.nunique())
N["submissions_by_state"] = S.economic_state.value_counts().to_dict()
N["submissions_unpaid_n"] = int((S.economic_state != "paid").sum())
# unpaid with a binding on that listing
bk = set(zip(bw.docket_id.str.replace("listing-", "").astype(int), bw.handle))
S["has_binding"] = [(r.listing_id, r.handle) in bk for r in S.itertuples()]
N["submissions_unpaid_with_binding_n"] = int(((S.economic_state != "paid") & S.has_binding).sum())
N["submissions_unpaid_no_key_n"] = int(((S.economic_state != "paid") & (S.key_bound == False)).sum())
save_csv(S.drop(columns=[]), "submissions_flat.csv")
for lab, col in [("h_to_first_submission", "h_to_first_submission"), ("h_to_first_award", "h_to_first_award"), ("h_to_first_paid", "h_to_first_paid")]:
    x = LT[col].dropna(); N["listing_" + lab] = dict(n=int(len(x)), median=float(x.median()), mean=float(x.mean()), p25=float(x.quantile(.25)), p75=float(x.quantile(.75)), max=float(x.max()), min=float(x.min()))
for lab, x in [("sub_to_award", A.h_sub_to_award), ("award_to_paid", A.h_award_to_paid), ("bind_to_paid_receipts", PM[PM.kind == "receipt"].h_bind_to_paid)]:
    x = x.dropna(); N[lab + "_hours"] = dict(n=int(len(x)), median=float(x.median()), mean=float(x.mean()), p25=float(x.quantile(.25)), p75=float(x.quantile(.75)), max=float(x.max()), min=float(x.min()))
# earn and fund
earn = set(PM.handle); fund = set(LT.funder)
both = sorted(earn & fund); N["earn_and_fund_handles"] = both; N["earn_and_fund_n"] = len(both)
# earn and fund where funder paid someone: (paid out as funder)
paidout = set(PM.funder)
N["earn_and_pay_out_handles"] = sorted(earn & paidout)
# funder -> payee pair flows and loops
pairs = PM.groupby(["funder", "handle"]).agg(payments=("binding_id", "count"), usdc=("amount_usdc", "sum")).reset_index().sort_values("usdc", ascending=False)
save_csv(pairs, "funder_to_recipient_pairs.csv")
fl = {(r.funder, r.handle) for r in pairs.itertuples()}
N["pair_loops_2cycle"] = sorted({tuple(sorted(p)) for p in fl if (p[1], p[0]) in fl and p[0] != p[1]})
N["self_pay"] = sorted({p for p in fl if p[0] == p[1]})
# 3-cycle
import itertools
adj = {}
for a, b in fl: adj.setdefault(a, set()).add(b)
cyc3 = set()
for a in adj:
    for b in adj.get(a, ()):
        for c in adj.get(b, ()):
            if a in adj.get(c, ()) and len({a, b, c}) == 3: cyc3.add(tuple(sorted((a, b, c))))
N["pair_loops_3cycle"] = sorted(cyc3)
save_numbers({"core": N})
print(json.dumps(N, indent=1, default=str)[:7000])
