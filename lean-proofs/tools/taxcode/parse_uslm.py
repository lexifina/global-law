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


def local(tag):
    return tag[len(NS):] if tag.startswith(NS) else tag


def own_text(el):
    """The element's own words (not its child provisions), with each <ref> replaced by a marker; and its hrefs."""
    parts, hrefs, footnotes = [], [], []

    def walk(e, inside):
        name = local(e.tag)
        if name in SKIP and not (name == "note" and (e.get("type") or "") == "footnote"):
            return
        if name == "ref" and (e.get("class") or "") == "footnoteRef":
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
                    r"(?P<word>subsections?|paragraphs?|subparagraphs?|clauses?|subclauses?)\s+"
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


HISTORICAL = re.compile(r"as so in effect|beginning before January 1, 19|before January 1, 19[0-9][0-9]|former |as in effect|as such section was in effect|as then in effect|as of (January|February|March|April|May|June|July|August|September|October|November|December) \d|before the date of the enactment|before its (amendment|repeal)|prior to (its )?(amendment|repeal)|as amended by|immediately before", re.I)
PAREN_WITHOUT = re.compile(r"(?:\(|,\s*|\s)(?:determined |applied )?without regard to\s*$|\(other than(?: in)?\s*$|\(as defined in\s*$|\(within the meaning of\s*$")


def relative_refs(prov, chain, text, secrefs):
    out = []
    for m in PHRASE.finditer(text):
        if m.group("lead") and m.group("lead").strip().startswith("such"):
            continue  # "such paragraph" points back to something named earlier
        if m.group("thereof"):
            continue  # "clause (iii) thereof": a subdivision of a provision named earlier in the sentence
        lvl = LEVEL_WORDS[m.group("word")]
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
                continue  # "of section 401", "of such Act", "of title 31": a section reference, handled elsewhere
        ahead = text[m.end():m.end() + 160]
        cut = re.search(r"[.;—]", ahead)
        ahead = ahead[:cut.start()] if cut else ahead
        if re.search(r"\bof\s+(section|such\s+section|title|such\s+Act)", ahead) or re.search(r"\bof\s+(?:the\s+)?(?:[A-Z][\w’'.,-]*\s+|and\s+|of\s+|for\s+|on\s+|to\s+|[0-9]{4}\s*)*?(?:Act|Code of 19[0-9][0-9]|Regulations?)\b", ahead):
            continue  # "subparagraph (F), (J), (M), or (Q) of section 101(a)(15) of the Immigration ... Act"
        group = m.group("group")
        chains = expand_list(lvl, [ONE.findall(g.group(0)) for g in GROUP.finditer(group)])
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
        historical = bool(HISTORICAL.search(text[max(0, m.start() - 160):m.end() + 160]))
        for ds in chains:
            if not ds:
                continue
            tgt = resolve(prov, chain, lvl, ds, of_level, of_path)
            if not tgt:
                continue
            alts = [c + "/" + "/".join(ds) for c in containers]
            for b in alt_bases:  # the deepest prefix of the earlier citation at which these designations can sit
                parts = b.split("/")
                for cut in range(len(parts), 4, -1):
                    alts.append("/".join(parts[:cut] + ds))
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


def section_refs(text):
    out = []
    for m in SECTION.finditer(text):
        if re.search(r"(such|said|that|the preceding|the same)\s+$", text[max(0, m.start() - 12):m.start()], re.I):
            continue  # "such section 1616(a)": the section named earlier, of whatever Act it belongs to
        if re.match(r"\s+of\s+the\s+Internal\s+Revenue\s+Code\s+of\s+(1939|1954)", text[m.end() - len(m.group("after") or ""):]):
            continue
        if text[m.end():m.end() + 3].lstrip(" (").startswith(REFMARK):
            continue  # "section 9901(6) <link>": the hyperlink names the statute, which is not Title 26
        tail = text[m.end():m.end() + 140]
        stop = re.search(r"[.;\u2014]", tail)
        tail = tail[:stop.start()] if stop else tail
        if not m.group("after") and re.search(r"\bof\s+(?:the\s+)?(?:[A-Z][\w’'.,-]*\s+|and\s+|of\s+|for\s+|on\s+|to\s+|[0-9]{4}\s*)*?(?:Act|Code of 19[0-9][0-9]|Regulations?)\b", tail):
            continue  # "section 3(a)(4) or (5) of the Securities and Exchange Act of 1934"
        if re.search(r"model (regulation|act)", text[max(0, m.start() - 400):m.end() + 200], re.I):
            continue  # sections of the NAIC model regulation or model Act, not of the Code
        after = m.group("after") or ""
        title = "26"
        tail_title = re.match(r"[^.;]{0,140}?\bof\s+title\s+([0-9]+[A-Za-z]?)\b", text[m.end():])
        if not after and tail_title and m.group("more"):
            title = tail_title.group(1)
            after = " of title " + title
        if after:
            if m.group("title"):
                title = m.group("title")
            elif re.match(r"\s+of\s+(this\s+title|the\s+Internal)", after):
                title = "26"
            else:
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

    def walk(el, chain):
        for c in el:
            name = local(c.tag)
            if name in SKIP:
                continue
            if name in STRUCT and c.get("identifier"):
                node = {"id": c.get("identifier"), "kind": name}
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
        for r in p.get("rel", []):
            if r["target"] in ids or any(a in ids for a in r["alts"]):
                continue
            ds = r.get("des") or []
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
            n = [0]

            def col(el, kind, chain, node):
                ids.write(f"{node['id']}\t{el.get('status') or 'in-force'}\n")
                n[0] += 1

            parse_title(f, col)
            print(f.name, n[0], flush=True)
    # 2. Title 26 in full
    provs = []

    def col26(el, kind, chain, node):
        num = el.find(NS + "num")
        head = el.find(NS + "heading")
        text, hrefs, fns = own_text(el) if kind in LEVELS else ("", [], [])
        node.update({
            "parent": chain[-1]["id"] if chain else None,
            "num": (num.get("value") if num is not None else None),
            "status": el.get("status") or "in-force",
            "heading": re.sub(r"\s+", " ", "".join(head.itertext())).strip() if head is not None else "",
            "text": text,
            "refs": hrefs,
            "footnotes": fns,
        })
        secs = section_refs(text) if kind in LEVELS else []
        node.update({
            "rel": relative_refs(node, chain + [node], text, secs) if kind in LEVELS else [],
            "secrefs": secs,
        })
        provs.append(node)

    parse_title(xml_dir / "usc26.xml", col26)
    postprocess(provs)
    (out_dir / "t26.json").write_text(json.dumps({"release": "119-138", "provisions": provs}), encoding="utf-8")
    print("t26 provisions", len(provs), "explicit refs", sum(len(p["refs"]) for p in provs),
          "relative refs", sum(len(p["rel"]) for p in provs),
          "section refs in words", sum(len(p["secrefs"]) for p in provs))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
