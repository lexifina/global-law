import KzGlobal.Pit

/-!
# Kazakhstan 2025: individual income tax on dividends (1100)

(B.) Tax Code 2017 (in force to 2025-12-31) art. 320: dividends 5 % (exempt if held more than 3 years: not modelled).
-/

namespace KzGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "ИПН с дивидендов (5 %)" i.amount pos (fun b => divR .down (500 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Tax Code 2017 art. 320")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .dividend, amount := 100000 }] } []).map (·.due) == [5000]

end KzGlobal.Capital
