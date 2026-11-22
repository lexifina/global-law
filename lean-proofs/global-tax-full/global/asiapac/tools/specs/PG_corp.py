S = {'cc': 'PG', 'doc': '# Papua New Guinea 2025: company tax and withholding (1200)\n\nIncome Tax Act 1959 (PacLII copy `pg_ita1959116`, not a 2025 consolidation) and the Income Tax (Rates) Act: rates as read by\nthe registry (B). Resident companies 30 %; dividend withholding 17 %, interest 15 %, royalties 10 % (30 % to associates).', 'regimeName': 'Income tax on companies', 'unsupported': [['company', 'non-resident company rate (48 %) and resource project rates not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'Income Tax Act 1959 / Income Tax (Rates) Act (resident companies)', 'dated': '2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'Income Tax Act 1959 Divs. 11A-11C', 'dated': '2025', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 3000)], 'citStatute': 'Income Tax Act 1959 / Income Tax (Rates) Act (resident companies)', 'wht': [{'kind': 'dividend', 'rate': 1700, 'statute': 'ITA 1959 Div. 11A (dividend withholding)'}, {'kind': 'interest', 'rate': 1500, 'statute': 'Div. 11B'}, {'kind': 'royalty', 'rate': 1000, 'statute': 'Div. 11C (non-associates)'}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['cit.citTax { profit := 1000000 } == 300000', 'wht.amount { kind := .dividend, amount := 1000 } == 170', 'wht.amount { kind := .interest, amount := 1000 } == 150', 'wht.amount { kind := .royalty, amount := 1000 } == 100']}

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

S['wht'] = S['wht'] + [dict(kind='services', rate=1700, statute='Income Tax, Dividend (Withholding) Tax and Interest (Withholding) Tax Rates Act 1984 s. 6B (17 % of the gross taxable management fee); ITA 1959 Div. III.14C ss. 196R-196U')]
_s7_wht_entry(add_unsupported=['services abroad are taken as management fees (ITA 1959 s. 4 definition; Div. III.14C); the Rates Act text is the PacLII consolidation (Wayback 20241027212428), its date not printed; ITA 2025 (No. 11 of 2025) not in force for 2025'])
S['guards'] = S['guards'] + ['wht.amount { kind := .services, amount := 1000 } == 170']
