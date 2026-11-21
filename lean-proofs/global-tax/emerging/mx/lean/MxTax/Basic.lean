import TaxKernel

/-!
# Mexico: units, the CFF's rounding, and the *tarifa* (cuota fija + % sobre el excedente)

Mexican tax tables are not written as bands. Each row of a *tarifa* (LISR arts. 96 and 152, updated in RMF
Anexo 8) gives a *límite inferior*, a *cuota fija* and a *por ciento para aplicarse sobre el excedente del límite
inferior*: the tax on `x` is `cuota fija + % × (x − límite inferior)` of the last row whose límite inferior is not
above `x`. Every amount is in **centavos** (`Int`): the statute's own limits have centavos (8,952.49) and
CFF art. 20 says "Para determinar las contribuciones se considerarán, inclusive, las fracciones del peso".
A tax before rounding is in *ticks* = centavos × 10,000 (rates in basis points), exactly as the kernel's
`Schedule.ticks`, so the two can be compared (`Theorems.lean`).

The table is not the same function as the kernel's band schedule with the same rates: each cuota fija was updated
by inflation and rounded on its own (LISR art. 152 último párrafo), so it differs by up to 1.52 centavos from the
tax of the row below at its upper limit (`Theorems.tarifa152_vs_bands`). That is a kernel gap (`CuotaFijaTable`).
-/

namespace MxTax
open TaxKernel

/-- One row of a *tarifa*: límite inferior and cuota fija in centavos, the rate in basis points. -/
structure Row where
  li : Int
  cf : Int
  rate : Int
  deriving Repr, DecidableEq, Inhabited

/-- The tax of a tarifa on `x` centavos, in ticks (centavos × 10,000): the last row (rows in the statute's order,
límites inferiores increasing) whose límite inferior is ≤ `x` gives "cuota fija" plus its rate "sobre el
excedente del límite inferior". Below the first límite inferior (0.01) the tax is nil. -/
def tarifaTicks : List Row → Int → Int
  | [], _ => 0
  | [r], x => if r.li ≤ x then r.cf * BP + r.rate * (x - r.li) else 0
  | r :: s :: rest, x =>
    if s.li ≤ x then tarifaTicks (s :: rest) x
    else if r.li ≤ x then r.cf * BP + r.rate * (x - r.li) else 0

/-- The marginal rate (bp) of the tarifa on the centavo `(x, x+1]` inside a row. -/
def tarifaRate : List Row → Int → Int
  | [], _ => 0
  | [r], x => if r.li ≤ x then r.rate else 0
  | r :: s :: rest, x => if s.li ≤ x then tarifaRate (s :: rest) x else if r.li ≤ x then r.rate else 0

/-- Ticks to centavos, halves up (the statute gives no rule below the centavo; a stated convention). -/
def ticksToCentavos (t : Int) : Int := divR .halfUp t BP

/-- CFF art. 20, tercer párrafo: "para efectuar su pago, el monto se ajustará para que las que contengan cantidades
que incluyan de 1 hasta 50 centavos se ajusten a la unidad inmediata anterior y las que contengan cantidades de 51 a
99 centavos, se ajusten a la unidad inmediata superior". From centavos to pesos: halves (50 centavos) go down. -/
def cffPesos (c : Int) : Int := divR .halfDown c 100

/-- Pesos to centavos. -/
def cts (pesos : Int) : Int := 100 * pesos

/-- `a × num / den` rounded half up (helper for percentages of amounts). -/
def mulDivHU (a num den : Int) : Int := divR .halfUp (a * num) den

end MxTax
