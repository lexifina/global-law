import RoTax.Params
import RoTax.DeductionTable
import RoTax.Deduction2022

/-!
# Wages: the monthly, final tax of art. 78 (law in force month by month)

art. 78 alin. (1): "un impozit lunar, final, care se calculează și se reține la sursă"; alin. (2) lit. a): 10 % of the
base "determinată ca diferență între venitul net din salarii calculat prin deducerea din venitul brut a contribuțiilor
sociale obligatorii aferente unei luni ... și ... (i) deducerea personală acordată pentru luna respectivă".
Each month has its own law (`MonthLaw`): the minimum wage in force (art. 77 alin. (3)) and the non-taxable sum of
OUG nr. 156/2024 art. LXVI. In 2025 all twelve months have the same law (4.050 lei, 300 lei up to 4.300 lei); the
structure carries the 2026 values for the tests against published 2026 figures.
-/

namespace RoTax
open TaxKernel

structure MonthLaw where
  mw : Int
  untaxed : Int
  untaxedCeiling : Int
  /-- art. 77 before OG nr. 16/2022 (2022): fixed-lei deduction table, no young or school deduction -/
  pre2023 : Bool := false
  deriving Repr

/-- 2025, every month (HG nr. 1.506/2024; OUG nr. 156/2024 art. LXVI alin. (6) "ianuarie-decembrie 2025"). -/
def law2025 (_month : Nat) : MonthLaw :=
  { mw := minWage2025, untaxed := untaxed2025, untaxedCeiling := untaxedCeiling2025 }

/-- July 2026 (tests only): minimum wage 4.325 lei (HG nr. 146/2026) and 200 lei (OUG nr. 89/2025) as reported in the
published worked example (Newsweek România 6 Aug 2026, figures by ImpozitSalariu.ro). The 2026 gross ceiling was not
verified against the statute; the tests only use the base-salary condition. -/
def lawJul2026 : MonthLaw := { mw := 4325, untaxed := 200, untaxedCeiling := 4600 }

/-- art. 77 alin. (4): percentage of the minimum wage (bp) for gross `g` and `n` dependants (0 above the band). -/
def basePct (L : MonthLaw) (g : Int) (n : Nat) : Int :=
  if g ≤ L.mw then firstRow.getD (min n 4) 0
  else Table.lookup (stepTable n) (g - L.mw) 0

structure WageIn where
  /-- gross monthly wage at the main job (art. 76 alin. (1)-(3)) -/
  gross : Int
  /-- contractual base salary without bonuses ("salariul de bază brut lunar ... fără a include sporuri") -/
  baseWage : Int
  /-- dependants (art. 77 alin. (5)-(7)) -/
  deps : Nat
  /-- under 26 (art. 77 alin. (10) lit. a)) -/
  young : Bool
  /-- children in education claimed by this parent (art. 77 alin. (10) lit. b), alin. (12)) -/
  schoolKids : Nat
  deriving Repr

structure WageOut where
  untaxed : Int
  cas : Int
  cass : Int
  dedBase : Int
  dedYoung : Int
  dedSchool : Int
  ded : Int
  base : Int
  tax : Int
  deriving Repr, Inhabited

/-- OUG nr. 156/2024 art. LXVI alin. (1) lit. a)-b): base salary equal to the minimum wage and gross at most 4.300 lei. -/
def untaxedSum (L : MonthLaw) (w : WageIn) : Int :=
  if 0 < w.gross ∧ w.baseWage = L.mw ∧ w.gross ≤ L.untaxedCeiling then min L.untaxed w.gross else 0

/-- One month of wages at the main job. -/
def wageMonth (L : MonthLaw) (w : WageIn) : WageOut :=
  let s := untaxedSum L w
  let b := pos (w.gross - s)
  let cas := pctOf casRate b                 -- art. 138 lit. a), art. 146 alin. (5)
  let cass := pctOf cassRate b               -- art. 156, art. 168 alin. (5)
  let net := b - cas - cass
  let inBand := decide (w.gross ≤ L.mw + dedBand)   -- art. 77 alin. (3)
  let dB := if inBand then pctOf (basePct L w.gross w.deps) L.mw else 0
  let dY := if inBand && w.young then pctOf youngPct L.mw else 0
  let dS := schoolChildDed * w.schoolKids
  let ded := min (pos net) (dB + dY + dS)    -- art. 77 alin. (2): "în limita venitului impozabil lunar"
  let base := pos (net - ded)
  { untaxed := s, cas, cass, dedBase := dB, dedYoung := dY, dedSchool := dS, ded, base,
    tax := pctOf taxRate base }

/-- One month of wages under the 2022 law (art. 77 alin. (2) in the OUG nr. 79/2017 wording; no non-taxable sum). -/
def wageMonth2022 (L : MonthLaw) (w : WageIn) : WageOut :=
  let b := pos w.gross
  let cas := pctOf casRate b
  let cass := pctOf cassRate b
  let net := b - cas - cass
  let dB := deduction2022 w.gross w.deps
  let ded := min (pos net) dB
  let base := pos (net - ded)
  let _ := L
  { untaxed := 0, cas, cass, dedBase := dB, dedYoung := 0, dedSchool := 0, ded, base, tax := pctOf taxRate base }

/-- The month's computation under its law. -/
def wageMonthAny (L : MonthLaw) (w : WageIn) : WageOut :=
  if L.pre2023 then wageMonth2022 L w else wageMonth L w

/-- The law of month `m` (1..12) of year `y` (`Params`: HG on the minimum wage, OUG nr. 168/2022 art. XXXVII, OUG
nr. 115/2023 art. LXXIII, OUG nr. 59/2024 art. II); 2025 and later: `law2025`. -/
def lawFor (y m : Nat) : MonthLaw :=
  if y ≤ 2022 then { mw := 2550, untaxed := 0, untaxedCeiling := 0, pre2023 := true }
  else if y = 2023 then { mw := if m ≤ 9 then 3000 else 3300, untaxed := 200, untaxedCeiling := 4000 }
  else if y = 2024 then
    (if m ≤ 6 then { mw := 3300, untaxed := 200, untaxedCeiling := 4000 }
     else { mw := 3700, untaxed := 300, untaxedCeiling := 4000 })
  else law2025 m

/-- Take-home pay of one month. -/
def wageNet (L : MonthLaw) (w : WageIn) : Int :=
  let o := wageMonth L w
  w.gross - o.cas - o.cass - o.tax

/-- An annual amount spread over 12 months, the first `annual % 12` months one leu more (as `TaxKernel.perPeriod`). -/
def months (annual : Int) : List Int :=
  let q := annual / 12
  let r := (annual % 12).toNat
  (List.range 12).map fun i => q + if i < r then 1 else 0

structure WageYear where
  untaxed : Int := 0
  cas : Int := 0
  cass : Int := 0
  ded : Int := 0
  base : Int := 0
  tax : Int := 0
  deriving Repr, Inhabited

/-- A year of wages: each month under that month's law (`lawOf` month 1..12). `baseOf` gives the contractual base
salary for a month's gross (default: the gross itself, no bonuses). -/
def wageYear (lawOf : Nat → MonthLaw) (annual : Int) (baseOf : Int → Int) (deps : Nat) (young : Bool)
    (school : Nat) : WageYear :=
  if annual ≤ 0 then {} else
  ((months annual).zip (List.range 12)).foldl (fun acc (g, i) =>
    let o := wageMonthAny (lawOf (i + 1)) { gross := g, baseWage := baseOf g, deps, young, schoolKids := school }
    { untaxed := acc.untaxed + o.untaxed, cas := acc.cas + o.cas, cass := acc.cass + o.cass,
      ded := acc.ded + o.ded, base := acc.base + o.base, tax := acc.tax + o.tax }) {}

/-! ## Pensions, month by month (art. 100, 101; art. 157^6 from August 2025) -/

/-- One month of a pension `p` in month `m` (1..12) of 2025: (CASS, tax). -/
def pensionMonth (m : Nat) (p : Int) (first : Nat := pensionCassFirstMonth) : Int × Int :=
  let over := pos (p - pensionAllow)
  let cass := if first ≤ m then pctOf cassRate over else 0
  (cass, pctOf taxRate (pos (over - cass)))

def pensionYear (annual : Int) (first : Nat := pensionCassFirstMonth) : Int × Int :=
  if annual ≤ 0 then (0, 0) else
  ((months annual).zip (List.range 12)).foldl (fun (c, t) (p, i) =>
    let (c', t') := pensionMonth (i + 1) p first
    (c + c', t + t')) (0, 0)

end RoTax
