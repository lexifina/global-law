import TaxKernel.Global

/-!
# Kuwait 2025: no VAT, no general sales tax, no excise (5111, 5112, 5121: cited absences)

Kuwait has enacted neither a VAT law nor an excise law under the GCC common agreements. Its tax acts are the Income
Tax Decree No. 3 of 1955 (as amended by Law 2/2008), Law 19/2000 (National Labour Support Tax), Law 46/2006 (zakat
contribution of shareholding companies) and Decree-Law 157/2024 (multinational group top-up tax), per the registry
agent's statute map (`registry/AFRICA_MENA.json`, records KW vat / excise_* "exists: no"). Grade of the absence: B
(no official database search result saved for the negative).
-/

namespace KwGlobal
open TaxKernel TaxKernel.Global

def consumptionAbsent : List Absent :=
  [{ oecd := .vat, why := "No VAT law enacted (tax acts: Income Tax Decree 3/1955, Law 19/2000, Law 46/2006, Decree-Law 157/2024)" },
   { oecd := .salesTax, why := "No general sales tax law" },
   { oecd := .excise, why := "No excise law enacted under the GCC Common Excise Agreement" }]

end KwGlobal
