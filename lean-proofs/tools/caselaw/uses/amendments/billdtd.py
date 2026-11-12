"""Translate a bill in GPO's bill DTD (BILLS-*.xml) into USLM-shaped XML, so the same instruction parser
(uslm_laws.parse_law) reads bills and public laws alike.

    enum -> num(value), header -> heading, text -> content (quoted blocks moved inside it, as USLM prints them),
    quote -> quotedText, quoted-block -> quotedContent, external-xref usc -> ref href=/us/usc/tT/sS/a/1,
    continuation-text -> continuation. Every content outside quotes whose own words carry an amending verb gets an
    empty <amendingAction/> marker (USLM tags these; the bill DTD does not).
"""
from __future__ import annotations

import re

from lxml import etree

NS = "http://schemas.gpo.gov/xml/uslm"
Q = f"{{{NS}}}"
LEVELS = {"section", "subsection", "paragraph", "subparagraph", "clause", "subclause", "item", "subitem",
          "subsubitem", "division", "title", "subtitle", "part", "subpart", "chapter", "subchapter"}
VERB = re.compile(r"\b(striking|inserting|adding|redesignating|amended to read|is repealed|are repealed|amending)\b")


def _href(text: str, cite: str) -> str | None:
    """'21 U.S.C. 841(b)(1)' (the words) or 'usc/21/841' (the attribute) -> '/us/usc/t21/s841/b/1'."""
    m = re.search(r"(\d+)\s+U\.S\.C\.\s+([0-9A-Za-z]+(?:[-–][0-9A-Za-z]+)?)((?:\([^)]+\))*)", text or "")
    if m:
        t, s, d = m.group(1), m.group(2).replace("–", "-"), m.group(3)
    else:
        m = re.match(r"usc/(\d+)/([0-9A-Za-z-]+)", cite or "")
        if not m:
            return None
        t, s, d = m.group(1), m.group(2), ""
    return f"/us/usc/t{t}/s{s}" + "".join("/" + x for x in re.findall(r"\(([^)]+)\)", d))


def _conv(el, quoted: bool):
    """Convert one bill-DTD element (and its subtree) to a USLM element."""
    tag = el.tag if isinstance(el.tag, str) else ""
    if tag in LEVELS:
        out = etree.Element(Q + tag)
        pending_content = None
        for ch in el:
            ct = ch.tag if isinstance(ch.tag, str) else ""
            if ct == "enum":
                n = etree.SubElement(out, Q + "num")
                n.text = "".join(ch.itertext())
                n.set("value", re.sub(r"[().\s§]", "", n.text))
            elif ct == "header":
                h = etree.SubElement(out, Q + "heading")
                h.text = "".join(ch.itertext())
            elif ct == "text":
                pending_content = _inline(ch, Q + "content", quoted)
                out.append(pending_content)
            elif ct == "quoted-block":
                qc = _quoted_block(ch)
                if pending_content is None:
                    pending_content = etree.SubElement(out, Q + "content")
                pending_content.append(qc)
            elif ct == "after-quoted-block":
                if pending_content is not None and len(pending_content):
                    last = pending_content[-1]
                    last.tail = (last.tail or "") + "".join(ch.itertext())
            elif ct == "continuation-text":
                out.append(_inline(ch, Q + "continuation", quoted))
            elif ct in LEVELS:
                out.append(_conv(ch, quoted))
                pending_content = None
        return out
    return None


def _quoted_block(el):
    qc = etree.Element(Q + "quotedContent")
    for ch in el:
        ct = ch.tag if isinstance(ch.tag, str) else ""
        if ct in LEVELS:
            qc.append(_conv(ch, True))
        elif ct == "text":
            qc.append(_inline(ch, Q + "content", True))
    return qc


def _inline(el, newtag, quoted):
    out = etree.Element(newtag)
    out.text = el.text
    for ch in el:
        ct = ch.tag if isinstance(ch.tag, str) else ""
        if ct == "quote":
            n = etree.SubElement(out, Q + "quotedText")
            n.text = "".join(ch.itertext())
        elif ct == "external-xref" and (ch.get("legal-doc") or "").startswith("usc") and not quoted:
            n = etree.SubElement(out, Q + "ref")
            words = "".join(ch.itertext())
            h = _href(words, ch.get("parsable-cite") or "")
            if (ch.get("legal-doc") or "") == "usc-chapter":
                m = re.match(r"usc-chapter/(\d+)/(\w+)", ch.get("parsable-cite") or "")
                h = f"/us/usc/t{m.group(1)}/ch{m.group(2)}" if m else None
            if h:
                n.set("href", h)
            n.text = words
        elif ct == "quoted-block":
            out.append(_quoted_block(ch))
        else:
            n = etree.SubElement(out, Q + "inline")
            n.text = "".join(ch.itertext())
        out[-1].tail = ch.tail
    if not quoted:
        plain = (out.text or "") + "".join(
            ("" if c.tag in (Q + "quotedText", Q + "quotedContent") else "".join(c.itertext())) + (c.tail or "") for c in out)
        if VERB.search(plain):
            out.insert(0, etree.Element(Q + "amendingAction", type="amend"))
            out[0].tail = out.text
            out.text = None
    return out


def translate(xml: bytes) -> bytes:
    root = etree.fromstring(xml, parser=etree.XMLParser(resolve_entities=False, no_network=True, recover=True))
    body = root.find(".//legis-body")
    law = etree.Element(Q + "pLaw", nsmap={None: NS})
    main = etree.SubElement(law, Q + "main")
    if body is not None:
        for ch in body:
            c = _conv(ch, False)
            if c is not None:
                main.append(c)
    return etree.tostring(law, encoding="utf-8")
