"""Turn the checker's findings into a reviewable table and summary figures.

    python tools/taxcode/report.py <out dir>

Reads t26.json and findings.json (written by `lake env lean --run TaxCode/Main.lean ...`), and writes:
  findings.csv     one row per finding: class, citing provision, target, the words, context, whether the Law Revision
                   Counsel's own footnote marks the same spot ("So in original", "See References in Text")
  summary.json     counts by class, overlap with the official footnotes, recall against those footnotes
"""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

out = Path(sys.argv[1])
provs = json.loads((out / "t26.json").read_text(encoding="utf-8"))["provisions"]
byid = {p["id"]: p for p in provs}
findings = json.loads((out / "findings.json").read_text(encoding="utf-8"))

def short(i):
    return i.replace("/us/usc/t26/s", "§").replace("/us/usc/t", "t").replace("/", ".", 0)

def cite(i):
    """'/us/usc/t26/s1202/b/4/A' -> '§1202(b)(4)(A)'; other titles as '15 U.S.C. §78'."""
    m = re.match(r"/us/usc/t([0-9A-Za-z]+)/s([^/]+)((?:/[^/]+)*)", i)
    if not m:
        return i
    t, sec, rest = m.groups()
    path = "".join(f"({x})" for x in rest.split("/") if x)
    return (f"§{sec}{path}" if t == "26" else f"{t} U.S.C. §{sec}{path}")

flag = defaultdict(set)
for f in findings:
    flag[f["citing"]].add(f["class"])

rows = []
seen = set()
for f in findings:
    k = (f["class"], f["citing"], f["target"])
    if k in seen:
        continue
    seen.add(k)
    p = byid.get(f["citing"], {})
    text = p.get("text", "")
    phrase = f["detail"].split(" — ")[0]
    i = text.replace("†", " ").find(phrase[:25]) if phrase else -1  # the parser reads with footnote marks blanked
    ctx = text[max(0, i - 160):i + 160] if i >= 0 else text[:300]
    fns = p.get("footnotes", [])
    rows.append({
        "class": f["class"], "citing": cite(f["citing"]), "target": cite(f["target"]), "words": phrase[:120],
        "detail": f["detail"], "context": ctx.replace("⟦REF⟧", "[link]").replace("†", "[footnote]"),
        "official_footnote": "; ".join(re.sub(r"^\d+\s*", "", x)[:90] for x in fns),
        "heading": byid.get("/".join(f["citing"].split("/")[:5]), {}).get("heading", ""),
    })

with open(out / "findings.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

rit = [p["id"] for p in provs for fn in p.get("footnotes", []) if "References in Text" in fn]
soi = [p["id"] for p in provs for fn in p.get("footnotes", []) if "So in original" in fn]
paren_soi = [p["id"] for p in provs for fn in p.get("footnotes", []) if "So in original" in fn and "parenthes" in fn]
summary = {
    "release": "119-138",
    "provisions": len(provs),
    "sections": sum(1 for p in provs if p["kind"] == "section"),
    "in_force_sections": sum(1 for p in provs if p["kind"] == "section" and p["status"] == "in-force"),
    "references_checked": sum(len(p["refs"]) + len(p.get("rel", [])) + len(p.get("secrefs", [])) for p in provs),
    "by_class": dict(Counter(r["class"] for r in rows)),
    "official_footnotes": {"see_references_in_text": len(rit), "so_in_original": len(soi)},
    "recall_see_references_in_text": sum(1 for i in rit if flag[i]) / max(1, len(rit)),
    "recall_parentheses": sum(1 for i in paren_soi if "unbalanced-parentheses" in flag[i]) / max(1, len(paren_soi)),
    "findings_with_official_footnote": sum(1 for r in rows if r["official_footnote"]),
    "findings_without_official_footnote": sum(1 for r in rows if not r["official_footnote"]),
}
(out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
