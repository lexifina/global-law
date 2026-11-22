import BgGlobal.Pit
import TaxKernel.Global2

/-!
# BG 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (ЗМДТ чл. 44-47 (данък при придобиване, 0,1-3 % по общини)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (ЗМДТ данък върху недвижимите имоти (София)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4100 Recurrent property tax (pass 6 note, grade C)**: ЗМДТ данък върху недвижимите имоти (София): rates set by each municipality between 0,01 % and 0,45 % of the tax value (ЗМДТ); no reference municipality's decision read (pass 6 note (PwC WWTS 2025 captures on disk))

* **4400 Real-estate transfer and stamp duties (pass 6 note, grade C)**: ЗМДТ чл. 44-47 (данък при придобиване, 0,1-3 % по общини): данък при придобиване на имущество: 0,1-3 % as each municipality sets (ЗМДТ); Sofia rate not read (pass 6 note (PwC WWTS 2025 captures on disk))


## 4100 Данък върху недвижимите имоти (rate as input) (gap pass, grade C)
Source: ЗМДТ чл. 22 (0,1-4,5 ‰ of the tax assessment); the main home 50 % off.
* rate as input: localRates.propertyTax {rate, source, date, municipality}; no rate given: grade C note per item


## 4100 Данък върху недвижимите имоти (local-tax framework pass, grade B)
Source: Закон за местните данъци и такси, consolidated text as of ДВ бр. 81/2024 (mrrb.bg), read from lexifina/bulgaria-law zakon/1997/dv117-zmdt/full-text.md; the Sofia rate from EC Taxes in Europe Database (TEDB), tax 1761, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21).
* чл. 22: 'Общинският съвет определя с наредбата по чл. 1, ал. 2 размера на данъка в граници от 0,1 до 4,5 на хиляда върху данъчната оценка на недвижимия имот.'
* чл. 25 (1): 'За имот, който е основно жилище, данъкът се дължи с 50 на сто намаление.'
* TEDB 1761 rate: 'The tax rate determined by Ordinance of the Municipal Council for the municipality of the capital city of Sofia is set at 1.875 per thousand on the tax value of the property.'
* worked case (Sofia, no rate given): main home assessed 100 000: 50 000 x 1,875 per mille = 93; other property 100 000: 187
-/

namespace BgGlobal.Property
open TaxKernel TaxKernel.Global

/-- A case entity from its JSON (local-tax framework pass guards). -/
def lfwG (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

/-- Данък върху недвижимите имоти (основно жилище) (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P0 : LocalTax :=
  { key := "propertyTax",   name := "Данък върху недвижимите имоти (основно жилище)",   base := .assets [.home],   unit := .permille,   ratioNum := 1,   ratioDen := 2,   minNum := 1,   minDen := 10,   maxNum := 45,   maxDen := 10,   default := some { municipality := "Sofia", num := 1875, den := 1000, source := "Наредба за определяне размера на местните данъци на територията на Столична община: 1,875 per mille, as stated in EC Taxes in Europe Database (TEDB), tax 1761, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21)", date := "2025-01-01" },   statute := "ЗМДТ чл. 22, чл. 25 ал. 1 (main home: 50 % reduction, applied to the assessment)" }

/-- Данък върху недвижимите имоти (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P1 : LocalTax :=
  { key := "propertyTax",   name := "Данък върху недвижимите имоти",   base := .assets [.realEstate, .land],   unit := .permille,   minNum := 1,   minDen := 10,   maxNum := 45,   maxDen := 10,   default := some { municipality := "Sofia", num := 1875, den := 1000, source := "Наредба за определяне размера на местните данъци на територията на Столична община: 1,875 per mille, as stated in EC Taxes in Europe Database (TEDB), tax 1761, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21)", date := "2025-01-01" },   statute := "ЗМДТ чл. 22" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4100 Данък върху недвижимите имоти (local rate input, framework pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       lfw4100P0.charges g
       ++ lfw4100P1.charges g }]

def absent : List Absent :=
  []

def notes : List String := ["BG 4100 local-tax framework pass: Данък върху недвижимите имоти (modelled, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ lfw4100P0.unknown g
  ++ lfw4100P1.unknown g

#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":150000,\"assessed\":100000}]}")).map (·.due)) == [93]
#guard ((lfw4100P1.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"assessed\":100000}]}")).map (·.due)) == [187]
#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":150000,\"assessed\":100000}],\"localRates\":{\"propertyTax\":{\"rate\":2.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"Plovdiv\"}}}")).map (·.due)) == [100]
#guard (lfw4100P1.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"assessed\":100000}],\"localRates\":{\"propertyTax\":{\"rate\":5.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P1.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"assessed\":100000}],\"localRates\":{\"propertyTax\":{\"rate\":5.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1
#guard (lfw4100P1.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"assessed\":100000,\"region\":\"Varna\"}]}")).isEmpty

end BgGlobal.Property
