"""state8 rule R8S, step 1: the treatments reader's rejected candidate sentences that the repaired rules
(rescue_rules.py) send to reading. Whole corpus (every data/reader_work/cand/<repo>.jsonl.gz with its rejects).

    python -X utf8 rescue.py [--procs 10]

Writes work/rescue/<repo>.jsonl (one line per rescued sentence: id, n, s0, s1, reason, tag, part, refs, in_queue,
in_r7ante, sent) and work/rescue_stats.json. Not read later: items in the round-3 own-act queue (agent `ownact` reads
them), items the round-7 antecedent agent already packed, and act sentences that name two or more cases (agent
`multicase`). No answer-key file is read.
"""
import argparse, collections, gzip, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common8 import C2, RW, L  # noqa: E402
import rescue_rules as RR  # noqa: E402

OUTD = os.path.join(HERE, "work", "rescue")
PF_HEAD = 400
NAME_RX = re.compile(r"[A-Z][\w.&'’\-]*(?:\s+[A-Z&][\w.&'’\-]*){0,5}\s+(?:v\.?|vs\.?|against)\s+[A-Z]")
CITE_RX = re.compile(r"\b\d{1,4}\s+(?:[A-Z][A-Za-z.'’]{0,9}\s?){1,5}(?:\d[a-z]{1,2}\.?\s?)?(?:\([^)]{1,12}\)\s?)?,?\s*\d{1,5}\b")
CASE_WORD = re.compile(r"\bthe\s+[A-Z][\w'’\-]+\s+(?:case|decision)\b|\bIn\s+re\s+[A-Z]|\bEx\s+parte\s+[A-Z]")

G = {}


def init(queue, ante):
    G["queue"] = queue
    G["ante"] = ante


def count_refs(s):
    spans = [(m.start(), m.end()) for m in NAME_RX.finditer(s)] + [(m.start(), m.end()) for m in CASE_WORD.finditer(s)]
    for m in CITE_RX.finditer(s):
        # a citation right after a name (or another citation) is the same reference
        if any(a <= m.start() <= b + 70 for a, b in spans):
            spans.append((m.start(), m.end()))
            continue
        spans.append((m.start(), m.end()))
        spans.append((-1, -1))  # marker: a standalone citation group
    spans.sort()
    groups = 0
    last = -10 ** 9
    for a, b in spans:
        if a < 0:
            continue
        if a > last + 70:
            groups += 1
        last = max(last, b)
    return groups


def one(repo):
    rej = {}
    rp = os.path.join(RW, "res", repo + ".rejects.tsv.gz")
    if not os.path.exists(rp):
        return repo, {"no_rejects": 1}
    with gzip.open(rp, "rt", encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            rej[p[0]] = p[1]
    st = collections.Counter()
    cut = {}
    out = open(os.path.join(OUTD, repo + ".jsonl"), "w", encoding="utf-8", newline="\n")
    with gzip.open(os.path.join(RW, "cand", repo + ".jsonl.gz"), "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["t"] == "d":
                parts = r["parts"]
                for i, (a, b, p) in enumerate(parts):
                    if p in ("majority", "perCuriam") and i + 1 < len(parts) and parts[i + 1][2] == "concurrence~" \
                            and b - a < PF_HEAD:
                        cut[r["n"]] = (parts[i + 1][0], parts[i + 1][1], p)
                        break
                continue
            if r["t"] != "c":
                continue
            cid = "%d:%d" % (r["n"], r["s0"])
            why = rej.get(cid)
            if why is None:
                continue
            st["rejected"] += 1
            sent = r["w"][r["s0"] - r["w0"]:r["s1"] - r["w0"]]
            fams = list(r.get("fam") or [])
            pf = False
            part = r.get("part", "")
            if why == "separate-opinion" and r["n"] in cut:
                a, b, p0 = cut[r["n"]]
                if a <= r["s0"] < b and part == "concurrence~":
                    pf = True
                    part = p0
            tag = RR.rescue(sent, fams, part, why, pf)
            if not tag:
                continue
            st["rescued"] += 1
            st["tag:" + tag.split(">")[-1].split(":")[0] + ":" + why] += 1
            refs = count_refs(sent)
            rec = {"id": cid, "n": r["n"], "s0": r["s0"], "s1": r["s1"], "reason": why, "tag": tag, "part": part,
                   "refs": refs, "in_queue": cid in G["queue"], "in_r7ante": cid in G["ante"], "sent": sent}
            st["q" if rec["in_queue"] else ("a" if rec["in_r7ante"] else ("multi" if refs >= 2 else "mine"))] += 1
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    out.close()
    return repo, dict(st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(OUTD, exist_ok=True)
    queue = set(l.split("\t", 1)[0] for l in open(os.path.join(C2, "work", "round3", "queue", "queue_snapshot.tsv"),
                                                  encoding="utf-8"))
    ante = set()
    mp = os.path.join(C2, "round7", "agents", "antecedent", "packs", "map.jsonl")
    for line in open(mp, encoding="utf-8"):
        ante.add(json.loads(line)["id"])
    repos = sorted(f[:-9] for f in os.listdir(os.path.join(RW, "cand")) if f.endswith(".jsonl.gz"))
    tot = collections.Counter()
    per = {}
    import multiprocessing as mpp
    with mpp.Pool(a.procs, initializer=init, initargs=(queue, ante)) as pool:
        for repo, st in pool.imap_unordered(one, repos, chunksize=1):
            tot.update(st)
            per[repo] = st
    json.dump({"total": dict(tot), "per_repo": per}, open(os.path.join(HERE, "work", "rescue_stats.json"), "w"),
              indent=1)
    print(json.dumps(dict(sorted(tot.items())), indent=1))


if __name__ == "__main__":
    main()
