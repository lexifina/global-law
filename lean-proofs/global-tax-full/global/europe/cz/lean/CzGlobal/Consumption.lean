import CzGlobal.Pit

/-!
# Czechia 2025: daň z přidané hodnoty (5111) and spotřební daně (5121)

Sources: zákon č. 235/2004 Sb. (DPH) and č. 353/2003 Sb. (spotřební daně) in the wording in force on 1 July 2025
(`cz/law/dph_zneni-20250701.html` "235/2004 verze 68", `spd_zneni-20250701.html`) from zakonyprolidi.cz, a private
publisher of the consolidated texts (the official e-Sbírka serves script-only pages): structure and figures from the
statute, publisher not official: grade B.
* **DPH § 47 (1)**: "a) základní sazba daně ve výši 21 %, nebo b) snížená sazba daně ve výši 12 %"; (3) goods in
  příloha č. 3 (food, water, medicines ...), (4) services in příloha č. 2 (accommodation, restaurants, passenger
  transport ...) at the reduced rate. **§ 6 (1)**: a taxable person becomes a payer after a year "ve kterém její obrat
  v tuzemsku překročil částku 2000000 Kč". Exempt without credit: §§ 54-58 (financial, insurance, letting, education,
  health).
* **Spotřební daně § 48**: "motorové benziny ... s obsahem olova do 0,013 g/l včetně 12840 Kč/1000 l"; "střední oleje a
  těžké plynové oleje ... 9950 Kč/1000 l". **§ 84**: líh "39 100 Kč/hl etanolu". **§ 96**: "Tichá vína ... 0 Kč/hl".
  **§ 104 (1)**: cigarety "30 %", "2,28 Kč/kus", "celkem nejméně však 4,44 Kč/kus".

## FT review (2026-11-21, third pass): heating oil
Same text (`cz/law/spd_zneni-20250701.txt`). Gas oil (KN 2710 19 43 to 2710 19 48, 2710 20 11 to 2710 20 19) is a
"těžký plynový olej" of **§ 45 (1) b)** whatever its use; **§ 48 (1)**: "střední oleje a těžké plynové oleje podle § 45
odst. 1 písm. b) 9950 Kč/1000 l". There is no separate heating rate: **§ 56 (1), (6)** give a person who used such
marked and dyed oil "pro výrobu tepla" a refund ("Daň se vrací ve výši daně snížené o 660 Kč/1000 l"), claimed by a
quarterly return with records per heating device (§ 56 (7)-(10)). The household's `heatingOil` bears the § 48 rate in
its price; the § 56 refund is a claim the entity does not state (listed, not computed).
-/

namespace CzGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Daň z přidané hodnoty", standard := 2100, reduced := 1200, threshold := 2000000,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .water | .medicines | .hotels | .restaurants | .transport => .reduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "zákon 235/2004 Sb. § 47 (1), (3), (4), přílohy 2, 3; §§ 54-58; § 6 (1) (2 000 000 Kč)"

def excise : Excise :=
  { rates := [
      { good := .petrol, name := "Spotřební daň z minerálních olejů (benzin)", perUnitNum := 12840, perUnitDen := 1000, statute := "zákon 353/2003 Sb. § 48: 12 840 Kč / 1 000 l" },
      { good := .diesel, name := "Spotřební daň z minerálních olejů (nafta)", perUnitNum := 9950, perUnitDen := 1000, statute := "zákon 353/2003 Sb. § 48: 9 950 Kč / 1 000 l" },
      { good := .cigarettes, name := "Spotřební daň z tabákových výrobků (cigarety)", perUnitNum := 228, perUnitDen := 100, adValoremBp := 3000, minNum := 444, minDen := 100, statute := "zákon 353/2003 Sb. § 104 (1): 30 % + 2,28 Kč/kus, nejméně 4,44 Kč/kus" },
      { good := .spirits, name := "Spotřební daň z lihu", perUnitNum := 391, onPureAlcohol := true, statute := "zákon 353/2003 Sb. § 84: 39 100 Kč/hl etanolu" },
      { good := .wine, name := "Spotřební daň z vína (tichá vína)", statute := "zákon 353/2003 Sb. § 96: tichá vína 0 Kč/hl" },
      { good := .heatingOil, name := "Spotřební daň z minerálních olejů (topný plynový olej)", perUnitNum := 9950, perUnitDen := 1000, statute := "zákon 353/2003 Sb. § 45 (1) b), § 48 (1): 9 950 Kč / 1 000 l (§ 56 refund to 660 Kč on a claim not applied)" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 DPH, 5121 spotřební daně", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["CZ 5111/5121: wording in force 2025-07-01 (zakonyprolidi.cz)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .books || s.good == .newspapers) then ["books and press (§ 71i) not read: taken at 21 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer) then ["beer duty (§ 82: per degree of original wort extract) not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .heatingOil) then ["heating oil at the § 48 (1) gas-oil rate (9 950 Kč / 1 000 l); the § 56 refund for oil used to produce heat (down to 660 Kč / 1 000 l, claimed by quarterly return) not applied"] else [])

#guard vat.embedded { good := .clothing, amount := 121 } == 21
#guard vat.embedded { good := .food, amount := 112 } == 12
#guard vat.net { turnover := 2000000, sales := [{ good := .other, net := 2000000 }] } == 0
#guard excise.duty { good := .petrol, amount := 40000, quantity := 1000000 } == 12840
#guard excise.duty { good := .diesel, amount := 40000, quantity := 1000000 } == 9950
-- 1 000 cigarettes at 5 000 Kč: 1 500 + 2 280 < 4 440 (the minimum binds); at 9 000 Kč: 2 700 + 2 280
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 4440
#guard excise.duty { good := .cigarettes, amount := 9000, quantity := 1000000 } == 4980
#guard excise.duty { good := .spirits, amount := 30000, quantity := 100000, abvBp := 4000 } == 15640
#guard excise.duty { good := .heatingOil, amount := 30000, quantity := 1000000 } == 9950

end CzGlobal.Consumption
