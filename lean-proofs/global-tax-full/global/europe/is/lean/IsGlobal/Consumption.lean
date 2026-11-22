import IsGlobal.Pit

/-!
# IS 2025: Virðisaukaskattur (5111); excises not modelled in this pass

Source: Lög nr. 50/1988 um virðisaukaskatt, althingi.is (official) as captured by the Internet Archive on 2025-09-04 (`is/law/vsk_wb.html`); sha256 in `law/SHA256SUMS`.
* 14. gr.: "Virðisaukaskattur skal vera [24%]"; "skal virðisaukaskattur af sölu á eftirtalinni vöru og þjónustu vera [11%]: 1. Fólksflutningar ... 2. Útleiga hótel- og gistiherbergja ... 5. Sala ... tímarita, dagblaða ... 6. Sala bóka ... 7. Sala á heitu vatni, rafmagni og olíu til hitunar húsa" (and food, item not quoted)
* 4. gr. 3. tölul.: "Þeir sem selja skattskylda vöru eða þjónustu fyrir [2.000.000 kr.]"
-/

namespace IsGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Virðisaukaskattur", standard := 2400, reduced := 1100, threshold := 2000000,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .transport | .hotels | .books | .newspapers | .electricity | .heatingOil => .reduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "Lög nr. 50/1988 um virðisaukaskatt 14. gr. (24 %, 11 %); 2. gr. 3. mgr. (undanþegið); 4. gr. 3. tölul. (2.000.000 kr.)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Virðisaukaskattur", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["IS 5111: althingi.is via Internet Archive 2025-09-04"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food || s.good == .nonAlcoholic) then ["food and non-alcoholic drinks at 11 % (14. gr. 2. mgr. item not quoted)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Lög nr. 96/1995 um gjald af áfengi og tóbaki; lög nr. 87/2004 um olíugjald) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 12400 } == 2400
#guard vat.embedded { good := .food, amount := 11100 } == 1100
#guard vat.net { turnover := 2000000, sales := [{ good := .other, net := 2000000 }] } == 0

end IsGlobal.Consumption
