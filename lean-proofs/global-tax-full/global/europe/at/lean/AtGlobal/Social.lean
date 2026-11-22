import AtGlobal.Pit

/-!
# AT 2025: employer social contributions (2200) and payroll taxes (3000)

Source: RIS Fassung vom 01.07.2025: ASVG (the 1.x model's `asvg_2025-07-01`), FLAG 1967 (`at/law/flag_2025-07-01.html`); Höchstbeitragsgrundlage from the 1.x model's parameters (ASVG § 45, § 54).
* ASVG § 51: "beläuft sich der Beitragsteil des/der Versicherten auf 3,87%, des Dienstgebers/der Dienstgeberin auf 3,78%"; "in der Pensionsversicherung ... des Dienstgebers auf 12,55%"
* AtTax.Params: Höchstbeitragsgrundlage "6 450 € per month"; Sonderzahlungen to "60fachen" daily amount (12 900 €): annual 12 × 6 450 + 12 900 = 90 300 €
* FLAG § 41 (5): "Ab dem Kalenderjahr 2025 beträgt der Beitrag 3,7 v.H. der Beitragsgrundlage"

## FT review (2026-11-21, third pass): the other employer contributions and the Kommunalsteuer
RIS Fassung vom 01.07.2025 (`at/law/ampfg_*`, `iesg_*`, `iesg_zuschlagsvo_*`, `wbfbg_*`; ASVG the 1.x model's
`germanic/at/law/asvg_2025-07-01.txt`; KommStG 1993 fetched 2026-11-21, Gesetzesnummer 10004841, `at/law/kommstg1993_2025-07-01.html`;
the `kommstg_2025-07-01.*` saved earlier is another act):
* **ASVG § 51 (1) Z 2**: "in der Unfallversicherung 1,1% der allgemeinen Beitragsgrundlage"; (3): borne "zur Gänze vom
  Dienstgeber"; **(6)**: for persons "die das 60. Lebensjahr vollendet haben" paid "aus Mitteln der Unfallversicherung".
* **AMPFG § 2 (1)**: "Der Arbeitslosenversicherungsbeitrag beträgt für Lehrlinge 2,3 vH und für die übrigen Versicherten
  5,9 vH der Beitragsgrundlage" (up to the Höchstbeitragsgrundlage; (2) Sonderzahlungen too); **(3)** "zu gleichen Teilen".
* **IESG § 12 (1) Z 4** with the **IESG-ZuschlagsVO**: "Der Zuschlag … wird ab dem 1. Jänner 2022 mit 0,1 vH festgesetzt" (Dienstgeber).
* **WBFBG § 3 (1) a**: "5 v. T. der allgemeinen Beitragsgrundlage in der Krankenversicherung"; **(2)**: the employer pays "einen
  gleich hohen Beitrag". The allgemeine Beitragsgrundlage excludes Sonderzahlungen: the base is 12/14 of the year's pay
  (14 equal salaries, as the model's ceiling), at most 12 x 6 450 = 77 400 €.
* **KommStG 1993 § 9**: "Die Steuer beträgt 3% der Bemessungsgrundlage" (§ 5: the wages paid). The allowance of § 9 second
  sentence (1 095 € where the employer's monthly wages do not exceed 1 460 €) depends on the employer's whole payroll: listed.

* **ASVG § 5 (2)** with Anm. 1 "gemäß BGBl. II Nr. 417/2024 für 2025: 551,1 €" (the 1.x model's reading, `AtTax.Params.geringfuegig`):
  an employment is geringfügig where the monthly pay does not exceed 551,10 €; **§ 53a (1)**: "Der Dienstgeber hat für alle bei
  ihm nach § 5 Abs. 2 beschäftigten Personen einen Beitrag zur Unfallversicherung in der Höhe von 1,1% der allgemeinen
  Beitragsgrundlage zu leisten" (no KV, PV, AV, IESG, WBF). Read on the year's pay in 14 equal salaries: at most 14 x 551,10 €.
  The Dienstgeberabgabe (where an employer's marginal wages exceed 1,5 times the limit) depends on the employer's payroll: listed.
-/

namespace AtGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Krankenversicherung (Dienstgeber)", sched := Schedule.flat 378, ceiling := 90300 }
def c1 : Contribution := { name := "Pensionsversicherung (Dienstgeber)", sched := Schedule.flat 1255, ceiling := 90300 }
def c2 : Contribution := { name := "Dienstgeberbeitrag zum FLAF", sched := Schedule.flat 370, ceiling := -1 }

def c3 : Contribution := { name := "Arbeitslosenversicherung (Dienstgeber)", sched := Schedule.flat 295, ceiling := 90300 }
def c4 : Contribution := { name := "IESG-Zuschlag", sched := Schedule.flat 10, ceiling := 90300 }
def c5 : Contribution := { name := "Kommunalsteuer", sched := Schedule.flat 300, ceiling := -1 }
def cUV : Contribution := { name := "Unfallversicherung (Dienstgeber)", sched := Schedule.flat 110, ceiling := 90300 }
def cWBF : Contribution := { name := "Wohnbauförderungsbeitrag (Dienstgeber)", sched := Schedule.flat 50, ceiling := 77400 }
/-- WBFBG § 3: on the allgemeine Beitragsgrundlage (no Sonderzahlungen): 12/14 of the year's pay. -/
def regularPay (w : Int) : Int := w * 12 / 14

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "ASVG § 51 (1) Z 1 lit. b, (3): Dienstgeber 3,78 %"),
   (c1, .sscEmployer, "ASVG § 51 (3) Z 2: Dienstgeber 12,55 %"),
   (c2, .payroll, "FLAG 1967 § 41 (5): ab 2025 3,7 v.H."),
   (c3, .sscEmployer, "AMPFG § 2 (1), (3): 5,9 vH, Dienstgeber die Hälfte"),
   (c4, .sscEmployer, "IESG § 12 (1) Z 4; IESG-ZuschlagsVO: 0,1 vH"),
   (c5, .payroll, "KommStG 1993 § 9: 3% der Bemessungsgrundlage (§ 5)")]

/-- On the household's wages: each adult, each contribution (borne by the employer). -/
def householdCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    if a.wages * 100 ≤ 14 * 55110 then
      ((contribs.filter (fun (_, o, _) => o == Oecd.payroll)).map fun (c, o, st) =>
        charge o c.name a.wages id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)
          (bearer := .employer) (statute := st))
      ++ [charge .sscEmployer cUV.name a.wages id (fun x => cUV.amount x) (event := s!"adult {i + 1}") (level := .social)
          (bearer := .employer) (statute := "ASVG § 5 (2) (551,10 € a month in 2025), § 53a (1): Unfallversicherung 1,1% (geringfügig Beschäftigte)")]
    else
    (contribs.map fun (c, o, st) =>
      charge o c.name a.wages id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)
        (bearer := .employer) (statute := st))
    ++ (if a.age < 60 then [charge .sscEmployer cUV.name a.wages id (fun x => cUV.amount x) (event := s!"adult {i + 1}") (level := .social)
          (bearer := .employer) (statute := "ASVG § 51 (1) Z 2, (3): 1,1% (Dienstgeber zur Gänze); (6): from age 60 paid by the Unfallversicherung")] else [])
    ++ [charge .sscEmployer cWBF.name a.wages regularPay (fun x => cWBF.amount x) (event := s!"adult {i + 1}") (level := .social)
          (bearer := .employer) (statute := "WBFBG § 3 (1) a, (2): 5 v. T. der allgemeinen Beitragsgrundlage (12/14 of the pay, at most 77 400 €)")]

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
  [{ name := "2200/3000 employer contributions", covers := [.payroll, .sscEmployer],
     run := fun args g prev =>
       householdCharges g ++ companyCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["AT 2200/3000: RIS Fassung vom 01.07.2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .household then ["Mitarbeitervorsorge (1,53 %), DZ (Kammerumlage 2) and U-Bahn-Steuer not modelled; apprentices' AV 2,3 % and the AV reductions for older workers not applied; the KommStG § 9 allowance (employer's monthly wages up to 1 460 €) not applied; annual ceiling assumes 14 equal salaries"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])
  ++ (if g.household.adults.any (fun a => 0 < a.wages && a.wages * 100 ≤ 14 * 55110) then ["pay up to 14 x 551,10 € read as one geringfügige Beschäftigung (ASVG § 5 (2)): employer UV 1,1 % only (§ 53a (1)); the Dienstgeberabgabe (employer's marginal payroll above 1,5 x the limit) not applied"] else [])

#guard c0.amount 50000 == 1890
#guard c0.amount 200000 == 3413
#guard c1.amount 50000 == 6275
#guard c1.amount 200000 == 11332
#guard c2.amount 50000 == 1850
#guard c2.amount 200000 == 7400
#guard c3.amount 50000 == 1475
#guard c3.amount 200000 == 2663
#guard c4.amount 50000 == 50
#guard c5.amount 50000 == 1500
#guard cUV.amount 50000 == 550
#guard cWBF.amount (regularPay 70000) == 300
#guard cWBF.amount (regularPay 200000) == 387

end AtGlobal.Social
