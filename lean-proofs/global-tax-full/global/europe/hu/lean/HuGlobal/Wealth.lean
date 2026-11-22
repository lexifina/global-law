import HuGlobal.Pit

/-!
# HU 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Itv. 8-17. § (öröklési illeték, 18 %; close relatives exempt)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, HU, Individual - Other taxes, accessed  (live page; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes,  (live page))


## 4300 Öröklési illeték (pass 6)
Source: 1990. évi XCIII. törvény az illetékekről (Itv.), net.jogtar.hu `docid=99000093.tv` (`hu/law/itv.txt`).
* 12. § (1): "Az öröklési és az ajándékozási illeték általános mértéke ... az egy-egy örökösnek, hagyományosnak juttatott örökség és a megajándékozottnak juttatott ajándék tiszta értéke után 18%." (2): lakástulajdon "9%"
* 16. § (1) i): "az örökhagyó egyenes ági rokona ..., valamint túlélő házastársa által megszerzett örökrész"; j): "az örökhagyó testvére által megszerzett örökrész"; d): movables up to 300 000 Ft per heir
-/

namespace HuGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- Itv. 12. § (1) (18 %); 16. § (1) i)-j) (lineal relatives, surviving spouse, siblings exempt) -/
def p6oroklClass : Relation → Nat
  | _ => 0
def p6orokl : InheritanceTax :=
  { name := "Öröklési illeték", classOf := p6oroklClass,   classes := [{ allowance := 0, sched := Schedule.flat 1800 }],   exemptRelations := [.spouse, .child, .grandchild, .parent, .sibling], lookbackYears := 0,   exemptValue := fun t => if t.kind == .gift then pos t.statutoryValue else 0 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Öröklési illeték", covers := [.estate],
     run := fun args g prev =>
       p6orokl.charges g.transfers "Itv. 12. § (1) (18 %); 16. § (1) i)-j) (lineal relatives, surviving spouse, siblings exempt)" }]

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none" }]

def notes : List String := ["HU 4300 Öröklési illeték: net.jogtar.hu Hatályos Jogszabályok Gyűjteménye (current text, fetched 2026-11-21; provisions unchanged in 2025 not checked against the 2025 időállapot) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty then ["4300 the 9 % rate for a home (12. § (2)), the 300 000 Ft movables exemption (16. § (1) d)) and step-relatives' 20 000 000 Ft (c)) not applied"] else [])
  ++ (if g.transfers.any (·.kind == .gift) then ["4300 ajándékozási illeték (gifts, 11. §, exemptions in 17. §) not modelled"] else [])

#guard p6orokl.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6orokl.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 0
#guard p6orokl.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6orokl.tax { kind := .inheritance, value := 1000000, relation := .child } == 0
#guard p6orokl.tax { kind := .inheritance, value := 100000, relation := .sibling } == 0
#guard p6orokl.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 0
#guard p6orokl.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 18000
#guard p6orokl.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 180000
#guard p6orokl.tax { kind := .gift, value := 1000000, relation := .unrelated } == 0

end HuGlobal.Wealth
