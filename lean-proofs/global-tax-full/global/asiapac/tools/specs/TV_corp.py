S = {'cc': 'TV', 'doc': '''# Tuvalu 2025: company income tax (1200) and non-resident withholding

Source: Income Tax Act (Cap. 26.16), 2022 Revised Edition, copied by the 1.x TV builder
(`cmp20/world/B14-pacific/tv/law/1992-0005_2.txt`; amendments after the 2022 Revised Edition not checked).
* **s. 5, Schedule 6 para. 1 (i)**: "Taxable income of any resident company (other than those specified elsewhere on
  this schedule)" 30 %; (j) a further company line at 40 % (its qualifier is cut in the text: taken as non-resident
  companies, not modelled).
* **s. 37, Schedule 5 Part A (2)**: non-resident withholding income: (a) dividend 15 %; (b) service fees 15 %;
  (c) specified alimony 30 %; (d) gross income other than dividends, service fees or alimony (interest, royalties) 15 %.''',
 'regimeName': 'Income tax on companies', 'sched': [(0, 3000)], 'citStatute': 'Income Tax Act (Cap. 26.16) s. 5, Schedule 6 para. 1 (i) (30 %)',
 'unsupported': [],
 'taxes': [{'oecd': '1200', 'tax': 'Income tax on resident companies (30 %)', 'statute': 'Income Tax Act (Cap. 26.16) s. 5, Schedule 6 para. 1 (i)', 'dated': '2022 Revised Edition; later amendments not checked', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['Schedule 6 para. 1 (j) 40 % company line not modelled']},
           {'oecd': '1200/1100', 'tax': 'Non-resident withholding (15 % dividends, service fees, interest, royalties)', 'statute': 'Income Tax Act (Cap. 26.16) s. 37, Schedule 5 Part A (2)', 'dated': '2022 Revised Edition', 'grade': 'A', 'kernel_parts': ['Wht'], 'unsupported': []}],
 'wht': [dict(kind='dividend', rate=1500, statute='Income Tax Act (Cap. 26.16) Schedule 5 Part A (2) (a) (15 %)'),
         dict(kind='services', rate=1500, statute='Income Tax Act (Cap. 26.16) Schedule 5 Part A (2) (b) (15 %)'),
         dict(kind='interest', rate=1500, statute='Income Tax Act (Cap. 26.16) Schedule 5 Part A (2) (d) (15 %)'),
         dict(kind='royalty', rate=1500, statute='Income Tax Act (Cap. 26.16) Schedule 5 Part A (2) (d) (15 %)')],
 'whtName': 'Non-resident withholding (Cap. 26.16 Schedule 5)',
 'guards': ['cit.citTax { profit := 1000000 } == 300000', 'wht.amount { kind := .dividend, amount := 1000 } == 150'],
 'absent': []}


# --- R3 session 11 (2026-11-21): year-in-force audit: downgraded to C (old content kept in S['_pre11']) ---
_N11 = 'session 11 year-in-force audit: Income Tax (Cap. 26.16) 2022 Revised Edition with later amendments not checked; no 2025 version or official 2025 source reached: grade C'
S['_pre11'] = {k: S.get(k) for k in ('sched', 'wht', 'guards', 'extra_lean', 'extra_run', 'extra_covers', 'taxes', 'unsupported')}
for _k in ['sched', 'wht']:
    S[_k] = [] if _k != 'extra_lean' else ''
S['guards'] = [g for g in S.get('guards', []) if g.startswith('absent')]
S['unsupported'] = [u for u in S.get('unsupported', []) if not True] + [['company', _N11]]
for _t in S['taxes']:
    if _t['oecd'] in ['1200', '1200/1100']:
        _t.update(grade='C', dated='not modelled (' + _N11 + ')', kernel_parts=[], unsupported=[_N11])
