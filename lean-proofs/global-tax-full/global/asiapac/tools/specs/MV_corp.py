S = {'cc': 'MV', 'doc': "# Maldives 2025: income tax on companies and withholding on non-residents (1200)\n\nIncome Tax Act (Law 25/2019): the the build server copy is the consolidated text of 2026-08-31 (not the 2025 version) (B).\n* Companies: first MVR 500,000 of taxable income 0 %, 15 % above (banks 25 %, not modelled).\n* Withholding on non-residents' royalties, interest and fees: 10 %.", 'regimeName': 'Income tax on companies', 'unsupported': [['company', 'bank rate (25 %) not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'Income Tax Act (Law 25/2019) (company rates)', 'dated': '2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'Law 25/2019 (withholding on non-residents)', 'dated': '2025', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 0), (500000, 1500)], 'citStatute': 'Income Tax Act (Law 25/2019) (company rates)', 'wht': [{'kind': 'interest', 'rate': 1000, 'statute': 'Law 25/2019 (non-resident withholding)'}, {'kind': 'royalty', 'rate': 1000, 'statute': 'idem'}, {'kind': 'services', 'rate': 1000, 'statute': 'idem'}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['cit.citTax { profit := 1000000 } == 75000', 'wht.amount { kind := .interest, amount := 1000 } == 100', 'wht.amount { kind := .royalty, amount := 1000 } == 100', 'wht.amount { kind := .services, amount := 1000 } == 100']}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind='dividend', rate=1000, statute='ITA (Law 3/2019) s. 55 (a) (4) (10 %); s. 12 (a) exempts only dividends to residents'),
            dict(kind='interest', rate=1000, statute='ITA s. 55 (a) (3) (10 %; not on interest to a bank or non-bank financial institution accepted by MIRA)'),
            dict(kind='royalty', rate=1000, statute='ITA s. 55 (a) (2) (10 %)'),
            dict(kind='services', rate=1000, statute='ITA s. 55 (a) (5) technical service fees, (b) non-resident contractors (10 %)')]
_s5_wht_entry(statute='Income Tax Act (Law 3/2019) s. 55, s. 12 (Dhivehi consolidation, mvlaw.gov.mv)', grade='B',
    dated='wording of the mvlaw.gov.mv consolidation in force from 2026-08-31 (cmp20/world/B11-south-asia/mv/law/ita_294_current.txt); the 2025 wording not confirmed',
    unsupported=['interest paid to banks or non-bank financial institutions accepted by MIRA (s. 55 (a) (3)) not distinguished'])
S['guards'] = S['guards'] + ['wht.amount { kind := .dividend, amount := 1000 } == 100']

# --- R3 session 10 (2026-11-21): FT reviewer 6 item 3: the 2025 text is consolidation 1 (mvlaw.gov.mv 1313) ---
# Consolidation 1313 ("with the first amendment", Law 15/2021) is in force 2021-07-20 to 2026-08-30; consolidation 1326
# (second amendment) from 2026-08-31. Read in cmp20/world/B11-south-asia/mv/law/mvlaw294_1313.html (page JSON):
# s. 55 (a) 10 % on (1) rent of immovable property in the Maldives, (2) royalty, (3) interest (not to a bank / NBFI
# accepted by MIRA), (4) dividend, (5) technical service fee, (6) commission, (7) entertainers, (8) R&D, (10) insurance
# premium; (a) (9) contractors removed by Law 15/2021; s. 55 (b) payments to a non-resident contractor 5 %; (1-b) a payment
# under both (a) and (b) is taken under (b). s. 12 (a) exempts only dividends of a resident company to a resident.
_MV10 = 'ITA (Law 25/2019) consolidation 1 (mvlaw.gov.mv 1313, in force 2021-07-20 to 2026-08-30)'
S['wht'] = [dict(kind='dividend', rate=1000, statute=_MV10 + ' s. 55 (a) (4): 10 %; s. 12 (a) exempts only dividends to residents'),
            dict(kind='interest', rate=1000, statute=_MV10 + ' s. 55 (a) (3): 10 % (not on interest to a bank or NBFI accepted by MIRA)'),
            dict(kind='royalty', rate=1000, statute=_MV10 + ' s. 55 (a) (2): 10 %'),
            dict(kind='rent', rate=1000, statute=_MV10 + ' s. 55 (a) (1): 10 % on rent of immovable property in the Maldives'),
            dict(kind='services', rate=1000, statute=_MV10 + ' s. 55 (a) (5): 10 % on technical service fees')]
_s5_wht_entry(statute='Income Tax Act (Law 25/2019) s. 55 (a), (b), s. 12 (a) (mvlaw.gov.mv consolidation 1313)', grade='A',
    dated='consolidation 1 (with Law 15/2021), in force 2021-07-20 to 2026-08-30: the whole of 2025 (consolidation 2, 1326, from 2026-08-31)',
    unsupported=['interest paid to banks or non-bank financial institutions accepted by MIRA (s. 55 (a) (3)) not distinguished',
                 'payments to a non-resident contractor: 5 % in 2025 (s. 55 (b), taking precedence under (1-b)); the services kind is read as a technical service fee (10 %)'])
S['guards'] = S['guards'] + ['wht.amount { kind := .rent, amount := 1000 } == 100']
