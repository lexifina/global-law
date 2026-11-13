"""Print the header region of given decisions (node ids), read from git objects; nothing written to disk.

    python show.py <chars> <node> [<node> ...]      (or node ids on stdin when none are given)
"""
import os, subprocess, sys
from collections import defaultdict

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")


def fetch(want):
    """{node: (repo, path, court idx, date)} -> {node: text}"""
    by = defaultdict(list)
    for n, (repo, path, _, _) in want.items():
        by[repo].append((n, path))
    out = {}
    for repo, items in by.items():
        inp = "".join("HEAD:%s\n" % p for _, p in items).encode()
        res = subprocess.run(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], input=inp,
                             capture_output=True).stdout
        i = 0
        for n, _ in items:
            nl = res.index(b"\n", i)
            hdr = res[i:nl].split()
            i = nl + 1
            if hdr[1] == b"missing":
                continue
            size = int(hdr[2])
            out[n] = res[i:i + size].decode("utf-8", "replace")
            i += size + 1
    return out


def lookup(ids):
    ids = set(ids)
    want = {}
    with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 5)
            if p[0] in ids:
                want[p[0]] = (p[1], p[2], p[3], p[4])
                if len(want) == len(ids):
                    break
    return want


def main():
    chars = int(sys.argv[1])
    ids = sys.argv[2:] or [l.strip() for l in sys.stdin if l.strip()]
    want = lookup(ids)
    texts = fetch(want)
    for n in ids:
        if n not in texts:
            print("=" * 20, n, "MISSING")
            continue
        t = texts[n]
        repo, path, _, date = want[n]
        print("=" * 20, n, repo, date, path)
        if t.startswith("---"):
            end = t.find("\n---", 3)
            keep = [l for l in t[3:end].splitlines() if l.split(":")[0] in
                    ("court", "docket", "judges", "precedential_status", "decision_type", "citations")]
            t = "\n".join(keep) + "\n--" + t[end + 4:]
        print(t[:chars])
        if len(t) > chars:
            print("... [tail]", t[-300:].replace("\n", " / "))


if __name__ == "__main__":
    main()
