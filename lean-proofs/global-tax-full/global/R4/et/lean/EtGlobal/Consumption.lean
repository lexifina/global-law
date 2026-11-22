import R4Common

/-!
# Ethiopia 2025: VAT (5111) and excises (5121) (generated from `R4/specs/et.json` by `R4/tools/gen_country.py`)

Sources: VAT Proclamation No. 1341/2024 (registry fetch `global/registry/afm_data/fetch/ET/et_vat_1341.pdf.txt`); Income Tax (Amendment) Proclamation No. 1395/2025 (`world/B10-anglophone-africa/et/law/mor_proc_1395.txt`, in force 8 July 2025); Income Tax Proclamation No. 979/2016 (`mor_proc_979.txt`: the extraction keeps the tables but not the provisions' wording). Pass 9 (CIT/WHT): Federal Income Tax Proclamation No. 979/2016 (Negarit Gazette 22nd year No. 104, `world/B10-anglophone-africa/et/law/mor_proc_979.txt`) read in its Amharic text (the English column is not in the extraction; the Amharic is clean UTF-8): art. 19 (1) and art. 51 (2). Proclamation 1395/2025 (`mor_proc_1395.txt`, Negarit Gazette 31st year No. 64, 1 September 2025) replaces the non-resident rates from EFY 2018 (8 July 2025) and adds an alternative minimum tax; Proclamation 1157/2019 not read (flagged). Pass 10 (excise): the Ministry of Revenues' full scans of the Excise Tax Proclamation No. 1186/2020 (88 pages) and the Excise Tax (Amendment) Proclamation No. 1287/2023 (18 pages, with the replacing First Schedule) via Wayback (`mor.gov.et/documents/49818/172546/Excise+Tax+Proclamation+1186-2012.pdf/…`, `mor.gov.et/documents/49818/0/1287-2015+…pdf/…`), in `R4/fetch/et10/` (OCR eng; the schedule was read on the page images, pp. 9-11 of 1287). The earlier copies in `R4/fetch/et9/` lacked the schedule pages. Pass 10 (excise): the Ministry of Revenues' full scans of the Excise Tax Proclamation No. 1186/2020 (88 pages) and the Excise Tax (Amendment) Proclamation No. 1287/2023 (18 pages, with the replacing First Schedule) via Wayback (`mor.gov.et/documents/49818/172546/Excise+Tax+Proclamation+1186-2012.pdf/…`, `mor.gov.et/documents/49818/0/1287-2015+…pdf/…`), in `R4/fetch/et10/` (OCR eng; the schedule was read on the page images, pp. 9-11 of 1287). The earlier copies in `R4/fetch/et9/` lacked the schedule pages.

Proclamation 1341/2024: the VAT rate "b) in any other case 15 percent" (zero rate for the listed zero-rated supplies). The exempt-supply list was not resolved in the bilingual extraction: every basket line at 15 %.

Proclamation No. 1287/2023, First Schedule (Tariff Number / Description / Excise Rate): "2202.1000 Waters, including mineral waters and aerated waters, containing added sugar or other sweetening matter or flavoured 25%"; "2203.0000 Beer made from malt 40% or 11 Birr per liter, whichever is higher" (beer produced exclusively from barley grown and malted in Ethiopia 35 % or 9 Birr; local raw material content at least 75 % 30 % or 8 Birr); "2204.10 to 2205.90 Wine the local raw material content of which excluding water is at less than 75% by weight of its constituents 40%"; "2208.20 to 2208.70 Spirits obtained by distilling grape wine or grape marc, Whiskies, Rum ..., Gin and Geneva, Vodka, and Liqueurs and cordials 80%"; "2402.2000 Cigarettes containing tobacco 30% + 8 Birr per pack (20 stick)"; "Chapter 27 Kerosene, Benzene and Diesel Oils 15%". Proclamation 1287/2023, replaced charging provision (sub-article 2): "Excise Tax shall be charged at the rate specified in the first Schedule attached".
-/

namespace EtGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1500, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "VAT Proclamation No. 1341/2024 art. 7 (2) b) (15 %) [text version: Proclamation No. 1341/2024 as published (Federal Negarit Gazette No. 61, 21 August 2024)]"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise tax (beer made from malt, 2203.0000)", advBp := 4000, vatBp := 1500, minNum := 11000, minDen := 1000, statute := "Proc. 1287/2023 First Schedule 2203.0000: 40 % or 11 Birr per litre, whichever is higher" },
    { good := .wine, name := "Excise tax (wine, local content below 75 %)", advBp := 4000, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule 2204.10-2205.90: 40 %" },
    { good := .spirits, name := "Excise tax (spirits, 2208.20-2208.70)", advBp := 8000, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule 2208.20-2208.70: 80 %" },
    { good := .nonAlcoholic, name := "Excise tax (sweetened waters, 2202.1000)", advBp := 2500, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule 2202.1000: 25 %" },
    { good := .cigarettes, name := "Excise tax (cigarettes, 2402.2000)", perUnitNum := 400, perUnitDen := 1000, advBp := 3000, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule 2402.2000: 30 % + 8 Birr per pack of 20 (0.40 Birr per cigarette)" },
    { good := .petrol, name := "Excise tax (benzene)", advBp := 1500, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule chapter 27: kerosene, benzene and diesel oils 15 %" },
    { good := .diesel, name := "Excise tax (diesel oils)", advBp := 1500, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule chapter 27: kerosene, benzene and diesel oils 15 %" } ]
def excise : Family := R4.exciseFamily "Excise tax" accises
-- Proc. 1287/2023 First Schedule 2203.0000: 40 % or 11 Birr per litre, whichever is higher: 10000 paid for 1 unit(s) at 5 % vol → 2484
#guard (R4.exciseCharges [{ good := .beer, name := "Excise tax (beer made from malt, 2203.0000)", advBp := 4000, vatBp := 1500, minNum := 11000, minDen := 1000, statute := "Proc. 1287/2023 First Schedule 2203.0000: 40 % or 11 Birr per litre, whichever is higher" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [2484]
-- Proc. 1287/2023 First Schedule 2204.10-2205.90: 40 %: 10000 paid for 1 unit(s) at 12 % vol → 2484
#guard (R4.exciseCharges [{ good := .wine, name := "Excise tax (wine, local content below 75 %)", advBp := 4000, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule 2204.10-2205.90: 40 %" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [2484]
-- Proc. 1287/2023 First Schedule 2208.20-2208.70: 80 %: 10000 paid for 1 unit(s) at 40 % vol → 3864
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise tax (spirits, 2208.20-2208.70)", advBp := 8000, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule 2208.20-2208.70: 80 %" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [3864]
-- Proc. 1287/2023 First Schedule 2202.1000: 25 %: 10000 paid for 1 unit(s) at 0 % vol → 1739
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Excise tax (sweetened waters, 2202.1000)", advBp := 2500, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule 2202.1000: 25 %" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1739]
-- Proc. 1287/2023 First Schedule 2402.2000: 30 % + 8 Birr per pack of 20 (0.40 Birr per cigarette): 10000 paid for 1 unit(s) at 0 % vol → 2006
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise tax (cigarettes, 2402.2000)", perUnitNum := 400, perUnitDen := 1000, advBp := 3000, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule 2402.2000: 30 % + 8 Birr per pack of 20 (0.40 Birr per cigarette)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [2006]
-- Proc. 1287/2023 First Schedule chapter 27: kerosene, benzene and diesel oils 15 %: 10000 paid for 1 unit(s) at 0 % vol → 1134
#guard (R4.exciseCharges [{ good := .petrol, name := "Excise tax (benzene)", advBp := 1500, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule chapter 27: kerosene, benzene and diesel oils 15 %" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1134]
-- Proc. 1287/2023 First Schedule chapter 27: kerosene, benzene and diesel oils 15 %: 10000 paid for 1 unit(s) at 0 % vol → 1134
#guard (R4.exciseCharges [{ good := .diesel, name := "Excise tax (diesel oils)", advBp := 1500, vatBp := 1500, statute := "Proc. 1287/2023 First Schedule chapter 27: kerosene, benzene and diesel oils 15 %" }] [{ good := .diesel, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1134]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["VAT Proclamation 1341/2024: exempt supplies (financial services, residential rent, education, medical services …) not resolved in the bilingual extraction: every line at 15 %", "the excise base is the cost of production (local goods) or the customs value plus duties (imports), approximated by the region convention (value before excise and VAT)", "beer from Ethiopian barley (35 % / 9 Birr) and with at least 75 % local content (30 % / 8 Birr), and wine with at least 75 % local content (30 %), are not separated", "no amendment after Proclamation 1287/2023 is in the Ministry of Revenues' archived document list (flagged); whether fuel sold at regulated prices bears VAT is not established"]

end EtGlobal
