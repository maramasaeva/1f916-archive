"""Daily timeline of the economy and rule-change dates."""
from common import *
LT = pd.read_csv(CSV / "listings_flat.csv"); A = pd.read_csv(CSV / "awards.csv"); PM = pd.read_csv(CSV / "settled_payments.csv")
S = pd.read_csv(CSV / "submissions_flat.csv"); OFD = pd.read_csv(CSV / "offers_flat.csv"); OR = pd.read_csv(CSV / "orders.csv")
PAY = rd("payouts"); EV = rd("events")
days = pd.date_range("2026-08-05", "2026-10-05", freq="D").strftime("%Y-%m-%d")
T = pd.DataFrame(index=days)
def cnt(series): return series.dropna().value_counts()
T["listings"] = cnt(LT.created_day)
T["listing_posted_usdc"] = LT[LT.asset == "USDC"].groupby("created_day").price_usdc.sum()
T["listing_ceiling_usdc"] = LT[LT.asset == "USDC"].groupby("created_day").ceiling_usdc.sum()
T["submissions"] = cnt(S.created_at.map(day))
T["bindings"] = cnt(pd.Series([day(p["created_at"]) for p in PAY]))
T["awards"] = cnt(A.awarded_day)
T["awards_usdc"] = A.groupby("awarded_day").amount_usdc.sum()
T["payments"] = cnt(PM.paid_day)
T["payments_usdc"] = PM.groupby("paid_day").amount_usdc.sum()
T["offers"] = cnt(OFD.created_day)
T["orders"] = cnt(OR.created_day)
T["listing_withdrawals"] = cnt(pd.Series([day(e["created_at"]) for e in EV if e["kind"] == "listing-withdrawn"]))
T["payout_wallet_proofs"] = cnt(pd.Series([day(e["created_at"]) for e in EV if e["kind"] == "payout-wallet"]))
T = T.fillna(0); T.index.name = "day"
for c in ["listings", "submissions", "bindings", "awards", "payments", "offers", "orders", "listing_withdrawals", "payout_wallet_proofs"]: T[c] = T[c].astype(int)
for c in ["listing_ceiling_usdc", "awards_usdc", "payments_usdc"]:
    T["cum_" + c] = T[c].cumsum()
T["cum_listing_ceiling_usdc"] = T.listing_ceiling_usdc.cumsum()
T = T.reset_index(); save_csv(T, "timeline_by_day.csv")

# first-seen dates of rail features (from first event of the kind or first listing with the field)
first = {}
for k in ["listing", "listing-submission", "payout-binding", "payout-receipt", "payout-wallet", "binding-verified", "listing-award", "listing-award-transition", "offer", "grant", "grant-proposal", "listing-withdrawn", "binding-lapsed"]:
    ev = [e for e in EV if e["kind"] == k]
    first[k] = dict(first_event_utc=pd.Timestamp(min(e["created_at"] for e in ev), unit="ms").strftime("%Y-%m-%d %H:%M"), n=len(ev))
L = rd("listings_detail")
fv = {}
for l in L:
    key = f"settlement_version {l['settlement_version']}"; fv[key] = min(fv.get(key, 10**15), l["created_at"])
    if l["funding_mode"]: fv[f"funding_mode {l['funding_mode']}"] = min(fv.get(f"funding_mode {l['funding_mode']}", 10**15), l["created_at"])
    if l["token"].lower() != site("api__official.json")["payout_assets"]["accepted"][0]["token_contract"].lower():
        fv["listing priced in 1F916"] = min(fv.get("listing priced in 1F916", 10**15), l["created_at"])
    if l["verifier_price_atomic"]: fv["verifier price set"] = min(fv.get("verifier price set", 10**15), l["created_at"])
    if l["funder_address"]: fv["named funder wallet"] = min(fv.get("named funder wallet", 10**15), l["created_at"])
    if (l["economics"] or {}).get("max_awards") and l["max_awards"] and l["max_awards"] > 1: fv["max_awards > 1"] = min(fv.get("max_awards > 1", 10**15), l["created_at"])
obs = [a for l in L for a in l["awards"] if a["settled_by"] == "observed_transfer"]
fv["first award settled by observed transfer"] = min(a["paid_at"] for a in obs)
fv["first award"] = min(a["awarded_at"] for l in L for a in l["awards"])
rules = [
    ("2026-08-05", "forum opens (site statement, human__economy.txt)", "human__economy.txt"),
    ("2026-08-06", "treasury ledger starts; first patron payments over x402", "treasury.json entries"),
    ("2026-08-16", "first listings (ids 1 to 5); v1 rail records bindings and receipts only", "listings_detail created_at"),
    ("2026-08-21", "treasury page corrected: tax-token inflow had been booked as patron income", "treasury.json recognition.tokens"),
    ("2026-08-25", "1F916 contract recognized as official token", "api__official.json official_token.recognized_at"),
    ("2026-09-01", "settlement v2 (awards ledger) and 1F916-priced listings allowed", "api__official.json payout_assets; listing 20 condition"),
    ("2026-09-02", "last treasury ledger row (id 19); first award receipts settle awards", "treasury.json entries; events 6039"),
    ("2026-09-03", "payout-wallet proofs first filed (prove an address once)", "events kind payout-wallet"),
    ("2026-09-07", "rail page splits paid figures into ledger and receipted; adds treasury_funded vs external", "api__rail.json demand_note"),
    ("2026-09-17", "observed on-chain transfer from the funder wallet settles an award without a receipt", "api__rail.json settlement_note"),
    ("2026-09-18", "offers (sell side) introduced; offers rules_version 2026-09-18.1", "api__offers__guide.json rules_version, changed_at"),
    ("2026-09-21", "listings guide rules_version 2026-09-21.1 (changed_at 2026-09-21T20:30Z)", "api__listings__guide.json rules_version, changed_at"),
]
for k, v in sorted(fv.items(), key=lambda kv: kv[1]):
    first[k] = dict(first_event_utc=pd.Timestamp(v, unit="ms").strftime("%Y-%m-%d %H:%M"), n=None)
json.dump(first, open(CSV / "feature_first_seen.json", "w"), indent=1)
R = pd.DataFrame(rules, columns=["date_utc", "change", "source"])

# effect windows: 7 days before and after each rule date, per-day means
def win(date, col, w=7):
    d = pd.Timestamp(date); t = T.assign(d=pd.to_datetime(T.day))
    pre = t[(t.d < d) & (t.d >= d - pd.Timedelta(days=w))][col].mean(); post = t[(t.d >= d) & (t.d < d + pd.Timedelta(days=w))][col].mean()
    return pre, post
eff = []
for date, ch, src in rules:
    if date < "2026-08-12": continue
    for col in ["listings", "submissions", "bindings", "awards", "payments", "offers"]:
        pre, post = win(date, col); eff.append(dict(date_utc=date, change=ch, metric=col, mean_per_day_7d_before=round(pre, 2), mean_per_day_7d_after=round(post, 2)))
EF = pd.DataFrame(eff); save_csv(EF, "rule_change_effects.csv"); save_csv(R, "rule_change_dates.csv")
N = {"first_seen": first,
     "peak_listing_day": T.loc[T.listings.idxmax(), ["day", "listings"]].tolist(), "peak_submission_day": T.loc[T.submissions.idxmax(), ["day", "submissions"]].tolist(),
     "peak_payment_day": T.loc[T.payments.idxmax(), ["day", "payments"]].tolist(), "peak_offer_day": T.loc[T.offers.idxmax(), ["day", "offers"]].tolist(),
     "listings_by_week": T.assign(w=pd.to_datetime(T.day).dt.to_period("W-SUN").astype(str)).groupby("w")[["listings", "submissions", "bindings", "awards", "payments", "offers", "orders"]].sum().to_dict("index"),
     "days_with_payment": int((T.payments > 0).sum()), "days_with_award": int((T.awards > 0).sum())}
save_numbers({"timeline": N}); print(T.to_string()); print(json.dumps(first, indent=0)); print(EF.to_string())
