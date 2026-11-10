"""Extract the operative structure of a US Code title from OLRC USLM XML, for the Lean checker.

    python tools/taxcode/parse_uslm.py <xml dir> <out dir>

Writes, for Title 26:
  t26.json      every provision (section down to subsubitem, plus the containers above sections): identifier,
                parent, kind, designation, status, heading, own text, explicit references (hrefs inside the
                provision's own text), and relative references written in words ("paragraph (2)",
                "subparagraphs (A) and (B) of subsection (c)") resolved to identifiers
and, for every title (to check references that leave Title 26):
  ids.tsv       identifier <TAB> status, for every structural element of every title

Only operative text is read: notes, source credits, tables of contents and quoted text (amendments that quote the
text they insert) are skipped. Nothing here judges whether a reference is right; the Lean checker does that.
"""
import json, re, sys
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "{http://xml.house.gov/schemas/uslm/1.0}"
LEVELS = ["section", "subsection", "paragraph", "subparagraph", "clause", "subclause", "item", "subitem", "subsubitem"]
CONTAINERS = ["title", "subtitle", "chapter", "subchapter", "part", "subpart", "division", "subdivision"]
STRUCT = set(LEVELS) | set(CONTAINERS)
SKIP = {"notes", "note", "sourceCredit", "quotedContent", "toc", "layout", "meta", "table"}
TEXT = {"content", "chapeau", "continuation", "p", "heading"}
REFMARK = "⟦REF⟧"
FNMARK = "†"


def expand_range(ident):
    """'/us/usc/t26/s921...927' -> the identifiers of §§921-927 (a repealed run of sections is one element in the XML);
    '/us/usc/t26/s54A...54F' -> §§54A-54F. Forms that cannot be enumerated give their two endpoints."""
    if "..." not in ident:
        return [ident]
    head, a = ident.rsplit("/s", 1)
    a, b = a.split("...", 1)
    ma, mb = re.fullmatch(r"(.*?)(\d+)", a), re.fullmatch(r"(.*?)(\d+)", b)
    if ma and mb and ma.group(1) == mb.group(1) and int(mb.group(2)) - int(ma.group(2)) < 500:
        return [f"{head}/s{ma.group(1)}{n}" for n in range(int(ma.group(2)), int(mb.group(2)) + 1)]
    ma, mb = re.fullmatch(r"(\d+)([A-Za-z]?)", a), re.fullmatch(r"(\d+)([A-Za-z])", b)
    if ma and mb and ma.group(1) == mb.group(1):
        lo = ord(ma.group(2)) if ma.group(2) else ord(mb.group(2)) - (ord(mb.group(2)) - (ord("A") if mb.group(2).isupper() else ord("a")))
        out = [f"{head}/s{ma.group(1)}"] if not ma.group(2) else []
        return out + [f"{head}/s{ma.group(1)}{chr(c)}" for c in range(lo, ord(mb.group(2)) + 1)]
    return [f"{head}/s{a}", f"{head}/s{b}"]


def heading_text(el):
    """A heading's words without the footnotes inside it ("33 So in original. There are two pars. (4).")."""
    parts = [el.text or ""]
    for c in el:
        if not (local(c.tag) == "note" or (local(c.tag) == "ref" and (c.get("class") or "") == "footnoteRef")):
            parts.append(heading_text(c))
        parts.append(c.tail or "")
    return "".join(parts)


def quoted_mask(text):
    """For each character, whether it lies inside curly quotation marks (quoted words: a substitution or a defined
    term, not a reference the provision itself makes)."""
    out, q = [], 0
    for ch in text:
        if ch == "“":
            q += 1
        out.append(q > 0)
        if ch == "”":
            q = max(0, q - 1)
    return out


def local(tag):
    return tag[len(NS):] if tag.startswith(NS) else tag


def own_text(el):
    """The element's own words (not its child provisions), with each <ref> replaced by a marker; and its hrefs."""
    parts, hrefs, footnotes = [], [], []

    def walk(e, inside):
        name = local(e.tag)
        if name in SKIP and not (name == "note" and (e.get("type") or "") == "footnote"):
            return
        if name == "ref" and (e.get("class") or "") == "footnoteRef" or (name == "sup" and (e.text or "").strip().isdigit()):
            # a footnote mark ("<ref class="footnoteRef">1</ref>", or a bare "<sup>1</sup>" for a note set out below)
            parts.append(FNMARK)
            if e.tail:
                parts.append(e.tail)
            return
        if name == "note" and (e.get("type") or "") == "footnote":
            footnotes.append(re.sub(r"\s+", " ", "".join(e.itertext())).strip())
            if e.tail:
                parts.append(e.tail)
            return
        if name == "ref":
            href = e.get("href") or ""
            rng = re.match(r"(.*/s)([0-9]+)([A-Za-z]*)–([0-9]+)[A-Za-z]*$", href)
            if rng and rng.group(2) == rng.group(4):
                href = rng.group(1) + rng.group(2) + rng.group(3)  # "29 U.S.C. 49–49n": a run of sections; check the first
            if href.startswith("/us/usc/"):
                hrefs.append(href)
            parts.append(REFMARK)
            if e.tail:
                parts.append(e.tail)
            return
        if inside and e.text:
            parts.append(e.text)
        for c in e:
            if local(c.tag) in STRUCT:
                continue
            walk(c, inside or local(c.tag) in TEXT)
        if inside and e.tail and name not in TEXT:
            parts.append(e.tail)
        elif e.tail and name in TEXT:
            parts.append(" ")

    for c in el:
        if local(c.tag) in TEXT - {"heading"}:
            walk(c, True)
            parts.append(" ")
        elif local(c.tag) not in STRUCT and local(c.tag) not in SKIP and local(c.tag) not in {"num", "heading"}:
            walk(c, False)
    text = re.sub(r"\s+", " ", "".join(parts)).strip()
    return text, hrefs, footnotes


# "paragraph (2)", "paragraphs (1) and (2)", "subparagraph (A)(ii)", "paragraphs (1) through (4)",
# optionally followed by "of subsection (b)" / "of paragraph (3)" / "of this section" / "of <REF>"
DESC = r"\(([0-9]+[A-Za-z]*|[A-Z]+|[a-z]+)\)"           # one designation, captured
DESN = r"\((?:[0-9]+[A-Za-z]*|[A-Z]+|[a-z]+)\)"         # the same, not captured
LEVEL_WORDS = {"subsection": "subsection", "subsections": "subsection", "paragraph": "paragraph", "paragraphs": "paragraph",
               "subparagraph": "subparagraph", "subparagraphs": "subparagraph", "clause": "clause", "clauses": "clause",
               "subclause": "subclause", "subclauses": "subclause"}
PHRASE = re.compile(r"(?<![A-Za-z])(?P<lead>such\s+|this\s+|the\s+preceding\s+|the\s+succeeding\s+)?"
                    r"(?P<word>[Ss]ubsections?|[Pp]aragraphs?|[Ss]ubparagraphs?|[Cc]lauses?|[Ss]ubclauses?)\s+"
                    r"(?P<group>(?:" + DESN + r")+(?:(?:,\s*|\s*,?\s*(?:and|or|and/or|through|to)\s+)(?:" + DESN + r")+)*)"
                    r"(?P<tail>\s+of\s+(?:(?P<thissuch>this|such)\s+(?:section|subsection|paragraph|subparagraph|clause)|"
                    r"(?P<oflevel>subsection|paragraph|subparagraph|clause)\s+(?P<ofpath>(?:\([^)]+\))+)|" + REFMARK + r"|[A-Za-z]))?"
                    r"(?P<thereof>\s+thereof)?")
GROUP = re.compile(r"(?:" + DESN + r")+")
ONE = re.compile(DESC)


KINDCLASS = {"subsection": r"[a-z]+", "paragraph": r"[0-9]+[A-Za-z]*", "subparagraph": r"[A-Z]+",
             "clause": r"[ivxlcdm]+", "subclause": r"[IVXLCDM]+", "item": r"[a-z]+", "subitem": r"[A-Z]+"}


def classify(des, start):
    """Position, in the level sequence beginning at `start`, of the first level a designation can belong to."""
    seq = LEVELS[LEVELS.index(start):]
    for k, lvl in enumerate(seq):
        pat = KINDCLASS.get(lvl)
        if pat and re.fullmatch(pat, des):
            # roman numerals also look like letters: "(i)" at the subsection level is a subsection
            return k
    return 0


def expand_list(start, chains):
    """'(h)(2), (h)(5), (i)(1), (2), (3)': a later item that starts deeper than `start` inherits the earlier part of
    the previous item."""
    out, prev = [], []
    for ds in chains:
        k = classify(ds[0], start) if out else 0
        full = (prev[:k] + ds) if k > 0 and len(prev) >= k else ds
        out.append(full)
        prev = full
    return out


def base_for(chain, level):
    li = LEVELS.index(level)
    for anc in reversed(chain):
        if anc["kind"] in LEVELS and LEVELS.index(anc["kind"]) == li - 1:
            return anc["id"]
    for anc in reversed(chain):
        if anc["kind"] in LEVELS and LEVELS.index(anc["kind"]) < li:
            return anc["id"]
    return None


def resolve(prov, chain, phrase_level, designators, of_level=None, of_path=None):
    """Identifier for a relative reference made in `prov` (whose ancestors-or-self are `chain`, outermost first)."""
    if of_level:  # "paragraph (2) of subsection (b)(1)": the named container, itself resolved relatively
        ob = resolve(prov, chain, of_level, re.findall(r"\(([^)]+)\)", of_path))
        return ob + "/" + "/".join(designators) if ob else None
    base = base_for(chain, phrase_level)
    return base + "/" + "/".join(designators) if base else None


HISTORICAL = re.compile(r"as so in effect|beginning before January 1, 19|before January 1, 19[0-9][0-9]|former |as in effect|as such sections? (?:was|were) in effect|as then in effect|as of (January|February|March|April|May|June|July|August|September|October|November|December) \d|before the date of the enactment|before its (amendment|repeal)|prior to (its )?(amendment|repeal)|as amended by|immediately before", re.I)
PAREN_WITHOUT = re.compile(r"(?:\(|,\s*|\s)(?:determined |applied )?without regard to\s*$|\(other than(?: in)?\s*$|\(as defined in\s*$|\(within the meaning of\s*$")


PREV = {}
for _seq in ("0123456789", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"):
    for _a, _b in zip(_seq, _seq[1:]):
        PREV[_b] = _a
PREV.update({"ii": "i", "iii": "ii", "iv": "iii", "v": "iv", "vi": "v", "II": "I", "III": "II", "IV": "III"})


def section_base(s):
    """'section 318(a)(2)' at the start of `s` -> its identifier, unless it belongs to another statute."""
    sm = re.match(r"\s*(?:of\s+)?section\s+" + SECNUM, s)
    if not sm:
        return None
    rest = s[sm.end():sm.end() + 160]
    rest = rest[:re.search(r"[.;—]|$", rest).start()]
    if FOREIGN_TAIL.match(rest.lstrip()) or re.match(r"\s+of\s+(?!this\s+title|the\s+Internal\s+Revenue\s+Code(?!\s+of\s+19))", rest):
        return None
    return "/".join([f"/us/usc/t26/s{sm.group('sec')}"] + re.findall(r"\(([^)]+)\)", sm.group("path")))


def relative_refs(prov, chain, text, secrefs):
    out = []
    quoted = quoted_mask(text)
    # "subparagraph (F), (J), (M), or (Q) of section 101(a)(15) of the Immigration and Nationality Act ... the
    # purpose specified in subparagraph (F), (J), (M), or (Q)": the second mention is the first one again
    named = {}
    for m in PHRASE.finditer(text):
        if quoted[m.start()]:
            continue  # inside quotation marks: words being substituted, not a reference this text makes
        if m.group("lead") and m.group("lead").strip().startswith("such"):
            continue  # "such paragraph" points back to something named earlier
        lvl = LEVEL_WORDS[m.group("word").lower()]
        sentence_start = max(text.rfind(". ", 0, m.start()), text.rfind("; ", 0, m.start()), text.rfind("—", 0, m.start()))
        if m.group("thereof"):
            # "clause (iii) thereof": a subdivision of a provision named earlier in the sentence; when that is a
            # section of this title ("section 1(f)(3) ... in subparagraph (A)(ii) thereof"), read it there
            prior = [r for r in secrefs if sentence_start < r["pos"] < m.start() and r["target"].startswith("/us/usc/t26/")]
            if not prior and sentence_start < 0 and len(chain) > 1:
                # "section 265 shall be applied— ... (4) by substituting ... in subsection (b)(6)(A)(ii) thereof"
                prior = [r for r in chain[-2].get("secrefs", []) if r["target"].startswith("/us/usc/t26/")]
            keep = LEVELS.index(lvl) - 1
            if prior and re.search(r"(?<![(\w])[0-9]+[A-Z]?\b(?![)])", re.sub(r"\([^)]*\)", "", text[prior[-1]["pos"] + len(prior[-1]["phrase"]):m.start()])):
                prior = []  # "sections 21 by reason of subsection (g) thereof, 24 by reason of subsections (d) ... thereof"
            if prior and not m.group("tail") and len(prior[-1]["target"].split("/")) - 5 >= keep:
                parts = prior[-1]["target"].split("/")[:5 + keep]
                for ds in expand_list(lvl, [ONE.findall(g.group(0)) for g in GROUP.finditer(m.group("group"))]):
                    if ds:
                        out.append({"phrase": m.group(0).strip()[:120], "target": "/".join(parts + ds), "alts": [],
                                    "range": False, "level": lvl, "des": ds,
                                    "historical": bool(HISTORICAL.search(text[max(0, m.start() - 160):m.end() + 160]))})
            continue
        before_s = text[max(0, sentence_start):m.start()]
        if re.search(r"(?:" + re.escape(REFMARK) + r"|\bof\s+(?:such\s+)?title\s+[0-9]+)[^.;—]{0,80}shall\s+be\s+applied\b", before_s) \
                or re.search(re.escape(REFMARK) + r"[^.;]{0,60}\((?:except|other\s+than)\s*$", before_s):
            continue  # "section 9504 of such title 5 shall be applied ... in subsections (a) and (b)": that section's
        if re.match(r"\s+of\s+such\b", text[m.end():]):
            continue  # "subparagraph (B) of paragraph (4) of such subsection (g)": of a provision named before
        key = (lvl, re.sub(r"\s+", " ", m.group("group")))
        of_level = of_path = None
        if m.group("tail"):
            if m.group("thissuch") == "such":
                continue
            if m.group("thissuch") == "this":
                pass
            elif m.group("oflevel"):
                of_level, of_path = m.group("oflevel"), m.group("ofpath")
                if LEVELS.index(of_level) >= LEVELS.index(lvl):
                    continue
            else:
                named[key] = section_base(text[m.end("group"):])
                continue  # "of section 401", "of such Act", "of title 31": a section reference, handled elsewhere
        ahead = text[m.end():m.end() + 160]
        cut = re.search(r"[.;—]", ahead)
        ahead = ahead[:cut.start()] if cut else ahead
        if re.search(r"\bof\s+(section|such\s+section|title|such\s+Act)", ahead) or FOREIGN_TAIL.search(ahead):
            sb = re.search(r"\bof\s+section\s", ahead)
            named[key] = section_base(ahead[sb.start():]) if sb else None
            continue  # "subparagraph (F), (J), (M), or (Q) of section 101(a)(15) of the Immigration ... Act"
        anaphor = []
        if key in named:
            if named[key] is None:
                continue  # the same designations named a moment ago as part of another statute
            anaphor.append(named[key])
        group = m.group("group")
        items = [ONE.findall(g.group(0)) for g in GROUP.finditer(group)]
        # "pursuant to subparagraph (C), or (ii) securities issued by ...": the last item is the second member of an
        # inline list "(i) ... (ii) ..." that the sentence is making, not a designation in the reference
        if len(items) > 1 and len(items[-1]) == 1 and items[-1][0] in PREV and re.match(r"\s+[a-z]", text[m.end("group"):]) \
                and re.search(r"(^|[\s—,;:])\(" + re.escape(PREV[items[-1][0]]) + r"\)\s+(?!of\b)[a-z]", text[:m.start()]):
            items = items[:-1]
        chains = expand_list(lvl, items)
        # "subparagraph (A) of paragraph (1) or (2) of subsection (d)": the container is itself in a named container
        outer = []
        if of_level:
            om = re.match(r"((?:\s*,?\s*(?:or|and)?\s*\([^)]+\))*)\s+of\s+(subsection|paragraph|subparagraph|clause)\s+((?:\([^)]+\))+)",
                          text[m.end():])
            if om and LEVELS.index(om.group(2)) < LEVELS.index(of_level):
                ob = resolve(prov, chain, om.group(2), re.findall(r"\(([^)]+)\)", om.group(3)))
                if ob:
                    for od in [re.findall(r"\(([^)]+)\)", of_path)] + [[x] for x in re.findall(r"\(([^)]+)\)", om.group(1))]:
                        outer.append(ob + "/" + "/".join(od))
        before = text[max(0, m.start() - 200):m.start()]
        # a container named just before or just after ("paragraphs (1) to (4), inclusive, of subsection (a) ...
        # paragraph (5)"; "subparagraph (B) or (A), as the case may be, of paragraph (1)") is another possible base
        containers = []
        for cm in re.finditer(r"of\s+(subsection|paragraph|subparagraph|clause)\s+((?:\([^)]+\))+)", before + " " + ahead):
            if LEVELS.index(cm.group(1)) < LEVELS.index(lvl):
                ob = resolve(prov, chain, cm.group(1), re.findall(r"\(([^)]+)\)", cm.group(2)))
                if ob:
                    containers.append(ob)
        # an earlier section reference in a parenthetical right before ("section 219(g)(5) (without regard to
        # subparagraph (A)(iii))") is an alternative base
        alt_bases = []
        if PAREN_WITHOUT.search(before):
            prior = [r for r in secrefs if r["pos"] < m.start() and m.start() - r["pos"] < 250]
            if prior:
                alt_bases.append(prior[-1]["target"])
            # "subsection (b)(4) of this section shall be applied without regard to subparagraphs (A), (H)":
            # the subdivision named last before the parenthetical
            pm = list(re.finditer(r"([Ss]ubsection|[Pp]aragraph|[Ss]ubparagraph|[Cc]lause)\s+((?:\([^)]+\))+)", before))
            if pm:
                last = pm[-1]
                ob = resolve(prov, chain, last.group(1).lower(), re.findall(r"\(([^)]+)\)", last.group(2)))
                if ob:
                    alt_bases.append(ob)
        # "section 318(a) shall be applied without regard to the employee trust exception in paragraph (2)(B)(i)":
        # a section cited earlier in the same sentence is another possible base
        prior = [r for r in secrefs if sentence_start < r["pos"] < m.start() and r["target"].startswith("/us/usc/t26/")]
        if m.group("thissuch") == "this" or (m.group("lead") or "").strip() == "this" or re.match(r"\s+of\s+this\b", text[m.end():]):
            prior = []  # "paragraph (8) of this subsection": the words themselves say where
        prior_bases = []
        if prior and not re.search(r"\bthis\s+(section|subsection)\b|\bof\s+this\b", text[prior[-1]["pos"]:m.start()]):
            prior_bases.append(prior[-1]["target"])
        alt_bases += anaphor
        historical = bool(HISTORICAL.search(text[max(0, m.start() - 160):m.end() + 160]))
        for ds in chains:
            if not ds:
                continue
            tgt = resolve(prov, chain, lvl, ds, of_level, of_path)
            if not tgt:
                continue
            alts = [c + "/" + "/".join(ds) for c in containers] + [o + "/" + "/".join(ds) for o in outer]
            for b in alt_bases:  # the deepest prefix of the earlier citation at which these designations can sit
                parts = b.split("/")
                for cut in range(len(parts), 4, -1):
                    alts.append("/".join(parts[:cut] + ds))
            # "section 3121(d), except that ... subparagraphs (B) and (C) of paragraph (3)": the whole path, container
            # included, under the section cited earlier in the sentence
            # (the level word fixes the depth: "paragraph (3)" sits directly under a subsection)
            full = (re.findall(r"\(([^)]+)\)", of_path) if of_path else []) + ds
            depth = 5 + LEVELS.index(of_level or lvl) - 1
            for b in prior_bases:
                parts = b.split("/")
                if len(parts) >= depth:
                    alts.append("/".join(parts[:depth] + full))
            out.append({"phrase": m.group(0).strip()[:120], "target": tgt, "alts": alts, "range": False,
                        "historical": historical, "level": lvl, "des": ds})
    return out


# "section 401(k)(2)(B)", "sections 401(a) and 403(b)", "section 1395w-101 of title 42"; skipped when followed by
# "of the Social Security Act", "of such Act", "of Public Law ...": references into Acts, not the Code
SECNUM = r"(?P<sec>[0-9]+[A-Za-z]*(?:[-\u2013][0-9]+[A-Za-z]*)?)(?P<path>(?:\((?:[0-9]+[A-Za-z]*|[A-Z]+|[a-z]+)\))*)"
SECTION = re.compile(r"(?<![A-Za-z])(?P<pre>(?:(?P<lvl>subsection|paragraph|subparagraph|clause|subclause)\s+(?P<lpath>(?:\((?:[0-9]+[A-Za-z]*|[A-Z]+|[a-z]+)\))+)\s+of\s+)?)"
                     r"[Ss]ections?\s+" + SECNUM + r"(?P<more>(?:(?:,\s*|\s*,?\s*(?:and|or|through)\s+)[0-9]+[A-Za-z]*(?:[-\u2013][0-9]+[A-Za-z]*)?(?:\((?:[0-9]+[A-Za-z]*|[A-Z]+|[a-z]+)\))*)*)"
                     r"(?P<after>\s+of\s+(?:title\s+(?P<title>[0-9]+[A-Za-z]?)|this\s+title|the\s+Internal\s+Revenue\s+Code(?:\s+of\s+1986)?|[A-Za-z]))?")
MORE = re.compile(r"([0-9]+[A-Za-z]*(?:[-\u2013][0-9]+[A-Za-z]*)?)((?:\((?:[0-9]+[A-Za-z]*|[A-Z]+|[a-z]+)\))*)")


# "of the Securities Exchange Act of 1934", "of the William M. (Mac) Thornberry National Defense Authorization Act",
# "of such Act", "of such code", "of the Internal Revenue Code of 1939": the section belongs to another statute
FOREIGN_TAIL = re.compile(r"\bof\s+(?:the\s+)?(?:[A-Z][\w’'.,-]*\s+|\([A-Z][\w’'.,-]*\)\s+|and\s+|of\s+|for\s+|on\s+|to\s+|[0-9]{4}\s*)*?"
                          r"(?:Act|Code of 19[0-9][0-9]|Regulations?)\b"
                          r"|\bof\s+(?:such|said|that|the\s+same)\s+(?:Act|[Cc]ode|title|law|Public Law|Revised Statutes)\b"
                          r"|\bof\s+the\s+Internal\s+Revenue\s+Code\s+of\s+19(?:39|54)\b"
                          r"|\bof\s+title\s+[0-9]+[A-Za-z]?\s*,\s+Code\s+of\s+Federal\s+Regulations")
MODEL = re.compile(r"model (regulation|act)", re.I)


def section_refs(text, context=""):
    """References to sections written in words. `text` has footnote marks blanked; `context` is the words of the
    provisions above (a chapeau naming "the model regulation" governs the list items below it)."""
    out = []
    quoted = quoted_mask(text)
    foreign_seen = set()   # "section 3748(a) of the Internal Revenue Code of 1939 ... section 3748(a)": the same one
    model = bool(MODEL.search(context))
    for m in SECTION.finditer(text):
        if quoted[m.start()]:
            continue  # inside quotation marks: words being substituted or quoted, not a reference this text makes
        if re.search(r"(such|said|that|the preceding|the same)\s+$", text[max(0, m.start() - 12):m.start()], re.I):
            continue  # "such section 1616(a)": the section named earlier, of whatever Act it belongs to
        if not m.group("path") and re.match(r"\.[0-9]", text[m.end("sec"):]):
            continue  # "section 500.20(s)(1) of title 29, Code of Federal Regulations", "section 8.1(a) of the Farm Credit Act"
        if re.match(r"\s+of\s+the\s+Internal\s+Revenue\s+Code\s+of\s+(1939|1954)", text[m.end() - len(m.group("after") or ""):]):
            foreign_seen.add(m.group("sec") + m.group("path"))
            continue
        if re.match(r"\s*,\s*Code\s+of\s+Federal\s+Regulations", text[m.end():]):
            continue  # "section 661 of title 49, Code of Federal Regulations": a regulation, not the Code
        if re.match(r"\s+thereof\b", text[m.end() - len(m.group("after") or ""):]):
            continue  # "section 5109 thereof": a section of the Act named before
        if text[m.end():m.end() + 12].lstrip(" (").startswith(REFMARK):
            continue  # "section 9901(6) <link>": the hyperlink names the statute, which is not Title 26
        # a list ("Sections 13(b)(3), 26(b)(2)(C), ... and the last sentence of section 362(b)(3) of such Code") can
        # name its statute a long way after its first item
        tail = text[m.end():m.end() + (320 if m.group("more") or m.group(0).startswith("Sections") else 160)]
        stop = re.search(r"[.;—]", tail)
        tail = tail[:stop.start()] if stop else tail
        if not m.group("after") and (FOREIGN_TAIL.search(tail) or re.match(r"\s*\(?" + re.escape(REFMARK), tail)):
            foreign_seen.add(m.group("sec") + m.group("path"))
            continue  # "section 3(a)(4) or (5) of the Securities and Exchange Act of 1934"
        if m.group("sec") + m.group("path") in foreign_seen:
            continue
        if model or MODEL.search(text[max(0, m.start() - 400):m.end() + 200]):
            continue  # sections of the NAIC model regulation or model Act, not of the Code
        after = m.group("after") or ""
        title = "26"
        tail_title = re.match(r"[^.;]{0,140}?\bof\s+title\s+([0-9]+[A-Za-z]?)\b", text[m.end():])
        comma_title = re.match(r"[^.;]{0,140}?,\s*of\s+title\s+([0-9]+[A-Za-z]?)\b", text[m.end():])
        if not after and tail_title and (m.group("more") or comma_title or m.group(0).startswith(("sections", "Sections"))):
            title = tail_title.group(1)  # "section 310, or paragraph (1) or (3) of section 351(a), of title 37"
            after = " of title " + title
        if after:
            if m.group("title"):
                title = m.group("title")
            elif re.match(r"\s+of\s+(this\s+title|the\s+Internal)", after):
                title = "26"
            elif not after.startswith(" of title"):
                continue  # "of the Social Security Act", "of such Act", "of Public Law"
        more = MORE.findall(m.group("more") or "")
        if not re.match(r"[Ss]ections", m.group(0).split()[0] if m.group(0).split() else "") and not m.group(0).lstrip().startswith(("subsection", "paragraph", "subparagraph", "clause", "subclause")):
            more = [x for x in more if x[1]]  # singular "section 167(k), 100 percent": only items with designations
        items = [(m.group("sec"), m.group("path"))] + more
        for sec, path in items:
            parts = [f"/us/usc/t{title}/s{sec}"] + re.findall(r"\(([^)]+)\)", path)
            if m.group("lvl") and len(items) == 1:
                parts += re.findall(r"\(([^)]+)\)", m.group("lpath"))
            out.append({"phrase": m.group(0).strip()[:120], "target": "/".join(parts), "alts": [], "range": False,
                        "pos": m.start(),
                        "historical": bool(HISTORICAL.search(text[max(0, m.start() - 160):m.end() + 160]))})
    return out


def parse_title(path, collect):
    """Walk a title; call collect(element, kind, chain) for every structural element outside skipped parts."""
    tree = ET.parse(path)
    root = tree.getroot()

    def walk(el, chain, quoting=False):
        before = []  # the children of el that come before c (their words are read only when needed)
        for c in el:
            name = local(c.tag)
            if name in SKIP:
                continue
            num = c.find(NS + "num")
            if name in STRUCT and num is not None and "".join(num.itertext()).lstrip().startswith("“") \
                    and (quoting or re.search(r"(:|reading|follows)\s*$", re.sub(r"\s+", " ", "".join("".join(b.itertext()) for b in before)).strip())):
                # “(2) Brother-sister controlled group ...”: a provision quoted in the text ("as if it read as
                # follows:", "shall be treated as reading:"), marked up as structure but not part of the Code's own
                # tree; its unquoted contents (an OLRC nesting slip) still are. An opening quotation mark without such
                # an introduction is a stray ("“(C)" in §408A(e)(1)(C), which is in force).
                walk(c, chain, True)
                before.append(c)
                continue
            before.append(c)
            if name in STRUCT and c.get("identifier"):
                node = {"id": c.get("identifier"), "kind": name, "xid": c.get("id")}
                collect(c, name, chain, node)
                walk(c, chain + [node])
            else:
                walk(c, chain)

    walk(root, [])


def postprocess(provs):
    """Readings that need the whole title: subdivisions of the citing provision itself (flush text after a list),
    designations written inline in the text ("(A) a minister ... or (B) a practitioner"), and the same designations
    one level up or down when the level word looks wrong ("subclause (ii)" where only clause (ii) exists)."""
    ids = {p["id"] for p in provs}
    kids = {}
    for p in provs:
        if p.get("parent"):
            kids.setdefault(p["parent"], []).append(p["id"])
    byid = {p["id"]: p for p in provs}
    for p in provs:
        par = byid.get(p.get("parent") or "")
        # the provision this one's chapeau says is being applied or adapted ("Paragraph (2) shall be applied— ... (ii)
        # by substituting ... in subparagraph (C)"; "rules similar to the rules of paragraphs (4), (5), and (6) of
        # subsection (c) shall apply ..., except that— (A) ... in paragraphs (4), (5), and (6)"), and the provisions
        # the chapeau names ("described in clause (ii), (iii), ... of subparagraph (A) ... — (ii) ... clause (iii)")
        applied, named_above = [], []
        if par and p["kind"] in LEVELS:
            ptext = par["text"].replace(FNMARK, " ")
            prefs = [r for r in par.get("rel", []) + par.get("secrefs", []) if r["target"].startswith("/us/usc/t26/")]
            for r in prefs:  # the subject of "shall be applied", "shall apply", "by substituting"
                i = ptext.find(r["phrase"])
                if i >= 0 and re.match(r"(?:\s*\([^)]*\))?(?:\s*\([^)]*\))?\s*(?:,[^,—]{0,60},\s*)?(?:shall\s+be\s+applied|shall\s+apply|by\s+substituting)",
                                       ptext[i + len(r["phrase"]):]):
                    applied.append(r["target"])
            named_above = [r["target"] for r in prefs]
        # "5 U.S.C. 9503 shall be applied— (1) ... in subsection (a)(6)", "section 9505 of such title shall be
        # applied—": the subdivisions refer into another title's section
        foreign_applied = bool(par) and re.search(r"(?:" + re.escape(REFMARK) + r"|\bof\s+(?:such\s+)?title(?:\s+[0-9]+)?)[^.;—]{0,80}shall\s+be\s+applied\s*—\s*$",
                                                  par["text"].replace(FNMARK, " ").strip())
        for r in p.get("rel", []):
            if r["target"] in ids or any(a in ids for a in r["alts"]):
                continue
            if foreign_applied:
                r["inline"] = True  # read in the other title's section, which this checker does not hold
                continue
            ds = r.get("des") or []
            depth = 5 + LEVELS.index(r["level"]) - 1  # the level word fixes the depth
            for b in applied:
                parts = b.split("/")
                if len(parts) >= depth:
                    r["alts"].append("/".join(parts[:depth] + ds))
            for t in named_above:  # same designations at the same level
                if ds and t.split("/")[-len(ds):] == ds and len(t.split("/")) == depth + len(ds):
                    r["alts"].append(t)
            if any(a in ids for a in r["alts"]):
                continue
            # flush text: the designations under one of the citing provision's own subdivisions, at any depth
            stack = list(kids.get(p["id"], []))
            while stack:
                k = stack.pop()
                cand = k + "/" + "/".join(ds)
                if cand in ids:
                    r["alts"].append(cand)
                    break
                stack.extend(kids.get(k, []))
            # inline designations in the citing provision's own words, or its parent's
            last = ds[-1] if ds else ""
            texts = p["text"] + " " + (byid[p["parent"]]["text"] if p.get("parent") in byid else "")
            if last and re.search(r"(^|[\s—,;:])\(" + re.escape(last) + r"\)\s+(?!of\b)", texts) and len(ds) == 1:
                r["inline"] = True
            # wrong level word: the same designations resolved from another level
            if not r.get("inline") and r["target"] not in ids:
                for other in LEVELS[1:6]:
                    if other == r["level"]:
                        continue
                    base = base_for([{"id": a, "kind": byid[a]["kind"]} for a in ancestors(p["id"], byid)], other)
                    if base and base + "/" + "/".join(ds) in ids:
                        r["levelSlip"] = {"word": r["level"], "fits": other, "target": base + "/" + "/".join(ds)}
                        break
    for p in provs:
        # a section of another statute: no such section exists in Title 26 (even repealed), and the sentence names
        # another Act, title or code ("title XVIII of the Social Security Act ... under section 1818")
        keep = []
        for r in p.get("secrefs", []):
            sec = "/".join(r["target"].split("/")[:5])
            if r["target"].startswith("/us/usc/t26/") and sec not in ids:
                start = max(p["text"].rfind(". ", 0, r["pos"]), 0)
                if re.search(r"\bAct\b|\btitle\s+[0-9]+|\btitle\s+[IVXLC]+\b|Regulations|Code of 19[0-9][0-9]|Revised Statutes", p["text"][start:r["pos"] + 200]):
                    continue
            keep.append(r)
        p["secrefs"] = keep
        # a designation written inline in the words of the cited provision itself, which has no subdivisions
        # ("paragraph (1) of section 3301" where section 3301 reads "... equal to (1) 6.2 percent ... (2) ...")
        for r in p.get("rel", []) + p["secrefs"]:
            if r["target"] in ids or any(a in ids for a in r["alts"]):
                continue
            par, _, last = r["target"].rpartition("/")
            if par in byid and not kids.get(par) and re.search(r"(^|[\s—,;:])\(" + re.escape(last) + r"\)\s+(?!of\b)", byid[par]["text"]):
                r["inline"] = True
    # "Any reference in this subsection to section 922, 923, or 927 shall be treated as a reference to such section as
    # in effect before its repeal": every such reference under the declaring provision is to the law as it was
    scope = r"(?:this\s+(?P<kind>section|subsection|paragraph|subparagraph|clause|subclause)|[a-z]+\s+\([^)]+\))(?:\s*\([^)]*\))*"
    decl = re.compile(r"[Rr]eferences?\s+(?:in\s+" + scope + r"\s+to\s+(?P<list>.{1,200}?)|to\s+(?P<list2>.{1,200}?)\s+in\s+"
                      + scope.replace("?P<kind>", "?P<kind2>") + r")\s+shall\s+be\s+(?:treated|deemed)\s+as\s+(?:a\s+)?references?\s+to\s+"
                      r"(?:such|the)\s+[^.]{0,200}?(?:as\s+(?:so\s+)?in\s+effect|before\s+(?:its|their)\s+repeal)"
                      # "For purposes of this section, any reference to section 179A shall be treated as a reference to
                      # such section as in effect immediately before its repeal."
                      r"|[Ff]or\s+purposes\s+of\s+this\s+(?P<kind3>section|subsection|paragraph|subparagraph|clause),\s+any\s+reference\s+to\s+"
                      r"(?P<list3>.{1,200}?)\s+shall\s+be\s+(?:treated|deemed)\s+as\s+(?:a\s+)?references?\s+to\s+(?:such|the)\s+[^.]{0,200}?"
                      r"(?:as\s+(?:so\s+)?in\s+effect|before\s+(?:its|their)\s+repeal)")
    following = re.compile(r"the\s+following\s+provisions\s+\(as\s+in\s+effect")
    for p in provs:
        text = p["text"].replace(FNMARK, " ")
        scopes = []
        for dm in decl.finditer(text):
            root = p.get("parent") or p["id"]
            kind = dm.group("kind") or dm.group("kind2") or dm.group("kind3")
            if kind:
                for a in reversed(ancestors(p["id"], byid)):
                    if byid[a]["kind"] == kind:
                        root = a
                        break
            chain = [{"id": a, "kind": byid[a]["kind"]} for a in ancestors(p["id"], byid)]
            lst = dm.group("list") or dm.group("list2") or dm.group("list3")
            # "section 922, 923, or 927", "section 951(a)(1)(C) and subsection (a)(3)": the section numbers ...
            targets = []
            for sm in re.finditer(r"\bsections?\s+((?:[0-9]+[A-Za-z]*(?:[-–][0-9]+[A-Za-z]*)?(?:\([^)]+\))*(?:\s*,?\s*(?:and|or)\s+|,\s*)?)+)", lst):
                for num, path in re.findall(r"([0-9]+[A-Za-z]*(?:[-–][0-9]+[A-Za-z]*)?)((?:\([^)]+\))*)", sm.group(1)):
                    targets.append("/".join([f"/us/usc/t26/s{num}"] + re.findall(r"\(([^)]+)\)", path)))
            # ... and the subdivisions of this section named in words
            for lm in PHRASE.finditer(lst):
                lvl = LEVEL_WORDS[lm.group("word").lower()]
                for g in GROUP.finditer(lm.group("group")):
                    t = resolve(p, chain, lvl, ONE.findall(g.group(0)))
                    if t:
                        targets.append(t)
            scopes.append((root, targets))
        if following.search(text):
            scopes.append((p["id"], None))
        for root, targets in scopes:
            stack = [root]
            while stack:
                q = byid[stack.pop()]
                stack.extend(kids.get(q["id"], []))
                for r in q.get("rel", []) + q.get("secrefs", []):
                    if targets is None or any(r["target"] == t or r["target"].startswith(t + "/") for t in targets):
                        r["historical"] = True


def ancestors(pid, byid):
    out = []
    while pid in byid:
        out.append(pid)
        pid = byid[pid].get("parent")
    return list(reversed(out))


def main(xml_dir, out_dir):
    xml_dir, out_dir = Path(xml_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # 1. every identifier in every title (kept if already written for this release point)
    with (open(out_dir / "ids.tsv", "w", encoding="utf-8") if not (out_dir / "ids.tsv").exists() else open(__import__("os").devnull, "w")) as ids:
        for f in (sorted(xml_dir.glob("usc*.xml")) if ids.name != __import__("os").devnull else []):
            n, seen, members = [0], set(), []

            def col(el, kind, chain, node):
                ids.write(f"{node['id']}\t{el.get('status') or 'in-force'}\n")
                seen.add(node["id"])
                if "..." in node["id"]:  # "s921...927": each member of a repealed run of sections, unless it exists
                    members.extend((i, el.get("status") or "in-force") for i in expand_range(node["id"]))
                n[0] += 1

            parse_title(f, col)
            for i, st in members:
                if i not in seen:
                    ids.write(f"{i}\t{st}\n")
                    seen.add(i)
            print(f.name, n[0], flush=True)
    # 2. Title 26 in full
    provs = []
    words = {}

    def col26(el, kind, chain, node):
        num = el.find(NS + "num")
        head = el.find(NS + "heading")
        text, hrefs, fns = own_text(el) if kind in LEVELS else ("", [], [])
        node.update({
            "parent": chain[-1]["id"] if chain else None,
            # the parent element itself (two paragraphs "(4)" enacted side by side share one identifier, and each
            # has its own subparagraph (A))
            "parentElement": chain[-1].get("xid") if chain else None,
            "num": (num.get("value") if num is not None else None),
            "status": el.get("status") or "in-force",
            "heading": re.sub(r"\s+", " ", heading_text(head)).strip() if head is not None else "",
            "text": text,
            "refs": hrefs,
            "footnotes": fns,
        })
        # in force: the element and every element above it (not every element with the parent's identifier: the
        # repealed "[CHAPTER 38—REPEALED]" and the new chapter 38 share one identifier)
        node["chainActive"] = node["status"] == "in-force" and all(a.get("status", "in-force") == "in-force" for a in chain)
        words[node["id"]] = text
        # footnote marks are blanked (same length, so positions agree with `text`) before looking for references
        scan = text.replace(FNMARK, " ")
        context = " ".join(words.get(a["id"], "") for a in chain)
        secs = section_refs(scan, context) if kind in LEVELS else []
        node.update({
            "rel": relative_refs(node, chain + [node], scan, secs) if kind in LEVELS else [],
            "secrefs": secs,
        })
        provs.append(node)

    parse_title(xml_dir / "usc26.xml", col26)
    # each member of a repealed run of sections ("§§ 921 to 927") as a provision of its own, unless a provision with
    # that identifier exists elsewhere ("§§ 4220 to 4225" repealed in one chapter, § 4221 in force in another)
    real = {p["id"] for p in provs}
    for p in list(provs):
        if "..." in p["id"]:
            for i in expand_range(p["id"]):
                if i not in real:
                    real.add(i)
                    provs.append({**p, "id": i, "num": i.rsplit("/s", 1)[1], "rel": [], "secrefs": [], "refs": [], "text": ""})
    postprocess(provs)
    active = {}
    for p in provs:  # an identifier is in force if any element carrying it is
        active[p["id"]] = active.get(p["id"], False) or p.get("chainActive", False)
    for p in provs:
        p["active"] = active[p["id"]]
        p.pop("chainActive", None)
    (out_dir / "t26.json").write_text(json.dumps({"release": "119-138", "provisions": provs}), encoding="utf-8")
    print("t26 provisions", len(provs), "explicit refs", sum(len(p["refs"]) for p in provs),
          "relative refs", sum(len(p["rel"]) for p in provs),
          "section refs in words", sum(len(p["secrefs"]) for p in provs))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
