import AlGlobal.Pit

/-!
# AL 2025: Tatimi mbi vlerën e shtuar (5111); excises not modelled in this pass

Source: PwC Worldwide Tax Summaries, Albania, Corporate - Other taxes, accessed 2025-08-03 (Wayback capture; `al/law/pwc_other_wb2025.html`); sha256 in `law/SHA256SUMS`.
* VAT 20 %; registration: annual turnover > ALL 10 000 000
* 6 %: accommodation, certified agritourism, audiovisual advertising, books, ... (PwC page reviewed 30 June 2025)
-/

namespace AlGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Tatimi mbi vlerën e shtuar", standard := 2000, reduced := 600, threshold := 10000000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .hotels | .books => .reduced
      | _ => .standard }

def vatStatute : String := "Ligji për TVSH (20 %, 6 %; registration above ALL 10 000 000)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Tatimi mbi vlerën e shtuar", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["AL 5111: PwC, last reviewed 30 June 2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the EU-style structure the source describes (health, education, finance, insurance, residential rent), not quoted item by item"] else [])
  ++ (if !g.consumption.isEmpty then ["the act's own text not reached: rates from PwC Worldwide Tax Summaries (reliable secondary host)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Ligji për akcizat (not read)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 12000 } == 2000
#guard vat.embedded { good := .hotels, amount := 10600 } == 600
#guard vat.net { turnover := 10000000, sales := [{ good := .other, net := 10000000 }] } == 0

end AlGlobal.Consumption
