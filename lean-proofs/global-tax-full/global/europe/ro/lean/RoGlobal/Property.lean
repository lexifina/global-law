import RoGlobal.Pit
import TaxKernel.Global2

/-!
# RO 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (taxe notariale / impozit pe transferul proprietăților (Codul fiscal art. 111: 1 %/3 % on the seller)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Codul fiscal Titlul IX (impozitul pe clădiri, București)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4400 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Romania, Corporate - Other taxes, accessed 2025-06-17 (Wayback capture; `law/pwc_corpother_wb2025.txt`): property transfer tax: none; notary fees only (PwC WWTS Corporate - Other taxes, 2025-06-17 (Wayback capture))

* **4100 Recurrent property tax (pass 6 note, grade C)**: Codul fiscal Titlul IX (impozitul pe clădiri, București): impozit pe clădiri / teren set by the local council (Codul fiscal art. 457-465 ranges); București rates not read (pass 6 note (PwC WWTS 2025 captures on disk))


## 4100 Impozit pe clădiri rezidențiale, persoane fizice (rate as input) (gap pass, grade C)
Source: Codul fiscal (Legea 227/2015) art. 457 (0,08-0,2 % of the taxable value of residential buildings of individuals).
* rate as input: localRates.propertyTax {rate, source, date, municipality}; no rate given: grade C note per item


## 4100 Impozit pe clădiri rezidențiale (local-tax framework pass, grade B, framework (local rate input))
Source: EC Taxes in Europe Database (TEDB), tax 497, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21).
* rate: 'For residential buildings: 0.08-0.2% from the taxable value of the building. For non-residential buildings: from 0.2% to 1.3%'
* worked case: home with taxable value 250 000 RON, example rate 0,1 %: 250 RON
-/

namespace RoGlobal.Property
open TaxKernel TaxKernel.Global

/-- A case entity from its JSON (local-tax framework pass guards). -/
def lfwG (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

/-- Impozit pe clădiri rezidențiale (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P0 : LocalTax :=
  { key := "propertyTax",   name := "Impozit pe clădiri rezidențiale",   base := .assets [.home, .realEstate],   unit := .percent,   minNum := 8,   minDen := 100,   maxNum := 2,   maxDen := 10,   statute := "Codul fiscal art. 457 alin. (1) (0,08-0,2 % of the taxable value of residential buildings)" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4100 Impozit pe clădiri rezidențiale (local rate input, framework pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       lfw4100P0.charges g }]

def absent : List Absent :=
  [{ oecd := .transactions, why := "property transfer tax: none; notary fees only" }]

def notes : List String := ["RO 4100 local-tax framework pass: Impozit pe clădiri rezidențiale (framework (local rate input), B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  lfw4100P0.unknown g

#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":300000,\"assessed\":250000}],\"localRates\":{\"propertyTax\":{\"rate\":0.1,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [250]
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":300000,\"assessed\":250000}],\"localRates\":{\"propertyTax\":{\"rate\":0.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P0.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":300000,\"assessed\":250000}],\"localRates\":{\"propertyTax\":{\"rate\":0.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":300000,\"assessed\":250000}]}")).isEmpty

end RoGlobal.Property
