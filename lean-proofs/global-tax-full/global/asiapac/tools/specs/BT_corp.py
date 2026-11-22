S = {'cc': 'BT', 'doc': '# Bhutan 2025: corporate income tax (1200)\n\nIncome Tax Act 2001 (fourth edition, `cmp20/world/B11-south-asia/bt/law/…2001_Fourth-Edition.txt`); the Income Tax Act\n2025 comes into force on the 13th day of the 11th month of the Wood Female Snake year (January 2026), so 2025 is under\nthe 2001 Act. Part I: corporate income tax 30 % (B: rate clause not re-located). TDS on non-residents: not reached (C).', 'regimeName': 'Corporate income tax', 'unsupported': [], 'taxes': [{'oecd': '1200', 'tax': 'Corporate income tax', 'statute': 'ITA 2001 Part I (corporate income tax)', 'dated': 'income year 2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'ITA 2001; Rules', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['not located']}], 'sched': [(0, 3000)], 'citStatute': 'ITA 2001 Part I (corporate income tax)', 'guards': ['cit.citTax { profit := 1000000 } == 300000']}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind='dividend', rate=1000, statute='ITA 2001 Part I s. 45.2 (d) (companies under limited tax liability), Part IV s. 13.2 (10 %, final)'),
            dict(kind='interest', rate=500, statute='ITA 2001 Part I s. 45.2 (c), Part IV s. 14.2 (5 %, final)'),
            dict(kind='royalty', rate=500, statute='ITA 2001 Part I s. 45.2 (c), Part IV s. 15.2 (5 %, final)'),
            dict(kind='services', rate=300, statute='ITA 2001 Part I s. 45.2 (b): contractors and consultants 3 % of the contract value; Part IV s. 18.2 (3 %, final)')]
S['whtName'] = 'Tax deducted at source from persons under limited tax liability (ITA 2001)'
_s5_wht_entry(tax='Tax deducted at source from persons under limited tax liability (dividends 10 %, interest and royalties 5 %, contractors and consultants 3 %)',
    statute='Income Tax Act of the Kingdom of Bhutan 2001 (Fourth Edition, as amended to 2020) Part I s. 45.2, Part IV ss. 13.2, 14.2, 15.2, 18.2',
    dated='in force to 31 Dec 2025 (ITA 2025 ss. 2-4: the new Act from 1 Jan 2026)', grade='A', kernel_parts=['Wht'],
    unsupported=['interest paid by financial institutions to Bhutanese citizens abroad (s. 14.2 applies to non-citizens) not distinguished'])
S['guards'] = S['guards'] + ['wht.amount { kind := .dividend, amount := 1000 } == 100', 'wht.amount { kind := .services, amount := 1000 } == 30']
