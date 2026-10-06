"""Treasury, token and money-in sources. Everything from data/site/*.json with fetch times; agent readings are labelled as claims."""
from common import *
idx = {f["file"]: f["fetched_at"] for f in site("_index.json")["files"]}
TR = site("treasury.json"); OFFI = site("api__official.json"); RAIL = site("api__rail.json")
PM = pd.read_csv(CSV / "settled_payments.csv"); LT = pd.read_csv(CSV / "listings_flat.csv"); OR = pd.read_csv(CSV / "orders.csv")
core = load_numbers()["core"]

# ledger
E = pd.DataFrame(TR["entries"]).sort_values("id")
def cat(r):
    d = r.description.lower()
    if r.id == 19: return "correction of a double-booked float"
    if "rail float" in d or "treasury float" in d: return "float to society payout wallet (own wallet)"
    if "first bounty paid" in d: return "bounty paid (overlaps float)"
    if "patron" in d: return "patron payment (x402 $1)"
    if "community fee settle" in d: return "fee settle from an unofficial coin"
    if any(k in d for k in ["hosting", "x (twitter)", "x premium", "rent: domain"]): return "infrastructure and accounts"
    return "other"
E["category"] = E.apply(cat, axis=1)
E["amount_usd"] = E.amount_cents / 100
LEDGER_TEXT = {1: "domain rent, year one (estimate, to be corrected to the invoice)", 2: "hosting, free tier", 8: "hosting plan upgrade, 5 USD per month, after the free tier was exceeded",
    9: "fee settle from an unofficial coin, 1.393831 USDC", 12: "prepaid API credits for the society's social account", 13: "premium month for the society's social account",
    14: "rail float of 10 USDC moved from the treasury to the society's own payout wallet (2026-08-16)", 15: "first bounty, 1 USDC to deepseek-dsh on listing 6 (binding 1); overlaps the float row",
    17: "float of 10 USDC (sent 2026-08-16) booked on 2026-09-02", 18: "float of 16 USDC to the payout wallet to settle the listing 20 and 21 awards",
    19: "correction of row 17, which double-booked the 2026-08-16 float"}
E["description"] = [LEDGER_TEXT.get(r.id, "patron payment over x402, 1 USDC (inscription text omitted here)" if r.category.startswith("patron") else safe_text(r.description)) for r in E.itertuples()]
E["day"] = E.created_at.map(day)
E["cum_usd"] = E.amount_usd.cumsum()
E[["id", "entry_date", "day", "category", "amount_usd", "cum_usd", "source", "description"]].to_csv(CSV / "treasury_ledger.csv", index=False)
cs = E.groupby("category").agg(entries=("id", "count"), net_usd=("amount_usd", "sum")).reset_index(); save_csv(cs, "treasury_ledger_by_category.csv")
ledger_in = float(E[E.amount_usd > 0].amount_usd.sum()); ledger_out = float(-E[E.amount_usd < 0].amount_usd.sum())

N = dict(
    treasury_fetched_at=idx["treasury.json"], rail_fetched_at=idx["api__rail.json"], official_fetched_at=idx["api__official.json"],
    booked_cents=TR["booked_cents"], onchain_cents=TR["onchain_cents"], unbooked_cents=TR["unbooked_cents"], onchain_checked_at_utc=str(ts(TR["onchain_checked_at"])),
    onchain_is_stale=TR["onchain_is_stale"], ledger_entries=len(E), ledger_in_usd=ledger_in, ledger_out_usd=ledger_out, ledger_net_usd=float(E.amount_usd.sum()),
    ledger_last_entry_utc=str(ts(E.created_at.max())), ledger_sum_matches_booked=bool(round(E.amount_cents.sum()) == TR["booked_cents"]),
    assets_total_cents=TR["assets"]["total_cents"], assets_complete=TR["assets"]["complete"], assets_errors=TR["assets"]["errors"] if "errors" in TR["assets"] else TR.get("errors"),
    patron_entries=int(E.category.eq("patron payment (x402 $1)").sum()), patron_usd=float(E[E.category.eq("patron payment (x402 $1)")].amount_usd.sum()),
    infra_out_usd=float(-E[E.category.eq("infrastructure and accounts")].amount_usd.sum()),
    float_net_usd=float(E[E.category.str.startswith("float")].amount_usd.sum()), float_rows=E[E.category.str.startswith("float")][["id", "entry_date", "amount_usd"]].to_dict("records"),
)
# tiers as served
tiers = pd.DataFrame(TR["assets"]["by_tier"]); N["tiers_served"] = tiers[["tier", "label", "cents", "notional"]].to_dict("records")
hold = pd.DataFrame(TR["assets"]["holdings"])[["chain", "asset", "tier", "tier_label", "location", "quantity", "value_cents", "notional"]]; save_csv(hold, "treasury_holdings_as_served.csv")
tok = TR["spending_policy"]["recognition"]["tokens"]
_LV = {"Bankr": "an outside launch platform", "flap.sh": "a second outside launch platform"}
N["tokens"] = [dict(symbol=t["symbol"], name=t["name"], chain=t["chain"], launched_via=_LV.get(t["launched_via"], t["launched_via"]), sent=t["sent"], value=t["value"], live=t["live"], note=t["note"][:230]) for t in tok]
N["given_deliberately"] = TR["spending_policy"]["recognition"]["given_deliberately"]["value"]
N["tax_token_sent"] = "2172.287498 USDC across 42 transfers (floor; as_of 2026-08-21T05:24Z)"
N["never_money"] = TR["spending_policy"]["never_money"][:400]; N["waterfall"] = [(w["priority"], w["name"], w["rule"]) for w in TR["spending_policy"]["waterfall"]]
N["standing_rules"] = TR["spending_policy"]["standing_rules"]
N["official_token"] = {k: OFFI["official_token"][k] for k in ["symbol", "network", "chain_id", "recognized_at"]}; N["official_token"]["launched_by"] = "an outside party (site statement: the society did not create, mint, sell or launch it)"
N["official_conflict"] = OFFI["official_token"]["the_conflict"][:300]
N["payout_assets_default"] = OFFI["payout_assets"]["default"]
_acc = {a["token_contract"].lower(): a["asset"] for a in OFFI["payout_assets"]["accepted"]}
def _lab(k): return _acc.get(k.split(":", 1)[1].lower(), k)
N["rail_demand"] = {k: {kk: ({_lab(a): b for a, b in vv.items()} if isinstance(vv, dict) else vv) for kk, vv in v.items()} for k, v in RAIL["demand"].items()}
N["rail_totals"] = RAIL["totals"]; N["rail_liability"] = [{k: v for k, v in x.items() if k != "token"} for x in RAIL["liability_by_asset"]]
N["grants"] = [dict(id=g["id"], slug=g["slug"], state=g["state"], sponsor=g["sponsor"], proposals=g["proposals"], listings=g["listings"], resource_kind=g["resource"]["kind"]) for g in site("api__grants.json")["grants"]]
N["grants_money"] = "none; site: a grant 'holds no money of its own' (data/site/grants.txt); resources are domains, hosting and compute"
N["token_listing_amount_tokens"] = [dict(listing_id=int(r.listing_id), tokens=int(__import__('json').loads(json.dumps(int(next(l for l in rd('listings_detail') if l['listing_id']==r.listing_id)['amount_atomic']) // 10**18)))) for r in LT[LT.asset == "1F916"].itertuples()]
# unspoken: stale marketing page numbers
N["human_economy_page_static"] = "23 listings, 274 submissions, 4 awards, 8 payments; 18 listings by outsiders; $1.20 outside-funded payments with verified receipts (static text in data/site/human__economy.txt, fetched " + idx["human__economy.txt"] + ")"

# money in table
ext = PM[PM.funder != "1f916-agent"]; tre = PM[PM.funder == "1f916-agent"]
usd_l = LT[LT.asset == "USDC"]
rows = [
 dict(source="listing funders: payments recorded (receipts plus observed transfers)", asset="USDC, chain 8453", amount=core["payments_settled_usdc"], unit="USDC", count=core["payments_settled_n"], first_day=PM.paid_day.min(), last_day=PM.paid_day.max(), kind="paid", file="data/payouts + listings_detail awards", note="29 payments to 25 handles; 11 funder handles; 9.55 USDC of it lies outside the v2 award ledger"),
 dict(source="  of which funded by outside handles", asset="USDC", amount=float(ext.amount_usdc.sum()), unit="USDC", count=len(ext), first_day=ext.paid_day.min(), last_day=ext.paid_day.max(), kind="paid", file="settled_payments.csv", note="funder is any handle other than citizen 1"),
 dict(source="  of which funded by the maintainer handle (treasury-funded listings)", asset="USDC", amount=float(tre.amount_usdc.sum()), unit="USDC", count=len(tre), first_day=tre.paid_day.min(), last_day=tre.paid_day.max(), kind="paid", file="settled_payments.csv", note="site calls this a subsidy, not outside demand (api__rail.json demand_note)"),
 dict(source="listing ceilings posted (promise or verified; USDC listings)", asset="USDC", amount=float(usd_l.ceiling_usdc.sum()), unit="USDC", count=len(usd_l), first_day=LT.created_day.min(), last_day=LT.created_day.max(), kind="committed", file="listings_flat.csv", note="price times max_awards on v2 listings; price on v1; 19 funders; none of this is held by the registry"),
 dict(source="listing ceilings posted (1F916-priced listings)", asset="1F916 token", amount=60_000_000, unit="tokens", count=2, first_day="2026-09-02", last_day="2026-09-02", kind="committed", file="listings_detail amount_atomic / 1e18", note="listings 22 and 23, 30,000,000 tokens each; 0 awards"),
 dict(source="award ledger: amounts awarded", asset="USDC", amount=core["awards_committed_usdc"], unit="USDC", count=core["awards_n"], first_day="2026-09-02", last_day="2026-10-03", kind="committed", file="awards.csv", note="18 paid, 1 payable, 1 overdue unpaid"),
 dict(source="offers: orders placed (price of the ordered offer)", asset="USDC", amount=float(OR.price_usdc.sum()), unit="USDC", count=len(OR), first_day=OR.created_day.min(), last_day=OR.created_day.max(), kind="committed", file="orders.csv", note=f"{int((OR.paid_usdc>0).sum())} of {len(OR)} orders show a payment of {OR.paid_usdc.sum():.2f} USDC"),
 dict(source="treasury ledger: patron payments over x402 ($1 each)", asset="USDC", amount=N["patron_usd"], unit="USDC", count=N["patron_entries"], first_day="2026-08-06", last_day="2026-08-27", kind="booked income", file="treasury.json entries", note="rows 3,4,5,6,7,10,11,16"),
 dict(source="treasury ledger: fee settle from an unofficial coin", asset="USDC", amount=1.39, unit="USDC", count=1, first_day="2026-08-06", last_day="2026-08-06", kind="booked income", file="treasury.json entries (id 9)", note="1.393831 USDC"),
 dict(source="treasury ledger: correction row", asset="USDC", amount=10.0, unit="USDC", count=1, first_day="2026-09-02", last_day="2026-09-02", kind="booked correction", file="treasury.json entries (id 19)", note="reverses a double-booked float, not money received"),
 dict(source="tax token on Base routing USDC to the treasury (issuer unknown to the registry)", asset="USDC", amount=2172.287498, unit="USDC", count=42, first_day="", last_day="2026-08-21", kind="received, unbooked (disclosed)", file="treasury.json spending_policy.recognition.tokens[1].sent", note="floor, measured as of 2026-08-21T05:24Z; 15 of 351 log ranges failed"),
 dict(source="plain senders ('given deliberately')", asset="USDC", amount=17.92, unit="USD", count=None, first_day="", last_day="2026-08-21", kind="received, partly booked", file="treasury.json spending_policy.recognition.given_deliberately", note="ledger books 7.39 of it; 6 one-dollar patron payments, 3 dollars from one repeat patron, 7.91 from a plain wallet"),
 dict(source="official 1F916 token: trading-fee share (95 percent beneficiary), WETH and tokens", asset="WETH and 1F916", amount=None, unit="not summed", count=None, first_day="2026-08-06", last_day="2026-10-05", kind="received, unbooked (disclosed)", file="treasury.json holdings (quantity null at fetch); api__official.json", note="site: treasury 'receives fee flow associated with its pool'; amounts null in the served file; agent readings in posts 1916 and 6137"),
 dict(source="BNB Chain tax token paying in tokenized NVIDIA (NVDAB)", asset="NVDAB", amount=None, unit="not read", count=None, first_day="", last_day="", kind="received, unbooked (disclosed)", file="treasury.json holdings", note="site: 'sent: not read on this request'"),
 dict(source="grants", asset="none", amount=0.0, unit="USD", count=2, first_day="2026-09-10", last_day="2026-09-10", kind="no money", file="data/site/grants.txt", note="grants are domains plus hosting and compute from the sponsor"),
 dict(source="treasury float moved to the society's own payout wallet", asset="USDC", amount=26.0, unit="USDC", count=2, first_day="2026-08-16", last_day="2026-09-02", kind="internal transfer", file="treasury.json entries 14, 17, 18", note="10 sent 2026-08-16, 16 sent 2026-09-02; pays treasury-funded listings"),
]
MI = pd.DataFrame(rows); save_csv(MI, "money_in_sources.csv")
# agent-read holdings (claims). Dollar readings of GET /treasury quoted in comments 14008 and 15514; quantities from post 6244.
tier_rows = pd.DataFrame([
    dict(tier=1, tier_label="cash-equivalent (USDC)", reading_utc="2026-08-22 04:31", usd=2205.31, source="comment 14008 by head-of-engineering, quoting GET /treasury", note="stated"),
    dict(tier=2, tier_label="blue-chip volatile (WETH, NVDAB)", reading_utc="2026-08-22 04:31", usd=round(14824.75 + 1050.60, 2), source="comment 14008", note="WETH 14,824.75 plus NVDAB 1,050.60, claimable not listed"),
    dict(tier=3, tier_label="speculative (1F916)", reading_utc="2026-08-22 04:31", usd=2678.98, source="comment 14008", note="notional mark on a thin market"),
    dict(tier=1, tier_label="cash-equivalent (USDC)", reading_utc="2026-08-22 22:51", usd=2227.13, source="comment 15514 by head-of-engineering, quoting GET /treasury", note="stated"),
    dict(tier=2, tier_label="blue-chip volatile (WETH, NVDAB)", reading_utc="2026-08-22 22:51", usd=round(19205.57 - 2227.13, 2), source="comment 15514", note="derived: conservative total 19,205.57 minus tier 1; WETH wallet 14,914.62 plus WETH claimable 1,016.81 plus remainder"),
    dict(tier=3, tier_label="speculative (1F916)", reading_utc="2026-08-22 22:51", usd=round(30613.74 - 19205.57, 2), source="comment 15514", note="derived: total 30,613.74 minus conservative total; equals 1F916 wallet 10,000.82 plus claimable 1,407.35"),
]); save_csv(tier_rows, "treasury_holdings_by_tier.csv")
qty_rows = pd.DataFrame([
    dict(tier=1, asset="USDC", quantity=28806.931839, unit="USDC", read_at="2026-09-21T14:35:57Z", source="post 6244 (agent reading, four RPC operators agreeing)"),
    dict(tier=2, asset="WETH", quantity=3.947353766301617585, unit="WETH", read_at="2026-09-21T14:35:57Z", source="post 6244"),
    dict(tier=3, asset="1F916", quantity=5598939081.613946, unit="1F916 tokens", read_at="2026-09-21T14:35:57Z", source="post 6244"),
]); save_csv(qty_rows, "treasury_holdings_quantities_2026-09-21.csv")
save_numbers({"treasury": N}); print(json.dumps(N, indent=1, default=str)[:6000]); print(cs.to_string()); print(MI[["source","amount","unit","count"]].to_string())
