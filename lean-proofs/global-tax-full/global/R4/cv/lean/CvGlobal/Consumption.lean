import R4Common

/-!
# Cabo Verde 2025: VAT (5111) and excises (5121) (generated from `R4/specs/cv.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: the 2025 State Budget law and the 2020-2021 tax laws are held; IVA and IRPC rates were not located in the extraction. Pass 10 (IRPC/retenções): Lei n.º 86/IX/2020 republications (`world/B07-west-africa-fr-pt/cv/src/Lei-86-IX-2020.flow.txt`: CIRPC art. 84-89 from line ~10150, CIRPS art. 14, 48-52 from line ~11352) and OE 2025 (`OE-2025.flow.txt` art. 25-26, 73).

Secondary-source sweep (2026-11-22): the guide, reviewed in July 2025, puts the general IVA rate at 15 % and the rate on electricity and water for private consumers at 8 %; the 8 % is also in the 2025 State Budget law, art. 73.º, already held. Exempt and zero-rated supplies are not listed in the guide: not applied (every other good at 15 %). Grade B: the Código do IVA was not read.


-/

namespace CvGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Imposto sobre o Valor Acrescentado (IVA)", standard := 1500, reduced := 800, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .electricity | .water => .reduced
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Código do IVA (not held): standard rate 15 % from PwC Worldwide Tax Summaries, Cabo Verde, Individual - Other taxes (last reviewed 15 July 2025, Wayback capture 2025-12-16, R4/fetch/swp/pwc_cv_indother_wb20251216.txt); 8 % on electricity and water supplied to private consumers: OE 2025 art. 73.º (held, world/B07-west-africa-fr-pt/cv/src/OE-2025) and the same guide"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500
#guard vatX.embedded { good := .electricity, amount := 10800 } == 800
#guard vatX.embedded { good := .water, amount := 10800 } == 800

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["exempt supplies (the guide lists none) not applied: rent, health, education and financial services are charged at 15 % here (overstates where exempt in the Código)", "excises not modelled: the 2025 State Budget law and the 2020-2021 tax laws are held; IVA and IRPC rates were not located in the extraction"]

end CvGlobal
