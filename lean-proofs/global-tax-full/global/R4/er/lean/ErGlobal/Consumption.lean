import R4Common

/-!
# Eritrea 2025: VAT (5111) and excises (5121) (generated from `R4/specs/er.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: no statute text is held locally (registry: grade C for every heading; the 1.x model's own sources are the income tax proclamations it cites).




-/

namespace ErGlobal
open TaxKernel TaxKernel.Global



def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["VAT not modelled: no statute text is held locally (registry: grade C for every heading; the 1.x model's own sources are the income tax proclamations it cites)", "excises not modelled: no statute text is held locally (registry: grade C for every heading; the 1.x model's own sources are the income tax proclamations it cites)"]

end ErGlobal
