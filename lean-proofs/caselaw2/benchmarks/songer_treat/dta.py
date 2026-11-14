#!/usr/bin/env python3
"""Minimal standard-library reader for Stata .dta formats 110-115 (old-style binary). Run with python -I.

    python -I dta.py <file.dta> <out.tsv>      writes every column as TSV (missing -> empty)

Downloaded files are treated as data only; nothing in them is executed.
"""
import struct
import sys


def read_dta(path):
    with open(path, "rb") as f:
        b = f.read()
    fmt = b[0]
    if fmt not in (110, 111, 113, 114, 115):
        raise ValueError("unsupported dta format %d" % fmt)
    bo = "<" if b[1] == 2 else ">"
    nvar, nobs = struct.unpack(bo + "Hi", b[4:10])
    pos = 10 + 81 + 18
    typ = list(b[pos:pos + nvar])
    pos += nvar
    names = []
    for i in range(nvar):
        names.append(b[pos:pos + 33].split(b"\0")[0].decode("latin-1"))
        pos += 33
    pos += 2 * (nvar + 1)
    pos += nvar * (49 if fmt >= 114 else 12)
    pos += nvar * 33  # value label names
    pos += nvar * 81  # variable labels
    while True:  # expansion fields
        dt = b[pos]
        ln = struct.unpack(bo + "i", b[pos + 1:pos + 5])[0]
        pos += 5
        if dt == 0 and ln == 0:
            break
        pos += ln
    old = fmt <= 110
    spec = []
    for t in typ:
        if old:
            if t in (ord("b"),):
                spec.append(("b", 1))
            elif t == ord("i"):
                spec.append(("h", 2))
            elif t == ord("l"):
                spec.append(("i", 4))
            elif t == ord("f"):
                spec.append(("f", 4))
            elif t == ord("d"):
                spec.append(("d", 8))
            elif t > 0x7f:
                spec.append(("s", t - 0x7f))
            else:
                raise ValueError("type %d" % t)
        else:
            if t == 251:
                spec.append(("b", 1))
            elif t == 252:
                spec.append(("h", 2))
            elif t == 253:
                spec.append(("i", 4))
            elif t == 254:
                spec.append(("f", 4))
            elif t == 255:
                spec.append(("d", 8))
            elif 1 <= t <= 244:
                spec.append(("s", t))
            else:
                raise ValueError("type %d" % t)
    reclen = sum(s[1] for s in spec)
    rows = []
    for r in range(nobs):
        rec = b[pos + r * reclen: pos + (r + 1) * reclen]
        o = 0
        row = []
        for code, ln in spec:
            v = rec[o:o + ln]
            o += ln
            if code == "s":
                row.append(v.split(b"\0")[0].decode("latin-1").strip())
                continue
            x = struct.unpack(bo + code, v)[0]
            miss = ((code == "b" and (x > 100 or (old and x == 127)))
                    or (code == "h" and x > 32740)
                    or (code == "i" and x > 2147483620)
                    or (code in "fd" and (x != x or abs(x) > 8.9e307 or (code == "f" and abs(x) > 1.7e38))))
            if miss:
                row.append("")
            elif code in "fd" and x == int(x):
                row.append(str(int(x)))
            else:
                row.append(str(x))
        rows.append(row)
    return names, rows


def main():
    names, rows = read_dta(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(names) + "\n")
        for r in rows:
            o.write("\t".join(c.replace("\t", " ").replace("\n", " ") for c in r) + "\n")
    print(sys.argv[1], "vars", len(names), "rows", len(rows))


if __name__ == "__main__":
    main()
