import TaxKernel.World

/-!
# Algeria: impôt sur le revenu global (IRG), Code des impôts directs et taxes assimilées (CIDTA) art. 104, 2025

Statute (Journal officiel, French translation, `joradp.dz/FTP/JO-FRANCAIS/<year>/F<year><no>.pdf`):
* **Loi n° 21-16 du 30 décembre 2021 portant loi de finances pour 2022, art. 31** (JO n° 100 of 2021, F2021100.pdf,
  sha256 in FINDINGS) rewrites CIDTA art. 104:
  I: "N'excédant pas 240.000 DA 0% / de 240.001 DA à 480.000 DA 23% / de 480.001 DA à 960.000 DA 27% / de 960.001 DA
  à 1.920.000 DA 30% / de 1.920.001 DA à 3.840.000 DA 33% / Supérieure à 3.840.000 DA 35%";
  II.3.a (salaries, pensions): withholding "calculée par mensualisation des revenus, sur la base du barème ci-dessus";
  "abattement proportionnel sur l'impôt global égal à 40%", "ne peut être inférieur à 12.000 DA /an ou supérieur à
  18.000 DA /an (soit entre 1.000 et 1.500 DA /mois)"; "exonération totale de l'IRG, les revenus qui n'excèdent pas
  30.000 dinars"; between 30,000 and 35,000: "IRG = IRG (selon le premier abattement) x (137/51) – (27 925/8)";
  retired workers of the general scheme (and disabled workers) between 30,000 and 42,500:
  "IRG = IRG (selon le premier abattement) x (93/61) – (81 213/41)".
  II.2: rents: final 7 % (housing) up to a threshold that **Loi n° 22-24 (LF 2023) art. 5** (JO n° 89 of 2022) raised
  from 600,000 to "1.800.000 DA"; that article leaves I and II.3 "(sans changement)".
* **Loi n° 24-08 du 24 novembre 2024 portant loi de finances pour 2025, art. 8** (JO n° 84 of 26 December 2024,
  F2024084.pdf, sha256 d0da2a51d537…) re-enacts art. 104 with I and II 1)-4) "(sans changement)": the 2022 wording
  governs 2025 unless the finance laws for 2023/2024 changed it (checked: FINDINGS / PROGRESS).
W5 pattern A (2026-11-20): employee social security (CNAS) 9 % of the contribution base, reported. **Décret exécutif
n° 06-339 du 25 septembre 2006 modifiant le décret exécutif n° 94-187 du 6 juillet 1994 fixant la répartition du taux
de la cotisation de sécurité sociale** (JO n° 60 of 27 September 2006, F2006060.pdf, p. 16; `dz/law/w5/`), art. 1:
"Article 1er.— Le taux de la cotisation de sécurité sociale ... est réparti à partir du 1er octobre 2006 comme suit :
— 25% ... à la charge de l'employeur, — 9% de l'assiette de cotisation de sécurité sociale à la charge du travailleur,
— 0,5% ... au titre de la quote-part du Fonds des œuvres sociales"; art. 2 table (34,5 %): worker 1,50 % assurances
sociales + 6,75 % retraite + 0,50 % assurance-chômage + 0,25 % retraite anticipée = 9 %. Base: Ordonnance 95-01 (not
reached; no ceiling in the decree). Later amendments of décret 94-187 were not checked. The deduction of the worker's
share from the IRG base (CIDTA, not reached: mfdgi.gov.dz did not answer) is NOT applied: the contribution is reported
only. `"w5Contrib": false` restores the pre-W5 model. Not modelled (flagged): capital income. Unit: individual; monthly withholding on 12 equal months.
-/

namespace DzTax
open TaxKernel

/-- Art. 104 I (annual, bp). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (240000, 2300), (480000, 2700), (960000, 3000), (1920000, 3300), (3840000, 3500)]

/-- The same barème "par mensualisation" (thresholds / 12, all exact). -/
def monthly : Schedule :=
  Schedule.ofList [(0, 0), (20000, 2300), (40000, 2700), (80000, 3000), (160000, 3300), (320000, 3500)]

/-- IRG after the 40 % abatement, bounded to 1,000–1,500 DA a month. -/
def afterFirst (r : Int) : Int :=
  let t := monthly.tax Rule.unitDown (pos r)
  pos (t - clamp 1000 1500 (t * 40 / 100))

/-- Art. 104 II.3.a: monthly IRG on salaries (`retired` = retired worker of the general scheme). -/
def monthlyIRG (retired : Bool) (r : Int) : Int :=
  let t1 := afterFirst r
  if r ≤ 30000 then 0
  else if !retired && r < 35000 then pos ((t1 * 137 * 8 - 27925 * 51) / (51 * 8))
  else if retired && r < 42500 then pos ((t1 * 93 * 41 - 81213 * 61) / (61 * 41))
  else t1

def wageIRG (annual : Int) : Int := perPeriod 12 (monthlyIRG false) (pos annual)

/-- W5 pattern A: Décret exécutif 06-339 art. 1-2, worker 9 % (1,5 + 6,75 + 0,5 + 0,25). -/
def cnasWorkerBp : Int := 900
def cnasWorker (w : Int) : Int := divR .down (pos w * cnasWorkerBp) 10000
#guard 150 + 675 + 50 + 25 = cnasWorkerBp ∧ 2500 + cnasWorkerBp + 50 = 3450 ∧ cnasWorker 600000 = 54000
def pensionIRG (annual : Int) : Int := perPeriod 12 (monthlyIRG true) (pos annual)

/-- Art. 104 II.1 (profits, annual barème) and II.2 (housing rents ≤ 1,800,000: final 7 %). Above 1,800,000 the rent
goes to the global barème with CIDTA art. 85's abatement (Loi n° 21-16, LF 2022, art. 28, law/jo/lf2022.txt; not changed
by LF 2023-2025): "Bénéficient d'un abattement de 25%, les revenus fonciers issus de la location à usage d'habitation à
retenir dans l'assiette de l'impôt sur le revenu global" (fixed by round L1-S, 2026-11-21: the base was the whole rent). -/
def profitsIRG (p : Int) : Int := sched.tax Rule.unitDown (pos p)
def rentIRG (r : Int) : Int :=
  if r ≤ 1800000 then pos r * 7 / 100 else sched.tax Rule.unitDown (pos r - pos r * 25 / 100)

def out (c : Canon) : Out :=
  let w := sumInts (c.adults.map fun a => wageIRG a.wages + pensionIRG a.pension + profitsIRG a.selfEmployment)
  let rent := match c.adult2? with
    | some _ => rentIRG (half1 c.rentalIncome) + rentIRG (half2 c.rentalIncome)
    | none => rentIRG c.rentalIncome
  let w5 := (c.bool? "w5Contrib").getD true
  let es := if w5 then sumInts (c.adults.map fun a => cnasWorker a.wages) else 0
  Out.make c "DZ" "DZD" (w + rent) (employeeSocial := es)
    (detail := [Out.d "rentIRG" rent, Out.d "taxableIncome" (sumInts (c.adults.map fun a => a.wages + a.pension + a.selfEmployment))])
    (unsupported := [if w5 then "CNAS worker 9 % (décret 06-339) reported; its deduction from the IRG base (CIDTA) not reached and not applied" else "CNAS employee social security not modelled and not deducted from the IRG base",
      "rents above 1,800,000 DA: provisional 7 % credited against the global barème; modelled as the barème on 75 % of the rent (art. 85 abatement), alone",
      "interest, dividends and capital gains not modelled",
      "disabled workers' second abatement (30,000–42,500) not modelled (no disability field)"])

def country : Country :=
  { code := "DZ", name := "Algeria (CIDTA art. 104, IRG)", currency := "DZD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- L1-S: art. 104 II.2 + art. 85: 7 % of 1,800,000 = 126,000; one dinar more: the barème on 1,350,000 (75 %) = 301,800. -/
#guard rentIRG 1800000 = 126000 ∧ rentIRG 1800001 = 301800 ∧ rentIRG 2400000 = sched.tax Rule.unitDown 1800000

/- The monthly barème is the annual one / 12 at every threshold. -/
#guard [240000, 480000, 960000, 1920000, 3840000, 4800000].all fun x => sched.tax Rule.unitDown x = 12 * monthly.tax Rule.unitDown (x / 12)
/- The two "second abatement" formulas join the ordinary rule at their ends (within 2 DA): 35,000 and 42,500. -/
#guard monthlyIRG false 34999 = 2069 ∧ monthlyIRG false 35000 = 2070
#guard monthlyIRG false 30000 = 0 ∧ monthlyIRG false 30010 = 6

end DzTax
