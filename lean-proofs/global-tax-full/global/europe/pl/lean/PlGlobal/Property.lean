import PlGlobal.Pit
import TaxKernel.Global2

/-!
# PL 2025: transfer duties on purchases (4400); recurrent property tax not modelled

Source: ustawa o podatku od czynności cywilnoprawnych, tekst jednolity Dz.U. 2024 poz. 295 (Sejm ELI API, `pl/law/pcc_tj.pdf`); sha256 in `law/SHA256SUMS`.
* art. 7 ust. 1 pkt 1 lit. a: "przy przeniesieniu własności nieruchomości, rzeczy ruchomych, prawa użytkowania wieczystego ... – 2%"

* **4100 Recurrent property tax (pass 6 note, grade C)**: local: podatek od nieruchomości: per-m2 rates set by each gmina within the national maxima of the ustawa o podatkach i opłatach lokalnych (2025: business buildings PLN 34,00/m2); area inputs are not in the model (pass 6 note (PwC WWTS 2025 captures on disk))


## 4100 Podatek od nieruchomości (local-tax framework pass, grade B, framework (local rate input))
Source: EC Taxes in Europe Database (TEDB), tax 461, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21).
* rate: 'Rates are determined by council of local government, but in 2025, they cannot be higher then: ... PLN 0.73 for m2 of the area - for other land, PLN 1.19 for 1 m2 of the usable area - for residential buildings, PLN 34.00 ... for buildings related to economic activity'
* worked case: home of 70 m² at an example 1,00 zł/m²: 70 zł; land of 500 m² at 0,50 zł/m²: 250 zł
-/

namespace PlGlobal.Property
open TaxKernel TaxKernel.Global

def d0 : TransferDuty :=
  { name := "Podatek od czynności cywilnoprawnych (sprzedaż nieruchomości)",   sched := Schedule.flat 200,   kinds := [.home, .realEstate, .land] }
/-- A case entity from its JSON (local-tax framework pass guards). -/
def lfwG (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

/-- Podatek od nieruchomości (budynki mieszkalne) (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P0 : LocalTax :=
  { key := "propertyTax",   name := "Podatek od nieruchomości (budynki mieszkalne)",   base := .area [.home, .realEstate],   unit := .perUnit,   maxNum := 119,   maxDen := 100,   statute := "ustawa o podatkach i opłatach lokalnych (residential buildings: at most 1,19 zł/m² in 2025)" }

/-- Podatek od nieruchomości (grunty pozostałe) (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P1 : LocalTax :=
  { key := "propertyTaxLand",   name := "Podatek od nieruchomości (grunty pozostałe)",   base := .area [.land],   unit := .perUnit,   maxNum := 73,   maxDen := 100,   statute := "ustawa o podatkach i opłatach lokalnych (other land: at most 0,73 zł/m² in 2025)" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 transfer duties", covers := [.transactions],
     run := fun args g prev =>
       d0.charges g.purchases "ustawa o PCC art. 7 ust. 1 pkt 1 lit. a (2 %)" },
   { name := "4100 Podatek od nieruchomości (local rate input, framework pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       lfw4100P0.charges g
       ++ lfw4100P1.charges g }]

def absent : List Absent :=
  []

def notes : List String := ["PL 4400: t.j. Dz.U. 2024 poz. 295", "PL 4100 local-tax framework pass: Podatek od nieruchomości (framework (local rate input), B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty then ["sales subject to VAT (new dwellings from developers) are outside PCC (art. 2 pkt 4): not separated; 2025 amendments not checked; the 6 % rate for multiple dwellings not modelled"] else [])
  ++ lfw4100P0.unknown g
  ++ lfw4100P1.unknown g

#guard d0.amount { kind := .home, price := 200000 } == 4000
#guard d0.amount { kind := .home, price := 2000000 } == 40000
#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":600000,\"areaM2\":70}],\"localRates\":{\"propertyTax\":{\"rate\":1.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [70]
#guard ((lfw4100P1.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":100000,\"areaM2\":500}],\"localRates\":{\"propertyTaxLand\":{\"rate\":0.5,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [250]
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":600000,\"areaM2\":70}],\"localRates\":{\"propertyTax\":{\"rate\":1.25,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P0.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":600000,\"areaM2\":70}],\"localRates\":{\"propertyTax\":{\"rate\":1.25,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":600000,\"areaM2\":70}]}")).isEmpty

end PlGlobal.Property
