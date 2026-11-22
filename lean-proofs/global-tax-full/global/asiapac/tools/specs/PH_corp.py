S = {'cc': 'PH', 'doc': '# Philippines 2025: corporate income tax and final tax on non-resident foreign corporations (1200)\n\nNIRC as amended by RA 11534 (CREATE) and RA 12066 (CREATE MORE): text not fetched for this package (B).\n* **s. 27 (A)**: 25 %; 20 % for domestic corporations with net taxable income ≤ PHP 5 m and total assets ≤ PHP 100 m\n  (flag `small`). **s. 27 (E)**: MCIT 2 % of gross income from the fourth year (not modelled).\n* **s. 28 (B) (1)**: non-resident foreign corporations 25 % of gross income (royalties, services); **(5) (a)**: interest\n  on foreign loans 20 %; **(5) (b)**: intercorporate dividends 15 % (tax-sparing condition; else 25 %).', 'regimeName': 'Corporate income tax', 'unsupported': [['company', 'MCIT 2 % of gross income (s. 27 (E)), improperly accumulated earnings and RBE incentive regimes not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Corporate income tax', 'statute': 'NIRC s. 27 (A) (RA 11534)', 'dated': '2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'NIRC s. 28 (B)', 'dated': '2025', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 2500)], 'citStatute': 'NIRC s. 27 (A) (RA 11534)', 'wht': [{'kind': 'dividend', 'rate': 1500, 'statute': 'NIRC s. 28 (B) (5) (b)', 'toCompany': True}, {'kind': 'interest', 'rate': 2000, 'statute': 'NIRC s. 28 (B) (5) (a)', 'toCompany': True}, {'kind': 'royalty', 'rate': 2500, 'statute': 'NIRC s. 28 (B) (1)', 'toCompany': True}, {'kind': 'services', 'rate': 2500, 'statute': 'NIRC s. 28 (B) (1)', 'toCompany': True}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['(cit { profit := 1000000 }).citTax { profit := 1000000 } == 250000', 'wht.amount { kind := .dividend, amount := 1000, toCompany := true } == 150', 'wht.amount { kind := .interest, amount := 1000, toCompany := true } == 200', 'wht.amount { kind := .royalty, amount := 1000, toCompany := true } == 250', 'wht.amount { kind := .services, amount := 1000, toCompany := true } == 250'], 'rateByFlag': [('small', 2000)]}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = S['wht'] + [dict(kind=k, toCompany=False, rate=2500, statute='NIRC s. 25 (B): nonresident alien not engaged in trade or business, 25 % of the gross amount') for k in ('dividend', 'interest', 'royalty', 'services')]
_s5_wht_entry(statute='NIRC s. 25 (B), s. 28 (B)', unsupported=['nonresident aliens engaged in trade or business (s. 25 (A)) not distinguished'])
S['guards'] = S['guards'] + ['wht.amount { kind := .interest, amount := 1000, toCompany := false } == 250']

# --- R3 gap-closing session (2026-11-21): NIRC s. 27 (A), 25 (B), 28 (B) read in lexifina/philippines-law ---
S['doc'] = S['doc'].replace("NIRC as amended by RA 11534 (CREATE) and RA 12066 (CREATE MORE): text not fetched for this package (B).",
    "NIRC as amended by RA 11534 (CREATE), RA 12066 (CREATE MORE) and RA 12214 (CMEPA): texts read in lexifina/philippines-law\n"
    "(gap-closing session; official source elibrary.judiciary.gov.ph showdocs/2/93191, /2/98085, /2/99213): RA 12066 s. 1 (s. 27 (A),\n"
    "in force 2024-12-03): 25 %; 20 % where net taxable income ≤ PHP 5 m and total assets ≤ PHP 100 m (the words \"One hundred\n"
    "million pesos\" govern the misprinted figure \"P1,000,000,000\"); RA 12214 s. 5 (s. 25 (B): 25 %) and s. 7 (s. 28 (B) (1): 25 %);\n"
    "RA 11534 s. 7 (s. 28 (B) (5) (b): 15 % on intercorporate dividends, tax-sparing condition). s. 28 (B) (5) (a) (interest on\n"
    "foreign loans 20 %) is \"x x x\" in every amending act read: not read.")
S['citStatute'] = "NIRC s. 27 (A) as amended by RA 11534 s. 6 and RA 12066 s. 1"
for _t in S['taxes']:
    if _t['oecd'] == '1200':
        _t['statute'] = "NIRC s. 27 (A) as amended by RA 11534 s. 6 and RA 12066 s. 1"
        _t['dated'] = ("2025: RA 12066 s. 1 (in force 2024-12-03; the s. 27 (A) text in force in 2025) read in lexifina/philippines-law "
                       "ra/2024/12066 (official source elibrary.judiciary.gov.ph showdocs/2/98085): 25 %, 20 % for small corporations; "
                       "gap-closing session: B -> A")
        _t['grade'] = 'A'
    if _t['oecd'] == '1200/1100':
        _t['statute'] = "NIRC s. 25 (B) (RA 12214 s. 5), s. 28 (B) (1) (RA 12214 s. 7), (5) (b) (RA 11534 s. 7), (5) (a) (not read)"
        _t['dated'] = ("2025: 25 % (s. 25 (B), s. 28 (B) (1)) and 15 % (s. 28 (B) (5) (b)) read in lexifina/philippines-law; the 20 % on "
                       "interest on foreign loans (s. 28 (B) (5) (a)) not read: stays B")
