"""Explore the Federal Circuit document dataset (source only; no model output). Run with python -I."""
import collections
import csv
import re
import sys
import zipfile

csv.field_size_limit(10 ** 8)


def codebook(path):
    with zipfile.ZipFile(path) as z:
        x = z.read("word/document.xml").decode("utf-8")
    paras = re.findall(r"<w:p[ >].*?</w:p>", x, flags=re.S)
    out = []
    for p in paras:
        t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
        if t.strip():
            out.append(t)
    return "\n".join(out)


def main():
    tab, cb = sys.argv[1], sys.argv[2]
    if len(sys.argv) > 3:
        with open(sys.argv[3], "w", encoding="utf-8", newline="\n") as f:
            f.write(codebook(cb))
    with open(tab, encoding="utf-8", errors="replace", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    print("rows", len(rows))
    for col in ("origin", "TribOfOrigin", "DispGeneral", "docType", "PrecedentialStatus", "enBanc", "DataSource",
                "duplicate", "Replaced"):
        c = collections.Counter(r.get(col, "") for r in rows)
        print(col, c.most_common(25))
    yrs = collections.Counter(r["docYear"] for r in rows)
    print("years", sorted(yrs.items()))
    ot = collections.Counter((r["origin"], bool(r["Orig_Trib_Dockets"].strip())) for r in rows)
    print("orig_trib filled by origin", ot.most_common(30))
    ex = collections.defaultdict(list)
    for r in rows:
        if r["Orig_Trib_Dockets"].strip() and len(ex[r["origin"]]) < 4:
            ex[r["origin"]].append(r["Orig_Trib_Dockets"])
    print(dict(ex))
    cx = collections.Counter((r["origin"], r["DispGeneral"]) for r in rows
                             if r["origin"] in ("CFC", "CIT", "DCT", "D. Ct.", "District Court", "CAVC"))
    print(cx.most_common(60))


if __name__ == "__main__":
    main()
