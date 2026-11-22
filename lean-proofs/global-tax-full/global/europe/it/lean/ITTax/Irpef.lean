import ITTax.Params

/-!
# IRPEF for one taxpayer: TUIR artt. 10-13, 16-ter; L. 207/2024 cc. 4-6; DL 3/2020 art. 1

Italy taxes each spouse separately (no joint return since Corte cost. 179/1976); the family enters only through
art. 12 (a dependent spouse, children aged 21-29) and art. 16-ter (number of children). All amounts in cents.

Order of the statute (art. 11 c. 3): imposta lorda on reddito complessivo net of oneri deducibili (art. 11 c. 1);
"l'imposta netta è determinata operando sull'imposta lorda, fino alla concorrenza del suo ammontare, le
detrazioni" (art. 11 c. 3: non-refundable); then the two cash "somme" that are not detrazioni: the trattamento
integrativo (DL 3/2020 art. 1) and the 2025 cuneo sum (L. 207/2024 c. 4), both "non concorre alla formazione del
reddito", paid through the payroll even when no tax is due (refundable).
-/

namespace ITTax
open TaxKernel

/-- "si assume nelle prime quattro cifre decimali" (art. 13 c. 6; art. 12 c. 4): a ratio truncated to 10⁻⁴,
returned as an integer number of 10⁻⁴; 0 when the ratio is not positive. -/
def r4 (num den : Int) : Int := if num ≤ 0 then 0 else (num * 10000) / den

/-- `amt` (cents) × ratio (10⁻⁴), to the cent, half up. -/
def mulR4 (amt r : Int) : Int := divR .halfUp (amt * r) 10000

/-- `amt` (cents) × num / den exactly, to the cent, half up (ratios without the four-decimal rule). -/
def mulFrac (amt num den : Int) : Int := divR .halfUp (amt * num) den

/-- Art. 13 c. 1 and c. 1.1: the detrazione for employment income, full year. -/
def detrDip (r : Int) (y : Nat := 2025) : Int :=
  let base :=
    if r ≤ eur 15000 then dipAY y
    else if r ≤ eur 28000 then dipB + mulR4 dipBInc (r4 (eur 28000 - r) (eur 13000))
    else if r ≤ eur 50000 then mulR4 dipB (r4 (eur 50000 - r) (eur 22000))
    else 0
  base + (if eur 25000 < r ∧ r ≤ eur 35000 then dipBonus else 0)

/-- Art. 13 c. 3 and c. 3-bis: the detrazione for pension income, full year. -/
def detrPen (r : Int) : Int :=
  let base :=
    if r ≤ eur 8500 then penA
    else if r ≤ eur 28000 then penB + mulR4 penBInc (r4 (eur 28000 - r) (eur 19500))
    else if r ≤ eur 50000 then mulR4 penB (r4 (eur 50000 - r) (eur 22000))
    else 0
  base + (if eur 25000 < r ∧ r ≤ eur 29000 then penBonus else 0)

/-- Art. 13 c. 5 and c. 5-ter: the detrazione for self-employment (lavoro autonomo) income. -/
def detrAut (r : Int) : Int :=
  let base :=
    if r ≤ eur 5500 then autA
    else if r ≤ eur 28000 then autB + mulR4 autBInc (r4 (eur 28000 - r) (eur 22500))
    else if r ≤ eur 50000 then mulR4 autB (r4 (eur 50000 - r) (eur 22000))
    else 0
  base + (if eur 11000 < r ∧ r ≤ eur 17000 then autBonus else 0)

/-- Art. 12 c. 1 a), b) and c. 4: the detrazione for a dependent spouse. -/
def detrConiuge (r : Int) : Int :=
  let base :=
    if r ≤ eur 15000 then
      let q := r4 r (eur 15000)
      if q = 10000 then conB else conA - mulR4 conAMinus q
    else if r ≤ eur 40000 then conB
    else if r ≤ eur 80000 then mulR4 conB (r4 (eur 80000 - r) (eur 40000))
    else 0
  base + conSupp.foldl (fun a (lo, hi, s) => if lo < r ∧ r ≤ hi then a + s else a) 0

/-- Art. 12 c. 1 c) and c. 4: the detrazione for `n` children aged 21-29 (each), before the split between parents:
"Se i rapporti ... sono pari a zero, minori di zero o uguali a uno, le detrazioni non competono". -/
def detrFigli (n : Nat) (r : Int) : Int :=
  if n = 0 then 0 else
  let d := figlioBase + figlioStep * ((n : Int) - 1)
  let q := r4 (d - r) d
  if q ≤ 0 ∨ q ≥ 10000 then 0 else (n : Int) * mulR4 figlio q

/-- TUIR art. 12 c. 1 c) as in force on 2022-01-15 (`Params.figlioOldU3`): the detrazione for children of every age
(1.220 under three, +200 each with more than three), before the split between parents, for the whole year;
January-February 2022 take 2/12 of it (art. 12 c. 3). -/
def detrFigliOld (ages : List Nat) (r : Int) : Int :=
  let n := ages.length
  if n = 0 then 0 else
  let d := figlioBase + figlioStep * ((n : Int) - 1)
  let q := r4 (d - r) d
  if q ≤ 0 ∨ q ≥ 10000 then 0 else
  let per (a : Nat) : Int := (if a < 3 then figlioOldU3 else figlio) + (if n > 3 then figlioOldMany else 0)
  ages.foldl (fun acc a => acc + mulR4 (per a) q) 0

/-- L. 207/2024 art. 1 c. 6: the extra 2025 detrazione for employees with reddito complessivo 20.000-40.000 (no
four-decimal rule: the exact product, to the cent). -/
def ulteriore (r : Int) : Int :=
  if r ≤ eur 20000 then 0
  else if r ≤ eur 32000 then ulterioreFull
  else if r ≤ eur 40000 then mulFrac ulterioreFull (eur 40000 - r) (eur 8000)
  else 0

/-- L. 207/2024 art. 1 c. 4: the 2025 cuneo sum, a percentage of the whole employment income `rld` chosen by `rld`
(full year), for reddito complessivo up to 20.000. -/
def cuneoRate (rld : Int) : Int :=
  if rld ≤ cuneoA then cuneoRateA else if rld ≤ cuneoB then cuneoRateB else cuneoRateC
def cuneoSomma (r rld : Int) : Int :=
  if rld ≤ 0 ∨ r > cuneoLimit then 0 else divR .halfUp (cuneoRate rld * rld) BP

/-- Imposta lorda (art. 11 c. 1), to the cent, half up. -/
def lorda (imponibile : Int) (y : Nat := 2025) : Int := (irpefSchedY y).tax Rule.unitHalfUp (pos imponibile)

/-- DL 3/2020 art. 1 c. 1: the trattamento integrativo (full year). `lordaLav`: imposta lorda on the employment
income; `lordaTot`: the whole imposta lorda; `d12`: art. 12 detrazioni. -/
def trattIntegrativo (r rld lordaTot d12 : Int) (y : Nat := 2025) : Int :=
  if rld ≤ 0 then 0
  else if r ≤ eur 15000 then (if lorda rld y > detrDip r y - tiMinusY y then tiFull else 0)
  else if r ≤ eur 28000 then
    let s := d12 + detrDip r y
    if s > lordaTot then min tiFull (s - lordaTot) else 0
  else 0

/-- Art. 16-ter: the most oneri (here: the charitable gifts) admitted to the detrazione. -1 = no ceiling. -/
def oneriCeiling (r : Int) (nFigli : Nat) : Int :=
  let b := capBase r
  if b < 0 then -1 else b * capCoeff nFigli / 100

/-- What one taxpayer brings (cents). -/
structure Person where
  wages : Int := 0          -- gross pay
  inps : Int := 0           -- employee social contributions withheld (excluded from income, TUIR art. 51 c. 2 a))
  pension : Int := 0
  selfEmp : Int := 0        -- net self-employment income, ordinary regime
  rentIrpef : Int := 0      -- rent taxed under IRPEF (95 % of the canone already applied)
  rentCed : Int := 0        -- canone under cedolare secca (outside IRPEF, but counts for the income tests)
  pensionContrib : Int := 0
  charity : Int := 0
  spouseDependent : Bool := false
  kids2129Share : Int := 0  -- percent of the art. 12 c) detrazione this parent takes (0, 50, 100)
  kids2129 : Nat := 0
  kidsDependent : Nat := 0  -- for art. 16-ter c. 3
  /-- tax year (2022-2025); `oecd`: the OECD's conventions for earlier years (see `Household`) -/
  year : Nat := 2025
  oecd : Bool := false
  /-- 2022 only: ages of all children, for the January-February art. 12 c. 1 c) of 2022-01-15 -/
  kidsOld : List Nat := []
  deriving Repr, Inhabited

/-- Everything the statute computes for one taxpayer. -/
structure Irpef where
  rld : Int
  redditoComplessivo : Int
  redditoRif : Int          -- the income for the detrazioni tests (incl. cedolare income, D.Lgs. 23/2011 art. 3 c. 7)
  oneriDeducibili : Int
  imponibile : Int
  lorda : Int
  d13 : Int
  d12 : Int
  ulteriore : Int
  dCharity : Int
  netta : Int
  ti : Int
  cuneo : Int
  deriving Repr, Inhabited

def Person.irpef (p : Person) : Irpef :=
  let rld := pos (p.wages - p.inps)
  let rc := rld + p.pension + p.selfEmp + p.rentIrpef
  let rr := rc + p.rentCed
  let ded := min (pos p.pensionContrib) (min pensionCap (pos rc))
  let imp := pos (rc - ded)
  let y := p.year
  let l := lorda imp y
  -- art. 13: the three detrazioni are "non cumulabile" with one another: the largest applicable one.
  let d13 := max (if rld > 0 then detrDip rr y else 0)
             (max (if p.pension > 0 then detrPen rr else 0) (if p.selfEmp > 0 then detrAut rr else 0))
  -- children: 2022 = 2/12 of the art. 12 c. 1 c) of 2022-01-15 (every age) + 10/12 of the post-March rule (21 and
  -- over); the OECD convention leaves January-February out (12/12 of the post-March rule)
  let kidsD := if y = 2022 ∧ !p.oecd then
      divR .halfUp (2 * detrFigliOld p.kidsOld rr + 10 * detrFigli p.kids2129 rr) 12
    else detrFigli p.kids2129 rr
  let d12 := (if p.spouseDependent then detrConiuge rr else 0)
             + divR .halfUp (kidsD * p.kids2129Share) 100
  let ul := if rld > 0 ∧ y ≥ 2025 then ulteriore rr else 0
  let ceil := if y ≥ 2025 then oneriCeiling rr p.kidsDependent else -1
  let elig := min (pos p.charity) charityCap
  let elig := if ceil < 0 then elig else min elig ceil
  let dc := divR .halfUp (elig * charityRate) BP
  let netta := pos (l - (d13 + d12 + ul + dc))
  let ti := trattIntegrativo rr rld l d12 y
  let cs := if y ≥ 2025 then cuneoSomma rr rld else 0
  { rld, redditoComplessivo := rc, redditoRif := rr, oneriDeducibili := ded, imponibile := imp, lorda := l, d13,
    d12, ulteriore := ul, dCharity := dc, netta, ti, cuneo := cs }

end ITTax
