import BaGlobal.Pit

/-!
# BA 2025: Porez na dodanu vrijednost (5111); excises not modelled in this pass

Source: PwC Worldwide Tax Summaries, Bosnia and Herzegovina, Corporate - Other taxes, accessed 2025-07-31 (Wayback capture; `ba/law/pwc_other_wb2025.html`); sha256 in `law/SHA256SUMS`.
* VAT 17 %, one rate in the whole country; no reduced rate
* registration: taxable supplies > BAM 100 000 (PwC page reviewed 6 February 2025)
-/

namespace BaGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Porez na dodanu vrijednost", standard := 1700, threshold := 100000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "Zakon o porezu na dodanu vrijednost BiH (17 %, no reduced rate; registration above BAM 100 000)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Porez na dodanu vrijednost", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["BA 5111: PwC, last reviewed 6 February 2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the EU-style structure the source describes (health, education, finance, insurance, residential rent), not quoted item by item"] else [])
  ++ (if !g.consumption.isEmpty then ["the act's own text not reached: rates from PwC Worldwide Tax Summaries (reliable secondary host)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Zakon o akcizama BiH (PwC: tobacco 42 % of retail price + BAM 0.75 a pack; not modelled)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 11700 } == 1700
#guard vat.net { turnover := 100000, sales := [{ good := .other, net := 100000 }] } == 0

end BaGlobal.Consumption
