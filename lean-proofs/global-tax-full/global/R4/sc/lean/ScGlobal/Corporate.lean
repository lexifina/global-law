import R4Common
import TaxKernel.Global2

/-!
# Seychelles 2025: corporate income tax (1200) and withholding (generated from `R4/specs/sc.json`)

Pass 10: official instruments from the Seychelles Revenue Commission legislation page (src.gov.sc / staging.src.gov.sc `wp-content/uploads/...`, links listed in `world/B09-southern-africa/sc/law/leg.html`), saved in `R4/fetch/sc10/` (SHA256SUMS; Business Tax schedule amendments in `R4/fetch/sc10/bt/`). Scanned gazettes were OCRed (tesseract eng; the VAT Act 2010 scan is landscape with one page per half: `tools/ocr10_halves.sh`) or read on the page image (S.I. 27 of 2010).

S.I. 108 of 2021 reg. 2 (in operation 1 January 2022) substitutes Item 1 (a) and (b) of the First Schedule to the Business Tax Act (rates on taxable income under section 6): an entity, government body or trustee under section 40 (5) pays "15% on the first SCR 1,000,000 of taxable income" and 25 % on the remainder; any other person 0 % up to SCR 102,666, 15 % from SCR 102,666 to SCR 1,000,000 and 25 % above; Items 1 (d) and 4 are repealed. Later First Schedule amendments: S.I. 107 of 2024 (interest withholding tables, items 3 (e) and 5 (2)).

S.I. 27 of 2010 (First Schedule substituted), item 3 (read on the page image): "The rate of business tax payable by a non-resident person under section 8 (a) in the case of a dividend, royalty, natural resource amount or technical service fee is 15%; (b) in the case of an insurance premium is 5%; or (c) in the case of interest, the rates shall be as follows— ..." S.I. 66 of 2012 reg. 2 (e): "by repealing in item 3(a) the figure '15%;' and inserting between item (a) and (b) the following— (i) 15%; or (ii) The rate applicable under a taxation agreement ...". S.I. 107 of 2024 (from 1 January 2025) substitutes the table under item 3 (e): "Interest payment by a person being a non-financial institution to a person not being a financial institution 15%" (current account 5 %, fixed deposit 0 % individuals / 5 % otherwise, savings 0 %, government securities 0 %).
-/

namespace ScGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Business tax (entities)", sched := (Schedule.ofUpper [(1000000, 1500)] 2500), lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2400249
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 150000
#guard R4.corpTax citR minT { profit := 999999, turnover := 10000000, lossesForward := 0 } 1 == 149999
#guard R4.corpTax citR minT { profit := 1000777, turnover := 10000000, lossesForward := 0 } 1 == 150194
def citS0 : CorpRegime :=
  { name := "Business tax (entities)", sched := (Schedule.ofUpper [(1000000, 2500)] 3300), lossFull := -1, lossExcessBp := 10000 }

def minS0 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS0 minS0 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3220329
#guard R4.corpTax citS0 minS0 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 250000
#guard R4.corpTax citS0 minS0 { profit := 999999, turnover := 10000000, lossesForward := 0 } 1 == 249999
#guard R4.corpTax citS0 minS0 { profit := 1000777, turnover := 10000000, lossesForward := 0 } 1 == 250256
/-- CIT by `company.sector` (kernel 2.5.0 `SectorCorp`): a company whose sector is given and in none of the rules is under the
general rule; an absent sector: `general` (declared here). -/
def citSec : SectorCorp :=
  { general := { regime := citR }, statute := "Business Tax Act 2009 (Cap 20) s. 6 and First Schedule item 1 (a) as substituted by the Business Tax (Amendment of Schedules) Regulations 2021 (S.I. 108 of 2021, from 1 Jan 2022): entities 15 % on the first SCR 1,000,000 of taxable income and 25 % on the remainder [text version: the Act and regulations as published, with the S.I. listed (to S.I. 107 of 2024, in force 1 January 2025)]", ifAbsent := .general,
    bySector := [{ sectors := ["telecom", "bank", "insurer", "alcoholManufacturing", "tobaccoManufacturing"], rule := { regime := citS0 }, statute := "Business Tax Act First Schedule item 1 (c) as added by S.I. 66 of 2012 (telecommunications service providers, banks, insurance companies, alcohol and tobacco manufacturers: 25 % on the first SCR 1,000,000, 33 % on the remainder); not repealed by S.I. 108 of 2021" }] }

/-- The minimum tax that goes with the rule `citSec.pick` chose (the rules are told apart by their provision). -/
def citMinFor (st : String) : R4.MinTax :=
  if st == "Business Tax Act First Schedule item 1 (c) as added by S.I. 66 of 2012 (telecommunications service providers, banks, insurance companies, alcohol and tobacco manufacturers: 25 % on the first SCR 1,000,000, 33 % on the remainder); not repealed by S.I. 108 of 2021" then minS0 else minT

def citSecCharges (g : CanonGlobal) : List Charge :=
  match citSec.pick g with
  | some (r, st) => [R4.citCharge r.regime (citMinFor st) g.company st (step := 1)]
  | none => []
def citSecT0 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-sc-bank\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 30000000, \"profit\": 3000000, \"lossesForward\": 0, \"sector\": \"bank\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT0).map (·.due)) == [910000]
def citSecT1 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-sc-none\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 30000000, \"profit\": 3000000, \"lossesForward\": 0}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT1).map (·.due)) == [650000]
def whtR : Wht :=
  { name := "Business tax on payments to non-residents (s. 8)",
    rules := [{ kind := .dividend, rateBp := 1500, statute := "First Schedule item 3 (a) (i): 15 %" },
              { kind := .royalty, rateBp := 1500, statute := "First Schedule item 3 (a) (i): 15 %" },
              { kind := .services, rateBp := 1500, statute := "First Schedule item 3 (a) (i): technical service fee 15 %" },
              { kind := .interest, rateBp := 1500, statute := "First Schedule item 3 (e) table (S.I. 107 of 2024): interest paid by a non-financial institution to a person not being a financial institution 15 %" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Business tax (entities)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else citSecCharges g ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["item 1 (c) by company.sector (S.I. 66 of 2012; S.I. 108 of 2021 replaced items 1 (a)-(b) and repealed 1 (d), not 1 (c)): 'telecom', 'bank', 'insurer', 'alcoholManufacturing', 'tobaccoManufacturing' 25 % on the first SCR 1,000,000 and 33 % on the remainder; another sector or none given: item 1 (a) (declared)", "corporate social responsibility tax and tourism marketing tax (0.5 % of turnover, Seventh Schedule) are separate levies, not modelled here", "only technical service fees are within s. 8 among service payments; managerial fees paid by financial institutions 33 % (S.I. 92 of 2010) not modelled", "treaty rates (item 3 (a) (ii)) not applied (statutory rates)", "S.I. 16 of 2013 and S.I. 63 of 2010 could not be read (rotated scans); S.I. 38 of 2013, which amends S.I. 16 of 2013, concerns the corporate social responsibility tax"] ++ citSec.notes "Business tax (entities)" g ++ citSec.unknown "Business tax (entities)" g

end ScGlobal
