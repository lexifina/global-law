import TaxKernel.World

/-!
# Bangladesh: income tax of a resident individual, income year 2025-26 (assessment year beginning 1 July 2026)

Access tier A. Statutes (Bengali; Global law holds only the English-language laws of bdlaws, and the Income Tax Act
2023 is Bengali-only there):
* Finance Ordinance 2025 (অর্থ অধ্যাদেশ, ২০২৫, Ordinance No. 28 of 2025, Bangladesh Gazette Extraordinary 2 June 2025),
  bdlaws upload `2025-06-17-10-04-01-Ordinance-No.-28-of-2025.pdf`, Internet Archive copy 20260306182325
  (`bd/law/ord28_2025.pdf`, sha256 6fa18894...); its text layer is a legacy font, so read by Bengali OCR
  (`tools/ocrb.sh`, tessdata_best ben) and every number used here checked on the page image (pp. 102, 105).
  s. 136 (1): for "২০২৬ সালের ১ জুলাই তারিখে আরব্ধ করবর্ষের" (the assessment year beginning 1 July 2026, i.e. income
  year July 2025 - June 2026) tax is charged at Schedule 2 Part 1 (তফসিল-২ প্রথম অংশ); s. 136 (5) surcharge Schedule 2
  Parts 2-3. s. 130 (7): Income Tax Act 2023 Sixth Schedule Part 1 para (27) "৪ (চার) লক্ষ ৫০ (পঞ্চাশ) হাজার" ->
  "৫ (পাঁচ) লক্ষ".
* Income Tax Act 2023 (আয়কর আইন, ২০২৩, Act No. 12 of 2023), bdlaws act-1429 as archived (Internet Archive): s. 78
  (2026-02-10 copy, with its Finance Ordinance 2025 s. 58 footnote "যাহা 2025 সনের 1 জুলাই হইতে কার্যকর"), s. 32
  (2026-01-14), s. 331 (2025-11-12); Sixth Schedule para (27) wording in the archived schedule PDF.
* **Finance Act 2026 (অর্থ আইন, ২০২৬, Act No. 96 of 2026, Bangladesh Gazette Extraordinary 30 June 2026; nbr.gov.bd
  `uploads/acts/Finance_Act_2026.pdf`, `bd/law/w4/fa2026.pdf`, sha256 in SHA256SUMS; legacy-font text layer, read by
  Bengali OCR and the rate page checked as an image, gazette p. 20424; round W4).** s. 1 (2): in force 1 July 2026.
  s. 160 (1): "২০২৬-২০২৭ হইতে ২০৩০-২০৩১ করবর্ষের জন্য কোনো কর নির্ধারণের ক্ষেত্রে এই আইনের তফসিল-২ এর প্রথম অংশে
  নির্দিষ্ট করহার অনুযায়ী আয়কর ধার্য হইবে". Tax year 2026-27 is the tax year that FO 2025 s. 136 called "২০২৬ সালের
  ১ জুলাই তারিখে আরব্ধ করবর্ষ" (income year 2025-26), so the later Act's Schedule 2 Part 1 para (ক) ("২০২৬-২০২৭ এবং
  ২০২৭-২০২৮ করবর্ষের জন্য করহার") governs it: "৪,০০,০০০ টাকা পর্যন্ত শূন্য; পরবর্তী ৩,০০,০০০ ১০%; পরবর্তী ৪,০০,০০০ ১৫%;
  পরবর্তী ৫,০০,০০০ ২০%; পরবর্তী ২০,০০,০০০ ২৫%; অবশিষ্ট ৩০%"; provisos (ক) women and 65+ ৪,৫০,০০০, (খ) third gender
  and disabled ৫,২৫,০০০, (গ) war-wounded freedom fighters and July warriors ৫,৫০,০০০, (ঘ) + ৫০,০০০ per disabled child,
  (চ) minimum tax ৫,০০০ (new taxpayers ১,০০০); Part 2 surcharge as in FO 2025 (page image p. 20430). Until W4 the model
  used FO 2025 Schedule 2 (৩,৭৫,০০০ / ৪,২৫,০০০ / ৫,০০,০০০ / ৫,২৫,০০০), which FA 2026 replaced for this tax year.
  FA 2026 s. 61 (s. 78 rebate: 0.10 and 7.50 lakh) is an amendment of the Act in force from 1 July 2026; the model keeps
  FO 2025's s. 78 for income year 2025-26, as it applied FO 2025's own s. 78 change from 1 July 2025 (a reading).
* NBR, আয়কর পরিপত্র ২০২৫-২০২৬ (Income tax circular 2025-26, 21 August 2025; nbr.gov.bd, sha256 05fe0f02...): the
  Board's own reading of the same rates (official secondary; consistent).
-/

namespace BdTax
open TaxKernel

/-- s. 331: "টাকার কোনো ভগ্নাংশ 50 (পঞ্চাশ) পয়সা বা ততোধিক হইলে উহা 1 (এক) টাকা হিসাবে গণ্য হইবে". -/
def r331 : Rule := { mode := .halfUp }

/-- The band structure (FA 2026 Schedule 2 Part 1 para (ক) keeps the widths and rates and sets the first band to ৪,০০,০০০;
the FO 2025 text it replaced for tax year 2026-27, page image p. 102): "৩,৭৫,০০০টাকা পর্যন্ত শূন্য; পরবর্তী
৩,০০,০০০টাকা ১০%; পরবর্তী ৪,০০,০০০টাকা ১৫%; পরবর্তী ৫,০০,০০০টাকা ২০%; পরবর্তী ২০,০০,০০০টাকা ২৫%;
অবশিষ্ট টাকার উপর ৩০%". The band widths after the first band are fixed; the first band is the exempt limit `z`
(provisos (ক)-(ঘ) raise "করমুক্ত আয়ের সীমা", the tax-free income limit; read as widening the first band). -/
def schedFor (z : Int) : Schedule :=
  Schedule.ofList [(0, 0), (z, 1000), (z + 300000, 1500), (z + 700000, 2000), (z + 1200000, 2500), (z + 3200000, 3000)]
def sched : Schedule := schedFor 400000

/-- Provisos (FA 2026 Schedule 2 Part 1 para (ক)): (ক) women and taxpayers aged 65 or over 4,50,000; (খ) third gender and
persons with disability 5,25,000; (গ) gazetted war-wounded freedom fighters and "July warriors" 5,50,000; (ঘ) + 50,000
for each disabled child (one parent). -/
def exemptLimit (age : Nat) (female thirdGenderOrDisabled warrior : Bool) (disabledChildren : Nat) : Int :=
  let base : Int := if warrior then 550000 else if thirdGenderOrDisabled then 525000
    else if female || age ≥ 65 then 450000 else 400000
  base + 50000 * disabledChildren

/-- Proviso: "মোট আয় করমুক্ত আয়ের সীমা অতিক্রম করিলে ন্যূনতম করের পরিমাণ হইবে ৫,০০০ (পাঁচ হাজার টাকা), তবে, নূতন
করদাতাগণের ক্ষেত্রে এইরূপ ন্যূনতম করের পরিমাণ হইবে ১,০০০". -/
def minTax (newTaxpayer : Bool) : Int := if newTaxpayer then 1000 else 5000

/-- Income Tax Act 2023 Sixth Schedule Part 1 para (27) as amended by FO 2025 s. 130 (7): exempt "চাকরি হইতে আয়
হিসাবে পরিগণিত আয়ের এক-তৃতীয়াংশ বা ৫ (পাঁচ) লক্ষ টাকা যাহা কম". -/
def salaryExempt (sal : Int) : Int := min (pos sal / 3) 500000

/-- s. 78: rebate the least of "(ক) 0.03 × 'ক'; (খ) 0.15 × 'খ'; (গ) 10 (দশ) লক্ষ টাকা"; 'ক' = total income less
exempt income, reduced-rate income, firm/AOP share income and final-settlement income; 'খ' = eligible investment
and expenditure under Sixth Schedule Part 3. -/
def rebate (incomeK investmentKh : Int) : Int :=
  min (min (divR .halfUp (300 * pos incomeK) BP) (divR .halfUp (1500 * pos investmentKh) BP)) 1000000

/-- Schedule 2 Part 2 para (ক) (page image p. 105): surcharge on the tax computed at the Part 1 rates, by net wealth
in the statement of assets and liabilities (s. 167): up to 4 crore nil; over 4 crore to 10 crore (or more than one
motor car in own name, or house property over 8,000 sq ft) 10 %; over 10 to 20 crore 20 %; over 20 to 50 crore
30 %; over 50 crore 35 %. -/
def surchargeRate (netWealth : Int) (cars : Nat) (bigHouse : Bool) : Int :=
  if netWealth > 500000000 then 3500 else if netWealth > 200000000 then 3000
  else if netWealth > 100000000 then 2000 else if netWealth > 40000000 || cars > 1 || bigHouse then 1000 else 0

/- The cumulative tax at the top of each band (statute's bands summed). -/
#guard sched.tax r331 700000 = 30000 ∧ sched.tax r331 1100000 = 90000 ∧ sched.tax r331 1600000 = 190000 ∧
  sched.tax r331 3600000 = 690000

structure PersonOut where
  ti : Int
  taxRates : Int
  reb : Int
  tax : Int
  surcharge : Int
  limit : Int

def person (c : Canon) (i : Nat) (a : Adult) (other investment : Int) : PersonOut :=
  let female := (c.str? (if i = 0 then "bdSex1" else "bdSex2")) == some "female"
  let flagB (k : String) := (c.bool? k).getD false
  let lim := exemptLimit a.age female (flagB (if i = 0 then "bdDisabled1" else "bdDisabled2"))
    (flagB (if i = 0 then "bdWarrior1" else "bdWarrior2"))
    (if i = 0 then ((c.int? "bdDisabledChildren").getD 0).toNat else 0)
  let sal := a.wages + a.pension
  let ti := pos (sal - salaryExempt sal) + a.selfEmployment + other
  let t := (schedFor lim).tax r331 ti
  let reb := min t (rebate ti investment)
  let afterReb := t - reb
  let tax := if ti > lim then max afterReb (minTax (flagB "bdNewTaxpayer")) else afterReb
  let nw := if i = 0 then (c.int? "bdNetWealth").getD 0 else (c.int? "bdNetWealth2").getD 0
  let cars := if i = 0 then ((c.int? "bdCars").getD 0).toNat else 0
  let sur := divR .halfUp (surchargeRate nw cars false * t) BP
  { ti, taxRates := t, reb, tax, surcharge := sur, limit := lim }

def compute (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let rs := (c.adults.zip (List.range n)).map fun (a, i) =>
    person c i a (share (c.interest + c.dividends + c.rentalIncome + c.capitalGains) i)
      (if i = 0 then c.pensionContributions else 0)
  let s (f : PersonOut → Int) := sumInts (rs.map f)
  Out.make c "BD" "BDT" (s (·.tax))
    (surtaxes := [("netWealthSurcharge", s (·.surcharge))])
    (detail := [Out.d "taxableIncome" (s (·.ti)), Out.d "taxBeforeRebate" (s (·.taxRates)), Out.d "rebate78" (s (·.reb)),
      Out.dStr "exemptLimit" (String.intercalate "," (rs.map fun r => toString r.limit))])
    (unsupported := ["interest, dividends, rent and gains taxed at the regular rates as total income; withholding as minimum tax (s. 163 (2)), house-property allowances and the capital-gains rates of the Sixth Schedule not modelled",
      "pensionContributions read as the eligible investment 'খ' of s. 78 (Sixth Schedule Part 3 limits not applied)",
      "no statutory employee social contribution modelled (none located; not searched further)",
      "environmental surcharge (Schedule 2 Part 3, per extra car) not modelled"])

def country : Country :=
  { code := "BD", name := "Bangladesh (income year 2025-26, AY 2026-27)", currency := "BDT", year := "2025-26",
    compute := compute }

theorem sched_progressive : sched.progressive = true := by decide

/- The minimum-tax notch: one taka of total income above the exempt limit costs 5,000 taka. -/
#guard (let t := sched.tax r331 400001; max t (minTax false)) - sched.tax r331 400000 = 5000
/- The minimum tax binds until the 10 % band yields 5,000: up to 450,000 of total income. -/
#guard sched.tax r331 450000 = 5000

end BdTax
