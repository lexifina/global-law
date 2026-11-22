import TaxKernel

/-!
# Hungary 2025: parameters, each with its source

Statute copies (net.jogtar.hu, Wolters Kluwer's free consolidated text, versioned by `timeshift`; njt.hu refused
connections from both of our hosts on 2026-11-19) are in `cmp20/central/hu/refs/jogtar/`:
* Szja tv. = 1995. évi CXVII. törvény a személyi jövedelemadóról: versions 2024.I.1, 2025.I.1, 2025.I.2-II.28,
  2025.VII.1-VII.19, 2025.X.1-X.27, 2026.X.1 (`szja_*.txt`);
* Tbj. = 2019. évi CXXII. törvény (2025.I.1, 2025.VII.1); Szocho tv. = 2018. évi LII. törvény (2025.I.1);
* Cst. = 1998. évi LXXXIV. törvény a családok támogatásáról (2025.I.1); 2025. évi XV. törvény (three-children mothers,
  2025.X.1); Kata tv. = 2022. évi XIII. törvény; Katv. (KIVA) = 2012. évi CXLVII. törvény.
NAV information booklets 2025 (`refs/nav/nav<NN>.txt`): 73 "Szja adóalap-kedvezmények" (published 2025-09-16),
100 átalányadózás, 99 KATA, 92 KIVA, 49 szocho, 12, 72.
Money: whole forints. Rates: basis points.
-/

namespace HuTax
open TaxKernel

/-- Szja tv. § 8 (1): "az adó mértéke ... az adóalap 15 százaléka". -/
def pitRate : Int := 1500

/-- Szja tv. § 29/A (2), version 2025.I.2-2025.VI.30 (`szja_20250102.txt`): the family allowance per beneficiary per
month "egy eltartott esetén 66 670 forint, kettő eltartott esetén 133 330 forint, három és minden további eltartott
esetén 220 000 forint" (index = number of dependants - 1; three or more: the last entry). -/
def famH1 : List Int := [66670, 133330, 220000]

/-- Szja tv. § 29/A (2) as set by 2024. évi LV. törvény 4. § (1), in force 2025.VII.1 (`szja_20250701.txt`):
"100 000 forint ... 200 000 forint ... 330 000 forint". NAV 73 § 9.4 applies it to the months July-December 2025
(no transitional rule is needed: the amount is "jogosultsági hónaponként"). -/
def famH2 : List Int := [100000, 200000, 330000]

/-- Szja tv. § 29/A (2a): supplement per long-term ill or severely disabled beneficiary per month: 66 670 forint
(2025.I.2 version), 100 000 forint (2025.VII.1 version). -/
def famDisabledH1 : Int := 66670
def famDisabledH2 : Int := 100000

/-- The 2026 amounts (`szja_jogtar_2026-11-19.txt`, version 2026.X.1): 133 340 / 266 660 / 440 000, supplement
133 340. Used only for the year-shift scans (not in 2025 results). -/
def fam2026 : List Int := [133340, 266660, 440000]

/-- Szja tv. § 29/F (2): the under-25 allowance is the youth's qualifying income, "de adóévenként legfeljebb a
jogosultsági hónapok számának és a tárgyévet megelőző év július hónapjára vonatkozóan közzétett nemzetgazdasági szintű
bruttó átlagkeresetnek a szorzata"; NAV 73 § 5.2: "A kedvezmény havi összege 2025-ben 656 785 forint". -/
def youthCapMonthly : Int := 656785

/-- Szja tv. § 29/G (3): the under-30 mothers' allowance has the same monthly cap (NAV 73 § 6.2: 656 785 forint). -/
def under30CapMonthly : Int := 656785

/-- Szja tv. § 29/E (3): "a minimálbér egyharmada száz forintra kerekítve"; NAV 73 § 7: 96 900 forint a month in
2025 (minimum wage 290 800). -/
def personalMonthly : Int := 96900

/-- Szja tv. § 29/C (3): first-marriage allowance "jogosultsági hónaponként 33 335 forint" for the couple together,
§ 29/C (4): at most 24 months from the month after the wedding. -/
def firstMarriageMonthly : Int := 33335

/-- Tbj. § 25 (1): "A társadalombiztosítási járulék mértéke 18,5 százalék" (no ceiling). -/
def tbRate : Int := 1850

/-- Tbj. § 34 (3): the family contribution allowance is "15 százaléka" of the family allowance not used against tax,
"de legfeljebb a társadalombiztosítási járulék ... összege". -/
def famContribRate : Int := 1500

/-- Szja tv. § 29/B (6): a family that used the contribution allowance during the year has its annual family
allowance reduced by the allowance "az adó mértékére vonatkozó rendelkezés szerinti mértékkel elosztott része
(667 százaléka)": 1/15 % = 666.67 %, printed as 667 % (finding F2). In basis points of the contribution allowance. -/
def famContribGrossUpBp : Int := 66700

/-- Szocho tv. § 2 (1): "Az adó mértéke az adóalap 13 százaléka". -/
def szochoRate : Int := 1300

/-- NAV 73 footnote 11 and NAV 100 § 6: "2025-ben a havi minimálbér 290 800 forint", "a garantált bérminimum
összege 348 800 forint". -/
def minWage : Int := 290800
def guaranteedMinWage : Int := 348800

/-- Szocho tv. § 2 (2): on income under § 1 (5) a)-e) (business withdrawals, securities lending, dividends,
capital gains, ...) the tax is due "amíg a természetes személy 1. § (1)–(3) bekezdés és az 1. § (5) bekezdés a)–e)
pontja szerinti jövedelme a tárgyévben eléri a minimálbér összegének huszonnégyszeresét". Interest (§ 1 (5) f)) is
outside the a)-e) list: no ceiling. -/
def szochoCapitalCeiling : Int := 24 * minWage

/-- Szja tv. 1. számú melléklet 4.48.: tax-free "az átalányadózást alkalmazó egyéni vállalkozó e tevékenységéből
származó jövedelmének az éves minimálbér felét meg nem haladó rész"; NAV 100 § 3: 1 744 800 forint in 2025. -/
def atalanyFree : Int := 6 * minWage

/-- NAV 100 § 6 (Tbj. § 40 and Szocho tv. minimum bases for the self-employed): a main-occupation sole trader pays
TB on at least the minimum wage (guaranteed minimum wage if the activity needs secondary qualification) and szocho
on at least 112.5 % of it: "2025-ben a szociális hozzájárulási adó alapja havonta legalább 327 150 forint, garantált
bérminimum alkalmazásakor 392 400 forint". -/
def szochoMinMonthly : Int := 327150
def szochoMinMonthlySkilled : Int := 392400

/-- Szja tv. § 53 (1)-(2), NAV 100 § 3: flat-rate expense ratio 40 % in general, 80 % for listed activities, 90 %
for retail only (basis points). -/
def atalanyCostDefault : Int := 4000

/-- Cst. § 11 (1) (version 2025.I.1, `cst_20250101.txt`): monthly családi pótlék per child, by the number of children
counted (one, two, three or more): couple family a) 12 200, c) 13 300, e) 16 000; lone parent b) 13 700, d) 14 800,
f) 17 000 forint. -/
def cspCouple : List Int := [12200, 13300, 16000]
def cspSingle : List Int := [13700, 14800, 17000]

/-- Kata tv. 8. § (NAV 99 § 4.1): "havi 50 ezer forint tételes adót"; 7. § (4)-(5) (NAV 99 § 4.2): 40 % on revenue
above 18 million forint a year, pro rata 1.5 million per month of liability. -/
def kataMonthly : Int := 50000
def kataRevenuePerMonth : Int := 1500000
def kataExcessRate : Int := 4000

/-- Katv. (KIVA, 2012. évi CXLVII.) 20. §, NAV 92: "Az adó mértéke az adóalap 10 százaléka" (company side; for the
owner-manager scan in `harness/search/company.json`). -/
def kivaRate : Int := 1000

/-- Earlier years (improvement round 1, 2026-11-19): Szja tv. § 29/A (2) in the versions of 2022.I.1 and 2023.I.1
(net.jogtar.hu timeshift, copies in `cmp20/improve-central/refs/hu/szja_2022*.txt`, `szja_2023*.txt`) and 2024.I.1
(`refs/jogtar/szja_20240101.txt`) reads "a) egy eltartott esetén 66 670 forint, ... bd) 2019-ben és az azt követő
években 133 330 forint, c) három és minden további eltartott esetén 220 000 forint": the `famH1` amounts for all
twelve months of 2022, 2023 and 2024 (the increase starts 2025.VII.1). Tbj. § 25 (1) "A társadalombiztosítási
járulék mértéke 18,5 százalék" in the 2022.I.1 and 2024.I.1 versions (`improve-central/refs/hu/tbj_*.txt`); Szja
tv. § 8 (1) 15 % and § 29/C (3) 33 335 forint in the 2022.I.1 and 2023.I.1 versions; Cst. § 11 amounts unchanged
since 2009.I.1 (`refs/jogtar/cst_20090101.html`). Years the model computes with year-specific family allowances. -/
def earliestYear : Nat := 2022

/-- Months of the year at the July-2025 amounts: 6 in 2025, 0 before. -/
def monthsAtNewAmounts (year : Nat) : Int := if year ≥ 2025 then 6 else 0

/-- The months of 2025 in each half: § 29/A (2) old amounts January-June, new amounts July-December. -/
def monthsH1 : Int := 6
def monthsH2 : Int := 6

/-! ## Minimum-wage-based amounts for 2023 and 2024 (improvement round 2, 2026-11-19)

Minimum wage and guaranteed minimum (Nemzeti Jogszabálytár copies in `cmp20/improve-central/refs/hu/`):
* 2023: 573/2022. (XII. 23.) Korm. rendelet 2. § (3) "a) az (1) bekezdés szerinti kötelező legkisebb összege 2023.
  január 1-jétől 232 000 forint, b) ... garantált bérminimum összege 2023. január 1-jétől 296 400 forint"
  (`mw_njt_2022_573.txt`);
* 2024: 508/2023. (XI. 20.) Korm. rendelet 2. § (3) "2023. december 1-jétől 266 800 forint", "2023. december 1-jétől
  326 000 forint" (`mw_njt_2023_508.txt`), in force for all of 2024.
* 2022: the decree was not fetched: 2022 keeps the 2025 amounts (stated in `unsupported`).
Derived amounts, by the same provisions as in 2025: Szja tv. § 29/E (3) "a minimálbér egyharmada száz forintra
kerekítve" (2023.I.1 version, `szja_20230101.txt`); Szja tv. 1. sz. melléklet 4.48. (half the annual minimum wage
tax-free for átalány); Szocho tv. § 8 (3) "legalább a minimálbér 112,5 százaléka" (2023.I.1 and 2024.I.1 versions,
`szocho_2023*.txt`, `szocho_2024*.txt`); Szocho tv. § 2 (2) "a minimálbér összegének huszonnégyszeresét"; Szocho tv.
§ 2 (1) "Az adó mértéke az adóalap 13 százaléka" in the 2022.I.1, 2023.I.1 and 2024.I.1 versions (13 % already on
2022.I.1: no 15,5 % months in 2022). Szocho tv. § 1 (5) f) (interest) is empty in the 2022.I.1, 2023.I.1 and 2024.I.1
versions and in force in the 2025.I.1 one: no szocho on interest under the Act before 2025 (the 2023 emergency
decree on interest is not modelled; stated in `unsupported`). -/
/-- Szja tv. 3. § 77. (2023.I.1 version; same in 2022.I.1): "Minimálbér: ... az év első napján érvényes kötelező
legkisebb munkabér havi összege" (also Szocho tv. 11. pont for its general rules): the amount of 1 January.
2022 (round 4): 703/2021. (XII. 15.) Korm. rendelet 2. § (3) "a) az (1) bekezdés szerinti kötelező legkisebb összege
2022. január 1-jétől 200 000 forint, b) a (2) bekezdés szerinti garantált bérminimum összege 2022. január 1-jétől
260 000 forint" (`improve-central/refs/hu/mw_njt_2021_703.txt`, Nemzeti Jogszabálytár). -/
def minWageFor (y : Nat) : Int :=
  if y = 2022 then 200000 else if y = 2023 then 232000 else if y = 2024 then 266800 else minWage
def guaranteedMinWageFor (y : Nat) : Int :=
  if y = 2022 then 260000 else if y = 2023 then 296400 else if y = 2024 then 326000 else guaranteedMinWage
/-- § 29/E (3): a third of the minimum wage, rounded to 100 forint (half up): 200 000 / 3 = 66 667 -> 66 700. -/
def personalMonthlyFor (y : Nat) : Int :=
  if y = 2022 then 66700 else if y = 2023 then 77300 else if y = 2024 then 88900 else personalMonthly

/-- Tbj. 4. § 14.1-14.2 (2024.I.1 version) and Szocho tv. 11. pont (the rules for sole traders): the minimum wage
(guaranteed minimum for a skilled main activity) "a tárgyhónap első napján érvényes": month by month. 508/2023.
(XI. 20.) Korm. rendelet 2. § (3) and 3. §: 266 800 / 326 000 forint "2023. december 1-jétől", so December 2023 is
at the new amounts (round 4). -/
def minWageMonth (y m : Nat) : Int := if y = 2023 ∧ m = 12 then 266800 else minWageFor y
def guaranteedMinWageMonth (y m : Nat) : Int := if y = 2023 ∧ m = 12 then 326000 else guaranteedMinWageFor y
/-- The year's minimum TB base of a main-occupation sole trader (Tbj. § 29 (3)/§ 40: "havonta legalább a minimálbér"). -/
def tbMinYearFor (y : Nat) (skilled : Bool) : Int :=
  ((List.range 12).map fun i => if skilled then guaranteedMinWageMonth y (i + 1) else minWageMonth y (i + 1)).foldl (· + ·) 0
/-- The year's minimum szocho base of a sole trader (Szocho tv. § 8 (3): "havonta ... legalább a minimálbér 112,5
százaléka"), month by month. -/
def szochoMinYearFor (y : Nat) (skilled : Bool) : Int :=
  ((List.range 12).map fun i =>
    1125 * (if skilled then guaranteedMinWageMonth y (i + 1) else minWageMonth y (i + 1)) / 1000).foldl (· + ·) 0

/-- Szja tv. § 29/F (2): the under-25 cap per month is the KSH national average gross wage "a tárgyévet megelőző év
július hónapjára vonatkozóan közzétett". 2022 (round 4): KSH Gyorstájékoztató "Keresetek, 2021. július"
(https://www.ksh.hu/docs/hun/xftp/gyor/ker/ker2107.html, copy `improve-central/refs/hu/ksh/ker2107.html`): "433 700
forint volt a bruttó átlagkereset 2021 júliusában". 2023 and 2024: the July 2022 release prints the rounded headline
"500 000 forint" (ker2207.html), the July 2023 page is gone (404): not cited, so the 2025 cap is kept (stated). -/
def youthCapFor (y : Nat) : Int := if y = 2022 then 433700 else youthCapMonthly
def atalanyFreeFor (y : Nat) : Int := 6 * minWageFor y
def szochoMinMonthlyFor (y : Nat) : Int := if y = 2023 ∨ y = 2024 then 1125 * minWageFor y / 1000 else szochoMinMonthly
def szochoMinMonthlySkilledFor (y : Nat) : Int :=
  if y = 2023 ∨ y = 2024 then 1125 * guaranteedMinWageFor y / 1000 else szochoMinMonthlySkilled
def szochoCapitalCeilingFor (y : Nat) : Int := 24 * minWageFor y
/-- Szocho tv. § 1 (5) f): szocho on interest only from the 2025.I.1 version on. -/
def interestSzochoFor (y : Nat) : Bool := y ≥ 2025 || y < 2022

theorem year_amounts_2022 :
    personalMonthlyFor 2022 = divR .halfUp (minWageFor 2022) 300 * 100 ∧
    tbMinYearFor 2023 false = 11 * 232000 + 266800 ∧ szochoMinYearFor 2023 false = 11 * 261000 + 300150 ∧
    tbMinYearFor 2025 false = 12 * minWage ∧ tbMinYearFor 2025 true = 12 * guaranteedMinWage ∧
    szochoMinYearFor 2025 false = 12 * szochoMinMonthly ∧ szochoMinYearFor 2025 true = 12 * szochoMinMonthlySkilled ∧
    youthCapFor 2025 = youthCapMonthly := by decide

theorem year_amounts :
    (personalMonthlyFor 2023, personalMonthlyFor 2024) = (77300, 88900) ∧
    -- a third of the minimum wage to the nearest 100: 232 000 / 3 = 77 333, 266 800 / 3 = 88 933
    (divR .halfUp (minWageFor 2023) 300 * 100, divR .halfUp (minWageFor 2024) 300 * 100) = (77300, 88900) ∧
    (szochoMinMonthlyFor 2023, szochoMinMonthlySkilledFor 2023, szochoMinMonthlyFor 2024,
      szochoMinMonthlySkilledFor 2024) = (261000, 333450, 300150, 366750) ∧
    (szochoMinMonthlyFor 2025, personalMonthlyFor 2025, atalanyFreeFor 2025, szochoCapitalCeilingFor 2025) =
      (szochoMinMonthly, personalMonthly, atalanyFree, szochoCapitalCeiling) := by decide

end HuTax
