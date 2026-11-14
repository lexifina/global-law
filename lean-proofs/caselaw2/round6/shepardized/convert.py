#!/usr/bin/env python3
"""Convert the downloaded Stata files (.dta formats 110 and 114) to plain TSV. Standard library only.

Run isolated:  python -I convert.py
The downloads are untrusted data: this script only parses bytes with struct; nothing in them is executed.
(pandas could not be used on this machine: an Application Control policy blocks its compiled modules.)

Outputs (work/): shepardized.tsv (all columns), songer96.tsv and songer_update.tsv (selected columns),
columns.txt (every column name, storage type and Stata variable label of each file).
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src", "extracted")
WORK = os.path.join(HERE, "work")

FILES = [
    ("shepardized", os.path.join(SRC, "shepardized_cta_stata", "shepardized_cta_stata.dta"), None),
    ("songer96", os.path.join(SRC, "cta96_stata", "cta96_stata.dta"), "songer"),
    ("songer_update", os.path.join(SRC, "KH_update_stata", "KH_update_stata.dta"), "songer"),
]
SONGER_KEEP = {"casenum", "year", "month", "day", "vol", "beginpg", "endpage", "cite", "citation", "circuit",
               "docnum", "method", "treat", "priorpub", "decdate", "date", "endopin"}


def cstr(b):
    return b.split(b"\0", 1)[0].decode("latin-1")


def read_dta(path):
    b = open(path, "rb").read()
    fmt = b[0]
    if fmt not in (110, 113, 114):
        raise SystemExit("unsupported dta format %d in %s" % (fmt, path))
    bo = "<" if b[1] == 2 else ">"
    nvar = struct.unpack_from(bo + "H", b, 4)[0]
    nobs = struct.unpack_from(bo + "i", b, 6)[0]
    stamp = cstr(b[91:109])
    p = 109
    typ = list(b[p:p + nvar]); p += nvar
    names = [cstr(b[p + 33 * i:p + 33 * i + 33]) for i in range(nvar)]; p += 33 * nvar
    p += 2 * (nvar + 1)
    fl = 49 if fmt == 114 else 12
    p += fl * nvar
    p += 33 * nvar
    labels = [cstr(b[p + 81 * i:p + 81 * i + 81]) for i in range(nvar)]; p += 81 * nvar
    while True:  # expansion fields
        t = b[p]
        ln = struct.unpack_from(bo + "i", b, p + 1)[0]
        p += 5
        if t == 0 and ln == 0:
            break
        p += ln
    if fmt >= 111:
        num = {251: ("b", 1, 100), 252: ("h", 2, 32740), 253: ("i", 4, 2147483620), 254: ("f", 4, None),
               255: ("d", 8, None)}

        def strlen(t):
            return t if t <= 244 else None
    else:
        num = {ord("b"): ("b", 1, 126), ord("i"): ("h", 2, 32766), ord("l"): ("i", 4, 2147483646),
               ord("f"): ("f", 4, None), ord("d"): ("d", 8, None)}

        def strlen(t):
            return t - 0x7F if t >= 0x80 else None
    spec = []
    width = 0
    for t in typ:
        if t in num:
            spec.append(("n",) + num[t])
            width += num[t][1]
        else:
            n = strlen(t)
            if n is None:
                raise SystemExit("unknown type code %d" % t)
            spec.append(("s", None, n, None))
            width += n
    if p + width * nobs > len(b):
        raise SystemExit("file shorter than header says: %s" % path)
    rows = []
    for r in range(nobs):
        row = []
        for kind, code, n, maxv in spec:
            if kind == "s":
                row.append(cstr(b[p:p + n]).replace("\t", " ").replace("\r", " ").replace("\n", " ").strip())
            else:
                v = struct.unpack_from(bo + code, b, p)[0]
                if code in "fd":
                    if v != v or abs(v) > 8.0e37 and code == "f" or abs(v) > 8.0e307:
                        row.append("")
                    elif v == int(v):
                        row.append(str(int(v)))
                    else:
                        row.append(repr(round(v, 6)))
                else:
                    row.append("" if v > maxv else str(v))
            p += n
        rows.append(row)
    return fmt, stamp, names, typ, labels, rows


def main():
    os.makedirs(WORK, exist_ok=True)
    with open(os.path.join(WORK, "columns.txt"), "w", encoding="utf-8", newline="\n") as cols:
        for name, path, kind in FILES:
            fmt, stamp, names, typ, labels, rows = read_dta(path)
            cols.write("== %s format=%d stamp=%s rows=%d cols=%d\n" % (name, fmt, stamp, len(rows), len(names)))
            for n, t, l in zip(names, typ, labels):
                cols.write("%s\t%d\t%s\n" % (n, t, l))
            idx = list(range(len(names)))
            if kind == "songer":
                idx = [i for i in idx if names[i].lower() in SONGER_KEEP]
            with open(os.path.join(WORK, name + ".tsv"), "w", encoding="utf-8", newline="\n") as o:
                o.write("\t".join(names[i].lower() for i in idx) + "\n")
                for r in rows:
                    o.write("\t".join(r[i] for i in idx) + "\n")
            print(name, "format", fmt, "stamp", stamp, len(rows), "rows", len(names), "cols")


if __name__ == "__main__":
    sys.exit(main())
