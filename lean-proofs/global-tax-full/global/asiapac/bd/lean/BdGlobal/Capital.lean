import BdGlobal.Pit
import TaxKernel.Global2

/-!
# Bangladesh 2025: tax on stock-exchange transactions (4400)
Income Tax Act 2023 s. 137 (bdlaws `act-1429/section-51967`, Internet Archive 2025-02-13 and 2026-01-23,
`bd/law/bd_ita2023_s137_wb*.html`): the stock exchange's chief executive collects tax "at the rate of 0.05 %" of the value
of securities transactions of its members (listed sukuk and bonds excluded). Finance Ordinance 2025 (Ordinance No. 28 of
2025, Bangladesh Gazette Extraordinary 2 June 2025) s. 84 substitutes "0.03 %"; s. 1 (2): in force from 1 July 2025 (the
2026 capture's footnote says the same). Session 12 (year in force): a listed-share sale takes the rate of its date
(`"date"` on the disposal record): 0.05 % to 30 June 2025, 0.03 % from 1 July 2025; an undated sale books nothing and is
listed (grade C). The tax is collected from the exchange member on the transaction value; it is booked here on the
seller's proceeds (as an STT). Dividends and interest (final/minimum) and listed-share gains: not modelled (C).
-/

namespace BdGlobal.Capital
open TaxKernel TaxKernel.Global

/-- The date of disposal `i` (`"date"` on the input record), as yyyymmdd. -/
def dispDay (g : CanonGlobal) (i : Nat) : Option Nat :=
  AdvanceTax.dayOfRecord ((arrField g.raw "disposals").toList.getD i Lean.Json.null)
/-- ITA 2023 s. 137: 0.05 % to 30 June 2025, 0.03 % from 1 July 2025 (Finance Ordinance 2025 s. 84). Basis points x 100. -/
def s137Rate (day : Nat) : Int := if day < 20250701 then 5 else 3
def sttF : Family :=
  { name := "4400 tax on stock-exchange transactions (ITA 2023 s. 137)", covers := [.transactions],
    run := fun _ g _ =>
      (g.disposals.zipIdx.filter fun (d, _) => d.kind == .listedShares).filterMap fun (d, k) =>
        (dispDay g k).map fun day =>
          charge .transactions (if day < 20250701 then "Tax on stock-exchange transactions (0.05 %, to 30 June 2025)" else "Tax on stock-exchange transactions (0.03 %, from 1 July 2025)")
            d.proceeds pos (fun b => divR .down (s137Rate day * b) BP) (event := s!"disposal {k + 1}")
            (statute := if day < 20250701 then "ITA 2023 s. 137 (0.05 %)" else "ITA 2023 s. 137 as amended by Finance Ordinance 2025 s. 84 (0.03 %, from 1 July 2025)") }

def families : List Family := [sttF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.zipIdx.any (fun (d, k) => d.kind == .listedShares && (dispDay g k).isNone) then ["tax on stock-exchange transactions (ITA 2023 s. 137): a listed-share sale without a date (0.05 % to 30 June 2025, 0.03 % from 1 July 2025): not booked (grade C)"] else [])

#guard (sttF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }], raw := (Lean.Json.parse "{\"disposals\": [{\"date\": \"2025-06-30\"}]}").toOption.getD Lean.Json.null } []).map (·.due) == [500]
#guard (sttF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }], raw := (Lean.Json.parse "{\"disposals\": [{\"date\": \"2025-07-01\"}]}").toOption.getD Lean.Json.null } []).map (·.due) == [300]
#guard (sttF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }] } []).length == 0

end BdGlobal.Capital
