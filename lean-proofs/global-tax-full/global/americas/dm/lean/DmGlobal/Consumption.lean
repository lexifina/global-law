import DmGlobal.Pit

/-!
# Dominica 2025: Value Added Tax (5111); excise grade C

Source: Value Added Tax Act No. 7 of 2005 and Amendment Acts 4/2006, 17/2008, 8/2014, 12/2015 (PDFs linked from the IRD
page ird.gov.dm/tax-laws/value-added-tax, on dominica.gov.dm; `dm/law/`). No consolidation: grade B.
* **s. 9 (1)**: (a) "15 percent of the value of every taxable supply"; (c) "to the extent provided in regulations, 10
  percent of the value of a taxable supply of (i) accommodation services by a hotel, guest house, inn ...". Act 4/2006
  adds (d) 10 % on the dive portion of a dive package. No rate change in 8/2014 or 12/2015.
* **Schedule I (zero rated)** 3 (g) "a supply of fuel"; (h) "the following foods to the extent provided in regulations:
  flour; milk; rice; sugar"; (l) "the first 50 units of electrical energy".
* **Schedule II (exempt)** 2 (a) financial services, (b) medical services, (d) education services, (f) accommodation in a
  dwelling, (k) unprocessed agricultural products, (l) bread, (n) transportation of passengers, (o) "a supply of water by
  the Dominica Water and Sewerage Company", (w) printed matter (books, newspapers).
* Food read as zero rated (flour, milk, rice, sugar; bread and unprocessed produce exempt; other food 15 %: lower bound);
  electricity read as standard (only the first 50 kWh are zero rated: upper bound). Medicines: no relief found: 15 %.
-/

namespace DmGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon DmGlobal

def vat : Vat :=
  { name := "Value Added Tax", standard := 1500, reduced := 1000,
    classOf := fun gd => match gd with
      | .food | .petrol | .diesel => .zero
      | .hotels => .reduced
      | .books | .newspapers | .water | .education | .transport | .financial | .insurance | .health | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act No. 7 of 2005 s. 9 (1) (a) 15 %, (c) 10 % (hotel accommodation); Sched. I 3 (g), (h) (zero); Sched. II 2 (a), (b), (d), (f), (l), (n), (o), (w) (exempt)"

def vatF : Family := vatFamily "Value Added Tax" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Inland Revenue Division (ird.gov.dm) list of the taxes it administers, `dm/law/ird_tax_laws_2025-01-21.*` and `dm/law/ird_past_taxes_2025-04-18.*` (Wayback 2025), names: Corporate Income Tax, Personal Income Tax, Withholding Tax, Value Added Tax, Excise Tax, Travel Tax, Licenses; 'Past Taxes' (the Sales Tax replaced by the VAT among them); the Sales Tax is listed among the IRD's 'Past Taxes' (replaced by the VAT); consolidated index of revenue Acts not held; none of them is a general sales or turnover tax beside the VAT of the 5111 row." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food: only flour, milk, rice, sugar (zero), bread and unprocessed produce (exempt) are relieved; other food 15 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .electricity) "electricity: only the first 50 units are zero rated (Sched. I 3 (l)); all charged at 15 % (upper bound)"
  ++ when (g.consumption.any fun s => s.good == .insurance) "insurance read as a financial service (exempt)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits) "excise tax not modelled (Excise Tax Act schedule not reached)"

#guard vat.embedded { good := .clothing, amount := 1150 } == 150
#guard vat.embedded { good := .hotels, amount := 1100 } == 100
#guard vat.embedded { good := .food, amount := 1150 } == 0

end DmGlobal.Consumption
