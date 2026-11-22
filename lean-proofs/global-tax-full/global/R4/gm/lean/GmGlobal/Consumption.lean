import R4Common

/-!
# Gambia 2025: VAT (5111) and excises (5121) (generated from `R4/specs/gm.json` by `R4/tools/gen_country.py`)

Sources: Gambia Revenue Authority VAT leaflet (registry fetch `global/registry/afm_data/fetch/GM/gm_vat.pdf.txt`, official secondary). Pass 10 (CIT/WHT): GRA brochures fetched from www.gra.gm/download-file/<id> (ids from `world/B10-anglophone-africa/gm/law/rescue2/gra_downloads.html`): 8d0c7954 'Corporation Income Tax', 8d0d0925 'Witholding Tax', 8d0c84c3 'Dividend Income Tax', in `R4/fetch/gm10/` (SHA256SUMS).

GRA leaflet: "The standard VAT rate is 15 percent … applied to all goods and services unless they are specifically" exempt; "Basic foods such as rice, sugar, flour, cooking oil, onions, potatoes, etc" are exempt (food line taxed at 15 % here). Source flagged official secondary.


-/

namespace GmGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1500, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "VAT Act 2012 (rate as stated by the GRA leaflet: 15 %; official secondary) [text version: GRA brochures as published on gra.gm on 21 August 2023 (the corporation-tax brochure dates its rate to 2018); Finance Acts 2024 and 2025 not held (flag)]"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["Gambia: VAT rate from the GRA leaflet (official secondary); exempt basic foods inside the food line", "excises not modelled: the Customs and Excise Act extraction (gm_cea.pdf.txt) was not mapped in this pass"]

end GmGlobal
