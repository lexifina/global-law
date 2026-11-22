import R4Common

/-!
# Zimbabwe 2025: VAT (5111) and excises (5121) (generated from `R4/specs/zw.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: Finance Acts 2024 and Veritas pages are held; the Income Tax Act rates (Charging Schedule) and the VAT Act were not resolved in this pass. Second pass: Finance Act 2025 (No. 7 of 2025) s. 34 (quotes the 2025 wording of the VAT general rate); Finance Acts 2023, 2024, 2024 (No. 2). Finance Act [Chapter 23:04], Income Tax Act [Chapter 23:06] and VAT Act [Chapter 23:12] as updated by ZIMRA to 1 December 2024 (incorporating the Finance (No. 2) Act 7 of 2024 amendments from 1 January 2025), from zimra.co.zw/legislation/17-acts (`cmp20/global/R4/fetch/zw8/`, SHA256SUMS).

Finance Act 2025 s. 34: "With effect from the 1st January, 2026, the Schedule to Chapter IV of the Finance Act [Chapter 23:04] is amended in Part I ('General Rate of Value Added Tax') by the deletion of 'fifteen per centum' and the substitution of 'fifteen comma five per centum'." So the general rate in force throughout 2025 was 15 %. The Schedule itself was not read (grade B); zero-rated and exempt supplies not applied.


-/

namespace ZwGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1500, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Finance Act [Chapter 23:04] Chapter IV Schedule Part I ('fifteen per centum'), as shown by Finance Act 2025 s. 34 (15,5 % only from 1 Jan 2026)"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["VAT 15 % in 2025 (Finance Act 2025 s. 34 raises it to 15,5 % from 1 Jan 2026); zero-rated basic foods not separable", "excises not modelled: Finance Acts 2024 and Veritas pages are held; the Income Tax Act rates (Charging Schedule) and the VAT Act were not resolved in this pass"]

end ZwGlobal
