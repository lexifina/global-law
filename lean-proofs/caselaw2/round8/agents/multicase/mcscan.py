"""Round 8, agent `multicase`: one corpus pass for act sentences that name two or more cases.

    python -X utf8 mcscan.py [--repos r1,r2,...] [--procs 10] [--force]

Streams every decision of ~/Documents/us-caselaw-repos/<repo> from git (as round7/agents/antecedent/antescan.py)
and writes scan/<repo>[.kk].jsonl.gz, one record per candidate ACT SENTENCE:

  a sentence of an opinion-of-the-court part (majority, majority~, perCuriam, plurality) that holds a strong
  status-changing verb (overrul / disapprov / abrogat / recede / repudiat / disavow / overturn), no phrase of the cue
  table's disqualify_treat list, no procedural object (objection, motion, demurrer, point of error, ...), and
  EITHER >= 2 case references in the sentence itself (citations "148 Ga. 376" and captions "A v. B", "In re A",
  "Ex parte A", "the A case", "A's Case"; a citation printed right after a caption or another citation joined by a
  comma counts with it)
  OR >= 1 reference in the sentence and >= 1 in the sentence just before it, with a plural back-reference in the act
  sentence ("those cases", "these decisions", "both", "they", "each of them", ...).

Record: {n, s:[s0,s1], act, p:[p0,p1] (previous sentence), part, flags, hw, nref, nref_prev,
         cites:[[key,c0,c1],...] (in [p0, s1)), names:[[text,c0,c1],...] (in [p0, s1)), ocites:[[key, prefix],...]}
Offsets are characters of the git-HEAD text (UTF-8, CRLF -> LF); the unwrapped view has the same length.
No answer key of any kind is read.
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

PRE = re.compile(r"overrul|disapprov|abrogat|recede|receding|repudiat|disavow|overturn")
ACT = re.compile(r"\b(?:overrul\w*|disapprov\w*|abrogat\w*|reced(?:e|es|ed|ing)\b|repudiat\w*|disavow\w*|overturn\w*)",
                 re.I)
_W = r"[A-Z][\w'.&\-]*"
_LINK = r"(?:[ ,]+(?:" + _W + r"|of|the|and|&|de|du|la|le|von|van|ex\s+rel\.?|et\s+al\.?|for|in|on|to|by))"
NAME = re.compile(
    r"\b(?:In\s+re|Ex\s+parte|Matter\s+of|In\s+the\s+Matter\s+of|Petition\s+of|Estate\s+of)\s+" + _W +
    r"|" + _W + _LINK + r"{0,7},?\s+(?:vs?\.?|versus)\s+" + _W +
    r"|\b(?:the\s+)?(?!(?:The|This|That|Said|Such|Each|Both|Our|Present|Instant|Former|Latter|Last|Same|First|"
    r"Second|Third|Principal|Above|Prior|Earlier|Later|Other|These|Those|Its|Their|His|Her|Any|Every|No|In|Of)\b)"
    r"[A-Z][a-z]{2,}(?:'s)?\s+[Cc]ases?\b")
DQ = tuple(CT.DISQUALIFY_TREAT)
PROC = re.compile(r"\b(?:objections?|motions?|demurrers?|exceptions?|pleas?|assignments?|specifications?|"
                  r"points?\s+of\s+error|issues?\s+(?:is|are)\s+overruled|contentions?|grounds?\s+of\s+error)\b", re.I)
REPORT = re.compile(r"\b(?:has|have|had|was|were|been|being|since|subsequently|later|previously|already|impliedly|"
                    r"effectively|implicitly|virtually|practically|in\s+effect)\s+(?:\w+\s+){0,2}?"
                    r"(?:overrul|disapprov|abrogat|reced|repudiat|overturn)", re.I)
NEG = re.compile(r"\b(?:not|n't|never|nor|unnecessary|need\s+not|without|decline|refuse|whether|if)\b", re.I)
PLURAL = re.compile(r"\b(?:those|these|such|said|both|all|the\s+(?:above|foregoing|cited|two|three|four|several))\s+"
                    r"(?:\w+\s+){0,2}?(?:cases|decisions|opinions|holdings|authorities|precedents|rulings|judgments)\b|"
                    r"\b(?:each|all|both)\s+of\s+(?:them|these|those)\b|\bboth\b|\bthey\b|\bthem\b|\btheir\b", re.I)
HEAD_LINE = re.compile(r"^#+ ", re.M)
LIMIT = re.compile(r"\b(?:to\s+the\s+extent|in\s*so\s+far|insofar|so\s+far\s+as|in\s+part|on\s+this\s+point|"
                   r"on\s+other\s+grounds|as\s+to\s+the|to\s+that\s+extent|in\s+this\s+respect|in\s+that\s+respect|"
                   r"so\s+far\s+as|pro\s+tanto|to\s+the\s+degree|in\s+the\s+particular)", re.I)
_SEP_SAME = re.compile(r"^[\s,()\-\d]{0,30}$")

FORCE = [False]


def norm(s):
    return s.replace(chr(9), " ").replace(NL, " ").replace(chr(13), " ")


def init(force=False):
    FORCE[0] = force


def refs(view, a, b):
    """(cites, names, number of distinct references) in view[a:b]."""
    cites = []
    for cm in C.CITE_RX.finditer(view, a, b):
        k = C.cite_key(cm)
        if k:
            cites.append([k, cm.start(), cm.end()])
    names = [[norm(m.group(0)), m.start(), m.end()] for m in NAME.finditer(view, a, b)]
    ev = sorted([(c[1], c[2], "c") for c in cites] + [(x[1], x[2], "n") for x in names])
    n = 0
    prev_end = None
    for s, e, t in ev:
        if prev_end is not None and s >= prev_end:
            gap = view[prev_end:s]
            if t == "c" and len(gap) <= 30 and ";" not in gap and _SEP_SAME.match(gap):
                prev_end = e
                continue
        if prev_end is not None and s < prev_end:  # overlapping matches
            prev_end = max(prev_end, e)
            continue
        n += 1
        prev_end = e
    return cites, names, n


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
            s0, s1 = C.sentence_span(view, m.start(), m.end(), back=1500, fwd=1000)
            if s0 <= last or s0 < a:
                continue
            last = s0
            s1 = min(s1, b)
            sent = view[s0:s1]
            sl = sent.lower()
            if any(d in sl for d in DQ) or PROC.search(sent):
                continue
            cs, ns, nr = refs(view, s0, s1)
            # previous sentence (same part, no heading between)
            p0, p1 = s0, s0
            if s0 > a:
                q = s0 - 1
                while q > a and view[q] in " \n":
                    q -= 1
                if q > a:
                    p0, p1 = C.sentence_span(view, q, q, back=1500, fwd=1)
                    p0 = max(p0, a)
                    p1 = min(p1, s0)
                    if HEAD_LINE.search(view, p0, p1) or p1 <= p0:
                        p0, p1 = s0, s0
            pr = refs(view, p0, p1) if p1 > p0 else ([], [], 0)
            ok = nr >= 2 or (nr >= 1 and pr[2] >= 1 and PLURAL.search(sent))
            if not ok:
                continue
            flags = []
            if REPORT.search(sent):
                flags.append("report")
            if NEG.search(sent):
                flags.append("neg")
            if LIMIT.search(sent):
                flags.append("limit")
            if ocites is None:
                ocites, seen = [], set()
                for a2, b2, p2 in segs:
                    for cm in C.CITE_RX.finditer(view, a2, b2):
                        k = C.cite_key(cm)
                        if k and k not in seen and len(ocites) < 400:
                            seen.add(k)
                            ocites.append([k, norm(view[max(a2, cm.start() - 90):cm.start()])])
            out.append({"n": nid, "s": [s0, s1], "act": norm(sent), "p": [p0, p1], "prev": norm(view[p0:p1]),
                        "part": p, "flags": flags, "hw": int(hw), "nref": nr, "nref_prev": pr[2],
                        "cites": pr[0] + cs, "names": pr[1] + ns, "ocites": ocites})
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
    ap.add_argument("--procs", type=int, default=10)
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
