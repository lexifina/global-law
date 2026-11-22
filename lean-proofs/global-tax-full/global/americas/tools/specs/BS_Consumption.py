S = dict(cc="BS", fam="Consumption",
doc=r'''# The Bahamas 2025: Value Added Tax (5111); excise grade C

Sources (Department of Inland Revenue, "Legal - VAT" page, fetched 2026-11-21; `bs/law/`, ARCHIVE_INDEX.tsv): Value Added
Tax Act (Reprint), Extraordinary Official Gazette 4 November 2024, "Reprinted as at 1st July, 2024"
(`vat_act_reprint_2024-11.pdf`; raw text `vat_act_reprint_2024-11.raw.txt`); Value Added Tax (Amendment) Act, 2025
(`vat_amend_act_2025.pdf`, "This Act shall come into operation on the 1st day of April, 2025"); Value Added Tax
(Amendment) (No. 2) Act, 2025 (administrative sections only: ss. 2, 18, 19, 22A, 27, 38C, 38K, 47A-C, 50, 56). Grade A
for the rates, B overall (the food rate starts on 1 April 2025).
* **s. 6 (1)** as substituted by the 2025 Act s. 3: VAT "is chargeable at - (a) a zero percent rate on ... the First
  Schedule ...; (b) a reduced rate of five percent on ... the Fourth Schedule if sold unprepared in a food store ...; and
  (c) a standard rate of ten per cent on the value of any taxable supply ... that is not zero rated or reduced rated".
  Before 1 April 2025, s. 6 (1) (b) of the reprint: "a standard rate of ten per cent".
* **Fourth Schedule** (2025 Act s. 8): meat, fish, dairy, vegetables, fruit, cereals and other foods by tariff line, "if
  sold unprepared by a food store".
* **First Schedule Part I para 14**: "A supply of utility goods that comprises - (a) electricity that is equivalent to
  $400.00 or below per billing period; (b) water, including sewerage services, that is equivalent to $50.00 or below".
* **Third Schedule Part I (exempt)**: (1) life insurance and insurance on owner-occupied dwellings; (2) financial services
  (other than for an explicit fee); (3) "Medical services where supplied by a public health care facility to a public
  patient"; (4) tuition-funded education; (5) "The rental of a dwelling"; (9) daycare.
* No relief for medicines, fuel, books or transport in the schedules read: 10 %.''',
vat=dict(name="Value Added Tax", standard=1000, reduced=500,
  statute="VAT Act (Reprint as at 1 July 2024) s. 6 (1) as substituted by the VAT (Amendment) Act, 2025 s. 3 (10 %; 5 % Fourth Schedule unprepared food from 1 April 2025); First Schedule Part I para 14 (utilities, zero); Third Schedule Part I paras (1)-(5) (exempt)",
  classes={"food":"reduced","electricity":"zero","water":"zero","insurance":"exempt","financial":"exempt","health":"exempt","education":"exempt","rent":"exempt"}),
unsupported=[["g.consumption.any fun s => s.good == .food", "food: 5 % only on Fourth Schedule food sold unprepared by a food store, and only from 1 April 2025 (10 % before and on prepared food): charged at 5 % for the whole year (lower bound)"],
 ["g.consumption.any fun s => s.good == .electricity || s.good == .water", "electricity up to $400 and water up to $50 a billing period are zero rated; larger bills are charged in full: read as within the caps (lower bound)"],
 ["g.consumption.any fun s => s.good == .health", "medical services read as public (exempt); private medical services are taxed at 10 % (lower bound)"],
 ["g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel", "excise tax on alcohol, tobacco and fuel not modelled"]],
guards=["vat.embedded { good := .clothing, amount := 1100 } == 100", "vat.embedded { good := .food, amount := 1050 } == 50",
        "vat.embedded { good := .electricity, amount := 1100 } == 0", "vat.embedded { good := .medicines, amount := 1100 } == 100"],
taxes=[dict(oecd="5111", tax="Value Added Tax", statute="VAT Act 2014 (Reprint as at 1 July 2024) s. 6 (1) (VAT (Amendment) Act, 2025 s. 3), First, Third and Fourth Schedules", dated="Reprint 4 November 2024; Amendment Act 2025 in force 1 April 2025", grade="B", package="P1", kernel_parts=["Vat"], unsupported=["5 % food rate only from 1 April 2025 and only unprepared in food stores", "utility caps"]),
 dict(oecd="5121", tax="Excise tax", statute="Excise Tax Act 2018", grade="C", status="unsupported", package="P1", kernel_parts=[], tried="inlandrevenue.finance.gov.bs VAT texts read; excise tariff not fetched", unsupported=["would unlock: the Excise Tax Act schedule in force 2025"])])
