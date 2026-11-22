S = {'cc': 'AF', 'regimeName': 'Income tax of legal persons', 'sched': [(0, 2000)], 'citStatute': 'Income Tax Law 2009 art. 4 (1) (legal persons 20 %)', 'wht': [{'kind': 'dividend', 'rate': 2000, 'statute': 'ITL 2009 art. 46 (1) 2 (20 %)'}, {'kind': 'interest', 'rate': 2000, 'statute': 'ITL 2009 art. 46 (1) 2 (20 %)'}, {'kind': 'royalty', 'rate': 2000, 'statute': 'ITL 2009 art. 46 (1) 2 (20 %)'}, {'kind': 'services', 'rate': 2000, 'statute': 'ITL 2009 art. 46 (1) 2 (service charges 20 %)'}], 'whtName': 'Withholding tax', 'doc': '# Afghanistan 2025: income tax of legal persons and withholding (1200)\n\nSource: Income Tax Law 2009, MoF consolidation "Version: December 2016" (`itl.txt`; 2025 application not confirmed: grade B).\n* **art. 4 (1)**: "The income tax of legal persons shall be 20" percent.\n* **art. 46 (1) 2**: legal persons withhold "twenty percent tax from interest, dividends, royalties, prizes, … and service\n  charges".', 'unsupported': [['company', 'the business receipts tax (5112) is booked in Consumption; BRT paid is deductible (not modelled)']], 'guards': ['cit.citTax { profit := 1000000 } == 200000', 'wht.amount { kind := .royalty, amount := 1000 } == 200'], 'taxes': [{'oecd': '1200', 'tax': 'Income tax of legal persons', 'statute': 'ITL 2009 art. 4 (1)', 'dated': 'MoF consolidation December 2016', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['2025 application under the de facto authorities not confirmed']}, {'oecd': '1200/1100', 'tax': 'Withholding tax', 'statute': 'ITL 2009 art. 46 (1) 2', 'dated': 'December 2016', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': ['contractor withholding (art. 72)']}]}


# --- R3 session 11 (2026-11-21): year-in-force audit: downgraded to C (old content kept in S['_pre11']) ---
_N11 = "session 11 year-in-force audit: the only text is the MoF consolidation 'Version: December 2016' of the Income Tax Law 2009; no 2025 version, amendment list or 2025 official source reached (the 2025 application of the 2016 text is not established): grade C"
S['_pre11'] = {k: S.get(k) for k in ('sched', 'wht', 'guards', 'extra_lean', 'extra_run', 'extra_covers', 'taxes', 'unsupported')}
for _k in ['sched', 'wht']:
    S[_k] = [] if _k != 'extra_lean' else ''
S['guards'] = [g for g in S.get('guards', []) if g.startswith('absent')]
S['unsupported'] = [u for u in S.get('unsupported', []) if not True] + [['company', _N11]]
for _t in S['taxes']:
    if _t['oecd'] in ['1200', '1200/1100']:
        _t.update(grade='C', dated='not modelled (' + _N11 + ')', kernel_parts=[], unsupported=[_N11])
