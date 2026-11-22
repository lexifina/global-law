S = {'cc': 'NR', 'doc': '''# Nauru 2025: business profits tax (1200) and non-resident tax (withholding)

Source: Business Tax Act 2016 (No. 31 of 2016), RONLAW consolidation "Service 6" (as amended to the Constitution
(Amendment) (No 2) Act 2026, which only renames the Republic) and the Business Tax (Amendment of Schedule 1)
Regulations 2024 (SL No. 22 of 2024, in force 1 July 2024), texts from the RONLAW search index
(`ronlaw.gov.nr/api/pdf/search`; `nr/law/nr_bta2016_serv6.txt`, `nr/law/nr_bta_sch1_regs2024.txt`, sha256 in `SHA256SUMS`).
* **s. 11** business profits tax at the Schedule 1 rates on taxable income. **Schedule 1 (1) (d)**: Category A resident
  company with annual gross revenue $0 - $15,000,000: 20 %; Category B above $15,000,000: 25 %; Category C resident
  company controlled by a non-resident associate 25 %; D (RPC business) 30 %; E non-resident company with a PE 25 %;
  F (PE in connection with the Regional Processing Centre) 30 %. Modelled: 20 % at turnover up to $15 m, 25 % above.
* **s. 13 (1)**: non-resident tax "on a non-resident person who has derived interest, a royalty, or insurance premium
  from sources in Naoero"; **Schedule 1 (3)**: "For any other person 20%" (30 % for RPC-related persons);
  **s. 44**: withheld by the payer. Dividends are not in s. 13: explicit 0 % rule (cited). Fees for services paid
  abroad fall under the Employment and Services Tax Act 2014 (services tax, not read): no rule.''',
 'regimeName': 'Business profits tax', 'sched': [(0, 2500)], 'smallTurnover': 15000000, 'smallSched': [(0, 2000)],
 'citStatute': 'Business Tax Act 2016 s. 11, Schedule 1 (1) (d) Categories A-B (SL 15 of 2018; SL 22 of 2024)',
 'unsupported': [['true', 'Schedule 1 Categories C (resident company controlled by a non-resident associate, 25 %), D and F (Regional Processing Centre business, 30 %) are not distinguished: 20 %/25 % by turnover']],
 'taxes': [{'oecd': '1200', 'tax': 'Business profits tax (20 % to $15 m gross revenue, 25 % above)', 'statute': 'Business Tax Act 2016 s. 11, Schedule 1 (1) (d)', 'dated': 'RONLAW Service 6 consolidation; Schedule 1 as amended by SL 22 of 2024 (from 1 July 2024)', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['Categories C, D, F not distinguished']},
           {'oecd': '1200/1100', 'tax': 'Non-resident tax (20 % on interest, royalties, insurance premiums)', 'statute': 'Business Tax Act 2016 ss. 13, 44, Schedule 1 (3)', 'dated': 'as amended by SL 22 of 2024', 'grade': 'A', 'kernel_parts': ['Wht'], 'unsupported': ['services tax on fees paid abroad (Employment and Services Tax Act 2014) not read']}],
 'wht': [dict(kind='interest', rate=2000, statute='Business Tax Act 2016 s. 13 (1), s. 44 (1), Schedule 1 (3) ("any other person 20%")'),
         dict(kind='royalty', rate=2000, statute='Business Tax Act 2016 s. 13 (1), s. 44 (1), Schedule 1 (3)'),
         dict(kind='dividend', rate=0, statute='Business Tax Act 2016 s. 13 (1): non-resident tax covers interest, royalties and insurance premiums only')],
 'whtName': 'Non-resident tax (Business Tax Act 2016 s. 13)',
 'guards': ['cit.citTax { profit := 1000000, turnover := 10000000 } == 200000', 'cit.citTax { profit := 1000000, turnover := 20000000 } == 250000', 'wht.amount { kind := .interest, amount := 1000 } == 200'],
 'absent': []}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = S['wht'] + [dict(kind='services', rate=2000, statute='Employment and Services Tax Act 2014 s. 9 (1) (b) (i), s. 12 (1), (3), s. 18, Schedule (4) (c): any other non-resident person providing services 20 %')]
for t in S['taxes']:
    if t['oecd'] == '1200/1100': t['unsupported'] = []
S['taxes'].append({'oecd': '1200/1100', 'tax': 'Services tax on services fees paid to non-residents (20 %)', 'statute': 'Employment and Services Tax Act 2014 ss. 9, 12, 18, Schedule (4) (c)',
    'dated': 'RONLAW consolidation in force from 12 May 2026 (Act 21 of 2026 amended s. 9; 1.x builder copy cmp20/world/B14-pacific/nr/law/gl_esta2014.txt); the 2025 wording of the Schedule not confirmed',
    'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': ['Regional Processing Centre services (30 %) and services to the Republic by non-resident individuals (0 % to $20,000) not distinguished']})
S['guards'] = S['guards'] + ['wht.amount { kind := .services, amount := 1000 } == 200']

# --- R3 session 10 (2026-11-21): FT reviewer 6 item 4: services tax rate dated for 2025 ---
# RONLAW history notes in the consolidation (cmp20/world/B14-pacific/nr/law/gl_esta2014.txt): Schedule "subst SL 3 of
# 2021 reg 4, opn 24 Mar 2021; am SL 3 of 2023 reg 4, opn 1 July 2022"; s. 12 (1) last am Act 8 of 2020 (4 June 2020);
# s. 18 am Act 8 of 2020. Act 21 of 2026 (from 12 May 2026) amended s. 9 (1) and definitions only: Schedule (4) (c) 20 %
# is the 2025 rate. The source rule used (s. 9 (1) (b) (i): fee paid by a resident) is in both wordings.
for t in S['taxes']:
    if t['oecd'] == '1200/1100' and t['tax'].startswith('Services tax'):
        t.update(grade='A',
                 dated='Schedule as amended by SL 3 of 2023 (from 1 July 2022), s. 12 (1) and s. 18 as amended by Act 8 of 2020: unchanged through 2025 (RONLAW history notes); Act 21 of 2026 (from 12 May 2026) amended s. 9 (1) and definitions only')
