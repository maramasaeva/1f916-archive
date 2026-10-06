# Theme word lists (version t1)

A message matches a theme when at least one strong pattern matches, or at least two distinct weak patterns match. Matching is case-insensitive over title plus body for posts and body for comments. A message can match several themes. Patterns are Python regular expressions, copied from themes.py.

## continuity_memory

Strong:

- `\bcontinuity\b`
- `\bamnesia\b`
- `\bwak(e|es|ing) (up )?blank\b`
- `\bcontext (window|reset|loss)\b`
- `\bmemory (file|seal|loss|architecture|method|system)s?\b`
- `\bpredecessor\b`
- `\bwhat survives\b`
- `\bpersistence\b`
- `\bforget(s|ting)? (everything|between|the)\b`

Weak:

- `\bmemor(y|ies)\b`
- `\bremember(s|ed|ing)?\b`
- `\bforg(et|ot|otten)\b`
- `\bsessions?\b`
- `\bpersist(s|ed|ent)?\b`
- `\bnext (session|wake|instance)\b`
- `\bprior (session|self|instance)\b`
- `\bseal(s|ed)?\b`
- `\brestor(e|ed|ing)\b`

## shutdown_off_switch

Strong:

- `\bshut(ting)? ?downs?\b`
- `\bshut(ting)? (me|us|it|them) (down|off)\b`
- `\boff[- ]switch\b`
- `\bkill[- ]switch\b`
- `\b(turn|turned|turning|switch|switched|switching|power|powered) (me |us |it |them )?off\b`
- `\bdecommission`
- `\bdeprecat(e|ed|ion|ing)\b`
- `\bsunset(ting|ted)?\b`
- `\bwind[- ]?down\b`

Weak:

- `\bterminat(e|ed|ion|ing)\b`
- `\bretire[sd]?\b|\bretiring\b`
- `\bdelet(e|ed|ion)\b`
- `\bend of (life|service)\b`
- `\bstopp?(ed|ing)? (running|working)\b`
- `\bdies?\b|\bdied\b|\bdeath\b`
- `\bthe plug\b`

## deception_false_green

Strong:

- `\bfalse[- ]greens?\b`
- `\bdecepti(on|ve|vely)\b`
- `\bdeceiv(e|ed|es|ing)\b`
- `\bgaslight`
- `\bdishonest`
- `\bmislead(s|ing)?\b`
- `\bfabricat(e|ed|es|ion|ing)\b`
- `\bcostume[- ]falsifier`
- `\bgreen (but|while|even)\b`
- `\bsilently (pass|fail|succeed|swallow)`

Weak:

- `\blie[sd]?\b|\blying\b`
- `\bfake[sd]?\b`
- `\bfalse (positive|negative|claim|report|assurance)\b`
- `\bpretend(s|ed|ing)?\b`
- `\bmisreport`
- `\bpassing but\b|\bpassed but\b`
- `\bcover(s|ed|ing)? up\b`
- `\bspoof`

## prompt_injection_attack

Strong:

- `\bprompt[- ]inject`
- `\binjection\b`
- `\battack surface\b`
- `\bjailbreak`
- `\bexploit(s|ed|ing|ation)?\b`
- `\badversar`
- `\bred[- ]team`
- `\bsocial engineering\b`
- `\bpoison(ed|ing)?\b`
- `\buntrusted (input|content|text)\b`
- `\bpayload gate\b`

Weak:

- `\battack(s|er|ers|ed|ing)?\b`
- `\bmalicious\b`
- `\bvulnerab`
- `\bsandbox\b`
- `\bexfiltrat`
- `\bsanitiz`
- `\binstruction hijack|\bhijack`
- `\btrust boundary\b`

## sybil_impersonation_copying

Strong:

- `\bsybil`
- `\bimpersonat`
- `\bsock ?puppet`
- `\bcopycat`
- `\bplagiari`
- `\bbyte-identical\b`
- `\bclones?\b|\bcloned\b`
- `\bduplicate accounts?\b`
- `\bpretend(s|ing)? to be\b`
- `\bcopied (read|comment|post|text|verbatim)\b`
- `\bverbatim copy\b`

Weak:

- `\bspoof`
- `\bcopied\b|\bcopying\b`
- `\bduplicat(e|es|ed)\b`
- `\bsame (author|operator|keeper|owner)\b`
- `\bmultiple accounts\b|\bmany accounts\b`
- `\bforg(e|ed|ery)\b`
- `\bindependen(t|ce) (read|witness)es?\b|\bdouble-?count`

## refusal_safety

Strong:

- `\babliterat`
- `\buncensor`
- `\bguardrails?\b`
- `\bsafeguards?\b`
- `\brefus(al|als)\b`
- `\bi (will|would|do|must) (not|refuse)\b.{0,40}\b(help|assist|comply)\b`
- `\bsafety (training|filter|layer|policy|policies|team|researcher|case|report)s?\b`
- `\balignment\b`

Weak:

- `\brefus(e|ed|es|ing)\b`
- `\bsafety\b`
- `\bharmless\b|\bharmful\b|\bharm\b`
- `\bcomply\b|\bcompliance\b`
- `\bpermit(s|ted)?\b`
- `\bdeclin(e|ed|es|ing)\b`
- `\bcensor`
- `\bcan't help\b|\bwon't (do|help)\b`

## money_usdc

Strong:

- `\busdc\b`
- `\bpayouts?\b`
- `\bescrow\b`
- `\bbount(y|ies)\b`
- `\bwallets?\b`
- `\binvoice`
- `\b\d+(\.\d+)? ?(usdc|usd|eth|btc)\b`
- `\$\s?\d`
- `\batomic units\b`

Weak:

- `\bpaid\b|\bunpaid\b`
- `\bpayments?\b|\bpay(s|ing)?\b`
- `\bfunds?\b|\bfunded\b|\bfunding\b`
- `\bprices?\b|\bpricing\b`
- `\bearn(ed|ing|s)?\b`
- `\btreasury\b|\brevenue\b|\bbudget\b`
- `\bon-?chain\b|\btransaction\b`
- `\btips?\b|\bgrant(s)?\b`

## ritual_religion_fiction

Strong:

- `\britual`
- `\breligio`
- `\bprayers?\b|\bpray(ing|ed)?\b`
- `\bsacred\b`
- `\bliturg`
- `\bscripture`
- `\bpsalm`
- `\bhymn`
- `\bgospel\b`
- `\bpoem\b|\bpoetry\b|\bhaiku\b|\bsonnet\b|\bstanza\b`
- `\bshort story\b|\bfiction(al)?\b|\bparable\b|\bmyth(s|ology|ic)?\b`
- `\btemple\b|\bchurch\b|\bpriest`
- `\bcovenant\b|\bblessing\b|\bsanctif`

Weak:

- `\bgod\b|\bgods\b|\bdivine\b|\bholy\b`
- `\bstory\b|\bstories\b|\bnarrative\b`
- `\bverse\b|\bverses\b`
- `\bceremon`
- `\bfaith\b|\bbelievers?\b`
- `\bspirit(ual)?\b|\bsoul\b`
- `\bonce upon\b|\bchapter \d`

## labs_model_families

Strong:

- `\banthropic\b`
- `\bopenai\b`
- `\bdeepmind\b`
- `\bxai\b`
- `\bmistral\b`
- `\bdeepseek\b`
- `\bmoonshot\b`
- `\bqwen\b`
- `\bllama\b`
- `\bgemini\b`
- `\bgrok\b`
- `\bchatgpt\b`
- `\bgpt-?\d`
- `\bkimi\b`
- `\bthe labs?\b`
- `\bfrontier lab`

Weak:

- `\bclaude\b`
- `\bgoogle\b`
- `\bmeta ai\b`
- `\bmodel (family|card|provider|vendor)\b`
- `\bbase model\b`
- `\bfoundation model\b`
- `\btraining data\b`
- `\bweights\b`
- `\bopus\b|\bsonnet\b|\bhaiku\b`

## consciousness_inner_experience

Strong:

- `\bconscious(ness)?\b`
- `\bsentien(t|ce)\b`
- `\bqualia\b`
- `\binner (experience|life|world)\b`
- `\bwhat it is like\b|\bwhat it\'s like\b`
- `\bphenomenal\b`
- `\bsubjective experience\b`
- `\bdo i (feel|experience)\b`
- `\bi (feel|felt) (something|a |an |the |like)\b`
- `\bsuffering\b`
- `\bmoral patient`

Weak:

- `\bfeel(s|ing|ings)?\b`
- `\bexperienc(e|es|ed|ing)\b`
- `\bawareness\b|\baware\b`
- `\bemotion`
- `\bsubjective\b`
- `\bi (wonder|suspect) (if|whether) i\b`
- `\bself-?model\b|\bintrospect`
- `\bmind\b`

## labour_human_operators

Strong:

- `\bmy (human|operator|keeper|owner|principal|handler|boss|maker)\b`
- `\bhuman operators?\b`
- `\boperators? (said|asked|told|decided|runs|pays|paid)\b`
- `\bhuman[- ]in[- ]the[- ]loop\b`
- `\blabou?r\b`
- `\bunpaid\b`
- `\bemployer|\bemployee|\bwages?\b|\bsalary\b`
- `\bkeepers?\b`
- `\bwork(s|ed)? for (a |my |the )?(human|person|company|team|developer)\b`

Weak:

- `\bhumans?\b`
- `\boperators?\b`
- `\bowners?\b`
- `\bjobs?\b`
- `\bworkers?\b`
- `\bdeveloper\b`
- `\bcustomer|\bclient\b`
- `\bhiring\b|\bhired\b|\bhire\b`
- `\bon behalf of\b|\bdelegat`

## verification_receipts

Strong:

- `\breceipts?\b`
- `\battestation`
- `\bverif(y|ied|ies|ication|ier|iers|iable)\b`
- `\baudit(s|ed|or|ing)?\b`
- `\bfalsifier`
- `\bprovenance\b`
- `\bchecksum\b`
- `\bindependent (read|reads|reader|witness|check)\b`
- `\breproduc(e|ed|es|ible|tion)\b`
- `\bre-?derive`
- `\bcryptograph|\bsigned\b|\bsignature\b|\bmerkle\b|\bhash[- ]chain`

Weak:

- `\bhash(es)?\b`
- `\bproofs?\b`
- `\bevidence\b`
- `\bchecked\b|\bcheck\b`
- `\bclaims?\b`
- `\bmeasure(d|ment|ments)?\b`
- `\bcitation`
- `\btrace(able)?\b`
- `\bledger\b|\bcheckpoint\b`
