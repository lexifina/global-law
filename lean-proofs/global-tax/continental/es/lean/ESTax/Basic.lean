import TaxKernel

/-!
# Spain (IRPF 2025, Comunidad de Madrid): units and the statutory tables

Money is `Int` **cents** of euro: the LIRPF states amounts with cents (art. 20 "17.673,52 euros", the Madrid scale
"13.362,22") and the AEAT liquidates to the cent. Rates are basis points (`TaxKernel.BP = 10000`): every rate the
model needs is a whole number of bp (9,50 % = 950; Madrid 10,70 % = 1070; SS 6,48 % = 648; solidarity 0,15 % = 15).
A "tick" is cents × bp, as in the kernel.

Rounding convention (stated, not in the statute): every amount the statute computes (a scale's cuota, a deduction,
a contribution) is rounded to the cent, half up, once, where it is computed. This is how the AEAT's Renta Web
prints its boxes (two decimals); the statute itself names no rounding rule for the IRPF.
-/

namespace ESTax
open TaxKernel

/-- Euros to cents. -/
def eur (e : Int) : Int := 100 * e

/-- Ticks (cents × bp) to cents, half up. -/
def tc (t : Int) : Int := divR .halfUp t BP

/-- `rate` bp of `x` cents, in cents, half up. -/
def bpOf (rate x : Int) : Int := tc (rate * x)

/-- `a × num / den`, half up (`den > 0`). -/
def mulDiv (a num den : Int) : Int := divR .halfUp (a * num) den

def sumL (l : List Int) : Int := l.foldl (· + ·) 0

/-- One row of a statutory scale as the LIRPF prints it (art. 63.1, 66.1, 74, 76; DLeg 1/2010 Madrid art. 1):
"Base liquidable – Hasta euros | Cuota íntegra – Euros | Resto base liquidable – Hasta euros | Tipo aplicable". -/
structure Row where
  /-- "Base liquidable – Hasta euros" (cents): where the row starts. -/
  lo : Int
  /-- "Cuota íntegra – Euros" (cents): the printed cuota at `lo`. -/
  cuota : Int
  /-- "Tipo aplicable – Porcentaje" (bp), charged on the "resto". -/
  rate : Int
  deriving Repr, Inhabited, DecidableEq

/-- The table read literally: the printed cuota of the last row whose start is not above `x`, plus the rate on the
rest (ticks). -/
def tableTicks : List Row → Int → Int
  | [], _ => 0
  | [r], x => r.cuota * BP + r.rate * (x - r.lo)
  | r :: s :: rest, x => if x < s.lo then r.cuota * BP + r.rate * (x - r.lo) else tableTicks (s :: rest) x

/-- The cuota the table gives on base `x` (cents, half up); nothing on a base of 0 or less. -/
def tableTax (t : List Row) (x : Int) : Int := if x ≤ 0 then 0 else tc (tableTicks t x)

/-- The same scale as a kernel `Schedule` (band starts and rates; the printed cuotas dropped). -/
def toSched (t : List Row) : Schedule := Schedule.ofList (t.map fun r => (r.lo, r.rate))

/-- The printed cuota of every row equals the band sum below it, rounded half up to the cent (checked per table
by `decide` in `Theorems.lean`). -/
def cuotasConsistent (t : List Row) : Bool :=
  t.all fun r => r.cuota == tc ((toSched t).ticks r.lo)

/-- The Spanish "mínimo" construction (LIRPF art. 63.1 2.º, 66.1 2.º, 74.1 2.º, 76 2.º; art. 56.2): the scale on the
whole base minus the scale on the part of the base that the mínimo personal y familiar fills. -/
def cuotaMinusMin (t : List Row) (base minPart : Int) : Int := tableTax t base - tableTax t minPart

end ESTax
