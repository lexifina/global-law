S = {'cc': 'FM', 'doc': '# Micronesia (FSM) 2025: no national tax on profits; the national tax on gross revenues\n\nSource: FSM Code Title 54 ch. 1 (2014 codification, `cmp20/world/B14-pacific/fm/law/T54_Ch01_SubChpII_2014.txt`).\n* **§ 141 (1)**: "a tax of $80 per year upon that portion of the amount of taxable gross revenues … [that] does not exceed\n  $10,000 per year"; **(2)**: "a tax of three percent per year upon that portion … " above $10,000 (`grt`). OECD treats\n  a gross-receipts tax under 5113 (general taxes on goods and services): booked as `.salesTax`.\n* Title 54 ch. 1 taxes wages, salaries and gross revenues only: no tax on business profits (B: later public laws not checked).', 'regimeName': 'Tax on gross revenues', 'unsupported': [], 'taxes': [{'oecd': '5113', 'tax': 'Tax on gross revenues', 'statute': 'FSMC Title 54 § 141', 'dated': 'FSMC 2014', 'grade': 'B', 'kernel_parts': ['charge'], 'unsupported': ['state taxes']}, {'oecd': '1200', 'tax': 'No tax on business profits (cited absence)', 'statute': 'FSMC Title 54 ch. 1', 'dated': 'FSMC 2014', 'grade': 'B', 'kernel_parts': ['Absent'], 'unsupported': []}], 'guards': ['grt 5000 == 80', 'grt 110000 == 3080'], 'extra_lean': '/-- § 141: $80 on the first $10,000 of gross revenue, 3 % above. -/\ndef grt (t : Int) : Int := if t ≤ 0 then 0 else 80 + divR .down (300 * pos (t - 10000)) BP\ndef grtCharge (co : Company) : Charge :=\n  charge .salesTax "Tax on gross revenues (§ 141)" co.turnover id grt (statute := "FSMC Title 54 § 141 (1)-(2)")', 'extra_run': ['[grtCharge g.company]'], 'extra_covers': ['.salesTax'], 'absent': [('cit', 'FSMC Title 54 ch. 1 levies only wage and gross-revenue taxes (§§ 111-143): no national tax on business profits (B: public laws after 2014 not checked)')]}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind=k, rate=0, statute='FSMC Title 54 ch. 1 (2014 codification): the national taxes are on wages and salaries (§ 121, withheld by employers § 131) and on business gross revenues (§ 141); no tax is withheld from payments abroad') for k in ('dividend', 'interest', 'royalty', 'services')]
S['whtName'] = 'No withholding on payments abroad (FSMC Title 54)'
_s5_wht_entry(tax='No withholding tax on payments abroad (cited)', statute='FSMC Title 54 ch. 1 §§ 121, 131, 141 (2014 codification)', dated='2014 codification (fsmlaw.org)',
    grade='A', kernel_parts=['Wht', 'Absent'], unsupported=['state taxes not read'])

# --- R3 gap-closing session (2026-11-21): the cited absence of a profits tax was wrong: 54 FSMC ch. 3 taxes Major Corporations ---
S['doc'] = S['doc'].replace("* Title 54 ch. 1 taxes wages, salaries and gross revenues only: no tax on business profits (B: later public laws not checked).",
    "* Gap-closing session (lexifina/micronesia-law, enrolled public laws from cfsm.gov.fm): **54 FSMC ch. 3 taxes Major\n"
    "  Corporations on taxable income**. Public Law No. 21-09 (approved 5 July 2019) s. 1 rewrote **§ 321**: for taxable years\n"
    "  ending on or after 31 March 2020, 21 % on the first $300,000,000, 25 % above that and below $500,000,000, 30 % above;\n"
    "  PL 20-158 (§ 352: annual return, no interim payments) and PL 23-23 (§ 325: 0 % of the tax to the FSM Trust Fund, 2023)\n"
    "  confirm the tax is in force. The session-1 cited absence (\"no tax on business profits\") was wrong and is withdrawn.\n"
    "  The definition of a Major Corporation (ch. 3) was not read: only a company flagged `majorCorporation` is charged;\n"
    "  other companies pay the gross revenue tax (§ 141). The repository holds 321 of the public laws: later amendments of\n"
    "  § 321 are not excluded (B).")
S['absent'] = [a for a in S.get('absent', []) if a[0] != 'cit']
S['extra_lean'] = S['extra_lean'] + '''
/-- 54 FSMC § 321 as amended by PL 21-09: 21 % to $300 m, 25 % to $500 m, 30 % above (taxable years ending from 31 Mar 2020). -/
def mcRegime : CorpRegime :=
  { name := "Major corporations tax", sched := Schedule.ofList [(0, 2100), (300000000, 2500), (500000000, 3000)] }'''
S['extra_run'] = list(S.get('extra_run', [])) + ['(if g.company.flags.contains "majorCorporation" then [mcRegime.citCharge g.company "54 FSMC § 321 as amended by PL 21-09 (2019): 21 % / 25 % / 30 %"] else [])']
S['extra_covers'] = list(S.get('extra_covers', [])) + ['.cit']
S['unsupported'] = list(S.get('unsupported', [])) + [['company', '1200 major corporations tax (54 FSMC ch. 3, § 321 as amended by PL 21-09): charged only on a company flagged majorCorporation (the definition of a Major Corporation was not read); other companies pay the gross revenue tax (§ 141)']]
S['guards'] = list(S['guards']) + ['mcRegime.citTax { profit := 400000000 } == 88000000', 'mcRegime.citTax { profit := 1000000 } == 210000']
for _i, _t in enumerate(S['taxes']):
    if _t['oecd'] == '1200':
        S['taxes'][_i] = {'oecd': '1200', 'tax': 'Major corporations tax (54 FSMC § 321: 21 % / 25 % / 30 %)',
            'statute': '54 FSMC ch. 3 § 321 as amended by Public Law No. 21-09 (2019); §§ 325, 352 (PL 23-23, PL 20-158)',
            'dated': '2025: PL 21-09 (approved 5 July 2019; taxable years ending from 31 March 2020), read in lexifina/micronesia-law; gap-closing fix: the earlier cited absence of a profits tax was wrong',
            'grade': 'B', 'kernel_parts': ['CorpRegime'],
            'unsupported': ['only companies flagged majorCorporation (ch. 3 definition not read)', 'later amendments of § 321 not excluded (repository holds part of the public laws)']}
