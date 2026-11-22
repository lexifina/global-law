import LuGlobal.Pit

/-!
# LU 2025: employer social contributions (2200) and payroll taxes (3000)

Source: Code de la sécurité sociale, recueil « La Sécurité sociale - 2025 » (IGSS, coordinated text with the arrêtés of 2024, `cmp20/germanic/lu/law/css_20250101.txt`, kept by the 1.x model) and the 1.x model's CCSS maximum cotisable (`LuTax.Params` maxCot1C/maxCot2C).
* CSS art. 238 (5) / 1.x: "taux de cotisation global est fixé à vingt-quatre pour cent"; art. 240, 1): la charge des cotisations incombe "par parts égales aux assurés et aux employeurs" (after the State's third, art. 239): 8 % employer
* CSS art. 29 note 4): "Le taux de cotisation pour le financement des soins de santé est fixé à 5,60%"; art. 29 al. 2: "le taux de cotisation est majoré de 0,5 pour cent" (prestations en espèces); art. 32: "par parts égales aux assurés et aux employeurs"
* CSS art. 141 note 3): "A 18.12.2024,1er : Le taux de cotisation unique, arrêté pour l'exercice 2025 par le conseil d'administration de l'Association d'assurance accident à 0,70 pourcent, est approuvé."; art. 150: "La charge des cotisations incombe à l'employeur"
* maximum cotisable (art. 241 (3), le quintuple du SSM; CCSS): 13 188,96 € a month Jan-Apr, 13 518,68 € May-Dec: annual 4 × 13 188,96 + 8 × 13 518,68 = 160 905 €

FT review 5 (2026-11-21), Dataset round 3 R3-2:
* **Mutualité des employeurs** (CSS art. 52-56, recueil 2025; Statuts de la Mutualité in the same recueil): compulsory
  affiliation of every employer (art. 53), contributions on the indemnité pécuniaire base of art. 34-36 (art. 55 (4);
  Statuts art. 3: the health cash-benefit base, so the same maximum cotisable), in exchange for the reimbursement of the
  pay the employer must continue during a worker's sickness (art. 52, Code du travail L. 121-6): a compulsory payment to
  a social security institution conferring a contingent sickness benefit: OECD **2200** (Interpretative Guide 2026 §40-41,
  "accident, injury and sickness benefits"; §45 excludes only the pay the employer itself continues). Rate by class of
  financial absenteeism (Statuts art. 4-5); the employer's record is not in the entity: **class 2**, the class Statuts
  art. 6 assigns to an affiliate without twelve months of observation ("Tout nouvel affilié obligatoire ou volontaire
  cotise dans la classe 2"). 2025 rate **0,99 %** (CCSS, "Taux de cotisation au 01.01.2025", avis of 14.03.2025, `lu/law/
  ccss_20250314_avis_80.pdf`: classes 0,07 / 0,99 / 1,48 / 2,64 %, after the L. 26.7.23 art. 1er 2° reductions).
* **Santé au travail (STM)**: Code du travail L. 322-1 2.: each employer chooses an in-house service, an inter-enterprise
  association or the national service; L. 323-1 (5): the STM's cost "est couvert par une cotisation à charge de tous les
  employeurs optant pour le recours à ce service", a rate set on its budget: a requited payment for a service the payer
  can avoid by another option: not a tax (Guide §1, §12). Not modelled (OECD Taxing Wages 2025 lists it, 0,14 %, among
  the contributions within the government sector: recorded, not followed).
-/

namespace LuGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Assurance pension (part patronale)", sched := Schedule.flat 800, ceiling := 160905 }
def c1 : Contribution := { name := "Assurance maladie - soins de santé (part patronale)", sched := Schedule.flat 280, ceiling := 160905 }
def c2 : Contribution := { name := "Assurance maladie - prestations en espèces (part patronale)", sched := Schedule.flat 25, ceiling := 160905 }
def c3 : Contribution := { name := "Assurance accident", sched := Schedule.flat 70, ceiling := 160905 }
/-- Mutualité des employeurs, class 2 (Statuts art. 6), 2025: 0,99 % (CCSS, taux au 01.01.2025). -/
def c4 : Contribution := { name := "Mutualité des employeurs (classe 2)", sched := Schedule.flat 99, ceiling := 160905 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "CSS art. 238 (taux global 24 %), art. 239 (un tiers à charge de l'État), art. 240, 1) (parts égales assurés et employeurs): 8 %; art. 241 (3): maximum cotisable le quintuple du SSM"),
   (c1, .sscEmployer, "CSS art. 29 note 4) (5,60 %), art. 32 (parts égales): 2,80 %"),
   (c2, .sscEmployer, "CSS art. 29 al. 2 (majoré de 0,5 pour cent), art. 32 (parts égales): 0,25 %"),
   (c3, .sscEmployer, "CSS art. 141 note 3) (A 18.12.2024: taux de cotisation unique 2025 0,70 pourcent), art. 150 (charge de l'employeur)"),
   (c4, .sscEmployer, "CSS art. 52-55 (Mutualité des employeurs; assiette art. 34-36), Statuts art. 4-6 (classe 2: nouvel affilié); CCSS taux au 01.01.2025: classe 2 0,99 %")]

/-- On the household's wages: each adult, each contribution (borne by the employer). -/
def householdCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    contribs.map fun (c, o, st) =>
      charge o c.name a.wages id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)
        (bearer := .employer) (statute := st)

/-- On a company's payroll, spread evenly over its employees (ceilings per employee). -/
def companyCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.payroll ≤ 0 then [] else
  let n : Int := max 1 (g.company.employees : Int)
  let avg := g.company.payroll / n
  contribs.map fun (c, o, st) =>
    charge o c.name g.company.payroll id (fun _ => n * c.amount avg) (event := "payroll") (level := .social)
      (statute := st)

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "2200/3000 employer contributions", covers := [.sscEmployer],
     run := fun args g prev =>
       householdCharges g ++ companyCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["LU 2200/3000: CSS recueil 2025 (arrêtés of December 2024)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["Mutualité des employeurs at class 2 (Statuts art. 6; the employer's absenteeism class 0,07 / 1,48 / 2,64 % not known), santé au travail (STM: a fee for a service the employer chooses, not a tax, Code du travail L. 322-1, L. 323-1 (5)) and the ceiling's application to the accident contribution (taken at the same maximum) not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 4000
#guard c0.amount 200000 == 12872
#guard c1.amount 50000 == 1400
#guard c1.amount 200000 == 4505
#guard c2.amount 50000 == 125
#guard c2.amount 200000 == 402
#guard c3.amount 50000 == 350
#guard c3.amount 200000 == 1126
#guard c4.amount 50000 == 495
#guard c4.amount 200000 == 1592

end LuGlobal.Social
