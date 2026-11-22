S = {'cc': 'SG', 'doc': '# Singapore YA 2025: corporate income tax and withholding (1200)\n\nIncome Tax Act 1947: the SSO historical text was not fetched for this package (laptop route works; deferred to the upgrade\npass); rates from IRAS tables (B).\n* **s. 43 (1) (a)**: 17 %. **s. 43 (6)**: partial exemption, 75 % of the first $10,000 and 50 % of the next $190,000 of\n  chargeable income exempt: modelled as effective bands 4.25 % / 8.5 % / 17 %.\n* **s. 45, s. 12 (7)**: interest 15 %, royalties 10 % (s. 43 (3A)), services 17 % to non-residents; no tax on dividends.', 'regimeName': 'Corporate income tax', 'unsupported': [['company', 'YA 2025 50 % CIT rebate (cap $40,000), start-up exemption (s. 43 (6A)) and the MNE minimum tax not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Corporate income tax', 'statute': 'ITA 1947 s. 43 (1) (a), s. 43 (6)', 'dated': 'YA 2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'ITA 1947 s. 45', 'dated': 'YA 2025', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 425), (10000, 850), (200000, 1700)], 'citStatute': 'ITA 1947 s. 43 (1) (a), s. 43 (6)', 'wht': [{'kind': 'interest', 'rate': 1500, 'statute': 'ITA s. 45, s. 12 (6)'}, {'kind': 'royalty', 'rate': 1000, 'statute': 'ITA s. 45, s. 12 (7), s. 43 (3A)'}, {'kind': 'services', 'rate': 1700, 'statute': 'ITA s. 45, s. 12 (7)'}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['cit.citTax { profit := 1000000 } == 152575', 'wht.amount { kind := .interest, amount := 1000 } == 150', 'wht.amount { kind := .royalty, amount := 1000 } == 100', 'wht.amount { kind := .services, amount := 1000 } == 170']}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind='dividend', rate=0, statute='ITA 1947 s. 13 (1) (za): dividends paid by a Singapore-resident company are exempt'),
            dict(kind='interest', rate=1500, statute='ITA 1947 s. 12 (6), s. 43 (3) (a), s. 45 (1) (a) (iii) (15 %)'),
            dict(kind='royalty', rate=1000, statute='ITA 1947 s. 12 (7) (a), (b), s. 43 (3A), s. 45A (10 %)'),
            dict(kind='services', toCompany=False, rate=2400, statute='ITA 1947 s. 12 (7) (c) management fees, s. 45A, s. 45 (1) (a) (i) (24 % for individuals)'),
            dict(kind='services', rate=1700, statute='ITA 1947 s. 12 (7) (c) management fees, s. 45A, s. 45 (1) (a) (ii) (17 %)')]
_s5_wht_entry(statute='ITA 1947 (2020 Rev. Ed.) s. 12 (6)-(7), s. 13 (1) (za), s. 43 (3), (3A), s. 45, s. 45A',
    dated='SSO informal consolidation in force 1-14 Nov 2024 (Wayback 20241206192918, sg/law/sg_ita1947_20241101_wb.pdf): YA 2025', grade='A',
    unsupported=['technical assistance under s. 12 (7) (b) is at 10 % with royalties; services are taken as management fees (s. 12 (7) (c)); services performed outside Singapore not distinguished'])
S['guards'] = S['guards'] + ['wht.amount { kind := .services, amount := 1000, toCompany := false } == 240', 'wht.amount { kind := .services, amount := 1000 } == 170', 'wht.amount { kind := .dividend, amount := 1000 } == 0']
