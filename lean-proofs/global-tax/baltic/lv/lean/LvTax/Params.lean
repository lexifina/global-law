import TaxKernel

/-!
# Latvia, tax year 2025: parameters, each with its provision and a short quote

Unit of account: **euro cents** (likums "Par iedzīvotāju ienākuma nodokli" (IIN) 16. panta 1. daļa: "Ienākumi,
attaisnotie izdevumi ... tiek noteikti euro"; VID computes and declares euro with cents). Rates in basis points.

Texts (likumi.lv consolidated versions, saved under `~/cmp20/baltic/lv/refs/`):
* IIN likums (https://likumi.lv/ta/id/56880), redakcija 16.05.2025-31.12.2025 (`iin_2025-05-16.txt`; also
  01.01.2025 and 01.01.2024 for history, and the 2026 text `iin_2026current.txt`);
* likums "Par valsts sociālo apdrošināšanu" (VSAOI, https://likumi.lv/ta/id/45466), redakcija 01.01.2025;
* Solidaritātes nodokļa likums (https://likumi.lv/ta/id/278636);
* Valsts sociālo pabalstu likums (VSPL, https://likumi.lv/ta/id/68483), redakcija 01.01.2025-31.12.2025;
* Mikrouzņēmumu nodokļa likums (MUN, https://likumi.lv/ta/id/215302), redakcija 01.01.2025;
* Uzņēmumu ienākuma nodokļa likums (UIN, https://likumi.lv/ta/id/292700), redakcija 01.01.2024-31.12.2025;
* LV portāls e-konsultācijas 37184 (1 Oct 2025) and 37449 (VID, 6 Nov 2025) for the self-employed contribution
  rule of VSAOI 14.1 pants and the 2025 minimum wage (`refs/lvp_37184.txt`, `refs/lvp_37449.txt`).
-/

namespace LvTax
open TaxKernel

/-- Whole euros to cents. -/
def eur (x : Int) : Int := 100 * x

/-- VSAOI 14. panta 5. daļa: "Obligāto iemaksu un brīvprātīgo iemaksu objekta maksimālais apmērs gadā ir
105 300 euro." The IIN schedule's band limit is this amount (IIN 15. panta 2. daļa). -/
def maxObject : Int := eur 105300

/-- IIN 15. panta 2. daļa (2025): "1) 25,5 procenti — gada ienākuma daļai, kas nepārsniedz likumā "Par valsts
sociālo apdrošināšanu" noteikto obligāto iemaksu objekta maksimālo apmēru; 2) 33 procenti — gada ienākuma daļai,
kas pārsniedz ...". Applied to the annual **income** (15. panta 21. daļa: without the art. 9 exempt income), not to
the taxable income: the deductions come off the part up to the maximum object first (3. panta 2.4 daļa, 15. panta
15. daļa), so they are worth 25,5 % (`taxAfterLowBand`, see `Basic.lean`). -/
def iinSched : Schedule := Schedule.ofList [(0, 2550), (10530000, 3300)]

/-- IIN 15. panta 3. daļa: "Algas nodokļa likme, kas jāmaksā no mēneša apliekamā ienākuma ... ir 25,5 procenti"
(monthly withholding: one rate, no 33 % band during the year). -/
def wageRate : Int := 2550

/-- IIN pārejas noteikumi 197. punkts: "mēneša neapliekamais minimums: 1) 2025. gadā ir 510 euro mēnesī".
(12. panta 1. daļa itself says 570 euro: that is the amount from 2027; see FINDINGS F6.) -/
def ntmMonth : Int := eur 510
/-- 12. panta 1. daļa: "Gada neapliekamais minimums ir visu gada mēnešu neapliekamo minimumu summa". -/
def ntmYear : Int := 12 * ntmMonth
/-- 12. panta 5. daļa: for a person granted a pension "neapliekamais minimums ir 12 000 euro gadā (šā likuma
izpratnē — pensionāra neapliekamais minimums)". -/
def ntmPensioner : Int := eur 12000

/-- 13. panta 1.2 daļa: "nodokļa atvieglojums par apgādībā esošu personu ir 250 euro mēnesī". -/
def depMonth : Int := eur 250
def depYear : Int := 12 * depMonth

/-- 15. panta 5. daļa (2025): "Nodokļa likmi 25,5 procentu apmērā piemēro ienākumam no kapitāla, tai skaitā no
kapitāla pieauguma." No neapliekamais minimums (12. panta 9. daļa) and no deductions (3. panta 2.5 daļa). -/
def capitalRate : Int := 2550

/-- 15. panta 6. daļas 3. punkts with 11. panta 12. daļa: rent received without registering a business, 10 % of
the receipts ("Nodokļa likmi 10 procentu apmērā piemēro: ... 3) šā likuma 11. panta divpadsmitajā daļā minētajam
ienākumam"); only the real-estate tax may be deducted (not modelled). -/
def rentRate : Int := 1000

/-- 15.1 pants 1. daļa: "Nodokļa papildu likme, kas jāmaksā rezumējošā kārtībā no kopējā ... taksācijas gada
ienākumu pārsnieguma virs 200 000 euro, ir trīs procenti"; 2. daļa: the base includes all taxable income "tai
skaitā ienākumi no kapitāla pieauguma un ienākumi no kapitāla" and the exempt dividends of 9. panta 1. daļas
2.1 punkts. -/
def surtaxRate : Int := 300
def surtaxThreshold : Int := eur 200000
/-- The additional rate as a kernel surcharge on the income above the threshold. -/
def surtax : Surcharge := Surcharge.above surtaxRate surtaxThreshold

/-- VSAOI 18. panta 1. daļa: "Obligāto iemaksu likme ... ir 34,09 procenti, no kuriem 23,59 procentus maksā darba
devējs un 10,50 procentus — darba ņēmējs." -/
def eeRate : Int := 1050
def erRate : Int := 2359
/-- A working old-age pensioner (VSAOI 20. panta 4. daļas 1. punkts: not insured against unemployment and
disability): employee share 9,25 % (MK 17.12.2020. noteikumi Nr. 786, as quoted in VID "Algas nodoklis 2025",
p. 4: "pensionāram ir 30,02 % (darba ņēmēja daļa 9,25 %, darba devēja daļa 20,77 %)"). -/
def eeRatePensioner : Int := 925

/-- Solidaritātes nodokļa likums 6.1 pants: "Nodokļa likme ir 25 procenti"; 6.2 pants 1. daļa: during the year
the full contribution rate applies above the maximum object; 3. daļa: the overpaid tax is refunded "tikai darba
devējam". 8.1 pants 3. punkts: 10 percentage points go "iedzīvotāju ienākuma nodokļa ieņēmumos". IIN 10. panta
1.10 daļa: the deductible contributions "ir samazināms par summu, kas ... ir pārskaitīta iedzīvotāju ienākuma
nodokļa sadales kontā". -/
def solidRate : Int := 2500
def solidIinShare : Int := 1000

/-- 2025 minimum monthly wage 740 euro (MK noteikumi; quoted in LV portāls 37184 and VID's answer 37449: "ja
ienākumi mēnesī ≥ 740 eiro (minimālā alga 2025. gadā)"). -/
def minWage : Int := eur 740

/-- Self-employed (VSAOI 14.1 pants, as quoted in LV portāls 37184): income below the minimum wage in a month:
"obligātās iemaksas pensiju apdrošināšanai 10 procentu apmērā no ienākuma"; at or above it: 31,07 % on an object
of at least the minimum wage plus 10 % "no brīvi izraudzītā obligāto iemaksu objekta un faktisko ienākumu
starpības" (the rate 31,07 %: VID 37449 "jāmaksā 31,07% no vismaz 740 eiro"). -/
def seFullRate : Int := 3107
def sePensionRate : Int := 1000

/-- IIN 10. panta 1.3 daļa: donations and medical/education costs together "nedrīkst pārsniegt 50 procentus no
maksātāja taksācijas gada apliekamā ienākuma lieluma, bet ne vairāk kā 600 euro". -/
def donationCap : Int := eur 600
def donationPct : Int := 5000
/-- IIN 10. panta 1.9 daļa: private pension and life-insurance premiums "nedrīkst pārsniegt 10 procentus no
maksātāja gada ienākuma lieluma ... bet ne vairāk kā 4000 euro gadā". -/
def pensionCap : Int := eur 4000
def pensionPct : Int := 1000

/-- IIN pārejas noteikumi 164. punkts: royalties of an author not registered as a business: tax withheld "piemērojot
maksātāja ieņēmumiem 25 procentu likmi"; 170. punkts: not in the progressive base, no 10., 12., 13. panta
deductions; 171. punkts: "80 procentus attiecina uz valsts sociālās apdrošināšanas obligātajām iemaksām", "20
procentus attiecina uz iedzīvotāju ienākuma nodokli"; 200. punkts: outside the 3 % additional rate. -/
def royaltyRate : Int := 2500
def royaltySocialShare : Int := 8000

/-- MUN 6. pants: "Mikrouzņēmumu nodokļa likme ir 25 procenti" of the turnover (5. panta 3. daļa); the tax
covers the owner's VSAOI and IIN (1. panta 4. punkts). Eligibility: turnover up to the VAT registration threshold
(4. panta 1. daļas 1. punkts), 50 000 euro in 2025 (VID's answer 37449: "plānotie ieņēmumi nesasniegs 50 000
eiro"). -/
def microRate : Int := 2500
def microCap : Int := eur 50000

/-- VSPL 6. panta 2.2 daļa: "Ģimenes valsts pabalsta apmērs ir: 1) par vienu bērnu — 25 euro mēnesī; 2) par
diviem bērniem — 100 euro mēnesī; 3) par trim bērniem — 225 euro mēnesī; 4) par četriem un vairāk bērniem — 100
euro mēnesī par katru bērnu." -/
def fvpMonth (n : Nat) : Int := familyTotal [eur 25, eur 100, eur 225, eur 400] (eur 100) n

/-- UIN 3. panta 1. daļa: "Nodokļa likme ir 20 procenti no aprēķinātās ar nodokli apliekamās bāzes, kura pirms
nodokļa likmes piemērošanas koriģēta saskaņā ar šā likuma 4. panta devīto daļu" (the 4(9) gross-up: base = net
distribution / 0,8). Used by the owner-manager scan (company.json), not by the household exe. -/
def citRate : Int := 2000

/-! ## Earlier years 2022-2024 (round 2, 2026-11-19)

Texts fetched from likumi.lv by redaction date (`refs/iin_2022-01-01.txt`, `iin_2023-01-01.txt`,
`iin_2024-01-01.txt`; `vsaoi_<y>-01-01.txt`; `vspl_<y>-01-01.txt`; MK 2017. gada 14. novembra noteikumi Nr. 676
`mk676_<y>-01-01.txt`, id 295500). -/

/-- IIN 15. panta 2. daļa (redactions 1.1.2022, 1.1.2023, 1.1.2024): "1) 20 procenti — gada ienākumam līdz 20 004
euro; 2) 23 procenti — gada ienākuma daļai, kas pārsniedz 20 004 euro, bet nepārsniedz ... obligāto iemaksu objekta
maksimālo apmēru; 3) 31 procents — ... kas pārsniedz ... maksimālo apmēru". VSAOI 14. panta 5. daļa (same
redactions): "maksimālais apmērs gadā ir 78 100 euro". -/
def maxObject2224 : Int := eur 78100
def iinSched2224 : Schedule := Schedule.ofList [(0, 2000), (eur 20004, 2300), (maxObject2224, 3100)]

/-- The year's schedule, lowest rate (every euro of deduction is worth it: 3. panta 2.4 daļa, 15. panta 15. daļa
"... reizinot ar nodokļa likmi 20 procentu apmērā" in 2022-2024) and maximum object. -/
def schedFor (y : Nat) : Schedule := if y ≤ 2024 then iinSched2224 else iinSched
def lowRateFor (y : Nat) : Int := if y ≤ 2024 then 2000 else wageRate
def maxObjectFor (y : Nat) : Int := if y ≤ 2024 then maxObject2224 else maxObject

/-- IIN 15. panta 5. daļa (2022-2024): "Nodokļa likmi 20 procentu apmērā piemēro ienākumam no kapitāla". -/
def capitalRateFor (y : Nat) : Int := if y ≤ 2024 then 2000 else capitalRate

/-- The 3 % additional rate (15.1 pants) does not exist in the 2022-2024 redactions. -/
def hasSurtax (y : Nat) : Bool := 2025 ≤ y

/-- IIN 12. panta 5. daļa: the pensioner's minimum "ir 3960 euro gadā" (1.1.2022 redaction; the mid-2022 increase is
not modelled), "ir 6000 euro gadā" (1.1.2023 and 1.1.2024 redactions). -/
def ntmPensionerFor (y : Nat) : Int := if y ≤ 2022 then eur 3960 else if y ≤ 2024 then eur 6000 else ntmPensioner

/-- The differentiated non-taxable minimum (IIN 12. panta 1. daļa, 1.1 daļa; MK noteikumi Nr. 676, 2. punkts
"GDNM = GNMmax – K x (AI – AImin)"). 2023 and 2024 (3. punkts): "3.1. maksimālais gada neapliekamais minimums – 6000
euro; 3.2. ... līdz kuram piemēro maksimālo ... – 6000 euro; 3.3. ... virs kura nepiemēro ... – 21 600 euro;
3.4. koeficients – 0,38462". 2022 (2.1 and 3.1 punkts, MK 07.12.2021 Nr. 804): GDNM = DNM1 + DNM2, 1 January -
30 June "maksimālais neapliekamais minimums – 2100 euro", AImin 3000, AImax 10 800, "koeficients – 0,26923";
1 July - 31 December 3000 euro, 3000, 10 800, "koeficients – 0,38462". AI is the person's taxable income of the
period (4.1 punkts: all income, including that taxed at reduced rates); the half-year incomes are taken as half the
year's (income spread evenly; stated assumption). Never below 0 (above AImax "nepiemēro"). Cents; K in 10^-5. -/
def dnm (mx aiMin k5 ai : Int) : Int := max 0 (min mx (mx - divR .halfUp (k5 * (ai - aiMin)) 100000))
def ntmFor (y : Nat) (ai : Int) : Int :=
  if y ≤ 2022 then dnm (eur 2100) (eur 3000) 26923 (ai / 2) + dnm (eur 3000) (eur 3000) 38462 (ai - ai / 2)
  else if y ≤ 2024 then dnm (eur 6000) (eur 6000) 38462 ai
  else ntmYear

/-- MK noteikumi Nr. 676 (redactions 1.1.2022, 1.1.2023, 1.1.2024): "nodokļa atvieglojums par apgādībā esošu
personu ir 250 euro mēnesī" (as `depMonth`). VSAOI 18. panta 1. daļa (1.1.2022 redaction): "34,09 procenti, no kuriem
23,59 procentus maksā darba devējs un 10,50 procentus — darba ņēmējs" (as `eeRate`). VSPL 6. panta 2.2 daļa
(1.1.2022, 2023, 2024 redactions): "1) par vienu bērnu — 25 euro mēnesī; 2) par diviem bērniem — 100 euro mēnesī;
3) par trim bērniem — 225 euro mēnesī; 4) par četriem un vairāk bērniem — 100 euro mēnesī par katru bērnu" (as
`fvpMonth`). -/
def depMonthFor (_y : Nat) : Int := depMonth

end LvTax
