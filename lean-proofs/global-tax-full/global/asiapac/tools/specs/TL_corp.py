S = {'cc': 'TL', 'doc': '# Timor-Leste 2025: income tax on companies and withholding (1200)\n\nSource: Lei 8/2008 (Lei Tributária), Jornal da República 2008 n.º 26 (`cmp20/world/B03-asia-east-se/tl/law/jr2008_no26.txt`).\n* Income tax rate table: "No caso de uma pessoa colectiva 10%".\n* Withholding: royalties (art. 54), rent of land or buildings (art. 55), prizes (art. 56): "à taxa de 10%" of the gross;\n  payments to non-residents (art. 60) at the same rate.', 'regimeName': 'Imposto sobre o rendimento (pessoas colectivas)', 'unsupported': [], 'taxes': [{'oecd': '1200', 'tax': 'Imposto sobre o rendimento (pessoas colectivas)', 'statute': 'Lei 8/2008, tabela do imposto sobre o rendimento', 'dated': 'Lei 8/2008 (in force 2025)', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'Lei 8/2008 arts. 52-60', 'dated': 'Lei 8/2008 (in force 2025)', 'grade': 'A', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 1000)], 'citStatute': 'Lei 8/2008, tabela do imposto sobre o rendimento', 'wht': [{'kind': 'royalty', 'rate': 1000, 'statute': 'Lei 8/2008 art. 54'}, {'kind': 'rent', 'rate': 1000, 'statute': 'Lei 8/2008 art. 55'}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['cit.citTax { profit := 1000000 } == 100000', 'wht.amount { kind := .royalty, amount := 1000 } == 100', 'wht.amount { kind := .rent, amount := 1000 } == 100']}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind='dividend', rate=0, statute='Lei 8/2008 art. 29 (f): dividends are exempt income; art. 60 (1): withholding does not apply to amounts not subject to income tax'),
            dict(kind='interest', rate=1000, statute='Lei 8/2008 art. 49 (1) (g), art. 57 (10 % on Timor-Leste-source payments to non-residents)'),
            dict(kind='royalty', rate=1000, statute='Lei 8/2008 art. 49 (1) (g), art. 57 (10 %)'),
            dict(kind='services', rate=1000, statute='Lei 8/2008 art. 49 (1) (g) (management fees paid by a resident), art. 57 (10 %)'),
            dict(kind='rent', rate=1000, statute='Lei 8/2008 art. 57 (10 %)')]
_s5_wht_entry(statute='Lei 8/2008 arts. 29, 49, 57, 60 (Lei Tributária)', unsupported=['services performed outside Timor-Leste other than management fees are not Timor-Leste-source (art. 49): not distinguished'])
S['guards'] = S['guards'] + ['wht.amount { kind := .interest, amount := 1000 } == 100', 'wht.amount { kind := .dividend, amount := 1000 } == 0']
