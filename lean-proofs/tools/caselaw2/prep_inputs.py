"""Split graph/nodes.tsv into one (node, path) input file per repo for scan.py.

    python prep_inputs.py <work-dir>/caselaw-lean-2/work/courts
"""
import os, sys

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")


def main(wd):
    os.makedirs(os.path.join(wd, "in"), exist_ok=True)
    fs = {}
    with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            fo = fs.get(p[1])
            if fo is None:
                fo = fs[p[1]] = open(os.path.join(wd, "in", p[1] + ".tsv"), "w", encoding="utf-8", newline="\n")
            fo.write(p[0] + "\t" + p[2] + "\n")
    for fo in fs.values():
        fo.close()
    print("repos", len(fs))


if __name__ == "__main__":
    main(sys.argv[1])
