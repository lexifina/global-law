import McTax.Legacy
import TaxKernel.Global

namespace McGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x model, unchanged. -/
def base : GlobalModel := GlobalModel.ofCountry McTax.country

/-- The 1.x income tax (income tax + surtaxes + local income tax) of a household: for stacking (`stackedTax`). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (base.pit args c)

end McGlobal
