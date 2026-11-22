import R4Common

/-!
# Chad 2025: VAT (5111) and excises (5121) (generated from `R4/specs/td.json` by `R4/tools/gen_country.py`)

Sources: CGI 2016 (`world/B08-central-africa-fr/td/law/cgi2016.raw.txt`), LF 2023 OCR (`lf2023.ocr.txt`), DGI circular on LF 2024 (`circ_lf2024.raw.txt`; the LF 2024 PDF itself is unreadable), LF 2025 OCR (`lf2025.ocr.txt`).

LF 2023 art. 16, art. 238 (nouveau): "Les taux de la taxe sur la valeur ajoutée sont les suivants : 1° 18 % applicable à toutes les opérations taxables ; 2° 9 % applicable aux produits locaux ci-après : ciment, sucre, huile, savon, textile ... produits et sous-produits de l'industrie agroalimentaire locale hors alcool". LF 2025 art. 32, art. 14 LF 2024 (nouveau): "il est institué au profit des Conseils Provinciaux et des Communes, des centimes additionnels sur les impôts et taxes ci-après : La taxe sur la valeur ajoutée (TVA) ; La Taxe spécifique sur les liqueurs ; (2) Le taux des centimes additionnels est fixé à 10 % du principal de l'impôt concerné." 18 % x 1,10 = 19,8 %. LF 2025 does not amend art. 238; the DGI circular on LF 2024 lists no change to it.


-/

namespace TdGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée + centimes additionnels", standard := 1980, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "CGI art. 238 1° as substituted by LF 2023 art. 16 (18 %); LF 2024 art. 14 as substituted by LF 2025 art. 32 (centimes additionnels 10 % of the VAT principal): 19,8 %"

-- the standard rate as printed: 19.8 % inside a tax-inclusive 11980
#guard vatX.embedded { good := .other, amount := 11980 } == 1980

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["CGI art. 238 2°: the 9 % rate on listed local products (sugar, oil, soap, local agri-food) is not separable from the basket lines: taxed at the standard rate", "excises not modelled: excise schedule (CGI 2016 art. 255 ff.) amended by LF 2017-2022 that are not held; LF 2025 art. 28 concerns a telecom levy"]

end TdGlobal
