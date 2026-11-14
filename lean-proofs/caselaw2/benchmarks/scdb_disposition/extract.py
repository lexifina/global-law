#!/usr/bin/env python3
"""Extract the SCDB fields this benchmark uses into work/scdb.tsv, and the codebook value lists into work/codes.tsv.

Run with `python -I extract.py` (raw/ is untrusted; nothing is executed from it, the zips are read as data).

Columns kept (everything else, in particular `precedentAlteration`, is NOT read into any work file):
  file, caseId, docketId, dateDecision, term, decisionType, usCite, sctCite, ledCite, lexisCite, docket, caseName,
  jurisdiction, caseOrigin, caseOriginState, caseSource, caseSourceState, lcDisposition, caseDisposition,
  caseDispositionUnusual
"""
import csv
import html
import io
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
WORK = os.path.join(HERE, "work")
FILES = [("modern", os.path.join(RAW, "modern_2026_01", "SCDB_2026_01_caseCentered_Citation.csv.zip")),
         ("legacy", os.path.join(RAW, "legacy_07", "SCDB_Legacy_07_caseCentered_Citation.csv.zip"))]
KEEP = ["caseId", "docketId", "dateDecision", "term", "decisionType", "usCite", "sctCite", "ledCite", "lexisCite",
        "docket", "caseName", "jurisdiction", "caseOrigin", "caseOriginState", "caseSource", "caseSourceState",
        "lcDisposition", "caseDisposition", "caseDispositionUnusual"]
CODEVARS = ["caseDisposition", "lcDisposition", "caseSource", "caseOrigin", "caseSourceState", "caseOriginState",
            "caseDispositionUnusual", "decisionType", "jurisdiction"]
ROW = re.compile(r"<tr>\s*<td[^>]*>\s*([^<]*?)\s*</td>\s*<td[^>]*>\s*(.*?)\s*</td>\s*</tr>", re.S)


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip().replace("\t", " ")


def main():
    os.makedirs(WORK, exist_ok=True)
    with open(os.path.join(WORK, "codes.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("var\tcode\tlabel\n")
        for v in CODEVARS:
            t = open(os.path.join(RAW, "pages", "cb_%s.html" % v), encoding="utf-8", errors="replace").read()
            i = t.find("Values:")
            n = 0
            for m in ROW.finditer(t, i if i >= 0 else 0):
                code = clean(m.group(1))
                if not re.fullmatch(r"-?\d+", code):
                    continue
                o.write("%s\t%s\t%s\n" % (v, code, clean(m.group(2))))
                n += 1
            print(v, n, "codes")
    with open(os.path.join(WORK, "scdb.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("file\t" + "\t".join(KEEP) + "\n")
        for label, p in FILES:
            z = zipfile.ZipFile(p)
            name = z.namelist()[0]
            raw = z.read(name)
            try:
                txt = raw.decode("utf-8")
            except UnicodeDecodeError:
                txt = raw.decode("cp1252", "replace")
            n = 0
            for r in csv.DictReader(io.StringIO(txt, newline="")):
                o.write(label + "\t" + "\t".join(re.sub(r"[\t\r\n]+", " ", r.get(k) or "") for k in KEEP) + "\n")
                n += 1
            print(label, n, "rows")


if __name__ == "__main__":
    main()
