import BsGlobal.Pit

/-!
# The Bahamas 2025: Value Added Tax (5111); excise grade C

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
* No relief for medicines, fuel, books or transport in the schedules read: 10 %.
-/

namespace BsGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon BsGlobal

def vat : Vat :=
  { name := "Value Added Tax", standard := 1000, reduced := 500,
    classOf := fun gd => match gd with
      | .food => .reduced
      | .electricity | .water => .zero
      | .insurance | .financial | .health | .education | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act (Reprint as at 1 July 2024) s. 6 (1) as substituted by the VAT (Amendment) Act, 2025 s. 3 (10 %; 5 % Fourth Schedule unprepared food from 1 April 2025); First Schedule Part I para 14 (utilities, zero); Third Schedule Part I paras (1)-(5) (exempt)"

def vatF : Family := vatFamily "Value Added Tax" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food: 5 % only on Fourth Schedule food sold unprepared by a food store, and only from 1 April 2025 (10 % before and on prepared food): charged at 5 % for the whole year (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .electricity || s.good == .water) "electricity up to $400 and water up to $50 a billing period are zero rated; larger bills are charged in full: read as within the caps (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .health) "medical services read as public (exempt); private medical services are taxed at 10 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) "excise tax on alcohol, tobacco and fuel not modelled"

#guard vat.embedded { good := .clothing, amount := 1100 } == 100
#guard vat.embedded { good := .food, amount := 1050 } == 50
#guard vat.embedded { good := .electricity, amount := 1100 } == 0
#guard vat.embedded { good := .medicines, amount := 1100 } == 100

end BsGlobal.Consumption
