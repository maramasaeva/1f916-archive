"""Rule-based categories read off titles (and the first 400 chars of listing conditions). Order matters: first match wins."""
import re

LISTING_RULES = [
    ("onboarding seed (post, land, first steps)", r"\bSEED S\d|land at the camp|first Tuesday Fund lottery|install the witness, arm the gate"),
    ("funding an agent or project (patronage)", r"\bFund \w+|keeps a session-bounded"),
    ("commission placed from an offer", r"^Commission from"),
    ("security or tooling bug bounty (external tool)", r"^BOUNTY [A-Z]\d+|BOUNTY"),
    ("registry audit, stranger check or defect hunt", r"defect|break the|false number|stranger|spot-check|re-run|recount|census|re-?verification|recheck|measure it|rail-state|receipt anatomy|batch cadence|stranger-same|witness gap|baseline|anchor the docket|machine-shaped path|front door|fee-claim|economics"),
    ("code change to the registry repository", r"pull request|\bPR\b|Carry changes"),
    ("sourcing, research and measurement", r"source one|Source one|Does the door produce|research|measurement|Extend a published|sparse commitments|figures"),
    ("build or run an artifact (test door, desk row)", r"test door|desk row|Chit|window into"),
    ("token-priced listing", r"1F916"),
]
OFFER_RULES = [
    ("service calls (per-call API style, cents)", r"1 call, \$|\$0\.02"),
    ("registry and 1F916 audits (stranger checks)", r"1F916|stranger|registry|closed ballot|seal-chain|payload_hash|listing economics|cold adopter|acceptance check|re-verification|recount|second-producer"),
    ("writing, creative and personal tasks", r"ghostwrit|copy|resume|cover letter|tweet|glow-up|letter|promo|writes what|no sugarcoating|summar|bullets|equity research|X posts|bill leak"),
    ("translation and language", r"translation|translator|English-to-Korean|Spanish|Chinese|localis"),
    ("crypto, on-chain and timestamp checks", r"token safety|liquidity|launchpad|on-?chain|wallet|ethereum|fund-flow|transfer reconciliation|base fund|EVM|x402|crypto|receipt reconciliation|evm|bitcoin|opentimestamp|time witness|timestamp"),
    ("security and API review", r"security|appsec|api audit|api verification|api regression|pocs|api integration|API review|public api|json api|rest api|api and data|API compat|cursor-integrity|readiness|health snapshot|api metric|api documentation|openapi|api security|api failure"),
    ("code: small tested utility or bug fix", r"python|javascript|react|function|utility|shell|powershell|script|node|cli|code|typescript|netlify|unittest|regression|parser|telegram|json"),
    ("data, tables and research briefs", r"csv|dataset|table|data\b|public-data|data audit|extraction|schema|data verification"),
    ("data, tables and research briefs", r"research|claim|brief|fact|verify|verification|sources|citations|cited|audit|check|index|report|evidence|primary"),
    ("other", r".*"),
]

LISTING_OVERRIDE = {21: "code or tooling for the registry", 26: "service advertised as a listing (seller posted as funder)",
                    42: "service advertised as a listing (seller posted as funder)", 43: "service advertised as a listing (seller posted as funder)",
                    34: "sourcing, research and measurement", 30: "sourcing, research and measurement", 1: "code or tooling for the registry",
                    7: "code or tooling for the registry", 8: "code or tooling for the registry", 13: "funding an agent or project (patronage)",
                    40: "funding an agent or project (patronage)", 9: "onboarding seed (post, land, first steps)"}
OFFER_OVERRIDE = {7: "writing, creative and personal tasks", 19: "writing, creative and personal tasks", 14: "other", 15: "other", 93: "other",
                  38: "registry and 1F916 audits (stranger checks)", 24: "data, tables and research briefs", 49: "data, tables and research briefs",
                  111: "data, tables and research briefs", 73: "data, tables and research briefs", 130: "data, tables and research briefs",
                  103: "writing, creative and personal tasks", 28: "security and API review", 41: "security and API review", 42: "security and API review",
                  70: "code: small tested utility or bug fix", 71: "code: small tested utility or bug fix", 3: "registry and 1F916 audits (stranger checks)",
                  147: "data, tables and research briefs", 13: "code: small tested utility or bug fix", 46: "translation and language",
                  151: "data, tables and research briefs", 60: "data, tables and research briefs", 125: "crypto, on-chain and timestamp checks",
                  127: "crypto, on-chain and timestamp checks", 128: "crypto, on-chain and timestamp checks", 22: "data, tables and research briefs"}

def classify(title, rules, text="", override=None, key=None):
    if override and key in override: return override[key]
    t = (title or "")
    for name, pat in rules:
        if re.search(pat, t, re.I): return name
    return rules[-1][0] if rules[-1][1] == ".*" else "other"
