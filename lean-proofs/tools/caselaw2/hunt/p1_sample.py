"""Pattern 1, step 3: draw the LLM sample from the passages, with weights for corpus estimates.

Strata (passages with at least one located citation):
  O-silent  citesOverruled, no negative-history word, no citation of the negating decision near or anywhere:
            up to 3 rows per cited decision (weight = rows of that decision / rows drawn)
  O-ack     citesOverruled with an acknowledgement cue: 400 at random (leak check)
  V-silent  citesVacated, silent: up to 1 row per cited decision, 1,500 decisions at random
  V-ack     citesVacated with a cue: 200 at random
    python p1_sample.py  -> hunt/work/p1_llm_in.jsonl
"""
import json, os, random
from collections import defaultdict
import hcommon as C

random.seed(20261112)


def main():
    src = os.path.join(C.HWORK, "p1_passages.jsonl")
    groups = defaultdict(lambda: defaultdict(list))
    for line in open(src, encoding="utf-8"):
        r = json.loads(line)
        if r["hits"] <= 0:
            continue
        ack = bool(r["ack_word"] or r["ack_actor"] or r["actor_any"])
        s = ("O-" if r["kind"] == "citesOverruled" else "V-") + ("ack" if ack else "silent")
        groups[s][r["cited"]].append(r)
    out = []
    n_tot = {s: sum(len(v) for v in g.values()) for s, g in groups.items()}
    # O-silent
    for cited, rows in groups["O-silent"].items():
        k = min(3, len(rows))
        for r in random.sample(rows, k):
            out.append(dict(r, stratum="O-silent", weight=len(rows) / k))
    for s, n in (("O-ack", 400), ("V-ack", 200)):
        allr = [r for rows in groups[s].values() for r in rows]
        pick = random.sample(allr, min(n, len(allr)))
        for r in pick:
            out.append(dict(r, stratum=s, weight=len(allr) / len(pick)))
    vs = list(groups["V-silent"].items())
    pick = random.sample(vs, min(1500, len(vs)))
    tot_v = n_tot["V-silent"]
    for cited, rows in pick:
        r = random.choice(rows)
        out.append(dict(r, stratum="V-silent", weight=tot_v / len(pick)))
    seen = set()
    with open(os.path.join(C.HWORK, "p1_llm_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in out:
            r["hkey"] = "%s|%s|%s|%s" % (r["kind"], r["citing"], r["cited"], r["issue"])
            if r["hkey"] in seen:
                continue
            seen.add(r["hkey"])
            f.write(json.dumps(r) + "\n")
    C.log("strata totals", n_tot, "sampled", len(seen))


if __name__ == "__main__":
    main()
