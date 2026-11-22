import NlGlobal.Pit
import TaxKernel.Global2

/-!
# NL 2025: transfer duties on purchases (4400); recurrent property tax not modelled

Source: Wet op belastingen van rechtsverkeer (BWBR0002740), wetten.overheid.nl geldend 2025 (`nl/law/wbrv_g2025.html`); sha256 in `law/SHA256SUMS`.
* art. 14: "1 De belasting bedraagt 10,4 percent. 2 In afwijking van het eerste lid bedraagt de belasting 2 percent voor de verkrijging" of a dwelling the acquirer will occupy as main residence
* art. 15 lid 1 onderdeel p (startersvrijstelling): exempt for a first home, buyer under 35, value "niet uitkomt boven € 525.000"


## 4100 Onroerendezaakbelastingen (eigenaren, woningen) (local-tax framework pass, grade B, framework (local rate input))
Source: EC Taxes in Europe Database (TEDB), tax 3828, situation 01/01/2025 (rest-api/tax/rate and legalBase, harvested 2026-11-21).
* legal base: 'Legal base is set by the central government. The municipalities value the real estate and set the rate of the tax.'
* rate: 'A percentage of the value of the real estate, the so called WOZ-waarde.'
* worked case: home with WOZ value 400 000 EUR at an example 0,04 %: 160 EUR
-/

namespace NlGlobal.Property
open TaxKernel TaxKernel.Global

def d0 : TransferDuty :=
  { name := "Overdrachtsbelasting (woning)",
    sched := Schedule.flat 200,
    kinds := [.home],
    firstHomeCap := 525000,
    firstHomeSched := Schedule.flat 0,
    additionalBp := 840 }

def d1 : TransferDuty :=
  { name := "Overdrachtsbelasting (overig)",
    sched := Schedule.flat 1040,
    kinds := [.realEstate, .land] }
/-- A case entity from its JSON (local-tax framework pass guards). -/
def lfwG (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

/-- OZB eigenaren (woningen) (kernel 2.8.0 `LocalTax`, local-tax framework pass). -/
def lfw4100P0 : LocalTax :=
  { key := "propertyTax",
    name := "OZB eigenaren (woningen)",
    base := .assets [.home, .realEstate],
    unit := .percent,
    statute := "Gemeentewet art. 220-220h (rate % of the WOZ value; no statutory maximum)" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 transfer duties", covers := [.transactions],
     run := fun args g prev =>
       d0.charges g.purchases "WBR art. 14 lid 1 (10,4 %), lid 2 (2 % own dwelling); art. 15 lid 1 onderdeel p (starters, ≤ € 525.000)"
       ++ d1.charges g.purchases "WBR art. 14 lid 1 (10,4 %)" },
   { name := "4100 Onroerendezaakbelastingen (eigenaren, woningen) (local rate input, framework pass)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       lfw4100P0.charges g }]

def absent : List Absent :=
  []

def notes : List String := ["NL 4400: wetten.overheid.nl geldend 2025", "NL 4100 local-tax framework pass: Onroerendezaakbelastingen (eigenaren, woningen) (framework (local rate input), B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.purchases.any (·.firstHome) then ["startersvrijstelling assumes the buyer is 18-34 and never used it"] else [])
  ++ (if g.purchases.any (·.additionalHome) then ["a home not occupied by the buyer: 10,4 % (2 % + 8,4 points)"] else [])
  ++ lfw4100P0.unknown g

#guard d0.amount { kind := .home, price := 200000 } == 4000
#guard d0.amount { kind := .home, price := 2000000 } == 40000
#guard d0.amount { kind := .home, price := 525000, firstHome := true } == 0
#guard d0.amount { kind := .home, price := 525001, firstHome := true } == 10500
#guard d0.amount { kind := .home, price := 300000, additionalHome := true } == 31200
#guard d1.amount { kind := .realEstate, price := 200000 } == 20800
#guard d1.amount { kind := .realEstate, price := 2000000 } == 208000
#guard ((lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":450000,\"assessed\":400000}],\"localRates\":{\"propertyTax\":{\"rate\":0.04,\"source\":\"worked case (example rate, not a decision)\",\"date\":\"2025-01-01\",\"municipality\":\"(case input)\"}}}")).map (·.due)) == [160]
#guard (lfw4100P0.charges (lfwG "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"assets\":[{\"kind\":\"home\",\"value\":450000,\"assessed\":400000}]}")).isEmpty

end NlGlobal.Property
