import UyTax.Legacy
import TaxKernel.Global
import AmerCommon

namespace UyGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x model, unchanged (`ofCountry`). -/
def base : GlobalModel := GlobalModel.ofCountry UyTax.country

/-- The 1.x income tax (income tax + surtaxes + local income tax) of a household: for stacking (`stackedTax`). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (base.pit args c)

end UyGlobal
