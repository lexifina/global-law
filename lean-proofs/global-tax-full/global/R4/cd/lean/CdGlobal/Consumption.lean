import R4Common

/-!
# DR Congo 2025: VAT (5111) and excises (5121) (generated from `R4/specs/cd.json` by `R4/tools/gen_country.py`)

Sources: Code des impôts 2023 (`cmp20/world/B08-central-africa-fr/cd/law/CODE-DES-IMPOTS-2023.txt`). Pass 11: Code des accises (Ordonnance-loi n° 18/002 du 8 mars 2018) from droitcongolais.info (file 621.03.18-Code-des-accises.pdf, R4/fetch/cd11, SHA256SUMS); finance laws 2019-2025 not read for later changes.

TVA art. 35: "les taux de la taxe sur la valeur ajoutée sont les suivants : taux normal : 16% applicable à toutes les opérations imposables à l'exclusion des opérations soumises au taux" réduit / zéro (lists not read). Exemptions not read.

art. 28: '17) bières de malt: i. d'un titre alcoométrique volumique excédant 0,5 % vol titrant moins de 6° 24 %; ii. ... titrant 6° et plus 28 %; 18) boissons à base de jus de fruits ou de légumes, limonades et autres boissons sucrées, aromatisées ou non: 10 %; 22) cigares ... cigarillos et cigarettes ...: 60 %; 31) eaux de vie, liqueurs et autres boissons spiritueuses: 80 %; 33) essences ... gasoils ...: i. essences et gasoils et autres produits: 25 %; 75) vins de raisins frais, y compris les vins enrichis en alcool: 45 %'.
-/

namespace CdGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1600, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Ordonnance-loi TVA art. 35 (taux normal 16 %) [text version: Ordonnance-loi TVA as printed in the DGI Code des impôts, édition 2023 (texts in force to 2023); the finance laws for 2024 and 2025 not held (flag)]"

-- the standard rate as printed: 16 % inside a tax-inclusive 11600
#guard vatX.embedded { good := .other, amount := 11600 } == 1600
def accises : List R4.Exc :=
  [ { good := .beer, name := "Droits d'accises bières de malt (< 6°)", advBp := 2400, vatBp := 1600, maxAbvBp := 599, statute := "art. 28 17) i.: 24 %" },
    { good := .beer, name := "Droits d'accises bières de malt (6° et plus)", advBp := 2800, vatBp := 1600, minAbvBp := 599, statute := "art. 28 17) ii.: 28 %" },
    { good := .wine, name := "Droits d'accises vins", advBp := 4500, vatBp := 1600, statute := "art. 28 75): 45 %" },
    { good := .spirits, name := "Droits d'accises boissons spiritueuses", advBp := 8000, vatBp := 1600, statute := "art. 28 31): 80 %" },
    { good := .nonAlcoholic, name := "Droits d'accises boissons sucrées", advBp := 1000, vatBp := 1600, statute := "art. 28 18): 10 %" },
    { good := .cigarettes, name := "Droits d'accises cigarettes", advBp := 6000, vatBp := 1600, statute := "art. 28 22): 60 %" },
    { good := .petrol, name := "Droits d'accises essences", advBp := 2500, vatBp := 1600, statute := "art. 28 33) i.: 25 %" },
    { good := .diesel, name := "Droits d'accises gasoils", advBp := 2500, vatBp := 1600, statute := "art. 28 33) i.: 25 %" } ]
def excise : Family := R4.exciseFamily "Droits d'accises" accises
-- art. 28 17) i.: 24 %: 10000 paid for 1 unit(s) at 5 % vol → 1668
#guard (R4.exciseCharges [{ good := .beer, name := "Droits d'accises bières de malt (< 6°)", advBp := 2400, vatBp := 1600, maxAbvBp := 599, statute := "art. 28 17) i.: 24 %" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [1668]
-- art. 28 17) ii.: 28 %: 10000 paid for 1 unit(s) at 6.99 % vol → 1885
#guard (R4.exciseCharges [{ good := .beer, name := "Droits d'accises bières de malt (6° et plus)", advBp := 2800, vatBp := 1600, minAbvBp := 599, statute := "art. 28 17) ii.: 28 %" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 699 }] []).map (·.due) == [1885]
-- art. 28 75): 45 %: 10000 paid for 1 unit(s) at 12 % vol → 2674
#guard (R4.exciseCharges [{ good := .wine, name := "Droits d'accises vins", advBp := 4500, vatBp := 1600, statute := "art. 28 75): 45 %" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [2674]
-- art. 28 31): 80 %: 10000 paid for 1 unit(s) at 40 % vol → 3830
#guard (R4.exciseCharges [{ good := .spirits, name := "Droits d'accises boissons spiritueuses", advBp := 8000, vatBp := 1600, statute := "art. 28 31): 80 %" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [3830]
-- art. 28 18): 10 %: 10000 paid for 1 unit(s) at 0 % vol → 783
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Droits d'accises boissons sucrées", advBp := 1000, vatBp := 1600, statute := "art. 28 18): 10 %" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [783]
-- art. 28 22): 60 %: 10000 paid for 1 unit(s) at 0 % vol → 3232
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Droits d'accises cigarettes", advBp := 6000, vatBp := 1600, statute := "art. 28 22): 60 %" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [3232]
-- art. 28 33) i.: 25 %: 10000 paid for 1 unit(s) at 0 % vol → 1724
#guard (R4.exciseCharges [{ good := .petrol, name := "Droits d'accises essences", advBp := 2500, vatBp := 1600, statute := "art. 28 33) i.: 25 %" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1724]
-- art. 28 33) i.: 25 %: 10000 paid for 1 unit(s) at 0 % vol → 1724
#guard (R4.exciseCharges [{ good := .diesel, name := "Droits d'accises gasoils", advBp := 2500, vatBp := 1600, statute := "art. 28 33) i.: 25 %" }] [{ good := .diesel, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1724]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["DR Congo: Code des impôts 2023; reduced 8 % list and exemptions not read", "fuel prices in the DRC are administered (structure des prix): the region's ad valorem convention (value before excise and VAT) is applied", "the 'titrant 6°' threshold is read as 6 % vol", "mineral waters 5 %, other non-alcoholic drinks 15 % not separated"]

end CdGlobal
