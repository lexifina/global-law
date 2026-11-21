import ITTax.Params

/-!
# INPS employee contributions and the assegno unico universale (AUU)

**INPS** (ordinary employee): 9,49 % of pay up to the massimale, plus 1 % on the part above the first pensionable
band (`Params`). Simplifications: the band is applied to the annual total (INPS applies it month by month, 1/12 of
the band, with a year-end equalisation, so the annual result is the same for steady pay); the massimale applies to
workers first insured after 1995 only.

**AUU** (D.Lgs. 230/2021 art. 4): a monthly amount per child set by the family's ISEE. ISEE = ISR / scala
(DPCM 159/2013 art. 2, art. 4, Allegato 1). The contract household has no assets, so the patrimonial part (ISP) is
0, and the ISEE is computed from the 2025 incomes (the real ISEE of 2025 uses the incomes of 2023: art. 4 c. 1
DPCM 159/2013 "secondo anno precedente"). Both choices are the OECD's convention; see FINDINGS.
Tabella 1 lowers each amount linearly between ISEE 15.000 and 40.000 (2022 terms); all amounts and thresholds are
revalued by F (art. 4 c. 11), so the 2025 amount at ISEE `i` is F × amount₂₀₂₂(i / F).
-/

namespace ITTax
open TaxKernel

def inpsContribution : Contribution :=
  { name := "INPS", sched := Schedule.ofList [(0, inpsRate), (inpsBand, inpsRate + inpsExtra)], ceiling := inpsMax,
    round := Rule.unitHalfUp }

def inps (wages : Int) : Int := if wages ≤ 0 then 0 else inpsContribution.amount wages

/-- INPS by year (`Params.inpsBandY`, `Params.esoneroBp13`): the contribution with that year's band and massimale,
less the IVS exemption for pay of at most 13 × 2.692 (13 × 1.923 for the extra point) a year in 13 equal
instalments, the exemption = pay × (points summed over the 13 periods) / 13, to the cent. -/
def inpsY (y : Nat) (oecd : Bool) (wages : Int) (em : Bool := false) : Int :=
  if wages ≤ 0 then 0
  else if y ≥ 2025 then inps wages
  else
    let c : Contribution := { name := "INPS", sched := Schedule.ofList [(0, inpsRate), (inpsBandY y, inpsRate + inpsExtra)],
                              ceiling := inpsMaxY y, round := Rule.unitHalfUp }
    let gross := c.amount wages
    let ex := if wages ≤ 13 * cuneoCap2692 then
        divR .halfUp (wages * esoneroBp13 y (decide (wages ≤ 13 * cuneoCap1923)) oecd em) (13 * BP) else 0
    gross - ex

/-- A 2022-terms amount pair `(full, floor)` at a 2022-terms ISEE `i` scaled by `s` (the ISEE is `i/s`), as an
exact numerator over `(auuHi - auuLo) * s`. -/
def auuNum (p : Int × Int) (iNum s : Int) : Int :=
  -- amount = full - (full - floor) * clamp((i - lo)/(hi - lo)), with i = iNum / s
  let w := (auuHi - auuLo) * s
  let t := max 0 (min w (iNum - auuLo * s))
  p.1 * w - (p.1 - p.2) * t

/-- One family's AUU for the year, cents. `isee` in cents. Children: `ages`; `bothWork`: art. 4 c. 8. -/
def auuYear (ages : List Nat) (isee : Int) (bothWork : Bool) (y : Nat := 2025) (oecd : Bool := false) : Int :=
  -- 2022-terms ISEE i = isee / F = isee * Fden / Fnum, kept as the fraction iNum / s with s = Fnum
  let fnum := auuFnumY y
  let iNum := isee * auuFden
  let s := fnum
  let w := (auuHi - auuLo) * s
  let minors := ages.filter (· < 18)
  let adults := ages.filter (fun a => 18 ≤ a ∧ a < 21)
  let n := minors.length + adults.length
  let perChild (a : Nat) (idx : Nat) : Int :=
    let base := if a < 18 then auuNum auuMinor iNum s else auuNum auuAdult iNum s
    -- c. 1: +50 % under one year; and for children aged 1-3 in families with three or more children (ISEE <= 40.000)
    let young := if y < auuYoungFrom then 0 else if a < 1 then base / 2
                 else if a < 3 ∧ n ≥ 3 ∧ iNum ≤ auuHi * s then base / 2 else 0
    let third := if idx ≥ 2 then auuNum auuThird iNum s else 0
    let bw := if bothWork ∧ a < 18 then auuNum auuBothWork iNum s else 0
    base + young + third + bw
  let eligible := (ages.filter (· < 21))
  let total := (eligible.zipIdx.map fun (a, i) => perChild a i).foldl (· + ·) 0
  -- total is (cents a month in 2022 terms) × w; times 12 months and F, rounded once to the cent
  divR .halfUp (total * auuMonthsY y oecd * fnum) (w * auuFden)

/-- ISEE (cents) from the household's incomes: `incomes` per adult is (reddito for ISEE, employment income,
pension income); children have no income. -/
def isee (adults : List (Int × Int × Int)) (nChildren : Nat) (magB : Int) : Int :=
  let red := adults.foldl (fun acc (r, dip, pen) =>
      let fr := if dip > 0 then min iseeDipCap (dip / 5) else if pen > 0 then min iseePenCap (pen / 5) else 0
      acc + pos (r - fr)) 0
  let members := adults.length + nChildren
  -- Allegato 1 a): "0,2 in caso di nuclei familiari con tre figli, 0,35 ... quattro figli, 0,5 ... almeno cinque"
  let magA : Int := if nChildren = 3 then 20 else if nChildren = 4 then 35 else if nChildren ≥ 5 then 50 else 0
  let scala := scalaBase members + magA + magB
  divR .halfUp (red * 100) scala

end ITTax
