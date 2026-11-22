import R4Common

/-!
# Nigeria 2025: VAT (5111) and excises (5121) (generated from `R4/specs/ng.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: only Finance Act OCR fragments (2019-2023) are held; the 2025 consolidations (CITA, VAT Act) and the Nigeria Tax Act 2025 are not. Pass 9 (CIT): Finance Act 2019 (official gazette, firs.gov.ng/wp-content/uploads/2021/02/finance-act-2019-official-gazette-1.pdf via Wayback) and Finance Act 2021 (firs.gov.ng/wp-content/uploads/2022/04/Finance-Act-2021-Gazetted.pdf via Wayback), OCR (tesseract eng) in `R4/fetch/ng9/` (SHA256SUMS); Finance Act 2020 and 2023 OCR already held (`world/B02-g20/ng/law/`); Finance Act 2023 Part III amends CITA s. 14, 32, 34, 37 and the Second Schedule only. Finance Act 2022 not held (flagged). The Nigeria Tax Act 2025 applies from 2026. Thirteenth pass: FIRS public notice on withholding tax (Wayback copy of firs.gov.ng PUBLIC-NOTICE-ON-WHT-3.pdf, PDF dated 2015-06-10; `R4/fetch/p13/ng_wht_notice.pdf`) section 3 'Prevailing tax rates for WHT payments' (CITA Cap. C21 and the WHT regulations; final tax for non-residents). Fourteenth pass: Deduction of Tax at Source (Withholding) Regulations 2024, gazette copy (14 pages) saved as `R4/fetch/p14/ng_wht_regs2024.pdf`.

Finance Act 2020 (OCR) s. 42: "Substitute for section 4 of the Act, a new section '4': 'Rate of tax. 4. The tax shall be computed at the rate of 7.5% with effect from 1 February 2020, on the value of all goods and services, except that goods and services listed under Part III of the First Schedule to this Act shall be taxed at zero rate.'" Finance Act 2023 Part IX amends ss. 7, 14 and 16 only. The Nigeria Tax Act 2025 applies from 1 January 2026. Grade B: the FA 2021 (and FA 2022, if any) were not held.


-/

namespace NgGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 750, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Value Added Tax Act Cap. V1 LFN 2004 s. 4 as substituted by the Finance Act 2020 s. 42 (7,5 % from 1 February 2020); Finance Act 2023 Part IX (ss. 22-24) does not amend s. 4; Finance Act 2021 not held"

-- the standard rate as printed: 7.5 % inside a tax-inclusive 10750
#guard vatX.embedded { good := .other, amount := 10750 } == 750

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["First Schedule Part I/II exemptions (basic food items, medical and pharmaceutical products, books, educational materials, ...) and Part III zero-rated items are not applied: the schedules were not read", "excises not modelled: only Finance Act OCR fragments (2019-2023) are held; the 2025 consolidations (CITA, VAT Act) and the Nigeria Tax Act 2025 are not"]

end NgGlobal
