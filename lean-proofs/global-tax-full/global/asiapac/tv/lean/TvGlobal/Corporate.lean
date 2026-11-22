import TvGlobal.Pit

/-!
# Tuvalu 2025: company income tax (1200) and non-resident withholding

Source: Income Tax Act (Cap. 26.16), 2022 Revised Edition, copied by the 1.x TV builder
(`cmp20/world/B14-pacific/tv/law/1992-0005_2.txt`; amendments after the 2022 Revised Edition not checked).
* **s. 5, Schedule 6 para. 1 (i)**: "Taxable income of any resident company (other than those specified elsewhere on
  this schedule)" 30 %; (j) a further company line at 40 % (its qualifier is cut in the text: taken as non-resident
  companies, not modelled).
* **s. 37, Schedule 5 Part A (2)**: non-resident withholding income: (a) dividend 15 %; (b) service fees 15 %;
  (c) specified alimony 30 %; (d) gross income other than dividends, service fees or alimony (interest, royalties) 15 %.
-/

namespace TvGlobal.Corporate
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["session 11 year-in-force audit: Income Tax (Cap. 26.16) 2022 Revised Edition with later amendments not checked; no 2025 version or official 2025 source reached: grade C"] else [])


end TvGlobal.Corporate
