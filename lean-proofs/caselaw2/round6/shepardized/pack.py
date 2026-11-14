#!/usr/bin/env python3
"""Build the reading pack for the disagreement analysis (step 4).

Usage: python -I pack.py [--tag asof20101119] [--seed 20261113] [--n 40]
Reads results/<tag>/cases.tsv and citers.tsv, graph/nodes.tsv, and decision texts from ~/Documents/us-caselaw-repos
(git cat-file HEAD:<path>). Writes results/<tag>/sample.tsv (the sampled cases) and results/<tag>/pack.txt (for each
sampled case: the Shepardized codes, the model rows, the opening of the target decision, and for every later
same-case candidate the passages around the citation of the target and the closing words).

Types sampled:
  A  Shepardized NEG, model not NEG_HIST          (random n, fixed seed)
  B  Shepardized PART, model CLEAN                (all, or random n)
  C  model NEG_HIST, Shepardized CLEAN            (all)
  D  both negative but kind or actor differs      (all)
"""
import argparse
import collections
import csv
import os
import random
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH = os.path.join(HERE, "..", "..", "..", "graph")
REPOS = os.path.join(os.path.expanduser("~"), "Documents", "us-caselaw-repos")
STOP = set("""v vs the of and in re ex parte rel et al inc co corp corporation company ltd united states america state
people commonwealth city county board commissioner commission national association assn dept department for
matter estate administrator secretary director general attorney labor relations internal revenue insurance bank
railroad railway""".split())


def toks(name):
    return {t for t in re.findall(r"[a-z]{3,}", name.lower()) if t not in STOP}


def text_of(repo, path):
    try:
        b = subprocess.run(["git", "-C", os.path.join(REPOS, repo), "cat-file", "-p", "HEAD:" + path],
                           capture_output=True, timeout=60).stdout
    except Exception:
        return ""
    return b.decode("utf-8", "replace").replace("\r\n", "\n")


def body(t):
    i = t.find("\n---", 3)
    return t[i + 4:] if t.startswith("---") and i > 0 else t


def flat(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="asof20101119")
    ap.add_argument("--seed", type=int, default=20261113)
    ap.add_argument("--n", type=int, default=40)
    a = ap.parse_args()
    res = os.path.join(HERE, "results", a.tag)
    cases = list(csv.DictReader(open(os.path.join(res, "cases.tsv"), encoding="utf-8", newline=""), delimiter="\t",
                                quoting=csv.QUOTE_NONE))
    L = [c for c in cases if c["node"]]
    A = [c for c in L if c["sclass"] == "NEG" and c["mclass"] != "NEG_HIST"]
    B = [c for c in L if c["sclass"] == "PART" and c["mcol"] == "CLEAN"]
    C = [c for c in L if c["mclass"] == "NEG_HIST" and c["sclass"] in ("CLEAN", "MOD")]
    D = [c for c in L if c["mclass"] == "NEG_HIST" and c["sclass"] in ("NEG", "PART")]
    rnd = random.Random(a.seed)
    A_s = sorted(rnd.sample(A, min(a.n, len(A))), key=lambda c: int(c["casenum"]))
    B_s = sorted(rnd.sample(B, min(a.n, len(B))), key=lambda c: int(c["casenum"]))
    picks = [("A", c) for c in A_s] + [("B", c) for c in B_s] + [("C", c) for c in C] + [("D", c) for c in D]

    citers = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(res, "citers.tsv"), encoding="utf-8", newline=""), delimiter="\t",
                            quoting=csv.QUOTE_NONE):
        citers[r["casenum"]].append(r)
    # node metadata for targets, citers, model actors; and Supreme Court nodes by year for name search
    need = set()
    for _, c in picks:
        need.add(c["node"])
        if c["mactor"] not in ("", "-"):
            need.add(c["mactor"])
        for r in citers[c["casenum"]]:
            need.add(r["citing"])
    meta = {}
    scotus = collections.defaultdict(list)
    with open(os.path.join(GRAPH, "nodes.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            if p[0] in need:
                meta[p[0]] = p
            if p[1] == "supreme-court":
                scotus[p[4][:4]].append(p)

    with open(os.path.join(res, "sample.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("type\tcasenum\tcite\tnode\tname\tssub\tmstatus\n")
        for t, c in picks:
            o.write("\t".join([t, c["casenum"], c["cite"], c["node"], c["name"], c["ssub"], c["mstatus"]]) + "\n")

    out = open(os.path.join(res, "pack.txt"), "w", encoding="utf-8", newline="\n")
    for t, c in picks:
        tm = meta[c["node"]]
        vol, ser, pg = re.match(r"(\d+) f(2d|3d) (\d+)", c["cite"]).groups()
        citre = re.compile(r"%s\s*F\.\s*%s\s*%s\b" % (vol, ser, pg))
        out.write("=" * 100 + "\n")
        out.write("[%s] casenum %s | %s | node %s | %s | circuit %s | decided %s\n" % (
            t, c["casenum"], tm[5], c["node"], tm[6], c["circuit"], tm[4]))
        out.write("Shepardized: class %s/%s appeal=%s coarehear=%s coaenbanc=%s scappeal=%s scresult=%s appaftre1=%s "
                  "us1=%s us2=%s method=%s\n" % (c["sclass"], c["ssub"], c["appeal"], c["coarehear"], c["coaenbanc"],
                                                 c["scappeal"], c["scresult"], c["appaftre1"], c["us1"], c["us2"],
                                                 c["method"]))
        out.write("Model: %s path=%s witness=%s actor=%s | history rows: %s\n" % (
            c["mstatus"], c["mpath"], c["mwitness"], c["mactor"], c["hist_rows"] or "none"))
        tb = body(text_of(tm[1], tm[2]))
        hm = tb.find("## Head matter")
        out.write("TARGET head: " + flat(tb[hm:hm + 700]) + "\n")
        out.write("TARGET end: " + flat(tb[-350:]) + "\n")
        cand = []
        for r in citers[c["casenum"]]:
            dy = int(r["date"][:4]) - int(tm[4][:4])
            if r["same_case_guess"] == "1" and dy <= 6:
                cand.append((r["citing"], "cites target; shared: " + r["shared"]))
        seen = {x[0] for x in cand}
        if c["mactor"] not in ("", "-") and c["mactor"] not in seen:
            cand.append((c["mactor"], "model actor"))
            seen.add(c["mactor"])
        tt = toks(tm[6])
        named = []
        for y in range(int(tm[4][:4]), int(tm[4][:4]) + 4):
            for p in scotus.get(str(y), []):
                if p[0] in seen or p[4] < tm[4]:
                    continue
                pt = toks(p[6])
                sh = tt & pt
                if sh and len(sh) / len(tt | pt) >= 0.5:
                    named.append(p)
        for p in named[:6]:
            meta[p[0]] = p
            cand.append((p[0], "Supreme Court, same name, does NOT cite target"))
        if not cand:
            out.write("LATER: no later same-case candidate in the corpus (no Supreme Court or same-circuit decision "
                      "citing it with a shared party name within 6 years; no Supreme Court decision with the same "
                      "name within 3 years)\n")
        for n, why in cand[:8]:
            m = meta[n]
            x = body(text_of(m[1], m[2]))
            out.write("LATER node %s | %s | %s | %s | %s | %s | %d chars\n" % (n, m[1], m[4], m[5], m[6], why, len(x)))
            k = 0
            for mm in citre.finditer(x):
                if k >= 3:
                    break
                s, e = max(0, mm.start() - 350), min(len(x), mm.end() + 350)
                out.write("   AT CITE: ..." + flat(x[s:e]) + "...\n")
                k += 1
            if len(x) < 1500:
                out.write("   FULL: " + flat(x) + "\n")
            else:
                h2 = x.find("## Head matter")
                out.write("   HEAD: " + flat(x[h2:h2 + 500]) + "\n")
                # closing words of the majority part
                parts = [mm.start() for mm in re.finditer(r"\n## ", x)]
                endmaj = len(x)
                for i, s in enumerate(parts):
                    if re.match(r"\n## (Majority|Per Curiam|Combined|Lead|Plurality)", x[s:s + 30]):
                        endmaj = parts[i + 1] if i + 1 < len(parts) else len(x)
                        break
                out.write("   END OF MAJORITY: ..." + flat(x[max(0, endmaj - 450):endmaj]) + "\n")
    out.close()
    # split for readers: A in two halves, B, C+D
    txt = open(os.path.join(res, "pack.txt"), encoding="utf-8").read().split("=" * 100 + "\n")[1:]
    groups = {"A1": [], "A2": [], "B": [], "CD": []}
    na = 0
    for e in txt:
        if e.startswith("[A]"):
            groups["A1" if na < (len(A_s) + 1) // 2 else "A2"].append(e)
            na += 1
        elif e.startswith("[B]"):
            groups["B"].append(e)
        else:
            groups["CD"].append(e)
    for g, es in groups.items():
        with open(os.path.join(res, "pack_%s.txt" % g), "w", encoding="utf-8", newline="\n") as o:
            o.write(("=" * 100 + "\n").join([""] + es))
    print("A %d of %d, B %d of %d, C %d, D %d -> %s" % (len(A_s), len(A), len(B_s), len(B), len(C), len(D),
                                                       os.path.join(res, "pack.txt")))


if __name__ == "__main__":
    main()
