import R4Common

/-!
# Ghana 2025: VAT (5111) and excises (5121) (generated from `R4/specs/gh.json` by `R4/tools/gen_country.py`)

Sources: VAT Act 2013 (Act 870) (registry fetch `global/registry/afm_data/fetch/GH/gh_vat870.pdf.txt`); Income Tax Act 2015 (Act 896) OCR (`world/B10-anglophone-africa/gh/law/act896_ocr.txt`).

s. 3: "Except as otherwise provided in this Act, the rate of the tax is fifteen percent and is calculated on the value of the taxable supply". The NHIL, GETFund levy and COVID-19 levy charged with VAT (separate acts), the flat-rate scheme and the exempt schedule were not read; the 2025 VAT reform (Act 1151, 2025) not checked.


-/

namespace GhGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1500, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "VAT Act 2013 (Act 870) s. 3 (15 %) [text version: Act 870 (2013) and Act 896 (2015) as enacted (gazetted copies), Act 896 para 3 (1) as restated by Act 1094 (2023); later amending Acts not consolidated (flag)]"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["Ghana: NHIL, GETFund and COVID-19 levies (separate acts) and the VAT exempt schedule not modelled; every line at 15 %", "excises not modelled: only an abridged guide of Act 878 is held (a secondary text) and the 2023-2025 amendments are not"]

end GhGlobal
