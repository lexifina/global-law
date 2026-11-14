"""Round 9, agent `state9`, part A: one corpus pass for IMPLICIT rejections of an earlier decision's holding
(class IMP9: the acting court's own words reject / depart from X's rule without a status verb).

    python -X utf8 impscan.py [--repos r1,r2,...] [--procs 8] [--force]

Copy of round7/agents/antecedent/antescan.py (same streaming, same record format, so antecands-style resolution
can be reused); only the sentence test differs. A candidate is a sentence of an opinion-of-the-court part
(majority, majority~, perCuriam, plurality) that holds one IMP cue (IMP below: "we disagree with", "we are not
persuaded by", "decline / refuse to follow", "no longer good law / sound / viable / controlling", "was wrongly /
incorrectly decided", "<holding|reasoning|rule ...> ... is unsound / erroneous / incorrect / mistaken",
"has been undermined / eroded / discredited / called into question", "contrary to the holding / decision in",
"we depart from"), and NO explicit status verb (overrul / disapprov / abrogat / recede: those sentences belong to
the explicit readers), no phrase of the cue table's disqualify_treat list, no procedural object.

Record: {n, s:[s0,s1], act:text, part, flags, tag, w:[w0, raw view text up to s1], pstart, cites, ocites}
(as antescan; `tag` = the IMP cue family that matched first). No answer key of any kind is read.
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

PRE = re.compile(r"disagree|agree with|persuaded|convinced|declin|refus|unwilling|inclined|no longer|wrongly|"
                 r"incorrectly|erroneously|unsound|erroneous|incorrect|mistaken|undermin|erode|discredit|"
                 r"called into|cast doubt|contrary to|depart")
_HOLD = r"(?:holding|reasoning|rationale|rule|conclusion|analysis|view|statement|language|dictum|dicta|decision|" \
        r"opinion|interpretation|construction|approach|test|pronouncement)s?"
IMP = [
    ("disagree", re.compile(r"\b(?:we|this\s+court|the\s+court|i)\s+(?:\w+\s+){0,3}?(?:disagree|cannot\s+agree|"
                            r"do\s+not\s+agree|are\s+(?:not\s+able|unable)\s+to\s+agree)\b", re.I)),
    ("notpersuaded", re.compile(r"\b(?:we|this\s+court)\s+(?:are|is|remain)\s+(?:\w+\s+)?(?:not|un)\s*(?:persuaded|"
                                r"convinced)\s+(?:by|that)\b", re.I)),
    ("decline", re.compile(r"\b(?:declin(?:e|es|ed|ing)|refus(?:e|es|ed|ing)|unwilling|not\s+inclined)\s+to\s+"
                           r"(?:follow|adopt|apply|extend|adhere\s+to)\b|\bwe\s+(?:do\s+not|will\s+not|cannot|"
                           r"shall\s+not|no\s+longer)\s+(?:follow|adhere\s+to)\b", re.I)),
    ("nolonger", re.compile(r"\bno\s+longer\s+(?:\w+\s+){0,3}?(?:good\s+law|valid|sound|viable|tenable|the\s+law|"
                            r"controlling|authoritative|binding|of\s+(?:any\s+)?(?:force|authority|precedential)|"
                            r"precedent\w*|authority|followed|persuasive|correct|accurate|represents?)\b", re.I)),
    ("wrongly", re.compile(r"\b(?:wrongly|incorrectly|erroneously|improperly)\s+decided\b", re.I)),
    ("unsound", re.compile(r"\b" + _HOLD + r"\b[^.;]{0,120}?\b(?:is|was|are|were)\s+(?:\w+\s+){0,2}?(?:unsound|"
                           r"erroneous|incorrect|mistaken|wrong|ill[\s-]considered|flawed|misguided|untenable|"
                           r"indefensible)\b", re.I)),
    ("undermined", re.compile(r"\b(?:has|have|had)\s+(?:\w+\s+){0,2}?been\s+(?:\w+\s+){0,2}?(?:undermined|eroded|"
                              r"discredited|weakened|vitiated|called\s+into\s+(?:question|doubt))\b|"
                              r"\b(?:undermines?|erodes?|discredits?)\s+(?:the\s+)?(?:\w+\s+){0,2}?" + _HOLD + r"\b",
                              re.I)),
    ("contrary", re.compile(r"\bcontrary\s+to\s+(?:the\s+|our\s+|its\s+)?(?:holding|decision|rule|reasoning|result|"
                            r"view|conclusion)s?\s+(?:of|in|reached\s+in|announced\s+in)\b|\b(?:different|contrary|"
                            r"opposite)\s+(?:result|conclusion)\s+(?:than|from|to)\b", re.I)),
    ("depart", re.compile(r"\b(?:we|this\s+court)\s+(?:\w+\s+){0,2}?depart(?:s|ed|ing)?\s+from\b", re.I)),
]
ANCH = {
    "disagree": (("disagree", "agree with"), 60, 40),
    "notpersuaded": (("persuaded", "convinced"), 60, 30),
    "decline": (("declin", "refus", "unwilling", "inclined", "not follow", "not adhere", "longer follow",
                 "longer adhere"), 30, 50),
    "nolonger": (("no longer",), 5, 80),
    "wrongly": (("wrongly decided", "incorrectly decided", "erroneously decided", "improperly decided"), 5, 30),
    "unsound": (("unsound", "erroneous", "incorrect", "mistaken", "ill-considered", "ill considered", "flawed",
                 "misguided", "untenable", "indefensible"), 220, 30),
    "undermined": (("undermin", "eroded", "erode", "discredit", "weakened", "vitiated", "called into"), 80, 60),
    "contrary": (("contrary to", "different result", "contrary result", "opposite result", "different conclusion",
                  "contrary conclusion", "opposite conclusion"), 5, 60),
    "depart": (("depart",), 40, 30),
}
REF = re.compile(r"\b\d{1,4}\s+[A-Z][A-Za-z.\s]{1,30}\d{1,5}\b|\sv\.\s|\bvs?\.\s+[A-Z]|\bIn\s+re\s|\bEx\s+parte\s")
NEGW = re.compile(r"\bclearly\s+erroneous|\bnot\s+(?:\w+\s+)?(?:unsound|erroneous|incorrect|mistaken|wrong|flawed|"
                  r"untenable)\b|\bn't\s+(?:\w+\s+)?(?:unsound|erroneous|incorrect|mistaken|wrong)\b", re.I)
EXPLICIT = re.compile(r"overrul|disapprov|abrogat|\breced", re.I)
PROC = re.compile(r"\b(?:objections?|motions?|demurrers?|exceptions?|pleas?|assignments?|specifications?|"
                  r"points?\s+of\s+error|contentions?)\b", re.I)
REPORT = re.compile(r"\b(?:has|have|had|was|were)\s+(?:\w+\s+){0,2}?(?:criticized|questioned|rejected|disagreed|"
                    r"declined|undermined|eroded|discredited)\s+(?:\w+\s+){0,2}?by\b", re.I)
SEP = re.compile(r"\b(?:dissent\w*|concurr\w*|majority\s+(?:opinion|holds|today))\b", re.I)
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
    # anchored matching (literal anchors first, the family regex only around them), then a cheap in-sentence
    # reference test (a citation, "v.", "In re", "Ex parte") before the part map is computed
    vlow = view.lower() if hw else low
    raw = []
    done = set()
    for tag, rx in IMP:
        anchors, back, fwd = ANCH[tag]
        for kw in anchors:
            i = vlow.find(kw, body0)
            while i >= 0:
                for m in rx.finditer(view, max(body0, i - back), min(len(view), i + fwd)):
                    if (m.start(), tag) in done:
                        continue
                    done.add((m.start(), tag))
                    s0, s1 = C.sentence_span(view, m.start(), m.end())
                    sent = view[s0:s1]
                    if REF.search(sent) and not NEGW.search(sent):
                        raw.append((tag, m.start(), m.end()))
                i = vlow.find(kw, i + 1)
    if not raw:
        return []
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    segs = [(a, b, p) for a, b, p, s_ in pm if p in OPC]
    if not segs:
        return []
    hits = []
    for tag, m0, m1 in raw:
        for a, b, p in segs:
            if a <= m0 < b:
                hits.append((m0, m1, tag, a, b, p))
                break
    hits.sort()
    out = []
    last = -1
    ocites = None
    for m0, m1, tag, a, b, p in hits:
        s0, s1 = C.sentence_span(view, m0, m1)
        if s0 <= last or s0 < a:
            continue
        last = s0
        s1 = min(s1, b)
        sent = view[s0:s1]
        sl = sent.lower()
        if EXPLICIT.search(sent):
            continue
        if any(d in sl for d in DQ) or PROC.search(sent):
            continue
        flags = []
        if REPORT.search(sent):
            flags.append("report")
        if SEP.search(sent):
            flags.append("sep")
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
        out.append({"n": nid, "s": [s0, s1], "act": norm(sent), "part": p, "flags": flags, "tag": tag,
                    "hw": int(hw), "w": [w0, wtext], "pstart": a, "cites": cites, "ocites": ocites})
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
    ap.add_argument("--procs", type=int, default=8)
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
