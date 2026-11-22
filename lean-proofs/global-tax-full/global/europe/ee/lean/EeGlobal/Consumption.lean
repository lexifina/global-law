import EeGlobal.Pit
import TaxKernel.Global2

/-!
# Estonia 2025: käibemaks (5111); excises not read

Source: Käibemaksuseadus, Riigi Teataja (official) as captured by the Internet Archive on 2025-08-07
(`ee/law/kmss_wb.html`, sha256 in `law/SHA256SUMS`; riigiteataja.ee itself answers scripts with Cloudflare).
* **§ 15 (1)**: "Käibemaksumäär on 24 protsenti maksustatavast väärtusest" (in force from 1 July 2025; 22 % in January
  to June 2025); **(1¹)** "13 protsenti majutuse"; **(2)** 9 %: "1) raamat ja õppekirjandus", "2) ... ravim",
  "5) ajakirjandusväljaanne" (from 1 January 2025).
* **§ 19 (1)**: registration when the year's turnover "ületab kalendriaasta algusest alates 40 000 eurot".


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), EE excise records for the situation on 1 July 2025 (tobacco 4070, alcohol 4068, energy 4069; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `ee/law/tedb_*.json`).
* TEDB EE beer (1.7.2025): 14 EUR per hl and % vol (= per litre of pure alcohol)
* TEDB EE still wine (1.7.2025): 162.97 EUR per hl of product
* TEDB EE ethyl alcohol (1.7.2025): 2074 EUR per hl of pure alcohol


## 5121 Aktsiisid, mille 2025. aasta määr muutus aasta jooksul (sigaretid, bensiin, diislikütus, kerge kütteõli) (gap pass 2) (gap pass, grade B)
Source: lexifina/estonia-law `riigikogu/seadused/2021/14-461-se.md` (commit 3b46bd43256), `2022/14-705-se.md` (f13f643b007), `2023/15-145-se.md` (887e9be568d), `2024/15-510-se.md` (e7971392636); every figure matches the TEDB at 1.1 and 1.7.2025.
* Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 56 lg 1, 1¹ (106,00 EUR / 1 000 + 30 % of the maximum retail price, at least 177,70; 145 SE § 1 p. 9, 12 from 1.1.2025)
* Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 56 lg 1, 1¹ (111,50 EUR / 1 000 + 30 %, at least 186,70; 145 SE § 1 p. 10, 13, brought forward to 1.7.2025 by 510 SE § 2 p. 3)
* Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 1 (563 EUR / 1 000 l: TEDB 1.1.2025; the act setting it not read)
* Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 1 (591 EUR / 1 000 l; 510 SE § 1 p. 21, § 4 (1): from 1.7.2025)
* Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 6 (399 EUR / 1 000 l; 461 SE § 1 p. 7)
* Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 6 (428 EUR / 1 000 l; 461 SE § 1 p. 8, § 4 (4) as moved to 1.5.2025 by 705 SE § 2 p. 2)
* Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 7¹ (399 EUR / 1 000 l; 461 SE § 1 p. 7)
* Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 7¹ (428 EUR / 1 000 l; 461 SE § 1 p. 8, § 4 (4), 705 SE § 2 p. 2: from 1.5.2025)
-/

namespace EeGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Käibemaks", standard := 2400, reduced := 1300, reduced2 := 900, threshold := 40000,
    classOf := fun gd => match gd with
      | .hotels => .reduced
      | .books | .medicines | .newspapers => .reduced2
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "Käibemaksuseadus § 15 (1) 24 % (from 1.7.2025), (1¹) 13 %, (2) 9 %; § 16 (maksuvabad); § 19 (1) (40 000 eurot)"

def excise : Excise :=
  { rates := [
      { good := .beer, name := "Excise duty on beer", perUnitNum := 14, onPureAlcohol := true, statute := "TEDB EE beer (1.7.2025): 14 EUR per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 16297, perUnitDen := 10000, statute := "TEDB EE still wine (1.7.2025): 162.97 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 1037, perUnitDen := 50, onPureAlcohol := true, statute := "TEDB EE ethyl alcohol (1.7.2025): 2074 EUR per hl of pure alcohol" }] }

/-- January-June 2025: standard rate 22 % (the § 15 (1) wording before RT I, 2024 amendment in force 1.7.2025). -/
def vatH1 : Vat := { vat with standard := 2200 }

/-- Kernel 2.1 `DatedVat`: 22 % to 30 June, 24 % from 1 July 2025; an undated basket is split by days. -/
def vatDated : DatedVat :=
  { periods := [{ vat := vatH1, statute := "Käibemaksuseadus § 15 (1) 22 % (to 30.6.2025)" },               { start := "2025-07-01", vat := vat, statute := "Käibemaksuseadus § 15 (1) 24 % (from 1.7.2025)" }],   undatedSupplies := .split }

/-- Aktsiisid, mille 2025. aasta määr muutus aasta jooksul (sigaretid, bensiin, diislikütus, kerge kütteõli) (gap pass 2; kernel 2.1 `ExciseRule` date windows). -/
def gxDated0 : ExciseRule :=
  { good := .cigarettes,   name := "Tubakaaktsiis (sigaretid)",   perUnitNum := 10600,   perUnitDen := 100000,   adValoremBp := 3000,   minNum := 17770,   minDen := 100000,   validTo := "2025-07-01",   statute := "Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 56 lg 1, 1¹ (106,00 EUR / 1 000 + 30 % of the maximum retail price, at least 177,70; 145 SE § 1 p. 9, 12 from 1.1.2025)" }
def gxDated1 : ExciseRule :=
  { good := .cigarettes,   name := "Tubakaaktsiis (sigaretid)",   perUnitNum := 11150,   perUnitDen := 100000,   adValoremBp := 3000,   minNum := 18670,   minDen := 100000,   validFrom := "2025-07-01",   statute := "Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 56 lg 1, 1¹ (111,50 EUR / 1 000 + 30 %, at least 186,70; 145 SE § 1 p. 10, 13, brought forward to 1.7.2025 by 510 SE § 2 p. 3)" }
def gxDated2 : ExciseRule :=
  { good := .petrol,   name := "Kütuseaktsiis (pliivaba bensiin)",   perUnitNum := 563,   perUnitDen := 1000,   validTo := "2025-07-01",   statute := "Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 1 (563 EUR / 1 000 l: TEDB 1.1.2025; the act setting it not read)" }
def gxDated3 : ExciseRule :=
  { good := .petrol,   name := "Kütuseaktsiis (pliivaba bensiin)",   perUnitNum := 591,   perUnitDen := 1000,   validFrom := "2025-07-01",   statute := "Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 1 (591 EUR / 1 000 l; 510 SE § 1 p. 21, § 4 (1): from 1.7.2025)" }
def gxDated4 : ExciseRule :=
  { good := .diesel,   name := "Kütuseaktsiis (diislikütus)",   perUnitNum := 399,   perUnitDen := 1000,   validTo := "2025-05-01",   statute := "Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 6 (399 EUR / 1 000 l; 461 SE § 1 p. 7)" }
def gxDated5 : ExciseRule :=
  { good := .diesel,   name := "Kütuseaktsiis (diislikütus)",   perUnitNum := 428,   perUnitDen := 1000,   validFrom := "2025-05-01",   statute := "Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 6 (428 EUR / 1 000 l; 461 SE § 1 p. 8, § 4 (4) as moved to 1.5.2025 by 705 SE § 2 p. 2)" }
def gxDated6 : ExciseRule :=
  { good := .heatingOil,   name := "Kütuseaktsiis (kerge kütteõli)",   perUnitNum := 399,   perUnitDen := 1000,   validTo := "2025-05-01",   statute := "Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 7¹ (399 EUR / 1 000 l; 461 SE § 1 p. 7)" }
def gxDated7 : ExciseRule :=
  { good := .heatingOil,   name := "Kütuseaktsiis (kerge kütteõli)",   perUnitNum := 428,   perUnitDen := 1000,   validFrom := "2025-05-01",   statute := "Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus § 66 lg 7¹ (428 EUR / 1 000 l; 461 SE § 1 p. 8, § 4 (4), 705 SE § 2 p. 2: from 1.5.2025)" }

def gxDatedRules : List ExciseRule := [gxDated0, gxDated1, gxDated2, gxDated3, gxDated4, gxDated5, gxDated6, gxDated7]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 käibemaks (two rate periods)", covers := [.excise, .vat],
     run := fun args g prev =>
       vatDated.charges g
       ++ excise.charges g.consumption
       ++ exciseRuleCharges gxDatedRules g }]

def absent : List Absent :=
  []

def notes : List String := ["EE 5111: standard rate 22 % to 30 June and 24 % from 1 July 2025 (kernel 2.1 DatedVat)", "EE 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)", "EE 5121 gap pass 2: Aktsiisid, mille 2025. aasta määr muutus aasta jooksul (sigaretid, bensiin, diislikütus, kerge kütteõli) (B, cigarettes and petrol from 1.7.2025, diesel and light heating oil from 1.5.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty then ["undated basket lines split by days between the 22 % and 24 % periods; the 22 % wording of § 15 (1) is taken from the rate change, not from a capture dated before July 2025"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus not read"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 EE: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 124 } == 24
#guard vat.embedded { good := .hotels, amount := 113 } == 13
#guard vat.embedded { good := .books, amount := 109 } == 9
#guard vat.net { turnover := 40000, sales := [{ good := .other, net := 40000 }] } == 0
#guard vatH1.embedded { good := .clothing, amount := 122 } == 22
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 70
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 162
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 829
#guard gxDated0.dutyOn { good := .cigarettes, amount := 5000, quantity := 1000000 } {} == 1606
#guard gxDated1.dutyOn { good := .cigarettes, amount := 5000, quantity := 1000000 } {} == 1611
#guard gxDated2.dutyOn { good := .petrol, amount := 1700, quantity := 1000000 } {} == 563
#guard gxDated3.dutyOn { good := .petrol, amount := 1700, quantity := 1000000 } {} == 591
#guard gxDated4.dutyOn { good := .diesel, amount := 1700, quantity := 1000000 } {} == 399
#guard gxDated5.dutyOn { good := .diesel, amount := 1700, quantity := 1000000 } {} == 428
#guard gxDated6.dutyOn { good := .heatingOil, amount := 1700, quantity := 1000000 } {} == 399
#guard gxDated7.dutyOn { good := .heatingOil, amount := 1700, quantity := 1000000 } {} == 428
#guard gxDated0.windowDays 2025 + gxDated1.windowDays 2025 == 365
#guard gxDated2.windowDays 2025 + gxDated3.windowDays 2025 == 365
#guard gxDated4.windowDays 2025 + gxDated5.windowDays 2025 == 365
#guard gxDated6.windowDays 2025 + gxDated7.windowDays 2025 == 365

end EeGlobal.Consumption
