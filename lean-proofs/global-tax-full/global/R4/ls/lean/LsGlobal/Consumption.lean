import R4Common
import R4Common.K21
import R4Common.Dated

/-!
# Lesotho 2025: VAT (5111) and excises (5121) (generated from `R4/specs/ls.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: the Income Tax Act 1993 held is a 2012 consolidation; no 2025 text for any heading. RSL pages and guides fetched 2026-11-21 (`cmp20/global/R4/fetch/ls8/`, SHA256SUMS): withholding tax guide, VAT Act 2001, VAT (Amendment) Regulations LN 18 of 2020 and LN 30 of 2021 (OCR). Pass 9 (VAT): the Revenue Services Lesotho uploads of the VAT (Amendment) Regulations LN 27 of 2018 and LN 34 of 2019 (www.rsl.org.ls/sites/default/files/2018-04/…, 2019-04/…, via Wayback; scanned gazettes, OCR eng) and RSL's 'VAT Rates Changes 2018' notice, in `R4/fetch/ls9/` (SHA256SUMS); LN 18 of 2020 and LN 30 of 2021 and the VAT Act 2001 already held in `R4/fetch/ls8/`. The RSL document list on Wayback shows no later VAT regulation (2022-2024).

LN 27 of 2018 reg. 2: "Regulation 6 of the Value Added Tax Regulations, 2003, is amended by - (a) deleting the words 'and telephone calls, 5%' in paragraph (b) and substituting '8%'; (b) deleting '14%' in paragraph (c) and substituting '15%', and (c) adding after paragraph (c) the following - '(d) In case of supplies of telecommunications, 9%'." LN 34 of 2019: "deleting '9%' in paragraph (d) and substituting '12%'"; LN 18 of 2020: "(a) '8%' in paragraph (b) and substituting '9%'; and (b) '12%' in paragraph (d) and substituting '15%'"; LN 30 of 2021 (from 1 April 2021): "Regulation 6(1)(b) ... is amended by deleting '9%' and substituting '10%'". VAT Act 2001 s. 6 (2): "the following supplies are exempt supplies – (a) a supply of public postal, transportation, medical or dental, financial, insurance, or education services; (b) a supply of unimproved land; (c) a supply by way of lease or letting of immovable property where – (i) the tenant is a manufacturer ... (d) a supply of water". RSL notice 'VAT Rates Change, Effective Date: 1st April 2018': "The standard rate of VAT will change from 14% to 15%, Electricity rate increases from 5% to 8%".

2024/2025 rates: SA Act 45 of 2024 s. 1 (2) ('deemed to have come into operation on 21 February 2024') and Part I: '104.10.20 2203.00.90 Other R135.89/li aa', '104.15.03 2204.21.41 ... R5.57/li', '104.23.05 2208.30.10 ... R274.39/li aa', '104.30.07 2402.20.90 Other R10.89/10 cigarettes'; 2025/2026 rates: SA Act 3 of 2026 s. 4 (2) (12 March 2025) and Sch. II: R145.07/li aa, R5.95/li, R292.91/li aa, R11.40/10 (R4/fetch/za8/act-45-of-2024.txt, act-3-of-2026.txt). Lesotho's own Customs and Excise Act 1982 and its notices are not held: the SACU common rates and SA's effective dates are applied (grade B).
-/

namespace LsGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value added tax", standard := 1500, reduced := 1000, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .electricity => .reduced
      | .transport | .health | .financial | .insurance | .education | .water => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "VAT Regulations 2003 reg. 6 (1) (c) as amended by LN 27 of 2018 reg. 2 (b) (14 % → 15 % from 1 April 2018); reg. 6 (1) (b) electricity 10 % (LN 27/2018, LN 18/2020, LN 30/2021); reg. 6 (1) (d) telecommunications 15 % (LN 27/2018, LN 34/2019, LN 18/2020); VAT Act 2001 s. 6 (2) exempt supplies"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500
#guard vatX.embedded { good := .electricity, amount := 11000 } == 1000
#guard vatX.embedded { good := .transport, amount := 10000 } == 0
#guard vatX.embedded { good := .health, amount := 10000 } == 0
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise duty beer (malt)", perUnitNum := 135890, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M135.89 per litre of absolute alcohol" },
    { good := .beer, name := "Excise duty beer (malt)", perUnitNum := 145070, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M145.07 per litre of absolute alcohol" },
    { good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5570, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M5.57 per litre" },
    { good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5950, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M5.95 per litre" },
    { good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 274390, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M274.39 per litre of absolute alcohol" },
    { good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 292910, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M292.91 per litre of absolute alcohol" },
    { good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1089, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M10.89 per 10 cigarettes" },
    { good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1140, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M11.40 per 10 cigarettes" } ]
def exciseWin : List (String × String) := [("", "2025-03-12"), ("2025-03-12", ""), ("", "2025-03-12"), ("2025-03-12", ""), ("", "2025-03-12"), ("2025-03-12", ""), ("", "2025-03-12"), ("2025-03-12", "")]
/-- the rates with their date windows (kernel 2.1 `ExciseRule.validFrom/validTo`; an undated line is taken for the window's share of the year) -/
def accisesD : List ExciseRule := (accises.zip exciseWin).map fun (e, w) => { e.toRule with validFrom := w.1, validTo := w.2 }
def excise : Family := exciseRuleFamily "Excise duties (SACU common excise tariff, Schedule 1 Part 2A)" accisesD
def excT (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M135.89 per litre of absolute alcohol: dated 2025-01-01 (inside 1 Jan-2025-03-12): 6
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-01-01\"}]}")).map (·.due) == [6]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 475
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":365000,\"quantity\":365000,\"abvBp\":500}]}")).map (·.due) == [475]
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M145.07 per litre of absolute alcohol: dated 2025-03-12 (inside 2025-03-12-31 Dec): 7
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-03-12\"}]}")).map (·.due) == [7]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 2139
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":365000,\"quantity\":365000,\"abvBp\":500}]}")).map (·.due) == [2139]
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M5.57 per litre: dated 2025-01-01 (inside 1 Jan-2025-03-12): 5
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-01-01\"}]}")).map (·.due) == [5]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 389
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":365000,\"quantity\":365000,\"abvBp\":1200}]}")).map (·.due) == [389]
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M5.95 per litre: dated 2025-03-12 (inside 2025-03-12-31 Dec): 5
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-03-12\"}]}")).map (·.due) == [5]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 1755
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":365000,\"quantity\":365000,\"abvBp\":1200}]}")).map (·.due) == [1755]
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M274.39 per litre of absolute alcohol: dated 2025-01-01 (inside 1 Jan-2025-03-12): 109
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-01-01\"}]}")).map (·.due) == [109]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 7682
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":365000,\"quantity\":365000,\"abvBp\":4000}]}")).map (·.due) == [7682]
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M292.91 per litre of absolute alcohol: dated 2025-03-12 (inside 2025-03-12-31 Dec): 117
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-03-12\"}]}")).map (·.due) == [117]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 34563
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":365000,\"quantity\":365000,\"abvBp\":4000}]}")).map (·.due) == [34563]
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M10.89 per 10 cigarettes: dated 2025-01-01 (inside 1 Jan-2025-03-12): 1
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == [1]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 76
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [76]
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M11.40 per 10 cigarettes: dated 2025-03-12 (inside 2025-03-12-31 Dec): 1
#guard (exciseRuleCharges [accisesD.getD 7 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-03-12\"}]}")).map (·.due) == [1]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 336
#guard (exciseRuleCharges [accisesD.getD 7 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [336]
#guard (exciseRuleCharges [accisesD.getD 7 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M135.89 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 5 % vol → 6
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty beer (malt)", perUnitNum := 135890, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M135.89 per litre of absolute alcohol" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [6]
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M145.07 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 5 % vol → 7
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty beer (malt)", perUnitNum := 145070, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M145.07 per litre of absolute alcohol" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [7]
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M5.57 per litre: 10000 paid for 1 unit(s) at 12 % vol → 5
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5570, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M5.57 per litre" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [5]
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M5.95 per litre: 10000 paid for 1 unit(s) at 12 % vol → 5
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5950, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M5.95 per litre" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [5]
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M274.39 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 40 % vol → 109
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 274390, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M274.39 per litre of absolute alcohol" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [109]
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M292.91 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 40 % vol → 117
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 292910, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M292.91 per litre of absolute alcohol" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [117]
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M10.89 per 10 cigarettes: 10000 paid for 1 unit(s) at 0 % vol → 1
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1089, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): M10.89 per 10 cigarettes" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1]
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M11.40 per 10 cigarettes: 10000 paid for 1 unit(s) at 0 % vol → 1
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1140, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (SACU Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): M11.40 per 10 cigarettes" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["reg. 6 (1) (b) is the electricity rate (RSL's 2018 notice: 'Electricity rate increases from 5% to 8%'; LN 27 removed 'and telephone calls' from it); the original text of reg. 6 (LN 95 of 2003) was not read: the paragraph contents are taken from the amending notices and RSL's notice", "transportation is exempt only for fare-paying passengers by road; zero-rated supplies (Schedule IV, e.g. basic foods) are not separated from the processed-food basket line", "grade B: Lesotho's Customs and Excise Act 1982 and its notices adopting the 2024/2025 and 2025/2026 SACU rates are not held; the common rates of SACU Agreement art. 21 (1) and SA's effective dates are applied", "fuel levy and ad valorem excise are not modelled"]

end LsGlobal
