import SETax.Assess

/-!
# The withholding tables (allmänna skattetabeller 2025) as the statute applied to a band

Skatteverket, *Teknisk beskrivning SKV 433, 2025*: a table number `T` (29-42) is a whole-percent "sammanlagd
skatte- och avgiftssats" in which "Begravningsavgift och avgift till trossamfund ska anses ingå ... med 1,16
procentenheter" (7.3); the annual income is "det högsta beloppet inom varje inkomstskikt ... multipliceras med
antalet lönetillfällen per år ... Avrundning ska göras nedåt till helt hundratal" (7.1); the jobbskatteavdrag uses
the municipal rate "exkl. 1,16 procentenheter" (7.5.2); the annual tax of column 1 is "statlig inkomstskatt +
kommunal inkomstskatt − skattereduktion för allmän pensionsavgift − skattereduktion för arbetsinkomst −
skattereduktion förvärvsinkomst + begravningsavgift och avgift till trossamfund + allmän pensionsavgift + public
service-avgift" (8).

So a cell is `person` (the statute model) run with kommun = T − 1,16 % and begravning = 1,16 %, divided by 12 and
rounded down. Checked against all 6 734 monthly rows × columns 1, 2, 3, 6 of Skatteverket's open data (every cell
equal; `harness/table_check.py`).
-/

namespace SETax
open TaxKernel

/-- The table's parameters for table number `t` (whole percent). -/
def tableParams (t : Int) : Params := { p2025 with kommun := 100 * t - 116, begravning := 116 }

/-- Columns: 1 wages under 66, 2 pension 66+, 3 wages 66+, 6 pension under 66 (SKV 433 avsnitt 3). -/
def tableAnnual (t : Int) (col : Nat) (monthTop : Int) : Int :=
  let y := toMultiple .down 100 (12 * monthTop)
  let p := tableParams t
  let r := match col with
    | 1 => person p false 40 y 0 0 0 0
    | 2 => person p false 70 0 0 y 0 0
    | 3 => person p false 70 y 0 0 0 0
    | _ => person p false 40 0 0 y 0 0
  r.total

/-- The band of the monthly table that contains a monthly wage `w`, as its highest amount (round 9). SKV 433 avsnitt 5:
"Inkomstintervallerna är 100 kr för inkomster upp t.o.m. 20 000 kr. Fr.o.m. 20 001 kr t.o.m. 80 000 kr är
inkomstintervallerna 200 kr" (the open-data rows start with one band "1 - 2000"); avsnitt 7.1: the tax of a band is
computed on "det högsta beloppet inom varje inkomstskikt". Above 80 000 kr the table gives a percentage, so the wage
itself is used. A band's own highest amount maps to itself. -/
def bandTop (w : Int) : Int :=
  if w ≤ 2000 then 2000
  else if w ≤ 20000 then ceilDiv w 100 * 100
  else if w ≤ 80000 then 20000 + ceilDiv (w - 20000) 200 * 200
  else w

/-- The monthly withholding in a cell (SKV 433 avsnitt 8, öretal dropped). -/
def tableMonthly (t : Int) (col : Nat) (monthTop : Int) : Int := tableAnnual t col monthTop / 12

end SETax
