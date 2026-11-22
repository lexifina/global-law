import TaxKernel.World

/-!
# Morocco: impôt sur le revenu, revenus salariaux (Code général des impôts), 2025

Statute: the DGI's consolidated **CGI 2025** ("tel que modifié et complété 2025", Word export of 20 December 2024),
archived official copy `web.archive.org/web/20250304013712id_/https://www.tax.gov.ma/wps/wcm/connect/d15709dd-…/CGI+2025+FR..pdf`
(tax.gov.ma refuses the build server and answers 403 to a second machine; sha256 f510cca73c15…, 750 pages).
* Art. 73-I (LF n° 60-24 for 2025, art. 8): "la tranche du revenu allant jusqu'à 40 000 dirhams est exonérée ; 10%
  … 40.001 à 60.000 ; 20% … 60.001 à 80.000 ; 30% … 80.001 à 100.000 ; 34% … 100.001 à 180.000 ; 37% pour le
  surplus". LF 60-24 art. 8 III-12°: arts. 73-I and 74-I "sont applicables aux revenus autres que fonciers acquis à
  compter du 1er janvier 2025".
* Art. 59-I-A: frais inhérents à la fonction "35% … dont le revenu brut annuel imposable n'excède pas soixante dix
  huit mille (78 000) dirhams. Ce taux est fixé à 25% pour les personnes dont le revenu brut annuel imposable est
  supérieur à … (78 000) dirhams, sans que cette déduction puisse excéder trente-cinq mille (35 000) dirhams" (LF 50-22
  for 2023). The base excludes benefits in cash or in kind.
* Art. 59-II-A: "Les retenues supportées pour la constitution de pensions ou de retraites : A.- En application : ...
  du régime de sécurité sociale régi par le dahir portant loi n° 1-72-184 du 15 joumada II 1392 (27 juillet 1972)";
  III: "Les cotisations aux organismes marocains de prévoyance sociale ainsi que les cotisations salariales de
  sécurité sociale pour la couverture des dépenses relatives aux prestations à court terme". Deducted from the gross
  sums alongside the art. 59-I frais (which are computed on the gross).
* W5 pattern A (2026-11-20): employee CNSS and AMO contributions. Rates: the CNSS page "Paiement de vos cotisations
  sociales", section "Barèmes et taux de cotisation" (cnss.ma, Internet Archive capture 2025-03-25; official
  secondary: décret 2-01-2723 as amended and the AMO décrets were not reached; `ma/law/w5/`), facts restated: short-term benefits
  1,05 % employer and 0,52 % employee (1,57 % in all) on each wage capped at 6 000 dirhams; long-term benefits 7,93 %
  and 3,96 % (11,89 %) on the same capped wage; compulsory health insurance (AMO) 4,11 % and 2,26 % (6,37 %) on the
  whole wage of the month or quarter; 0,57 % of the short-term rate funds the job-loss allowance, 0,19 % of it from
  the employee. The CNSS notice "AMO Ajustement des taux de cotisation" (capture 2016-02-25) dates the AMO 2,26 %
  employee share from 1 January 2016. So the employee pays 0,52 % + 3,96 % = 4,48 % of the wage up to 6 000 dirhams a
  month and 2,26 % of the whole wage; 12 equal months; dirhams, rounded down. All deducted (art. 59-II-A for the long
  term, III for the short term and the AMO). `"w5Contrib": false` restores the pre-W5 model.
* Art. 74-I: "une somme de cinq cents (500) dirhams par personne à charge … le montant total des réductions pour
  charge de famille ne peut pas dépasser trois mille (3000) dirhams"; II: "A.- son épouse" (no income condition) and children (≤ 27 years, own
  income not above the exempt band); the wife may claim for her husband and children when legally at her charge.
Unit: individual (each spouse taxed on own income). The family reductions go to the first adult (or to the earning
spouse when the first has no income).
-/

namespace MaTax
open TaxKernel

/-- Art. 73-I (bp). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (40000, 1000), (60000, 2000), (80000, 3000), (100000, 3400), (180000, 3700)]

def taxOn (ni : Int) : Int := sched.tax Rule.unitDown (pos ni)

/-- Art. 59-I-A: professional expenses on the gross annual taxable salary `g`. -/
def fraisPro (g : Int) : Int :=
  if g ≤ 78000 then pos g * 35 / 100 else min 35000 (pos g * 25 / 100)

def netSalary (g : Int) : Int := pos g - fraisPro g

/-- W5 pattern A: CNSS page rates, employee 0,52 % (court terme) + 3,96 % (long terme) on the wage capped at 6 000 a
month, 2,26 % AMO on the whole wage. Annual, on an annual wage paid evenly. -/
def pctBp : Int := 52
def pltBp : Int := 396
def amoBp : Int := 226
def plafondMonth : Int := 6000
def cnssEmp (g : Int) : Int :=
  divR .down (min (pos g) (12 * plafondMonth) * (pctBp + pltBp)) BP + divR .down (pos g * amoBp) BP
/- The page's global rates: 1,05 + 0,52 = 1,57; 7,93 + 3,96 = 11,89; 4,11 + 2,26 = 6,37. -/
#guard 105 + pctBp = 157 ∧ 793 + pltBp = 1189 ∧ 411 + amoBp = 637
/- 72 000 a year (the cap exactly): 3 225 + 1 627 = 4 852; 120 000: the CNSS part stays 3 225, AMO 2 712. -/
#guard cnssEmp 72000 = 4852 ∧ cnssEmp 120000 = 3225 + 2712

/-- Art. 60-I (CGI 2025): pensions and life annuities, "un abattement forfaitaire de : - 70% sur le montant brut qui ne
dépasse pas annuellement 168 000 dirhams ; - 40% pour le surplus" (after the contributions of art. 59 III and IV, not
modelled). Round D6. -/
def pensionAbatement (p : Int) : Int := divR .down (7000 * min (pos p) 168000) BP + divR .down (4000 * pos (p - 168000)) BP
def netPension (p : Int) : Int := pos p - pensionAbatement p

/-- LF n° 60-24 pour 2025, art. 8-III-8° (CGI 2025 p. ~27530): art. 57-27° (exemption of basic-scheme pensions) applies
to pensions acquired from 1 January 2026; "A titre transitoire ..., les titulaires des pensions de retraite et des rentes
viagères acquises dans le cadre des régimes de retraite de base visés à l'article 59-II-A ..., à l'exclusion de celles
acquises dans le cadre des régimes de retraite complémentaire, bénéficient d'une réduction de 50% du montant de l'impôt
dû au titre desdites pensions ... acquises au titre de l'année 2025". The tax due on the pension is its share of the
person's tax (after the family reduction) in proportion to the net pension (reading); pensions are read as basic-scheme
pensions unless `maPensionComplementary` is true. Round D6. -/
def pensionReduction (taxDue niTotal niPension : Int) : Int :=
  if niTotal ≤ 0 || niPension ≤ 0 then 0 else divR .down (taxDue * niPension) (2 * niTotal)

/-- Art. 74-I: 500 per dependant, total at most 3,000. -/
def familyReduction (n : Nat) : Int := min 3000 (500 * n)

def out (c : Canon) : Out :=
  let a1 := c.adult1
  let kids := c.childrenUnder 28
  let basic := !((c.bool? "maPensionComplementary").getD false)
  let w5 := (c.bool? "w5Contrib").getD true
  let cn (g : Int) : Int := if w5 then cnssEmp g else 0
  let np1 := netPension a1.pension
  let ni1 := pos (netSalary a1.wages - cn a1.wages) + a1.selfEmployment + np1
  let (ni2, np2, spouseDep) := match c.adult2? with
    | some a2 => (pos (netSalary a2.wages - cn a2.wages) + a2.selfEmployment + netPension a2.pension, netPension a2.pension, (if c.married then 1 else 0))
    | none => (0, 0, 0)
  -- the claimant: adult 1, unless adult 1 has no income and adult 2 has (art. 74-II last paragraph)
  let claim2 := ni1 == 0 && ni2 > 0
  let red := familyReduction (kids + (if claim2 then 0 else spouseDep))
  let t1 := taxOn ni1
  let t2 := taxOn ni2
  let (t1', t2') := if claim2 then (t1, pos (t2 - red)) else (pos (t1 - red), t2)
  let pr1 := if basic then pensionReduction t1' ni1 np1 else 0
  let pr2 := if basic then pensionReduction t2' ni2 np2 else 0
  let es := sumInts (c.adults.map fun a => cn a.wages)
  Out.make c "MA" "MAD" (t1' - pr1 + t2' - pr2) (employeeSocial := es)
    (detail := [Out.d "taxableIncome" (ni1 + ni2), Out.d "taxBeforeCredits" (t1 + t2), Out.d "familyReduction" red,
      Out.d "pensionReduction2025" (pr1 + pr2), Out.d "pensionAbatement" (pensionAbatement a1.pension + (match c.adult2? with | some a => pensionAbatement a.pension | none => 0)),
      Out.d "fraisProfessionnels" (fraisPro a1.wages + (match c.adult2? with | some a => fraisPro a.wages | none => 0))])
    (unsupported := [if w5 then "CNSS 0,52 % + 3,96 % (6 000 a month cap) and AMO 2,26 % from the CNSS rate page (official secondary; the décrets not reached), deducted (art. 59-II-A, III)" else "CNSS / AMO / pension contributions not modelled and not deducted (art. 59-II, III)",
      "pensions: art. 60-I abatement and the 2025 transitional 50 % reduction (LF 60-24 art. 8-III-8°) for basic-scheme pensions; the pensioner's art. 59 III/IV contributions not deducted",
      "rental income (art. 64, 73-II), interest and dividends (art. 73-II withholding) not modelled",
      "self-employment taken as net professional income (art. 30 ff. not read)"])

/- A basic-scheme pension of 240,000, no dependants: abatement 117,600 + 28,800 = 146,400; net 93,600; tax 2,000 +
4,000 + 30 % x 13,600 = 10,080; the 2025 reduction halves it: 5,040. -/
#guard pensionAbatement 240000 = 146400 ∧ taxOn (netPension 240000) = 10080
#guard (out { id := "p", adults := [{ age := 65, pension := 240000 }] }).incomeTax = 5040

def country : Country :=
  { code := "MA", name := "Morocco (CGI 2025, IR salaires)", currency := "MAD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Art. 73-I band ends: 60,000 → 2,000; 80,000 → 6,000; 100,000 → 12,000; 180,000 → 39,200. -/
#guard taxOn 60000 = 2000 ∧ taxOn 80000 = 6000 ∧ taxOn 100000 = 12000 ∧ taxOn 180000 = 39200
/- Art. 59-I-A: the deduction falls from 27,300 to 19,500 when gross pay passes 78,000 by one dirham. -/
#guard fraisPro 78000 = 27300 ∧ fraisPro 78001 = 19500 ∧ fraisPro 200000 = 35000
#guard taxOn (netSalary 78000) = 1070 ∧ taxOn (netSalary 78001) = 1850

end MaTax
