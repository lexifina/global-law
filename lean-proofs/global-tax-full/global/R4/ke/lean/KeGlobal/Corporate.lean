import R4Common

/-!
# Kenya 2025: corporation tax (1200) and non-resident withholding

Source: Income Tax Act Cap. 470, Kenya Law consolidation at 2025-07-01 (`cmp20/world/B10-anglophone-africa/ke/law/ita_2025-07-01.txt`).

* **Corporation rate** Third Schedule Head B para 2 (a): resident company "for the year of income 2021 and each
  subsequent year … 6.00" shillings in each twenty (30 %); (b) non-resident with a PE, "for the year of income 2024 and
  each subsequent year of income | 6.00" (30 %).
* **Minimum tax** s. 12D: "[Repealed by Act No. 9 of 2025, s. 6]" (Finance Act 2025, from 1 July 2025); Head B para
  11 had it at "one per cent of the gross turnover". Not applied (mid-year repeal noted per entity).
* **Non-resident rates** Head B para 3: (a) management or professional fees "twenty per cent of the gross sum"; (b)
  "a royalty … twenty per cent"; (d) "a dividend, fifteen per cent" (EAC citizens 5 %); (e) (i) interest "fifteen per
  cent of the gross sum payable".
-/

namespace KeGlobal
open TaxKernel TaxKernel.Global

def ct : CorpRegime := { name := "Corporation tax", sched := Schedule.flat 3000 }

def nonResident : Wht :=
  { name := "Withholding tax (non-residents)",
    rules := [{ kind := .dividend, rateBp := 1500, statute := "ITA Third Schedule Head B para 3 (d) (15 %)" },
              { kind := .interest, rateBp := 1500, statute := "ITA Third Schedule Head B para 3 (e) (i) (15 %)" },
              { kind := .royalty, rateBp := 2000, statute := "ITA Third Schedule Head B para 3 (b) (20 %)" },
              { kind := .services, rateBp := 2000, statute := "ITA Third Schedule Head B para 3 (a) (20 %)" }] }

def corporate : Family :=
  R4.corpFamily "corporation tax" ct {} "ITA Third Schedule Head B para 2 (a) (6.00 in each twenty shillings: 30 %)" nonResident

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["ITA s. 12D minimum tax (1 % of gross turnover) repealed by the Finance Act 2025 (Act No. 9 of 2025, s. 6) from 1 July 2025: not applied"]
  ++ (if g.company.lossesForward ≠ 0 then ["ITA s. 15 (4) loss rule not read: losses offset in full"] else [])
  ++ ["significant economic presence tax (s. 12E) and the domestic minimum top-up tax: not modelled"]

#guard R4.corpTax ct {} { profit := 1000000 } == 300000
#guard nonResident.amount { kind := .dividend, amount := 1000000 } == 150000

end KeGlobal
