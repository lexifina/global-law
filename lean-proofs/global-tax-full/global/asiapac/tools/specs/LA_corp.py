S = {'cc': 'LA', 'doc': '# Lao PDR 2025: profit tax (1200)\n\nLaw on Income Tax No. 67/NA (2019): not on the build server (the 1.x `rescue` folder only); rate from the registry reading (B).\n* Profit tax 20 % (lump-sum regime for small businesses not modelled). Withholding on non-residents: not reached (C).', 'regimeName': 'Profit tax', 'unsupported': [['company', 'lump-sum small-business regime and mining rates not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Profit tax', 'statute': 'Law on Income Tax No. 67/NA (2019)', 'dated': '2019 law', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding on non-residents', 'statute': 'Law on Income Tax No. 67/NA', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['text not reached']}], 'sched': [(0, 2000)], 'citStatute': 'Law on Income Tax No. 67/NA (2019)', 'guards': ['cit.citTax { profit := 1000000 } == 200000']}

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

_L = "Law on Income Tax No. 67/NA (2019)"
S['wht'] = [dict(kind='dividend', rate=1000, statute=_L + ' art. 46 (4), art. 49 (2) (10 % of the gross), art. 50 (the payer deducts)'),
            dict(kind='interest', rate=1000, statute=_L + ' art. 46 (4), art. 49 (2) (10 % of the gross), art. 50'),
            dict(kind='royalty', rate=500, statute=_L + ' art. 46 (5), art. 49 (3) (5 % of the gross: copyrights, patents, trade marks), art. 50'),
            dict(kind='services', toCompany=True, rate=300, statute=_L + ' art. 12 (2) (non-residents without an enterprise in Laos), art. 13 (2), art. 14 (2) (deemed profit 15 % of revenue for commerce and services), art. 15 (20 %), art. 20 (the purchaser declares): 3 % of the gross'),
            dict(kind='services', toCompany=False, rate=1000, statute=_L + ' art. 46 (2) (remuneration of board members, artists, athletes and others), art. 49 (2) (10 %), art. 50')]
S['whtName'] = 'Income tax withheld from non-residents (Law on Income Tax 2019)'
_s7_wht_entry(tax='Income tax withheld from non-residents (dividends and interest 10 %, royalties 5 %, services: deemed profit tax 3 % to companies, 10 % to individuals)',
    statute=_L + ' arts. 12-15, 20, 32, 46-50', dated='in force from 2020 (art. 79); no later amendment listed on the Lao Trade Portal legal-document index (checked 2026-11-21)', grade='A', kernel_parts=['Wht'],
    drop_unsupported=['text not reached'],
    add_unsupported=['dividends, interest and royalties to foreign companies are taken under the non-resident personal income tax (arts. 32, 46-49: persons and organisations not conducting business in Laos)', 'services to individuals read as "remuneration ... and others" (art. 46 (2)); consultancy fees are 5 % for residents (art. 39 (4)) and not listed for non-residents', 'OCR text (Lao, tessdata_fast) read; interest is limited to loan interest (art. 46 (4))'])
S['guards'] = S.get('guards', []) + ['wht.amount { kind := .services, amount := 1000 } == 30', 'wht.amount { kind := .royalty, amount := 1000, toCompany := false } == 50']
