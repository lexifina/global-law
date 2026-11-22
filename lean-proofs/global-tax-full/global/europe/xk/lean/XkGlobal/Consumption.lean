import XkGlobal.Pit

/-!
# XK 2025: Tatimi mbi vlerën e shtuar (5111); excises not modelled in this pass

Source: PwC Worldwide Tax Summaries, Kosovo, Corporate - Other taxes, accessed 2025-06-24 (Wayback capture; `xk/law/pwc_other_wb2025.html`); sha256 in `law/SHA256SUMS`.
* law: Ligji Nr. 05/L-037 për TVSH; registration: turnover > EUR 30 000 in a calendar year
* VAT 18 %; 8 %: water (not bottled), electricity, grains and grain products, dairy, textbooks and serials, library book lending, ... (PwC page reviewed 22 January 2025)


## 5111 TVSH: neni 26 read; medicines and newspapers moved to 8 % (stays B: amendments after 2015 not excluded) (gap pass, grade C)
Source: Gazeta Zyrtare e Republikës së Kosovës: Ligji nr. 06/L-105 për tatimin në të ardhurat e korporatave neni 7 and the withholding articles (commit 94aeb29291); Ligji nr. 05/L-037 për TVSH neni 26 (commit e9e51ada36, in force 1.9.2015), acts as enacted read from lexifina/kosovo-law.
* neni 26.1: standard rate 18 %; 26.2: 8 % on water (2.1), electricity and central heating (2.2), cereals, flour, bread, edible oils, dairy, salt and eggs (2.3-2.8), school books and serial publications (2.9), library books and printed matter (2.10), IT equipment (2.11), medicines and medical devices (2.12-2.13)
* Corrections: medicines and newspapers were charged 18 % (now 8 %)
-/

namespace XkGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Tatimi mbi vlerën e shtuar", standard := 1800, reduced := 800, threshold := 30000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .water | .electricity | .books | .medicines | .newspapers => .reduced
      | _ => .standard }

def vatStatute : String := "Ligji Nr. 05/L-037 për TVSH (18 %, 8 %; registration above EUR 30 000)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Tatimi mbi vlerën e shtuar", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["XK 5111: PwC, last reviewed 22 January 2025", "XK gap pass: 5111 TVSH: neni 26 read; medicines and newspapers moved to 8 % (stays B: amendments after 2015 not excluded)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the EU-style structure the source describes (health, education, finance, insurance, residential rent), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food) then ["food at the standard rate: the reduced rate covers only grain products, oils, dairy, salt and eggs (8 %) (not separable in the basket's food line)"] else [])
  ++ (if !g.consumption.isEmpty then ["the act's own text not reached: rates from PwC Worldwide Tax Summaries (reliable secondary host)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Ligji për akcizat (not read)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 11800 } == 1800
#guard vat.embedded { good := .water, amount := 10800 } == 800
#guard vat.net { turnover := 30000, sales := [{ good := .other, net := 30000 }] } == 0
#guard vat.embedded { good := .medicines, amount := 10800 } == 800

end XkGlobal.Consumption
