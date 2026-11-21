import LuTax.Years

/-!
# Luxembourg personal income tax 2025 (residents), on the shared kernel

Order of the computation (L.I.R.): revenus nets by category (art. 10, 104-107) → total des revenus nets → dépenses
spéciales (art. 109-113) and abattements (art. 126-129b) → revenu imposable ajusté (RIA, art. 126 (1)) → rounded down to
50 euros (art. 126 (2)) → tarif by tax class (art. 118-121) → cote rounded down to the euro, nil under 12 euros
(art. 124) → majoration for the fonds pour l'emploi (loi du 30 juin 1976, art. 6) → crédits d'impôt, refundable
(art. 139quater, 152ter, 154ter, 154quater, 154quinquies). Employee social contributions at statutory rates (CSS);
allocations familiales and allocation de rentrée scolaire (CSS art. 272, 275) as `benefits`.

Options (`computeWith`): `--oecd` (OECD Taxing Wages conventions: cotes and majoration not rounded, no allocation de
rentrée scolaire), `--individual` (married couple opts for individual taxation, art. 3ter (2)).
-/

namespace LuTax
open TaxKernel Lean

/-! ## Tarif and tax classes -/

/-- Art. 118: the tarif as a kernel schedule (euros, bp). -/
def tarif : Schedule := Schedule.ofList tarifBands

/-- Art. 120bis written as its own schedule in the RIA `x` (derived, not in the statute's words): below 51 804 the
tarif applied to `x − (79 380 − x)/4 = (5x − 79 380)/4` charges 1,25 × the tarif's rates from `x = 0,8 t + 15 876`
for each tarif threshold `t`; from 51 804 the capped rates 39/40/41/42 % apply at the tarif's own thresholds. The
derivation is checked against the statute's formula in `Theorems.lean` (`c1a_eq_formula_*`) and against the ACD's
official formulas in `harness/acd_formulas.py`. -/
def c1aBands : List (Int × Int) :=
  [(0, 0), (26460, 1000), (28224, 1125), (29988, 1250), (31752, 1375), (33516, 1500), (35280, 1750),
   (37116, 2000), (38952, 2250), (40788, 2500), (42624, 2750), (44460, 3000), (46296, 3250), (48132, 3500),
   (49968, 3750), (51804, 3900), (117450, 4000), (176160, 4100), (234870, 4200)]
def tarif1a : Schedule := Schedule.ofList c1aBands

/-- The statute's own class-1a formula below the cap, in quarter-euro ticks: the tarif (thresholds × 4) applied to
`4 × (x − (79 380 − x)/4) = 5x − 79 380`. -/
def tarif4 : Schedule := tarif.mapLo (fun t => 4 * t)
def c1aFormulaQ (x : Int) : Int := tarif4.ticks (5 * x - c1aComplement)

inductive TaxClass | c1 | c1a | c2
  deriving Repr, DecidableEq, Inhabited

def TaxClass.name : TaxClass → String
  | .c1 => "1" | .c1a => "1a" | .c2 => "2"

/-- Exact tax in ticks (euros × bp) of the class on the rounded RIA `x` (art. 120, 120bis, 121). Class 2: "le double de
la cote qui, par application du tarif prévu à l'article 118, correspond à la moitié du revenu imposable ajusté"
(the kernel's `splitting`; `x` is a multiple of 50, so `x/2` is whole). -/
def classTicks : TaxClass → Int → Int
  | .c1, x => tarif.ticks x
  | .c1a, x => tarif1a.ticks x
  | .c2, x => splitting tarif.ticks x 0

/-- Art. 124 (1) "arrondies au multiple inférieur d'un euro", (2) "inférieures à 12 euros ... nulles": the cote in
euros. -/
def cote (k : TaxClass) (x : Int) : Int :=
  let t := Rule.unitDown.ofTicks (classTicks k x)
  if t < minCote then 0 else t

/-- Art. 126 (2): RIA in cents → euros, rounded down to a multiple of 50. -/
def roundRIA (riaC : Int) : Int := toMultiple .down incomeStep (pos riaC / 100)

/-! ## Fonds pour l'emploi (loi du 30 juin 1976, art. 6) -/

/-- The cote at the threshold of 150 000 (classes 1, 1a) or 300 000 (class 2): the "tranche ... dépassant" is charged
109 %, i.e. 2 % more on the tax that accrues above the threshold (the ACD's formula `I × 0,09 − 931,8 / 885,36 /
1 863,6` is exactly 7 % of `I` plus 2 % of `I − cote(threshold)`). -/
def feThresholdOf : TaxClass → Int
  | .c2 => feThreshold2 | _ => feThreshold12
def coteAtThreshold (k : TaxClass) : Int := cote k (feThresholdOf k)
def feBase : Surcharge := Surcharge.flatPct feRate
def feHigh (k : TaxClass) : Surcharge := Surcharge.above (feRateHigh - feRate) (coteAtThreshold k)
/-- Majoration in ticks (euros × bp) on a cote `i` of class `k`. -/
def feTicks (k : TaxClass) (i : Int) : Int := feBase.ticks i + (feHigh k).ticks i
/-- Cote + majoration in euros, "à arrondir à l'euro inférieur" (ACD, barème 2025 notes; RGD 20.12.2024). -/
def taxWithFE (k : TaxClass) (x : Int) : Int :=
  let i := cote k x
  i + Rule.unitDown.ofTicks (feTicks k i)
/-- OECD convention: no rounding of the cote or of the majoration (cents). -/
def taxWithFE_oecdC (k : TaxClass) (x : Int) : Int :=
  let tq := classTicks k x
  let i := tq / 100    -- cents
  let thr := classTicks k (feThresholdOf k) / 100
  i + (feRate * i + (feRateHigh - feRate) * pos (i - thr)) / BP

/-! ## Crédits d'impôt (cents, "arrondis au cent (0,01 euro) supérieur") -/

/-- CIS / CIP / CII on gross `g` euros (art. 154quater (2), 154quinquies (2), 152ter (2)). -/
def cisC (g : Int) : Int :=
  if g < cisLow then 0
  else if g ≤ cisKink then ceilDiv ((cisBase * 1000 + (g - cisLow) * cisInRateM) * 100) 1000
  else if g ≤ cisStart then cisFull * 100
  else if g < cisEnd then ceilDiv (cisFull * 1000000 - (g - cisStart) * cisOutRateM10 * 100) 10000
  else 0
/-- CIP: as the CIS, and 300 euros "de 300 à 935 euros" (art. 154quinquies (2)). -/
def cipC (g : Int) : Int := if 300 ≤ g ∧ g < cisLow then cisBase * 100 else cisC g
/-- CI-CO2 (salarié, pensionné, indépendant). -/
def co2C (g : Int) (lowFrom : Int := cisLow) : Int :=
  if g < lowFrom then 0
  else if g ≤ cisStart then co2Full * 100
  else if g < cisEnd then ceilDiv (co2Full * 1000000 - (g - cisStart) * co2OutRateM10 * 100) 10000
  else 0
/-- CIM on the (unrounded) RIA in cents (art. 154ter (2)); the statute states no rounding: rounded up to the cent like
the other credits (convention). -/
def cimC (riaC : Int) : Int :=
  if riaC < cimStart * 100 then cimFull * 100
  else if riaC ≤ cimEnd * 100 then ceilDiv (cimFull * 1000000 - (riaC - cimStart * 100) * cimRateM10) 10000
  else cimFloor * 100
/-- CISSM per month on a monthly wage `m` in cents (art. 139quater (3)), rounded up to the cent; ×12 for the year
(full-time wage paid evenly over 12 months assumed). -/
def cissmMonthC (mC : Int) : Int :=
  if mC < cissmLow * 100 then 0
  else if mC ≤ cissmKink * 100 then cissmFull * 100
  else if mC < cissmEnd * 100 then ceilDiv (cissmFull * (cissmEnd * 100 - mC)) 600
  else 0
def cissmC (w : Int) : Int := 12 * cissmMonthC (w * 100 / 12)

/-! ## Social contributions (cents), wage `w` euros paid evenly over 12 months -/

/-- Monthly base capped at the maximum cotisable, summed over 2025 (CSS art. 39, 241 (3)); in cents. -/
def cappedBaseC (w : Int) : Int :=
  let m := w * 100 / 12
  months1 * min m maxCot1C + months2 * min m maxCot2C
/-- Dependence base: monthly income less "un abattement correspondant à un quart du salaire social minimum"
(CSS art. 377 (4)), no ceiling (art. 377 (3)); in cents ×4 to keep the quarter exact. -/
def depBase4C (w : Int) : Int :=
  let m4 := w * 400 / 12
  months1 * pos (m4 - ssm1C) + months2 * pos (m4 - ssm2C)
def rateC (rate baseC : Int) : Int := (rate * baseC + BP / 2) / BP
/-- Employee: pension 8 %, soins 2,80 %, espèces 0,25 % (deductible, art. 110 1.), dépendance 1,4 % (not deductible). -/
def wageSocialDedC (w : Int) : Int := rateC (pensionRate + healthRate + cashRate) (cappedBaseC w)
def depC (w : Int) : Int := (depRate * depBase4C w + 2 * BP) / (4 * BP)
/-- Pensioner: soins 2,80 % (deductible) + dépendance 1,4 % (simplified: same abattement). -/
def pensionSocialDedC (p : Int) : Int := rateC healthRate (cappedBaseC p)
/-- Self-employed (simplified: base = the year's profit, no minimum base): pension 16 %, health 6,10 % (deductible,
art. 110 2.), dépendance 1,4 %. -/
def seSocialDedC (s : Int) : Int := rateC (sePensionRate + seHealthRate) (cappedBaseC s)

/-! ## Allocations familiales (cents), CSS art. 272 and 275 -/

def afMonthC (age : Nat) (idx : Int) : Int :=
  let r (a : Int) := (a * idx + 5000) / 10000   -- amount at index 100 (cents) × index/100, rounded to the cent
  r afBaseC100 + (if age ≥ 12 then r afSupp12C100 else if age ≥ 6 then r afSupp6C100 else 0)
def afYearC (age : Nat) : Int :=
  if age < 18 then months1 * afMonthC age index1 + months2 * afMonthC age index2 else 0
def rentreeC (age : Nat) : Int :=
  if age ≥ 18 then 0 else if age ≥ 12 then rentree12 * 100 else if age ≥ 6 then rentree6 * 100 else 0

/-! ## Tax years 2022-2024 (`Years.lean`): the same computation with the year's parameters

For a year with `yearP? y = none` (2025) every `...Y` function below is the 2025 function above, by definition. -/

def YearP.tarif (p : YearP) : Schedule := Schedule.ofList p.tarifBands

/-- Art. 120bis (2017-2024 wording): the tarif applied to `x − (C − x)/2 = (3x − C)/2` up to the cap point, computed
exactly as half the ticks of the tarif with doubled thresholds at `3x − C`; above the cap point the capped rates
39/40/41/42 % (`c1aCapBands`). -/
def YearP.c1aTicks (p : YearP) (x : Int) : Int :=
  let t2 := p.tarif.mapLo (fun t => 2 * t)
  let below (z : Int) : Int := t2.ticks (pos (3 * z - p.c1aC)) / 2
  let cap := Schedule.ofList p.c1aCapBands
  if x ≤ p.c1aCap then below x else below p.c1aCap + cap.ticks x - cap.ticks p.c1aCap

def classTicksY (y : Nat) (k : TaxClass) (x : Int) : Int :=
  match yearP? y with
  | none => classTicks k x
  | some p =>
    match k with
    | .c1 => p.tarif.ticks x
    | .c1a => p.c1aTicks x
    | .c2 => splitting p.tarif.ticks x 0

def coteY (y : Nat) (k : TaxClass) (x : Int) : Int :=
  let t := Rule.unitDown.ofTicks (classTicksY y k x)
  if t < minCote then 0 else t
def feTicksY (y : Nat) (k : TaxClass) (i : Int) : Int :=
  feBase.ticks i + (Surcharge.above (feRateHigh - feRate) (coteY y k (feThresholdOf k))).ticks i
def taxWithFEY (y : Nat) (k : TaxClass) (x : Int) : Int :=
  let i := coteY y k x
  i + Rule.unitDown.ofTicks (feTicksY y k i)
def taxWithFE_oecdCY (y : Nat) (k : TaxClass) (x : Int) : Int :=
  let tq := classTicksY y k x
  let i := tq / 100
  let thr := classTicksY y k (feThresholdOf k) / 100
  i + (feRate * i + (feRateHigh - feRate) * pos (i - thr)) / BP

theorem classTicksY_2025 (k : TaxClass) (x : Int) : classTicksY 2025 k x = classTicks k x := by
  simp [classTicksY, yearP?]

/-- CIS / CIP / CII of the year (art. 154quater, 154quinquies, 152ter), cents, rounded up to the cent. -/
def cisCY (p : YearP) (g : Int) : Int :=
  if g < cisLow then 0
  else if g ≤ cisKink then ceilDiv ((p.cisBase * 1000 + (g - cisLow) * cisInRateM) * 100) 1000
  else if g ≤ cisStart then p.cisFull * 100
  else if g < cisEnd then ceilDiv (p.cisFull * 1000000 - (g - cisStart) * p.cisOutM10 * 100) 10000
  else 0
def cipCY (p : YearP) (g : Int) : Int := if 300 ≤ g ∧ g < cisLow then p.cisBase * 100 else cisCY p g
def co2CY (p : YearP) (g : Int) (lowFrom : Int := cisLow) : Int :=
  if p.co2Full = 0 ∨ g < lowFrom then 0
  else if g ≤ cisStart then p.co2Full * 100
  else if g < cisEnd then ceilDiv (p.co2Full * 1000000 - (g - cisStart) * p.co2OutM10 * 100) 10000
  else 0
/-- CIM of the year (art. 154ter (2)); rounded up to the cent as for 2025. -/
def cimCY (p : YearP) (riaC : Int) : Int :=
  if riaC < p.cimStart * 100 then p.cimFull * 100
  else if riaC ≤ p.cimEnd * 100 then ceilDiv (p.cimFull * 100 * p.cimDen - (riaC - p.cimStart * 100) * p.cimNum) p.cimDen
  else p.cimFloor * 100
def cissmMonthCY (p : YearP) (mC : Int) : Int :=
  if mC < p.cissmLow * 100 then 0
  else if mC ≤ p.cissmKink * 100 then p.cissmFull * 100
  else if mC < p.cissmEnd * 100 then ceilDiv (p.cissmFull * (p.cissmEnd * 100 - mC)) (p.cissmEnd - p.cissmKink)
  else 0
def cissmCY (p : YearP) (w : Int) : Int := 12 * cissmMonthCY p (w * 100 / 12)
/-- CIE salarié / pensionné per month (art. 154septies (2), 154octies (2), loi du 29.6.2022): "de 78 euros à 3.667
euros, ... 84 euros par mois, de 3.667 euros à 5.667 euros, ... [84 - (salaire brut mensuel - 3.667) x (8/2.000)] ...,
de 5.667 euros à 8.334 euros, ... [76 - (salaire brut mensuel - 5.667) x (76/2.667)]", rounded up to the cent. -/
def cieMonthC (mC : Int) : Int :=
  if mC < 7800 then 0
  else if mC ≤ 366700 then 8400
  else if mC ≤ 566700 then ceilDiv (8400 * 2000 - (mC - 366700) * 8) 2000
  else if mC < 833400 then ceilDiv (7600 * 2667 - (mC - 566700) * 76) 2667
  else 0
def cieC (p : YearP) (w : Int) : Int := (p.cieMonths.length : Int) * cieMonthC (w * 100 / 12)
/-- CIE indépendant (art. 154sexies (2)): N x 84 up to 44 000, [N x 84 - (b - 44 000) x N x 8 / 24 000] to 68 000,
[N x 76 - (b - 68 000) x N x 76 / 32 000] to 100 000 (N = months; 2023: N = 3, "252 euros par an"). -/
def cieIndepC (p : YearP) (s : Int) : Int :=
  let n := (p.cieMonths.length : Int)
  if n = 0 ∨ s < 936 then 0
  else if s ≤ 44000 then n * 8400
  else if s ≤ 68000 then ceilDiv (n * 8400 * 24000 - (s - 44000) * n * 800) 24000
  else if s ≤ 100000 then ceilDiv (n * 7600 * 32000 - (s - 68000) * n * 7600) 32000
  else 0

/-- CIC salarié / pensionné per month (art. 154decies (2), 154undecies (2), 2023 only): "de 1.125 euros à 1.250 euros,
... [(salaire brut mensuel – 1.125) x (4/125)]; de 1.250 euros à 2.100 euros, ... [(... – 1.250) x (3/850) + 4]; de
2.100 euros à 4.600 euros, ... [(... – 2.100) x (37/2.500) + 7]; de 4.600 euros à 9.500 euros, ... 44 euros; de 9.500
euros à 9.925 euros, ... [(... – 9.500) x (4/425) + 44]; de 9.925 euros à 14.175 euros, ... 48 euros; de 14.175 euros à
14.916 euros, ... [(... – 14.175) x (3/356) + 48]; supérieur à 14.916 euros, ... 54,25 euros par mois", "arrondi au cent
(0,01 euro) supérieur"; nothing below 1.125 euros. -/
def cicMonthC (mC : Int) : Int :=
  if mC < 112500 then 0
  else if mC ≤ 125000 then ceilDiv ((mC - 112500) * 4) 125
  else if mC ≤ 210000 then ceilDiv ((mC - 125000) * 3) 850 + 400
  else if mC ≤ 460000 then ceilDiv ((mC - 210000) * 37) 2500 + 700
  else if mC ≤ 950000 then 4400
  else if mC ≤ 992500 then ceilDiv ((mC - 950000) * 4) 425 + 4400
  else if mC ≤ 1417500 then 4800
  else if mC ≤ 1491600 then ceilDiv ((mC - 1417500) * 3) 356 + 4800
  else 5425
def cicC (p : YearP) (w : Int) : Int := if p.cic then 12 * cicMonthC (w * 100 / 12) else 0
/-- CIC indépendant (art. 154nonies (2)), annual on the net profit `s` euros: the same table x 12 ("de 13.500 euros à
15.000 euros ... [(bénéfice net – 13.500) x 4/125] ... à partir de 179.000 euros, ... 651 euros par an"). -/
def cicIndepC (p : YearP) (s : Int) : Int :=
  if !p.cic || s < 13500 then 0
  else if s ≤ 15000 then ceilDiv ((s - 13500) * 400) 125
  else if s ≤ 25200 then ceilDiv ((s - 15000) * 300) 850 + 4800
  else if s ≤ 55200 then ceilDiv ((s - 25200) * 3700) 2500 + 8400
  else if s ≤ 114000 then 52800
  else if s ≤ 119100 then ceilDiv ((s - 114000) * 400) 425 + 52800
  else if s ≤ 170100 then 57600
  else if s < 179000 then ceilDiv ((s - 170100) * 300) 356 + 57600
  else 65100

/-- Contributions of the year: monthly base capped at the month's maximum (CCSS table); dependence on the monthly
income less a quarter of the month's SSM. Rates unchanged 2014-2025 (CCSS table: soins 5,60, espèces 0,50,
dépendance 1,40, pension 16). -/
def cappedBaseCY (y : Nat) (w : Int) : Int :=
  match yearP? y with
  | none => cappedBaseC w
  | some p => let m := w * 100 / 12; sumInts (p.maxCotC.map fun mx => min m mx)
def depCY (y : Nat) (w : Int) : Int :=
  match yearP? y with
  | none => depC w
  | some p => let m4 := w * 400 / 12; (depRate * sumInts (p.ssmC.map fun s => pos (m4 - s)) + 2 * BP) / (4 * BP)
def afYearCY (y : Nat) (age : Nat) : Int :=
  match yearP? y with
  | none => afYearC age
  | some p => if age < 18 then sumInts (p.afIdx.map (afMonthC age)) else 0

theorem cappedBaseCY_2025 (w : Int) : cappedBaseCY 2025 w = cappedBaseC w := by simp [cappedBaseCY, yearP?]
theorem depCY_2025 (w : Int) : depCY 2025 w = depC w := by simp [depCY, yearP?]
theorem afYearCY_2025 (a : Nat) : afYearCY 2025 a = afYearC a := by simp [afYearCY, yearP?]

/-! ### Transitional amounts of the 2016 reform (round 9)

L. 23.7.2016, art. VI (modifiée par L. 17.12.21, 27), printed under CSS art. 272 in the consolidation of 1.1.2025
(`germanic/lu/law/css_20250101.txt`, note 2 to art. 272): "Pour un enfant qui ouvre déjà droit à l'allocation familiale
avant l'entrée en vigueur de la présente loi, le montant de l'allocation familiale tel que prévu à l'article 272 ... se
modifie comme suit : Enfant faisant partie, avant l'entrée en vigueur de la loi, d'un groupe familial de ... 2 enfants
35,61; 3 enfants 41,26; ... 25 enfants 51,20"; "Les montants prévus au deuxième alinéa correspondent au nombre cent de
l'indice ... et ils sont adaptés ... conformément aux dispositions applicables aux traitements des fonctionnaires"
(L.17.12.21, 48, 5°: effective 1.10.2021); the EMAF derogation of 1.4.2022-1.4.2023 also covers them (loi du 29.6.2022,
art. 6, Mémorial A 317, `improve-central/refs/lu/loi_2022-06-29_a317.txt`). Read here as replacing the art. 272 al. 1
base amount; the al. 2 age majorations still apply. Whether a child was entitled before 1.8.2016, and the size of its
family group then, are facts the canonical household does not carry: inputs `luEntitled2016` (per child, default
false) and `luGroup2016` (household; default the number of children flagged). -/
def afTransC100 : List Int :=
  [3561, 4126, 4409, 4578, 4691, 4772, 4832, 4879, 4917, 4948, 4973, 4995, 5014, 5030, 5044, 5056, 5067, 5077, 5086,
   5094, 5101, 5108, 5114, 5120]

/-- The base amount (index 100, cents) for a child: the transitional amount of its 2016 family group (2-25+), else
art. 272 al. 1. -/
def afBaseFor (entitled2016 : Bool) (group : Nat) : Int :=
  if entitled2016 && group ≥ 2 then afTransC100.getD (min group 25 - 2) 5120 else afBaseC100

def afMonthCB (base : Int) (age : Nat) (idx : Int) : Int :=
  let r (a : Int) := (a * idx + 5000) / 10000
  r base + (if age ≥ 12 then r afSupp12C100 else if age ≥ 6 then r afSupp6C100 else 0)

theorem afMonthCB_base (age : Nat) (idx : Int) : afMonthCB afBaseC100 age idx = afMonthC age idx := by
  simp [afMonthCB, afMonthC]

/-- The year's allocation familiale (cents) with a given base amount; equals `afYearCY` for the art. 272 base. -/
def afYearCYB (base : Int) (y : Nat) (age : Nat) : Int :=
  if base = afBaseC100 then afYearCY y age else
  if age ≥ 18 then 0 else
  match yearP? y with
  | none => months1 * afMonthCB base age index1 + months2 * afMonthCB base age index2
  | some p => sumInts (p.afIdx.map (afMonthCB base age))

theorem afYearCYB_default (y age : Nat) : afYearCYB afBaseC100 y age = afYearCY y age := by
  simp [afYearCYB]

theorem afTrans_table : afBaseFor true 2 = 3561 ∧ afBaseFor true 3 = 4126 ∧ afBaseFor true 25 = 5120 ∧
    afBaseFor true 30 = 5120 ∧ afBaseFor true 1 = afBaseC100 ∧ afBaseFor false 2 = afBaseC100 := by decide

/-! ## One taxpayer (or a collectively taxed couple) -/

structure Person where
  wages : Int := 0
  se : Int := 0
  pension : Int := 0
  age : Nat := 40
  deriving Repr, Inhabited

def Person.ofAdult (a : Adult) : Person := { wages := a.wages, se := a.selfEmployment, pension := a.pension, age := a.age }

/-- Revenus nets of one person (cents), art. 104-107 (forfaits limited to the receipts, art. 107 (5)). -/
def Person.netC (p : Person) : Int :=
  (p.wages * 100 - min (foWage * 100) (pos p.wages * 100)) + (p.pension * 100 - min (foPension * 100) (pos p.pension * 100))
    + p.se * 100
/-- Deductible compulsory contributions (art. 110 1., 2.). -/
def Person.socialDedC (p : Person) : Int := wageSocialDedC p.wages + pensionSocialDedC p.pension + seSocialDedC p.se
/-- All employee contributions incl. dépendance (output `employeeSocial`). -/
def Person.socialC (p : Person) : Int := p.socialDedC + depC (p.wages + p.pension + p.se)
def Person.socialDedCY (y : Nat) (p : Person) : Int :=
  rateC (pensionRate + healthRate + cashRate) (cappedBaseCY y p.wages) + rateC healthRate (cappedBaseCY y p.pension)
    + rateC (sePensionRate + seHealthRate) (cappedBaseCY y p.se)
def Person.socialCY (y : Nat) (p : Person) : Int := p.socialDedCY y + depCY y (p.wages + p.pension + p.se)

/-! ## `--eurostat`: Eurostat earn_net ESMS 3.4 (sha256 89ab2734..., `tests/data/_methodology/earn_net_esms.htm`):
"Income tax and social security contributions parameters refer to the beginning of the fiscal year, i.e. changes
occurring later during the year are ignored." Contributions: the maximum cotisable and the SSM of January (the first
period of the CCSS table) for all twelve months. Convention, never statute mode. -/
def cappedBaseCS (s : Bool) (y : Nat) (w : Int) : Int :=
  if !s then cappedBaseCY y w else
  let m := w * 100 / 12
  match yearP? y with
  | none => 12 * min m maxCot1C
  | some p => 12 * min m (p.maxCotC.headD 0)
def depCS (s : Bool) (y : Nat) (w : Int) : Int :=
  if !s then depCY y w else
  let m4 := w * 400 / 12
  match yearP? y with
  | none => (depRate * (12 * pos (m4 - ssm1C)) + 2 * BP) / (4 * BP)
  | some p => (depRate * (12 * pos (m4 - p.ssmC.headD 0)) + 2 * BP) / (4 * BP)
def Person.socialDedCS (s : Bool) (y : Nat) (p : Person) : Int :=
  rateC (pensionRate + healthRate + cashRate) (cappedBaseCS s y p.wages) + rateC healthRate (cappedBaseCS s y p.pension)
    + rateC (sePensionRate + seHealthRate) (cappedBaseCS s y p.se)
def Person.socialCS (s : Bool) (y : Nat) (p : Person) : Int := p.socialDedCS s y + depCS s y (p.wages + p.pension + p.se)
theorem cappedBaseCS_false (y : Nat) (w : Int) : cappedBaseCS false y w = cappedBaseCY y w := by simp [cappedBaseCS]
theorem depCS_false (y : Nat) (w : Int) : depCS false y w = depCY y w := by simp [depCS]
theorem socialDedCS_false (y : Nat) (p : Person) : p.socialDedCS false y = p.socialDedCY y := by
  simp [Person.socialDedCS, Person.socialDedCY, cappedBaseCS_false]
theorem socialCS_false (y : Nat) (p : Person) : p.socialCS false y = p.socialCY y := by
  simp [Person.socialCS, Person.socialCY, socialDedCS_false, depCS_false]
/-! ## `--euromod` (round 14; a EUROMOD convention, never statute mode): EUROMOD's reference date for legislative
parameters is 30 June of the policy year. Source: EUROMOD "Nowcasting prices" note, Feb 2025 (shipped in the J2.0+
Documentation folder, sha256 64eb954e350abd1c076260741b2b030aa7f897549ab9814f6ae505dd543b11f7), section 1.3
("Reference date parameters: End June y") and 1.4 ("Legislative parameters of the tax system are referred in EM to
30 June"). Here: the maximum cotisable, the SSM (dependence abattement) and the allocation-familiale index in force in
June (month index 5) for all twelve months. Tax credits are not re-timed. -/
def juneIdx : Nat := 5
def ssmAt (y : Nat) (k : Nat) : Int :=
  match yearP? y with
  | none => if (k : Int) < months1 then ssm1C else ssm2C
  | some p => p.ssmC.getD k 0
def maxCotAt (y : Nat) (k : Nat) : Int :=
  match yearP? y with
  | none => if (k : Int) < months1 then maxCot1C else maxCot2C
  | some p => p.maxCotC.getD k 0
def afIdxAt (y : Nat) (k : Nat) : Int :=
  match yearP? y with
  | none => if (k : Int) < months1 then index1 else index2
  | some p => p.afIdx.getD k 0
def cappedBaseCJ (y : Nat) (w : Int) : Int := 12 * min (w * 100 / 12) (maxCotAt y juneIdx)
def depCJ (y : Nat) (w : Int) : Int :=
  let m4 := w * 400 / 12
  (depRate * (12 * pos (m4 - ssmAt y juneIdx)) + 2 * BP) / (4 * BP)
def Person.socialDedCJ (y : Nat) (p : Person) : Int :=
  rateC (pensionRate + healthRate + cashRate) (cappedBaseCJ y p.wages) + rateC healthRate (cappedBaseCJ y p.pension)
    + rateC (sePensionRate + seHealthRate) (cappedBaseCJ y p.se)
def Person.socialCJ (y : Nat) (p : Person) : Int := p.socialDedCJ y + depCJ y (p.wages + p.pension + p.se)
/-- The year's allocation familiale at the June index for all twelve months (`--euromod`). -/
def afYearCJB (base : Int) (y : Nat) (age : Nat) : Int :=
  if age < 18 then 12 * afMonthCB base age (afIdxAt y juneIdx) else 0
theorem june_2025 : ssmAt 2025 juneIdx = ssm2C ∧ maxCotAt 2025 juneIdx = maxCot2C ∧ afIdxAt 2025 juneIdx = index2 := by
  decide

/-- Professional income in the sense of art. 129b (2) a) (wages or business profit). -/
def Person.professional (p : Person) : Bool := p.wages > 0 || p.se > 0
/-- Credits of one person (cents): CIS + CI-CO2 salarié + CISSM if wages; else CIP + CI-CO2 pensionné; else CII + CI-CO2
indépendant ("ne peut être cumulé"). -/
def Person.creditsC (p : Person) : Int :=
  if p.wages > 0 then cisC p.wages + co2C p.wages + cissmC p.wages
  else if p.pension > 0 then cipC p.pension + co2C p.pension 300
  else if p.se > 0 then (if p.se < cisLow then cisBase * 100 else cisC p.se) + co2C p.se
  else 0
/-- The year's credits; 2025: `creditsC`. Below 936 euros the CII is 300 euros in every year (art. 152ter). -/
def Person.creditsCY (y : Nat) (pp : Person) : Int :=
  match yearP? y with
  | none => pp.creditsC
  | some p =>
    if pp.wages > 0 then cisCY p pp.wages + co2CY p pp.wages + cissmCY p pp.wages + cieC p pp.wages + cicC p pp.wages
    else if pp.pension > 0 then cipCY p pp.pension + co2CY p pp.pension 300 + cieC p pp.pension + cicC p pp.pension
    else if pp.se > 0 then (if pp.se < cisLow then cisBase * 100 else cisCY p pp.se) + co2CY p pp.se + cieIndepC p pp.se
      + cicIndepC p pp.se
    else 0

structure Unit' where
  persons : List Person
  collective : Bool          -- art. 3: one assessment (class 2)
  individual3ter : Bool := false
  klass : TaxClass
  dividends : Int := 0
  rental : Int := 0
  charitable : Int := 0
  pensionContrib : Int := 0
  singleParent : Bool := false   -- CIM (art. 154ter): class 1a by a child, not living with the other parent
  year : Nat := 2025
  /-- `--eurostat`: contribution parameters of 1 January for the whole year (ESMS 3.4) -/
  startYear : Bool := false
  /-- `--euromod`: contribution parameters of 30 June for the whole year (EUROMOD reference date) -/
  june : Bool := false
  deriving Repr, Inhabited

def Unit'.sDed (u : Unit') (p : Person) : Int :=
  if u.june then p.socialDedCJ u.year else p.socialDedCS u.startYear u.year
def Unit'.sCap (u : Unit') (w : Int) : Int :=
  if u.june then cappedBaseCJ u.year w else cappedBaseCS u.startYear u.year w
def Unit'.sAll (u : Unit') (p : Person) : Int :=
  if u.june then p.socialCJ u.year else p.socialCS u.startYear u.year

/-- Capital income taxable by assessment (cents): dividends 50 % exempt (art. 115 n° 15a), less the frais d'obtention
forfait (art. 107 (1) 3., doubled for a couple who each receive half) and the 1 500 / 3 000 euros exemption (art. 115
n° 15). -/
def Unit'.capitalC (u : Unit') : Int :=
  let n := if u.collective then 2 else 1
  let half := u.dividends * 100 * (BP - divExemptPct) / BP
  let fo := min (n * foCapital * 100) (pos half)
  pos (half - fo - n * capExempt * 100)

structure Assess where
  totalNetC : Int
  dsC : Int
  abattC : Int
  riaC : Int
  taxable : Int
  coteE : Int
  taxFE : Int      -- cote + majoration (euros)
  feE : Int
  creditsC : Int
  socialC : Int
  deriving Repr, Inhabited

def Unit'.assess (u : Unit') (oecd : Bool) : Assess :=
  let ps := u.persons
  let totalNet := sumInts (ps.map Person.netC) + u.capitalC + u.rental * 100
  let social := sumInts (ps.map u.sDed)
  -- art. 113: minimum forfaitaire 480 (sum for spouses who each have wages, reduced if the lower salary is small)
  let wageEarners := ps.filter (·.wages > 0)
  let forfait := if u.collective ∧ wageEarners.length = 2 then
      let low := (wageEarners.map fun p => p.wages * 100 - min (foWage * 100) (p.wages * 100) - rateC (pensionRate + healthRate + cashRate) (u.sCap p.wages)).foldl min (1000000000000)
      dsForfait * 100 + min (dsForfait * 100) (pos low)
    else dsForfait * 100
  let prev := min (pos u.pensionContrib * 100) (ps.length * prevoyanceCap * 100)
  let dsGroup := max forfait prev
  let gifts := min (pos u.charitable * 100) (min (pos totalNet * giftPct / BP) (giftCap * 100))
  let ds := social + dsGroup + gifts
  -- art. 129b: abattement extra-professionnel when both spouses have professional income, capped by each one's net
  let abatt := if u.collective ∧ ps.length = 2 ∧ ps.all Person.professional then
      let caps := ps.map fun p => pos (p.netC - u.sDed p - dsForfait * 100)
      min (abattExtraPro * 100) (caps.foldl min (abattExtraPro * 100))
    else 0
  let ria := pos (totalNet - ds - abatt)
  let x := roundRIA ria
  let c := coteY u.year u.klass x
  let twf := if oecd then taxWithFE_oecdCY u.year u.klass x else taxWithFEY u.year u.klass x * 100
  let fe := if oecd then twf - classTicksY u.year u.klass x / 100 else (taxWithFEY u.year u.klass x - c) * 100
  let cim := if u.singleParent then (match yearP? u.year with | none => cimC ria | some p => cimCY p ria) else 0
  let credits := sumInts (ps.map (Person.creditsCY u.year)) + cim
  { totalNetC := totalNet, dsC := ds, abattC := abatt, riaC := ria, taxable := x, coteE := c, taxFE := twf,
    feE := fe, creditsC := credits, socialC := sumInts (ps.map u.sAll) }

/-- Euros from cents, half up (also for negatives). -/
def eur (c : Int) : Int := (c + 50) / 100

/-! ## The household -/

def classOf (p : Person) (hasChild : Bool) : TaxClass :=
  if hasChild || p.age ≥ 64 then .c1a else .c1

def units (c : Canon) (individual : Bool) : List Unit' :=
  let kids := c.nChildren > 0
  let ps := c.adults.map Person.ofAdult
  match ps with
  | [p] =>
    [{ persons := [p], collective := false, klass := classOf p kids, dividends := c.dividends, rental := c.rentalIncome,
       charitable := c.charitable, pensionContrib := c.pensionContributions,
       singleParent := kids, year := c.year }]
  | [p, q] =>
    let joint := c.married || c.bool? "pacsJoint" == some true
    if joint ∧ ¬ individual then
      [{ persons := [p, q], collective := true, klass := .c2, dividends := c.dividends, rental := c.rentalIncome,
         charitable := c.charitable, pensionContrib := c.pensionContributions, year := c.year }]
    else
      -- separate returns; art. 3ter (2): class 1 for each spouse; unmarried: the children count in adult 1's household
      let k1 := if joint then TaxClass.c1 else classOf p kids
      let k2 := if joint then TaxClass.c1 else classOf q false
      [{ persons := [p], collective := false, individual3ter := joint, klass := k1, dividends := half1 c.dividends,
         rental := half1 c.rentalIncome, charitable := half1 c.charitable,
         pensionContrib := half1 c.pensionContributions, year := c.year },
       { persons := [q], collective := false, individual3ter := joint, klass := k2, dividends := half2 c.dividends,
         rental := half2 c.rentalIncome, charitable := half2 c.charitable,
         pensionContrib := half2 c.pensionContributions, year := c.year }]
  | _ => []

/-- Test probes (extra input fields, for the validation harness): `luRIA` (euros, a rounded RIA) gives the cote and the
cote + majoration of each class; `luGross` gives the CIS and CI-CO2 (cents); `luRIAC` (cents) gives the CIM (cents). -/
def probe (c : Canon) : List (String × Lean.Json) :=
  (match c.int? "luRIA" with
   | some x => [TaxClass.c1, .c1a, .c2].flatMap fun k =>
       [Out.d ("cote_" ++ k.name) (cote k x), Out.d ("tax_" ++ k.name) (taxWithFE k x)]
   | none => []) ++
  (match c.int? "luGross" with
   | some g => [Out.d "cisC" (cisC g), Out.d "co2C" (co2C g), Out.d "cipC" (cipC g), Out.d "cissmC" (cissmC g)]
   | none => []) ++
  (match c.int? "luRIAC" with
   | some r => [Out.d "cimC" (cimC r)]
   | none => [])

/-- Under art. 3ter (2) each spouse with professional income gets 2 250 of abattement (art. 129b (1)); applied here as a
reduction of the RIA through `Unit'.assess` would need the other spouse's income: added after the fact. -/
def outWith (args : List String) (c : Canon) : Out :=
  let oecd := args.contains "--oecd"
  let indiv := args.contains "--individual"
  let eurostat := args.contains "--eurostat"
  let euromod := args.contains "--euromod"
  let us := (units c indiv).map fun u => { u with startYear := eurostat, june := euromod }
  let both := c.adults.length = 2 ∧ (c.adults.map Person.ofAdult).all Person.professional
  let as := us.map fun u =>
    if u.individual3ter ∧ both then
      -- art. 129b (1) second sentence: 2 250 each when both spouses have professional income
      let a := u.assess oecd
      let ria := pos (a.riaC - abattExtraProIndiv * 100)
      let u2 := u
      let x := roundRIA ria
      let c0 := coteY u2.year u2.klass x
      let twf := if oecd then taxWithFE_oecdCY u2.year u2.klass x else taxWithFEY u2.year u2.klass x * 100
      { a with abattC := abattExtraProIndiv * 100, riaC := ria, taxable := x, coteE := c0, taxFE := twf,
               feE := if oecd then twf - classTicksY u2.year u2.klass x / 100 else (taxWithFEY u2.year u2.klass x - c0) * 100 }
    else u.assess oecd
  let taxFEC := sumInts (as.map (·.taxFE))
  let feC := sumInts (as.map (·.feE))
  let creditsC := sumInts (as.map (·.creditsC))
  let socialC := sumInts (as.map (·.socialC))
  let relibiC := rateC relibiRate (pos c.interest * 100)
  let kidsRaw : Array Json := match c.raw.getObjVal? "children" with | .ok (.arr a) => a | _ => #[]
  -- `--euromod` (convention, never statute mode; round 15): EUROMOD assigns the transitional regime by birth date.
  -- EUROMOD Country Report Luxembourg 2022-2025, 2.5.1.4 "Benefit amount" and Table 15: "For children born before
  -- 1 August 2016 or the families arrived at Luxembourg before 1 August 2016" the transitional (group) amounts; with
  -- age only, a child aged `a` at the end of year `y` with y − a ≤ 2015 was born before 1 August 2016. Statute mode
  -- keeps the default false (entitlement on 31 July 2016 is not a fact of the canonical household).
  let emBornBefore (i : Nat) : Bool := euromod && (c.children.getD i default).age + 2015 ≥ (c.year : Int)
  let flag (i : Nat) : Bool := match (kidsRaw.getD i Json.null).getObjVal? "luEntitled2016" with
    | .ok (.bool b) => b | _ => emBornBefore i
  let nFlag := ((List.range c.children.length).filter flag).length
  let group := match c.raw.getObjVal? "luGroup2016" with
    | .ok (.num n) => (numToInt n).toNat | _ => nFlag
  let afC := sumInts ((c.children.zipIdx).map fun (k, i) =>
    if euromod then afYearCJB (afBaseFor (flag i) group) c.year k.age else afYearCYB (afBaseFor (flag i) group) c.year k.age)
  let rsC := if oecd then 0 else sumInts (c.children.map fun k => rentreeC k.age)
  -- incomeTax = cote − crédits (the crédits are imputed on the cote + majoration and refunded beyond it)
  let itC := taxFEC - feC - creditsC
  Out.make c "LU" "EUR" (eur itC) (surtaxes := [("fondsEmploi", eur feC), ("RELIBI", eur relibiC)])
    (employeeSocial := eur socialC) (benefits := eur (afC + rsC))
    (detail := [Out.d "taxableIncome" (sumInts (as.map (·.taxable))),
      Out.dStr "taxClass" (String.intercalate "+" (us.map (·.klass.name))),
      Out.d "taxBeforeCredits" (eur taxFEC), Out.d "taxBeforeCreditsC" taxFEC, Out.d "cote" (sumInts (as.map (·.coteE))),
      Out.d "fondsEmploiC" feC, Out.d "creditsC" creditsC, Out.d "riaC" (sumInts (as.map (·.riaC))),
      Out.d "abattementC" (sumInts (as.map (·.abattC))), Out.d "depensesSpecialesC" (sumInts (as.map (·.dsC))),
      Out.d "socialC" socialC, Out.d "allocFamC" afC, Out.d "rentreeC" rsC, Out.d "relibiC" relibiC,
      Out.dBool "oecdConventions" oecd] ++ (if eurostat then [Out.dBool "eurostatConvention" true] else []) ++ probe c)
    (unsupported := ["capital gains: long-held non-substantial shares exempt (art. 99bis, 100); speculative/substantial gains not modelled",
      "RELIBI 250 EUR per-agent de minimis not applied", "bonification d'impôt pour enfant (art. 123bis) not modelled",
      "frais de déplacement (art. 105bis/107bis) not modelled", "self-employed social base simplified"] ++
      (if euromod then ["--euromod (EUROMOD J2.0+ convention, not statute): maximum cotisable, SSM and the allocation-familiale index of June for all twelve months (EUROMOD reference date 30 June: Nowcasting prices note Feb 2025, 1.3-1.4; CR LU General remark 'as of June 30th, when relevant'); tax credits not re-timed; children born before 1 August 2016 (y - age <= 2015) on the transitional group amounts (CR LU 2.5.1.4, Table 15)"] else []) ++
      (if eurostat then ["--eurostat (Eurostat earn_net ESMS 3.4): contribution ceiling and SSM of January for all twelve months; allocations familiales: the art. 272 amounts are the same for every age 6-11 (majoration 6-11), so the most-generous-within-6-11 rule changes nothing" ++ (if (yearP? c.year).isSome then "; for tax years before 2025 the tax credits introduced or ended within the year (CIE 2022, CIC 2023) are not re-timed to 1 January" else "")] else []) ++
      (if (yearP? c.year).isSome then ["tax year " ++ toString c.year ++ ": tarif, class 1a, CIS/CIP/CII, CI-CO2, CIM, CISSM, CIE, CIC (2023), contribution ceilings and allocations familiales by year (Years.lean); the 2022 CIE start month and the EMAF allocation months (July 2022, February 2023) follow from loi du 25.3.2015 art. 3 (2)-(4) and STATEC semestrial averages (Years.lean Index); allocation de rentrée scolaire and the other amounts as in 2025"] else []))

def out (c : Canon) : Out := outWith [] c

def country : Country :=
  { code := "LU", name := "Luxembourg", currency := "EUR", year := "2025", compute := out,
    computeWith := outWith }

end LuTax
