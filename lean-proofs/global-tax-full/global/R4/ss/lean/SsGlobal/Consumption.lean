import R4Common
import R4Common.Dated
import R4Common.K21

/-!
# South Sudan 2025: VAT (5111) and excises (5121) (generated from `R4/specs/ss.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: Financial Acts 2023/24 and 2024/25 are held but not mapped in this pass. Second pass: Financial Act 2024/2025 (FY July 2024 - June 2025); the 2025/26 Act not held. Pass 10 (sales tax/excise): Financial Act 2024/2025 OCR (`world/B10-anglophone-africa/ss/law/fa2425_ocr.txt`) chapters 5-8 and Schedule 1 (A) items 6-7; Taxation Amendment Act 2016 OCR (`taxact2016_ocr.txt`, assented 20 December 2016) Schedules 4-6; Financial Act 2023/2024 (`financial_act_2023_2024.txt`) Schedule 1 item 2 for comparison.

Financial Act 2024/2025 Schedule 1 (A) item 6 "PIT/BPT, surtax and Sales Tax Rates: Replace Schedule 1 (1,2&4) of the Taxation Act, 2009 with the following: ... 2 Sales Tax: Imported goods 18%; Locally manufactured goods 18%; Hotel, bar and restaurant services 18%; Telecommunication services 18%; Commission, fee or charge levied for financial services, cash/money transfer or travel & tour agency 18%". The Act's chapters 5-7 say "For that year the rate is charged at twenty percent (20%) as per Taxation Act, 2009 (amended in 2016)", but the Taxation Amendment Act 2016 they cite substitutes 18 % in Schedules 4, 5 and 6 ("Sales Tax on Domestically-produced goods ... 18%"; "Sales Tax on Hotel, Restaurant, and Bar services ... 18%"; "Sales Tax on Imported Goods ... 18 %"), and the Financial Act 2023/2024 schedule also prints 18 % for each line.

Financial Act 2024/2025 chapter 8 (2): "The value, on which the tax is assessed, shall be the greater of the manufacturer selling price or fair market value of goods produced in South Sudan or, in case of imported goods the customs value"; (4) "For that year the rates are charged as outlined in Schedule 1". Schedule 1 (A) item 7 "EXCISE DUTY RATE: Replace Schedule 1 (3) of the Taxation Act, 2009 with the following" (HS / description / current / FY-2024/25 approved): "22.02 Waters ... containing added sugar or other sweetening matter or flavoured, and other non-alcoholic beverages 5% 5%; 22.03 Beer made from malt 50% 50%; 22.04 Wine of fresh grapes ... 50%; 22.08 ... spirits, liqueurs and other spirituous beverages 100% 100%; 24.02 Cigars, cheroots, cigarillos and cigarettes ... 100% 100%; 27.10 Petroleum oils ... 5% 5%". Sales tax is assessed on the value including excise (chapters 5 and 7: "manufacturer selling price inclusive of excise duties"; "customs value, plus excise duty and customs duty").
-/

namespace SsGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Sales tax", standard := 1800, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .rent | .health | .medicines | .education | .transport | .insurance => .exempt
      | _ => .standard }

def vat : Family := R4.vatKnownToFamily vatX "Financial Act 2024/2025 Schedule 1 (A) item 6 (replacing Schedule 1 (1, 2 & 4) of the Taxation Act 2009): sales tax 18 % on imported goods, locally manufactured goods, hotel, bar and restaurant services, telecommunication services and financial-service / money-transfer / travel-agency charges; Taxation Amendment Act 2016 Schedules 4-6 (18 %) [text version: Financial Act 2024/2025 as enacted (FY 1 July 2024-30 June 2025), applied to 30 June 2025 only; the Financial Act 2025/2026 (FY 1 July 2025-30 June 2026) was not found: NRA uploads (cms.nra.gov.ss) and MoFEP (mofep-grss.org) document pages on the Internet Archive (CDX, 21 Nov 2026) hold the Acts for 2014/15-2024/25 only]" "2025-07-01"

-- the standard rate as printed: 18 % inside a tax-inclusive 11800
#guard vatX.embedded { good := .other, amount := 11800 } == 1800
#guard vatX.embedded { good := .rent, amount := 10000 } == 0
#guard vatX.embedded { good := .health, amount := 10000 } == 0
#guard vatX.embedded { good := .medicines, amount := 10000 } == 0
def excT (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
-- known to 2025-07-01: a line of 11800 dated 2025-06-30 bears 1800; one dated 2025-07-01 bears none (grade C); an undated 4307000 is charged for 181/365 of the year: 2135800 -> 325800
#guard ((vat.run [] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"other\",\"amount\":11800,\"date\":\"2025-06-30\"}]}") []).map (·.due)) == [1800]
#guard ((vat.run [] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"other\",\"amount\":11800,\"date\":\"2025-07-01\"}]}") []).map (·.due)) == [0]
#guard ((vat.run [] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"other\",\"amount\":4307000}]}") []).map (·.due)) == [325800]
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise duty (beer, HS 22.03)", advBp := 5000, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 22.03: 50 % (to 30 June 2025)" },
    { good := .wine, name := "Excise duty (wine, HS 22.04)", advBp := 5000, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 22.04: 50 % (to 30 June 2025)" },
    { good := .spirits, name := "Excise duty (spirits, HS 22.08)", advBp := 10000, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 22.08: 100 % (to 30 June 2025)" },
    { good := .cigarettes, name := "Excise duty (cigarettes, HS 24.02)", advBp := 10000, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 24.02: 100 % (to 30 June 2025)" },
    { good := .nonAlcoholic, name := "Excise duty (sweetened waters, HS 22.02)", advBp := 500, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 22.02: 5 % (to 30 June 2025)" },
    { good := .petrol, name := "Excise duty (petroleum oils, HS 27.10)", advBp := 500, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 27.10: 5 % (to 30 June 2025)" },
    { good := .diesel, name := "Excise duty (petroleum oils, HS 27.10)", advBp := 500, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 27.10: 5 % (to 30 June 2025)" } ]
def exciseWin : List (String × String) := [("", "2025-07-01"), ("", "2025-07-01"), ("", "2025-07-01"), ("", "2025-07-01"), ("", "2025-07-01"), ("", "2025-07-01"), ("", "2025-07-01")]
/-- the rates with their date windows (kernel 2.1 `ExciseRule.validFrom/validTo`; an undated line is taken for the window's share of the year) -/
def accisesD : List ExciseRule := (accises.zip exciseWin).map fun (e, w) => { e.toRule with validFrom := w.1, validTo := w.2 }
def excise : Family := exciseRuleFamily "Excise duty" accisesD
-- Schedule 1 (A) item 7, HS 22.03: 50 % (to 30 June 2025): dated 2025-01-01 (inside 1 Jan-2025-07-01): 2824
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-01-01\"}]}")).map (·.due) == [2824]
-- undated 365 000 paid for 365 units: 181/365 of the year -> 181000 for 181 units -> 51129
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":365000,\"quantity\":365000,\"abvBp\":500}]}")).map (·.due) == [51129]
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-07-01\"}]}")).map (·.due) == []
-- Schedule 1 (A) item 7, HS 22.04: 50 % (to 30 June 2025): dated 2025-01-01 (inside 1 Jan-2025-07-01): 2824
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-01-01\"}]}")).map (·.due) == [2824]
-- undated 365 000 paid for 365 units: 181/365 of the year -> 181000 for 181 units -> 51129
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":365000,\"quantity\":365000,\"abvBp\":1200}]}")).map (·.due) == [51129]
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-07-01\"}]}")).map (·.due) == []
-- Schedule 1 (A) item 7, HS 22.08: 100 % (to 30 June 2025): dated 2025-01-01 (inside 1 Jan-2025-07-01): 4237
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-01-01\"}]}")).map (·.due) == [4237]
-- undated 365 000 paid for 365 units: 181/365 of the year -> 181000 for 181 units -> 76694
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":365000,\"quantity\":365000,\"abvBp\":4000}]}")).map (·.due) == [76694]
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-07-01\"}]}")).map (·.due) == []
-- Schedule 1 (A) item 7, HS 24.02: 100 % (to 30 June 2025): dated 2025-01-01 (inside 1 Jan-2025-07-01): 4237
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == [4237]
-- undated 365 000 paid for 365 units: 181/365 of the year -> 181000 for 181 units -> 76694
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [76694]
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-07-01\"}]}")).map (·.due) == []
-- Schedule 1 (A) item 7, HS 22.02: 5 % (to 30 June 2025): dated 2025-01-01 (inside 1 Jan-2025-07-01): 403
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"nonAlcoholic\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == [403]
-- undated 365 000 paid for 365 units: 181/365 of the year -> 181000 for 181 units -> 7304
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"nonAlcoholic\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [7304]
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"nonAlcoholic\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-07-01\"}]}")).map (·.due) == []
-- Schedule 1 (A) item 7, HS 27.10: 5 % (to 30 June 2025): dated 2025-01-01 (inside 1 Jan-2025-07-01): 403
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"petrol\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == [403]
-- undated 365 000 paid for 365 units: 181/365 of the year -> 181000 for 181 units -> 7304
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"petrol\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [7304]
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"petrol\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-07-01\"}]}")).map (·.due) == []
-- Schedule 1 (A) item 7, HS 27.10: 5 % (to 30 June 2025): dated 2025-01-01 (inside 1 Jan-2025-07-01): 403
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"diesel\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == [403]
-- undated 365 000 paid for 365 units: 181/365 of the year -> 181000 for 181 units -> 7304
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"diesel\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [7304]
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"diesel\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-07-01\"}]}")).map (·.due) == []
-- Schedule 1 (A) item 7, HS 22.03: 50 % (to 30 June 2025): 10000 paid for 1 unit(s) at 5 % vol → 2824
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty (beer, HS 22.03)", advBp := 5000, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 22.03: 50 % (to 30 June 2025)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [2824]
-- Schedule 1 (A) item 7, HS 22.04: 50 % (to 30 June 2025): 10000 paid for 1 unit(s) at 12 % vol → 2824
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty (wine, HS 22.04)", advBp := 5000, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 22.04: 50 % (to 30 June 2025)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [2824]
-- Schedule 1 (A) item 7, HS 22.08: 100 % (to 30 June 2025): 10000 paid for 1 unit(s) at 40 % vol → 4237
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise duty (spirits, HS 22.08)", advBp := 10000, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 22.08: 100 % (to 30 June 2025)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [4237]
-- Schedule 1 (A) item 7, HS 24.02: 100 % (to 30 June 2025): 10000 paid for 1 unit(s) at 0 % vol → 4237
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise duty (cigarettes, HS 24.02)", advBp := 10000, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 24.02: 100 % (to 30 June 2025)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [4237]
-- Schedule 1 (A) item 7, HS 22.02: 5 % (to 30 June 2025): 10000 paid for 1 unit(s) at 0 % vol → 403
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Excise duty (sweetened waters, HS 22.02)", advBp := 500, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 22.02: 5 % (to 30 June 2025)" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [403]
-- Schedule 1 (A) item 7, HS 27.10: 5 % (to 30 June 2025): 10000 paid for 1 unit(s) at 0 % vol → 403
#guard (R4.exciseCharges [{ good := .petrol, name := "Excise duty (petroleum oils, HS 27.10)", advBp := 500, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 27.10: 5 % (to 30 June 2025)" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [403]
-- Schedule 1 (A) item 7, HS 27.10: 5 % (to 30 June 2025): 10000 paid for 1 unit(s) at 0 % vol → 403
#guard (R4.exciseCharges [{ good := .diesel, name := "Excise duty (petroleum oils, HS 27.10)", advBp := 500, vatBp := 1800, statute := "Schedule 1 (A) item 7, HS 27.10: 5 % (to 30 June 2025)" }] [{ good := .diesel, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [403]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["chapters 5-7 of the Act print 20 % 'as per Taxation Act 2009 (amended in 2016)', while the amending Act they cite and the replacing Schedule both say 18 %: the Schedule rate is used (conflict flagged)", "sales tax is not a credit-invoice VAT: it falls on imports, local manufactures and the listed services; services outside the list (rent, health, education, transport, insurance) are untaxed; electricity, water and recreation are treated as taxable goods (not established)", "twentieth pass (year in force): the FY 2024/25 rates are applied to 30 June 2025 only: basket lines dated from 1 July 2025 are not charged (listed, grade C), undated lines are charged on 181/365 of their amount, a company's supplies only with an entity date before 1 July 2025; the Financial Act 2025/2026 (FY 1 July 2025-30 June 2026) was not found: NRA uploads (cms.nra.gov.ss) and MoFEP (mofep-grss.org) document pages on the Internet Archive (CDX, 21 Nov 2026) hold the Acts for 2014/15-2024/25 only", "the non-alcoholic basket line is charged at the sweetened-waters rate (unsweetened waters 15 %, juices 50 % not separated)", "sales tax is assumed to apply on top of excise for fuel as for other goods", "twentieth pass (year in force): the FY 2024/25 rates hold to 30 June 2025 (the 'current' and 'approved' columns agree for every modelled line); lines dated from 1 July 2025 are not charged and an undated line is charged on 181/365 of it, the rest listed (grade C); the Financial Act 2025/2026 (FY 1 July 2025-30 June 2026) was not found: NRA uploads (cms.nra.gov.ss) and MoFEP (mofep-grss.org) document pages on the Internet Archive (CDX, 21 Nov 2026) hold the Acts for 2014/15-2024/25 only"] ++ R4.vatKnownToNotes "Sales tax" "2025-07-01" "the Financial Act 2025/2026 (from 1 July 2025) was not found" g ++ R4.exciseGapNotes "Excise duty" [.beer, .wine, .spirits, .cigarettes, .nonAlcoholic, .petrol, .diesel] "2025-07-01" "" "the Financial Act 2025/2026 (from 1 July 2025) was not found" g

end SsGlobal
