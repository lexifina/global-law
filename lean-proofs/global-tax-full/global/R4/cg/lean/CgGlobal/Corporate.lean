import R4Common
import TaxKernel.Global2

/-!
# Congo 2025: corporate income tax (1200) and withholding (generated from `R4/specs/cg.json`)

Code général des impôts tome 1 (local copy `cmp20/world/B08-central-africa-fr/cg/law/cgi_tome1.txt`, edition without post-2021 amendment notes); Journal officiel 2022-2025 issues held locally do not include the LF 2025. Pass 9: the Journal officiel special editions held under `world/B08-central-africa-fr/cg/law/jo/` were read for P1/P2: `jo-2024-15-sp.txt` = LF 2025 (Loi n° 47-2024: art. 122 IS 30 % restored, art. 8 of the excise text new rates, VAT art. 7 items 12 and 22 only), `congo-jo-2023-06-sp.raw.txt` = LF 2024 (Loi n° 39-2023, which modifies and completes loi n° 12-97 on VAT: art. 7 exemptions, art. 22 rates, art. 38 A centimes additionnels). Withholding from CGI tome 1 (`cgi_tome1.txt`) art. 185 ter. Thirteenth pass: CGI tome 2 (Wayback copy of finances.gouv.cg `CGI Tome II.pdf`, capture 2021-08-15, 171 pages), saved as `R4/fetch/p13/cg_cgi_tome2.pdf`.

LF 2025 (Loi n° 47-2024), point 6, restoring the rate in force before the 2020 (COVID) amending finance law: CGI tome 1 art. 122 (new) "Le taux de l'impôt sur les sociétés est fixé à 30%", fractions of profit below 1 000 FCFA disregarded; art. 122 A (new), by derogation: 25 % (microfinance, private education, ...), 28 % (mines and quarries, property), 33 % (foreign legal persons of art. 126 ter ff.).

art. 185 ter (Loi n°5/96 du 2 mars 1996; second sentence Loi n°17-2000 du 30 décembre 2000): persons with neither domicile nor tax residence in Congo "font l'objet d'une retenue à la source dont le taux est fixé à 20%" on income earned in or from Congo, including work or services of any kind performed, supplied or used there; not on loan interest paid to such a person by a borrowing company established in Congo. Thirteenth pass (kernel 2.3.0 grade-C withholding): dividend 20 %: CGI tome 2 (MinFin edition posted 2021) livre III (impôt sur le revenu des valeurs mobilières) art. 1er 1°, art. 3 1° (20 %); LF 2022-2025 held: no change to art. 3 found; interest 0 % to companies: CGI tome 1 art. 185 ter, 2nd sentence (the 20 % retenue 'n'est pas applicable aux intérêts d'emprunts payés à une personne physique ou morale étrangère'); CGI tome 2 livre III art. 1er 7° (IRVM on interest of negotiable bonds only); a foreign lender without an establishment is outside the IS: no tax on loan interest paid to a foreign company (cited 0)
-/

namespace CgGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 3000000
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 300000
def citS0 : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minS0 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS0 minS0 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 2500000
#guard R4.corpTax citS0 minS0 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 0
#guard R4.corpTax citS0 minS0 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 0
#guard R4.corpTax citS0 minS0 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 250000
def citS1 : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 2800, lossFull := -1, lossExcessBp := 10000 }

def minS1 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS1 minS1 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 2800000
#guard R4.corpTax citS1 minS1 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 0
#guard R4.corpTax citS1 minS1 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 0
#guard R4.corpTax citS1 minS1 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 280000
/-- CIT by `company.sector` (kernel 2.5.0 `SectorCorp`): a company whose sector is given and in none of the rules is under the
general rule; an absent sector: `general` (declared here). -/
def citSec : SectorCorp :=
  { general := { regime := citR }, statute := "CGI tome 1 art. 122 as substituted by Loi n° 47-2024 (LF 2025) point 6 (30 %; fraction below 1 000 F disregarded); art. 122 A: 25 % microfinance and private education, 28 % mining/quarrying and property, 33 % foreign legal persons under art. 126 ter", ifAbsent := .general,
    bySector := [{ sectors := ["microfinance", "privateEducation"], rule := { regime := citS0 }, statute := "CGI tome 1 art. 122 A (Loi n° 47-2024, LF 2025): 25 % for microfinance and private education run as a company" },
      { sectors := ["mining", "quarrying", "realEstate"], rule := { regime := citS1 }, statute := "CGI tome 1 art. 122 A (Loi n° 47-2024, LF 2025): 28 % for mines and quarries and property letting" }] }

/-- The minimum tax that goes with the rule `citSec.pick` chose (the rules are told apart by their provision). -/
def citMinFor (st : String) : R4.MinTax :=
  if st == "CGI tome 1 art. 122 A (Loi n° 47-2024, LF 2025): 25 % for microfinance and private education run as a company" then minS0 else if st == "CGI tome 1 art. 122 A (Loi n° 47-2024, LF 2025): 28 % for mines and quarries and property letting" then minS1 else minT

def citSecCharges (g : CanonGlobal) : List Charge :=
  match citSec.pick g with
  | some (r, st) => [R4.citCharge r.regime (citMinFor st) g.company st (step := 1000)]
  | none => []
def citSecT0 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-cg-mf\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000999, \"lossesForward\": 0, \"sector\": \"microfinance\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT0).map (·.due)) == [250000]
def citSecT1 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-cg-min\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000999, \"lossesForward\": 0, \"sector\": \"mining\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT1).map (·.due)) == [280000]
def citSecT2 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-cg-none\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000999, \"lossesForward\": 0}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT2).map (·.due)) == [300000]
def whtR : Wht :=
  { name := "Retenue à la source sur les non-résidents",
    rules := [{ kind := .services, rateBp := 2000, statute := "CGI art. 185 ter (20 %)" },
              { kind := .royalty, rateBp := 2000, statute := "CGI art. 185 ter (20 %, revenus réalisés au Congo)" },
              { kind := .dividend, rateBp := 2000, statute := "CGI tome 2 (MinFin edition posted 2021) livre III (impôt sur le revenu des valeurs mobilières) art. 1er 1°, art. 3 1° (20 %); LF 2022-2025 held: no change to art. 3 found" },
              { kind := .interest, rateBp := 0, toCompany := some true, statute := "CGI tome 1 art. 185 ter, 2nd sentence (the 20 % retenue 'n'est pas applicable aux intérêts d'emprunts payés à une personne physique ou morale étrangère'); CGI tome 2 livre III art. 1er 7° (IRVM on interest of negotiable bonds only); a foreign lender without an establishment is outside the IS: no tax on loan interest paid to a foreign company (cited 0)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 200000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 200000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 200000
#guard whtR.amount { kind := .interest, amount := 1000000, toCompany := true } == 0
def corporate : Family :=
  { name := "1200 Impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else citSecCharges g ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["art. 122 A by company.sector: 'microfinance', 'privateEducation' 25 %; 'mining' (also 'quarrying'), 'realEstate' 28 %; another sector or none given: 30 % (declared); the 33 % rate for foreign legal persons under art. 126 ter is not modelled (not a sector)", "the minimum/turnover-based charges (taxe spéciale sur les sociétés of tome 1 art. 168-170, status in 2025 not established) are not modelled", "CGI tome 1 edition date not established (flagged); LF 2025 point 7 amends the retenue article only for wholesalers' 10 % retenue on rebates", "thirteenth pass: IRVM 20 % on dividends (tome 2 livre III art. 3 1°); loan interest to a foreign company cited 0 (art. 185 ter); to a foreign individual left C (IRPP by return)"] ++ citSec.notes "Impôt sur les sociétés" g ++ citSec.unknown "Impôt sur les sociétés" g

end CgGlobal
