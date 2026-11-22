import MnGlobal.Pit

/-!
# Mongolia 2025: personal income tax on investment income and property sales (1100)
(B, registry ASIA_PACIFIC.json reading; text not re-read this session.) Хувь хүний орлогын албан татварын тухай хууль (2019) art. 21: dividends, interest and rent 10 %; sale of
immovable property 2 % of the price (`propF`).
-/

namespace MnGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "ХХОАТ ногдол ашиг (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "PIT law (2019) art. 21"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "ХХОАТ хүү (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "art. 21"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .rent && !i.foreign).map fun (i, k) =>
        charge .pit "ХХОАТ түрээс (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "art. 21")) }

def propF : Family :=
  { name := "1100 PIT on immovable property sales", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else (g.disposals.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>
      charge .pit "ХХОАТ үл хөдлөх хөрөнгө борлуулсан (2 %)" d.proceeds pos (fun b => divR .down (200 * b) BP) (event := s!"disposal {i + 1}") (statute := "PIT law (2019) art. 21") }

def families : List Family := [fam0, propF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .dividend, amount := 100000 }] } []).map (·.due) == [10000]

end MnGlobal.Capital
