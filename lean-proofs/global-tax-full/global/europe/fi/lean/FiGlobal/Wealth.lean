import FiGlobal.Pit

/-!
# FI 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Perintö- ja lahjaverolaki 378/1940): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Finland, Individual - Other taxes, accessed 2025-06-13 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes, 2025-06-13 (Wayback capture))


## 4300 Perintövero (veroluokka I) (pass 6)
Source: PwC Worldwide Tax Summaries, Finland, Individual - Other taxes, accessed 2025-06-13 (Wayback capture; `law/pwc_indother_wb2025.txt`).
* inheritance tax class I (spouse, parents, lineal descendants, spouse's descendants): EUR 20 000-40 000: 100 + 7 %; 40 000-60 000: 1 500 + 10 %; 60 000-200 000: 3 500 + 13 %; 200 000-1 000 000: 21 700 + 16 %; above: 149 700 + 19 %
* the EUR 100 at 20 000 is written as a 1-euro band at 1 000 000 bp (19 999 to 20 000), so a value of exactly 20 000 bears 100 instead of 0


## 4300 Lahjavero (veroluokka I) (pass 6)
Source: PwC Worldwide Tax Summaries, Finland, Individual - Other taxes, accessed 2025-06-13 (Wayback capture; `law/pwc_indother_wb2025.txt`).
* gift tax class I: EUR 5 000-25 000: 100 + 8 %; to 55 000: 10 %; to 200 000: 12 %; to 1 000 000: 15 %; above: 17 %; same-donor gifts aggregated over 3 years
-/

namespace FiGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- Perintö- ja lahjaverolaki 14 § (veroluokka I scale) -/
def p6perintClass : Relation → Nat
  | _ => 0
def p6perint : InheritanceTax :=
  { name := "Perintövero (veroluokka I)", classOf := p6perintClass,   classes := [{ allowance := 0, sched := Schedule.ofList [(0, 0), (19999, 1000000), (20000, 700), (40000, 1000), (60000, 1300), (200000, 1600), (1000000, 1900)] }],   exemptRelations := [], lookbackYears := 0,   exemptValue := fun t => if t.kind == .gift then pos t.statutoryValue else 0 }

/-- Perintö- ja lahjaverolaki 14 § (veroluokka I gift scale) -/
def p6lahjaClass : Relation → Nat
  | _ => 0
def p6lahja : InheritanceTax :=
  { name := "Lahjavero (veroluokka I)", classOf := p6lahjaClass,   classes := [{ allowance := 0, sched := Schedule.ofList [(0, 0), (4999, 1000000), (5000, 800), (25000, 1000), (55000, 1200), (200000, 1500), (1000000, 1700)] }],   exemptRelations := [], lookbackYears := 3,   exemptValue := fun t => if t.kind == .gift then 0 else pos t.statutoryValue }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Perintövero (veroluokka I)", covers := [.estate],
     run := fun args g prev =>
       p6perint.charges g.transfers "Perintö- ja lahjaverolaki 14 § (veroluokka I scale)" },
   { name := "4300 Lahjavero (veroluokka I)", covers := [.estate],
     run := fun args g prev =>
       p6lahja.charges g.transfers "Perintö- ja lahjaverolaki 14 § (veroluokka I gift scale)" }]

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none" }]

def notes : List String := ["FI 4300 Perintövero (veroluokka I): PwC WWTS Individual - Other taxes, 2025-06-13 (Wayback capture) (grade B)", "FI 4300 Lahjavero (veroluokka I): PwC WWTS Individual - Other taxes, 2025-06-13 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (fun t => t.kind == .inheritance && !(t.relation == .spouse || t.relation == .child || t.relation == .grandchild || t.relation == .parent)) then ["4300 veroluokka II (other relatives and unrelated persons: higher scale) is not in the B source: the class I scale is applied (understates)"] else [])
  ++ (if !g.transfers.isEmpty then ["4300 the spouse's EUR 90 000 and minor child's EUR 60 000 deductions (PerVL 26 §) are not in the B source"] else [])
  ++ (if g.transfers.any (fun t => t.kind == .gift && !(t.relation == .spouse || t.relation == .child || t.relation == .grandchild || t.relation == .parent)) then ["4300 gift tax class II not in the B source: the class I scale is applied (understates)"] else [])

#guard p6perint.tax { kind := .inheritance, value := 100000, relation := .spouse } == 8700
#guard p6perint.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 149700
#guard p6perint.tax { kind := .inheritance, value := 100000, relation := .child } == 8700
#guard p6perint.tax { kind := .inheritance, value := 1000000, relation := .child } == 149700
#guard p6perint.tax { kind := .inheritance, value := 100000, relation := .sibling } == 8700
#guard p6perint.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 149700
#guard p6perint.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 8700
#guard p6perint.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 149700
#guard p6perint.tax { kind := .gift, value := 1000000, relation := .unrelated } == 0
#guard p6lahja.tax { kind := .gift, value := 100000, relation := .spouse } == 10100
#guard p6lahja.tax { kind := .gift, value := 1000000, relation := .spouse } == 142100
#guard p6lahja.tax { kind := .gift, value := 100000, relation := .child } == 10100
#guard p6lahja.tax { kind := .gift, value := 1000000, relation := .child } == 142100
#guard p6lahja.tax { kind := .gift, value := 100000, relation := .sibling } == 10100
#guard p6lahja.tax { kind := .gift, value := 1000000, relation := .sibling } == 142100
#guard p6lahja.tax { kind := .gift, value := 100000, relation := .unrelated } == 10100
#guard p6lahja.tax { kind := .gift, value := 1000000, relation := .unrelated } == 142100
#guard p6lahja.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 0

end FiGlobal.Wealth
