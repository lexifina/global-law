import TaxKernel.Basic

/-!
# TaxKernel.Unit: the unit of assessment

How a couple's incomes `a`, `b` meet a tax function `f` (units → units):

* `individual`: `f a + f b` (UK, SE, DK…: each spouse alone);
* `joint`: `f (a + b)` (aggregation with one schedule for the couple, e.g. a couple's schedule);
* `splitting`: `2 · f ((a + b) / 2)` (Germany EStG § 32a (5), Portugal, Poland's joint return);
* `quotient`: `n · f (R / n)` with `n` parts (France CGI art. 193-194; the parts are counted in halves, `n2 = 2n`),
  optionally capped per half-part (`cappedQuotient`, CGI art. 197 I 2 plafonnement).

Generic theorems (`TaxKernel.Theorems.Unit`): `splitting_le_separate`: if `f` is convex on the integers
(non-decreasing increments: any progressive `Schedule`, `Schedule.ticks_convex`) then splitting never costs more
than separate assessment, for every split of the couple's income; `splitting_eq_separate_of_equal`: and it gains
nothing when the two incomes are equal; `splitting_gain_le`: the gain is at most what moving half the gap to the
lower earner saves.
-/

namespace TaxKernel

inductive AssessUnit where
  | individual
  | joint
  | splitting
  | quotient
  deriving Repr, DecidableEq, Inhabited

def separate (f : Int → Int) (a b : Int) : Int := f a + f b
def joint (f : Int → Int) (a b : Int) : Int := f (a + b)
/-- EStG § 32a (5): "das Zweifache des Steuerbetrags, der sich für die Hälfte ihres gemeinsam zu versteuernden
Einkommens … ergibt" (half rounded down to the unit here; Germany's own rounding is applied by `f`). -/
def splitting (f : Int → Int) (a b : Int) : Int := 2 * f ((a + b) / 2)

/-- Quotient with `n2` half-parts (`n2 = 2` single, `4` couple, `5` couple + 1 child, …): `n2 · f (2R / n2) / 2`. -/
def quotient (f : Int → Int) (n2 : Int) (r : Int) : Int := n2 * f (2 * r / n2) / 2

/-- Quotient capped: the advantage of the half-parts above `base2` over the quotient with `base2` half-parts is at
most `capPerHalf` per extra half-part. -/
def cappedQuotient (f : Int → Int) (n2 base2 capPerHalf r : Int) : Int :=
  max (quotient f n2 r) (quotient f base2 r - capPerHalf * (n2 - base2))

/-- Tax of a couple under a unit. -/
def AssessUnit.tax (u : AssessUnit) (f : Int → Int) (a b : Int) (n2 : Int := 4) : Int :=
  match u with
  | .individual => TaxKernel.separate f a b
  | .joint => TaxKernel.joint f a b
  | .splitting => TaxKernel.splitting f a b
  | .quotient => TaxKernel.quotient f n2 (a + b)

/-- Discrete convexity: increments never fall. -/
def Convex (f : Int → Int) : Prop := ∀ x, f (x + 1) - f x ≤ f (x + 2) - f (x + 1)

/-- Monotone. -/
def Monotone' (f : Int → Int) : Prop := ∀ x y, x ≤ y → f x ≤ f y

/-- Transfer of an unused allowance (or a part of it, capped) from spouse 1 to spouse 2 (UK marriage allowance,
IE, NZ none…): returns the two allowances after the transfer. -/
def transferAllowance (a1 a2 inc1 cap : Int) : Int × Int :=
  let unused := pos (a1 - pos inc1)
  let t := min unused cap
  (a1 - t, a2 + t)

end TaxKernel
