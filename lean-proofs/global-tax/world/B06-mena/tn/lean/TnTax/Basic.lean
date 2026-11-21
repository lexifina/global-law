import TaxKernel.World

/-!
# Tunisia: impôt sur le revenu des personnes physiques (Code de l'IRPP et de l'IS, loi 89-114), revenus 2025

Statute:
* Barème: Code IRPP art. 44 I as replaced by **Loi n° 2024-48 du 9 décembre 2024 portant loi de finances pour 2025,
  art. 36** (JORT n° 149 of 10 December 2024, official PDF `finances.gov.tn/sites/default/files/2024-12/LF2025.pdf`,
  sha256 08feaf86e175…): bands 0–5,000 0 %; 5,000.001–10,000 15 %; 10,000.001–20,000 25 %; 20,000.001–30,000 30 %;
  30,000.001–40,000 33 %; 40,000.001–50,000 36 %; 50,000.001–70,000 38 %; above 70,000 40 %; art. 36 (2): "تطبق أحكام هذا
  الفصل على المداخيل المحققة ابتداء من غرة جانفي 2025". The printed "taux effectif à la limite supérieure" column
  (7.50 %, 16.25 %, 20.83 %, 23.88 %, 26.30 %, 29.64 %) is checked below with `#guard`.
* The DGI consolidated code (`jibaya.tn/wp-content/uploads/2025/07/code-IS-et-IRPP-francais-1.pdf`, sha256
  0006d25e15d7…, July 2025, "Modifié … Art 36-1 LF 2024-48"):
  art. 26 I: salary net of "les retenues obligatoires … régimes obligatoires de sécurité sociale" and "les frais
  professionnels fixés forfaitairement à 10% du reliquat … sans que la déduction dépasse 2.000 dinars par an";
  art. 26 II pensions "abattement de 25%"; art. 28 II rents: 25 % of gross deducted (built property);
  art. 40 I chef de famille 300 dinars; II "au titre des quatre premiers enfants … 100 dinars" (children under 20 on
  1 January); art. 5: the husband is chef de famille; the wife when the husband has no income.
  art. 44 I: "décompter la fraction du dinar comme un dinar entier".
* Contribution sociale de solidarité (CSS): LF 2018 (loi 2017-66) art. 53 and LF 2023 art. 22, read through the DGI's
  Note commune n° 1/2026 (`jibaya.tn/wp-content/uploads/2026/01/مذكرة-عامة-عدد-1.pdf`, part I, which restates the law
  in force to 31 December 2025): the CSS is the difference between the tax on the art. 44 barème with **half a point**
  added to each band rate ("بإضافة نصف نقطة لنسب الضريبة") and the tax without it, for wages paid from 1 January
  2023 to the end of 2025; exempt: persons with only wages/pensions whose net annual income after the family
  deductions does not exceed 5,000 dinars. `"source": "official secondary"` (the LF 2018 and LF 2023 texts themselves
  were not reached).
W5 pattern A (2026-11-20): CNSS employee contribution 9,18 % of all remuneration, deducted under art. 26 I before the
10 % professional expenses. Source: the CNSS page for employers of the non-agricultural sector, contributions tab
(cnss.tn, fetched 2026-11-20; official secondary: the décrets under loi 60-30 were not reached): "حددت نسبة اشتراكات
الضمان الاجتماعي بـ 25,75 % موزعة كما يلي : 16,57 % على كاهل المؤجر 9,18 % على كاهل الأجير" and the base "مجموع عناصر
الأجور و الرّواتب و المنح و غيرها من المنافع النقدية و العينية" (no ceiling; legislative references: loi 60-30 arts.
40-47, 105). `"w5Contrib": false` restores the pre-W5 model. Not modelled (flagged): interest and dividends (separate
withholding regimes not read).
Unit: individual; the chef de famille takes the family deductions.
-/

namespace TnTax
open TaxKernel

/-- Art. 44 I (LF 2025 art. 36): the barème (bp). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (5000, 1500), (10000, 2500), (20000, 3000), (30000, 3300), (40000, 3600), (50000, 3800),
    (70000, 4000)]

/-- The CSS barème: every band rate + 50 bp (LF 2023 art. 22 via Note commune 1/2026). -/
def schedCss : Schedule :=
  Schedule.ofList [(0, 50), (5000, 1550), (10000, 2550), (20000, 3050), (30000, 3350), (40000, 3650), (50000, 3850),
    (70000, 4050)]

def taxOn (ni : Int) : Int := sched.tax Rule.unitDown (pos ni)

/-- CSS = tax on barème + 0.5 point − tax on barème; exempt for wage/pension-only income ≤ 5,000. -/
def css (ni : Int) (wageOnly : Bool) : Int :=
  if wageOnly && ni ≤ 5000 then 0
  else pos ((schedCss.ticks (pos ni) - sched.ticks (pos ni)) / BP)

/-- Art. 26 I: net salary (no CNSS deducted: not modelled) less 10 % professional expenses capped at 2,000. -/
def netSalary (w : Int) : Int := pos w - min 2000 (pos w / 10)

/-- W5 pattern A: CNSS employee 9,18 % of all remuneration (CNSS page; 25,75 = 16,57 + 9,18), in whole dinars
(the model's unit), rounded down. -/
def cnssEmpBp : Int := 918
def cnssEmp (w : Int) : Int := divR .down (pos w * cnssEmpBp) 10000
#guard 1657 + cnssEmpBp = 2575 ∧ cnssEmp 20000 = 1836

/-- Art. 26 II: pensions less 25 %. -/
def netPension (p : Int) : Int := pos p - pos p / 4

/-- Art. 28 II: rents less 25 %. -/
def netRent (r : Int) : Int := pos r - pos r / 4

/-- Art. 40: chef de famille 300 + 100 for each of the first four children under 20. -/
def familyDeduction (married : Bool) (kidsUnder20 : Nat) : Int :=
  (if married then 300 else 0) + 100 * (min kidsUnder20 4 : Nat)

structure PersonResult where
  net : Int
  tax : Int
  css : Int

def person (a : Adult) (rent : Int) (fam : Int) (cn : Int := 0) : PersonResult :=
  let gross := netSalary (pos a.wages - cn) + netPension a.pension + a.selfEmployment + netRent rent
  let ni := pos (gross - fam)
  let wageOnly := a.selfEmployment == 0 && rent == 0
  { net := ni, tax := taxOn ni, css := css ni wageOnly }

def out (c : Canon) : Out :=
  let kids := c.childrenUnder 20
  let a1 := c.adult1
  let rent := c.rentalIncome
  -- art. 5: the husband (first adult) is chef de famille unless he has no income
  let a1Chef := match c.adult2? with
    | some a2 => !(a1.wages + a1.pension + a1.selfEmployment == 0 && a2.wages + a2.pension + a2.selfEmployment > 0)
    | none => true
  -- a single parent (divorced with custody, widowed) is chef de famille too (art. 5); a single without children not
  let chefDed := familyDeduction (c.married || (c.adult2?.isNone && kids > 0)) kids
  let w5 := (c.bool? "w5Contrib").getD true
  let cnOf (a : Adult) : Int := if w5 then cnssEmp a.wages else 0
  let r1 := person a1 (half1 rent) (if a1Chef then chefDed else 0) (cnOf a1)
  let rs := match c.adult2? with
    | some a2 => [r1, person a2 (half2 rent) (if a1Chef then 0 else chefDed) (cnOf a2)]
    | none => [r1]
  let it := sumInts (rs.map (·.tax))
  let cs := sumInts (rs.map (·.css))
  let es := sumInts (c.adults.map cnOf)
  Out.make c "TN" "TND" it (surtaxes := [("contributionSocialeSolidarite", cs)]) (employeeSocial := es)
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.net))), Out.dStr "cssSource" "official secondary (DGI NC 1/2026)"])
    (unsupported := [if w5 then "CNSS employee 9,18 % from the CNSS page (official secondary; décrets under loi 60-30 not reached), deducted (art. 26 I)" else "CNSS employee contributions not modelled and not deducted (art. 26 I)",
      "interest and dividends not modelled (withholding regimes not read)",
      "art. 39 deductions (life insurance, housing-loan interest, savings) not claimed",
      "children's own income, students (1,000) and disabled children (2,000) deductions not modelled"])

def country : Country :=
  { code := "TN", name := "Tunisia (Code de l'IRPP, barème LF 2025)", currency := "TND", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- The barème's printed "taux effectif à la limite supérieure" (LF 2025 art. 36): 10,000 → 7.50 %,
   20,000 → 16.25 %, 30,000 → 20.83 %, 40,000 → 23.88 % (23.875), 50,000 → 26.30 %, 70,000 → 29.64 % (29.643). -/
#guard taxOn 10000 = 750 ∧ taxOn 20000 = 3250 ∧ taxOn 30000 = 6250 ∧ taxOn 40000 = 9550
#guard taxOn 50000 = 13150 ∧ taxOn 70000 = 20750
/- CSS: half a point on every band = 0.5 % of the income; exempt at 5,000 for a wage earner, 25 dinars just above. -/
#guard css 5000 true = 0 ∧ css 5001 true = 25 ∧ css 5000 false = 25

end TnTax
