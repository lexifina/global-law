import BeGlobal.Pit

/-!
# BE 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Taxe sur les comptes-titres recorded under net wealth; regional taxes): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor here: the securities-account tax is a 4200 item; regional taxes left

* **6000 not levied (cited, gap pass, grade B)**: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVBEL v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/BEL.csv`, SHA256SUMS; general government S13; 2025 not yet published): heading 6000 total 0 in 2021-2024; the only non-zero figure is -0,2 million EUR in 2021 (a correction of an earlier year): the OECD books no revenue under heading 6000 in any of 2021-2024 (guide § 85: taxes on bases other than those of 1000-5000); the only non-zero figure is -0,2 million EUR in 2021 (a correction of an earlier year) (OECD Revenue Statistics 2021-2024 (2025 not yet published); no 6000 tax known in the national law read)
-/

namespace BeGlobal.Other
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .other, why := "the OECD books no revenue under heading 6000 in any of 2021-2024 (guide § 85: taxes on bases other than those of 1000-5000); the only non-zero figure is -0,2 million EUR in 2021 (a correction of an earlier year)" }]

def notes : List String := ["BE 6000 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)"] else [])


end BeGlobal.Other
