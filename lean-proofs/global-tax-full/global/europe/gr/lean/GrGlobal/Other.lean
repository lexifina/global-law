import GrGlobal.Pit

/-!
# GR 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes

* **6000 not levied (cited, gap pass, grade B)**: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVGRC v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/GRC.csv`, SHA256SUMS; general government S13; 2025 not yet published): heading 6000 total 0 in 2021-2024; the stamp duties (χαρτόσημο) are booked by the OECD under other headings, not 6000: the OECD books no revenue under heading 6000 in any of 2021-2024 (guide § 85: taxes on bases other than those of 1000-5000); the stamp duties (χαρτόσημο) are booked by the OECD under other headings, not 6000 (OECD Revenue Statistics 2021-2024 (2025 not yet published); no 6000 tax known in the national law read)
-/

namespace GrGlobal.Other
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .other, why := "the OECD books no revenue under heading 6000 in any of 2021-2024 (guide § 85: taxes on bases other than those of 1000-5000); the stamp duties (χαρτόσημο) are booked by the OECD under other headings, not 6000" }]

def notes : List String := ["GR 6000 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)"] else [])


end GrGlobal.Other
