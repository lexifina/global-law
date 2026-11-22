import TaxKernel.Global2.Basket

/-!
# TaxKernel.Global2.DatedVat (2.1.0): VAT whose rates change during the year (OECD 5111)

A `DatedVat` is a list of `VatPeriod`s in date order, each a full 2.0 `Vat` (rates, classes, threshold) with the date
it starts and its statute. The first period covers the year from 1 January whatever its `start`; period `i` runs to
the day before period `i + 1` starts.

**Basket** (`basketCharges`): a line with a date (`"date"` on the line, else on the entity) goes wholly to the period
in force on that date; an undated line is spread over the year by days, `amount × days_i / days_of_year` rounded down
in each period (`scaleDays`). One `Vat.basketCharge` per period that receives a line; when undated lines were spread,
its statute gets `splitNote days_i days_of_year` (default `"; 212/365 of the basket"`).

**Supplies of a company** (`businessCharges`): with a date on the entity, the period in force then; otherwise
`undatedSupplies`: `.endOfYear` (the last period, statute + `endNote year`) or `.split` (sales and inputs spread by days;
the registration threshold is still tested on the year's turnover).

This is the pattern FJ (15 % → 12.5 % on 2025-08-01), VN (Res. 204/2025: 8 % from 2025-07-01) and IN (GST rates
from 2025-09-22) need. Theorems: `daysOf_single` (one period covers the whole year), `basketCharges_nil`,
`scaleDays_le` (a period's share of a line never exceeds it).
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-- One VAT regime and the date it starts. -/
structure VatPeriod where
  /-- first day the period applies, `"YYYY-MM-DD"` (`""`: 1 January; ignored for the first period) -/
  start : String := ""
  vat : Vat
  statute : String := ""

inductive UndatedSupplies where
  /-- the regime in force at the end of the year -/
  | endOfYear
  /-- sales and inputs spread over the periods by days -/
  | split
  deriving Repr, DecidableEq, Inhabited, BEq

structure DatedVat where
  periods : List VatPeriod
  undatedSupplies : UndatedSupplies := .endOfYear
  splitNote : Nat → Nat → String := fun d n => s!"; {d}/{n} of the basket"
  splitNoteSupplies : Nat → Nat → String := fun d n => s!"; {d}/{n} of the year's supplies"
  endNote : Nat → String := fun y => s!" (no date given: the rate in force at the end of {y})"

namespace DatedVat

/-- Day (of `year`) each period starts; the first starts on day 0. -/
def starts (dv : DatedVat) (year : Nat) : List Nat :=
  dv.periods.zipIdx.map fun (p, i) => if i = 0 then 0 else startDay year p.start

/-- Days in period `i`. -/
def daysOf (dv : DatedVat) (year : Nat) (i : Nat) : Nat :=
  (dv.starts year).getD (i + 1) (daysInYear year) - (dv.starts year).getD i 0

/-- The period in force on day `d`: the last one started on or before it. -/
def periodAt (dv : DatedVat) (year : Nat) (d : Nat) : Nat :=
  (dv.starts year).zipIdx.foldl (fun acc (st, i) => if st ≤ d then i else acc) 0

def lineDay (year : Nat) (x : SpendX) : Option Nat := dayOfYear? year x.date

/-- The basket lines that fall in period `i`; undated lines by their share of the year. -/
def linesIn (dv : DatedVat) (year : Nat) (xs : List (Spend × SpendX)) (i : Nat) : List Spend :=
  xs.filterMap fun (s, x) => match lineDay year x with
    | some day => if dv.periodAt year day = i then some s else none
    | none => some { s with amount := scaleDays s.amount (dv.daysOf year i) (daysInYear year) }

def basketChargesOf (dv : DatedVat) (year : Nat) (xs : List (Spend × SpendX)) : List Charge :=
  if xs.isEmpty then [] else
  let n := daysInYear year
  let undated := xs.any fun (_, x) => (lineDay year x).isNone
  dv.periods.zipIdx.filterMap fun (p, i) =>
    let d := dv.daysOf year i
    let dated := xs.any fun (_, x) => match lineDay year x with
      | some day => dv.periodAt year day == i
      | none => false
    if !dated && (!undated || d == 0) then none else
    let note := if undated && d != n then dv.splitNote d n else ""
    some (p.vat.basketCharge (dv.linesIn year xs i) (p.statute ++ note))

/-- VAT on the household basket, one charge per period that receives a line. -/
def basketCharges (dv : DatedVat) (g : CanonGlobal) : List Charge := dv.basketChargesOf g.year (consumptionX g)

/-- VAT on a company's supplies (`Vat.businessCharge` of the period(s)). -/
def businessCharges (dv : DatedVat) (g : CanonGlobal) : List Charge :=
  if !(g.entity == .company && !g.company.sales.isEmpty) then [] else
  let y := g.year
  let n := daysInYear y
  match (g.str? "date").bind (dayOfYear? y) with
  | some day => match dv.periods[dv.periodAt y day]? with
    | some p => [p.vat.businessCharge g.company p.statute]
    | none => []
  | none => match dv.undatedSupplies with
    | .endOfYear => match dv.periods.getLast? with
      | some p => [p.vat.businessCharge g.company (p.statute ++ dv.endNote y)]
      | none => []
    | .split => dv.periods.zipIdx.filterMap fun (p, i) =>
      let d := dv.daysOf y i
      if d == 0 then none else
      let sc := fun (ss : List Supply) => ss.map fun s => { s with net := scaleDays s.net d n }
      let co := { g.company with sales := sc g.company.sales, inputs := sc g.company.inputs }
      some (p.vat.businessCharge co (p.statute ++ (if d != n then dv.splitNoteSupplies d n else "")))

def charges (dv : DatedVat) (g : CanonGlobal) : List Charge := dv.basketCharges g ++ dv.businessCharges g

/-- The 5111 family: basket and supplies. -/
def family (dv : DatedVat) (name : String) : Family :=
  { name := s!"5111 {name}", covers := [.vat], run := fun _ g _ => dv.charges g }

/-- The rate in force on a date (for a country's own transaction-level rules). -/
def vatOn (dv : DatedVat) (year : Nat) (date : String) : Option Vat :=
  (dv.periods[dv.periodAt year (startDay year date)]?).map (·.vat)

end DatedVat

theorem DatedVat.daysOf_single (p : VatPeriod) (y : Nat) (u : UndatedSupplies) :
    ({ periods := [p], undatedSupplies := u } : DatedVat).daysOf y 0 = daysInYear y := by
  simp [DatedVat.daysOf, DatedVat.starts]

theorem DatedVat.basketCharges_nil (dv : DatedVat) (y : Nat) : dv.basketChargesOf y [] = [] := by
  simp [DatedVat.basketChargesOf]

end TaxKernel.Global
