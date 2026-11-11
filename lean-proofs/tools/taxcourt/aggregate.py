"""Collect every encoded Tax Court case's result into one summary.

    python tools/taxcourt/aggregate.py <taxcourt dir>      # writes <dir>/summary.json and prints totals

Each <id>.result.json (written by the encoding agents) lists, per issue the opinion decides, what the court held, what
the Lean model computed from the court's findings of fact, and a verdict:
  match         the model reproduces the holding
  mismatch      it does not (diagnosis says why: encoding, framework gap, or the court's/IRS's own arithmetic)
  judgment      the decisive step is a judgment the court made (credibility, reasonable cause), encoded as a fact
  not-encodable the question is outside what the model can express
  pending-year  the tax year is not yet supported
"""
import glob, json, sys, collections
from pathlib import Path

D = Path(sys.argv[1])
CANON = {"match": "match", "mismatch": "mismatch", "judgment": "judgment", "not-encodable": "not-encodable",
         "not encodable": "not-encodable", "pending-year": "pending-year", "pending": "pending-year"}


def load(p):
    raw = Path(p).read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return json.loads(raw.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise ValueError(p)


import re
RULES = [(r"6662", "Accuracy penalty (§6662)"), (r"6651\(a\)\(2\)|failure to pay", "Late payment (§6651(a)(2))"),
         (r"6651", "Late filing (§6651(a)(1))"), (r"6654", "Estimated-tax addition (§6654)"),
         (r"72\(t\)", "Early-distribution tax (§72(t))"), (r"\b86\b|social security|railroad", "Taxable Social Security (§86)"),
         (r"\b32\b|earned income credit|EIC|EITC", "Earned income credit (§32)"), (r"\b24\b|child tax credit|ACTC|CTC", "Child tax credit (§24)"),
         (r"2\(b\)|head of household", "Head of household (§2(b))"), (r"152\(d\)|qualifying relative", "Qualifying relative (§152(d))"),
         (r"152|qualifying child|dependen|151", "Qualifying child / dependency (§§151, 152)"),
         (r"408\(d\)\(3\)|rollover", "IRA rollover (§408(d)(3))"), (r"219", "IRA deduction (§219)"), (r"408|IRA", "IRA distributions (§408(d))"),
         (r"\b71\b|215|alimony", "Alimony (§§71, 215)"), (r"25A|education", "Education credits (§25A)"),
         (r"165\(d\)|gambling", "Gambling losses (§165(d))"), (r"1401|1402|self-employment", "Self-employment tax (§1401)"),
         (r"6211|deficien", "Deficiency (§6211)"), (r"\b61\b|gross income|income", "Gross income (§61)")]


def classify(text):
    for pat, name in RULES:
        if re.search(pat, text, re.I):
            return name
    return "Other provisions"


idx = load(D / "index.json")
idx = idx if isinstance(idx, list) else idx["cases"]
meta = {c["id"]: c for c in idx}
cases, totals, by_tag = [], collections.Counter(), collections.defaultdict(collections.Counter)
for p in sorted(glob.glob(str(D / "encoded" / "*.result.json"))):
    r = load(p)
    cid = r.get("id") or Path(p).name.split(".")[0]
    m = meta.get(cid, {})
    issues = []
    for it in r.get("issues", []):
        v = CANON.get(str(it.get("verdict", "")).strip().lower(), str(it.get("verdict")))
        totals[v] += 1
        issues.append({**it, "verdict": v})
    for it in issues:
        by_tag[classify(str(it.get("provision", "")) + " " + str(it.get("issue", "")))][it["verdict"]] += 1
    cases.append({"id": cid, "citation": r.get("citation") or m.get("citation"), "name": m.get("case_name"),
                  "date": m.get("date"), "type": m.get("opinion_type"), "years": m.get("tax_years"),
                  "issues": issues, "deficiency": r.get("deficiency"), "notes": r.get("notes")})
decided = totals["match"] + totals["mismatch"]
out = {"cases": len(cases), "issues": sum(totals.values()), "totals": dict(totals),
       "computable_agreement": f"{totals['match']}/{decided}" if decided else "-",
       "by_tag": {k: dict(v) for k, v in by_tag.items()}, "detail": cases}
(D / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(cases), "cases;", dict(totals), "; match on computable:", out["computable_agreement"])
