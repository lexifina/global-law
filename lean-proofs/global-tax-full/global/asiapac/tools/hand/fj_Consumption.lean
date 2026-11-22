import FjGlobal.Pit
import TaxKernel.Global2

/-!
# Fiji 2025: Value Added Tax (5111), two rates in 2025; excise duty (5121)

Sources: **Value Added Tax (Budget Amendment) Act 2025** (Act No. 10 of 2025, assented 21 July 2025; parliament.gov.fj
PDF, `cmp20/global/registry/ap_work/law/fj_act10_2025_vat_budget_amendment.txt`, sha256 in `law/SOURCES.tsv`):
s. 1 (2) "This Act comes into force on 1 August 2025"; s. 4 (a): section 14 (1) of the VAT Act 1991 amended by
"deleting “15%” and substituting “12.5%”" (s. 5: the same in s. 15 (1)). So supplies to 31 July 2025 bear 15 % and
from 1 August 2025 12.5 %. s. 9 adds payment services to Schedule 1 (exempt supplies), which lists financial
services. The principal Act's registration threshold and its zero-rated basic items were not read: no threshold is
applied and every basket good except financial services is taken at the standard rate.

Gap-closing session: the principal Act's rate sections were read in lexifina/fiji-law (laws.gov.fj consolidation of
2023-08-01, `act/1991/value-added-tax`): s. 14 (1) (imports) and s. 15 (1) (supplies) "at the rate of 15%" (Act 6 of 2023,
effective 1 August 2023): the rate to 31 July 2025. Its Schedules 1 (exempt) and 2 (zero-rated) were not read.

**Excise duty** (gap-closing session): Excise Act 1986, laws.gov.fj consolidation of 2026-10-21 read in lexifina/fiji-law
`act/1986/excise` (Table of Amendments: last Excise (Budget Amendment) Act 2024, No. 9 of 2024, ss. 2-4 from 1 August 2024;
none in 2025, so its rates are those of all 2025). Schedule 2 Part 1: beer 3.01 $1.90 a litre (3.00 % or less), 3.02 $2.21
(3.01 % or more); spirits 4.03 $41.61 a litre (over 11.49 % up to 57.12 %), 4.04 $72.86 a litre of alcohol (over 57.12 %),
4.05 ready-to-drink mixtures of 11.49 % or less $1.35 a litre; wine 5.01 sparkling $3.35, 5.02 still $2.93 a litre. The
Act taxes goods manufactured in Fiji; imports bear import excise under the Customs Tariff Act 1986 (not read): every line
is taken as excisable. Not booked (listed): cigarettes (1.01 $3.82 / 1.02 $2.55 per 10 by the origin of the tobacco, not
in the input), other tobacco (per kg), soft drinks and sweetened beverages ($0.40 a litre: the basket class mixes them with
water and juice), biscuits, ice cream, snack food and confectionery (food class).

Periods: a line may give `"date": "YYYY-MM-DD"` (the date of the purchases); without it the basket is spread evenly
over the year (212 days at 15 %, 153 days at 12.5 %).
-/

namespace FjGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat1 : Vat :=
  { name := "Value Added Tax (to 31 July 2025)", standard := 1500,
    classOf := fun gd => match gd with
      | .financial => .exempt
      | _ => .standard }
def vat2 : Vat := { vat1 with name := "Value Added Tax (from 1 August 2025)", standard := 1250 }

def vatStatute1 : String := "VAT Act 1991 s. 14 (1) (15 %) to 31 July 2025"
def vatStatute2 : String := "VAT Act 1991 s. 14 (1) as amended by Act No. 10 of 2025 s. 4 (a) (12.5 % from 1 August 2025)"

/-- Kernel 2.1 `DatedVat` (API §4e.1): a dated line goes to the period in force; an undated basket is spread by days
(212/365, 153/365); undated supplies take the rate in force at the end of 2025. Hand-edited: do not regenerate from
`tools/specs/FJ_cons.json`. -/
def fjVat : DatedVat :=
  { periods := [{ vat := vat1, statute := vatStatute1 }, { start := "2025-08-01", vat := vat2, statute := vatStatute2 }] }

/-- Excise Act 1986 Schedule 2 Part 1 (consolidation of 2026-10-21; rates from Act No. 9 of 2024): the duty on one basket
line in dollars, with its item; `none` when the line is not booked (no quantity or strength, or a good not modelled). -/
def exciseOn (s : Spend) : Option (Int × String) :=
  let st (i : String) : String := "Excise Act 1986 Schedule 2 Part 1 item " ++ i
  match s.good with
  | .beer => if s.quantity ≤ 0 || s.abvBp ≤ 0 then none
      else if s.abvBp ≤ 300 then some (divR .down (s.quantity * 190) 100000, st "3.01 ($1.90 a litre)")
      else some (divR .down (s.quantity * 221) 100000, st "3.02 ($2.21 a litre)")
  | .spirits => if s.quantity ≤ 0 || s.abvBp ≤ 0 then none
      else if s.abvBp ≤ 1149 then some (divR .down (s.quantity * 135) 100000, st "4.05 ($1.35 a litre)")
      else if s.abvBp ≤ 5712 then some (divR .down (s.quantity * 4161) 100000, st "4.03 ($41.61 a litre)")
      else some (divR .down (s.quantity * s.abvBp * 7286) 1000000000, st "4.04 ($72.86 a litre of alcohol)")
  | .wine => if s.quantity ≤ 0 then none else some (divR .down (s.quantity * 293) 100000, st "5.02 (still wine $2.93 a litre)")
  | _ => none

def exciseCharges (xs : List Spend) : List Charge :=
  (xs.zipIdx.filterMap fun (s, k) => (exciseOn s).map fun (d, stt) => (s, k, d, stt)).map fun (s, k, d, stt) =>
    charge .excise "Excise duty" s.amount id (fun _ => d) (event := s!"line {k + 1} ({s.good.name})") (bearer := .consumer) (statute := stt)

def exciseFamily : Family :=
  { name := "5121 excise duty (Excise Act 1986)", covers := [.excise], run := fun _ g _ => exciseCharges g.consumption }

def families : List Family := [fjVat.family "VAT (two periods)", exciseFamily]

def absent : List Absent :=
  []

def notes : List String := ["FJ 5111: VAT Act 1991 s. 14 (1) with Act No. 10 of 2025 (12.5 % from 1 August 2025)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther) then ["5121 excise on cigarettes ($3.82 or $2.55 per 10 by the origin of the tobacco, Excise Act 1986 Schedule 2 Part 1 items 1.01-1.03) and other tobacco (per kg): the input gives neither: not booked (grade C)"] else [])
  ++ (if g.consumption.any (fun s => (s.good == .beer || s.good == .spirits || s.good == .wine) && (exciseOn s).isNone) then ["5121 excise: a beer, spirits or wine line without its quantity (or strength): not booked (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .wine) then ["5121 excise: wine taken as still wine ($2.93 a litre; sparkling $3.35, item 5.01)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .nonAlcoholic || s.good == .food) then ["5121 excise on soft drinks and sweetened beverages ($0.40 a litre) and on biscuits, ice cream, snack food and confectionery (Schedule 1 items 7-11): the basket classes mix them with untaxed goods: not booked"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer || s.good == .spirits || s.good == .wine) then ["5121 excise: every line taken as excisable (the Excise Act taxes goods made in Fiji; imports bear import excise under the Customs Tariff Act 1986, not read)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food || s.good == .medicines || s.good == .education || s.good == .health || s.good == .rent || s.good == .water || s.good == .electricity) then ["zero-rated and exempt items of the principal VAT Act (Schedules 1-2) other than financial services not read: standard rate applied"] else [])

#guard vat1.embedded { good := .food, amount := 11500 } == 1500
#guard vat2.embedded { good := .food, amount := 11250 } == 1250
#guard (fjVat.basketCharges { id := "x", household := { id := "x" }, consumption := [{ good := .food, amount := 36500 }] }).map (·.due) == [2765, 1700]

#guard (fjVat.vatOn 2025 "2025-09-01").map (·.standard) == some 1250
#guard (fjVat.vatOn 2025 "2025-03-01").map (·.standard) == some 1500

-- R3 gap-closing session: excise
#guard (exciseOn { good := .beer, amount := 50, quantity := 10000, abvBp := 500 }).map (·.1) == some 22
#guard (exciseOn { good := .spirits, amount := 80, quantity := 1000, abvBp := 4000 }).map (·.1) == some 41
#guard (exciseOn { good := .spirits, amount := 80, quantity := 1000, abvBp := 6000 }).map (·.1) == some 43
#guard (exciseOn { good := .wine, amount := 40, quantity := 2000 }).map (·.1) == some 5
#guard (exciseOn { good := .cigarettes, amount := 40, quantity := 20000 }).isNone

end FjGlobal.Consumption
