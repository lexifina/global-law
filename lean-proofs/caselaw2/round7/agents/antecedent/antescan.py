"""Round 7, agent `antecedent`: one corpus pass for overrulings stated with an anaphor (DESIGN7 2.2, class (i)).

    python -X utf8 antescan.py [--repos r1,r2,...] [--procs 22] [--force]

Streams every decision of ~/Documents/us-caselaw-repos/<repo> from git (cat-file --batch on the HEAD tree, as
round6/history/r6scan.py) and writes scan/<repo>[.kk].jsonl.gz, one record per candidate ACT SENTENCE:

  a sentence of an opinion-of-the-court part (majority, majority~, perCuriam, plurality) that holds a status-changing
  cue (ACT: overrul / disapprov / abrogat / recede / repudiat / disavow / overturn / "no longer ... law|authority|..")
  AND an anaphor phrase (ANAPHOR: "those cases", "that case", "these decisions", "they are overruled", ...), and no
  phrase of the cue table's disqualify_treat list and no procedural object (objection, motion, demurrer, ...).

Record: {n, s:[s0,s1], act:text, part, flags, w:[w0, raw view text up to s1], pstart, cites:[[key,c0,c1],...],
         ocites:[[key, prefix],...]}     (ocites: every citation of the opinion-of-the-court parts with the 90
         characters before it, for the case names of decisions the opinion cites elsewhere; first 300 keys)
Offsets are characters of the git-HEAD text (UTF-8, CRLF -> LF); the view of a hard-wrapped text has the same length
(reader/common.unwrap_view), so view offsets are text offsets. Citation keys are the reader's (graph/cite_index.tsv
keys); they are resolved later (antecands.py), not here. No answer key of any kind is read.
"""
import argparse, gzip, json, os, re, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/reader")
sys.path.insert(0, TOOLS)
import common as C  # noqa: E402
import cue_table as CT  # noqa: E402

REPOS = C.REPOS
OUT = os.path.join(HERE, "scan")
NL = chr(10)
OPC = ("majority", "majority~", "perCuriam", "plurality")

PRE = re.compile(r"overrul|disapprov|abrogat|recede|receding|repudiat|disavow|overturn|no longer")
ACT = re.compile(r"\b(?:overrul\w*|disapprov\w*|abrogat\w*|reced(?:e|es|ed|ing)\b|repudiat\w*|disavow\w*|overturn\w*|"
                 r"no\s+longer\s+(?:\w+\s+){0,4}?(?:law|authorit\w*|follow\w*|valid\w*|control\w*|viable|precedent\w*|"
                 r"binding|approve\w*|adhere\w*))", re.I)
_DET = r"(?:those|these|such|said|both|all\s+(?:such|of\s+the(?:se|m)?|three|four|the\s+(?:above|foregoing|cited))|" \
       r"the\s+(?:above(?:[\s-]+(?:cited|mentioned|named))?|foregoing|said|former|latter|cited|aforesaid|preceding|" \
       r"two|three|four|last[\s-]+(?:named|cited|mentioned)|earlier|prior|other)|that|each\s+of\s+(?:these|those|the))"
_NOUN = r"(?:cases?|decisions?|opinions?|holdings?|authorities|authority|precedents?|rulings?|judgments?|line\s+of\s+" \
        r"(?:cases|decisions|authority)|expressions?|statements?|dicta|dictum|language)"
ANAPHOR = re.compile(
    r"\b" + _DET + r"\s+(?:(?:\w+[\s-]+){0,2})?" + _NOUN + r"\b|"
    r"\bthe\s+(?:cases|decisions|authorities|opinions)\s+(?:above\s+|just\s+|last\s+|hereinbefore\s+|heretofore\s+|"
    r"previously\s+|so\s+)?(?:cited|mentioned|referred\s+to|named|listed|discussed|relied\s+(?:up)?on|noted)\b|"
    r"\b(?:each|all|both|either|any|none)\s+of\s+them\b|"
    r"\b(?:they|it|them)\b\s+(?:\w+\s+){0,3}?(?:overrul|disapprov|abrogat|reced|repudiat|disavow|overturn)|"
    r"\b(?:overrul\w+|disapprov\w+|abrogat\w+|repudiat\w+|disavow\w+|overturn\w*)\s+(?:\w+\s+){0,2}?(?:them|it)\b|"
    r"\b(?:to\s+the\s+extent|insofar\s+as|in\s+so\s+far\s+as|so\s+far\s+as)\s+(?:that\s+)?(?:they|it)\b|"
    r"\b(?:they|it)\s+(?:is|are|were|was|must\s+be|should\s+be|will\s+be|stand|stands)\s+(?:hereby\s+|now\s+|"
    r"therefore\s+|accordingly\s+|expressly\s+|to\s+that\s+extent\s+|pro\s+tanto\s+)*(?:overrul|disapprov|abrogat|"
    r"repudiat|disavow|overturn)", re.I)
PROC = re.compile(r"\b(?:objections?|motions?|demurrers?|exceptions?|pleas?|assignments?|specifications?|"
                  r"points?\s+of\s+error|issues?\s+(?:is|are)\s+overruled|contentions?)\b", re.I)
REPORT = re.compile(r"\b(?:has|have|had|was|were|been|being|since|subsequently|later|previously|already|impliedly|"
                    r"effectively|implicitly)\s+(?:\w+\s+){0,2}?(?:overrul|disapprov|abrogat|reced|repudiat|overturn)",
                    re.I)
NEG = re.compile(r"\b(?:not|n't|never|nor|unnecessary|need\s+not|without|decline|refuse|whether|if)\b", re.I)
DQ = tuple(CT.DISQUALIFY_TREAT)
HEAD_LINE = re.compile(r"^#+ ", re.M)

G = {}
FORCE = [False]


def norm(s):
    return s.replace(chr(9), " ").replace(NL, " ").replace(chr(13), " ")


def init(force=False):
    FORCE[0] = force


def scan_text(nid, text):
    low = text.lower()
    if not PRE.search(low):
        return []
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    hw = C.hard_wrapped(text, body0)
    view = C.unwrap_view(text, body0) if hw else text
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    segs = [(a, b, p) for a, b, p, s_ in pm if p in OPC]
    if not segs:
        return []
    out = []
    last = -1
    ocites = None
    for a, b, p in segs:
        for m in ACT.finditer(view, a, b):
            s0, s1 = C.sentence_span(view, m.start(), m.end())
            if s0 <= last or s0 < a:
                continue
            last = s0
            s1 = min(s1, b)
            sent = view[s0:s1]
            sl = sent.lower()
            if not ANAPHOR.search(sent):
                continue
            if any(d in sl for d in DQ) or PROC.search(sent):
                continue
            flags = []
            if REPORT.search(sent):
                flags.append("report")
            if NEG.search(sent):
                flags.append("neg")
            # preceding region: same part segment, not across a heading line, at most 2000 characters back
            w0 = max(a, s0 - 2000)
            hh = [h.start() for h in HEAD_LINE.finditer(view, w0, s0)]
            if hh:
                w0 = view.find(NL, hh[-1]) + 1 or s0
            wtext = view[w0:s1]
            cites = []
            for cm in C.CITE_RX.finditer(view, w0, s1):
                k = C.cite_key(cm)
                if k:
                    cites.append([k, cm.start(), cm.end()])
            if ocites is None:
                ocites, seen = [], set()
                for a2, b2, p2 in segs:
                    for cm in C.CITE_RX.finditer(view, a2, b2):
                        k = C.cite_key(cm)
                        if k and k not in seen and len(ocites) < 300:
                            seen.add(k)
                            ocites.append([k, norm(view[max(a2, cm.start() - 90):cm.start()])])
            out.append({"n": nid, "s": [s0, s1], "act": norm(sent), "part": p, "flags": flags, "hw": int(hw),
                        "w": [w0, wtext], "pstart": a, "cites": cites, "ocites": ocites})
    return out


def run_repo(task):
    repo, k, K = task
    t0 = time.time()
    tag = repo if K == 1 else "%s.%02d" % (repo, k)
    out_j = os.path.join(OUT, tag + ".jsonl.gz")
    if os.path.exists(os.path.join(OUT, tag + ".stats.json")) and not FORCE[0]:
        return tag, {"skipped": 1}
    nodes = {}
    for line in open(os.path.join(C.WORK, "nodes", repo + ".tsv"), encoding="utf-8"):
        p, nid, _date, _court = line.rstrip(NL).split("\t")
        nodes[p] = int(nid)
    rd = os.path.join(REPOS, repo)
    tree = subprocess.run(["git", "-C", rd, "ls-tree", "-r", "HEAD", "--", "decisions"], capture_output=True,
                          check=True, creationflags=0x08000000).stdout.decode("utf-8")
    items = []
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        _, typ, bsha = meta.split()
        if typ == "blob" and path.endswith(".md") and path in nodes:
            items.append((bsha, path))
    items = items[k * len(items) // K:(k + 1) * len(items) // K]
    p = subprocess.Popen(["git", "-C", rd, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         creationflags=0x08000000)

    def feed():
        for bsha, _ in items:
            p.stdin.write((bsha + NL).encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    st = {"files": 0, "cand": 0, "dec": 0, "err": 0}
    with gzip.open(out_j + ".part", "wt", encoding="utf-8", newline=NL, compresslevel=4) as fj:
        for bsha, path in items:
            header = p.stdout.readline().split()
            size = int(header[2])
            data = p.stdout.read(size)
            p.stdout.read(1)
            st["files"] += 1
            nid = nodes[path]
            text = data.decode("utf-8", "replace").replace("\r\n", NL)
            try:
                recs = scan_text(nid, text)
            except Exception as ex:
                st["err"] += 1
                if st["err"] <= 3:
                    sys.stderr.write("%s %s: %r\n" % (repo, path, ex))
                continue
            if recs:
                st["dec"] += 1
            for r in recs:
                st["cand"] += 1
                fj.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + NL)
    p.wait()
    os.replace(out_j + ".part", out_j)
    st["sec"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT, tag + ".stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(st, f)
    return tag, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos")
    ap.add_argument("--procs", type=int, default=22)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    all_repos = sorted(f[:-4] for f in os.listdir(os.path.join(C.WORK, "nodes")) if f.endswith(".tsv"))
    repos = a.repos.split(",") if a.repos else all_repos
    FORCE[0] = a.force

    def size(r):
        return os.path.getsize(os.path.join(C.WORK, "nodes", r + ".tsv"))
    order = sorted(repos, key=size, reverse=True)
    tasks = []
    for r in order:
        nlines = sum(1 for _ in open(os.path.join(C.WORK, "nodes", r + ".tsv"), encoding="utf-8"))
        K = max(1, -(-nlines // 30000))
        tasks += [(r, k, K) for k in range(K)]
    tasks.sort(key=lambda t: 0)
    print("repos:", len(order), "tasks:", len(tasks), flush=True)
    if a.procs <= 1 or len(tasks) == 1:
        for t in tasks:
            print(run_repo(t), flush=True)
        return
    import multiprocessing as mp
    with mp.Pool(a.procs, initializer=init, initargs=(a.force,)) as pool:
        for tag, st in pool.imap_unordered(run_repo, tasks, chunksize=1):
            print(tag, json.dumps(st), flush=True)


if __name__ == "__main__":
    main()
