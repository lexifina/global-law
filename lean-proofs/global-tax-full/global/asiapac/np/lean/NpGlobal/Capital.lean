import NpGlobal.Pit

/-!
# Nepal FY 2082/83: final withholding on investment income and gains on listed shares (1100)
(B, registry ASIA_PACIFIC.json reading; text not re-read this session.) ITA 2058 s. 88: dividends 5 %, interest (individuals) 6 %, rent 10 % final; s. 95A: gains on listed
shares of individuals 7.5 % (held ≤ 365 days) / 5 % (longer).
-/

namespace NpGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "TDS on dividends (5 %)" i.amount pos (fun b => divR .down (500 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "ITA 2058 s. 88"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "TDS on interest (6 %)" i.amount pos (fun b => divR .down (600 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "ITA 2058 s. 88"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .rent && !i.foreign).map fun (i, k) =>
        charge .pit "TDS on rent (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "ITA 2058 s. 88")) }

def fam1 : Family :=
  { name := "1100 capital gains", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares].contains d.kind && decide ((d.heldMonths : Int) < 12)).map fun (d, k) =>
        charge .pit "Tax on listed-share gains (7.5 %)" d.gain pos (fun b => divR .down (750 * b) BP) (event := s!"disposal {k + 1}") (level := .central) (statute := "ITA 2058 s. 95A"))
      ++ ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares].contains d.kind && decide ((d.heldMonths : Int) ≥ 12)).map fun (d, k) =>
        charge .pit "Tax on listed-share gains (5 %)" d.gain pos (fun b => divR .down (500 * b) BP) (event := s!"disposal {k + 1}") (level := .central) (statute := "ITA 2058 s. 95A")) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .interest, amount := 100000 }] } []).map (·.due) == [6000]
#guard (fam1.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 200000, cost := 100000 }] } []).map (·.due) == [7500]

end NpGlobal.Capital
