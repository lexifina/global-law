import TwGlobal.Pit

/-!
# Taiwan 2025: separate taxation of dividends, the integrated property-gains tax, securities transaction tax (1100, 4400)
所得稅法 (`tw/law/moj/ita_current.txt`, arts. 14-4 to 14-8 and 15 unamended since 2021 per the history page):
* art. 15 (5): dividends may be taxed separately at 28 % (option taken here; aggregation with the 8.5 % credit is the 1.x
  line's).
* art. 14-4 (3) 1: gains on houses and land (房地合一) held ≤ 2 years 45 %, ≤ 5 years 35 %, ≤ 10 years 20 %, > 10 years
  15 % (`hgTax`); self-use homes 10 % above NT$4 m (art. 14-5) not modelled. Gains on securities are exempt (art. 4-1).
* 證券交易稅條例 art. 2 (B, text not fetched): shares 0.3 % of the sale price, paid by the seller.

Session 12 (registry sample): 證券交易稅條例 (law.moj.gov.tw pcode G0340078, 修正日期 民國114; `tw/law/moj12/stt.html`)
art. 2 (1): shares "徵千分之三" (0.3 %) of each sale price, payable by the seller; art. 2-2 day-trading 0.15 % to 2026 and
art. 2-1 bond suspensions not modelled. Art. 2 unamended by the 2025 change: grade A.
-/

namespace TwGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "股利 分開計稅 (28 %)" i.amount pos (fun b => divR .down (2800 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "所得稅法 art. 15 (5)")) }

def fam1 : Family :=
  { name := "4400 securities transaction tax", covers := [.transactions],
    run := fun _ g _ => 
      ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares, .unlistedShares].contains d.kind).map fun (d, k) =>
        charge .transactions "證券交易稅 (0.3 %)" d.proceeds pos (fun b => divR .down (30 * b) BP) (event := s!"disposal {k + 1}") (statute := "證券交易稅條例 art. 2 (1)")) }

/-- 所得稅法 art. 14-4 (3) 1 (individuals, residents): rate by holding period. -/
def hgRate (m : Nat) : Int := if m ≤ 24 then 4500 else if m ≤ 60 then 3500 else if m ≤ 120 then 2000 else 1500
def hgF : Family :=
  { name := "1100 房地合一 property gains", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.disposals.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>
        charge .pit "房地合一所得稅" d.gain pos (fun b => divR .down (hgRate d.heldMonths * b) BP) (event := s!"disposal {i + 1}") (statute := "所得稅法 art. 14-4 (3) 1") }

def families : List Family := [fam0, fam1, hgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (fun d => d.mainHome) then ["self-use home relief (art. 14-5: 10 % above NT$4 m) not modelled"] else [])
  ++ (if g.incomes.any (fun i => i.kind == .dividend) then ["dividends taken under the 28 % separate option (aggregation option is the 1.x line)"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .dividend, amount := 100000 }] } []).map (·.due) == [28000]
#guard hgRate 30 == 3500
#guard (fam1.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 100000, cost := 1 }] } []).map (·.due) == [300]

end TwGlobal.Capital
