S = {'cc': 'MH', 'doc': '''# Marshall Islands 2025: tax on gross revenues (5113), no tax on business profits, non-resident tax on services

Source: Income Tax Act 1989 (48 MIRC Ch. 1), RMI Nitijela consolidation "Amended By ... P.L. 2024-14, P.L. 2025-34"
(`cmp20/world/B14-pacific/mh/law/1989-0050_5.txt`); Net Profit Tax Act 2025 (48 MIRC Ch. 7, `2025-0038A_1.txt`).
* **§ 109**: "$80 per year upon that portion of the amount of gross revenues ... which does not exceed $10,000 per year;
  and ... three percent (3%) per year upon that portion ... in excess of $10,000" (P.L. 1991-134): `grt`, booked as
  5113 (a gross-receipts tax) as for the FSM.
* **Net Profit Tax Act 2025 § 705** (16 % net profit tax) **§ 749 (2)**: "This Chapter shall apply to tax years
  commencing on or after October 1, 2026": no tax on business profits in 2025 (cited absence).
* **§ 117**: "a non-resident tax of ten percent (10%) on the gross income earned by every non-resident person in respect
  of services provided ... relating to any client in the Marshall Islands", withheld by the client (§ 118). No
  withholding on dividends, interest or royalties paid abroad in ch. 1 (explicit 0 % rules, cited).''',
 'regimeName': 'Tax on gross revenues', 'unsupported': [],
 'taxes': [{'oecd': '5113', 'tax': 'Tax on gross revenues ($80 on the first $10,000, 3 % above)', 'statute': '48 MIRC Ch. 1 (Income Tax Act 1989) § 109', 'dated': 'consolidation as amended to P.L. 2025-34', 'grade': 'A', 'kernel_parts': ['charge'], 'unsupported': []},
           {'oecd': '1200', 'tax': 'No tax on business profits in 2025 (cited absence)', 'statute': 'Income Tax Act 1989 Parts II-III; Net Profit Tax Act 2025 § 749 (2) (tax years from 1 Oct 2026)', 'dated': 'consolidation as amended to P.L. 2025-34; NPT Act 2025 as certified', 'grade': 'A', 'kernel_parts': ['Absent'], 'unsupported': []},
           {'oecd': '1200/1100', 'tax': 'Non-resident tax on services (10 %)', 'statute': '48 MIRC Ch. 1 §§ 117-118', 'dated': 'consolidation as amended to P.L. 2025-34', 'grade': 'A', 'kernel_parts': ['Wht'], 'unsupported': []}],
 'wht': [dict(kind='services', rate=1000, statute='Income Tax Act 1989 § 117 (10 % of the gross fee for services), § 118 (withheld by the client)'),
         dict(kind='dividend', rate=0, statute='Income Tax Act 1989: no tax on dividends paid abroad (Part VI taxes services only)'),
         dict(kind='interest', rate=0, statute='Income Tax Act 1989: no tax on interest paid abroad (Part VI taxes services only)'),
         dict(kind='royalty', rate=0, statute='Income Tax Act 1989: no tax on royalties paid abroad (Part VI taxes services only)')],
 'whtName': 'Non-resident tax (Income Tax Act 1989 § 117)',
 'guards': ['grt 5000 == 80', 'grt 110000 == 3080', 'wht.amount { kind := .services, amount := 1000 } == 100'],
 'extra_lean': '/-- § 109: $80 on the first $10,000 of gross revenue, 3 % above. -/\ndef grt (t : Int) : Int := if t ≤ 0 then 0 else 80 + divR .down (300 * pos (t - 10000)) BP\ndef grtCharge (co : Company) : Charge :=\n  charge .salesTax "Tax on gross revenues (§ 109)" co.turnover id grt (statute := "48 MIRC Ch. 1 § 109")',
 'extra_run': ['[grtCharge g.company]'], 'extra_covers': ['.salesTax'],
 'absent': [('cit', 'Income Tax Act 1989 taxes wages, gross revenues and non-residents\' service fees only; the Net Profit Tax Act 2025 (16 %, § 705) applies to tax years commencing on or after 1 October 2026 (§ 749 (2))')]}
