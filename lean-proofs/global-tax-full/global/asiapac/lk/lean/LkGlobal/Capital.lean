import LkGlobal.Pit

/-!
# Sri Lanka 2025: dividend tax and capital gains tax (1100)
Inland Revenue Act No. 24 of 2017, IRD consolidated text "incorporating amendments up to 31st March 2025" (dated 30 June
2025; Acts No. 10 of 2021, 45 of 2022, 4 of 2023, 14 of 2023 and 2 of 2025 with their effective dates; ird.gov.lk,
Internet Archive 2026-03-08, `lk/law/lk_ira_cons2025_ird_wb20260308.pdf`), and Act No. 2 of 2025 itself
(`lk/law/lk_ira_act02_2025_ird_wb20250709.pdf`):
* **dividends**: s. 84A (1A) (from 1 January 2023) advance income tax on dividends at First Schedule para. 10 (1) (d) (v)
  "dividend paid-15%" (Act No. 45 of 2022 s. 33 (6)); Act No. 2 of 2025 changed only (d) (ii) (interest 5 % -> 10 % from
  1 April 2025). The same 15 % in Y/A 2024/25 (to 31 March 2025) and 2025/26.
* **gains of individuals**: First Schedule para. 1 (2) (a) "those gains from the realisation of investment assets shall be
  taxed at the rate of 10%" (no amendment note; Act No. 2 of 2025 inserted (1D) and (6) and replaced (2) (c) only): 10 % in
  both years of assessment. (Companies: para. 4 (4) (a) 30 % from 1 October 2022: not this family.)
Session 12 (year in force): rows identical either side of 1 April 2025: no split. The dividend tax is booked as final
(s. 84A (1A) credit rules not read: grade B); capital gains grade A.
-/

namespace LkGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "WHT on dividends (15 %, final)" i.amount pos (fun b => divR .down (1500 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "IRA 2017 s. 84, Fifth Schedule")) }

def fam1 : Family :=
  { name := "1100 capital gains", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.disposals.zipIdx.filter fun (d, _) => [.realEstate, .land, .unlistedShares].contains d.kind).map fun (d, k) =>
        charge .pit "Capital gains tax (10 %)" d.gain pos (fun b => divR .down (1000 * b) BP) (event := s!"disposal {k + 1}") (level := .central) (statute := "IRA 2017 s. 37, Third Schedule")) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .dividend, amount := 100000 }] } []).map (·.due) == [15000]
#guard (fam1.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .land, proceeds := 2000000, cost := 1000000 }] } []).map (·.due) == [100000]

end LkGlobal.Capital
