S = {'cc': 'PW', 'doc': '# Palau 2025: business profits tax (1200)\n\nRPPL 11-11 (2022 tax reform, `pw/law/RPPL-11-11.txt`): business profits tax 12 % of net profits from 2023 (B: rate clause\nnot re-located; the 12 % found in the text is the wage-tax top band). Non-resident withholding: not reached (C).', 'regimeName': 'Business profits tax', 'unsupported': [], 'taxes': [{'oecd': '1200', 'tax': 'Business profits tax', 'statute': 'RPPL 11-11 (business profits tax)', 'dated': 'from 2023', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'RPPL 11-11', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['provisions not located']}], 'sched': [(0, 1200)], 'citStatute': 'RPPL 11-11 (business profits tax)', 'guards': ['cit.citTax { profit := 1000000 } == 120000']}
# --- R3 session 4 (2026-11-21): rate clause and non-resident tax located in RPPL 11-11 (statute text read) ---
S['doc'] = '''# Palau 2025: business profits tax (1200) and non-resident tax (withholding)

Source: RPPL 11-11 (Senate Bill 11-15, SD1; tax reform, commencement date 1 January 2023), text copied by the 1.x PW
builder (`cmp20/world/B14-pacific/pw/law/RPPL-11-11.txt`, sha256 in `pw/law/SOURCES.tsv`).
* **§ 1421**: every PGST-registered person "must pay business profits tax on the net income ... at the same rate as the
  highest rate of tax on wages and salary established in Section 1101"; **§ 1101**: 6 % to $8,000, 10 % to $40,000,
  "twelve percent (12%) upon the amount over the first forty thousand dollars": 12 %.
* **§ 1422**: non-resident tax on "the gross amount of interest, a royalty, technical fee, or insurance premium derived
  from sources in the Republic": (b) (1) insurance premium 5 %, (2) any other amount 10 %; withheld by the payer (§ 1465).
  Dividends are not in § 1422: explicit 0 % rule (cited).'''
S['citStatute'] = 'RPPL 11-11 § 1421 (rate of § 1101 top band, 12 %)'
S['taxes'] = [{'oecd': '1200', 'tax': 'Business profits tax (12 %)', 'statute': 'RPPL 11-11 § 1421, § 1101', 'dated': 'from 1 Jan 2023 (commencement date)', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['applies to PGST-registered persons; others are under the gross revenue rules of Title 40']},
              {'oecd': '1200/1100', 'tax': 'Non-resident tax (10 % interest, royalties, technical fees; 5 % insurance premiums)', 'statute': 'RPPL 11-11 § 1422, § 1465', 'dated': 'from 1 Jan 2023', 'grade': 'A', 'kernel_parts': ['Wht'], 'unsupported': []}]
S['wht'] = [dict(kind='interest', rate=1000, statute='RPPL 11-11 § 1422 (a), (b) (2) (10 %)'),
            dict(kind='royalty', rate=1000, statute='RPPL 11-11 § 1422 (a), (b) (2) (10 %)'),
            dict(kind='services', rate=1000, statute='RPPL 11-11 § 1422 (a), (b) (2): technical fees 10 %'),
            dict(kind='dividend', rate=0, statute='RPPL 11-11 § 1422 (a): interest, royalties, technical fees and insurance premiums only')]
S['whtName'] = 'Non-resident tax (RPPL 11-11 § 1422)'
S['guards'] = S['guards'] + ['wht.amount { kind := .interest, amount := 1000 } == 100']
