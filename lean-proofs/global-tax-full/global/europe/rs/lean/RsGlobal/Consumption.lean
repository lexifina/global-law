import RsGlobal.Pit

/-!
# RS 2025: Porez na dodatu vrednost (5111); excises not modelled in this pass

Source: Zakon o porezu na dodatu vrednost, consolidated text published by Paragraf (private publisher; the official Pravno-informacioni sistem is script-only), `rs/law/pdv.html`; sha256 in `law/SHA256SUMS`.
* čl. 23: "Opšta stopa PDV za oporezivi promet dobara i usluga ili uvoz dobara iznosi 20%"; "Po posebnoj stopi PDV od 10% oporezuje se ..."
* čl. 33: promet in the previous 12 months "nije veći od 8.000.000 dinara"


## 5111 PDV: 2025 text read (čl. 23), A; natural gas and passenger transport moved to 10 % (gap pass, grade C)
Source: Službeni glasnik RS, official consolidations (pravno-informacioni-sistem.rs) read from lexifina/serbia-law: Zakon o porezu na dodatu vrednost `zakon/2004/84-25/clan-023.md` (version of 1.7.2018, unchanged to 2026), Zakon o porezu na dobit pravnih lica čl. 39-40 (commit a90dae4616).
* čl. 23 st. 1: "Општа стопа ПДВ ... износи 20%"; st. 2: 10 % on basic foods (t. 1-2), medicines (t. 3), textbooks (t. 7), daily newspapers (t. 8), monographic and serial publications (t. 9), accommodation (t. 11), natural gas (t. 13), heat (t. 13а), piped drinking water (t. 15), passenger transport (t. 20)
* Corrections: natural gas and passenger transport were charged 20 % (now 10 %); electricity and restaurants stay at 20 % (not listed)
-/

namespace RsGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Porez na dodatu vrednost", standard := 2000, reduced := 1000, threshold := 8000000,
    classOf := fun gd => match gd with
      | .food | .medicines | .newspapers | .books | .hotels | .water | .gas | .transport => .reduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "Zakon o porezu na dodatu vrednost čl. 23 (20 %, 10 %); čl. 25 (oslobođenja); čl. 33 (8.000.000 dinara)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Porez na dodatu vrednost", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["RS 5111: consolidated text (Paragraf), current", "RS 5111 Porez na dodatu vrednost: back to B (pass 17, 2025 text read)", "RS gap pass: 5111 PDV: 2025 text read (čl. 23), A; natural gas and passenger transport moved to 10 %"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["food at 10 % (čl. 23 st. 2: bread, milk, flour, sugar, oils ...); other food 20 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Zakon o akcizama) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 12000 } == 2000
#guard vat.embedded { good := .food, amount := 11000 } == 1000
#guard vat.net { turnover := 8000000, sales := [{ good := .other, net := 8000000 }] } == 0
#guard vat.embedded { good := .gas, amount := 11000 } == 1000
#guard vat.embedded { good := .transport, amount := 11000 } == 1000

end RsGlobal.Consumption
