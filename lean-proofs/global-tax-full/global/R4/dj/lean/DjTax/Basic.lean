import TaxKernel.World

/-!
# Djibouti: impôt sur les traitements et salaires (ITS), Code général des impôts art. 15 as rewritten by the finance
law for 2022, tax year 2025

Sources: Journal officiel de la République de Djibouti (journalofficiel.dj, "texte-juridique" pages, fetched
2026-11-20; files in `dj/law/`):
* Loi de finances n° 111/AN/20/8ème L (budget initial 2021) art. 6: "L'article 15 du CGI relatif au barème et aux taux
  de l'Impôt sur les Traitements et Salaires est modifié comme suit : Il est appliqué aux rémunérations mensuelles
  imposables, supérieures à 50.000 FD, qui comprennent la valeur des avantages en natures ..., les taux progressifs
  ci-après : ... 2% ... 12% ... 15% ... 20 % ... 30% ... 35% ... Au-delà 2 000 001 : 40%."
* Loi de finances n° 142/AN/21/8ème L (budget initial 2022) art. 7: "L'article 15 relatif au barème et aux taux de
  l'impôt sur les Traitements et Salaires est modifié comme suit : – Pour la fraction de revenu inférieur à 30 000 : 2%
  – ... comprise entre 30 000 à 50 000 : 12% – ... 50 001 à 150 000 : 15% – ... 150 001 à 300 000 : 22% – ... 300 001
  à 600 000 : 25% – ... 600 001 à 1000 000 : 30% – ... 1 000 001 à 2 000 000 : 35% – Au-delà de 2 000 001 : 45%."
  The 2022 text no longer contains the 2021 sentence restricting the barème to monthly pay "supérieures à 50.000 FD"
  (FINDINGS F2: model default = the literal 2022 article; input `itsThreshold50000: true` applies the 2021 sentence).
* Finance laws checked for later changes to art. 15: LFR 2022 (169/AN/22), LF 2023 (181/AN/22), LFR 2023 (45/AN/23),
  LF 2024 (64/AN/23: only art. 287, the payment date), LFR 2024 (129/AN/24), LF 2025 (150/AN/24: arts. 73, 90-G, 284,
  176-2, 483, 505, 508, 509, 166, 430, 517), LF 2026 (203/AN/25): none touches art. 15.
The CGI itself (arts. 1-14: taxable remuneration, deductions, exemptions) was not reached: no deduction is modelled;
CNSS employee contributions: W5 pattern A (2026-11-20): 4 % retraite + 2 % soins = 6 % of all remuneration, reported
and not deducted (the CGI deductions, arts. 1-14, were not reached). Source: the CNSS page "Déclaration et versement
des cotisations" (cnss.dj, published 04/12/2016, Internet Archive capture 2024-07-13; official secondary: the laws
and decrees fixing the rates were not reached): "Les cotisations sociales représentent 21.7% des rémunérations totales
versées. Dont : 5.5 % pour le régime des prestations familiales, 8.2 % pour le régime de soins et accident de travail,
8 % pour le régime de retraite ... Les cotisations du régime de retraite sont à la charge conjointe de l'employeur (4%)
et du salarié (4%). Pour le régime des soins, les cotisations sont respectivement 5% pour l'employeur et de 2% pour le
salarié"; "assises sur l'ensemble des rémunérations"; no ceiling. The same page also says the soins contributions are
"à la charge exclusive de l'employeur" (FINDINGS W5A-1: the specific 5 % / 2 % sentence is followed). The plancher of
20 000 FD a month for professional employers is not applied. Input `cnssEmployee`, when given, replaces the statutory
amount as before; `"w5Contrib": false` restores the pre-W5 model.
-/

namespace DjTax
open TaxKernel

/-- CGI art. 15 (LF 2022 art. 7), monthly. -/
def sched : Schedule := Schedule.ofList
  [(0, 200), (30000, 1200), (50000, 1500), (150000, 2200), (300000, 2500), (600000, 3000), (1000000, 3500), (2000000, 4500)]
def threshold2021 : Int := 50000

/-- W5 pattern A: CNSS salarié 4 % retraite + 2 % soins (CNSS page, 2016), all remuneration, no ceiling. -/
def cnssRetraiteBp : Int := 400
def cnssSoinsBp : Int := 200
def cnssWorker (w : Int) : Int := divR .down (pos w * (cnssRetraiteBp + cnssSoinsBp)) 10000
/- The page's 21,7 % = 5,5 + 8,2 + 8; retraite 8 = 4 + 4. -/
#guard 550 + 820 + 800 = 2170 ∧ 2 * cnssRetraiteBp = 800 ∧ cnssWorker 1200000 = 72000

def itsMonth (thr : Bool) (m : Int) : Int :=
  if m ≤ 0 then 0 else if thr && m ≤ threshold2021 then 0 else sched.tax Rule.unitHalfUp m

def out (c : Canon) : Out :=
  let thr := (c.bool? "itsThreshold50000").getD false
  let socIn := (c.int? "cnssEmployee").getD 0
  let w5 := (c.bool? "w5Contrib").getD true
  let useStat := w5 && socIn == 0
  let soc := if useStat then sumInts (c.adults.map fun a => cnssWorker a.wages) else socIn
  let tax := sumInts (c.adults.map fun a => perPeriod 12 (itsMonth thr) (pos a.wages))
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business profits not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["capital income, rents and gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "DJ" "DJF" tax (employeeSocial := soc)
    (detail := [Out.d "its" tax, Out.d "threshold2021Reading" (if thr then 1 else 0),
      Out.dStr "note" "ITS monthly on gross pay (CGI art. 15, LF 2022 art. 7): 2/12/15/22/25/30/35/45 %; CGI deductions (arts. 1-14) not reached"])
    (unsupported := unsup ++ ["CGI arts. 1-14 (taxable base, deductions, exemptions) not reached: ITS applied to the whole gross wage",
      "wages paid evenly over 12 months (ITS is monthly)", if useStat then "CNSS employee 6 % (CNSS page 2016, official secondary) reported, not deducted (CGI not reached); 20 000 FD plancher not applied" else "CNSS employee contribution: rate not reached (input reported, not deducted)"])

def country : Country := { code := "DJ", name := "Djibouti (ITS)", currency := "DJF", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: 200 000 FD a month: 600 + 2 400 + 15 000 + 11 000 = 29 000. -/
#guard itsMonth false 200000 = 29000
/- The 2021 sentence would make 50 000 a month tax-free and 50 001 pay 3 000: a 3 000 FD notch. -/
#guard itsMonth true 50000 = 0 ∧ itsMonth true 50001 = 3000 ∧ itsMonth false 50000 = 3000

/- No annual reconciliation (the tax is on each month's pay, CGI art. 15): 2 400 000 FD paid evenly costs 12 x 29 000
   = 348 000; paid in one month it costs 776 000. -/
#guard 12 * itsMonth false 200000 = 348000 ∧ itsMonth false 2400000 = 776000

end DjTax
