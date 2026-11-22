import R4Common

/-!
# Somalia 2025: VAT (5111) and excises (5121) (generated from `R4/specs/so.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: Law 37 and the 2020 Inland Revenue law OCR held; not mapped in this pass. Pass 10 (CIT/WHT): Law No. 37 of 11 May 2025 (Income Tax Law, Somali text, OCR `world/B10-anglophone-africa/so/law/law37_ocr.txt` of sharciga_cashuurta_dakhliga_37.pdf): First Schedule art. 3 and 5, art. 91-92, 105-106. The 2020 'Xeerarka Maaliyadda' held is the public financial management regulation (no tax rates).




-/

namespace SoGlobal
open TaxKernel TaxKernel.Global



def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["VAT not modelled: no sales-tax law is held: Law No. 37 of 2025 is the Income Tax Law (modelled under 1200) and the 2020 'Xeerarka Maaliyadda' is the public financial management regulation; the archived mof.gov.so PDFs hold only the 2020 customs tariff and valuation book", "excises not modelled: no excise text for 2025 is held (only the 2020 customs tariff schedule on mof.gov.so, not read)"]

end SoGlobal
