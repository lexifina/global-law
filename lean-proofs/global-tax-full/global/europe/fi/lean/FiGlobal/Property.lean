import FiGlobal.Pit
import TaxKernel.Global2

/-!
# FI 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Varainsiirtoverolaki (3 % / 1,5 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Kiinteistöverolaki (Helsinki)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4100 Recurrent property tax (pass 6 note, grade C)**: Kiinteistöverolaki (Helsinki): kiinteistövero: rates set by each municipality within the Kiinteistöverolaki bands; reference municipality's rates not read (pass 6 note (PwC WWTS 2025 captures on disk))


## 4400 Varainsiirtovero (kiinteistö) (pass 6)
Source: Varainsiirtoverolaki 931/1996, Finlex ajantasalainsäädäntö, Wayback capture 2025-06-25 (`fi/law/vvl_wb2025.txt`).
* 6 § 1 mom.: "Kiinteistön luovutuksessa vero on kolme prosenttia kauppahinnasta tai muun vastikkeen arvosta." (21.12.2023/1185, in force 1.1.2024; before: 4 prosenttia)
* 20 § 1 mom.: "Arvopaperin luovutuksessa vero on 1,5 prosenttia kauppahinnasta tai muun vastikkeen arvosta." (1185/2023; before: 1,6); 3 mom. (2,0 % for housing-company shares) amended by 1185/2023
* 11 § (ensiasunnon verovapaus) repealed by 1185/2023


## 4100 Kiinteistövero, vakituinen asuinrakennus (rate as input) (gap pass, grade C)
Source: Kiinteistöverolaki (654/1992) 12 § (vakituinen asuinrakennus 0,41-1,00 %); the general rate and other buildings not modelled.
* rate as input: localRates.propertyTax {rate, source, date, municipality}; no rate given: grade C note per item


## 4100 Kiinteistövero (local-tax framework pass, grade B, framework (local rate input))
Source: EC Taxes in Europe Database (TEDB), tax 262, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21).
* rate: 'The general rate for buildings may vary between 0.93 % and 2.00 %, the general rate for land may vary between 1.30 % and 2.00 % whereas the rate for permanent residences may vary between 0.41 % and 1.0 %. ... buildings used as second residences ... between 0.93 % and 2.00 %'
* worked case: home (permanent residence) with taxable value 200 000 EUR at an example 0,41 %: 820; other building 100 000 at 1,00 %: 1 000; land 50 000 at 1,30 %: 650
-/

namespace FiGlobal.Property
open TaxKernel TaxKernel.Global

/-- Varainsiirtoverolaki 931/1996 6 § 1 mom. (3 % of the price, L 1185/2023 from 1.1.2024); 20 § 1 mom. (1,5 % on securities) -/
def p6vvl : TransferDuty := { name := "Varainsiirtovero (kiinteistö)", sched := Schedule.flat 300, kinds := [.realEstate, .land, .home] }


/-- A case entity from its JSON (local-tax framework pass guards). -/
def lfwG (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

/-- Kiinteistövero, vakituinen asuinrakennus (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P0 : LocalTax :=
  { key := "propertyTax",   name := "Kiinteistövero, vakituinen asuinrakennus",   base := .assets [.home],   unit := .percent,   minNum := 41,   minDen := 100,   maxNum := 1,   maxDen := 1,   statute := "Kiinteistöverolaki (permanent residence 0,41-1,00 %)" }

/-- Kiinteistövero, muut rakennukset (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P1 : LocalTax :=
  { key := "propertyTaxOtherBuildings",   name := "Kiinteistövero, muut rakennukset",   base := .assets [.realEstate],   unit := .percent,   minNum := 93,   minDen := 100,   maxNum := 2,   maxDen := 1,   statute := "Kiinteistöverolaki (general rate for buildings, second residences 0,93-2,00 %)" }

/-- Kiinteistövero, maapohja (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P2 : LocalTax :=
  { key := "propertyTaxLand",   name := "Kiinteistövero, maapohja",   base := .assets [.land],   unit := .percent,   minNum := 130,   minDen := 100,   maxNum := 2,   maxDen := 1,   statute := "Kiinteistöverolaki (general rate for land 1,30-2,00 %)" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Varainsiirtovero (kiinteistö)", covers := [.transactions],
     run := fun args g prev =>
       p6vvl.charges g.purchases "Varainsiirtoverolaki 931/1996 6 § 1 mom. (3 % of the price, L 1185/2023 from 1.1.2024); 20 § 1 mom. (1,5 % on securities)" },
   { name := "4100 Kiinteistövero (local rate input, framework pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       lfw4100P0.charges g
       ++ lfw4100P1.charges g
       ++ lfw4100P2.charges g }]

def absent : List Absent :=
  []

def notes : List String := ["FI 4400 Varainsiirtovero (kiinteistö): Finlex ajantasa, Wayback capture 2025-06-25 (`fi/law/vvl_wb2025.txt`) (grade A)", "FI 4100 local-tax framework pass: Kiinteistövero (framework (local rate input), B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.purchases.any (·.kind == .home) then ["4400 a home bought as housing-company shares (asunto-osake) bears 1,5 % (20 §), a detached house 3 % (6 §): the input does not say which; 3 % applied"] else [])
  ++ (if g.purchases.any (·.firstHome) then ["4400 no first-home exemption: 11 § repealed from 1.1.2024 (L 1185/2023)"] else [])
  ++ lfw4100P0.unknown g
  ++ lfw4100P1.unknown g
  ++ lfw4100P2.unknown g

#guard p6vvl.amount { kind := .realEstate, price := 200000 } == 6000
#guard p6vvl.amount { kind := .realEstate, price := 2000000 } == 60000
#guard p6vvl.amount { kind := .vehicle, price := 100000 } == 0
#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":250000,\"assessed\":200000}],\"localRates\":{\"propertyTax\":{\"rate\":0.41,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [820]
#guard ((lfw4100P1.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"realEstate\",\"value\":150000,\"assessed\":100000}],\"localRates\":{\"propertyTaxOtherBuildings\":{\"rate\":1.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [1000]
#guard ((lfw4100P2.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":60000,\"assessed\":50000}],\"localRates\":{\"propertyTaxLand\":{\"rate\":1.3,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [650]
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":250000,\"assessed\":200000}],\"localRates\":{\"propertyTax\":{\"rate\":1.2,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P0.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":250000,\"assessed\":200000}],\"localRates\":{\"propertyTax\":{\"rate\":1.2,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1
#guard (lfw4100P2.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":60000,\"assessed\":50000}],\"localRates\":{\"propertyTaxLand\":{\"rate\":1.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).isEmpty && (lfw4100P2.unknown (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"land\",\"value\":60000,\"assessed\":50000}],\"localRates\":{\"propertyTaxLand\":{\"rate\":1.0,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).length == 1

end FiGlobal.Property
