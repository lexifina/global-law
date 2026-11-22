import EeGlobal.Pit
import TaxKernel.Global2

/-!
# EE 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (riigilõiv (notary and land register fees)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Maamaksuseadus (Tallinn)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4100 Recurrent property tax (pass 6 note, grade C)**: Maamaksuseadus (Tallinn): land tax only (buildings untaxed), at 0,1-1 % of the assessed land value as each municipality sets; reference municipality's rate not read (pass 6 note (PwC WWTS 2025 captures on disk))

* **4400 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Estonia, Corporate - Other taxes, accessed 2026-11-21 (live page; `law/pwc_corpother_live.txt`): transfer tax: none; state and notary fees only (not modelled) (PwC WWTS Corporate - Other taxes, 2026-11-21 (live page))


## 4100 Maamaks (rate as input) (gap pass, grade C)
Source: Maamaksuseadus § 5 (residential land up to 1,0 %, other land up to 2,0 % of the taxable value from 2025).
* rate as input: localRates.propertyTax {rate, source, date, municipality}; no rate given: grade C note per item


## 4100 Maamaks (land tax) (local-tax framework pass, grade B, framework (local rate input))
Source: EC Taxes in Europe Database (TEDB), tax 208, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21).
* rate: 'The tax rate is between 0.1-2.0%. The council of a local government establishes the rate of tax for each subsequent group of intended use of land ... 1) for residential land ... 0.1-1.0 per cent ...; 2) for profit-yielding land ... 0.1-0.5 per cent ...; 3) ... 0.1-2.0 per cent per year of the taxable value of land'
* limit on land tax increase from 1.1.2025: at most +50 % on the previous period's tax (needs the previous tax: not modelled)
* worked case: land with taxable value 80 000 EUR, example rate 1,0 %: 80 000 x 1,0 % = 800 EUR
-/

namespace EeGlobal.Property
open TaxKernel TaxKernel.Global

/-- A case entity from its JSON (local-tax framework pass guards). -/
def lfwG (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

/-- Maamaks (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P0 : LocalTax :=
  { key := "propertyTax",   name := "Maamaks",   base := .assets [.land],   unit := .percent,   minNum := 1,   minDen := 10,   maxNum := 2,   maxDen := 1,   statute := "Maamaksuseadus § 5 (0,1-2,0 % of the land's taxable value; residential land 0,1-1,0 %, profit-yielding land 0,1-0,5 %)" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4100 Maamaks (land tax) (local rate input, framework pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       lfw4100P0.charges g }]

def absent : List Absent :=
  [{ oecd := .transactions, why := "transfer tax: none; state and notary fees only (not modelled)" }]

def notes : List String := ["EE 4100 local-tax framework pass: Maamaks (land tax) (framework (local rate input), B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  lfw4100P0.unknown g
  ++ (if g.assets.any (·.kind == .home) then ["4100 Maamaks: the land under a home is not a separate asset here: give it as a land asset with its taxable value (grade C)"] else [])

#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":90000,\"assessed\":80000}],\"localRates\":{\"propertyTax\":{\"rate\":1.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [800]
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":90000,\"assessed\":80000}],\"localRates\":{\"propertyTax\":{\"rate\":2.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P0.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":90000,\"assessed\":80000}],\"localRates\":{\"propertyTax\":{\"rate\":2.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":90000,\"assessed\":80000}],\"localRates\":{\"propertyTax\":{\"rate\":0.05,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P0.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":90000,\"assessed\":80000}],\"localRates\":{\"propertyTax\":{\"rate\":0.05,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":90000,\"assessed\":80000}]}")).isEmpty

end EeGlobal.Property
