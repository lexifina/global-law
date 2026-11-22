import UzGlobal.Pit

/-!
# Uzbekistan 2025: income tax on dividends (1100)

(B.) Tax Code (ZRU-599) art. 381: dividends of individuals 5 %.
-/

namespace UzGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "Налог на доходы с дивидендов (5 %)" i.amount pos (fun b => divR .down (500 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Tax Code art. 381")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .dividend, amount := 100000 }] } []).map (·.due) == [5000]

end UzGlobal.Capital
