"""diag step 3: text search for kind D. Later Supreme Court decisions that say "X was overruled (by Y)".

For every pair (Y, X) of pairs.tsv (+ pairs_extra.tsv) with a known X:
  1. `git grep -l` over the supreme-court repo at HEAD for any citation of X (U.S., nominative, S. Ct.);
  2. keep the files decided after Y (date from graph/nodes.tsv, streamed), fetch them from git;
  3. print every paragraph that names X (citation or party token) with a status cue nearby.
A Supreme Court decision speaking about a Supreme Court decision is always on the `feed` side of the round-5 notes
split (same court), so no holdout statement is read here.

    python dsearch.py grep        step 1 (writes dsearch_files.tsv; about one minute)
    python dsearch.py scan        steps 2-3 (writes dsearch_hits.tsv)
"""
import csv
import os
import re
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(HERE))
W = os.path.dirname(C2)
REPO = os.path.expanduser("~/Documents/us-caselaw-repos/supreme-court")
sys.path.insert(0, os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/reader"))
import common as RC  # noqa: E402

NOM = {"Dall.": "Dall", "Cranch": "Cranch", "Wheat.": "Wheat", "Pet.": "Pet", "How.": "How", "Black": "Black",
       "Wall.": "Wall"}
CUE = re.compile(r"overrul|abrogat|repudiat|overturn|disapprov|no longer (?:good )?law|discredit|abandon|"
                 r"reject|disavow|discard|interred|overthrown|not survive|eroded|undermined", re.I)


def load_pairs():
    out = []
    for fn in ("pairs.tsv", "pairs_extra.tsv"):
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            with open(p, encoding="utf-8", newline="") as f:
                out += [r for r in csv.DictReader(f, delimiter="\t") if r["target_node"] not in ("-1", "-2", "")]
    return out


def load_meta():
    m = {}
    with open(os.path.join(HERE, "nodes_meta.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            m[p[0]] = p
    return m


def cite_patterns(cites):
    """ERE alternatives for the citations of one decision (git grep -E and python re compatible)."""
    pats = []
    for c in cites.split("|"):
        m = re.match(r"^(\d+) U\.S\. (\d+)$", c)
        if m:
            pats.append(r"%s U\. ?S\.,? %s([^0-9]|$)" % m.groups())
            continue
        m = re.match(r"^(\d+) (Dall\.|Cranch|Wheat\.|Pet\.|How\.|Black|Wall\.) (\d+)$", c)
        if m:
            pats.append(r"%s %s\.?,? %s([^0-9]|$)" % (m.group(1), NOM[m.group(2)], m.group(3)))
            continue
        m = re.match(r"^(\d+) S\. Ct\. (\d+)$", c)
        if m:
            pats.append(r"%s S\. ?Ct\. %s([^0-9]|$)" % m.groups())
    return pats


def do_grep():
    pairs = load_pairs()
    meta = load_meta()
    xs = sorted({p["target_node"] for p in pairs}, key=int)
    hits = defaultdict(set)
    # one git grep per chunk of targets keeps each command line short; -l output then re-attributed in scan
    allp = []
    for x in xs:
        allp += cite_patterns(meta[x][5])
    args = ["git", "-C", REPO, "grep", "-l", "-E"]
    for p in allp:
        args += ["-e", p]
    args += ["HEAD", "--", "decisions"]
    res = subprocess.run(args, capture_output=True).stdout.decode("utf-8", "replace")
    files = sorted({l.split(":", 1)[1] for l in res.splitlines() if l.startswith("HEAD:")})
    with open(os.path.join(HERE, "dsearch_files.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for p in files:
            f.write(p + "\n")
    print("targets", len(xs), "patterns", len(allp), "files", len(files))


def do_scan():
    pairs = load_pairs()
    meta = load_meta()
    with open(os.path.join(HERE, "dsearch_files.tsv"), encoding="utf-8") as f:
        files = {l.strip() for l in f if l.strip()}
    node = {}
    with open(os.path.join(W, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 7)
            if p[1] == "supreme-court" and p[2] in files:
                node[p[2]] = (p[0], p[4], p[6])
    paths = sorted(node)
    inp = "".join("HEAD:%s\n" % p for p in paths).encode()
    res = subprocess.run(["git", "-C", REPO, "cat-file", "--batch"], input=inp, capture_output=True).stdout
    texts = {}
    i = 0
    for p in paths:
        nl = res.index(b"\n", i)
        hdr = res[i:nl].split()
        i = nl + 1
        if hdr[1] == b"missing":
            continue
        size = int(hdr[2])
        texts[p] = res[i:i + size].decode("utf-8", "replace").replace("\r\n", "\n")
        i += size + 1
    print("files", len(paths), "texts", len(texts))
    prepared = {}
    for p, t in texts.items():
        pm, body0 = RC.part_map2(t)
        view = RC.unwrap_view(t, body0) if RC.hard_wrapped(t, body0) else t
        prepared[p] = (view, pm, body0)
    out = []
    for pr in pairs:
        y, x = pr["by_node"], pr["target_node"]
        ym, xm = meta[y], meta[x]
        xc = re.compile("|".join(cite_patterns(xm[5])))
        yc = re.compile("|".join(cite_patterns(ym[5])))
        xt = sorted(RC.name_tokens(xm[6]) | RC.name_tokens(pr.get("target_name", "")), key=len, reverse=True)
        yt = sorted(RC.name_tokens(ym[6]), key=len, reverse=True)
        xn = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(t) for t in xt)) if xt else None
        yn = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(t) for t in yt)) if yt else None
        for p, (view, pm, body0) in prepared.items():
            wn, wd, wname = node[p]
            if wn in (y, x) or not wd or int(wd) <= int(ym[4]):
                continue
            if not xc.search(view):
                continue
            off = body0
            for line in view[body0:].split("\n"):
                la = off
                off += len(line) + 1
                if len(line) < 20:
                    continue
                refs = [m for m in xc.finditer(line)] + ([m for m in xn.finditer(line)] if xn else [])
                if not refs:
                    continue
                best = None
                for c in CUE.finditer(line):
                    for r in refs:
                        d = min(abs(c.start() - r.end()), abs(r.start() - c.end()))
                        if d <= 260 and (best is None or d < best[0]):
                            best = (d, c, r)
                if not best:
                    continue
                d, c, r = best
                a = max(0, min(c.start(), r.start()) - 160)
                b = min(len(line), max(c.end(), r.end()) + 200)
                has_y = bool(yc.search(line) or (yn and yn.search(line)))
                part, sec = RC.part_at(pm, la + c.start())
                out.append([y, x, wn, wd, part, sec[:40], "1" if has_y else "0", str(d), str(la + c.start()),
                            line[a:b].replace("\t", " ")])
    out.sort(key=lambda o: (int(o[0]), int(o[1]), int(o[3]), int(o[8])))
    with open(os.path.join(HERE, "dsearch_hits.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("by_node\ttarget_node\tw_node\tw_date\tpart\tsec\thas_y\tdist\toffset\tsnippet\n")
        for o in out:
            f.write("\t".join(o) + "\n")
    print("hits", len(out))


if __name__ == "__main__":
    {"grep": do_grep, "scan": do_scan}[sys.argv[1]]()
