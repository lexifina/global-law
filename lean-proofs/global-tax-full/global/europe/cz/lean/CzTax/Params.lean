import CzTax.Kernel

/-!
# Parameters for 2025 (zdaňovací období 2025, the calendar year: § 16b ZDP)

Sources (official consolidated texts from e-Sbírka, fetched through its open API
`https://www.e-sbirka.cz/sbr-cache/dokumenty-sbirky/...` on 2026-11-19, copies in `refs/esb/`):

* ZDP = zákon č. 586/1992 Sb., o daních z příjmů, version in force 2025-10-01 … 2025-12-31
  (https://www.e-sbirka.cz/sb/1992/586/2025-10-01), cross-checked against the 2025-01-01 version.
* ZPSZ = zákon č. 589/1992 Sb., o pojistném na sociální zabezpečení (https://www.e-sbirka.cz/sb/1992/589/2025-07-01).
* ZPVZP = zákon č. 592/1992 Sb., o pojistném na veřejné zdravotní pojištění (https://www.e-sbirka.cz/sb/1992/592/2025-07-01).
* ZVZP = zákon č. 48/1997 Sb., o veřejném zdravotním pojištění (https://www.e-sbirka.cz/sb/1997/48/2025-03-01).
* ZSSP = zákon č. 117/1995 Sb., o státní sociální podpoře, version 2025-05-01 (https://www.e-sbirka.cz/sb/1995/117/2025-05-01).
* NV 282/2024 Sb. (všeobecný vyměřovací základ 2023 = 43 682 Kč, koeficient 1,0658), Sdělení MPSV 286/2024 Sb.
  (minimální mzda 2025), NV 436/2022 Sb. (životní minimum), zákon 427/2011 Sb. (doplňkové penzijní spoření),
  zákon 155/1995 Sb. (důchodové pojištění), zákon 280/2009 Sb. (daňový řád).
-/

namespace CzTax

/-! ## Wage references -/

/-- Průměrná mzda 2025 = 46 557 Kč. ZDP § 21g odst. 2: "Průměrnou mzdou se pro účely daní z příjmů rozumí průměrná
mzda stanovená podle zákona upravujícího pojistné na sociální zabezpečení"; that is the všeobecný vyměřovací základ
of 2023 (NV 282/2024 Sb. § 1 odst. 1: "činí 43 682 Kč") × přepočítací koeficient ("1,0658", § 1 odst. 2) =
46 556,28, rounded up to the crown (ZPVZP § 3a odst. 2 states the same formula: "zaokrouhluje na celé koruny nahoru"). -/
def avgWage : Int := 46557

/-- Minimální mzda 2025 = 20 800 Kč/month: Sdělení MPSV č. 286/2024 Sb., bod 1: "měsíční minimální mzda 20 800 Kč";
ZDP § 21g odst. 1: the monthly minimum wage "účinná k prvnímu dni příslušného zdaňovacího období". -/
def minWage : Int := 20800

/-! ## Income tax (ZDP) -/

/-- § 16 odst. 1 písm. b): 23 % "pro část základu daně přesahující 36násobek průměrné mzdy" = 1 676 052 Kč. -/
def threshold23 : Int := 36 * avgWage

/-- § 16 odst. 1: rates in basis points. -/
def rateLow : Int := 1500
def rateHigh : Int := 2300

/-- § 35ba odst. 1 písm. a): "základní slevu ve výši 30 840 Kč na poplatníka". -/
def slevaPoplatnik : Int := 30840

/-- § 35bb odst. 1: "Výše slevy na manžela činí 24 840 Kč"; odst. 2 písm. a) child under 3 in the household,
písm. b) "manžel poplatníka nemá vlastní příjem přesahující za zdaňovací období 68 000 Kč". -/
def slevaManzel : Int := 24840
def spouseIncomeLimit : Int := 68000

/-- § 35c odst. 1: "15 204 Kč ročně na jedno dítě, 22 320 Kč ročně na druhé dítě a 27 840 Kč ročně na třetí a každé
další dítě". -/
def childCredit (order : Nat) : Int :=
  if order = 0 then 15204 else if order = 1 then 22320 else 27840

/-- § 35c odst. 3: the bonus can be claimed "pokud jeho výše činí alespoň 100 Kč". -/
def bonusMin : Int := 100

/-- § 35c odst. 4: bonus only if the taxpayer "měl příjem podle § 6 nebo 7 alespoň ve výši šestinásobku minimální
mzdy" = 124 800 Kč. -/
def bonusIncomeMin : Int := 6 * minWage

/-- § 7 odst. 7: výdaje procentem z příjmů and their caps (rate in percent, cap in Kč). -/
def expenseCap (ratePct : Int) : Int :=
  if ratePct = 80 then 1600000 else if ratePct = 60 then 1200000
  else if ratePct = 30 then 600000 else 800000

/-- § 9 odst. 4: rent, 30 % of receipts "nejvýše však do částky 600 000 Kč". -/
def rentExpenseCap : Int := 600000

/-- § 4 odst. 1 písm. g): a regularly paid pension is exempt up to "36násobku minimální mzdy" = 748 800 Kč. -/
def pensionExempt : Int := 36 * minWage

/-- § 4 odst. 3: exempt share-sale income above 40 000 000 Kč in a period is taxed in proportion. -/
def shareExemptCap : Int := 40000000

/-- § 15 odst. 1: gifts deductible if they exceed "2 % ze základu daně anebo činí alespoň 1000 Kč"; "V úhrnu lze
odečíst nejvýše 15 % ze základu daně". -/
def giftMinAbs : Int := 1000

/-- § 15 odst. 3–4: mortgage interest, "nesmí překročit 150 000 Kč". -/
def mortgageCap : Int := 150000

/-- § 15 odst. 5: retirement products "v celkovém úhrnu nejvýše 48 000 Kč". Odst. 6: for penzijní připojištění /
doplňkové penzijní spoření only "část měsíčního příspěvku, která převyšuje částku, od které náleží nejvyšší státní
příspěvek"; zákon 427/2011 Sb. § 14 odst. 2 písm. b): "1 700 a více Kč … 340 Kč". -/
def retirementCap : Int := 48000
def dpsMonthlyFloor : Int := 1700

/-- § 36 odst. 2: zvláštní sazba 15 % on dividends (písm. a–d) and on interest; odst. 3: "Daň z příjmů vybíraná
zvláštní sazbou se zaokrouhluje na celé koruny dolů". -/
def withholdingRate : Int := 1500

/-- § 21 odst. 1: corporate rate "21 %", base "zaokrouhleného na celé tisíce Kč dolů". -/
def citRate : Int := 2100

/-! ### Paušální daň (§ 2a, § 7a, § 38lk) -/

/-- § 38lk odst. 7: the income-tax part of the monthly paušální záloha: "100 Kč" / "4 963 Kč" / "9 320 Kč". -/
def pausalTax (band : Nat) : Int := if band = 1 then 100 else if band = 2 then 4963 else 9320

/-! ## Social security (ZPSZ) -/

/-- § 7 odst. 1 písm. d): "u zaměstnance 7,1 % z vyměřovacího základu, z toho 0,6 % na nemocenské pojištění a 6,5 % na
důchodové pojištění". -/
def eeSocialRate : Int := 710

/-- § 7 odst. 1 písm. a): employer 24,8 %. -/
def erSocialRate : Int := 2480

/-- § 7 odst. 1 písm. e) bod 1: OSVČ 29,2 %. -/
def seSocialRate : Int := 2920

/-- § 15a odst. 1 and 5: "čtyřicetiosminásobku průměrné mzdy" = 2 234 736 Kč. -/
def socialCeiling : Int := 48 * avgWage

/-- § 5b odst. 1: OSVČ base "od roku 2024 55 % daňového základu". -/
def seSocialShare : Int := 5500

/-- § 14 odst. 5: monthly minimum base for hlavní činnost "35 % průměrné mzdy v roce 2025" = 16 294,95, rounded up to
16 295 (the ČSSZ figure; the minimum záloha 4 759 Kč = 29,2 % × 16 295 rounded up). Vedlejší: "nejméně 11 % průměrné
mzdy" = 5 121,27 → 5 122. -/
def seMinBaseMain : Int := 16295
def seMinBaseSide : Int := 5122

/-- Zákon 155/1995 § 10 odst. 2: a vedlejší OSVČ is insured only if its income reaches the rozhodná částka, "2,4násobek"
of VVZ 2023 × koeficient = 2,4 × 43 682 × 1,0658 = 111 735,07 → 111 736 Kč (ČSSZ's published 2025 figure). -/
def seSideThreshold : Int := 111736

/-- § 14 odst. 3: monthly bases in the paušální režim: band 1 = minimum base "zvýšeného o 15 %" (16 295 × 1,15 =
18 739,25 → 18 740, which reproduces the published 8 716 Kč band-1 záloha), band 2 "28 050 Kč", band 3 "42 900 Kč". -/
def pausalSocialBase (band : Nat) : Int := if band = 1 then 18740 else if band = 2 then 28050 else 42900

/-! ## Health insurance (ZPVZP, ZVZP) -/

/-- ZPVZP § 2 odst. 1: "13,5 % z vyměřovacího základu"; odst. 2: "zaokrouhluje na celé koruny směrem nahoru". -/
def healthRate : Int := 1350

/-- ZVZP § 9 odst. 2: "Pojistné za zaměstnance hradí z jedné třetiny zaměstnanec, ze dvou třetin zaměstnavatel". -/
def healthEeDen : Int := 3

/-- ZPVZP § 3 odst. 6 and 10: minimum base = minimum wage; the employee pays "13,5 % z rozdílu těchto základů". -/
def healthMinBaseEe : Int := minWage

/-- ZPVZP § 3a odst. 1–2: OSVČ base "50 % daňového základu", minimum "dvanáctinásobek 50 % průměrné mzdy"
(monthly 23 278,5 → 23 279; the minimum záloha 3 143 Kč). -/
def seHealthMinMonthly : Int := 23279

/-- ZPVZP § 3a odst. 5: paušální režim bases: band 1 the minimum, band 2 "319 200 Kč", band 3 "470 400 Kč" a year. -/
def pausalHealthYear (band : Nat) : Int :=
  if band = 1 then 12 * seHealthMinMonthly else if band = 2 then 319200 else 470400

/-! ## Přídavek na dítě (ZSSP, version 2025-05-01) -/

/-- § 17: entitled if "rozhodný příjem v rodině nepřevyšuje součin částky životního minima rodiny a koeficientu 3,40". -/
def pridavekCoefPct : Int := 340

/-- § 18 odst. 1 (basic) and odst. 3 (zvýšená výměra), per month, by age band (<6, 6–15, 15–26). -/
def pridavekBasic (age : Int) : Int := if age < 6 then 830 else if age < 15 then 970 else 1080
def pridavekRaised (age : Int) : Int := if age < 6 then 1330 else if age < 15 then 1470 else 1580

/-- NV 436/2022 Sb.: životní minimum (in force 2023-01-01 and through 2025): jednotlivec 4 860; first person 4 470;
further adult 4 040; dependent child 15–26 3 490, 6–15 3 050, under 6 2 480 Kč/month. -/
def zmSingle : Int := 4860
def zmFirst : Int := 4470
def zmAdult : Int := 4040
def zmChild (age : Int) : Int := if age < 6 then 2480 else if age < 15 then 3050 else 3490

/-! ## Withholding (§ 38h) -/

/-- § 38h odst. 2: 23 % above "3násobku průměrné mzdy" a month = 139 671 Kč. -/
def monthlyThreshold23 : Int := 3 * avgWage

/-- § 35d odst. 4 (monthly bonus at least 50 Kč) and the condition of half the minimum wage a month. -/
def monthlyBonusMin : Int := 50
def monthlyBonusIncomeMin : Int := minWage / 2

/-- Zákon 187/2006 Sb. § 7a odst. 1: a DPP is insured if the month's income reaches "25 % průměrné mzdy … po
zaokrouhlení na celé pětisetkoruny směrem dolů" = 11 639,25 → 11 500 Kč (2025). ZDP § 6 odst. 4 písm. a): below it the
income is a samostatný základ daně taxed by final withholding. -/
def dppLimit : Int := 11500

theorem threshold23_val : threshold23 = 1676052 := by decide
theorem socialCeiling_val : socialCeiling = 2234736 := by decide
theorem bonusIncomeMin_val : bonusIncomeMin = 124800 := by decide
theorem pensionExempt_val : pensionExempt = 748800 := by decide

/-! ## Tax years 2022–2024 (tests round 2, `cmp20/improve-emerging/IMPROVE.md`)

The parameters an employee household needs, each from the version of the text in force in that year (e-Sbírka API,
copies in `refs/esb/<name>/text.txt`, fetched 2026-11-19 by `tools/fetch_years.sh`):

* průměrná mzda (ZDP § 21g odst. 2 → ZPSZ: VVZ × koeficient, rounded up): 2022 = NV 356/2021 Sb. § 1 "36 119 Kč",
  "1,0773" → 38 911; 2023 = NV 290/2022 Sb. § 1 "38 294 Kč", "1,0530" → 40 324; 2024 = NV 286/2023 Sb. § 1
  "40 638 Kč", "1,0819" → 43 967 (refs/esb/nv356_2021, nv290_2022, nv286_2023).
* minimální mzda (NV 567/2006 Sb. § 2 odst. 1 at 2022-01-01, 2023-01-01, 2024-01-01): "16 200 Kč", "17 300 Kč",
  "18 900 Kč" a month.
* ZDP § 16 odst. 1 (refs/esb/itc_20220101, itc_20230101): "15 % pro část základu daně do 48násobku průměrné mzdy";
  2024 (itc_20240101): "do 36násobku průměrné mzdy".
* ZDP § 35ba odst. 1 písm. b) (2022, 2023): sleva na manžela 24 840 Kč "pokud nemá vlastní příjem přesahující za
  zdaňovací období 68 000 Kč" — no condition on the children; from 2024 § 35bb odst. 2 (a child under 3), as in 2025.
* ZDP § 35c odst. 1 (2022, 2023, 2024): "15 204 Kč ročně na jedno dítě, 22 320 Kč ročně na druhé dítě a 27 840 Kč ročně
  na třetí a každé další dítě" (as in 2025); odst. 3 "alespoň 100 Kč"; odst. 4 "šestinásobku minimální mzdy".
* ZDP § 35bc (2022, 2023 only; repealed from 2024): sleva za umístění dítěte = the fees paid, at most the minimum wage.
  Fees are not a contract input, so the statute mode never claims it (see `--oecd`).
* ZPSZ § 7 odst. 1 (refs/esb/ssc_2022…, ssc_2023…): 2022 písm. b) / 2023 písm. c) "u zaměstnance 6,5 % z vyměřovacího
  základu"; 2024 písm. c) "7,1 % … z toho 0,6 % na nemocenské pojištění"; § 15a odst. 1 "čtyřicetiosminásobku
  průměrné mzdy" in every year.
* ZSSP § 17 (2022–2024): coefficient "3,40"; § 18 odst. 1 and 3: 2022 (sss_20220101, unchanged at 2022-07-01) "630 Kč",
  "770 Kč", "880 Kč" and zvýšená výměra "1 130 Kč", "1 270 Kč", "1 380 Kč"; 2023 and 2024 "830 Kč", "970 Kč", "1 080 Kč"
  (zvýšená: + 500 Kč, as in 2025).
* životní minimum: NV 61/2020 Sb. (to 2022-03-31): 3 860 / 3 550 / 3 200 / 2 770 / 2 420 / 1 970 Kč; NV 75/2022 Sb.
  (from 2022-04-01): 4 250 / 3 910 / 3 530 / 3 050 / 2 670 / 2 170; NV 204/2022 Sb. (from 2022-07-01): 4 620 / 4 250 /
  3 840 / 3 320 / 2 900 / 2 360; NV 436/2022 Sb. (from 2023-01-01, still in force in 2025): the 2025 values above.

Not re-parametrised (the 2025 values are used, and the output says so for another year): OSVČ minimum bases and the
paušální režim, the DPP limit, withholding tables. -/

structure YearP where
  year : Int
  avgWage : Int
  minWage : Int
  thrMult : Int
  eeSocialRate : Int
  spouseNeedsChildUnder3 : Bool
  skolkovne : Bool
  pridBasic : Int × Int × Int
  pridRaised : Int × Int × Int
  deriving Repr

def YearP.threshold23 (p : YearP) : Int := p.thrMult * p.avgWage
def YearP.socialCeiling (p : YearP) : Int := 48 * p.avgWage
def YearP.bonusIncomeMin (p : YearP) : Int := 6 * p.minWage
def YearP.pensionExempt (p : YearP) : Int := 36 * p.minWage
def YearP.pridavek (p : YearP) (raised : Bool) (age : Int) : Int :=
  let t := if raised then p.pridRaised else p.pridBasic
  if age < 6 then t.1 else if age < 15 then t.2.1 else t.2.2

def yearP2025 : YearP :=
  { year := 2025, avgWage := avgWage, minWage := minWage, thrMult := 36, eeSocialRate := eeSocialRate,
    spouseNeedsChildUnder3 := true, skolkovne := false, pridBasic := (830, 970, 1080), pridRaised := (1330, 1470, 1580) }

/-- The parameters of tax year `y` (2022–2025; other years: 2025's). -/
def yearP (y : Int) : YearP :=
  if y = 2022 then
    { year := 2022, avgWage := 38911, minWage := 16200, thrMult := 48, eeSocialRate := 650,
      spouseNeedsChildUnder3 := false, skolkovne := true, pridBasic := (630, 770, 880), pridRaised := (1130, 1270, 1380) }
  else if y = 2023 then
    { year := 2023, avgWage := 40324, minWage := 17300, thrMult := 48, eeSocialRate := 650,
      spouseNeedsChildUnder3 := false, skolkovne := true, pridBasic := (830, 970, 1080), pridRaised := (1330, 1470, 1580) }
  else if y = 2024 then
    { year := 2024, avgWage := 43967, minWage := 18900, thrMult := 36, eeSocialRate := 710,
      spouseNeedsChildUnder3 := true, skolkovne := false, pridBasic := (830, 970, 1080), pridRaised := (1330, 1470, 1580) }
  else yearP2025

/-- životní minimum of one month: (jednotlivec, first person, further adult, child 15–26, 6–15, under 6). -/
structure ZmP where
  single : Int
  first : Int
  adult : Int
  c15 : Int
  c6 : Int
  c0 : Int
  deriving Repr

def zmP (y : Int) (month : Nat) : ZmP :=
  if y = 2022 ∧ month ≤ 3 then ⟨3860, 3550, 3200, 2770, 2420, 1970⟩
  else if y = 2022 ∧ month ≤ 6 then ⟨4250, 3910, 3530, 3050, 2670, 2170⟩
  else if y = 2022 then ⟨4620, 4250, 3840, 3320, 2900, 2360⟩
  else ⟨zmSingle, zmFirst, zmAdult, zmChild 15, zmChild 6, zmChild 0⟩

def ZmP.child (z : ZmP) (age : Int) : Int := if age < 6 then z.c0 else if age < 15 then z.c6 else z.c15

theorem yearP_2025_same : (yearP 2025).threshold23 = threshold23 ∧ (yearP 2025).socialCeiling = socialCeiling ∧
    (yearP 2025).bonusIncomeMin = bonusIncomeMin ∧ (yearP 2025).pensionExempt = pensionExempt := by decide
/-- VVZ × koeficient rounded up to the crown gives the průměrná mzda used above for each year. -/
theorem avgWage_years : cdiv (36119 * 10773) 10000 = (yearP 2022).avgWage ∧ cdiv (38294 * 10530) 10000 = (yearP 2023).avgWage ∧
    cdiv (40638 * 10819) 10000 = (yearP 2024).avgWage := by decide
theorem threshold_2022 : (yearP 2022).threshold23 = 1867728 ∧ (yearP 2023).threshold23 = 1935552 ∧
    (yearP 2024).threshold23 = 1582812 := by decide

end CzTax
