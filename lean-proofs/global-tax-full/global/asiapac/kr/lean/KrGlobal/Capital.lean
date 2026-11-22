import KrGlobal.Pit

/-!
# Korea 2025: separate taxation of financial income and the securities transaction tax (1100, 4400)
* 소득세법 art. 129 (1) 1-2: withholding 14 % on interest and dividends, final for financial income up to 2,000만 (art. 14
  (3) 6); 지방세법 art. 103-3: local income tax 10 % of it (1.4 %). (B: rates from the act's known wording; the 소득세법
  text fetched is the 2026 version, these items unamended since 2017.)
* 증권거래세법 art. 8 (1) (`kr/law/lawgo/증권거래세법_20220701.txt`): "1만분의 35" (unlisted shares 0.35 %); (2): listed
  shares lowered by decree: 2025 시행령 art. 5: KOSPI 0 % + 농어촌특별세 0.15 %, KOSDAQ 0.15 % (listed: 0.15 % in all).
-/

namespace KrGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "이자소득 원천징수 (14 %)" i.amount pos (fun b => divR .down (1400 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "소득세법 art. 129 (1) 1, art. 14 (3) 6"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "지방소득세 (1.4 %)" i.amount pos (fun b => divR .down (140 * b) BP) (event := s!"income {k + 1}") (level := .local) (statute := "지방세법 art. 103-3"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "배당소득 원천징수 (14 %)" i.amount pos (fun b => divR .down (1400 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "소득세법 art. 129 (1) 2"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "지방소득세 (1.4 %)" i.amount pos (fun b => divR .down (140 * b) BP) (event := s!"income {k + 1}") (level := .local) (statute := "지방세법 art. 103-3")) }

def fam1 : Family :=
  { name := "4400 securities transaction tax", covers := [.transactions],
    run := fun _ g _ => 
      ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares].contains d.kind).map fun (d, k) =>
        charge .transactions "증권거래세 / 농어촌특별세 (listed 0.15 %)" d.proceeds pos (fun b => divR .down (15 * b) BP) (event := s!"disposal {k + 1}") (statute := "증권거래세법 art. 8 (2); 시행령 art. 5 (2025); 농어촌특별세법 art. 5 (1) 5"))
      ++ ((g.disposals.zipIdx.filter fun (d, _) => [.unlistedShares].contains d.kind).map fun (d, k) =>
        charge .transactions "증권거래세 (unlisted 0.35 %)" d.proceeds pos (fun b => divR .down (35 * b) BP) (event := s!"disposal {k + 1}") (statute := "증권거래세법 art. 8 (1)")) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.incomes.any (fun i => i.kind == .interest || i.kind == .dividend) then ["financial income above 2,000만 aggregated with the 1.x line (art. 14 (3) 6, 62) not modelled"] else [])
  ++ (if g.disposals.any (fun d => d.kind.isRealEstate || d.kind == .unlistedShares || (d.kind == .listedShares && decide (d.stakeBp ≥ 100))) then ["capital gains tax (소득세법 arts. 94-104) on real estate, unlisted shares and major shareholders not modelled"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .interest, amount := 1000000 }] } []).map (·.due) == [140000, 14000]
#guard (fam1.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 10000000, cost := 9000000 }] } []).map (·.due) == [15000]

end KrGlobal.Capital
