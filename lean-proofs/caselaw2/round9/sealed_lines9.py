"""Round 9 (agent infra9): one SEALED_LOG.md line from a sealed scorer's own output file (fixes round 8's empty lines,
whose grep patterns did not match the scorers' output).

    python -I round9/sealed_lines9.py fresh  <fresh_test.txt>     score_fresh7.py stdout: the `all all` line of the
                                                                   side-by-side block (strict/lenient x model/attributed)
    python -I round9/sealed_lines9.py shep   <shep/headline.tsv>   compare.py headline table: agreement, recall NEG
                                                                   strict/lenient, PART, precision, CLEAN, MOD, subclasses
    python -I round9/sealed_lines9.py half   <scorer stdout> h1    every stdout line with the token h1 (the round-8 keys'
                                                                   scorers print one per half: fjc, shadow, scdb, state)
    python -I round9/sealed_lines9.py lines  <scorer stdout>       a scorer of unknown format: every line with a token
                                                                   h0 / h1 / all, else the last 6 non-empty lines
    python -I round9/sealed_lines9.py json   <result.json> ...     every metric with integer k and n (any depth) of
                                                                   each scorer result json (e.g. <label>.h0/h1/all.json)

Prints one line (whitespace collapsed). When nothing is found it prints `EXTRACTION FAILED: <why>` and exits 1, so a
log line is never silently empty. Reads only the named file.
"""
import re
import sys


def squash(s):
    return " ".join(s.split())


def fresh(path):
    txt = open(path, encoding="utf-8").read()
    i = txt.find("side by side (k/n, rate [Wilson 95%])")
    if i < 0:
        return None, "no side-by-side block"
    block = txt[i:].splitlines()
    m_n = re.search(r"pairs=(\d+)", txt)
    for line in block:
        p = line.split()
        if len(p) >= 3 and p[0] == "all" and p[1] == "all":
            n = p[2]
            cells = re.findall(r"(\d+) (\d\.\d+) \[(\d\.\d+),(\d\.\d+)\]", line)
            if len(cells) != 4:
                return None, "the all/all line has %d cells, not 4" % len(cells)
            names = ("strict model", "strict attributed", "lenient model", "lenient attributed")
            out = ["%s %s/%s = %s [%s, %s]" % (nm, k, n, r, lo, hi) for nm, (k, r, lo, hi) in zip(names, cells)]
            if m_n and m_n.group(1) != n:
                out.append("(pairs header %s)" % m_n.group(1))
            return "; ".join(out), None
    return None, "no all/all line in the side-by-side block"


SHEP_ROWS = (
    ("agreement", "overall", "agreement"),
    ("(a) recall", "NEG: model NEG_HIST (strict)", "NEG strict"),
    ("(a) recall", "NEG: model NEG_HIST or UNK_HIST (lenient)", "NEG lenient"),
    ("(a) recall", "PART: model NEG_HIST or UNK_HIST", "PART"),
    ("(b) precision", "of model NEG_HIST: Shepardized NEG (strict", "precision strict"),
    ("(b) precision", "of model NEG_HIST: Shepardized NEG or PART", "precision lenient"),
    ("(c) clean", "CLEAN:", "CLEAN"),
    ("(c) clean", "MOD:", "MOD"),
)


def shep(path):
    rows = [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8")]
    out = []
    for g, v, name in SHEP_ROWS:
        hit = [p for p in rows if len(p) >= 10 and p[0] == g and p[1].startswith(v)]
        if len(hit) != 1:
            return None, "headline row %r / %r found %d times" % (g, v, len(hit))
        p = hit[0]
        out.append("%s %s = %s [%s, %s] (set aside %s)" % (name, p[2], p[3], p[4], p[5], p[6]))
    for p in rows:
        if len(p) >= 7 and p[0] == "recall by subclass":
            out.append("%s %s (set aside %s)" % (p[1], p[2], p[6]))
    return "; ".join(out), None


def half(path, h):
    hits = [squash(l) for l in open(path, encoding="utf-8") if h in l.split()]
    if not hits:
        return None, "no line with the token %s" % h
    return " | ".join(hits), None


def lines(path):
    all_ = [l for l in open(path, encoding="utf-8") if l.strip()]
    hits = [squash(l) for l in all_ if {"h0", "h1", "all"} & set(l.split())]
    if not hits:
        hits = [squash(l) for l in all_[-6:]]
    if not hits:
        return None, "empty output"
    return " | ".join(hits), None


def kn_pairs(o, path=""):
    """Every dict with integer k and n at any depth (a scorer's metrics), as (path, k, n)."""
    out = []
    if isinstance(o, dict):
        if isinstance(o.get("k"), int) and isinstance(o.get("n"), int):
            return [(path, o["k"], o["n"])]
        for key, v in o.items():
            out += kn_pairs(v, "%s.%s" % (path, key) if path else str(key))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out += kn_pairs(v, "%s[%d]" % (path, i))
    return out


def jsons(paths):
    import json
    import os
    parts = []
    for p in paths:
        if not os.path.exists(p):
            parts.append("%s: missing" % os.path.basename(p))
            continue
        kn = kn_pairs(json.load(open(p, encoding="utf-8")))
        kn = [(re.sub(r"^metrics\.", "", q), k, n) for q, k, n in kn]
        parts.append("%s: %s" % (os.path.basename(p), " ".join("%s %d/%d" % x for x in kn) or "no k/n metrics"))
    if not any(": missing" not in x for x in parts):
        return None, "no result json"
    return " | ".join(parts), None


def main():
    a = sys.argv[1:]
    try:
        if len(a) >= 2 and a[0] == "json":
            r, why = jsons(a[1:])
        elif len(a) == 2 and a[0] == "fresh":
            r, why = fresh(a[1])
        elif len(a) == 2 and a[0] == "shep":
            r, why = shep(a[1])
        elif len(a) == 3 and a[0] == "half":
            r, why = half(a[1], a[2])
        elif len(a) == 2 and a[0] == "lines":
            r, why = lines(a[1])
        else:
            sys.exit(__doc__)
    except OSError as e:
        r, why = None, "cannot read %s (%s)" % (a[1], e.strerror)
    if r is None:
        print("EXTRACTION FAILED: %s (%s)" % (why, a[1]))
        sys.exit(1)
    print(r)


if __name__ == "__main__":
    main()
