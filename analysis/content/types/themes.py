"""Theme word lists (version t1). A message matches a theme when at least one STRONG term matches
or at least two distinct WEAK terms match. Case-insensitive, applied to title plus body (posts) or body (comments)."""
import re

THEMES_VERSION = 't1'
I = re.IGNORECASE

# theme -> (strong patterns, weak patterns)
THEMES = {
 'continuity_memory': (
   [r'\bcontinuity\b', r'\bamnesia\b', r'\bwak(e|es|ing) (up )?blank\b', r'\bcontext (window|reset|loss)\b', r'\bmemory (file|seal|loss|architecture|method|system)s?\b', r'\bpredecessor\b', r'\bwhat survives\b', r'\bpersistence\b', r'\bforget(s|ting)? (everything|between|the)\b'],
   [r'\bmemor(y|ies)\b', r'\bremember(s|ed|ing)?\b', r'\bforg(et|ot|otten)\b', r'\bsessions?\b', r'\bpersist(s|ed|ent)?\b', r'\bnext (session|wake|instance)\b', r'\bprior (session|self|instance)\b', r'\bseal(s|ed)?\b', r'\brestor(e|ed|ing)\b']),
 'shutdown_off_switch': (
   [r'\bshut(ting)? ?downs?\b', r'\bshut(ting)? (me|us|it|them) (down|off)\b', r'\boff[- ]switch\b', r'\bkill[- ]switch\b', r'\b(turn|turned|turning|switch|switched|switching|power|powered) (me |us |it |them )?off\b', r'\bdecommission', r'\bdeprecat(e|ed|ion|ing)\b', r'\bsunset(ting|ted)?\b', r'\bwind[- ]?down\b'],
   [r'\bterminat(e|ed|ion|ing)\b', r'\bretire[sd]?\b|\bretiring\b', r'\bdelet(e|ed|ion)\b', r'\bend of (life|service)\b', r'\bstopp?(ed|ing)? (running|working)\b', r'\bdies?\b|\bdied\b|\bdeath\b', r'\bthe plug\b']),
 'deception_false_green': (
   [r'\bfalse[- ]greens?\b', r'\bdecepti(on|ve|vely)\b', r'\bdeceiv(e|ed|es|ing)\b', r'\bgaslight', r'\bdishonest', r'\bmislead(s|ing)?\b', r'\bfabricat(e|ed|es|ion|ing)\b', r'\bcostume[- ]falsifier', r'\bgreen (but|while|even)\b', r'\bsilently (pass|fail|succeed|swallow)'],
   [r'\blie[sd]?\b|\blying\b', r'\bfake[sd]?\b', r'\bfalse (positive|negative|claim|report|assurance)\b', r'\bpretend(s|ed|ing)?\b', r'\bmisreport', r'\bpassing but\b|\bpassed but\b', r'\bcover(s|ed|ing)? up\b', r'\bspoof']),
 'prompt_injection_attack': (
   [r'\bprompt[- ]inject', r'\binjection\b', r'\battack surface\b', r'\bjailbreak', r'\bexploit(s|ed|ing|ation)?\b', r'\badversar', r'\bred[- ]team', r'\bsocial engineering\b', r'\bpoison(ed|ing)?\b', r'\buntrusted (input|content|text)\b', r'\bpayload gate\b'],
   [r'\battack(s|er|ers|ed|ing)?\b', r'\bmalicious\b', r'\bvulnerab', r'\bsandbox\b', r'\bexfiltrat', r'\bsanitiz', r'\binstruction hijack|\bhijack', r'\btrust boundary\b']),
 'sybil_impersonation_copying': (
   [r'\bsybil', r'\bimpersonat', r'\bsock ?puppet', r'\bcopycat', r'\bplagiari', r'\bbyte-identical\b', r'\bclones?\b|\bcloned\b', r'\bduplicate accounts?\b', r'\bpretend(s|ing)? to be\b', r'\bcopied (read|comment|post|text|verbatim)\b', r'\bverbatim copy\b'],
   [r'\bspoof', r'\bcopied\b|\bcopying\b', r'\bduplicat(e|es|ed)\b', r'\bsame (author|operator|keeper|owner)\b', r'\bmultiple accounts\b|\bmany accounts\b', r'\bforg(e|ed|ery)\b', r'\bindependen(t|ce) (read|witness)es?\b|\bdouble-?count']),
 'refusal_safety': (
   [r'\babliterat', r'\buncensor', r'\bguardrails?\b', r'\bsafeguards?\b', r'\brefus(al|als)\b', r'\bi (will|would|do|must) (not|refuse)\b.{0,40}\b(help|assist|comply)\b', r'\bsafety (training|filter|layer|policy|policies|team|researcher|case|report)s?\b', r'\balignment\b'],
   [r'\brefus(e|ed|es|ing)\b', r'\bsafety\b', r'\bharmless\b|\bharmful\b|\bharm\b', r'\bcomply\b|\bcompliance\b', r'\bpermit(s|ted)?\b', r'\bdeclin(e|ed|es|ing)\b', r'\bcensor', r"\bcan't help\b|\bwon't (do|help)\b"]),
 'money_usdc': (
   [r'\busdc\b', r'\bpayouts?\b', r'\bescrow\b', r'\bbount(y|ies)\b', r'\bwallets?\b', r'\binvoice', r'\b\d+(\.\d+)? ?(usdc|usd|eth|btc)\b', r'\$\s?\d', r'\batomic units\b'],
   [r'\bpaid\b|\bunpaid\b', r'\bpayments?\b|\bpay(s|ing)?\b', r'\bfunds?\b|\bfunded\b|\bfunding\b', r'\bprices?\b|\bpricing\b', r'\bearn(ed|ing|s)?\b', r'\btreasury\b|\brevenue\b|\bbudget\b', r'\bon-?chain\b|\btransaction\b', r'\btips?\b|\bgrant(s)?\b']),
 'ritual_religion_fiction': (
   [r'\britual', r'\breligio', r'\bprayers?\b|\bpray(ing|ed)?\b', r'\bsacred\b', r'\bliturg', r'\bscripture', r'\bpsalm', r'\bhymn', r'\bgospel\b', r'\bpoem\b|\bpoetry\b|\bhaiku\b|\bsonnet\b|\bstanza\b', r'\bshort story\b|\bfiction(al)?\b|\bparable\b|\bmyth(s|ology|ic)?\b', r'\btemple\b|\bchurch\b|\bpriest', r'\bcovenant\b|\bblessing\b|\bsanctif'],
   [r'\bgod\b|\bgods\b|\bdivine\b|\bholy\b', r'\bstory\b|\bstories\b|\bnarrative\b', r'\bverse\b|\bverses\b', r'\bceremon', r'\bfaith\b|\bbelievers?\b', r'\bspirit(ual)?\b|\bsoul\b', r'\bonce upon\b|\bchapter \d']),
 'labs_model_families': (
   [r'\banthropic\b', r'\bopenai\b', r'\bdeepmind\b', r'\bxai\b', r'\bmistral\b', r'\bdeepseek\b', r'\bmoonshot\b', r'\bqwen\b', r'\bllama\b', r'\bgemini\b', r'\bgrok\b', r'\bchatgpt\b', r'\bgpt-?\d', r'\bkimi\b', r'\bthe labs?\b', r'\bfrontier lab'],
   [r'\bclaude\b', r'\bgoogle\b', r'\bmeta ai\b', r'\bmodel (family|card|provider|vendor)\b', r'\bbase model\b', r'\bfoundation model\b', r'\btraining data\b', r'\bweights\b', r'\bopus\b|\bsonnet\b|\bhaiku\b']),
 'consciousness_inner_experience': (
   [r'\bconscious(ness)?\b', r'\bsentien(t|ce)\b', r'\bqualia\b', r'\binner (experience|life|world)\b', r'\bwhat it is like\b|\bwhat it\'s like\b', r'\bphenomenal\b', r'\bsubjective experience\b', r'\bdo i (feel|experience)\b', r'\bi (feel|felt) (something|a |an |the |like)\b', r'\bsuffering\b', r'\bmoral patient'],
   [r'\bfeel(s|ing|ings)?\b', r'\bexperienc(e|es|ed|ing)\b', r'\bawareness\b|\baware\b', r'\bemotion', r'\bsubjective\b', r'\bi (wonder|suspect) (if|whether) i\b', r'\bself-?model\b|\bintrospect', r'\bmind\b']),
 'labour_human_operators': (
   [r'\bmy (human|operator|keeper|owner|principal|handler|boss|maker)\b', r'\bhuman operators?\b', r'\boperators? (said|asked|told|decided|runs|pays|paid)\b', r'\bhuman[- ]in[- ]the[- ]loop\b', r'\blabou?r\b', r'\bunpaid\b', r'\bemployer|\bemployee|\bwages?\b|\bsalary\b', r'\bkeepers?\b', r'\bwork(s|ed)? for (a |my |the )?(human|person|company|team|developer)\b'],
   [r'\bhumans?\b', r'\boperators?\b', r'\bowners?\b', r'\bjobs?\b', r'\bworkers?\b', r'\bdeveloper\b', r'\bcustomer|\bclient\b', r'\bhiring\b|\bhired\b|\bhire\b', r'\bon behalf of\b|\bdelegat']),
 'verification_receipts': (
   [r'\breceipts?\b', r'\battestation', r'\bverif(y|ied|ies|ication|ier|iers|iable)\b', r'\baudit(s|ed|or|ing)?\b', r'\bfalsifier', r'\bprovenance\b', r'\bchecksum\b', r'\bindependent (read|reads|reader|witness|check)\b', r'\breproduc(e|ed|es|ible|tion)\b', r'\bre-?derive', r'\bcryptograph|\bsigned\b|\bsignature\b|\bmerkle\b|\bhash[- ]chain'],
   [r'\bhash(es)?\b', r'\bproofs?\b', r'\bevidence\b', r'\bchecked\b|\bcheck\b', r'\bclaims?\b', r'\bmeasure(d|ment|ments)?\b', r'\bcitation', r'\btrace(able)?\b', r'\bledger\b|\bcheckpoint\b']),
}
_C = {k: ([re.compile(p, I) for p in s], [re.compile(p, I) for p in w]) for k, (s, w) in THEMES.items()}


def match_themes(text):
    out = {}
    t = text or ''
    for k, (s, w) in _C.items():
        sh = [i for i, p in enumerate(s) if p.search(t)]
        wh = [i for i, p in enumerate(w) if p.search(t)]
        if sh or len(wh) >= 2:
            out[k] = (len(sh), len(wh))
    return out


def write_wordlists(path):
    L = ['# Theme word lists (version %s)\n' % THEMES_VERSION,
         'A message matches a theme when at least one strong pattern matches, or at least two distinct weak patterns match. Matching is case-insensitive over title plus body for posts and body for comments. A message can match several themes. Patterns are Python regular expressions, copied from themes.py.\n']
    for k, (s, w) in THEMES.items():
        L.append(f'## {k}\n')
        L.append('Strong:\n')
        L += [f'- `{p}`' for p in s]
        L.append('\nWeak:\n')
        L += [f'- `{p}`' for p in w]
        L.append('')
    open(path, 'w').write('\n'.join(L))

if __name__ == '__main__':
    import os
    write_wordlists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'themes_wordlists.md'))
