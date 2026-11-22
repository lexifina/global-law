import SiGlobal.Pit

/-!
# SI 2025: Davek na dodano vrednost (5111); excises not modelled in this pass

Source: rates: FURS (Finančna uprava, official guide) "Stopnje DDV", 11. izdaja, April 2025, as captured by the Internet Archive on 2025-06-01 (`si/law/furs_stopnje_ddv_wb20250601.docx`); threshold: ZDDV-1O, Uradni list RS 104/2024 (Wayback 2025-12-14, `si/law/zddv1o_ul104_2024_wb.html`); the act's own čl. 41 not reached (pisrs.si script-only); sha256 in `law/SHA256SUMS`.
* FURS: "DDV se obračunava in plačuje po splošni, 22 % stopnji od davčne osnove ... za dobave blaga in storitev iz Priloge I k ZDDV-1 ... po nižji, 9,5 % stopnji ..., za dobave blaga in storitev iz Priloge IV pa po posebni nižji stopnji 5 %"; Priloga I: "HRANA (VKLJUČNO S PIJAČO, RAZEN ALKOHOLNIH PIJAČ IN PIJAČ Z DODANIM SLADKORJEM ...)"; Priloga IV: "DOBAVA KNJIG, ČASOPISOV, PERIODIČNIH PUBLIKACIJ"
* ZDDV-1O: a taxable person "ki utemeljeno pričakuje, da v tekočem koledarskem letu ne bo presegel zneska 60.000 eurov letnega prometa" (čl. 94 threshold from 1.1.2025)


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), SI excise records for the situation on 1 July 2025 (tobacco 4152, alcohol 4150, energy 4151; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `si/law/tedb_*.json`).
* TEDB SI still wine (1.7.2025): 0 EUR per hl of product
* TEDB SI energy products (1.7.2025): unleaded petrol 496.93 EUR per 1 000 l
-/

namespace SiGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Davek na dodano vrednost", standard := 2200, reduced := 950, superReduced := 500, threshold := 60000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .water | .medicines | .transport | .restaurants | .hotels => .reduced
      | .books | .newspapers => .superReduced
      | _ => .standard }

def vatStatute : String := "ZDDV-1 čl. 41 (22 %, 9,5 %, 5 %; Priloga I, Priloga IV), čl. 94 (1) (60.000 eurov, ZDDV-1O, Uradni list RS 104/2024)"

def excise : Excise :=
  { rates := [
      { good := .wine, name := "Excise duty on still wine", statute := "TEDB SI still wine (1.7.2025): 0 EUR per hl of product" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 49693, perUnitDen := 100000, statute := "TEDB SI energy products (1.7.2025): unleaded petrol 496.93 EUR per 1 000 l" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Davek na dodano vrednost", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["SI 5111: FURS guide April 2025; ZDDV-1O in force 1.1.2025", "SI 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .nonAlcoholic) then ["non-alcoholic drinks at 22 % (drinks with added sugar left Priloga I in 2025; unsweetened drinks are 9,5 %)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Zakon o trošarinah (not read)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .beer || s.good == .spirits || s.good == .diesel || s.good == .heatingOil) then ["5121 SI: excise on cigarettes, beer, spirits, diesel, heatingOil not charged: the 2025 rate changed during the year and the purchase is undated (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 SI: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12200 } == 2200
#guard vat.embedded { good := .food, amount := 10950 } == 950
#guard vat.embedded { good := .books, amount := 10500 } == 500
#guard vat.net { turnover := 60000, sales := [{ good := .other, net := 60000 }] } == 0
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 0
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 496

end SiGlobal.Consumption
