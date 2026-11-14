"""diag cross-check: sentences of Y (parts that are not head matter / dissent / concurrence by the part map) that
hold a phrase of the provisional `operative` cue list AND name X (a party token or a citation of X).

    python cuecheck.py [-a]        -a: every part (part labels of slip opinions are unreliable)

Prints the sentences; used to re-check the readers' A = 0 calls.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dsearch as D  # noqa: E402
import ctx  # noqa: E402
import merge  # noqa: E402

RC = D.RC
CUES = json.load(open(os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues/cue_table.json"),
                      encoding="utf-8"))


def find_list(o, name):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == name and isinstance(v, list):
                return v
            r = find_list(v, name)
            if r:
                return r
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    allparts = "-a" in sys.argv
    op = find_list(CUES, "operative")
    rx = re.compile("|".join(re.escape(c) for c in op), re.I)
    meta = D.load_meta()
    with open(os.path.join(HERE, "pairs.tsv"), encoding="utf-8", newline="") as f:
        pairs = list(csv.DictReader(f, delimiter="\t"))
    n = 0
    for pr in pairs:
        idx, y, x = int(pr["idx"]), pr["by_node"], pr["target_node"]
        xname = pr["target_name"]
        if x == "-1":
            if idx not in merge.EXTRA_X:
                continue
            x, xname = merge.EXTRA_X[idx]
        toks = set(RC.name_tokens(xname)) | (set(RC.name_tokens(meta[x][6])) if x in meta else set())
        toks = sorted(toks, key=len, reverse=True)
        pats = (D.cite_patterns(meta[x][5]) if x in meta else []) + [r"\b%s\b" % re.escape(t) for t in toks]
        if not pats:
            continue
        xr = re.compile("|".join(pats))
        text = open(os.path.join(HERE, "text", y + ".md"), encoding="utf-8", newline="").read()
        pm, body0 = RC.part_map2(text)
        view = RC.unwrap_view(text, body0) if RC.hard_wrapped(text, body0) else text
        for s, e, p, sec in pm:
            if p in ("front", "title"):
                continue
            if not allparts and p.lower().startswith(("dissent", "concur", "head")):
                continue
            off = s
            for line in view[s:e].split("\n"):
                la, lb = off, off + len(line)
                off = lb + 1
                if not rx.search(line) or not xr.search(line):
                    continue
                for a, b in ctx.sentences(view, la, lb):
                    t = view[a:b]
                    m = rx.search(t)
                    if m and xr.search(t):
                        n += 1
                        c = m.start()
                        print("%d %s/%s @%d [%s] %s" % (idx, y, x, a, p, t[max(0, c - 260):c + 200].replace("\n", " ")))
    print("sentences", n)


if __name__ == "__main__":
    main()
