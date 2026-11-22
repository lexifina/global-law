S = dict(cc="LV", fam="Corporate",
doc=r'''# Latvia 2025: uzņēmumu ienākuma nodoklis on distributed profit (1200)

Source: Uzņēmumu ienākuma nodokļa likums, likumi.lv "Redakcija uz" 01.07.2025 (`lv/law/uin_2025-07-01.html`; sha256 in
`law/SHA256SUMS`).
* **4. pants (9)**: "Nosakot taksācijas perioda ar uzņēmumu ienākuma nodokli apliekamo bāzi, ar uzņēmumu ienākuma
  nodokli apliekamā objekta vērtību dala ar koeficientu 0,8."
* **4. pants (1)** (rate): "Nodokļa likme ir 20 procenti no aprēķinātās ar nodokli apliekamās bāzes".
The tax falls on distributed profit (dividends, deemed distributions), not on the year's accounting profit: the base is
the dividends paid grossed up by 0,8.
''',
lean=r'''
/-- 4. pants (9): the object's value divided by 0,8. -/
def grossedBase (paid : Int) : Int := divR .down (pos paid * 10) 8

/-- 4. pants (1): 20 % of the grossed-up base. -/
def citOnDistribution (paid : Int) : Int := divR .down (2000 * grossedBase paid) BP
''',
families=[("1200 UIN (sadalītā peļņa)", [".cit"],
  "(if g.entity == .company && g.company.dividendsPaid > 0 then [charge .cit \"Uzņēmumu ienākuma nodoklis (sadalītā peļņa)\" g.company.dividendsPaid grossedBase (fun b => divR .down (2000 * b) BP) (statute := \"UIN likums 4. pants (1) (20 %), (9) (/ 0,8)\")] else [])")],
notes=["LV 1200: distribution tax (no tax on retained profit)"],
unsupported=[("g.entity == .company", "deemed distributions (non-business expenses, bad debts, loans to related parties, 4. pants (2) 2)) and the dividend reduction for earlier taxed profit not modelled"),
  ("g.entity == .company && !g.company.paymentsAbroad.isEmpty", "withholding on payments to non-residents (5. pants: 20 % on management fees, payments to low-tax jurisdictions) not modelled")],
guards=["grossedBase 80000 == 100000", "citOnDistribution 80000 == 20000", "citOnDistribution 0 == 0"],
taxes=[{"oecd": "1200", "tax": "Uzņēmumu ienākuma nodoklis (distributed profit)", "statute": "UIN likums 4. pants (1), (9)", "dated": "likumi.lv redakcija uz 01.07.2025", "grade": "A", "kernel_parts": ["charge (distribution base)"], "unsupported": ["deemed distributions", "dividend reductions (6. pants)"]},
 {"oecd": "1200", "tax": "Withholding on payments to non-residents", "statute": "UIN likums 5. pants", "dated": "likumi.lv redakcija uz 01.07.2025", "grade": "B", "status": "not modelled (read in part: 20 % on management and consultancy fees)", "kernel_parts": [], "unsupported": ["no withholding on dividends, interest and royalties to non-low-tax residents (structure only)"]}])

# ---- pass 8 (R1 Europe, 2026-11-21): withholding under kernel 2.3.0, P5/P6 gaps, P7 surcharges, carry-overs (tools/p8_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
p8_rows(S)
p6_finish(S)

# ---- pass 9 (R1 Europe, 2026-11-21): remaining withholding, carry-overs, B -> A, P5/P6 (tools/p9_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
p9_rows(S)
p6_finish(S)
