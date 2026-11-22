S = {'cc': 'VN', 'doc': '# Viet Nam 2025: corporate income tax and foreign contractor tax (1200)\n\nLuật Thuế TNDN 67/2025/QH15 (in force 2025-10-01, applies from tax period 2025): text not fetched in this package (B).\n* **art. 10**: 20 %; 15 % for enterprises with total annual revenue ≤ VND 3 bn, 17 % for revenue 3-50 bn\n  (`smallTurnover` uses the 3 bn band only).\n* Foreign contractor tax (Circular 103/2014/TT-BTC): CIT portion 5 % on services and interest, 10 % on royalties;\n  dividends to foreign companies 0 %.', 'regimeName': 'Thuế thu nhập doanh nghiệp (corporate income tax)', 'unsupported': [['company', '17 % band (revenue VND 3-50 bn) and incentive rates (10 %, 17 %) not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Thuế thu nhập doanh nghiệp (corporate income tax)', 'statute': 'Luật 67/2025/QH15 art. 10', 'dated': 'tax period 2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'Circular 103/2014/TT-BTC (foreign contractor tax)', 'dated': 'tax period 2025', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 2000)], 'citStatute': 'Luật 67/2025/QH15 art. 10', 'wht': [{'kind': 'interest', 'rate': 500, 'statute': 'Circular 103/2014/TT-BTC art. 13'}, {'kind': 'royalty', 'rate': 1000, 'statute': 'Circular 103/2014 art. 13'}, {'kind': 'services', 'rate': 500, 'statute': 'Circular 103/2014 art. 13'}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['cit.citTax { profit := 1000000, turnover := 5000000000 } == 200000', 'wht.amount { kind := .interest, amount := 1000 } == 50', 'wht.amount { kind := .royalty, amount := 1000 } == 100', 'wht.amount { kind := .services, amount := 1000 } == 50', 'cit.citTax { profit := 1000000, turnover := 2000000000 } == 150000'], 'smallTurnover': 3000000000, 'smallSched': [(0, 1500)]}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind='dividend', toCompany=False, rate=500, statute='PIT Law (VBHN 28/VBHN-VPQH, 2025) art. 27: investment income of non-resident individuals 5 %'),
            dict(kind='interest', toCompany=False, rate=500, statute='PIT Law (VBHN 28/VBHN-VPQH, 2025) art. 27 (5 %)'),
            dict(kind='royalty', toCompany=False, rate=500, statute='PIT Law (VBHN 28/VBHN-VPQH, 2025) art. 30 (1): 5 % (on the part above 10 m dong per contract)')] + S['wht']
_s5_wht_entry(unsupported=['the 10 m dong per-contract allowance on royalties to individuals (PIT Law art. 30 (1)) not applied',
                           'dividends to foreign organisations: the CIT rule not read (grade C line)'])
S['guards'] = S['guards'] + ['wht.amount { kind := .dividend, amount := 1000, toCompany := false } == 50']

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

S['wht'] = [dict(kind='dividend', toCompany=True, rate=0, statute='Luật Thuế TNDN 67/2025/QH15 art. 4 (7): income shared from capital contributions or shares in domestic enterprises, after their CIT, is exempt (in force 1 Oct 2025, applies from the 2025 tax period, art. 19 (1))')] + S['wht']
_s7_wht_entry(drop_unsupported=['dividends to foreign organisations'],
    add_unsupported=['other payments to foreign organisations: CIT Law 67/2025 art. 11 (2) (a) leaves the % of revenue to a Government decree; the Circular 103/2014 rates are kept (decree not read)'])
S['guards'] = S['guards'] + ['wht.amount { kind := .dividend, amount := 1000 } == 0']

# --- R3 session 12 (2026-11-21): registry sample: Luật 67/2025/QH15 art. 10 read (OCR of the official signed PDF); 17 % band added ---
S['doc'] = S['doc'].replace("Luật Thuế TNDN 67/2025/QH15 (in force 2025-10-01, applies from tax period 2025): text not fetched in this package (B).",
    "Luật Thuế TNDN 67/2025/QH15 (datafiles.chinhphu.vn signed PDF, OCR `vn/law/cit/vn_cit67_2025_ocr.txt`; session 12, A): art. 19 (1)\n"
    "in force 1 Oct 2025 \"và áp dụng từ kỳ tính thuế thu nhập doanh nghiệp năm 2025\" (the whole 2025 tax period).").replace(
    "* **art. 10**: 20 %; 15 % for enterprises with total annual revenue ≤ VND 3 bn, 17 % for revenue 3-50 bn\n  (`smallTurnover` uses the 3 bn band only).",
    "* **art. 10**: (1) 20 %; (2) 15 % for enterprises with total annual revenue not above VND 3 bn; (3) 17 % above 3 bn up\n  to 50 bn; the revenue is that of the preceding tax period (the model reads the line's `turnover`; session 12 added the 17 % band).")
S['rateByFlag'] = [('__turnover__', 2000)]
S['rateOfLean'] = '''/-- Luật 67/2025/QH15 art. 10 (1)-(3): 15 % to VND 3 bn of annual revenue, 17 % to 50 bn, else 20 %. -/
def rateOf (co : Company) : Int :=
  if co.turnover ≤ 3000000000 then 1500 else if co.turnover ≤ 50000000000 then 1700 else 2000'''
S.pop('smallTurnover', None); S.pop('smallSched', None)
S['citStatute'] = "Luật 67/2025/QH15 art. 10 (1)-(3), art. 19 (1)"
S['guards'] = [g for g in S['guards'] if not g.startswith('cit.citTax')] + [
    '(cit { profit := 1000000, turnover := 2000000000 }).citTax { profit := 1000000, turnover := 2000000000 } == 150000',
    '(cit { profit := 1000000, turnover := 5000000000 }).citTax { profit := 1000000, turnover := 5000000000 } == 170000',
    '(cit { profit := 1000000, turnover := 60000000000 }).citTax { profit := 1000000, turnover := 60000000000 } == 200000']
S['unsupported'] = [['company', 'revenue test on the preceding tax period read from the line\'s turnover; incentive rates (art. 13: 10 %, 15 %, 17 %) and sector rates (art. 10 (4)) not modelled']]
for _t in S['taxes']:
    if _t['oecd'] == '1200':
        _t['statute'] = "Luật 67/2025/QH15 art. 10 (1)-(3), art. 19 (1)"
        _t['dated'] = "tax period 2025 (art. 19 (1): in force 1 Oct 2025, applies from the 2025 tax period); text read in the official signed PDF (OCR); session 12 registry sample"
        _t['grade'] = 'A'
        _t['unsupported'] = ["revenue of the preceding period not distinguished; incentive and sector rates not modelled"]
