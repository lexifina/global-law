import TaxKernel.Global2
import R5Common

/-!
# Israel 2025: vehicle licence fee (אגרת רישיון רכב, 5200)

Transport Regulations 5721-1961 (תקנות התעבורה), First Schedule part ג, item 2 (private passenger cars by price group
and age) and item 5 (motorcycles); reg. 15א(ב): the fees change on **1 April** each year with the CPI. Read in the
official gazette (Kovetz HaTakanot, Reshumot; PDFs mirrored on olaw.org.il, linked from the Hebrew Wikisource
consolidation):
* **1 January - 31 March 2025**: Transport Notice (Fees) 5784-2024, KT 11161 of 19/02/2024 p. 1738 (amounts from
  1 April 2024; `law/il_takanot-11161.pdf`);
* **1 April - 31 December 2025**: Transport Notice (Fees) 5785-2025, KT 11753 of 17/02/2025 p. 1182 (amounts from
  1 April 2025; `law/il_takanot-11753.pdf`).
Item 2(א) (NIS a year; columns: year of manufacture or going on the road up to 3 years / 4-6 / 7-10 / over 10):

  | group | from 1/4/2024                 | from 1/4/2025                 |
  |-------|-------------------------------|-------------------------------|
  | 1     | 1 194 / 1 046 / 917 / 801     | 1 233 / 1 080 / 947 / 827     |
  | 2     | 1 519 / 1 325 / 1 161 / 1 015 | 1 568 / 1 368 / 1 198 / 1 048 |
  | 3     | 1 831 / 1 602 / 1 403 / 1 224 | 1 891 / 1 654 / 1 449 / 1 264 |
  | 4     | 2 185 / 1 857 / 1 580 / 1 342 | 2 255 / 1 918 / 1 631 / 1 386 |
  | 5     | 2 502 / 2 061 / 1 701 / 1 406 | 2 583 / 2 128 / 1 756 / 1 451 |
  | 6     | 3 552 / 2 664 / 1 998 / 1 495 | 3 667 / 2 750 / 2 063 / 1 544 |
  | 7     | 5 062 / 3 542 / 2 479 / 1 737 | 5 226 / 3 657 / 2 560 / 1 793 |

Item 5 motorcycles (cm³ up to 50 / 51-150 / 151 and more; electric 5(ב)): 49 / 183 / 337; 49 (from 1/4/2024) and
51 / 189 / 348; 51 (from 1/4/2025).

Price group (Appendix א, by the consumer price of the car; the group is fixed at first registration): table 1טז
(registered 2017-2021: up to 101 000 / 122 000 / 144 000 / 162 000 / 210 000 / 299 000 / above), 1יז (2022-2023:
106 000 / 128 000 / 151 000 / 170 000 / 221 000 / 314 000), 1יח (2024: 111 000 / 135 000 / 159 000 / 179 000 /
232 000 / 330 000; KT 11017 of 24/12/2023 p. 1036, `law/il_takanot-11017.pdf`), 1יט (2025: 114 000 / 138 000 /
162 000 / 183 000 / 238 000 / 338 000; KT 11594 of 12/12/2024 p. 426, `law/il_takanot-11594.pdf`). Tables 1טז and
1יז from the Wikisource consolidation (`law/il_takanot_taavura_rev3001187.txt`, revision of 27/03/2026, before the
April 2026 update; unofficial reprint). Older tables are omitted there: cars first registered before 2017 are not
computed (grade C).

Transport Ordinance s. 84 (פקודת התעבורה; Wikisource, `law/il_pkudat_taavura.txt`) adds to the licence fee of a
motor vehicle other than a motorcycle an amount for the Israeli Public Broadcasting Corporation: NIS 141 from
1/4/2024 (KT 11161 p. 1749), NIS 139 from 1/4/2025 (KT 11753 p. 1193).

**Two windows.** The licence is given for a year and renewed each year (item 2: "כשהרישיון ניתן לתקופה של שנה"),
at the amounts in force on the day. With kernel 2.6.0 `firstRegMonth` given, the 2025 renewal (or the first licence of
a car registered in 2025) is taken in that month: January-March at the April 2024 amounts, April-December at the April
2025 amounts (renewal on the anniversary of first registration: an assumption, the regulations fix no month). Without
it, the months-weighted mean (3 × the April 2024 amount + 9 × the April 2025 amount) / 12, rounded down to the shekel. Input: vehicle `vehicleKind`
"car" with `listPrice` (price when new) and `firstRegYear` (age = 2025 − it); "motorcycle" with `engineCcm` or `fuel`
"electric". The owner pays. Not modelled: commercial vehicles (item 2(א1), table 1א; item 3 by weight), buses,
taxis, the flexible-fuel and safety-system reductions, exemptions (reg. 290א). **Grade B** (amounts read in the
gazette; the renewal-month weighting and the unofficial 2017-2023 group tables).
-/

namespace IlGlobal
open TaxKernel TaxKernel.Global R5Common

/-- Appendix א upper bounds of price groups 1-6 by year of first registration (group 7: above the last). -/
def groupBounds (y : Nat) : Option (List Int) :=
  if 2017 ≤ y ∧ y ≤ 2021 then some [101000, 122000, 144000, 162000, 210000, 299000]
  else if 2022 ≤ y ∧ y ≤ 2023 then some [106000, 128000, 151000, 170000, 221000, 314000]
  else if y = 2024 then some [111000, 135000, 159000, 179000, 232000, 330000]
  else if y = 2025 then some [114000, 138000, 162000, 183000, 238000, 338000]
  else none

/-- price group 1-7: one more than the number of bounds below the price (bounds are "up to"). -/
def priceGroup (bs : List Int) (p : Int) : Nat := (bs.filter (· < p)).length + 1

/-- age column: up to 3 years / 4-6 / 7-10 / over 10 -/
def ageCol (age : Int) : Nat := if age ≤ 3 then 0 else if age ≤ 6 then 1 else if age ≤ 10 then 2 else 3

def fee2024 : List (List Int) :=
  [[1194, 1046, 917, 801], [1519, 1325, 1161, 1015], [1831, 1602, 1403, 1224], [2185, 1857, 1580, 1342],
   [2502, 2061, 1701, 1406], [3552, 2664, 1998, 1495], [5062, 3542, 2479, 1737]]
def fee2025 : List (List Int) :=
  [[1233, 1080, 947, 827], [1568, 1368, 1198, 1048], [1891, 1654, 1449, 1264], [2255, 1918, 1631, 1386],
   [2583, 2128, 1756, 1451], [3667, 2750, 2063, 1544], [5226, 3657, 2560, 1793]]

def cell (t : List (List Int)) (g c : Nat) : Int := (t.getD (g - 1) []).getD c 0

/-- 3 months at the April 2024 amount, 9 at the April 2025 amount. -/
def weighted (a b : Int) : Int := divR .down (3 * a + 9 * b) 12

/-- the tariff of the renewal month (kernel 2.6.0 `firstRegMonth`, 1-12; 0: not given → `weighted`) -/
def window (m : Nat) (a b : Int) : Int := if m = 0 then weighted a b else if m ≤ 3 then a else b

def windowNote (m : Nat) : String :=
  if m = 0 then "KT 11161 (from 1/4/2024) × 3/12 + KT 11753 (from 1/4/2025) × 9/12 (no renewal month)"
  else if m ≤ 3 then s!"KT 11161 (amounts from 1/4/2024; renewal month {m})" else s!"KT 11753 (amounts from 1/4/2025; renewal month {m})"

def carFee (y : Nat) (price : Int) (m : Nat := 0) : Option Int :=
  (groupBounds y).map fun bs =>
    let g := priceGroup bs price
    let c := ageCol (2025 - (y : Int))
    window m (cell fee2024 g c) (cell fee2025 g c)

/-- s. 84 broadcasting addition: 141 (from 1/4/2024), 139 (from 1/4/2025). -/
def ipbcAddition (m : Nat := 0) : Int := window m 141 139

def motoFee (v : Vehicle) : Option Int :=
  let m := v.firstRegMonth
  if v.fuel == .electric then some (window m 49 51)
  else if v.engineCcm < 0 then none
  else if v.engineCcm ≤ 50 then some (window m 49 51)
  else if v.engineCcm ≤ 150 then some (window m 183 189)
  else some (window m 337 348)

def carFeeOf (v : Vehicle) : Option Int := if v.listPrice ≥ 0 then carFee v.firstRegYear v.listPrice v.firstRegMonth else none

def vehicleCharges (v : Vehicle) (k : Nat) : List Charge :=
  let ev := s!"vehicle {k + 1} ({v.source})"
  if v.kind == "car" then
    match carFeeOf v with
    | some f =>
      let grp := priceGroup ((groupBounds v.firstRegYear).getD []) v.listPrice
      [charge .useOfGoods "אגרת רישיון רכב (licence fee, private car)" v.listPrice pos (fun _ => f) (event := ev)
         (statute := s!"Transport Regulations First Schedule part ג item 2(א), Appendix א (price group {grp}); {windowNote v.firstRegMonth}"),
       charge .useOfGoods "תוספת אגרה לתאגיד השידור (licence fee addition, s. 84)" v.listPrice pos (fun _ => ipbcAddition v.firstRegMonth) (event := ev)
         (statute := s!"Transport Ordinance s. 84: NIS 141 (from 1/4/2024) / NIS 139 (from 1/4/2025); {windowNote v.firstRegMonth}")]
    | none => []
  else if v.kind == "motorcycle" then
    match motoFee v with
    | some f => [charge .useOfGoods "אגרת רישיון אופנוע (licence fee, motorcycle)" (max v.engineCcm 0) pos (fun _ => f) (event := ev)
         (statute := s!"Transport Regulations First Schedule part ג item 5 (by cm³; electric 5(ב)); {windowNote v.firstRegMonth}")]
    | none => []
  else []

def vehicles : Family :=
  { name := "5200 אגרת רישיון רכב (vehicle licence fee)", covers := [.useOfGoods],
    run := fun _ g _ => g.vehicles.zipIdx.flatMap fun (v, k) => vehicleCharges v k }

def vehiclesUnsupported (g : CanonGlobal) : List String :=
  (g.vehicles.zipIdx.filterMap fun (v, k) =>
    if v.kind == "car" then
      if (carFeeOf v).isSome then none
      else some s!"5200 licence fee: vehicle {k + 1} ({v.source}): needs listPrice and a first registration 2017-2025 (older price-group tables not read) (grade C)"
    else if v.kind == "motorcycle" then
      if (motoFee v).isSome then none else some s!"5200 licence fee: vehicle {k + 1} ({v.source}): motorcycle engineCcm not given (grade C)"
    else some s!"5200 licence fee: vehicle {k + 1} ({v.source}, {v.kind}): commercial and other vehicle fees not modelled (grade C)")
  ++ (if g.vehicles.isEmpty then [] else
      ["licence fee: renewal taken in the month of first registration (firstRegMonth: January-March April-2024 amounts, else April-2025); without it 3/12 + 9/12 of the two; age = 2025 − firstRegYear"])

#guard priceGroup [114000, 138000, 162000, 183000, 238000, 338000] 114000 == 1
#guard priceGroup [114000, 138000, 162000, 183000, 238000, 338000] 120000 == 2
#guard priceGroup [114000, 138000, 162000, 183000, 238000, 338000] 400000 == 7
#guard carFee 2025 120000 == some 1555
#guard carFee 2019 200000 == some 2111
#guard carFee 2012 200000 == none
#guard ipbcAddition == 139
#guard ipbcAddition 2 == 141
#guard carFee 2025 120000 2 == some 1519
#guard carFee 2019 200000 7 == some 2128
#guard weighted 183 189 == 187

end IlGlobal
