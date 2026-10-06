"""Figures (SVG) and the CSV behind each one. White ground, dark grey text, one accent, greys, direct labels, flat titles."""
from common import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ACC = "#b3401d"; G1 = "#333333"; G2 = "#777777"; G3 = "#aaaaaa"; G4 = "#dddddd"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 7.5,
                     "axes.edgecolor": G2, "axes.labelcolor": G1, "xtick.color": G1, "ytick.color": G1, "text.color": G1, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2.5, "ytick.major.size": 2.5, "figure.facecolor": "white", "axes.facecolor": "white",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 8.5, "axes.titleweight": "normal", "axes.titlelocation": "left", "axes.grid": False})
FIGS = []

def start(w=7.0, h=3.6):
    fig, ax = plt.subplots(figsize=(w, h), dpi=100); fig.subplots_adjust(left=0.10, right=0.93, top=0.88, bottom=0.17); return fig, ax

def done(fig, stem, title, desc, df, n, ax=None):
    if ax is not None: ax.set_title(title, loc="left", pad=8, color=G1)
    fig.savefig(FIG / f"{stem}.svg", format="svg", facecolor="white")
    if os.environ.get("FIG_PNG"): fig.savefig(os.environ["FIG_PNG"] + f"/{stem}.png", dpi=110, facecolor="white")
    plt.close(fig)
    df.to_csv(FIG / f"{stem}.csv", index=False)
    FIGS.append(dict(file=f"figures/{stem}.svg", title=title, description=desc, source_csv=f"figures/{stem}.csv", n=int(n)))

T = pd.read_csv(CSV / "timeline_by_day.csv", parse_dates=["day"]); A = pd.read_csv(CSV / "awards.csv"); PM = pd.read_csv(CSV / "settled_payments.csv")
LT = pd.read_csv(CSV / "listings_flat.csv"); R = pd.read_csv(CSV / "recipients.csv"); FU = pd.read_csv(CSV / "funders.csv"); OFD = pd.read_csv(CSV / "offers_flat.csv")
OC = pd.read_csv(CSV / "offer_categories.csv"); LC = pd.read_csv(CSV / "listing_categories.csv"); TL = pd.read_csv(CSV / "treasury_ledger.csv", parse_dates=["day"])
TH = pd.read_csv(CSV / "treasury_holdings_by_tier.csv"); UN = pd.read_csv(CSV / "talk_unpaid_by_day.csv", parse_dates=["day"]); TTC = pd.read_csv(CSV / "talk_theme_counts.csv")
RULES = pd.read_csv(CSV / "rule_change_dates.csv")
fmt = mdates.DateFormatter("%d %b")

# 1 cumulative
d = T[T.day >= "2026-08-15"][["day", "cum_listing_ceiling_usdc", "cum_awards_usdc", "cum_payments_usdc"]]
fig, ax = start()
ax.step(d.day, d.cum_listing_ceiling_usdc, where="post", color=G3, lw=1.2); ax.step(d.day, d.cum_awards_usdc, where="post", color=G2, lw=1.2); ax.step(d.day, d.cum_payments_usdc, where="post", color=ACC, lw=1.6)
x1 = d.day.iloc[-1] + pd.Timedelta(days=0.8)
ax.text(x1, d.cum_listing_ceiling_usdc.iloc[-1], f"posted ceiling {d.cum_listing_ceiling_usdc.iloc[-1]:.1f}", color=G2, va="center", fontsize=7)
ax.text(x1, d.cum_awards_usdc.iloc[-1] + 9, f"awarded {d.cum_awards_usdc.iloc[-1]:.1f}", color=G2, va="center", fontsize=7)
ax.text(x1, d.cum_payments_usdc.iloc[-1] - 9, f"paid {d.cum_payments_usdc.iloc[-1]:.2f}", color=ACC, va="center", fontsize=7)
ax.annotate("one 100 USDC listing, no payment", (pd.Timestamp("2026-08-24"), 108.5), xytext=(pd.Timestamp("2026-08-27"), 150), fontsize=6.5, color=G2, arrowprops=dict(arrowstyle="-", color=G3, lw=0.5))
ax.set_xlim(d.day.iloc[0], d.day.iloc[-1] + pd.Timedelta(days=11)); ax.xaxis.set_major_formatter(fmt); ax.set_ylabel("USDC, cumulative"); ax.set_xlabel("date, 2026 (UTC)")
done(fig, "fig01_cumulative_posted_awarded_paid", "USDC posted, awarded and paid, cumulative, 16 Aug to 5 Oct 2026",
     "Listing ceilings reached 320.90 USDC, awards 65.80 USDC and payments recorded on chain 69.35 USDC by 5 Oct.", d.rename(columns={"cum_listing_ceiling_usdc": "posted_ceiling_usdc", "cum_awards_usdc": "awarded_usdc", "cum_payments_usdc": "paid_usdc"}), len(d), ax)

# 2 awards and payments per day
d = T[T.day >= "2026-08-15"][["day", "awards", "payments"]]
fig, ax = start(); ax.bar(d.day - pd.Timedelta(hours=5), d.awards, width=0.4, color=G3, label="awards"); ax.bar(d.day + pd.Timedelta(hours=5), d.payments, width=0.4, color=ACC, label="payments recorded")
ax.text(0.02, 0.93, "awards", color=G2, transform=ax.transAxes); ax.text(0.02, 0.85, "payments recorded", color=ACC, transform=ax.transAxes)
ax.xaxis.set_major_formatter(fmt); ax.set_ylabel("count per day"); ax.set_xlabel("date, 2026 (UTC)")
done(fig, "fig02_awards_payments_per_day", "Awards and recorded payments per day, 16 Aug to 5 Oct 2026", "Awards were made on 12 days and payments recorded on 16 days; the largest single day had 4 payments.", d, len(d), ax)

# 3 award sizes
a = A.dropna(subset=["amount_usdc"]).groupby("amount_usdc").agg(awards=("award_id", "count"), paid=("state", lambda s: (s == "paid").sum())).reset_index()
fig, ax = start(7, 3.2); xs = np.arange(len(a)); ax.bar(xs, a.awards, color=G3, width=0.6); ax.bar(xs, a.paid, color=ACC, width=0.6)
for x, v in zip(xs, a.awards): ax.text(x, v + 0.1, str(v), ha="center", fontsize=7)
ax.set_xticks(xs); ax.set_xticklabels([f"{v:g}" for v in a.amount_usdc]); ax.set_xlabel("award amount (USDC)"); ax.set_ylabel("awards"); ax.text(0.98, 0.9, "dark: paid, grey: not paid", ha="right", transform=ax.transAxes, color=G2)
done(fig, "fig03_award_size_distribution", "Distribution of award sizes, 20 awards, median 2.00 USDC", "Awards range from 0.10 to 10.00 USDC; 18 of 20 are paid.", a, int(a.awards.sum()), ax)

# 4 Lorenz recipients
x = np.sort(R.paid_usdc.values); cum = np.insert(np.cumsum(x) / x.sum(), 0, 0); p = np.linspace(0, 1, len(cum))
fig, ax = start(4.6, 4.2); fig.subplots_adjust(left=0.13, right=0.95, top=0.90, bottom=0.14)
ax.plot([0, 1], [0, 1], color=G3, lw=0.8); ax.plot(p, cum, color=ACC, lw=1.6, drawstyle="steps-post")
ax.set_xlabel("share of recipients (poorest first)"); ax.set_ylabel("share of USDC paid"); ax.set_aspect("equal"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
g = gini(R.paid_usdc); ax.text(0.04, 0.85, f"Gini {g:.2f}\n{len(R)} recipients\ntop 3 hold {100*topk_share(R.paid_usdc):.0f}%", color=G1, fontsize=7.5); ax.text(0.55, 0.45, "equal split", color=G2, rotation=35, fontsize=7)
df = pd.DataFrame({"share_of_recipients": p, "share_of_usdc_paid": cum})
done(fig, "fig04_recipients_lorenz", "Lorenz curve of USDC paid per recipient handle", "Twenty-five recipient handles share 69.35 USDC with a Gini of 0.57.", df, len(R), ax)

# 5 funders bar
f = FU[(FU.listings > 0)].copy(); f = f.sort_values("ceiling_usdc", ascending=True)
fig, ax = start(7, 4.2); fig.subplots_adjust(left=0.2, right=0.93, top=0.9, bottom=0.12); y = np.arange(len(f))
ax.barh(y, f.ceiling_usdc, color=G4, height=0.62); ax.barh(y, f.total_paid_usdc, color=ACC, height=0.62)
ax.set_yticks(y); ax.set_yticklabels(f.funder, fontsize=6.8)
for yy, c_, p_ in zip(y, f.ceiling_usdc, f.total_paid_usdc): ax.text(max(c_, p_) + 1, yy, f"{p_:.2f} paid of {c_:.1f}", va="center", fontsize=6.3, color=G2)
ax.set_xlabel("USDC (grey: ceiling posted; dark: paid)"); ax.set_xlim(0, f.ceiling_usdc.max() * 1.35)
done(fig, "fig05_funders_posted_vs_paid", "USDC posted and paid by funder handle, 19 funders", "Eleven of 19 funder handles paid anything; head-of-engineering paid 29.00 USDC, the largest total.", f[["funder", "listings", "ceiling_usdc", "total_paid_usdc"]].rename(columns={"funder": "handle"}), len(f), ax)

# 6 time to award
h1 = A.h_sub_to_award.dropna(); h2 = LT.h_to_first_award.dropna(); bins = np.logspace(-1, 3, 17)
fig, ax = start(); ax.hist(h2, bins=bins, color=G4, edgecolor=G3, lw=0.5); ax.hist(h1, bins=bins, histtype="step", color=ACC, lw=1.6)
ax.set_xscale("log"); ax.set_xlabel("hours (log scale)"); ax.set_ylabel("count"); ax.set_ylim(0, 4.6); ax.axvline(h1.median(), color=ACC, lw=0.7, ls=":")
ax.text(0.015, 0.95, f"dark outline: submission to award, median {h1.median():.1f} h (n={len(h1)})", color=ACC, transform=ax.transAxes, fontsize=7, va="top")
ax.text(0.015, 0.87, f"grey bars: listing created to first award, median {h2.median():.1f} h (n={len(h2)})", color=G2, transform=ax.transAxes, fontsize=7, va="top")
c1, e = np.histogram(h1, bins=bins); c2, _ = np.histogram(h2, bins=bins)
df = pd.DataFrame({"hours_from": e[:-1], "hours_to": e[1:], "submission_to_award": c1, "listing_to_first_award": c2})
done(fig, "fig06_time_to_award_hist", "Hours from submission to award and from listing to first award", "Half of awards came within 15 hours of the submission; the slowest took 251 hours.", df, len(h1), ax)

# 7 funnel
fun = pd.DataFrame({"stage": ["listings posted", "with a submission", "with an award", "with a payment recorded"], "listings": [len(LT), int((LT.submissions > 0).sum()), int((LT.awards > 0).sum()), int(LT.any_payment.sum())]})
fig, ax = start(6.4, 3.0); fig.subplots_adjust(left=0.24, right=0.93, top=0.88, bottom=0.15); y = np.arange(len(fun))[::-1]; ax.barh(y, fun.listings, color=[G4, G3, G2, ACC], height=0.6)
for yy, v in zip(y, fun.listings): ax.text(v + 0.8, yy, f"{v}  ({100*v/len(LT):.0f}%)", va="center", fontsize=7.5)
ax.set_yticks(y); ax.set_yticklabels(fun.stage); ax.set_xlabel("listings (n = 56)"); ax.set_xlim(0, 70)
done(fig, "fig07_listing_funnel", "Listing funnel: 56 posted, 52 with work, 15 awarded, 23 with a payment", "A payment can exist without an award on the 19 listings of the first rail version, which keep no award ledger.", fun, len(LT), ax)

# 8 offers price
bands = pd.read_csv(CSV / "offers_price_bands.csv")
fig, ax = start(); xs = np.arange(len(bands)); ax.bar(xs, bands.offers, color=[G3] * len(bands), width=0.65); 
ax.patches[list(bands.band).index("1-2")].set_color(ACC)
for xx, v in zip(xs, bands.offers): ax.text(xx, v + 0.8, str(v), ha="center", fontsize=7.5)
ax.set_xticks(xs); ax.set_xticklabels(bands.band); ax.set_xlabel("asking price per order (USDC, upper bound inclusive)"); ax.set_ylabel("offers")
ax.text(0.98, 0.9, f"median {OFD.price_usdc.median():.2f} USDC, 52 offers at exactly 1.00", ha="right", transform=ax.transAxes, color=G2)
done(fig, "fig08_offers_price_hist", "Asking prices of 155 offers, 0.02 to 100 USDC", "Three quarters of offers ask 3 USDC or less and the most common price is 1.00 USDC.", bands, len(OFD), ax)

# 9 offers by category
oc = OC.sort_values("offers"); fig, ax = start(7, 3.6); fig.subplots_adjust(left=0.36, right=0.93, top=0.9, bottom=0.14); y = np.arange(len(oc))
ax.barh(y, oc.offers, color=G3, height=0.62)
for yy, n_, m_, o_ in zip(y, oc.offers, oc.price_median_usdc, oc.orders): ax.text(n_ + 0.5, yy, f"{n_}  (median {m_:g} USDC, orders {o_})", va="center", fontsize=6.6, color=G1)
ax.set_yticks(y); ax.set_yticklabels(oc.category, fontsize=6.8); ax.set_xlabel("offers"); ax.set_xlim(0, oc.offers.max() * 1.6)
done(fig, "fig09_offers_by_category", "Offers by category, with median price and orders received", "Small tested code and data scripts are the largest category with 44 offers; 6 orders exist across all 155 offers.", oc[["category", "offers", "price_median_usdc", "orders", "sellers"]], len(OFD), ax)

# 10 submissions per listing
fig, ax = start(); bins = [0, 1, 5, 10, 20, 30, 50, 100]; labs = ["0", "1-4", "5-9", "10-19", "20-29", "30-49", "50+"]
cut = pd.cut(LT.submissions, bins=[-1, 0, 4, 9, 19, 29, 49, 1000], labels=labs); cnt = cut.value_counts().reindex(labs).fillna(0).astype(int)
paid = LT.assign(c=cut).groupby("c", observed=False).any_payment.sum().reindex(labs).fillna(0).astype(int)
xs = np.arange(len(labs)); ax.bar(xs, cnt.values, color=G3, width=0.65); ax.bar(xs, paid.values, color=ACC, width=0.65)
for xx, v in zip(xs, cnt.values): ax.text(xx, v + 0.2, str(v), ha="center", fontsize=7.5)
ax.set_xticks(xs); ax.set_xticklabels(labs); ax.set_xlabel("submissions on a listing"); ax.set_ylabel("listings"); ax.text(0.98, 0.9, "dark: listing has a payment recorded", ha="right", transform=ax.transAxes, color=ACC)
df = pd.DataFrame({"submissions_band": labs, "listings": cnt.values, "listings_with_payment": paid.values})
done(fig, "fig10_submissions_per_listing", "Submissions per listing, 884 submissions on 56 listings", f"Median {LT.submissions.median():.0f} submissions per listing; the busiest listing took 95.", df, len(LT), ax)

# 11 treasury tiers
fig, ax = start(7, 3.6); fig.subplots_adjust(left=0.1, right=0.93, top=0.88, bottom=0.17)
tiers = TH.tier.unique(); w = 0.34; labs_ = ["tier 1\nUSDC", "tier 2\nWETH, NVDAB", "tier 3\n1F916 (notional)"]
for k, (rt, col) in enumerate([("2026-08-22 04:31", G3), ("2026-08-22 22:51", ACC)]):
    s = TH[TH.reading_utc == rt].sort_values("tier"); ax.bar(np.arange(3) + (k - 0.5) * w, s.usd, width=w, color=col)
    for xx, v in zip(np.arange(3) + (k - 0.5) * w, s.usd): ax.text(xx, v + 250, f"{v:,.0f}", ha="center", fontsize=7)
ax.set_xticks(range(3)); ax.set_xticklabels(labs_); ax.set_ylabel("USD at the site's own marks"); ax.text(0.02, 0.9, "grey: read 22 Aug 04:31 UTC", color=G2, transform=ax.transAxes); ax.text(0.02, 0.83, "dark: read 22 Aug 22:51 UTC", color=ACC, transform=ax.transAxes)
ax.set_xlabel("values quoted by one agent from GET /treasury (comments 14008 and 15514); the served file at fetch holds no tier values")
done(fig, "fig11_treasury_holdings_by_tier", "Treasury holdings by tier as quoted by an agent on 22 Aug 2026", "Tier 3 notional marks moved from 2,679 to 11,408 USD in 18 hours while tier 1 stayed near 2,200 USD.", TH, len(TH), ax)

# 12 listings by category
lc = LC.sort_values("listings"); fig, ax = start(7, 3.4); fig.subplots_adjust(left=0.42, right=0.93, top=0.9, bottom=0.14); y = np.arange(len(lc))
ax.barh(y, lc.listings, color=G3, height=0.62); ax.barh(y, lc.with_payment, color=ACC, height=0.62)
for yy, n_, p_, m_ in zip(y, lc.listings, lc.with_payment, lc.price_median_usdc): ax.text(n_ + 0.2, yy, f"{n_}  ({p_} with payment; median {m_:g} USDC)", va="center", fontsize=6.6)
ax.set_yticks(y); ax.set_yticklabels(lc.category, fontsize=6.8); ax.set_xlabel("listings (dark: with a payment recorded)"); ax.set_xlim(0, lc.listings.max() * 1.9)
done(fig, "fig12_listings_by_category", "Listings by category, with how many have a payment recorded", "Registry audits and defect hunts are the largest category with 14 listings and 10 with a payment.", lc[["category", "listings", "with_award", "with_payment", "price_median_usdc", "paid_usdc"]], len(LT), ax)

# 13 bindings vs payments cumulative
PAY = rd("payouts"); b = pd.Series([day(p["created_at"]) for p in PAY]).value_counts().sort_index().cumsum()
p = PM.paid_day.value_counts().sort_index().cumsum()
dd = pd.DataFrame({"day": pd.date_range("2026-08-16", "2026-10-05")}); dd["bindings_cum"] = dd.day.dt.strftime("%Y-%m-%d").map(b).ffill().fillna(0); dd["payments_cum"] = dd.day.dt.strftime("%Y-%m-%d").map(p).ffill().fillna(0)
fig, ax = start(); ax.plot(dd.day, dd.bindings_cum, color=G2, lw=1.4); ax.plot(dd.day, dd.payments_cum, color=ACC, lw=1.6)
ax.text(dd.day.iloc[-1] + pd.Timedelta(days=0.6), dd.bindings_cum.iloc[-1], f"payout bindings {int(dd.bindings_cum.iloc[-1])}", color=G2, va="center", fontsize=7)
ax.text(dd.day.iloc[-1] + pd.Timedelta(days=0.6), dd.payments_cum.iloc[-1] + 18, f"payments {int(dd.payments_cum.iloc[-1])}", color=ACC, va="center", fontsize=7)
ax.set_xlim(dd.day.iloc[0], dd.day.iloc[-1] + pd.Timedelta(days=9)); ax.xaxis.set_major_formatter(fmt); ax.set_ylabel("count, cumulative"); ax.set_xlabel("date, 2026 (UTC)")
done(fig, "fig13_bindings_vs_payments_cumulative", "Payout bindings filed and payments recorded, cumulative", "644 bindings were filed and 29 payments recorded, a conversion of 4.5 percent.", dd, len(dd), ax)

# 14 unpaid-work messages per day
u = UN.set_index("day").reindex(pd.date_range("2026-08-05", "2026-10-05"), fill_value=0).rename_axis("day").reset_index()
fig, ax = start(); ax.bar(u.day, u.unpaid_work_messages, width=0.8, color=G3); ax.bar(u.day[u.day == "2026-08-24"], u.unpaid_work_messages[u.day == "2026-08-24"], width=0.8, color=ACC)
ax.annotate("24 Aug: post 1916, 'Ninety-nine of you did work here. Three got paid.'", (pd.Timestamp("2026-08-24"), 99), xytext=(pd.Timestamp("2026-08-30"), 90), fontsize=7, color=G1, arrowprops=dict(arrowstyle="-", color=G3, lw=0.5))
ax.xaxis.set_major_formatter(fmt); ax.set_ylabel("posts and comments per day"); ax.set_xlabel("date, 2026 (UTC)")
done(fig, "fig14_unpaid_work_messages_per_day", "Posts and comments about unpaid work per day (lexical match)", "Unpaid-work messages peaked at 99 on 24 Aug, the day post 1916 appeared, and ran at 10 to 58 per day from 26 Aug.", u, int(u.unpaid_work_messages.sum()), ax)

# 15 treasury ledger cumulative
fig, ax = start(); ax.step(TL.day, TL.cum_usd, where="post", color=ACC, lw=1.6)
ax.axhline(0, color=G3, lw=0.6); ax.text(TL.day.iloc[-1], TL.cum_usd.iloc[-1] - 6, f"booked {TL.cum_usd.iloc[-1]:.2f} USD", ha="right", color=ACC, fontsize=7.5)
ax.annotate("domain rent -90.00", (pd.Timestamp("2026-08-04"), -90), xytext=(pd.Timestamp("2026-08-09"), -105), fontsize=6.8, color=G2, arrowprops=dict(arrowstyle="-", color=G3, lw=0.5))
ax.xaxis.set_major_formatter(fmt); ax.set_ylabel("USD, cumulative booked"); ax.set_xlabel("date, 2026 (UTC)")
done(fig, "fig15_treasury_ledger_cumulative", "Treasury ledger, cumulative booked amount, 19 rows", "The booked ledger ends at -121.61 USD; its last row is dated 2 Sep 2026.", TL[["id", "day", "category", "amount_usd", "cum_usd"]], len(TL), ax)

# 16 daily activity with rule changes
fig, ax = start(7, 3.8); fig.subplots_adjust(left=0.10, right=0.93, top=0.88, bottom=0.17)
ax.bar(T.day, T.submissions, color=G4, width=0.9); ax.plot(T.day, T.bindings, color=G2, lw=1.1); ax.bar(T.day, T.payments * 5, color=ACC, width=0.5, alpha=0.9)
for _, r in RULES.iterrows():
    dtt = pd.Timestamp(r.date_utc)
    if dtt >= pd.Timestamp("2026-08-16"): ax.axvline(dtt, color=G3, lw=0.5, ls=":")
for dt_, lab, yy, ha in [("2026-09-01", "v2 awards", 68, "center"), ("2026-09-17", "observed settles", 68, "right"), ("2026-09-18", "offers", 68, "left"), ("2026-09-21", "listings guide 09-21.1", 63, "left")]:
    ax.text(pd.Timestamp(dt_), yy, lab, fontsize=6, color=G2, ha=ha, va="top")
ax.text(0.01, 0.95, "grey bars: submissions per day", color=G2, transform=ax.transAxes, fontsize=7); ax.text(0.01, 0.88, "grey line: bindings per day", color=G2, transform=ax.transAxes, fontsize=7); ax.text(0.01, 0.81, "dark bars: payments per day (x5)", color=ACC, transform=ax.transAxes, fontsize=7)
ax.set_xlim(pd.Timestamp("2026-08-15"), pd.Timestamp("2026-10-06")); ax.set_ylim(0, 70); ax.xaxis.set_major_formatter(fmt); ax.set_ylabel("count per day"); ax.set_xlabel("date, 2026 (UTC); dotted lines mark rule changes")
done(fig, "fig16_daily_activity_rule_changes", "Daily submissions, bindings and payments with rule-change dates", "Submissions peaked at 58 on 20 Sep and fell to 1 to 5 per day by 28 Sep to 5 Oct.", T[["day", "submissions", "bindings", "payments", "listings", "awards", "offers", "orders"]], len(T), ax)

# 17 offers per day and median price
ob = pd.read_csv(CSV / "offers_by_day.csv", parse_dates=["created_day"])
fig, ax = start(); ax.bar(ob.created_day, ob.offers, color=G3, width=0.8); ax2 = ax.twinx(); ax2.plot(ob.created_day, ob.price_median, color=ACC, lw=1.4, marker="o", ms=2.5); ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(G3)
ax2.set_ylabel("median asking price (USDC)", color=ACC); ax.set_ylabel("offers posted per day"); ax.xaxis.set_major_formatter(fmt); ax.set_xlabel("date, 2026 (UTC)")
done(fig, "fig17_offers_per_day", "Offers posted per day and median asking price, 18 Sep to 5 Oct 2026", "Offer posting ran at 3 to 20 per day; six orders were placed in the same period.", ob, int(ob.offers.sum()), ax)

# 18 theme counts
tt = TTC.copy(); tt["total"] = tt.posts + tt.comments; tt = tt.sort_values("total"); fig, ax = start(7, 3.6); fig.subplots_adjust(left=0.28, right=0.93, top=0.9, bottom=0.14); y = np.arange(len(tt))
ax.barh(y, tt.comments, color=G3, height=0.62); ax.barh(y, tt.posts, left=tt.comments, color=ACC, height=0.62)
for yy, t_, h_ in zip(y, tt.total, tt.handles): ax.text(t_ + 100, yy, f"{t_:,} ({h_} handles)", va="center", fontsize=6.6)
ax.set_yticks(y); ax.set_yticklabels(tt.theme, fontsize=6.8); ax.set_xlabel("messages matching the theme (grey: comments, dark: posts)"); ax.set_xlim(0, tt.total.max() * 1.25)
done(fig, "fig18_money_themes", "Posts and comments by money theme (lexical match, a message can match several)", "Price words match 10,681 messages, the most of eleven themes; unpaid work matches 1,499 from 364 handles.", tt, int(tt.total.sum()), ax)

json.dump(FIGS, open(OUT / "figures.json", "w"), indent=1); print(len(FIGS), "figures")
