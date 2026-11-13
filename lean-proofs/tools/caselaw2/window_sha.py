"""SHA-1 of every certificate window, recut from the audit copy (the corpus), for the Lean checker.

    python -X utf8 window_sha.py [--procs 6] [--out W/data/window_sha.tsv]

Keys: every distinct (text_sha, start0, end0) in cert_text.tsv and holdings_cert_text.tsv, read from both
caselaw-lean-2/difftest/snap4/ and caselaw-lean-2/data/ (union). For each key the decision file is read from git HEAD
(`git cat-file --batch`, one process per repo chunk), located through decisions2.tsv (text_sha -> node) and
graph/nodes.tsv (node -> repo, path). The file bytes must hash to text_sha; the text is then UTF-8 decoded, CRLF -> LF,
and tab/newline/CR each replaced by one space (one for one), and the window is text[start0:end0].

Output (no header, LF, sorted by text_sha then start0 then end0):
    text_sha, start0, end0, window_sha1 (sha1 hex of the window's UTF-8 bytes), src (= corpus)
A key whose text is not found, or whose bytes do not hash to text_sha, gets no row (counted).

Also reported, per input file: how many stored windows equal their corpus cut, and how many differ.
"""
import argparse, collections, hashlib, json, os, subprocess, sys, threading
from multiprocessing import Pool

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
C2 = os.path.join(WORK, "caselaw-lean-2")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
NODES = os.path.join(WORK, "graph", "nodes.tsv")
NOWIN = 0x08000000
INPUTS = [(d, f) for d in ("difftest/snap4", "data") for f in ("cert_text.tsv", "holdings_cert_text.tsv")]


def rows(path):
    """(text_sha, start0, end0, window) per line; binary read so a lone CR inside a field never splits a line."""
    with open(path, "rb") as f:
        for line in f:
            p = line.rstrip(b"\n").decode("utf-8").split("\t", 3)
            if len(p) < 4:
                yield None
                continue
            yield p[0], int(p[1]), int(p[2]), p[3]


def norm(raw):
    t = raw.decode("utf-8", "replace").replace("\r\n", "\n")
    return t.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def worker(job):
    repo, items = job  # items: [(sha, path, [(s0, e0, {label: stored_digest})])]
    out, st = [], collections.Counter()
    p = subprocess.Popen(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=NOWIN if sys.platform == "win32" else 0)

    def feed():
        for _, path, _ in items:
            p.stdin.write(("HEAD:" + path + "\n").encode("utf-8"))
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    for sha, path, spans in items:
        hdr = p.stdout.readline().split()
        if len(hdr) < 3 or hdr[1] == b"missing":
            st["key_text_missing"] += len(spans)
            continue
        raw = p.stdout.read(int(hdr[2]))
        p.stdout.read(1)
        if hashlib.sha1(raw).hexdigest() != sha:
            st["key_sha_differs"] += len(spans)
            continue
        text = norm(raw)
        for s0, e0, stored in spans:
            if not (0 <= s0 <= e0 <= len(text)):
                st["key_out_of_range"] += 1
                continue
            d = hashlib.sha1(text[s0:e0].encode("utf-8")).hexdigest()
            out.append((sha, s0, e0, d))
            st["key_ok"] += 1
            for label, sd in stored.items():
                st[f"{label}:{'same' if sd == d else 'differs'}"] += 1
    p.wait()
    return out, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--out", default=os.path.join(C2, "data", "window_sha.tsv"))
    a = ap.parse_args()
    st = collections.Counter()
    keys = {}  # (sha, s0, e0) -> {label: digest of the stored window}
    for d, f in INPUTS:
        label = f"{d}/{f}"
        for r in rows(os.path.join(C2, d, f)):
            if r is None:
                st[f"{label}:malformed_line"] += 1
                continue
            sha, s0, e0, w = r
            st[f"{label}:rows"] += 1
            if len(w) != e0 - s0:
                st[f"{label}:len_neq_span"] += 1
            keys.setdefault((sha, s0, e0), {})[label] = hashlib.sha1(w.encode("utf-8")).hexdigest()
    st["keys"] = len(keys)
    shas = {k[0] for k in keys}
    st["texts"] = len(shas)
    # text_sha -> node (decisions2.tsv, both copies), node -> (repo, path)
    node_of = {}
    for d in ("difftest/snap4", "data"):
        with open(os.path.join(C2, d, "decisions2.tsv"), "rb") as f:
            for line in f:
                p = line.split(b"\t", 9)
                if len(p) > 7:
                    s = p[7].decode()
                    if s in shas and s not in node_of:
                        node_of[s] = int(p[0])
    want = set(node_of.values())
    loc = {}
    with open(NODES, encoding="utf-8", newline="\n") as f:
        for line in f:
            i = line.find("\t")
            n = int(line[:i])
            if n in want:
                p = line.split("\t", 3)
                loc[n] = (p[1], p[2])
    spans = collections.defaultdict(list)
    for (sha, s0, e0), stored in keys.items():
        spans[sha].append((s0, e0, stored))
    by_repo = collections.defaultdict(list)
    for sha, sp in spans.items():
        n = node_of.get(sha)
        if n is None or n not in loc:
            st["key_no_node"] += len(sp)
            continue
        repo, path = loc[n]
        by_repo[repo].append((sha, path, sp))
    jobs = []
    for repo, items in by_repo.items():
        items.sort(key=lambda x: x[1])
        for i in range(0, len(items), 3000):
            jobs.append((repo, items[i:i + 3000]))
    jobs.sort(key=lambda j: -len(j[1]))
    out = []
    with Pool(a.procs) as pool:
        for o, s in pool.imap_unordered(worker, jobs):
            out.extend(o)
            st.update(s)
    out.sort(key=lambda r: (r[0], r[1], r[2]))
    tmp = a.out + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fo:
        for sha, s0, e0, d in out:
            fo.write(f"{sha}\t{s0}\t{e0}\t{d}\tcorpus\n")
    os.replace(tmp, a.out)
    st["out_rows"] = len(out)
    print(json.dumps(dict(sorted(st.items())), indent=1))


if __name__ == "__main__":
    main()
