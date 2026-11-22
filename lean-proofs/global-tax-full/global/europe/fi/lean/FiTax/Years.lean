import FiTax.Assess

/-!
# FiTax.Years: tax years 2022, 2023 and 2024 (round 8, 2026-11-19)

The 2025 model keeps its constants and proofs; an earlier year goes through the per-year record `YP` and `stageY`,
which follows `Assess.stage` step by step with that year's parameters and the earned-income deduction (TVL 105 a §,
2023-2024 wording). Sources (saved in `refs/years/`, `refs/tvl_current.txt`, `refs/yle_484_2012.dec.txt`):
* State scale: Laki vuoden 2024 tuloveroasteikosta 1193/2023: 0 -> 12,64 %; 20 500 -> 19 %; 30 500 -> 30,25 %;
  50 400 -> 34 %; 88 200 -> 42 %; 150 000 -> 44 %.
* TVL 105 a § [L 20.12.2022/1123] (in force 2023-2024, repealed by 702/2024): "Vähennys on 51 prosenttia ...
  tulojen 2 500 euroa ylittävältä osalta tulojen 7 230 euron määrään saakka ja sen ylittävältä osalta 28 prosenttia.
  Vähennyksen enimmäismäärä on kuitenkin 3 570 euroa. ... puhtaan ansiotulon ylittäessä 14 000 euroa vähennyksen
  määrä pienenee 4,5 prosentilla"; deducted "Verovelvollisen puhtaasta ansiotulosta" (state and municipal).
* TVL 106 § [1194/2023]: "3 980 euron", 18 %.
* TVL 125 § [1194/2023]: "12 prosenttia ... enimmäismäärä ... 2 140 euroa ... ylittäessä 23 420 euroa ... 2,03
  prosentilla ... ylittää 71 900 euroa ... 1,21 prosentilla"; "korotetaan 1 200 eurolla, jos ... täyttänyt 65 vuotta
  ennen verovuoden alkua"; no child increase (added by 702/2024 from 2025).
* Yleisradioverolaki 2 § (wording replaced by 920/2024 from 2025): "2,5 prosenttia ... 14 000 euroa ylittävästä
  osasta ... ei ... 163 euroa enempää".
* STM 1008/2023: TyEL "7,15" / "8,65"; laki 1127/2023: "Palkansaajan työttömyysvakuutusmaksu vuonna 2024 on 0,79
  prosenttia"; VN 1026/2023: sairaanhoitomaksu "0,51 prosenttia", other earned income "1,48 prosenttia",
  päivärahamaksu "1,01 prosenttia ... vähintään 16 499 euroa".
* Helsinki 2024: "Helsinki 5,30" (LUETTELO kuntien ja seurakuntien tuloveroprosenteista vuonna 2024, 1038/2023);
  weighted average 2024: 7,47 % (Kuntaliitto, Kuntien veroprosentit 2025, table "2024 7,47").
* Lapsilisä 2024 (lapsilisälaki 7 § [1299/2023]): base amounts as 2025; single-parent supplement "73,30 eurolla";
  under-3 increase (+26,00 €) "sovelletaan 1.4.2024 lähtien" (9 months).
Not sourced for 2022-2024 (2025 rules used, stated in `unsupported`): the eläketulovähennys (each year's full
national pension and the 2023-2024 / 2022 wordings of 100 §, 2022 also 101 §) and the deficit credit's first-home
increase (131 § 3-5 mom, repealed from 2025). Capital income tax (124 § 2 mom, 785/2012) and the eläketulon lisävero
(124 § 4 mom, 1510/2016) have the same wording in 2022-2025 (round 10). -/

namespace FiTax
open TaxKernel

structure YP where
  year : Nat
  sched : Schedule
  ansio : Bool
  basicFull : Int
  wcRate : Int
  wcMax : Int
  wcTaper : Schedule
  wcAge65 : Int
  /-- 2023 only (125 § 3 mom [1123/2022]): +200 € from 60, +400 € from 62 "ennen verovuoden alkua" -/
  wcAge60 : Int := 0
  wcAge62 : Int := 0
  /-- 2022: the work-income credit base starts at 2 500 € ("tulojen 2 500 euroa ylittävältä osalta") -/
  wcBase : Int := 0
  /-- 2022: separate state and municipal bases (ansiotulo- and perusvähennys in municipal taxation only) -/
  split : Bool := false
  /-- 2022: the scale as printed (lower limit, tax at the limit, rate above), cents and bp; empty = `sched` -/
  tab : List (Int × Int × Int) := []
  /-- months of lapsilisä paid in the year (2022: December paid twice, 983/2022) -/
  cbMonths : Int := 12
  yleThr : Int
  yleMx : Int
  tyelR : Int
  tyel53R : Int
  unempR : Int
  dailyR : Int
  dailyLim : Int
  medR : Int
  medExtraR : Int
  helsinki : Int
  average : Int
  cbSingle : Int
  /-- months of the year with the under-3 increase -/
  under3Months : Nat

def yp2024 : YP :=
  { year := 2024,
    sched := Schedule.ofList [(0, 1264), (eur 20500, 1900), (eur 30500, 3025), (eur 50400, 3400), (eur 88200, 4200),
      (eur 150000, 4400)],
    ansio := true, basicFull := eur 3980,
    wcRate := 1200, wcMax := eur 2140, wcTaper := Schedule.ofList [(0, 0), (eur 23420, 203), (eur 71900, 121)],
    wcAge65 := eur 1200, yleThr := eur 14000, yleMx := eur 163,
    tyelR := 715, tyel53R := 865, unempR := 79, dailyR := 101, dailyLim := eur 16499, medR := 51, medExtraR := 97,
    helsinki := 530, average := 747, cbSingle := 7330, under3Months := 9 }

/-- 2023 (round 8). Laki vuoden 2023 tuloveroasteikosta 1122/2022: 0 -> 12,64 %; 19 900 -> 19 %; 29 700 -> 30,25 %;
49 000 -> 34 %; 85 800 -> 44 %. TVL [1123/2022]: 105 a § as 2024; 106 § "3 870 euron"; 125 § "12 prosenttia ...
2 030 euroa ... ylittäessä 22 000 euroa ... 2,03 prosentilla ... ylittää 70 000 euroa ... 1,21 prosentilla", raised
"200 eurolla" (60-61), "400 eurolla" (62-64), "600 eurolla" (65+) at the start of the year. Yleisradioverolaki 2 §
[L 1.12.2017/817] (in force 2018-2024): 14 000 / 163. STM 903/2022: 7,15 / 8,65; laki 891/2022: "vuonna 2023 on 1,50
prosenttia"; VN 921/2022: sairaanhoitomaksu "0,60" (other earned income "1,57"), päivärahamaksu "1,36 ... vähintään
15 703 euroa". Helsinki "5,36" (LUETTELO kuntien ja seurakuntien tuloveroprosenteista vuonna 2023, 930/2022; the 2024
list 1038/2023 gives "Helsinki 5,30"); weighted average 7,37 % (Kuntaliitto, Kuntien veroprosentit 2025, table:
"2023* 7,37"). Lapsilisä: single-parent supplement "68,30 euroa" (1226/2022); no under-3 increase. -/
def yp2023 : YP :=
  { year := 2023,
    sched := Schedule.ofList [(0, 1264), (eur 19900, 1900), (eur 29700, 3025), (eur 49000, 3400), (eur 85800, 4400)],
    ansio := true, basicFull := eur 3870,
    wcRate := 1200, wcMax := eur 2030, wcTaper := Schedule.ofList [(0, 0), (eur 22000, 203), (eur 70000, 121)],
    wcAge65 := eur 600, wcAge60 := eur 200, wcAge62 := eur 400, yleThr := eur 14000, yleMx := eur 163,
    tyelR := 715, tyel53R := 865, unempR := 150, dailyR := 136, dailyLim := eur 15703, medR := 60, medExtraR := 97,
    helsinki := 536, average := 737, cbSingle := 6830, under3Months := 0 }

/-- 2022 (round 8). Laki vuoden 2022 tuloveroasteikosta 1131/2021: "19 200 8 6 / 28 700 578 17,25 / 47 300 3 786,5
21,25 / 82 900 11 351,5 31,25" (no tax below 19 200 €). TVL as in 2022 (1132/2021 and the earlier wordings it kept):
105 a § "Kunnallisverotuksen ansiotulovähennys" [1141/2007]: 51 % / 28 %, 2 500 / 7 230, max 3 570, 4,5 % above 14 000;
106 § "Kunnallisverotuksen perusvähennys ... 3 740 euron" [1132/2021], 18 %; 125 § [1132/2021] "13 prosenttia ...
tulojen 2 500 euroa ylittävältä osalta. Vähennyksen enimmäismäärä on kuitenkin 1 930 euroa ... ylittäessä 33 000 euroa
... 1,96 prosentilla". Yleisradioverolaki 2 § [817/2017]: 14 000 / 163. STM 937/2021: 7,15 / 8,65; laki 1189/2021:
"vuonna 2022 on 1,50 prosenttia"; VN 1016/2021: sairaanhoitomaksu "0,53" (other earned income "1,50"), päivärahamaksu
"1,18 ... vähintään 15 128 euroa"; sairaanhoitomaksu on "kunnallisverotuksessa verotettavasta ansiotulosta". Helsinki
"18,00" (LUETTELO ... vuonna 2022, 1048/2021); weighted average 20,00 % (Kuntaliitto table "2022 20,00"). Lapsilisä:
single-parent supplement 63,30 € (lapsilisälaki 7 § as in 559/2022), "Lapsilisä maksetaan kaksinkertaisena vuoden 2022
joulukuulta" (983/2022): 13 monthly amounts. -/
def yp2022 : YP :=
  { year := 2022, sched := Schedule.flat 0,
    tab := [(eur 19200, 800, 600), (eur 28700, eur 578, 1725), (eur 47300, 378650, 2125), (eur 82900, 1135150, 3125)],
    split := true, ansio := true, basicFull := eur 3740,
    wcRate := 1300, wcBase := eur 2500, wcMax := eur 1930, wcTaper := Schedule.ofList [(0, 0), (eur 33000, 196)],
    wcAge65 := 0, yleThr := eur 14000, yleMx := eur 163,
    tyelR := 715, tyel53R := 865, unempR := 150, dailyR := 118, dailyLim := eur 15128, medR := 53, medExtraR := 97,
    helsinki := 1800, average := 2000, cbSingle := 6330, under3Months := 0, cbMonths := 13 }

/-- Tax from a printed scale: nothing below the first limit; else the tax at the highest limit not above the income
plus its rate on the excess (half up to the cent). -/
def tabTax (tab : List (Int × Int × Int)) (ti : Int) : Int :=
  tab.foldl (fun acc (lo, base, r) => if lo ≤ ti then base + pctOf r (ti - lo) else acc) 0

def ypFor (y : Nat) : Option YP := if y = 2022 then some yp2022 else if y = 2023 then some yp2023 else if y = 2024 then some yp2024 else none

def tyelY (q : YP) (p : Person) : Int :=
  if p.yel || p.age < 17 || p.age ≥ 68 then 0
  else (flatContribution "TyEL" (if 53 ≤ p.age ∧ p.age ≤ 62 then q.tyel53R else q.tyelR)).amount p.wages
def unemploymentY (q : YP) (p : Person) : Int :=
  if p.yel || p.age < 18 || p.age ≥ 65 then 0 else (flatContribution "työttömyysvakuutusmaksu" q.unempR).amount p.wages
def dailyY (q : YP) (p : Person) : Int :=
  if p.age ≥ 68 then 0
  else ({ name := "päivärahamaksu", sched := Schedule.flat q.dailyR, floor := q.dailyLim,
          round := Rule.unitHalfUp } : Contribution).amount (dailyBase p)
def contributionsY (q : YP) (p : Person) : Int := tyelY q p + unemploymentY q p + dailyY q p

/-- TVL 105 a § (2023-2024): 51 % of the work income between 2 500 and 7 230 €, 28 % above, at most 3 570 €, less
4,5 % of the net earned income above 14 000 €. -/
def ansioDed (q : YP) (p : Person) : Int :=
  if !q.ansio then 0 else
  let w := pos p.work
  let gross := min (eur 3570) (pctOf 5100 (pos (min w (eur 7230) - eur 2500)) + pctOf 2800 (pos (w - eur 7230)))
  pos (gross - pctOf 450 (pos (netEarned p - eur 14000)))

def beforeBasicY (q : YP) (p : Person) : Int := pos (netEarned p - contributionsY q p - pensionDed p - ansioDed q p)
def basicDedY (q : YP) (inc : Int) : Int :=
  min (pos inc) (({ full := q.basicFull, start := q.basicFull, num := 18, den := 100 } : Taper).amount inc)
def taxableY (q : YP) (p : Person) : Int := pos (beforeBasicY q p - basicDedY q (beforeBasicY q p))
def medicalY (q : YP) (p : Person) (ti : Int) : Int := pctOf q.medR ti + pctOf q.medExtraR (pos (ti - dailyBase p))
def workCreditY (q : YP) (p : Person) : Int :=
  -- `age` is the age at the end of the year: "täyttänyt N vuotta ennen verovuoden alkua" ⇔ age ≥ N + 1
  let mx := q.wcMax + (if p.age ≥ 66 then q.wcAge65 else if p.age ≥ 63 then q.wcAge62 else if p.age ≥ 61 then q.wcAge60 else 0)
  pos (min (pctOf q.wcRate (pos (p.work - q.wcBase))) mx - q.wcTaper.tax Rule.unitHalfUp (netEarned p))
def yleY (q : YP) (p : Person) : Int :=
  if p.age < 18 then 0
  else min q.yleMx (({ rate := yleRate, exempt := q.yleThr, deduct := q.yleThr, round := Rule.unitHalfUp } : Surcharge).amount (yleBase p))

def stageY (q : YP) (r : Rates) (p : Person) : Stage :=
  let ti := taxableY q p
  -- 2022: the state base has no ansiotulo- or perusvähennys (both "kunnallisverotuksen")
  let tiS := if q.split then pos (netEarned p - contributionsY q p - pensionDed p) else ti
  let s0 := (if q.tab.isEmpty then q.sched.tax Rule.unitHalfUp tiS else tabTax q.tab tiS) + pensionSurtax p
  let t0 : Taxes := { state := s0, municipal := municipalTax r ti, medical := medicalY q p ti,
                      church := if ti < municipalMinIncome then 0 else pctOf r.church ti }
  let w := workCreditY q p
  { netEarned := netEarned p, contributions := contributionsY q p, tyel := tyelY q p,
    unemployment := unemploymentY q p, daily := dailyY q p, pensionDed := pensionDed p,
    basicDed := basicDedY q (beforeBasicY q p) + ansioDed q p, taxable := tiS, stateBefore := s0,
    pensionSurtax := pensionSurtax p, workCredit := w, afterWork := applyWorkCredit t0 w,
    capitalTax := capitalTax p, yle := yleY q p }

end FiTax
