import TaxKernel

/-!
# Bulgaria 2025: parameters, each with its provision and a short quotation

Money is in **stotinki** (1 лв. = 100 ст.): the statutes and the payroll compute contributions and taxes to the
stotinka (ЗДДФЛ чл. 48, ал. 8 rounds only the balance due after advance payments to the whole lev). Inputs of the
canonical household are whole leva and are multiplied by 100. Rates are basis points (`1000` = 10 %).

Sources (texts saved under `cmp20/southeast/bg/law/`):
* ЗДДФЛ = Закон за данъците върху доходите на физическите лица (ДВ 95/2006, consolidated text as amended to
  ДВ 85/2026, Ciela free zone; the 2025 wording is read from the dated amendment notes).
* ЗДБРБ 2025 = Закон за държавния бюджет на Република България за 2025 г. (ДВ 26/2025), ПЗР § 3 and чл. 64.
* ЗБДОО 2025 = Закон за бюджета на държавното обществено осигуряване за 2025 г. (ДВ 25/2025), чл. 9, 14, 15.
* ЗБНЗОК 2025 = Закон за бюджета на НЗОК за 2025 г. (ДВ 25/2025), чл. 2.
* КСО = Кодекс за социално осигуряване (NRA consolidated text 08/2026); ЗЗО = Закон за здравното осигуряване;
  ЗСПД = Закон за семейни помощи за деца; ЗКПО = Закон за корпоративното подоходно облагане.
-/

namespace BgTax
open TaxKernel

/-- 1 лв. in stotinki. -/
def LEV : Int := 100

/-! ## Personal income tax (ЗДДФЛ) -/

/-- ЗДДФЛ чл. 48, ал. 1: "общата годишна данъчна основа по чл. 17 се умножи по данъчна ставка 10 на сто". -/
def pitRate : Int := 1000

/-- ЗДДФЛ чл. 46, ал. 3: "Ставката на данъка е 5 на сто за доходите по чл. 38, ал. 1" (dividends, final tax on the
gross amount, чл. 38, ал. 2). -/
def dividendRate : Int := 500

/-- ЗДДФЛ чл. 31, ал. 1: rent "придобитият доход се намалява с 10 на сто разходи". -/
def rentExpenseRate : Int := 1000

/-- ЗДДФЛ чл. 29, ал. 1, т. 3: "с 25 на сто за доходи от упражняване на свободна професия ... или възнаграждения по
извънтрудови правоотношения" (the canonical `selfEmployment` is read as a free profession). -/
def freelanceExpenseRate : Int := 2500

/-- ЗДДФЛ чл. 29, ал. 1, т. 2, б. "б" (authors' royalties) and "г" (lawyers, notaries from 2023): 40 %. -/
def authorExpenseRate : Int := 4000

/-- ЗДДФЛ чл. 19, ал. 1: voluntary pension contributions "в общ размер до 10 на сто от сумата от годишните данъчни
основи по чл. 17". -/
def voluntaryPensionCapRate : Int := 1000

/-- ЗДДФЛ чл. 22, ал. 1, т. 1: donations "до 5 на сто" of the sum of the annual tax bases (most recipients). -/
def donationCapRate : Int := 500

/-- ЗДБРБ 2025, ПЗР § 3, ал. 1: the child relief deducted from the annual tax bases for 2025 is "1. едно ненавършило
пълнолетие дете - в размер на 6 000 лв.; 2. две ... 12 000 лв.; 3. три и повече ... 18 000 лв." (the codified
ЗДДФЛ чл. 22в, ал. 1 still reads "двеста лв. / четиристотин лв. / шестстотин лв.": see FINDINGS F-statute). -/
def childRelief : Nat → Int
  | 0 => 0
  | 1 => 6000 * LEV
  | 2 => 12000 * LEV
  | _ => 18000 * LEV

/-- The codified amounts of ЗДДФЛ чл. 22в, ал. 1 (in force since 1 Jan 2015, never amended): "двеста лв. - при едно
ненавършило пълнолетие дете; четиристотин лв. - при две ...; шестстотин лв. - при три и повече". -/
def childReliefCodified : Nat → Int
  | 0 => 0
  | 1 => 200 * LEV
  | 2 => 400 * LEV
  | _ => 600 * LEV

/-- ЗДБРБ 2025, ПЗР § 3, ал. 4: monthly advance relief through the employer: 500 / 1 000 / 1 500 лв. -/
def childReliefMonthly : Nat → Int
  | 0 => 0
  | 1 => 500 * LEV
  | 2 => 1000 * LEV
  | _ => 1500 * LEV

/-! ## Social insurance (КСО, ЗЗО, budget acts) -/

/-- ЗБДОО 2025 чл. 9: "максимален месечен размер на осигурителния доход - 3 750 лв." (1 Jan - 31 Mar) and
"- 4 130 лв." (1 Apr - 31 Dec). `m` is the month index 0..11. -/
def maxInsurable (m : Nat) : Int := if m < 3 then 3750 * LEV else 4130 * LEV

/-- ЗБДОО 2025 чл. 9: "минимален месечен размер на осигурителния доход за самоосигуряващите се лица - 933 лв."
(1 Jan - 31 Mar) and "- 1 077 лв." (1 Apr - 31 Dec). -/
def minSelfInsured (m : Nat) : Int := if m < 3 then 933 * LEV else 1077 * LEV

/-- The twelve months of 2025. -/
def months : List Nat := List.range 12

/-- Annual maximum insurable income: 3 × 3 750 + 9 × 4 130 = 48 420 лв. -/
def maxInsurableYear : Int := months.foldl (fun a m => a + maxInsurable m) 0

/-- Annual minimum for the self-insured: 3 × 933 + 9 × 1 077 = 12 492 лв. -/
def minSelfInsuredYear : Int := months.foldl (fun a m => a + minSelfInsured m) 0

/-- ПМС № 359/2024 чл. единствен, ал. 1: "минималната месечна работна заплата за страната 1077 лв." from 1 Jan 2025. -/
def minWage : Int := 1077 * LEV

/-! ## Earlier years 2022-2024 (round 2, 2026-11-19)

Texts read in the public corpus github.com/lexifina/bulgaria-law (sparse clone `refs/bglaw`, acts as promulgated):
* ЗБДОО 2022 (ДВ 18/2022, `zakon/2022/dv018-164014/art-009.md`) чл. 9: "1. от 1 януари до 31 март: ... б)
  минимален месечен размер на осигурителния доход за самоосигуряващите се лица - 650 лв.; ... г) максимален месечен
  размер на осигурителния доход - 3000 лв.; 2. от 1 април до 31 декември: ... б) ... - 710 лв.; ... г) ... - 3400 лв."
  (its amending act ДВ 51/2022, `dv051-164213`, changes the maximum pension, not чл. 9);
* ЗБДОО 2023 (ДВ 66/2023, `zakon/2023/dv066-164944/art-009.md`) чл. 9: "1. от 1 януари до 31 юли: ... б) ... 710 лв.;
  ... г) ... 3400 лв.; 2. от 1 август до 31 декември: ... б) ... 780 лв.; ... г) ... 3400 лв.";
* ЗБДОО 2024 (ДВ 106/2023, `zakon/2023/dv106-165234/art-009.md`) чл. 9: "2. минимален месечен размер на
  осигурителния доход за самоосигуряващите се лица - 933 лв.; 3. максимален месечен размер на осигурителния доход -
  3750 лв.";
* ЗБНЗОК 2022, 2023, 2024 (`dv018-164016`, `dv066-164943`, `dv106-165233`) чл. 2: "Размерът на задължителната
  здравноосигурителна вноска за 202x г. е 8 на сто" (the employee rates of КСО чл. 6 and чл. 157 are the 2025 ones in
  every year: the amendment notes of the КСО text show no change of those rates between 2022 and 2025);
* minimum wage: ПМС 331/2020 (650 лв. from 1 Jan 2021, until ПМС 37/2022), ПМС 37/2022
  (`postanovlenie/2022/dv025-171427`): "от 1 април 2022 г. ... 710 лв."; ПМС 497/2022 (`postanovlenie/2023/dv001-182723`):
  "от 1 януари 2023 г. ... 780 лв."; ПМС 193/2023 (`postanovlenie/2023/dv087-200585`): "от 1 януари 2024 г. ... 933 лв.";
* ЗДБРБ 2022 (ДВ 18/2022, `zakon/2022/dv018-164015/art-014.md`) чл. 62: ал. 2 (full allowance) "1. от 1 януари до 31
  март - 410 лв.; 2. от 1 април - 510 лв.", ал. 3 (80 %) "от 410,01 лв. до 510 лв." / "от 510,01 лв. до 610 лв.",
  ал. 4 (January-March) "едно дете - 40 лв.; ... две деца - 90 лв.; ... три деца - 135 лв.; ... четири деца - 145 лв.,
  като за всяко следващо дете ... расте с 20 лв.", ал. 5 (from April) 50 / 110 / 165 / 175 лв.; ПЗР § 2, ал. 1
  (4 500 / 9 000 / 13 500 лв.) as amended by ДВ 52/2022 (`zakon/2022/dv052-164211`, § 1 т. 2 а): "4 500" replaced by
  "6 000", "9 000" by "12 000", "13 500" by "18 000") for the 2022 annual relief;
* ЗДБРБ 2023 (ДВ 66/2023, `zakon/2023/dv066-164945/art-014.md`) чл. 63: 510 лв. full, "от 510,01 лв. до 610 лв."
  80 %, amounts 50 / 110 / 165 / 175 лв.; ПЗР § 2, ал. 1: 6 000 / 12 000 / 18 000 лв.;
* ЗДБРБ 2024 (ДВ 108/2023, `zakon/2023/dv108-165235/art-001.md`) чл. 63: "е 710 лв." full, "от 710,01 лв. до 810 лв.
  включително" 80 %, amounts 50 / 110 / 165 / 175 лв.; ПЗР § 2, ал. 1: 6000 / 12 000 / 18 000 лв. (the three 2024
  amending acts, ДВ 38, 67, 83/2024, change only чл. 107 and its annex);
* school grants 300 лв. every year (ЗДБРБ 2022 чл. 62, ал. 19-20; 2023 and 2024 чл. 63, ал. 18-19); ЗСПД чл. 10а,
  ал. 1 covers grades 2-4 only since ДВ 102/2022 ("изм. и доп. - ДВ, бр. 102 от 2022 г."; the 2022 budget act still
  says "ученици, записани в първи клас"): in 2022 the grant is for first grade (and grade 8, чл. 10б) only.
The child relief is 6 000 / 12 000 / 18 000 лв. in each of 2022-2025 (`childRelief`). The 10 % rate, the 5 %
dividend tax and the statutory expense rates are unchanged in the ЗДДФЛ amendment notes for 2022-2025. -/

/-- The monthly maximum insurable income of month `m` of year `y` (2025 and later: `maxInsurable`). -/
def maxInsurableY (y m : Nat) : Int :=
  if y ≤ 2022 then (if m < 3 then 3000 * LEV else 3400 * LEV)
  else if y = 2023 then 3400 * LEV
  else if y = 2024 then 3750 * LEV
  else maxInsurable m

/-- The self-insured minimum of month `m` of year `y`. -/
def minSelfInsuredY (y m : Nat) : Int :=
  if y ≤ 2022 then (if m < 3 then 650 * LEV else 710 * LEV)
  else if y = 2023 then (if m < 7 then 710 * LEV else 780 * LEV)
  else if y = 2024 then 933 * LEV
  else minSelfInsured m

def maxInsurableYearY (y : Nat) : Int := months.foldl (fun a m => a + maxInsurableY y m) 0
def minSelfInsuredYearY (y : Nat) : Int := months.foldl (fun a m => a + minSelfInsuredY y m) 0

theorem maxInsurableY_2025 (m : Nat) : maxInsurableY 2025 m = maxInsurable m := by simp [maxInsurableY]
theorem minSelfInsuredY_2025 (m : Nat) : minSelfInsuredY 2025 m = minSelfInsured m := by simp [minSelfInsuredY]
theorem maxInsurableYear_2022_2024 :
    maxInsurableYearY 2022 = 39600 * LEV ∧ maxInsurableYearY 2023 = 40800 * LEV ∧
    maxInsurableYearY 2024 = 45000 * LEV := by decide

/-- The monthly minimum wage of month `m` of year `y`. -/
def minWageY (y m : Nat) : Int :=
  if y ≤ 2022 then (if m < 3 then 650 * LEV else 710 * LEV)
  else if y = 2023 then 780 * LEV
  else if y = 2024 then 933 * LEV
  else minWage

/-- Employee contribution rates (basis points) by fund, for a person born **after 31 Dec 1959**:
* pension (ДОО): КСО чл. 6, ал. 3, т. 9, б. "а": "5,7 на сто за сметка на осигуреното лице" + т. 4, б. "а", "б" of
  ал. 1: two increases of 1 point "от който ... 0,44 за сметка на осигуреното лице" = 6.58 %;
* general illness and maternity: чл. 6, ал. 1, т. 5 "3,5 на сто", split 60:40 (ал. 3, т. 7) = 1.4 %;
* unemployment: чл. 6, ал. 1, т. 6 "едно на сто", split 60:40 = 0.4 %;
* universal pension fund: чл. 157, ал. 3, т. 1: "за сметка на осигуреното лице - 2,2 на сто";
* health: ЗБНЗОК 2025 чл. 2 "8 на сто", ЗЗО чл. 40, ал. 1, т. 1 "2010 г. и следващите години - 60:40" = 3.2 %. -/
def eePension1960 : Int := 658
def eeGim : Int := 140
def eeUnemployment : Int := 40
def eeUpf : Int := 220
def eeHealth : Int := 320

/-- Born **before 1 Jan 1960** (no universal pension fund): КСО чл. 6, ал. 3, т. 8, б. "а": "7,9 на сто за сметка на
осигуреното лице" + 2 × 0.44 = 8.78 %. The employee total is 13.78 % in both cases. -/
def eePensionPre1960 : Int := 878

/-- Employer rates (for the owner-manager comparison only; not in the household's net income): pension 7.1 + 2 × 0.56
= 8.22 % (КСО чл. 6, ал. 3, т. 9, б. "б"), GIM 2.1 %, unemployment 0.6 %, universal fund 2.8 % (чл. 157, ал. 3, т. 2),
work accident 0.4 % (ЗБДОО 2025 чл. 14 and прил. 2/2А, the lowest group; range "от 0,4 до 1,1 на сто", КСО чл. 6,
ал. 1, т. 7), health 4.8 %; ЗБДОО 2025 чл. 15, ал. 1: "За 2025 г. не се внасят вноски за Фонд "Гарантирани вземания""
→ 18.92 %. -/
def erTotal : Int := 822 + 210 + 60 + 280 + 40 + 480

/-- Self-insured (КСО чл. 4, ал. 3, т. 1 free professions) born after 1959: pension "12,8 на сто" (чл. 6, ал. 3, т. 9,
б. "а") + 2 points (ал. 1, т. 4) = 14.8 %, universal fund 5 % (чл. 157, ал. 1, т. 1, б. "в"), health 8 %; general
illness and maternity (3.5 %) is optional (чл. 4, ал. 4: "по свой избор") and not taken. -/
def sePension1960 : Int := 1480
def sePensionPre1960 : Int := 1980
def seUpf : Int := 500
def seHealth : Int := 800

/-! ## Family allowances (ЗСПД, ЗДБРБ 2025 чл. 64) -/

/-- ЗДБРБ 2025 чл. 64, ал. 2 and 3: monthly income per family member for the full allowance ("от 1 януари до 31 март
- 710 лв.; от 1 април - 760 лв.") and the upper limit of the 80 % band ("от 710,01 лв. до 810 лв.";
"от 760,01 лв. до 860 лв."). -/
def allowanceFullLimit (m : Nat) : Int := if m < 3 then 710 * LEV else 760 * LEV
def allowancePartLimit (m : Nat) : Int := if m < 3 then 810 * LEV else 860 * LEV

/-- ЗДБРБ 2025 чл. 64, ал. 4: "1. за семейство с едно дете - 50 лв.; 2. ... две деца - 110 лв.; 3. ... три деца -
165 лв.; 4. ... четири деца - 175 лв., като за всяко следващо дете ... расте с 20 лв." (monthly, per family). -/
def allowanceFull : Nat → Int
  | 0 => 0
  | 1 => 50 * LEV
  | 2 => 110 * LEV
  | 3 => 165 * LEV
  | n + 4 => (175 + 20 * (n : Int)) * LEV

/-- ЗДБРБ 2025 чл. 64, ал. 5: in the upper band the allowance "е 80 на сто от размера на помощта". -/
def allowancePartRate : Int := 8000

/-- The allowance limits of year `y` (2022-2024: the ЗДБРБ articles quoted above; 2025: чл. 64). -/
def allowanceFullLimitY (y m : Nat) : Int :=
  if y ≤ 2022 then (if m < 3 then 410 * LEV else 510 * LEV)
  else if y = 2023 then 510 * LEV
  else if y = 2024 then 710 * LEV
  else allowanceFullLimit m
def allowancePartLimitY (y m : Nat) : Int :=
  if y ≤ 2022 then (if m < 3 then 510 * LEV else 610 * LEV)
  else if y = 2023 then 610 * LEV
  else if y = 2024 then 810 * LEV
  else allowancePartLimit m

/-- ЗДБРБ 2022 чл. 62, ал. 4: January-March 2022: 40 / 90 / 135 / 145 лв., +20 лв. per further child. -/
def allowanceFullJanMar2022 : Nat → Int
  | 0 => 0
  | 1 => 40 * LEV
  | 2 => 90 * LEV
  | 3 => 135 * LEV
  | n + 4 => (145 + 20 * (n : Int)) * LEV

/-- EUROMOD convention (`--euromod`, round 15; 30 June rule, see `Social.lean`): the 2022 annual child relief in
force on 30 June 2022, ЗДБРБ 2022 ПЗР § 2, ал. 1 as promulgated (ДВ 18/2022): "4 500 / 9 000 / 13 500 лв.". The
amending act ДВ 52/2022 (`refs/bglaw/zakon/2022/dv052-164211`, in force 1 July 2022) raised them to 6 000 / 12 000 /
18 000 лв. after that date. 2023-2025: the relief in force on 30 June is `childRelief` (6 000 / 12 000 / 18 000). -/
def childReliefJ (y : Nat) : Nat → Int
  | 0 => 0
  | 1 => if y ≤ 2022 then 4500 * LEV else childRelief 1
  | 2 => if y ≤ 2022 then 9000 * LEV else childRelief 2
  | n + 3 => if y ≤ 2022 then 13500 * LEV else childRelief (n + 3)

def allowanceFullY (y m n : Nat) : Int :=
  if y ≤ 2022 && m < 3 then allowanceFullJanMar2022 n else allowanceFull n

/-- ЗДБРБ 2025 чл. 64, ал. 18 and 19: one-off grant for pupils in grades 1-4 (ЗСПД чл. 10а) and in grade 8
(чл. 10б) for 2025-26 "е 300 лв."; both "независимо от дохода на семейството" (чл. 10а, ал. 2; чл. 10б, ал. 2). -/
def schoolGrant : Int := 300 * LEV

/-! ## Company side (owner-manager comparison) -/

/-- ЗКПО чл. 20: "Данъчната ставка на корпоративния данък е 10 на сто." -/
def citRate : Int := 1000

end BgTax
