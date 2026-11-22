import R4Common
import R4Common.Dated

/-!
# Ethiopia 2025: corporate income tax (1200) and withholding (generated from `R4/specs/et.json`)

Sources: VAT Proclamation No. 1341/2024 (registry fetch `global/registry/afm_data/fetch/ET/et_vat_1341.pdf.txt`); Income Tax (Amendment) Proclamation No. 1395/2025 (`world/B10-anglophone-africa/et/law/mor_proc_1395.txt`, in force 8 July 2025); Income Tax Proclamation No. 979/2016 (`mor_proc_979.txt`: the extraction keeps the tables but not the provisions' wording). Pass 9 (CIT/WHT): Federal Income Tax Proclamation No. 979/2016 (Negarit Gazette 22nd year No. 104, `world/B10-anglophone-africa/et/law/mor_proc_979.txt`) read in its Amharic text (the English column is not in the extraction; the Amharic is clean UTF-8): art. 19 (1) and art. 51 (2). Proclamation 1395/2025 (`mor_proc_1395.txt`, Negarit Gazette 31st year No. 64, 1 September 2025) replaces the non-resident rates from EFY 2018 (8 July 2025) and adds an alternative minimum tax; Proclamation 1157/2019 not read (flagged). Pass 10 (excise): the Ministry of Revenues' full scans of the Excise Tax Proclamation No. 1186/2020 (88 pages) and the Excise Tax (Amendment) Proclamation No. 1287/2023 (18 pages, with the replacing First Schedule) via Wayback (`mor.gov.et/documents/49818/172546/Excise+Tax+Proclamation+1186-2012.pdf/…`, `mor.gov.et/documents/49818/0/1287-2015+…pdf/…`), in `R4/fetch/et10/` (OCR eng; the schedule was read on the page images, pp. 9-11 of 1287). The earlier copies in `R4/fetch/et9/` lacked the schedule pages. Pass 10 (excise): the Ministry of Revenues' full scans of the Excise Tax Proclamation No. 1186/2020 (88 pages) and the Excise Tax (Amendment) Proclamation No. 1287/2023 (18 pages, with the replacing First Schedule) via Wayback (`mor.gov.et/documents/49818/172546/Excise+Tax+Proclamation+1186-2012.pdf/…`, `mor.gov.et/documents/49818/0/1287-2015+…pdf/…`), in `R4/fetch/et10/` (OCR eng; the schedule was read on the page images, pp. 9-11 of 1287). The earlier copies in `R4/fetch/et9/` lacked the schedule pages.

Proc. 979/2016 art. 19 (Amharic text): (numbered '09.' in the extraction, Ethiopic tens lost) "በንግድ ሥራ ገቢ ላይ ተፈፃሚ የሚሆኑ መጣኔዎች 1/ በድርጅት ላይ ተፈፃሚ የሚሆነው የንግድ ሥራ ገቢ የግብር መጣኔ ሰላሳ በመቶ (፴%) ነው፡፡" (the business income tax rate applicable to a body is thirty percent).

Proc. 979/2016 art. 51 (Amharic text): "1/ በኢትዮጵያ ነዋሪ ያልሆነ ሰው የትርፍ ድርሻ፣ ወለድ፣ ሮያሊቲ፣ የሥራ አመራር ክፍያ፣ የቴክኒክ አገልግሎት ክፍያ ወይም የመድን አረቦን ከኢትዮጵያ ውስጥ ያገኘ እንደሆነ በዚህ አንቀጽ ንዑስ አንቀጽ (2) በተመለከተው መጣኔ መሠረት ግብር የመክፈል ግዴታ አለበት፡፡ 2/ በኢትዮጵያ ነዋሪ ያልሆነ ሰው ግብር የሚከፍልበት መጣኔ፡- ሀ) ለመድህን በሚከፈል አረቦን ወይም ከሮያሊቲ ጠቅላላው ክፍያ ላይ 5% (አምስት በመቶ)፤ ለ) ከትርፍ ድርሻ ወይም ከወለድ፣ ጠቅላላ ገቢ ላይ 10% (አስር በመቶ)፤ ሐ) ከስራ አመራር ክፍያ ወይም ከቴክኒክ አገልግሎት ክፍያ ከጠቅላላ ገቢው ላይ 15% (አሥራ አምስት በመቶ)" (the extraction prints the Ethiopic-numeral tens as '0%'/'05%'; the words in brackets read ten and fifteen percent).
-/

namespace EtGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Business income tax (bodies)", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3000299
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 300000
def whtD : List R4.DatedWhtRule :=
  [{ rule := { kind := .royalty, rateBp := 500, statute := "Proc. 979/2016 art. 51 (2) (a): 5 % (to 6 August 2025)" }, validFrom := "", validTo := "2025-08-07" },
   { rule := { kind := .royalty, rateBp := 1000, statute := "Proc. 1395/2025 art. 52 (2) (Schedule D tax collected from 7 August 2025, art. 4 (2)) (a): 10 %" }, validFrom := "2025-08-07", validTo := "" },
   { rule := { kind := .dividend, rateBp := 1000, statute := "Proc. 979/2016 art. 51 (2) (b): 10 % (to 6 August 2025)" }, validFrom := "", validTo := "2025-08-07" },
   { rule := { kind := .dividend, rateBp := 1500, statute := "Proc. 1395/2025 art. 52 (2) (Schedule D tax collected from 7 August 2025, art. 4 (2)) (b): 15 %" }, validFrom := "2025-08-07", validTo := "" },
   { rule := { kind := .interest, rateBp := 1000, statute := "Proc. 979/2016 art. 51 (2) (b): 10 % (to 6 August 2025)" }, validFrom := "", validTo := "2025-08-07" },
   { rule := { kind := .interest, rateBp := 1000, statute := "Proc. 1395/2025 art. 52 (2) (Schedule D tax collected from 7 August 2025, art. 4 (2)) (c): 10 %" }, validFrom := "2025-08-07", validTo := "" },
   { rule := { kind := .services, rateBp := 1500, statute := "Proc. 979/2016 art. 51 (2) (c): management or technical service fee 15 % (to 6 August 2025)" }, validFrom := "", validTo := "2025-08-07" },
   { rule := { kind := .services, rateBp := 1500, statute := "Proc. 1395/2025 art. 52 (2) (Schedule D tax collected from 7 August 2025, art. 4 (2)) (d): management or technical fee 15 %" }, validFrom := "2025-08-07", validTo := "" }]
#guard (R4.whtAtDay "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD ((R4.isoDay? "2025-01-01").getD 0)).amount { kind := .royalty, amount := 1000000 } == 50000
#guard (R4.whtAtDay "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD ((R4.isoDay? "2025-08-07").getD 0)).amount { kind := .royalty, amount := 1000000 } == 100000
#guard (R4.whtAtDay "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD ((R4.isoDay? "2025-01-01").getD 0)).amount { kind := .dividend, amount := 1000000 } == 100000
#guard (R4.whtAtDay "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD ((R4.isoDay? "2025-08-07").getD 0)).amount { kind := .dividend, amount := 1000000 } == 150000
#guard (R4.whtAtDay "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD ((R4.isoDay? "2025-01-01").getD 0)).amount { kind := .interest, amount := 1000000 } == 100000
#guard (R4.whtAtDay "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD ((R4.isoDay? "2025-08-07").getD 0)).amount { kind := .interest, amount := 1000000 } == 100000
#guard (R4.whtAtDay "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD ((R4.isoDay? "2025-01-01").getD 0)).amount { kind := .services, amount := 1000000 } == 150000
#guard (R4.whtAtDay "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD ((R4.isoDay? "2025-08-07").getD 0)).amount { kind := .services, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Business income tax (bodies)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Federal Income Tax Proclamation No. 979/2016 art. 19 (1) (business income tax rate for bodies 30 %); unchanged by Proclamation 1395/2025" (step := 1)] ++ R4.datedWhtCharges "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD g }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["the alternative minimum tax of Proclamation 1395/2025 (EFY 2018, from 8 July 2025) is not modelled; Proclamation 1157/2019 (amendment) not read (flagged); the Ethiopian fiscal year runs 8 July-7 July", "only management/technical fees are taxed among service payments (other services by non-residents without a PE are outside art. 51)", "twentieth pass (year in force): split at 7 August 2025 (Proclamation 1395/2025 art. 4 (2): 'The tax to be collected on schedule D income and the withholding tax collected on transactions ... shall become effective as of August 7, 2025'): a payment dated to 6 August bears the Proclamation 979/2016 rates, from 7 August the 1395/2025 rates; an undated royalty or dividend is not computed (grade C), undated interest and fees bear the unchanged 10 % / 15 %"] ++ R4.datedWhtNotes "Income tax on non-residents' Ethiopian-source payments (Schedule D)" whtD "Proclamation No. 1395/2025 art. 4 (2): royalty 5 -> 10 %, dividend 10 -> 15 % from 7 August 2025" g

end EtGlobal
