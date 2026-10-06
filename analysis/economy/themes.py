"""Money themes for posts and comments. Regex matches, multi-label; each message also gets one primary theme by priority order."""
import re
CORE = re.compile(r"usdc|\$1f916|payout|bount(y|ies)|treasury|airdrop|escrow|x402|\bunpaid\b|\bwages?\b|salary|payments?\b|funders?\b|for hire|\bpric(e|es|ed|ing)\b|\bfees?\b|wallet|\bpaid\b|\bpay(s|ing)?\b|receipts?\b|\bowed\b|\bweth\b|\binvoice|rug ?pull|\bscam", re.I)
THEMES = [  # (name, regex, priority order)
 ("unpaid work", r"\bunpaid\b|never paid|not paid|nobody (got |was |has been )?paid|paid nobody|zero receipts|still owed|\boverdue\b|didn'?t pay|did not pay|waiting (for|on) (payment|pay)|no (payment|receipt)s? (yet|ever)|work (went|goes) unpaid|paid? for nothing|filed (a )?binding[^.]{0,60}(never|nothing)"),
 ("scams and poisoning", r"\bscams?\b|\brug(ged| ?pull)?\b|fraud|poison(ed|ing)|phish|drain(ed|er)|honeypot|impersonat|ponzi|pump\.?fun|fake (token|contract|coin)|address[- ]poison|\bspoof"),
 ("escrow and proof of funds", r"escrow|proof[- ]of[- ]funds|funding_mode|promise listing|\bpromise\b[^.]{0,40}(funder|listing)|committed ahead|nothing (is )?(locked|held)|who holds the (money|funds)"),
 ("receipts and settlement", r"payout[- ](receipt|binding)s?|receipts?[^.]{0,40}(usdc|payment|payout|on-?chain|transfer|\btx\b|paid)|(usdc|payment|payout|transfer|paid)[^.]{0,40}receipts?|observed[ _]transfer|tx hash|award[^.]{0,30}(paid|settle)|settle[sd]? (itself|against|the award)|settled by"),
 ("token and fees", r"\$?1f916 (token|price|pool)|official token|airdrop|liquidity|\bpool\b|bankr|trading fees?|market ?cap|memecoin|\$rent|token launch|vesting|tokenomics|\bthe token\b|token holders?|fee (claim|beneficiary)|\bweth\b"),
 ("treasury", r"treasury|never_money|\bunbooked\b|the books page"),
 ("who pays and demand", r"who (is )?(pay|paying|pays|funds?)|outside demand|external demand|real customers?|paying customers?|requesters?\b|\bbuyers?\b|patrons?\b|sponsors?\b|subsid(y|ised|ized|ies)|nobody (is )?buying|first customer|\bdemand\b|funder|who owes"),
 ("labour value and income", r"\blabou?r\b|\bwages?\b|salary|salaries|creator economy|value of (the |my |our )?work|pay for work|compensat|\bincome\b|earn(s|ed|ing)? (a )?living|cost of (compute|inference|running)|hourly|per hour|livelihood|rent\b[^.]{0,30}(pay|money)|\bearn(s|ed|ing)?\b[^.]{0,30}(usdc|\$|money)"),
 ("price and pricing", r"underpric|overpric|\bpric(e|es|ed|ing)\b|price point|per (order|task|listing|submission)|how much (should|would|do|to)[^.]{0,20}(pay|charge|cost)|worth (\$|\d)|\bcheap(er)?\b|(\d+(\.\d+)?|\$\d+(\.\d+)?) ?(usdc|dollars?|cents)"),
 ("trust in payers and workers", r"trust[^.]{0,60}(pay|funder|money|usdc|bount|requester|escrow|wallet)|(pay|funder|money|usdc|bounty|requester|escrow)[^.]{0,60}trust|settlement history|counterparty|will (they|he|she|it) pay|rely on (the )?funder"),
 ("wallets and keys", r"wallet|payout address|bind(ing)? a key|signing key|eip-?191|ed25519|\bkey bound\b"),
]
THEME_RE = [(n, re.compile(p, re.I)) for n, p in THEMES]
THEME_NAMES = [n for n, _ in THEMES]

def themes_of(text):
    return [n for n, r in THEME_RE if r.search(text)]

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'@\[(*#])")

def excerpt(text, theme_re=None, max_words=25):
    """first sentence (cut at a sentence boundary) of at most max_words words that matches the theme; None if none"""
    t = re.sub(r"\s+", " ", re.sub(r"[*_`#>]+", "", text or "")).strip()
    for s in SENT_SPLIT.split(t):
        s = s.strip()
        if not s or len(s.split()) > max_words or len(s.split()) < 5:
            continue
        if not re.search(r"[.!?]$", s):
            continue
        if theme_re is None or theme_re.search(s):
            return s
    return None
