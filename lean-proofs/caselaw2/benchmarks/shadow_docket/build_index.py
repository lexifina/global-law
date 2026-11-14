#!/usr/bin/env python3
"""Docket index of the corpus: every decision dated 1985-01-01 or later whose front matter gives a docket number.

Reads (read only): round6/history/cache/*.meta.tsv.gz (columns: node, sha, len, date, court2, docket, type, title,
parties, citations, flags; the docket is the front-matter `docket:` field) and data/courts2.tsv.
Writes: work/docket_index.tsv.gz  (key, node, date, court2, system, tier, circuit, repo, raw docket, title, citations)
        one row per (decision, docket key); work/docket_coverage.tsv (repo, decisions >= 1985, with docket).
No model output, no Shadow Docket row is read here.
"""
import collections
import gzip
import multiprocessing as mp
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sdlib  # noqa: E402

CACHE = os.path.join(sdlib.ROOT, "round6", "history", "cache")
MIN_DATE = 19850101


def shard_repo(fn):
    b = fn[:-len(".meta.tsv.gz")]
    parts = b.rsplit(".", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return b


def work(fn):
    repo = shard_repo(fn)
    rows = []
    tot = withd = 0
    with gzip.open(os.path.join(CACHE, fn), "rt", encoding="utf-8", newline="\n") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 11:
                continue
            try:
                d = int(p[3])
            except ValueError:
                continue
            if d < MIN_DATE:
                continue
            tot += 1
            if not p[5].strip():
                continue
            withd += 1
            keys = sdlib.docket_keys(p[5])
            for k in keys:
                rows.append((k, p[0], p[3], p[4], repo, p[5], p[7], p[9]))
    return repo, tot, withd, rows


def main():
    courts = sdlib.load_courts()
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    files = sorted(f for f in os.listdir(CACHE) if f.endswith(".meta.tsv.gz"))
    cov = collections.Counter()
    covd = collections.Counter()
    out = gzip.open(os.path.join(HERE, "work", "docket_index.tsv.gz"), "wt", encoding="utf-8", newline="\n")
    n = 0
    with mp.Pool(16) as pool:
        for repo, tot, withd, rows in pool.imap_unordered(work, files):
            cov[repo] += tot
            covd[repo] += withd
            for k, node, date, c2, rp, raw, title, cites in rows:
                sysid, tier, circ = courts.get(int(c2) if c2.lstrip("-").isdigit() else -1, (-1, "?", 0))
                out.write("\t".join([k, node, date, c2, str(sysid), tier, str(circ), rp, sdlib.clean(raw),
                                     sdlib.clean(title), sdlib.clean(cites)]) + "\n")
                n += 1
    out.close()
    with open(os.path.join(HERE, "work", "docket_coverage.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("repo\tdecisions_since_1985\twith_docket\n")
        for r in sorted(cov):
            o.write("%s\t%d\t%d\n" % (r, cov[r], covd[r]))
    print("index rows", n, "decisions", sum(cov.values()), "with docket", sum(covd.values()))


if __name__ == "__main__":
    main()
