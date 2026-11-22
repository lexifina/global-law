import SkGlobal.Pit
import TaxKernel.Global2

/-!
# SK 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (no real-estate transfer tax (absence not yet cited)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (zákon 582/2004 Z. z. (daň z nehnuteľností, Bratislava)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4400 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Slovak Republic, Corporate - Other taxes, accessed 2025-06-13 (Wayback capture; `law/pwc_corpother_wb2025.txt`): transfer tax / stamp duty on property or shares: none (small administrative fees only) (PwC WWTS Corporate - Other taxes, 2025-06-13 (Wayback capture))

* **4100 Recurrent property tax (pass 6 note, grade C)**: zákon 582/2004 Z. z. (daň z nehnuteľností, Bratislava): daň z nehnuteľností (zákon 582/2004 Z. z.): per-m2 rates set by each municipality; area inputs are not in the model (pass 6 note (PwC WWTS 2025 captures on disk))


## 4100 Daň zo stavieb a daň z bytov (local-tax framework pass, grade B, framework (local rate input))
Source: EC Taxes in Europe Database (TEDB), tax 559, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21).
* rate: 'Tax on constructions: EUR 0.033 per every square metre of built-up area the tax administrator (municipality) may increase or decrease the tax rate, although it may not exceed 10 times the lowest annual tax rate set by a tax administrator. ... Apartment tax: EUR 0.033 per each square metre ...'
* worked case: flat of 80 m² at an example 0,50 EUR/m²: 40 EUR
-/

namespace SkGlobal.Property
open TaxKernel TaxKernel.Global

/-- A case entity from its JSON (local-tax framework pass guards). -/
def lfwG (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

/-- Daň zo stavieb a z bytov (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P0 : LocalTax :=
  { key := "propertyTax",   name := "Daň zo stavieb a z bytov",   base := .area [.home, .realEstate],   unit := .perUnit,   statute := "zákon 582/2004 Z. z. (tax on buildings and flats: the municipality's rate per m²)" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4100 Daň zo stavieb a daň z bytov (local rate input, framework pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       lfw4100P0.charges g }]

def absent : List Absent :=
  [{ oecd := .transactions, why := "transfer tax / stamp duty on property or shares: none (small administrative fees only)" }]

def notes : List String := ["SK 4100 local-tax framework pass: Daň zo stavieb a daň z bytov (framework (local rate input), B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  lfw4100P0.unknown g

#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":200000,\"areaM2\":80}],\"localRates\":{\"propertyTax\":{\"rate\":0.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [40]
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":200000,\"areaM2\":80}]}")).isEmpty

end SkGlobal.Property
