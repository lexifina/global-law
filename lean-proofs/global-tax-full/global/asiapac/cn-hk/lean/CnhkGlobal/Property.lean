import CnhkGlobal.Pit
import TaxKernel.Global2

/-!
# Hong Kong 2025/26: rates, government rent, ad valorem stamp duty (4100, 4400)
(B: tables of the Rating and Valuation Department and IRD.) Rating Ordinance (Cap. 116): rates 5 % of rateable value (the
progressive rates on domestic rateable value above $550,000 from 2025/26 not modelled); Government Rent (Cap. 515) 3 % of
rateable value: both on the annual value (`annualValue`). Stamp Duty Ordinance Sch. 1 head 1 (1AAB) Scale 2 (from 2024-02-28
for all buyers; 2025-02-26: $100 up to $4 m): `avd`, with the marginal relief bands.
Session 11 (year in force): IRD "AVD" FAQ (Internet Archive 2025-01-06 and 2025-06-30, `cn-hk/law/hk_ird_avd_faq_wb*.html`):
Scale 2 for instruments executed from 22 February 2023 and before 26 February 2025: up to $3,000,000 $100; to $3,528,240
$100 + 10 % of the excess over $3,000,000; to $4,500,000 1.50 %; above, as from 26 February 2025 (`avd24`). The rate is taken
by the purchase record's `"date"`; an undated purchase whose duty differs between the two scales ($3,000,001-$4,323,779) is
not booked and is listed (grade C).
-/

namespace CnhkGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "Rates (5 % of rateable value)", sched := Schedule.flat 500, onAnnualValue := true, ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.home, .realEstate, .land] }

def prop1 : PropertyTax :=
  { name := "Government rent (3 %)", sched := Schedule.flat 300, onAnnualValue := true, ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "Rating Ordinance Cap. 116 s. 19" (level := .local)
      ++ prop1.charges g.assets "Government Rent (Assessment and Collection) Ordinance Cap. 515 s. 8" (level := .local) }

/-- Ad valorem stamp duty, Scale 2 (whole-amount rates with marginal relief), from 2025-02-26. -/
def avd (p : Int) : Int :=
  if p ≤ 4000000 then 100 else if p ≤ 4323780 then 100 + (p - 4000000) / 5
  else if p ≤ 4500000 then divR .down (150 * p) BP else if p ≤ 4935480 then 67500 + (p - 4500000) / 10
  else if p ≤ 6000000 then divR .down (225 * p) BP else if p ≤ 6642860 then 135000 + (p - 6000000) / 10
  else if p ≤ 9000000 then divR .down (300 * p) BP else if p ≤ 10080000 then 270000 + (p - 9000000) / 10
  else if p ≤ 20000000 then divR .down (375 * p) BP else if p ≤ 21739120 then 750000 + (p - 20000000) / 10
  else divR .down (425 * p) BP
def avdF : Family :=
  { name := "4400 ad valorem stamp duty", covers := [.transactions],
    run := fun _ g _ => (g.purchases.filter (·.kind.isRealEstate)).zipIdx.map fun (p, i) =>
      charge .transactions "Ad valorem stamp duty (Scale 2)" (max p.price p.assessed) id avd (event := s!"purchase {i + 1}") (statute := "SDO Cap. 117 Sch. 1 head 1 (1AAB) Scale 2") }

/-- Scale 2 for instruments executed before 26 February 2025 (from 22 February 2023): IRD AVD FAQ, captures 2025-01-06 and
2025-06-30. Above $4,500,000 the two scales are the same. -/
def avd24 (p : Int) : Int :=
  if p ≤ 3000000 then 100 else if p ≤ 3528240 then 100 + (p - 3000000) / 10
  else if p ≤ 4500000 then divR .down (150 * p) BP else avd p
/-- The date of purchase `i` (`"date"` on the input record), as yyyymmdd. -/
def purDay (g : CanonGlobal) (i : Nat) : Option Nat :=
  AdvanceTax.dayOfRecord ((arrField g.raw "purchases").toList.getD i Lean.Json.null)
/-- An undated purchase is booked only where both scales give the same duty. -/
def avdOn (day : Option Nat) (p : Int) : Option Int :=
  match day with
  | some d => some (if d < 20250226 then avd24 p else avd p)
  | none => if avd24 p == avd p then some (avd p) else none
def avdDF : Family :=
  { name := "4400 ad valorem stamp duty", covers := [.transactions],
    run := fun _ g _ => (g.purchases.zipIdx.filter fun (p, _) => p.kind.isRealEstate).filterMap fun (p, i) =>
      let v := max p.price p.assessed
      (avdOn (purDay g i) v).map fun d =>
        charge .transactions (if (purDay g i).any (· < 20250226) then "Ad valorem stamp duty (Scale 2, instruments before 26 February 2025)" else "Ad valorem stamp duty (Scale 2)")
          v id (fun _ => d) (event := s!"purchase {i + 1}") (statute := "SDO Cap. 117 Sch. 1 head 1 (1AAB) Scale 2 (as from 22 February 2023 / as from 26 February 2025)") }

def families : List Family := [fam0, avdDF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.purchases.zipIdx.any (fun (p, i) => p.kind.isRealEstate && (avdOn (purDay g i) (max p.price p.assessed)).isNone) then ["ad valorem stamp duty: an undated purchase between $3,000,001 and $4,323,779 (Scale 2 changed on 26 February 2025): not booked (grade C)"] else [])

#guard prop0.amount { kind := .home, value := 9000000, annualValue := 200000 } == 10000
#guard avd 3000000 == 100
#guard avd 5000000 == 112500
#guard avd24 3500000 == 50100
#guard avd 3500000 == 100
#guard avd24 4000000 == 60000
#guard avd24 6000000 == avd 6000000
#guard avdOn none 3500000 == none
#guard avdOn none 5000000 == some 112500
#guard avdOn (some 20250225) 3500000 == some 50100
#guard avdOn (some 20250226) 3500000 == some 100

end CnhkGlobal.Property
