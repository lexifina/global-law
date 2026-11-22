import NOTax.Legacy
import TaxKernel.Global

namespace NoGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x `Country`, as the 1.x `main` builds it from the options. -/
def countryFor (args : List String) : Country := (NOTax.country (args.contains "--oecd"))

def base : GlobalModel :=
  { GlobalModel.ofCountry (countryFor []) with
    pit := fun args c => ((countryFor args).computeWith args c).toJson }

/-- The 1.x income tax (income tax + surtaxes + local income tax) of a household: for stacking (`stackedTax`). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (base.pit args c)

end NoGlobal
