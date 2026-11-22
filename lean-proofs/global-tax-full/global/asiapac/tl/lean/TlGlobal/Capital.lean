import TlGlobal.Pit

/-!
# Timor-Leste 2025: withholding on rents (1100)
Lei 8/2008 (`jr2008_no26.txt`) art. 55: payments of rent for land or buildings, "à taxa de 10%" of the gross, final.
-/

namespace TlGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .rent && !i.foreign).map fun (i, k) =>
        charge .pit "Retenção na fonte sobre rendas (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Lei 8/2008 art. 55")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .rent, amount := 100000 }] } []).map (·.due) == [10000]

end TlGlobal.Capital
