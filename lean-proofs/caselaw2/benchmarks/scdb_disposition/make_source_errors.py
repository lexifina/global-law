#!/usr/bin/env python3
"""Write source_errors.tsv: SCDB rows whose caseDisposition contradicts the disposition stated in our text of the
Supreme Court opinion (found while reading disagreements; see DISAGREEMENTS.md).

python -I make_source_errors.py
The caseIds and the reading are hand-entered below (the classification made by reading); the quote is re-extracted
from the corpus text here (the last majority/per-curiam/combined sentence of the SC opinion containing "revers"),
so every quote is verbatim corpus text. Rows whose quote cannot be re-found are written with quote "-" and flagged.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import link as L  # noqa: E402
import ctx as C  # noqa: E402

# caseId -> what our SC text shows (reading notes)
ERRORS = {
    "1907-018": "judgment of the Circuit Court of Appeals reversed with direction to dismiss the writ of error; SCDB 9",
    "1911-173": "decree reversed as to No. 129 and affirmed as to No. 128 (partial); SCDB 2",
    "1913-076": "decree of the Circuit Court of Appeals reversed, that of the Circuit Court affirmed; SCDB 2",
    "1914-012": "decree of the Circuit Court of Appeals reversed, that of the Circuit Court affirmed; SCDB 2",
    "1921-039": "judgment of the Supreme Court of Arizona reversed; SCDB 2",
    "1922-070": "decrees of the Circuit Court of Appeals reversed, District Court affirmed (Mason modified); SCDB 2",
    "1924-075": "reversed; SCDB 2",
    "1924-184": "reversed; SCDB 2",
    "1924-235": "decree of the Circuit Court of Appeals reversed; SCDB 2",
    "1925-123": "judgment reversed; SCDB 2",
    "1926-066": "judgment reversed; SCDB 2",
    "1926-086": "judgment of the Supreme Court of Missouri reversed; SCDB 2",
    "1926-096": "reversed; SCDB 2",
    "1927-026": "reversed; SCDB 2",
    "1927-054": "judgment reversed; SCDB 2",
    "1927-090": "judgment reversed; SCDB 2",
    "1927-145": "judgment reversed; SCDB 2",
    "1928-047": "judgment reversed; SCDB 2",
    "1928-050": "reversed; SCDB 2",
    "1929-023": "judgment reversed; SCDB 2",
    "1930-043": "reversed; SCDB 2",
    "1931-011": "reversed; SCDB 2",
    "1931-013": "judgment reversed; SCDB 2",
    "1931-045": "judgment reversed; SCDB 2",
    "1931-058": "decree of the Circuit Court of Appeals reversed, District Court affirmed; SCDB 2",
    "1931-060": "judgment below reversed; SCDB 2",
    "1931-107": "decree of the Circuit Court of Appeals reversed, Board of Tax Appeals affirmed; SCDB 2",
    "1933-039": "reversed; SCDB 9",
    "1934-043": "judgment reversed; SCDB 2",
    "1935-130": "reversed; SCDB 2",
    "1936-059": "reversed; SCDB 2",
    "1936-060": "judgment of conviction reversed; SCDB 2",
    "1938-003": "decree of the Circuit Court of Appeals reversed; SCDB 2",
    "1938-136": "reversed; SCDB 2",
    "1940-056": "judgment of the Circuit Court of Appeals reversed; SCDB 2",
    "1940-058": "reversed; SCDB 2",
    "1940-084": "judgment reversed; SCDB 2",
    "1940-085": "judgment below reversed; SCDB 2",
    "1941-069": "judgment below reversed; SCDB 2",
    "1941-081": "judgment reversed and remanded; SCDB 2",
    "1944-025": "reversed; SCDB 2",
    "2002-009": "judgment of the Tenth Circuit reversed; SCDB 2",
    "2014-059": "first question dismissed as improvidently granted, judgment reversed in part (qualified immunity); SCDB 9",
}
OVERRIDE = {
    "1929-023": "The judgment is Reversed.",
    "1940-085": "Accordingly, the judgment below is Reversed.",
    "1941-069": "the judgment below must be Reversed.",
    "2002-009": "the judgment of the Tenth Circuit is Reversed.",
    "1934-043": "The judgment is reversed, and the cause remanded to the Supreme Court of Missouri",
}
CUE = re.compile(r"(?:is|are|be|must be|will be) [Rr]eversed|[Ww]e (?:therefore |now |accordingly )?reverse\b|^\W*(?:IV For these reasons, )?(?:Accordingly, )?(?:the )?(?:[Jj]udgment |[Dd]ecree |Circuit Court of Appeals )?(?:below )?(?:is )?[Rr]eversed\b")


def main():
    lk = {r["caseId"]: r for r in C.rows(os.path.join(HERE, "links.tsv"))}
    ky = {r["caseId"]: r for r in C.rows(os.path.join(HERE, "key.tsv"))}
    ns = [int(lk[c]["sc_node"]) for c in ERRORS]
    nr = C.node_rows(ns)
    out = open(os.path.join(HERE, "source_errors.tsv"), "w", encoding="utf-8", newline="\n")
    out.write("caseId\tfile\tusCite\tcaseName\tscdb_caseDisposition\tscdb_class\tsc_node\tbelow\treading\t"
              "quote_section\tquote\n")
    bad = 0
    for c, reading in ERRORS.items():
        n = int(lk[c]["sc_node"])
        tx = L.fetch("supreme-court", [(n, nr[n][2])])[n]
        if tx.startswith("---"):
            tx = tx[tx.find("\n---", 3) + 4:]
        parts = re.split(r"^## (.+)$", tx, flags=re.M)
        last = None
        for i in range(1, len(parts), 2):
            h = parts[i].lower()
            if "dissent" in h or "concurr" in h:
                continue
            for s in re.split(r"(?<=[.;])\s+(?=[A-Z])", parts[i + 1]):
                if CUE.search(s.strip()) and len(s) < 700 and not re.search(r"urging|would reverse|refusal to reverse", s):
                    last = (parts[i][:40], re.sub(r"\s+", " ", s.strip()))
        if c in OVERRIDE:  # sentence splitting failed on these; the exact substring is checked against the text
            flat = re.sub(r"\s+", " ", tx)
            last = ("verbatim substring", OVERRIDE[c]) if OVERRIDE[c] in flat else None
        if last is None:
            bad += 1
            last = ("-", "-")
        k = ky[c]
        out.write("\t".join([c, k["file"], k["usCite"], k["caseName"], k["caseDisposition"], k["class"], str(n),
                             lk[c]["below"], reading, last[0], last[1].replace("\t", " ")]) + "\n")
    out.close()
    print("rows", len(ERRORS), "without quote", bad)


if __name__ == "__main__":
    main()
