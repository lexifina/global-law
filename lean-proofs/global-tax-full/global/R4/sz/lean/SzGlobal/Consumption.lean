import R4Common
import R4Common.K21
import R4Common.Dated

/-!
# Eswatini 2025: VAT (5111) and excises (5121) (generated from `R4/specs/sz.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: the Income Tax Order 1975 extraction shows only individual tables; the company rate and the VAT Act 2011 text were not located. Fetched from ers.org.sz (`cmp20/global/R4/fetch/sz8/`, SHA256SUMS): VAT Act 2011, VAT Regulations, VAT (Rates) (Amendment) Regulations 2018 (OCR), VAT (Amendment) Act 2022 (OCR), LN 130 of 2025 (OCR), ERS pages 'Rates and thresholds', 'Withholding', 'VAT'. Pass 9 (excise): the Eswatini Revenue Service's Excise page (ers.org.sz/CustomExcise/Excisepage, saved in `R4/fetch/sz8/CustomExcise_Excisepage.html`) states that excise is charged at the rates of the SACU tariff schedule and links to SARS's 'Schedules to the Customs and Excise Act'; the 2025/2026 SACU rates are those read for ZA (Act 3 of 2026 Sch. II, `R4/fetch/za8/`).

VAT Act 2011 s. 24 (3): "Subject to subsection (4), the rate of tax shall be as specified in the VAT Regulations"; (4): zero-rated supplies are those of the Second Schedule. LN 112 of 2018 reg. 2: "Legal Notice No. 52 of 2012 is amended in regulation 3 by deleting sub-regulation (1) and replacing it with ... (1) The rate of Value Added Tax shall be fifteen percent (15%)"; in force 1 August 2018. ERS 'VAT' page (2026): standard rate 15 % on most goods and services. First Schedule 1: exempt "(b) the supply of financial services; (c) the supply of insurance services; ... (f) the supply of education services; (g) the supply of medical, dental, and nursing services; ... (m) the supply of passenger transportation services, other than services ...; (n) the supply of tap water and sewage"; Second Schedule 1 (p): zero-rated "the supply of prescription drugs and medicines". LN 130 of 2025 (17 Dec 2025) restates tap water as exempt (Part B clause 1(1)(l)).

ERS Excise Duties page (facts restated): excise falls on alcoholic drinks, tobacco, road fuels, cars, TVs and refrigerators, collected on import into SACU or on local manufacture as in the other SACU states, at the rates of the SACU tariff schedule, which changes from time to time; alcohol and cigarettes bear specific duties. The page links the SARS 'Schedules to the Customs and Excise Act'. SACU 2025/2026 rates (SA Act 3 of 2026 Sch. II, deemed from 12 March 2025): "104.10.20 2203.00.90 Other R145.07/li aa"; "104.15.03 2204.21.41 ... R5.95/li"; "104.23.05 2208.30.10 ... R292.91/li aa"; "104.30.07 2402.20.90 ... R11.40/10". The lilangeni is at par with the rand. 2024/2025 rates: SA Act 45 of 2024 s. 1 (2) ('deemed to have come into operation on 21 February 2024') and Part I: '104.10.20 2203.00.90 Other R135.89/li aa', '104.15.03 2204.21.41 ... R5.57/li', '104.23.05 2208.30.10 ... R274.39/li aa', '104.30.07 2402.20.90 Other R10.89/10 cigarettes'; 2025/2026 rates: SA Act 3 of 2026 s. 4 (2) (12 March 2025) and Sch. II: R145.07/li aa, R5.95/li, R292.91/li aa, R11.40/10 (R4/fetch/za8/act-45-of-2024.txt, act-3-of-2026.txt).
-/

namespace SzGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1500, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .financial | .insurance | .education | .health | .transport | .water => .exempt
      | .medicines => .zero
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Value Added Tax Act 2011 s. 24 (3) (rate set by the VAT Regulations); VAT (Rates) Regulations (LN 52 of 2012) reg. 3 (1) as replaced by the VAT (Rates) (Amendment) Regulations 2018 (LN 112 of 2018, from 1 August 2018): 15 %; First Schedule (exempt), Second Schedule (zero-rated)"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500
#guard vatX.embedded { good := .financial, amount := 10000 } == 0
#guard vatX.embedded { good := .insurance, amount := 10000 } == 0
#guard vatX.embedded { good := .education, amount := 10000 } == 0
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise duty beer (malt)", perUnitNum := 135890, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E135.89 per litre of absolute alcohol" },
    { good := .beer, name := "Excise duty beer (malt)", perUnitNum := 145070, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E145.07 per litre of absolute alcohol" },
    { good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5570, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E5.57 per litre" },
    { good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5950, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E5.95 per litre" },
    { good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 274390, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E274.39 per litre of absolute alcohol" },
    { good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 292910, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E292.91 per litre of absolute alcohol" },
    { good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1089, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E10.89 per 10 cigarettes" },
    { good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1140, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E11.40 per 10 cigarettes" } ]
def exciseWin : List (String × String) := [("", "2025-03-12"), ("2025-03-12", ""), ("", "2025-03-12"), ("2025-03-12", ""), ("", "2025-03-12"), ("2025-03-12", ""), ("", "2025-03-12"), ("2025-03-12", "")]
/-- the rates with their date windows (kernel 2.1 `ExciseRule.validFrom/validTo`; an undated line is taken for the window's share of the year) -/
def accisesD : List ExciseRule := (accises.zip exciseWin).map fun (e, w) => { e.toRule with validFrom := w.1, validTo := w.2 }
def excise : Family := exciseRuleFamily "Excise duties (SACU common excise tariff, Schedule No. 1 Part 2A)" accisesD
def excT (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E135.89 per litre of absolute alcohol: dated 2025-01-01 (inside 1 Jan-2025-03-12): 6
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-01-01\"}]}")).map (·.due) == [6]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 475
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":365000,\"quantity\":365000,\"abvBp\":500}]}")).map (·.due) == [475]
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E145.07 per litre of absolute alcohol: dated 2025-03-12 (inside 2025-03-12-31 Dec): 7
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-03-12\"}]}")).map (·.due) == [7]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 2139
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":365000,\"quantity\":365000,\"abvBp\":500}]}")).map (·.due) == [2139]
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E5.57 per litre: dated 2025-01-01 (inside 1 Jan-2025-03-12): 5
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-01-01\"}]}")).map (·.due) == [5]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 389
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":365000,\"quantity\":365000,\"abvBp\":1200}]}")).map (·.due) == [389]
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E5.95 per litre: dated 2025-03-12 (inside 2025-03-12-31 Dec): 5
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-03-12\"}]}")).map (·.due) == [5]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 1755
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":365000,\"quantity\":365000,\"abvBp\":1200}]}")).map (·.due) == [1755]
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E274.39 per litre of absolute alcohol: dated 2025-01-01 (inside 1 Jan-2025-03-12): 109
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-01-01\"}]}")).map (·.due) == [109]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 7682
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":365000,\"quantity\":365000,\"abvBp\":4000}]}")).map (·.due) == [7682]
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E292.91 per litre of absolute alcohol: dated 2025-03-12 (inside 2025-03-12-31 Dec): 117
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-03-12\"}]}")).map (·.due) == [117]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 34563
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":365000,\"quantity\":365000,\"abvBp\":4000}]}")).map (·.due) == [34563]
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E10.89 per 10 cigarettes: dated 2025-01-01 (inside 1 Jan-2025-03-12): 1
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == [1]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 76
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [76]
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E11.40 per 10 cigarettes: dated 2025-03-12 (inside 2025-03-12-31 Dec): 1
#guard (exciseRuleCharges [accisesD.getD 7 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-03-12\"}]}")).map (·.due) == [1]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 336
#guard (exciseRuleCharges [accisesD.getD 7 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [336]
#guard (exciseRuleCharges [accisesD.getD 7 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E135.89 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 5 % vol → 6
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty beer (malt)", perUnitNum := 135890, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E135.89 per litre of absolute alcohol" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [6]
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E145.07 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 5 % vol → 7
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty beer (malt)", perUnitNum := 145070, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E145.07 per litre of absolute alcohol" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [7]
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E5.57 per litre: 10000 paid for 1 unit(s) at 12 % vol → 5
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5570, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E5.57 per litre" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [5]
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E5.95 per litre: 10000 paid for 1 unit(s) at 12 % vol → 5
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5950, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E5.95 per litre" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [5]
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E274.39 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 40 % vol → 109
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 274390, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E274.39 per litre of absolute alcohol" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [109]
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E292.91 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 40 % vol → 117
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 292910, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E292.91 per litre of absolute alcohol" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [117]
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E10.89 per 10 cigarettes: 10000 paid for 1 unit(s) at 0 % vol → 1
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1089, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): E10.89 per 10 cigarettes" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1]
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E11.40 per 10 cigarettes: 10000 paid for 1 unit(s) at 0 % vol → 1
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1140, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): E11.40 per 10 cigarettes" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["the schedules were restructured into Parts A (services) and B (goods) by the VAT (Amendment) Act 2022 and LN 270 of 2022 (the schedule notice is not held: the ERS link answers 404); the 2011 schedule items are applied", "Second Schedule basic foods (maize meal, maize, beans, milk, brown bread, fresh fruit and vegetables, eggs, vegetable oil) are zero-rated: the basket food line is processed food (region convention), so not applied", "residential lettings exempt (First Schedule 1 (e)) not separable", "grade B: Eswatini's own legal notice adopting the 2025/2026 SACU rates was not read; the ERS guide points to the SACU schedule (SA text)", "2024/2025 SACU rates to 11 March 2025 and 2025/2026 rates from 12 March 2025, by the line's date (the dates of SA's acts: Eswatini's adopting notices not read, flag); fuel levies, ad valorem duties (Part 2B) and the Alcohol and Tobacco Levy Act levy are not modelled"]

end SzGlobal
