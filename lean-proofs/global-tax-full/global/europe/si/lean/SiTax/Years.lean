import TaxKernel
import SiTax.Params

/-!
# Slovenia: parameters by tax year (2022-2025) and the child-benefit tables by period (round 2, 2026-11-19)

Copies of the dated texts are in `cmp20/improve-central/refs/si/` (fetched 2026-11-19) and `cmp20/central/si/refs/`:
* FURS, "Obvestilo o lestvici za odmero dohodnine in olajšave za leto 2022" (24. 3. 2022; ZDoh-2 as amended by
  Ur. l. RS 39/22 and the Pravilnik Ur. l. RS 41/22): `improve-central/refs/si/fu_Lestvica_2022.txt`;
  "... za leto 2023" (19. 12. 2022; ZDoh-2 incl. 158/22): `fu_Lestvica_2023.txt`;
  "... za leto 2024" (11. 12. 2023; ZIPRS2425 čl. 77: no indexation for 2024): `central/si/refs/fu_Lestvica_2024.txt`.
* Sklep o usklajenih višinah transferjev (ZUTPG čl. 3): Ur. l. RS 17/22 (SKLE12652, "od 1. marca 2022"),
  25/23 (SKLE13135, "od 1. marca 2023"), 15/24 (SKLE13562, "od 1. marca 2024"), 9/25 (SKLE13906, "od 1. marca
  2025"): `improve-central/refs/si/SKLE*_*.txt` (PISRS API by sop) and `central/si/refs/skle13906_transferji_2025.txt`.
* FURS "Obvezni zdravstveni prispevek - OZP": "S 1. januarjem 2024 je bil uveden obvezni zdravstveni prispevek",
  35,00 EUR from 1. 1. 2024 (`central/si/refs/fu_Obvezni_zdravstveni_prispevek_-_OZP.txt`): no OZP in 2022-2023.
* Employee contribution rates 15,50 + 6,36 + 0,10 + 0,14 = 22,10 % (FURS brošura 2.2); the 1 % long-term care
  contribution only "za obdobje od 1. julija 2025 dalje" (ZDOsk-1): 22,10 % in 2022-2024; s.p. 38,20 % before July
  2025 (brošura 3.1).
-/

namespace SiTax
open TaxKernel

/-- One tax year's parameters (cents, basis points). -/
structure YP where
  sched : Schedule
  /-- bracket edges (for the parents' cheapest split) -/
  edges : List Int
  generalTaper : Taper
  /-- čl. 114(1) child allowances for the first five children, and the step for each further child -/
  child5 : List Int
  childStep : Int
  otherDep : Int
  age70 : Int
  young : Int
  /-- employee contribution rate for the year (bp) -/
  eeRate : Int
  /-- OZP for the year (cents) -/
  ozp : Int
  /-- pensioner's long-term care contribution for the year (bp of the annual pension) -/
  pensionLtc : Int
  /-- s.p. contribution rate for the year (bp) -/
  seRate : Int
  deriving Inhabited

/-- 2025: exactly the 2025 parameters of `Params.lean`. -/
def yp2025 : YP :=
  { sched, edges := [0, 921026, 2708900, 5417800, 7801632], generalTaper,
    child5 := [283830, 308552, 514639, 720726, 926812], childStep := 206087, otherDep := otherDependant,
    age70 := age70Allowance, young := youngWorkerAllowance, eeRate := employeeRate, ozp := ozpYear,
    pensionLtc := pensionLtcRate, seRate }

/-- 2024 (FURS Lestvica 2024): "8.755,00 ... 25.750,00 ... 51.500,00 ... 74.160,00", 16/26/33/39/50 %; general
allowance "5.000,00 + (18.761,40 - 1,17259 x skupni dohodek)" up to 16.000,00, else 5.000,00; children "2.698,00 ...
2.933,00 ... 4.892,00 ... 6.851,00 ... 8.810,00", further "+1.959,00"; other dependant "2.698,00"; 70+ "1.500,00";
employee up to 29 "1.300,00"; OZP 12 x 35,00. -/
def yp2024 : YP :=
  { sched := Schedule.ofList [(0, 1600), (875500, 2600), (2575000, 3300), (5150000, 3900), (7416000, 5000)],
    edges := [0, 875500, 2575000, 5150000, 7416000],
    generalTaper := { full := 500000 + 1876140, start := 0, num := 117259, den := 100000, floor := 500000 },
    child5 := [269800, 293300, 489200, 685100, 881000], childStep := 195900, otherDep := 269800,
    age70 := 150000, young := 130000, eeRate := 2210, ozp := 12 * 3500, pensionLtc := 0, seRate := 3820 }

/-- 2023 (FURS Lestvica 2023): the same amounts as 2024 (the 2024 notice carries them over), no OZP. -/
def yp2023 : YP := { yp2024 with ozp := 0 }

/-- 2022 (FURS Lestvica 2022, ZDoh-2 as amended by Ur. l. RS 39/22): brackets as 2023 but the top rate "+ 45 % nad
74.160,00"; general allowance "4.500,00 + (19.261,43 - 1,40427 x skupni dohodek)" up to 13.716,33, else 4.500,00;
children "2.510,03 ... 2.728,72 ... 4.551,10 ... 6.373,48 ... 8.195,86", further "+1.822,38"; other dependant
"2.510,03"; 70+ "1.500,00"; no allowance for employees up to 29 in the 2022 notice; no OZP. -/
def yp2022 : YP :=
  { sched := Schedule.ofList [(0, 1600), (875500, 2600), (2575000, 3300), (5150000, 3900), (7416000, 4500)],
    edges := [0, 875500, 2575000, 5150000, 7416000],
    generalTaper := { full := 450000 + 1926143, start := 0, num := 140427, den := 100000, floor := 450000 },
    child5 := [251003, 272872, 455110, 637348, 819586], childStep := 182238, otherDep := 251003,
    age70 := 150000, young := 0, eeRate := 2210, ozp := 0, pensionLtc := 0, seRate := 3820 }

/-- The years implemented; any other year is computed as 2025. -/
def yp (y : Nat) : YP :=
  if y = 2022 then yp2022 else if y = 2023 then yp2023 else if y = 2024 then yp2024 else yp2025

/-- čl. 114(1): the allowance for the child of rank `n` (0 = first) in year `y`. -/
def childAmountY (y : Nat) (n : Nat) : Int :=
  let p := yp y
  if n < 5 then p.child5.getD n 0 else p.child5.getD 4 0 + p.childStep * ((n : Int) - 4)

def childTotalY (y : Nat) (n : Nat) : Int := ((List.range n).map (childAmountY y)).foldl (· + ·) 0

theorem yp_2025_child : (List.range 8).map (childAmountY 2025) = (List.range 8).map childAmount := by decide

/-- FURS 2024 fixed amounts at the bracket edges: "1.400,80", "5.819,50", "14.317,00", "23.154,40". -/
theorem furs_2024_fixed :
    yp2024.sched.tax Rule.unitHalfUp 875500 = 140080 ∧ yp2024.sched.tax Rule.unitHalfUp 2575000 = 581950 ∧
    yp2024.sched.tax Rule.unitHalfUp 5150000 = 1431700 ∧ yp2024.sched.tax Rule.unitHalfUp 7416000 = 2315440 := by
  decide

/-- The 2022 general allowance is back to its floor at "13.716,33" (19.261,43 - 1,40427 x 13.716,33 = 0). -/
theorem general_2022_limit : yp2022.generalTaper.amount 1371633 = 450000 ∧
    450000 < yp2022.generalTaper.amount 1371500 := by decide

/-! ## Otroški dodatek tables (one per Sklep) -/

/-- A child-benefit table: upper limits of classes 1-8 (cents of monthly income per person), the amounts per class
for children up to the end of primary school (1st, 2nd, 3rd+ child), the secondary-school amounts of classes 7 and
8 (classes 1-6 are the same), and the annual large-family allowance for three / four or more children (ZSDP-1
čl. 77 as indexed). -/
structure CBT where
  limits : List Int
  prim : List (List Int)
  sec7 : List Int
  sec8 : List Int
  lf3 : Int
  lf4 : Int
  deriving Inhabited

/-- Sklep Ur. l. RS 9/25 (from 1. 3. 2025): the amounts of `Params.childBenefitMonthly`. -/
def cb2025 : CBT :=
  { limits := [23514, 39192, 47031, 54869, 69242, 83610, 107128, 129336],
    prim := [[14381, 15818, 17258], [12294, 13591, 14880], [9371, 10473, 11573], [7391, 8433, 9495],
             [6043, 7052, 8055], [3829, 4792, 5750], [2874, 3829, 4792], [2502, 3460, 4416]],
    sec7 := [3627, 4583, 6245], sec8 := [2879, 3837, 5018], lf3 := 49693, lf4 := 60386 }

/-- Sklep Ur. l. RS 15/24 (from 1. 3. 2024): "do 230,76 | 141,13 | 155,23 | 169,36", ..., "od 1.051,32 do 1.269,24 |
24,55 | 33,95 | 43,34 | 28,25 | 37,65 | 49,24"; large family "487,66" / "592,60". -/
def cb2024 : CBT :=
  { limits := [23076, 38461, 46154, 53846, 67951, 82051, 105131, 126924],
    prim := [[14113, 15523, 16936], [12065, 13338, 14603], [9196, 10278, 11357], [7253, 8276, 9318],
             [5930, 6921, 7905], [3758, 4703, 5643], [2820, 3758, 4703], [2455, 3395, 4334]],
    sec7 := [3559, 4498, 6129], sec8 := [2825, 3765, 4924], lf3 := 48766, lf4 := 59260 }

/-- Sklep Ur. l. RS 25/23 (from 1. 3. 2023): "do 221,46 | 135,44 | 148,97 | 162,53", ..., "od 1.008,94 do 1.218,08 |
23,56 | 32,58 | 41,59 | 27,11 | 36,13 | 47,26"; large family "468,00" / "568,71". -/
def cb2023 : CBT :=
  { limits := [22146, 36911, 44294, 51676, 65212, 78744, 100893, 121808],
    prim := [[13544, 14897, 16253], [11579, 12800, 14014], [8825, 9864, 10899], [6961, 7942, 8942],
             [5691, 6642, 7586], [3607, 4513, 5416], [2706, 3607, 4513], [2356, 3258, 4159]],
    sec7 := [3416, 4317, 5882], sec8 := [2711, 3613, 4726], lf3 := 46800, lf4 := 56871 }

/-- Sklep Ur. l. RS 17/22 (from 1. 3. 2022): "do 200,78 | 122,79 | 135,06 | 147,35", ..., "od 914,72 do 1.104,33 |
21,36 | 29,54 | 37,71 | 24,58 | 32,76 | 42,85"; large family "424,30" / "515,60". -/
def cb2022 : CBT :=
  { limits := [20078, 33464, 40158, 46850, 59122, 71391, 91471, 110433],
    prim := [[12279, 13506, 14735], [10498, 11605, 12705], [8001, 8943, 9881], [6311, 7200, 8107],
             [5160, 6022, 6878], [3270, 4092, 4910], [2453, 3270, 4092], [2136, 2954, 3771]],
    sec7 := [3097, 3914, 5333], sec8 := [2458, 3276, 4285], lf3 := 42430, lf4 := 51560 }

/-- The table in force from 1 March of year `y` (2022-2025). -/
def cbFor (y : Nat) : CBT :=
  if y = 2022 then cb2022 else if y = 2023 then cb2023 else if y = 2024 then cb2024 else cb2025

/-- The table in force in January-February of year `y`: the previous year's Sklep. For 2022 the 2021 amounts were not
fetched: the March-2022 table is used (stated in `unsupported`). -/
def cbJanFeb (y : Nat) : CBT :=
  if y = 2023 then cb2022 else if y = 2024 then cb2023 else if y = 2025 then cb2024 else cbFor y

/-- Income class (1-8; 0 above class 8) for a monthly income per person (cents). -/
def CBT.cls (t : CBT) (x : Int) : Int :=
  let k : Int := (t.limits.filter (· < x)).length
  if k ≥ 8 then 0 else k + 1

/-- Monthly amount by class and child rank (0 = first); `secondary`: a child aged 15 or more. -/
def CBT.amount (t : CBT) (cls : Int) (rank : Nat) (secondary : Bool) : Int :=
  let r := min rank 2
  if cls < 1 ∨ cls > 8 then 0
  else if secondary ∧ cls = 7 then t.sec7.getD r 0
  else if secondary ∧ cls = 8 then t.sec8.getD r 0
  else (t.prim.getD (cls.toNat - 1) []).getD r 0

def CBT.largeFamily (t : CBT) (n : Nat) : Int := if n ≥ 4 then t.lf4 else if n = 3 then t.lf3 else 0

/-- The 2025 table reproduces `Params.classTable` at every class edge and `Params.childBenefitMonthly` for every
class, rank and school level. -/
theorem cb2025_classes : [0, 23514, 23515, 39192, 39193, 54869, 54870, 107128, 107129, 129336, 129337].map
    cb2025.cls = [0, 23514, 23515, 39192, 39193, 54869, 54870, 107128, 107129, 129336, 129337].map
    (fun x => classTable.lookup x 0) := by decide
theorem cb2025_amounts : (((List.range 10).map (fun c : Nat => (c : Int))).flatMap fun c => (List.range 3).flatMap fun r =>
    [cb2025.amount c r false, cb2025.amount c r true]) =
    (((List.range 10).map (fun c : Nat => (c : Int))).flatMap fun c => (List.range 3).flatMap fun r =>
    [childBenefitMonthly c r false, childBenefitMonthly c r true]) := by decide

end SiTax
