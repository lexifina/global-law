"""Dump one sheet of an .xlsx (stdlib only) as rows of cell values.
usage: python3 -I xlsx_dump.py <file.xlsx> <sheet name> [maxrows]"""
import sys, re, zipfile
import xml.etree.ElementTree as ET

path, name = sys.argv[1], sys.argv[2]
maxrows = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
z = zipfile.ZipFile(path)
try:
    ss = ["".join(t.itertext()) for t in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
except KeyError:
    ss = []
wb = ET.fromstring(z.read("xl/workbook.xml"))
rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
rmap = {r.get("Id"): r.get("Target") for r in rels}
target = None
for s in wb.find("m:sheets", ns):
    if s.get("name") == name:
        target = rmap[s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")]
if target is None:
    sys.exit("no sheet " + name)
target = target.lstrip("/")
if not target.startswith("xl/"):
    target = "xl/" + target
sh = ET.fromstring(z.read(target))
n = 0
for row in sh.iter("{%s}row" % ns["m"]):
    vals = []
    for c in row.findall("m:c", ns):
        v = c.find("m:v", ns)
        t = c.get("t")
        if v is None:
            isel = c.find("m:is", ns)
            val = "".join(isel.itertext()) if isel is not None else ""
        elif t == "s":
            val = ss[int(v.text)]
        else:
            val = v.text
        vals.append(c.get("r") + "=" + re.sub(r"\s+", " ", val))
    if vals:
        print(" | ".join(vals))
        n += 1
        if n >= maxrows:
            break
