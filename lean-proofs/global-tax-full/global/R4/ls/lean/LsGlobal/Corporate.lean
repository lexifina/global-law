import R4Common
import TaxKernel.Global2

/-!
# Lesotho 2025: corporate income tax (1200) and withholding (generated from `R4/specs/ls.json`)

No usable 2025 text for these headings: the Income Tax Act 1993 held is a 2012 consolidation; no 2025 text for any heading. RSL pages and guides fetched 2026-11-21 (`cmp20/global/R4/fetch/ls8/`, SHA256SUMS): withholding tax guide, VAT Act 2001, VAT (Amendment) Regulations LN 18 of 2020 and LN 30 of 2021 (OCR). Pass 9 (VAT): the Revenue Services Lesotho uploads of the VAT (Amendment) Regulations LN 27 of 2018 and LN 34 of 2019 (www.rsl.org.ls/sites/default/files/2018-04/…, 2019-04/…, via Wayback; scanned gazettes, OCR eng) and RSL's 'VAT Rates Changes 2018' notice, in `R4/fetch/ls9/` (SHA256SUMS); LN 18 of 2020 and LN 30 of 2021 and the VAT Act 2001 already held in `R4/fetch/ls8/`. The RSL document list on Wayback shows no later VAT regulation (2022-2024).

Third Schedule (section 10), Resident Company Income Tax Rates: "1. Manufacturing income derived from a manufacturing activity of an industrial, scientific or educational nature which promotes industrial, scientific, educational or other development within Lesotho 10% ... 3. Other manufacturing income 10% 4. Other income 25%" [Third Schedule substituted by sec. 3 of Act No. 2 of 2007]; s. 2: "standard rate of tax" means a rate of 25%. The RSL 'corporate income tax' page (2026) still attaches this consolidation. Grade B flagged: no Finance Act after 2012 was read.

s. 107 (1): "withholding tax at the standard rate of tax is payable on the gross amount of a Lesotho-source dividend, interest, royalty, natural resource payment, or management charge paid to a non-resident"; (3): 15 % where the payment relates to concessionary manufacturing income; s. 108 (1): "Withholding tax at the rate of 10% is payable on the gross amount of a payment under a Lesotho-source services contract paid to a non-resident"; s. 109 (1): final tax. RSL Withholding Tax Guide table: "Dividends 25% ... Interest 25% ... Management Fee 25% ... Royalty 25%".
-/

namespace LsGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Company income tax", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2500249
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 250000
def citS0 : CorpRegime :=
  { name := "Company income tax", sched := Schedule.flat 1000, lossFull := -1, lossExcessBp := 10000 }

def minS0 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS0 minS0 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 1000099
#guard R4.corpTax citS0 minS0 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 100000
/-- CIT by `company.sector` (kernel 2.5.0 `SectorCorp`): a company whose sector is given and in none of the rules is under the
general rule; an absent sector: `general` (declared here). -/
def citSec : SectorCorp :=
  { general := { regime := citR }, statute := "Income Tax Act 1993 s. 10 and Third Schedule item 4 (other income 25 %; substituted by Act No. 2 of 2007), consolidation to 1 April 2012 as published by the RSL; amendments 2013-2025 not held (flagged)", ifAbsent := .general,
    bySector := [{ sectors := ["manufacturing"], rule := { regime := citS0 }, statute := "Income Tax Act 1993 Third Schedule items 1 and 3 (manufacturing income 10 %; Act No. 2 of 2007)" }] }

/-- The minimum tax that goes with the rule `citSec.pick` chose (the rules are told apart by their provision). -/
def citMinFor (st : String) : R4.MinTax :=
  if st == "Income Tax Act 1993 Third Schedule items 1 and 3 (manufacturing income 10 %; Act No. 2 of 2007)" then minS0 else minT

def citSecCharges (g : CanonGlobal) : List Charge :=
  match citSec.pick g with
  | some (r, st) => [R4.citCharge r.regime (citMinFor st) g.company st (step := 1)]
  | none => []
def citSecT0 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ls-mfg\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"manufacturing\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT0).map (·.due)) == [100000]
def citSecT1 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ls-none\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT1).map (·.due)) == [250000]
def whtR : Wht :=
  { name := "Withholding on payments to non-residents",
    rules := [{ kind := .dividend, rateBp := 2500, statute := "ITA 1993 s. 107 (1) (standard rate 25 %)" },
              { kind := .interest, rateBp := 2500, statute := "ITA 1993 s. 107 (1) (standard rate 25 %)" },
              { kind := .royalty, rateBp := 2500, statute := "ITA 1993 s. 107 (1) (standard rate 25 %)" },
              { kind := .services, rateBp := 1000, statute := "ITA 1993 s. 108 (1) (10 %)" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 250000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 250000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 250000
#guard whtR.amount { kind := .services, amount := 1000000 } == 100000
def corporate : Family :=
  { name := "1200 Company income tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else citSecCharges g ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["Third Schedule by company.sector: 'manufacturing' 10 % on all its income (the model does not split manufacturing from other income); manufacturing exports outside SACU (item 2) not applied; another sector or none given: 25 % (declared); advance corporation tax on distributions (33,33 %, creditable) not modelled", "management charges are at 25 % under s. 107 (s. 108 (2) excludes them from the 10 % services rate): the services line is taken as an ordinary services contract", "dividends out of concessionary manufacturing income are exempt and related interest/royalties/fees are at 15 % (s. 107 (2)-(3)): not separable"] ++ citSec.notes "Company income tax" g ++ citSec.unknown "Company income tax" g

end LsGlobal
