import NoGlobal.Pit

/-!
# NO 2025: Merverdiavgift (5111); excises not modelled in this pass

Source: Stortingsvedtak om merverdiavgift for 2025, Lovtidend (LTI/forskrift/2024-12-13-3208, lovdata.no, `no/law/stv_mva2025.html`); merverdiavgiftsloven (lov 19. juni 2009 nr. 58, lovdata.no current text, `no/law/mval.html`); sha256 in `law/SHA256SUMS`.
* § 1: "Fra 1. januar 2025 beregnes merverdiavgift etter satsene i dette vedtaket"; § 2: "Merverdiavgift beregnes med 25 pst. av avgiftspliktig omsetning ..."
* § 3: "15 pst. av omsetning, uttak og innførsel av næringsmidler som nevnt i merverdiavgiftsloven § 5-2"; § 4: "12 pst. ... a. persontransport mv. ... c. utleie av rom i hotellvirksomhet mv. ..."; § 5: 11,11 pst. viltlevende marine ressurser
* merverdiavgiftsloven § 2-1 (1): registration when turnover "har oversteget 50.000 kroner i en periode på tolv måneder"
-/

namespace NoGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Merverdiavgift", standard := 2500, reduced := 1500, reduced2 := 1200, threshold := 50000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .nonAlcoholic => .reduced
      | .transport | .hotels => .reduced2
      | _ => .standard }

def vatStatute : String := "Stortingsvedtak om merverdiavgift for 2025 (FOR-2024-12-13-3208) §§ 2-5; merverdiavgiftsloven § 2-1 (1) (50 000 kroner), § 5-2, kap. 3 (unntak)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Merverdiavgift", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["NO 5111: Stortingsvedtak for budsjettåret 2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .water) then ["water from waterworks at 25 % (the 15 % in vedtak II applies from a date the ministry sets)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Stortingsvedtak om særavgifter 2025 (not fetched)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 12500 } == 2500
#guard vat.embedded { good := .food, amount := 11500 } == 1500
#guard vat.embedded { good := .transport, amount := 11200 } == 1200
#guard vat.net { turnover := 50000, sales := [{ good := .other, net := 50000 }] } == 0

end NoGlobal.Consumption
