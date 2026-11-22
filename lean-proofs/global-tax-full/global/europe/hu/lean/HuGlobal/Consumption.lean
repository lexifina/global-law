import HuGlobal.Pit

/-!
# HU 2025: Általános forgalmi adó (5111); excises not modelled in this pass

Source: 2007. évi CXXVII. törvény az általános forgalmi adóról, net.jogtar.hu (Wolters Kluwer, private publisher of the consolidated text; njt.hu reset the connection), `hu/law/afa.html`; sha256 in `law/SHA256SUMS`.
* 82. § (1): "Az adó mértéke az adó alapjának 27 százaléka"
* (2) "A 3. számú mellékletben felsorolt termékek, szolgáltatások esetében ... 5 százaléka"
* (3) "A 3/A. számú mellékletben ... 18 százaléka"

## FT review (2026-11-21, second pass): daily newspapers and commercial accommodation (ftd_ec_tedb_vat_2025 dev failures)
Same text (`hu/law/afa.txt`, net.jogtar.hu, with its amendment notes in `afa.html`):
* **82. § (4)**: "A 3/B. számú mellékletben felsorolt termékek esetében az adó mértéke az adó alapjának 0 százaléka."
  **3/B. számú melléklet 1.**: "Napilap (hetenként legalább négyszer megjelenő kiadvány)" (vtsz. 4902-ből); inserted
  by 2023. évi LIX. törvény 68. §, 3. melléklet, in force from 2024-01-01 (the transitional rule: "a 3/B. számú
  mellékletben foglalt táblázat 1. pontját ... 2024. január 1-jére vagy azt követő időpontra esik"). The household's
  `newspapers` is read as daily newspapers; periodicals ("Folyóirat, más újság", 3. melléklet I. 16.) stay 5 %.
  Items 2-3 of 3/B (prescription-only medicines) were inserted by 2026. évi XL. törvény from 2026-09-01: not 2025.
* **82. § (2)** with **3. melléklet II. rész 5.**: "Kereskedelmi szálláshely-szolgáltatás" at 5 % (established by
  2018. évi XLI. törvény 88. §, 10. melléklet); the model had accommodation at 18 % (3/A., whose II. 1. is repealed).


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), HU excise records for the situation on 1 July 2025 (tobacco 4088, alcohol 4085; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `hu/law/tedb_*.json`).
* TEDB HU manufactured tobacco (1.7.2025): 32300 HUF per 1 000 cigarettes + 24.0 % of the retail selling price, at least 45200 HUF per 1 000
* TEDB HU beer (1.7.2025): 1870 HUF per hl and % vol (= per litre of pure alcohol)
* TEDB HU still wine (1.7.2025): 0 HUF per hl of product
* TEDB HU ethyl alcohol (1.7.2025): 589040 HUF per hl of pure alcohol
-/

namespace HuGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Általános forgalmi adó", standard := 2700, reduced := 1800, superReduced := 500, threshold := 0,
    classOf := fun gd => match gd with
      | .medicines | .books | .restaurants | .hotels => .superReduced
      | .newspapers => .zero
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "2007. évi CXXVII. törvény 82. § (1) 27 %, (2) 5 % (3. melléklet, II. 5. szálláshely), (3) 18 % (3/A. melléklet), (4) 0 % (3/B. melléklet 1. napilap, from 2024-01-01); 85.-86. § (mentes)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 323, perUnitDen := 10, adValoremBp := 2400, minNum := 226, minDen := 5, statute := "TEDB HU manufactured tobacco (1.7.2025): 32300 HUF per 1 000 cigarettes + 24.0 % of the retail selling price, at least 45200 HUF per 1 000" },
      { good := .beer, name := "Excise duty on beer", perUnitNum := 1870, onPureAlcohol := true, statute := "TEDB HU beer (1.7.2025): 1870 HUF per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", statute := "TEDB HU still wine (1.7.2025): 0 HUF per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 29452, perUnitDen := 5, onPureAlcohol := true, statute := "TEDB HU ethyl alcohol (1.7.2025): 589040 HUF per hl of pure alcohol" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Általános forgalmi adó", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["HU 5111: consolidated text (jogtar), current", "HU 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["food at 27 %; milk, eggs, pork, poultry and other 3. melléklet foods are 5 %"] else [])
  ++ (if g.entity == .company then ["alanyi adómentesség (small-business exemption, 188. §) not read: no threshold applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Jövedéki adóról szóló 2016. évi LXVIII. törvény) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .newspapers) then ["newspapers read as daily newspapers (0 %, 3/B. 1.); periodicals 5 % (3. melléklet I. 16.) not distinguished"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .heatingOil) then ["5121 HU fuel excise not modelled: the rate depends on the world market crude oil price (Jöt. 120. §, two rates in the TEDB)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 HU: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12700 } == 2700
#guard vat.embedded { good := .medicines, amount := 10500 } == 500
#guard vat.embedded { good := .hotels, amount := 10500 } == 500
#guard vat.embedded { good := .newspapers, amount := 10500 } == 0
#guard vat.embedded { good := .restaurants, amount := 10500 } == 500
#guard vat.embedded { good := .transport, amount := 12700 } == 2700
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 45200
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 9350
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 0
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 235616

end HuGlobal.Consumption
