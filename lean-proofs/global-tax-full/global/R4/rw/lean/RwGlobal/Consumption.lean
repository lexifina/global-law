import R4Common

/-!
# Rwanda 2025: VAT (5111) and excises (5121) (generated from `R4/specs/rw.json` by `R4/tools/gen_country.py`)

Sources: Official Gazette texts (trilingual) in `cmp20/world/B10-anglophone-africa/rw/law/` (law027_2022.txt, law051_2023.txt, law014_2025.txt). Third pass: VAT Law 049/2023 and Excise Law 011/2025 fetched from apis.amategeko.gov.rw (documents-files/4497, /10055).

Law 049/2023 art. 4: "... (b) or 18% for other goods and services supplied in Rwanda" (zero-rated and exempt supplies under the Law). Official gazette PDFs fetched from the amategeko.gov.rw API (`R4/rw/law/fetch/`, SHA256SUMS).

Law 011/2025 annex: "Beer whose local raw material content, excluding water, is at least 70% ... 40% ... Other beers 65% ... Wine whose local raw material content ... 40% ... Other wines 70% of the value of a litre not exceeding FRW 40,000 ... Lemonade, soda ... 39%"; art. 6 (b): "the tax base for a product manufactured in Rwanda ... is the selling price of the product" (taken as the value before excise and VAT). Grade B: in force from its publication (mid-2025; Law 050/2023 applied before) and the selling-price base read as the pre-tax value.
-/

namespace RwGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1800, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Law Nº 049/2023 of 05/09/2023 art. 4 (b) (18 %); Law Nº 009/2025 of 27/05/2025 does not change the rate"

-- the standard rate as printed: 18 % inside a tax-inclusive 11800
#guard vatX.embedded { good := .other, amount := 11800 } == 1800
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise duty (other beers)", advBp := 6500, vatBp := 1800, statute := "Law 011/2025 annex item 6 (65 %)" },
    { good := .wine, name := "Excise duty (other wines)", advBp := 7000, vatBp := 1800, statute := "Law 011/2025 annex item 8 (70 %)" },
    { good := .nonAlcoholic, name := "Excise duty (lemonade, soda)", advBp := 3900, vatBp := 1800, statute := "Law 011/2025 annex (39 %)" } ]
def excise : Family := R4.exciseFamily "Excise duty" accises
-- Law 011/2025 annex item 6 (65 %): 10000 paid for 1 unit(s) at 5 % vol → 3337
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty (other beers)", advBp := 6500, vatBp := 1800, statute := "Law 011/2025 annex item 6 (65 %)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [3337]
-- Law 011/2025 annex item 8 (70 %): 10000 paid for 1 unit(s) at 12 % vol → 3488
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty (other wines)", advBp := 7000, vatBp := 1800, statute := "Law 011/2025 annex item 8 (70 %)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [3488]
-- Law 011/2025 annex (39 %): 10000 paid for 1 unit(s) at 0 % vol → 2377
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Excise duty (lemonade, soda)", advBp := 3900, vatBp := 1800, statute := "Law 011/2025 annex (39 %)" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [2377]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["VAT 18 %; zero-rated and exempt supplies (Law 049/2023 annexes) not separated from the basket lines", "Law 011/2025: beer and wine with at least 70 % local raw material are at 40 % (not separable); spirits, tobacco, fuel and the pre-publication Law 050/2023 rates not modelled"]

end RwGlobal
