import LuTax.Params

/-!
# Luxembourg: tax years 2022, 2023, 2024 (improvement round 6, 2026-11-19)

Statute: L.I.R. "texte coordonné en vigueur au 1er janvier" 2022 (actualisation 28/09/2022), 2023 (11/07/2023) and
2024 (07/03/2025), published by the ACD (https://impotsdirects.public.lu/dam-assets/fr/legislation/LIR/LIR2022.pdf,
LIR2023.pdf, LIR2024.pdf; copies and text in `~/cmp20/improve-central/refs/lu/`). Each article is cited with the
amending laws printed under it in that text. Energy tax credits: loi du 29 juin 2022 (Mémorial A 2022 n° 317,
`refs/lu/loi_2022-06-29_a317.txt`), art. 154sexies-154octies as consolidated in LIR2023/LIR2024. Social parameters: the
CCSS table "Nombre indice, salaire social minimum non-qualifié, minimum et maximum cotisable" (as for 2025,
`germanic/lu/refs/ccss_parametres_sociaux.txt`). Allocations familiales: CSS art. 272 al. 3 (L. 17.12.21, 26, 2°:
indexed like civil servants' pay) and the derogation of L. 19.6.22, 4 ("échelle mobile des allocations familiales",
EMAF, 1.4.2022-1.4.2023) (`germanic/lu/law/css_20250101.txt`).

2025 is NOT computed from this file: `yearP? 2025 = none` and the 2025 functions of `Basic.lean` are used unchanged.
-/

namespace LuTax
open TaxKernel

/-- L.I.R. art. 118 (L. 23.12.16), identical in the coordinated texts of 1.1.2022 and 1.1.2023: "0% ... inférieure à
11.265 euros; 8% ... entre 11.265 et 13.137 euros; ... 39% ... entre 45.897 et 100.002 euros; 40% ... 100.002 et
150.000 euros; 41% ... 150.000 et 200.004 euros; 42% ... dépassant 200.004 euros". -/
def tarifBands2017 : List (Int × Int) :=
  [(0, 0), (11265, 800), (13137, 900), (15009, 1000), (16881, 1100), (18753, 1200), (20625, 1400),
   (22569, 1600), (24513, 1800), (26457, 2000), (28401, 2200), (30345, 2400), (32289, 2600), (34233, 2800),
   (36177, 3000), (38121, 3200), (40065, 3400), (42009, 3600), (43953, 3800), (45897, 3900), (100002, 4000),
   (150000, 4100), (200004, 4200)]

/-- L.I.R. art. 118 (L.23.12.16 - L.05.07.23,2 - L.22.12.23,2), coordinated text of 1.1.2024 ("Barème ... applicable
à partir de l'année d'imposition 2024"): "0% ... inférieure à 12.438 euros; 8% ... entre 12.438 et 14.508 euros; ...
39% ... entre 50.751 et 110.403 euros; 40% ... 110.403 et 165.600; 41% ... 165.600 et 220.788; 42% ... dépassant
220.788 euros". -/
def tarifBands2024 : List (Int × Int) :=
  [(0, 0), (12438, 800), (14508, 900), (16578, 1000), (18648, 1100), (20718, 1200), (22788, 1400),
   (24939, 1600), (27090, 1800), (29241, 2000), (31392, 2200), (33543, 2400), (35694, 2600), (37845, 2800),
   (39996, 3000), (42147, 3200), (44298, 3400), (46449, 3600), (48600, 3800), (50751, 3900), (110403, 4000),
   (165600, 4100), (220788, 4200)]

/-- The year-specific parameters (euros unless named `C` = cents; `M10` = per 10 000). -/
structure YearP where
  tarifBands : List (Int × Int)
  /-- art. 120bis: class 1a: the tarif applied to the RIA "réduit de la moitié de son complément à" `c1aC` euros -/
  c1aC : Int
  /-- ... "sous réserve que le taux d'accroissement maximal ne puisse pas dépasser 39%" from `c1aCap`, then 40 / 41 /
  42 % at the tarif's thresholds (`c1aCapBands`) -/
  c1aCap : Int
  c1aCapBands : List (Int × Int)
  /-- CIS / CIP / CII (art. 154quater, 154quinquies, 152ter): base, full amount, phase-out per 10 000 -/
  cisBase : Int
  cisFull : Int
  cisOutM10 : Int
  /-- CI-CO2 (a separate credit from 2024): full amount, phase-out per 10 000. 0 in 2022-23, where the CO2
  compensation is inside the CIS of 696 euros. -/
  co2Full : Int
  co2OutM10 : Int
  /-- CIM (art. 154ter (2)): `cimFull` below `cimStart`, then minus (RIA - start) x num/den, `cimFloor` above `cimEnd` -/
  cimFull : Int
  cimStart : Int
  cimNum : Int
  cimDen : Int
  cimEnd : Int
  cimFloor : Int
  /-- CISSM (art. 139quater (3)), monthly -/
  cissmFull : Int
  cissmLow : Int
  cissmKink : Int
  cissmEnd : Int
  /-- months (1-12) in which the CIE salarié / pensionné (art. 154septies, 154octies) applies -/
  cieMonths : List Int
  /-- the crédit d'impôt conjoncture (CIC, art. 154nonies-154undecies, L.05.07.23,9-11: "Article uniquement applicable
  pour l'année d'imposition 2023") -/
  cic : Bool := false
  /-- CCSS table, per month Jan..Dec: social minimum wage and maximum cotisable (cents, monthly) -/
  ssmC : List Int
  maxCotC : List Int
  /-- index (x 100) of the allocations familiales per month Jan..Dec -/
  afIdx : List Int

def rep (n : Nat) (x : Int) : List Int := List.replicate n x

/-- 2022.
* tarif `tarifBands2017`; art. 120bis (L.23.12.16,1er,15°): "réduit de la moitié de son complément à 45.060 euros ...
  39% pour la tranche de revenu comprise entre 37.842 euros et 100.002 euros, 40% ... 100.002 euros et 150.000 euros,
  41% ... 150.000 euros et 200.004 euros et 42% ... dépassant 200.004 euros".
* art. 154quater (2) (L.17.12.21,3,13): "de 936 euros à 11.265 euros, le CIS s'élève à [396 + (salaire brut - 936) x
  0,029] ... de 11.266 euros à 40.000 euros, ... 696 euros ... de 40.001 euros à 79.999 euros, ... [696 - (salaire brut
  - 40.000) x 0,0174]"; art. 154quinquies (2): the CIP the same, and "de 300 à 935 euros, le CIP s'élève à 396 euros";
  art. 152ter: the CII the same, and 300 euros below 936.
* art. 154ter (2) (L.23.12.16,1er,28°): "1.500 euros lorsque le revenu imposable ajusté ... est inférieur à 35.000
  euros et à 750 euros lorsque ... supérieur à 105.000 euros ... la différence entre ... 1.875 euros et ... le produit de
  la multiplication du revenu imposable ajusté avec le quotient dont le numérateur s'élève à 750 euros et le
  dénominateur à 70.000 euros" (= 1 500 - (RIA - 35 000) x 750/70 000).
* art. 139quater (3) (L.17.12.21,3,12): "de 1 500 euros à 2 500 euros, le CISSM s'élève à 70 euros par mois, de 2 500
  à 3 000 euros, ... 70 / 500 x [3 000 – salaire brut mensuel (fictif)]".
* art. 154septies / 154octies (loi du 29.6.2022): the CIE runs from "le premier jour du mois pour lequel la première
  adaptation des traitements ... serait déclenchée au cours des mois de mai à décembre 2022 ... et le 31 décembre 2022
  inclus". That month is July 2022 (`Index.firstAdapt2022`, below: loi du 25.3.2015 art. 3 (2)-(4) applied to STATEC's
  published semestrial averages; round 7). The same month is the first EMAF adaptation of the allocations familiales (CSS art. 272, L. 19.6.22, 4: "un mois après que la
  moyenne semestrielle ... a accusé une différence de deux pour cent et demi par rapport à la cote d'échéance de
  l'échelle mobile des salaires d'avril 2022 augmentée de deux pour cent et demi").
* CCSS: 01.01.2022 index 855,62, SSM 2.256,95, maximum 11.284,77; 01.04.2022 index 877,01, SSM 2.313,38, maximum
  11.566,88. Allocations: 855,62 (Jan-Mar), 877,01 (Apr-Jun), EMAF 898,93 (= 877,01 x 1,025; from July: `Index.firstAdapt2022`). -/
def yp2022 : YearP :=
  { tarifBands := tarifBands2017, c1aC := 45060, c1aCap := 37842,
    c1aCapBands := [(0, 0), (37842, 3900), (100002, 4000), (150000, 4100), (200004, 4200)],
    cisBase := 396, cisFull := 696, cisOutM10 := 174, co2Full := 0, co2OutM10 := 0,
    cimFull := 1500, cimStart := 35000, cimNum := 750, cimDen := 70000, cimEnd := 105000, cimFloor := 750,
    cissmFull := 70, cissmLow := 1500, cissmKink := 2500, cissmEnd := 3000,
    cieMonths := [7, 8, 9, 10, 11, 12],
    ssmC := rep 3 225695 ++ rep 9 231338, maxCotC := rep 3 1128477 ++ rep 9 1156688,
    afIdx := rep 3 85562 ++ rep 3 87701 ++ rep 6 89893 }

/-- 2023.
* tarif and art. 120bis as in 2022 (coordinated text of 1.1.2023, actualised 11/07/2023: unchanged; the loi du
  5.7.2023 changes art. 118 only in the 1.1.2024 text, "applicable à partir de l'année d'imposition 2024").
* CIS / CIP / CII as in 2022 (art. 154quater, 154quinquies, 152ter of the 1.1.2023 text: same amounts).
* art. 154ter (2) (L.23.12.22,3,10): "inférieur à 60 000 euros, ... 2 505 euros; ... entre 60 000 euros et 105 000
  euros, ... [2 505 – (revenu imposable ajusté – 60 000) x 0,039]; ... supérieur à 105 000 euros, ... 750 euros".
* art. 139quater (3) (L.23.12.22,3,9): "de 1 800 euros à 3 000 euros, le CISSM s'élève à 70 euros par mois, de 3 000
  à 3 600 euros, ... 70 / 600 x [3 600 – salaire brut mensuel (fictif)]".
* art. 154septies (2) b), 154octies (2) b): CIE "Pour l'année d'imposition 2023" with the 2022 monthly amounts,
  "entre le 1er janvier 2023 et le 31 mars 2023 inclus".
* art. 154decies / 154undecies (L.05.07.23,10-11; LIR2023 text, and "Article uniquement applicable pour l'année
  d'imposition 2023" in LIR2024): the CIC salarié / pensionné, monthly, all of 2023 (table in `Basic.cicMonthC`);
  art. 154nonies: the CIC indépendant, annual (`Basic.cicIndepC`).
* CCSS: 01.01.2023 877,01 / SSM 2.387,40 / max 11.936,98; 01.02.2023 898,93 / 2.447,07 / 12.235,34; 01.04.2023
  921,40 / 2.508,24 / 12.541,18; 01.09.2023 944,43 / 2.570,93 / 12.854,64.
* Allocations: EMAF 898,93 in January; the second EMAF adaptation 921,40 (= 898,93 x 1,025) from February
  (`Index.secondAdapt2023`: the cote d'échéance 964,87 is first reached by the semestrial average of January 2023, so
  the adaptation is triggered one month later; the same crossing gives the CCSS salary tranche of 01.02.2023); from 1.4.2023 the general rule (civil
  servants' index): 921,40, then 944,43 from September. -/
def yp2023 : YearP :=
  { yp2022 with
    cimFull := 2505, cimStart := 60000, cimNum := 39, cimDen := 1000, cimEnd := 105000, cimFloor := 750,
    cissmFull := 70, cissmLow := 1800, cissmKink := 3000, cissmEnd := 3600,
    cieMonths := [1, 2, 3], cic := true,
    ssmC := [238740, 244707, 244707] ++ rep 5 250824 ++ rep 4 257093,
    maxCotC := [1193698, 1223534, 1223534] ++ rep 5 1254118 ++ rep 4 1285464,
    afIdx := [89893] ++ rep 7 92140 ++ rep 4 94443 }

/-- 2024.
* art. 118 (L.05.07.23,2 - L.22.12.23,2): `tarifBands2024`; art. 120bis (L.05.07.23,3 - L.22.12.23,3): "réduit de la
  moitié de son complément à 49.752 euros ... 39% pour la tranche de revenu comprise entre 41.814 euros et 110.403
  euros, 40% ... 110.403 euros et 165.600 euros, 41% ... 165.600 euros et 220.788 euros et 42% ... dépassant 220.788".
* art. 154quater (2) (L.05.07.23,7 - L.22.12.23,1,2°): CIS "[300 + (salaire brut - 936) x 0,029] ... 600 euros ...
  [600 - (salaire brut - 40.000) x 0,015]"; "CI-CO2 salarié ... de 936 euros à 40.000 euros ... 168 euros par an, de
  40.001 euros à 79.999 euros, ... [168 - (salaire brut - 40.000) x 0,0042]"; art. 154quinquies: CIP 300 / 600 and
  CI-CO2 pensionné 168 "de 300 euros à 40.000 euros".
* art. 154ter (2): as in 2023 (2 505 / 0,039 / 750). art. 139quater (3): as in 2023 (70; 1 800 / 3 000 / 3 600).
* CIE: none (its periods ended on 31.3.2023).
* CCSS: 01.01.2024 index 944,43, SSM 2.570,93, maximum 12.854,64, all year; allocations at 944,43 all year. -/
def yp2024 : YearP :=
  { yp2023 with
    tarifBands := tarifBands2024, c1aC := 49752, c1aCap := 41814,
    c1aCapBands := [(0, 0), (41814, 3900), (110403, 4000), (165600, 4100), (220788, 4200)],
    cisBase := 300, cisFull := 600, cisOutM10 := 150, co2Full := 168, co2OutM10 := 42,
    cieMonths := [], cic := false,
    ssmC := rep 12 257093, maxCotC := rep 12 1285464, afIdx := rep 12 94443 }


/-! ## Index months (round 7, 2026-11-19): every adaptation month cited, none remembered

* Loi du 25 mars 2015 fixant le régime des traitements ... des fonctionnaires de l'État, art. 3 (Mémorial A, legilux
  `eli/etat/leg/loi/2015/03/25/n3/jo`, copy `improve-central/refs/lu/loi2015_n3.txt`): (2) "L'adaptation est
  déclenchée un mois après que cet indice [the semestrial average] a accusé une différence de deux pour-cent et demi par
  rapport à la cote ayant déclenché l'adaptation précédente. Cette cote est dénommée cote d'échéance. Le point de
  départ pour le calcul de la cote d'échéance est le niveau moyen de 437,83 points atteint au 1er septembre 1984."
  (4) "Les cotes dont question ci-dessus sont calculées au centième près."
* Loi du 29 juin 2022 (Mémorial A 317) art. 3: new art. 3 (7) "la première adaptation déclenchée après le 1er avril 2022
  est effectuée le 1er avril 2023"; art. 4: CSS art. 272, EMAF 1.4.2022-1.4.2023, "La première adaptation est
  déclenchée un mois après que la moyenne semestrielle ... a accusé une différence de deux pour cent et demi par rapport
  à la cote d'échéance de l'échelle mobile des salaires d'avril 2022 ...; les adaptations subséquentes ... par rapport à
  la cote d'échéance EMAF ayant déclenché l'adaptation précédente"; CIE: "le premier jour du mois pour lequel la
  première adaptation ... serait déclenchée au cours des mois de mai à décembre 2022".
* STATEC, "Six month moving average of the National Consumer Price index, base 100 in 1.1.1948", LUSTAT SDMX dataflow
  `LU1,DSD_PRIX_CONSO@DF_E5101,1.0`, https://lustat.statec.lu/rest/data/LU1,DSD_PRIX_CONSO@DF_E5101,1.0/all?startPeriod=2021-06&endPeriod=2023-12
  (fetched 2026-11-19, `improve-central/refs/lu/r7/DF_E5101.csv`, sha256 ac804e4f...).
* Check against the CCSS application dates (01.10.2021, 01.04.2022, 01.02.2023, 01.09.2023): the chain's crossings
  give exactly those months (`crossings_match_ccss`), so the chain needs no reset in this period.
-/
namespace Index

/-- Art. 3 (2)-(4): the cote d'échéance chain in hundredths, from 437,83 points (1.9.1984), each +2,5 % "au centième
près" (halves up). -/
def cote : Nat → Nat
  | 0 => 43783
  | n + 1 => (cote n * 1025 + 500) / 1000

/-- STATEC DF_E5101, semestrial averages (yyyymm, hundredths of a point), 2021-06 .. 2023-12. -/
def semAvg : List (Nat × Nat) :=
  [(202106, 88952), (202107, 89073), (202108, 89440), (202109, 89623), (202110, 89933), (202111, 90301),
   (202112, 90633), (202201, 91027), (202202, 91609), (202203, 92326), (202204, 93037), (202205, 93668),
   (202206, 94433), (202207, 95031), (202208, 95451), (202209, 95756), (202210, 96072), (202211, 96334),
   (202212, 96376), (202301, 96506), (202302, 96748), (202303, 97001), (202304, 97261), (202305, 97566),
   (202306, 98022), (202307, 98478), (202308, 98904), (202309, 99293), (202310, 99534), (202311, 99710),
   (202312, 99807)]

/-- The first month whose semestrial average reaches the cote `c`. -/
def firstCross (c : Nat) : Option Nat := (semAvg.find? (fun p => c ≤ p.2)).map (·.1)

/-- The month after `yyyymm` (the adaptation "un mois après"). -/
def nextMonth (m : Nat) : Nat := if m % 100 = 12 then (m / 100 + 1) * 100 + 1 else m + 1

theorem cotes : cote 29 = 89598 ∧ cote 30 = 91838 ∧ cote 31 = 94134 ∧ cote 32 = 96487 ∧ cote 33 = 98899 := by decide

/-- The four salary tranches of the period fall on the CCSS application dates 01.10.2021, 01.04.2022, 01.02.2023 and
01.09.2023 (the July 2022 one is moved to 01.04.2023 by art. 3 (7)). -/
theorem crossings_match_ccss :
    (firstCross (cote 29)).map nextMonth = some 202110 ∧ (firstCross (cote 30)).map nextMonth = some 202204 ∧
    (firstCross (cote 32)).map nextMonth = some 202302 ∧ (firstCross (cote 33)).map nextMonth = some 202309 := by
  decide

/-- The first adaptation after April 2022 (cote 941,34) is triggered in July 2022: the CIE start month and the first
EMAF adaptation (898,93). -/
theorem firstAdapt2022 : (firstCross (cote 31)).map nextMonth = some 202207 := by decide

/-- The next one (cote 964,87): February 2023, the second EMAF adaptation (921,40). -/
theorem secondAdapt2023 : (firstCross (cote 32)).map nextMonth = some 202302 := by decide

end Index

/-- The year's parameters for 2022-2024; `none` = the 2025 model, unchanged. -/
def yearP? (y : Nat) : Option YearP :=
  if y = 2022 then some yp2022 else if y = 2023 then some yp2023 else if y = 2024 then some yp2024 else none

/-- The CIE months and the allocation index months of 2022-2023 are those the index chain gives. -/
theorem cie_af_months_cited : yp2022.cieMonths = [7, 8, 9, 10, 11, 12] ∧
    yp2022.afIdx.drop 6 = rep 6 89893 ∧ yp2022.afIdx.take 6 = rep 3 85562 ++ rep 3 87701 ∧
    yp2023.afIdx.take 1 = [89893] ∧ (yp2023.afIdx.drop 1).take 7 = rep 7 92140 := by decide

theorem yp_lengths : yp2022.ssmC.length = 12 ∧ yp2022.maxCotC.length = 12 ∧ yp2022.afIdx.length = 12 ∧
    yp2023.ssmC.length = 12 ∧ yp2023.maxCotC.length = 12 ∧ yp2023.afIdx.length = 12 ∧
    yp2024.ssmC.length = 12 ∧ yp2024.maxCotC.length = 12 ∧ yp2024.afIdx.length = 12 := by decide

/-- The CIM is continuous at its upper end in every year: 1 500 - 70 000 x 750/70 000 = 750 and
2 505 - 45 000 x 0,039 = 750. -/
theorem cim_ends : 1500 * 70000 - (105000 - 35000) * 750 = 750 * 70000 ∧
    2505 * 1000 - (105000 - 60000) * 39 = 750 * 1000 := by decide

end LuTax
