import LaGlobal.Pit

/-!
# Lao PDR 2025: income tax on dividends, interest and rent (1100)

(B, registry ASIA_PACIFIC.json reading; text not re-read this session.) Law on Income Tax No. 67/NA (2019): dividends, interest and rent 10 %.
-/

namespace LaGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "Income tax on dividends (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Law on Income Tax 67/NA"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "Income tax on interest (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "idem"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .rent && !i.foreign).map fun (i, k) =>
        charge .pit "Income tax on rent (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "idem")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .rent, amount := 100000 }] } []).map (·.due) == [10000]

end LaGlobal.Capital
