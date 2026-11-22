S = {'cc': 'FJ', 'doc': '# Fiji 2025: company income tax (1200)\n\nIncome Tax Act 2015 and the Income Tax (Budget Amendment) Acts (the build server `fj/law/act*_ita_budget.txt`): rate as read by the\nregistry (B): resident companies 25 % (listed 20 %, flag `listed`). NRWT: not reached in this pass (C).', 'regimeName': 'Income tax on companies', 'unsupported': [], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'Income Tax Act 2015 Schedule (as amended by the 2023 budget)', 'dated': '2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'ITA 2015 Part 10 (non-resident withholding)', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['rates not located']}], 'sched': [(0, 2500)], 'citStatute': 'Income Tax Act 2015 Schedule (as amended by the 2023 budget)', 'guards': ['(cit { profit := 1000000 }).citTax { profit := 1000000 } == 250000'], 'rateByFlag': [('listed', 2000)]}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind='dividend', rate=0, statute='Income Tax (Exempt Income) Regulations 2016 Sch. Part 5 (1): any dividend received is exempt income (Rates Regs 2016 reg 10 (5) (c) repealed)'),
            dict(kind='interest', rate=1000, statute='Income Tax (Rates of Tax and Levies) Regulations 2016 reg 10 (5) (b) (10 %)'),
            dict(kind='royalty', rate=1500, statute='Income Tax (Rates of Tax and Levies) Regulations 2016 reg 10 (5) (a) (15 %)'),
            dict(kind='services', rate=1500, statute='Income Tax (Rates of Tax and Levies) Regulations 2016 reg 10 (5) (a): management fee, fee for professional or other independent services (15 %)')]
S['whtName'] = 'Non-resident withholding tax (ITA 2015)'
_s5_wht_entry(tax='Non-resident withholding tax (interest 10 %, royalties, management and professional fees 15 %; dividends exempt)',
    statute='Income Tax Act 2015; Income Tax (Rates of Tax and Levies) Regulations 2016 reg 10 (5); Income Tax (Exempt Income) Regulations 2016 Sch. Part 5',
    dated='consolidations in force from 1 Aug 2022 (laws.gov.fj; local copy of the 1.x builder, cmp20/world/B14-pacific/fj/law/gl_rates_regs.txt, gl_exempt_sch.txt); no later change in the 2023-2026 Budget Acts read', grade='A', kernel_parts=['Wht'],
    unsupported=['insurance premiums 3 % (reg 10 (5) (d)) not a payment kind'])
S['guards'] = S['guards'] + ['wht.amount { kind := .interest, amount := 1000 } == 100', 'wht.amount { kind := .royalty, amount := 1000 } == 150', 'wht.amount { kind := .dividend, amount := 1000 } == 0']
