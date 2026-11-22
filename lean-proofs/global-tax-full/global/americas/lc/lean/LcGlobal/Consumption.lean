import LcGlobal.Pit

/-!
# Saint Lucia 2025: Value Added Tax (5111); excise grade C

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
  bound, flagged). Medicines: no zero rating or exemption of pharmaceuticals found in Schedules 1-2: standard.
-/

namespace LcGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon LcGlobal

def vat : Vat :=
  { name := "Value Added Tax", standard := 1250,
    classOf := fun gd => match gd with
      | .food | .books | .newspapers | .education | .transport | .insurance | .financial | .health | .rent => .exempt
      | .water | .electricity | .petrol | .diesel => .zero
      | _ => .standard }

def vatStatute : String := "VAT Act Cap. 15.15 (Rev. 2023) s. 10 (1) (12.5 %); Sched. 1 para 2 (1) (h), (j), services (e), (f) (zero); Sched. 2 para 2 (a), (b), (h), (j), (m), (q), (cc) (exempt)"

def vatF : Family := vatFamily "Value Added Tax" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food: only the basic foods listed in VAT Sched. 1 para 2 (1) (j) and Sched. 2 para 2 (cc) are relieved; other food is taxable at 12.5 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .hotels) "hotel accommodation: tourism-sector rate under s. 10 (2) (S.I. 188/2020) not read; charged at 12.5 % (upper bound)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits) "excise tax on alcohol and tobacco not modelled (Excise Tax Act schedules not reached)"

#guard vat.embedded { good := .clothing, amount := 1125 } == 125
#guard vat.embedded { good := .electricity, amount := 1125 } == 0
#guard vat.embedded { good := .rent, amount := 1125 } == 0

end LcGlobal.Consumption
