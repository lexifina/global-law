"""calpart9 (copy of round-8 calpart scan_parts.py; PJ on part_map2 AND on r6scan's map, moved chars old->new): corpus-wide count of rule PJ (partfix.py) over every decision (git HEAD texts of every repo).

    python -X utf8 scan_parts.py [--procs 10] [--repos a,b] [--force]

Per shard writes work/scan/<tag>.jsonl (one line per decision the rule relabels, or that the old short-head cut
test of state8 hits without PJ ("cut_only"), or that has a header-only dissent note ("dissent_note"; not relabelled))
and work/scan/<tag>.stats.json. Same part map as r6scan (part_map2 for hard-wrapped texts, else part_map).
No answer-key file is read.
"""
import argparse, json, os, re, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, HERE)
import r6lib as L  # noqa: E402
import partfix as PF  # noqa: E402
import partzone as PZ  # noqa: E402

C = L.reader_common()
NL = chr(10)
OUTD = os.path.join(HERE, "work", "scan")
DISSENT = re.compile(r"\bdissent(?:s|ed|ing)?\b", re.I)


def moved_chars(pm, new):
    """{"old->new": chars} of the zone parts that change between two part maps."""
    import collections
    a = PZ.to_zones(pm, 10 ** 12)
    b = PZ.to_zones(new, 10 ** 12)
    pts = sorted(set([x for z in a for x in z[:2]] + [x for z in b for x in z[:2]]))
    out = collections.Counter()
    for i in range(len(pts) - 1):
        s0, s1 = pts[i], pts[i + 1]
        pa = PZ.zone_at(a, s0, s1)[2]
        pb = PZ.zone_at(b, s0, s1)[2]
        if pa != pb:
            out[pa + "->" + pb] += s1 - s0
    return dict(out)


def scan_text(text):
    """PJ on both part maps the readers use: pm2 (treatments reader: part_map2 for every text) and r6 (round-6
    history scan: part_map2 when hard-wrapped, else part_map)."""
    b0 = PZ.body_start(text)
    hw = C.hard_wrapped(text, b0)
    pm2, _ = C.part_map2(text)
    pm1 = pm2 if hw else C.part_map(text)[0]
    rec = None
    for tag, pm in (("pm2", pm2), ("r6", pm1)):
        new, ch = PF.fix_parts(text, pm)
        if ch:
            rec = rec or {"kind": "PJ", "hw": int(hw)}
            rec[tag] = {"changes": [list(c) for c in ch], "moved": moved_chars(pm, new)}
            a, m0 = ch[0][0], ch[0][1]
            rec["head"] = text[a:m0][:400].replace(NL, " / ")
            rec["after"] = text[m0:m0 + 300].replace(NL, " / ")
    if rec:
        return rec
    pm = pm2
    # old cut test (state8 partcount / rescue PF): majority segment < 400 chars followed by a separate-opinion part
    for i, (a, b, p, s) in enumerate(pm):
        if p in PF.BASE_PARTS and i + 1 < len(pm) and pm[i + 1][2] in PF.SEP_PARTS and b - a < 400:
            ml = PF.mark_line(text, pm[i + 1][0])
            kind = "cut_only"
            if PF.header_block(text, a, pm[i + 1][0]) and PF.header_line(ml) and DISSENT.search(ml)                     and not PF.CONCUR.search(ml):
                kind = "dissent_note"
            return {"kind": kind, "hw": int(hw), "mark": ml.strip()[:200], "part": pm[i + 1][2],
                    "head": text[a:pm[i + 1][0]][:400].replace(NL, " / "),
                    "after": text[pm[i + 1][0]:pm[i + 1][0] + 300].replace(NL, " / ")}
    return None


def run(task):
    repo, k, K = task
    tag = repo if K == 1 else "%s.%02d" % (repo, k)
    sp = os.path.join(OUTD, tag + ".stats.json")
    if os.path.exists(sp) and not G.get("force"):
        return tag, {"skipped": 1}
    t0 = time.time()
    nodes = {}
    for line in open(os.path.join(C.WORK, "nodes", repo + ".tsv"), encoding="utf-8"):
        p, nid, date, court = line.rstrip(NL).split("\t")
        nodes[p] = (int(nid), date, court)
    rd = os.path.join(L.REPOS, repo)
    tree = subprocess.run(["git", "-C", rd, "ls-tree", "-r", "HEAD", "--", "decisions"], capture_output=True,
                          check=True, creationflags=L.NOWIN).stdout.decode("utf-8")
    items = []
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        _, typ, bsha = meta.split()
        if typ == "blob" and path.endswith(".md") and path in nodes:
            items.append((bsha, path))
    items = items[k * len(items) // K:(k + 1) * len(items) // K]
    p = subprocess.Popen(["git", "-C", rd, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         creationflags=L.NOWIN)

    def feed():
        for bsha, _ in items:
            p.stdin.write((bsha + NL).encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    st = {"files": 0, "concur_text": 0, "PJ": 0, "cut_only": 0, "dissent_note": 0, "err": 0}
    with open(os.path.join(OUTD, tag + ".jsonl.part"), "w", encoding="utf-8", newline=NL) as fo:
        for bsha, path in items:
            header = p.stdout.readline().split()
            size = int(header[2])
            data = p.stdout.read(size)
            p.stdout.read(1)
            st["files"] += 1
            low = data.lower()
            if b"concurr" not in low and b"dissent" not in low:
                continue
            st["concur_text"] += 1
            nid, date, court = nodes[path]
            text = data.decode("utf-8", "replace").replace("\r\n", NL)
            try:
                rec = scan_text(text)
            except Exception as ex:  # keep going; count
                st["err"] += 1
                if st["err"] <= 3:
                    sys.stderr.write("%s %s: %r\n" % (repo, path, ex))
                continue
            if rec:
                st[rec["kind"]] += 1
                rec.update({"n": nid, "repo": repo, "date": date, "court": court})
                fo.write(json.dumps(rec, ensure_ascii=False) + NL)
    p.wait()
    os.replace(os.path.join(OUTD, tag + ".jsonl.part"), os.path.join(OUTD, tag + ".jsonl"))
    st["sec"] = round(time.time() - t0, 1)
    with open(sp, "w", encoding="utf-8", newline=NL) as f:
        json.dump(st, f)
    return tag, st


G = {}


def init(force):
    G["force"] = force


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUTD, exist_ok=True)
    all_repos = sorted(f[:-4] for f in os.listdir(os.path.join(C.WORK, "nodes")) if f.endswith(".tsv"))
    repos = a.repos.split(",") if a.repos else all_repos

    def size(r):
        return os.path.getsize(os.path.join(C.WORK, "nodes", r + ".tsv"))
    tasks = []
    for r in sorted(repos, key=size, reverse=True):
        nlines = sum(1 for _ in open(os.path.join(C.WORK, "nodes", r + ".tsv"), encoding="utf-8"))
        K = max(1, -(-nlines // 30000))
        tasks += [(r, k, K) for k in range(K)]
    print("repos:", len(repos), "tasks:", len(tasks), flush=True)
    import multiprocessing as mp
    tot = {}
    with mp.Pool(a.procs, initializer=init, initargs=(a.force,)) as pool:
        for tag, st in pool.imap_unordered(run, tasks, chunksize=1):
            for k2, v in st.items():
                tot[k2] = tot.get(k2, 0) + v
            print(tag, json.dumps(st), flush=True)
    print("TOTAL", json.dumps(tot), flush=True)


if __name__ == "__main__":
    main()
