import R4Common
import TaxKernel.Global2

/-!
# Guinea 2025: corporate income tax (1200) and withholding (generated from `R4/specs/gn.json`)

Sources: CGI 2021 (`cmp20/world/B07-west-africa-fr-pt/gn/src/cgi2021.txt`), Loi 2024-23 (LF) OCR.

art. 229: "I. ... toute fraction du bénéfice imposable inférieure à mille (1 000) francs guinéens est négligée. II. Les taux de l'Impôt sur les Sociétés sont fixés comme suit : 1. trente-cinq pourcent (35%) ... téléphonie, les banques et assurances et ... produits pétroliers ; 2. trente pourcent (30%) ... titre d'exploitation minière ; 3. vingt-cinq pourcent (25%) pour les autres personnes morales." CGI 2021 (Loi L/2021/32) edition; the 2025 finance law held (Loi 2024-23) is budgetary and LF 2022-2024 were not checked: grade B.

art. 187 I: "les revenus de capitaux mobiliers de source Guinéenne payés en Guinée et perçus par les personnes ayant leur domicile fiscal ou leur siège de direction effective hors de Guinée, font l'objet d'une retenue à la source égale à 15% du montant brut des revenus distribués"; III: "La même retenue s'applique également aux produits de placements à revenus fixes"; VI: "libératoire". Art. 198 I-III: a withholding on payments by a debtor established in Guinea to a person without tax residence in Guinea for services taxable in Guinea under the VAT territoriality rules; "Le taux de la retenue est fixé à quinze pourcent (15%) du montant brut des sommes versées" (excluding VAT). Twelfth pass (kernel 2.3.0 grade-C withholding): royalty 15 %: CGI 2021 art. 198 I-III with art. 356 Ter I ('une prestation de services peut consister notamment en l'utilisation ou en la cession d'un bien incorporel'): 15 %
-/

namespace GnGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 2500000
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 250000
def citS0 : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 3500, lossFull := -1, lossExcessBp := 10000 }

def minS0 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS0 minS0 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 3500000
#guard R4.corpTax citS0 minS0 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 0
#guard R4.corpTax citS0 minS0 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 0
#guard R4.corpTax citS0 minS0 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 350000
def citS1 : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minS1 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS1 minS1 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 3000000
#guard R4.corpTax citS1 minS1 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 0
#guard R4.corpTax citS1 minS1 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 0
#guard R4.corpTax citS1 minS1 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 300000
/-- CIT by `company.sector` (kernel 2.5.0 `SectorCorp`): a company whose sector is given and in none of the rules is under the
general rule; an absent sector: `general` (declared here). -/
def citSec : SectorCorp :=
  { general := { regime := citR }, statute := "CGI 2021 art. 229 II 3 (25 % for other companies; base rounded down to 1 000 GNF)", ifAbsent := .general,
    bySector := [{ sectors := ["telecom", "bank", "insurer", "petroleum"], rule := { regime := citS0 }, statute := "CGI 2021 art. 229 II 1 (35 %: telephony companies, banks and insurers, importers, storers and distributors of petroleum products)" },
      { sectors := ["mining"], rule := { regime := citS1 }, statute := "CGI 2021 art. 229 II 2 (30 %: holders of a mining title)" }] }

/-- The minimum tax that goes with the rule `citSec.pick` chose (the rules are told apart by their provision). -/
def citMinFor (st : String) : R4.MinTax :=
  if st == "CGI 2021 art. 229 II 1 (35 %: telephony companies, banks and insurers, importers, storers and distributors of petroleum products)" then minS0 else if st == "CGI 2021 art. 229 II 2 (30 %: holders of a mining title)" then minS1 else minT

def citSecCharges (g : CanonGlobal) : List Charge :=
  match citSec.pick g with
  | some (r, st) => [R4.citCharge r.regime (citMinFor st) g.company st (step := 1000)]
  | none => []
def citSecT0 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-gn-tel\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000500, \"lossesForward\": 0, \"sector\": \"telecom\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT0).map (·.due)) == [350000]
def citSecT1 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-gn-min\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000500, \"lossesForward\": 0, \"sector\": [\"mining\"]}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT1).map (·.due)) == [300000]
def citSecT2 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-gn-none\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000500, \"lossesForward\": 0}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT2).map (·.due)) == [250000]
def whtR : Wht :=
  { name := "Retenues à la source (non-résidents)",
    rules := [{ kind := .dividend, rateBp := 1500, statute := "CGI art. 187 I (15 %)" },
              { kind := .interest, rateBp := 1500, statute := "CGI art. 187 III (15 %)" },
              { kind := .services, rateBp := 1500, statute := "CGI art. 198 III (15 %)" },
              { kind := .royalty, rateBp := 1500, statute := "CGI 2021 art. 198 I-III with art. 356 Ter I ('une prestation de services peut consister notamment en l'utilisation ou en la cession d'un bien incorporel'): 15 %" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else citSecCharges g ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CGI 2021 art. 229 by company.sector: 'telecom', 'bank', 'insurer', 'petroleum' (import, storage and distribution of petroleum products) 35 %; 'mining' (holders of a mining title) 30 %; another sector 25 %; no sector given: 25 % (declared); minimum tax (IMF) not read", "royalties: art. 198 covers services as defined in art. 356 Ter; whether royalties fall under it was not established"] ++ citSec.notes "Impôt sur les sociétés" g ++ citSec.unknown "Impôt sur les sociétés" g

end GnGlobal
