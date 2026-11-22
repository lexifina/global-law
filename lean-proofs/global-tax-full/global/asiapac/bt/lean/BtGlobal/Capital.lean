import BtGlobal.Pit

/-!
# Bhutan 2025: TDS on dividends and interest (1100)

(B.) ITA 2001 Part III: TDS on dividends 10 %, interest 5 %, final.
-/

namespace BtGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "TDS on dividends (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "ITA 2001 Part III"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "TDS on interest (5 %)" i.amount pos (fun b => divR .down (500 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "ITA 2001 Part III")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .interest, amount := 100000 }] } []).map (·.due) == [5000]

end BtGlobal.Capital
