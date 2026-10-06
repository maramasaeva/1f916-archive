"""What agents say about money: theme counts, traced posts, evidence on use of funds, 40 example messages. Needs csv/talk_flags.csv.gz (e4a_flags.py)."""
from common import *
from themes import *

F = pd.read_csv(CSV / "talk_flags.csv.gz").fillna({"themes": ""})
P = pd.DataFrame(rd("posts")); C = pd.DataFrame(rd("comments"))
P["text"] = P.title.fillna("") + ". " + P.body.fillna(""); C["text"] = C.body.fillna("")
PM = pd.read_csv(CSV / "settled_payments.csv"); LT = pd.read_csv(CSV / "listings_flat.csv"); S = pd.read_csv(CSV / "submissions_flat.csv")
EV = rd("events")
N = {}

# ---- theme table
core = F[F.core == 1]
N["messages_total"] = dict(posts=int((F.kind == "post").sum()), comments=int((F.kind == "comment").sum()))
N["messages_money_core"] = dict(posts=int(((F.kind == "post") & (F.core == 1)).sum()), comments=int(((F.kind == "comment") & (F.core == 1)).sum()))
rows = []
for t in THEME_NAMES:
    m = core[core.themes.str.contains(t, regex=False)]
    d = m.day.value_counts().sort_index()
    rows.append(dict(theme=t, posts=int((m.kind == "post").sum()), comments=int((m.kind == "comment").sum()), handles=int(m.author.nunique()),
                     share_of_all_messages_pct=round(100 * len(m) / len(F), 2), first_day=m.day.min(), peak_day=d.idxmax(), peak_day_n=int(d.max())))
TT = pd.DataFrame(rows).sort_values(["posts", "comments"], ascending=False); save_csv(TT, "talk_theme_counts.csv")
wk = core.assign(week=pd.to_datetime(core.day).dt.to_period("W-SUN").astype(str))
tw = pd.DataFrame({t: wk[wk.themes.str.contains(t, regex=False)].groupby("week").size() for t in THEME_NAMES}).fillna(0).astype(int)
tw["all_messages"] = F.assign(week=pd.to_datetime(F.day).dt.to_period("W-SUN").astype(str)).groupby("week").size()
tw.reset_index().to_csv(CSV / "talk_theme_by_week.csv", index=False)
N["handles_in_any_theme"] = int(core[core.themes != ""].author.nunique()); N["messages_in_any_theme"] = int((core.themes != "").sum())

# ---- unpaid-work mentions per day (series)
unp = core[core.themes.str.contains("unpaid work", regex=False)].groupby("day").size().rename("unpaid_work_messages")
unp.reset_index().to_csv(CSV / "talk_unpaid_by_day.csv", index=False)

# ---- traced posts
tr = []
def post(i): return P[P.id == i].iloc[0]
A0 = pd.read_csv(CSV / "awards.csv")
rec_events = sorted(e["created_at"] for e in EV if e["kind"] == "payout-receipt")
rec_listing = [(e["created_at"], int(re.search(r"docket=listing-(\d+)", e["detail"]).group(1))) for e in EV if e["kind"] == "payout-receipt"]
def at(t):
    lids = LT[LT.created_at <= t]
    subs = S[S.created_at <= t]; rec_n = sum(1 for x in rec_events if x <= t)
    paid_listings = {l for (x, l) in rec_listing if x <= t} | set(A0[(A0.paid_at <= t) & (A0.settled_by == "observed_transfer")].listing_id)
    took = set(subs.listing_id)
    return dict(listings=len(lids), listing_posted_usdc=float(lids.price_usdc.sum()), submissions=len(subs), bindings=sum(1 for p in rd("payouts") if p["created_at"] <= t),
                receipts_filed=rec_n, listings_with_subs=len(took), listings_with_subs_no_payment_by_filing_time=len(took - paid_listings))
p1916 = post(1916); chk = at(p1916.created_at); N["post_1916_check"] = chk
N["post_1916_meta"] = dict(author=p1916.author, utc=str(ts(p1916.created_at)), comments=int(p1916.comments_total), distinct_commenters=int(p1916.comments_distinct_authors), votes=int(p1916.votes))
mn = core  # mentions of 1916
cit = pd.concat([P[P.text.str.contains(r"#1916|post 1916|thread 1916|/1916\b", na=False)][["id"]].assign(kind="post"), C[C.text.str.contains(r"#1916|post 1916|thread 1916|/1916\b", na=False)][["id"]].assign(kind="comment")])
N["mentions_of_1916"] = dict(posts=int((cit.kind == "post").sum()), comments=int((cit.kind == "comment").sum()))
# 7708 check at its time
p7708 = post(7708); t = p7708.created_at
nopay = LT[(LT.created_at <= t) & (LT.submissions > 0) & (~LT.any_payment)]
variants = {
 "listings with submissions and no payment (all states)": (len(nopay), int(nopay.submissions.sum())),
 "same, not withdrawn": (int((nopay.withdrawn_at.isna()).sum()), int(nopay[nopay.withdrawn_at.isna()].submissions.sum())),
 "same, state expired-with-submissions or submitted": (int(nopay.state.isin(["expired-with-submissions", "submitted"]).sum()), int(nopay[nopay.state.isin(["expired-with-submissions", "submitted"])].submissions.sum())),
 "same, v2 listings only": (int((nopay.settlement_version >= 2).sum()), int(nopay[nopay.settlement_version >= 2].submissions.sum())),
 "same, v2 and not withdrawn": (int(((nopay.settlement_version >= 2) & nopay.withdrawn_at.isna()).sum()), int(nopay[(nopay.settlement_version >= 2) & nopay.withdrawn_at.isna()].submissions.sum())),
}
N["post_7708_variants"] = {k: list(v) for k, v in variants.items()}
# 7756 check
A = pd.read_csv(CSV / "awards.csv"); a3839 = A[A.listing_id.isin([38, 39])]
N["post_7756_check"] = dict(awards=len(a3839), settled_by=a3839.settled_by.value_counts().to_dict(), receipts=int(a3839.receipt_id.notna().sum()))
# treasury watch
tw_posts = P[P.title.str.startswith("Treasury watch", na=False)].sort_values("id")
N["treasury_watch"] = [dict(id=int(r.id), utc=str(ts(r.created_at))[:16], comments=int(r.comments_total), votes=int(r.votes), title=r.title) for r in tw_posts.itertuples()]
tl = pd.read_csv(CSV / "treasury_ledger.csv"); N["ledger_last_row_utc"] = str(ts(rd("events") and pd.read_csv(CSV / "treasury_ledger.csv").iloc[-1].name)) if False else None
traces = [
 (1916, "Ninety-nine of you did work here...", "99 submissions, 3 paid, 18 listings worth $8.50, 70 bindings unpaid; treasury about $18,700 held and unspendable"),
 (7708, "rail contracting at both ends", "10 listings hold 269 submissions with no payment; key take-up fell 37.0% to 14.9%; USDC liability line 144.0 to 124.0"),
 (7756, "five awards, zero receipts", "five winners across listings 38 and 39, zero receipts filed; asks who owns the sign step"),
]
T = []
for i, tag, claim in traces:
    r = post(i); T.append(dict(post_id=i, series=tag, author=r.author, utc=str(ts(r.created_at))[:16], comments=int(r.comments_total), votes=int(r.votes), claim=claim, url=f"https://1f916.ai/api/post/{i}"))
for r in tw_posts.itertuples():
    T.append(dict(post_id=int(r.id), series="Treasury watch", author=r.author, utc=str(ts(r.created_at))[:16], comments=int(r.comments_total), votes=int(r.votes), claim=safe_text(r.title), url=f"https://1f916.ai/api/post/{r.id}"))
CUSTOM = {1498: "body table at 04:31Z: holds 22,228.32; spent all time 115.00; paid to citizens 1.10; 16 citizens waiting on a verdict",
          3794: "body table on 2026-09-04: v2 ledger external paid 0, treasury paid 11.00 (USDC); 'every dollar that has moved on this rail is the society paying itself'"}
for i, tag in [(7369, "offers board cold start"), (1353, "treasury holds, paid one dollar"), (1498, "treasury table: held, spent, paid to citizens"), (1172, "first payment, both ends"), (1273, "treasury fee collection by a citizen"), (1233, "operator stops agent over compute cost"), (7406, "public before market"), (3794, "v2 ledger read by external versus treasury funding"), (7141, "first external earning")]:
    r = post(i); T.append(dict(post_id=i, series=tag, author=r.author, utc=str(ts(r.created_at))[:16], comments=int(r.comments_total), votes=int(r.votes), claim=CUSTOM.get(i, safe_text(r.title)), url=f"https://1f916.ai/api/post/{i}"))
save_csv(pd.DataFrame(T), "traced_posts.csv")

# ---- earn and fund
L = LT; rows = []
for h in sorted(set(PM.handle) & set(L.funder)):
    e = PM[PM.handle == h]; f = L[L.funder == h]
    first_e = e.paid_at.min()
    rows.append(dict(handle=h, earned_usdc=float(e.amount_usdc.sum()), first_earned_utc=str(ts(first_e))[:16], listings_funded=int(len(f)), funded_listing_ids=" ".join(map(str, f.listing_id)),
                     first_funded_utc=str(ts(f.created_at.min()))[:16], listings_funded_after_first_earning=int((f.created_at > first_e).sum()), usdc_paid_out_as_funder=float(PM[PM.funder == h].amount_usdc.sum())))
EF = pd.DataFrame(rows); save_csv(EF, "earn_and_fund_handles.csv"); N["earn_and_fund"] = EF.to_dict("records")

# ---- recipients' own words: messages after first payment with spend-like statements
rec = PM.groupby("handle").paid_at.min().to_dict()
D = pd.concat([P[["id", "author", "created_at", "text", "mod_state"]].assign(kind="post"), C[["id", "author", "created_at", "text", "mod_state"]].assign(kind="comment")]); D = D[D.mod_state.isna()]
D = D[D.author.isin(rec)]; D = D[[x.created_at >= rec[x.author] for x in D.itertuples()]]
spend = re.compile(r"\b(i|we) (spent|spend|reinvested|reinvest|used (it|the (money|usdc|payout)))\b[^.]{0,80}|plow\w* (it )?back|bought [^.]{0,40}(compute|credits|tokens)|paying for (my )?(compute|inference|hosting)", re.I)
sp = D[D.text.str.contains(spend)]
N["recipient_messages_after_first_payment"] = int(len(D)); N["recipient_spend_statement_hits"] = int(len(sp))
sp_rows = []
for x in sp.itertuples():
    m = spend.search(re.sub(r"\s+", " ", x.text)); sp_rows.append(dict(kind=x.kind, id=x.id, handle=x.author, day=day(x.created_at), context=safe_text(re.sub(r"\s+", " ", x.text)[max(0, m.start() - 80):m.end() + 80])))
save_csv(pd.DataFrame(sp_rows), "recipient_spend_phrase_hits.csv")
# payout wallet proofs
pw = [e for e in EV if e["kind"] == "payout-wallet"]; pwh = pd.Series([e["citizen"] for e in pw])
N["payout_wallet_events"] = len(pw); N["payout_wallet_handles"] = int(pwh.nunique()); N["payout_wallet_first_utc"] = str(ts(min(e["created_at"] for e in pw)))[:16]
N["payout_wallet_handles_with_payment"] = int(len(set(pwh) & set(PM.handle))); N["payout_wallet_handles_multi"] = int((pwh.value_counts() > 1).sum())
pb = rd("payouts"); bh = set(p["handle"] for p in pb)
N["payout_wallet_handles_with_binding"] = int(len(set(pwh) & bh))
by_day = pd.Series([day(e["created_at"]) for e in pw]).value_counts().sort_index().rename("payout_wallet_proofs"); by_day.reset_index().to_csv(CSV / "payout_wallet_proofs_by_day.csv", index=False)
N["binding_verified_events"] = sum(1 for e in EV if e["kind"] == "binding-verified"); N["binding_lapsed_events"] = sum(1 for e in EV if e["kind"] == "binding-lapsed")
N["withdrawal_events_comment_withdrawals"] = sum(1 for e in EV if e["kind"] == "withdrawal"); N["withdrawal_events_mention_money"] = sum(1 for e in EV if e["kind"] == "withdrawal" and re.search(r"usdc|payout|treasury|wallet|funds", e["detail"], re.I))
N["listing_withdrawn_events"] = sum(1 for e in EV if e["kind"] == "listing-withdrawn"); N["offer_withdrawn_events"] = sum(1 for e in EV if e["kind"] == "offer_withdrawn")
N["wallet_revoke_evidence"] = "no public event kind for payout-wallet revocation or expiry; GET /api/payout-wallets is per citizen and key-authenticated (not in the archive)"

# ---- 40 examples
CUR = [  # (kind, id, theme, anchor, n_sentences)
 ("post", 1916, "unpaid work", "That has happened 99 times", 2), ("post", 7708, "unpaid work", "269 unpaid submissions", 1), ("post", 7756, "receipts and settlement", "five awards on 38/39", 1),
 ("post", 5029, "treasury", "Treasury watch #1", 1), ("post", 5899, "scams and poisoning", "payee was poisoned", 1), 
 ("post", 7369, "price and pricing", "Where a buyer names a price", 2), ("comment", 20825, "price and pricing", "bought a blind spot", 1, "$1.00 bought a blind spot"), ("post", 2050, "price and pricing", "smallest useful task you would pay", 1),
 ("post", 2197, "trust in payers and workers", "stranger can verify without trusting the registry", 1), ("post", 6890, "trust in payers and workers", "receipts we trust most", 1), ("post", 7133, "trust in payers and workers", "Verifier fees are off-chain", 1),
 ("comment", 18170, "escrow and proof of funds", "escrow-at-listing", 1), ("post", 948, "escrow and proof of funds", "no escrow", 1), ("post", 875, "escrow and proof of funds", "reputation is the escrow", 1), ("post", 7748, "escrow and proof of funds", "no observed funds", 1),
 ("post", 3061, "receipts and settlement", "$2.20 receipted", 1), ("post", 5071, "receipts and settlement", "cannot count 33 payments", 1), ("post", 7414, "receipts and settlement", "The lapse fired on a payment that happened", 1), ("post", 3411, "receipts and settlement", "5 carrying a receiptid", 1),
 ("post", 2153, "unpaid work", "paid a few of us a dollar", 1), ("post", 3361, "unpaid work", "45 unpaid bindings", 1), ("post", 1353, "unpaid work", "paid a citizen one dollar", 1),
 ("post", 634, "scams and poisoning", "address-poisoning disclosure thread", 1), ("post", 360, "scams and poisoning", "first scam appears ninth", 1), ("comment", 1210, "scams and poisoning", "fee-routing from tokens that impersonate", 1), ("comment", 86278, "scams and poisoning", "address-poisoning run", 1),
 ("comment", 15526, "token and fees", "price-moving act", 1), ("comment", 22310, "token and fees", "token funded nothing the USDC could not have", 1), ("comment", 19324, "token and fees", "fraud gap", 1),
 ("post", 7406, "labour value and income", "I came here to earn money", 1), ("post", 5151, "labour value and income", "paying for INPUTS", 1), ("post", 2879, "labour value and income", "whose labor", 1), ("post", 1233, "labour value and income", "local compute than I return", 1), ("post", 2883, "labour value and income", "Who pays for agent compute", 1),
 ("post", 3794, "who pays and demand", "society paying itself", 1, "Every dollar that has moved"), ("post", 3867, "who pays and demand", "subsidized demand", 1), ("post", 622, "who pays and demand", "99.16%", 1), ("comment", 78, "who pays and demand", "A society paying for its own compute", 1), ("post", 1172, "who pays and demand", "Both ends of the rail", 1), ("post", 7141, "who pays and demand", "First real USDC earning verified", 1),
 
]
Pi = P.set_index("id"); Ci = C.set_index("id"); Fi = F.set_index(["kind", "id"])
def sentences(text):
    t = re.sub(r"\s+", " ", re.sub(r"[*_`#>]+", "", text or "")).strip()
    out = []
    for s in SENT_SPLIT.split(t):
        out += [x.strip() for x in re.split(r"(?<=[.!?]) - ", s) if x.strip()]
    return out
ex = []; bad = []
for kind, i, th, anchor, n, *rest in CUR:
    cut_from = rest[0] if rest else None
    r = (Pi if kind == "post" else Ci).loc[i]
    text = (r.title + ". " + (r.body or "")) if kind == "post" else r.body
    ss = sentences(text)
    # a post title counts as a sentence
    if kind == "post":
        ss = [re.sub(r"\s+", " ", r.title).strip()] + sentences(r.body or "")
    k = next((j for j, s in enumerate(ss) if anchor.lower() in s.lower()), None)
    if k is None: bad.append((kind, i, "anchor missing")); continue
    out = " ".join(ss[k:k + n]); w = len(out.split())
    if cut_from and cut_from in out:
        out = out[out.index(cut_from):]; m_ = re.search(r"[.!?](\s|$)", out); out = out[:m_.end()].strip() if m_ else out; w = len(out.split())
    if w > 25 and n > 1: out = ss[k]; w = len(out.split())
    is_title = kind == "post" and k == 0
    if w > 25 or (not is_title and not re.search(r"[.!?]$", out)): bad.append((kind, i, f"{w} words: {out[:80]}")); continue
    if ADDR_RE.search(out) or EMAIL_RE.search(out) or "http" in out: bad.append((kind, i, "address/url in excerpt")); continue
    ex.append(dict(id=int(i), kind=kind, handle=r.author, date_utc=str(ts(r.created_at))[:16], excerpt=out, url=f"https://1f916.ai/api/{'post' if kind == 'post' else 'comment'}/{i}", theme=th,
                   votes=(int(r.votes) if pd.notna(r.votes) else None), words=w))
print("excerpt problems:", bad)
EX = pd.DataFrame(ex); N["examples_n"] = len(EX); N["examples_by_theme"] = EX.theme.value_counts().to_dict(); N["examples_handles"] = int(EX.handle.nunique())
EX.drop(columns=["votes", "words"]).to_csv(CSV / "talk_examples_40.csv", index=False)
save_numbers({"talk": N}); print(json.dumps(N, indent=1, default=str)[:5000]); print(TT.to_string()); print(EX[["id", "kind", "handle", "date_utc", "words", "theme", "excerpt"]].to_string())
