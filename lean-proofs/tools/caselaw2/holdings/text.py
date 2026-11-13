"""Decision texts streamed from git (no files on disk), with the SCHEMA normalisation.

    norm_text(raw bytes) -> str: UTF-8 decoded, \r\n -> \n (offsets in SCHEMA CERT columns index this string)
    text_sha(raw bytes) -> sha1 hex of the file bytes at HEAD
    map_nodes(nids, fn, procs=8): run fn(nid, raw_bytes) in worker processes, one `git cat-file --batch` per repo,
        yielding fn's results (None results are dropped). At most `procs` git processes run at once.
"""
import hashlib, os, subprocess, sys, threading
from multiprocessing import Pool

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
NODES = os.path.join(WORK, "graph", "nodes.tsv")
NOWIN = 0x08000000


def norm_text(raw):
    return raw.decode("utf-8", "replace").replace("\r\n", "\n")


def text_sha(raw):
    return hashlib.sha1(raw).hexdigest()


def quote_of(text, s, e):
    return text[s:e].replace("\t", " ").replace("\n", " ")


def node_paths(nids):
    want = set(int(n) for n in nids)
    out = {}
    with open(NODES, encoding="utf-8") as f:
        for line in f:
            i = line.find("\t")
            n = int(line[:i])
            if n in want:
                p = line.split("\t", 3)
                out[n] = (p[1], p[2])
    return out


def _repo_worker(args):
    repo, items, fn, chunk = args
    res = []
    p = subprocess.Popen(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=NOWIN if sys.platform == "win32" else 0)

    def feed():
        for _, path in items:
            p.stdin.write(("HEAD:" + path + "\n").encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    for nid, path in items:
        hdr = p.stdout.readline().split()
        if len(hdr) < 3 or hdr[1] == b"missing":
            continue
        raw = p.stdout.read(int(hdr[2]))
        p.stdout.read(1)
        try:
            r = fn(nid, raw)
        except Exception as e:  # keep going; report
            r = ("__error__", nid, repr(e)[:200])
        if r is not None:
            res.append(r)
    p.wait()
    return res


def map_nodes(nids, fn, procs=8, chunk=4000, paths=None):
    paths = paths or node_paths(nids)
    by = {}
    for n in nids:
        if n in paths:
            repo, path = paths[n]
            by.setdefault(repo, []).append((n, path))
    jobs = []
    for repo, items in by.items():
        items.sort(key=lambda x: x[1])
        for i in range(0, len(items), chunk):
            jobs.append((repo, items[i:i + chunk], fn, chunk))
    jobs.sort(key=lambda j: -len(j[1]))
    with Pool(procs) as pool:
        for res in pool.imap_unordered(_repo_worker, jobs):
            for r in res:
                yield r


def fetch(nids):
    """{nid: raw bytes} for a small set (single process)."""
    paths = node_paths(nids)
    out = {}
    by = {}
    for n, (repo, path) in paths.items():
        by.setdefault(repo, []).append((n, path))
    for repo, items in by.items():
        for nid, raw in _repo_worker((repo, items, lambda n, r: (n, r), 0)):
            out[nid] = raw
    return out
