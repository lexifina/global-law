import LvGlobal.Pit
import TaxKernel.Global2

/-!
# LV 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Likums par valsts nodevām (2 % kancelejas nodeva)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Likums Par nekustamā īpašuma nodokli (Rīga)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Valsts nodeva (zemesgrāmata) (pass 6)
Source: PwC Worldwide Tax Summaries, Latvia, Corporate - Other taxes, accessed 2025-08-29 (Wayback capture; `law/pwc_corpother_wb2025.txt`).
* Land Register state fee 2 % of max(deal value, cadastral value), cap EUR 50 000


## 4100 Nekustamā īpašuma nodoklis (rate as input) (gap pass, grade C)
Source: Likums Par nekustamā īpašuma nodokli 3. pants (0,2-3 % of the cadastral value; default housing rates by value band where the municipality decides none).
* rate as input: localRates.propertyTax {rate, source, date, municipality}; no rate given: grade C note per item


## 4100 Nekustamā īpašuma nodoklis (local-tax framework pass, grade B, framework (local rate input))
Source: EC Taxes in Europe Database (TEDB), tax 4542, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21).
* rate: 'The immovable property tax rate or rates from 0.2 to 3 per cent from the cadastral value ... shall be determined by a local government in the binding regulations thereof ... published ... until 1 November of the pre-taxation year'
* fallback where no regulations are published: 1,5 %; housing 0,2 % to 56 915 EUR, 0,4 % to 106 715 EUR, 0,6 % above (not modelled: Riga publishes its own)
* worked case: home with cadastral value 100 000 EUR, example rate 0,2 %: 200 EUR
-/

namespace LvGlobal.Property
open TaxKernel TaxKernel.Global

/-- Cabinet regulation on state fees for the Land Register (2 % of the deal or cadastral value, at most EUR 50 000) -/
def p6nod : TransferDuty := { name := "Valsts nodeva (zemesgrāmata)", sched := Schedule.flat 200, kinds := [.home, .realEstate, .land] }
/-- the duty per purchase, at most 50000 -/
def p6nodCap (p : Purchase) : Int := min 50000 (p6nod.amount p)
def p6nodCharges (ps : List Purchase) : List Charge :=
  (ps.zipIdx.filter fun (p, _) => p6nod.kinds.contains p.kind).map fun (p, i) =>
    charge .transactions p6nod.name p.price (fun _ => p6nod.base p) (fun _ => p6nodCap p) (event := s!"purchase {i + 1}") (statute := "Cabinet regulation on state fees for the Land Register (2 % of the deal or cadastral value, at most EUR 50 000)")


/-- A case entity from its JSON (local-tax framework pass guards). -/
def lfwG (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

/-- Nekustamā īpašuma nodoklis (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P0 : LocalTax :=
  { key := "propertyTax",   name := "Nekustamā īpašuma nodoklis",   base := .assets [.home, .realEstate, .land],   unit := .percent,   minNum := 2,   minDen := 10,   maxNum := 3,   maxDen := 1,   statute := "Likums \"Par nekustamā īpašuma nodokli\" 3. pants (0,2-3 % of the cadastral value)" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Valsts nodeva (zemesgrāmata)", covers := [.transactions],
     run := fun args g prev =>
       p6nodCharges g.purchases },
   { name := "4100 Nekustamā īpašuma nodoklis (local rate input, framework pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       lfw4100P0.charges g }]

def absent : List Absent :=
  []

def notes : List String := ["LV 4400 Valsts nodeva (zemesgrāmata): PwC WWTS Corporate - Other taxes, 2025-08-29 (Wayback capture) (grade B)", "LV 4100 local-tax framework pass: Nekustamā īpašuma nodoklis (framework (local rate input), B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty then ["4400 the base is the higher of the deal and cadastral value (the price stands in); reduced fees for family transfers not modelled"] else [])
  ++ lfw4100P0.unknown g

#guard p6nodCap { kind := .home, price := 200000 } == 4000
#guard p6nodCap { kind := .home, price := 2000000 } == 40000
#guard p6nodCap { kind := .home, price := 10000000000000 } == 50000
#guard p6nodCap { kind := .vehicle, price := 100000 } == 0
#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":120000,\"assessed\":100000}],\"localRates\":{\"propertyTax\":{\"rate\":0.2,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [200]
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":120000,\"assessed\":100000}],\"localRates\":{\"propertyTax\":{\"rate\":3.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P0.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":120000,\"assessed\":100000}],\"localRates\":{\"propertyTax\":{\"rate\":3.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":120000,\"assessed\":100000}]}")).isEmpty

end LvGlobal.Property
