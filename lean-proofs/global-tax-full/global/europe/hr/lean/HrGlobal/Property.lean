import HrGlobal.Pit
import TaxKernel.Global2

/-!
# HR 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Zakon o porezu na promet nekretnina (3 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (porez na nekretnine (local)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Porez na promet nekretnina (pass 6)
Source: PwC Worldwide Tax Summaries, Croatia, Individual - Other taxes, accessed 2025-08-02 (Wayback capture; `law/pwc_indother_wb2025.txt`).
* porez na promet nekretnina 3 %: transfers of real estate outside VAT (sale, exchange, gift, inheritance, liquidation); exemptions exist


## 4100 Porez na nekretnine (rate as input) (gap pass, grade C)
Source: Zakon o lokalnim porezima (NN 152/2024) porez na nekretnine: 0,60-8,00 EUR per m² a year; the owner's main home exempt.
* rate as input: localRates.propertyTax {rate, source, date, municipality}; no rate given: grade C note per item


## 4100 Porez na nekretnine (local-tax framework pass, grade A, framework (local rate input))
Source: Zakon o izmjenama i dopuni Zakona o lokalnim porezima, NN 152/2024 (narodne-novine.nn.hr/eli/sluzbeni/2024/152/2504), read from lexifina/croatia-law zakon/2024/2504/clanak-001..015.md.
* čl. 4 (new čl. 26 (1)): 'Porez na nekretnine plaća se godišnje od 0,60 do 8,00 eura/m² korisne površine nekretnine'
* new čl. 26 (3): no decision of the council: 0,60 EUR/m² (not used as a default: Zagreb decides its own rate)
* čl. 5 (new čl. 27 (1)): not paid on property 1. used for permanent residence, 2. let on a contract for permanent residence
* worked case: a holiday flat of 80 m², example rate 2,00 EUR/m²: 160 EUR; the owner's home (permanent residence): nothing
-/

namespace HrGlobal.Property
open TaxKernel TaxKernel.Global

/-- Zakon o porezu na promet nekretnina (3 %; not where VAT is charged) -/
def p6pn : TransferDuty := { name := "Porez na promet nekretnina", sched := Schedule.flat 300, kinds := [.home, .realEstate, .land] }


/-- A case entity from its JSON (local-tax framework pass guards). -/
def lfwG (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

/-- Porez na nekretnine (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P0 : LocalTax :=
  { key := "propertyTax",   name := "Porez na nekretnine",   base := .area [.realEstate],   unit := .perUnit,   minNum := 60,   minDen := 100,   maxNum := 800,   maxDen := 100,   statute := "Zakon o lokalnim porezima čl. 26 st. 1 (0,60-8,00 EUR/m² of useful area), čl. 27 st. 1 (permanent residence exempt)" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Porez na promet nekretnina", covers := [.transactions],
     run := fun args g prev =>
       p6pn.charges g.purchases "Zakon o porezu na promet nekretnina (3 %; not where VAT is charged)" },
   { name := "4100 Porez na nekretnine (local rate input, framework pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       lfw4100P0.charges g }]

def absent : List Absent :=
  []

def notes : List String := ["HR 4400 Porez na promet nekretnina: PwC WWTS Individual - Other taxes, 2025-08-02 (Wayback capture) (grade B)", "HR 4100 local-tax framework pass: Porez na nekretnine (framework (local rate input), A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty then ["4400 exemptions (first home of citizens, close-family transfers) not modelled; inheritances and gifts of real estate also bear the tax (not modelled: purchases only)"] else [])
  ++ lfw4100P0.unknown g

#guard p6pn.amount { kind := .home, price := 200000 } == 6000
#guard p6pn.amount { kind := .home, price := 2000000 } == 60000
#guard p6pn.amount { kind := .vehicle, price := 100000 } == 0
#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"areaM2\":80}],\"localRates\":{\"propertyTax\":{\"rate\":2.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [160]
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":150000,\"areaM2\":80}],\"localRates\":{\"propertyTax\":{\"rate\":2.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"areaM2\":80}],\"localRates\":{\"propertyTax\":{\"rate\":9.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P0.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"areaM2\":80}],\"localRates\":{\"propertyTax\":{\"rate\":9.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"areaM2\":80}],\"localRates\":{\"propertyTax\":{\"rate\":0.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P0.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"areaM2\":80}],\"localRates\":{\"propertyTax\":{\"rate\":0.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1

end HrGlobal.Property
