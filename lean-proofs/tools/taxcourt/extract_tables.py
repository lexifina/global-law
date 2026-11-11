"""Extract the printed EIC Tables (Pub. 596) and Tax Tables (Form 1040 instructions), 2016-2024, to JSON.

    # fetch (irs.gov/pub/irs-prior/p596--YYYY.pdf, i1040gi--YYYY.pdf) into DIR, then
    pdftotext -layout DIR/p596-YYYY.pdf DIR/p596-YYYY.txt      (and i1040gi-YYYY)
    python -I extract_tables.py DIR OUTDIR

writes OUTDIR/eic_tables.json  {year: [[atLeast, [8 columns]], ...]}
       OUTDIR/tax_tables.json  {year: [[atLeast, butLessThan, [single, mfj, mfs, hoh]], ...]}
The page layout puts two or three table blocks side by side, so a handful of rows per year are mis-assembled by this
parser (values shifted between columns); CheckTables.lean reports every mismatch so they can be inspected.
"""
import json, re, sys

src, out = sys.argv[1], sys.argv[2]
eic, tax = {}, {}
for y in range(2016, 2025):
    t = open(f'{src}/p596-{y}.txt', encoding='latin-1').read()
    rows = {}
    for line in t.splitlines():
        toks = [int(x) for x in (s.replace(',', '') for s in re.findall(r'\$?([\d][\d,]*)', line)) if x]
        i = 0
        while i + 10 <= len(toks):
            a, b = toks[i], toks[i + 1]
            if (b == a + 50 or (a == 1 and b == 50)) and a % 50 in (0, 1):
                rows.setdefault(a, toks[i + 2:i + 10]); i += 10
            else:
                i += 1
    eic[y] = sorted(rows.items())
    t = open(f'{src}/i1040gi-{y}.txt', encoding='latin-1').read()
    i = t.find('Sample Table'); j = t.find('Tax Computation Worksheet', i + 1000)
    rows = {}
    for line in t[i:j].splitlines():
        toks = [int(x.replace(',', '')) for x in re.findall(r'(?<![\d.])(\d[\d,]*)(?![\d.])', line)]
        k = 0
        while k + 6 <= len(toks):
            a, b = toks[k], toks[k + 1]
            if b - a in (5, 10, 25, 50) and b <= 100000:
                rows.setdefault(a, (b, toks[k + 2:k + 6])); k += 6
            else:
                k += 1
    tax[y] = sorted((a, b, v) for a, (b, v) in rows.items())
json.dump(eic, open(f'{out}/eic_tables.json', 'w'))
json.dump(tax, open(f'{out}/tax_tables.json', 'w'))
print({y: (len(eic[y]), len(tax[y])) for y in eic})
