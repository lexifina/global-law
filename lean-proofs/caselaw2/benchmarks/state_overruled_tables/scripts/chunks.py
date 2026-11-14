"""Cut a table's OCR lines (pages.py output) into reader chunks.

    python -I chunks.py <lines.tsv> <outdir> full <lines_per_chunk> [leaf_from leaf_to]
    python -I chunks.py <lines.tsv> <outdir> window <lines_per_chunk> <before> <after> [leaf_from leaf_to]

Each chunk line: "[leaf N] text". window mode keeps only lines within <before>/<after> lines of a treatment word
(overrul, denied, doubted, questioned, limited, disapprov, receded, abrogat, criticis), merged; gaps marked "....".
"""
import os
import re
import sys

KW = re.compile(r"(?i)o[vt]err?u[l1]|verrul|denied|doubted|question|limited|disapprov|receded|abrogat|critici")


def main():
    src, outdir, mode, per = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    rest = sys.argv[5:]
    before = after = 0
    if mode == "window":
        before, after = int(rest[0]), int(rest[1])
        rest = rest[2:]
    lo, hi = (int(rest[0]), int(rest[1])) if rest else (0, 10 ** 9)
    lines = []
    with open(src, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            leaf = int(p[0])
            if lo <= leaf <= hi and "Digitized by" not in p[6]:
                lines.append((leaf, p[6]))
    if mode == "window":
        keep = set()
        for i, (_, t) in enumerate(lines):
            if KW.search(t):
                keep.update(range(max(0, i - before), min(len(lines), i + after + 1)))
        out, last = [], None
        for i in sorted(keep):
            if last is not None and i != last + 1:
                out.append(None)
            out.append(lines[i])
            last = i
    else:
        out = lines
    os.makedirs(outdir, exist_ok=True)
    k = 0
    for s in range(0, len(out), per):
        part = out[s:s + per]
        with open(os.path.join(outdir, "chunk_%02d.txt" % k), "w", encoding="utf-8", newline="\n") as o:
            for x in part:
                o.write("....\n" if x is None else "[leaf %d] %s\n" % x)
        k += 1
    print(src, mode, "lines", len(out), "chunks", k)


if __name__ == "__main__":
    main()
