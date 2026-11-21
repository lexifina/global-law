import CiTax.Params

/-!
# Côte d'Ivoire 2025: impôt sur les traitements, salaires, pensions et rentes viagères (ITS), IRVM, CNPS

The ITS is withheld monthly on the month's gross pay (art. 121-123; the annual regularisation of art. 132 recomputes
it on the same monthly basis); the year is the sum of twelve equal months (the contract's annual wage split by
`monthOf`). The RICF (art. 120) is a fixed monthly reduction by number of parts, not an income quotient.

Parts (art. 120 2°): single/divorced/widowed without child 1; married without child 2; single with k ≥ 1 children
1,5 + k/2; married with k children 2 + k/2; at most 5. Reading: each married spouse with pay is "marié"; the children
are counted by the spouse with the higher pay (the article does not say which spouse counts them).
-/

namespace CiTax
open TaxKernel

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
def monthOf (annual : Int) (m : Int) : Int := annual * m / 12 - annual * (m - 1) / 12

/-- Art. 119 bis: tax on one month's gross pay (rounded down to the franc). -/
def monthTax (g : Int) : Int := divR .down (monthly.ticks (pos g)) BP

/-- Half-parts (art. 120 2°). -/
def halfParts (married : Bool) (kids : Int) : Int :=
  let base : Int := if married then 4 else 2
  let k : Int := if kids > 0 then (if married then kids else kids + 1) else 0
  min 10 (base + k)

/-- One month's ITS after the RICF, floored at 0. -/
def monthNet (n2 g : Int) : Int := pos (monthTax g - ricfMonthly n2)

/-- Annual ITS on wages and taxable pensions of one person; retired people over 70 get 75 % off (art. 120 1°). -/
def itsYear (n2 wages pension : Int) (over70retired : Bool) : Int :=
  let pTaxable (m : Int) : Int := pos (monthOf pension m - pensionExemptMonthly)
  let t := sumInts (months.map fun m => monthNet n2 (monthOf wages m + pTaxable m))
  if over70retired then t - t * retiree70Abat / BP else t

/-- CNPS retirement contribution of one month (6,3 % of pay between the SMIG floor and the ceiling). -/
def cnpsMonth (g : Int) : Int :=
  if g ≤ 0 then 0 else divR .down (clamp smigMonthly pensionCeilingMonthly g * pensionEmployeeRate) BP

def cnpsYear (w : Int) : Int := sumInts (months.map fun m => cnpsMonth (monthOf w m))

def out (c : Canon) : Out :=
  let kids : Int := c.childrenUnder childAgeLimit
  let married := c.married && c.adults.length == 2
  let ws := c.adults.map (·.wages)
  let top := ws.foldl max 0
  let idxTop := (ws.findIdx? (· == top)).getD 0
  let its := sumInts ((c.adults.zipIdx).map fun (a, i) =>
    if a.wages ≤ 0 && a.pension ≤ 0 then 0 else
    itsYear (halfParts married (if i == idxTop then kids else 0)) a.wages a.pension
      (a.age > 70 && a.pension > 0 && a.wages ≤ 0))
  let divT := divR .down (pos c.dividends * dividendRate) BP
  let soc := sumInts (ws.map cnpsYear)
  let unsup :=
    (if c.interest != 0 then ["interest: impôt sur le revenu des créances (CGI chapter on IRC) not read; not taxed here"] else []) ++
    (if c.rentalIncome != 0 then ["rentalIncome: impôt sur le revenu foncier not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: BIC/BNC and the entreprenant regime not modelled"] else []) ++
    ["employeeSocial: CNPS retirement 6,3 % only (CNPS page, official secondary); CMU health contribution not modelled",
     "children aged 18-26 in education (art. 120 2°) cannot be expressed; not counted"]
  Out.make c "CI" "XOF" (its + divT) (employeeSocial := soc)
    (detail := [Out.d "its" its, Out.d "dividendTax" divT,
                Out.d "taxableIncome" (sumInts (c.adults.map fun a => pos a.wages)),
                Out.dStr "note" "CGI art. 119 bis monthly barème on gross pay, RICF art. 120 by parts (Ord. 2023-719); IRVM 17 % (LF 2025 art. 37); CNPS 6,3 %"])
    (unsupported := unsup)

def country : Country :=
  { code := "CI", name := "Côte d'Ivoire (ITS, IRVM, CNPS)", currency := "XOF", year := "2025", compute := out }

end CiTax
