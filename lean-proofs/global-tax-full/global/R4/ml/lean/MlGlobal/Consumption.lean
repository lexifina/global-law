import R4Common

/-!
# Mali 2025: VAT (5111) and excises (5121) (generated from `R4/specs/ml.json` by `R4/tools/gen_country.py`)

The only local text is a CGI edition with amendment notes up to the LF 2018 (`cmp20/world/B07-west-africa-fr-pt/ml/src/CGI.txt`) and the DGI 2025 activity report (`RA-DGI-2025.ocr.txt`). Pass 9: the DGI's own online CGI (https://www.dgi.gouv.ml/CGI/, the 'Code Général des Impôts' link of dgi.gouv.ml, re-checked 2026-11-21) is still the 2017 consolidation held as `world/B07-west-africa-fr-pt/ml/src/CGI.txt`; the DGI annual report 2025 (`RA-DGI-2025.ocr.txt`) reports receipts only. Per the region convention an edition older than 2025 with no later finance law in hand is graded B and flagged.

art. 229 (Sous-section 6 - Taux de la TVA): "(Loi n°11-078) Les taux de la TVA sont fixés ainsi qu'il suit : 5 % pour les produits visés au point D de la sous-section 1 de la section 1 du chapitre 1 du titre 2 du CGI ci-dessus ; 18 % pour les autres produits et les services non exonérés en application des dispositions du point IV (Produits) de l'article 195 du CGI ci-dessus."


-/

namespace MlGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1800, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "CGI (consolidation 2017) art. 229 (Loi n°11-078): 5 % for the products of point D, 18 % for other products and non-exempt services — edition of 2017, flagged"

-- the standard rate as printed: 18 % inside a tax-inclusive 11800
#guard vatX.embedded { good := .other, amount := 11800 } == 1800

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["2017 consolidation (no LF 2018-2025 held): the 2025 rate is not confirmed by a 2025 text", "the art. 195 exemptions and the 5 % point-D products are not applied", "excises not modelled: rates set by decree n° 2015-0548 within art. 240 ranges; 2025 rates not available"]

end MlGlobal
