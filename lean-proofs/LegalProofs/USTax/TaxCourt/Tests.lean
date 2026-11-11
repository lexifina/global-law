import LegalProofs.USTax.TaxCourt.Case

/-!
# Tests: per-year spot checks against printed IRS tables, and two worked cases

The per-year EIC rows are from each year's Pub. 596 EIC Table (columns: no child, one, two, three or more — single,
head of household or qualifying surviving spouse; then married filing jointly). Every row of all nine tables (and
every row of the nine Tax Tables) was also compared by `tools/taxcourt/CheckTables.lean`; see the findings in `LegalProofs/USTax/TaxCourt.lean`.

The two cases are hypothetical, built on the patterns of the Pub. 596 and Pub. 590-B examples, with every figure worked
by hand from the printed tables (the working is in the comments); they are not court cases.
-/

namespace Legal.USTax.TaxCourt.Tests
open Legal.USTax.TaxCourt TaxCode.Individual

private def py (y : Nat) : Params := (params? y).getD default

/-- One printed EIC Table row: the eight columns at amount `x`. -/
def eicRow (y : Nat) (x : Int) : List Int :=
  [false, true].flatMap fun j => [0, 1, 2, 3].map fun k => eicTableAmount (py y) k j x

#guard eicRow 2016 5000 = [384, 1709, 2010, 2261, 384, 1709, 2010, 2261]
#guard eicRow 2016 12000 = [218, 3373, 4810, 5411, 506, 3373, 4810, 5411]
#guard eicRow 2016 20000 = [0, 3080, 5186, 5882, 31, 3373, 5572, 6269]
#guard eicRow 2016 30000 = [0, 1482, 3080, 3776, 0, 2368, 4248, 4945]
#guard eicRow 2017 5000 = [384, 1709, 2010, 2261, 384, 1709, 2010, 2261]
#guard eicRow 2017 12000 = [228, 3400, 4810, 5411, 510, 3400, 4810, 5411]
#guard eicRow 2017 20000 = [0, 3131, 5261, 5963, 44, 3400, 5616, 6318]
#guard eicRow 2017 30000 = [0, 1533, 3155, 3857, 0, 2426, 4332, 5034]
#guard eicRow 2018 5000 = [384, 1709, 2010, 2261, 384, 1709, 2010, 2261]
#guard eicRow 2018 12000 = [248, 3461, 4810, 5411, 519, 3461, 4810, 5411]
#guard eicRow 2018 20000 = [0, 3243, 5429, 6143, 71, 3461, 5716, 6431]
#guard eicRow 2018 30000 = [0, 1645, 3323, 4037, 0, 2554, 4521, 5235]
#guard eicRow 2019 5000 = [384, 1709, 2010, 2261, 384, 1709, 2010, 2261]
#guard eicRow 2019 12000 = [271, 3526, 4810, 5411, 529, 3526, 4810, 5411]
#guard eicRow 2019 20000 = [0, 3367, 5618, 6347, 103, 3526, 5828, 6557]
#guard eicRow 2019 30000 = [0, 1769, 3512, 4241, 0, 2694, 4732, 5460]
#guard eicRow 2020 5000 = [384, 1709, 2010, 2261, 384, 1709, 2010, 2261]
#guard eicRow 2020 12000 = [290, 3584, 4810, 5411, 538, 3584, 4810, 5411]
#guard eicRow 2020 20000 = [0, 3473, 5774, 6514, 129, 3584, 5920, 6660]
#guard eicRow 2020 30000 = [0, 1875, 3668, 4408, 0, 2816, 4908, 5648]
#guard eicRow 2021 5000 = [769, 1709, 2010, 2261, 769, 1709, 2010, 2261]
#guard eicRow 2021 12000 = [1439, 3618, 4810, 5411, 1502, 3618, 4810, 5411]
#guard eicRow 2021 20000 = [215, 3537, 5874, 6621, 1125, 3618, 5980, 6728]
#guard eicRow 2021 30000 = [0, 1939, 3768, 4515, 0, 2890, 5021, 5768]
#guard eicRow 2022 5000 = [384, 1709, 2010, 2261, 384, 1709, 2010, 2261]
#guard eicRow 2022 12000 = [341, 3733, 4810, 5411, 560, 3733, 4810, 5411]
#guard eicRow 2022 20000 = [0, 3733, 6164, 6935, 198, 3733, 6164, 6935]
#guard eicRow 2022 30000 = [0, 2152, 4080, 4851, 0, 3132, 5371, 6142]
#guard eicRow 2023 5000 = [384, 1709, 2010, 2261, 384, 1709, 2010, 2261]
#guard eicRow 2023 12000 = [430, 3995, 4810, 5411, 600, 3995, 4810, 5411]
#guard eicRow 2023 20000 = [0, 3995, 6604, 7430, 320, 3995, 6604, 7430]
#guard eicRow 2023 30000 = [0, 2642, 4821, 5647, 0, 3691, 6203, 7028]
#guard eicRow 2024 5000 = [384, 1709, 2010, 2261, 384, 1709, 2010, 2261]
#guard eicRow 2024 12000 = [502, 4089, 4810, 5411, 632, 4089, 4810, 5411]
#guard eicRow 2024 20000 = [0, 4213, 6960, 7830, 420, 4213, 6960, 7830]
#guard eicRow 2024 30000 = [0, 3046, 5422, 6292, 0, 4151, 6879, 7749]

/-! ## CTC spot check for 2020 (the other years are in CTC.lean) -/

-- 2020: three children, no tax, earned income $30,000, social security taxes $2,295, EIC $4,408 (2020 table,
-- $30,000–30,050): 15% × $27,500 = $4,125 exceeds SS taxes − EIC; capped at 3 × $1,400 = $4,200 → $4,125.
private def f2020 : CtcFacts :=
  { filing := .single, magi := 30000, taxLeft := 0, earnedIncome := 30000, ssTaxes := 2295, eic := 4408 }
#guard (ctcFor (py 2020) ⟨3, 0, 0⟩ f2020).refundable = 4125

/-! ## Worked case 1 (tax year 2019): head of household, EIC and CTC; a niece who does not qualify

A single mother, wages $21,000, filed as head of household claiming her son (8, lived with her all year) and her
niece (14, lived with her 150 days; the niece's mother claims her). She claimed the EIC and CTC for two children.
The court finds the niece is not her qualifying child (residence) and not a qualifying relative (a qualifying child of
another taxpayer).

As corrected (one child): AGI $21,000; HoH standard deduction $18,350; taxable income $2,650; Tax Table
2,650–2,675: $266. CTC $2,000: $266 nonrefundable; ACTC = min($1,400 cap, 15% × ($21,000 − $2,500) = $2,775,
$1,734 unused) = $1,400. EIC, one child, Table 21,000–21,050: $3,207. Net tax $266 − $266 − $3,207 − $1,400 =
−$4,607.

As filed (two children): CTC $4,000: $266 nonrefundable; ACTC = min(2 × $1,400, $2,775, $3,734) = $2,775. EIC, two
children: $5,408. Net tax −$8,183.

Deficiency $3,576 (−$4,607 − (−$8,183)). Understatement $3,576 is not over $5,000: no §6662 penalty. -/
def son : PersonFacts := { name := "son", age := 8, daysWithTaxpayer := 365, livedWithWholeYear := true }

def case1 : Case :=
  { citation := "Worked example 1 (hypothetical, after Pub. 596 (2019))"
    taxYear := 2019
    facts :=
      { filing := .hoh, taxpayerAge := 32, wages := 21000
        dependents :=
          [son, { name := "niece", relationship := .siblingsChild, age := 14, daysWithTaxpayer := 150
                  qualifyingChildOfAnother := true }] }
    status := some { paidOverHalfHouseholdCost := true }
    asFiled := some
      { filing := .hoh, taxpayerAge := 32, wages := 21000
        dependents := [son, { name := "niece", relationship := .siblingsChild, age := 14, daysWithTaxpayer := 365 }] }
    accuracy := some {}
    expected :=
      [{ item := "filingStatus", text := some "hoh" }, { item := "qualifyingChild:niece", flag := some false },
       { item := "dependent:niece", flag := some false }, { item := "eicChild:son", flag := some true },
       { item := "taxableIncome", value := some 2650 }, { item := "regularTax", value := some 266 },
       { item := "eic", value := some 3207 }, { item := "refundableCtc", value := some 1400 },
       { item := "deficiency", value := some 3576 }, { item := "accuracyPenalty", value := some 0 },
       { item := "substantialUnderstatement", flag := some false }] }

#guard (decideCase case1).agrees
#guard (decideCase case1).deficiency = some 3576
#guard ((decideCase case1).asFiled.map (·.netTax)) = some (-8183)

/-! ## Worked case 2 (tax year 2022): an unreported 401(k) distribution, a late return, §6662

Single, 45, wages $60,000 (withholding $5,000). She took $30,000 from her 401(k) while still employed (no
exception) and did not report it. The return (wages only) was filed 1 Aug 2023 with the balance paid that day; no
extension. The IRS asserts §72(t), §6662(a) and §6651(a)(1) and (a)(2); supervisory approval was obtained.

As corrected: AGI $90,000; standard deduction $12,950; taxable income $77,050; Tax Table 77,050–77,100 single:
$12,574. §72(t): 10% × $30,000 = $3,000. Total tax $15,574.
As filed: taxable income $47,050; Table 47,050–47,100: $5,974.
Deficiency $9,600. Understatement $9,600 exceeds the greater of $1,557.40 (10%) and $5,000: §6662 penalty
20% × $9,600 = $1,920.
§6651: due 18 Apr 2023, filed 1 Aug 2023: 4 months (105 days, so the $450 minimum is in play but lower). Net amount
required $15,574 − $5,000 = $10,574; (a)(2) on the tax shown less withholding, $974, for 4 months = $19.48 → $19.
(a)(1) = 20% × $10,574 − (c)(1) offset $19.48 = $2,095.32 → $2,095. -/
def case2 : Case :=
  { citation := "Worked example 2 (hypothetical, after Pub. 590-B (2022))"
    taxYear := 2022
    facts :=
      { taxpayerAge := 45, wages := 60000, pensions := 30000, withholding := 5000
        earlyDistributions := [{ amountIncludible := 30000, plan := .qualifiedPlan }] }
    asFiled := some { taxpayerAge := 45, wages := 60000, withholding := 5000 }
    accuracy := some {}
    lateness := some { filed := some ⟨2023, 8, 1⟩, paid := some ⟨2023, 8, 1⟩ }
    expected :=
      [{ item := "taxableIncome", value := some 77050 }, { item := "regularTax", value := some 12574 },
       { item := "earlyDistributionTax", value := some 3000 }, { item := "deficiency", value := some 9600 },
       { item := "substantialUnderstatement", flag := some true }, { item := "accuracyPenalty", value := some 1920 },
       { item := "failureToFile", value := some 2095 }, { item := "failureToPay", value := some 19 }] }

#guard (decideCase case2).agrees
#guard (decideCase case2).checks.length = 8

/-! ## The JSON reader fills in defaults -/

-- Case 2 as a case agent would write it (only what the opinion finds).
def case2Json : String := "{\"citation\": \"Worked example 2\", \"taxYear\": 2022,
  \"facts\": {\"taxpayerAge\": 45, \"wages\": 60000, \"pensions\": 30000, \"withholding\": 5000,
            \"earlyDistributions\": [{\"amountIncludible\": 30000, \"plan\": \"qualifiedPlan\"}]},
  \"asFiled\": {\"taxpayerAge\": 45, \"wages\": 60000, \"withholding\": 5000},
  \"accuracy\": {},
  \"lateness\": {\"filed\": \"2023-08-01\", \"paid\": \"2023-08-01\"},
  \"expected\": [{\"item\": \"deficiency\", \"value\": 9600}, {\"item\": \"accuracyPenalty\", \"value\": 1920},
               {\"item\": \"failureToFile\", \"value\": 2095}, {\"item\": \"failureToPay\", \"value\": 19}]}"

#guard match parseCase case2Json with
  | .ok c => (decideCase c).agrees && (decideCase c).deficiency == some 9600
  | .error _ => false

/-! ## 2012–2015 (Rev. Procs. 2011-52, 2013-15, 2013-35, 2014-61)

EIC rows from Pub. 596 (2012–2015) and Tax Table rows from the 2012–2015 Form 1040 Tax Tables (i1040tt). All 4,083
extracted rows of the four EIC Tables (`pdftotext -raw`) and every Tax Table row agree (`tools/taxcourt/CheckTables.lean`,
Nov 2026); the 2012–2015 tables phase out from the unrounded maximum, like 2016–2023. -/

#guard eicRow 2012 12000 = [150, 3169, 4810, 5411, 475, 3169, 4810, 5411]
#guard eicRow 2012 20000 = [0, 2700, 4618, 5272, 0, 3169, 5236, 5891]
#guard eicRow 2012 27350 = [0, 1525, 3070, 3724, 0, 2358, 4167, 4822]
#guard eicRow 2013 12000 = [177, 3250, 4810, 5411, 487, 3250, 4810, 5411]
#guard eicRow 2013 30000 = [0, 1254, 2741, 3412, 0, 2107, 3865, 4537]
#guard eicRow 2014 12000 = [196, 3305, 4810, 5411, 496, 3305, 4810, 5411]
#guard eicRow 2014 27350 = [0, 1780, 3450, 4132, 0, 2647, 4593, 5276]
#guard eicRow 2015 20000 = [0, 3053, 5145, 5838, 23, 3359, 5548, 6242]
#guard eicRow 2015 30000 = [0, 1455, 3039, 3732, 0, 2337, 4201, 4895]

-- Tax Tables (single, MFJ, MFS, HoH)
#guard tableRow 2012 48500 = [8161, 6409, 8161, 6776]
#guard tableRow 2012 77000 = [15286, 11316, 15457, 13901]
#guard tableRow 2013 48500 = [8060, 6386, 8060, 6641]
#guard tableRow 2014 77000 = [15113, 10969, 15191, 13669]
#guard tableRow 2015 99950 = [21064, 16581, 21519, 19316]

-- Printed base amounts: Rev. Proc. 2011-52 Table 3 (2012 single, over $388,350: $112,683.50; 35% is the top rate);
-- Rev. Proc. 2013-15 Table 1 (2013 joint, over $450,000: $125,846 plus 39.6%); Rev. Proc. 2013-35 Table 2 (2014 HoH,
-- over $432,200: $123,424); Rev. Proc. 2014-61 Table 4 (2015 separate, over $232,425: $64,998.25).
#guard (rateSched 2012 .single).mills 388350 = 112683500 ∧
  (rateSched 2012 .single).mills 1388350 = 112683500 + 350 * 1000000
#guard (rateSched 2013 .mfj).mills 450000 = 125846000
#guard (rateSched 2014 .hoh).mills 432200 = 123424000
#guard (rateSched 2015 .mfs).mills 232425 = 64998250

-- Capital gain: 2012 has no 20% rate. Single, $1,000,000 of long-term gain: 0% to $35,350, 15% on the rest
-- ($144,697.50 → $144,698). 2013: 0% to $36,250, 15% to $400,000 ($54,562.50 → $54,563), 20% on $600,000.
#guard regularTax (py 2012) .single 1000000 1000000 = 144698
#guard regularTax (py 2013) .single 1000000 1000000 = 54563 + 120000

-- Standard deduction, exemptions: 2012 single $5,950 + $3,800: wages $40,000 → taxable $30,250.
#guard (computeReturn (py 2012) { wages := 40000 }).taxableIncome = 30250
-- 2015 joint, both 66: $12,600 + 2 × $1,250 = $15,100.
#guard (computeReturn (py 2015) { filing := .mfj, taxpayerAge := 66, spouseAge := 66 }).standardDeduction = 15100
-- §151(d)(3): none in 2012 (four exemptions at AGI $1,000,000 = $15,200); 2013 joint AGI $350,000 is $50,000 over
-- $300,000: 20 steps of $2,500 = 40% of $15,600 lost.
#guard exemptions (py 2012) .mfj 1000000 4 = 15200
#guard exemptions (py 2013) .mfj 350000 4 = 15600 - 6240
-- Qualifying relative gross income: $3,899 passes in 2013 ($3,900), $3,900 does not.
#guard qualifyingRelative (py 2013)
  { relationship := .parent, grossIncome := 3899, taxpayerProvidedOverHalfSupport := true, youngerThanTaxpayer := false,
    age := 70 } = true
#guard qualifyingRelative (py 2013)
  { relationship := .parent, grossIncome := 3900, taxpayerProvidedOverHalfSupport := true, youngerThanTaxpayer := false,
    age := 70 } = false
-- 2012 payroll tax holiday: profit $50,000: SE tax $6,141, §164(f) deduction $3,532 (59.6% × 10.4% part + ½ × 2.9%).
#guard (computeReturn (py 2012) { seProfit := 50000 }).seTax = 6141
#guard (computeReturn (py 2012) { seProfit := 50000 }).halfSeTax = 3532
#guard (computeReturn (py 2013) { seProfit := 50000 }).seTax = 7065
-- §72(t)(2)(B) medical floor: 2012 7.5%; 2014 10%, 7.5% if 65 or over (§213(f)).
#guard (earlyDistTax (py 2012) 50000 false { amountIncludible := 10000, medicalExpenses := 8000 }).exempt = 4250
#guard (earlyDistTax (py 2014) 50000 false { amountIncludible := 10000, medicalExpenses := 8000 }).exempt = 3000
#guard (earlyDistTax (py 2014) 50000 true { amountIncludible := 10000, medicalExpenses := 8000 }).exempt = 4250
-- CTC: $1,000 per child; ACTC 15% over $3,000 (2014: one child, no tax, earned $8,000 → $750).
#guard (ctcFor (py 2014) ⟨1, 0, 0⟩ { filing := .single, magi := 8000, taxLeft := 0, earnedIncome := 8000 }).refundable = 750
-- §6651(a) minimum: $135 (2012–2014 returns), $205 (2015 return, due 18 Apr 2016).
#guard [2012, 2013, 2014, 2015].map (fun y => (py y).ftfMinimum) = [135, 135, 135, 205]
#guard (lateAdditions (py 2014) 500 500 { filed := some ⟨2015, 7, 1⟩, paid := some ⟨2015, 4, 15⟩ }).failureToFile = 135

/-! ## §6651(g): the substitute for return (T.C. Memo. 2024-67)

A non-filer for 2018; the IRS prepared a substitute for return on 12 Sep 2022 showing $60,811, with withholding of
$42,961 (net $17,850). The deficiency is measured against a tax shown of 0; the §6651(a)(2) addition and the (c)(1)
offset against the SFR's tax. (a)(2): 41 months (15 Apr 2019 – 12 Sep 2022) × 0.5% × $17,850 = $3,659.25 → $3,659.
(a)(1): 5 months × 5% less 5 × 0.5% = 22.5% × $17,850 = $4,016.25 → $4,016 — both as the court sustained. -/
def moranJson : String := "{\"citation\": \"T.C. Memo. 2024-67\", \"taxYear\": 2018,
  \"facts\": {\"filing\": \"single\", \"wages\": 213630, \"capitalGain\": 32227, \"otherIncome\": 6236,
            \"pensions\": 2417, \"ordinaryDividends\": 2, \"withholding\": 42961,
            \"earlyDistributions\": [{\"amountIncludible\": 2417, \"plan\": \"qualifiedPlan\"}]},
  \"taxShown\": 0, \"sfrTax\": 60811, \"lateness\": {\"asOf\": \"2022-09-12\"},
  \"expected\": [{\"item\": \"taxableIncome\", \"value\": 242512}, {\"item\": \"regularTax\", \"value\": 60569},
               {\"item\": \"totalTax\", \"value\": 60811}, {\"item\": \"deficiency\", \"value\": 60811},
               {\"item\": \"failureToFile\", \"value\": 4016}, {\"item\": \"failureToPay\", \"value\": 3659},
               {\"item\": \"adjustments\", \"value\": 0}, {\"item\": \"taxShown\", \"value\": 0}]}"

#guard match parseCase moranJson with
  | .ok c => (decideCase c).agrees
  | .error _ => false
-- Without `sfrTax` the additions would use the tax shown of 0: no (a)(2), and (a)(1) without the offset (25%).
#guard match parseCase moranJson with
  | .ok c => (decideCase { c with sfrTax := none }).lateness.map (fun l => (l.failureToFile, l.failureToPay)) =
      some (4463, 0)
  | .error _ => false

-- The as-filed items: case 2's return as filed has taxable income $47,050 and tax $5,974.
#guard (decideCase { case2 with expected := [{ item := "asFiled.taxableIncome", value := some 47050 },
  { item := "asFiled.tax", value := some 5974 }, { item := "adjustments", value := some 0 }] }).agrees

end Legal.USTax.TaxCourt.Tests
