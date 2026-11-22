import MdGlobal.Pit

/-!
# MD 2025: Taxa pe valoarea adăugată (5111); excises not modelled in this pass

Source: PwC Worldwide Tax Summaries, Moldova, Corporate - Other taxes, accessed 2025-05-25 (Wayback capture; `md/law/pwc_other_wb2025.html`); sha256 in `law/SHA256SUMS`.
* VAT 20 %; 8 %: bread and bakery products, milk and dairy, ...; hotels, restaurants, cafes 8 % (12 % before 10.8.2023)
* registration: turnover ≥ MDL 1 200 000 in the last 12 months (PwC page reviewed 20 January 2025)
-/

namespace MdGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Taxa pe valoarea adăugată", standard := 2000, reduced := 800, threshold := 1200000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .hotels | .restaurants => .reduced
      | _ => .standard }

def vatStatute : String := "Codul fiscal Titlul III art. 96 (20 %, 8 %); registration at MDL 1 200 000"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Taxa pe valoarea adăugată", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["MD 5111: PwC, last reviewed 20 January 2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the EU-style structure the source describes (health, education, finance, insurance, residential rent), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food) then ["food at the standard rate: the reduced rate covers only bread, bakery and dairy products (8 %) (not separable in the basket's food line)"] else [])
  ++ (if !g.consumption.isEmpty then ["the act's own text not reached: rates from PwC Worldwide Tax Summaries (reliable secondary host)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Codul fiscal Titlul IV (not read)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 12000 } == 2000
#guard vat.embedded { good := .hotels, amount := 10800 } == 800
#guard vat.net { turnover := 1200000, sales := [{ good := .other, net := 1200000 }] } == 0

end MdGlobal.Consumption
