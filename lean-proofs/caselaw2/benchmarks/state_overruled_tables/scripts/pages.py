"""djvu.xml -> one line per OCR text line: leaf, line_no, x0, top, x1, bottom, text   (stdlib; run with python -I)

    python -I pages.py <djvu.xml> <out.tsv>

Refuses a file that declares entities. Leaf = the scan leaf index from the PAGE param (…_0123.djvu -> 123).
Word coords in IA djvu.xml are "x0,bottom,x1,top[,baseline]".
"""
import re
import sys
import xml.etree.ElementTree as ET


def main(src, out):
    with open(src, "rb") as f:
        head = f.read(1 << 16)
    if b"<!ENTITY" in head:
        sys.exit("entity declaration: refused")
    leaf = -1
    n = 0
    with open(out, "w", encoding="utf-8", newline="\n") as o:
        lno = 0
        for ev, el in ET.iterparse(src, events=("start", "end")):
            if ev == "start" and el.tag == "OBJECT":
                m = re.search(r"_(\d+)\.djvu$", el.get("usemap", ""))
                leaf = int(m.group(1)) if m else leaf + 1
                lno = 0
            elif ev == "end" and el.tag == "LINE":
                ws = []
                for w in el.iter("WORD"):
                    c = [int(x) for x in (w.get("coords") or "0,0,0,0").split(",")[:4]]
                    ws.append((c, (w.text or "").strip()))
                if ws:
                    x0 = min(c[0] for c, _ in ws)
                    x1 = max(c[2] for c, _ in ws)
                    top = min(c[3] for c, _ in ws)
                    bot = max(c[1] for c, _ in ws)
                    txt = " ".join(t for _, t in ws).replace("\t", " ")
                    o.write("%d\t%d\t%d\t%d\t%d\t%d\t%s\n" % (leaf, lno, x0, top, x1, bot, txt))
                    lno += 1
                    n += 1
                el.clear()
            elif ev == "end" and el.tag == "OBJECT":
                el.clear()
    print(src, "lines", n, "last leaf", leaf)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
