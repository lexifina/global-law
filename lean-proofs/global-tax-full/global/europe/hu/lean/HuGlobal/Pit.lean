import HuTax.Legacy
import TaxKernel.Global

namespace HuGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x model, unchanged. -/
def base : GlobalModel := GlobalModel.ofCountry HuTax.country

/-- The 1.x income tax (income tax + surtaxes + local income tax) of a household: for stacking (`stackedTax`). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (base.pit args c)

end HuGlobal
