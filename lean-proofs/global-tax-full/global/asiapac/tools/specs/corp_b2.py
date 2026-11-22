SPECS = {}
SPECS["BN"] = dict(cc="BN", regimeName="Income tax on companies", sched=[(0, 1850)],
  citStatute="Income Tax Act (Cap. 35) s. 35 (1) (f) (18.5 % from the year of assessment 2015)",
  wht=[dict(kind="interest", rate=250, statute="Cap. 35 s. 35 (2), s. 9 (4) (2.5 % of the gross interest)"),
       dict(kind="royalty", rate=1000, statute="Cap. 35 s. 35 (2A) (a), s. 9 (5) (a) (10 %)"),
       dict(kind="services", rate=1000, statute="Cap. 35 s. 35 (2A), s. 9 (5) (ba), (c) (technical and management services 10 %)"),
       dict(kind="rent", rate=1000, statute="Cap. 35 s. 35 (2A) (a), s. 9 (5) (d) (rent of movable property 10 %)")],
  whtName="Withholding tax on non-residents",
  doc=r'''# Brunei 2025: income tax on companies and withholding on non-residents (1200)

Source: Laws of Brunei Chapter 35, Income Tax, revised edition B.L.R.O. 1/2024 (`cmp20/world/B15-no-pit/bn/law/ita_cap35_2024.txt`;
sha256 in `law/SOURCES.tsv`).
* **s. 35 (1) (f)**: "the year of assessment 2015 and subsequent years of assessment upon the chargeable income of every company,
  tax at the rate of 18.5 per cent".
* **s. 35 (2)**: "tax at the rate of 2.5 per cent … on the gross amount of any income referred to in section 9(4)" (interest,
  commission and fees on loans) of a non-resident; **(2A)**: payments of s. 9 (5) (a), (b), (ba), (d) (royalties, technical
  knowledge and services, rent of movable property) and (c) (management) "at the rate of 10 per cent".
Dividends are not taxed (no dividend withholding).''',
  unsupported=[["losses", "loss carry-forward period (s. 32) not checked; losses offset in full"],
               ["company", "petroleum income (Income Tax (Petroleum) Act) not modelled"]],
  guards=["cit.citTax { profit := 1000000 } == 185000", "wht.amount { kind := .interest, amount := 1000 } == 25",
          "wht.amount { kind := .royalty, amount := 1000 } == 100", "wht.amount { kind := .dividend, amount := 1000 } == 0"],
  taxes=[{"oecd": "1200", "tax": "Income tax on companies", "statute": "Cap. 35 s. 35 (1) (f)", "dated": "revised edition B.L.R.O. 1/2024", "grade": "A", "kernel_parts": ["CorpRegime"], "unsupported": ["loss period", "petroleum income tax"]},
         {"oecd": "1200/1100", "tax": "Withholding tax on non-residents", "statute": "Cap. 35 s. 35 (2), (2A), s. 9 (4)-(5)", "dated": "B.L.R.O. 1/2024", "grade": "A", "kernel_parts": ["Wht"], "unsupported": ["non-resident directors' fees 10 % (s. 35 (2B))"]}])

SPECS["AF"] = dict(cc="AF", regimeName="Income tax of legal persons", sched=[(0, 2000)],
  citStatute="Income Tax Law 2009 art. 4 (1) (legal persons 20 %)",
  wht=[dict(kind="dividend", rate=2000, statute="ITL 2009 art. 46 (1) 2 (20 %)"),
       dict(kind="interest", rate=2000, statute="ITL 2009 art. 46 (1) 2 (20 %)"),
       dict(kind="royalty", rate=2000, statute="ITL 2009 art. 46 (1) 2 (20 %)"),
       dict(kind="services", rate=2000, statute="ITL 2009 art. 46 (1) 2 (service charges 20 %)")],
  whtName="Withholding tax",
  doc=r'''# Afghanistan 2025: income tax of legal persons and withholding (1200)

Source: Income Tax Law 2009, MoF consolidation "Version: December 2016" (`itl.txt`; 2025 application not confirmed: grade B).
* **art. 4 (1)**: "The income tax of legal persons shall be 20" percent.
* **art. 46 (1) 2**: legal persons withhold "twenty percent tax from interest, dividends, royalties, prizes, … and service
  charges".''',
  unsupported=[["company", "the business receipts tax (5112) is booked in Consumption; BRT paid is deductible (not modelled)"]],
  guards=["cit.citTax { profit := 1000000 } == 200000", "wht.amount { kind := .royalty, amount := 1000 } == 200"],
  taxes=[{"oecd": "1200", "tax": "Income tax of legal persons", "statute": "ITL 2009 art. 4 (1)", "dated": "MoF consolidation December 2016", "grade": "B", "kernel_parts": ["CorpRegime"], "unsupported": ["2025 application under the de facto authorities not confirmed"]},
         {"oecd": "1200/1100", "tax": "Withholding tax", "statute": "ITL 2009 art. 46 (1) 2", "dated": "December 2016", "grade": "B", "kernel_parts": ["Wht"], "unsupported": ["contractor withholding (art. 72)"]}])
for cc, s in SPECS.items():
    open(f"specs/{cc}_corp.py", "w").write("S = " + repr(s) + "\n")
print(list(SPECS))
