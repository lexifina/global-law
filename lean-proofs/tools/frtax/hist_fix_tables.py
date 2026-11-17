"""Parse-compat patch for old M releases under current Mlang: a variable named T<dd> clashes with the cells of a
table T (tableau[N]); rename it to T_Q<dd> in every file of the release (a consistent rename, no semantic change)."""
import re, sys, glob, os
d = sys.argv[1]
files = glob.glob(os.path.join(d, "*.m"))
decl = {}
tabs = set()
for f in files:
    for line in open(f, encoding="latin1"):
        m = re.match(r"^([A-Z0-9_]+)\s*:\s*(tableau\[\d+\])?", line)
        if m:
            decl[m.group(1)] = True
            if m.group(2): tabs.add(m.group(1))
ren = {v: re.sub(r"(\d\d)$", r"Q\1", v) for v in decl if re.search(r"\d\d$", v) and v[:-2] in tabs}
print("renames:", ren)
if ren:
    pat = re.compile(r"\b(" + "|".join(map(re.escape, ren)) + r")\b")
    for f in files:
        t = open(f, encoding="latin1").read()
        t2 = pat.sub(lambda m: ren[m.group(1)], t)
        if t2 != t: open(f, "w", encoding="latin1").write(t2)
