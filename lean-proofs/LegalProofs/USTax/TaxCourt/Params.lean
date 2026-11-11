import LegalProofs.USTax.TaxCourt.Basic
import TaxCode.Individual.D.EarnedIncome

/-!
# Year parameters, tax years 2016–2024

Every inflation-adjusted figure is copied from the revenue procedure for its year; statutory figures cite the Code
section as it read for that year. Sources (all read from the IRS PDFs, Nov 2026):

| year | revenue procedure | notes |
|---|---|---|
| 2016 | Rev. Proc. 2015-53 | |
| 2017 | Rev. Proc. 2016-55 | |
| 2018 | Rev. Proc. 2018-18 (2018-10 I.R.B. 392) | replaces Rev. Proc. 2017-58 after Pub. L. 115-97 (TCJA); the EIC figures fell with chained CPI |
| 2019 | Rev. Proc. 2018-57 | |
| 2020 | Rev. Proc. 2019-44 | |
| 2021 | Rev. Proc. 2020-45 | childless EIC, EIC investment-income limit and §24 replaced by Pub. L. 117-2 (ARPA) §§9611, 9621, 9624 |
| 2022 | Rev. Proc. 2021-45 | |
| 2023 | Rev. Proc. 2022-38 | |
| 2024 | Rev. Proc. 2023-34 | |

The social security contribution and benefit base (§1402(b)(1), SSA §230) is from the SSA's annual announcements.
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual

/-! ## Rate schedules -/

/-- A seven-rate §1 schedule: the tops of the first six rows (`e1`…`e6`, whole dollars), the seven rates in tenths of
a percent (per mille: 396 is 39.6%), and the base amount printed on the row starting at each top (`b1`…`b6`, cents). -/
structure RateSched where
  e1 : Int
  e2 : Int
  e3 : Int
  e4 : Int
  e5 : Int
  e6 : Int
  r1 : Int
  r2 : Int
  r3 : Int
  r4 : Int
  r5 : Int
  r6 : Int
  r7 : Int
  b1 : Int
  b2 : Int
  b3 : Int
  b4 : Int
  b5 : Int
  b6 : Int
  deriving Repr, DecidableEq

/-- The tax in mills (1/1000 dollar) on whole-dollar taxable income `x`, read off the table row by row. -/
def RateSched.mills (s : RateSched) (x : Int) : Int :=
  if x ≤ 0 then 0
  else if x ≤ s.e1 then s.r1 * x
  else if x ≤ s.e2 then 10 * s.b1 + s.r2 * (x - s.e1)
  else if x ≤ s.e3 then 10 * s.b2 + s.r3 * (x - s.e2)
  else if x ≤ s.e4 then 10 * s.b3 + s.r4 * (x - s.e3)
  else if x ≤ s.e5 then 10 * s.b4 + s.r5 * (x - s.e4)
  else if x ≤ s.e6 then 10 * s.b5 + s.r6 * (x - s.e5)
  else 10 * s.b6 + s.r7 * (x - s.e6)

/-- Rows in order, and each printed base amount exactly the tax at the top of the row before (no jump at any edge). -/
def RateSched.Ok (s : RateSched) : Prop :=
  0 < s.e1 ∧ s.e1 < s.e2 ∧ s.e2 < s.e3 ∧ s.e3 < s.e4 ∧ s.e4 < s.e5 ∧ s.e5 < s.e6 ∧
  10 * s.b1 = s.r1 * s.e1 ∧ 10 * s.b2 = 10 * s.b1 + s.r2 * (s.e2 - s.e1) ∧
  10 * s.b3 = 10 * s.b2 + s.r3 * (s.e3 - s.e2) ∧ 10 * s.b4 = 10 * s.b3 + s.r4 * (s.e4 - s.e3) ∧
  10 * s.b5 = 10 * s.b4 + s.r5 * (s.e5 - s.e4) ∧ 10 * s.b6 = 10 * s.b5 + s.r6 * (s.e6 - s.e5)

instance (s : RateSched) : Decidable s.Ok := by unfold RateSched.Ok; infer_instance

/-- Pre-TCJA rates, §1(a)–(d) and §1(i)(2)-(3): 10, 15, 25, 28, 33, 35, 39.6 percent. -/
def oldRates (e1 e2 e3 e4 e5 e6 b1 b2 b3 b4 b5 b6 : Int) : RateSched :=
  ⟨e1, e2, e3, e4, e5, e6, 100, 150, 250, 280, 330, 350, 396, b1, b2, b3, b4, b5, b6⟩

/-- §1(j)(2) rates (2018–2025): 10, 12, 22, 24, 32, 35, 37 percent. -/
def tcjaRates (e1 e2 e3 e4 e5 e6 b1 b2 b3 b4 b5 b6 : Int) : RateSched :=
  ⟨e1, e2, e3, e4, e5, e6, 100, 120, 220, 240, 320, 350, 370, b1, b2, b3, b4, b5, b6⟩

/-- Schedules by year and filing status, as printed (Tables 1–4 of each revenue procedure; Table 1 is "married
individuals filing joint returns and surviving spouses"). Bases in cents. -/
def rateSched : Nat → Filing → RateSched
  -- Rev. Proc. 2015-53 §3.01
  | 2016, .single => oldRates 9275 37650 91150 190150 413350 415050 92750 518375 1855875 4627875 11993475 12052975
  | 2016, .mfj | 2016, .qss =>
      oldRates 18550 75300 151900 231450 413350 466950 185500 1036750 2951750 5179150 11181850 13057850
  | 2016, .mfs => oldRates 9275 37650 75950 115725 206675 233475 92750 518375 1475875 2589575 5590925 6528925
  | 2016, .hoh => oldRates 13250 50400 130150 210800 413350 441000 132500 689750 2683500 4941700 11625850 12593600
  -- Rev. Proc. 2016-55 §3.01
  | 2017, .single => oldRates 9325 37950 91900 191650 416700 418400 93250 522625 1871375 4664375 12091025 12150525
  | 2017, .mfj | 2017, .qss =>
      oldRates 18650 75900 153100 233350 416700 470700 186500 1045250 2975250 5222250 11272800 13162800
  | 2017, .mfs => oldRates 9325 37950 76550 116675 208350 235350 93250 522625 1487625 2611125 5636400 6581400
  | 2017, .hoh => oldRates 13350 50800 131200 212500 416700 444550 133500 695250 2705250 4981650 11720250 12695000
  -- Rev. Proc. 2018-18 §3.01
  | 2018, .single => tcjaRates 9525 38700 82500 157500 200000 500000 95250 445350 1408950 3208950 4568950 15068950
  | 2018, .mfj | 2018, .qss =>
      tcjaRates 19050 77400 165000 315000 400000 600000 190500 890700 2817900 6417900 9137900 16137900
  | 2018, .mfs => tcjaRates 9525 38700 82500 157500 200000 300000 95250 445350 1408950 3208950 4568950 8068950
  | 2018, .hoh => tcjaRates 13600 51800 82500 157500 200000 500000 136000 594400 1269800 3069800 4429800 14929800
  -- Rev. Proc. 2018-57 §3.01
  | 2019, .single => tcjaRates 9700 39475 84200 160725 204100 510300 97000 454300 1438250 3274850 4662850 15379850
  | 2019, .mfj | 2019, .qss =>
      tcjaRates 19400 78950 168400 321450 408200 612350 194000 908600 2876500 6549700 9325700 16470950
  | 2019, .mfs => tcjaRates 9700 39475 84200 160725 204100 306175 97000 454300 1438250 3274850 4662850 8235475
  | 2019, .hoh => tcjaRates 13850 52850 84200 160700 204100 510300 138500 606500 1296200 3132200 4521000 15238000
  -- Rev. Proc. 2019-44 §3.01
  | 2020, .single => tcjaRates 9875 40125 85525 163300 207350 518400 98750 461750 1460550 3327150 4736750 15623500
  | 2020, .mfj | 2020, .qss =>
      tcjaRates 19750 80250 171050 326600 414700 622050 197500 923500 2921100 6654300 9473500 16730750
  | 2020, .mfs => tcjaRates 9875 40125 85525 163300 207350 311025 98750 461750 1460550 3327150 4736750 8365375
  | 2020, .hoh => tcjaRates 14100 53700 85500 163300 207350 518400 141000 616200 1315800 3183000 4592600 15479350
  -- Rev. Proc. 2020-45 §3.01
  | 2021, .single => tcjaRates 9950 40525 86375 164925 209425 523600 99500 466400 1475100 3360300 4784300 15780425
  | 2021, .mfj | 2021, .qss =>
      tcjaRates 19900 81050 172750 329850 418850 628300 199000 932800 2950200 6720600 9568600 16899350
  | 2021, .mfs => tcjaRates 9950 40525 86375 164925 209425 314150 99500 466400 1475100 3360300 4784300 8449675
  | 2021, .hoh => tcjaRates 14200 54200 86350 164900 209400 523600 142000 622000 1329300 3214500 4638500 15635500
  -- Rev. Proc. 2021-45 §3.01
  | 2022, .single => tcjaRates 10275 41775 89075 170050 215950 539900 102750 480750 1521350 3464750 4933550 16271800
  | 2022, .mfj | 2022, .qss =>
      tcjaRates 20550 83550 178150 340100 431900 647850 205500 961500 3042700 6929500 9867100 17425350
  | 2022, .mfs => tcjaRates 10275 41775 89075 170050 215950 323925 102750 480750 1521350 3464750 4933550 8712675
  | 2022, .hoh => tcjaRates 14650 55900 89050 170050 215950 539900 146500 641500 1370800 3314800 4783600 16121850
  -- Rev. Proc. 2022-38 §3.01
  | 2023, .single => tcjaRates 11000 44725 95375 182100 231250 578125 110000 514700 1629000 3710400 5283200 17423825
  | 2023, .mfj | 2023, .qss =>
      tcjaRates 22000 89450 190750 364200 462500 693750 220000 1029400 3258000 7420800 10566400 18660150
  | 2023, .mfs => tcjaRates 11000 44725 95375 182100 231250 346875 110000 514700 1629000 3710400 5283200 9330075
  | 2023, .hoh => tcjaRates 15700 59850 95350 182100 231250 578100 157000 686800 1467800 3549800 5122600 17262350
  -- Rev. Proc. 2023-34 §3.01
  | 2024, .single => tcjaRates 11600 47150 100525 191950 243725 609350 116000 542600 1716850 3911050 5567850 18364725
  | 2024, .mfj | 2024, .qss =>
      tcjaRates 23200 94300 201050 383900 487450 731200 232000 1085200 3433700 7822100 11135700 19666950
  | 2024, .mfs => tcjaRates 11600 47150 100525 191950 243725 365600 116000 542600 1716850 3911050 5567850 9833475
  | 2024, .hoh => tcjaRates 16550 63100 100500 191950 243700 609350 165500 724100 1546900 3741700 5397700 18195450
  | _, _ => tcjaRates 1 2 3 4 5 6 10 34 254 494 814 1164  -- outside 2016–2024: never used (see `Params.valid`)

/-- The years this library covers. -/
def years : List Nat := [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
def filings : List Filing := [.single, .mfj, .mfs, .hoh, .qss]

/-- **Every printed base amount in the nine revenue procedures' Tables 1–4 is the exact tax at the top of the row
before.** A typo in any of the 216 printed bases or 216 bracket tops would make this fail. -/
theorem rateSched_ok : ∀ y ∈ years, ∀ f ∈ filings, (rateSched y f).Ok := by decide

/-! ## Everything else that changes by year -/

deriving instance Inhabited for TaxCode.Individual.D.EicParams

/-- §24 parameters for one year. -/
structure CtcParams where
  perChild : Int          -- §24(a) / (h)(2)
  perOther : Int          -- §24(h)(4) credit for other dependents (0 before 2018)
  thrJoint : Int          -- §24(b)(2) / (h)(3) threshold amounts
  thrOther : Int
  thrMfs : Int
  refundCap : Int         -- §24(h)(5) per-child cap on the refundable part (0 = no cap: 2016–2017)
  earnedFloor : Int       -- §24(d)(1)(B)(i) ($3,000 before 2018; $2,500 by §24(h)(6))
  ssnForChild : Bool      -- §24(h)(7) (2018–2025): a child without an SSN gets only the $500
  deriving Repr, Inhabited

def oldCtc : CtcParams := ⟨1000, 0, 110000, 75000, 55000, 0, 3000, false⟩
def tcjaCtc (cap : Int) : CtcParams := ⟨2000, 500, 400000, 200000, 200000, cap, 2500, true⟩

structure Params where
  year : Nat
  /-- §63(c)(2) basic standard deduction. -/
  stdJoint : Int
  stdHoh : Int
  stdSingle : Int            -- also married filing separately
  /-- §63(f): additional amount for the aged or blind (married / unmarried and not a surviving spouse). -/
  addlMarried : Int
  addlUnmarried : Int
  /-- §63(c)(5): a dependent's basic standard deduction is at most the greater of `depMin` and earned income plus
  `depAddon`. -/
  depMin : Int
  depAddon : Int
  /-- §151(d) personal exemption amount (zero 2018–2025 by §151(d)(5)(A)). -/
  exemption : Int
  /-- The exemption amount used in the §152(d)(1)(B) gross-income test (Notice 2018-70; indexed). -/
  exemption152d : Int
  /-- §151(d)(3) phase-out threshold amounts (2016–2017 only; 0 = no phase-out): joint, HoH, unmarried, separate. -/
  pepJoint : Int
  pepHoh : Int
  pepSingle : Int
  pepMfs : Int
  /-- §1(h)(1)(B)/(C) (2016–2017) or §1(j)(5)(B) (2018+): the maximum zero-rate and 15%-rate amounts. -/
  cg0Joint : Int
  cg0Hoh : Int
  cg0Single : Int
  cg0Mfs : Int
  cg15Joint : Int
  cg15Hoh : Int
  cg15Single : Int
  cg15Mfs : Int
  /-- §32(b) by number of qualifying children (0, 1, 2, 3+). -/
  eic0 : TaxCode.Individual.D.EicParams
  eic1 : TaxCode.Individual.D.EicParams
  eic2 : TaxCode.Individual.D.EicParams
  eic3 : TaxCode.Individual.D.EicParams
  /-- §32(i)(1) disqualified-income limit. -/
  eicInvLimit : Int
  ctc : CtcParams
  /-- SSA §230 contribution and benefit base, read by §1402(b)(1) and §3121(a)(1). -/
  ssWageBase : Int
  /-- §6651(a) flush language: the minimum addition for a return more than 60 days late (by the year the return is
  required to be filed, i.e. `year + 1`). -/
  ftfMinimum : Int
  /-- §213(a) floor (basis points of AGI) for the year, read by §72(t)(2)(B). -/
  medicalFloorBp : Int
  /-- Return due date (§6072(a), moved by §7503 or postponed under §7508A), and the extended due date (§6081). -/
  dueDate : Date
  extendedDueDate : Date
  deriving Repr, Inhabited

open TaxCode.Individual.D in
/-- The parameters for tax year `y`, or `none` outside 2016–2024. -/
def params? : Nat → Option Params
  | 2016 => some {
      year := 2016
      -- Rev. Proc. 2015-53 §3.14(1)-(3)
      stdJoint := 12600, stdHoh := 9300, stdSingle := 6300, addlMarried := 1250, addlUnmarried := 1550
      depMin := 1050, depAddon := 350
      -- §3.24: $4,050; phase-out begins $311,300 / $285,350 / $259,400 / $155,650
      exemption := 4050, exemption152d := 4050
      pepJoint := 311300, pepHoh := 285350, pepSingle := 259400, pepMfs := 155650
      -- §1(h)(1)(B)-(C) before 2018: the 0% rate reaches the top of the 15% bracket and the 15% rate the top of the
      -- 35% bracket (Rev. Proc. 2015-53 Tables 1-4)
      cg0Joint := 75300, cg0Hoh := 50400, cg0Single := 37650, cg0Mfs := 37650
      cg15Joint := 466950, cg15Hoh := 441000, cg15Single := 415050, cg15Mfs := 233475
      -- §3.06(1)-(2)
      eic0 := ⟨765, 765, 6610, 8270, 13820, 506, 14880, 20430⟩
      eic1 := ⟨3400, 1598, 9920, 18190, 23740, 3373, 39296, 44846⟩
      eic2 := ⟨4000, 2106, 13930, 18190, 23740, 5572, 44648, 50198⟩
      eic3 := ⟨4500, 2106, 13930, 18190, 23740, 6269, 47955, 53505⟩
      eicInvLimit := 3400
      -- §24 as in force before Pub. L. 115-97; §3.04: the §24(d)(1)(B)(i) amount is $3,000
      ctc := oldCtc
      ssWageBase := 118500
      -- Pub. L. 114-125 §921 ($205 for returns due after 2015), stated in Rev. Proc. 2016-55 §2.
      -- (Rev. Proc. 2015-53 §3.43's $135 predates that Act.)
      ftfMinimum := 205
      -- §213(a) 10%; §213(f) kept 7.5% for 2016 if either spouse was 65 (handled in EarlyDistribution)
      medicalFloorBp := 1000
      -- 15 Apr 2017 a Saturday, Emancipation Day observed Mon 17 Apr: due Tue 18 Apr 2017; extended to Mon 16 Oct
      dueDate := ⟨2017, 4, 18⟩, extendedDueDate := ⟨2017, 10, 16⟩ }
  | 2017 => some {
      year := 2017
      -- Rev. Proc. 2016-55 §3.14, §3.24
      stdJoint := 12700, stdHoh := 9350, stdSingle := 6350, addlMarried := 1250, addlUnmarried := 1550
      depMin := 1050, depAddon := 350
      exemption := 4050, exemption152d := 4050
      pepJoint := 313800, pepHoh := 287650, pepSingle := 261500, pepMfs := 156900
      cg0Joint := 75900, cg0Hoh := 50800, cg0Single := 37950, cg0Mfs := 37950
      cg15Joint := 470700, cg15Hoh := 444550, cg15Single := 418400, cg15Mfs := 235350
      -- §3.05
      eic0 := ⟨765, 765, 6670, 8340, 13930, 510, 15010, 20600⟩
      eic1 := ⟨3400, 1598, 10000, 18340, 23930, 3400, 39617, 45207⟩
      eic2 := ⟨4000, 2106, 14040, 18340, 23930, 5616, 45007, 50597⟩
      eic3 := ⟨4500, 2106, 14040, 18340, 23930, 6318, 48340, 53930⟩
      eicInvLimit := 3450
      ctc := oldCtc
      ssWageBase := 127200
      -- Rev. Proc. 2016-55 §3.46: $210 for tax years beginning in 2017
      ftfMinimum := 210
      -- §213(f) as amended by Pub. L. 115-97 §11027: 7.5% for 2017 and 2018
      medicalFloorBp := 750
      -- 15 Apr 2018 a Sunday, Emancipation Day Mon 16 Apr: due Tue 17 Apr 2018; extended Mon 15 Oct 2018
      dueDate := ⟨2018, 4, 17⟩, extendedDueDate := ⟨2018, 10, 15⟩ }
  | 2018 => some {
      year := 2018
      -- Rev. Proc. 2018-18 §3.14, §3.24 (exemption $0); §152(d)(1)(B) $4,150 (Notice 2018-70, Rev. Proc. 2018-57 §2.03)
      stdJoint := 24000, stdHoh := 18000, stdSingle := 12000, addlMarried := 1300, addlUnmarried := 1600
      depMin := 1050, depAddon := 350
      exemption := 0, exemption152d := 4150
      pepJoint := 0, pepHoh := 0, pepSingle := 0, pepMfs := 0
      -- §1(j)(5)(B) as enacted (2018 figures in the statute; separate = one-half of joint)
      cg0Joint := 77200, cg0Hoh := 51700, cg0Single := 38600, cg0Mfs := 38600
      cg15Joint := 479000, cg15Hoh := 452400, cg15Single := 425800, cg15Mfs := 239500
      -- Rev. Proc. 2018-18 §3.05
      eic0 := ⟨765, 765, 6780, 8490, 14170, 519, 15270, 20950⟩
      eic1 := ⟨3400, 1598, 10180, 18660, 24350, 3461, 40320, 46010⟩
      eic2 := ⟨4000, 2106, 14290, 18660, 24350, 5716, 45802, 51492⟩
      eic3 := ⟨4500, 2106, 14290, 18660, 24350, 6431, 49194, 54884⟩
      eicInvLimit := 3500
      -- §24(h)(5) "$1,400" (its indexing, also in §24(h)(5), starts after 2018: Rev. Proc. 2018-57 §2.02)
      ctc := tcjaCtc 1400
      ssWageBase := 128400
      -- Rev. Proc. 2017-58 §3.46: $215 for returns required to be filed in 2019
      ftfMinimum := 215
      medicalFloorBp := 750
      -- due Mon 15 Apr 2019 (Maine and Massachusetts residents 17 Apr); extended Tue 15 Oct 2019
      dueDate := ⟨2019, 4, 15⟩, extendedDueDate := ⟨2019, 10, 15⟩ }
  | 2019 => some {
      year := 2019
      -- Rev. Proc. 2018-57 §3.16, §3.25 ($4,200), §3.03
      stdJoint := 24400, stdHoh := 18350, stdSingle := 12200, addlMarried := 1300, addlUnmarried := 1650
      depMin := 1100, depAddon := 350
      exemption := 0, exemption152d := 4200
      pepJoint := 0, pepHoh := 0, pepSingle := 0, pepMfs := 0
      cg0Joint := 78750, cg0Hoh := 52750, cg0Single := 39375, cg0Mfs := 39375
      cg15Joint := 488850, cg15Hoh := 461700, cg15Single := 434550, cg15Mfs := 244425
      -- §3.07
      eic0 := ⟨765, 765, 6920, 8650, 14450, 529, 15570, 21370⟩
      eic1 := ⟨3400, 1598, 10370, 19030, 24820, 3526, 41094, 46884⟩
      eic2 := ⟨4000, 2106, 14570, 19030, 24820, 5828, 46703, 52493⟩
      eic3 := ⟨4500, 2106, 14570, 19030, 24820, 6557, 50162, 55952⟩
      eicInvLimit := 3600
      -- §3.05: $1,400
      ctc := tcjaCtc 1400
      ssWageBase := 132900
      -- Pub. L. 116-94 div. O §402: $435 for returns due (with extensions) after 31 Dec 2019 (Rev. Proc. 2020-45 §2)
      ftfMinimum := 435
      medicalFloorBp := 750
      -- postponed to Wed 15 Jul 2020 (Notice 2020-23, §7508A); extended Thu 15 Oct 2020
      dueDate := ⟨2020, 7, 15⟩, extendedDueDate := ⟨2020, 10, 15⟩ }
  | 2020 => some {
      year := 2020
      -- Rev. Proc. 2019-44 §3.16, §3.25 ($4,300), §3.03
      stdJoint := 24800, stdHoh := 18650, stdSingle := 12400, addlMarried := 1300, addlUnmarried := 1650
      depMin := 1100, depAddon := 350
      exemption := 0, exemption152d := 4300
      pepJoint := 0, pepHoh := 0, pepSingle := 0, pepMfs := 0
      cg0Joint := 80000, cg0Hoh := 53600, cg0Single := 40000, cg0Mfs := 40000
      cg15Joint := 496600, cg15Hoh := 469050, cg15Single := 441450, cg15Mfs := 248300
      -- §3.07
      eic0 := ⟨765, 765, 7030, 8790, 14680, 538, 15820, 21710⟩
      eic1 := ⟨3400, 1598, 10540, 19330, 25220, 3584, 41756, 47646⟩
      eic2 := ⟨4000, 2106, 14800, 19330, 25220, 5920, 47440, 53330⟩
      eic3 := ⟨4500, 2106, 14800, 19330, 25220, 6660, 50954, 56844⟩
      eicInvLimit := 3650
      ctc := tcjaCtc 1400
      ssWageBase := 137700
      -- Pub. L. 116-94 div. O §402 ($435); Rev. Proc. 2020-45 §2
      ftfMinimum := 435
      medicalFloorBp := 750
      -- postponed to Mon 17 May 2021 (Notice 2021-21); extended Fri 15 Oct 2021
      dueDate := ⟨2021, 5, 17⟩, extendedDueDate := ⟨2021, 10, 15⟩ }
  | 2021 => some {
      year := 2021
      -- Rev. Proc. 2020-45 §3.16, §3.25 ($4,300), §3.03
      stdJoint := 25100, stdHoh := 18800, stdSingle := 12550, addlMarried := 1350, addlUnmarried := 1700
      depMin := 1100, depAddon := 350
      exemption := 0, exemption152d := 4300
      pepJoint := 0, pepHoh := 0, pepSingle := 0, pepMfs := 0
      cg0Joint := 80800, cg0Hoh := 54100, cg0Single := 40400, cg0Mfs := 40400
      cg15Joint := 501600, cg15Hoh := 473750, cg15Single := 445850, cg15Mfs := 250800
      -- childless: §32(n) (ARPA §9621): 15.3%, earned income amount $9,820, phaseout amount $11,610; joint adds the
      -- indexed §32(b)(2)(B) amount $5,950 (Rev. Proc. 2020-45: $25,470 − $19,520), so $17,560: the completed
      -- phase-out is $21,430 / $27,380 (Pub. 596 (2021)) = threshold + $9,820, and the 2021 EIC Table shows the full
      -- $1,502 on the joint $17,550–17,600 line. (Rev. Proc. 2020-45's pre-ARPA childless joint gap was $5,940.)
      -- Max $1,502. With children: Rev. Proc. 2020-45 §3.07.
      eic0 := ⟨1530, 1530, 9820, 11610, 17560, 1502, 21430, 27380⟩
      eic1 := ⟨3400, 1598, 10640, 19520, 25470, 3618, 42158, 48108⟩
      eic2 := ⟨4000, 2106, 14950, 19520, 25470, 5980, 47915, 53865⟩
      eic3 := ⟨4500, 2106, 14950, 19520, 25470, 6728, 51464, 57414⟩
      -- §32(i)(1) as amended by ARPA §9624: $10,000 (Rev. Proc. 2020-45's $3,650 superseded)
      eicInvLimit := 10000
      -- §24(i) (ARPA §9611) governs 2021; these are the §24(h) values it modifies
      ctc := tcjaCtc 1400
      ssWageBase := 142800
      -- Rev. Proc. 2020-45 §3.52: $435 for returns required to be filed in 2022
      ftfMinimum := 435
      medicalFloorBp := 750
      -- 15 Apr 2022 Emancipation Day observed: due Mon 18 Apr 2022; extended Mon 17 Oct 2022
      dueDate := ⟨2022, 4, 18⟩, extendedDueDate := ⟨2022, 10, 17⟩ }
  | 2022 => some {
      year := 2022
      -- Rev. Proc. 2021-45 §3.15, §3.24 ($4,400), §3.03
      stdJoint := 25900, stdHoh := 19400, stdSingle := 12950, addlMarried := 1400, addlUnmarried := 1750
      depMin := 1150, depAddon := 400
      exemption := 0, exemption152d := 4400
      pepJoint := 0, pepHoh := 0, pepSingle := 0, pepMfs := 0
      cg0Joint := 83350, cg0Hoh := 55800, cg0Single := 41675, cg0Mfs := 41675
      cg15Joint := 517200, cg15Hoh := 488500, cg15Single := 459750, cg15Mfs := 258600
      -- §3.06
      eic0 := ⟨765, 765, 7320, 9160, 15290, 560, 16480, 22610⟩
      eic1 := ⟨3400, 1598, 10980, 20130, 26260, 3733, 43492, 49622⟩
      eic2 := ⟨4000, 2106, 15410, 20130, 26260, 6164, 49399, 55529⟩
      eic3 := ⟨4500, 2106, 15410, 20130, 26260, 6935, 53057, 59187⟩
      eicInvLimit := 10300
      -- §3.05: $1,500
      ctc := tcjaCtc 1500
      ssWageBase := 147000
      -- Rev. Proc. 2021-45 §3.52: $450 for returns required to be filed in 2023
      ftfMinimum := 450
      medicalFloorBp := 750
      -- 15 Apr 2023 a Saturday, Emancipation Day observed Mon 17 Apr: due Tue 18 Apr 2023; extended Mon 16 Oct 2023
      dueDate := ⟨2023, 4, 18⟩, extendedDueDate := ⟨2023, 10, 16⟩ }
  | 2023 => some {
      year := 2023
      -- Rev. Proc. 2022-38 §3.15, §3.24 ($4,700), §3.03
      stdJoint := 27700, stdHoh := 20800, stdSingle := 13850, addlMarried := 1500, addlUnmarried := 1850
      depMin := 1250, depAddon := 400
      exemption := 0, exemption152d := 4700
      pepJoint := 0, pepHoh := 0, pepSingle := 0, pepMfs := 0
      cg0Joint := 89250, cg0Hoh := 59750, cg0Single := 44625, cg0Mfs := 44625
      cg15Joint := 553850, cg15Hoh := 523050, cg15Single := 492300, cg15Mfs := 276900
      -- §3.06
      eic0 := ⟨765, 765, 7840, 9800, 16370, 600, 17640, 24210⟩
      eic1 := ⟨3400, 1598, 11750, 21560, 28120, 3995, 46560, 53120⟩
      eic2 := ⟨4000, 2106, 16510, 21560, 28120, 6604, 52918, 59478⟩
      eic3 := ⟨4500, 2106, 16510, 21560, 28120, 7430, 56838, 63398⟩
      eicInvLimit := 11000
      -- §3.05: $1,600
      ctc := tcjaCtc 1600
      ssWageBase := 160200
      -- Rev. Proc. 2022-38 §3.52: $485 for returns required to be filed in 2024
      ftfMinimum := 485
      medicalFloorBp := 750
      -- due Mon 15 Apr 2024; extended Tue 15 Oct 2024
      dueDate := ⟨2024, 4, 15⟩, extendedDueDate := ⟨2024, 10, 15⟩ }
  | 2024 => some {
      year := 2024
      -- Rev. Proc. 2023-34 §3.15, §3.24 ($5,050), §3.03
      stdJoint := 29200, stdHoh := 21900, stdSingle := 14600, addlMarried := 1550, addlUnmarried := 1950
      depMin := 1300, depAddon := 450
      exemption := 0, exemption152d := 5050
      pepJoint := 0, pepHoh := 0, pepSingle := 0, pepMfs := 0
      cg0Joint := 94050, cg0Hoh := 63000, cg0Single := 47025, cg0Mfs := 47025
      cg15Joint := 583750, cg15Hoh := 551350, cg15Single := 518900, cg15Mfs := 291850
      -- §3.06
      eic0 := ⟨765, 765, 8260, 10330, 17250, 632, 18591, 25511⟩
      eic1 := ⟨3400, 1598, 12390, 22720, 29640, 4213, 49084, 56004⟩
      eic2 := ⟨4000, 2106, 17400, 22720, 29640, 6960, 55768, 62688⟩
      eic3 := ⟨4500, 2106, 17400, 22720, 29640, 7830, 59899, 66819⟩
      eicInvLimit := 11600
      -- §3.05: $1,700
      ctc := tcjaCtc 1700
      ssWageBase := 168600
      -- Rev. Proc. 2023-34 §3.53: $510 (the text says "filed in 2024"; the figure is the one for returns filed in
      -- 2025: Rev. Proc. 2022-38 had already set $485 for 2024)
      ftfMinimum := 510
      medicalFloorBp := 750
      -- due Tue 15 Apr 2025; extended Wed 15 Oct 2025
      dueDate := ⟨2025, 4, 15⟩, extendedDueDate := ⟨2025, 10, 15⟩ }
  | _ => none

/-- The schedule for a year's parameters. -/
def Params.sched (p : Params) (f : Filing) : RateSched := rateSched p.year f

def Params.eic (p : Params) : Nat → TaxCode.Individual.D.EicParams
  | 0 => p.eic0
  | 1 => p.eic1
  | 2 => p.eic2
  | _ => p.eic3

def Params.basicStd (p : Params) : Filing → Int
  | .mfj | .qss => p.stdJoint
  | .hoh => p.stdHoh
  | _ => p.stdSingle

def Params.cg0 (p : Params) : Filing → Int
  | .mfj | .qss => p.cg0Joint
  | .hoh => p.cg0Hoh
  | .mfs => p.cg0Mfs
  | .single => p.cg0Single

def Params.cg15 (p : Params) : Filing → Int
  | .mfj | .qss => p.cg15Joint
  | .hoh => p.cg15Hoh
  | .mfs => p.cg15Mfs
  | .single => p.cg15Single

def Params.pepThreshold (p : Params) : Filing → Int
  | .mfj | .qss => p.pepJoint
  | .hoh => p.pepHoh
  | .mfs => p.pepMfs
  | .single => p.pepSingle

/-- All nine years are present, each labelled with its own year. -/
theorem params_years : ∀ y ∈ years, (params? y).map (·.year) = some y := by decide

/-! ## Consistency checks on the printed EIC figures (every year, every column) -/

open TaxCode.Individual.D in
/-- The printed "maximum amount of credit" is the credit percentage times the earned income amount, rounded to the
nearest dollar. -/
def eicMaxOk (p : EicParams) : Bool := roundDollar (p.cp * p.eia) 10000 == p.maxCredit

open TaxCode.Individual.D in
/-- The printed "completed phaseout amount" is within $3 of threshold + maximum ÷ phase-out percentage (computed from
the rounded or the unrounded maximum: the 2021 childless column uses the unrounded one). -/
def eicCompletedOk (p : EicParams) (joint : Bool) : Bool :=
  let co := p.co joint
  let thr := p.thr joint
  (co * p.pp - (thr * p.pp + 10000 * p.maxCredit)).natAbs ≤ 3 * p.pp ||
  (co * p.pp - (thr * p.pp + p.cp * p.eia)).natAbs ≤ 3 * p.pp

def allEicParams : List TaxCode.Individual.D.EicParams :=
  years.flatMap fun y => match params? y with
    | some p => [p.eic0, p.eic1, p.eic2, p.eic3]
    | none => []

theorem eic_max_consistent : allEicParams.all eicMaxOk = true := by decide
theorem eic_completed_consistent :
    allEicParams.all (fun p => eicCompletedOk p false && eicCompletedOk p true) = true := by decide

end Legal.USTax.TaxCourt
