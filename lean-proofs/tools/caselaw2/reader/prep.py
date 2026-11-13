"""Prepare lookup tables for the caselaw-lean-2 reader (run once).

    python -X utf8 prep.py

Writes under caselaw-lean-2/data/reader_work/:
  nodes/<repo>.tsv   path, node id, date, court id   (one file per repo, for the scanners)
  cites_indptr.npy, cites_idx.npy   CSR of graph/edges.bin by citing node (cited cases of each decision)
  node_date.npy, node_court.npy     per-node date (yyyymmdd) and v1 court id
"""
import array, collections, os

import numpy as np

W = os.path.expanduser("~/Documents/us-caselaw-lean-work")
OUT = os.path.join(W, "caselaw-lean-2", "data", "reader_work")


def main():
    os.makedirs(os.path.join(OUT, "nodes"), exist_ok=True)
    by_repo = collections.defaultdict(list)
    n = 0
    dates = array.array("i")
    courts = array.array("i")
    for line in open(os.path.join(W, "graph", "nodes.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        nid = int(f[0])
        assert nid == n
        n += 1
        by_repo[f[1]].append(f"{f[2]}\t{nid}\t{f[4]}\t{f[3]}\n")
        dates.append(int(f[4] or 0))
        courts.append(int(f[3]))
    for r, rows in by_repo.items():
        with open(os.path.join(OUT, "nodes", r + ".tsv"), "w", encoding="utf-8", newline="\n") as fo:
            fo.writelines(rows)
    np.save(os.path.join(OUT, "node_date.npy"), np.frombuffer(dates, dtype=np.int32))
    np.save(os.path.join(OUT, "node_court.npy"), np.frombuffer(courts, dtype=np.int32))
    e = np.fromfile(os.path.join(W, "graph", "edges.bin"), dtype=np.uint32).reshape(-1, 2)
    order = np.argsort(e[:, 0], kind="stable")
    src = e[order, 0]
    dst = e[order, 1].copy()
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.add.at(indptr, src.astype(np.int64) + 1, 1)
    indptr = np.cumsum(indptr)
    np.save(os.path.join(OUT, "cites_indptr.npy"), indptr)
    np.save(os.path.join(OUT, "cites_idx.npy"), dst)
    print(n, "nodes,", len(by_repo), "repos,", len(dst), "edges")


if __name__ == "__main__":
    main()
