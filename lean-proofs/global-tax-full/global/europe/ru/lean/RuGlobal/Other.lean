import RuGlobal.Pit

/-!
# RU 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Transport tax (НК гл. 28, regional), mineral extraction tax (гл. 26)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: obsolete placement: transport tax belongs to 5200; mineral extraction tax is sector-only (minor)
-/

namespace RuGlobal.Other
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)"] else [])
  ++ (if true then ["6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)"] else [])


end RuGlobal.Other
