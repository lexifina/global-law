"""calpart9 rule PJ, step 2 (treatments): the reader's candidate sentences rejected `separate-opinion` that lie in a
part rule PJ moves back to the opinion of the court, re-classified with the reader's rules as majority
(state8 rescue_rules.rescue with part_fixed=True, unchanged).

    python -X utf8 rescue9.py [--procs 8]

In: work/scan/*.jsonl (scan_parts.py; decisions where PJ changes the part_map2 map), data/reader_work/cand + res.
Out: work/rescue/<repo>.jsonl (state8 rescue.py format; tag "PF..." = part repaired) and work/rescue_stats.json.
Items state8 already rescued and sent to reading (round8/agents/state8/work/rescue) are marked in_state8 and skipped
later. No answer-key file is read.
"""
import argparse
import collections
import glob
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import partzone as PZ  # noqa: E402
import rescue_rules as RR  # noqa: E402
from rescue import count_refs  # noqa: E402

C2 = PZ.C2
L = PZ.L
RW = os.path.join(C2, "data", "reader_work")
OUTD = os.path.join(HERE, "work", "rescue")
BASEP = ("majority", "majority~", "perCuriam", "plurality")
G = {}


def init(queue, ante, s8):
    G.update(queue=queue, ante=ante, s8=s8)


def one(job):
    repo, nodes = job
    rej = {}
    rp = os.path.join(RW, "res", repo + ".rejects.tsv.gz")
    st = collections.Counter()
    if not os.path.exists(rp):
        return repo, {"no_rejects": 1}
    with gzip.open(rp, "rt", encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            n = int(p[0].split(":")[0])
            if n in nodes:
                rej[p[0]] = p[1]
    cands = collections.defaultdict(list)
    with gzip.open(os.path.join(RW, "cand", repo + ".jsonl.gz"), "rt", encoding="utf-8") as f:
        for line in f:
            if '"t": "c"' not in line[:12] and '"t":"c"' not in line[:12]:
                continue
            r = json.loads(line)
            if r["n"] in nodes:
                cid = "%d:%d" % (r["n"], r["s0"])
                if rej.get(cid) == "separate-opinion":
                    cands[r["n"]].append(r)
    st["sep_rejects"] = sum(len(v) for v in cands.values())
    texts = L.fetch_texts(list(cands)) if cands else {}
    out = open(os.path.join(OUTD, repo + ".jsonl"), "w", encoding="utf-8", newline="\n")
    for n, rs in cands.items():
        if n not in texts:
            st["no_text"] += len(rs)
            continue
        text = texts[n][1]
        _hw, pm, new, ch = PZ.part_maps(text)
        for r in rs:
            st["in_pj_node"] += 1
            po, _ = PZ.C.part_at(pm, r["s0"])
            pn, _ = PZ.C.part_at(new, r["s0"])
            if not (po in ("concurrence~", "dissent~") and pn in BASEP):
                st["not_moved"] += 1
                continue
            st["moved"] += 1
            cid = "%d:%d" % (r["n"], r["s0"])
            sent = r["w"][r["s0"] - r["w0"]:r["s1"] - r["w0"]]
            fams = list(r.get("fam") or [])
            tag = RR.rescue(sent, fams, pn, "separate-opinion", True)
            if not tag:
                st["not_act"] += 1
                continue
            st["rescued"] += 1
            refs = count_refs(sent)
            rec = {"id": cid, "n": r["n"], "s0": r["s0"], "s1": r["s1"], "reason": "separate-opinion",
                   "tag": tag, "part": pn, "refs": refs, "in_queue": cid in G["queue"], "in_r7ante": cid in G["ante"],
                   "in_state8": cid in G["s8"], "sent": sent}
            st["state8" if rec["in_state8"] else ("q" if rec["in_queue"] else (
                "a" if rec["in_r7ante"] else ("multi" if refs >= 2 else "mine")))] += 1
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    out.close()
    return repo, dict(st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(OUTD, exist_ok=True)
    pj = collections.defaultdict(set)
    for p in glob.glob(os.path.join(HERE, "work", "scan", "*.jsonl")):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if r["kind"] == "PJ" and "pm2" in r:
                pj[r["repo"]].add(int(r["n"]))
    print("PJ (pm2) decisions", sum(len(v) for v in pj.values()), "repos", len(pj), flush=True)
    queue = set(ln.split("\t", 1)[0] for ln in open(os.path.join(C2, "work", "round3", "queue",
                                                                  "queue_snapshot.tsv"), encoding="utf-8"))
    ante = set(json.loads(ln)["id"] for ln in open(os.path.join(C2, "round7", "agents", "antecedent", "packs",
                                                                "map.jsonl"), encoding="utf-8"))
    s8 = set()
    for p in glob.glob(os.path.join(C2, "round8", "agents", "state8", "work", "rescue", "*.jsonl")):
        for ln in open(p, encoding="utf-8"):
            s8.add(json.loads(ln)["id"])
    tot = collections.Counter()
    for repo, st in L.pmap(one, sorted(pj.items(), key=lambda kv: -len(kv[1])), procs=a.procs, initializer=init,
                           initargs=(queue, ante, s8)):
        tot.update(st)
        print(repo, json.dumps(st), flush=True)
    print("TOTAL", json.dumps(dict(tot)), flush=True)
    json.dump(dict(tot), open(os.path.join(HERE, "work", "rescue_stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
