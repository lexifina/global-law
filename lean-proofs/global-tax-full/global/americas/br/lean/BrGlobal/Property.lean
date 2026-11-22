import BrGlobal.Pit

/-!
# BR 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (Lei SP 10.705/2000 (ITCMD 4 %)): tried not read in this pass; would unlock: the act's 2025 text.
-/

namespace BrGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon BrGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 12): Constituição art. 150 I: \"exigir ou aumentar tributo sem lei que o estabeleça\" (`br/law/const_art-150.md`); Constituição art. 153 VII: \"grandes fortunas, nos termos de lei complementar\" (`br/law/const_art-153.md`). The tax on grandes fortunas of art. 153 VII needs a lei complementar, which has not been enacted; no law read in this build levies a recurrent tax on net wealth (laws read include: Lei SP 6.374/1989 art. 34; Lei 10.637/2002 art. 2; Lei municipal 13.701/2003 art. 16; TIPI (Decreto 11.158/2022), RFB consolidated table updated to ADE RFB 5/2026 (no chapter 22 or 24 change noted after 2022): 2202.10.00 / 2202.99.00 2,6 %; Decreto 7.212/2010 art. 212-B (Decreto 12.127/2024); Lei 10.336/2001 art. 5)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end BrGlobal.Property
