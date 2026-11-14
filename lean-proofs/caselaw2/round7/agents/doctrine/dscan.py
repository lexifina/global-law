"""Round 7, agent doctrine: one corpus pass for doctrine ties and doctrine rejections (court text only).

    python -X utf8 dscan.py [--repos r1,r2] [--procs 22] [--force] [--limit N]

Streams every decision of ~/Documents/us-caselaw-repos/<repo> from git HEAD (cat-file --batch, as r6scan.py) and
writes scan/<tag>.jsonl.gz with, for decisions that have a hit in an opinion-of-the-court part
(majority / plurality / perCuriam, incl. the inferred `~` forms):
  {"t":"tie", n, form, label, lc, noun, case, ckey, verb, s:[s0,s1], q, part}
        a tie sentence: a doctrine label D tied by its own words to ONE case reference
        forms: ofq  (the NOUN of "D" [verb] in|of CASE),  ofu (the NOUN of d e f [verb] in CASE),
               pre  (the D NOUN [verb] in|of CASE),        pos (CASE's D NOUN)
        ckey: citation key (reader common.cite_key) of the first citation right after the case name, or null
  {"t":"rej", n, cue, labels:[[label, lc, form, noun, a, b]], s:[s0,s1], q, part}
        a sentence with a rejection cue and at least one doctrine label (a, b: label span in the text)
  {"t":"nm", n, pairs:[[case name, cite key], ...]}
        "Name v. Name, <cite>" pairs of the decision (for short-name resolution offline)
Offsets are characters of the git-HEAD text (UTF-8, CRLF -> LF); q is text[s0:s1] with tab/newline -> space.
No answer key is read. Resolution of citation keys to nodes is done offline (build_registry.py).
"""
import argparse, gzip, json, os, re, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/reader")
sys.path.insert(0, TOOLS)
import common as C  # noqa: E402

REPOS = C.REPOS
OUT = os.path.join(HERE, "scan")
NL = chr(10)
NOWIN = 0x08000000 if os.name == "nt" else 0
COURT_PARTS = {"majority": "majority", "majority~": "majority", "perCuriam": "perCuriam", "plurality": "plurality"}

NOUN = r"(?:doctrine|rule|test|principle|formula|standard|presumption|exception)"
NOUN_RX = re.compile(r"\b" + NOUN + r"\b", re.I)
AFTER_NOUN = re.compile(r"[a-z]*\s+(?:of\s|announced|established|adopted|laid|first|enunciated|formulated|set\s+forth|"
                        r"articulated|in\s|as\s|which|that\s+was|originated|created|fashioned|introduced|pronounced|"
                        r"expounded|propounded|stated|,)")
REJ_STEMS = ("place", "no longer", "reject", "repudiat", "abandon", "discard", "disapprov", "overrul", "abolish",
             "renounc", "disavow", "jettison", "recede", "depart", "retreat", "to follow", "unsound", "erroneous",
             "outmoded", "anachronis", "discredit", "law", "cannot", "wrongly", "overthrown", "swept", "to rest",
             "dead", "viab", "vitality")
LOWNOUN = re.compile(r"doctrine|rule|test|principle|formula|standard|presumption|exception")
QO, QC = "“\"‘'", "”\"’'"
# ---- label forms ------------------------------------------------------------------------------------------------
OFQ = re.compile(r"\b(?P<noun>" + NOUN + r")\s+of\s+(?P<q>[“\"‘'])\s*(?P<lab>[^”\"’'\n“‘]{3,80}?)\s*[”\"’']", re.I)
WORD = r"[a-z][a-z'’\-]*"
OFU = re.compile(r"\b(?P<noun>(?i:" + NOUN + r"))\s+of\s+(?P<lab>" + WORD + r"(?:\s+" + WORD + r"){0,5})")
PRE = re.compile(r"\b(?:the|a|its|this|that|his|her|their|our)\s+(?:so[\s-]called\s+)?(?P<lab>(?:[“\"‘'][^”\"’'\n“‘]{3,80}?[”\"’']|"
                 r"[A-Za-z][A-Za-z'’\-]*)(?:\s+(?:[“\"‘'][^”\"’'\n“‘]{3,60}?[”\"’']|[A-Za-z][A-Za-z'’\-]*)){0,5}?)\s+"
                 r"(?P<noun>" + NOUN + r")\b", re.I)
POS = re.compile(r"\b(?P<case>[A-Z][A-Za-z\-]{2,})['’]s\s+(?P<lab>(?:[“\"‘'][^”\"’'\n“‘]{3,80}?[”\"’']|[a-z][a-z'’\-]*)"
                 r"(?:\s+(?:[“\"‘'][^”\"’'\n“‘]{3,60}?[”\"’']|[a-z][a-z'’\-]*)){0,5}?)\s+(?P<noun>" + NOUN + r")\b")
# words that end an unquoted label (OFU) or may not be a label word at all
STOP_IN = set("""in as announced established adopted laid first which that is was has had have be been being to
by under with for on at from upon this these those such it its their his her our we they he she was were are not no any
all every each than then when where while if so also there here may might must should would could can will shall
expressed enunciated formulated articulated stated recognized applied followed set originally initially later
subsequently previously declared pronounced created developed fashioned introduced embodied approved""".split())
# first words that make a PRE label generic (determiner-like adjectives)
PRE_STOP_FIRST = set("""same general above following foregoing said such new old majority minority settled well common usual
ordinary prevailing present former latter applicable proper correct traditional familiar basic fundamental firmly long
last first second third federal state other another different particular specific narrow broad strict strictest
appropriate controlling governing relevant pertinent established accepted recognized proposed suggested modern
universal uniform only one two three this that these those any every each all its their his her our your my which
whose what so very more most less least better best rule doctrine test principle formula standard presumption
exception old-fashioned well-settled well-established long-standing longstanding time-honored court's courts court
district appellate trial supreme lower higher legal judicial statutory constitutional equitable""".split())
LABEL_STOP_ANY = set("""the a an of in is was are were be been this that these those our we it its his her their
court court's""".split())

CASE = (r"(?P<case>(?:In\s+re|Ex\s+parte|Matter\s+of)\s+[A-Z][\w'’.&\-]*(?:\s+[A-Z][\w'’.&\-]*){0,4}"
        r"|[A-Z][\w'’.&\-]*(?:\s+(?:[A-Z][\w'’.&\-]*|of|the|and|&|ex\s+rel\.?)){0,6}\s+v\.?\s+[A-Z][\w'’.&\-]*"
        r"(?:\s+(?:[A-Z][\w'’.&\-]*|of|the|and|&)){0,6}"
        r"|[A-Z][\w'’\-]{2,}(?=\s*(?:,|\(|\s+supra|\s+and\s|\s*\d|\.\s)))")
VERB = (r"(?:announced|established|adopted|laid\s+down|stated|enunciated|formulated|originated|articulated|"
        r"set\s+(?:forth|out)|created|fashioned|introduced|pronounced|expounded|propounded|first\s+[a-z]+)")
ATTACH = re.compile(r"\s*[”\"’']?\s*,?\s*(?:(?:as|which\s+was|that\s+was|first|originally|initially)\s+)?"
                    r"(?:(?P<verb>" + VERB + r")\s+(?:by\s+(?:this|the|our)\s+(?:[A-Za-z.]+\s+){0,3}?)?)?"
                    r"(?P<prep>in|of)\s+(?:the\s+case\s+of\s+)?" + CASE)
# ---- rejection cues (broad; the certified list is the lean agent's `doctrine_reject`) ------------------------------
REJ = re.compile(
    r"\b(?:has|have|had)\s+no\s+(?:further\s+|proper\s+|legitimate\s+|longer\s+(?:any\s+)?)?place\b|\bno\s+longer\b|"
    r"\b(?:reject|rejects|rejected|repudiat\w*|abandon\w*|discard\w*|disapprov\w*|overrul\w*|abolish\w*|renounc\w*|"
    r"disavow\w*|jettison\w*|recede[sd]?\s+from|depart\w*\s+from|retreat\w*\s+from|decline\s+to\s+follow|"
    r"declines\s+to\s+follow|refuse\s+to\s+follow|unsound|erroneous|outmoded|anachronis\w*|discredit\w*|"
    r"not\s+(?:the|good)\s+law|cannot\s+(?:survive|stand|be\s+reconciled)|wrongly\s+decided|overthrown|"
    r"swept\s+away|laid\s+to\s+rest|is\s+dead|now\s+dead|"
    r"no\s+(?:longer\s+)?(?:viab\w*|vitality))\b", re.I)
PRE_RX = re.compile(NOUN + r"s?\s+of\s|['’]s\s+[^.\n]{1,60}?" + NOUN + r"|" + NOUN + r"\s+(?:announced|established|"
                    r"adopted|laid|first|enunciated|formulated|set\s+forth|articulated)", re.I)
NM_RX = re.compile(r"((?:In\s+re|Ex\s+parte)\s+[A-Z][\w'’.&\-]*(?:\s+[A-Z][\w'’.&\-]*){0,3}|[A-Z][\w'’.&\-]*"
                   r"(?:\s+(?:[A-Z][\w'’.&\-]*|of|the|and|&)){0,6}\s+v\.?\s+[A-Z][\w'’.&\-]*(?:\s+(?:[A-Z][\w'’.&\-]*|"
                   r"of|the|and|&)){0,6}),?\s*$")


def norm(s):
    return s.replace("\t", " ").replace(NL, " ").replace("\r", " ")


def compact(s):
    return re.sub(r"[^0-9a-z]", "", s.lower())


def words_of(s):
    return [w for w in re.split(r"[\s\-]+", re.sub(r"[“”\"‘’']", " ", s.lower())) if w]


TOK = re.compile(r"[“\"‘'][^”\"’'\n“‘]{3,80}?[”\"’']|[A-Za-z][A-Za-z'’\-]*")
CUT = STOP_IN | LABEL_STOP_ANY | set("""so-called so called an on about whether over against between into through
because since after before during without within among toward towards per via""".split())
QCH = "“”\"‘’'"


def label_key(core, noun):
    """Registry key of a label: the compact core (letters and digits, lower case); a one-word core keeps its noun
    ("laches|doctrine"), so that the key always stands for at least two words."""
    ws = words_of(core)
    k = compact(core)
    return k if len(ws) >= 2 else k + "|" + noun


def core_ok(core, form, noun):
    ws = words_of(core)
    if not ws:
        return False
    if len(ws) < 2 and len(compact(core)) < 3:
        return False
    full = ws if len(ws) >= 2 else ws + [noun]
    if len("".join(full)) < 8:
        return False
    if re.search(r"\bv\.?\s", core) or re.search(r"\d", core):
        return False  # a case name or a citation: not a doctrine label (operative class)
    if ws[0] in LABEL_STOP_ANY:
        return False
    if form == "pre" and ws[0] in PRE_STOP_FIRST:
        return False
    return True


def labels_in(s, base=0):
    """[(core, key, form, noun, a, b)] of the doctrine labels in sentence s. core: the label without its noun and
    without quote marks; [a, b) the span of the whole label phrase (noun included), offset by base."""
    out = []
    for m in OFQ.finditer(s):
        core = m.group("lab").strip()
        if core_ok(core, "ofq", m.group("noun").lower()):
            out.append((core, label_key(core, m.group("noun").lower()), "ofq", m.group("noun").lower(),
                        base + m.start(), base + m.end()))
    for m in OFU.finditer(s):
        ws = m.group("lab").split()
        keep = []
        for w in ws:
            if w.lower() in STOP_IN:
                break
            keep.append(w)
        while keep and keep[-1].lower() in ("of", "the", "a", "an", "and", "or", "but"):
            keep.pop()
        if not keep or keep[0].lower() in ("the", "a", "an", "this", "that", "such", "these", "those", "its", "law"):
            continue
        core = " ".join(keep)
        noun = m.group("noun").lower()
        if core_ok(core, "ofu", noun):
            e = m.start("lab") + len(" ".join(ws[:len(keep)]))
            out.append((core, label_key(core, noun), "ofu", noun, base + m.start(), base + e))
    for m in PRE.finditer(s):
        la = m.start("lab")
        lab = m.group("lab")
        toks = list(TOK.finditer(lab))
        cut = -1
        for i, t in enumerate(toks):
            if t.group(0).lower().strip(QCH) in CUT:
                cut = i
        if cut >= 0:
            if cut + 1 >= len(toks):
                continue
            la = m.start("lab") + toks[cut + 1].start()
            lab = s[la:m.end("lab")]
        core = lab.strip().strip(QCH).strip()
        noun = m.group("noun").lower()
        if not core_ok(core, "pre", noun):
            continue
        form = "epon" if re.match(r"[A-Z]", core) else "pre"
        if form == "pre" and re.search(r"[A-Z]", core):
            continue  # a capital inside a lower-case label: a name; leave it out
        out.append((core, label_key(core, noun), form, noun, base + la, base + m.end()))
    for m in POS.finditer(s):
        core = m.group("lab").strip().strip(QCH).strip()
        noun = m.group("noun").lower()
        toks = [t.group(0).lower().strip(QCH) for t in TOK.finditer(core)]
        if any(t in CUT for t in toks) or len(words_of(core)) > 5:
            continue  # "General's argument for an across-the-board rule": not a label
        if core_ok(core, "pos", noun):
            out.append((core, label_key(core, noun), "pos", noun, base + m.start("lab"), base + m.end()))
    return out


def first_cite(s, a, lim=90):
    m = C.CITE_RX.search(s, a, min(len(s), a + lim))
    if m:
        return C.cite_key(m)
    return None


def ties_in(view, s0, s1):
    """Tie records of the sentence view[s0:s1]."""
    s = view[s0:s1]
    out = []
    seen = set()
    for core, lk, form, noun, a, b in labels_in(s):
        if form == "pos":
            mm = None
            for m2 in POS.finditer(s):
                if m2.start("lab") <= a <= m2.start("lab") + 2:
                    mm = m2
                    break
            if mm is None:
                continue
            case, verb, prep = mm.group("case"), "possessive", "pos"
            ckey = None
        else:
            m = ATTACH.match(s, b)
            if not m:
                continue
            case, verb, prep = m.group("case"), (m.group("verb") or ""), m.group("prep")
            if prep == "of" and verb == "" and form in ("ofq", "ofu"):
                continue  # "the rule of d of X": not a tie form
            ckey = first_cite(s, m.end("case"))
        key = (lk, case)
        if key in seen:
            continue
        seen.add(key)
        out.append({"t": "tie", "form": form, "core": core, "lk": lk, "noun": noun, "case": case, "ckey": ckey,
                    "verb": re.sub(r"\s+", " ", verb.lower()), "prep": prep, "la": [s0 + a, s0 + b]})
    return out


def scan_text(nid, text):
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    low = text.lower()
    tie_pos, rej_pos = [], []
    last_t = last_r = -1
    for h in LOWNOUN.finditer(low, body0):
        p = h.start()
        if p > last_t and (AFTER_NOUN.match(low, h.end()) or "'s " in low[max(0, p - 90):p] or
                           "’s " in low[max(0, p - 90):p]):
            tie_pos.append(p)
            last_t = p
        if p > last_r:
            lw = low[max(body0, p - 320):p + 320]
            if any(st in lw for st in REJ_STEMS) and REJ.search(text, max(body0, p - 320), p + 320):
                rej_pos.append(p)
                last_r = p
    if not tie_pos and not rej_pos:
        return []
    hw = C.hard_wrapped(text, body0)
    view = C.unwrap_view(text, body0) if hw else text
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    recs = []
    done = set()
    # ties
    for p in tie_pos:
        part, _ = C.part_at(pm, p)
        if part not in COURT_PARTS:
            continue
        s0, s1 = C.sentence_span(view, p, p + 1)
        if ("t", s0) in done:
            continue
        done.add(("t", s0))
        for r in ties_in(view, s0, s1):
            r.update({"n": nid, "s": [s0, s1], "q": norm(view[s0:s1]), "part": COURT_PARTS[part]})
            recs.append(r)
    # rejections: the sentence of the noun must itself hold a rejection cue
    for p in rej_pos:
        part, _ = C.part_at(pm, p)
        if part not in COURT_PARTS:
            continue
        s0, s1 = C.sentence_span(view, p, p + 1)
        if ("r", s0) in done:
            continue
        done.add(("r", s0))
        s = view[s0:s1]
        if not REJ.search(s):
            continue
        labs = labels_in(s, s0)
        if not labs:
            continue
        cues = sorted(set(re.sub(r"\s+", " ", x.group(0).lower()) for x in REJ.finditer(s)))
        recs.append({"t": "rej", "n": nid, "cue": cues, "labels": [list(x) for x in labs], "s": [s0, s1],
                     "q": norm(s), "part": COURT_PARTS[part]})
    if any(r["t"] == "tie" for r in recs):
        pairs = []
        for m in C.CITE_RX.finditer(view, body0):
            k = C.cite_key(m)
            if not k:
                continue
            mm = NM_RX.search(view[max(body0, m.start() - 160):m.start()])
            if mm:
                pairs.append([re.sub(r"\s+", " ", mm.group(1)), k])
        if pairs:
            recs.append({"t": "nm", "n": nid, "pairs": pairs[:400]})
    return recs


def run_repo(task):
    repo, k, K, force, limit = task
    t0 = time.time()
    tag = repo if K == 1 else "%s.%02d" % (repo, k)
    out_j = os.path.join(OUT, tag + ".jsonl.gz")
    st_p = os.path.join(OUT, tag + ".stats.json")
    if os.path.exists(st_p) and not force:
        return tag, {"skipped": 1}
    nodes = {}
    for line in open(os.path.join(C.WORK, "nodes", repo + ".tsv"), encoding="utf-8"):
        p, nid, _date, _court = line.rstrip(NL).split("\t")
        nodes[p] = int(nid)
    rd = os.path.join(REPOS, repo)
    tree = subprocess.run(["git", "-C", rd, "ls-tree", "-r", "HEAD", "--", "decisions"], capture_output=True,
                          check=True, creationflags=NOWIN).stdout.decode("utf-8")
    items = []
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        _, typ, bsha = meta.split()
        if typ == "blob" and path.endswith(".md") and path in nodes:
            items.append((bsha, path))
    items = items[k * len(items) // K:(k + 1) * len(items) // K]
    if limit:
        items = items[:limit]
    p = subprocess.Popen(["git", "-C", rd, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         creationflags=NOWIN)

    def feed():
        for bsha, _ in items:
            p.stdin.write((bsha + NL).encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    st = {"files": 0, "tie": 0, "rej": 0, "nm": 0, "err": 0}
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
            for r in recs:
                st[r["t"]] += 1
                fj.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + NL)
    p.wait()
    os.replace(out_j + ".part", out_j)
    st["sec"] = round(time.time() - t0, 1)
    with open(st_p, "w", encoding="utf-8", newline=NL) as f:
        json.dump(st, f)
    return tag, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos")
    ap.add_argument("--procs", type=int, default=22)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    all_repos = sorted(f[:-4] for f in os.listdir(os.path.join(C.WORK, "nodes")) if f.endswith(".tsv"))
    repos = a.repos.split(",") if a.repos else all_repos

    def size(r):
        return os.path.getsize(os.path.join(C.WORK, "nodes", r + ".tsv"))
    order = sorted(repos, key=size, reverse=True)
    tasks = []
    for r in order:
        nlines = sum(1 for _ in open(os.path.join(C.WORK, "nodes", r + ".tsv"), encoding="utf-8"))
        K = max(1, -(-nlines // 30000))
        tasks += [(r, k, K, a.force, a.limit) for k in range(K)]
    print("repos:", len(order), "tasks:", len(tasks), flush=True)
    if a.procs <= 1 or len(tasks) == 1:
        for t in tasks:
            print(run_repo(t), flush=True)
        return
    import multiprocessing as mp
    with mp.Pool(a.procs) as pool:
        for tag, st in pool.imap_unordered(run_repo, tasks, chunksize=1):
            print(tag, json.dumps(st), flush=True)


if __name__ == "__main__":
    main()
