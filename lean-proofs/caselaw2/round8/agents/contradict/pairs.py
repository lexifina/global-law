"""Rebuild the base-vs-new contradiction pairs against the round-7 frozen build v3.

    python -X utf8 round8/agents/contradict/pairs.py [--procs 10]

Inputs (no answer key):
  round6/history/rules/{below_other,below_sc,rehear}/cert/rejects.tsv   conflictBase rejects (row line, base id)
  round6/history/rules/<x>/rows.jsonl                                    the rejected new rows
  round7/stage/v3/history.tsv, round7/out/v3/certs.tsv                   base row still present + admitted?
  round6/history/cache/<repo>.*.jsonl.gz                                 `z` parts + `h` own disposition sentences
Output (this folder):
  work/pairs.tsv     one line per (new row, base row) pair with the sub-case columns
  work/pairs.json    counts per sub-case
  work/rows_new.jsonl the new rows (round-6 row JSON), keyed by pair id
"""
import argparse, collections, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

RULES = os.path.join(C2, "round6", "history", "rules")
SRCS = ("below_other", "below_sc", "rehear")
V3S = os.path.join(C2, "round7", "stage", "v3")
V3O = os.path.join(C2, "round7", "out", "v3")
WORK = os.path.join(HERE, "work")
NEG = frozenset(("reversed", "vacated", "withdrawn", "substitutedBy", "depublished"))
POS = frozenset(("affirmed", "certDenied", "reviewDismissed", "writRefused", "reinstated"))
COURT_PARTS = frozenset(("majority", "perCuriam"))


def pol(k):
    return "neg" if k in NEG else ("pos" if k in POS else "neutral")


def scan_shard(args):
    path, want = args
    out = {}
    for n, g in L.decisions(path):
        if n in want:
            z = g["z"]
            out[n] = {"parts": z["parts"] if z else None,
                      "h": [(r["k"], r["s"][0], r["s"][1], r["m"][0], r["m"][1], r["part"]) for r in g["h"]]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)

    # ---- the rejected new rows
    pairs = []
    for src in SRCS:
        rows = open(os.path.join(RULES, src, "rows.jsonl"), encoding="utf-8").read().splitlines()
        for line in open(os.path.join(RULES, src, "cert", "rejects.tsv"), encoding="utf-8"):
            p = line.rstrip("\n").split("\t")
            if len(p) < 7 or p[1] != "conflictBase":
                continue
            ln = int(p[0].rsplit(":", 1)[1])
            r = json.loads(rows[ln - 1])
            assert r["by"] == int(p[3]) and r["target"] == int(p[4]) and r["kind"] == p[5], (src, ln)
            pairs.append({"src": src, "line": ln, "row": r, "base_id": p[6]})

    # ---- base rows in v3
    need_pairs = {(x["row"]["by"], x["row"]["target"]) for x in pairs}
    hist = {}
    pair_rows = collections.defaultdict(list)
    with open(os.path.join(V3S, "history.tsv"), encoding="utf-8", newline="\n") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            key = (int(p[2]), int(p[1]))
            if key in need_pairs:
                hist[p[0]] = p
                pair_rows[key].append(p[0])
    certs = {}
    with open(os.path.join(V3O, "certs.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] == "history" and p[1] in hist:
                certs[p[1]] = (p[2], p[3])

    # ---- own disposition sentences (cache `h`) of the acting decisions
    bys = {x["row"]["by"] for x in pairs}
    repos = collections.defaultdict(set)
    for n in bys:
        repos[L.node_row(n)[1]].add(n)
    jobs = []
    for path in L.shards():
        repo = os.path.basename(path).rsplit(".", 3)[0]
        if repo in repos:
            jobs.append((path, repos[repo]))
    cache = {}
    for res in L.pmap(scan_shard, jobs, procs=a.procs):
        cache.update(res)
    texts = L.fetch_texts(bys)

    out = []
    cnt = collections.Counter()
    for i, x in enumerate(pairs):
        r = x["row"]
        by, tg = r["by"], r["target"]
        b = hist.get(x["base_id"])
        cs = certs.get(x["base_id"], ("absent", "absent"))
        rec = {"pid": "c%03d" % i, "src": x["src"], "line": x["line"], "rule": r["rule"], "by": by, "target": tg,
               "new_kind": r["kind"], "new_scope": r["scope"], "new_s": r["disp"][0], "new_e": r["disp"][1],
               "new_part": r.get("part", "-"), "base_id": x["base_id"], "base_present": int(b is not None),
               "base_cert": cs[0]}
        if b is None:
            rec.update(base_kind="-", base_scope="-", base_s=-1, base_e=-1, base_rule="-", same_text=0)
        else:
            rec.update(base_kind=b[4], base_scope=b[5], base_s=int(b[7]), base_e=int(b[8]), base_rule=b[12],
                       base_part=b[11])
            sha = texts.get(by, ("?", ""))[0]
            rec["same_text"] = int(sha == b[6])
        # position of the new quote relative to the base quote
        if rec["base_s"] < 0 or rec["base_e"] <= rec["base_s"]:
            pos = "nospan"
        elif rec["new_s"] >= rec["base_e"]:
            pos = "after"
        elif rec["new_e"] <= rec["base_s"]:
            pos = "before"
        else:
            pos = "overlap"
        rec["pos"] = pos
        # final own disposition: no later own disposition sentence (court parts) of another polarity
        c = cache.get(by)
        if c is None:
            rec["final"] = "nocache"
        else:
            later = [h for h in c["h"] if h[5] in COURT_PARTS and h[1] >= rec["new_e"]]
            opp = [h for h in later if pol(h[0]) != pol(r["kind"])]
            rec["final"] = "final" if not later else ("final_samepol" if not opp else "later_opp")
            rec["n_h"] = len(c["h"])
            # is the new quote one of the court's own disposition sentences (cache `h`, reader HIST)?
            hit = [h for h in c["h"] if h[3] >= rec["new_s"] and h[4] <= rec["new_e"]]
            rec["new_is_h"] = ("h_court" if any(h[5] in COURT_PARTS for h in hit) else "h_other") if hit else "no_h"
            if rec["base_s"] >= 0:
                bh = [h for h in c["h"] if h[3] >= rec["base_s"] and h[4] <= rec["base_e"]]
                rec["base_is_h"] = ("h_court" if any(h[5] in COURT_PARTS for h in bh) else "h_other") if bh else "no_h"
        others = [h for h in pair_rows.get((by, tg), ()) if h != x["base_id"]]
        rec["v3_others"] = "|".join(others) if others else "-"
        rec["scopes"] = "%s/%s" % (rec["new_scope"], rec.get("base_scope", "-"))
        rec["admitted"] = int(cs[0].startswith("ok"))
        cnt["src:" + x["src"]] += 1
        cnt["base_present:%d" % rec["base_present"]] += 1
        cnt["base_cert:" + cs[0]] += 1
        if rec["admitted"]:
            cnt["adm|pos:" + pos] += 1
            cnt["adm|final:" + rec["final"]] += 1
            cnt["adm|scopes:" + rec["scopes"]] += 1
            cnt["adm|same_text:%d" % rec["same_text"]] += 1
            cnt["adm|%s|%s|%s" % (x["src"], pos, rec["final"])] += 1
            cnt["adm|kinds:%s<-%s" % (r["kind"], rec["base_kind"])] += 1
            cnt["adm|new_is_h:%s|pos:%s" % (rec.get("new_is_h"), pos)] += 1
            cnt["adm|base_is_h:%s" % rec.get("base_is_h")] += 1
            if others:
                cnt["adm|v3_other_rows_for_pair"] += 1
        out.append(rec)

    cols = ["pid", "src", "line", "rule", "by", "target", "new_kind", "new_scope", "new_s", "new_e", "new_part",
            "base_id", "base_present", "base_cert", "admitted", "base_kind", "base_scope", "base_s", "base_e",
            "base_rule", "same_text", "pos", "final", "scopes", "v3_others", "new_is_h", "base_is_h"]
    with open(os.path.join(WORK, "pairs.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for rec in out:
            f.write("\t".join(str(rec.get(c, "-")) for c in cols) + "\n")
    with open(os.path.join(WORK, "rows_new.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for i, x in enumerate(pairs):
            f.write(json.dumps(dict(x["row"], pid="c%03d" % i)) + "\n")
    json.dump(dict(sorted(cnt.items())), open(os.path.join(WORK, "pairs.json"), "w"), indent=1)
    for k, v in sorted(cnt.items()):
        print("%-50s %d" % (k, v))


if __name__ == "__main__":
    main()
