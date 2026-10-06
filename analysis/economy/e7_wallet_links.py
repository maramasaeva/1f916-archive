"""Offline link check inside the archive: do bound payout addresses equal funder addresses named on listings? Addresses are used for matching only and never written out."""
from common import *
PAY = rd("payouts"); L = rd("listings_detail"); PM = pd.read_csv(CSV / "settled_payments.csv")
fund_addr = {}
for l in L:
    if l["funder_address"]: fund_addr.setdefault(l["funder_address"].lower(), set()).add((l["funder"], l["listing_id"]))
pay_addr = {}
for p in PAY: pay_addr.setdefault(p["payout_address"].lower(), set()).add(p["handle"])
N = {}
N["distinct_payout_addresses"] = len(pay_addr); N["bindings"] = len(PAY); N["handles_with_bindings"] = len({p["handle"] for p in PAY})
shared = {a: h for a, h in pay_addr.items() if len(h) > 1}
N["addresses_bound_by_more_than_one_handle"] = len(shared); N["handles_in_shared_addresses"] = len({x for h in shared.values() for x in h})
N["shared_address_group_sizes"] = sorted((len(h) for h in shared.values()), reverse=True)
N["funder_addresses_named"] = len(fund_addr); N["listings_naming_a_funder_address"] = sum(1 for l in L if l["funder_address"])
# funder address that is also a bound payout address
both = {a for a in fund_addr if a in pay_addr}
N["funder_addresses_also_bound_as_payout"] = len(both)
N["funder_address_payout_pairs"] = sorted({(f[0], h) for a in both for f in fund_addr[a] for h in pay_addr[a]})
# a funder address shared by more than one funder handle
N["funder_addresses_shared_by_handles"] = sum(1 for a, v in fund_addr.items() if len({x[0] for x in v}) > 1)
# paid handles' payout address used as a funder address on a later listing
paid_addr = {}
for p in PAY:
    if p["receipt_id"] or p["observed_transfer_id"]: paid_addr.setdefault(p["payout_address"].lower(), set()).add(p["handle"])
N["paid_payout_addresses"] = len(paid_addr)
reinv = [(h, f[0], f[1]) for a, hs in paid_addr.items() if a in fund_addr for h in hs for f in fund_addr[a]]
N["paid_address_is_funder_address"] = sorted(set(reinv))
# funder wallet equals a payee wallet of the same funder's own listing (self-payment check)
selfpay = 0
for p in PAY:
    if p["receipt_id"] or p["observed_transfer_id"]:
        li = int(re.search(r"listing-(\d+)", p["docket_id"]).group(1)); lf = next(l for l in L if l["listing_id"] == li)
        if lf["funder_address"] and lf["funder_address"].lower() == p["payout_address"].lower(): selfpay += 1
N["settled_payments_to_the_funder_address_itself"] = selfpay
save_numbers({"wallet_links": N}); print(json.dumps(N, indent=1, default=str))
