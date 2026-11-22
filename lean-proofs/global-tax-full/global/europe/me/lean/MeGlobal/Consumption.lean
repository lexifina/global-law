import MeGlobal.Pit

/-!
# ME 2025: Porez na dodatu vrijednost (5111); excises not modelled in this pass

Source: PwC Worldwide Tax Summaries, Montenegro, Corporate - Other taxes, accessed 2025-07-18 (Wayback capture; `me/law/pwc_other_wb2025.html`); sha256 in `law/SHA256SUMS`.
* VAT 21 %; 15 %: books, publications, some hospitality and accommodation; 7 %: bread, flour, milk and dairy, schoolbooks, medicines, orthopaedic / prosthetic devices, public transport
* registration: turnover > EUR 30 000 in the last 12 months (PwC page reviewed 15 July 2025)
-/

namespace MeGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Porez na dodatu vrijednost", standard := 2100, reduced := 1500, reduced2 := 700, threshold := 30000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .books | .newspapers | .hotels => .reduced
      | .medicines | .transport => .reduced2
      | _ => .standard }

def vatStatute : String := "Zakon o porezu na dodatu vrijednost (21 %, 15 %, 7 %; registration above 30 000 EUR)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Porez na dodatu vrijednost", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["ME 5111: PwC, last reviewed 15 July 2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the EU-style structure the source describes (health, education, finance, insurance, residential rent), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food) then ["food at the standard rate: the reduced rate covers only bread, flour, milk and dairy products (7 %) (not separable in the basket's food line)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .restaurants) then ["restaurants at 21 %: the hospitality services at 15 % are not specified"] else [])
  ++ (if !g.consumption.isEmpty then ["the act's own text not reached: rates from PwC Worldwide Tax Summaries (reliable secondary host)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Zakon o akcizama (not read)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 12100 } == 2100
#guard vat.embedded { good := .books, amount := 11500 } == 1500
#guard vat.embedded { good := .medicines, amount := 10700 } == 700
#guard vat.net { turnover := 30000, sales := [{ good := .other, net := 30000 }] } == 0

end MeGlobal.Consumption
