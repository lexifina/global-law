import TaxKernel

/-!
# Slovenia 2025: parameters, each with its source (all money in euro CENTS)

Slovene income tax is assessed in euros and cents (FURS tables print cents), so this model computes in cents and
converts to whole euros only for the contract's output.

Sources (copies under `~/cmp20/central/si/refs/`):
* ZDoh-2 (Zakon o dohodnini, Ur. l. RS 117/06 …, 104/24 – ZDoh-2AB), PISRS ZAKO4697, unofficial consolidation
  NPB 34 (in use 11.12.2024–18.07.2025; čl. 2: the law in force on 1 January of the tax year applies):
  `refs/zdoh2_npb34.txt` (from https://pisrs.si/api/datoteke/integracije/358109730).
* FURS, "Obvestilo o lestvici za odmero dohodnine in olajšave za leto 2025" (20.12.2024), applying the
  "Pravilnik o določitvi usklajenih zneskov olajšav, enačbe za določitev olajšave in lestvice za odmero dohodnine za
  leto 2025" (Ur. l. RS 108/24): `refs/fu_Lestvica_2025.txt`
  (https://www.fu.gov.si/fileadmin/Internet/Davki_in_druge_dajatve/Podrocja/Dohodnina/Letna_odmera_dohodnine/Opis/Lestvica_za_leto_2025.docx).
* FURS, "Brošura o plačevanju prispevkov za socialno varnost" (contribution rates, incl. long-term care from
  1.7.2025): `refs/fu_Brosura_prispevki.txt`; FURS "Obvezni zdravstveni prispevek – OZP": `refs/fu_Obvezni_zdravstveni_prispevek_-_OZP.txt`;
  FURS LZP_7_2025.xlsx (PP = 2.394,92 EUR): `refs/fu_LZP_7_2025.xlsx`.
* Sklep o usklajenih višinah transferjev … (Ur. l. RS 9/25, PISRS SKLE13906), from 1.3.2025: child benefit and
  large-family allowance: `refs/skle13906_transferji_2025.txt`. ZSDP-1 (ZAKO6688) čl. 72, 77; ZUPJS (ZAKO4780) čl. 10,
  12, 15, 22; Pravilnik PRAV12104 čl. 2, 10.
-/

namespace SiTax
open TaxKernel

/-- Cents in a euro. -/
def CENT : Int := 100

/-- ZDoh-2 čl. 122(1) with the 2025 amounts (FURS Lestvica 2025: "nad 9.210,26 … 27.089,00 … 54.178,00 …
78.016,32"; rates 16 %, 26 %, 33 %, 39 %, 50 %). Thresholds in cents. The statute's base amounts (8.500, 25.000,
50.000, 72.000) times 1.03 (2024) times 1.052 (2025). -/
def sched : Schedule :=
  Schedule.ofList [(0, 1600), (921026, 2600), (2708900, 3300), (5417800, 3900), (7801632, 5000)]

/-- The annual tax table as FURS prints it (fixed amount at the lower threshold + rate above it):
"9.210,26 … 1.473,64 + 26 %", "27.089,00 … 6.122,11 + 33 %", "54.178,00 … 15.061,48 + 39 %",
"78.016,32 … 24.358,43 + 50 %" (refs/fu_Lestvica_2025.txt). (lower threshold, fixed amount, rate bp), cents. -/
def furTable : List (Int × Int × Int) :=
  [(0, 0, 1600), (921026, 147364, 2600), (2708900, 612211, 3300), (5417800, 1506148, 3900),
   (7801632, 2435843, 5000)]

/-- ZDoh-2 čl. 111(1) "zmanjšanje letne davčne osnove v višini 5.000 eurov", indexed: FURS 2025 "5.260,00". -/
def generalBase : Int := 526000

/-- ZDoh-2 čl. 111(3): additional general allowance "18.761,40 eura – 1,17259 x skupni dohodek" for total income
up to 16.000 €; 2025 (FURS Lestvica 2025): "do 16.832,00: 5.260,00 + (19.736,99 - 1,17259 x skupni dohodek)".
As a kernel `Taper`: full = 5.260,00 + 19.736,99, withdrawn at 117259/100000 per cent of income from 0, never
below 5.260,00. (Above 16.832,00 the formula is negative, so the floor reproduces the statute's cut-off; see F3
for the four cents just below it.) -/
def generalTaper : Taper :=
  { full := 526000 + 1973699, start := 0, num := 117259, den := 100000, floor := 526000 }

/-- FURS Lestvica 2025: upper limit of total income for the additional allowance "16.832,00". -/
def generalExtraLimit : Int := 1683200

/-- ZDoh-2 čl. 114(1)-(2), 2025 amounts (FURS Lestvica 2025, "Posebna olajšava za vzdrževane otroke"):
first child 2.838,30; second 3.085,52; third 5.146,39; fourth 7.207,26; fifth 9.268,12; each further child
"poveča za 2.060,87 evrov … glede na višino olajšave za predhodnega vzdrževanega otroka". Rank n (0 = first). -/
def childAmount : Nat → Int
  | 0 => 283830
  | 1 => 308552
  | 2 => 514639
  | 3 => 720726
  | 4 => 926812
  | n + 5 => 926812 + 206087 * ((n : Int) + 1)

/-- ZDoh-2 čl. 114(1) 3. "za vsakega drugega vzdrževanega družinskega člana 2.698 eurov" (2025: "2.838,30");
čl. 115(1): a spouse who "ni zaposlen ter ne opravlja dejavnosti, nima lastnih dohodkov … ali so ti manjši od"
that amount. The same amount is the own-income limit. -/
def otherDependant : Int := 283830

/-- ZDoh-2 čl. 112(8): 70 years and over, "1.500 eurov letno" (2025: "1.578,00"). -/
def age70Allowance : Int := 157800

/-- ZDoh-2 čl. 113(6) (ZDoh-2AB, from 2025): employees up to the year they turn 29, "1.300 eurov letno"
(2025: "1.367,60"), pro rata per full month of employment (the model assumes 12 months when wages > 0). -/
def youngWorkerAllowance : Int := 136760

/-- ZDoh-2 čl. 112(3): "zmanjšanje dohodnine v višini 13,5% odmerjene pokojnine", at most the tax on the pension
(čl. 112(7)). Basis points. -/
def pensionCreditRate : Int := 1350

/-! ## Employee social contributions (FURS brošura, 2.2 "Vrste in stopnje prispevkov")
Insured person: pension 15,50 %, health 6,36 %, parental care 0,10 %, unemployment 0,14 % (22,10 %), plus long-term
care 1,00 % "za obdobje od 1. julija 2025 dalje" (ZDOsk-1), plus the flat monthly OZP. No ceiling. Annual wages are
taken as paid evenly over the year, so the year's rate is 22,10 % + 1,00 % × 6/12 = 22,60 %. -/

/-- 22,60 % effective for 2025 (22,10 % × 12 months + 1,00 % × 6 months). -/
def employeeRate : Int := 2260

/-- The kernel contribution for wages: flat 22,60 %, no ceiling, rounded to the cent. -/
def employeeSSC : Contribution :=
  { name := "employee 22.1 % + LTC 1 % from July", sched := Schedule.flat employeeRate, round := Rule.unitHalfUp }

/-- OZP (ZZVZZ čl. 48(2), (4)): "35,00" €/month 1.1.2024–28.2.2025, "37,17" from 1.3.2025 (FURS OZP table; Ur. l.
RS 12/2025): 2 × 35,00 + 10 × 37,17 = 441,70 € in 2025, payable by every insured adult. -/
def ozpYear : Int := 2 * 3500 + 10 * 3717

/-- Pensioners: long-term care 1,00 % of the pension from 1.7.2025 (FURS brošura 16.2, ZDOsk-1 čl. 56(10)); health
5,96 % is paid by ZPIZ, not by the pensioner. 6 months of 1 % = 50 bp of the annual pension. -/
def pensionLtcRate : Int := 50

/-! ## Self-employed (s.p.) contributions (FURS brošura 3.1): the insured pays both shares: 24,10 % + 16,10 %
from 1.7.2025 (38,20 % before: no long-term care), on a base between 60 % and 350 % of PP (the last known average
monthly gross wage, 2.394,92 € in FURS LZP_7_2025). The year's rate: 38,20 % + 2,00 % × 6/12 = 39,20 %. -/

def seRate : Int := 3920
/-- 60 % × 2.394,92 = 1.436,95 €/month (FURS brošura 3.1.2 "od leta 2018 dalje: 60 % PP"), × 12. -/
def seMinBase : Int := 143695 * 12
/-- 3,5 × PP = 8.382,22 €/month (FURS LZP_7_2025 "3,5 PP"), × 12. -/
def seMaxBase : Int := 838222 * 12

/-- s.p. as a side occupation (not insured under ZPIZ-2 čl. 15): lump sums (FURS "Plačevanje pavšalnih prispevkov v
letu 2025", refs/fu_Pavsalni_prispevki_2025.txt): pension/disability "46,28 EUR mesečno" to 31.3.2025 and "49,15" from
1.4.2025 (ZPIZ-2 čl. 20, Sklep Ur. l. RS 15/2025, 6. člen); health "0,53 % od PP … 12,66 EUR" and "6,36 % od 25 % PP
… 37,97 EUR" a month; long-term care 1 % of 25 % PP (5,97 €) from July (brošura 3.2). Year: 3 × 46,28 + 9 × 49,15
+ 12 × (12,66 + 37,97) + 6 × 5,97 = 1.224,57 €. -/
def sideContribYear : Int := 3 * 4628 + 9 * 4915 + 12 * (1266 + 3797) + 6 * 597

/-! ## Flat-rate expenses (normirani odhodki), ZDoh-2 čl. 59 as amended by ZDoh-2AB (from 2025) -/

/-- čl. 59(1): insured full time as self-employed ≥ 9 months: 80 % of revenue up to 60.000 €. -/
def normFullCap : Int := 6000000
/-- čl. 59(2): otherwise 80 % up to 12.500 € and 40 % of revenue between 12.500 and 30.000 €. -/
def normPartCap1 : Int := 1250000
def normPartCap2 : Int := 3000000
/-- čl. 135.a: "po stopnji 20 % in se šteje kot dokončen davek". -/
def normTaxRate : Int := 2000

/-! ## Capital and rental income (final taxes, not in the annual base: čl. 131.a) -/

/-- čl. 132(1): "po stopnji 25%"; (2): gains after 5 years 20 %, after 10 years 15 %; čl. 96(1): no tax after 15. -/
def capitalRate : Int := 2500
def gainsRate (years : Int) : Int :=
  if years ≥ 15 then 0 else if years ≥ 10 then 1500 else if years ≥ 5 then 2000 else 2500
/-- čl. 133: interest on bank deposits (and 2024-2026 retail state bonds) is reduced by 1.000 € per person. -/
def interestExempt : Int := 100000
/-- čl. 77(1): rent less 10 % flat costs; čl. 135.č: 25 % final. -/
def rentCostPct : Int := 1000
def rentRate : Int := 2500

/-! ## Child benefit (otroški dodatek), ZUPJS čl. 22 amounts as indexed from 1.3.2025 (Sklep, Ur. l. RS 9/25) -/

/-- Income classes: average monthly income per family member (cents), upper limit of each class 1-8:
"do 235,14", "391,92", "470,31", "548,69", "692,42", "836,10", "1.071,28", "1.293,36". Above class 8: nothing. -/
def classTable : Table :=
  [⟨0, 23514, 1⟩, ⟨23515, 39192, 2⟩, ⟨39193, 47031, 3⟩, ⟨47032, 54869, 4⟩, ⟨54870, 69242, 5⟩,
   ⟨69243, 83610, 6⟩, ⟨83611, 107128, 7⟩, ⟨107129, 129336, 8⟩]

/-- Monthly amount by class (1-8) and child rank (0 = first = oldest, ZUPJS čl. 22(3)); `secondary` = a child in
secondary school (the model: aged 15 or more). Sklep 9/25 point I. -/
def childBenefitMonthly (cls : Int) (rank : Nat) (secondary : Bool) : Int :=
  let r := min rank 2
  let row : List Int :=
    match cls with
    | 1 => [14381, 15818, 17258]
    | 2 => [12294, 13591, 14880]
    | 3 => [9371, 10473, 11573]
    | 4 => [7391, 8433, 9495]
    | 5 => [6043, 7052, 8055]
    | 6 => [3829, 4792, 5750]
    | 7 => if secondary then [3627, 4583, 6245] else [2874, 3829, 4792]
    | 8 => if secondary then [2879, 3837, 5018] else [2502, 3460, 4416]
    | _ => [0, 0, 0]
  row.getD r 0

/-- ZSDP-1 čl. 72(1): single-parent family "se posamezni znesek otroškega dodatka poveča za 30 odstotkov". -/
def loneParentPct : Int := 13000

/-- Sklep 9/25: "dodatek za veliko družino s tremi otroki znaša 496,93 eura, … s štirimi ali več otroki pa 603,86
eura" (ZSDP-1 čl. 77, annual, no income test). -/
def largeFamily (n : Nat) : Int := if n ≥ 4 then 60386 else if n = 3 then 49693 else 0

end SiTax
