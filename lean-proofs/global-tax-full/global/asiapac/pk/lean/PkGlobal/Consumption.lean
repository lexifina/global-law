import PkGlobal.Pit

/-!
# Pakistan 2025: federal sales tax on goods (5111); provincial sales tax on services and federal excise not modelled

Source: Sales Tax Act, 1990 "As amended up to 30th June, 2025" (FBR consolidation, Finance Act 2025;
`download1.fbr.gov.pk/Docs/202586148252375SalesTaxActupdatedupto2025-26.pdf`, fetched 2026-11-21;
`pk/law/pk_sales_tax_act1990_upto_2025-06-30.pdf`, sha256 in `SHA256SUMS`).
* **s. 3 (1)**: "there shall be charged, levied and paid a tax known as sales tax at the rate of [eighteen] per cent of the
  value of (a) taxable supplies made by a registered person …" (18 % unchanged through 2025).
* **Sixth Schedule Table-1** (exempt, s. 13 (1)): S. No. 21 rice, wheat and meslin and other unprocessed food items of the
  Table; S. Nos. 32-33 books, newsprint; S. No. 176 (inserted by Finance Act 2024) "POL products: (i) MS (Petrol) (ii) High
  Speed Diesel Oil (iii) Kerosene (iv) Light Diesel Oil".
* **Eighth Schedule S. No. 81**: "Substances registered as drugs under the Drugs Act, 1976": 1 %, charged at manufacture or
  import as final discharge (`superReduced` 1 %, applied to the retail amount: flagged).
The federal Act taxes goods; services (restaurants, hotels, transport, telecoms, health, education, finance, insurance)
fall under provincial sales tax on services (Punjab Sales Tax on Services Act 2012), not modelled: those classes carry no
federal tax here. Rent of dwellings is not a supply of goods. Grade B (class-level mapping of HS-coded schedules).

**Federal excise duty (session 6, grade A)**: Federal Excise Act 2005 s. 3, First Schedule Table I (FBR consolidations
as amended up to 30 June 2024 and up to 30 June 2025: the entries below are the same in both). **S. No. 9**: locally
produced cigarettes whose on-pack printed retail price exceeds Rs 12,500 per thousand: Rs 16,500 per thousand;
**S. No. 10**: not exceeding Rs 12,500 per thousand: Rs 5,050 per thousand. The tier is chosen from the household's price
per stick (tax-inclusive, as printed on the pack). **S. No. 8** (imported cigarettes: 65 % of retail price or the S. No. 9
rate, whichever is higher) is not applied (the basket has no origin). **S. Nos. 4-6** aerated waters 20 % of retail price:
the non-alcoholic class mixes aerated waters with other drinks: not modelled. No duty on alcoholic beverages in the
First Schedule.
-/

namespace PkGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Sales tax", standard := 1800, superReduced := 100,
    classOf := fun gd => match gd with
      | .food | .books | .newspapers | .petrol | .diesel | .heatingOil | .rent | .restaurants | .hotels | .transport | .communication | .health | .education | .financial | .insurance => .exempt
      | .medicines => .superReduced
      | _ => .standard }

def vatStatute : String := "Sales Tax Act, 1990 s. 3 (1) (18 %), Sixth Schedule Table-1 S. Nos. 21, 32, 33, 176, Eighth Schedule S. No. 81 (1 %) (as amended up to 30 June 2025)"

/-- Federal Excise Act 2005, First Schedule Table I S. Nos. 9-10: rupees per thousand locally produced cigarettes,
chosen by the printed retail price per thousand (amount × 10^6 / quantity, quantity in thousandths of a stick). -/
def fedCigRate (s : Spend) : Int :=
  if s.quantity <= 0 then 0
  else if s.amount * 1000000 > 12500 * s.quantity then 16500 else 5050

def fedCig (s : Spend) : Int := divR .down (s.quantity * fedCigRate s) 1000000

def fedCharges (xs : List Spend) : List Charge :=
  (xs.filter fun s => s.good == .cigarettes).map fun s =>
    charge .excise "Federal excise duty (cigarettes)" s.amount id (fun _ => fedCig s) (event := s.good.name) (bearer := .consumer)
      (statute := s!"Federal Excise Act 2005 s. 3, First Schedule Table I S. No. {(if fedCigRate s == 16500 then 9 else 10 : Int)} (Rs {fedCigRate s} per thousand)")

def families : List Family :=
  [{ name := "5111 Sales tax on goods (federal)", covers := [.vat, .excise],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ fedCharges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["PK 5111: Sales Tax Act 1990 (as amended up to 30 June 2025) s. 3 (1), Sixth and Eighth Schedules", "PK 5121: Federal Excise Act 2005 First Schedule Table I S. Nos. 9-10 (cigarettes), FBR consolidations to 30 June 2024 and 30 June 2025"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["food taken as exempt (Sixth Schedule Table-1: unprocessed staples); processed and packaged food is taxable at 18 % or under the Third Schedule on retail price"] else [])
  ++ (if g.consumption.any (fun s => s.good == .medicines) then ["drugs: 1 % on the manufacturer's or importer's value (Eighth Schedule S. No. 81) applied to the retail amount"] else [])
  ++ (if g.consumption.any (fun s => s.good == .restaurants || s.good == .hotels || s.good == .transport || s.good == .communication || s.good == .health || s.good == .education || s.good == .financial || s.good == .insurance) then ["provincial sales tax on services (e.g. Punjab Sales Tax on Services Act 2012, 16 %) not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes) then ["federal excise duty: cigarettes taken as locally produced (First Schedule Table I S. Nos. 9-10); imported cigarettes (S. No. 8: 65 % of retail price or the S. No. 9 rate, whichever is higher) not distinguished; a line without a quantity bears no duty"] else [])
  ++ (if g.consumption.any (fun s => s.good == .nonAlcoholic) then ["federal excise duty on aerated waters, 20 % of retail price (First Schedule Table I S. Nos. 4-6): not modelled (the class mixes aerated waters with other drinks)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .tobaccoOther) then ["federal excise duty on other tobacco (S. Nos. 7, 8a-8d: per kg) not modelled"] else [])

#guard vat.embedded { good := .clothing, amount := 11800 } == 1800
#guard vat.embedded { good := .petrol, amount := 11800 } == 0
#guard vat.embedded { good := .medicines, amount := 10100 } == 100
#guard fedCig { good := .cigarettes, amount := 400, quantity := 20000 } == 330
#guard fedCig { good := .cigarettes, amount := 200, quantity := 20000 } == 101
#guard fedCig { good := .cigarettes, amount := 400 } == 0

end PkGlobal.Consumption
