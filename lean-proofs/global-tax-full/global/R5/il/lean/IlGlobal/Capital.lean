import TaxKernel.Global
import R5Common
import IlTax

/-!
# Israel 2025: individuals' capital income and gains (1100), routed through the 1.x model

The 1.x PIT model already taxes the household's interest, dividends, rents and capital gains (fields of `Canon`); the
detail items of a global line (disposals, extra incomes) are routed into those fields and taxed by the 1.x model
(`R5Common.stackedCapital`, kernel `stackedTax`): the statute is the 1.x model's (Income Tax Ordinance s. 91, 125B as applied by the 1.x model (25 %)).
Grade B: the routing rule (every disposal's net gain is a taxable gain) is not itself read from the code.
-/

namespace IlGlobal
open TaxKernel TaxKernel.Global R5Common

def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (IlTax.country.computeWith args c).toJson

def capital : Family := stackedCapital pitOf "Income tax on capital income and gains (routed)" "Income Tax Ordinance s. 91, 125B as applied by the 1.x model (25 %)"

def capitalUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || g.disposals.isEmpty then [] else ["real-estate gains fall under the Real Estate Taxation Law (betterment tax), not modelled; s. 91 indexation not read"]

end IlGlobal
