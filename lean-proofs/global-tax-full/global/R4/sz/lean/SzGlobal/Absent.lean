import R4Common

/-! # SZ 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace SzGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .payroll, why := "SZ: no payroll tax or training levy charged in 2025 (grade B). The 1982 Act lets the Minister impose a levy only by a training levy order for a given industry (s. 13 (1), below 1 % of pay, s. 13 (2) (c)); no such order was located, the revenue authority lists no skills levy, and the OECD Revenue Statistics table for Eswatini books 0 under heading 3000 in every year it publishes (2021, 2022, 2023; 2024 and 2025 not yet published). Not an absence proved from a text: an industry order could exist (flag)." }]

#guard absentList.length == 1

end SzGlobal
