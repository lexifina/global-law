S = {'cc': 'IE', 'fam': 'Wealth', 'families': [], 'doc': "# IE 2025: Wealth family not reached (grade C)\n\n* 4300 Inheritance and gift tax (Capital Acquisitions Tax Consolidation Act 2003 (33 %, group thresholds)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)\n* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)\n", 'notes': [], 'unsupported': [('!g.transfers.isEmpty || !g.assets.isEmpty', '4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)'), ('!g.transfers.isEmpty || !g.assets.isEmpty', '4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)')], 'guards': [], 'taxes': [{'oecd': '4300', 'tax': 'Inheritance and gift tax', 'statute': 'Capital Acquisitions Tax Consolidation Act 2003 (33 %, group thresholds)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)"]}, {'oecd': '4200', 'tax': 'Net wealth tax', 'statute': 'none recorded', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)"]}]}

# ---- pass 3 (R1 Europe, 2026-11-21): capital acquisitions tax ----
S["doc"] = S["doc"].split("\n* 4300")[0].split("\n* 4200")[0].replace("Wealth family not reached (grade C)", "capital acquisitions tax (4300)") + r'''

## Capital acquisitions tax (4300), pass 3
Source: Revenue, Notes for Guidance, Capital Acquisitions Tax Consolidation Act 2003 "(as amended by subsequent Acts
up to and including the Finance Act 2024)", via the Internet Archive (captures 2025-08-09;
`ie/law/cat_nfg2024_schedules.pdf`, `cat_nfg2024_part09.pdf`, `cat_nfg2024_part01.pdf`); the Act's own text
(irishstatutebook / revisedacts) not read: grade B.
* Schedule 2: "3 group thresholds: Group A €400,000, Group B €40,000, Group C €20,000"; Group A where the donee or
  successor is "the child, or minor child of a deceased child of the disponer" (or a parent inheriting an absolute
  interest); Group B "a lineal ancestor, a lineal descendant (other than a child ...), a brother, a sister, or a
  child of a brother or of a sister"; Group C otherwise; "Benefits taken by a beneficiary since 5 December 1991,
  which have the same group threshold as the current benefit, are aggregated"; "A single 33% rate of tax applies
  for both gifts and inheritances" (Sch. 2 Part 1 paras. 1, 3, 4).
* s. 69: "the first €3,000 of the total taxable value of all taxable gifts taken by a donee from the disponer in any
  relevant period"; s. 70, 71: gifts and inheritances taken by the spouse/civil partner are exempt.
'''
S["lean"] = (S.get("lean") or "") + r'''
/-- CATCA 2003 Sch. 2 Part 1 para. 1 (Notes for Guidance, FA 2024 edition): group thresholds; para. 4: 33 %. -/
def groupA : TaxClass := { allowance := 400000, sched := Schedule.flat 3300 }
def groupB : TaxClass := { allowance := 40000, sched := Schedule.flat 3300 }
def groupC : TaxClass := { allowance := 20000, sched := Schedule.flat 3300 }
def groupOf : Relation → Nat
  | .child => 0
  | .grandchild | .parent | .sibling | .nieceNephew => 1
  | _ => 2
/-- Aggregation since 5 December 1991 (same donor in the input), the s. 69 small-gift exemption, the spouse exemption (ss. 70, 71). -/
def cat : InheritanceTax :=
  { name := "Capital acquisitions tax", classOf := groupOf, classes := [groupA, groupB, groupC],
    exemptRelations := [.spouse], lookbackYears := 34,
    exemptValue := fun t => if t.kind == .gift then min (pos t.statutoryValue) 3000 else 0 }
'''
S["families"] = S.get("families", []) + [("4300 capital acquisitions tax", [".estate"], 'cat.charges g.transfers "CATCA 2003 Sch. 2 Part 1 paras. 1, 3, 4 (A 400 000, B 40 000, C 20 000; 33 %); ss. 69-71"')]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("4300")] + [
  ("!g.transfers.isEmpty", "4300 CAT: aggregation covers prior benefits from the same disponer only (the Act aggregates all benefits within the group since 5.12.1991); a parent inheriting an absolute interest (Group A) taken as Group B; reliefs (agricultural, business, dwelling-house s. 86), charities (s. 76), the s. 69 exemption applied once per gift"),
  ]
S["notes"] = S.get("notes", []) + ["IE 4300: CAT from Revenue Notes for Guidance (FA 2024 edition, Wayback 2025-08-09): A 400 000, B 40 000, C 20 000, 33 %"]
S["guards"] = S.get("guards", []) + [
  "-- child inherits 500 000: (500 000 - 400 000) x 33 % = 33 000",
  "cat.tax { kind := .inheritance, value := 500000, relation := .child } == 33000",
  "cat.tax { kind := .inheritance, value := 400000, relation := .child } == 0",
  "-- nephew inherits 100 000: (100 000 - 40 000) x 33 % = 19 800",
  "cat.tax { kind := .inheritance, value := 100000, relation := .nieceNephew } == 19800",
  "-- unrelated gift 50 000: (50 000 - 3 000 - 20 000) x 33 % = 8 910",
  "cat.tax { kind := .gift, value := 50000, relation := .unrelated } == 8910",
  "cat.tax { kind := .gift, value := 3000, relation := .unrelated } == 0",
  "cat.tax { kind := .inheritance, value := 5000000, relation := .spouse } == 0",
  "-- a prior 30 000 benefit inside the look-back: tax on 130 000 less tax on 30 000 (nephew): 29 700 - 0",
  "cat.tax { kind := .inheritance, value := 100000, relation := .nieceNephew, prior := [(30000, 5)] } == 29700"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "4300"] + [
 {"oecd": "4300", "tax": "Capital acquisitions tax (gift and inheritance tax)", "statute": "Capital Acquisitions Tax Consolidation Act 2003 Sch. 2 Part 1 paras. 1, 3, 4; ss. 69, 70, 71",
  "dated": "Revenue Notes for Guidance, CATCA 2003 as amended up to and including Finance Act 2024 (Wayback 2025-08-09)",
  "grade": "B", "kernel_parts": ["InheritanceTax", "TaxClass", "withLookback"],
  "unsupported": ["figures from Revenue's Notes for Guidance (the Act's text not read)", "aggregation across disponers in the same group", "agricultural and business relief, dwelling-house exemption, charities", "parent inheriting an absolute interest (Group A)"]}]
S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
p6_finish(S)

# ---- pass 16 (R1 Europe, 2026-11-21): year-in-force audit (tools/p16_rows.py, tools/yif16_rows.json) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p16_rows.py")).read())
p16_rows(S)
p6_finish(S)
