import R4Common
import TaxKernel.Global2

/-!
# Côte d'Ivoire 2025: corporate income tax (1200) and withholding (generated from `R4/specs/ci.json`)

CGI 2025, DGI online edition (`https://cgici.com/V2025/page-N.html`, 711 pages fetched 2026-11-21 at 2 req/s; the dgi.gouv.ci menu entry 'Le code général des Impôts' points to cgici.com), concatenated text `cmp20/global/R4/fetch/ci8/cgi2025_cgici.txt` (+ v2025.tgz, SHA256SUMS). The online pages also show superseded versions of some articles; the version headed by the latest year marker is used.

art. 51 (version 2024): "Le taux de l'impôt est fixé à 25 % pour les personnes morales et les personnes physiques. Ce taux est porté à 30 % pour les entreprises du secteur des télécommunications, des technologies de l'information et de la communication, ainsi que les entreprises du secteur des jeux de hasard. Pour le calcul de l'impôt, le bénéfice net est arrondi à la centaine de francs inférieure." art. 39: "Un impôt minimum forfaitaire frappe les personnes physiques ou morales soumises au régime du bénéfice réel normal. Il est exigible ... a) le montant de l'impôt sur les bénéfices de l'exercice est inférieur à l'impôt minimum forfaitaire ... 1° La cotisation ... est égale à 0,5% du chiffre d'affaires, toutes taxes comprises ... ne peut être inférieure à un minimum de perception de 3 000 000 de francs ... Le maximum de perception de l'impôt minimum forfaitaire est fixé à 35 000 000 de francs."

art. 92 1° a): "Sont passibles de l'impôt sur les bénéfices non commerciaux ... les personnes et sociétés n'ayant pas d'installation professionnelle en Côte d'Ivoire, à raison des sommes qu'elles perçoivent en rémunération des prestations de toute nature fournies ou utilisées en Côte d'Ivoire" (b: including copyright and patent royalties); d): "Le montant net des sommes imposables est déterminé en appliquant aux encaissements bruts une déduction de 20 %"; 2° a): "II est fait application du taux de 25 %". Art. 182: "Le taux de l'impôt est fixé à 15 % pour ... 3-les produits et toutes les sommes imposables à l'impôt sur le revenu des valeurs mobilières non visés par le présent article. Ce taux est porté à 17 % en ce qui concerne les revenus ci-dessus dont le bénéficiaire est une personne physique" (LF 2025 art. 37-1). Art. 193: "1° - Le taux de l'impôt sur le revenu des créances est fixé à 18 %".
-/

namespace CiGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les bénéfices industriels et commerciaux (sociétés)", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 50, fixed := 0, floor := 3000000, cap := 35000000, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 100 == 3000000
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 100 == 5000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 100 == 3000000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 100 == 3000000
def citS0 : CorpRegime :=
  { name := "Impôt sur les bénéfices industriels et commerciaux (sociétés)", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minS0 : R4.MinTax := { bp := 50, fixed := 0, floor := 3000000, cap := 35000000, onAssets := false }
#guard R4.corpTax citS0 minS0 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 100 == 3000270
#guard R4.corpTax citS0 minS0 { profit := 0, turnover := 1000000000, lossesForward := 0 } 100 == 5000000
#guard R4.corpTax citS0 minS0 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 100 == 3000000
#guard R4.corpTax citS0 minS0 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 100 == 3000000
def citS1 : CorpRegime :=
  { name := "Impôt sur les bénéfices industriels et commerciaux (sociétés)", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minS1 : R4.MinTax := { bp := 15, fixed := 0, floor := 3000000, cap := 35000000, onAssets := false }
#guard R4.corpTax citS1 minS1 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 100 == 3000000
#guard R4.corpTax citS1 minS1 { profit := 0, turnover := 1000000000, lossesForward := 0 } 100 == 3000000
#guard R4.corpTax citS1 minS1 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 100 == 3000000
#guard R4.corpTax citS1 minS1 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 100 == 3000000
def citS2 : CorpRegime :=
  { name := "Impôt sur les bénéfices industriels et commerciaux (sociétés)", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minS2 : R4.MinTax := { bp := 10, fixed := 0, floor := 500000, cap := 35000000, onAssets := false }
#guard R4.corpTax citS2 minS2 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 100 == 2500225
#guard R4.corpTax citS2 minS2 { profit := 0, turnover := 1000000000, lossesForward := 0 } 100 == 1000000
#guard R4.corpTax citS2 minS2 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 100 == 500000
#guard R4.corpTax citS2 minS2 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 100 == 500000
def citS3 : CorpRegime :=
  { name := "Impôt sur les bénéfices industriels et commerciaux (sociétés)", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minS3 : R4.MinTax := { bp := 10, fixed := 0, floor := 3000000, cap := 35000000, onAssets := false }
#guard R4.corpTax citS3 minS3 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 100 == 3000000
#guard R4.corpTax citS3 minS3 { profit := 0, turnover := 1000000000, lossesForward := 0 } 100 == 3000000
#guard R4.corpTax citS3 minS3 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 100 == 3000000
#guard R4.corpTax citS3 minS3 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 100 == 3000000
/-- CIT by `company.sector` (kernel 2.5.0 `SectorCorp`): a company whose sector is given and in none of the rules is under the
general rule; an absent sector: `general` (declared here). -/
def citSec : SectorCorp :=
  { general := { regime := citR }, statute := "CGI 2025 art. 51 (25 %; base rounded down to 100 F) and art. 39 (impôt minimum forfaitaire, régime du réel normal: 0,5 % of turnover, minimum 3 000 000 F, maximum 35 000 000 F)", ifAbsent := .general,
    bySector := [{ sectors := ["telecom", "ict", "gambling"], rule := { regime := citS0 }, statute := "CGI 2025 art. 51 al. 2 (30 %: telecommunications, information and communication technologies, games of chance); IMF art. 39 at 0,5 %" },
      { sectors := ["bank", "financialInstitution", "insurer"], rule := { regime := citS1 }, statute := "CGI 2025 art. 51 (25 %) and art. 39 (IMF 0,15 % for banks, financial institutions, insurers and reinsurers; minimum 3 000 000 F, maximum 35 000 000 F)" },
      { sectors := ["serviceStation", "butaneDistribution"], rule := { regime := citS2 }, statute := "CGI 2025 art. 51 (25 %) and art. 39 (IMF 0,10 % for sellers of petroleum products and butane distributors; minimum 500 000 F for service stations and butane distributors, maximum 35 000 000 F)" },
      { sectors := ["petroleum", "utilities"], rule := { regime := citS3 }, statute := "CGI 2025 art. 51 (25 %) and art. 39 (IMF 0,10 % for production, processing and sale of petroleum products and production and distribution of water and electricity; minimum 3 000 000 F, maximum 35 000 000 F)" }] }

/-- The minimum tax that goes with the rule `citSec.pick` chose (the rules are told apart by their provision). -/
def citMinFor (st : String) : R4.MinTax :=
  if st == "CGI 2025 art. 51 al. 2 (30 %: telecommunications, information and communication technologies, games of chance); IMF art. 39 at 0,5 %" then minS0 else if st == "CGI 2025 art. 51 (25 %) and art. 39 (IMF 0,15 % for banks, financial institutions, insurers and reinsurers; minimum 3 000 000 F, maximum 35 000 000 F)" then minS1 else if st == "CGI 2025 art. 51 (25 %) and art. 39 (IMF 0,10 % for sellers of petroleum products and butane distributors; minimum 500 000 F for service stations and butane distributors, maximum 35 000 000 F)" then minS2 else if st == "CGI 2025 art. 51 (25 %) and art. 39 (IMF 0,10 % for production, processing and sale of petroleum products and production and distribution of water and electricity; minimum 3 000 000 F, maximum 35 000 000 F)" then minS3 else minT

def citSecCharges (g : CanonGlobal) : List Charge :=
  match citSec.pick g with
  | some (r, st) => [R4.citCharge r.regime (citMinFor st) g.company st (step := 100)]
  | none => []
def citSecT0 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ci-tel\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 2000000000, \"profit\": 100000050, \"lossesForward\": 0, \"sector\": \"telecom\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT0).map (·.due)) == [30000000]
def citSecT1 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ci-bank\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 2000000000, \"profit\": 0, \"lossesForward\": 0, \"sector\": \"bank\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT1).map (·.due)) == [3000000]
def citSecT2 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ci-stn\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 2000000000, \"profit\": 0, \"lossesForward\": 0, \"sector\": \"serviceStation\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT2).map (·.due)) == [2000000]
def citSecT3 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ci-pet\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 2000000000, \"profit\": 0, \"lossesForward\": 0, \"sector\": \"petroleum\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT3).map (·.due)) == [3000000]
def citSecT4 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ci-none\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 2000000000, \"profit\": 0, \"lossesForward\": 0}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT4).map (·.due)) == [10000000]
def whtR : Wht :=
  { name := "Retenues sur paiements à l'étranger",
    rules := [{ kind := .services, rateBp := 2000, statute := "CGI art. 92 (25 % x 80 % = 20 %)" },
              { kind := .royalty, rateBp := 2000, statute := "CGI art. 92 1° b (25 % x 80 % = 20 %)" },
              { kind := .dividend, rateBp := 1500, statute := "CGI art. 182 3 (IRVM 15 %)" },
              { kind := .interest, rateBp := 1800, statute := "CGI art. 193 1° (IRC 18 %)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 200000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 200000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 180000
def corporate : Family :=
  { name := "1200 Impôt sur les bénéfices industriels et commerciaux (sociétés)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else citSecCharges g ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["the IMF base is turnover including taxes; the model's turnover (before VAT) is used", "by company.sector: art. 51 30 % for 'telecom', 'ict', 'gambling'; art. 39 IMF 0,15 % for 'bank', 'financialInstitution', 'insurer', 0,10 % for 'petroleum' and 'utilities' (water, electricity), 0,10 % with a 500 000 F minimum for 'serviceStation' and 'butaneDistribution'; another sector or none given: 25 % and IMF 0,5 % (declared); the simplified regime (art. 45, 53) is not modelled", "art. 183 bis: IRVM is increased by 25 % for payments to persons in privileged tax regimes (not modelled); listed-share dividends 10 % (art. 183)"] ++ citSec.notes "Impôt sur les bénéfices industriels et commerciaux (sociétés)" g ++ citSec.unknown "Impôt sur les bénéfices industriels et commerciaux (sociétés)" g

end CiGlobal
