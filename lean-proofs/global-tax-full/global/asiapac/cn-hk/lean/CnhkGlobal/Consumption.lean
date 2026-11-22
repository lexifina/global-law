import CnhkGlobal.Pit

/-!
# Hong Kong SAR 2025: duties on dutiable commodities (5121); no VAT or sales tax

Source: Dutiable Commodities Ordinance (Cap. 109) Schedule 1, read in lexifina/hong-kong-law `cap-109/sch-1.md` (git history of the Laws of Hong Kong; versions in force from 2024-10-16, L.N. 136 and 193 of 2024, and from 2025-09-19, Ordinance 39 of 2025 s. 9, which changes only the heading's section references). The same rates apply all through
2025.
* **Part I** para. 1: liquor of not more than 30 % by volume and wine: 0 %. Para. 1A-1C (from 16 October 2024): liquor of
  more than 30 %: 100 % of the value on the first $200 and 10 % on the remainder, per bottle of not more than 1 litre, and
  for larger bottles per litre of the value per litre (1B-1C). The basket gives no bottle size: the per-litre rule is used
  (exact for bottles of 1 litre or more; a smaller bottle pays more under para. 1A). The value is the s. 26A value; the
  basket's retail price, net of the duty, is used (the retail margin is inside it).
* **Part II** para. 1 (a): $3,306 per 1,000 cigarettes (L.N. 25 of 2024, from 28 February 2024).
* **Part III** para. 1 (d): unleaded petrol $6.06 per litre; para. 1B (b): Euro V diesel $0 from 14 July 2008 (road diesel
  sold in Hong Kong meets the Euro V specification: no charge).
Methyl alcohol (Part IV), cigars and other tobacco (Part II (b)-(d)) are not in the basket's classes (other tobacco is
listed when present).
-/

namespace CnhkGlobal.Consumption
open TaxKernel TaxKernel.Global

def st (p : String) : String := "Dutiable Commodities Ordinance (Cap. 109) Schedule 1 " ++ p

/-- Part I para. 1A-1C (per litre): with `p` the tax-inclusive amount and `l` litres (thousandths), the value before the duty `b`
solves p = b + b (b ≤ $200 a litre) or p = b + 180 l + 0.1 b (above): the duty is p − b. -/
def liquorDuty (p q : Int) : Int :=
  if q ≤ 0 then 0
  else if p * 1000 ≤ 400 * q then p - divR .down p 2
  else p - divR .down ((p - divR .down (180 * q) 1000) * 10) 11

/-- The duty on one basket line; `none` when the line lacks the quantity or strength the rate needs. -/
def dutyOn (s : Spend) : Option (Int × String) :=
  match s.good with
  | .cigarettes => if s.quantity > 0 then some (divR .down (s.quantity * 3306) 1000000, st "Part II para. 1 (a): $3,306 per 1,000 cigarettes") else none
  | .petrol => if s.quantity > 0 then some (divR .down (s.quantity * 606) 100000, st "Part III para. 1 (d): unleaded petrol $6.06 per litre") else none
  | .spirits => if s.abvBp ≤ 0 || s.quantity ≤ 0 then none
      else if s.abvBp ≤ 3000 then some (0, st "Part I para. 1: liquor of not more than 30 % by volume 0 %")
      else some (liquorDuty s.amount s.quantity, st "Part I para. 1A-1C: 100 % on the first $200 of the value per litre, 10 % on the remainder")
  | .beer => some (0, st "Part I para. 1: liquor of not more than 30 % by volume 0 %")
  | .wine => some (0, st "Part I para. 1: wine 0 %")
  | .diesel => some (0, st "Part III para. 1B (b): Euro V diesel $0 from 14 July 2008")
  | _ => none

def dutiable (g : Good) : Bool := [Good.cigarettes, .petrol, .spirits, .beer, .wine, .diesel].contains g

def basketCharges (xs : List Spend) : List Charge :=
  (xs.zipIdx.filterMap fun (s, k) => (dutyOn s).map fun (d, stt) => (s, k, d, stt)).map fun (s, k, d, stt) =>
    charge .excise "Duty on dutiable commodities (Cap. 109)" s.amount id (fun _ => d) (event := s!"line {k + 1} ({s.good.name})")
      (bearer := .consumer) (statute := stt)

def families : List Family :=
  [{ name := "5121 duties on dutiable commodities (Cap. 109)", covers := [.excise],
     run := fun _ g _ => basketCharges g.consumption }]

def absent : List Absent :=
  [{ oecd := .vat, why := "no VAT, GST or general sales tax ordinance in Hong Kong (only the Dutiable Commodities Ordinance Cap. 109 taxes goods)" }]

def notes : List String := ["CN-HK 5121: Cap. 109 Schedule 1 read in lexifina/hong-kong-law (versions in force from 2024-10-16 and 2025-09-19: same rates)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => dutiable s.good && (dutyOn s).isNone) then ["5121 Cap. 109 duty: a cigarette, petrol or spirits line without its quantity (or the spirits' strength): not booked (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .tobaccoOther) then ["5121 Cap. 109 Part II (b)-(d): cigars $4,258/kg, Chinese prepared tobacco $811/kg, other manufactured tobacco $4,005/kg: the basket's other-tobacco line has no mass: not booked (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits && s.abvBp > 3000) then ["5121 liquor above 30 %: the per-litre rule (Sch. 1 Part I para. 1B-1C) on the retail value net of the duty; bottles under 1 litre pay more (para. 1A); the s. 26A value excludes the retail margin"] else [])

-- 20 sticks: $66.12 -> 66
#guard (dutyOn { good := .cigarettes, amount := 100, quantity := 20000 }).map (·.1) == some 66
-- 40 litres of petrol: $242.40 -> 242
#guard (dutyOn { good := .petrol, amount := 900, quantity := 40000 }).map (·.1) == some 242
-- 1 litre of 40 % spirits at $300 (value $150): duty 150
#guard (dutyOn { good := .spirits, amount := 300, quantity := 1000, abvBp := 4000 }).map (·.1) == some 150
-- 1 litre at $730: value (730 - 180) / 1.1 = 500, duty 0.1 x 500 + 180 = 230
#guard (dutyOn { good := .spirits, amount := 730, quantity := 1000, abvBp := 4000 }).map (·.1) == some 230
#guard (dutyOn { good := .spirits, amount := 730, quantity := 1000 }).isNone
#guard (dutyOn { good := .wine, amount := 200, quantity := 750 }).map (·.1) == some 0
#guard (basketCharges [{ good := .clothing, amount := 100 }]).length == 0
#guard absent.length == 1

end CnhkGlobal.Consumption
