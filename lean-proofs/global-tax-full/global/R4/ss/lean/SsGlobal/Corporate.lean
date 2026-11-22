import R4Common
import R4Common.Dated

/-!
# South Sudan 2025: corporate income tax (1200) and withholding (generated from `R4/specs/ss.json`)

No usable 2025 text for these headings: Financial Acts 2023/24 and 2024/25 are held but not mapped in this pass. Second pass: Financial Act 2024/2025 (FY July 2024 - June 2025); the 2025/26 Act not held. Pass 10 (sales tax/excise): Financial Act 2024/2025 OCR (`world/B10-anglophone-africa/ss/law/fa2425_ocr.txt`) chapters 5-8 and Schedule 1 (A) items 6-7; Taxation Amendment Act 2016 OCR (`taxact2016_ocr.txt`, assented 20 December 2016) Schedules 4-6; Financial Act 2023/2024 (`financial_act_2023_2024.txt`) Schedule 1 item 2 for comparison.



Schedule 1 (2): "Dividends 10% 10% / Interest 10% 10% / Royalties 10% 10% / Rent 20% 20% / ... Technical/consultancy fees 20% 20%" (the FY 2023/24 and FY 2024/25 columns agree). Rates apply to payments generally (no separate non-resident schedule).
-/

namespace SsGlobal
open TaxKernel TaxKernel.Global

def whtD : List R4.DatedWhtRule :=
  [{ rule := { kind := .dividend, rateBp := 1000, statute := "Financial Act 2024/25 Sch. 1 (2) (10 %) (to 30 June 2025)" }, validFrom := "", validTo := "2025-07-01" },
   { rule := { kind := .interest, rateBp := 1000, statute := "Financial Act 2024/25 Sch. 1 (2) (10 %) (to 30 June 2025)" }, validFrom := "", validTo := "2025-07-01" },
   { rule := { kind := .royalty, rateBp := 1000, statute := "Financial Act 2024/25 Sch. 1 (2) (10 %) (to 30 June 2025)" }, validFrom := "", validTo := "2025-07-01" },
   { rule := { kind := .services, rateBp := 2000, statute := "Financial Act 2024/25 Sch. 1 (2) technical/consultancy fees (20 %) (to 30 June 2025)" }, validFrom := "", validTo := "2025-07-01" }]
#guard (R4.whtAtDay "Withholding tax (Schedule 1 (2))" whtD ((R4.isoDay? "2025-01-01").getD 0)).amount { kind := .dividend, amount := 1000000 } == 100000
#guard (R4.whtAtDay "Withholding tax (Schedule 1 (2))" whtD ((R4.isoDay? "2025-01-01").getD 0)).amount { kind := .interest, amount := 1000000 } == 100000
#guard (R4.whtAtDay "Withholding tax (Schedule 1 (2))" whtD ((R4.isoDay? "2025-01-01").getD 0)).amount { kind := .royalty, amount := 1000000 } == 100000
#guard (R4.whtAtDay "Withholding tax (Schedule 1 (2))" whtD ((R4.isoDay? "2025-01-01").getD 0)).amount { kind := .services, amount := 1000000 } == 200000
def corporate : Family :=
  { name := "1200 withholding", covers := [],
    run := fun _ g _ => if g.entity != .company then [] else R4.datedWhtCharges "Withholding tax (Schedule 1 (2))" whtD g }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CIT not modelled: BPT 30 % is set by the Financial Act 2024/2025 for FY 2024/25 (to 30 June 2025); the Financial Act 2025/2026 (FY 1 July 2025-30 June 2026) was not found: NRA uploads (cms.nra.gov.ss) and MoFEP (mofep-grss.org) document pages on the Internet Archive (CDX, 21 Nov 2026) hold the Acts for 2014/15-2024/25 only, so the rate for July-December 2025 is not known and a 2025 profit cannot be taxed (twentieth pass: B -> C)", "twentieth pass (year in force): the Schedule 1 (2) rates apply to payments dated to 30 June 2025; a payment dated later or without a date is not computed (grade C)"] ++ R4.datedWhtNotes "Withholding tax (Schedule 1 (2))" whtD "Financial Act 2024/2025 to 30 June 2025; the 2025/2026 Act not found" g

end SsGlobal
