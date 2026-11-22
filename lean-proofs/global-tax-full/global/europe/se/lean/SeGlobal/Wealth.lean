import SeGlobal.Pit

/-!
# SE 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (arvsskatt abolished 2005 (not cited)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (förmögenhetsskatt abolished 2007 (not cited)): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited)**: Lag (1997:323) om statlig förmögenhetsskatt: the act's record at Regeringskansliet/Lagrummet (data.riksdagen.se sfs-1997-323) reads "Upphävd: 2008-01-01": no net wealth tax in 2025

* **4300 not levied (cited)**: Lag (1941:416) om arvsskatt och gåvoskatt: the act's record at Regeringskansliet/Lagrummet (data.riksdagen.se sfs-1941-416) reads "Upphävd: 2005-01-01": no inheritance or gift tax in 2025
-/

namespace SeGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "the act's record at Regeringskansliet/Lagrummet (data.riksdagen.se sfs-1997-323) reads \"Upphävd: 2008-01-01\": no net wealth tax in 2025" },
   { oecd := .estate, why := "the act's record at Regeringskansliet/Lagrummet (data.riksdagen.se sfs-1941-416) reads \"Upphävd: 2005-01-01\": no inheritance or gift tax in 2025" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end SeGlobal.Wealth
