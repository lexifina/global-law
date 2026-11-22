S = dict(cc="AG", fam="Consumption",
doc=r'''# Antigua and Barbuda 2025: Antigua and Barbuda Sales Tax (ABST, 5111); excise grade C

Sources (laws.gov.ag, fetched 2026-11-21; `ag/law/`): ABST Act 2006 No. 5 of 2006 (scanned; OCR `abst_2006.ocr.txt`),
Amendment Acts No. 15 of 2011, 11 of 2012, 37 of 2017, 30 of 2018, 32 of 2019, 1 of 2024; Revenue (Miscellaneous
Provisions) Acts 13 of 2023 and 5 of 2024. The official annual-law lists for 2023-2025 hold no other ABST act. No
consolidation: grade B.
* **s. 8 (3)**: "(a) if the supply or import is zero-rated, zero per cent; (b) if the supply is taxable because, under
  paragraph (2) of Schedule 4, the supplier chooses not to treat the supply as exempt under item 6 or 7 ... [rate];
  ... (d) in any other case, 15 per cent." Para (b) was 10.5 % (2006), "13 per cent" (Act 30 of 2018) and "14 per cent"
  (Act 32 of 2019, in force 2025). Schedule 4 para (2): hotel accommodation is not exempt for the first 45 days of a
  stay, so a guest's hotel bill bears the para (b) rate: hotels 14 %.
* **Schedule 3 (zero rated)**: 1 food "of a kind specified in the Regulations"; 3 (a) "electricity provided to residential
  premises for domestic use"; 4 "water"; 5 fuel.
* **Schedule 4 (exempt)**: 1 financial services; 7 residential accommodation; 9 "transportation of passengers by land,
  sea, or air within" the State; 10 education services; 11 medical services; 13 "prescription medicines".
* Food read as zero rated (only kinds listed in the Regulations: lower bound, flagged). The 2023 and 2024 Revenue
  (Miscellaneous Provisions) Acts add excise taxes, not ABST rates.''',
vat=dict(name="Antigua and Barbuda Sales Tax", standard=1500, reduced=1400, statute="ABST Act 2006 s. 8 (3) (d) 15 %, (b) 14 % (Act 32 of 2019; hotel accommodation, Sched. 4 para (2)); Sched. 3 items 1, 3 (a), 4, 5 (zero); Sched. 4 items 1, 7, 9, 10, 11, 13 (exempt)",
  classes={"food":"zero","electricity":"zero","water":"zero","petrol":"zero","diesel":"zero","hotels":"reduced",
           "financial":"exempt","insurance":"exempt","rent":"exempt","transport":"exempt","education":"exempt","health":"exempt","medicines":"exempt"}),
unsupported=[["g.consumption.any fun s => s.good == .food", "food: zero rated only for the kinds specified in the ABST Regulations; other food 15 % (lower bound)"],
 ["g.consumption.any fun s => s.good == .medicines", "medicines: only prescription medicines are exempt (Sched. 4 item 13); all read as exempt"],
 ["g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits", "excise and consumption taxes on alcohol and tobacco (incl. the 10 % additional excise tax of Act 13 of 2023) not modelled"]],
guards=["vat.embedded { good := .clothing, amount := 1150 } == 150", "vat.embedded { good := .hotels, amount := 1140 } == 140", "vat.embedded { good := .water, amount := 1150 } == 0"],
taxes=[dict(oecd="5111", tax="Antigua and Barbuda Sales Tax (ABST)", statute="ABST Act 2006 s. 8 (3), Scheds. 3, 4; Act 32 of 2019 s. 4", dated="Acts as published on laws.gov.ag (no consolidation; annual lists 2023-2025 checked)", grade="B", package="P1", kernel_parts=["Vat"], unsupported=["food limited to Regulation kinds"]),
 dict(oecd="5121", tax="Excise / consumption taxes", statute="Customs (Control and Management) Act; Revenue (Miscellaneous Provisions) Act 2023 (additional 10 % excise)", grade="C", status="unsupported", package="P1", kernel_parts=[], tried="Revenue (Misc.) Acts 2023/2024 read (additional 10 % excise on listed goods); base duty schedules not reached", unsupported=["would unlock: the 2025 consumption-tax tariff schedules"])])
