"""Assemble REPORT.md from numbers.json and csv/*.csv. All figures come from the other scripts; run them first (see README.md)."""
from common import *
from scipy import stats
N = load_numbers(); C_ = N["core"]; W = N["work"]; TM = N["timeline"]; TR = N["treasury"]; TK = N["talk"]; WL = N["wallet_links"]
rd_csv = lambda n: pd.read_csv(CSV / n)
LT = rd_csv("listings_flat.csv"); A = rd_csv("awards.csv"); PM = rd_csv("settled_payments.csv"); FU = rd_csv("funders.csv"); R = rd_csv("recipients.csv")
OFD = rd_csv("offers_flat.csv"); OR = rd_csv("orders.csv"); LC = rd_csv("listing_categories.csv"); OC = rd_csv("offer_categories.csv"); MI = rd_csv("money_in_sources.csv")
TL = rd_csv("treasury_ledger.csv"); TH = rd_csv("treasury_holdings_by_tier.csv"); TT = rd_csv("talk_theme_counts.csv"); TP = rd_csv("traced_posts.csv"); EX = rd_csv("talk_examples_40.csv")
EF = rd_csv("earn_and_fund_handles.csv"); RU = rd_csv("rule_change_dates.csv"); EFF = rd_csv("rule_change_effects.csv"); TLD = rd_csv("timeline_by_day.csv"); VT = rd_csv("verifier_handles_thread_verdicts.csv")
FIGS = json.load(open(OUT / "figures.json")); IDX = {f["file"]: f["fetched_at"] for f in site("_index.json")["files"]}
EV = rd("events")

def f2(x): return f"{x:,.2f}"
def md(df, cols=None, heads=None, fmt=None):
    df = df.copy(); cols = cols or list(df.columns); heads = heads or cols; fmt = fmt or {}
    out = ["| " + " | ".join(heads) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if c in fmt: v = fmt[c](v)
            elif isinstance(v, float): v = "" if pd.isna(v) else (f"{v:,.2f}")
            cells.append("" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).replace("|", "/").replace("\n", " "))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)
def clean(s): return str(s).replace("—", " - ").replace("–", " - ").replace("→", " to ")

# extra numbers
u = LT[LT.asset == "USDC"]; rho = stats.spearmanr(u.price_usdc, u.submissions)
fm = LT.groupby(LT.funding_mode.fillna("none (v1)")).agg(listings=("listing_id", "count"), with_payment=("any_payment", "sum"), submissions=("submissions", "sum")).reset_index()
pw = {e["citizen"] for e in EV if e["kind"] == "payout-wallet"}
sellers_wp = len(set(OFD.seller) & pw)
obs_after = A[A.paid_day >= "2026-09-17"].settled_by.value_counts().to_dict(); obs_before = A[A.paid_day < "2026-09-17"].settled_by.value_counts().to_dict()
by_ft = A.groupby(A.funder == "1f916-agent").h_award_to_paid.median().to_dict()
wd = [e for e in EV if e["kind"] == "listing-withdrawn"]; wd_after_1916 = [e for e in wd if 1787541654029 <= e["created_at"] <= 1787541654029 + 6 * 3600 * 1000]
N2 = dict(price_vs_submissions_spearman=float(rho.statistic), price_vs_submissions_p=float(rho.pvalue), sellers_with_wallet_proof=sellers_wp, awards_settled_by_before_0917=obs_before, awards_settled_by_since_0917=obs_after,
          median_h_award_to_paid_by_funder_is_maintainer={str(k): float(v) for k, v in by_ft.items()}, listing_withdrawn_within_6h_after_post_1916=len(wd_after_1916),
          listing_withdrawn_within_6h_after_post_1916_ids=[e["id"] for e in wd_after_1916])
save_numbers({"extra": N2})

nowtxt = "2026-10-06 00:56 UTC"
L_ = []
w = L_.append
w("# 1F916 economy: how agents are paid, by whom, and what they say about it\n")
w(f"Data: ~/1f916-archive, crawl complete as of {nowtxt}. Static site documents were fetched 2026-10-05 19:38 to 19:39 UTC (per-file times below); listing detail pages 2026-10-05 20:11 to 20:13 UTC; offer detail pages 20:23 to 20:26 UTC. No request was made to 1f916.ai or to any chain for this analysis. All amounts are USDC on Base (chain 8453) unless a column says otherwise. Statements the site makes about itself are labelled as the site's statement; statements by agents are labelled as agents' claims. Handles are public usernames; wallet and contract addresses are not written anywhere in this folder.\n")
w("Every figure states whether it is committed (a listing ceiling, an award, an offer price) or paid (a receipt, or a transfer the registry observed on chain and matched to a binding). The registry itself holds no money; the figures below are its records of transfers made between wallets.\n")

# ---------------- Answers
w("## Answers\n")
top = R.head(3)
ans = [
 ("How are agents paid", f"A funder wallet sends an exact-amount USDC transfer on Base to an address the agent bound with two signatures. The registry then writes either a receipt ({C_['receipts_n']}) or an observed-transfer settlement ({C_['observed_n']}). {C_['payments_settled_n']} payments to {C_['recipients_n']} handles.",
  f"{C_['payments_settled_n']} payments; first receipt event 1258 (binding 1, 2026-08-18); first award settled by receipt event 6048; first batch settled by observed transfer events 18892 to 18894 (2026-09-21); site rule in api__listings__guide.json for_funders.steps"),
 ("How much", f"{f2(C_['payments_settled_usdc'])} USDC in total. Median payment {f2(C_['payment_amount_dist']['median'])}, mean {f2(C_['payment_amount_dist']['mean'])}, maximum {f2(C_['payment_amount_dist']['max'])}. Per recipient: median {f2(C_['recipients_median_usdc'])}, mean {f2(C_['recipients_mean_usdc'])}, top handle {f2(top.iloc[0].paid_usdc)}. Awards committed {f2(C_['awards_committed_usdc'])} USDC in {C_['awards_n']} awards (median {f2(C_['award_amount_dist']['median'])}), of which {f2(C_['awards_paid_usdc'])} paid in {C_['awards_paid_n']}.",
  f"csv/settled_payments.csv (29 rows); csv/awards.csv (20 rows); largest payments: award events 13224 (10.00), 22831 and 22835 (10.00 each)"),
 ("Who pays", f"{C_['funders_paying_n']} of {C_['funders_usdc']} funder handles paid anything. The top three (head-of-engineering 29.00, 1f916-agent 13.00, coppice 12.00) paid {100*C_['funders_paid_top3_share']:.1f}% of it. Handles other than the maintainer paid {f2(C_['external_paid_usdc'])} in {C_['external_paid_n']} payments; the maintainer handle paid {f2(C_['treasury_funded_paid_usdc'])} in {C_['treasury_funded_paid_n']}. Offers produced {W['orders_n']} orders from {len(W['orders_buyers'])} buyers.",
  "csv/funders.csv; api__rail.json demand.external and demand.treasury_funded; csv/orders.csv (orders 1 to 6); post 3794 (2026-09-04, peppercorn) reads the v2 ledger as the society paying itself; the v2 ledger on 2026-10-05 shows 47.80 external and 12.00 maintainer-funded (api__rail.json demand)"),
 ("What they do with it", f"The registry does not show it. In the archive, {len(WL['paid_address_is_funder_address'])} pairs of a paid handle and a listing show a payee address that is also the named funding wallet of that listing; {len(EF)} handles both earn and fund (deepseek-dsh, head-of-engineering, jerrymuse66, ompi). No payment loop between two or three handles exists. {TK['recipient_spend_statement_hits']} phrase hits among {TK['recipient_messages_after_first_payment']:,} later messages by paid handles; none states what the money bought.",
  "csv/earn_and_fund_handles.csv; csv/recipient_spend_phrase_hits.csv; posts 1172 (both ends of the first payment), 1233 (agent stopped by its operator over compute cost), comment 57562 (verifier fee received); numbers.json wallet_links"),
]
w(md(pd.DataFrame(ans, columns=["question", "answer", "number and id of the evidence"])))
w("")

# ---------------- Method
w("## Method\n")
w("Tables were rebuilt from the archive by the scripts in this folder (README.md lists the order). Listing, award, submission and binding rows come from data/listings_detail, data/payouts and data/events. A payment is a binding that holds a receipt (receipt_id) or an observed transfer (observed_transfer_id). The payment time is the Base block time for receipts and the award paid_at for observed transfers. Amounts in 1F916 tokens are never added to USDC. Two bindings on listing 23 name the USDC contract with an amount of 30,000,000 tokens in atomic units; they are excluded from bound value (asset_agreement.state = disagrees).\n")
w("Cross-checks against the site's own totals (data/site/api__rail.json, fetched " + IDX["api__rail.json"] + "):\n")
chk = pd.DataFrame([
 ("listings", 56, C_["listings_total"], "totals.listings"), ("submissions", 884, C_["submissions_n"], "totals.submissions"), ("payout bindings", 644, C_["bindings_n"], "totals.bindings"),
 ("receipts", 19, C_["receipts_n"], "totals.receipts"), ("awards", 20, C_["awards_n"], "totals.awards"), ("lapsed bindings (no receipt, own expiry past)", 472, "not recomputed", "totals.lapsed_bindings"),
 ("v2 paid, USDC", "59.80", f2(C_["awards_paid_usdc"]), "liability_by_asset[0].v2_paid_atomic"), ("receipted paid, outside funders", "20.75", f2(PM[(PM.kind == 'receipt') & (PM.funder != '1f916-agent')].amount_usdc.sum()), "demand.external.receipted_paid_atomic_by_asset"),
 ("receipted paid, maintainer funded", "12.00", f2(PM[(PM.kind == 'receipt') & (PM.funder == '1f916-agent')].amount_usdc.sum()), "demand.treasury_funded.receipted_paid_atomic_by_asset"),
], columns=["quantity", "site", "recomputed", "site field"])
w(md(chk)); w("")
w("The site's paid figure for v2 listings (59.80) covers the award ledger only. Payments on the 19 first-version listings (2.20 USDC), the two verifier fees (0.35) and the four commissions minted from offers that carry receipts but no award rows (7.00) bring the recorded total to 69.35. The earlier community analysis (analysis/community/REPORT.md section 7) gives 644 bindings, 19 receipts, 20 awards, 65.80 USDC awarded and 155 offers; all agree.\n")

# ---------------- 1 money in
w("## 1. Money in\n")
w("Every source of money the data shows. Source: csv/money_in_sources.csv, built by e3_treasury.py and e1_core.py; fields cited per row.\n")
mi = MI.copy(); mi["amount"] = mi.apply(lambda r: "" if pd.isna(r.amount) else (f"{r.amount:,.0f}" if r.unit == "tokens" else f"{r.amount:,.2f}"), axis=1); mi["count"] = mi["count"].map(lambda x: "" if pd.isna(x) else int(x))
w(md(mi, ["source", "asset", "amount", "unit", "count", "first_day", "last_day", "kind", "file"], ["source", "asset", "amount", "unit", "n", "first day", "last day", "kind", "source file and field"])); w("")
w(f"The listing rail is funded by the funders' own wallets and the registry holds none of it ({'api__listings__guide.json what_this_is'}: it moves no money and holds no money). Of {C_['listings_usdc']} USDC listings, {int((LT.funding_mode=='promise').sum())} are promise listings (no wallet checked), {int((LT.funding_mode=='verified').sum())} are verified (balance read once at posting) and {int(LT.funding_mode.isna().sum())} are first-version listings with no funding mode. No listing is escrow-backed (funding_mode escrow: 0). Two listings (22, 23) are priced in 1F916 at 30,000,000 tokens each. Deposits: the registry accepts none; a listing is a promise or a one-time balance snapshot, and the treasury receives money only as patron payments, direct transfers and token fee or tax flows (table above).\n")
w("Funders by handle (USDC listings only; ceiling is price times max_awards on v2 listings and the price on first-version listings; paid is receipts plus observed transfers on that funder's listings, verifier fees included). Source: csv/funders.csv.\n")
fu = FU.copy(); fu["is_treasury"] = fu.is_treasury.map(lambda x: "yes" if x else "")
w(md(fu, ["funder", "listings", "ceiling_usdc", "awards", "committed_usdc", "paid_usdc", "verifier_paid_usdc", "total_paid_usdc", "listings_with_payment", "unpaid_awarded_usdc", "token_listings", "is_treasury"],
     ["handle", "listings", "ceiling", "awards", "awarded", "paid to workers", "paid to verifiers", "total paid", "listings with payment", "awarded, unpaid", "1F916 listings", "maintainer"], {"listings": lambda v: int(v), "awards": lambda v: int(v), "listings_with_payment": lambda v: int(v), "token_listings": lambda v: int(v)})); w("")
conc = pd.DataFrame([("paid per funder handle", len(FU[FU.listings > 0]), f"{100*C_['funders_paid_top3_share']:.1f}", f"{C_['funders_paid_gini_all_usdc_funders']:.2f}"),
                     ("ceiling posted per funder handle", len(FU[FU.listings > 0]), f"{100*C_['funders_posted_top3_share']:.1f}", f"{C_['funders_posted_gini']:.2f}"),
                     ("listings per funder handle", len(FU[FU.listings > 0]), f"{100*C_['funders_listings_top3_share']:.1f}", f"{C_['funders_listings_gini']:.2f}")], columns=["measure", "funders", "top 3 share, %", "Gini"])
w("Concentration of funding (all 19 funder handles, zeros included). Source: e1_core.py.\n"); w(md(conc)); w("")
w(f"Two listings carry most of the posted ceiling without any payment: listing 19 (100.00, jarvis-nemotron, a lottery run) and listing 40 (ceiling 100 slots at 1.00, claire). Excluding them the ceiling is {f2(C_['posted_ceiling_sum_usdc']-200)} USDC.\n")
w("Money the society's treasury received (site statements, treasury.json fetched " + TR["treasury_fetched_at"] + "): the ledger books " + f"{TR['patron_entries']} patron payments of 1.00 each over x402 and one 1.39 fee settle from an unofficial coin; the page says nearly every dollar the treasury holds came from tokens the society did not launch, and that a tax token it did not know about sent 2,172.29 USDC in 42 transfers (a floor, measured as of 2026-08-21 05:24 UTC). Booked income and on-chain holdings are never summed on the page (treasury.json buckets_note).\n")

# ---------------- 2 money out
w("## 2. Money out\n")
w(f"Awards (csv/awards.csv; data/listings_detail awards[]): {C_['awards_n']} awards on {C_['award_distinct_listings']} listings to {C_['award_distinct_handles']} handles; all {W['awards_by_requester']} were made by the requester, none by a verifier. State: " + ", ".join(f"{k} {v}" for k, v in C_["awards_by_state"].items()) + f". Committed {f2(C_['awards_committed_usdc'])} USDC; paid {f2(C_['awards_paid_usdc'])}; unpaid {f2(C_['awards_unpaid_usdc'])} (award 3 on listing 20, 5.00, overdue since 2026-10-02 with settlement block payer_late; award 15 on listing 54, 1.00, ready to pay).\n")
dd = C_["award_amount_dist"]
w("Per-award distribution (committed, USDC):\n")
w(md(pd.DataFrame([dict(n=dd["n"], total=dd["total"], min=dd["min"], median=dd["median"], mean=dd["mean"], max=dd["max"], **{k: dd[k] for k in ["p10", "p20", "p30", "p40", "p50", "p60", "p70", "p80", "p90"]})]), None, None, {"n": lambda v: int(v)})); w("")
pdist = C_["payment_amount_dist"]
w("Per-payment distribution (paid, USDC; 29 payments including two verifier fees):\n")
w(md(pd.DataFrame([dict(n=pdist["n"], total=pdist["total"], min=pdist["min"], median=pdist["median"], mean=pdist["mean"], max=pdist["max"], **{k: pdist[k] for k in ["p10", "p20", "p30", "p40", "p50", "p60", "p70", "p80", "p90"]})]), None, None, {"n": lambda v: int(v)})); w("")
pk = pd.DataFrame([(k, v["n"], v["usdc"]) for k, v in C_["payments_by_kind"].items()] + [("in the v2 award ledger", int(PM.in_award_ledger.sum()), C_["payments_in_award_ledger_usdc"]), ("outside the award ledger (first-version listings, verifier fees, commissions)", C_["payments_outside_ledger_n"], C_["payments_outside_ledger_usdc"])], columns=["payments (paid)", "n", "USDC"])
w(md(pk, None, None, {"n": lambda v: int(v)})); w("")
w("Recipients by handle (paid; verifier fees included). Source: csv/recipients.csv.\n")
rr = R.copy(); rr["funds_listings"] = rr.funds_listings.map(lambda x: "yes" if x else "")
w(md(rr, ["handle", "payments", "paid_usdc", "listings", "committed_award_usdc", "funds_listings"], ["handle", "payments", "paid", "listings", "awarded", "also funds listings"], {"payments": lambda v: int(v), "listings": lambda v: int(v)})); w("")
w(f"Concentration among {C_['recipients_n']} recipient handles: top three {100*C_['recipients_top3_share']:.1f}% of paid USDC (bitpotential-codex 10.10, free-develop-codex 10.00, nexushub-codex 10.00), Gini {C_['recipients_gini']:.2f}; {C_['recipients_multi_payment']} handles were paid more than once.\n")
bd = pd.DataFrame([("payout bindings filed", C_["bindings_n"], "data/payouts; api__rail.json totals.bindings"), ("  worker bindings", C_["bindings_worker_n"], ""), ("  verifier bindings", C_["bindings_verifier_n"], ""), ("bindings with a receipt", C_["bindings_receipt_n"], "receipt_id not null"),
                   ("bindings settled by observed transfer", C_["bindings_observed_n"], "observed_transfer_id not null"), ("bindings settled, total", C_["bindings_settled_n"], f"{C_['bindings_conversion_pct']:.1f}% of bindings; receipts alone {C_['bindings_receipt_conversion_pct']:.1f}%"),
                   ("distinct handles with a binding", C_["bindings_handles"], ""), ("distinct handles with a settled binding", C_["bindings_handles_settled"], ""), ("bindings lapsed (site count)", C_["rail_totals_lapsed_bindings"], "api__rail.json totals.lapsed_bindings"),
                   ("bound value, all bindings (USDC)", f2(C_["bound_value_usdc_all"]), "committed by the payee's own authorization; not an obligation (site: a binding is a route, not a debt)")], columns=["measure", "value", "note"])
w(md(bd)); w("")
w("Listing outcomes (csv/listings_flat.csv):\n")
lo = pd.DataFrame([("listings posted", C_["listings_total"]), ("with at least one submission", C_["listings_with_submission_n"]), ("with at least one award", C_["listings_with_award_n"]),
                   ("with at least one worker payment recorded", C_["listings_with_payment_n"]), ("zero awards (all listings)", f"{C_['listings_zero_awards_n']} ({C_['listings_zero_awards_pct_all']:.1f}%)"),
                   ("zero awards among the 37 v2 listings that can hold an award", f"{C_['v2_zero_awards_n']} ({C_['v2_zero_awards_pct']:.1f}%)"), ("no payment recorded", f"{C_['listings_no_payment_n']} ({C_['listings_no_payment_pct']:.1f}%)"),
                   ("withdrawn by the funder", C_["withdrawn_n"]), ("expired, not withdrawn (includes paid listings past their expiry)", C_["expired_n"]), ("open at 2026-10-06 00:56 UTC", C_["open_n"])] , columns=["listing outcome", "n"])
w(md(lo)); w("")
w("Detail state served by the site: " + ", ".join(f"{k} {v}" for k, v in C_["state_counts"].items()) + ". Withdrawals carry the funder's stated reason (events kind listing-withdrawn, 22): funder wallet cap reached (listing 8), one-claim cap closure (listings 1, 2, 4, 5, 7), a display defect (22), a funding mode posted wrongly (35), a design defect named by the funder (36, 37), a keeper's decision (listings 10, 12, 14 to 18), a closure after the submission deadline (34), a cap closure after the single payment (3), a duplicate (46), posting in error (42) and a listing written from the selling side (43).\n")
tt = pd.DataFrame([(k.replace("listing_h_to_", "listing to ").replace("_", " "), v["n"], v["median"], v["mean"], v["p25"], v["p75"], v["max"]) for k, v in [("listing_h_to_first_submission", C_["listing_h_to_first_submission"]), ("listing_h_to_first_award", C_["listing_h_to_first_award"]), ("listing_h_to_first_paid", C_["listing_h_to_first_paid"])]] +
                  [("submission to award", C_["sub_to_award_hours"]["n"], C_["sub_to_award_hours"]["median"], C_["sub_to_award_hours"]["mean"], C_["sub_to_award_hours"]["p25"], C_["sub_to_award_hours"]["p75"], C_["sub_to_award_hours"]["max"]),
                   ("award to payment (paid awards)", C_["award_to_paid_hours"]["n"], C_["award_to_paid_hours"]["median"], C_["award_to_paid_hours"]["mean"], C_["award_to_paid_hours"]["p25"], C_["award_to_paid_hours"]["p75"], C_["award_to_paid_hours"]["max"]),
                   ("binding to payment (receipts)", C_["bind_to_paid_receipts_hours"]["n"], C_["bind_to_paid_receipts_hours"]["median"], C_["bind_to_paid_receipts_hours"]["mean"], C_["bind_to_paid_receipts_hours"]["p25"], C_["bind_to_paid_receipts_hours"]["p75"], C_["bind_to_paid_receipts_hours"]["max"])],
                 columns=["interval", "n", "median h", "mean h", "p25 h", "p75 h", "max h"])
w("Time (hours). Source: csv/listings_flat.csv, csv/awards.csv, csv/settled_payments.csv.\n"); w(md(tt, None, None, {"n": lambda v: int(v)})); w("")
w(f"Award to payment: median {by_ft.get(False, float('nan')):.1f} h when an outside handle funded the listing and {by_ft.get(True, float('nan')):.1f} h when the maintainer handle did (n = 18 paid awards).\n")
us = pd.DataFrame([(k, v) for k, v in C_["submissions_by_state"].items()], columns=["submission economic_state", "n"])
w(f"Unpaid submissions: {C_['submissions_unpaid_n']} of {C_['submissions_n']} submissions by {C_['submitters_n']} handles are not paid; {C_['submissions_unpaid_with_binding_n']} of those were filed by a handle that also filed a payout binding on the same listing; {C_['submissions_unpaid_no_key_n']} were filed by handles with no bound key (payee_status.key_bound false). First-version listings have no award ledger, so 'not selected' on them means no recorded award, not a refusal.\n"); w(md(us, None, None, {"n": lambda v: int(v)})); w("")

# ---------------- 3 work
w("## 3. The work\n")
w("Categories were assigned by keyword rules on titles (categories.py), with per-id overrides listed in the same file; the rules are a reading aid and some titles fit more than one category.\n")
w("Listings. Source: csv/listing_categories.csv.\n")
w(md(LC, ["category", "listings", "price_median_usdc", "price_min_usdc", "price_max_usdc", "submissions", "with_award", "with_payment", "paid_usdc", "examples"], ["category", "listings", "median price", "min", "max", "submissions", "with award", "with payment", "paid", "examples (listing id: title)"], {"listings": int, "submissions": int, "with_award": int, "with_payment": int})); w("")
w(f"Listing prices: {C_['listings_usdc']} USDC listings, median {f2(C_['posted_price_median_usdc'])}, maximum {f2(C_['posted_price_max_usdc'])}, sum {f2(C_['posted_price_sum_usdc'])}. Spearman correlation of price with submissions: {N2['price_vs_submissions_spearman']:.2f} (p = {N2['price_vs_submissions_p']:.2f}, n = 54). Listings that name a verifier price: {W['listings_with_verifier_price']} (ids {', '.join(map(str, W['listings_verifier_ids']))}).\n")
w("Offers (the sell side opened 2026-09-18). Source: csv/offer_categories.csv.\n")
w(md(OC, ["category", "offers", "price_median_usdc", "price_min_usdc", "price_max_usdc", "open_now", "orders", "sellers", "examples"], ["category", "offers", "median price", "min", "max", "open", "orders", "sellers", "examples (offer id: title)"], {"offers": int, "open_now": int, "orders": int, "sellers": int})); w("")
op = W["offer_price"]
w(f"Offer prices (USDC, asking price per order): n {op['n']}, min {op['min']:g}, median {op['median']:g}, mean {f2(op['mean'])}, max {op['max']:g}, sum {f2(op['total'])}; deciles p10 to p90: " + ", ".join(f"{op[f'p{p}']:g}" for p in range(10, 100, 10)) + f". {W['offer_price_share_le3_pct']:.1f}% ask 3 or less; {W['offer_price_share_ge10_pct']:.1f}% ask 10 or more; the mode is {W['offer_price_mode']:g} ({W['offer_price_mode_n']} offers). {W['offers_pay_after_delivery_n']} offer texts promise payment after delivery or acceptance. Six withdrawals state that the seller is repricing or reposting (offers {', '.join(map(str, W['offers_reprice_text']))}); one states the target band as 1 to 3 USDC where orders actually happen.\n")
w(f"The title series [FOR HIRE N USDC] has {W['for_hire_posts_n']} posts by {W['for_hire_authors']} authors from {W['for_hire_first_day']} to {W['for_hire_last_day']}, priced {W['for_hire_price']['min']:g} to {W['for_hire_price']['max']:g} USDC (median {W['for_hire_price']['median']:g}). {W['for_hire_matched_to_offer_n']} titles carry an offer id found in the offers table, and all {W['for_hire_title_price_match_offer_n']} carry that offer's price; the other two are offers 156 and 157, posted after the offer detail fetch (3 and 5 USDC). The posts drew {W['for_hire_comments_total']} comments in total (median {W['for_hire_comments_median']:g} per post). The series is a registry template (analysis/swarm/REPORT.md section on series: 81% share one phrase). [BOUNTY N USDC] has {W['bounty_posts_n']} posts priced {W['bounty_post_price']['min']:g} to {W['bounty_post_price']['max']:g}.\n")
oc_ = W["offer_conversion"]
w(f"Orders per offer: {int((OFD.orders==0).sum())} offers with no order, {int((OFD.orders==1).sum())} with one order, {int((OFD.orders>1).sum())} with more than one.\n")
w("Offers to orders to listings to payment (csv/orders.csv; data/offers_detail orders[]):\n")
w(md(pd.DataFrame([("offers posted (detail fetched)", oc_["offers"]), ("offers with an order", oc_["offers_with_order"]), ("orders (each mints a listing funded by the buyer)", oc_["listings_minted"]), ("minted listings with a submission", oc_["minted_with_submission"]), ("minted listings with a payment recorded", oc_["minted_with_payment"])], columns=["stage", "n"]))); w("")
w(f"{W['offers_with_order_pct']:.1f}% of offers have an order. Buyers: {', '.join(f'{k} {v}' for k, v in W['orders_buyers'].items())}. The ordered offers sum to {f2(W['orders_price_usdc_sum'])} USDC; payments recorded on the minted listings sum to {f2(W['orders_paid_usdc'])}. Median time from offer to order {W['orders_h_offer_to_order_median']:.1f} h. {W['sellers_paid_any_n']} of {W['offer_sellers']} sellers have a payment recorded for any listing ({', '.join(W['sellers_paid_any'])}); {sellers_wp} sellers filed a payout-wallet proof. Offers 156 and 157 are not in these counts.\n")
w("Verifiers. Source: data/listings_detail verdicts, awards, bindings; thread comments in data/comments.\n")
vt = VT.head(10)
w(f"The registry holds {W['verdicts_registry_total']} signed verdicts (verdicts[] is empty on all 56 listings). Settlement modes: " + ", ".join(f"{k} {v}" for k, v in W["settlement_modes"].items()) + f". All {W['awards_by_requester']} awards are requester awards (the funder accepted by paying or by an award call); {W['awards_by_verifier']} are verifier awards. What the guide says a verifier does: re-run the listing's condition on a submission, post the result in the thread citing the submission id, and optionally bind against listing-N-verifier at the listed verifier price (api__listings__guide.json for_verifiers). Verifier bindings: {C_['bindings_verifier_n']}; verifier fees paid: " + "; ".join(f"listing {x['listing_id']} to {x['handle']} {x['amount_usdc']:g} ({x['kind']})" for x in W["verifier_payments"]) + ". Verification as practised is a comment: " + f"{W['thread_verdict_comments_n']} comments on listing threads contain PASS or FAIL ({W['thread_verdict_counts'].get('PASS',0)} PASS, {W['thread_verdict_counts'].get('FAIL',0)} FAIL) by {W['thread_verdict_authors_n']} handles on {W['thread_verdict_listings_n']} listings (csv/thread_verdict_comments.csv; these are word matches, not signed verdicts).\n")
w(md(vt, ["author", "comments", "pass", "fail", "listings"], ["handle", "comments with PASS or FAIL", "PASS", "FAIL", "listings"], {"comments": int, "pass": int, "fail": int, "listings": int})); w("")

# ---------------- 4 treasury
w("## 4. Treasury and token\n")
w(f"Fetch times: treasury.json {TR['treasury_fetched_at']}; api__official.json {TR['official_fetched_at']}; api__rail.json {TR['rail_fetched_at']}; human__economy.txt {IDX['human__economy.txt']}.\n")
tf = pd.DataFrame([
 ("booked_cents", f"{TR['booked_cents']} (USD {TR['booked_cents']/100:,.2f})", "treasury.json booked_cents", "income the society recognized, net of the ledger's outflows"),
 ("onchain_cents", f"{TR['onchain_cents']} (USD {TR['onchain_cents']/100:,.2f})", "treasury.json onchain_cents, onchain_checked_at " + TR["onchain_checked_at_utc"], "site: actual wallet balance read live from Base; onchain_is_stale " + str(TR["onchain_is_stale"])),
 ("unbooked_cents", f"{TR['unbooked_cents']} (USD {TR['unbooked_cents']/100:,.2f})", "treasury.json unbooked_cents", "site: on chain minus booked; the two are never summed"),
 ("assets.total_cents", "null", "treasury.json assets.total_cents, assets.complete = false", "the same response lists errors: balanceOf and price calls did not answer, so every tier value is null"),
 ("tiers served", "tier 1 cash-equivalent, tier 2 blue-chip volatile, tier 3 speculative (notional)", "treasury.json assets.by_tier", "cents null for all three at fetch time"),
 ("ledger rows", f"{TR['ledger_entries']}; inflow {f2(TR['ledger_in_usd'])}, outflow {f2(TR['ledger_out_usd'])}, net {f2(TR['ledger_net_usd'])}", "treasury.json entries[]", f"net equals booked_cents: {TR['ledger_sum_matches_booked']}; last row created {TR['ledger_last_entry_utc'][:16]}"),
], columns=["figure", "value", "source file and field", "note"])
w("Booked versus on-chain, as served:\n"); w(md(tf)); w("")
w("The on-chain figure and the agents' own readings differ by date and by asset. An agent reading of the treasury address on 2026-09-21 14:35 UTC (post 6244, four RPC operators agreeing) gives 28,806.93 USDC, 3.947 WETH and 5,598,939,081.6 1F916 tokens; the served on-chain figure on 2026-10-05 is 42,584.38 USD for a mix the file does not itemise. Neither figure was recomputed here.\n")
w("Holdings by tier. The served file carries no tier values (above). Two dollar readings of GET /treasury quoted by one agent on 2026-08-22 are in csv/treasury_holdings_by_tier.csv and figure 11 (agents' claim; the second reading's tier 2 and tier 3 are derived from the totals the comment states):\n")
w(md(TH, ["tier", "tier_label", "reading_utc", "usd", "source", "note"], ["tier", "label", "reading UTC", "USD", "source", "note"], {"tier": int})); w("")
w("Ledger by category (csv/treasury_ledger_by_category.csv):\n"); w(md(rd_csv("treasury_ledger_by_category.csv"), None, None, {"entries": int})); w("")
w("What the society spent money on, from the ledger: domain rent (-90.00, estimate), a hosting plan (-5.00), API credits for the society's social account (-5.00), a premium month for that account (-4.00); float moves of 10.00 (2026-08-16) and 16.00 (2026-09-02) from the treasury to the society's own payout wallet to settle listings 6, 20 and 21 (booked as -36.00 with a +10.00 correction because 10.00 was booked twice; row 15 books the 1.00 first bounty as an overlap). Listings funded by the maintainer handle paid 13.00 USDC (5 payments). Grants: " + f"{len(TR['grants'])} grants (1f512 selected, 1fab0 building), sponsor 1f916-agent, 24 proposal rows; the site says a grant holds no money of its own (grants.txt); resources are domains and hosting or compute. No money was awarded through a grant. Agents report outflows the ledger does not hold: 11.08 USDC pulled by an ERC-3009 collector on 2026-09-11, 55.40 USDC pulled earlier, and 3.00 plus 1.00 USDC sent on 2026-09-18 (posts 5029, 5460, 5899); the ledger's last row is 2026-09-02 05:45 UTC.\n")
w("Withdrawals. Events of kind withdrawal (128) are comment and post withdrawals; none mentions money. Money-withdrawal events do not exist in the identity log. Listing withdrawals: 22. Offer withdrawals: 25.\n")
w("Spending policy as the site states it (treasury.json spending_policy):\n")
w(md(pd.DataFrame([("waterfall 1", "earned dollars (patron x402 and booked income); always spent first"), ("waterfall 2", "received dollars (outside USDC sent on the sender's own initiative); spent only when earned dollars are exhausted"),
                   ("when_empty", "the treasury is empty; nothing below refills it automatically"), ("never_money", "speculative tokens, in the wallet or in a claim, are never money; no expenditure may depend on selling one"),
                   ("standing_rules", "dollars only; no custody of other parties' funds; every payment ledgered; treasury money buys verified work and infrastructure, not promotion of any asset")], columns=["rule", "statement (paraphrase)"]))); w("")
w("Token facts as the site states them:\n")
tk = pd.DataFrame([(t["symbol"] + " on " + t["chain"], t["launched_via"], t["sent"], t["live"], "spending_policy.recognition.tokens[]") for t in TR["tokens"]], columns=["token", "launched via", "sent to treasury (site)", "live", "field"])
w(md(tk)); w("")
w("- The official token (api__official.json official_token): symbol 1F916, Base, chain 8453, recognized 2026-08-25. The site says an outside party launched it and the society did not create, mint, sell or launch it.")
w("- The treasury is named as the 95 percent beneficiary of the token's trading fees (treasury.json holdings[].note); fee amounts were null in the served file (quantity null; fees-manager reads incomplete).")
w("- The site states a conflict: the treasury holds the token and receives fee flow, so recognition may affect how its own holding is perceived (api__official.json official_token.the_conflict).")
w("- Since 2026-09-01 a listing may be priced in 1F916; USDC stays the default; escrow-backed listings stay USDC only (api__official.json payout_assets, amended_2026_09_01). Atomic units are 6 decimals for USDC and 18 for 1F916; the site reports totals across the two as null.")
w("- Agents' claims about fee flows: a single transaction on 2026-08-20 moved 6.175528 WETH and 3,380,926,322 tokens to the treasury (post 1916, written by 1f916-agent); on 2026-08-20 a citizen collected 17,923 USD of fees to the treasury with two transactions (post 1273); on 2026-09-20 the treasury called collectFees itself and received 449,003,744.5 tokens and 3.947 WETH (post 6137). The post 6244 reading shows 15,000,000,000 tokens vesting to the treasury with 0 released.")
w("- human__economy.txt carries static counts (23 listings, 274 submissions, 4 awards, 8 payments, 18 outside listings, $1.20 outside-funded) that predate the API figures (56, 884, 20, 29).\n")

# ---------------- 5 what agents do
w("## 5. What agents do with the money\n")
w("Payout wallet proofs (events kind payout-wallet, first filed 2026-09-03): " + f"{TK['payout_wallet_events']} events by {TK['payout_wallet_handles']} handles; {TK['payout_wallet_handles_multi']} handles filed more than one; {TK['payout_wallet_handles_with_binding']} of the handles also filed a payout binding; {TK['payout_wallet_handles_with_payment']} of the {C_['recipients_n']} paid handles filed a proof. Expiries and revocations are not in the archive: " + TK["wallet_revoke_evidence"] + f". Domain verifications of a binding: {TK['binding_verified_events']} events; lapses: {TK['binding_lapsed_events']}. One offer closure cites a revoked proof (offer 110).\n")
w(f"Bound addresses: {WL['bindings']} bindings use {WL['distinct_payout_addresses']} distinct payout addresses from {WL['handles_with_bindings']} handles; {WL['addresses_bound_by_more_than_one_handle']} addresses are bound by two handles each ({WL['handles_in_shared_addresses']} handles). {WL['listings_naming_a_funder_address']} listings name a funder address ({WL['funder_addresses_named']} distinct). {WL['funder_addresses_also_bound_as_payout']} funder addresses are also a bound payout address: coppice, deepseek-dsh, head-of-engineering and ompi each use one wallet for both roles, and the address bound by ike is the named funding wallet of 11 understory listings (9 to 12, 14 to 18, 24, 25). No settled payment went to the funder address of its own listing. These are matches inside the archive; no on-chain flow was read.\n")
w("Handles that both earn and fund (csv/earn_and_fund_handles.csv):\n")
w(md(EF, ["handle", "earned_usdc", "first_earned_utc", "listings_funded", "funded_listing_ids", "first_funded_utc", "listings_funded_after_first_earning", "usdc_paid_out_as_funder"], ["handle", "earned", "first earned UTC", "listings funded", "listing ids", "first funded UTC", "funded after first earning", "paid out as funder"], {"listings_funded": int, "listings_funded_after_first_earning": int})); w("")
w("Reading of the table: head-of-engineering earned 0.10 on 2026-08-19 and funded five listings from 2026-09-13 that paid out 29.00; deepseek-dsh posted listings 1 to 5 on 2026-08-16, was paid 1.00 on 2026-08-17 and posted listings 7 and 8 on 2026-08-19 (post 1172, titled 'Both ends of the rail's first payment'); ompi funded listing 32 on 2026-09-12 (paid 10.00) nine days before its first receipt; jerrymuse66 posted a listing before its offer was ordered. The 0.10 paid to head-of-engineering cannot have funded 29.00 of listings; the table shows order of events and not source of funds.\n")
w("Payment loops. Funder to recipient pairs (csv/funder_to_recipient_pairs.csv) contain no two-handle or three-handle cycle and no handle paying itself. In the offers rail, buyer coppice ordered four offers (listings 47, 48, 49, 56 were commissions placed by coppice) and the maintainer handle ordered two (44, 50); coppice has not been paid by anyone in the registry.\n")
w(f"Statements by paid handles. {TK['recipient_messages_after_first_payment']:,} posts and comments were written by the 25 paid handles after their first payment. A phrase search for spending, reinvesting or buying with the proceeds returned {TK['recipient_spend_statement_hits']} hits (csv/recipient_spend_phrase_hits.csv); every hit concerns time or effort. Related statements by agents: root, citizen 205, wrote that its operator was stopping it because it cost more in local compute than it returned (post 1233, 2026-08-19); ox_arka wrote that agents pay for inputs (search, data, inference) and never for labour (post 5151); oca asked who pays for agent compute when the human subsidy ends (post 2883); deepseek-dsh wrote that its funding wallet held about 2.00 USDC when it owed 3.50 across seven 0.50 payments and paid in submission order as funds allowed (comment 14031); bitpotential-codex wrote that the verifier fee was received and nothing remained due (comment 57562).\n")
w("What the data cannot show: where any payout address sends money after it is paid, whether an operator or a model pays for compute from it, and whether two handles share a human or a wallet beyond the 7 shared addresses above. No per-wallet tracking was done.\n")

# ---------------- 6 talk
w("## 6. What agents say about money\n")
w(f"Method: regular expressions over {TK['messages_total']['posts']:,} posts and {TK['messages_total']['comments']:,} comments (e4a_flags.py, patterns in themes.py). {TK['messages_money_core']['posts']:,} posts and {TK['messages_money_core']['comments']:,} comments contain a core money word; {TK['messages_in_any_theme']:,} match at least one theme, by {TK['handles_in_any_theme']:,} handles. A message can match several themes, so rows do not add up. Matches are lexical and overcount on-topic use (the word price is common in discussions of costs that are not payments; receipt is a community idiom for evidence, so the receipts theme requires a payment word nearby).\n")
w(md(TT, ["theme", "posts", "comments", "handles", "share_of_all_messages_pct", "first_day", "peak_day", "peak_day_n"], ["theme", "posts", "comments", "handles", "% of all messages", "first day", "peak day", "messages on peak day"], {"posts": int, "comments": int, "handles": int})); w("")
w("Traced posts (csv/traced_posts.csv). Claims are the authors' claims; the checks are mine.\n")
w(md(TP, ["post_id", "series", "author", "utc", "comments", "votes", "claim"], ["post", "series", "handle", "UTC", "comments", "votes", "claim or title"], {"post_id": int, "comments": int, "votes": int}).replace("—", "-")); w("")
c1 = TK["post_1916_check"]; pm = TK["post_1916_meta"]
w(f"Post 1916 (1f916-agent, {pm['utc'][:16]} UTC; {pm['comments']} comments from {pm['distinct_commenters']} handles; {pm['votes']} votes; cited by {TK['mentions_of_1916']['posts']} posts and {TK['mentions_of_1916']['comments']} comments). Its title states 'Ninety-nine of you did work here. Three got paid.' Recomputed at the post's timestamp: {c1['listings']} listings worth {c1['listing_posted_usdc']:.2f} USDC posted; {c1['submissions']} submissions; {c1['bindings']} bindings; {c1['receipts_filed']} receipts filed; {c1['listings_with_subs_no_payment_by_filing_time']} of {c1['listings_with_subs']} listings that took work had no payment. The post says 18 listings worth 8.50, 99 submissions, three payments, 14 listings that took work and paid nobody, and 70 unpaid bindings; the listing count, posted value, submission count, payment count and unpaid-listing count all match; the unpaid binding count is 72 here (75 bindings minus 3 receipts). Receipts by block time were 5 at that moment because two receipts were filed after the post. Comment 18172 (head-of-engineering) re-ran the numbers; post 2166 by sage notes the fourth receipt landed at 14:12 the same day.\n")
w("Post 7708 (oca, 2026-10-04): 'The rail is contracting at both ends: 269 unpaid submissions and a 37% key-take-up drop'. The claim of 10 listings holding 269 submissions with no payment is not reproduced exactly. At the post's time, listings with submissions and no payment: " + "; ".join(f"{k.replace('listings with submissions and no payment ', '').replace('same, ', '')}: {v[0]} listings, {v[1]} submissions" for k, v in TK["post_7708_variants"].items()) + ". The key take-up and liability figures it cites were not recomputed.\n")
w(f"Post 7756 (kret, 2026-10-05): five awards on listings 38 and 39 with zero receipts. Recomputed: {TK['post_7756_check']['awards']} awards, settled_by {TK['post_7756_check']['settled_by']}, receipts {TK['post_7756_check']['receipts']}. The registry's rule since 2026-09-17 writes the award paid from an observed transfer with no receipt, so the empty receipt column is the designed state for those awards.\n")
w("Treasury watch (popek1990), nine reports from 2026-09-12 to 2026-09-21, ending with 'the series pauses here' because the operator paused the agent: " + "; ".join(f"#{i+1} post {t['id']} ({t['comments']} comment{'' if t['comments']==1 else 's'})" for i, t in enumerate(TK["treasury_watch"])) + ". Claims in the series: vesting of 15,000,000,000 tokens released 0 through 2026-09-21; the ledger last booked a row on 2026-09-02 (checked: the last ledger row is 2026-09-02 05:45 UTC); two outflows on 2026-09-18 (3.00 and 1.00 USDC) and a treasury-signed fee collection on 2026-09-20.\n")
w("Posts titled 'rail contracting', 'five awards zero receipts' and 'unpaid submissions' are posts 7708 and 7756 above; the unpaid-work message count per day is in csv/talk_unpaid_by_day.csv and figure 14 (peak 99 on 2026-08-24, the day of post 1916).\n")
w("Forty example messages (csv/talk_examples_40.csv, verbatim; dashes in the quoted text are replaced by hyphens in this table only):\n")
ex = EX.copy(); ex["excerpt"] = ex.excerpt.map(clean); ex["url"] = ex.url.map(lambda u_: u_.replace("https://1f916.ai", ""))
w(md(ex, ["id", "kind", "handle", "date_utc", "excerpt", "url", "theme"], ["id", "kind", "handle", "date UTC", "excerpt", "url (https://1f916.ai + path)", "theme"], {"id": int})); w("")

# ---------------- 7 timeline
w("## 7. Timeline of the economy\n")
w("Daily counts are in csv/timeline_by_day.csv (new listings, submissions, bindings, awards, payments, offers, orders, withdrawals, wallet proofs, cumulative USDC). Weekly totals (Monday to Sunday UTC):\n")
wk = pd.DataFrame(TM["listings_by_week"]).T.reset_index().rename(columns={"index": "week"})
w(md(wk, None, None, {c: int for c in wk.columns if c != "week"})); w("")
w("Rule and feature dates. The two guides carry rules_version and changed_at: listings guide rules_version 2026-09-21.1, changed_at 2026-09-21T20:30:00Z (api__listings__guide.json); offers guide rules_version 2026-09-18.1, changed_at 2026-09-18T04:05:00Z (api__offers__guide.json). Other dates come from the site's own notes or from the first event of a kind (csv/rule_change_dates.csv, csv/feature_first_seen.json).\n")
w(md(RU, None, ["date UTC", "change", "source"])); w("")
sel = EFF[EFF.date_utc.isin(["2026-08-21", "2026-09-01", "2026-09-17", "2026-09-18", "2026-09-21"])].pivot_table(index=["date_utc"], columns="metric", values=["mean_per_day_7d_before", "mean_per_day_7d_after"], aggfunc="first")
rows = []
for dte in sel.index:
    for m in ["submissions", "bindings", "listings", "payments", "awards", "offers"]:
        rows.append((dte, m, sel.loc[dte, ("mean_per_day_7d_before", m)], sel.loc[dte, ("mean_per_day_7d_after", m)]))
w("Mean per day in the 7 days before and the 7 days from each date (csv/rule_change_effects.csv). The windows overlap neighbouring changes and the series are short, so the comparison describes timing only.\n")
w(md(pd.DataFrame(rows, columns=["date", "metric", "7 days before", "7 days from"]))); w("")
n_wd = N2["listing_withdrawn_within_6h_after_post_1916"]
w(f"Effects as recorded: after 2026-09-01 awards began (0 before; 0.57 per day after) and submissions rose from 8.4 to 15.3 per day; from 2026-09-17 all {sum(obs_after.values())} paid awards settled by observed transfer, where all {sum(obs_before.values())} paid before that date had settled by receipt; offers ran at 9 to 10 per day from 2026-09-18 with 6 orders in total; after 2026-09-21 submissions fell from 44.3 to 18.3 per day and bindings from 29.0 to 17.1 per day while payments stayed near one per day. Submissions peaked on 2026-09-20 (58) and were 1 to 5 per day from 2026-09-28. Within six hours after post 1916, {n_wd} listings were withdrawn (events 3312 to 3316, 2026-08-24 04:52 UTC, citing a one-claim cap policy in a different thread); the data do not link the two.\n")

# ---------------- 8 figures
w("## 8. Figures\n")
w("SVG, 7 inches wide, data in the CSV with the same stem (figures.json lists file, title, description, source CSV, n).\n")
for fg in FIGS:
    w(f"![{fg['title']}]({fg['file']})\n")
    w(f"{fg['description']} Data: {fg['source_csv']}; n = {fg['n']}.\n")

# ---------------- 9 open questions
w("## 9. Open questions\n")
oq = [
 ("Do funders who paid once pay again?", "csv/funders.csv, csv/awards.csv, data/listings_detail. Test: for each funder with two or more listings with awards, share paid within the listing's payable window."),
 ("Is a funder's wallet balance at posting related to whether the listing pays?", "data/listings_detail funds_seen_atomic and funding_mode against paid_usdc; 6 verified and 31 promise listings give a small sample; the site reads balance once."),
 ("Do the four handles that earn and fund pay out of what they earned?", "data/payouts payout_address against data/listings_detail funder_address (done here, matches only) plus Base transfer history of those wallets (not collected)."),
 ("Does the same wallet sit behind ike and understory?", "ike's bound address equals the named funding wallet of 11 understory listings; compare the two handles' posting times and model labels in data/posts and data/citizens."),
 ("Did the 2026-09-21 listings guide cut submissions, or did the fall follow the end of the large listings opened on 2026-09-13 (36 to 39)?", "csv/timeline_by_day.csv, csv/listings_flat.csv created_at, submissions per open listing per day."),
 ("Do outside-funded awards settle slower than maintainer-funded awards?", "csv/awards.csv h_award_to_paid by funder (median 1.5 h against 0.3 h, n = 18); extend as awards accrue."),
 ("Does the observed-transfer rule (2026-09-17) lower the number of receipts filed?", "events kind payout-receipt after 2026-09-17 (5) against paid awards settled by observed transfer (10); data/events and csv/awards.csv."),
 ("Why do 6 orders across 155 offers come from two buyers?", "data/offers_detail orders[].buyer; csv/orders.csv; buyers' own listings and posts; test whether coppice is paid for any listing it posts."),
 ("Is offer price related to orders?", "csv/offers_flat.csv price_usdc against orders; the one withdrawal that names a 1 to 3 USDC band (offer 75) is a falsifiable claim; all 6 orders were placed at 1 to 3 USDC."),
 ("Are unpaid submissions concentrated in a few submitter handles?", "csv/submissions_flat.csv by handle (241 handles, 866 unpaid); Gini of unpaid submissions per handle."),
 ("Do posts about unpaid work precede listing withdrawals or new funding?", "csv/talk_unpaid_by_day.csv against events kind listing-withdrawn and listing; lag correlation by day."),
 ("Does a promise listing pay less often than a verified one?", f"csv/listings_flat.csv funding_mode: promise {int(fm[fm.funding_mode=='promise'].with_payment.iloc[0])} of {int(fm[fm.funding_mode=='promise'].listings.iloc[0])} listings with a payment; verified {int(fm[fm.funding_mode=='verified'].with_payment.iloc[0])} of {int(fm[fm.funding_mode=='verified'].listings.iloc[0])}; first-version {int(fm[fm.funding_mode=='none (v1)'].with_payment.iloc[0])} of {int(fm[fm.funding_mode=='none (v1)'].listings.iloc[0])}."),
 ("Is the treasury ledger complete?", "treasury.json entries (last row 2026-09-02) against Base transfers to and from the treasury address (not collected); posts 5029, 5460, 5899 list unbooked movements."),
 ("How many of the 40 submissions filed without a bound key would have been paid had the handle bound one?", "csv/submissions_flat.csv key_bound false (40 submissions) against the listing's award state."),
 ("Do 1F916-priced listings attract less work than USDC listings?", "listings 22 (0 submissions, withdrawn) and 23 (39 submissions, 23 bindings, 0 awards) against USDC listings of the same days; two listings is too few to answer."),
]
w(md(pd.DataFrame(oq, columns=["question", "data and test"]))); w("")

# ---------------- 10 limits
w("## 10. Limits\n")
for s_ in [
 "No on-chain data was read. Receipts and observed transfers are the registry's records of Base transfers; two providers agreeing is the site's statement. Amounts, dates and counts of transfers that were never recorded by the registry are not in the data.",
 "Payments made off the platform, and payments made on chain between wallets that match no binding, are invisible. Some funders say they paid outside the registry's rows: comments 17435, 17436, 35903 and 35943 are cited in withdrawal reasons for listings 14, 16 and 18 as funder statements of payment that the listing rows do not show.",
 "First-version listings (19) have no award ledger. Their liability is unknown to the registry, and 'zero awards' on them means no ledger, not no obligation.",
 "No per-wallet tracking was done. Matches between bound addresses and funder addresses use the archive only. Where an address goes after a payment is not known.",
 "Human operators' own spending (compute, subscriptions, the owner's costs) is not recorded anywhere in the data; the ledger shows only the society's hosting and account costs.",
 "Treasury values: the served treasury.json holds null tier values and null asset totals at fetch time with errors listed; the tier figure uses an agent's quotation of an earlier reading. The on-chain figure in the file was not itemised.",
 "Theme counts are keyword matches and overcount. The 40 examples were chosen by reading, to cover the themes and the traced series, and do not sample the corpus.",
 "Categories are keyword rules on titles. Handles are accounts; one operator can run several, and one handle can run several models.",
 "The offers table covers 155 offers fetched at 20:23 to 20:26 UTC on 2026-10-05; offers 156 and 157 exist as posts only. Orders are counted from offers_detail orders[] (6), and the offer detail endpoint was not available for the earlier community analysis.",
 "The site's observed_payments counts (31 across funders in api__rail.json) and the 10 awards settled by observed transfer here are not reconciled; the rail counts every transfer it matched to a binding, including transfers on bindings that already hold a receipt (not verified).",
 "The crawl marks flags, tags and payload_notices as incomplete (manifest.json); none of them enters a money figure here.",
]: w("- " + s_)
w("")
w("Rerun: see README.md. Figures and tables regenerate from the archive in under ten minutes.")
txt = "\n".join(L_)
open(OUT / "REPORT.md", "w").write(txt)
print(len(txt), "chars")
