import ThGlobal.Pit

/-!
# Thailand 2025: inheritance tax and tax on gifts (4300)
(B.) Inheritance Tax Act B.E. 2558: 10 % of the inheritance above 100 m baht, 5 % for ascendants and descendants; spouses
exempt. Revenue Code s. 42 (10), (28), s. 48 (1/1): gifts from ascendants/descendants above 20 m baht a year, and from
other relatives above 10 m, taxed at 5 % separately.
-/

namespace ThGlobal.Transfers
open TaxKernel TaxKernel.Global

def inh : InheritanceTax :=
  { name := "Inheritance tax", exemptRelations := [.spouse, .charity],
    classOf := fun r => if r == .child || r == .grandchild || r == .parent then 0 else 1,
    classes := [{ allowance := 100000000, sched := Schedule.flat 500 }, { allowance := 100000000, sched := Schedule.flat 1000 }] }
def gift : InheritanceTax :=
  { name := "Income tax on gifts (5 %)", exemptRelations := [.spouse, .charity],
    classOf := fun r => if r == .child || r == .grandchild || r == .parent then 0 else 1,
    classes := [{ allowance := 20000000, sched := Schedule.flat 500 }, { allowance := 10000000, sched := Schedule.flat 500 }] }
def inhF : Family :=
  { name := "4300 inheritance tax, gift tax", covers := [.estate],
    run := fun _ g _ => inh.charges (g.transfers.filter (·.kind == .inheritance)) "Inheritance Tax Act B.E. 2558 s. 16"
      ++ gift.charges (g.transfers.filter (·.kind == .gift)) "Revenue Code s. 42 (10), (28), s. 48 (1/1)" }

def families : List Family := [inhF]

def absent : List Absent :=
  [{ oecd := .wealth, why := "No net wealth tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (inhF.run [] { id := "t", household := { id := "t" }, transfers := [{ kind := .inheritance, value := 120000000, relation := .child }] } []).map (·.due) == [1000000]

end ThGlobal.Transfers
