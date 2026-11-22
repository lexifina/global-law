import GdGlobal.Pit

/-!
# Grenada 2025: Value Added Tax (5111); excise grade C

Source: Value Added Tax Act, Cap. 333A (Act No. 23 of 2009 amended by Act No. 7 of 2011), laws.gov.gd download fetched
2026-11-21 (`gd/law/vat_cap333a.pdf`). Later amendments not checked: grade B.
* **s. 8 (3)**: "(a) if the supply or import is zero-rated, zero per cent; (b) if the supply is a supply of hotel or
  holiday accommodation ... ten per cent; (c) ... dive package, ten per cent; ... (e) in any other case, fifteen per cent."
* **Third Schedule (zero rated)**: 1 food "to the extent provided in the Regulations"; 2 water by NAWASA to residences
  for domestic use; 3 "electricity by GRENLEC provided to residential premises for domestic" use; 5 "motor spirit
  (gasoline), diesel, LPG cooking gas, or Kerosene" (conditions).
* **Fourth Schedule (exempt)**: 1 financial services incl. (f) insurance contracts; 4-5 residential property and lets;
  9 education services; 10 medical services; 16 "transportation of passengers within Grenada by taxi, bus or ferry".
* Food read as zero rated (Regulation list only: lower bound). Medicines: no item found: 15 %.
-/

namespace GdGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon GdGlobal

def vat : Vat :=
  { name := "Value Added Tax", standard := 1500, reduced := 1000,
    classOf := fun gd => match gd with
      | .food | .water | .electricity | .petrol | .diesel => .zero
      | .hotels => .reduced
      | .financial | .insurance | .rent | .education | .health | .transport => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act Cap. 333A s. 8 (3) (e) 15 %, (b) 10 % (hotel accommodation); Third Sched. items 1, 2, 3, 5 (zero); Fourth Sched. items 1, 4, 5, 9, 10, 16 (exempt)"

def vatF : Family := vatFamily "Value Added Tax" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food: zero rated only to the extent of the VAT Regulations list; other food 15 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .water || s.good == .electricity) "water and electricity: zero rated for residential domestic use only"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits) "excise tax not modelled (Excise Tax Act not reached)"

#guard vat.embedded { good := .clothing, amount := 1150 } == 150
#guard vat.embedded { good := .hotels, amount := 1100 } == 100
#guard vat.embedded { good := .electricity, amount := 1150 } == 0

end GdGlobal.Consumption
