import TaxKernel

/-!
# Malta, income of calendar year 2025 (year of assessment 2026): every parameter with its source

Statute texts: Global law (`malta/national/acts/...`, official publisher legislation.mt), saved in `mt/law/`.
"ITA" = Income Tax Act (Cap. 123); "SSA" = Social Security Act (Cap. 318); "ITMA" = Income Tax Management Act
(Cap. 372). Malta taxes the income of the year immediately preceding the year of assessment (ITA art. 56(1):
"in the year immediately preceding the year of assessment"), so 2025 income is assessed in YA 2026, and the
bands below are those of Act IX of 2025 s. 15 marked "§ Applicable from year of assessment 2026".

Money: whole euros for incomes; tax is first computed exactly in cents (the statute's "multiply by 15% and then
subtract" gives cents) and then rounded to the nearest euro (ITA art. 56(19)(b): "round up or down any amount to
the nearest euro").
-/

namespace MtTax
open TaxKernel

/-! ## ITA art. 56(1): the three rate tables for YA 2026 (Act IX of 2025) -/

/-- ITA art. 56(1)(a) (married couple, joint computation): "does not exceed €15,000 … 0%; exceeds €15,000 but is
less than €23,000 … 15% and then subtracting €2,250; exceeds €23,000 but is less than €60,000 … 25% … €4,550;
exceeds €60,000 … 35% … €10,550". -/
def marriedSched : Schedule := Schedule.ofList [(0, 0), (15000, 1500), (23000, 2500), (60000, 3500)]

/-- ITA art. 56(1)(b) (any other resident individual, incl. each spouse under art. 49A/50): "does not exceed
€12,000 … 0%; exceeds €12,000 but is less than €16,000 … 15% … €1,800; exceeds €16,000 but is less than €60,000 …
25% … €3,400; exceeds €60,000 … 35% … €9,400". -/
def singleSched : Schedule := Schedule.ofList [(0, 0), (12000, 1500), (16000, 2500), (60000, 3500)]

/-- ITA art. 56(1)(b), "Provided further that where … a parent maintained under his or her custody a child, or
paid maintenance …, and such child was not over 18 years of age (or not over 23 years if receiving full-time
instruction …)": "does not exceed €13,000 … 0%; exceeds €13,000 but is less than €17,500 … 15% … €1,950; exceeds
€17,500 but is less than €60,000 … 25% … €3,700; exceeds €60,000 … 35% … €9,700". -/
def parentSched : Schedule := Schedule.ofList [(0, 0), (13000, 1500), (17500, 2500), (60000, 3500)]

/-- The statute's own formula ("multiplying the chargeable income by r% and then subtracting €s"), in cents, for a
table with zero band up to `t1`, 15 % up to `t2`, 25 % up to `t3`, 35 % above, subtractions `s2 s3 s4` (euros).
At exactly `t2` and `t3` the YA 2026 wording ("exceeds X but is less than Y" / "exceeds Y") names no formula (see
FINDINGS F4); we use the upper one, which gives the same amount because the table is continuous. -/
def formulaCents (t1 t2 t3 s2 s3 s4 : Int) (x : Int) : Int :=
  if x ≤ t1 then 0
  else if x < t2 then 15 * x - 100 * s2
  else if x < t3 then 25 * x - 100 * s3
  else 35 * x - 100 * s4

def marriedFormula : Int → Int := formulaCents 15000 23000 60000 2250 4550 10550
def singleFormula : Int → Int := formulaCents 12000 16000 60000 1800 3400 9400
def parentFormula : Int → Int := formulaCents 13000 17500 60000 1950 3700 9700

/-! ## Earlier and later tables (versioned law; used by the findings only) -/

/-- YA 2025 (income 2024), ITA art. 56(1) before Act IX of 2025 (diff in `law/cap123_art56_diff_2024_2025.txt`):
single "exceeds €9,100 but is less than €14,501 … 15% … €1,365; exceeds €14,500 but is less than €19,501 … 25% …
€2,815; exceeds €19,500 but is less than €60,001 … 25% … €2,725; exceeds €60,000 … 35% … €8,725". Cents. -/
def singleYA2025 (x : Int) : Int :=
  if x ≤ 9100 then 0 else if x ≤ 14500 then 15 * x - 136500 else if x ≤ 19500 then 25 * x - 281500
  else if x ≤ 60000 then 25 * x - 272500 else 35 * x - 872500

/-- YA 2025 married: 12,700 / 21,200 / 28,700 / 60,000; subtract 1,905 / 4,025 / 3,905 / 9,905. Cents. -/
def marriedYA2025 (x : Int) : Int :=
  if x ≤ 12700 then 0 else if x ≤ 21200 then 15 * x - 190500 else if x ≤ 28700 then 25 * x - 402500
  else if x ≤ 60000 then 25 * x - 390500 else 35 * x - 990500

/-- YA 2025 parent: 10,500 / 15,800 / 21,200 / 60,000; subtract 1,575 / 3,155 / 3,050 / 9,050. Cents. -/
def parentYA2025 (x : Int) : Int :=
  if x ≤ 10500 then 0 else if x ≤ 15800 then 15 * x - 157500 else if x ≤ 21200 then 25 * x - 315500
  else if x ≤ 60000 then 25 * x - 305000 else 35 * x - 905000

/-- YA 2027 (income 2026), ITA art. 56(1)(b)(iv) as inserted by Act III of 2026 (parent, one child): "does not
exceed €14,500 … 0%; exceeds €14,500 but is less than €21,000 … 15% … €2,175; exceeds €21,000 but is less than
€60,000 … 25% … €4,275; exceeds €60,000 … 35% … €10,270". Cents. -/
def parent1YA2027 (x : Int) : Int :=
  if x ≤ 14500 then 0 else if x < 21000 then 15 * x - 217500 else if x ≤ 60000 then 25 * x - 427500
  else 35 * x - 1027000

/-! ## ITA art. 12(1)(c)(iii)(C)(b): dividend "relevant thresholds" (unchanged since YA 2025) -/

/-- "in the case where the rates prescribed under article 56(1)(a) apply, the relevant threshold is €28,700" -/
def divThresholdMarried : Int := 28700
/-- "… article 56(1)(b) apply, the relevant threshold is €19,500" -/
def divThresholdSingle : Int := 19500
/-- "… the last proviso to article 56(1)(b) apply, the relevant threshold is €21,200" -/
def divThresholdParent : Int := 21200

/-! ## Final and flat taxes -/

/-- ITA art. 33(1): "deduct tax … at a rate of fifteen cents (€0.15) on every euro" of investment income
(art. 41(a): bank interest, government and listed bond interest). Final unless the recipient elects gross
(arts. 34-36). -/
def interestWhtBp : Int := 1500
/-- ITA art. 31D(2): rent from a tenement, "at the option of the person … fifteen cents (0.15) on every euro of the
gross rental income received. Such tax shall be final". -/
def rentFinalBp : Int := 1500
/-- ITA art. 90A(11): "With effect from the year of assessment 2023, the rate of tax on income from part-time work
… shall be ten cents (€0.10) on every euro". -/
def partTimeBp : Int := 1000
/-- Part-Time Work Rules (S.L. 123.39) r. 3(2): the excess over "ten thousand euro (€10,000) in the case of income
chargeable under article 4(1)(b)" (employment) is charged at the normal rates. -/
def partTimeLimitEmployment : Int := 10000
/-- S.L. 123.39 r. 3(2): "twelve thousand euro (€12,000) in the case of income chargeable under article 4(1)(a)". -/
def partTimeLimitTrade : Int := 12000
/-- ITA art. 56(6): "thirty-five cents (0.35) on every euro of the chargeable income of every company"; the
dividend carries this tax (art. 59(1)(a), full imputation, art. 31). -/
def companyRateBp : Int := 3500

/-! ## Credits -/

/-- ITA art. 57(1) as prescribed by the Personal Retirement Scheme Rules (S.L. 123.163) r. 8: "twenty-five percent
(25%) of the aggregate amount of the qualifying contributions … may not exceed seven hundred and fifty euro
(€750)". Non-refundable (art. 57(5)); each spouse may claim (art. 57(2)). -/
def prsRateBp : Int := 2500
def prsCap : Int := 750

/-! ## SSA Tenth Schedule, Part I (Class One, employed persons), as substituted by L.N. 10 of 2025 (deemed in force
1 January 2024; the text in force throughout 2025: no later change in the record to 2026-10-06). Cents per week. -/

/-- Category A: "Persons under eighteen (18) years of age whose basic weekly wage … does not exceed €213.54": €6.62 -/
def c1CatA : Int := 662
/-- Category B: "Persons over eighteen (18) years … does not exceed €213.54": €21.35 -/
def c1CatB : Int := 2135
/-- The category A/B wage limit, €213.54 a week. -/
def c1LowWage : Int := 21354
/-- Category C: "10% calculated to the nearest cent of their basic weekly wage". -/
def c1RateBp : Int := 1000
/-- Category D, born on 31 December 1961 or before: €42.31 (= 10 % of the €423.07 limit of category C). -/
def c1MaxOld : Int := 4231
/-- Category D, born on 1 January 1962 or after: €53.23 (Note 2: pensionable income "guaranteed at the amount of
€27,679.09", 1/52 = €532.29). -/
def c1MaxNew : Int := 5323

/-! ## SSA Tenth Schedule, Part III (Class Two, self-occupied persons), same L.N. Cents per week. -/

/-- Category SA "Is less than €12,028.92": €34.70. -/
def c2Min : Int := 3470
def c2LowIncomeCents : Int := 1202892
/-- Category SB: "The weekly equivalent of 15% of their annual net earnings calculated to the nearest cent". -/
def c2RateBp : Int := 1500
/-- Category SC: €63.46 (born 1961 or before), €79.84 (born 1962 or after). -/
def c2MaxOld : Int := 6346
def c2MaxNew : Int := 7984
/-- Self-occupied threshold: SSA (Cap. 318) art. 2, "\"self-occupied\" means a self-employed person who is engaged in
any activity through which earnings exceeding €910 per annum are being derived" (consolidated text,
`improve-central/refs/mt/cap318_current.txt`; audit round 8; EUROMOD CR MT Table 2.21 gives the same €910). -/
def c2Exempt : Int := 910

/-! ## SSA art. 76 and Fourteenth Schedule Part VI (Children's Allowance), L.N. 10 of 2025 (deemed in force 6 January
2024; no later change in the record to 2026-10-06). -/

/-- "Where the maximum annual reckonable income for entitlement purposes is €27,006.12 or less" (cents). -/
def caThreshold : Int := 2700612
/-- "any annual reckonable income below €7,741.12 shall be considered to be equivalent to €7,741.12" (cents). -/
def caFloor : Int := 774112
/-- "Children in household under sixteen (16) years of age: 6.5% for each such child". -/
def caRateBp : Int := 650
/-- Table B, "Fixed Children's Allowance … €8.66 per week for each such child" (cents). -/
def caFixedWeekly : Int := 866

/-! ## Earlier income years 2022-2024 (= YA 2023-2025); improvement round 2, 2026-11-19

Copies of the official PDFs (legislation.mt, fetched 2026-11-19) in `cmp20/improve-central/refs/mt/`.

* ITA art. 56(1): the tables of the text in force on 2024-06-30 (`law/cap123_art56_diff_2024_2025.txt`, the
  "[-...-]" side; `singleYA2025`, `marriedYA2025`, `parentYA2025` above) apply to YA 2023, 2024 and 2025. The only
  amendments of art. 56 between the YA 2019-2021 substitutions (VII.2018.23, VII.2019.21, VIII.2020.21) and Act IX
  of 2025 are Act VII of 2022 s. 28 (sub-arts. (17), (26), (26A); `Act_2022_7.txt`) and Act XIII of 2024 s. 12
  (sub-arts. (26), (26A); `Act_2024_13.txt`): neither touches sub-art. (1).
* SSA Tenth Schedule Part I (Class One) and Part III (Class Two, self-occupied), and Fourteenth Schedule Part VI
  (Children's Allowance):
  - 2022: L.N. 232 of 2023, Social Security Act (Amendment of Schedules) Regulations, 2023, reg. 1(2): "deemed to
    have come into force ... in the case of the Tenth Schedule, with effect from the 3rd January, 2022" and the
    Fourteenth "with effect from the 1st January, 2022" (`LN_2023_232.txt`);
  - 2023: L.N. 257 of 2023 (Amendment No. 2 of Schedules) Regulations, 2023, reg. 1(2): Tenth Schedule "with effect
    from the 2nd January, 2023", Fourteenth "with effect from the 7th January, 2023" (`LN_2023_257.txt`);
  - 2024: L.N. 10 of 2025 (the values above, `refs/LN_2025_10.txt`), also used for 2025 (finding F11).
-/

/-- The Tenth Schedule amounts of one contribution year (cents; Class One weekly, Class Two weekly, annual limits). -/
structure SSParams where
  /-- category A/B wage limit ("does not exceed ...") -/
  lowWage : Int
  catA : Int
  catB : Int
  /-- category D: born 1961 or before / born 1962 or after -/
  maxOld : Int
  maxNew : Int
  /-- Class Two (self-occupied) SA amount, its income limit ("is less than ...", cents), SC maxima -/
  c2Min : Int
  c2Low : Int
  c2MaxOld : Int
  c2MaxNew : Int
  deriving Repr

/-- L.N. 232 of 2023, Tenth Schedule Part I: A "€6.62" / B "€18.28" for a wage that "does not exceed €182.83";
D "€37.90" (born 1961 or before, wage "exceeds €378.98") and "€49.97" (born 1962 or after, "exceeds €499.73");
Part III (self-occupied): SA "Is less than €10,848." "€31.29"; SC "€ 56.85" / "€74.96". -/
def ss2022 : SSParams :=
  { lowWage := 18283, catA := 662, catB := 1828, maxOld := 3790, maxNew := 4997,
    c2Min := 3129, c2Low := 1084800, c2MaxOld := 5685, c2MaxNew := 7496 }

/-- L.N. 257 of 2023, Tenth Schedule Part I: A "€6.62" / B "€19.27" for a wage that "does not exceed €192.73";
D "€39.28" ("exceeds €392.77") and "€51.60" ("exceeds €515.99"); Part III: SA "Is less than €11,362.80." "€32.78";
SC "€58.91" / "€77.40". -/
def ss2023 : SSParams :=
  { lowWage := 19273, catA := 662, catB := 1927, maxOld := 3928, maxNew := 5160,
    c2Min := 3278, c2Low := 1136280, c2MaxOld := 5891, c2MaxNew := 7740 }

/-- L.N. 10 of 2025 (2024 amounts, the constants above; also used for 2025). -/
def ss2024 : SSParams :=
  { lowWage := c1LowWage, catA := c1CatA, catB := c1CatB, maxOld := c1MaxOld, maxNew := c1MaxNew,
    c2Min := c2Min, c2Low := c2LowIncomeCents, c2MaxOld := c2MaxOld, c2MaxNew := c2MaxNew }

def ssFor (y : Nat) : SSParams := if y ≤ 2022 then ss2022 else if y = 2023 then ss2023 else ss2024

/-- Fourteenth Schedule Part VI of one year: (threshold, floor, fixed weekly), cents. 2022 (L.N. 232 of 2023):
"€ 25,409 or less ... below € 6,144 shall be considered to be equivalent to € 6,144", Table B "€ 8.65 per week";
2023 (L.N. 257 of 2023): "€25,924", "€6,659", "€8.66 per week"; 2024 (L.N. 10 of 2025): €27,006.12, €7,741.12,
€8.66. The rate, "6.5% for each such child" under 16, is the same in all three. -/
def caFor (y : Nat) : Int × Int × Int :=
  if y ≤ 2022 then (2540900, 614400, 865)
  else if y = 2023 then (2592400, 665900, 866)
  else (caThreshold, caFloor, caFixedWeekly)

/-- National Minimum Wage, age 18 and over, per week (cents), Cap. 452 art. 4 orders (improvement round 7; official
PDFs in `cmp20/improve-central/refs/mt/nmw/`): L.N. 462 of 2021 art. 2(a) "Age 18 years and over ...€182.83" (in
force 1 January 2022); L.N. 334 of 2022 art. 2 "Age eighteen (18) years and over €192.73" (1 January 2023); L.N. 287 of
2023 art. 3 "€213.54" (1 January 2024); L.N. 342 of 2024 art. 3 "€221.78" (1 January 2025). Other years: none (the
Fourteenth Schedule Part VI note 2 floor is then not applied). -/
def nmwWeekly18 (y : Nat) : Option Int :=
  if y = 2022 then some 18283 else if y = 2023 then some 19273 else if y = 2024 then some 21354
  else if y = 2025 then some 22178 else none

/-! ## Eurostat convention `--eurostat` (round 10): a no-op for Malta
Eurostat earn_net ESMS 3.4 ("parameters refer to the beginning of the fiscal year"; "the most generous" family allowance
within ages 6-11; tests/data/_methodology/earn_net_esms.htm, sha256 89ab2734...). In this model the art. 56 tables, the
Tenth Schedule and the national minimum wage change only from 1 January (one schedule per contribution year), and the
Children's Allowance (Fourteenth Schedule: 6.5 % per child under 16, fixed weekly amount) does not vary with age
within 6-11. The flag is accepted and changes nothing (400 households per year, round 10). -/

end MtTax
