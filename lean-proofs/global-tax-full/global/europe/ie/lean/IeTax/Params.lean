import TaxKernel

/-!
# Ireland 2025: every number the model uses, with the provision that fixes it

Money is in **cents** (`Int`): Irish income tax, USC and PRSI are computed to the cent (Revenue's own examples,
e.g. TDM Part 18D-00-01 para. 4.1 "12,012 x 0.5% = 60.06"; the PRSI credit is "one-sixth of the difference between
the reckonable earnings ... and €352.01"). Rates are basis points. Year of assessment = calendar 2025 (TCA 1997
s. 2: a year of assessment begins on 1 January).

Sources (all official):
* TCA = Taxes Consolidation Act 1997. There is no free official consolidated text of the TCA (it is not among the
  Law Reform Commission's Revised Acts, so it is not in Global law either); the amounts below are taken from the
  amending act as enacted, **Finance Act 2024 (No. 43 of 2024) ss. 2-3** ("As respects the year of assessment
  2025"), https://www.irishstatutebook.ie/eli/2024/act/43/enacted/en/print.html (saved `refs/fa2024.txt`), and the
  structure from Revenue's *Notes for Guidance - TCA 1997 - Finance Act 2025 edition* (Parts 2, 7, 15, 18D, 30;
  https://www.revenue.ie/en/tax-professionals/documents/notes-for-guidance/tca/partNN.pdf, saved `refs/nfg/`),
  cross-checked with Revenue's "Tax rates, bands and reliefs" chart (columns 2022-2026,
  https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx, `refs/rev/`).
* SWCA = Social Welfare Consolidation Act 2005, Law Reform Commission revised act updated to 21 January 2026
  (Global law `ireland/national/acts/social-welfare-consolidation-act-2005`; official PDF
  https://rev-acts.s3.eu-west-1.amazonaws.com/2005/26/act_new.pdf, `refs/swca_rev.txt`), with the dated rate
  substitutions of the **Social Welfare (Miscellaneous Provisions) Act 2024 (No. 24 of 2024) s. 3 and Table**
  (https://www.irishstatutebook.ie/eli/2024/act/24/enacted/en/print.html) and the **Social Welfare Act 2024
  (No. 36 of 2024) s. 13** (working family payment thresholds from 2 January 2025,
  https://www.irishstatutebook.ie/eli/2024/act/36/enacted/en/print.html).
-/

namespace IeTax

/-- Euro to cents. -/
def eur (x : Int) : Int := 100 * x

/-! ## Income tax: rate bands (TCA s. 15 and its Table, substituted by FA 2024 s. 3(a)(ii)) -/

/-- Table Part 1: "The first €44,000 - 20 per cent - the standard rate; The remainder - 40 per cent". -/
def bandSingle : Int := eur 44000
/-- Table Part 2 (an individual entitled to the single person child carer credit, s. 462B): "The first €48,000". -/
def bandSPCC : Int := eur 48000
/-- Table Part 3 (married / civil partners assessed under s. 1017 / 1031C): "The first €53,000". -/
def bandMarried : Int := eur 53000
/-- s. 15(3) as amended by FA 2024 s. 3(a)(i) ("€35,000" for "€33,000"): the Part 3 band is increased by the lesser
of €35,000 and the specified income of the spouse with the lower income (notes for guidance, Part 2, s. 15(3)). -/
def bandIncreaseCap : Int := eur 35000
/-- s. 15 Table: "20 per cent - the standard rate", "40 per cent - the higher rate". -/
def standardRate : Int := 2000
def higherRate : Int := 4000

/-! ## Personal tax credits (Part 15), FA 2024 s. 3(b)-(i) -/

/-- s. 461(a)/(b): €4,000 (married jointly assessed, or widowed in the year of bereavement); s. 461(c): €2,000. -/
def basicCreditMarried : Int := eur 4000
def basicCreditSingle : Int := eur 2000
/-- s. 462B(3): single person child carer credit €1,900 (FA 2024 s. 3(c)). -/
def spccCredit : Int := eur 1900
/-- s. 464: age tax credit €490 (married, jointly assessed) / €245 (any other case), for 65 or over at any time in
the year (notes for guidance Part 15, s. 464; not changed by FA 2024). -/
def ageCreditMarried : Int := eur 490
def ageCreditSingle : Int := eur 245
def ageCreditAge : Nat := 65
/-- s. 466A(2): home carer tax credit €1,950 (FA 2024 s. 3(f)); s. 466A(6): reduced by one half of the carer
spouse's income above €7,200; s. 466A(8): not together with the s. 15(3) band increase ("opt for whichever is the
more beneficial"). -/
def homeCarerCredit : Int := eur 1950
def homeCarerIncomeLimit : Int := eur 7200
/-- s. 472(4): employee tax credit, the lesser of €2,000 and the standard rate on the emoluments (FA 2024 s. 3(h)). -/
def employeeCredit : Int := eur 2000
/-- s. 472AB(2): earned income tax credit, lesser of €2,000 and 20 % of qualifying earned income; s. 472AB(3): with
the employee credit not more than €2,000 for one individual's income (FA 2024 s. 3(i)). -/
def earnedIncomeCredit : Int := eur 2000

/-! ## Age exemption (s. 188) -/
/-- s. 188(2): exemption limits €18,000 (single) and €36,000 (married, jointly assessed, either spouse 65+). -/
def ageExemptSingle : Int := eur 18000
def ageExemptMarried : Int := eur 36000
/-- s. 188(2A): increased by €575 for each of the first 2 qualifying children and €830 for each later one. -/
def ageExemptChild12 : Int := eur 575
def ageExemptChild3 : Int := eur 830
/-- s. 188(5): marginal relief, tax limited to 40 per cent of the excess of total income over the exemption
limit, while total income does not exceed twice the limit. -/
def ageMarginalRate : Int := 4000

/-! ## Deposit interest (DIRT) and capital gains -/
/-- s. 256(1) "appropriate tax": 33 % for interest paid in 2025; s. 261(c): for an individual the DIRT is the final
income tax on the interest (notes for guidance Part 8, ss. 256, 261). -/
def dirtRate : Int := 3300
/-- TCA s. 28(3): CGT rate 33 %; s. 601(1): annual exemption €1,270 per individual (each spouse their own). -/
def cgtRate : Int := 3300
def cgtExemption : Int := eur 1270

/-! ## Pension contributions (Part 30): age-related limits (s. 774(7)(c), s. 787(8)) and the earnings cap (s. 790A) -/
/-- Under 30: 15 %; to 39: 20 %; to 49: 25 %; to 54: 30 %; to 59: 35 %; 60 or older: 40 % (notes Part 30 s. 774(7)(c)). -/
def pensionPct (age : Nat) : Int :=
  if age < 30 then 1500 else if age < 40 then 2000 else if age < 50 then 2500
  else if age < 55 then 3000 else if age < 60 then 3500 else 4000
/-- s. 790A: the "earnings limit" €115,000. -/
def pensionEarningsCap : Int := eur 115000

/-! ## Universal social charge (Part 18D) -/
/-- s. 531AM(2): no USC if aggregate income "does not exceed €13,000"; above it the whole income is chargeable. -/
def uscExempt : Int := eur 13000
/-- s. 531AN Table Part 1 (FA 2024 s. 2(1)(b)), 2025: first €12,012 at 0.5 %, next €15,370 at 2 %, next €42,662 at
3 %, the remainder at 8 %. -/
def usc1 : Int := eur 12012
def usc2 : Int := eur 15370
def usc3 : Int := eur 42662
def uscSchedule : TaxKernel.Schedule :=
  TaxKernel.Schedule.ofList [(0, 50), (usc1, 200), (usc1 + usc2, 300), (usc1 + usc2 + usc3, 800)]
/-- s. 531AN(1) and Table Part 2: aged 70 or over with aggregate income not over €60,000: 0.5 % on the first
€12,012, 2 % on the remainder. -/
def uscReducedLimit : Int := eur 60000
def uscReducedAge : Nat := 70
def uscReducedSchedule : TaxKernel.Schedule := TaxKernel.Schedule.ofList [(0, 50), (usc1, 200)]
/-- s. 531AN(3) amount for 2025 (FA 2024 s. 2(1)(a): "€27,382" for "€25,760"): full medical card holders under 70
pay no more than 2 % above it. It must equal the end of the 2 % band (usc1 + usc2); see `Theorems.usc_medical_card_aligned`. -/
def uscMedicalCardFrom : Int := eur 27382
/-- s. 531AN(2): relevant (non-PAYE) income above €100,000: the excess charged at 11 % instead of 8 %. -/
def uscSurchargeFrom : Int := eur 100000
def uscSurchargeRate : Int := 300

/-! ## PRSI (SWCA 2005): Class A1 employee and Class S -/
/-- SWCA s. 13(2)(a): no employee contribution where the week's reckonable earnings are "not more than €352". -/
def prsiWeeklyFloor : Int := eur 352
/-- s. 13(2)(b): earnings "more than €352 and not exceeding €424": the contribution is reduced by "the difference
between €12 and one-sixth of the difference between the reckonable earnings ... and €352.01". -/
def prsiCreditTop : Int := eur 424
def prsiCreditMax : Int := eur 12
def prsiCreditBase : Int := 35201
/-- s. 13(2)(b)(ii), (db)(ii): "4.1 per cent" from 1 October 2024, "4.2 per cent" from 1 October 2025
(SW(MP)A 2024 s. 3(1), (2), Table amendments 1 and 4, columns (4) and (5)). -/
def prsiRateJanSep : Int := 410
def prsiRateOctDec : Int := 420
/-- The model pays weekly on Fridays: 3 January to 26 December 2025 = 52 pay days, 39 before 1 October 2025 (the
first on or after it is Friday 3 October). Contribution weeks follow the pay date (SWCA s. 13(2): "in any
contribution week a payment ... is made"). -/
def payWeeks : Int := 52
def payWeeksAt41 : Int := 39
/-- SWCA s. 21(1)(a): Class S "the greater of an amount equal to 4.2 per cent of the reckonable income or the amount
of €650" (4.1 % before 1 October 2025, SW(MP)A 2024 Table amendment 9). For the 2025 contribution year the
Department of Social Protection and Revenue charge the blended 4.125 % (three quarters at 4.1 %, one at 4.2 %), as
they charged 4.025 % for 2024: a reading of an annual charge whose rate changes on 1 October (FINDINGS F3).
The rate is held as a fraction `prsiClassSNum / prsiClassSDen` = 4.125 %. -/
def prsiClassSNum : Int := 4125
def prsiClassSDen : Int := 100000
def prsiClassSMin : Int := eur 650
/-- Reckonable income below €5,000 in the year: not a self-employed contributor (SWCA Sch. 1 Pt 3 and the
Contributions Regulations; the threshold as the Department publishes it). -/
def prsiClassSThreshold : Int := eur 5000
/-- Pensionable age 66 (SWCA s. 2): no employment or self-employment contribution from then (s. 12, s. 20). -/
def prsiAgeLimit : Nat := 66

/-! ## Benefits -/
/-- SWCA s. 221(1): child benefit "a monthly benefit of €140 in respect of each qualified child" (since 1 Jan 2016,
SWPA 2015 s. 7(1)). -/
def childBenefitMonthly : Int := eur 140
/-- SWCA s. 228 (substituted by SWA 2024 s. 13, in operation from 2 January 2025): working family payment where the
weekly family income is less than €705 / €806 / €907 / €998 / €1,124 / €1,240 / €1,376 / €1,472 for 1 ... 8+
children. -/
def wfpThreshold (n : Nat) : Int :=
  match n with
  | 0 => 0 | 1 => eur 705 | 2 => eur 806 | 3 => eur 907 | 4 => eur 998 | 5 => eur 1124 | 6 => eur 1240
  | 7 => eur 1376 | _ => eur 1472
/-- SWCA s. 229(1): "60 per cent of the amount by which the weekly family income is less than" the threshold;
s. 229(2): "any fraction of €1 shall be treated as €1". -/
def wfpRate : Int := 6000
/-- s. 229(2): "where the weekly rate so calculated is below a prescribed amount, the supplement shall be payable at
the prescribed amount": €20 a week (the prescribed amount as published by INOU, https://inou.ie/information/back-to-work-supports1/working-family-payment,
and One Family, https://onefamily.ie/parenting-information/working-family-payment/; the Department's own page and
the regulation could not be retrieved by script, so this one figure rests on secondary sources). -/
def wfpMinimum : Int := eur 20

/-! ## Tax years 2022-2024 (round 2): the parameters that change by year

`YP` holds every amount that differs between 2022 and 2025; everything else above is the same in all four years
(age credit and exemption, DIRT, CGT, the USC exemption and 70+ schedule, the PRSI weekly floor and credit, child
benefit €140 a month, the WFP rate and minimum). Sources (official; irishstatutebook.ie print versions fetched
2026-11-19 and saved with sha256 in `cmp20/improve-anglo/refs/ie/`):
* 2022: **Finance Act 2021 (No. 45 of 2021)**: USC s. 531AM(3) "€21,295" for "€20,687", Table Part 1 "The next
  €9,283" at 2 per cent, then "4.5 per cent"; s. 15 Table "The first €36,800" / "The first €40,800" / "The first
  €45,800"; s. 15(3)(i) "€27,800" for "€26,300"; s. 461 "€3,400" (a), (b), "€1,700" (c); s. 472(4) "€1,700";
  s. 472AB(2), (3) "€1,700". Not amended by that Act: s. 462B €1,650, s. 466A €1,600 (Revenue, "Tax rates, bands and
  reliefs", 2022 column, saved `cmp20/anglo/ie/refs/rev/charts.txt`). WFP: **Social Welfare Act 2021 (No. 44 of
  2021)** s. 14 (s. 228: "only one child, €551", 2 children €652, 3 €753, 4 €844, 5 €970, 6 €1,086, 7 €1,222,
  8 or more €1,318).
* 2023: **Finance Act 2022 (No. 44 of 2022)**: s. 531AM(3) "€22,920" for "€21,295"; "The next €10,908"; s. 15(3)(i)
  "€31,000" for "€27,800"; Table "The first €40,000" / "€44,000" / "€49,000"; s. 461 "€3,550", "€1,775"; s. 466A(2)
  "€1,700" for "€1,600"; s. 472(4) and s. 472AB "€1,775". s. 462B €1,650 unchanged (Revenue chart 2023). WFP:
  **Social Welfare Act 2022 (No. 43 of 2022)** s. 10 (from 5 January 2023: €591, €692, €793, €884, €1,010, €1,126,
  €1,262, €1,358).
* 2024: **Finance (No. 2) Act 2023 (No. 39 of 2023)**: s. 531AM(3) "€25,760" for "€22,920"; "The next €13,748";
  "4 per cent"; s. 15(3)(i) "€33,000" for "€31,000"; Table "The first €42,000" / "€46,000" / "€51,000"; s. 461
  "€3,750", "€1,875"; s. 462B(3) "€1,750" for "€1,650"; s. 466A(2) "€1,800" for "€1,700"; s. 472(4) and s. 472AB
  "€1,875". WFP: **Social Welfare Act 2023 (No. 37 of 2023)** s. 14 (from 4 January 2024: €645, €746, €847, €938,
  €1,064, €1,180, €1,316, €1,412).
* USC bands of every year also as Revenue publishes them ("Standard rates and thresholds of USC for 2022 / 2023 /
  2024", saved `cmp20/anglo/ie/refs/rev/usc_rates.txt`).
* PRSI Class A1 employee: 4 per cent in 2022, 2023 and to 30 September 2024 (SWCA s. 13(2)(b)); 4.1 per cent from
  1 October 2024 (Social Welfare (Miscellaneous Provisions) Act 2024 (No. 24 of 2024) s. 3(1) and Table, as cited
  for 2025 above). Weekly pay on Fridays: 52 pay days in 2022 (7 Jan - 30 Dec), 2023 (6 Jan - 29 Dec) and 2024
  (5 Jan - 27 Dec); in 2024 the 39 Fridays to 27 September fall before 1 October. Class S: 4 % for 2022 and 2023,
  4.025 % for 2024 (the same blended reading of an annual charge as for 2025, FINDINGS F3).
-/

structure YP where
  year : Nat
  bandSingle : Int
  bandSPCC : Int
  bandMarried : Int
  bandIncreaseCap : Int
  basicCreditMarried : Int
  basicCreditSingle : Int
  spccCredit : Int
  homeCarerCredit : Int
  employeeCredit : Int
  earnedIncomeCredit : Int
  /-- USC Table Part 1: the 0.5 % band, the 2 % band, the third band and its rate (bp); 8 % above -/
  usc1 : Int
  usc2 : Int
  usc3 : Int
  usc3Rate : Int
  /-- PRSI Class A1: rate (bp) on the first `payWeeksAtRate1` pay days, then `prsiRate2` -/
  prsiRate1 : Int
  prsiRate2 : Int
  payWeeks : Int
  payWeeksAtRate1 : Int
  /-- Class S rate as a fraction of `prsiClassSDen` -/
  prsiClassSNum : Int
  wfpThreshold : Nat → Int

def YP.uscSchedule (y : YP) : TaxKernel.Schedule :=
  TaxKernel.Schedule.ofList [(0, 50), (y.usc1, 200), (y.usc1 + y.usc2, y.usc3Rate), (y.usc1 + y.usc2 + y.usc3, 800)]

/-- 2025: the constants above. -/
def yp2025 : YP :=
  { year := 2025, bandSingle, bandSPCC, bandMarried, bandIncreaseCap, basicCreditMarried, basicCreditSingle,
    spccCredit, homeCarerCredit, employeeCredit, earnedIncomeCredit, usc1, usc2, usc3, usc3Rate := 300,
    prsiRate1 := prsiRateJanSep, prsiRate2 := prsiRateOctDec, payWeeks, payWeeksAtRate1 := payWeeksAt41,
    prsiClassSNum, wfpThreshold }

def yp2024 : YP :=
  { year := 2024, bandSingle := eur 42000, bandSPCC := eur 46000, bandMarried := eur 51000,
    bandIncreaseCap := eur 33000, basicCreditMarried := eur 3750, basicCreditSingle := eur 1875,
    spccCredit := eur 1750, homeCarerCredit := eur 1800, employeeCredit := eur 1875, earnedIncomeCredit := eur 1875,
    usc1 := eur 12012, usc2 := eur 13748, usc3 := eur 44284, usc3Rate := 400,
    prsiRate1 := 400, prsiRate2 := 410, payWeeks := 52, payWeeksAtRate1 := 39, prsiClassSNum := 4025,
    wfpThreshold := fun n => match n with
      | 0 => 0 | 1 => eur 645 | 2 => eur 746 | 3 => eur 847 | 4 => eur 938 | 5 => eur 1064 | 6 => eur 1180
      | 7 => eur 1316 | _ => eur 1412 }

def yp2023 : YP :=
  { year := 2023, bandSingle := eur 40000, bandSPCC := eur 44000, bandMarried := eur 49000,
    bandIncreaseCap := eur 31000, basicCreditMarried := eur 3550, basicCreditSingle := eur 1775,
    spccCredit := eur 1650, homeCarerCredit := eur 1700, employeeCredit := eur 1775, earnedIncomeCredit := eur 1775,
    usc1 := eur 12012, usc2 := eur 10908, usc3 := eur 47124, usc3Rate := 450,
    prsiRate1 := 400, prsiRate2 := 400, payWeeks := 52, payWeeksAtRate1 := 52, prsiClassSNum := 4000,
    wfpThreshold := fun n => match n with
      | 0 => 0 | 1 => eur 591 | 2 => eur 692 | 3 => eur 793 | 4 => eur 884 | 5 => eur 1010 | 6 => eur 1126
      | 7 => eur 1262 | _ => eur 1358 }

def yp2022 : YP :=
  { year := 2022, bandSingle := eur 36800, bandSPCC := eur 40800, bandMarried := eur 45800,
    bandIncreaseCap := eur 27800, basicCreditMarried := eur 3400, basicCreditSingle := eur 1700,
    spccCredit := eur 1650, homeCarerCredit := eur 1600, employeeCredit := eur 1700, earnedIncomeCredit := eur 1700,
    usc1 := eur 12012, usc2 := eur 9283, usc3 := eur 48749, usc3Rate := 450,
    prsiRate1 := 400, prsiRate2 := 400, payWeeks := 52, payWeeksAtRate1 := 52, prsiClassSNum := 4000,
    wfpThreshold := fun n => match n with
      | 0 => 0 | 1 => eur 551 | 2 => eur 652 | 3 => eur 753 | 4 => eur 844 | 5 => eur 970 | 6 => eur 1086
      | 7 => eur 1222 | _ => eur 1318 }

/-- The year's parameters (2022-2025); other years fall back to the nearest modelled year and the output says so. -/
def ypFor (year : Nat) : YP :=
  if year ≤ 2022 then yp2022 else if year = 2023 then yp2023 else if year = 2024 then yp2024 else yp2025

-- the 2025 instance is the constants' schedule; band ends of each year (USC 2 % band to €21,295 / €22,920 /
-- €25,760 / €27,382, the third band to €70,044 every year); the married band plus its cap = two single bands
#guard yp2025.uscSchedule.tax TaxKernel.Rule.unitDown (eur 60258) = uscSchedule.tax TaxKernel.Rule.unitDown (eur 60258)
#guard [yp2022, yp2023, yp2024, yp2025].map (fun y => (y.usc1 + y.usc2, y.usc1 + y.usc2 + y.usc3)) =
  [(eur 21295, eur 70044), (eur 22920, eur 70044), (eur 25760, eur 70044), (eur 27382, eur 70044)]
#guard [yp2022, yp2023, yp2024, yp2025].map (fun y => y.bandMarried + y.bandIncreaseCap - 2 * y.bandSingle) = [0, 0, 0, 0]

end IeTax
