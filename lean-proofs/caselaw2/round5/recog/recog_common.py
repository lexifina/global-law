"""Shared helpers of round5/recog: paths, table lookups by streaming, W's text from git, the recognised text checks
(DESIGN5 section 2.2) exactly as the reference states them, and the choice of evidence inside a quote.

Nothing here reads gold lists, the holdout or the undetermined split. `reports_typed.tsv` is only ever read through
`typed_rows(ids)`, which keeps the rows whose id is in the given (feed) id set and never looks at the others.
"""
import gzip
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", ".."))
WORKROOT = os.path.normpath(os.path.join(C2, ".."))
DATA = os.path.join(C2, "data")
GRAPH = os.path.join(WORKROOT, "graph")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
TOOLS = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2")
READER = os.path.join(TOOLS, "reader")
TESTS = os.path.join(C2, "round5", "tests")
FEED = os.path.join(TESTS, "split", "feed_ids.tsv")
TYPED = os.path.join(C2, "gold", "reports_typed.tsv")
ITEMS = os.path.join(HERE, "items.jsonl.gz")
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

if READER not in sys.path:
    sys.path.insert(0, READER)
import common as RC  # noqa: E402  (reader/common.py: CITE_RX, cite_key, part_map2, part_at, name tokens)
import cue_table  # noqa: E402  (generated; RECOGNISED and DISQUALIFY_RECOGNISED are provisional until FREEZE.md)

NEG_KINDS = ("overruled", "abrogated", "disapproved", "recededFrom")
CERT_PARTS = ("majority", "plurality", "perCuriam")
PART_OUT = {"majority": "majority", "majority~": "majority", "perCuriam": "perCuriam", "plurality": "plurality",
            "concurrence": "concurrence", "concurrence~": "concurrence", "dissent": "dissent", "dissent~": "dissent"}
KIND_STEM = {"overruled": "overrul", "abrogated": "abrogat", "disapproved": "disapprov", "recededFrom": "reced"}
# stricter than the checker's substring test: the cue must start a word ("preceded" holds "reced")
CUE_WORD = re.compile(r"\b(overrul|abrogat|disapprov|reced)", re.I)
READER_ID = "claude-subagent:recog"


def tests_common():
    """round5/tests/common.py under another module name (reader/common.py is already `common`)."""
    spec = importlib.util.spec_from_file_location("r5tests_common", os.path.join(TESTS, "common.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ------------------------------------------------------------------------------------------- text normalisation
_ASCII_LOWER = {c: c + 32 for c in range(65, 91)}


def ascii_lower(s):
    return s.translate(_ASCII_LOWER)


def alnum(s):
    return re.sub(r"[^0-9a-z]", "", ascii_lower(s))


def clean(x):
    """SCHEMA: tabs and newlines (and a lone CR) become spaces, one for one."""
    return x.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def decode(raw):
    """The decision file text as SCHEMA defines it: bytes at HEAD, UTF-8 decoded, CR LF -> LF."""
    return raw.decode("utf-8", "replace").replace("\r\n", "\n")


def body_start(text):
    """Offset of the body as tools/caselaw2/eval/notes_extract.py cut it (note_offset counts from here)."""
    if text.startswith("---"):
        e = text.find("\n---", 3)
        if e >= 0:
            return e + 4
    return 0


# ------------------------------------------------------------------------------------------- streaming lookups
def nodes_info(want):
    """graph/nodes.tsv rows of the wanted node ids -> {node: (repo, path, cite, name)}."""
    out = {}
    wantb = {str(n).encode() for n in want}
    with open(os.path.join(GRAPH, "nodes.tsv"), "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            if raw[:i] in wantb:
                p = raw.rstrip(b"\r\n").decode("utf-8", "replace").split("\t")
                out[int(p[0])] = (p[1], p[2], p[5] if len(p) > 5 else "", p[6] if len(p) > 6 else "")
    return out


def decisions_info(want):
    """data/decisions2.tsv rows of the wanted nodes -> {node: (court_id, date, text_sha)}."""
    out = {}
    wantb = {str(n).encode() for n in want}
    with open(os.path.join(DATA, "decisions2.tsv"), "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            if raw[:i] in wantb:
                p = raw.rstrip(b"\r\n").split(b"\t")
                if len(p) >= 8:
                    out[int(p[0])] = (int(p[1]), int(p[2] or 0), p[7].decode("ascii", "replace"))
    return out


def typed_rows(ids):
    """Rows of gold/reports_typed.tsv whose id is in `ids` (feed ids only): {id: dict}. Other rows are skipped on
    their first field and never parsed."""
    out = {}
    idb = {str(i).encode() for i in ids}
    with open(TYPED, "rb") as f:
        head = f.readline().rstrip(b"\r\n").decode("utf-8").split("\t")
        for raw in f:
            i = raw.find(b"\t")
            if raw[:i] in idb:
                p = raw.rstrip(b"\r\n").decode("utf-8", "replace").split("\t")
                out[int(p[0])] = dict(zip(head, p))
    return out


def read_rows(path, minf=1):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if line:
                p = line.split("\t")
                if len(p) >= minf:
                    rows.append(p)
    return rows


def write_rows(path, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ------------------------------------------------------------------------------------------- git
def git_texts(repo, paths):
    """{path: bytes} of HEAD:<path> for each path of one corpus repo (one `git cat-file --batch`)."""
    out = {}
    if not paths:
        return out
    rd = os.path.join(REPOS, repo)
    inp = "".join("HEAD:%s\n" % p for p in paths).encode("utf-8")
    pr = subprocess.run(["git", "-C", rd, "cat-file", "--batch"], input=inp, capture_output=True,
                        creationflags=CREATE_NO_WINDOW)
    buf = pr.stdout
    pos = 0
    for p in paths:
        nl = buf.find(b"\n", pos)
        if nl < 0:
            break
        head = buf[pos:nl].split()
        pos = nl + 1
        if len(head) >= 2 and head[-1] == b"missing":
            continue
        if len(head) != 3:
            break
        size = int(head[2])
        out[p] = buf[pos:pos + size]
        pos += size + 1
    return out


def tree_shas(repo):
    """{path: blob sha} of every file under decisions/ at HEAD (one `git ls-tree -r`)."""
    rd = os.path.join(REPOS, repo)
    buf = subprocess.run(["git", "-C", rd, "ls-tree", "-r", "-z", "HEAD", "--", "decisions"], capture_output=True,
                         creationflags=CREATE_NO_WINDOW).stdout
    out = {}
    for ent in buf.split(b"\0"):
        if not ent:
            continue
        meta, path = ent.split(b"\t", 1)
        f = meta.split()
        if f[1] == b"blob":
            out[path.decode("utf-8", "replace")] = f[2].decode("ascii")
    return out


def git_blobs(repo, shas):
    """[bytes or None] for each blob sha, in order (one `git cat-file --batch`; far faster than HEAD:<path>)."""
    if not shas:
        return []
    rd = os.path.join(REPOS, repo)
    pr = subprocess.run(["git", "-C", rd, "cat-file", "--batch"], input="".join(s + "\n" for s in shas).encode(),
                        capture_output=True, creationflags=CREATE_NO_WINDOW)
    buf, pos, out = pr.stdout, 0, []
    for _ in shas:
        nl = buf.find(b"\n", pos)
        if nl < 0:
            out.append(None)
            continue
        head = buf[pos:nl].split()
        pos = nl + 1
        if len(head) != 3:
            out.append(None)
            continue
        size = int(head[2])
        out.append(buf[pos:pos + size])
        pos += size + 1
    return out


# ------------------------------------------------------------------------------------------- citation indexes
def live_cite_index():
    """data/cite_index.tsv as the checkers load it: compact key -> node, None when >= 2 distinct nodes."""
    m = {}
    for p in read_rows(os.path.join(DATA, "cite_index.tsv"), 2):
        k = alnum(p[0])
        if k:
            m.setdefault(k, set()).add(int(p[1]))
    return {k: (next(iter(v)) if len(v) == 1 else None) for k, v in m.items()}


def graph_cite_rows(keys):
    """graph/cite_index.tsv rows whose normalised key is in `keys`: {key: set(nodes)} (streamed)."""
    out = {}
    kb = {k.encode("utf-8") for k in keys}
    if not kb:
        return out
    with open(os.path.join(GRAPH, "cite_index.tsv"), "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            if raw[:i] in kb:
                out.setdefault(raw[:i].decode("utf-8"), set()).add(int(raw[i + 1:].strip()))
    return out


def cite_keys_in(s):
    """[(normalised key, compact key)] of every citation pattern in s, in order."""
    out = []
    for m in RC.CITE_RX.finditer(s):
        k = RC.cite_key(m)
        if k:
            out.append((k, alnum(k)))
    return out


# ------------------------------------------------------------------------------------------- the text checks
def cue_ok(quote):
    return any(c in ascii_lower(quote) for c in cue_table.RECOGNISED)


def disqualifiers_in(quote):
    ql = ascii_lower(quote)
    return [d for d in cue_table.DISQUALIFY_RECOGNISED if d in ql]


def resolve_in_quote(ev, quote, node, index):
    """DESIGN5 2.2: the evidence resolves against the normalised quote only. `index`: compact key -> node / None."""
    ql = ascii_lower(quote)
    if ev.startswith("cite:"):
        c = alnum(ev[5:])
        return bool(c) and c in alnum(ql) and index.get(c) == node
    if ev.startswith("name:"):
        words = set(re.findall(r"[0-9a-z]+", ql))
        toks = [alnum(x) for x in ev[5:].split(" ")]
        toks = [x for x in toks if len(x) >= 3]
        return bool(toks) and all(x in words for x in toks)
    return False


def caption_words(name, other_name):
    """The caption's distinctive words usable as `name:` evidence, in caption order: a list of piece lists (a word
    such as "Meraz-Valeta" has two pieces; pieces under 3 characters are dropped). Words of the other decision's
    caption are left out."""
    def toks(nm):
        return RC.name_tokens(nm) | RC.short_name_tokens(nm)
    mine, theirs = toks(name), {t.lower() for t in toks(other_name)}
    theirs |= set(re.findall(r"[0-9a-z]+", (other_name or "").lower()))
    out = []
    for t in sorted(mine, key=lambda t: ((name or "").find(t), t)):
        pieces = [x for x in re.sub(r"[^0-9A-Za-z]+", " ", t).split() if len(x) >= 3]
        if pieces and not any(x.lower() in theirs for x in pieces):
            out.append(pieces)
    return out


def name_evidence(name, other_name, quote):
    """`name:` evidence for a caption: the caption's distinctive words (reader/common.name_tokens and the three-letter
    party names) that stand in the quote as capitalised whole words and are not words of the other decision's
    caption. At most two, in caption order. None when there is none."""
    qwords = set(re.findall(r"[0-9A-Za-z]+", quote))
    picked = [" ".join(pieces) for pieces in caption_words(name, other_name) if all(x in qwords for x in pieces)]
    if not picked:
        return None
    return "name:" + " ".join(picked[:2])


def evidence_for(node, name, other, quote, live, graph, cite_only=False):
    """The evidence the certifier takes for `node` inside `quote`, and the cite_index delta row it needs (or None):
    the first citation of the quote that resolves to the node (live index: compact key -> node; else the graph
    index when the key is absent from the live one and names exactly this node), else `name:` caption words.
    (None, None) when the quote does not name the node. certify_recog.py and build_t1f.py both use this."""
    for k, c in cite_keys_in(quote):
        if live.get(c) == node:
            return "cite:" + k, None
        if c not in live and graph.get(k) == {node}:
            return "cite:" + k, (k, node)
    if cite_only:
        return None, None
    return name_evidence(name, other, quote), None


# ------------------------------------------------------------------------------------------- the reader's quote
def find_quote(lw, quote, prefer, hyphen=False):
    """Position of the reader's quote in the window (as reader/certify.find_quote): exact, else tolerant of
    whitespace runs and quote-mark styles (and, with hyphen=True, of line-end hyphenation the reader left out).
    The window's own text is what gets used."""
    q = (quote or "").strip()
    if not q or len(q) > 900:
        return None
    hits = [m.start() for m in re.finditer(re.escape(q), lw)]
    if hits:
        i = min(hits, key=lambda h: abs(h - prefer))
        return i, i + len(q)
    parts = []
    for ch in q:
        if ch.isspace():
            if not parts or parts[-1] != r"\s+":
                parts.append(r"\s+")
        elif ch in "'’‘`":
            parts.append("['’‘`]")
        elif ch in '"“”':
            parts.append('["“”]')
        elif hyphen and ch.isalpha():
            parts.append(re.escape(ch) + "(?:- +)?")
        else:
            parts.append(re.escape(ch))
    try:
        ms = list(re.finditer("".join(parts), lw))
    except re.error:
        return None
    if not ms:
        return None
    m = min(ms, key=lambda m: abs(m.start() - prefer))
    return m.start(), m.end()


def quoted(w, a, b):
    """As reader/certify.quoted: w[a:b] sits inside a quotation of another text (it starts with an opening quote mark
    or an altered capital, or an opening curly quote before it is still open and closes within 300 characters)."""
    q = w[a:b].lstrip()
    if q[:1] in ("“", '"') or re.match(r"\[[A-Z]\]", q):
        return True
    before = w[max(0, a - 400):a]
    if before.rfind("“") > before.rfind("”") and "”" in w[b:b + 300]:
        return True
    return False


# scope words inside a quote (tools/caselaw2/eval/notes_build.py): only ever used to make a scope narrower
OTHER_RX = re.compile(r"other\s+grounds?|another\s+ground|different\s+grounds?|other\s+points?|another\s+point|"
                      r"different\s+point|other\s+issues?|another\s+issue|unrelated\s+grounds|separate\s+grounds", re.I)
PART_RX = re.compile(r"\bin\s+part\b|relevant\s+part|other\s+part|other\s+respects|partially|to\s+the\s+extent|insofar|"
                     r"in\s+so\s+far|so\s+far\s+as|on\s+(?:this|that|the\s+latter|the\s+former)\s+point", re.I)


def para_intro(text, off, d0, hw, n=400):
    """(intro, start): the first n characters of the paragraph (footnote, list) that holds `off`, when that start
    lies before the shown window (d0); "" otherwise. Paragraphs end at a blank line in a hard-wrapped text, at a
    line break otherwise. The intro stops at the window start (no text is shown twice)."""
    sep = "\n\n" if hw else "\n"
    p = text.rfind(sep, 0, off)
    p = 0 if p < 0 else p + len(sep)
    if p >= d0:
        return "", p
    return clean(text[p:min(p + n, d0)]).strip(), p


def explicit_ok_pairs():
    """(Y, X) pairs with an explicit scope-all status-changing row by Y on X whose certificate is `ok` in
    out/certs.tsv; and the live treatments / witness tables."""
    live_t = {p[0]: p for p in read_rows(os.path.join(DATA, "treatments.tsv"), 16)}
    wit = read_rows(os.path.join(DATA, "treatment_witness.tsv"), 4)
    certs = {}
    for p in read_rows(os.path.join(C2, "out", "certs.tsv"), 3):
        if p[0] == "treatment":
            certs[p[1]] = p[2]
    ok = set()
    for p in live_t.values():
        if p[7] == "1" and p[4] in NEG_KINDS and p[5] == "all" and certs.get(p[0]) == "ok":
            ok.add((int(p[1]), int(p[2])))
    return ok, live_t, wit, certs


ITEMS_T1S = os.path.join(HERE, "items_t1s.jsonl.gz")


# the introduction of a list ("the Court has overruled in whole or in part 33 of its previous decisions"): every
# entry of such a list is partial unless it says otherwise
WHOLE_PART_RX = re.compile(r"in\s+whole\s+or\s+in\s+part|in\s+part\s+or\s+in\s+whole|whole\s+or\s+(?:in\s+)?part|"
                           r"wholly\s+or\s+(?:in\s+part|partly|partially)|entirely\s+or\s+in\s+part|"
                           r"in\s+part\s+or\s+entirely", re.I)


def load_items(path=None, ids=None):
    """Items by id. Default: items.jsonl.gz (T0, T1, T2, T3) and items_t1s.jsonl.gz (T1s) when present."""
    paths = [path] if path else [p for p in (ITEMS, ITEMS_T1S) if os.path.exists(p)]
    out = {}
    for p in paths:
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                it = json.loads(line)
                if ids is None or it["id"] in ids:
                    out[it["id"]] = it
    return out


def sha1_bytes(b):
    return hashlib.sha1(b).hexdigest()


def sha1_text(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()
