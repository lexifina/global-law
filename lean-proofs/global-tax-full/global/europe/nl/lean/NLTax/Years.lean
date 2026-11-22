import NLTax.Params

/-!
# Belastingjaren 2022-2024 (round 3, improve-continental)

Each amount is copied from the dated consolidated text on wetten.overheid.nl (the version in force on the date
given; saved in `../law/hist/`, fetched 2026-11-19): Wet IB 2001 (BWBR0011353) on 2022-01-01, 2023-01-01,
2024-01-01; AKW (BWBR0002368) on 2022-01-01, 2022-07-01, 2023-01-01, 2023-07-01, 2024-01-01 (with the retroactive
change to 2024-01-01 the page records), 2024-07-01; Wet op het kindgebonden budget (BWBR0022751) on 2022-01-01,
2023-01-01 (with Stcrt. 2023, 4605, retroactive to 2023-01-01), 2024-01-01; WML (BWBR0002638) art. 8 lid 1 on each
1 January ("per 1 januari 2022: EUR 1.725,00"; 2023: 1.934,40; 2024: 2.069,40 per maand).
* Art. 2.10 lid 1 (tax part, kolom I-IV): 2022 "EUR 35.472 | 9,42%", "EUR 35.472 | EUR 69.398 | EUR 3.341 | 37,07%",
  "EUR 69.398 | EUR 15.917 | 49,50%"; 2023 37.149 / 9,28%, 73.031 / 3.447 / 36,93%, 16.698 / 49,50%; 2024 38.098 /
  9,32%, 75.518 / 3.550 / 36,97%, 17.384 / 49,50%. Lid 2: 9,5% (2022), 12,57% (2023), 12,53% (2024).
* Art. 8.10 (reduced on "het belastbare inkomen uit werk en woning" in 2022-2024, not the verzamelinkomen): 2022
  EUR 2.888, 6,007%, above 21.317; 2023 3.070, 6,095%, 22.660; 2024 3.362, 6,630%, 24.812.
* Art. 8.11 lid 2 a-d: 2022 4,541% max 470; 28,461% above 10.350, cap 3.887; 2,610% above 22.356, cap 4.260; minus
  5,86% above 36.649. 2023 8,231% / 884; 29,861% / 10.740 / 4.605; 3,085% / 23.201 / 5.052; 6,51% / 37.691. 2024
  8,425% / 968; 31,433% / 11.490 / 5.158; 2,471% / 24.820 / 5.532; 6,51% / 39.957.
* Art. 8.14a lid 2: 11,45% above 5.219 (2022), 5.547 (2023), 6.073 (2024), max 2.534 / 2.694 / 2.950.
* Art. 8.17: 1.726 / 1.835 / 2.010, 15% of the verzamelinkomen above 38.464 / 40.888 / 44.770; art. 8.18: 449 / 478
  / 524.
* Premies volksverzekeringen 17,90 / 0,10 / 9,65 % (unchanged 2022-2025), capped at the first kolom-II amount of
  art. 2.10 (Wfsv art. 8 lid 3): taken from the year's table.
* AKW art. 12 lid 3, per quarter (younger than 6 / 6-11 / 12-17): 2022 Q1-Q2 230,69 / 280,13 / 329,56, Q3-Q4
  249,31 / 302,74 / 356,16; 2023 Q1-Q2 269,76 / 327,56 / 385,37, Q3-Q4 261,70 / 317,77 / 373,85; 2024 Q1-Q2 279,49
  / 339,38 / 399,27 (the retroactive replacement of 261,70 / 317,77 / 373,85), Q3-Q4 281,69 / 342,05 / 402,41.
* Wkb art. 2: 2022 lid 2 "een kind: EUR 1.220; twee kinderen: 2.326; drie: 3.327; meer dan drie: 3.327 verhoogd met
  zoveel maal EUR 1.001", lid 4 251, lid 5 447, lid 6 3.285, lid 7-8 6,75%, partner + 17.240; art. 1 lid 4
  wealth 120.020 / 151.767. 2023: "een kind: EUR 1.653; twee of meer: EUR 1.532 per kind voor het tweede of
  volgende kind", lid 4 267,00 and lid 5 476,00 and lid 8 18.327,00 (Stcrt. 2023, 4605, retroactive), lid 6
  3.848, 6,75%; wealth 127.582 / 161.329. 2024: 2.436 per child, 694,00, 924,00, 3.480, 6,75%, partner + 9.030,00;
  wealth 140.213 / 177.301. Drempelinkomen (art. 1 lid 1 d): 108% x 12 x the WML per maand of January.
* Art. 2.10a lid 1 (born before 1946; round 5): 2022 "EUR 36.409 | 9,42%", "36.409 | 69.398 | 3.429 | 37,07%",
  "69.398 | 15.658 | 49,50%"; 2023 38.703 / 9,28%, 73.031 / 3.591 / 36,93%, 16.268; 2024 40.021 / 9,32%, 75.518 /
  3.729 / 36,97%, 16.852.
* Box 3 (round 8): 2023 art. 2.13 "32%", art. 5.5 "EUR 57.000", art. 5.3 lid 3 f "EUR 3.400" (partners 6.800), art. 5.2
  lid 2 6,17% overige bezittingen, 2,46% schulden and banktegoeden 0,92% ("In het tweede lid, de tweede zin, wordt
  '0,01%' vervangen door '0,92%'", Stcrt. 2024, 12218, retroactive to 2023-01-01); 2024 "36%", EUR 57.000, EUR 3.700
  (7.400), 6,04% overige bezittingen, and "'0,92%' vervangen door '1,44%' en ... '2,46%' vervangen door '2,61%'"
  (Stcrt. 2025, 8295, retroactive to 2024-01-01). 2022 (the rendementsklassen text plus the Wet rechtsherstel box 3
  choice) is not modelled: flagged in `unsupported` when box-3 inputs are given.
* Box 3 2022 (round 9): Wet IB 2022 art. 2.13 "31%", art. 5.5 "EUR 50.650", art. 5.3 lid 3 f "EUR 3.200", art. 5.2 lid 1
  "-0,01% ... rendementsklasse I, vermeerderd met 5,53% ... rendementsklasse II" with the table (EUR 0-50.650: 67% / 33%;
  50.650-962.350: 21% / 79%; above: 0% / 100%); and the Wet rechtsherstel box 3 (BWBR0047699, consolidation of
  2025-07-19, `../law/hist/rh_BWBR0047699.txt`) art. 3: rendement 0,00% banktegoeden, 5,53% overige bezittingen, minus
  2,28% schulden, times grondslag / rendementsgrondslag; art. 1 lid 4: applied only "voor zover dit ... tot een lager
  voordeel uit sparen en beleggen leidt". Partners (round 10): the table is applied to each partner's allocated part of the joint
  grondslag (art. 5.2 lid 2), and the lower of the two methods is kept per partner (`box3Shares`).
* Box 2 (round 9), art. 2.12: 2022 and 2023 "bedraagt 26,9%"; 2024 "– | EUR 67.000 | – | 24,5%", "EUR 67.000 | – |
  EUR 16.415 | 33%".
* Zvw (round 9), Regeling zorgverzekering (BWBR0018715) art. 5.1 lid 2 (the percentage of Zvw art. 45 lid 2, paid by the
  insured on income without werkgeversheffing) and art. 5.2-5.3 (maximum bijdrage-inkomen): versions of 2022-02-01
  ("5,50", "EUR 59.706"), 2023-01-01 ("5,43", "EUR 66.956"), 2024-01-01 ("5,32", "EUR 71.628"); pages saved
  (gzipped) in `../law/hist/regeling_zvw_*.html.gz` (the 2022-01-01 address answers with an error page; the 2022-02-01
  version prints the 2022 amounts).
Earlier note (rounds 3-5; box 2, box 3 2023-2024 and the Zvw now superseded): box 2  and box 3, the Zvw bijdrage (self-employed / pensions), zelfstandigenaftrek and MKB-vrijstelling, the
OECD's pension convention (`--oecd`).
-/

namespace NLTax

structure YP where
  year : Nat
  t210 : Table3
  /-- Art. 2.10a (born before 1 January 1946), round 5. -/
  t210a : Table3
  grondslagRate : Int
  ahkOnVi : Bool
  ahkMax : Int
  ahkRate : Int
  ahkStart : Int
  akRateA : Int
  akCapA : Int
  akRateB : Int
  akStartB : Int
  akCapB : Int
  akRateC : Int
  akStartC : Int
  akCapC : Int
  akRateD : Int
  akStartD : Int
  iackStart : Int
  iackRate : Int
  iackMax : Int
  okMax : Int
  okRate : Int
  okStart : Int
  aokAmount : Int
  kbQ1 : Nat → Int
  kbQ3 : Nat → Int
  kgbBase : Int → Int
  kgb12 : Int
  kgb16 : Int
  kgbAlo : Int
  kgbRate : Int
  kgbPartnerExtra : Int
  kgbDrempelMilli : Int
  kgbWealthSingle : Int
  kgbWealthPartners : Int
  /-- Box 3 (round 8): art. 2.13 rate, art. 5.2 lid 2 percentages (bp), art. 5.5 heffingvrij vermogen, art. 5.3 lid 3 f
  debt threshold; `box3Ok` false where the year's box-3 rules are not modelled (2022). -/
  box3Rate : Int := NLTax.box3Rate
  box3Bank : Int := NLTax.box3Bank
  box3Other : Int := NLTax.box3Other
  box3Debt : Int := NLTax.box3Debt
  hvv : Int := NLTax.hvv
  debtThreshold : Int := NLTax.debtThreshold
  box3Ok : Bool := true
  /-- Box 2 (art. 2.12) and the Zvw inkomensafhankelijke bijdrage (Regeling zorgverzekering art. 5.1 lid 2, 5.2-5.3),
  round 9. A flat box-2 rate is `box2B1 = 0`, `box2C2 = 0`, `box2R2` = the rate. -/
  box2B1 : Int := NLTax.box2B1
  box2C2 : Int := NLTax.box2C2
  box2R1 : Int := NLTax.box2R1
  box2R2 : Int := NLTax.box2R2
  zvwRate : Int := NLTax.zvwRate
  /-- 2022: the rendementsklassen regime of art. 5.2 (2022 wording) and the Wet rechtsherstel box 3, the lower. -/
  box3Klassen : Bool := false
  zvwMax : Int := NLTax.zvwMax

def kgbBase2025 (n : Int) : Int := n * kgbPerChild

def y2025 : YP :=
  { year := 2025, t210 := t210, t210a := t210a, grondslagRate := grondslagRate, ahkOnVi := true, ahkMax := ahkMax,
    ahkRate := ahkRate, ahkStart := ahkStart, akRateA := akRateA, akCapA := akCapA, akRateB := akRateB,
    akStartB := akStartB, akCapB := akCapB, akRateC := akRateC, akStartC := akStartC, akCapC := akCapC,
    akRateD := akRateD, akStartD := akStartD, iackStart := iackStart, iackRate := iackRate, iackMax := iackMax,
    okMax := okMax, okRate := okRate, okStart := okStart, aokAmount := aokAmount, kbQ1 := kbQ1, kbQ3 := kbQ3,
    kgbBase := kgbBase2025, kgb12 := kgb12, kgb16 := kgb16, kgbAlo := kgbAlo, kgbRate := kgbRate,
    kgbPartnerExtra := kgbPartnerExtra, kgbDrempelMilli := kgbDrempelMilli, kgbWealthSingle := kgbWealthSingle,
    kgbWealthPartners := kgbWealthPartners }

def kb2022Q1 (age : Nat) : Int := if age < 6 then 23069 else if age < 12 then 28013 else if age < 18 then 32956 else 0
def kb2022Q3 (age : Nat) : Int := if age < 6 then 24931 else if age < 12 then 30274 else if age < 18 then 35616 else 0
def kb2023Q1 (age : Nat) : Int := if age < 6 then 26976 else if age < 12 then 32756 else if age < 18 then 38537 else 0
def kb2023Q3 (age : Nat) : Int := if age < 6 then 26170 else if age < 12 then 31777 else if age < 18 then 37385 else 0
def kb2024Q1 (age : Nat) : Int := if age < 6 then 27949 else if age < 12 then 33938 else if age < 18 then 39927 else 0
def kb2024Q3 (age : Nat) : Int := if age < 6 then 28169 else if age < 12 then 34205 else if age < 18 then 40241 else 0

def kgbBase2022 (n : Int) : Int :=
  if n ≤ 0 then 0 else if n = 1 then eur 1220 else if n = 2 then eur 2326 else eur 3327 + (n - 3) * eur 1001
def kgbBase2023 (n : Int) : Int := if n ≤ 0 then 0 else eur 1653 + (n - 1) * eur 1532
def kgbBase2024 (n : Int) : Int := n * eur 2436

def y2024 : YP :=
  { year := 2024
    t210a := { b1 := 4002100, b2 := 7551800, c2 := 372900, c3 := 1685200, r1 := 932, r2 := 3697, r3 := 4950 }
    t210 := { b1 := 3809800, b2 := 7551800, c2 := 355000, c3 := 1738400, r1 := 932, r2 := 3697, r3 := 4950 }
    grondslagRate := 1253
    ahkOnVi := false
    ahkMax := eur 3362
    ahkRate := 6630
    ahkStart := eur 24812
    akRateA := 8425
    akCapA := eur 968
    akRateB := 31433
    akStartB := eur 11490
    akCapB := eur 5158
    akRateC := 2471
    akStartC := eur 24820
    akCapC := eur 5532
    akRateD := 6510
    akStartD := eur 39957
    iackStart := eur 6073
    iackRate := 11450
    iackMax := eur 2950
    okMax := eur 2010
    okRate := 15000
    okStart := eur 44770
    aokAmount := eur 524
    kbQ1 := kb2024Q1
    kbQ3 := kb2024Q3
    kgbBase := kgbBase2024
    kgb12 := eur 694
    kgb16 := eur 924
    kgbAlo := eur 3480
    kgbRate := 6750
    kgbPartnerExtra := eur 9030
    kgbDrempelMilli := 108 * 12 * 206940 / 10
    kgbWealthSingle := eur 140213
    kgbWealthPartners := eur 177301
    box3Rate := 3600
    box3Bank := 144
    box3Other := 604
    box3Debt := 261
    hvv := eur 57000
    debtThreshold := eur 3700
    box2B1 := 6700000
    box2C2 := 1641500
    box2R1 := 2450
    box2R2 := 3300
    zvwRate := 532
    zvwMax := eur 71628 }

def y2023 : YP :=
  { year := 2023
    t210a := { b1 := 3870300, b2 := 7303100, c2 := 359100, c3 := 1626800, r1 := 928, r2 := 3693, r3 := 4950 }
    t210 := { b1 := 3714900, b2 := 7303100, c2 := 344700, c3 := 1669800, r1 := 928, r2 := 3693, r3 := 4950 }
    grondslagRate := 1257
    ahkOnVi := false
    ahkMax := eur 3070
    ahkRate := 6095
    ahkStart := eur 22660
    akRateA := 8231
    akCapA := eur 884
    akRateB := 29861
    akStartB := eur 10740
    akCapB := eur 4605
    akRateC := 3085
    akStartC := eur 23201
    akCapC := eur 5052
    akRateD := 6510
    akStartD := eur 37691
    iackStart := eur 5547
    iackRate := 11450
    iackMax := eur 2694
    okMax := eur 1835
    okRate := 15000
    okStart := eur 40888
    aokAmount := eur 478
    kbQ1 := kb2023Q1
    kbQ3 := kb2023Q3
    kgbBase := kgbBase2023
    kgb12 := eur 267
    kgb16 := eur 476
    kgbAlo := eur 3848
    kgbRate := 6750
    kgbPartnerExtra := eur 18327
    kgbDrempelMilli := 108 * 12 * 193440 / 10
    kgbWealthSingle := eur 127582
    kgbWealthPartners := eur 161329
    box3Rate := 3200
    box3Bank := 92
    box3Other := 617
    box3Debt := 246
    hvv := eur 57000
    debtThreshold := eur 3400
    box2B1 := 0
    box2C2 := 0
    box2R1 := 2690
    box2R2 := 2690
    zvwRate := 543
    zvwMax := eur 66956 }

def y2022 : YP :=
  { year := 2022
    t210a := { b1 := 3640900, b2 := 6939800, c2 := 342900, c3 := 1565800, r1 := 942, r2 := 3707, r3 := 4950 }
    t210 := { b1 := 3547200, b2 := 6939800, c2 := 334100, c3 := 1591700, r1 := 942, r2 := 3707, r3 := 4950 }
    grondslagRate := 950
    ahkOnVi := false
    ahkMax := eur 2888
    ahkRate := 6007
    ahkStart := eur 21317
    akRateA := 4541
    akCapA := eur 470
    akRateB := 28461
    akStartB := eur 10350
    akCapB := eur 3887
    akRateC := 2610
    akStartC := eur 22356
    akCapC := eur 4260
    akRateD := 5860
    akStartD := eur 36649
    iackStart := eur 5219
    iackRate := 11450
    iackMax := eur 2534
    okMax := eur 1726
    okRate := 15000
    okStart := eur 38464
    aokAmount := eur 449
    kbQ1 := kb2022Q1
    kbQ3 := kb2022Q3
    kgbBase := kgbBase2022
    kgb12 := eur 251
    kgb16 := eur 447
    kgbAlo := eur 3285
    kgbRate := 6750
    kgbPartnerExtra := eur 17240
    kgbDrempelMilli := 108 * 12 * 172500 / 10
    kgbWealthSingle := eur 120020
    kgbWealthPartners := eur 151767
    box3Klassen := true
    box3Rate := 3100
    box3Bank := 0
    box3Other := 553
    box3Debt := 228
    hvv := eur 50650
    debtThreshold := eur 3200
    box2B1 := 0
    box2C2 := 0
    box2R1 := 2690
    box2R2 := 2690
    zvwRate := 550
    zvwMax := eur 59706 }

def ypFor (yr : Nat) : YP :=
  if yr = 2022 then y2022 else if yr = 2023 then y2023 else if yr = 2024 then y2024 else y2025
def yearSupported (yr : Nat) : Bool := 2022 ≤ yr && yr ≤ 2025

-- the tables' kolom III are the rounded cumulative band sums (as in 2025)
#guard y2024.t210.c2 = 3809800 * 932 / 10000 / 100 * 100
#guard y2023.t210.c2 = 3714900 * 928 / 10000 / 100 * 100
#guard y2022.t210.c2 = 3547200 * 942 / 10000 / 100 * 100
#guard y2024.t210a.c2 = 4002100 * 932 / 10000 / 100 * 100
#guard y2023.t210a.c2 = 3870300 * 928 / 10000 / 100 * 100
#guard y2022.t210a.c2 = 3640900 * 942 / 10000 / 100 * 100

end NLTax
