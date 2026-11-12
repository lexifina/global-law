"""Cross-references inside the US Code, read from every version of every section.

    python tools/caselaw/usc_xrefs.py scan <usc git dir> <versions.tsv> <out dir> [workers]

For each distinct (section, text) in the record it writes, to <out>/scan-*.pkl:
  * whether the section is live (a file with text whose heading is not "Repealed", "Transferred", "Reserved", ...);
  * its designation paths ("b.2.A"), read from the bullet tree: a line "- (x) ..." indented 2n spaces is at depth n,
    and a line that starts with several designations, "(c)(1)(A)", is printed at the depth of its last one. A
    designation whose line reads "Repealed", "Omitted", "Reserved" or "Transferred" is a dead path. Designations
    written inside a line ("(A) ... and (B) ...") are soft paths: children of the line's designation and of its
    parent, so a reference to them is never called dangling;
  * duplicate designations: the same designation twice among the live children of one parent;
  * the explicit references it makes (see `refs_in_line`).

A reference is (kind, target section path, designation path). Kinds:
  sec   "section 924(c)(1) of title 18", "section 401 of this title", "section 1 of the Internal Revenue Code of 1986",
        also lists and ranges ("sections 1 through 5 of this title": each end);
  bare  "section 2244" with no "of ..." after it, in a title enacted as positive law on that day (and title 26), where
        a bare section number names a section of the same title;
  usc   an enacted parenthetical "(42 U.S.C. 1320a-7a(m))" (not a bracketed editorial one, not "note");
  sub   "subsection (c)", "paragraph (2) of subsection (a)", "subsection (b)(1) of this section": a path from the top
        of the same section (only when the outermost level is a subsection, or "of this section" is written);
  thissub "paragraph (2) of this subsection": a path under the line's own subsection.
Not read: "of such section", "of such Act", "of that section", "of the X Act" (another law), "chapter N" (the record
has no chapters), bare "paragraph (2)" (relative to wherever the sentence sits), references "as in effect" on some
earlier day and "former section ...", and anything inside square brackets (editorial).
"""
import collections, os, pickle, re, subprocess, sys, threading
from multiprocessing import Pool

DESLINE = re.compile(r"^( *)- (\[?)((?:\([A-Za-z0-9]{1,6}\))+)(\]?)(.*)$")
DEAD_DES = re.compile(r"^\s*\]?\s*(?:Repealed|Omitted|Reserved|Transferred|Redesignated|Struck)\b")
DEAD_HEAD = re.compile(r"^# \d+[A-Za-z]? U\.S\.C\. § [^ ]+\s+(?:Repealed|Transferred|Reserved|Vacant|Expired|Omitted|Renumbered)\b|"
                       r"^# \d+[A-Za-z]? U\.S\.C\. § [^ ]+?\.\s*(?:Repealed|Transferred|Reserved|Vacant|Expired|Omitted|Renumbered)\b")
INLINE = re.compile(r"(?:^|(?<=[\s—:;,]))((?:\([A-Za-z0-9]{1,4}\))+)(?=[\s—])")
LEVEL_BEFORE = re.compile(r"(?:sub)?(?:sections?|paragraphs?|subparagraphs?|clauses?|subclauses?|items?|subitems?)\s*$", re.I)

# positive-law titles: from this day a bare "section 123" in the title names a section of the same title
POSITIVE = {1: 19470730, 3: 19480625, 4: 19470730, 5: 19660906, 9: 19470730, 10: 19560810, 11: 19781106, 13: 19540831,
            14: 19490804, 17: 19470730, 18: 19480625, 23: 19580827, 26: 19540816, 28: 19480625, 31: 19820913,
            32: 19560810, 35: 19520719, 36: 19980812, 37: 19620907, 38: 19580902, 39: 19700812, 40: 20020821,
            41: 20110104, 44: 19681019, 46: 20061006, 49: 19940705, 51: 20101218, 54: 20141219}

D = r"\((?:[A-Za-z]{1,5}|\d{1,3}[A-Za-z]{0,2})\)"
DS = rf"{D}(?: ?{D})*"
SECNUM = r"\d+[A-Za-z]*(?:[-–]\d+[A-Za-z]*)?"
JOIN = r"(?:\s*,\s*(?:and\s+|or\s+)?|\s+(?:and|or|through)\s+)"
LEVELW = r"(?:subsections?|paragraphs?|subparagraphs?|clauses?|subclauses?|items?|subitems?)"
START = re.compile(rf"(?<![A-Za-z])(?:[Ss]ections?|[Ss]ub[Ss]ections?|{LEVELW}|Paragraphs?|Subparagraphs?|Clauses?|Subclauses?)\s+(?=\(|\d)")
LEVELGRP = re.compile(rf"({LEVELW})\s+({DS}(?:{JOIN}{DS})*)", re.I)
SECGRP = re.compile(rf"([Ss]ections?)\s+({SECNUM}(?:{DS})?(?:{JOIN}(?:section\s+)?{SECNUM}(?:{DS})?)*)(?![\w.]?\d)")
ITEM_D = re.compile(rf"({JOIN})?({DS})")
ITEM_S = re.compile(rf"({JOIN})?(?:section\s+)?({SECNUM})((?:{D})*)")
OF = re.compile(r"\s+of\s+(?:such\s+)?")
TAIL = re.compile(r"\s+of\s+(?:(this section)|(this subsection)|(this title)|title (\d{1,2})(?![\d])(?!,? Code of Federal Regulations|,? of the Code of Federal Regulations| of the (?!United States Code))(?:,? United States Code)?|"
                  r"(?:the )?Internal Revenue Code of (?:1986|1954)|(.))")
AFTER_SKIP = re.compile(r"^[\s,()]*(?:as (?:in effect|so in effect|it (?:existed|read|was in effect)|(?:such|that|those|the|it) [\w ]{0,30}?(?:was|were|existed|read)\b)|"
                        r"as (?:of|on) the (?:day|date) before|(?:immediately )?(?:before|prior to) (?:the (?:date|day|amendment|enactment|effective)|its|their)\b)", re.I)
HISTORIC = re.compile(r"(?:prior to|before) (?:its |their |the )?repeal\b|as (?:in effect|so in effect) (?:on|before|immediately|prior)|as (?:such|that|those|the|it) (?:\w+ ){0,2}(?:is|are|was|were) in effect (?:on|before|immediately|prior)|^\s*\[[^\]]*U\.S\.C\.")
USC_PAREN = re.compile(rf"\((\d{{1,2}}) U\.S\.C\. ({SECNUM})((?:{D})*)(?:\s+(note|et seq\.?))?")


def kind_of(w):
    w = w.lower().rstrip("s")
    return {"subsection": 0, "paragraph": 1, "subparagraph": 2, "clause": 3, "subclause": 4, "item": 5, "subitem": 6}.get(w, 9)


def split_ds(s):
    return re.findall(r"\(([A-Za-z0-9]+)\)", s)


def dclass(d):
    return "n" if d[0].isdigit() else ("l" if d.islower() else "u")


def items(rx, s, sec=False):
    """List items of a group: [(designations or (num, designations))]; a range gives its two ends. A list of
    designations stops where one is of another kind than the first ("subsection (k) and (B) has ..." is not a list)."""
    out = []
    for m in rx.finditer(s):
        if sec:
            out.append((m.group(2).replace("–", "-"), tuple(split_ds(m.group(3) or ""))))
        else:
            ds = tuple(split_ds(m.group(2)))
            if out and first_class(ds[0]) != first_class(out[0][0]):
                # "(j)(2)(A)(i), (ii)": a later item at a deeper level takes the first item's prefix
                f0 = out[0]
                k = next((k for k in range(1, len(f0)) if first_class(f0[k]) == first_class(ds[0])), None)
                if k is None and dclass(ds[0]) != dclass(f0[0]):
                    k = next((k for k in range(1, len(f0)) if dclass(f0[k]) == dclass(ds[0])), None)
                    if k is None:
                        break
                if k is not None:
                    ds = f0[:k] + ds
            out.append(ds)
    return out


ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}


def roman(s):
    s = s.lower()
    if not s or any(c not in ROMAN for c in s):
        return None
    v = 0
    for i, c in enumerate(s):
        x = ROMAN[c]
        v += -x if i + 1 < len(s) and ROMAN[s[i + 1]] > x else x
    return v if 0 < v < 60 else None


def interps(d):
    """The ways a designation can be read: (class, value)."""
    out = []
    m = re.fullmatch(r"(\d+)([A-Za-z]*)", d)
    if m:
        return [("n", (int(m.group(1)), m.group(2)))]
    cl = "l" if d.islower() else "u"
    r = roman(d)
    if r is not None:
        out.append(("r" + cl, (r, "")))
    if d.isalpha() and d == d[0] * len(d):
        out.append(("a" + cl, (len(d), ord(d[0].lower()))))
    return out


def _next(c, v):
    if c[0] == "a":
        n, o = v
        return (n + 1, ord("a")) if o == ord("z") else (n, o + 1)
    return (v[0] + 1, "")


def follows(prev, cls, d, exact):
    """Whether designation `d` can come after `prev`, read in the class `cls` its siblings established; returns the
    class of `d` or None."""
    for c1, v1 in interps(prev):
        if cls and c1 != cls:
            continue
        for c2, v2 in interps(d):
            if c1 != c2:
                continue
            if exact:
                if v2 == _next(c1, v1) or (c1 == "n" and v2[0] == v1[0] and v2[1] > v1[1]) or                         (c1 == "n" and v1[1] and v2 == (v1[0] + 1, "")):
                    return c1
            elif v2 > v1:
                if c1[0] == "a" and v2[0] != v1[0]:
                    if v2 == _next(c1, v1):
                        return c1
                    continue
                gap = (v2[1] - v1[1]) if c1[0] == "a" else (v2[0] - v1[0])
                if gap <= 6:
                    return c1
    return None


FIRST = {"a": "al", "1": "n", "A": "au", "i": "rl", "I": "ru", "aa": "al", "AA": "au"}


def first_class(d):
    if d in FIRST:
        return FIRST[d]
    its = interps(d)
    if not its:
        return "?"
    if len(d) == 1 and d.isalpha():
        return "al" if d.islower() else "au"
    return its[0][0]


def place(stack, start, d0):
    """Where a line's first designation goes, and its class. The record sometimes prints a designation at the wrong
    indent (a clause "(ii)" at the left margin, a subsection "(ee)" six levels deep). The depths where it is the exact
    next designation after the sibling there (in the class those siblings established), or a first designation under
    the deepest, are its candidates: the printed depth if it is one, else the candidate nearest the printed depth.
    With no candidate, the printed depth, which allows a gap (a sibling repealed without a trace)."""
    def fits(k, exact):
        if k < len(stack):
            return follows(stack[k][0], stack[k][2], d0, exact)
        return FIRST.get(d0)
    cands = []
    for k in range(len(stack) + 1):
        c = fits(k, True)
        if c:
            cands.append((abs(k - start), k, c))
    if cands:
        _, k, c = min(cands)
        return k, c
    c = fits(start, False)
    if c:
        return start, c
    return start, (stack[start][2] if start < len(stack) else first_class(d0))


def tree(lines):
    """Walk the designated lines: yields (line no, line match, path after the line, [(parent id, designation, node
    id)]) for designated lines and (line no, None, path, []) for others."""
    stack = []  # [(designation, node id, class)]
    nid = 0
    for ln, line in enumerate(lines):
        if ln == 0 and line.startswith("# "):
            continue
        m = DESLINE.match(line)
        new = []
        if m:
            level = len(m.group(1)) // 2
            ds = split_ds(m.group(3))
            start, cls = place(stack, max(0, min(level - len(ds) + 1, len(stack))), ds[0])
            stack = stack[:start]
            for j, d in enumerate(ds):
                parent = stack[-1][1] if stack else 0
                nid += 1
                c = cls if j == 0 else first_class(d)
                new.append((parent, d, nid))
                stack.append((d, nid, c))
        yield ln, m, tuple(x[0] for x in stack), new


def in_brackets(text, i):
    return text.rfind("[", 0, i) > text.rfind("]", 0, i)


def refs_in_line(text, here, title, day, self_path):
    """References in one line of a section. `here`: the line's designation path; `title`: the section's title.
    Yields (kind, target path, designation path tuple, start, end)."""
    out = []
    pos = 0
    while True:
        m = START.search(text, pos)
        if not m:
            break
        st = m.start()
        groups = []  # inner to outer: ("L", kind, [ds...]) or ("S", [(num, ds)...])
        i = st
        ok = True
        while True:
            g = LEVELGRP.match(text, i)
            if g:
                groups.append(("L", kind_of(g.group(1)), items(ITEM_D, g.group(2))))
                i = g.end()
            else:
                g = SECGRP.match(text, i)
                if g:
                    groups.append(("S", items(ITEM_S, g.group(2), sec=True)))
                    i = g.end()
                else:
                    ok = False
                    break
            if groups[-1][0] == "S":
                break
            o = OF.match(text, i)
            if o and (LEVELGRP.match(text, o.end()) or SECGRP.match(text, o.end())):
                if o.group(0).strip() != "of":  # "of such subsection": names something mentioned earlier
                    ok = False
                    break
                i = o.end()
                continue
            break
        if not ok or not groups:
            pos = m.end()
            continue
        pos = max(i, m.end())
        tail = TAIL.match(text, i)
        tkind, ttitle = None, None
        if tail:
            if tail.group(1):
                tkind = "self"
            elif tail.group(2):
                tkind = "thissub"
            elif tail.group(3):
                tkind, ttitle = "title", title
            elif tail.group(4):
                tkind, ttitle = "title", int(tail.group(4))
            elif tail.group(5) is not None:
                tkind = "foreign"
            else:
                tkind, ttitle = "title", 26
            end = tail.end() if tkind != "foreign" else i
        else:
            end = i
        if tkind == "foreign":
            continue
        if re.match(r"\s*,?\s*(?:thereof|therein|of (?:such|that|the same) (?:section|subsection|title|Act)|respectively,? of (?:such|that|the)\b|,? District of Columbia Code|of the District of Columbia Code)", text[end:end + 40]):
            continue
        pre = text[max(0, st - 12):st]
        if re.search(r"(?:former|old|repealed|prior|such|said|that)\s+$", pre, re.I) or in_brackets(text, st):
            continue
        if AFTER_SKIP.match(text[end:end + 90]) or HISTORIC.search(text[end:end + 150]):
            continue
        # designation path pieces, outer to inner
        lv = [g for g in groups if g[0] == "L"]
        sg = groups[-1] if groups[-1][0] == "S" else None
        chains = [()]
        for g in reversed(lv):
            chains = [c + ds for c in chains for ds in g[2]][:40]
        if sg:
            if tkind == "title":
                kind, t = "sec", ttitle
            elif tkind is None:
                # a list of bare numbers may end in "of title 49" or "of the X Act" further on in the sentence
                rest = re.split(r"[.;](?:\s|$)", text[end:end + 300], maxsplit=1)[0]
                if re.search(r"\bof (?:title \d|such title|the [A-Z][\w ,.'-]*?(?:Act|Code)\b)|respectively,? of\b", rest):
                    continue
                if title in POSITIVE and day >= POSITIVE[title]:
                    kind, t = "bare", title
                else:
                    continue
            else:
                continue
            for j, (num, ds) in enumerate(sg[1][:40]):
                for c in (chains if j == 0 else [()]):  # "(9) of section 402(c) and section 402(f)"
                    out.append((kind, f"title-{t}/{num}.md", ds + c, st, end))
        else:
            outer = lv[-1][1] if lv else 9
            if tkind == "thissub":
                if outer == 0 or not here or not re.fullmatch(r"[a-z]{1,3}", here[0]):
                    continue
                for c in chains:
                    out.append(("thissub", self_path, (here[0],) + c, st, end))
            elif tkind == "self" or (tkind is None and outer == 0):
                for c in chains:
                    out.append(("sub", self_path, c, st, end))
    for m in USC_PAREN.finditer(text):
        if m.group(4) and m.group(4).startswith("note"):
            continue
        if in_brackets(text, m.start()) or AFTER_SKIP.match(text[m.end():m.end() + 90]) or (
                HISTORIC.search(text[m.end():m.end() + 150])):
            continue
        out.append(("usc", f"title-{int(m.group(1))}/{m.group(2).replace('–', '-')}.md", tuple(split_ds(m.group(3) or "")),
                    m.start(), m.end()))
    return out


def analyse(path, text, day):
    """One version of one section: live, hard paths, soft paths, dead paths, duplicates, references."""
    title = int(path.split("/")[0].split("-")[1])
    lines = text.split("\n")
    dh = DEAD_HEAD.match(lines[0]) if lines else None
    live = bool(text.strip()) and not dh
    why = "" if live else (re.search(r"(Repealed|Transferred|Reserved|Vacant|Expired|Omitted|Renumbered)", lines[0]).group(1)
                           if dh else "empty")
    hard, soft, dead = set(), set(), set()
    kids = collections.defaultdict(list)  # parent node id -> [(designation, live)]
    idpath = {0: ()}
    refs = []
    lin = []  # per designated line: (its designations, live?, designations written inside it)
    for ln, m, here, new in tree(lines):
        body = lines[ln]
        lds = tuple(d for _, d, _ in new)
        if m:
            rest = m.group(5)
            isdead = bool(DEAD_DES.match(rest)) or (m.group(2) == "[" and m.group(4) == "" and "Repealed" in rest[:40])
            for j, (parent, d, nid) in enumerate(new):
                last = j == len(new) - 1
                kids[parent].append((d, not (isdead and last)))
                idpath[nid] = idpath.get(parent, ()) + (d,)
                (dead if isdead and last else hard).add(idpath[nid])
            body = rest
        seen = []  # inline designations earlier in the line: "(4) ... so long as (A) ..." may be (4)(A)
        for im in INLINE.finditer(body):
            if LEVEL_BEFORE.search(body[max(0, im.start() - 16):im.start()]):
                continue
            ch = tuple(split_ds(im.group(1)))
            for k in range(1, len(ch) + 1):
                soft.add(here + ch[:k])
                if here:
                    soft.add(here[:-1] + ch[:k])
                for p in seen[-8:]:
                    if first_class(p[0]) != first_class(ch[0]):
                        soft.add(here + p + ch[:k])
            seen.append(ch)
        inl = tuple(d for c in seen for d in c)
        if lds or inl:
            lin.append((lds, not (m and (bool(DEAD_DES.match(m.group(5))))), inl))
        for r in refs_in_line(body, here, title, day, path):
            refs.append((r[0], r[1], r[2], here, body[max(0, r[3] - 160):r[4] + 80], ln))
    dups = []
    for parent, ch in kids.items():
        c = collections.Counter(d for d, lv in ch if lv)
        for d, k in c.items():
            if k > 1:
                dups.append((idpath.get(parent, ()), d, k))
    return live, hard, soft - hard, dead - hard, dups, refs, why, lin


def _work(job):
    out = []
    for path, blob, day, text in job:
        out.append((path, blob, analyse(path, text, day)))
    return out


def read_blobs(git, blobs):
    pr = subprocess.Popen(["git", "--git-dir", git, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def feed():
        for b in blobs:
            pr.stdin.write((b + "\n").encode())
        pr.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    for b in blobs:
        size = int(pr.stdout.readline().split()[2])
        t = pr.stdout.read(size).decode("utf-8", "replace")
        pr.stdout.read(1)
        yield b, t
    pr.wait()


def scan(git, versions, out, workers=4):
    os.makedirs(out, exist_ok=True)
    first = {}
    for l in open(versions, encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if f[5] and (f[0], f[5]) not in first:
            first[(f[0], f[5])] = int(f[4])
    byblob = collections.defaultdict(list)
    for (p, b), d in first.items():
        byblob[b].append((p, d))
    blobs = sorted(byblob)
    print("distinct (section, text)", len(first), "blobs", len(blobs), flush=True)

    def jobs():
        batch, size = [], 0
        for b, t in read_blobs(git, blobs):
            for p, d in byblob[b]:
                batch.append((p, b, d, t))
                size += len(t)
            if size > 4_000_000:
                yield batch
                batch, size = [], 0
        if batch:
            yield batch
    res = {}
    with Pool(int(workers)) as pool:
        for k, part in enumerate(pool.imap_unordered(_work, jobs(), chunksize=1)):
            for p, b, a in part:
                res[(p, b)] = a
            if k % 20 == 0:
                print("done", len(res), flush=True)
    with open(os.path.join(out, "scan.pkl"), "wb") as f:
        pickle.dump(res, f, protocol=pickle.HIGHEST_PROTOCOL)
    print("scanned", len(res), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "scan":
        scan(*sys.argv[2:])


# ---------------------------------------------------------------------------------------------------------------------
# build: the Lean input. One block per target section (its dated versions: live, and its paths that some reference
# names), then one row per (referring section, target, path): the referring section's dated versions, each saying
# whether its text makes the reference.

START_DAY = 19950104
# the first day each title's text is in the record (the record's first edition of the title; a title made later starts
# then): a reference into a title is judged only from this day.
COVER = {7: 19960116, 28: 19960116, 39: 19960116, 6: 20021125, 34: 20180112, 51: 20120103, 52: 20150105, 54: 20150105}


def load_versions(versions):
    vers = collections.defaultdict(list)  # path -> [(day, law?, label, blob, short title, order)]
    for i, l in enumerate(open(versions, encoding="utf-8")):
        f = l.rstrip("\n").split("\t")
        vers[f[0]].append((int(f[4]), f[2] == "law", f[3], f[5], f[6] if len(f) > 6 else "", i))
    for p in vers:
        vers[p].sort(key=lambda v: (v[0], v[5]))
    low = collections.Counter(p.lower() for p in vers)
    LOWER[id(vers)] = {p.lower(): p for p in vers if low[p.lower()] == 1}
    return vers


LOWER = {}  # id(versions dict) -> lower-cased path -> path (when unique)


def pstr(p):
    return ".".join(p)


def linear(path, lin):
    """Whether a designation path can be read off the section's lines in order, ignoring indentation: each designation
    on a line (or written inside one) after the previous one's line, before the line that starts the previous one's
    next sibling. The record's indents are sometimes wrong; this finds (a)(10)(A)(i) where a misprinted indent has
    hung the clause elsewhere, and still misses (a)(1)(A) after (A) became (1)."""
    pos = -1
    for i, d in enumerate(path):
        lo = 0 if i == 0 else pos
        hi = len(lin)
        if i > 0:
            prev = path[i - 1]
            for j in range(pos + 1, len(lin)):
                if any(follows(prev, None, x, True) and dclass(x) == dclass(prev) for x in lin[j][0][:1]):
                    hi = j
                    break
        found = None
        for j in range(lo, hi):
            ds, live, inl = lin[j]
            if j == pos:
                # the previous designation's own line: "(c)(1)" carries (1) after (c); or written inside it
                k = ds.index(path[i - 1]) if path[i - 1] in ds else len(ds)
                ok = d in ds[k + 1:] or d in inl
            else:
                ok = (d in ds and live) or d in inl
            if ok:
                found = j
                break
        if found is None:
            return False
        pos = found
    return True


def norm_ref(tgt, path, vers):
    """A number written with a dash, "sections 541–555 of title 40", is a range (its two ends) when the record has no
    section of that name but has its first end."""
    if tgt not in vers and tgt.lower() in LOWER.get(id(vers), {}):
        return [(LOWER[id(vers)][tgt.lower()], path)]  # "654A" written for the section the record files as 654a
    if tgt not in vers:
        m = re.fullmatch(r"(title-\d+/)(\d+)-(\d+)\.md", tgt)
        if m and int(m.group(2)) < int(m.group(3)) and f"{m.group(1)}{m.group(2)}.md" in vers:
            return [(f"{m.group(1)}{m.group(2)}.md", path), (f"{m.group(1)}{m.group(3)}.md", path)]
    return [(tgt, path)]


def build(versions, out, shards=4):
    vers = load_versions(versions)
    scan_ = pickle.load(open(os.path.join(out, "scan.pkl"), "rb"))
    titles = {int(p.split("/")[0][6:]) for p in vers}
    keys = collections.defaultdict(dict)  # source -> {(target, path): kinds}
    vkeys = {}  # (source, blob) -> set of (target, path) its text makes
    for (p, b), a in scan_.items():
        ks = set()
        for kind, tgt, path, here, ctx, ln in a[5]:
            for k in norm_ref(tgt, path, vers):
                keys[p].setdefault(k, set()).add(kind)
                ks.add(k)
        vkeys[(p, b)] = ks
    wanted = collections.defaultdict(set)  # target -> paths named
    rows = []
    for src, ks in keys.items():
        for (tgt, path), kinds in ks.items():
            t = int(tgt.split("/")[0][6:])
            if t not in titles:
                continue
            if kinds == {"bare"} and tgt not in vers:
                continue  # a bare number that is no section of this title in the record: another title or Act
            wanted[tgt].add(path)
            rows.append((tgt, src, path, kinds))
    rows.sort()
    print("rows", len(rows), "targets", len(wanted), flush=True)
    meta = open(os.path.join(out, "rows.tsv"), "w", encoding="utf-8", newline="\n")
    fs = [open(os.path.join(out, f"lean_in_{k}.tsv"), "w", encoding="utf-8", newline="\n") for k in range(int(shards))]
    last, rid, fo = None, 0, None
    tlist = sorted(wanted)
    shard_of = {t: i * int(shards) // len(tlist) for i, t in enumerate(tlist)}
    for tgt, src, path, kinds in rows:
        if tgt != last:
            fo = fs[shard_of[tgt]]
            vs = []
            keep = wanted[tgt]
            for day, law, label, blob, short, _ in vers.get(tgt, []):
                if blob and (tgt, blob) in scan_:
                    live, hard, soft, dead = scan_[(tgt, blob)][:4]
                    have = (hard | soft) & keep
                    lin = scan_[(tgt, blob)][7]
                    have |= {x for x in keep - have - dead if x and linear(x, lin)}
                    ps = sorted(pstr(x) for x in have)
                    vs.append(f"{day},{1 if live else 0}," + " ".join(ps))
                else:
                    vs.append(f"{day},0,")
            fo.write("T\t" + tgt + "\t" + "\t".join(vs) + "\n")
            last = tgt
        t = int(tgt.split("/")[0][6:])
        s = int(src.split("/")[0][6:])
        frm = max(START_DAY, COVER.get(t, START_DAY), COVER.get(s, START_DAY))
        sv = []
        for day, law, label, blob, short, _ in vers[src]:
            mk = bool(blob) and (tgt, path) in vkeys.get((src, blob), ())
            sv.append(f"{day},{1 if mk else 0}")
        fo.write(f"R\t{rid}\t{frm}\t{pstr(path)}\t" + ";".join(sv) + "\n")
        meta.write(f"{rid}\t{src}\t{tgt}\t{pstr(path)}\t{','.join(sorted(kinds))}\n")
        rid += 1
    for f in fs:
        f.close()
    meta.close()
    print("written", rid, flush=True)


if __name__ == "__main__" and sys.argv[1] == "build":
    build(*sys.argv[2:])
