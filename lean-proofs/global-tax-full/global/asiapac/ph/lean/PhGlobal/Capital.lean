import PhGlobal.Pit
import TaxKernel.Global2

/-!
# Philippines 2025: final taxes on passive income, gains, stock transaction tax (1100, 4400)
To 30 June 2025: NIRC as amended by RA 10963 (TRAIN; official copy, R3 OCR `ph/law/train/p04.txt`, `p23.txt`): s. 24 (B) (1)
interest 20 % final, (2) dividends from domestic corporations 10 % final; s. 127 (A) stock transaction tax "six-tenths of one
percent (6/10 of 1%) of the gross selling price". From 1 July 2025: RA 12214 (CMEPA), read in lexifina/philippines-law `ra/2025/12214` (gap-closing session; official
source elibrary.judiciary.gov.ph showdocs/2/99213): s. 4 re-enacts s. 24 (B) (1) interest 20 %, (2) dividends 10 % and
s. 24 (C) unlisted shares 15 %; s. 17: s. 127 (A) "one-tenths of one percent (1/10 of 1%)"; s. 28 (transitory): the
new rates apply from July 1, 2025. s. 24 (C): gains on unlisted shares 15 %; s. 24 (D): sale of real property
6 % of the gross selling price. Session 11 (year in force): the stock transaction tax takes the rate of the disposal's date
(`"date"` on the disposal record); an undated disposal of listed shares books nothing and is listed (grade C).
-/

namespace PhGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "Final tax on interest (20 %)" i.amount pos (fun b => divR .down (2000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "NIRC s. 24 (B) (1)"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "Final tax on dividends (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "NIRC s. 24 (B) (2)")) }

def fam1 : Family :=
  { name := "1100 capital gains", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.disposals.zipIdx.filter fun (d, _) => [.unlistedShares].contains d.kind).map fun (d, k) =>
        charge .pit "Capital gains tax on unlisted shares (15 %)" d.gain pos (fun b => divR .down (1500 * b) BP) (event := s!"disposal {k + 1}") (level := .central) (statute := "NIRC s. 24 (C)")) }

def rpF : Family :=
  { name := "1100 Capital gains tax on real property (6 % of the selling price)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.disposals.zipIdx.filter fun (d, _) => [.home, .realEstate, .land].contains d.kind).map fun (d, i) =>
        charge .pit "Capital gains tax on real property (6 % of the selling price)" d.proceeds pos (fun b => divR .down (600 * b) BP) (event := s!"disposal {i + 1}") (statute := "NIRC s. 24 (D) (1)") }

/-- The date of disposal `i` (`"date"` on the input record), as yyyymmdd. -/
def dispDay (g : CanonGlobal) (i : Nat) : Option Nat :=
  AdvanceTax.dayOfRecord ((arrField g.raw "disposals").toList.getD i Lean.Json.null)
/-- s. 127 (A): 0.6 % (RA 10963) on sales to 30 June 2025, 0.1 % (RA 12214) from 1 July 2025. -/
def sttBp (day : Nat) : Int := if day < 20250701 then 60 else 10
def sttF : Family :=
  { name := "4400 stock transaction tax (s. 127 (A))", covers := [.transactions],
    run := fun _ g _ =>
      (g.disposals.zipIdx.filter fun (d, _) => d.kind == .listedShares).filterMap fun (d, k) =>
        (dispDay g k).map fun day =>
          charge .transactions (if day < 20250701 then "Stock transaction tax (0.6 %, sale to 30 June 2025)" else "Stock transaction tax (0.1 %, sale from 1 July 2025)")
            d.proceeds pos (fun b => divR .down (sttBp day * b) BP) (event := s!"disposal {k + 1}")
            (statute := if day < 20250701 then "NIRC s. 127 (A) as amended by RA 10963 (6/10 of 1 %)" else "NIRC s. 127 (A) as amended by RA 12214 (0.1 %, from 1 July 2025)") }

def families : List Family := [fam0, fam1, rpF, sttF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.zipIdx.any (fun (d, k) => d.kind == .listedShares && (dispDay g k).isNone) then ["stock transaction tax: a listed-share sale without a date (0.6 % to 30 June 2025, 0.1 % from 1 July 2025): not booked (grade C)"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .interest, amount := 100000 }] } []).map (·.due) == [20000]
#guard (fam1.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .unlistedShares, proceeds := 200000, cost := 100000 }] } []).map (·.due) == [15000]
#guard (rpF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .land, proceeds := 1000000, cost := 1 }] } []).map (·.due) == [60000]
#guard (sttF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }], raw := (Lean.Json.parse "{\"disposals\": [{\"date\": \"2025-03-01\"}]}").toOption.getD Lean.Json.null } []).map (·.due) == [6000]
#guard (sttF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }], raw := (Lean.Json.parse "{\"disposals\": [{\"date\": \"2025-07-01\"}]}").toOption.getD Lean.Json.null } []).map (·.due) == [1000]
#guard (sttF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }] } []).length == 0

end PhGlobal.Capital
