import TaxKernel

/-!
# Croatia 2025: parameters, each with its source

Money is in **euro cents** (`Int`) inside the model: the statute and the payroll forms state amounts in euros and
cents; the output contract carries whole euros (rounded half-up at the end). Rates are basis points.

Sources (copies under `hr/refs/`, fetched 2026-11-19):
* ZPD = Zakon o porezu na dohodak, NN 115/16 (`refs/nn115_2016_ZPD.txt`) as amended by NN 106/18, 121/19, 32/20,
  138/20, 151/22, 114/23 (`refs/nn114_2023_ZPD.txt`, the 2024 reform) and 152/24 (`refs/nn152_2024_ZPD_amend.txt`,
  in force 2025-01-01). No amendment in force during 2025 changes the provisions used here.
* ZD = Zakon o doprinosima, NN 84/08 (`refs/nn84_2008_ZD.txt`) as amended (NN 115/16, 106/18, 114/23 art. 21.a,
  152/24); Naredba o iznosima osnovica za obračun doprinosa za 2025., NN 137/24 (`refs/nn137_2024_Naredba2025.txt`)
  and its amendment NN 25/25.
* Odluka o visini poreznih stopa godišnjeg poreza na dohodak Grada Zagreba, NN 28/2025-291
  (`refs/nn28_2025_291_zagreb_rates.txt`).
* Pravilnik o paušalnom oporezivanju samostalnih djelatnosti art. 3 st. 1 (NN 1/24 čl. 1; NN 16/25 čl. 1).
-/

namespace HrTax
open TaxKernel

/-- Cents per euro. -/
def C : Int := 100

/-! ## Income tax (ZPD) -/

/-- ZPD čl. 14 st. 1 (NN 152/24 čl. 2): "osnovni osobni odbitak u visini 600,00 eura ... za svaki mjesec". Cents. -/
def basicPA : Int := 60000

/-- ZPD čl. 14 st. 3 r.br. 2-10 (NN 152/24 čl. 2): coefficients, in tenths, for the 1st to 9th dependent child:
"Prvo uzdržavano dijete 0,5 ... Deveto uzdržavano dijete 4,9". -/
def childCoefs : List Int := [5, 7, 10, 14, 19, 25, 32, 40, 49]

/-- ZPD čl. 14 st. 3 r.br. 11: "Za svako daljnje uzdržavano dijete koeficijent ... progresivno se uvećava za 1,1 …
više u odnosu prema koeficijentu za prethodno dijete" (reading: +1,1 per further child; see FINDINGS F6). Tenths. -/
def childCoefStep : Int := 11

/-- ZPD čl. 14 st. 3 r.br. 1: "Uzdržavani članovi uže obitelji 0,5" (a dependent spouse, parent, ...). Tenths. -/
def coefDependant : Int := 5

/-- ZPD čl. 14 st. 3 r.br. 12 and 13: disability 0,3; 100 % disability 1,0 (not in the contract; for completeness). -/
def coefDisability : Int := 3
def coefDisability100 : Int := 10

/-- ZPD čl. 17 st. 1 (NN 151/22 čl. 7, NN 114/23 čl. 7): a dependant's own receipts may not exceed
"šesterostruki iznos osnovnog osobnog odbitka iz članka 14. stavka 1. ... na godišnjoj razini" = 6 × 600 € = 3,600 €
a year (Porezna uprava, "Osobni odbitak", `refs/pu_osobni_odbitak.txt`: "(3.600,00 eura)"). Cents. -/
def dependantLimit : Int := 6 * basicPA

/-- ZPD čl. 19 (NN 152/24 čl. 3): "po nižoj stopi na poreznu osnovicu do visine 60.000,00 eura te po višoj stopi
na dio porezne osnovice koji prelazi iznos od 60.000,00 eura". Cents. -/
def bandLimitAnnual : Int := 6000000

/-- ZPD čl. 24 st. 3 (NN 152/24 čl. 5): monthly withholding band "5000,00 eura". Cents. -/
def bandLimitMonthly : Int := 500000

/-- The two local rates (bp). -/
structure Rates where
  lower : Int
  higher : Int
  deriving Repr, DecidableEq

/-- Grad Zagreb 2025: Odluka NN 28/2025-291 čl. 2: "niža porezna stopa 23 %, viša porezna stopa 33 %",
applied "od 1. ožujka 2025."; for the annual assessment it applies to the whole of 2025 (NN 152/24 čl. 14 st. 3:
"a u postupku godišnjeg obračuna poreza na dohodak za cijelo porezno razdoblje 2025. godine"). -/
def zagreb2025 : Rates := ⟨2300, 3300⟩

/-- Grad Zagreb's 2024 decision (23,6 % / 35,4 %; Porezna uprava, "Stope poreza na dohodak usporedba 2024 i 2025",
`refs/pu_stope_usporedba_2024_2025.tsv`, row ZAGREB), still used for withholding in January and February 2025
(NN 152/24 čl. 14 st. 4). -/
def zagreb2024 : Rates := ⟨2360, 3540⟩

/-- ZPD čl. 19.a st. 5: a unit without a decision: "stopa od 20 % ... i 30 %". -/
def defaultRates : Rates := ⟨2000, 3000⟩

/-- ZPD čl. 19.a st. 2 (NN 152/24 čl. 4): statutory ranges (lower min, lower max, higher min, higher max) for
1 općina, 2 grad, 3 veliki grad / sjedište županije, 4 Grad Zagreb. -/
def rateRange : Nat → Int × Int × Int × Int
  | 1 => (1500, 2000, 2500, 3000)
  | 2 => (1500, 2100, 2500, 3100)
  | 3 => (1500, 2200, 2500, 3200)
  | _ => (1500, 2300, 2500, 3300)

/-- The annual schedule for local rates `r` (ZPD čl. 19). -/
def annualSched (r : Rates) : Schedule := Schedule.ofList [(0, r.lower), (bandLimitAnnual, r.higher)]

/-- The monthly withholding schedule (ZPD čl. 24 st. 3). -/
def monthlySched (r : Rates) : Schedule := Schedule.ofList [(0, r.lower), (bandLimitMonthly, r.higher)]

/-- ZPD čl. 46 st. 2 (NN 121/19 čl. 13; NN 114/23 čl. 18): "fizičkim osobama do 25 godina života ... 100%
razmjernog dijela porezne obveze obračunane na dio porezne osnovice na koju se ... plaća godišnji porez po nižoj
stopi, a koja se odnosi na dohodak od nesamostalnog rada (plaću ...)"; "od 26 do 30 godina života ... 50%". Per
čl. 46 st. 8 (old st. 4) the age is the one reached in the year (Porezna uprava, `refs/pu_mladi.txt`: in 2025 born
2000 or later 100 %, born 1995-1999 50 %). bp of the lower-rate tax on wages. -/
def youngReliefBp (age : Nat) : Int := if age ≤ 25 then 10000 else if age ≤ 30 then 5000 else 0

/-- ZPD čl. 15 st. 2: donations raise the personal allowance "do visine 2% primitaka" (bp). -/
def donationCapBp : Int := 200

/-- ZPD čl. 70 st. 1 (interest) and st. 19 (dividends), čl. 62 st. 1 (rent), as changed by NN 114/23 čl. 24, 28:
"po stopi od 12 %". Final taxes outside the annual base (čl. 12 st. 4). -/
def capitalRate : Int := 1200

/-- ZPD čl. 57 st. 1: rental expenses "u visini 30% od ostvarene najamnine" (bp). -/
def rentExpenseBp : Int := 3000

/-- ZPD čl. 82 st. 5 (NN 114/23 čl. 34) and Pravilnik o paušalnom oporezivanju čl. 4 st. 1 (NN 1/24 čl. 2):
"Godišnji porez u paušalnom iznosu po stopi od 12%". -/
def pausalRate : Int := 1200

/-- Pravilnik o paušalnom oporezivanju samostalnih djelatnosti čl. 3 st. 1 t. 1-5 (NN 1/24 čl. 1) and t. 6-7
(NN 16/25 čl. 1): annual paušalni dohodak by receipts class (upper limit of receipts, dohodak), cents. -/
def pausalClasses : List (Int × Int) :=
  [(1130000, 169500), (1530000, 229500), (1990000, 298500), (3060000, 459000), (4000000, 600000),
   (5000000, 750000), (6000000, 900000)]

/-- ZPD čl. 82 st. 1: paušal only while receipts do not exceed the VAT registration threshold, 60.000,00 eura in 2025
(Porezna uprava, "Obrtnici paušalisti", `refs/pu_pausalisti.txt`: "primici nisu veći od 60.000,00 eura"). -/
def pausalCeiling : Int := 6000000

/-! ## Contributions (ZD) -/

/-- ZD čl. 13 st. 1 t. 1.2: pension (pillar I) "po stopi od 15%" for a member of the second pillar;
t. 1.1: "po stopi od 20%" for a member of pillar I only. -/
def pillar1Rate (pillar2 : Bool) : Int := if pillar2 then 1500 else 2000
/-- ZD čl. 17 st. 1 t. 1: pillar II "po stopi od 5%". -/
def pillar2Rate (pillar2 : Bool) : Int := if pillar2 then 500 else 0
/-- ZD čl. 14 st. 1 t. 1 (NN 106/18 čl. 8): health "po stopi od 16,5%" (employer side for employees). -/
def healthRate : Int := 1650

/-- Naredba NN 137/24 čl. 2: prosječna plaća 1.798,00 eura. Cents. -/
def avgWage : Int := 179800
/-- Naredba NN 137/24 čl. 4 (ZD čl. 205): "Najviša mjesečna osnovica ... 10.788,00 eura". Cents. -/
def maxMonthlyBase : Int := 1078800
/-- Naredba NN 137/24 čl. 5 (ZD čl. 208): "Najviša godišnja osnovica ... 129.456,00 eura". Cents. -/
def maxAnnualBase : Int := 12945600
/-- Naredba NN 137/24 čl. 6 r.br. 1 (ZD čl. 66 st. 1 t. 1): obrt, dohodak: coefficient 0,65, "1.168,70". Cents. -/
def seMonthlyBase : Int := 116870
/-- Naredba NN 137/24 čl. 7 r.br. 1 (ZD čl. 70): obrt taxed on paušal: coefficient 0,4, "719,20". Cents. -/
def pausalMonthlyBase : Int := 71920

/-- ZD čl. 21.a (NN 114/23 čl. 4): the monthly pension (pillar I) base is reduced by 300,00 eura for monthly gross
pay up to 700,00 eura, and by "0,5x(1300,00 – ukupan iznos bruto plaća za određeni mjesec)" from 700,01 to
1300,00 eura. As a kernel `Taper` (cents): 300 € withdrawn by one half of the excess over 700 €. -/
def baseReduction : Taper := { full := 30000, start := 70000, num := 1, den := 2 }

/-! ## Child benefit (doplatak za djecu): Zakon o doplatku za djecu (ZDD, NN 94/01, `refs/nn94_2001_ZDD.txt`) čl. 16 t. 1
(limit 140 %) and čl. 17 st. 1-5 (14 / 12,5 / 11 / 9 / 7 % per child), čl. 18 (66,36 €), as amended by NN 156/2023 čl. 7-9
(`refs/nn156_2023_ZDD.txt`, in force 1 March 2024, its čl. 21): "Ako ukupni dohodak po članu kućanstva korisnika
mjesečno ne prelazi 20 % proračunske osnovice, korisniku pripada doplatak za djecu u visini od 14 % proračunske
osnovice, po djetetu" ... "iznad 100 % do 140 % ... 7 %". Percentages of the proračunska osnovica 441,44 € (Zakon o
izvršavanju Državnog proračuna za 2025., NN 149/24 čl. 39 st. 2; 2024: NN 149/23 čl. 38 st. 2, `refs/nn149_2023_ZIDP2024.txt`;
2023: NN 145/22 čl. 39 st. 2, `refs/nn145_2022_ZIDP2023.txt`: "Osnovica za obračun naknada i drugih primanja ... iznosi
441,44 eura"). Round 3 (2026-11-19): the ZDD texts replace the EUROMOD tables formerly cited here; `Tests.lean`
checks every amount and limit against the percentages. Not modelled: čl. 21 st. 2 (+15 % for a child "bez jednog
roditelja ili ... čiji je jedan roditelj nepoznat": a missing parent, not a separated one). -/

/-- Income per household member per month: bracket upper limits and monthly amount per child (cents). -/
def dzdBrackets : List (Int × Int) :=
  [(8829, 6180), (17658, 5518), (26486, 4856), (44144, 3973), (61802, 3090)]

/-- Supplement for the 3rd child (66,36 €) and for 4 or more children (132,72 €) per month, cents. -/
def dzdSupp3 : Int := 6636
def dzdSupp4 : Int := 13272

/-! ## Earlier tax years (improvement round 2, 2026-11-19)

One record per tax year. 2025 is the record of the constants above (unchanged). 2024 and 2023 are cited below from
the dated Narodne novine texts in `hr/refs/`. 2022 (kuna) is not modelled: the contract's currency for Croatia is the
euro, adopted on 2023-01-01. -/

/-- Parameters of one tax year (cents, bp, tenths). -/
structure YP where
  year : Nat
  /-- ZPD čl. 14: osnovni osobni odbitak per month -/
  basicPA : Int
  /-- the amount the čl. 14 coefficients multiply (2024-25: the basic allowance; 2023: osnovica osobnog odbitka) -/
  coefBase : Int
  childCoefs : List Int
  coefDependant : Int
  /-- ZPD čl. 19: annual band limit -/
  bandAnnual : Int
  /-- default (Zagreb) rates -/
  rates : Rates
  /-- prirez porezu na dohodak (bp of the tax), Zagreb; 0 from 2024 (abolished by NN 114/23) -/
  surtaxBp : Int
  /-- ZPD čl. 62, 70: final rate on interest, dividends and rent -/
  capitalRate : Int
  /-- ZD čl. 205: najviša mjesečna osnovica (Naredba of the year) -/
  maxMonthly : Int
  /-- Naredba čl. 6 r.br. 1 (obrt, books) and čl. 7 r.br. 1 (paušal obrt): monthly bases -/
  seBase : Int
  pausalBase : Int
  /-- ZD čl. 21.a pension-base reduction (from 2024-01-01) -/
  reduction : Bool
  /-- paušal taxation modelled for the year -/
  pausalOk : Bool
  pausalClasses : List (Int × Int)
  pausalRate : Int
  pausalCeiling : Int
  /-- months of the year under the doplatak schedule in force before 2024-03-01 (NN 156/23 čl. 21) -/
  dzdOldMonths : Int
  /-- doplatak income test: factor (bp) applied to the year's own income; 10 000 = the statute mode's reading (the
  year's own income, contract convention); `--euromod` sets EUROMOD's $empnr (Household.lean) -/
  dzdIncomeFactorBp : Int := 10000

/-- 2025: the constants above. -/
def yp2025 : YP :=
  { year := 2025, basicPA, coefBase := basicPA, childCoefs, coefDependant, bandAnnual := bandLimitAnnual,
    rates := zagreb2025, surtaxBp := 0, capitalRate, maxMonthly := maxMonthlyBase, seBase := seMonthlyBase,
    pausalBase := pausalMonthlyBase, reduction := true, pausalOk := true, pausalClasses, pausalRate,
    pausalCeiling, dzdOldMonths := 0 }

/-- 2024 (ZPD as amended by NN 114/23, in force 2024-01-01, `refs/nn114_2023_ZPD.txt`):
* čl. 14 st. 1: "osnovni osobni odbitak u visini 560,00 eura ... za svaki mjesec"; st. 3 table: dependants 0,5,
  children 0,5 / 0,7 / 1,0 / 1,4 / 1,9 / 2,5 / 3,2 / 4,0 / 4,9 (the same coefficients as 2025);
* čl. 19: "po nižoj stopi na poreznu osnovicu do visine 50.400,00 eura te po višoj stopi" above;
* Grad Zagreb 2024: 23,6 % / 35,4 % (`zagreb2024`): Odluka o visini poreznih stopa godišnjeg poreza na dohodak Grada
  Zagreba, NN 155/2023-2381 (`refs/nn155_2023_2381_zagreb_rates2024.txt`): "niža porezna stopa 23,60 %, viša porezna
  stopa 35,40 %", "stupa na snagu 1. siječnja 2024." (also the PU table "usporedba 2024 i 2025" and the PU calculator's
  podaci.json 2024, `refs/kalk/`); no prirez
  (NN 114/23 deletes "i prireza porezu na dohodak" throughout);
* čl. 62 st. 1, čl. 70 st. 1, 4, 17, 19, čl. 82 st. 5: "od 10 %" -> "od 12 %";
* ZD čl. 21.a (NN 114/23 ZD, `refs/nn114_2023_ZD.txt`): the 300 € pension-base reduction, from 2024-01-01;
* Naredba za 2024., NN 150/2023-2163 (`refs/nn150_2023_2163_Naredba2024.txt`): čl. 4 "Najviša mjesečna osnovica ...
  9.360,00 eura"; čl. 6 r.br. 1 obrt 0,65 "1.014,00"; čl. 7 r.br. 1 paušal obrt 0,4 "624,00";
* Pravilnik o paušalnom oporezivanju čl. 3 st. 1 t. 1-5 as set by NN 1/24 čl. 1 (`refs/nn1_2024_PravPausal.txt`):
  1.695 / 2.295 / 2.985 / 4.590 / 6.000 € up to receipts of 11.300 / 15.300 / 19.900 / 30.600 / 40.000 €;
  classes 6-7 came only with NN 16/25 (2025), so in 2024 paušal ends at 40.000 €;
* doplatak: the NN 156/23 schedule from 1 March 2024 (čl. 21 "stupa na snagu 1. ožujka 2024."), the earlier one in
  January and February. -/
def yp2024 : YP :=
  { year := 2024, basicPA := 56000, coefBase := 56000, childCoefs := [5, 7, 10, 14, 19, 25, 32, 40, 49],
    coefDependant := 5, bandAnnual := 5040000, rates := zagreb2024, surtaxBp := 0, capitalRate := 1200,
    maxMonthly := 936000, seBase := 101400, pausalBase := 62400, reduction := true, pausalOk := true,
    pausalClasses := [(1130000, 169500), (1530000, 229500), (1990000, 298500), (3060000, 459000), (4000000, 600000)],
    pausalRate := 1200, pausalCeiling := 4000000, dzdOldMonths := 2 }

/-- 2023 (ZPD as amended by NN 151/22, in force 2023-01-01, `refs/nn151_2022_ZPD.txt`):
* čl. 14 st. 1 "osnovica osobnog odbitka ... iznosi 331,81 euro", st. 3 "osnovni osobni odbitak u visini 530,90
  eura"; st. 4 table (coefficients of the osnovica): dependants 0,7 (232,27), children 0,7 / 1,0 / 1,4 / 1,9 / 2,5 /
  3,2 / 4,0 / 4,9 / 5,9; r.br. 11 "+1,1 ... više" from 5,9;
* čl. 19: "do visine 47.780,28 eura" at the lower rate; the rates 20 % / 30 % (NN 138/20: "stope od 24%" -> "stope od
  20%", "stope od 36%" -> "stope od 30%" throughout, `refs/nn138_2020_ZPD.txt`);
* prirez porezu na dohodak, Grad Zagreb 18 %: Zakon o lokalnim porezima (NN 115/16, `refs/nn115_2016_ZLP.txt`)
  čl. 21 st. 1 t. 4 "Grad Zagreb po stopi do 18%" (not changed by NN 101/17 or 114/22, `refs/nn101_2017_ZLP.txt`, `refs/nn114_2022_ZLP.txt`; deleted by NN 114/23 čl. 6, whose čl. 11 st. 2 keeps decisions taken under ZLP čl. 42 st. 1 "na snazi do 31. prosinca 2023.", `refs/nn114_2023_ZLP.txt`);
  the rate: Odluka o lokalnim porezima i o prirezu porezu na dohodak Grada Zagreba, NN 28/2017-654
  (`refs/nn28_2017_654_zagreb_prirez.txt`) čl. 4 "Prirez porezu na dohodak plaća se po stopi od 18%." (ZLP čl. 42 st. 3:
  prirez decisions must be published in Narodne novine; NN titles 2017-2022 searched for a later Zagreb prirez
  decision, see improve-central/round3/hrhu.md); round 3 replaces the EUROMOD citation formerly used here,
  levied on the income tax (Zakon o lokalnim porezima čl. 20-21) including the final taxes on capital income;
* čl. 62 st. 1, čl. 70: 10 % (the text NN 114/23 replaced, "od 10 %" -> "od 12 %");
* ZD: no čl. 21.a reduction (inserted by NN 114/23, from 2024); Naredba za 2023., NN 1/2023-8
  (`refs/nn1_2023_8_Naredba2023.txt`): čl. 4 "Najviša mjesečna osnovica ... 8.203,08 eura"; obrt 0,65 "888,67";
  paušal obrt 0,4 "546,87";
* paušal (round 8): Pravilnik o paušalnom oporezivanju samostalnih djelatnosti (NN 1/20, `refs/nn1_2020_PravPausal.txt`) čl. 3
  st. 1 as replaced by NN 156/22 čl. 1 (`refs/nn156_2022_PravPausal.txt`, its čl. 3: "primjenjuju za 2023. godinu i
  nadalje") and corrected by NN 15/23 čl. 1 (`refs/nn15_2023_PravPausal.txt`: "39.816,85 eura" -> "39.816,84 eura"):
  paušalni dohodak "1.692,22 ... do 11.281,44", "2.289,47 ... do 15.263,13", "2.976,31 ... do 19.842,06", "4.578,94 ... do
  30.526,25", "5.972,53 ... do 39.816,84" eura; ZPD čl. 82 st. 5 (NN 138/20 version) "po stopnji od 10 %"; the Pravilnik
  (čl. 4 st. 2 of NN 1/20) adds "prirez porezu na dohodak" of the residence unit (Zagreb 18 %);
* doplatak: the schedule before NN 156/23 all year. -/
def yp2023 : YP :=
  { year := 2023, basicPA := 53090, coefBase := 33181, childCoefs := [7, 10, 14, 19, 25, 32, 40, 49, 59],
    coefDependant := 7, bandAnnual := 4778028, rates := ⟨2000, 3000⟩, surtaxBp := 1800, capitalRate := 1000,
    maxMonthly := 820308, seBase := 88867, pausalBase := 54687, reduction := false, pausalOk := true,
    pausalClasses := [(1128144, 169222), (1526313, 228947), (1984206, 297631), (3052625, 457894), (3981684, 597253)],
    pausalRate := 1000, pausalCeiling := 3981684, dzdOldMonths := 12 }

/-- The record for a tax year: 2023, 2024, else 2025. -/
def ypFor (y : Nat) : YP := if y = 2023 then yp2023 else if y = 2024 then yp2024 else yp2025

/-- Doplatak za djecu before 2024-03-01: ZDD čl. 17 as rewritten by NN 138/06 čl. 3 (`refs/nn138_2006_ZDD.txt`, in force
1 January 2007): "ne prelazi 16,33% proračunske osnovice ... 9% proračunske osnovice, po djetetu"; "između 16,34 i
33,66% ... 7,5%"; "između 33,67 i 50% ... 6%"; NN 58/18 čl. 2-3 (`refs/nn58_2018_ZDD.txt`): "U članku 16. točki 1. broj:
»50« zamjenjuje se brojem: »70«" and "U članku 17. stavku 3. broj: »50« zamjenjuje se brojem: »70«"; no later change
until NN 156/23 (amendments NN 107/07, 37/08, 61/11, 112/12, 82/15 read: none touches čl. 16 t. 1 or čl. 17).
Proračunska osnovica 441,44 € (2023: NN 145/22 čl. 39 st. 2; 2024: NN 149/23 čl. 38 st. 2). Limits 72,09 / 148,59 /
309,01 € and amounts 39,73 / 33,11 / 26,49 € per child (cents, half up; `Tests.dzd_old_from_statute`). Supplement for
the 3rd and 4th child: NN 138/06 čl. 4 "500,00 kuna za treće i četvrto dijete" = 66,36 € (NN 156/23 čl. 9). -/
def dzdBracketsOld : List (Int × Int) := [(7209, 3973), (14859, 3311), (30901, 2649)]

end HrTax
