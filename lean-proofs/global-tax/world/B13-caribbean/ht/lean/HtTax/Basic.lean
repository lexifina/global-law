import TaxKernel.World

/-!
# Haiti: impôt sur le revenu of a resident employee and the CAS levy, under the Code Fiscal of 30 September 2026
# (fiscal year 2026-27: the 2024-25 text was not reached; access B)

Source: Décret remplaçant le Décret du 19 décembre 2022 portant Code Fiscal, Le Moniteur Spécial N° 48-A du 30
septembre 2026 (DGI, dgi.gouv.ht, `Code-Fiscal_dgi_2026-10.pdf`, answering only from the laptop; text layer checked):
* art. 540: "Le présent Décret entre en vigueur au 1er octobre 2026"; the Haitian fiscal year runs October-September.
  The Décret du 19 décembre 2022 portant Code Fiscal, which governed the fiscal year 2024-25 (the one holding most of
  2025), was not found on dgi.gouv.ht (WordPress media search: only the 2026 Code); the model is for 2026-27 and says so.
* art. 3 (personnes physiques) 3.: "Les revenus d'un couple sont déclarés séparément par chaque conjoint".
* art. 98: the base for wages is "le montant brut des salaires ... et de tous les avantages"; art. 100: monthly
  withholding of one twelfth of the annual tax.
* art. 126 1. c.: deductible from global income "les prélèvements légalement effectués sur les salaires autres que
  l'impôt sur le revenu".
* art. 132: "a. pour la fraction du revenu allant de 1 Gourde à 360 000 Gourdes: 0% ; b. ... de 360 001 Gourdes à
  540 000 Gourdes: 12 % ; c. ... de 540 001 Gourdes à 1 080 000 Gourdes: 18 % ; d. ... de 1 080 001 Gourdes à 2 160 000
  Gourdes: 25%; e. ... supérieure à 2 160 000 Gourdes: 30%".
* art. 243 1. b.: the Caisse d'Assistance Sociale levy, "un prélèvement d'un pour cent (1 %), chaque mois, sur les
  salaires des employés publics et non publics" (journaliers, stagiaires, vacataires exempt).
The ONA old-age contribution (not in the Code) was not reached: unsupported.
-/

namespace HtTax
open TaxKernel

/-- art. 132. -/
def sched : Schedule := Schedule.ofList [(0, 0), (360000, 1200), (540000, 1800), (1080000, 2500), (2160000, 3000)]

/-- art. 243 1. b.: 1 % of monthly salaries. -/
def casMonth (m : Int) : Int := divR .down (100 * pos m) 10000

structure Person where
  cas : Int
  base : Int
  tax : Int

def person (a : Adult) : Person :=
  let w := pos a.wages
  let cas := perPeriod 12 casMonth w
  let base := pos (w + pos a.selfEmployment - cas)
  { cas := cas, base := base, tax := sched.tax Rule.unitDown base }

def out (c : Canon) : Out :=
  let ps := c.adults.map person
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["capital and property income (categorical rules, withholding) not modelled"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["BIC/BNC rules (forfait, art. 62-65) not modelled: self-employment added to global income"] else [])
  Out.make c "HT" "HTG" (sumInts (ps.map (·.tax))) (surtaxes := [("caisseAssistanceSociale", sumInts (ps.map (·.cas)))])
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.base))),
      Out.dStr "year" "fiscal year 2026-27 (Code Fiscal in force 1 Oct 2026); the 2024-25 law (Decret du 19 decembre 2022) was not reached",
      Out.dStr "note" "separate declaration (art. 3); art. 132 0/12/18/25/30 %; CAS 1 % (art. 243) deducted (art. 126 1. c.)"])
    (unsupported := unsup ++ ["model year 2026-27, not 2025", "ONA old-age contribution not reached",
      "art. 126 deductions (rent, mortgage interest, insurance, school fees) need inputs"])

def country : Country := { code := "HT", name := "Haiti (Code Fiscal 2026, fiscal year 2026-27)", currency := "HTG", year := "2026-27", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard sched.tax Rule.unitDown 540000 = 21600
#guard sched.tax Rule.unitDown 1080000 = 118800
#guard sched.tax Rule.unitDown 2160000 = 388800

end HtTax
