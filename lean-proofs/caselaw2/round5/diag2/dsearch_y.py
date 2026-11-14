"""diag step 3b: kind D keyed on the overruling decision Y only (any target).

Later Supreme Court decisions that cite Y and say, next to Y's citation or name, "overruling ...", "overruled by Y",
"in Y we overruled ...". Used to catch (a) targets the gold lists do not name and (b) the 10 decisions with no
listed target. Same-court statements only (Supreme Court on Supreme Court: feed side of the split).

    python dsearch_y.py grep     writes dsearch_y_files.tsv   (one git grep, about a minute)
    python dsearch_y.py scan     writes dsearch_y_hits.tsv
"""
import csv
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dsearch as D  # noqa: E402

RC = D.RC
CUE = re.compile(r"overrul|abrogat|disapprov", re.I)


def ys():
    with open(os.path.join(HERE, "pairs.tsv"), encoding="utf-8", newline="") as f:
        return sorted({r["by_node"] for r in csv.DictReader(f, delimiter="\t")}, key=int)


def us_only(cites):
    return [p for p in D.cite_patterns("|".join(c for c in cites.split("|") if " U.S. " in c))]


def do_grep():
    meta = D.load_meta()
    args = ["git", "-C", D.REPO, "grep", "-l", "-E"]
    n = 0
    for y in ys():
        for p in us_only(meta[y][5]):
            args += ["-e", p]
            n += 1
    args += ["HEAD", "--", "decisions"]
    res = subprocess.run(args, capture_output=True).stdout.decode("utf-8", "replace")
    files = sorted({l.split(":", 1)[1] for l in res.splitlines() if l.startswith("HEAD:")})
    with open(os.path.join(HERE, "dsearch_y_files.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for p in files:
            f.write(p + "\n")
    print("patterns", n, "files", len(files))


def do_scan():
    meta = D.load_meta()
    with open(os.path.join(HERE, "dsearch_y_files.tsv"), encoding="utf-8") as f:
        files = {l.strip() for l in f if l.strip()}
    node = {}
    with open(os.path.join(D.W, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 7)
            if p[1] == "supreme-court" and p[2] in files:
                node[p[2]] = (p[0], p[4], p[6])
    paths = sorted(node)
    pats = {}
    for y in ys():
        ym = meta[y]
        yc = re.compile("|".join(us_only(ym[5])))
        yt = sorted(RC.name_tokens(ym[6]), key=len, reverse=True)
        yn = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(t) for t in yt)) if yt else None
        pats[y] = (yc, yn, int(ym[4]))
    out = []
    B = 400
    for k in range(0, len(paths), B):
        chunk = paths[k:k + B]
        inp = "".join("HEAD:%s\n" % p for p in chunk).encode()
        res = subprocess.run(["git", "-C", D.REPO, "cat-file", "--batch"], input=inp, capture_output=True).stdout
        i = 0
        for p in chunk:
            nl = res.index(b"\n", i)
            hdr = res[i:nl].split()
            i = nl + 1
            if hdr[1] == b"missing":
                continue
            size = int(hdr[2])
            t = res[i:i + size].decode("utf-8", "replace").replace("\r\n", "\n")
            i += size + 1
            if not CUE.search(t):
                continue
            wn, wd, wname = node[p]
            pm, body0 = RC.part_map2(t)
            view = RC.unwrap_view(t, body0) if RC.hard_wrapped(t, body0) else t
            for y, (yc, yn, yd) in pats.items():
                if wn == y or not wd or int(wd) <= yd or not yc.search(view):
                    continue
                off = body0
                for line in view[body0:].split("\n"):
                    la = off
                    off += len(line) + 1
                    if len(line) < 20 or not CUE.search(line):
                        continue
                    refs = list(yc.finditer(line)) + (list(yn.finditer(line)) if yn else [])
                    if not refs:
                        continue
                    best = None
                    for c in CUE.finditer(line):
                        for r in refs:
                            # Y then "overruling X" (within 170), or "overruled by/in Y" (Y within 90 after the cue)
                            if 0 <= c.start() - r.end() <= 170 or 0 <= r.start() - c.end() <= 90:
                                d = min(abs(c.start() - r.end()), abs(r.start() - c.end()))
                                if best is None or d < best[0]:
                                    best = (d, c, r)
                    if not best:
                        continue
                    d, c, r = best
                    part, sec = RC.part_at(pm, la + c.start())
                    a = max(0, min(c.start(), r.start()) - 120)
                    b = min(len(line), max(c.end(), r.end()) + 220)
                    out.append([y, wn, wd, part, sec[:40], str(d), str(la + c.start()),
                                line[a:b].replace("\t", " ")])
    out.sort(key=lambda o: (int(o[0]), int(o[2]), int(o[6])))
    with open(os.path.join(HERE, "dsearch_y_hits.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("by_node\tw_node\tw_date\tpart\tsec\tdist\toffset\tsnippet\n")
        for o in out:
            f.write("\t".join(o) + "\n")
    print("files", len(paths), "hits", len(out))


if __name__ == "__main__":
    {"grep": do_grep, "scan": do_scan}[sys.argv[1]]()
