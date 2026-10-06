"""Flag every post and comment for money themes (regex, multi-label). Slow step (about 1 to 3 minutes with a process pool); writes csv/talk_flags.csv.gz."""
from common import *
from themes import *
from multiprocessing import Pool

def work(args):
    kind, i, text = args
    core = bool(CORE.search(text))
    return kind, i, int(core), "|".join(themes_of(text)) if core else ""

if __name__ == "__main__":
    P = pd.DataFrame(rd("posts")); C = pd.DataFrame(rd("comments"))
    P["text"] = P.title.fillna("") + "\n" + P.body.fillna(""); C["text"] = C.body.fillna("")
    jobs = [("post", r.id, r.text) for r in P.itertuples()] + [("comment", r.id, r.text) for r in C.itertuples()]
    with Pool(max(2, (os.cpu_count() or 4) - 1)) as pool:
        res = pool.map(work, jobs, chunksize=500)
    F = pd.DataFrame(res, columns=["kind", "id", "core", "themes"])
    meta = pd.concat([P[["id", "author", "created_at", "mod_state"]].assign(kind="post"), C[["id", "author", "created_at", "mod_state"]].assign(kind="comment")])
    F = F.merge(meta, on=["kind", "id"])
    F["day"] = F.created_at.map(day)
    F.to_csv(CSV / "talk_flags.csv.gz", index=False)
    print(F.groupby("kind").core.agg(["count", "sum"]))
