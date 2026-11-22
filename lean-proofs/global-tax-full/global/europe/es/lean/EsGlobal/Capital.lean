import EsGlobal.Pit

/-!
# ES 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (Ley 35/2006 del IRPF arts. 33-38, 46, 49, 66): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)
-/

namespace EsGlobal.Capital
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .household && !g.disposals.isEmpty then ["1100 Gains of individuals on shares and property (disposals): not modelled (grade C: the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed))"] else [])


end EsGlobal.Capital
