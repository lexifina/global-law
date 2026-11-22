import R4Common

/-!
# Central African Republic 2025: VAT (5111) and excises (5121) (generated from `R4/specs/cf.json` by `R4/tools/gen_country.py`)

Sources: Code général des impôts, édition officielle mise à jour 2023 (`cmp20/world/B08-central-africa-fr/cf/law/cgi2023.txt`); LF 2025 OCR pages 1-60 (`lf2025.ocr1-60.txt`).

art. 257: "Le taux général de 19%, le taux réduit de 5% et le taux 0% s'appliquent à une base calculée hors TVA"; the 5 % list (milk and cream of heading 04.01 …) sits in the food line. Exemptions not read.


-/

namespace CfGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1900, reduced := 500, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "CGI art. 257 (taux général 19 %, réduit 5 %, 0 %)"

-- the standard rate as printed: 19 % inside a tax-inclusive 11900
#guard vatX.embedded { good := .other, amount := 11900 } == 1900

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["CGI art. 257: the 5 % list of staples (milk, …) is inside the food line, taxed at 19 %; exemptions not read", "excises not modelled: CGI art. 292: \"Les montants et taux des droits d'accises sont fixés par la loi de finances\"; the LF 2025 pages available (1-60 OCR) do not hold the table"]

end CfGlobal
