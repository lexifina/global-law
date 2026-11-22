import VnGlobal.Pit

/-!
# Viet Nam 2025: PIT on investment income, transfers of capital, securities and real estate, inheritances and gifts (1100)
Source: Luật Thuế TNCN 04/2007/QH12, văn bản hợp nhất 103/VBHN-VPQH (2025) (`cmp20/world/B03-asia-east-se/vn/law/van-ban-
hop-nhat-so-103-…txt`), art. 23 (2) "Biểu thuế toàn phần": investment income 5 %; capital transfers (art. 13 (1)) 20 %
(of the gain); securities transfers 0.1 % (of the price); real estate transfers 2 % (of the price); inheritances and gifts
10 % (above VND 10 m, art. 16). Deposit interest is exempt (art. 4).
-/

namespace VnGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "Thuế TNCN thu nhập từ đầu tư vốn (5 %)" i.amount pos (fun b => divR .down (500 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Luật 04/2007 (hợp nhất 103/VBHN) art. 23 (2) a")) }

def fam1 : Family :=
  { name := "1100 capital gains", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.disposals.zipIdx.filter fun (d, _) => [.unlistedShares].contains d.kind).map fun (d, k) =>
        charge .pit "Thuế TNCN chuyển nhượng vốn (20 %)" d.gain pos (fun b => divR .down (2000 * b) BP) (event := s!"disposal {k + 1}") (level := .central) (statute := "art. 23 (2) đ")) }

def secF : Family :=
  { name := "1100 Thuế TNCN chuyển nhượng chứng khoán (0.1 %)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.disposals.zipIdx.filter fun (d, _) => [.listedShares].contains d.kind).map fun (d, i) =>
        charge .pit "Thuế TNCN chuyển nhượng chứng khoán (0.1 %)" d.proceeds pos (fun b => divR .down (10 * b) BP) (event := s!"disposal {i + 1}") (statute := "art. 23 (2) đ") }
def reF : Family :=
  { name := "1100 Thuế TNCN chuyển nhượng bất động sản (2 %)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.disposals.zipIdx.filter fun (d, _) => [.home, .realEstate, .land].contains d.kind).map fun (d, i) =>
        charge .pit "Thuế TNCN chuyển nhượng bất động sản (2 %)" d.proceeds pos (fun b => divR .down (200 * b) BP) (event := s!"disposal {i + 1}") (statute := "art. 23 (2) e") }
def giftF : Family :=
  { name := "1100 PIT on inheritances and gifts", covers := [.pit],
    run := fun _ g _ => g.transfers.zipIdx.map fun (t, i) =>
      charge .pit "Thuế TNCN thừa kế, quà tặng (10 %)" t.statutoryValue (fun v => pos (v - 10000000)) (fun b => divR .down (1000 * b) BP) (event := s!"transfer {i + 1}") (statute := "art. 16, art. 23 (2) d") }

def families : List Family := [fam0, fam1, secF, reF, giftF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (fun t => t.relation == .spouse || t.relation == .child || t.relation == .parent) then ["exemption of transfers between spouses, parents and children of real estate (art. 4 (1), (4)) not modelled"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .dividend, amount := 100000 }] } []).map (·.due) == [5000]
#guard (secF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }] } []).map (·.due) == [1000]
#guard (giftF.run [] { id := "t", household := { id := "t" }, transfers := [{ kind := .gift, value := 110000000, relation := .unrelated }] } []).map (·.due) == [10000000]

end VnGlobal.Capital
