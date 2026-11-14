"""Print a provision of Title 26 from the OLRC release point (119-138), for writing rules from the statute.

    python -I tools/taxcode/loopholes/statute.py 1 g          # §1(g)
    python -I tools/taxcode/loopholes/statute.py 643 a 3      # §643(a)(3)
"""
import re, sys
import xml.etree.ElementTree as ET

XML = r"~\Documents\tax-formalization-data\xml\usc26.xml"
NS = "{http://xml.house.gov/schemas/uslm/1.0}"
SKIP = {"notes", "note", "sourceCredit", "toc", "meta"}


def text(e, depth=0, out=None):
    out = [] if out is None else out
    name = e.tag[len(NS):] if e.tag.startswith(NS) else e.tag
    if name in SKIP:
        return out
    if name in ("num", "heading", "chapeau", "content", "continuation", "p") :
        s = re.sub(r"\s+", " ", "".join(e.itertext())).strip()
        if s:
            out.append(("  " * depth) + s)
        return out
    d = depth + (1 if name in ("subsection", "paragraph", "subparagraph", "clause", "subclause", "item") else 0)
    for c in e:
        text(c, d, out)
    return out


def main():
    ident = "/us/usc/t26/s" + sys.argv[1] + "".join("/" + p for p in sys.argv[2:])
    for ev, el in ET.iterparse(XML, events=("end",)):
        if el.get("identifier") == ident:
            sys.stdout.reconfigure(encoding="utf-8")
            print("\n".join(text(el)))
            return
        if el.tag.endswith("section"):
            el.clear()
    print("not found", ident)


main()
