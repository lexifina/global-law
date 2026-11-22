import MkGlobal.Pit

/-!
# MK 2025: Данок на додадена вредност (5111); excises not modelled in this pass

Source: PwC Worldwide Tax Summaries, North Macedonia, Corporate - Other taxes, accessed 2025-08-10 (Wayback capture; `mk/law/pwc_other_wb2025.html`); sha256 in `law/SHA256SUMS`.
* VAT 18 %; preferential 5 % and 10 %
* 5 %: food, public drinking water, medicines and medical equipment, books / newspapers, household electricity, passenger transport, accommodation; 10 %: restaurant and catering services (alcohol excluded)
* registration: annual turnover > MKD 2 000 000 (PwC page reviewed 18 February 2025)
-/

namespace MkGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Данок на додадена вредност", standard := 1800, reduced := 500, reduced2 := 1000, threshold := 2000000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .water | .medicines | .books | .newspapers | .electricity | .transport | .hotels => .reduced
      | .restaurants => .reduced2
      | _ => .standard }

def vatStatute : String := "Закон за данокот на додадена вредност (18 %, 5 %, 10 %; registration above MKD 2 000 000)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Данок на додадена вредност", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["MK 5111: PwC, last reviewed 18 February 2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the EU-style structure the source describes (health, education, finance, insurance, residential rent), not quoted item by item"] else [])
  ++ (if !g.consumption.isEmpty then ["the act's own text not reached: rates from PwC Worldwide Tax Summaries (reliable secondary host)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Закон за акцизите (not read)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 11800 } == 1800
#guard vat.embedded { good := .food, amount := 10500 } == 500
#guard vat.embedded { good := .restaurants, amount := 11000 } == 1000
#guard vat.net { turnover := 2000000, sales := [{ good := .other, net := 2000000 }] } == 0

end MkGlobal.Consumption
