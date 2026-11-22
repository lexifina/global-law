S = {'cc': 'UK', 'fam': 'Corporate', 'doc': '# UK 2025: Corporation tax (1200) and withholding on payments abroad\n\nSource: legislation.gov.uk point in time 2025-07-01: FA 2021 ss. 6, 7; CTA 2010 ss. 18B, 18D; ITA 2007 ss. 874, 906 (`uk/law/*_2025-07-01.html`); sha256 in `law/SHA256SUMS`.\n* FA 2021 s. 6: the main rate "(b) is 25% for the financial year 2023" (later years charged at the same main rate by the annual Finance Acts, not read)\n* FA 2021 s. 7: "(a) the standard small profits rate is 19%, and (b) the standard marginal relief fraction is 3/200ths"\n* CTA 2010 s. 18D: "(a) the lower limit is £50,000, and (b) the upper limit is £250,000"; s. 18B: relief F × (U − A) × N/A\n* The marginal relief turns into a marginal schedule (no associated companies, N = A): 19 % to £50,000, 26.5 % from £50,000 to £250,000, 25 % above (at £250,000: 9 500 + 53 000 = 62 500 = 25 %)\n* ITA 2007 s. 874 (2): deduct income tax "at the basic rate"; s. 906 the same for royalties\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Corporation tax",\n    sched := Schedule.ofList [(0, 1900), (50000, 2650), (250000, 2500)] }\n\ndef wht : Wht :=\n  { name := "Income tax deducted at source (interest, royalties)", rules := [\n    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "ITA 2007 s. 874: income tax at the basic rate (20 %)" },\n    { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "ITA 2007 s. 906: income tax at the basic rate (20 %)" }] }\n\ndef citStatute : String := "FA 2021 s. 6 (main rate 25 %), s. 7 (small profits rate 19 %, marginal relief fraction 3/200); CTA 2010 Part 3A s. 18B, 18D (£50,000 / £250,000)"\n', 'families': [('1200 Corporation tax', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])\n       ++ (if g.entity == .company then wht.charges g.company else [])')], 'notes': ['UK 1200: legislation.gov.uk 2025-07-01'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 22750', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 250000', 'wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 20000', 'wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20000'], 'taxes': [{'oecd': '1200', 'tax': 'Corporation tax', 'statute': 'FA 2021 s. 6 (main rate 25 %), s. 7 (small profits rate 19 %, marginal relief fraction 3/200); CTA 2010 Part 3A s. 18B, 18D (£50,000 / £250,000)', 'dated': 'legislation.gov.uk 2025-07-01', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['FY2025 charge (annual Finance Act) not read', 'associated companies divide the limits (s. 18E)', 'loss restriction (CTA 2010 Part 7ZA) not modelled']}, {'oecd': '1200', 'tax': 'Income tax deducted at source (interest, royalties)', 'statute': 'ITA 2007 s. 874: income tax at the basic rate (20 %); ITA 2007 s. 906: income tax at the basic rate (20 %)', 'dated': 'legislation.gov.uk 2025-07-01', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': ['the basic rate (20 %) is set by the annual income tax charge (not read)', 'treaty and EU-derived exemptions out of scope']}]}

# ---- FT review (2026-11-21): CTA 2010 Part 7ZA restriction on carried-forward losses ----
S["doc"] += r'''
* **CTA 2010 Part 7ZA** (FT review 2026-11-21; legislation.gov.uk point in time 2025-07-01, `uk/law/cta2010_s269Z*_2025-07-01.html`):
  s. 269ZB (2), (5): carried-forward trade-loss deductions "may not exceed the relevant maximum", "the sum of— (a) 50% of
  the company's relevant trading profits ..., and (b) the company's trading profits deductions allowance"; s. 269ZF (1):
  relevant trading profits = qualifying trading profits "less" that allowance; s. 269ZW (2): a company not in a group has a
  "deductions allowance for the accounting period [of] £5,000,000". So losses brought forward are set off in full up to
  £5 m of profit and against 50 % of the excess (`lossFull`, `lossExcessBp`); s. 269ZD applies the same maximum to
  deductions from total profits.'''
S["lean"] = S["lean"].replace('''    sched := Schedule.ofList [(0, 1900), (50000, 2650), (250000, 2500)] }''', '''    sched := Schedule.ofList [(0, 1900), (50000, 2650), (250000, 2500)],
    lossFull := 5000000, lossExcessBp := 5000 }''', 1)
S["lean"] = S["lean"].replace('"FA 2021 s. 6 (main rate 25 %), s. 7 (small profits rate 19 %, marginal relief fraction 3/200); CTA 2010 Part 3A s. 18B, 18D (£50,000 / £250,000)"\n', '"FA 2021 s. 6 (main rate 25 %), s. 7 (small profits rate 19 %, marginal relief fraction 3/200); CTA 2010 Part 3A s. 18B, 18D (£50,000 / £250,000); Part 7ZA ss. 269ZB, 269ZD, 269ZF, 269ZW (losses: £5 m + 50 %)"\n', 1)
assert "lossFull := 5000000" in S["lean"]
S["guards"] = S["guards"] + ["-- CTA 2010 ss. 269ZB, 269ZW: £5 m allowance, then 50 % of the excess",
  "cit.taxableProfit { profit := 12000000, lossesForward := 20000000 } == 3500000",
  "cit.taxableProfit { profit := 4000000, lossesForward := 20000000 } == 0",
  "cit.taxableProfit { profit := 12000000, lossesForward := 1000000 } == 11000000"]
for _t in S["taxes"]:
    if _t["tax"] == "Corporation tax":
        _t["statute"] += "; CTA 2010 Part 7ZA (ss. 269ZB, 269ZD, 269ZF, 269ZW)"
        _t["unsupported"] = [u for u in _t["unsupported"] if "7ZA" not in u] + ["groups share one £5 m deductions allowance (s. 269ZR): the entity taken as not in a group"]

# ---- pass 8 (R1 Europe, 2026-11-21): withholding under kernel 2.3.0, P5/P6 gaps, P7 surcharges, carry-overs (tools/p8_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
p8_rows(S)
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
