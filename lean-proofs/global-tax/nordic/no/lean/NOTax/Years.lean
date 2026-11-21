import NOTax.Person

/-!
# NOTax.Years: the income years 2023 and 2024 (round 3, 2026-11-19)

The 2025 model keeps its module constants (and the theorems about them). Earlier years go through a per-year
parameter record `YP` and a parallel computation (`linesY`) that differs from `Person.lines` only in the parameters.

Sources (saved in `refs/stv/`):
* Stortingets skattevedtak for inntektsåret 2023 (Lovdata STV/forskrift/2022-12-13-2199, `stv2023.txt`) and for
  2024 (STV/forskrift/2023-12-14-2071, `stv2024.txt`): § 3-1 trinnskatt, § 3-2 fellesskatt, § 3-8 municipal and
  county maxima, § 6-1 minstefradrag maxima, § 6-3 personfradrag, § 6-4 skattebegrensning, § 6-5 pension credit.
* Trygdeavgift: Innst. 3 S (2023–2024) (`inns-202324-003s.txt`), the recommended and adopted "Stortingsvedtak om
  fastsetting av avgifter mv. til folketrygden for 2024" §§ 6-8: "5,1 pst.", "7,8 pst.", "11,0 pst."; Innst. 3 S
  (2022–2023) (`inns-202223-003s.txt`) § 3.1.2: the 2022 rates "8,0 pst. på lønns- og trygdeinntekt, 11,2 pst. på
  næringsinntekt og 5,1 pst. på pensjonsinntekt", reduced "med 0,1 prosentenhet i 2023, til henholdsvis 7,9 og
  11,1 pst." (pension rate unchanged), adopted ("Komiteen slutter seg ... §§ 6, 7 og 8"); nedre grense raised
  "fra 64 650 kroner ... til 69 650 kroner" for 2023 (budget agreement, ftrl. § 23-3 (4) via Innst. 4 L), and
  still 69 650 in 2024 (Innst. 3 S 2023–2024: "øke nedre grense for å betale trygdeavgift fra 69 650 kroner").
  The vedtak text itself for 2023/2024 was not located on Lovdata; the Stortinget recommendations are cited.
* Minstefradrag rates 46 % / 40 % (sktl. § 6-32 (1); Innst. 3 S 2022–2023: "uendret fra 2022 på 46 pst. for
  lønn/trygd og 40 pst. for" pensjon).
Not sourced for 2023/2024, so not modelled (listed in `unsupported`): barnetrygd and utvidet barnetrygd amounts;
the pension-credit taper rates of sktl. § 16-1 (3) (the 2025 rates 16,7 % / 6 % are used), skjermingsrente, IPS cap.
-/

namespace NOTax
open TaxKernel

structure YP where
  year : Nat
  kommune : Int
  fylke : Int
  felles : Int
  trinn : Schedule
  trinnLow2 : Schedule
  minstMax : Int
  minstPensionMax : Int
  pf : Int
  taLow : Int
  taMid : Int
  taHigh : Int
  taFloor : Int
  pcFull : Int
  pcTaper : Schedule
  sbSingle : Int
  sbSpouse : Int
  /-- SV 2022 § 6-1: minstefradrag "ikke settes lavere enn 31 800 kroner" (wages) / "4 000 kroner" (pensions);
  no lower limit in SV 2023 and 2024. -/
  minstMin : Int := 0
  minstPensionMin : Int := 0

/-- 2022 (round 4): Stortingets skattevedtak for inntektsåret 2022 (Lovdata STV/forskrift/2021-12-14-3571,
`refs/stv/stv2022.txt`): § 3-1 "1,7 pst. ... 190 350 kroner, 4,0 pst. ... 267 900 kroner, 13,4 pst. ... 643 800
kroner, ... 16,4 pst. ... 969 200 kroner, ... 17,4 pst. ... 2 000 000 kroner"; § 3-2 "ellers: 8,65 pst."; § 3-8
"maksimum 2,40 pst." (fylke), "maksimum 10,95 pst." (kommune); § 6-1 "ikke settes lavere enn 31 800 kroner og ikke
høyere enn 109 950 kroner", pensions "4 000" / "90 800"; § 6-3 "58 250 kroner"; § 6-4 147 450 / 135 550; § 6-5
"33 400 kroner", "210 950 kroner i trinn 1 og 318 000 kroner i trinn 2"; § 6-6 "4 373 kroner pr. påbegynt måned".
Trygdeavgift 2022 (Innst. 3 S (2022–2023) § 3.1.2): "8,0 pst. på lønns- og trygdeinntekt, 11,2 pst. på
næringsinntekt og 5,1 pst. på pensjonsinntekt", "nedre grense på 64 650 kroner". -/
def yp2022 : YP :=
  { year := 2022, kommune := 1095, fylke := 240, felles := 865,
    trinn := Schedule.ofList [(0, 0), (190350, 170), (267900, 400), (643800, 1340), (969200, 1640), (2000000, 1740)],
    trinnLow2 := Schedule.ofList [(0, 0), (190350, 170), (267900, 400), (643800, 0)],
    minstMax := 109950, minstPensionMax := 90800, pf := 58250,
    taLow := 510, taMid := 800, taHigh := 1120, taFloor := 64650,
    pcFull := 33400, pcTaper := Schedule.ofList [(0, 0), (210950, 1670), (318000, 600)],
    sbSingle := 147450, sbSpouse := 135550, minstMin := 31800, minstPensionMin := 4000 }

/-- 2023: SV 2023 § 3-1 "1,7 pst. ... 198 350 kroner, 4,0 pst. ... 279 150 kroner, 13,5 pst. ... 642 950 kroner,
16,5 pst. ... 926 800 kroner, og 17,5 pst. ... 1 500 000 kroner"; § 3-2 "ellers: 8,40 pst."; § 3-8 "maksimum 2,45
pst." (fylke), "maksimum 11,15 pst." (kommune); § 6-1 "104 450 kroner", "86 250 kroner"; § 6-3 "79 600 kroner";
§ 6-4 "147 450 kroner for enslige og 135 550 kroner for hver ektefelle"; § 6-5 (as amended 16 June 2023 nr. 972)
"32 825 kroner", "246 800 kroner i trinn 1 og 373 650 kroner i trinn 2". Trygdeavgift 5,1 / 7,9 / 11,1 %, floor
69 650. -/
def yp2023 : YP :=
  { year := 2023, kommune := 1115, fylke := 245, felles := 840,
    trinn := Schedule.ofList [(0, 0), (198350, 170), (279150, 400), (642950, 1350), (926800, 1650), (1500000, 1750)],
    trinnLow2 := Schedule.ofList [(0, 0), (198350, 170), (279150, 400), (642950, 0)],
    minstMax := 104450, minstPensionMax := 86250, pf := 79600,
    taLow := 510, taMid := 790, taHigh := 1110, taFloor := 69650,
    pcFull := 32825, pcTaper := Schedule.ofList [(0, 0), (246800, 1670), (373650, 600)],
    sbSingle := 147450, sbSpouse := 135550 }

/-- 2024: SV 2024 § 3-1 "1,7 pst. ... 208 050 kroner, 4,0 pst. ... 292 850 kroner, 13,6 pst. ... 670 000 kroner,
16,6 pst. ... 937 900 kroner, og 17,6 pst. ... 1 350 000 kroner"; § 3-2 "ellers: 8,7 pst."; § 3-8 "maksimum 2,35
pst." (fylke), "maksimum 10,95 pst." (kommune); § 6-1 "104 450 kroner", "86 250 kroner"; § 6-3 "88 250 kroner";
§ 6-4 147 450 / 135 550; § 6-5 "34 350 kroner", "258 400 kroner i trinn 1 og 391 550 kroner i trinn 2".
Trygdeavgift 5,1 / 7,8 / 11,0 %, floor 69 650. -/
def yp2024 : YP :=
  { year := 2024, kommune := 1095, fylke := 235, felles := 870,
    trinn := Schedule.ofList [(0, 0), (208050, 170), (292850, 400), (670000, 1360), (937900, 1660), (1350000, 1760)],
    trinnLow2 := Schedule.ofList [(0, 0), (208050, 170), (292850, 400), (670000, 0)],
    minstMax := 104450, minstPensionMax := 86250, pf := 88250,
    taLow := 510, taMid := 780, taHigh := 1100, taFloor := 69650,
    pcFull := 34350, pcTaper := Schedule.ofList [(0, 0), (258400, 1670), (391550, 600)],
    sbSingle := 147450, sbSpouse := 135550 }

/-- SV 2023 § 6-6: "Fradrag etter skatteloven § 6-80 er 4 373 kroner pr. påbegynt måned. Fradrag gis kun for
perioden 1. januar 2023 til 28. februar 2023": 2 × 4 373 = 8 746 kroner for a single parent (enslig forsørger) in
2023; none in 2024 (no § 6-6 in SV 2024). Added to the person's deductions in alminnelig inntekt. -/
def saerfradragEnslig (y : Nat) : Int := if y = 2022 then 12 * 4373 else if y = 2023 then 2 * 4373 else 0

def ypFor (y : Nat) : Option YP := if y = 2022 then some yp2022 else if y = 2023 then some yp2023 else if y = 2024 then some yp2024 else none

def minstY (q : YP) (wages pension : Int) : Int :=
  let w := max (min (pos wages) q.minstMin) (cappedDeduction wages q.minstMax minstWageRate wages)
  let pe := max (min (pos pension) q.minstPensionMin) (cappedDeduction pension q.minstPensionMax minstPensionRate pension)
  min q.minstMax (w + pe)

def alminneligBeforeOppY (q : YP) (p : PersonIn) : Int :=
  alminneligBeforeOpp p + minstefradrag p.wages p.pension - minstY q p.wages p.pension

def grunnlagY (q : YP) (p : PersonIn) : Int := taxableAfter q.pf (alminneligBeforeOppY q p + oppTillegg p)

def taRateTicksY (q : YP) (p : PersonIn) : Int :=
  if lowRateAge p.age then q.taLow * personinntekt p
  else q.taMid * pos p.wages + q.taLow * pos p.pension + q.taHigh * pos p.business

def taTicksY (q : YP) (p : PersonIn) : Int :=
  if personinntekt p ≤ q.taFloor then 0
  else min (taRateTicksY q p) (taCapRate * pos (personinntekt p - q.taFloor))

/-- (central, local, social) before credits, in ticks. -/
def ticksY (q : YP) (p : PersonIn) : Int × Int × Int :=
  let g := grunnlagY q p
  ((Schedule.flat q.felles).ticks g + q.trinn.ticks (personinntekt p),
   (Schedule.flat q.kommune).ticks g + (Schedule.flat q.fylke).ticks g, taTicksY q p)

/-- Statute rounding (skattebetalingsforskriften § 10-4-4: each tax rounded down to the krone). -/
def ordinaryPartsY (q : YP) (p : PersonIn) : Int × Int × Int :=
  let g := grunnlagY q p
  let rd (t : Int) := Rule.unitDown.ofTicks t
  (rd ((Schedule.flat q.felles).ticks g) + rd (q.trinn.ticks (personinntekt p)),
   rd ((Schedule.flat q.kommune).ticks g) + rd ((Schedule.flat q.fylke).ticks g), rd (taTicksY q p))

def ordinaryTaxY (q : YP) (p : PersonIn) : Int :=
  let (c, l, s) := ordinaryPartsY q p
  c + l + s

def pensionCreditY (q : YP) (p : PersonIn) : Int :=
  let gross := if p.alderspensjon then pos (q.pcFull - Rule.unitDown.ofTicks (q.pcTaper.ticks (pos p.pension))) else 0
  usedCredit (ordinaryTaxY q p) gross

def sbIncomeY (q : YP) (p : PersonIn) : Int :=
  alminneligBeforeOppY q p
    + sbWealthRate * pos (p.netWealth - (if p.spouse then sbWealthFreeSpouse else sbWealthFreeSingle)) / BP

def sbListedY (q : YP) (p : PersonIn) : Int :=
  let g := grunnlagY q p
  let rd (t : Int) := Rule.unitDown.ofTicks t
  rd ((Schedule.flat q.kommune).ticks g) + rd ((Schedule.flat q.fylke).ticks g) + rd ((Schedule.flat q.felles).ticks g)
    + q.trinnLow2.tax Rule.unitDown (personinntekt p) + rd (taTicksY q p)

def sbTaxY (q : YP) (p : PersonIn) : Int :=
  let lim := if p.spouse then q.sbSpouse else q.sbSingle
  if sbIncomeY q p ≤ lim then 0
  else min (sbListedY q p) (Rule.unitDown.ofTicks (sbRate * (sbIncomeY q p - lim))) + (ordinaryTaxY q p - sbListedY q p)

def totalTaxY (q : YP) (p : PersonIn) : Int :=
  let viaCredit := ordinaryTaxY q p - pensionCreditY q p
  let t := if sbApplies p then min viaCredit (sbTaxY q p) else viaCredit
  t - usedCredit t (bsuCreditGross p)

/-- The lines of a person in year `q` (statute rounding, or unrounded half-up once with `oecd`). -/
def linesY (oecd : Bool) (q : YP) (p : PersonIn) : Lines :=
  let (c0, l0, s0) := if oecd then
      let (a, b, d) := ticksY q p
      (Rule.unitHalfUp.ofTicks a, Rule.unitHalfUp.ofTicks b, Rule.unitHalfUp.ofTicks d)
    else ordinaryPartsY q p
  let r := ordinaryTaxY q p - totalTaxY q p
  let rc := min r c0
  let rl := min (r - rc) l0
  let rs := r - rc - rl
  { central := c0 - rc, local_ := l0 - rl, social := s0 - rs }

end NOTax
