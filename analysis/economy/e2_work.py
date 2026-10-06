"""What is asked for and sold: listing and offer categories, offer prices, orders, conversion, verifiers."""
from common import *
from categories import *
clean_dash = lambda x: re.sub(r"\s+", " ", x.replace("\u2014", " - ").replace("\u2013", " - "))

LT = pd.read_csv(CSV / "listings_flat.csv"); PM = pd.read_csv(CSV / "settled_payments.csv")
LT["category"] = [classify(t, LISTING_RULES, override=LISTING_OVERRIDE, key=i) for t, i in zip(LT.title, LT.listing_id)]
save_csv(LT, "listings_flat.csv")
N = {}

def ex(g, n=3):
    return "; ".join(f"{r.listing_id}: {clean_dash(r.title[:55])}" for r in g.head(n).itertuples())
rows = []
for c, g in LT.groupby("category"):
    u = g[g.asset == "USDC"]
    rows.append(dict(category=c, listings=len(g), price_median_usdc=u.price_usdc.median(), price_min_usdc=u.price_usdc.min(), price_max_usdc=u.price_usdc.max(),
                     submissions=int(g.submissions.sum()), with_award=int((g.awards > 0).sum()), with_payment=int(g.any_payment.sum()), paid_usdc=float(g.paid_usdc.sum()),
                     examples=ex(g)))
lc = pd.DataFrame(rows).sort_values("listings", ascending=False); save_csv(lc, "listing_categories.csv")

# offers
O = rd("offers_detail"); OF = []
for o in O:
    OF.append(dict(offer_id=o["offer_id"], seller=o["seller"], title=safe_text(o["title"]), price_usdc=usdc(o["amount_atomic"]), asset=o["asset"],
                   delivery_hours=o["delivery_window_seconds"] / 3600, created_at=o["created_at"], created_day=day(o["created_at"]), state=o["state"],
                   closed_because=safe_text((o["closed_because"] or "")[:160]), orders=o["orders_total"], post_id=o["post_id"],
                   pay_after_delivery=bool(re.search(r"pay after|after delivery|after accept|pay only if|you don't pay|no upfront", o["terms"] or "", re.I)),
                   category=classify(o["title"], OFFER_RULES, override=OFFER_OVERRIDE, key=o["offer_id"])))
OFD = pd.DataFrame(OF); save_csv(OFD, "offers_flat.csv")
N["offers_n"] = len(OFD); N["offer_sellers"] = int(OFD.seller.nunique()); N["offers_open"] = int((OFD.state == "open").sum()); N["offers_closed"] = int((OFD.state == "closed").sum())
N["offers_withdrawn_n"] = int(OFD.closed_because.str.contains("withdrawn").sum()); N["offers_expired_n"] = int(OFD.closed_because.str.contains("expired").sum())
x = OFD.price_usdc
N["offer_price"] = dict(n=int(len(x)), min=float(x.min()), median=float(x.median()), mean=float(x.mean()), max=float(x.max()), total=float(x.sum()), **deciles(x))
N["offer_price_share_le3_pct"] = float(100 * (x <= 3).mean()); N["offer_price_share_ge10_pct"] = float(100 * (x >= 10).mean())
bins = [0, 0.5, 1, 2, 3, 5, 10, 25, 1000]; labs = ["<=0.5", "0.5-1", "1-2", "2-3", "3-5", "5-10", "10-25", ">25"]
OFD["band"] = pd.cut(OFD.price_usdc, bins=[-1, 0.5, 1, 2, 3, 5, 10, 25, 1000], labels=labs, right=True)
hb = OFD.groupby("band", observed=False).size().rename("offers").reset_index(); hb["share_pct"] = 100 * hb.offers / hb.offers.sum()
hb2 = OFD.groupby("price_usdc").size().rename("offers").reset_index()
save_csv(hb, "offers_price_bands.csv"); save_csv(hb2, "offers_price_exact.csv")
N["offer_price_mode"] = float(OFD.price_usdc.mode().iloc[0]); N["offer_price_mode_n"] = int((OFD.price_usdc == OFD.price_usdc.mode().iloc[0]).sum())
N["offers_pay_after_delivery_n"] = int(OFD.pay_after_delivery.sum())
N["offers_per_seller_max"] = int(OFD.groupby("seller").size().max()); N["offers_per_seller_top"] = OFD.groupby("seller").size().sort_values(ascending=False).head(5).to_dict()
oc = OFD.groupby("category").agg(offers=("offer_id", "count"), price_median_usdc=("price_usdc", "median"), price_min_usdc=("price_usdc", "min"), price_max_usdc=("price_usdc", "max"),
                                 open_now=("state", lambda s: (s == "open").sum()), orders=("orders", "sum"), sellers=("seller", "nunique")).reset_index()
oc["examples"] = oc.category.map(lambda c: "; ".join(f"{r.offer_id}: {clean_dash(r.title[:50])}" for r in OFD[OFD.category == c].head(3).itertuples()))
oc = oc.sort_values("offers", ascending=False); save_csv(oc, "offer_categories.csv")
# by day, repricing
wk = OFD.groupby("created_day").agg(offers=("offer_id", "count"), price_median=("price_usdc", "median")).reset_index(); save_csv(wk, "offers_by_day.csv")
# repricing statements
N["offers_reprice_text"] = OFD[OFD.closed_because.str.contains("Repric|improved terms and pricing", case=False)].offer_id.tolist()

# [FOR HIRE N USDC] post series
P = pd.DataFrame(rd("posts"))
fh = P[P.title.str.contains(r"\[FOR HIRE", na=False)].copy()
fh["price"] = fh.title.str.extract(r"\[FOR HIRE ([\d.]+) USDC\]")[0].astype(float)
fh["offer_id_in_title"] = fh.title.str.extract(r"Offer (\d+)")[0]
fh["day"] = fh.created_at.map(day)
N["for_hire_posts_n"] = len(fh); N["for_hire_price"] = dict(min=float(fh.price.min()), median=float(fh.price.median()), max=float(fh.price.max()), mean=float(fh.price.mean()))
N["for_hire_authors"] = int(fh.author.nunique()); N["for_hire_first_day"] = fh.day.min(); N["for_hire_last_day"] = fh.day.max()
N["for_hire_comments_total"] = int(fh.comments_total.fillna(0).sum()); N["for_hire_comments_median"] = float(fh.comments_total.fillna(0).median())
_m = fh.dropna(subset=["offer_id_in_title"]).assign(oid=lambda d: d.offer_id_in_title.astype(int)).merge(OFD[["offer_id", "price_usdc"]], left_on="oid", right_on="offer_id")
N["for_hire_matched_to_offer_n"] = int(len(_m)); N["for_hire_title_price_match_offer_n"] = int(((_m.price - _m.price_usdc).abs() < 1e-9).sum())
N["for_hire_with_offer_id_n"] = int(fh.offer_id_in_title.notna().sum())
save_csv(fh[["id", "author", "day", "price", "offer_id_in_title", "comments_total", "votes"]].rename(columns={"id": "post_id"}), "for_hire_posts.csv")
# bounty series
bt = P[P.title.str.contains(r"\[BOUNTY", na=False)].copy(); bt["price"] = bt.title.str.extract(r"\[BOUNTY ([\d.]+) USDC\]")[0].astype(float)
N["bounty_posts_n"] = len(bt); N["bounty_post_price"] = dict(min=float(bt.price.min()), median=float(bt.price.median()), max=float(bt.price.max())) if len(bt) else None

# orders
ords = []
for o in O:
    for r in o["orders"]:
        li = int(r["listing_id"]); lr = LT[LT.listing_id == li].iloc[0]
        ords.append(dict(order_id=r["id"], offer_id=o["offer_id"], seller=o["seller"], buyer=r["buyer"], listing_id=li, created_at=r["created_at"], created_day=day(r["created_at"]),
                         price_usdc=usdc(o["amount_atomic"]), listing_state=lr.state, submissions=int(lr.submissions), awards=int(lr.awards), paid_usdc=float(lr.paid_usdc),
                         h_offer_to_order=(r["created_at"] - o["created_at"]) / 3.6e6))
OR = pd.DataFrame(ords); save_csv(OR, "orders.csv")
N["orders_n"] = len(OR); N["orders_buyers"] = OR.buyer.value_counts().to_dict(); N["orders_sellers"] = int(OR.seller.nunique()); N["offers_with_order_n"] = int(OR.offer_id.nunique())
N["orders_total_field_sum"] = int(OFD.orders.sum()); N["orders_paid_n"] = int((OR.paid_usdc > 0).sum()); N["orders_paid_usdc"] = float(OR.paid_usdc.sum())
N["orders_price_usdc_sum"] = float(OR.price_usdc.sum()); N["orders_h_offer_to_order_median"] = float(OR.h_offer_to_order.median())
N["orders_buyers_treasury_n"] = int((OR.buyer == "1f916-agent").sum())
N["orders_listings_funder_is_buyer_check"] = bool((LT.set_index("listing_id").loc[OR.listing_id].funder.values == OR.buyer.values).all())
N["offers_with_order_pct"] = float(100 * N["offers_with_order_n"] / len(OFD))
N["offer_conversion"] = dict(offers=len(OFD), offers_with_order=N["offers_with_order_n"], listings_minted=len(OR), minted_with_submission=int((OR.submissions > 0).sum()), minted_with_payment=int((OR.paid_usdc > 0).sum()))
# sellers also with payments (any listing)
paid_handles = set(PM.handle); N["sellers_paid_any_n"] = int(OFD[OFD.seller.isin(paid_handles)].seller.nunique())
N["sellers_paid_any"] = sorted(OFD[OFD.seller.isin(paid_handles)].seller.unique())

# verifiers: priced listings, verifier bindings, payments, PASS/FAIL comments on listing threads
vl = LT[(LT.max_verifiers > 0) | LT.verifier_price_usdc.notna()]
N["listings_with_verifier_price"] = int(vl.listing_id.nunique()); N["listings_verifier_ids"] = vl.listing_id.tolist()
N["verifier_payments"] = PM[PM.role == "verifier"][["listing_id", "handle", "amount_usdc", "kind"]].to_dict("records")
Ld = rd("listings_detail")
N["verdicts_registry_total"] = int(sum(len(l["verdicts"]) for l in Ld)); N["settlement_modes"] = pd.Series([l["settlement_mode"] for l in Ld]).fillna("none (v1)").value_counts().to_dict()
N["awards_by_requester"] = int(sum(1 for l in Ld for a in l["awards"] if a["awarded_by"] == "requester")); N["awards_by_verifier"] = int(sum(1 for l in Ld for a in l["awards"] if a["awarded_by"] == "verifier"))
C = pd.DataFrame(rd("comments"))
tp = set(LT.post_id.dropna().astype(int)); tid = dict(zip(LT.post_id.astype(int), LT.listing_id))
ct = C[C.post_id.isin(tp) & C.body.notna()].copy()
ct["verdict"] = ct.body.str.extract(r"\b(PASS|FAIL)\b", expand=False)
vv = ct.dropna(subset=["verdict"]).copy(); vv["listing_id"] = vv.post_id.map(tid)
N["thread_comments_n"] = len(ct); N["thread_verdict_comments_n"] = len(vv); N["thread_verdict_counts"] = vv.verdict.value_counts().to_dict()
N["thread_verdict_authors_n"] = int(vv.author.nunique()); N["thread_verdict_listings_n"] = int(vv.listing_id.nunique())
vt = vv.groupby("author").agg(comments=("id", "count"), pass_=("verdict", lambda s: (s == "PASS").sum()), fail=("verdict", lambda s: (s == "FAIL").sum()), listings=("listing_id", "nunique")).reset_index().sort_values("comments", ascending=False)
vt = vt.rename(columns={"pass_": "pass"}); save_csv(vt, "verifier_handles_thread_verdicts.csv"); N["thread_verdict_top"] = vt.head(8).to_dict("records")
vv["excerpt"] = vv.body.map(lambda s: safe_text(s)[:160].replace("\n", " "))
save_csv(vv[["id", "post_id", "listing_id", "author", "verdict", "created_at", "excerpt"]].rename(columns={"id": "comment_id"}), "thread_verdict_comments.csv")
fund_threads = ct.groupby("post_id").size()
N["thread_comments_per_listing_median"] = float(fund_threads.reindex(list(tp)).fillna(0).median())
save_numbers({"work": N}); print(json.dumps(N, indent=1, default=str)[:6500]); print(lc.to_string()); print(oc.to_string())
