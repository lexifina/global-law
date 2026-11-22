import IeGlobal.Pit

/-!
# IE 2025: capital acquisitions tax (4300)


## Capital acquisitions tax (4300), pass 3
Source: Revenue, Notes for Guidance, Capital Acquisitions Tax Consolidation Act 2003 "(as amended by subsequent Acts
up to and including the Finance Act 2024)", via the Internet Archive (captures 2025-08-09;
`ie/law/cat_nfg2024_schedules.pdf`, `cat_nfg2024_part09.pdf`, `cat_nfg2024_part01.pdf`); the Act's own text
(irishstatutebook / revisedacts) not read: grade B.
* Schedule 2: "3 group thresholds: Group A €400,000, Group B €40,000, Group C €20,000"; Group A where the donee or
  successor is "the child, or minor child of a deceased child of the disponer" (or a parent inheriting an absolute
  interest); Group B "a lineal ancestor, a lineal descendant (other than a child ...), a brother, a sister, or a
  child of a brother or of a sister"; Group C otherwise; "Benefits taken by a beneficiary since 5 December 1991,
  which have the same group threshold as the current benefit, are aggregated"; "A single 33% rate of tax applies
  for both gifts and inheritances" (Sch. 2 Part 1 paras. 1, 3, 4).
* s. 69: "the first €3,000 of the total taxable value of all taxable gifts taken by a donee from the disponer in any
  relevant period"; s. 70, 71: gifts and inheritances taken by the spouse/civil partner are exempt.

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, IE, Individual - Other taxes, accessed  (live page; `law/pwc_indother_wb2025.txt`): net wealth tax on individuals: none (PwC WWTS Individual - Other taxes,  (live page))
-/

namespace IeGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- CATCA 2003 Sch. 2 Part 1 para. 1 (Notes for Guidance, FA 2024 edition): group thresholds; para. 4: 33 %. -/
def groupA : TaxClass := { allowance := 400000, sched := Schedule.flat 3300 }
def groupB : TaxClass := { allowance := 40000, sched := Schedule.flat 3300 }
def groupC : TaxClass := { allowance := 20000, sched := Schedule.flat 3300 }
def groupOf : Relation → Nat
  | .child => 0
  | .grandchild | .parent | .sibling | .nieceNephew => 1
  | _ => 2
/-- Aggregation since 5 December 1991 (same donor in the input), the s. 69 small-gift exemption, the spouse exemption (ss. 70, 71). -/
def cat : InheritanceTax :=
  { name := "Capital acquisitions tax", classOf := groupOf, classes := [groupA, groupB, groupC],   exemptRelations := [.spouse], lookbackYears := 34,   exemptValue := fun t => if t.kind == .gift then min (pos t.statutoryValue) 3000 else 0 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 capital acquisitions tax", covers := [.estate],
     run := fun args g prev =>
       cat.charges g.transfers "CATCA 2003 Sch. 2 Part 1 paras. 1, 3, 4 (A 400 000, B 40 000, C 20 000; 33 %); ss. 69-71" }]

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax on individuals: none" }]

def notes : List String := ["IE 4300: CAT from Revenue Notes for Guidance (FA 2024 edition, Wayback 2025-08-09): A 400 000, B 40 000, C 20 000, 33 %"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty then ["4300 CAT: aggregation covers prior benefits from the same disponer only (the Act aggregates all benefits within the group since 5.12.1991); a parent inheriting an absolute interest (Group A) taken as Group B; reliefs (agricultural, business, dwelling-house s. 86), charities (s. 76), the s. 69 exemption applied once per gift"] else [])

-- child inherits 500 000: (500 000 - 400 000) x 33 % = 33 000
#guard cat.tax { kind := .inheritance, value := 500000, relation := .child } == 33000
#guard cat.tax { kind := .inheritance, value := 400000, relation := .child } == 0
-- nephew inherits 100 000: (100 000 - 40 000) x 33 % = 19 800
#guard cat.tax { kind := .inheritance, value := 100000, relation := .nieceNephew } == 19800
-- unrelated gift 50 000: (50 000 - 3 000 - 20 000) x 33 % = 8 910
#guard cat.tax { kind := .gift, value := 50000, relation := .unrelated } == 8910
#guard cat.tax { kind := .gift, value := 3000, relation := .unrelated } == 0
#guard cat.tax { kind := .inheritance, value := 5000000, relation := .spouse } == 0
-- a prior 30 000 benefit inside the look-back: tax on 130 000 less tax on 30 000 (nephew): 29 700 - 0
#guard cat.tax { kind := .inheritance, value := 100000, relation := .nieceNephew, prior := [(30000, 5)] } == 29700

end IeGlobal.Wealth
