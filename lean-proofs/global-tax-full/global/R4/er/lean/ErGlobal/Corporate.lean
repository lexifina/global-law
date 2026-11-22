import R4Common

/-!
# Eritrea 2025: corporate income tax (1200) and withholding (generated from `R4/specs/er.json`)

No usable 2025 text for these headings: no statute text is held locally (registry: grade C for every heading; the 1.x model's own sources are the income tax proclamations it cites).




-/

namespace ErGlobal
open TaxKernel TaxKernel.Global



def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CIT not modelled: no statute text is held locally (registry: grade C for every heading; the 1.x model's own sources are the income tax proclamations it cites)", "withholding on payments abroad not modelled: no statute text is held (Income Tax Proclamation 62/1994 and amendments not found online)"]

end ErGlobal
