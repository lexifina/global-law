"""Print the header region of random decisions (read from git objects; nothing written to disk).

    python peek.py <repo> <n> [court-substring] [chars] [seed]
"""
import os, random, subprocess, sys

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")


def courts():
    c = {}
    for line in open(os.path.join(WORK, "graph/courts.tsv"), encoding="utf-8"):
        f = line.split("\t")
        c[f[0]] = f[1]
    return c


def main():
    repo, n = sys.argv[1], int(sys.argv[2])
    sub = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
    chars = int(sys.argv[4]) if len(sys.argv) > 4 else 2500
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    cn = courts()
    pool = []
    with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 5)
            if p[1] == repo and (sub is None or sub in cn[p[3]]):
                pool.append((p[0], p[2], cn[p[3]], p[4]))
    random.seed(seed)
    pick = random.sample(pool, min(n, len(pool)))
    inp = "".join("HEAD:%s\n" % r[1] for r in pick).encode()
    res = subprocess.run(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], input=inp,
                         capture_output=True).stdout
    i = 0
    for r in pick:
        nl = res.index(b"\n", i)
        hdr = res[i:nl].split()
        i = nl + 1
        if hdr[1] == b"missing":
            continue
        size = int(hdr[2])
        data = res[i:i + size].decode("utf-8", "replace")
        i += size + 1
        print("=" * 30, r[0], r[2], r[3], r[1])
        if data.startswith("---"):
            end = data.find(chr(10) + "---", 3)
            fm = data[3:end]
            keep = [l for l in fm.splitlines() if l.split(":")[0] in ("court", "docket", "judges", "precedential_status", "decision_type")]
            data = chr(10).join(keep) + chr(10) + "--" + chr(10) + data[end + 4:]
        print(data[:chars])


main()
