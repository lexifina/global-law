import PkGlobal.Pit
import TaxKernel.Global2

/-!
# Pakistan 2025: advance income tax on immovable property (ITO ss. 236C, 236K); Punjab property taxes not reached (4100, 4400)

**Advance tax (session 10, grade A; kernel 2.6.0 `AdvanceTax`)**: Income Tax Ordinance 2001, consolidations of the FBR
amended up to 30 June 2024 (`pk/law/pk_ito_upto20240630.pdf`) and up to 31 July 2025 (`ito25.txt` of the 1.x build).
* **s. 236C (1)**: the person registering or attesting a transfer of immovable property collects advance tax from the
  seller at the First Schedule Part IV **Division X** rate on the gross consideration: 3 % (up to Rs 50 m), 3.5 % (to Rs
  100 m), 4 % (above) in the 30.06.2024 text; 4.5 / 5 / 5.5 % in the 31.07.2025 text (Finance Act 2025, from 1 July 2025).
  **s. 236C (2)**: adjustable.
* **s. 236K (1)**: the same collects advance tax from the purchaser at the **Division XVIII** rate on the fair market
  value: 3 / 3.5 / 4 % to 30 June 2025; 1.5 / 2 / 2.5 % from 1 July 2025 (table substituted by the Finance Act 2025).
  **s. 236K (2)**: adjustable.
The rate is the one of the band the whole base falls in, chosen by the transaction's `"date"` (an undated transaction:
grade C, never guessed). Booked as 1100 after the income-tax families and credited against the 1100 already booked
(adjustable). Rates for persons on the active taxpayers' list; the Tenth Schedule rates for others, the exemptions of the
s. 236C (1) provisos and the same-year proviso of s. 236C (2) are not modelled.
The Punjab Urban Immovable Property Tax Act 1958 and the Punjab stamp duty / capital value tax schedules: not reached (C).
-/

namespace PkGlobal.Property
open TaxKernel TaxKernel.Global

/-- ITO 2001 s. 236C, First Schedule Part IV Division X (seller, gross consideration). -/
def pk236C : AdvanceTax :=
  { name := "Advance tax on sale or transfer of immovable property (s. 236C)", source := .disposals [.home, .realEstate, .land],
    rates := [
      { ceilings := [(50000000, 300), (100000000, 350)], topBp := 400, dateTo := "2025-06-30",
        statute := "ITO 2001 s. 236C (1); First Schedule Part IV Division X (FBR text to 30.06.2024): 3 / 3.5 / 4 %" },
      { ceilings := [(50000000, 450), (100000000, 500)], topBp := 550, dateFrom := "2025-07-01",
        statute := "ITO 2001 s. 236C (1); Division X as substituted (Finance Act 2025, from 1 July 2025): 4.5 / 5 / 5.5 %" }],
    credit := .adjustable, creditStatute := "ITO 2001 s. 236C (2): adjustable" }

/-- ITO 2001 s. 236K, Division XVIII (purchaser, fair market value). -/
def pk236K : AdvanceTax :=
  { name := "Advance tax on purchase or transfer of immovable property (s. 236K)", source := .purchases [.home, .realEstate, .land],
    rates := [
      { ceilings := [(50000000, 300), (100000000, 350)], topBp := 400, dateTo := "2025-06-30",
        statute := "ITO 2001 s. 236K (1); Division XVIII (table before the Finance Act 2025): 3 / 3.5 / 4 %" },
      { ceilings := [(50000000, 150), (100000000, 200)], topBp := 250, dateFrom := "2025-07-01",
        statute := "ITO 2001 s. 236K (1); Division XVIII table substituted by the Finance Act 2025 (from 1 July 2025): 1.5 / 2 / 2.5 %" }],
    credit := .adjustable, creditStatute := "ITO 2001 s. 236K (2): adjustable" }

def pkAdvance : List AdvanceTax := [pk236C, pk236K]

def advF : Family := advanceTaxFamily "advance tax on immovable property (ITO ss. 236C, 236K)" pkAdvance

def families : List Family := [advF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !(advanceTaxUnknown pkAdvance g).isEmpty then ["advance tax on immovable property: a transaction without a date (rate before / from 1 July 2025 undecided): grade C"] else [])
  ++ (if !g.disposals.isEmpty || !g.purchases.isEmpty then ["advance tax on immovable property: active-taxpayers'-list rates; Tenth Schedule rates for others, the s. 236C (1) provisos and the s. 236C (2) same-year proviso not modelled; Punjab stamp duty and capital value tax not reached"] else [])

#guard (pk236C.rates.map (·.bpOf 50000000)) == [300, 450]
#guard (pk236C.rates.map (·.bpOf 60000000)) == [350, 500]
#guard (pk236K.rates.map (·.bpOf 120000000)) == [400, 250]

end PkGlobal.Property
