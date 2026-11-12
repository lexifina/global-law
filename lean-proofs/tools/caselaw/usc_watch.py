"""Watch lists over the US Code record: tell a user when a section they depend on changes, with the diff and the law.

    python tools/caselaw/usc_watch.py --list watch.txt --since 2015-01-01 [--html out.html] [--json out.json]
    python tools/caselaw/usc_watch.py --doc opinion.md            (watched from the date in its front matter)
    python tools/caselaw/usc_watch.py --list watch.txt --digest 2026-10-01 2026-11-03

A watch list has one citation per line, in any form usc_cite reads ("18 USC 924(c)", "11 U.S.C. § 707(b)",
"section 1334 of title 28", "9 U.S.C. §§ 1-16" for a range); "#" starts a comment. A document (txt, md, docx, pdf if
pypdf is installed) is read for every US Code citation it makes, as the case-law reader does.

What is watched: the deepest designation the citation names that the record's text has ("924(c)(1)(A)" watches
paragraph (c)(1)(A); a designation found in no version of the section falls back to its parent, and to the whole
section). Words are compared after folding whitespace and typography (usc_encode.norm), so a reprint is not a change.

The decision to alert is Lean's: LegalProofs/USCaseLaw/Watch.lean (`alerts`, `notices`), run in one batch by
RunWatch.lean. An alert is a law in force after the since-day and by the read-day that changed the words watched; an
edition (reprint, editorial change) that changed them is a notice, reported apart, never an alert.
"""
from __future__ import annotations

import argparse, collections, datetime, difflib, hashlib, html, json, os, re, subprocess, sys, tempfile, threading, time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import usc_cite  # noqa: E402
from usc_encode import FOLD, blocks  # noqa: E402

_FOLD_PAIRS = [(chr(k), v) for k, v in FOLD.items()]


def norm(s):
    """usc_encode.norm (fold typography, collapse whitespace), written with str.replace: str.translate with a dict
    is slow on long sections."""
    for a, b in _FOLD_PAIRS:
        if a in s:
            s = s.replace(a, b)
    return " ".join(s.split())

HOME = os.path.expanduser("~")
WORK = os.path.join(HOME, "Documents", "us-caselaw-lean-work")
GIT = os.path.join(WORK, "usc-full.git")
VERSIONS = os.path.join(WORK, "usc", "versions.tsv")
LEAN_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RUNNER = "LegalProofs/USCaseLaw/RunWatch.lean"
REVIEW_WORDS = 20  # an edition notice that changes this many words is marked for review
SUBX = re.compile(r"\s?\(([a-zA-Z]{1,6}|\d{1,3}[A-Z]{0,2})\)")
LINE = re.compile(r"^ *-\s+\[?((?:\([A-Za-z0-9]+\))+)", re.M)
ROMAN = re.compile(r"^(?:i{1,3}|iv|vi{0,3}|ix|xi{0,3}|xiv|xvi{0,3}|xix|xx)$", re.I)

V = collections.namedtuple("V", "path sha law label day blob short order")


def ymd(s):
    s = str(s).replace("-", "")
    return int(s[:8])


def iso(d):
    s = str(d)
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}"


# ---------------------------------------------------------------- record

def load_versions(fn=VERSIONS):
    vers = collections.defaultdict(list)
    for i, l in enumerate(open(fn, encoding="utf-8")):
        f = l.rstrip("\n").split("\t")
        vers[f[0]].append(V(f[0], f[1], f[2] == "law", f[3], int(f[4]), f[5], html.unescape(f[6]) if len(f) > 6 else "", i))
    for p in vers:
        vers[p].sort(key=lambda v: (v.day, v.order))
    return vers


def cat_batch(git, names):
    """git cat-file --batch for many objects at once: name -> bytes (None when missing)."""
    names = list(dict.fromkeys(n for n in names if n))
    out = {}
    if not names:
        return out
    pr = subprocess.Popen(["git", "--git-dir", git, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def feed():
        for n in names:
            pr.stdin.write((n + "\n").encode())
        pr.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    for n in names:
        head = pr.stdout.readline().split()
        if len(head) < 3 or head[1] == b"missing":
            out[n] = None
            continue
        size = int(head[2])
        out[n] = pr.stdout.read(size)
        pr.stdout.read(1)
    pr.wait()
    return out


# ---------------------------------------------------------------- what to watch

def _chain(text, pos):
    out = []
    while True:
        m = SUBX.match(text, pos)
        if not m:
            return out
        out.append(m.group(1))
        pos = m.end()


def items_from_text(text, vers, decided=None, ranges=False):
    """(title, section, chain of designations) for every citation in `text`, first-seen order, with mentions."""
    exists = lambda t, s: f"title-{t}/{s}.md" in vers  # noqa: E731
    found = collections.OrderedDict()
    by_title = None
    for c in usc_cite.cites(text, exists, long_forms=True):
        t, s = c["title"], c["section"]
        if decided and usc_cite.old_numbering(c, iso(decided), None, None):
            continue
        secs = [s]
        if c["role"] == "range-end":
            continue
        if c["role"] == "range-start":
            if not ranges:
                continue
            a, b = c["section"], c.get("range_to", "")
            if not (a.isdigit() and b.isdigit()):
                continue
            if by_title is None:
                by_title = collections.defaultdict(list)
                for p in vers:
                    tt, ss = p[6:-3].split("/", 1)
                    by_title[tt].append(ss)
            secs = sorted((x for x in by_title[str(t)] if re.match(r"\d+", x) and int(a) <= int(re.match(r"\d+", x).group()) <= int(b)),
                          key=lambda x: (int(re.match(r"\d+", x).group()), x))
        for sec in secs:
            ch = _chain(text, c["at"] + len(s)) if sec == s and c["role"] == "cited" else []
            k = (t, sec, tuple(ch))
            if k not in found:
                found[k] = {"title": t, "section": sec, "chain": ch, "mentions": 0, "how": c["how"][:120]}
            found[k]["mentions"] += 1
    # a bare citation of a section that is also cited at a designation adds nothing
    named = {(k[0], k[1]) for k in found if k[2]}
    return [v for k, v in found.items() if k[2] or (k[0], k[1]) not in named]


def read_document(fn):
    """Text of a document and the day in its front matter (decided/date), if any."""
    ext = os.path.splitext(fn)[1].lower()
    day = None
    if ext == ".docx":
        with zipfile.ZipFile(fn) as z:
            x = z.read("word/document.xml").decode("utf-8", "replace")
        x = re.sub(r"</w:p>", "\n", x)
        text = html.unescape(re.sub(r"<[^>]+>", "", x))
    elif ext == ".pdf":
        import pypdf  # optional
        text = "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(fn).pages)
    else:
        text = open(fn, encoding="utf-8", errors="replace").read()
        if text.startswith("---"):
            end = text.find("\n---", 3)
            fm = text[:end]
            m = re.search(r'^(?:decided|date):\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M)
            if m:
                day = ymd(m.group(1))
            text = text[end + 4:]
    return text, day


# ---------------------------------------------------------------- the words watched

def _succ(d):
    if d.isdigit():
        return {str(int(d) + k) for k in (1, 2, 3)}
    if ROMAN.match(d) and len(d) > 1:
        return set()
    if len(d) == 1:
        return {chr(ord(d) + k) for k in (1, 2, 3)}
    if d == d[0] * len(d):
        return {chr(ord(d[0]) + k) * len(d) for k in (1, 2, 3)}
    return set()


def narrow(block, target):
    """The part of `block` (whose first line starts the parent) designated `target` at any depth below it, or None.
    Where several lines start with the designation, the one printed shallowest (first among equals) is taken. It runs
    to the next sibling designation, or to the next line printed less deep than it (the parent's flush text, "Except
    when ..."), whichever comes first."""
    lines = block.split("\n")
    best = None
    for i, ln in enumerate(lines):
        m = LINE.match(ln)
        if not m:
            continue
        ch = re.findall(r"\(([A-Za-z0-9]+)\)", m.group(1))
        if i == 0:
            ch = ch[1:]  # the parent's own designation
        if ch and ch[0] == target:
            ind = len(ln) - len(ln.lstrip(" "))
            if best is None or ind < best[1]:
                best = (i, ind)
    if best is None:
        return None
    start, ind = best
    succ = _succ(target)
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        li = len(ln) - len(ln.lstrip(" "))
        if ln.lstrip().startswith("-") and li < ind:
            return "\n".join(lines[start:i])
        m = LINE.match(ln)
        if m:
            ch = re.findall(r"\(([A-Za-z0-9]+)\)", m.group(1))
            if ch and ch[0] in succ:
                return "\n".join(lines[start:i])
    return "\n".join(lines[start:])


def watched_block(text, chain, depth):
    """Text of the watched designation (chain[:depth]) in one version of a section ('' when absent). The subsection
    is usc_encode's block; below it, each level is narrowed in turn. Where the record prints a run-in list flush with
    the subsections (so that the block ends early), the search below the subsection runs on to the section's end."""
    if depth == 0:
        return text
    b = blocks(text).get(chain[0])
    if b is None:
        return ""
    if depth == 1:
        return b
    r = _descend(b, chain, depth)
    if r is None:
        r = _descend(text[text.find(b):], chain, depth)
    return r or ""


def _descend(b, chain, depth):
    for k in range(1, depth):
        # the first line of `b` may combine several designations: "(c)(1)(A) ..."
        first = LINE.match(b)
        fch = re.findall(r"\(([A-Za-z0-9]+)\)", first.group(1)) if first else []
        if len(fch) > k and fch[:k + 1] == list(chain[:k + 1]):
            nb = narrow_combined(b, chain[k], k)
        else:
            nb = narrow(b, chain[k])
        if nb is None:
            return None
        b = nb
    return b


def narrow_combined(block, target, k):
    lines = block.split("\n")
    succ = _succ(target)
    for i, ln in enumerate(lines[1:], 1):
        m = LINE.match(ln)
        if m:
            ch = re.findall(r"\(([A-Za-z0-9]+)\)", m.group(1))
            if ch and ch[0] in succ:
                return "\n".join(lines[:i])
    return block


def display(s):
    s = norm(s)
    s = re.sub(r"(^| )- (?=\[?\()", r"\1", s)
    s = re.sub(r"^# ", "", s)
    return s


# ---------------------------------------------------------------- diffs

def _word_ops(A, B):
    if len(A) * len(B) > 25_000_000:
        return [("replace", A, B)]
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    return [(t, A[i1:i2], B[j1:j2]) for t, i1, i2, j1, j2 in sm.get_opcodes()]


def word_diff(a, b, ctx=10, max_hunks=8):
    """Word-level diff of two blocks of the record: (segments, words struck, words inserted, hunks). Lines are
    matched first (so that a long section costs little), then words within the lines that differ. Segments are
    (kind, text) with kind 'eq', 'del', 'ins' or 'gap' (elided context)."""
    la = [x for x in (display(l) for l in a.splitlines()) if x]
    lb = [x for x in (display(l) for l in b.splitlines()) if x]
    raw = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes():
        A = " ".join(la[i1:i2]).split()
        B = " ".join(lb[j1:j2]).split()
        raw += [(tag, A, B)] if tag == "equal" else _word_ops(A, B)
    ops = []
    for tag, A, B in raw:  # merge neighbouring equal runs
        if ops and tag == "equal" and ops[-1][0] == "equal":
            ops[-1] = ("equal", ops[-1][1] + A, ops[-1][2] + B)
        elif A or B:
            ops.append((tag, A, B))
    segs, struck, ins, hunks = [], 0, 0, 0
    for n, (tag, A, B) in enumerate(ops):
        if tag == "equal":
            w = A
            first, last = n == 0, n == len(ops) - 1
            if first and len(w) > ctx:
                segs += [("gap", ""), ("eq", " ".join(w[-ctx:]))]
            elif last and len(w) > ctx:
                segs += [("eq", " ".join(w[:ctx])), ("gap", "")]
            elif not first and not last and len(w) > 2 * ctx + 3:
                segs += [("eq", " ".join(w[:ctx])), ("gap", ""), ("eq", " ".join(w[-ctx:]))]
            else:
                segs.append(("eq", " ".join(w)))
            continue
        hunks += 1
        if A:
            segs.append(("del", " ".join(A))); struck += len(A)
        if B:
            segs.append(("ins", " ".join(B))); ins += len(B)
    if hunks > max_hunks:
        # keep the first max_hunks changes
        out, h = [], 0
        for s in segs:
            if s[0] in ("del", "ins"):
                if out and out[-1][0] not in ("del", "ins"):
                    h += 1
                elif not out:
                    h += 1
            if h > max_hunks:
                out.append(("gap", f"{hunks - max_hunks} more changes"))
                break
            out.append(s)
        segs = out
    return segs, struck, ins, hunks


def diff_text(segs):
    o = []
    for k, t in segs:
        o.append({"eq": t, "gap": f"… {t} …" if t else "…", "del": f"[-{t}-]", "ins": f"{{+{t}+}}"}[k])
    return " ".join(x for x in o if x)


# ---------------------------------------------------------------- commit notes

ENTRY = re.compile(r"^(\d+) U\.S\.C\. §([0-9A-Za-z\-]+)(\([^ ]*)?\. (.*)$")


def section_notes(msg, t, s):
    """The law's own entries for this section in its commit message: [{action, note, link}]."""
    out, cur = [], None
    for ln in msg.splitlines():
        m = ENTRY.match(ln)
        if m:
            cur = None
            if m.group(1) == str(t) and m.group(2) == s:
                cur = {"action": m.group(4).split(".")[0], "where": (m.group(3) or ""), "lines": [], "link": ""}
                out.append(cur)
            continue
        if cur is None:
            continue
        if ln.startswith("  "):
            x = ln.strip()
            if x.startswith("https://"):
                cur["link"] = x
            elif not x.startswith("Instruction:"):
                cur["lines"].append(x)
        elif ln.strip():
            cur = None
    return [{"action": e["action"] + (" " + e["where"] if e["where"] else ""), "note": " ".join(e["lines"]), "link": e["link"]}
            for e in out]


# ---------------------------------------------------------------- the watch

def tid_factory():
    ids = {}

    def tid(s):
        if s is None:
            return 0
        h = hashlib.sha1(s.encode()).digest()
        return ids.setdefault(h, len(ids) + 1)
    return tid


def run_lean(rows, lean_dir=LEAN_DIR):
    with tempfile.TemporaryDirectory() as td:
        inp, out = os.path.join(td, "in.tsv"), os.path.join(td, "out.tsv")
        with open(inp, "w", encoding="utf-8", newline="\n") as f:
            f.write("".join(r + "\n" for r in rows))
        r = subprocess.run(["lake", "env", "lean", "--run", RUNNER, inp, out], cwd=lean_dir, capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("Lean runner failed:\n" + r.stdout + r.stderr)
        res = {}
        for l in open(out, encoding="utf-8"):
            f = l.rstrip("\n").split("\t")
            res[f[0]] = {"alert": f[1] == "1", "alerts": int(f[2]), "notices": int(f[3]), "sorted": f[4] == "1",
                         "same": f[5] == "1", "codes": f[6] if len(f) > 6 else ""}
        return res, r.stdout.strip()


def watch(items, since, today, vers, git=GIT, lean_dir=LEAN_DIR):
    """Run a watch: for each item, every version after `since` and by `today`, Lean's decision, diffs and laws."""
    t0 = time.time()
    plan = []
    for n, it in enumerate(items):
        path = f"title-{it['title']}/{it['section']}.md"
        vs = [v for v in vers.get(path, []) if v.day <= today]
        it = dict(it, id=n, path=path, cite=f"{it['title']} U.S.C. § {it['section']}" + "".join(f"({c})" for c in it["chain"]))
        if not vs:
            plan.append((it, []))
            continue
        k = max((i for i, v in enumerate(vs) if v.day <= since), default=-1)
        plan.append((it, vs[max(k, 0):]))
    blobs = cat_batch(git, [v.blob for _, vs in plan for v in vs])
    text = {b: x.decode("utf-8", "replace") for b, x in blobs.items() if x is not None}
    tid = tid_factory()
    rows = []
    for it, vs in plan:
        if not vs:
            continue
        txt = [text.get(v.blob) if v.blob else None for v in vs]
        # the deepest designation named that some version has
        depth, ch0 = 0, list(it["chain"])
        # the chain as cited; read with "l" as "1" (a common scanning error, "1154(a)(l)(D)"); with a paragraph
        # number dropped before a subparagraph the record prints flush with the subsection ("553(b)(3)(A)" for
        # "553(b)(A)"); then shorter and shorter
        ocr = [("1" if c == "l" else c) for c in ch0]
        skips = [ch0[:k] + ch0[k + 1:] for k in range(len(ch0) - 2, 0, -1) if ch0[k].isdigit() and ch0[k + 1].isupper()]
        # after a lettered subsection, "(l)" is a paragraph "(1)" misread
        ocr_first = any(c == "l" and k > 0 and ch0[k - 1].isalpha() and ch0[k - 1].islower() for k, c in enumerate(ch0))
        cands = ([ocr, ch0] if ocr_first else [ch0] + ([ocr] if ocr != ch0 else [])) + skips + [ch0[:d] for d in range(len(ch0) - 1, 0, -1)]
        for ch in cands:
            if any(t is not None and watched_block(t, ch, len(ch)).strip() for t in txt):
                it["chain"], depth = ch, len(ch)
                break
        it["depth"] = depth
        it["watched"] = (f"{it['title']} U.S.C. § {it['section']}" + "".join(f"({c})" for c in it["chain"][:depth]))
        whole = depth == 0
        it["blocks"] = [watched_block(t, it["chain"], depth) if t is not None else None for t in txt]
        parts = []
        for v, t, b in zip(vs, txt, it["blocks"]):
            x = tid(norm(t)) if t is not None else 0
            y = (tid(norm(b)) if b is not None else 0) if not whole else x
            parts.append(f"{v.day},{1 if v.law else 0},{x},{y}")
        rows.append(f"{it['id']}\t{since}\t{today}\t{1 if whole else 0}\t" + "\t".join(parts))
    t1 = time.time()
    res, lean_msg = run_lean(rows, lean_dir) if rows else ({}, "")
    t2 = time.time()
    # law messages for the versions in the window
    shas = [v.sha for _, vs in plan for v in vs if since < v.day <= today]
    commits = cat_batch(git, shas)
    msgs = {s: (c.decode("utf-8", "replace").split("\n\n", 1)[1] if c else "") for s, c in commits.items()}
    out = []
    for it, vs in plan:
        rec = {k: it[k] for k in ("id", "cite", "title", "section", "chain", "mentions") if k in it}
        rec.update(path=it["path"], since=iso(since), today=iso(today))
        if not vs:
            rec.update(status="not in the record", watched=it["cite"], alert=False, changes=[], editions=[])
            out.append(rec)
            continue
        r = res[str(it["id"])]
        rec.update(watched=it["watched"], level=["section", "subsection", "paragraph", "subparagraph", "clause", "subclause"][min(it["depth"], 5)],
                   alert=r["alert"], alerts=r["alerts"], notices=r["notices"], same_words=r["same"], lean_sorted=r["sorted"])
        changes, editions = [], []
        for i, (v, code) in enumerate(zip(vs, r["codes"])):
            if code == ".":
                continue
            prev_t = it["blocks"][i - 1] if i > 0 else None
            new_t = it["blocks"][i]
            full_prev = text.get(vs[i - 1].blob) if i > 0 and vs[i - 1].blob else None
            full_new = text.get(v.blob) if v.blob else None
            c = {"day": iso(v.day), "by": "law" if v.law else "edition", "law": v.label, "short_title": v.short,
                 "commit": v.sha, "lean": code,
                 "watched_changed": code in ("A", "N")}
            if full_new is None:
                c["event"] = "repealed" if v.law else "removed"
            elif full_prev is None:
                c["event"] = "added"
            else:
                c["event"] = "amended"
            # which subsections changed
            if full_prev is not None and full_new is not None:
                bp, bn = blocks(full_prev), blocks(full_new)
                c["subsections_changed"] = [k for k in list(dict.fromkeys(list(bp) + list(bn))) if norm(bp.get(k, "")) != norm(bn.get(k, ""))]
            if v.law:
                c["notes"] = section_notes(msgs.get(v.sha, ""), it["title"], it["section"])
            if code in ("A", "N"):
                segs, s_, i_, h_ = word_diff(prev_t or "", new_t or "")
                c.update(diff=segs, words_struck=s_, words_inserted=i_, hunks=h_)
                if not v.law and s_ + i_ >= REVIEW_WORDS:
                    # the record credits to an edition what no law taking effect that day accounts for: mostly
                    # editorial, but also law changes it could not date (the First Step Act's change to 21 U.S.C. 841)
                    c["review"] = True
            if code in ("A", "N") and full_new is not None and it["depth"] and not (new_t or "").strip() and (prev_t or "").strip():
                c["event"] = "designation gone (struck or redesignated)"
                now = find_designation(prev_t, full_new)
                if now:
                    c["event"] = f"redesignated: now ({now})"
            if c["event"] in ("repealed", "removed") and full_prev:
                c["moved_to"] = find_move(git, vers, v.day, full_prev)
            (changes if v.law else editions).append(c)
        rec["changes"], rec["editions"] = changes, editions
        last = vs[-1]
        if not last.blob:
            mv = next((c.get("moved_to") for c in reversed(changes + editions) if c.get("moved_to")), None)
            rec["status"] = f"moved to {mv}" if mv else ("repealed" if last.law else "removed by an edition")
        elif r["alert"]:
            rec["status"] = "changed by law"
        elif r["notices"]:
            rec["status"] = "edition change only"
        elif changes:
            rec["status"] = "other parts amended"
        else:
            rec["status"] = "unchanged"
        out.append(rec)
    # several citations that come down to the same words watched are one item
    merged, at = [], {}
    for r in out:
        k = r["watched"]
        if k in at:
            at[k]["cited_as"].append(r["cite"]); at[k]["mentions"] = at[k].get("mentions", 0) + r.get("mentions", 0)
            continue
        r["cited_as"] = [r["cite"]]
        at[k] = r
        merged.append(r)
    out = merged
    timing = {"read_and_encode_s": round(t1 - t0, 3), "lean_s": round(t2 - t1, 3), "report_s": round(time.time() - t2, 3),
              "lean": lean_msg}
    return out, timing


def find_designation(old_block, new_text):
    """The top-level designation of `new_text` whose words are nearly those of `old_block`, or None."""
    a = set(display(old_block).lower().split()[1:])
    best, bk = 0.0, None
    for k, b in blocks(new_text).items():
        w = set(display(b).lower().split()[1:])
        j = len(a & w) / max(1, len(a | w))
        if j > best:
            best, bk = j, k
    return bk if best >= 0.6 else None


_FIRSTS = {}


def find_move(git, vers, day, prev_text):
    """A section whose first version came into force the same day with nearly the same words (a renumbering or a
    transfer to another title), or None."""
    if not _FIRSTS:
        for p, vs in vers.items():
            f = next((v for v in vs if v.blob), None)
            if f:
                _FIRSTS.setdefault(f.day, []).append((p, f.blob))
    cand = _FIRSTS.get(day, [])[:5000]
    if not cand:
        return None
    got = cat_batch(git, [b for _, b in cand])
    a = set(norm(prev_text).lower().split()[8:])
    best, bp = 0.0, None
    for p, b in cand:
        x = got.get(b)
        if not x:
            continue
        w = set(norm(x.decode("utf-8", "replace")).lower().split()[8:])
        jx = len(a & w) / max(1, len(a | w))
        if jx > best:
            best, bp = jx, p
    if best >= 0.6:
        t, s_ = bp[6:-3].split("/", 1)
        return f"{t} U.S.C. § {s_}"
    return None


# ---------------------------------------------------------------- reports

def terminal(recs, since, today, title=None, record_end=None):
    o = []
    al = [r for r in recs if r.get("alert")]
    o.append(title or "US Code watch")
    o.append(f"Watched from {iso(since)} to {iso(today)}" + (f" (the record runs to {iso(record_end)})" if record_end else "")
             + f": {len(recs)} items, {len(al)} with an alert.")
    o.append("")
    for r in recs:
        if not r.get("alert"):
            continue
        o.append(f"ALERT  {r['watched']}  ({r['status']})" + (f"  [cited as {', '.join(r['cited_as'])}]" if r["cited_as"] != [r["watched"]] else ""))
        for c in r["changes"]:
            mark = "words changed" if c["watched_changed"] else "other parts only"
            if c["watched_changed"] or True:
                o.append(f"  {c['day']}  {c['law']}" + (f" ({c['short_title']})" if c["short_title"] else "") + f"  -- {c['event']}, {mark}"
                         + (f"; changed: {', '.join('(' + x + ')' for x in c.get('subsections_changed', [])[:8])}" if c.get("subsections_changed") else ""))
            for n in c.get("notes", [])[:2]:
                if n["note"]:
                    o.append(f"      {n['action']}: {n['note'][:240]}")
            if c.get("diff"):
                o.append(f"      -{c['words_struck']} +{c['words_inserted']} words: " + diff_text(c["diff"])[:900])
            if c.get("moved_to"):
                o.append(f"      moved to {c['moved_to']}")
        if r["editions"]:
            o.append(f"  editions (not alerts): " + "; ".join(f"{c['day']} {c['law']}" + (" (changed the words" + (f", {c['words_struck'] + c['words_inserted']} words: review, may be an undated law" if c.get("review") else "") + ")" if c["watched_changed"] else "") for c in r["editions"]))
        o.append("")
    quiet = collections.Counter(r["status"] for r in recs if not r.get("alert"))
    o.append("No alert: " + ", ".join(f"{v} {k}" for k, v in quiet.most_common()))
    for r in recs:
        if not r.get("alert") and r["status"] != "unchanged":
            ed = [c for c in r.get("editions", []) if c["watched_changed"]]
            o.append(f"  {r['watched']}: {r['status']}" + (f" (edition {', '.join(c['day'] + (' REVIEW ' + str(c['words_struck'] + c['words_inserted']) + ' words' if c.get('review') else '') for c in ed)})" if ed else "")
                     + (f"; laws on other parts: {', '.join(c['law'] for c in r['changes'])}" if r.get("changes") else ""))
    return "\n".join(o)


def digest(recs):
    """Every law change in the window, grouped by law."""
    laws = collections.OrderedDict()
    for r in recs:
        for c in r.get("changes", []):
            k = (c["day"], c["law"])
            if k not in laws:
                laws[k] = {"day": c["day"], "law": c["law"], "short_title": c["short_title"], "items": []}
            laws[k]["items"].append({"watched": r["watched"], "watched_changed": c["watched_changed"], "event": c["event"],
                                     "subsections_changed": c.get("subsections_changed", []),
                                     "notes": c.get("notes", []), "diff": c.get("diff"),
                                     "words_struck": c.get("words_struck"), "words_inserted": c.get("words_inserted")})
    return sorted(laws.values(), key=lambda x: (x["day"], x["law"]))


def digest_terminal(groups, recs, since, today):
    f0 = datetime.datetime.strptime(str(since), "%Y%m%d").date() + datetime.timedelta(days=1)
    o = [f"Digest: law changes in force {f0.isoformat()} to {iso(today)} to the {len(recs)} watched items", ""]
    for g in groups:
        o.append(f"{g['day']}  {g['law']}" + (f" ({g['short_title']})" if g["short_title"] else ""))
        for x in g["items"]:
            o.append(f"   {'ALERT ' if x['watched_changed'] else '      '}{x['watched']}: {x['event']}"
                     + ("" if x["watched_changed"] else ", other parts only")
                     + (f" ({', '.join('(' + s + ')' for s in x['subsections_changed'][:6])})" if x["subsections_changed"] else ""))
            for n in x["notes"][:1]:
                if n["note"]:
                    o.append(f"         {n['note'][:200]}")
        o.append("")
    ed = sum(len(r.get("editions", [])) for r in recs)
    o.append(f"{len(groups)} laws; {sum(len(g['items']) for g in groups)} section changes; {ed} edition versions (not alerts).")
    return "\n".join(o)


CSS = """
:root{--bg:#0f1720;--panel:#16212c;--line:#2a3a4c;--ink:#e6eaef;--mute:#9aa6b5;--del:#ff6a55;--ins:#5fd1a4;--warn:#ffb35c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 "IBM Plex Sans",system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:32px 16px 64px}h1{font-size:24px;font-weight:600;margin:0 0 6px}
.sub{color:var(--mute);margin:0 0 24px}.stats{display:flex;gap:28px;flex-wrap:wrap;margin:0 0 28px}
.stats b{display:block;font-size:26px;font-weight:600}.stats span{font:11px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:1px;color:var(--mute);text-transform:uppercase}
.item{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:0 0 14px}
.item h2{font-size:17px;margin:0;font-weight:600;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.tag{font:12px "IBM Plex Mono",monospace;padding:2px 8px;border-radius:6px;border:1px solid var(--line);color:var(--mute)}
.tag.alert{color:#0f1720;background:var(--del);border-color:var(--del)}.tag.ed{color:var(--warn);border-color:var(--warn)}
.cited{color:var(--mute);font-size:13px;margin:4px 0 0}.chg{border-top:1px solid var(--line);margin-top:12px;padding-top:10px}
.chg .h{font-weight:600}.chg .m{color:var(--mute);font-size:13px}.note{color:#c9d1db;font-size:13px;margin:4px 0}
.diff{font:13px/1.6 "IBM Plex Mono",ui-monospace,monospace;background:#0b1219;border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:8px 0 0;overflow-wrap:anywhere;white-space:normal}
del{color:var(--del);background:rgba(255,106,85,.12);text-decoration:line-through}ins{color:var(--ins);background:rgba(95,209,164,.12);text-decoration:none}
.gap{color:#5d6b7a}a{color:#8fc1ff}details{margin-top:8px}summary{cursor:pointer;color:var(--mute)}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--mute);font-weight:500}.law{margin:0 0 18px}
"""


def _diff_html(segs):
    o = []
    for k, t in segs:
        e = html.escape(t)
        o.append({"eq": e, "gap": f'<span class="gap">… {e} …</span>' if t else '<span class="gap">…</span>', "del": f"<del>{e}</del>", "ins": f"<ins>{e}</ins>"}[k])
    return " ".join(o)


def _chg_html(c):
    h = [f'<div class="chg"><div class="h">{c["day"]} · {html.escape(c["law"])}' + (f' ({html.escape(c["short_title"])})' if c["short_title"] else "") + "</div>"]
    m = ("the words watched changed" if c["watched_changed"] else "another part of the section changed") + f" · {c['event']}"
    if c.get("subsections_changed"):
        m += " · changed: " + ", ".join(f"({html.escape(x)})" for x in c["subsections_changed"][:10])
    if c.get("moved_to"):
        m += f" · moved to {html.escape(c['moved_to'])}"
    h.append(f'<div class="m">{m}</div>')
    for n in c.get("notes", [])[:3]:
        if n["note"] or n["link"]:
            h.append(f'<div class="note">{html.escape(n["action"])}: {html.escape(n["note"][:400])}'
                     + (f' <a href="{html.escape(n["link"])}">record</a>' if n["link"] else "") + "</div>")
    if c.get("diff"):
        h.append(f'<div class="m">{c["words_struck"]} words struck, {c["words_inserted"]} inserted</div><div class="diff">{_diff_html(c["diff"])}</div>')
    h.append("</div>")
    return "".join(h)


def html_report(recs, since, today, title, subtitle="", groups=None, timing=None):
    al = [r for r in recs if r.get("alert")]
    nlaws = len({(c["day"], c["law"]) for r in recs for c in r.get("changes", []) if c["watched_changed"]})
    o = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         f"<title>{html.escape(title)}</title>",
         '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">',
         f"<style>{CSS}</style></head><body><main>",
         f"<h1>{html.escape(title)}</h1><p class=\"sub\">{html.escape(subtitle)} Watched from {iso(since)} to {iso(today)}. "
         "An alert is a law, in force in that window, that changed the words watched; Lean decides it. Edition changes are listed apart.</p>",
         '<div class="stats">' + "".join(f"<div><b>{v}</b><span>{k}</span></div>" for k, v in
                                         [("items watched", len(recs)), ("with an alert", len(al)), ("laws behind them", nlaws),
                                          ("edition notices", sum(1 for r in recs if not r.get("alert") and r.get("notices")))]) + "</div>"]
    if groups is not None:
        o.append("<h2 style=\"font-size:18px\">By law</h2>")
        for g in groups:
            o.append(f'<div class="item law"><h2>{g["day"]} · {html.escape(g["law"])}</h2><div class="cited">{html.escape(g["short_title"])}</div><table><tr><th>Section</th><th>What changed</th></tr>')
            for x in g["items"]:
                what = ("<span class=\"tag alert\">alert</span> " if x["watched_changed"] else "other parts only ") + html.escape(
                    ", ".join(f"({s})" for s in x["subsections_changed"][:10]))
                note = next((n["note"] for n in x["notes"] if n["note"]), "")
                o.append(f"<tr><td>{html.escape(x['watched'])}</td><td>{what}<div class=\"note\">{html.escape(note[:300])}</div></td></tr>")
            o.append("</table></div>")
    o.append('<h2 style="font-size:18px">Alerts</h2>' if al else "<p>No alerts.</p>")
    for r in al:
        o.append(f'<div class="item"><h2>{html.escape(r["watched"])} <span class="tag alert">{r["alerts"]} alert{"s" if r["alerts"] != 1 else ""}</span>'
                 f'<span class="tag">{html.escape(r["status"])}</span></h2>')
        if r["cited_as"] != [r["watched"]]:
            o.append(f'<div class="cited">Cited as {html.escape(", ".join(r["cited_as"]))}. Where the record has no text for a deeper designation, its parent is watched.</div>')
        for c in r["changes"]:
            if c["watched_changed"]:
                o.append(_chg_html(c))
        other = [c for c in r["changes"] if not c["watched_changed"]]
        if other or r["editions"]:
            o.append(f"<details><summary>{len(other)} law change(s) to other parts, {len(r['editions'])} edition version(s)</summary>")
            for c in other + r["editions"]:
                o.append(_chg_html(c))
            o.append("</details>")
        o.append("</div>")
    rest = [r for r in recs if not r.get("alert")]
    if rest:
        o.append(f'<h2 style="font-size:18px">No alert ({len(rest)})</h2><div class="item"><table><tr><th>Watched</th><th>Status</th><th>Since then</th></tr>')
        for r in rest:
            since_then = "; ".join([f"{c['day']} {c['law']} (other parts)" for c in r.get("changes", [])] +
                                   [f"{c['day']} edition" + (" — changed the words" if c["watched_changed"] else "") for c in r.get("editions", [])])
            o.append(f"<tr><td>{html.escape(r['watched'])}</td><td>{html.escape(r['status'])}</td><td>{html.escape(since_then) or '—'}</td></tr>")
        o.append("</table></div>")
        for r in rest:
            for c in r.get("editions", []):
                if c.get("diff"):
                    o.append(f'<details class="item"><summary>{html.escape(r["watched"])}: edition of {c["day"]} changed the words (not an alert{"; " + str(c["words_struck"] + c["words_inserted"]) + " words, review: may be a law the record could not date" if c.get("review") else ""})</summary>{_chg_html(c)}</details>')
    if timing:
        o.append(f'<p class="sub">Read and encoded in {timing["read_and_encode_s"]} s; Lean decided in {timing["lean_s"]} s ({html.escape(timing["lean"])}).</p>')
    o.append("</main></body></html>")
    return "\n".join(o)


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", help="watch list: one citation per line")
    g.add_argument("--doc", help="a document whose US Code citations are watched")
    ap.add_argument("--since", help="watch from this day (default for --doc: its date)")
    ap.add_argument("--today", help="read on this day (default: today)")
    ap.add_argument("--digest", nargs=2, metavar=("FROM", "TO"), help="every law change in force FROM..TO to the listed sections")
    ap.add_argument("--json"), ap.add_argument("--html"), ap.add_argument("--title")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--versions", default=VERSIONS), ap.add_argument("--git", default=GIT), ap.add_argument("--lean", default=LEAN_DIR)
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    t0 = time.time()
    vers = load_versions(a.versions)
    record_end = max(v.day for vs in vers.values() for v in vs)
    t_load = time.time() - t0
    doc_day = None
    if a.list:
        items = []
        for ln in open(a.list, encoding="utf-8"):
            ln = ln.split("#", 1)[0].strip()
            if ln:
                got = items_from_text(ln, vers, ranges=True)
                if not got:
                    m = re.match(r"(\d+)\s*/\s*([0-9A-Za-z\-]+)((?:\([A-Za-z0-9]+\))*)$", ln)
                    if m:
                        got = [{"title": int(m.group(1)), "section": m.group(2), "chain": re.findall(r"\(([A-Za-z0-9]+)\)", m.group(3)), "mentions": 1, "how": ln}]
                    else:
                        print(f"not a US Code citation: {ln}", file=sys.stderr)
                items += got
        seen, uniq = set(), []
        for it in items:
            k = (it["title"], it["section"], tuple(it["chain"]))
            if k not in seen:
                seen.add(k); uniq.append(it)
        items = uniq
        src = os.path.basename(a.list)
    else:
        text, doc_day = read_document(a.doc)
        items = items_from_text(text, vers, decided=doc_day)
        src = os.path.basename(a.doc)
    if a.digest:
        f0 = datetime.datetime.strptime(str(ymd(a.digest[0])), "%Y%m%d").date() - datetime.timedelta(days=1)
        since, today = int(f0.strftime("%Y%m%d")), ymd(a.digest[1])
    else:
        if a.since:
            since = ymd(a.since)
        elif doc_day:
            since = doc_day
        else:
            raise SystemExit("--since is needed (the document has no date)")
        today = ymd(a.today) if a.today else int(datetime.date.today().strftime("%Y%m%d"))
    recs, timing = watch(items, since, today, vers, a.git, a.lean)
    timing["load_versions_s"] = round(t_load, 3)
    timing["total_s"] = round(time.time() - t0, 3)
    title = a.title or (f"Digest for {src}" if a.digest else f"What has changed under {src}")
    groups = digest(recs) if a.digest else None
    if not a.quiet:
        print(digest_terminal(groups, recs, since, today) if a.digest else terminal(recs, since, today, title, record_end))
        print(f"\n[{len(items)} items; load {timing['load_versions_s']} s, read+encode {timing['read_and_encode_s']} s, Lean {timing['lean_s']} s, total {timing['total_s']} s]")
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"source": src, "since": iso(since), "today": iso(today), "record_end": iso(record_end), "timing": timing,
                       "items": recs, "digest": groups}, f, ensure_ascii=False, indent=1)
    if a.html:
        with open(a.html, "w", encoding="utf-8", newline="\n") as f:
            f.write(html_report(recs, since, today, title, f"Source: {src}. The US Code record runs to {iso(record_end)}.", groups, timing))
    return recs, timing


if __name__ == "__main__":
    main()
