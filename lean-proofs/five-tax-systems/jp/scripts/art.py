"""Print articles of an e-Gov law XML.
usage: python3 -I art.py <xml> <ArticleNum...>          (e.g. 28 83_2)
       python3 -I art.py <xml> --table <substring of AppdxTableTitle>
       python3 -I art.py <xml> --grep <regex>            (main provision articles whose text matches)
       python3 -I art.py <xml> --suppl <regex>           (supplementary provisions whose text matches)
"""
import sys, re
import xml.etree.ElementTree as ET

path = sys.argv[1]
root = ET.parse(path).getroot()
WS = re.compile(r"\s*[\r\n]\s*")


def text(e):
    return WS.sub("", "".join(e.itertext())).strip()


def show(e, ind=0):
    tag = e.tag
    pad = "  " * ind
    if tag == "Article":
        cap = e.find("ArticleCaption")
        tit = e.find("ArticleTitle")
        print(pad + (text(cap) if cap is not None else "") + " " + (text(tit) if tit is not None else "") + "  [Num=" + str(e.get("Num")) + "]")
        for c in e:
            if c.tag == "Paragraph":
                show(c, ind + 1)
    elif tag == "Paragraph":
        num = e.find("ParagraphNum")
        s = e.find("ParagraphSentence")
        n = text(num) if num is not None and text(num) else "1"
        print(pad + "[" + n + "] " + (text(s) if s is not None else ""))
        for c in e:
            if c.tag.startswith("Item") or c.tag in ("TableStruct", "List"):
                show(c, ind + 1)
    elif tag.startswith("Item") or tag.startswith("Subitem"):
        t = None
        s = None
        for c in e:
            if c.tag.endswith("Title"):
                t = text(c)
            if c.tag.endswith("Sentence"):
                s = " / ".join(text(x) for x in c)
        print(pad + (t or "") + " " + (s or ""))
        for c in e:
            if c.tag.startswith("Subitem") or c.tag in ("TableStruct", "List"):
                show(c, ind + 1)
    elif tag == "TableStruct":
        for row in e.iter("TableRow"):
            print(pad + " | ".join(text(c) for c in row))
    else:
        print(pad + text(e))


args = sys.argv[2:]
if args and args[0] == "--table":
    for t in root.iter("AppdxTable"):
        tt = t.find("AppdxTableTitle")
        title = text(tt) if tt is not None else ""
        if args[1] in title:
            print("== " + title)
            for row in t.iter("TableRow"):
                print(" | ".join(text(c) for c in row))
elif args and args[0] == "--grep":
    rx = re.compile(args[1])
    main = root.find(".//MainProvision")
    for a in main.iter("Article"):
        if rx.search(text(a)):
            cap = a.find("ArticleCaption")
            print(a.get("Num"), text(cap) if cap is not None else "")
elif args and args[0] == "--fusoku":
    # articles of the ORIGINAL supplementary provision (no AmendLawNum), by Num
    for sp in root.iter("SupplProvision"):
        if sp.get("AmendLawNum"):
            continue
        for num in args[1:]:
            for a in sp.iter("Article"):
                if a.get("Num") == num:
                    print("### 附則")
                    show(a)
                    print()
elif args and args[0] == "--suppl":
    rx = re.compile(args[1])
    for sp in root.iter("SupplProvision"):
        an = sp.get("AmendLawNum") or "原始"
        for a in sp.iter("Article"):
            if rx.search(text(a)):
                print("### 附則 (" + an + ")")
                show(a)
        for p in sp.findall("Paragraph"):
            if rx.search(text(p)):
                print("### 附則 (" + an + ") paragraph")
                show(p)
else:
    main = root.find(".//MainProvision")
    for num in args:
        found = False
        for a in main.iter("Article"):
            if a.get("Num") == num:
                show(a)
                print()
                found = True
        if not found:
            print("!! article", num, "not found")
