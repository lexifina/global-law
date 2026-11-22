import R4Common
import TaxKernel.Global2

/-!
# Namibia 2025: corporate income tax (1200) and withholding (generated from `R4/specs/na.json`)

Source: Income Tax Act 1981, NamibLII consolidation at 2024-09-16, archived copy `web.archive.org/web/20260212092155id_/https://namiblii.org/akn/na/act/1981/24/eng@2024-09-16` (`R4/na/law/namiblii_ita_2024-09-16_wayback20260212.txt`, html sha256 f8590e2fd0fb1b94…). VAT Act 2000 and excise texts not held. VAT Act 2000 (NamibLII 2023-01-01, archived 2024-11-10).

Schedule 4 para. 3 (1): "the rates of normal tax to be levied in respect of the taxable income derived by a company shall be as follows: (a) on each N$ of taxable income derived from a source other than mining= (i) 31 cents in respect of the year of assessment on or after 1 January 2024; and (ii) 30 cents in respect of any year of assessment on or after 1 January 2025". Mining (37,5 cents) and diamond rates not modelled.

s. 35A (3): "The rate of tax is - (a) 10 per cent of any management fee or consultancy fee specified in subsection (1)"; s. 45: "The rate of tax is - (a) 10 per cent of the amounts specified in section 42 if the beneficial owner is a company which holds directly or indirectly at least 25 per cent of the capital of the company paying the dividends; or (b) 20 per cent of the amounts specified in section 42 in all other cases." Twelfth pass (kernel 2.3.0 grade-C withholding): interest 10 %: ITA s. 35B (2)-(4) (withholding tax on foreign interest 10 %, final; consolidation as in force 2024-09-16); royalty 10 %: ITA s. 35 (1)-(2) (withholding tax on royalties 10 %, final; substituted by Act 13 of 2015)
-/

namespace NaGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Normal tax on companies", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3000299
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 300000
def citS0 : CorpRegime :=
  { name := "Normal tax on companies", sched := Schedule.flat 3750, lossFull := -1, lossExcessBp := 10000 }

def minS0 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS0 minS0 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3750374
#guard R4.corpTax citS0 minS0 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 375000
def citS1 : CorpRegime :=
  { name := "Normal tax on companies", sched := Schedule.flat 5500, lossFull := -1, lossExcessBp := 10000 }

def minS1 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS1 minS1 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 5500549
#guard R4.corpTax citS1 minS1 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS1 minS1 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS1 minS1 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 550000
/-- CIT by `company.sector` (kernel 2.5.0 `SectorCorp`): a company whose sector is given and in none of the rules is under the
general rule; an absent sector: `general` (declared here). -/
def citSec : SectorCorp :=
  { general := { regime := citR }, statute := "ITA Schedule 4 para. 3 (1) (a) (ii) (30 cents per N$ for years of assessment from 1 Jan 2025; Act 4 of 2024 s. 6 (b))", ifAbsent := .general,
    bySector := [{ sectors := ["mining"], rule := { regime := citS0 }, statute := "ITA Schedule 4 para. 3 (1) (b) (mining of minerals other than diamonds, and services to licensed miners: 37,5 cents per N$)" },
      { sectors := ["diamondMining"], rule := { regime := citS1 }, statute := "ITA Schedule 4 para. 3 (1) (c) (diamond mining: 50 cents per N$ plus a surcharge of 10 % of that tax, 55 %)" }],
    outside := [{ sectors := ["petroleum"], statute := "the Petroleum (Taxation) Act, 1991 (Act 3 of 1991; in force 30 September 1992, per the ITA's amendment notes)" }] }

/-- The minimum tax that goes with the rule `citSec.pick` chose (the rules are told apart by their provision). -/
def citMinFor (st : String) : R4.MinTax :=
  if st == "ITA Schedule 4 para. 3 (1) (b) (mining of minerals other than diamonds, and services to licensed miners: 37,5 cents per N$)" then minS0 else if st == "ITA Schedule 4 para. 3 (1) (c) (diamond mining: 50 cents per N$ plus a surcharge of 10 % of that tax, 55 %)" then minS1 else minT

def citSecCharges (g : CanonGlobal) : List Charge :=
  if (citSec.outsideOf g).isSome then [] else
  match citSec.pick g with
  | some (r, st) => [R4.citCharge r.regime (citMinFor st) g.company st (step := 1)]
  | none => []
def citSecT0 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-na-min\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"mining\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT0).map (·.due)) == [375000]
def citSecT1 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-na-dia\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"diamondMining\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT1).map (·.due)) == [550000]
def citSecT2 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-na-none\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT2).map (·.due)) == [300000]
def citSecT3 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s19-na-pet\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"petroleum\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT3).map (·.due)) == []
def whtR : Wht :=
  { name := "Withholding on payments to non-residents",
    rules := [{ kind := .services, rateBp := 1000, statute := "ITA s. 35A (3) (a) (10 %)" },
              { kind := .dividend, rateBp := 1000, toCompany := some true, minStakeBp := 2500, statute := "ITA s. 45 (a) (10 %, company holding at least 25 %)" },
              { kind := .dividend, rateBp := 2000, statute := "ITA s. 45 (b) (20 %)" },
              { kind := .interest, rateBp := 1000, statute := "ITA s. 35B (2)-(4) (withholding tax on foreign interest 10 %, final; consolidation as in force 2024-09-16)" },
              { kind := .royalty, rateBp := 1000, statute := "ITA s. 35 (1)-(2) (withholding tax on royalties 10 %, final; substituted by Act 13 of 2015)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 100000
#guard whtR.amount { kind := .dividend, amount := 1000000, toCompany := true, stakeBp := 2500 } == 100000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 200000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 100000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 100000
def corporate : Family :=
  { name := "1200 Normal tax on companies", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else citSecCharges g ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["ITA Schedule 4 para. 3 (1) (a) (ii): 30 % for years of assessment from 1 Jan 2025 (non-mining)", "by company.sector: 'mining' 37,5 % (para 3 (1) (b)), 'diamondMining' 55 % (para 3 (1) (c), 50 % plus the 10 % surcharge), on all the company's taxable income (the model does not split mining from other income); another sector or none given: 30 % (declared); a 'petroleum' company is taxed under the Petroleum (Taxation) Act, 1991 (Act 3 of 1991), not under this tax: no charge here, listed as grade C (nineteenth pass, kernel 2.7.0 SectorCorp.outside)"] ++ citSec.notes "Normal tax on companies" g ++ citSec.unknown "Normal tax on companies" g

end NaGlobal
