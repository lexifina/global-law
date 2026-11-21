import TaxKernel

/-!
# Italy, periodo d'imposta 2025: every parameter, with its provision

Money is `Int` **cents** (the sostituto d'imposta and the OECD compute IRPEF to the cent; the dichiarazione rounds
each line to the euro). Rates are kernel basis points (2300 = 23 %); every 2025 Italian rate used here is a whole
number of basis points. Ratios that the statute says are taken "nelle prime quattro cifre decimali" are integers in
units of 10⁻⁴ (`r4`).

Texts: `law/*.md` (normattiva.it, as in force on 2025-12-31; Lazio from Global law `italy/lazio/acts`; Roma
Capitale from the MEF register of municipal rates).
-/

namespace ITTax
open TaxKernel

/-- Euros to cents. -/
def eur (x : Int) : Int := 100 * x

/-! ## IRPEF: TUIR (DPR 917/1986) art. 11 c. 1, as replaced by L. 207/2024 art. 1 c. 2 lett. a)
"a) fino a 28.000 euro, 23 per cento; b) oltre 28.000 euro e fino a 50.000 euro, 35 per cento;
c) oltre 50.000 euro, 43 per cento" -/
def irpefSched : Schedule := Schedule.ofList [(0, 2300), (eur 28000, 3500), (eur 50000, 4300)]

/-! ## Art. 13 c. 1 (lavoro dipendente), c. 1.1, c. 3 (pensione), c. 3-bis, c. 5 (autonomo), c. 5-ter -/
/-- c. 1 a): "1.955 euro, se il reddito complessivo non supera 15.000 euro" (1.955 by L. 207/2024 c. 2 b)). -/
def dipA : Int := eur 1955
/-- c. 1 b), c): "1.910 euro, aumentata del prodotto tra 1.190 euro e ... (28.000 − R) / 13.000". -/
def dipB : Int := eur 1910
def dipBInc : Int := eur 1190
/-- c. 1.1: "aumentata di un importo pari a 65 euro, se il reddito complessivo è superiore a 25.000 euro ma non a
35.000 euro". -/
def dipBonus : Int := eur 65
/-- c. 3 a) "1.955 euro, se il reddito complessivo non supera 8.500 euro"; b) "700 euro, aumentata del prodotto
fra 1.255 euro e ... (28.000 − R) / 19.500"; c) "700 euro ... (50.000 − R) / 22.000"; 3-bis "+50 euro" between
25.000 and 29.000. -/
def penA : Int := eur 1955
def penB : Int := eur 700
def penBInc : Int := eur 1255
def penBonus : Int := eur 50
/-- c. 5 a) "1.265 euro, se il reddito complessivo non supera 5.500 euro"; b) "500 euro, aumentata del prodotto
fra 765 euro e ... (28.000 − R) / 22.500"; b-bis) "500 euro ... (50.000 − R) / 22.000"; 5-ter "+50 euro" between
11.000 and 17.000. -/
def autA : Int := eur 1265
def autB : Int := eur 500
def autBInc : Int := eur 765
def autBonus : Int := eur 50

/-! ## Art. 12 (carichi di famiglia) -/
/-- c. 1 a) 1) "800 euro, diminuiti del prodotto tra 110 euro e ... rapporto fra reddito complessivo e 15.000
euro"; 2), 3) "690 euro"; 3) "(80.000 − R) / 40.000". -/
def conA : Int := eur 800
def conAMinus : Int := eur 110
def conB : Int := eur 690
/-- c. 1 b): the 10/20/30/20/10 euro supplements: (lower limit, upper limit, supplement), "superiore a ... ma non
a ...". -/
def conSupp : List (Int × Int × Int) :=
  [(eur 29000, eur 29200, eur 10), (eur 29200, eur 34700, eur 20), (eur 34700, eur 35000, eur 30),
   (eur 35000, eur 35100, eur 20), (eur 35100, eur 35200, eur 10)]
/-- c. 1 c): "950 euro per ciascun figlio ... di età pari o superiore a 21 anni ma inferiore a 30 anni";
"(95.000 − R) / 95.000"; "l'importo di 95.000 euro è aumentato per tutti di 15.000 euro per ogni figlio successivo
al primo". -/
def figlio : Int := eur 950
def figlioBase : Int := eur 95000
def figlioStep : Int := eur 15000
/-- c. 2: dependants' "reddito complessivo ... non superiore a 2.840,51 euro, al lordo degli oneri deducibili". -/
def caricoLimit : Int := 284051

/-! ## L. 207/2024 art. 1 cc. 4-6 (the 2025 cuneo fiscale) -/
/-- c. 4: "reddito complessivo non superiore a 20.000 euro ... a) 7,1 per cento, se il reddito di lavoro dipendente
non è superiore a 8.500 euro; b) 5,3 per cento ... non a 15.000 euro; c) 4,8 per cento". -/
def cuneoLimit : Int := eur 20000
def cuneoA : Int := eur 8500
def cuneoB : Int := eur 15000
def cuneoRateA : Int := 710
def cuneoRateB : Int := 530
def cuneoRateC : Int := 480
/-- c. 6: "a) a 1.000 euro, se ... superiore a 20.000 euro ma non a 32.000 euro; b) al prodotto tra 1.000 euro e
... (40.000 − R) / 8.000, se ... superiore a 32.000 euro ma non a 40.000 euro". -/
def ulterioreFull : Int := eur 1000

/-! ## DL 3/2020 art. 1 c. 1 (trattamento integrativo), as amended by L. 207/2024 c. 3 -/
/-- "1.200 euro a decorrere dall'anno 2021, se il reddito complessivo non è superiore a 15.000 euro"; the
detrazione of art. 13 c. 1 "diminuita dell'importo di 75 euro". -/
def tiFull : Int := eur 1200
def tiMinus : Int := eur 75

/-! ## TUIR art. 16-ter (from 2025, L. 207/2024 c. 10): ceiling on oneri detraibili above 75.000 -/
/-- c. 2: "a) 14.000 euro, se il reddito complessivo ... superiore a 75.000 euro e non superiore a 100.000 euro;
b) 8.000 euro, se ... superiore a 100.000 euro". -1 = no ceiling. -/
def capBase (r : Int) : Int := if r ≤ eur 75000 then -1 else if r ≤ eur 100000 then eur 14000 else eur 8000
/-- c. 3: coefficient ×100 by number of dependent children: 0,50; 0,70; 0,85; 1. -/
def capCoeff (nFigli : Nat) : Int :=
  if nFigli = 0 then 50 else if nFigli = 1 then 70 else if nFigli = 2 then 85 else 100

/-! ## Oneri -/
/-- D.Lgs. 252/2005 art. 8 c. 4: pension-fund contributions "deducibili ... per un importo non superiore ad euro
5.164,57". -/
def pensionCap : Int := 516457
/-- D.Lgs. 117/2017 art. 83 c. 1: "30 per cento degli oneri ... per un importo complessivo in ciascun periodo
d'imposta non superiore a 30.000 euro". -/
/- Not cut by D.Lgs. 216/2023 art. 2 (2024: −260 EUR above 50.000 of reddito complessivo): that cut applies only to the
19 % oneri, gifts to political parties (DL 149/2013 art. 11) and catastrophe-insurance premiums (normattiva, art. 2
vigente 2024-06-30, `improve-central/refs/it/dlgs216_2023_art2_2024-06-30.html`); this 30 % art. 83 credit is none of
them. -/
def charityRate : Int := 3000
def charityCap : Int := eur 30000

/-! ## Addizionale regionale Lazio 2025 (`law/lazio_addizionale_2025.md`), comunale Roma (`law/roma_addizionale_2025.md`) -/
/-- 1,23 % base (D.Lgs. 68/2011 art. 6 c. 1) + 0,50 % (L. 311/2004 art. 1 c. 174) = 1,73 %, on the whole base
when it is up to 28.000 (L.R. 22/2024 art. 2 c. 2 lifts the 1,60 % maggiorazione there). -/
def lazioLow : Schedule := Schedule.flat 173
/-- Above 28.000: 1,73 % to 15.000 and 1,73 + 1,60 = 3,33 % above (L.R. 1/2023 art. 2 c. 1). -/
def lazioHigh : Schedule := Schedule.ofList [(0, 173), (eur 15000, 333)]
def lazioNoMagg : Int := eur 28000
/-- L.R. 22/2024 art. 2 c. 3: "detrazione ... pari a 60,00 euro ... compreso tra 28.001 e 35.000,00 euro";
"non può, comunque, derivare il riconoscimento di alcun credito d'imposta". -/
def lazioDetr : Int := eur 60
def lazioDetrLo : Int := eur 28001
def lazioDetrHi : Int := eur 35000
/-- Roma Capitale, delibera A.C. 186/2024: "Esenzione per redditi imponibili fino a euro 14.000,00; 0,9 Aliquota
unica". -/
def romaRate : Int := 90
def romaExempt : Int := eur 14000

/-! ## INPS employee contributions 2025 (ordinary employee in industry; worker first insured after 1995) -/
/-- FPLD employee 9,19 % + 0,30 % employee share of CIGS/FIS (the OECD's 9,49 %). The 0,30 % is D.Lgs. 148/2015 art. 23
c. 1 (normattiva, text in force from 1-1-2022, read !vig=2025-01-01 in round 8: "contributo ordinario nella misura dello
0,90 per cento ... di cui 0,60 per cento a carico dell'impresa ... e 0,30 per cento a carico del lavoratore",
`improve-central/refs/it/r8/dlgs148.html`); it applies to workers within the CIGS rules (c. 1-bis: from 2022 also
employers with more than 15 employees on average), so the household is taken to work for such an employer; +1 % on pay above the first
pensionable band (DL 384/1992 art. 3-ter); band 55.448 and massimale 120.607 (L. 335/1995 art. 2 c. 18) for 2025,
INPS circolare 26/2025. -/
def inpsRate : Int := 949
def inpsExtra : Int := 100
def inpsBand : Int := eur 55448
def inpsMax : Int := eur 120607

/-! ## Capital income -/
/-- DL 66/2014 art. 3 c. 1: "sono stabilite nella misura del 26 per cento". -/
def sostitutiva : Int := 2600
/-- D.Lgs. 23/2011 art. 3 c. 2: cedolare secca "aliquota del 21 per cento" on the canone. -/
def cedolare : Int := 2100
/-- TUIR art. 37 c. 4-bis: under IRPEF the canone counts "ridotto forfetariamente del 5 per cento". -/
def rentIrpefShare : Int := 9500

/-! ## Assegno unico universale (D.Lgs. 230/2021 art. 4) and ISEE (DPCM 159/2013) -/
/-- Art. 4 c. 11 revaluation, cumulated: 2023 +8,1 %, 2024 +5,4 %, 2025 +0,8 % (INPS circ. 33/2025):
F = 1,081 × 1,054 × 1,008 = 1,148488992 (unrounded, as the OECD; INPS publishes rounded amounts). -/
def auuFnum : Int := 1148488992
def auuFden : Int := 1000000000
/-- Art. 4 cc. 1-3, 8, in 2022 terms (cents a month): full amount up to ISEE 15.000, falling (tabella 1) to the
floor at 40.000. -/
def auuLo : Int := eur 15000
def auuHi : Int := eur 40000
def auuMinor : Int × Int := (eur 175, eur 50)
def auuAdult : Int × Int := (eur 85, eur 25)
def auuThird : Int × Int := (eur 85, eur 15)
def auuBothWork : Int × Int := (eur 30, 0)
/-- DPCM 159/2013 Allegato 1: scala ×100 for 1..5 members, +35 per further member. -/
def scalaBase : Nat → Int
  | 0 => 100 | 1 => 100 | 2 => 157 | 3 => 204 | 4 => 246 | 5 => 285
  | k + 6 => 285 + 35 * (k + 1)
/-- DPCM 159/2013 art. 4 c. 3 e): "fino ad un massimo di 3.000 euro ... pari al 20 per cento" of employment
income; f) "fino ad un massimo di 1.000 euro" for pensions. -/
def iseeDipCap : Int := eur 3000
def iseePenCap : Int := eur 1000

/-! ## Earlier tax years 2022-2024 (improvement round 4, 2026-11-19)

Texts in `~/cmp20/improve-central/refs/it/` (normattiva.it multivigente, `vig` dates as in each file name; MEF
Dipartimento delle Finanze registers of regional and municipal rates). The 2025 values above are untouched; each
`...Y` function returns them for `y ≥ 2025`. -/

/-- TUIR art. 11 c. 1 in force 2022-06-30 and 2023-06-30 (L. 234/2021 art. 1 c. 2 a)): "a) fino a 15.000 euro, 23
per cento; b) oltre 15.000 euro e fino a 28.000 euro, 25 per cento; c) oltre 28.000 euro e fino a 50.000 euro, 35 per
cento; d) oltre 50.000 euro, 43 per cento". For 2024, D.Lgs. 216/2023 art. 1 c. 1 ("Per l'anno 2024 ... in luogo
delle aliquote previste dall'articolo 11, comma 1 ... a) fino a 28.000 euro, 23 per cento; b) oltre 28.000 euro e
fino a 50.000 euro, 35 per cento; c) oltre 50.000 euro, 43 per cento") = the 2025 schedule. -/
def irpefSched2022 : Schedule := Schedule.ofList [(0, 2300), (eur 15000, 2500), (eur 28000, 3500), (eur 50000, 4300)]
def irpefSchedY (y : Nat) : Schedule := if y ≤ 2023 then irpefSched2022 else irpefSched

/-- TUIR art. 13 c. 1 a) in force 2022-06-30, 2023-06-30 and 2024-06-30: "1.880 euro, se il reddito complessivo non
supera 15.000 euro"; for 2024 D.Lgs. 216/2023 art. 1 c. 2: "Per l'anno 2024, la detrazione prevista dall'articolo
13, comma 1, lettera a) ... è innalzata a 1.955 euro" (from 2025 the TUIR text itself, L. 207/2024). -/
def dipAY (y : Nat) : Int := if y ≤ 2023 then eur 1880 else dipA

/-- DL 3/2020 art. 1 c. 1 (text in force 2022-06-30 to 2024-06-30): the first test compares the imposta lorda with
"la detrazione spettante ai sensi dell'articolo 13, comma 1" (no reduction); for 2024 D.Lgs. 216/2023 art. 1 c. 3:
"diminuita dell'importo di 75 euro rapportato al periodo di lavoro nell'anno"; 2025: L. 207/2024 c. 3 (`tiMinus`). -/
def tiMinusY (y : Nat) : Int := if y ≤ 2023 then 0 else tiMinus

/-- INPS first pensionable band (DL 384/1992 art. 3-ter: +1 point "sulle quote di retribuzione eccedente il limite
della prima fascia di retribuzione pensionabile") and the massimale (L. 335/1995 art. 2 c. 18), both revalued each
year by the ISTAT cost-of-living index (L. 67/1988 art. 21 c. 6). The 2025 values (INPS circ. 26/2025) divided back
by the same index variations the model uses for the assegno unico (+0,8 % 2025, +5,4 % 2024, +8,1 % 2023), rounded to
the euro: band 55.008 (2024), 52.190 (2023), 48.279 (2022); massimale 119.650, 113.520, 105.014. The INPS circulars
that publish them were not retrieved (derived values, stated in `unsupported`). -/
def inpsBandY (y : Nat) : Int :=
  if y ≤ 2022 then eur 48279 else if y = 2023 then eur 52190 else if y = 2024 then eur 55008 else inpsBand
def inpsMaxY (y : Nat) : Int :=
  if y ≤ 2022 then eur 105014 else if y = 2023 then eur 113520 else if y = 2024 then eur 119650 else inpsMax

/-- The employee IVS contribution exemptions ("esonero sulla quota dei contributi previdenziali per l'invalidità, la
vecchiaia e i superstiti a carico del lavoratore"), as the sum over the 13 monthly pay periods (12 months + the
tredicesima) of the points granted, in basis points, for pay "parametrata su base mensile per tredici mensilità"
not above `cuneoCap2692` (and the extra point up to `cuneoCap1923`). Pay is taken as 13 equal instalments.
* 2022: L. 234/2021 art. 1 c. 121 ("per i periodi di paga dal 1° gennaio 2022 al 31 dicembre 2022 ... esonero ... di 0,8
  punti percentuali a condizione che la retribuzione imponibile, parametrata su base mensile per tredici mensilità, non
  ecceda l'importo mensile di 2.692 euro, maggiorato, per la competenza del mese di dicembre, del rateo di tredicesima";
  normattiva Akoma Ntoso, vigente 2022-06-30, `improve-central/refs/it/akn/l234_2021_vig20220630.akn.xml`), 0,8 points
  for every pay period of 2022 incl. the tredicesima; DL 115/2022
  art. 20 c. 1: "Per i periodi di paga dal 1° luglio 2022 al 31 dicembre 2022, compresi la tredicesima ... è
  incrementato di 1,2 punti percentuali": 6 × 80 + 7 × 200 = 1.880.
* 2023: L. 197/2022 art. 1 c. 281 ("per i periodi di paga dal 1° gennaio 2023 al 31 dicembre 2023 ... nella misura di 2
  punti percentuali ... ed è incrementato di un ulteriore punto percentuale, a condizione che la retribuzione
  imponibile ... non ecceda l'importo mensile di 1.923 euro"; Akoma Ntoso, vigente 2023-06-30,
  `refs/it/akn/l197_2022_vig20230630.akn.xml`), 2 points (3 up to 1.923 a month) for every pay period incl. the
  tredicesima; DL
  48/2023 art. 39 c. 1: "Per i periodi di paga dal 1° luglio 2023 al 31 dicembre 2023 ... incrementato di 4 punti
  percentuali, senza ulteriori effetti sul rateo di tredicesima": 7 × 200 + 6 × 600 = 5.000 (7 × 300 + 6 × 700 = 6.300).
* 2024: L. 213/2023 art. 1 c. 15: "per i periodi di paga dal 1° gennaio 2024 al 31 dicembre 2024 ... senza effetti sul
  rateo di tredicesima ... di 6 punti percentuali, a condizione che la retribuzione imponibile, parametrata su base
  mensile per tredici mensilità, non ecceda l'importo mensile di 2.692 euro ... ulteriore punto percentuale ...
  1.923 euro": 12 × 600 = 7.200 (12 × 700 = 8.400).
* 2025: none (replaced by the L. 207/2024 c. 4 sum).
The texts of L. 234/2021 c. 121 and L. 197/2022 c. 281 could not be retrieved (normattiva and the Gazzetta serve only
the first part of their art. 1); their points are the ones the fetched DL 115/2022 art. 20 and DL 48/2023 art. 39
increase. `oecd`: the OECD's 2022 convention, 0,8 points for all 13 periods (no DL 115/2022 increase). -/
def cuneoCap2692 : Int := eur 2692
def cuneoCap1923 : Int := eur 1923
def esoneroBp13 (y : Nat) (low : Bool) (oecd : Bool := false) (em : Bool := false) : Int :=
  if em ∧ y = 2022 then 13 * 140
  else if em ∧ y = 2023 then (if low then 13 * 500 else 13 * 400)
  else if y = 2022 then (if oecd then 13 * 80 else 6 * 80 + 7 * 200)
  else if y = 2023 then (if low then 7 * 300 + 6 * 700 else 7 * 200 + 6 * 600)
  else if y = 2024 then (if low then 12 * 700 else 12 * 600)
  else 0

/-- `--euromod` (convention, not statute): EUROMOD Country Report Italy 2022-2025 (JRC, 2026; software/euromod/
country_reports/Y16_CR_IT.txt), section 2.2.1: "In the model the annual average social contribution rate (i.e. 4% and
5% respectively) has been applied", and the notes to its employee SIC table: "In 2022: decontribution of -0.8 p.p. in
the period January-June; -2 p.p. in the period July-December; yearly average: -1.4 p.p. ... In 2023: yearly average:
-4.19% and 5.19% ... In 2024: ... for 12 months over 13". EUROMOD therefore applies the 12-month average reduction to
the whole year's pay (1,4 points in 2022; 5 / 4 points in 2023), where the statute (DL 115/2022 art. 20, L. 197/2022
c. 281, DL 48/2023 art. 39) gives 0,8 / 2 points by pay period incl. the tredicesima (2022) and 3-2 / 7-6 points with
the tredicesima at the January rate (2023). 2024: the same as statute (12 of 13 periods). -/
theorem esonero_em_2024 (low : Bool) : esoneroBp13 2024 low false true = esoneroBp13 2024 low := by
  cases low <;> rfl
theorem esonero_em_2025 (low : Bool) : esoneroBp13 2025 low false true = esoneroBp13 2025 low := by
  cases low <;> rfl

/-- D.Lgs. 230/2021 art. 4 c. 11 revaluation of the assegno unico, cumulated from 2022 terms (unrounded, as for
2025): 2022 = 1; 2023 = 1,081; 2024 = 1,081 × 1,054 = 1,139374; 2025 `auuFnum`. -/
def auuFnumY (y : Nat) : Int :=
  if y ≤ 2022 then 1000000000 else if y = 2023 then 1081000000 else if y = 2024 then 1139374000 else auuFnum

/-- Months of assegno unico in the year: from March 2022 (D.Lgs. 230/2021 art. 10 cc. 2-5: ANF and the art. 65 L.
448/1998 assegno for families with children cease "a decorrere dal 1° marzo 2022"; DL 73/2022 art. 38 c. 2:
"mensilità spettanti da marzo 2022"). `oecd`: the OECD counts 12 months in 2022. -/
def auuMonthsY (y : Nat) (oecd : Bool := false) : Int := if y = 2022 ∧ !oecd then 10 else 12

/-- Art. 4 c. 1 (text in force 2023-06-30): "A decorrere dal 1° gennaio 2023 ... incrementati del 50 per cento": the
under-one and 1-3-year (three or more children) increases exist from 2023 (absent in the 2022-06-30 text). -/
def auuYoungFrom : Nat := 2023

/-- TUIR art. 12 c. 1 c) in force 2022-01-15 (before D.Lgs. 230/2021 art. 10 c. 4, effective 1 March 2022, c. 5):
"950 euro per ciascun figlio ... La detrazione è aumentata a 1.220 euro per ciascun figlio di età inferiore a tre
anni ... Per i contribuenti con più di tre figli a carico la detrazione è aumentata di 200 euro per ciascun figlio a
partire dal primo"; base 95.000 + 15.000 per further child; art. 12 c. 3: "rapportate a mese": January-February 2022
= 2/12 of the year's amount. -/
def figlioOldU3 : Int := eur 1220
def figlioOldMany : Int := eur 200

/-- Roma Capitale 2022-2024: MEF register (anno 2022, 2023, 2024: delibera A.C. 14/2015 "conferma"): "Esenzione per
redditi imponibili fino a euro 12.000,00; 0,9 Aliquota unica". -/
def romaExemptY (y : Nat) : Int := if y ≤ 2024 then eur 12000 else romaExempt

/-- Lazio, MEF register of regional rates (`refs/it/mef_addreg_lazio_<year>.html`): 1,73 % to 15.000 and 3,33 %
above in 2022, 2023 and 2024, with
* 2022 (L.R. 29 marzo 2022 n. 7 art. 1 cc. 1-2; L.R. 17/2016 art. 2): 1,73 % on the whole base when it is "non
  superiore a 35.000,00 euro" (a); a detrazione of 300,00 euro for bases "non superiore a 40.000,00 euro" that do not
  benefit from (a); no credit. The 50.000 thresholds of (b)-(d) (three or more children, disabled children, disabled
  over-70s) are not modelled.
* 2023 (L.R. 1/2023 art. 2 c. 1): no relief.
* 2024 (L.R. 25 marzo 2024 n. 4): 1,73 % on the whole base "fino a 28.000,00 euro"; a detrazione of 60,00 euro for
  bases "non superiore a 35.000,00 euro"; "Le suddette agevolazioni non sono cumulabili tra loro". -/
def lazio2022Exempt : Int := eur 35000
def lazio2022Detr : Int := eur 300
def lazio2022DetrHi : Int := eur 40000

end ITTax
