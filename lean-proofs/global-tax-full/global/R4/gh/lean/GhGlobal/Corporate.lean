import R4Common
import TaxKernel.Global2

/-!
# Ghana 2025: corporate income tax (1200) and withholding (generated from `R4/specs/gh.json`)

Sources: VAT Act 2013 (Act 870) (registry fetch `global/registry/afm_data/fetch/GH/gh_vat870.pdf.txt`); Income Tax Act 2015 (Act 896) OCR (`world/B10-anglophone-africa/gh/law/act896_ocr.txt`).

First Schedule para 3 (1): "The chargeable income of a company other than a company principally engaged in the hotel industry … is taxed at the rate of twenty-five percent"; (2) hotels 22 %; (3) non-traditional exports 8 %.

First Schedule (withholding rates): payments under s. 115 "(i) in the case of dividends, eight percent; … (iii) in the case of any other interest, eight percent; … (ix) natural resource payments and royalties, fifteen percent"; s. 116: "(viii) in the case of management and technical service fees referred to in section 116(9), twenty percent".
-/

namespace GhGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2500249
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 250000
def citS0 : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 2200, lossFull := -1, lossExcessBp := 10000 }

def minS0 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS0 minS0 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2200219
#guard R4.corpTax citS0 minS0 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 220000
def citS1 : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 3500, lossFull := -1, lossExcessBp := 10000 }

def minS1 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS1 minS1 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3500349
#guard R4.corpTax citS1 minS1 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS1 minS1 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS1 minS1 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 350000
def citS2 : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 3500, lossFull := -1, lossExcessBp := 10000 }

def minS2 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS2 minS2 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3500349
#guard R4.corpTax citS2 minS2 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS2 minS2 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS2 minS2 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 350000
/-- CIT by `company.sector` (kernel 2.5.0 `SectorCorp`): a company whose sector is given and in none of the rules is under the
general rule; an absent sector: `general` (declared here). -/
def citSec : SectorCorp :=
  { general := { regime := citR }, statute := "Income Tax Act 2015 (Act 896) First Schedule para 3 (1) (25 %) [text version: Act 870 (2013) and Act 896 (2015) as enacted (gazetted copies), Act 896 para 3 (1) as restated by Act 1094 (2023); later amending Acts not consolidated (flag)]", ifAbsent := .general,
    bySector := [{ sectors := ["hotel"], rule := { regime := citS0 }, statute := "Income Tax Act 2015 (Act 896) First Schedule para 3 (2) (company principally engaged in the hotel industry 22 %)" },
      { sectors := ["petroleumOperations"], rule := { regime := citS1 }, statute := "Income Tax Act 2015 (Act 896) First Schedule para 5 (petroleum operations 35 %)" },
      { sectors := ["mining"], rule := { regime := citS2 }, statute := "Income Tax Act 2015 (Act 896) First Schedule para 6 (mineral operations 35 %)" }] }

/-- The minimum tax that goes with the rule `citSec.pick` chose (the rules are told apart by their provision). -/
def citMinFor (st : String) : R4.MinTax :=
  if st == "Income Tax Act 2015 (Act 896) First Schedule para 3 (2) (company principally engaged in the hotel industry 22 %)" then minS0 else if st == "Income Tax Act 2015 (Act 896) First Schedule para 5 (petroleum operations 35 %)" then minS1 else if st == "Income Tax Act 2015 (Act 896) First Schedule para 6 (mineral operations 35 %)" then minS2 else minT

def citSecCharges (g : CanonGlobal) : List Charge :=
  match citSec.pick g with
  | some (r, st) => [R4.citCharge r.regime (citMinFor st) g.company st (step := 1)]
  | none => []
def citSecT0 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-gh-hot\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"hotel\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT0).map (·.due)) == [220000]
def citSecT1 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-gh-min\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"mining\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT1).map (·.due)) == [350000]
def citSecT2 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-gh-none\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT2).map (·.due)) == [250000]
def whtR : Wht :=
  { name := "Withholding tax (non-residents)",
    rules := [{ kind := .dividend, rateBp := 800, statute := "Act 896 First Schedule (dividends 8 %)" },
              { kind := .interest, rateBp := 800, statute := "Act 896 First Schedule (other interest 8 %)" },
              { kind := .royalty, rateBp := 1500, statute := "Act 896 First Schedule (royalties 15 %)" },
              { kind := .services, rateBp := 2000, statute := "Act 896 First Schedule (management and technical fees 20 %)" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 80000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 80000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 200000
def corporate : Family :=
  { name := "1200 Income tax (companies)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else citSecCharges g ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["Act 896 with Act 1094 (2023), which restates para 3 (1) at 25 % (OCR of the gazette copy); other later rate changes not checked", "the Growth and Sustainability Levy (Act 1095, 2023) on company profits is booked by its own entry (category C rate), not here", "First Schedule by company.sector: 'hotel' 22 % (para 3 (2)); 'petroleumOperations' (upstream petroleum operations) 35 % (para 5); 'mining' (mineral operations) 35 % (para 6); another sector or none given: 25 % (declared); non-traditional exports 8 %, manufacturing by location (75 % / 50 % of the rate), lottery operations (para 7A) and free-zone rates are not applied"] ++ citSec.notes "Income tax (companies)" g ++ citSec.unknown "Income tax (companies)" g

end GhGlobal
