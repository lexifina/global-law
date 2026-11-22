import R4Common

/-! # LR 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace LrGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .transactions, why := "LR: no stamp duty or transfer duty. LRC s. 4 lists the taxes in effect (income tax and royalties, GST, excise, customs duties, real property tax, government agency fees); s. 3 (c)-(d): all changes to taxation are made by amendments to the Code and taxation may not be included in non-tax legislation. Chapter 20 (real property tax) s. 2005 only requires registrars of deeds to report conveyances. Deed registration and probate charges are fees, not modelled." },
   { oecd := .wealth, why := "LR: the general tax code held (REVENUE-CODE-LIBERIA-REVENUE-CODE-AMENDEMENT-2020-min.txt) has no charging provision on net wealth (full-text search 'impôt sur la fortune / le patrimoine', 'patrimoine net'); edition as held, later finance laws not all checked" }]

#guard absentList.length == 2

end LrGlobal
