S = {'cc': 'NZ', 'doc': '# New Zealand 2025-26: company tax and NRWT (1200)\n\nIncome Tax Act 2007: rates as read by the registry (B; the Wayback copy of Sch. 1 was not fetched in this package).\n* **Sch. 1 Part A cl. 2**: companies 28 %.\n* **subpart RF, Sch. 1 Part D**: NRWT on unimputed dividends 30 %, interest 15 %, royalties 15 %.', 'regimeName': 'Income tax on companies', 'unsupported': [['company', 'imputation credits, the approved issuer levy and the 15 % rate on fully imputed dividends not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'ITA 2007 Sch. 1 Part A cl. 2', 'dated': '2025-26', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'ITA 2007 subpart RF, Sch. 1 Part D', 'dated': '2025-26', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 2800)], 'citStatute': 'ITA 2007 Sch. 1 Part A cl. 2', 'wht': [{'kind': 'dividend', 'rate': 3000, 'statute': 'ITA 2007 Sch. 1 Part D cl. 3 (unimputed)'}, {'kind': 'interest', 'rate': 1500, 'statute': 'Sch. 1 Part D cl. 2'}, {'kind': 'royalty', 'rate': 1500, 'statute': 'Sch. 1 Part D cl. 2'}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['cit.citTax { profit := 1000000 } == 280000', 'wht.amount { kind := .dividend, amount := 1000 } == 300', 'wht.amount { kind := .interest, amount := 1000 } == 150', 'wht.amount { kind := .royalty, amount := 1000 } == 150']}

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

_s7_wht_entry(add_unsupported=['services to non-residents: non-resident contractors\' tax applies to contract payments for services performed in New Zealand, with the recipient taxed by return; services performed abroad are not NZ-sourced; neither read in the ITA 2007 text: kept grade C, not a cited zero'])

# --- R3 session 8 (2026-11-21): CIT B -> A. ITA 2007 Schedule 1 Part A clause 2, version as at 10 July 2026 via the Internet
# Archive (capture 20260719212644 of legislation.govt.nz/act/public/2007/97/en/latest/parts/DLM1523173/;
# nz/law/nz_ita2007_sch_wb20260719.html): "To the extent to which a company does not have a basic rate under clauses 3 to 9,
# the basic rate of income tax for the company on each dollar of the company's taxable income is 0.28." Amendment notes:
# clause 2 last amended 2011 (2011 No 63, 2010 No 27): the same text applies to the 2025-26 income year. Pre-change copy
# tools/bak8/NZ_corp.py.
for _t in S["taxes"]:
    if _t["oecd"] == "1200":
        _t["statute"] = "ITA 2007 Sch. 1 Part A cl. 2 (basic rate 0.28 for companies)"
        _t["dated"] = "legislation.govt.nz version as at 10 July 2026 (Internet Archive); cl. 2 unchanged since 2011, so in force for 2025-26"
        _t["grade"] = "A"
S["citStatute"] = "ITA 2007 Sch. 1 Part A cl. 2"
S["doc"] = S["doc"].replace("rates as read by the registry (B; the Wayback copy of Sch. 1 was not fetched in this package).", "company rate read in Sch. 1 Part A cl. 2 (version as at 10 July 2026 via the Internet Archive, unchanged since 2011: A, session 8); NRWT rates as read by the registry (B).")

# --- R3 session 12 (2026-11-21): year in force: NRWT rates read (ITA 2007 ss. RF 7, RF 8), 2024-25 and 2025-26 ---
S['doc'] = S['doc'].replace("NRWT rates as read by the registry (B).", "NRWT rates read in ss. RF 7 and RF 8 (session 12, A).").replace(
    "* **subpart RF, Sch. 1 Part D**: NRWT on unimputed dividends 30 %, interest 15 %, royalties 15 %.",
    "* **subpart RF**: s. RF 7 (2) general rate for NRWT \"payment x 0.15\" (interest, royalties); s. RF 8 (2) dividends not fully\n  imputed \"dividend payment x 0.3\".") + """

**Session 12 (year in force), withholding grade A.** Income Tax Act 2007, version as at 1 January 2026 (legislation.govt.nz
PDF `act/public/2007/97/en/2026-01-01.pdf`, Internet Archive 2026-03-19; extract `nz/law/nz_ita2007_RF7-RF9_v20260101.txt`):
s. RF 7 (general rate 0.15) carries no amendment note and s. RF 8 (dividends 0.3) none after 2017, so both rates applied
throughout 2024-25 and 2025-26: no split. Not modelled: approved issuer levy (s. RF 12, 0 % NRWT with 2 % levy), treaty
rates, fully imputed dividends with supplementary dividends (s. RF 9: 15 % / 0 %), non-resident contractors' tax."""
S['wht'] = [dict(w) for w in S['wht']]
for _w in S['wht']:
    _w['statute'] = {'dividend': 'ITA 2007 s. RF 8 (2) (dividend not fully imputed, x 0.3)', 'interest': 'ITA 2007 s. RF 7 (2) (x 0.15)',
                     'royalty': 'ITA 2007 s. RF 7 (2) (x 0.15)'}[_w['kind']]
for _t in S['taxes']:
    if _t['oecd'] == '1200/1100':
        _t['statute'] = "ITA 2007 subpart RF: ss. RF 7 (2) (0.15), RF 8 (2) (0.3)"
        _t['dated'] = ("2025: ITA 2007 version as at 1 January 2026 (legislation.govt.nz PDF, Internet Archive 2026-03-19): RF 7 without amendment "
                       "notes, RF 8 notes to 2017: the same in 2024-25 and 2025-26 (no split); session 12 year in force")
        _t['grade'] = 'A'
        _t['unsupported'] = list(_t.get('unsupported', [])) + ["approved issuer levy (RF 12), treaty rates and fully imputed dividends (RF 9) not modelled"]
