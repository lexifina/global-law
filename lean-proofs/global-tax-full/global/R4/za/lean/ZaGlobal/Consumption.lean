import R4Common
import R4Common.K21
import R4Common.Dated

/-!
# South Africa 2025: VAT (5111) and excises (5121) (generated from `R4/specs/za.json` by `R4/tools/gen_country.py`)

Sources: SARS web pages saved locally (`cmp20/world/B02-g20/za/law/sars_intdiv.html`); the acts held by Global law are not reached (GL) in this pass. Amending acts fetched from sars.gov.za (redirects to wp-content/uploads/Legal/AmendActs/*.pdf), saved in `cmp20/global/R4/fetch/za8/` with SHA256SUMS and layout text.

Act 21 of 2018 s. 9 (1) (a): section 7 (1) of the VAT Act is amended so that the tax is "calculated at the rate of [14] 15 per cent on the value of the supply concerned or the importation". Act 3 of 2026 s. 13 (1): "Despite (a) section 7(4) of the Value-Added Tax Act, 1991; and (b) the announcement by the Minister of Finance on 12 March 2025 in the national annual budget ... the alteration of the VAT rate specified in section 7 of that Act, 1991, does not come into effect"; (2) deemed in effect from 1 May 2025. So 15 % applied throughout 2025.

2024/2025 rates: SA Act 45 of 2024 s. 1 (2) ('deemed to have come into operation on 21 February 2024') and Part I: '104.10.20 2203.00.90 Other R135.89/li aa', '104.15.03 2204.21.41 ... R5.57/li', '104.23.05 2208.30.10 ... R274.39/li aa', '104.30.07 2402.20.90 Other R10.89/10 cigarettes'; 2025/2026 rates: SA Act 3 of 2026 s. 4 (2) (12 March 2025) and Sch. II: R145.07/li aa, R5.95/li, R292.91/li aa, R11.40/10 (R4/fetch/za8/act-45-of-2024.txt, act-3-of-2026.txt). Each rate applies on its window; an undated line bears each on its share of the year (70/365 and 295/365).
-/

namespace ZaGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1500, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Value-Added Tax Act 89 of 1991 s. 7 (1) as amended by the Rates and Monetary Amounts and Amendment of Revenue Laws Act 21 of 2018 s. 9 (15 % from 1 April 2018); the 2025 budget increase did not take effect (Act 3 of 2026 s. 13, deemed from 1 May 2025)"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise duty beer (malt)", perUnitNum := 135890, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R135.89 per litre of absolute alcohol" },
    { good := .beer, name := "Excise duty beer (malt)", perUnitNum := 145070, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R145.07 per litre of absolute alcohol" },
    { good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5570, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R5.57 per litre" },
    { good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5950, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R5.95 per litre" },
    { good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 274390, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R274.39 per litre of absolute alcohol" },
    { good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 292910, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R292.91 per litre of absolute alcohol" },
    { good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1089, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R10.89 per 10 cigarettes" },
    { good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1140, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R11.40 per 10 cigarettes" } ]
def exciseWin : List (String × String) := [("", "2025-03-12"), ("2025-03-12", ""), ("", "2025-03-12"), ("2025-03-12", ""), ("", "2025-03-12"), ("2025-03-12", ""), ("", "2025-03-12"), ("2025-03-12", "")]
/-- the rates with their date windows (kernel 2.1 `ExciseRule.validFrom/validTo`; an undated line is taken for the window's share of the year) -/
def accisesD : List ExciseRule := (accises.zip exciseWin).map fun (e, w) => { e.toRule with validFrom := w.1, validTo := w.2 }
def excise : Family := exciseRuleFamily "Specific excise duties (Schedule 1 Part 2A)" accisesD
def excT (s : String) : CanonGlobal :=
  match Lean.Json.parse s with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R135.89 per litre of absolute alcohol: dated 2025-01-01 (inside 1 Jan-2025-03-12): 6
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-01-01\"}]}")).map (·.due) == [6]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 475
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":365000,\"quantity\":365000,\"abvBp\":500}]}")).map (·.due) == [475]
#guard (exciseRuleCharges [accisesD.getD 0 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R145.07 per litre of absolute alcohol: dated 2025-03-12 (inside 2025-03-12-31 Dec): 7
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-03-12\"}]}")).map (·.due) == [7]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 2139
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":365000,\"quantity\":365000,\"abvBp\":500}]}")).map (·.due) == [2139]
#guard (exciseRuleCharges [accisesD.getD 1 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"beer\",\"amount\":10000,\"quantity\":1000,\"abvBp\":500,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R5.57 per litre: dated 2025-01-01 (inside 1 Jan-2025-03-12): 5
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-01-01\"}]}")).map (·.due) == [5]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 389
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":365000,\"quantity\":365000,\"abvBp\":1200}]}")).map (·.due) == [389]
#guard (exciseRuleCharges [accisesD.getD 2 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R5.95 per litre: dated 2025-03-12 (inside 2025-03-12-31 Dec): 5
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-03-12\"}]}")).map (·.due) == [5]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 1755
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":365000,\"quantity\":365000,\"abvBp\":1200}]}")).map (·.due) == [1755]
#guard (exciseRuleCharges [accisesD.getD 3 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"wine\",\"amount\":10000,\"quantity\":1000,\"abvBp\":1200,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R274.39 per litre of absolute alcohol: dated 2025-01-01 (inside 1 Jan-2025-03-12): 109
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-01-01\"}]}")).map (·.due) == [109]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 7682
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":365000,\"quantity\":365000,\"abvBp\":4000}]}")).map (·.due) == [7682]
#guard (exciseRuleCharges [accisesD.getD 4 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R292.91 per litre of absolute alcohol: dated 2025-03-12 (inside 2025-03-12-31 Dec): 117
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-03-12\"}]}")).map (·.due) == [117]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 34563
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":365000,\"quantity\":365000,\"abvBp\":4000}]}")).map (·.due) == [34563]
#guard (exciseRuleCharges [accisesD.getD 5 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"spirits\",\"amount\":10000,\"quantity\":1000,\"abvBp\":4000,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R10.89 per 10 cigarettes: dated 2025-01-01 (inside 1 Jan-2025-03-12): 1
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == [1]
-- undated 365 000 paid for 365 units: 70/365 of the year -> 70000 for 70 units -> 76
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [76]
#guard (exciseRuleCharges [accisesD.getD 6 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-03-12\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R11.40 per 10 cigarettes: dated 2025-03-12 (inside 2025-03-12-31 Dec): 1
#guard (exciseRuleCharges [accisesD.getD 7 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-03-12\"}]}")).map (·.due) == [1]
-- undated 365 000 paid for 365 units: 295/365 of the year -> 295000 for 295 units -> 336
#guard (exciseRuleCharges [accisesD.getD 7 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":365000,\"quantity\":365000,\"abvBp\":0}]}")).map (·.due) == [336]
#guard (exciseRuleCharges [accisesD.getD 7 default] (excT "{\"id\":\"t\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"cigarettes\",\"amount\":10000,\"quantity\":1000,\"abvBp\":0,\"date\":\"2025-01-01\"}]}")).map (·.due) == []
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R135.89 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 5 % vol → 6
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty beer (malt)", perUnitNum := 135890, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R135.89 per litre of absolute alcohol" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [6]
-- Sch. 1 Part 2A 104.10.20 (2203.00.90) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R145.07 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 5 % vol → 7
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty beer (malt)", perUnitNum := 145070, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.10.20 (2203.00.90) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R145.07 per litre of absolute alcohol" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [7]
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R5.57 per litre: 10000 paid for 1 unit(s) at 12 % vol → 5
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5570, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R5.57 per litre" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [5]
-- Sch. 1 Part 2A 104.15.03 (2204.21.41) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R5.95 per litre: 10000 paid for 1 unit(s) at 12 % vol → 5
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty unfortified wine", perUnitNum := 5950, perUnitDen := 1000, vatBp := 1500, minAbvBp := 449, maxAbvBp := 1650, statute := "Sch. 1 Part 2A 104.15.03 (2204.21.41) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R5.95 per litre" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [5]
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R274.39 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 40 % vol → 109
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 274390, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R274.39 per litre of absolute alcohol" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [109]
-- Sch. 1 Part 2A 104.23.05 (2208.30.10) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R292.91 per litre of absolute alcohol: 10000 paid for 1 unit(s) at 40 % vol → 117
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise duty spirits (whisky)", perUnitNum := 292910, perUnitDen := 1000, vatBp := 1500, onPureAlcohol := true, statute := "Sch. 1 Part 2A 104.23.05 (2208.30.10) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R292.91 per litre of absolute alcohol" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [117]
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R10.89 per 10 cigarettes: 10000 paid for 1 unit(s) at 0 % vol → 1
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1089, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (Act 45 of 2024 Part I (deemed in operation from 21 February 2024)): R10.89 per 10 cigarettes" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1]
-- Sch. 1 Part 2A 104.30.07 (2402.20.90) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R11.40 per 10 cigarettes: 10000 paid for 1 unit(s) at 0 % vol → 1
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise duty cigarettes", perUnitNum := 1140, perUnitDen := 1000, vatBp := 1500, statute := "Sch. 1 Part 2A 104.30.07 (2402.20.90) (Act 3 of 2026 Sch. II (deemed in operation from 12 March 2025)): R11.40 per 10 cigarettes" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["VAT Act s. 11 zero-rating (basic foodstuffs, Schedule 2 Part B) and s. 12 exemptions (financial services, residential rent, passenger transport, education) are not applied: the consolidated VAT Act was not read", "fuel levy (Part 5A), ad valorem duties (Part 2B) and the health promotion levy on sugary beverages are not modelled", "2024/2025 rates (Act 45 of 2024) to 11 March 2025 and 2025/2026 rates (Act 3 of 2026) from 12 March 2025, by the line's date"]

end ZaGlobal
