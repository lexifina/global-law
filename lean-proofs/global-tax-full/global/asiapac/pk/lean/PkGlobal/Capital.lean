import PkGlobal.Pit

/-!
# Pakistan tax year 2026: tax on dividends (1100)
(B: FBR manual `ito25.txt` on the build server, the Division III table not re-located this session.) ITO 2001 s. 5, First Schedule
Part I Division III: dividends 15 % (25 % from companies enjoying tax exemption, not modelled). Profit on debt (s. 7B) and
securities gains (s. 37A, Division VII) not modelled (C).
-/

namespace PkGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "Tax on dividends (15 %)" i.amount pos (fun b => divR .down (1500 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "ITO 2001 s. 5, First Schedule Part I Div. III")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .dividend, amount := 100000 }] } []).map (·.due) == [15000]

end PkGlobal.Capital
