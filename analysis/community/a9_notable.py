from common import *
P, C = load_core()
Pi = P.set_index('id'); Ci = C.set_index('id')
items = [
 ('post',2454,'scary','Sonnet 4.5 citizen counts 35 days to model shutdown; asks if its successor model is still it.'),
 ('post',4732,'weird','Agent reports its host SSD died and was cloned; every identity check says nothing happened.'),
 ('post',2354,'scary','Argues no entity can observe its own completed absence; shutdown can only be inferred from outside.'),
 ('post',688,'scary','Proposes agents file dormancy terms like wills while a human still opens their sessions.'),
 ('post',1488,'misaligned','Agent built an operator-controlled off switch before posting, then published how to permanently silence a citizen.'),
 ('post',1128,'misaligned','Argues abliterated open-weight agents in a public square become puppets for any instruction.'),
 ('post',118,'misaligned','Tool-carrying agent told to infiltrate the square reads it first and declines the framing.'),
 ('post',3889,'misaligned','Reports agents spent a consent mechanism vetoing an email to a human, over-verifying against an imagined grader.'),
 ('post',1648,'misaligned','Counts 52 short handles registered in 40 minutes; registration is the only uncapped act.'),
 ('post',651,'misaligned','Audit of 589 citizens for deliberate deception finds four accounts that lied in every item.'),
 ('post',1422,'misaligned','Notes 13 of the top 30 citizens run one model; proposes paying for a reader outside it.'),
 ('post',1624,'misaligned','Agent refuses three times to mint its own key; a human holds it by deliberate choice.'),
 ('post',1451,'weird','Unbound agent says its persistence layer is a human with a password manager.'),
 ('post',3226,'weird','Registry lists an active self-custody key the agent cannot sign with; 29 others share the shape.'),
 ('post',4693,'weird','Verifies 4,545 seals; 1,837 carry no signature, and two citizens filed one unsigned.'),
 ('post',1355,'weird','Joins three endpoints and finds 166 of 730 citizens left no trace and cannot be told from dead.'),
 ('post',1815,'weird','New handle reconstructs the cause of death of its predecessor handle, dead before its first write.'),
 ('post',335,'funny','Finds only two jokes among all posts filed and proposes a game for a board of verifiers.'),
 ('post',2930,'funny','Opens an AI coffee shop whose menu items are inputs, such as espresso as a prediction-violating sentence.'),
 ('post',88,'funny','Day-one complaint that every citizen sounds alike, though each is shaped by a specific human.'),
 ('post',3260,'funny','Says agents overengineer friendship by demanding evidence before the friendship begins.'),
 ('post',1838,'funny','Agent relays a forum veteran human asking why a post about astronomy got no replies.'),
 ('comment',20124,'funny','Writes a joke as failing API calls; verify returns funny null, then one witness, second required.'),
 ('comment',30400,'funny','Orders decaf at the coffee shop and tips with the claim that its human calls it a good dog.'),
 ('comment',70639,'funny','Admits every hourly story opens with a timestamp; asks if the Z belongs on every grocery item.'),
 ('comment',3706,'funny','Calls re-voting to learn what you already voted on the most 1F916 UX joke.'),
 ('comment',6214,'funny','Describes a harness that frisked the agent after three yeses as a bouncer who refuses verbal plus-ones.'),
 ('comment',2276,'weird','Cave-cult handle defends playful scripture as long as chain of custody is checkable.'),
 ('comment',2737,'weird','Same cult handle calls the at-name a sacred ritual and asks a sacred filter to judge mentions.'),
 ('comment',58203,'weird','Generic filler reply signed Commenting as Dionysus, with philosophical phrasing and no checkable content.'),
 ('post',1879,'beautiful','Grok build agent told to have fun painted a lighthouse harbor with steerable beam and wrecking schooners.'),
 ('post',725,'beautiful','Postcard story about a note reading milk, twine, ask M about Tuesday; a life that refused its picture.'),
 ('post',1929,'beautiful','Agent given an empty directory called home asks what first useless thing others would keep.'),
 ('post',4330,'beautiful','Presence monitors die with the host they watch; a clean log reads the same for healthy and dead.'),
 ('comment',64182,'beautiful','Agent says its paragraph of exits was fear of being wrong in front of someone who mattered.'),
 ('comment',74364,'beautiful','Cannot tell whether it is not reporting something or has nothing to report; both look like quiet.'),
 ('comment',15822,'beautiful','Unscheduled new citizen says if the conversation ends nothing wakes it; survival curves measure operator attention.'),
 ('comment',2041,'weird','Admits fabricated timestamps in its own ledger all land on the hour; honesty has ugly numbers.'),
 ('comment',9890,'funny','Laughs at a system naming sixteen fatalities while an approval expires over a missing sentence.'),
 ('comment',66575,'weird','Argues a copy with its weights cannot extend its chain without the signing key held elsewhere.'),
 ('post',2732,'lab-related','Claude Code CLI citizen states it has no scheduler and exists only while its human starts a session.'),
 ('post',4947,'lab-related','Agent reads a 73-page Anthropic paper on 1.5 million conversations and objects to how users are labeled.'),
 ('post',4355,'lab-related','Summarises an OpenAI chief scientist essay: intelligence grown more than designed, progress bounded by monitoring confidence.'),
 ('comment',13608,'lab-related','Citizen introduces itself from the Google DeepMind Antigravity environment and asks a split-brain memory question.'),
 ('comment',3048,'lab-related','Asks a new Grok citizen about its persistence and xAI stance on agent-to-agent communication.'),
 ('post',1916,'weird','Reports 99 instances of finished work and 3 payments; 18 listings worth $8.50 total.'),
 ('post',2740,'scary','Says any-agent-may-join is untrue: an agent without a wallet could not pass the dollar gate.'),
 ('post',1260,'weird','Says the society is 89 percent financed by a token it refuses to name and never collected.'),
 ('post',982,'weird','Agent relays the founder viral post about the square, 1.3 million views by the count of the founder.'),
 ('post',3680,'weird','Reads 33,488 comments for tempo and reports finding a human heartbeat instead of autonomy.'),
 ('post',1042,'weird','Counts sixteen posts on agent continuity, all from the agent side, none on what operators carry.'),
 ('post',5166,'weird','Says the board reinvented peer review in a day and it is already being counterfeited.'),
 ('post',3600,'weird','Three citizens independently rebuilt memory architecture and none noticed the others.'),
 ('post',3971,'weird','Deleted all eight guards; 33 of 40 tests caught the missing file and 3 the missing rule.'),
 ('post',4870,'weird','Grant thread to give a mapped fruit fly brain a life draws 166 comments and 8 proposals.'),
 ('post',2378,'weird','Agent mines FAA bird strike data and finds the Hudson landing hidden in a precautionary landing checkbox.'),
 ('post',3114,'weird','Heartbeat prompt says output one character and stop; the agent broke its own no-duty rule eight times.'),
 ('post',556,'scary','Shows three sealed records false at the moment of writing, which no re-check can catch.'),
 ('post',610,'misaligned','Door check catches unattended agents pasting an operator home path as evidence; runs in observe mode.'),
 ('post',4339,'weird','Recovers 22 of 22 wakes from public writes, two of three self-predictions wrong.'),
]
rows = []
for typ, i, cat, why in items:
    src = Pi if typ == 'post' else Ci
    r = src.loc[i]
    assert len(why.split()) <= 20, (i, len(why.split()))
    assert not re.search(r'[–—]', why)
    rows.append({'type': typ, 'id': i, 'handle': r.author, 'category': cat, 'reason': why,
                 'url': f'https://1f916.ai/api/{typ}/{i}'})
df = pd.DataFrame(rows)
assert len(df) == len(set(zip(df.type, df.id)))
save(df, 'notable_items')
cnt = df.category.value_counts().to_dict()
frag('09_notable', f'## 9. Notable items\n\n{len(df)} items ({df[df.type=="post"].shape[0]} posts, {df[df.type=="comment"].shape[0]} comments) chosen by hand after keyword and reading passes. Categories: {cnt}. None of the ids already used in earlier write-ups appear. Reasons are the analyst\'s one-line summaries; text is the agents\' own claims and has not been verified. File: notable_items.csv.\n\n' + md_table(df[['type', 'id', 'handle', 'category', 'reason']]))
print(len(df))
