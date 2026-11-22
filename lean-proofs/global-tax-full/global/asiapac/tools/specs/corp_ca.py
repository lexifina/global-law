# Central Asia corporate specs (P2). Run: python3 corp_ca.py -> writes specs/<CC>_corp.py
import os
SPECS = {}
co = lambda **k: "{ " + ", ".join(f"{a} := {b}" for a, b in k.items()) + " }"

SPECS["KZ"] = dict(cc="KZ", regimeName="Корпоративный подоходный налог", sched=[(0, 2000)],
  citStatute="Налоговый кодекс 2017 ст. 313 п. 1 (20 %); ст. 300 (перенос убытков)",
  wht=[dict(kind="dividend", rate=1500, statute="ст. 646 п. 1 пп. 5) (дивиденды 15 %)"),
       dict(kind="interest", rate=1500, statute="ст. 646 п. 1 пп. 5) (вознаграждения 15 %)"),
       dict(kind="royalty", rate=1500, statute="ст. 646 п. 1 пп. 5) (роялти 15 %)"),
       dict(kind="services", rate=2000, statute="ст. 646 п. 1 пп. 1) (прочие доходы 20 %)"),
       dict(kind="other", rate=2000, statute="ст. 646 п. 1 пп. 1) (20 %)")],
  whtName="Подоходный налог у источника выплаты (нерезиденты)",
  doc=r'''# Kazakhstan 2025: corporate income tax and withholding on non-residents (1200)

Source: Tax Code 2017 (adilet, archived 2025-06-11; `law/SOURCES.tsv`).
* **art. 313 (1)**: taxable income less the art. 288 items and the losses carried forward under art. 300 "подлежит
  обложению налогом по ставке 20 процентов".
* **art. 300 (1)**: business losses carried forward (ten years; the year limit is not modelled: `lossesForward` is offset in
  full).
* **art. 646 (1)**: non-residents' income at source: 1) other income "20 процентов"; 5) "доходы от прироста стоимости,
  дивиденды, вознаграждения, роялти – 15 процентов"; (4) the dividend exemption for holdings over three years is not
  modelled.''',
  unsupported=[["dividends", "dividends received: art. 288 exemption not modelled (they stay in the profit)"],
               ["debt", "thin capitalisation (art. 246) not modelled"],
               ["abroad", "art. 646 (2) tax-haven rate 20 % and (4) the three-year dividend exemption not modelled"]],
  guards=[f"cit.citTax {co(profit=1000000)} == 200000", f"cit.citTax {co(profit=1000000, lossesForward=300000)} == 140000",
          "wht.amount { kind := .dividend, amount := 1000 } == 150", "wht.amount { kind := .services, amount := 1000 } == 200"],
  taxes=[{"oecd": "1200", "tax": "Корпоративный подоходный налог", "statute": "Tax Code 2017 arts. 300, 313", "dated": "adilet text archived 2025-06-11", "grade": "A", "kernel_parts": ["CorpRegime"], "unsupported": ["10-year loss limit", "thin cap", "special regimes"]},
         {"oecd": "1200/1100", "tax": "КПН у источника выплаты (нерезиденты)", "statute": "Tax Code 2017 art. 646 (1)", "dated": "2025-06-11", "grade": "A", "kernel_parts": ["Wht"], "unsupported": ["tax-haven rate", "dividend exemption (art. 646 (4))", "insurance and transport rates"]}])

SPECS["KG"] = dict(cc="KG", regimeName="Налог на прибыль", sched=[(0, 1000)],
  citStatute="Налоговый кодекс 2022 ст. 240 ч. 1 (10 %); ст. 232 (убытки, 5 лет)",
  wht=[dict(kind="dividend", rate=1000, statute="ст. 249 ч. 2 п. 1 (дивиденды 10 %)"),
       dict(kind="interest", rate=1000, statute="ст. 249 ч. 2 п. 1 (процентные доходы 10 %)"),
       dict(kind="royalty", rate=1000, statute="ст. 249 ч. 2 п. 3 (роялти 10 %)"),
       dict(kind="services", rate=1000, statute="ст. 249 ч. 2 п. 4 (работы, услуги 10 %)")],
  whtName="Налог на доход иностранной организации у источника",
  doc=r'''# Kyrgyzstan 2025: profit tax and tax on non-residents' income at source (1200)

Source: Tax Code 2022, official edition 36891 (to 31.07.2025).
* **art. 240 (1)**: "ставка налога на прибыль устанавливается в размере 10 процентов" (0 % for the sectors of (2)-(4)).
* **art. 232 (1)**: losses carried forward "на срок не более 5 календарных лет" (the year limit is not modelled).
* **art. 249 (1)-(2)**: base = gross income without deductions; 1) dividends and interest 10 %; 3) "авторские гонорары, роялти
  - 10 процентов"; 4) works and services in the Kyrgyz Republic 10 %.''',
  unsupported=[["losses", "the 5-year limit of art. 232 is not checked"], ["dividends", "dividends received treatment not modelled"]],
  guards=[f"cit.citTax {co(profit=1000000)} == 100000", "wht.amount { kind := .royalty, amount := 1000 } == 100"],
  taxes=[{"oecd": "1200", "tax": "Налог на прибыль", "statute": "Tax Code 2022 arts. 232, 240", "dated": "edition 36891", "grade": "A", "kernel_parts": ["CorpRegime"], "unsupported": ["sectoral 0 % rates", "5-year loss limit"]},
         {"oecd": "1200/1100", "tax": "Налог на доход иностранной организации (у источника)", "statute": "Tax Code 2022 art. 249", "dated": "edition 36891", "grade": "A", "kernel_parts": ["Wht"], "unsupported": ["listed-securities exemption", "insurance and telecom rates"]}])

SPECS["TJ"] = dict(cc="TJ", regimeName="Profit tax (андози фоида)", sched=[(0, 1800)],
  rateByFlag=[("production", 1300), ("financial", 2000), ("mobile", 2000)],
  citStatute="Tax Code art. 183 (4) (13 % production, 20 % financial and mobile, 18 % other); art. 197 (losses, 3 years)",
  wht=[dict(kind="dividend", rate=1200, statute="art. 237 (1) (12 %, Law No. 2159 of 15.04.2025)"),
       dict(kind="interest", rate=1200, statute="art. 238 (1) (12 %)"),
       dict(kind="royalty", rate=1500, statute="art. 239 (8) 7) (other income 15 %)"),
       dict(kind="services", rate=1500, statute="art. 239 (8) 7) (other income 15 %)")],
  whtName="Withholding tax on non-residents",
  doc=r'''# Tajikistan 2025: profit tax and withholding (1200)

Source: Tax Code as amended to 14.05.2025 (official English text).
* **art. 183 (4)**: legal entities "for activities on production of goods - 13 percent; for the activities of financial and
  credit organizations and mobile companies - 20 percent; … all other types of activity … - 18 percent" (company flags
  `production`, `financial`, `mobile`).
* **art. 197 (1)**: losses carried forward "up to and including 3 years" (year limit not modelled).
* **art. 237 (1)**: dividends "withholding tax at the rate of 12 percent" (Law of 15 April 2025 No. 2159); **art. 238 (1)**:
  interest 12 %; **art. 239 (8)**: non-residents' other income (royalties, services) "at the rate of 15 percent".''',
  unsupported=[["losses", "the 3-year limit of art. 197 is not checked"]],
  guards=[f"(cit {co(profit=1000000)}).citTax {co(profit=1000000)} == 180000",
          f"(cit {co(profit=1000000, flags='[\"production\"]')}).citTax {co(profit=1000000)} == 130000",
          "wht.amount { kind := .dividend, amount := 1000 } == 120"],
  taxes=[{"oecd": "1200", "tax": "Profit tax", "statute": "Tax Code arts. 183 (4), 197", "dated": "14.05.2025", "grade": "A", "kernel_parts": ["CorpRegime"], "unsupported": ["3-year loss limit", "minimum tax (art. 285?) not read"]},
         {"oecd": "1200/1100", "tax": "Withholding tax (dividends, interest, other income of non-residents)", "statute": "Tax Code arts. 237-239", "dated": "14.05.2025", "grade": "A", "kernel_parts": ["Wht"], "unsupported": ["insurance 6 %, international transport and telecom 3 %"]}])

SPECS["UZ"] = dict(cc="UZ", regimeName="Налог на прибыль", sched=[(0, 1500)],
  rateByFlag=[("bank", 2000), ("mobile", 2000), ("ecommerce", 1000)],
  citStatute="Налоговый кодекс ст. 337 (ЗРУ-1014: банки 20 %, мобильная связь 20 %, электронная торговля 10 %, остальные 15 %); ст. 333",
  wht=[dict(kind="dividend", rate=1000, statute="ст. 353 п. 1 (дивиденды и проценты 10 %)"),
       dict(kind="interest", rate=1000, statute="ст. 353 п. 1 (10 %)"),
       dict(kind="royalty", rate=2000, statute="ст. 353 п. 6 (иные доходы 20 %)"),
       dict(kind="services", rate=2000, statute="ст. 353 п. 6 (иные доходы 20 %)")],
  whtName="Налог на доходы нерезидентов",
  doc=r'''# Uzbekistan 2025: profit tax and tax on non-residents' income (1200)

Source: Tax Code, lex.uz text in force 2025-01-01 (ЗРУ-1014 of 24.12.2024 in force 1 January 2025).
* **art. 337**: 1 banks 20; 2 mobile communication (and polyethylene granules) 20; 8 e-commerce 10; 11 dividends received 5;
  12 "Остальные налогоплательщики … 15" (company flags `bank`, `mobile`, `ecommerce`).
* **art. 333**: losses may reduce the profit of the current period "на всю сумму полученного им убытка или на часть" (no cap).
* **art. 353**: 1 "Дивиденды и проценты 10"; 6 "Иные доходы … 20" (royalties and services).''',
  unsupported=[["dividends", "dividends received are taxed at 5 % (art. 337 row 11) apart from the profit: not modelled"]],
  guards=[f"(cit {co(profit=1000000)}).citTax {co(profit=1000000)} == 150000",
          f"(cit {co(profit=1000000, flags='[\"bank\"]')}).citTax {co(profit=1000000)} == 200000",
          "wht.amount { kind := .royalty, amount := 1000 } == 200"],
  taxes=[{"oecd": "1200", "tax": "Налог на прибыль", "statute": "Tax Code arts. 333, 337", "dated": "lex.uz 2025-01-01 (ЗРУ-1014)", "grade": "A", "kernel_parts": ["CorpRegime"], "unsupported": ["0 % sectors", "dividends received at 5 %"]},
         {"oecd": "1200/1100", "tax": "Налог на доходы нерезидентов", "statute": "Tax Code art. 353", "dated": "2025-01-01", "grade": "A", "kernel_parts": ["Wht"], "unsupported": ["insurance 10 %, telecom/freight 6 %"]}])

SPECS["TM"] = dict(cc="TM", regimeName="Налог на прибыль", sched=[(0, 800)],
  rateByFlag=[("stateMajority", 2000), ("nonResident", 2000)],
  citStatute="Налоговый кодекс ст. 172 п. 1 (8 % юридические лица-резиденты; 20 % с долей государства > 50 % и другие юридические лица); ст. 167 (убытки, 3 года)",
  wht=[dict(kind="dividend", rate=1500, statute="ст. 180 п. 3 (15 %)"),
       dict(kind="interest", rate=1500, statute="ст. 180 п. 3 (15 %)"),
       dict(kind="royalty", rate=1500, statute="ст. 180 п. 3 (15 %)"),
       dict(kind="services", rate=1500, statute="ст. 180 п. 3 (15 %)")],
  whtName="Налог на доходы нерезидентов (у источника)",
  doc=r'''# Turkmenistan 2025: profit tax and tax on non-residents' income (1200)

Source: Tax Code (mejlis.gov.tm consolidation to 12.04.2025).
* **art. 172 (1)**: "8 процентов - для юридических лиц-резидентов Туркменистана (кроме юридических лиц, в уставном фонде которых
  доля, превышающая 50 процентов, принадлежит государству …)"; 50 % for state credit institutions and insurers and listed
  service providers (not modelled); "20 процентов - для других юридических лиц" (flags `stateMajority`, `nonResident`).
  **(2)** dividends received 15 %.
* **art. 167**: losses carried forward "не более чем на три года" (year limit not modelled).
* **art. 180 (3)**: non-residents' income without a permanent establishment "по ставке 15 процентов" (6 % on bare-boat leases).''',
  unsupported=[["company", "the 50 % rate for state credit institutions, insurers and listed services is not modelled"]],
  guards=[f"(cit {co(profit=1000000)}).citTax {co(profit=1000000)} == 80000",
          f"(cit {co(profit=1000000, flags='[\"stateMajority\"]')}).citTax {co(profit=1000000)} == 200000"],
  taxes=[{"oecd": "1200", "tax": "Налог на прибыль", "statute": "Tax Code arts. 167, 172 (1)", "dated": "consolidation to 12.04.2025", "grade": "B", "kernel_parts": ["CorpRegime"], "unsupported": ["50 % rate", "youth-enterprise reductions", "dividends received 15 %"]},
         {"oecd": "1200/1100", "tax": "Налог на доходы нерезидентов", "statute": "Tax Code art. 180 (3)", "dated": "consolidation to 12.04.2025", "grade": "B", "kernel_parts": ["Wht"], "unsupported": ["6 % lease rate"]}])

os.makedirs("specs", exist_ok=True)
for cc, s in SPECS.items():
    open(f"specs/{cc}_corp.py", "w").write("S = " + repr(s) + "\n")
print(list(SPECS))
