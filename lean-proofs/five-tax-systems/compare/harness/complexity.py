"""Measured complexity of the five Lean models, counted the same way for every country.

    python3 complexity.py   -> charts/complexity.json

For each model: the modules the calculator executable imports (its "computation" closure, followed through `import`
lines from the exe's root module), and every module in the model's folder (computation plus tests and proofs). Counted:
  lines        non-blank, non-comment lines of Lean (docstrings and comments excluded)
  comment      lines inside comments and docstrings (where the statute is quoted and cited)
  defs         def / abbrev / structure / inductive / instance declarations
  theorems     theorem / lemma declarations (proofs for all inputs)
  checks       #guard / example / `by decide` test lines
  literals     distinct integer literals in the closure's code (outside comments), excluding scale constants: a rough
               proxy for the number of numeric parameters the law fixes
  provisions   distinct provisions cited in comments and docstrings, by each country's citation pattern
  sorry, native_decide: occurrences (should be 0)
The counts are a measuring stick for the models, not for the law: two people formalising the same statute would get
different numbers. They are comparable across countries only because the five models were written to one style
(CONTRACT.md: one definition per provision, statute quoted, whole currency units).
"""
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
ROOT = os.path.join(HOME, "cmp", "compare")

MODELS = {
    "US": {"src": os.path.join(ROOT, "lean"), "root": "TaxCode.Individual.Form1040",
           "folder": os.path.join(ROOT, "lean", "TaxCode", "Individual"), "prefix": "TaxCode"},
    "FR": {"src": os.path.join(ROOT, "lean"), "root": "FrTax.Liquidation",
           "folder": os.path.join(ROOT, "lean", "FrTax"), "prefix": "FrTax"},
    "UK": {"src": os.path.join(HOME, "cmp", "uk", "lean"), "root": None,
           "folder": os.path.join(HOME, "cmp", "uk", "lean", "UkTax"), "prefix": "UkTax"},
    "DE": {"src": os.path.join(HOME, "cmp", "de", "lean"), "root": None,
           "folder": os.path.join(HOME, "cmp", "de", "lean", "DeTax"), "prefix": "DeTax"},
    "JP": {"src": os.path.join(HOME, "cmp", "jp", "lean"), "root": None,
           "folder": os.path.join(HOME, "cmp", "jp", "lean", "JpTax"), "prefix": "JpTax"},
}
# The adapters this comparison added to the US and French models (counted separately)
ADAPTERS = {"US": ["Compare.Us"], "FR": ["Compare.Fr"]}

CITE = {
    "US": re.compile(r"§\s*(\d+[A-Z]?)"),
    "FR": re.compile(r"\bart(?:icle|\.)\s*(L?R?D?\s?\d+[\w-]*(?:\s(?:bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies|undecies|duodecies|terdecies|quaterdecies|quindecies|sexdecies|septdecies|vicies|quatervicies))?)", re.I),
    "UK": re.compile(r"\b(?:s|ss|section|sections)\.?\s*(\d+[A-Z]*)"),
    "DE": re.compile(r"§\s*(\d+[a-z]?)"),
    "JP": re.compile(r"第\s*([0-9０-９一二三四五六七八九十百千]+)\s*条(?:の\s*[0-9０-９一二三四五六七八九十]+)?"),
}
SCALE = {0, 1, 2, 3, 4, 5, 10, 12, 100, 1000, 10000, 100000, 1000000, 10000000}


def lakefile_root(src):
    """The exe's root module, read from lakefile.toml (`root = "..."` of the first [[lean_exe]])."""
    p = os.path.join(src, "lakefile.toml")
    if not os.path.exists(p):
        return None
    t = open(p, encoding="utf-8").read()
    m = re.search(r"\[\[lean_exe\]\][^\[]*?root\s*=\s*\"([^\"]+)\"", t, re.S)
    return m.group(1) if m else None


def path_of(src, mod):
    return os.path.join(src, *mod.split(".")) + ".lean"


def imports(path):
    out = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\s*import\s+(.+)", line)
        if m:
            out += m.group(1).split()
        elif line.strip() and not line.startswith("import") and not line.startswith("--") and out:
            break
    return out


def closure(src, root, prefixes):
    seen, todo = [], [root]
    while todo:
        m = todo.pop()
        if m in seen:
            continue
        p = path_of(src, m)
        if not os.path.exists(p):
            continue
        seen.append(m)
        for i in imports(p):
            if any(i == pr or i.startswith(pr + ".") for pr in prefixes):
                todo.append(i)
    return sorted(seen)


def strip(text):
    """Split Lean text into code (comments removed) and comment text."""
    code, com = [], []
    i, n, depth = 0, len(text), 0
    buf_code, buf_com = [], []
    while i < n:
        if depth == 0 and text.startswith("--", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            buf_com.append(text[i:j])
            i = j
            continue
        if text.startswith("/-", i):
            depth += 1
            i += 2
            continue
        if depth > 0 and text.startswith("-/", i):
            depth -= 1
            i += 2
            continue
        (buf_com if depth > 0 else buf_code).append(text[i])
        i += 1
    return "".join(buf_code), "".join(buf_com)


def file_literals(code):
    out = set()
    for block in re.split(r"\n(?=\S)", code):
        b = block.lstrip()
        if b.startswith(("theorem", "lemma", "#guard", "example", "#eval", "#print")):
            continue
        for m in re.finditer(r"(?<![\w.])(\d[\d_]*)(?![\w.])", block):
            v = int(m.group(1).replace("_", ""))
            if v not in SCALE:
                out.add(v)
    return out


def count_files(paths, country):
    tot = {"files": 0, "lines": 0, "comment_lines": 0, "defs": 0, "theorems": 0, "checks": 0, "sorry": 0,
           "native_decide": 0, "data_table_files": [], "distinct_literals_outside_tables": 0}
    lits, cites, lits_nt = set(), set(), set()
    for p in paths:
        t = open(p, encoding="utf-8").read()
        code, com = strip(t)
        fl = file_literals(code)
        # a file holding a reproduced official table (hundreds of numbers, e.g. the US EIC table) is data, not
        # parameters: listed apart
        if len(fl) > 400:
            tot["data_table_files"].append({"file": os.path.relpath(p, HOME), "distinct_literals": len(fl)})
        else:
            lits_nt |= fl
        tot["files"] += 1
        tot["lines"] += sum(1 for l in code.splitlines() if l.strip())
        tot["comment_lines"] += sum(1 for l in com.splitlines() if l.strip())
        tot["defs"] += len(re.findall(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|partial\s+)*(?:def|abbrev|structure|inductive|instance)\b", code, re.M))
        tot["theorems"] += len(re.findall(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)*(?:theorem|lemma)\b", code, re.M))
        tot["checks"] += len(re.findall(r"^\s*(?:#guard|example)\b", code, re.M))
        tot["sorry"] += len(re.findall(r"\bsorry\b", code))
        tot["native_decide"] += len(re.findall(r"\bnative_decide\b", code))
        # literals: only in definitions (exclude theorem statements and #guard lines, which hold test values)
        for block in re.split(r"\n(?=\S)", code):
            b = block.lstrip()
            if b.startswith(("theorem", "lemma", "#guard", "example", "#eval", "#print")):
                continue
            for m in re.finditer(r"(?<![\w.])(\d[\d_]*)(?![\w.])", block):
                v = int(m.group(1).replace("_", ""))
                if v not in SCALE:
                    lits.add(v)
        for m in CITE[country].finditer(com):
            cites.add(re.sub(r"\s+", " ", m.group(1)).strip())
    tot["distinct_literals"] = len(lits)
    tot["distinct_literals_outside_tables"] = len(lits_nt)
    tot["distinct_provisions_cited"] = len(cites)
    return tot, sorted(cites)


def main():
    res = {"definitions": __doc__, "models": {}}
    for c, m in MODELS.items():
        if not os.path.isdir(m["folder"]):
            res["models"][c] = {"missing": m["folder"]}
            continue
        root = m["root"] or lakefile_root(m["src"])
        allfiles = []
        for dp, dn, fn in os.walk(m["folder"]):
            for f in fn:
                if f.endswith(".lean"):
                    allfiles.append(os.path.join(dp, f))
        top = os.path.join(m["src"], m["prefix"] + ".lean")
        if os.path.exists(top):
            allfiles.append(top)
        entry = {"root": root, "folder": m["folder"]}
        if root:
            mods = closure(m["src"], root, [m["prefix"]])
            cl, cites = count_files([path_of(m["src"], x) for x in mods], c)
            entry["computation"] = cl
            entry["computation_modules"] = mods
            entry["provisions_sample"] = cites[:400]
        whole, _ = count_files(sorted(allfiles), c)
        entry["whole_model"] = whole
        if c in ADAPTERS:
            ad, _ = count_files([path_of(os.path.join(ROOT, "lean"), x) for x in ADAPTERS[c]], c)
            entry["comparison_adapter"] = ad
        res["models"][c] = entry
    json.dump(res, open(os.path.join(ROOT, "charts", "complexity.json"), "w"), indent=1, ensure_ascii=False)
    for c, e in res["models"].items():
        print(c, e.get("root"), "computation:", e.get("computation"), "\n   whole:", e.get("whole_model"))


if __name__ == "__main__":
    main()
