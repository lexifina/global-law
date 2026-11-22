S = {'cc': 'AU', 'doc': '# Australia 2024-25: company tax and withholding on non-residents (1200)\n\nIncome Tax Rates Act 1986 and the Income Tax (Dividends, Interest and Royalties Withholding Tax) Act 1974: rates as read by the\nregistry from legislation.gov.au (B: compilations not fetched in this package).\n* **ITRA s. 23 (2)**: 30 %; **s. 23AA**: base rate entities (aggregated turnover < $50 m) 25 % (flag `baseRate`).\n* **DIRWT Act s. 7**: unfranked dividends 30 %, interest 10 %, royalties 30 %.', 'regimeName': 'Income tax on companies', 'unsupported': [['company', 'franking credits, the global and domestic minimum tax and thin capitalisation not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'ITRA 1986 s. 23 (2), s. 23AA', 'dated': '2024-25 income year', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'Income Tax (Dividends, Interest and Royalties Withholding Tax) Act 1974 s. 7', 'dated': '2024-25 income year', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 3000)], 'citStatute': 'ITRA 1986 s. 23 (2), s. 23AA', 'wht': [{'kind': 'dividend', 'rate': 3000, 'statute': 'DIRWT Act 1974 s. 7 (a) (unfranked)'}, {'kind': 'interest', 'rate': 1000, 'statute': 's. 7 (b)'}, {'kind': 'royalty', 'rate': 3000, 'statute': 's. 7 (c)'}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['(cit { profit := 1000000 }).citTax { profit := 1000000 } == 300000', 'wht.amount { kind := .dividend, amount := 1000 } == 300', 'wht.amount { kind := .interest, amount := 1000 } == 100', 'wht.amount { kind := .royalty, amount := 1000 } == 300'], 'rateByFlag': [('baseRate', 2500)]}

# ---- FT review (2026-11-21): ITRA 1986 s. 23 (2), ss. 23AA-23AB read in the compilation in force on 2025-07-01 ----
S["doc"] += '''

FT review (2026-11-21): **Income Tax Rates Act 1986, Compilation No. 65 (28 March 2025, in force on 2025-07-01)**,
legislation.gov.au C2004A03348 epub (`au/law/fedleg/itra_20250701.html`, sha256 in `SHA256SUMS`):
* **s. 23 (2)**: "The rate of tax in respect of the taxable income of a company is: (a) if the company is a base rate
  entity for a year of income—25%; or (b) otherwise—30%".
* **s. 23AA**: "An entity is a base rate entity for a year of income if: (a) no more than 80% of its assessable income
  for the year of income is base rate entity passive income; and (b) its aggregated turnover ... is less than
  $50 million."
* **s. 23AB (1)**: passive income includes "(a) a distribution ... by a corporate tax entity ..., other than a
  non-portfolio dividend", "(d) interest ..., royalties and rent", "(f) a net capital gain".
The test is applied to the entity's own fields: turnover for aggregated turnover (no connected entities), assessable
income = turnover + dividends received, passive income = dividends received from stakes under 10 % (portfolio; ITAA
1936 s. 317: non-portfolio = at least 10 %). Flags `baseRate` / `notBaseRate` override the test.'''
S["rateOfLean"] = '''/-- ITRA 1986 s. 23AA (b): aggregated turnover less than $50 million. -/
def breTurnover : Int := 50000000
/-- s. 23AB (1) (a): portfolio dividends (stake under 10 %, ITAA 1936 s. 317) are passive; the entity carries no other
passive income (interest, rent, royalties, gains received). -/
def passiveIncome (co : Company) : Int := if co.participationBp < 1000 then pos co.dividendsReceived else 0
/-- s. 23AA: a base rate entity (flags `baseRate` / `notBaseRate` override the test on the entity's fields). -/
def baseRateEntity (co : Company) : Bool :=
  if co.flags.contains "baseRate" then true else if co.flags.contains "notBaseRate" then false else
  decide (co.turnover < breTurnover) && decide (passiveIncome co * 100 ≤ 80 * (pos co.turnover + pos co.dividendsReceived))
/-- s. 23 (2): 25 % for a base rate entity, otherwise 30 %. -/
def rateOf (co : Company) : Int := if baseRateEntity co then 2500 else 3000'''
S["citStatute"] = "ITRA 1986 s. 23 (2), ss. 23AA-23AB (Compilation No. 65, in force 2025-07-01)"
S["guards"] = S["guards"] + [
  "-- s. 23 (2) (a), s. 23AA (b): the $50 million edge",
  "(cit { turnover := 49999999, profit := 1000000 }).citTax { turnover := 49999999, profit := 1000000 } == 250000",
  "(cit { turnover := 50000000, profit := 1000000 }).citTax { turnover := 50000000, profit := 1000000 } == 300000",
  "-- s. 23AA (a): more than 80 % portfolio dividends is not a base rate entity",
  "(cit { turnover := 100, profit := 1000, dividendsReceived := 1000, participationBp := 500 }).citTax { turnover := 100, profit := 1000, dividendsReceived := 1000, participationBp := 500 } == 300",
  "(cit { turnover := 100, profit := 1000, dividendsReceived := 1000, participationBp := 1000 }).citTax { turnover := 100, profit := 1000, dividendsReceived := 1000, participationBp := 1000 } == 250",
  "(cit { turnover := 1000, profit := 1000, flags := [\"notBaseRate\"] }).citTax { turnover := 1000, profit := 1000 } == 300"]
for _t in S["taxes"]:
    if _t["oecd"] == "1200":
        _t["statute"] = "ITRA 1986 s. 23 (2), ss. 23AA-23AB"
        _t["dated"] = "Compilation No. 65 (28 March 2025), in force on 2025-07-01 (legislation.gov.au C2004A03348)"
        _t["grade"] = "A"
        _t["unsupported"] = _t.get("unsupported", []) + ["aggregated turnover = the entity's own turnover (no connected entities or affiliates); passive income = portfolio dividends only"]
S["unsupported"] = S["unsupported"] + [["company", "base rate entity test on the entity's own turnover and portfolio dividends (no connected entities; interest, rent, royalties and gains received not in the entity)"]]
# the pass-2 guard took a company without turnover as a 30 % company; under s. 23AA it is a base rate entity
S["guards"] = [("(cit { turnover := 60000000, profit := 1000000 }).citTax { turnover := 60000000, profit := 1000000 } == 300000"
                if g == "(cit { profit := 1000000 }).citTax { profit := 1000000 } == 300000" else g) for g in S["guards"]]

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

_s7_wht_entry(add_unsupported=['services to non-residents: no final withholding read; foreign resident withholding (TAA 1953 Sch. 1 s. 12-315) covers only payments prescribed by regulation (works, entertainment and sport, casino junkets); other Australian-source services income is taxed by assessment on the recipient (ITAA 1997 s. 6-5 (3)): kept grade C, not a cited zero'])

# ---- R3 session 9 (2026-11-21): DIRWT Act B -> A. Pre-change copy: tools/bak9/AU_corp.py.
# legislation.gov.au: title C2004A00086, versions API: compilation C2007C00596 in force from 2007-09-24 with no end date
# (isLatest), i.e. the text in force throughout 2025; epub text au/law/fedleg/dirwt1974_C2007C00596_asat20250701.html.
S["wht"] = [{"kind": "dividend", "rate": 3000, "statute": "Income Tax (Dividends, Interest and Royalties Withholding Tax) Act 1974 s. 7 (a): 30 % on income to which ITAA 1936 s. 128B (4) applies (dividends; franked parts exempt, s. 128B (3) (ga))"},
            {"kind": "interest", "rate": 1000, "statute": "DIRWT Act 1974 s. 7 (b): 10 % on income to which ITAA 1936 s. 128B (5) applies (interest)"},
            {"kind": "royalty", "rate": 3000, "statute": "DIRWT Act 1974 s. 7 (c): 30 % on income to which ITAA 1936 s. 128B (5A) applies (royalties)"}]
_s7_wht_entry(grade="A", statute="Income Tax (Dividends, Interest and Royalties Withholding Tax) Act 1974 s. 7 (a)-(c); ITAA 1936 s. 128B (4), (5), (5A)",
              dated="compilation C2007C00596 (legislation.gov.au), in force from 2007-09-24 with no later compilation: the text in force in 2025")
