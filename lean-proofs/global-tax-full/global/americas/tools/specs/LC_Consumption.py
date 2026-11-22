S = dict(cc="LC", fam="Consumption",
doc=r'''# Saint Lucia 2025: Value Added Tax (5111); excise grade C

Source: Value Added Tax Act, Cap. 15.15, Revised Laws of Saint Lucia (2023), Attorney General's Chambers site
(`lc/law/vat_s10.html` and others, fetched 2026-11-21; ARCHIVE_INDEX.tsv). Grade B (the 2023 revision with notes of
later S.I.s; the body of the tourism-sector rate order was not reached).
* **s. 10 (1)**: "at the rate of 12.5% of the value of taxable goods or services ... except in the case of a supply that
  is zero rated (Amended by S.I. 101/2016)". s. 10 (2): the Minister may by Order specify the rate for hotels and other
  tourism providers (S.I. 188/2020, in force 1 Dec 2020: text not reached; hotels charged 12.5 %, upper bound, flagged).
* **Schedule 1 (zero rated)** para 2 (1) (h) "a supply of fuel"; (j) listed basic foods (milk, sugar, infant food,
  pasta ...); services (e) "water and sewerage provided by the Saint Lucia Water and Sewerage Company", (f) "electrical
  energy provided by Saint Lucia Electricity Services Limited".
* **Schedule 2 (exempt)** para 2 (a) financial services (incl. "insurance and reinsurance transactions"), (b) medical
  services, (h) education services, (j) educational supplies (printed matter 49.01-49.05: books, newspapers), (m)
  accommodation in a dwelling, (q) "local transportation of passengers", (cc) 112 tariff lines of basic food.
* Food: only listed basic foods are zero rated or exempt; other food is taxable at 12.5 % (food read as relieved: lower
  bound, flagged). Medicines: no zero rating or exemption of pharmaceuticals found in Schedules 1-2: standard.''',
vat=dict(name="Value Added Tax", standard=1250, statute="VAT Act Cap. 15.15 (Rev. 2023) s. 10 (1) (12.5 %); Sched. 1 para 2 (1) (h), (j), services (e), (f) (zero); Sched. 2 para 2 (a), (b), (h), (j), (m), (q), (cc) (exempt)",
  classes={"food":"exempt","books":"exempt","newspapers":"exempt","water":"zero","electricity":"zero","petrol":"zero","diesel":"zero",
           "education":"exempt","transport":"exempt","insurance":"exempt","financial":"exempt","health":"exempt","rent":"exempt"}),
unsupported=[["g.consumption.any fun s => s.good == .food", "food: only the basic foods listed in VAT Sched. 1 para 2 (1) (j) and Sched. 2 para 2 (cc) are relieved; other food is taxable at 12.5 % (lower bound)"],
 ["g.consumption.any fun s => s.good == .hotels", "hotel accommodation: tourism-sector rate under s. 10 (2) (S.I. 188/2020) not read; charged at 12.5 % (upper bound)"],
 ["g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits", "excise tax on alcohol and tobacco not modelled (Excise Tax Act schedules not reached)"]],
guards=["vat.embedded { good := .clothing, amount := 1125 } == 125", "vat.embedded { good := .electricity, amount := 1125 } == 0", "vat.embedded { good := .rent, amount := 1125 } == 0"],
taxes=[dict(oecd="5111", tax="Value Added Tax", statute="VAT Act Cap. 15.15 s. 10, Scheds. 1, 2", dated="Revised Laws of Saint Lucia (2023), AG Chambers site fetched 2026-11-21", grade="B", package="P1", kernel_parts=["Vat"], unsupported=["tourism-sector rate order", "food relief limited to listed tariff lines"]),
 dict(oecd="5121", tax="Excise tax", statute="Excise Tax Act", grade="C", status="unsupported", package="P1", kernel_parts=[], tried="AG Chambers site (VAT Act read; excise schedule not fetched)", unsupported=["would unlock: the Excise Tax Act schedule in force 2025"])])
