S = {'cc': 'SB', 'doc': '# Solomon Islands 2025: company tax (1200)\n\nIncome Tax Act (Cap. 123) (`sb/law/ita.txt`): rates as read by the registry (B): resident companies 30 %, non-resident 35 %.\nNon-resident withholding: not reached (C).', 'regimeName': 'Income tax on companies', 'unsupported': [], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'Income Tax Act (Cap. 123) Schedule (resident companies)', 'dated': '2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'Income Tax Act (Cap. 123)', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['rates not located']}], 'sched': [(0, 3000)], 'citStatute': 'Income Tax Act (Cap. 123) Schedule (resident companies)', 'guards': ['cit.citTax { profit := 1000000 } == 300000']}
# --- R3 session 4 (2026-11-21): rates read in the Income Tax Act (Cap. 123) Reprint as in force at 5 February 2024 ---
S['doc'] = '''# Solomon Islands 2025: company tax (1200) and withholding on payments to non-residents

Source: Income Tax Act (Cap. 123), Reprint as in force at 5 February 2024 (Legislation Act 2023), copied by the 1.x SB
builder (`cmp20/world/B14-pacific/sb/law/ita.txt`; later amendments not checked).
* **s. 33 (1)**: chargeable income of a person other than an individual or a company not incorporated in Solomon Islands
  "charged at the rate of thirty cents for every dollar"; (2) companies not incorporated there 35 cents (not modelled).
* **s. 36 (1)**: a resident company deducts tax from dividends: (a) resident shareholders 20 %; (b) non-resident
  shareholders "the rate prescribed in section 33(1)": 30 %.
* **s. 34, Sixth Schedule** (non-resident withholding): interest 15 cents in the dollar; professional services 20 %;
  royalties 15 cents; management services 35 cents; lease of property 10 cents.'''
S['citStatute'] = 'Income Tax Act (Cap. 123) s. 33 (1) (30 cents in the dollar)'
S['taxes'] = [{'oecd': '1200', 'tax': 'Income tax on companies (30 %)', 'statute': 'Income Tax Act (Cap. 123) s. 33 (1)', 'dated': 'Reprint as in force at 5 February 2024; later amendments not checked', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['companies not incorporated in Solomon Islands 35 % (s. 33 (2)) and approved mining companies not modelled']},
              {'oecd': '1200/1100', 'tax': 'Withholding on payments to non-residents (dividends 30 %, interest and royalties 15 %, professional services 20 %)', 'statute': 'Income Tax Act (Cap. 123) ss. 34, 36 (1) (b), Sixth Schedule', 'dated': 'Reprint as in force at 5 February 2024', 'grade': 'A', 'kernel_parts': ['Wht'], 'unsupported': ['management services 35 cents taken under services at the professional-services rate 20 %']}]
S['wht'] = [dict(kind='dividend', rate=3000, statute='Income Tax Act (Cap. 123) s. 36 (1) (b), s. 33 (1) (30 %)'),
            dict(kind='interest', rate=1500, statute='Income Tax Act (Cap. 123) s. 34, Sixth Schedule (i) (15 cents in the dollar)'),
            dict(kind='royalty', rate=1500, statute='Income Tax Act (Cap. 123) s. 34, Sixth Schedule (iii) (15 cents in the dollar)'),
            dict(kind='services', rate=2000, statute='Income Tax Act (Cap. 123) s. 34, Sixth Schedule (ii) professional services (20 %)')]
S['whtName'] = 'Non-resident withholding tax (Cap. 123 s. 34, s. 36)'
S['guards'] = S['guards'] + ['wht.amount { kind := .dividend, amount := 1000 } == 300', 'wht.amount { kind := .interest, amount := 1000 } == 150']
