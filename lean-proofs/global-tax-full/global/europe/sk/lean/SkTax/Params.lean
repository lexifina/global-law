import TaxKernel

/-!
# Slovakia, tax year 2025: parameters (every number with its source)

Unit of account: the **euro cent** (`Int`), because the statute computes to the cent (ZDP § 47). Rates in basis points.

Sources (copies in `cmp20/central/sk/refs/`):
* ZDP = zákon č. 595/2003 Z. z. o dani z príjmov, znenie účinné od 1. 1. 2025
  (https://static.slov-lex.sk/static/SK/ZZ/2003/595/20250101.html, `refs/slovlex/zdp595_20250101.txt`);
  the 1. 1. 2024 version (`zdp595_20240101`) for the dividend rate kept by § 52zzzb ods. 5.
* ZSP = zákon č. 461/2003 Z. z. o sociálnom poistení, znenie 1. 1. 2025 (`refs/slovlex/soc461_20250101.txt`).
* ZZP = zákon č. 580/2004 Z. z. o zdravotnom poistení, znenie 1. 1. 2025 (`refs/slovlex/zdrav580_20250101.txt`).
* ZPD = zákon č. 600/2003 Z. z. o prídavku na dieťa, znenie 1. 1. 2025 (`refs/slovlex/pridavok600_20250101.txt`).
* Opatrenie MPSVR SR č. 149/2024 Z. z. (ŽM from 1. 7. 2024, `refs/slovlex/zm_opatrenie149_2024.txt`).
* Finančná správa, "Daňový bonus na vyživované dieťa za rok 2025"
  (https://podpora.financnasprava.sk/790897, `refs/fs/fs_bonus2025_790897.txt`): the 2023 average wage 1 430 €.
-/

namespace SkTax
open TaxKernel

/-- ZDP § 47: "Všetky prepočty podľa tohto zákona sa vykonajú s presnosťou na dve desatinné miesta ...
číslica päť alebo číslica väčšia ako päť, sa zväčšuje o jednu": `n / d` to the cent, halves up. -/
def rh (n d : Int) : Int := divR .halfUp n d

/-- ZSP § 129 ods. 2 ("Jednotlivé sumy poistného ... sa zaokrúhľujú na najbližší eurocent nadol") and ZZP § 16
ods. 1, § 19 ods. 3 ("na najbližší eurocent nadol"): `bp` of `x` cents, rounded down. -/
def pctD (x bp : Int) : Int := (x * bp) / 10000

/-- ZDP § 47: `bp` of `x` cents, halves up. -/
def pctH (x bp : Int) : Int := rh (x * bp) 10000

/-! ## Životné minimum and the ZDP amounts tied to it -/

/-- Opatrenie č. 149/2024 Z. z. (účinnosť 1. júla 2024): "suma podľa § 2 písm. a) zákona je 273,99 eura". ZDP § 11
ods. 2 písm. a) uses the ŽM "platného k 1. januáru príslušného zdaňovacieho obdobia" → 273,99 € for 2025. -/
def zm : Int := 27399

/-- `tenths/10 × ŽM` in cents, rounded by § 47. -/
def zmTimes (tenths : Int) : Int := rh (tenths * zm) 10

/-- § 11 ods. 2 písm. a): "21,0-násobku sumy životného minima" (NČZD na daňovníka, full). -/
def ncz21 : Int := zmTimes 210
/-- § 11 ods. 2 písm. a): "92,8-násobok sumy životného minima" (start of the NČZD withdrawal). -/
def ncz928 : Int := zmTimes 928
/-- § 11 ods. 2 písm. b): "rozdielu 44,2-násobku platného životného minima a jednej štvrtiny základu dane". -/
def ncz442 : Int := zmTimes 442
/-- § 15 písm. a) bod 1a/1b and 3a/3b: "176,8-násobok sumy platného životného minima" (the 25 % threshold); also § 11
ods. 3 (the spouse allowance threshold). -/
def th1768 : Int := zmTimes 1768
/-- § 11 ods. 3 písm. a) bod 1: "19,2-násobku platného životného minima" (spouse). -/
def sp192 : Int := zmTimes 192
/-- § 11 ods. 3 písm. b) bod 1: "rozdielu 63,4-násobku platného životného minima a jednej štvrtiny základu dane". -/
def sp634 : Int := zmTimes 634

theorem zm_amounts : ncz21 = 575379 ∧ ncz928 = 2542627 ∧ ncz442 = 1211036 ∧ th1768 = 4844143 ∧
    sp192 = 526061 ∧ sp634 = 1737097 := by decide

/-! ## § 15 rates -/

/-- § 15 písm. a) bod 1a: "19 % z tej časti základu dane, ktorá nepresiahne 176,8-násobok". -/
def rate19 : Int := 1900
/-- § 15 písm. a) bod 1b: "25 % z tej časti základu dane, ktorá presiahne 176,8-násobok". -/
def rate25 : Int := 2500
/-- § 15 písm. a) bod 2: "15 % zo základu dane zisteného podľa § 4 ods. 1 písm. b) ... pre daňovníka, ktorý dosiahol
... zdaniteľné príjmy (výnosy) podľa § 6 ods. 1 a 2 neprevyšujúce sumu 100 000 eur". -/
def rate15 : Int := 1500
def smallBizLimit : Int := 10000000

/-- § 43 ods. 1 písm. a) in the version in force until 31. 12. 2024: "10 % z príjmov podľa odseku 3 písm. r) a s)";
§ 52zzzb ods. 5 applies the new 7 % (znenie 1. 1. 2025) only to dividends "vykázaných za zdaňovacie obdobie začínajúce
najskôr 1. januára 2025": dividends paid in 2025 out of 2024 (or earlier) profits stay at 10 %. -/
def divRateOld : Int := 1000
/-- § 43 ods. 1 písm. a) and § 15 písm. a) bod 5, znenie 1. 1. 2025: "7 %". -/
def divRateNew : Int := 700
/-- § 43 ods. 1 písm. b) with ods. 3 písm. a): bank interest "19 %" withheld (final, § 43 ods. 6). -/
def interestRate : Int := 1900

/-- § 9 ods. 1 písm. g) and i): rent (§ 6 ods. 3) and § 8 ods. 1 písm. d)–f) income exempt "500 eur", together
"najviac v úhrnnej výške 500 eur". -/
def smallIncomeExempt : Int := 50000

/-- § 6 ods. 10: "výdavky vo výške 60 % z úhrnu príjmov ... najviac do výšky 20 000 eur". -/
def pausalPct : Int := 6000
def pausalCap : Int := 2000000

/-- § 11 ods. 9: DDS / PEPP contributions "najviac do 180 eur za rok". -/
def ddsCap : Int := 18000

/-! ## § 33 daňový bonus -/

/-- § 33 ods. 1 písm. b): "100 eur mesačne, ak vyživované dieťa nedovŕšilo 15 rokov veku". -/
def bonusUnder15 : Int := 10000
/-- § 33 ods. 1 písm. a): "50 eur mesačne, ak vyživované dieťa dovŕšilo 15 rokov veku a nedovŕšilo 18 rokov". -/
def bonus15to18 : Int := 5000

/-- § 33 ods. 6: "Percentuálny limit": 1 dieťa 29 %, 2: 36 %, 3: 43 %, 4: 50 %, 5: 57 %, 6 a viac 64 %. -/
def bonusPct (n : Int) : Int := if n ≤ 0 then 0 else if 6 ≤ n then 6400 else 2200 + 700 * n

theorem bonusPct_table : bonusPct 1 = 2900 ∧ bonusPct 2 = 3600 ∧ bonusPct 3 = 4300 ∧ bonusPct 4 = 5000 ∧
    bonusPct 5 = 5700 ∧ bonusPct 6 = 6400 ∧ bonusPct 9 = 6400 := by decide

/-- Average monthly wage 2023 (ŠÚ SR), 1 430 €: Finančná správa (podpora 790897, otázka 5): "25 740 (1 430*1,5 eur*12)".
Used by ZDP § 33 ods. 11 (year t−2) and as 1/12 of the všeobecný vymeriavací základ (ZSP § 11: "12-násobok priemernej
mesačnej mzdy") of 2023 in ZSP § 138 ods. 9–10, and as the "priemerná mesačná mzda" of ZZP § 13 ods. 10. -/
def avgWage2023 : Int := 143000

/-- § 33 ods. 11: "1,5-násobok 12-násobku priemernej mesačnej mzdy" = 25 740 €. -/
def bonusTaperStart : Int := 3 * 12 * avgWage2023 / 2
/-- The monthly form used in withholding (Finančná správa, "Zmeny platné od 1.1.2025", bod 4): 2 145 €. -/
def bonusTaperStartMonthly : Int := 3 * avgWage2023 / 2

theorem bonusTaper_values : bonusTaperStart = 2574000 ∧ bonusTaperStartMonthly = 214500 := by decide

/-! ## Contributions -/

/-- ZSP § 130 písm. a): nemocenské poistenie "zamestnanca 1,4 %". -/
def sickEE : Int := 140
/-- ZSP § 131 ods. 1 písm. a): starobné poistenie "zamestnanca 4 %". -/
def oldEE : Int := 400
/-- ZSP § 132 písm. a): invalidné poistenie "zamestnanca 3 %". -/
def invEE : Int := 300
/-- ZSP § 136 písm. a): poistenie v nezamestnanosti "zamestnanca 1 %". -/
def unempEE : Int := 100
/-- ZSP § 130 písm. c), § 131 ods. 1 písm. c), § 132 písm. c), § 137: SZČO 4,4 % + 18 % + 6 % + 4,75 %. -/
def sickSE : Int := 440
def oldSE : Int := 1800
def invSE : Int := 600
def reserveSE : Int := 475

/-- ZSP § 138 ods. 10: "Maximálny mesačný vymeriavací základ v úhrne je 11-násobok jednej dvanástiny všeobecného
vymeriavacieho základu" of year t−2 (2023): 11 × 1 430 € = 15 730 €. -/
def socMaxMonthly : Int := 11 * avgWage2023
/-- ZSP § 138 ods. 9: "Minimálny mesačný vymeriavací základ je 50 % jednej dvanástiny všeobecného vymeriavacieho
základu" (2023): 715 €. -/
def socMinMonthly : Int := avgWage2023 / 2
/-- ZSP § 21 ods. 1: an SZČO is compulsorily insured when its prior-year income "bol vyšší ako 12-násobok vymeriavacieho
základu uvedeného v § 138 ods. 9 písm. a)": 12 × 715 € = 8 580 € (steady state: this year's receipts stand for last
year's). -/
def seThreshold : Int := 12 * socMinMonthly
/-- ZSP § 138 ods. 2 and ZZP § 13 ods. 2: the SZČO base is the tax base before contributions divided by "koeficientu
1,486" (in thousandths). -/
def seCoef : Int := 1486

/-- ZZP § 12 ods. 1 písm. a): "zamestnanca 4 %". -/
def healthEE : Int := 400
/-- ZZP § 12 ods. 1 písm. c): "samostatne zárobkovo činnú osobu 14 %"; písm. b) with § 13 ods. 7: 14 % on the § 7
and § 8 ZDP bases. -/
def healthSE : Int := 1400
/-- ZZP § 13 ods. 10: "minimálny základ samostatne zárobkovo činnej osoby ... 50 % z priemernej mesačnej mzdy". -/
def healthMinMonthly : Int := avgWage2023 / 2

theorem contribution_values : socMaxMonthly = 1573000 ∧ socMinMonthly = 71500 ∧ seThreshold = 858000 ∧
    healthMinMonthly = 71500 := by decide

/-! ## Prídavok na dieťa -/

/-- ZPD § 8 ods. 1: "Prídavok je 60 eur mesačne." -/
def pridavok : Int := 6000

/-- ZPD § 8 ods. 1 písm. b) (znenie 1. 1. 2025, `refs/slovlex/pridavok600_20250101.txt`): the prídavok is increased
"o 110 eur za kalendárny mesiac, v ktorom nezaopatrené dieťa prvýkrát nastúpilo do prvého ročníka základnej školy"
(improvement round 1, 2026-11-19). -/
def schoolEntryIncrease : Int := 11000

/-! ## § 32a zamestnanecká prémia -/

/-- Monthly minimum wage 2025, 816 € (zákon 663/2007 § 8 formula of 2024: 57 % of the 2023 average wage 1 430 €,
rounded up; the 2025 amount was announced in the Zbierka, not fetched here). Used only by § 32a; the theorem
`premia_dead` shows the result is the same for every minimum wage ≥ 554 €. -/
def minWage2025 : Int := 81600

/-! ## Earlier tax years 2022-2024 (improvement round 2, 2026-11-19)

Dated texts fetched from static.slov-lex.sk into `refs/slovlex/` (file names give the version date):
`zdp595_20220101`, `zdp595_20220701`, `zdp595_20230101`, `zdp595_20240101`; `pridavok600_20210101` (in force
1. 1. 2021 - 30. 6. 2022), `pridavok600_20220701`, `pridavok600_20230101`, `pridavok600_20240101`;
`pridavok_opatrenie497_2021` (opatrenie MPSVR SR č. 497/2021 Z. z., from 1. 1. 2022); `zm_opatrenie244_2021`,
`zm_opatrenie227_2022`, `zm_opatrenie220_2023` (ŽM from 1. 7. 2021 / 2022 / 2023); `soc461_2022/2023/20240101`,
`zdrav580_2022/2023/20240101`; `mw_oznamenie352_2021` (minimum wage 2022). The § 11, § 15 and § 47 texts of the
2022, 2023 and 2024 versions are the same as in 2025 (multiples 21,0 / 92,8 / 44,2 / 19,2 / 63,4 / 176,8 of the
ŽM "platného k 1. januáru príslušného zdaňovacieho obdobia"); only the ŽM changes. -/

/-- ŽM (§ 2 písm. a) zákona 601/2003) valid at 1 January of tax year `y`: opatrenie 244/2021 "218,06 eura" (2022),
227/2022 "234,42 eura" (2023), 220/2023 "268,88 eura" (2024), 149/2024 "273,99 eura" (2025 and later). -/
def zmFor (y : Nat) : Int :=
  if y ≤ 2022 then 21806 else if y = 2023 then 23442 else if y = 2024 then 26888 else zm

/-- `tenths/10 × ŽM` of year `y`, rounded by § 47. -/
def zmTimesY (y : Nat) (tenths : Int) : Int := rh (tenths * zmFor y) 10

theorem zmFor_2025 : zmFor 2025 = zm := by decide
theorem zmTimesY_2025 (t : Int) : zmTimesY 2025 t = zmTimes t := by
  simp [zmTimesY, zmTimes, zmFor_2025]

/-- ZSP § 138 ods. 10 (versions 1. 1. 2022, 2023, 2024: the ceiling "7-násobok jednej dvanástiny všeobecného
vymeriavacieho základu" of year t−2). The všeobecný vymeriavací základ itself (ŠÚ SR average monthly wage of
2020 / 2021 / 2022: 1 133 / 1 211 / 1 304 €) is NOT in a dated legal text we hold: it is the statistical figure the
Sociálna poisťovňa announces (marked in `unsupported` for those years). It binds only for monthly wages above
7 931 / 8 477 / 9 128 €. 2025: the 11-násobok of § 138 ods. 10 (`socMaxMonthly`). -/
def vvzMonthlyFor (y : Nat) : Int :=
  if y ≤ 2022 then 113300 else if y = 2023 then 121100 else if y = 2024 then 130400 else avgWage2023
def socMaxMonthlyFor (y : Nat) : Int := if y ≤ 2024 then 7 * vvzMonthlyFor y else socMaxMonthly

theorem socMaxMonthlyFor_2025 : socMaxMonthlyFor 2025 = socMaxMonthly := by decide

/-- ZDP § 52zzp ods. 4 (versions 1. 1. 2023 and 1. 1. 2024), applied "od 1. januára 2023 do 31. decembra 2024" by
ods. 3 and 5: "a) 50 eur mesačne, ak vyživované dieťa dovŕšilo 18 rokov veku, alebo b) 140 eur mesačne, ak
vyživované dieťa nedovŕšilo 18 rokov veku, a to poslednýkrát za kalendárny mesiac, v ktorom dieťa dovŕši 18 rokov". -/
def bonus2324Under18 : Int := 14000
def bonus2324Adult : Int := 5000

/-- ZDP § 33 ods. 6 (versions 1. 1. 2023 and 1. 1. 2024, applied by § 52zzp ods. 3) and § 52zzn ods. 8 (version
1. 7. 2022, of half the base for July-December 2022): "1 ... 20 %, 2 ... 27 %, 3 ... 34 %, 4 ... 41 %, 5 ... 48 %,
6 a viac ... 55 %". -/
def bonusPct2224 (n : Int) : Int := if n ≤ 0 then 0 else if 6 ≤ n then 5500 else 1300 + 700 * n

theorem bonusPct2224_table : bonusPct2224 1 = 2000 ∧ bonusPct2224 2 = 2700 ∧ bonusPct2224 3 = 3400 ∧
    bonusPct2224 4 = 4100 ∧ bonusPct2224 5 = 4800 ∧ bonusPct2224 6 = 5500 := by decide

/-- ZDP § 33 ods. 1 (version 1. 1. 2022, in force to 30. 6. 2022): "a) 22,17 eur mesačne, ak vyživované dieťa
dovŕšilo 15 rokov veku, b) dvojnásobok sumy podľa písmena a) ... ak ... nedovŕšilo šesť rokov veku ... c) 1,85-násobok
sumy podľa písmena a) ... ak ... dovŕšilo šesť rokov veku a nedovŕšilo 15 rokov veku". The 22,17 € is not the amount
paid: § 52zd ods. 7 (text of 1. 1. 2015, unchanged in the 2022 version) "Daňový bonus podľa § 33 sa zvyšuje k 1. januáru
príslušného zdaňovacieho obdobia rovnakým koeficientom, ako sa zvyšovala suma životného minima k 1. júlu
predchádzajúceho zdaňovacieho obdobia ... Ustanovenie § 52 ods. 48 sa od 1. januára 2015 neuplatňuje." (Round 3
correction: round 2 cited § 52 ods. 48, which § 52zd ods. 7 disapplies; the January–June figure is the same.) 22,17 € is
the amount of the ŽM 205,07 € period (opatrenie 196/2018, from 1. 7. 2018); the ŽM then rose on 1 July to 210,20 €
(opatrenie 183/2019), 214,83 € (174/2020) and 218,06 € (244/2021), applied each 1 January (2020, 2021, 2022), each step
rounded by § 47: 22,72 → 23,22 → 23,57 € for the whole of 2022. The 1. 7. 2022 ŽM (227/2022) would only act from
1. 1. 2023, and § 52zzp ods. 7 (version 1. 1. 2023) disapplies § 52zd ods. 7 first and second sentences from 2023.
So the § 33 of 30. 6. 2022 that § 52zzn ods. 1 compares with for July–December is also 23,57 € (`bonus22aH2`). -/
def valorise (amt : Int) : List (Int × Int) → Int
  | [] => amt
  | (a, b) :: r => valorise (rh (amt * b) a) r

def bonus22a : Int := valorise 2217 [(20507, 21020), (21020, 21483), (21483, 21806)]
def bonus22aH2 : Int := bonus22a
/-- § 33 ods. 1 písm. b) and c) on the valorised letter a) amount (§ 47 to the cent). -/
def bonus22b (a : Int) : Int := 2 * a
def bonus22c (a : Int) : Int := rh (185 * a) 100

theorem bonus22_values : bonus22a = 2357 ∧ bonus22b bonus22a = 4714 ∧ bonus22c bonus22a = 4360 ∧
    bonus22aH2 = 2357 ∧ bonus22b bonus22aH2 = 4714 ∧ bonus22c bonus22aH2 = 4360 := by decide

/-- ZDP § 52zzn ods. 3 (version 1. 7. 2022), July-December 2022: "a) 40 eur mesačne, ak vyživované dieťa dovŕšilo
15 rokov veku, alebo b) 70 eur mesačne, ak vyživované dieťa nedovŕšilo 15 rokov veku". -/
def bonus22H2Over15 : Int := 4000
def bonus22H2Under15 : Int := 7000

/-- Oznámenie MPSVR SR č. 352/2021 Z. z.: minimum wage 2022 "646 eur za mesiac"; ZDP § 33 ods. 1 (1. 1. 2022): the
bonus needs § 5 (or § 6 ods. 1, 2) income "aspoň vo výške 6-násobku minimálnej mzdy" (3 876 €). -/
def minWage2022 : Int := 64600

/-- Nariadenie vlády SR č. 102/2020 Z. z., § 1d (version in force 20. 5. 2022, `refs/slovlex/nv102_2020_20220520.txt`):
"Suma prídavku na dieťa podľa osobitného predpisu sa za máj 2022 zvýši o 74,12 eura." (Round 3: explains the OECD's
2022 family benefit, 818,80 € for two children.) -/
def pridavokMay2022Increase : Int := 7412

/-- Nariadenie vlády SR č. 102/2020 Z. z., § 1e (version in force 28. 10. 2022, `refs/slovlex/nv102_2020_20221028.txt`):
"Suma prídavku na dieťa ... sa za október 2022 zvýši o 70 eur na nezaopatrené dieťa narodené od 1. júna 2022 do
31. októbra 2022." -/
def pridavokOct2022Newborn : Int := 7000

/-- Prídavok per month in tax year `y`, month `m`: opatrenie 497/2021 "suma podľa § 8 ods. 1 prvej vety zákona je
25,88 eura" (January-June 2022); ZPD § 8 ods. 1 version 1. 7. 2022 "Prídavok je 30 eur mesačne" (July-December 2022);
versions 1. 1. 2023 and 1. 1. 2024 "Prídavok je 60 eur mesačne"; 2025: `pridavok`. -/
def pridavokAt (y : Nat) (m : Int) : Int :=
  if y ≤ 2022 then (if m ≤ 6 then (if m = 5 then 2588 + pridavokMay2022Increase else 2588) else 3000) else pridavok

/-- The one-off increase for the first school entry (September): ZPD § 8 ods. 1 version 1. 7. 2022 "zvýši o 100 eur
za kalendárny mesiac, v ktorom nezaopatrené dieťa prvýkrát nastúpilo do prvého ročníka základnej školy"; 1. 1. 2023 and
1. 1. 2024: "o 110 eur"; 2025: `schoolEntryIncrease`. -/
def schoolEntryFor (y : Nat) : Int := if y ≤ 2022 then 10000 else schoolEntryIncrease

/-- ZDP § 43 ods. 1 písm. a) (dividends): "7 % z príjmov podľa odseku 3 písm. r) a s)" in the versions of 1. 1. 2022
and 1. 1. 2023; "10 %" in the version of 1. 1. 2024. -/
def divRateFor (y : Nat) : Int := if y ≤ 2023 then 700 else divRateOld

end SkTax
