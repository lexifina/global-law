import TaxKernel.World

/-!
# Mauritania: impôt sur les traitements et salaires (ITS), Code général des impôts, 2025

Statute: the DGI's consolidated **CGI 2023** (French, Word export of 17 February 2023), archived official copy
`web.archive.org/web/20230526234015id_/http://impots.gov.mr/DGI/files/CGI-Fr-2023.pdf` (sha256 2972be620009…), checked
against the DGI's CGI of 10 March 2020 (`impots.gov.mr/DGI/files/Mauritanie-CGI-2020-francais.pdf`, sha256
53ebf34e4d5a…), same wording of arts. 110 and 114 (1)-(5) (art. 114 tagged "(LFI2022)", which added (6)).
* Art. 110 1) c): "un montant de six mille (6.000) Ouguiya par mois de la rémunération" not taxable;
  b) other allowances up to 1,000 a month (not in the household).
* Art. 113 2) a): "les retenues obligatoires opérées pour la constitution de pensions ou de retraites et les cotisations
  de sécurité sociale" deducted.
* W5 pattern A (2026-11-20): CNSS worker 1 % of pay up to the ceiling, deducted (art. 113 2) a)). Source: the CNSS page
  "Recouvrement des cotisations" (cnss.mr, Internet Archive capture 2021-08-12; same text on its 2016 "cotisation" page;
  official secondary: loi 67-039 and its rate décrets were not reached; `mr/law/w5/`): "Les cotisations dues à la CNSS
  sont assises sur l'ensemble des rémunérations ... dans la limite d'un plafond actuellement à 70.000 UM par mois et par
  travailleur Taux de cotisation 14 % pour la sécurité sociale dont 1% est supporté par le travailleur et 13 % sont à la
  charge de l'employeur". The page states the ceiling in old ouguiya; the model works in new ouguiya (MRU, the 2018
  redenomination at 10 old for 1 new, reading; the redenomination law was not reached): 7 000 MRU a month. Whether the
  ceiling was revised after 2016 was not found. Not modelled: the CNAM health-insurance employee contribution
  (ordonnance 2005-006 and its décret not reached). `"w5Contrib": false` restores the pre-W5 model.
* Art. 114 1)-2): monthly taxable pay ≤ 9,000: 15 %; 9,000–21,000: 25 % ("I = (R.I. x 0.25) - 900"); above 21,000:
  40 % ("I = (R.I. x 0.40) - 4.050"); 3) "la base d'imposition est arrondie à la dizaine d'Ouguiya inférieure".
* Art. 109 2): pensions taxed under the same tariff (the 6,000 exemption of art. 110 1) is for pay only).
2025 check: the finance law for 2025 (`finances.gov.mr/sites/default/files/2025-01/قانون المالية لسنة 2025.pdf`) amends
CGI arts. 159, 160, 168, 175, 297, 309-405 and the amending finance law 2025 arts. 227-266, 370, 407-411: none of
arts. 109-114. The 2024 finance laws' text layer is unreadable (fonts without Unicode map) and the DGI's CGI 2024 PDF
is served truncated (no trailer, 261,908,483 bytes; the Wayback copy breaks at 79.5 MB): a 2024 change to the ITS
cannot be excluded (access B). Unit: individual, monthly withholding (12 equal months).
-/

namespace MrTax
open TaxKernel

/-- Art. 114 1): monthly bands (bp). -/
def sched : Schedule := Schedule.ofList [(0, 1500), (9000, 2500), (21000, 4000)]

def exemptMonthly : Int := 6000   -- art. 110 1) c)

/-- Art. 114 2)-3): tax on a monthly taxable pay rounded down to 10 ouguiya. -/
def monthlyTax (ri : Int) : Int := sched.tax Rule.unitDown (toMultiple .down 10 (pos ri))

/-- Annual ITS on wages paid in 12 equal months. -/
def wageTax (annual : Int) : Int := perPeriod 12 (fun m => monthlyTax (m - exemptMonthly)) (pos annual)

def pensionTax (annual : Int) : Int := perPeriod 12 monthlyTax (pos annual)

/-- W5 pattern A: CNSS worker 1 % of the month's pay up to 70 000 UM = 7 000 MRU (CNSS page). -/
def cnssWorkerBp : Int := 100
def cnssPlafondMonth : Int := 70000 / 10
def cnssMonth (m : Int) : Int := divR .down (min (pos m) cnssPlafondMonth * cnssWorkerBp) BP
/-- Art. 113 2) a): the month's taxable pay is net of the worker's CNSS contribution. -/
def wageTaxNet (annual : Int) : Int := perPeriod 12 (fun m => monthlyTax (m - cnssMonth m - exemptMonthly)) (pos annual)
def cnssYear (annual : Int) : Int := perPeriod 12 cnssMonth (pos annual)
/- CNSS page: 14 % = 1 % worker + 13 % employer; at the ceiling the worker pays 70 MRU a month. -/
#guard cnssWorkerBp + 1300 = 1400 ∧ cnssMonth 7000 = 70 ∧ cnssMonth 50000 = 70 ∧ cnssMonth 5000 = 50

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let it := sumInts (c.adults.map fun a => (if w5 then wageTaxNet a.wages else wageTax a.wages) + pensionTax a.pension)
  let es := if w5 then sumInts (c.adults.map fun a => cnssYear a.wages) else 0
  Out.make c "MR" "MRU" it (employeeSocial := es)
    (detail := [Out.d "taxableIncome" (sumInts (c.adults.map fun a => pos (a.wages - 12 * exemptMonthly) + pos a.pension))])
    (unsupported := [if w5 then "CNSS worker 1 % up to 7 000 MRU a month (CNSS page, official secondary; ceiling printed in old ouguiya) deducted; CNAM employee contribution not modelled (not reached)" else "CNSS / CNAM employee contributions not modelled and not deducted (art. 113 2) a))",
      "self-employment (IBAPP/BIC), rents (IRF) and capital income (IRCM) not modelled",
      "2024 finance laws not verified (text layer unreadable); CGI 2024 PDF truncated on the DGI server"])

def country : Country :=
  { code := "MR", name := "Mauritania (CGI, ITS)", currency := "MRU", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Art. 114 2) prints the tariff as formulas: R.I. × 0.15 up to 9,000; R.I. × 0.25 − 900 to 21,000; R.I. × 0.40 − 4,050
   above. The bands reproduce each formula at and between the limits. -/
#guard monthlyTax 9000 = 1350 ∧ monthlyTax 15000 = 15000 * 25 / 100 - 900 ∧ monthlyTax 21000 = 4350
#guard monthlyTax 30000 = 30000 * 40 / 100 - 4050 ∧ monthlyTax 9005 = 1350
#guard (List.range 400).all fun k => let x : Int := 100 * k
  monthlyTax x = (if x ≤ 9000 then x * 15 / 100 else if x ≤ 21000 then x * 25 / 100 - 900 else x * 40 / 100 - 4050)

/- Art. 114 is a monthly withholding with no annual reconciliation in arts. 109-115: 180,000 paid as 6 months of 30,000
   costs 33,300; paid as 12 months of 15,000 it costs 16,200 (FINDINGS F2). -/
#guard 6 * monthlyTax (30000 - exemptMonthly) = 33300 ∧ 12 * monthlyTax (15000 - exemptMonthly) = 16200

end MrTax
