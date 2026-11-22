import TaxKernel

/-!
# The numbers for the 2025 taxation year (Canada federal + Ontario)

Money in **cents** (`Int`): the return (T1, ON428) and CRA's payroll formulas compute to the cent, and the
statutes do not round the tax (only the indexation of each dollar amount is rounded to the dollar: ITA s. 117.1(3),
Taxation Act, 2007 (Ontario) s. 23(4)). Rates in basis points. Each number cites the provision that fixes it and,
for an indexed amount, the official publication of its 2025 value.

Sources (saved under `cmp20/anglo/ca/refs/`):
* ITA = Income Tax Act, R.S.C. 1985, c. 1 (5th Supp.), consolidated XML (Justice Canada,
  github.com/justicecanada/laws-lois-xml, commit 959c7473 = in force 2025-06-27, commit a782c13d = 2026-06-18), read
  through Global law (canada/federal/acts/I-3.3).
* C-4 = Making Life More Affordable for Canadians Act, S.C. 2026, c. 2 (assented 2026-03-12), s. 2:
  s. 117(2)(a) "14.5%" for 2025 (s. 2(3)), "14%" from 2026 (s. 2(2), (4)).
* OTA = Taxation Act, 2007 (Ontario), S.O. 2007, c. 11, Sched. A (e-Laws, canada/ontario/acts/07t11), as in force
  2025-07-01.
* T4127 = CRA, Payroll Deductions Formulas, 120th ed., effective 1 January 2025 (t4127-01-25e.pdf), ch. 8.
* TD1-2025, TD1ON-2025, ON428-2025 (5006-C), T4114 (July 2025 to June 2026): CRA forms and booklet.
* IDX = CRA, "Indexation adjustment for personal income tax and benefit amounts" (canada.ca, page of 2026-03-12),
  2025 column.
-/

namespace CaTax
open TaxKernel

/-- Dollars to cents. -/
def dol (x : Int) : Int := 100 * x

/-! ## Federal (ITA Part I, Division E) -/

/-- ITA s. 117(2) as replaced by C-4 s. 2(1) for 2025 (s. 2(3)): 14.5 % up to $57,375, 20.5 % to $114,750, 26 % to
$177,882, 29 % to $253,414, 33 % above. The dollar amounts are already the 2025 indexed amounts (T4127 Table 8.1;
IDX). -/
def fedSchedule : Schedule :=
  Schedule.ofList [(0, 1450), (dol 57375, 2050), (dol 114750, 2600), (dol 177882, 2900), (dol 253414, 3300)]

/-- ITA s. 248(1) "appropriate percentage": the lowest rate of s. 117(2), 14.5 % for 2025 (C-4 s. 2(3)). -/
def appropriatePct : Int := 1450

/-- ITA s. 118(1.1) basic personal amount: A = $12,298 indexed = $14,538 (2025, IDX); F = $15,000 indexed = $16,129
(2025: TD1-2025 line 1, T4127 BPAF formula); the enhancement C = F − A = $1,591 is withdrawn linearly between the
first dollar amounts of s. 117(2)(d) and (e) ($177,882 and $253,414). -/
def bpaMin : Int := dol 14538
def bpaMax : Int := dol 16129
def bpaTaperStart : Int := dol 177882
def bpaTaperEnd : Int := dol 253414

/-- ITA s. 118(10) Canada employment amount: "$1,000" indexed (s. 117.1(2)(i)) = $1,471 (T4127 Table 8.2 "CEA"). -/
def ceaMax : Int := dol 1471

/-- ITA s. 118(2) age amount: $6,408 indexed = $9,028; threshold $25,921 indexed = $45,522 (TD1-2025 line 3); "15%
of the amount ... by which the individual's income ... would exceed" the threshold. -/
def ageAmount : Int := dol 9028
def ageThreshold : Int := dol 45522
def ageTaperRate : Int := 1500

/-- ITA s. 118(3) pension credit: "the lesser of (a) $2,000" (not indexed: not listed in s. 117.1(2)). -/
def pensionAmountMax : Int := dol 2000

/-- ITA s. 118.1(3): "$200" at the appropriate percentage; 33 % ("highest individual percentage") on gifts out of
income taxed at 33 %; 29 % on the rest. -/
def giftLowTier : Int := dol 200
def giftTopRate : Int := 3300
def giftMidRate : Int := 2900

/-- ITA s. 82(1)(b)(ii): eligible dividends grossed up by 38 % (years after 2011). -/
def eligibleGrossUp : Int := 3800
/-- ITA s. 121(b)(iv): dividend tax credit 6/11 of the gross-up (years after 2011). -/
def fedDtcNum : Int := 6
def fedDtcDen : Int := 11

/-- ITA s. 38(a): a taxable capital gain is "½ of the taxpayer's capital gain". -/
def cgInclusionNum : Int := 1
def cgInclusionDen : Int := 2

/-- ITA s. 146(1) "RRSP dollar limit" for 2025 = money purchase limit for 2024 ($32,490; s. 147.1(1)); s. 146(1)
"RRSP deduction limit": 18 % of earned income. -/
def rrspDollarLimit : Int := dol 32490
def rrspPct : Int := 1800

/-! ### Canada workers benefit, ITA s. 122.7 (2025 values: IDX) -/
/-- s. 122.7(2) A: "27% of the amount ... by which the individual's working income ... exceeds $3,000" (not
indexed), capped at $1,395 (single) / $2,403 (family) indexed = $1,633 / $2,813. -/
def cwbInRate : Int := 2700
def cwbWorkThreshold : Int := dol 3000
def cwbMaxSingle : Int := dol 1633
def cwbMaxFamily : Int := dol 2813
/-- s. 122.7(2) B: "15% of the amount ... by which the adjusted net income ... exceeds $22,944" (single) / "$26,177"
(family), indexed = $26,855 / $30,639. -/
def cwbOutRate : Int := 1500
def cwbOutSingle : Int := dol 26855
def cwbOutFamily : Int := dol 30639
/-- s. 122.7(1.3) secondary earner exemption: "$14,000" indexed = $16,386. -/
def cwbSecondaryExemption : Int := dol 16386

/-! ## Benefits paid July 2025 to June 2026 (base year 2024) -/

/-- ITA s. 122.61(1) E and Q, base year 2024 values (T4114 2025-26 p. 15; IDX "2025" column): $7,997 per child under
6, $6,748 aged 6 to 17; reduction 7 / 13.5 / 19 / 23 % of AFNI over $37,487 up to $81,222; above it $3,061 / $5,904 /
$8,310 / $10,059 plus 3.2 / 5.7 / 8 / 9.5 %. -/
def ccbUnder6 : Int := dol 7997
def ccb6to17 : Int := dol 6748
def ccbT1 : Int := dol 37487
def ccbT2 : Int := dol 81222
def ccbRate1 (n : Nat) : Int := if n = 0 then 0 else if n = 1 then 700 else if n = 2 then 1350 else if n = 3 then 1900 else 2300
def ccbRate2 (n : Nat) : Int := if n = 0 then 0 else if n = 1 then 320 else if n = 2 then 570 else if n = 3 then 800 else 950
def ccbFixed2 (n : Nat) : Int :=
  if n = 0 then 0 else if n = 1 then dol 3061 else if n = 2 then dol 5904 else if n = 3 then dol 8310 else dol 10059

/-- ITA s. 122.5(3), 2025-26 values (IDX "Canada Groceries and Essentials Benefit (formerly GST/HST credit)", 2025):
$349 per adult (and for an eligible dependant in place of a spouse), $184 per child, single supplement $184
(for a single person phased in at 2 % over $11,337); reduced by 5 % of adjusted income over $45,521. Annual
amounts (paid quarterly, ¼ each). -/
def gstAdult : Int := dol 349
def gstChild : Int := dol 184
def gstSingleSupp : Int := dol 184
def gstSuppPhaseIn : Int := dol 11337
def gstSuppRate : Int := 200
def gstThreshold : Int := dol 45521
def gstOutRate : Int := 500

/-- OTA s. 104(5): "[(A × B) − C]/12", A = $1,310 (indexed under s. 23(1) para. 7.3) = $143.91 a month for July 2025
to June 2026 (T4114 2025-26 "Ontario child benefit"), C = "8 per cent of the amount ... by which the individual's
adjusted income ... exceeds $20,000" indexed = $26,364 (T4114). -/
def ocbPerChildMonthly : Int := 14391
def ocbThreshold : Int := dol 26364
def ocbRate : Int := 800

/-- OTA s. 104.11 Ontario sales tax credit, July 2025 to June 2026 (base year 2024; CRA "Ontario" benefits page):
$371 per adult and per child; reduced by 4 % of adjusted net income over $28,506 (single, no children) or of
adjusted family net income over $35,632 (others). -/
def ostcPerPerson : Int := dol 371
def ostcThresholdSingle : Int := dol 28506
def ostcThresholdFamily : Int := dol 35632
def ostcRate : Int := 400

/-! ## Ontario (Taxation Act, 2007) -/

/-- OTA s. 6(1) with s. 3(1) rates (5.05 / 9.15 / 11.16 / 12.16 / 13.16 %) and thresholds indexed by s. 23(1)
para. 1, 1.1 ($40,120 → $52,886; $80,242 → $105,775), $150,000 and $220,000 not indexed (ON428-2025 Part A; T4127
Table 8.1 ON). -/
def onSchedule : Schedule :=
  Schedule.ofList [(0, 505), (dol 52886, 915), (dol 105775, 1116), (dol 150000, 1216), (dol 220000, 1316)]
/-- OTA s. 3(1) "lowest tax rate" 5.05 % (years after 2009). -/
def onLowRate : Int := 505
/-- OTA s. 9(2): "$8,881" indexed = $12,747 (ON428-2025 line 9; TD1ON-2025). -/
def onBpa : Int := dol 12747
/-- OTA s. 9(3): "A × [$7,541 – (B – $754)]" indexed = $10,823 and $1,082 (ON428-2025 lines 11-13: base $11,905,
maximum $10,823; TD1ON-2025 line 5). -/
def onSpouseMax : Int := dol 10823
def onSpouseFloor : Int := dol 1082
/-- OTA s. 9(8): "A × ($4,336 – H)", H = 15 % over "$32,280", indexed = $6,223 / $46,330 (TD1ON-2025 line 2). -/
def onAgeAmount : Int := dol 6223
def onAgeThreshold : Int := dol 46330
/-- OTA s. 9(10): "the lesser of $1,228" indexed = $1,762 (ON428-2025 line 27). -/
def onPensionMax : Int := dol 1762
/-- ON428-2025 lines 47-48: gifts at 5.05 % on the first $200 and 11.16 % above (OTA s. 9(21)). -/
def onGiftHighRate : Int := 1116
/-- OTA s. 19.1(b): "36.3158 per cent" of the s. 82(1)(b)(ii) gross-up (eligible dividends); in millionths. -/
def onDtcPpm : Int := 363158
/-- OTA s. 16(1): 20 % of gross tax over $4,006 and 36 % over $5,127, indexed by s. 23(1) para. 4 = $5,710 and
$7,307 (ON428-2025 lines 66-67; T4127 Table 8.2). -/
def onSurtaxT1 : Int := dol 5710
def onSurtaxT2 : Int := dol 7307
def onSurtaxR1 : Int := 2000
def onSurtaxR2 : Int := 3600
/-- OTA s. 20(4), (5): basic reduction $205 and $379 per dependant, indexed by s. 23(1) para. 5 = $294 and $544
(ON428-2025 lines 74-76; T4127 Table 8.2 S2 and Factor S). -/
def onReductionBasic : Int := dol 294
def onReductionPerDependant : Int := dol 544
/-- OTA s. 21.1(3.1) LIFT credit (2022 and later; not indexed): D = lesser of $875 and lowest rate × employment
income; E = 5 % of the greater of personal adjusted income over $32,500 and family adjusted income over $65,000. -/
def liftMax : Int := dol 875
def liftRate : Int := 500
def liftPersonal : Int := dol 32500
def liftFamily : Int := dol 65000

/-- OTA s. 24(2), Ontario Health Premium on combined income (taxable income + split income), not indexed:
six steps, 6 % / 25 % phase-ins to $300 / $450 / $600 / $750 / $900. -/
def ohp (x : Int) : Int :=
  let r6 (a cap : Int) : Int := divR .halfUp (600 * min cap (pos a)) BP
  let r25 (a cap : Int) : Int := divR .halfUp (2500 * min cap (pos a)) BP
  if x ≤ dol 20000 then 0
  else if x ≤ dol 36000 then r6 (x - dol 20000) (dol 5000)
  else if x ≤ dol 48000 then dol 300 + r6 (x - dol 36000) (dol 2500)
  else if x ≤ dol 72000 then dol 450 + r25 (x - dol 48000) (dol 600)
  else if x ≤ dol 200000 then dol 600 + r25 (x - dol 72000) (dol 600)
  else dol 750 + r25 (x - dol 200000) (dol 600)

/-! ## Canada Pension Plan and Employment Insurance, 2025 (T4127 Tables 8.3 to 8.7) -/

/-- CPP Act ss. 8(1), 11.1 and 19: base employee rate 4.95 %, first additional 1.00 % (total 5.95 %) on pensionable
earnings between the basic exemption $3,500 and the YMPE $71,300 (T4127 Tables 8.3-8.5). -/
def cppBaseRate : Int := 495
def cppFirstAddRate : Int := 100
def cppYbe : Int := dol 3500
def cppYmpe : Int := dol 71300
/-- CPP Act s. 8(1.2): second additional contribution 4 % between the YMPE and the YAMPE $81,200 (T4127 Table 8.6). -/
def cpp2Rate : Int := 400
def cppYampe : Int := dol 81200
/-- EI Act s. 67 with the 2025 rate fixed under s. 66: 1.64 % of insurable earnings up to $65,700 (T4127 Table 8.7,
ch. 7). -/
def eiRate : Int := 164
def eiMie : Int := dol 65700

/-! ## Tax years 2022, 2023 and 2024 (round 6 of the 38-model tests)

`YP` holds every amount that differs between 2022 and 2025; `y2025` is the constants above. Sources:
* **Indexed amounts** (ITA s. 117.1(1); s. 122.61(5) for the CCB, s. 122.5(5) for the GST/HST credit, s. 122.7 for
  the CWB; Taxation Act, 2007 (Ontario) s. 23): derived from each provision's statutory base amount and Statistics
  Canada's CPI (table 18-10-0004-01, v41690973 Canada and v41691919 Ontario; 12 months to 30 September, factor
  rounded half up to 1/1000, amounts carried unrounded and rounded to the dollar), `cmp20/improve-anglo/r5/
  ca_derive.py` and its output; **every chain reproduces the 2025 value cited above** (round-5 log, section 4).
  Factors 2022 / 2023 / 2024: federal 2.4 / 6.3 / 4.7 %, Ontario 2.4 / 6.5 / 4.5 %. Benefit amounts are the July
  amounts of the benefit year that starts in the household's year (as for 2025: July 2025 - June 2026).
* **Statutory amounts**: lowest federal rate 15 % for 2022-2024 (s. 117(2)(a) before S.C. 2026, c. 2); s. 118(1.1)
  F "(c) for the 2022 taxation year, $14,398, and (d) for the 2023 and subsequent taxation years, $15,000" (2024
  indexed by s. 117.1(2)(g)); CPP first additional rate 0.75 % (2022) and 1 % (2023-2024), CPP2 from 2024 (CPP Act
  ss. 8, 11.1, 18.1).
* **CPP and EI figures**: CRA, "CPP contribution rates, maximums and exemptions" (canada.ca, page dated 2026-11-09):
  YMPE $64,900 / $66,600 / $68,500 (2025 $71,300 = `cppYmpe`), rate 5.70 % / 5.95 % / 5.95 %; CRA, "Second additional
  CPP contribution rates and maximums": AYMPE 2024 $73,200 (2025 $81,200 = `cppYampe`), 4 %; CRA, "EI premium rates
  and maximums" (page dated 2025-09-16): maximum insurable earnings $60,300 / $61,500 / $63,200 (2025 $65,700 =
  `eiMie`), rates 1.58 / 1.63 / 1.66 % (2025 1.64 % = `eiRate`). The EI rates are also those of the Canada Gazette
  Part I notices of 2 Oct 2021, 8 Oct 2022 and 7 Oct 2023 (EI Act s. 66.5); each YMPE and maximum is one of the two
  values the statutory chains (CPP Act s. 18, EI Act s. 4) allow from Statistics Canada's earnings data (round 6).
  (Values supplied verbatim by the test coordinator from the live CRA pages.)
* GST/HST credit phase-in and reduction threshold: s. 122.5(3)(f) "$6,911" and B "$27,749", chained from 2003 (round
  7): $9,919 / $10,544 / $11,039 and $39,826 / $42,335 / $44,324, reproducing 2025's $11,337 / $45,521.
* **Not derived** (flagged in `unsupported` for 2022-2024): the RRSP dollar limit (2025's $32,490 kept).
-/

structure YP where
  year : Nat
  fedSchedule : Schedule
  lowRate : Int
  topThreshold : Int
  bpaMin : Int
  bpaMax : Int
  bpaTaperStart : Int
  bpaTaperEnd : Int
  ceaMax : Int
  ageAmount : Int
  ageThreshold : Int
  cwbMaxSingle : Int
  cwbMaxFamily : Int
  cwbOutSingle : Int
  cwbOutFamily : Int
  cwbSecondaryExemption : Int
  ccbUnder6 : Int
  ccb6to17 : Int
  ccbT1 : Int
  ccbT2 : Int
  ccbFixed2 : Nat → Int
  gstAdult : Int
  gstChild : Int
  gstSingleSupp : Int
  gstSuppPhaseIn : Int
  gstThreshold : Int
  ocbPerChildMonthly : Int
  ocbThreshold : Int
  ostcPerPerson : Int
  ostcThresholdSingle : Int
  ostcThresholdFamily : Int
  onSchedule : Schedule
  onBpa : Int
  onSpouseMax : Int
  onSpouseFloor : Int
  onAgeAmount : Int
  onAgeThreshold : Int
  onPensionMax : Int
  onSurtaxT1 : Int
  onSurtaxT2 : Int
  onReductionBasic : Int
  onReductionPerDependant : Int
  cppFirstAddRate : Int
  cppYmpe : Int
  cppYampe : Int
  cpp2Rate : Int
  eiRate : Int
  eiMie : Int
  /-- ITA s. 122.5(3.004), (4.4) (S.C. 2026): the one-time top-up deemed paid in January 2026 for the 2024 taxation
  year; on only in the benefit set for base taxation year 2024 (round 8). -/
  gstTopUp : Bool := false

def y2025 : YP :=
  { year := 2025, fedSchedule, lowRate := appropriatePct, topThreshold := dol 253414, bpaMin, bpaMax,
    bpaTaperStart, bpaTaperEnd, ceaMax, ageAmount, ageThreshold, cwbMaxSingle, cwbMaxFamily, cwbOutSingle,
    cwbOutFamily, cwbSecondaryExemption, ccbUnder6, ccb6to17, ccbT1, ccbT2, ccbFixed2, gstAdult, gstChild,
    gstSingleSupp, gstSuppPhaseIn, gstThreshold, ocbPerChildMonthly, ocbThreshold, ostcPerPerson,
    ostcThresholdSingle, ostcThresholdFamily, onSchedule, onBpa, onSpouseMax, onSpouseFloor, onAgeAmount,
    onAgeThreshold, onPensionMax, onSurtaxT1, onSurtaxT2, onReductionBasic, onReductionPerDependant,
    cppFirstAddRate, cppYmpe, cppYampe, cpp2Rate, eiRate, eiMie }

/-- A year's federal schedule: 15 % / 20.5 % / 26 % / 29 % / 33 % on the year's indexed thresholds. -/
def fedSched15 (a b c d : Int) : Schedule :=
  Schedule.ofList [(0, 1500), (dol a, 2050), (dol b, 2600), (dol c, 2900), (dol d, 3300)]

def onSched (a b : Int) : Schedule :=
  Schedule.ofList [(0, 505), (dol a, 915), (dol b, 1116), (dol 150000, 1216), (dol 220000, 1316)]

def ccbFixedOf (a b c d : Int) (n : Nat) : Int :=
  if n = 0 then 0 else if n = 1 then dol a else if n = 2 then dol b else if n = 3 then dol c else dol d

def y2024 : YP :=
  { y2025 with
    year := 2024
    fedSchedule := fedSched15 55867 111733 173205 246752
    lowRate := 1500
    topThreshold := dol 246752
    bpaMin := dol 14156
    bpaMax := dol 15705
    bpaTaperStart := dol 173205
    bpaTaperEnd := dol 246752
    ceaMax := dol 1433
    ageAmount := dol 8790
    ageThreshold := dol 44325
    cwbMaxSingle := dol 1590
    cwbMaxFamily := dol 2739
    cwbOutSingle := dol 26149
    cwbOutFamily := dol 29833
    cwbSecondaryExemption := dol 15955
    ccbUnder6 := dol 7787
    ccb6to17 := dol 6570
    ccbT1 := dol 36502
    ccbT2 := dol 79087
    ccbFixed2 := ccbFixedOf 2981 5749 8091 9795
    gstAdult := dol 340
    gstChild := dol 179
    gstSingleSupp := dol 179
    gstSuppPhaseIn := dol 11039
    gstThreshold := dol 44324
    ocbPerChildMonthly := 14000
    ocbThreshold := dol 25646
    ostcPerPerson := dol 360
    ostcThresholdSingle := dol 27729
    ostcThresholdFamily := dol 34661
    onSchedule := onSched 51446 102894
    onBpa := dol 12399
    onSpouseMax := dol 10528
    onSpouseFloor := dol 1053
    onAgeAmount := dol 6054
    onAgeThreshold := dol 45068
    onPensionMax := dol 1714
    onSurtaxT1 := dol 5554
    onSurtaxT2 := dol 7108
    onReductionBasic := dol 286
    onReductionPerDependant := dol 529
    cppFirstAddRate := 100
    cppYmpe := dol 68500
    cppYampe := dol 73200
    cpp2Rate := 400
    eiRate := 166
    eiMie := dol 63200 }

def y2023 : YP :=
  { y2024 with
    year := 2023
    fedSchedule := fedSched15 53359 106717 165430 235675
    topThreshold := dol 235675
    bpaMin := dol 13520
    bpaMax := dol 15000
    bpaTaperStart := dol 165430
    bpaTaperEnd := dol 235675
    ceaMax := dol 1368
    ageAmount := dol 8396
    ageThreshold := dol 42335
    cwbMaxSingle := dol 1518
    cwbMaxFamily := dol 2616
    cwbOutSingle := dol 24975
    cwbOutFamily := dol 28494
    cwbSecondaryExemption := dol 15239
    ccbUnder6 := dol 7437
    ccb6to17 := dol 6275
    ccbT1 := dol 34863
    ccbT2 := dol 75537
    ccbFixed2 := ccbFixedOf 2847 5491 7728 9355
    gstAdult := dol 325
    gstChild := dol 171
    gstSingleSupp := dol 171
    gstSuppPhaseIn := dol 10544
    gstThreshold := dol 42335
    ocbPerChildMonthly := 13392
    ocbThreshold := dol 24542
    ostcPerPerson := dol 345
    ostcThresholdSingle := dol 26535
    ostcThresholdFamily := dol 33169
    onSchedule := onSched 49231 98463
    onBpa := dol 11865
    onSpouseMax := dol 10075
    onSpouseFloor := dol 1007
    onAgeAmount := dol 5793
    onAgeThreshold := dol 43127
    onPensionMax := dol 1641
    onSurtaxT1 := dol 5315
    onSurtaxT2 := dol 6802
    onReductionBasic := dol 274
    onReductionPerDependant := dol 506
    cppYmpe := dol 66600
    cppYampe := dol 66600
    cpp2Rate := 0
    eiRate := 163
    eiMie := dol 61500 }

def y2022 : YP :=
  { y2023 with
    year := 2022
    fedSchedule := fedSched15 50197 100392 155625 221708
    topThreshold := dol 221708
    bpaMin := dol 12719
    bpaMax := dol 14398
    bpaTaperStart := dol 155625
    bpaTaperEnd := dol 221708
    ceaMax := dol 1287
    ageAmount := dol 7898
    ageThreshold := dol 39826
    cwbMaxSingle := dol 1428
    cwbMaxFamily := dol 2461
    cwbOutSingle := dol 23495
    cwbOutFamily := dol 26805
    cwbSecondaryExemption := dol 14336
    ccbUnder6 := dol 6997
    ccb6to17 := dol 5903
    ccbT1 := dol 32797
    ccbT2 := dol 71060
    ccbFixed2 := ccbFixedOf 2678 5166 7270 8801
    gstAdult := dol 306
    gstChild := dol 161
    gstSingleSupp := dol 161
    gstSuppPhaseIn := dol 9919
    gstThreshold := dol 39826
    ocbPerChildMonthly := 12575
    ocbThreshold := dol 23044
    ostcPerPerson := dol 324
    ostcThresholdSingle := dol 24916
    ostcThresholdFamily := dol 31144
    onSchedule := onSched 46226 92454
    onBpa := dol 11141
    onSpouseMax := dol 9460
    onSpouseFloor := dol 946
    onAgeAmount := dol 5440
    onAgeThreshold := dol 40495
    onPensionMax := dol 1541
    onSurtaxT1 := dol 4991
    onSurtaxT2 := dol 6387
    onReductionBasic := dol 257
    onReductionPerDependant := dol 475
    cppFirstAddRate := 75
    cppYmpe := dol 64900
    cppYampe := dol 64900
    eiRate := 158
    eiMie := dol 60300 }

/-- **Benefit year for base taxation year 2025** (July 2026 to June 2027; round 7): only the benefit amounts differ
from `y2025`. ITA s. 122.6 "base taxation year" (months July-December of a year: the preceding taxation year);
s. 122.61(5) and s. 122.5(4)-(5) (the months specified for a taxation year are July and October of the next year and
January and April of the year after); OTA ss. 104, 104.11 likewise. Amounts: the round-5 chains carried one more year
with the 2026 factors (federal 2.0 %, Ontario 1.9 %, Statistics Canada CPI to September 2025): CCB $8,157 / $6,883,
thresholds $38,237 / $82,847, fixed reductions $3,123 / $6,022 / $8,476 / $10,260; GST/HST credit: for the months
July 2026 to April 2031 s. 122.5(4.6) makes the s. 122.5(3) amount nil and s. 122.5(3.005) applies instead ($445 /
$445 / $234 a dependant / $234 single-parent supplement, the single supplement phased in at 2 % over $11,564, reduced by
5 % over $46,432; S.C. 2026, consolidation of 2026-06-18; round 8), the phase-in and threshold being exactly the
chained s. 122.5(3) amounts (base $6,911 / $27,749, 2026 factor), a check on the chain; OCB $1,760 a child ($146.67 a month),
threshold $26,865; OSTC $378, thresholds $29,047 / $36,309. -/
def y2026Benefits : YP :=
  { y2025 with
    year := 2026
    ccbUnder6 := dol 8157
    ccb6to17 := dol 6883
    ccbT1 := dol 38237
    ccbT2 := dol 82847
    ccbFixed2 := ccbFixedOf 3123 6022 8476 10260
    gstAdult := dol 445
    gstChild := dol 234
    gstSingleSupp := dol 234
    gstSuppPhaseIn := dol 11564
    gstThreshold := dol 46432
    ocbPerChildMonthly := 14667
    ocbThreshold := dol 26865
    ostcPerPerson := dol 378
    ostcThresholdSingle := dol 29047
    ostcThresholdFamily := dol 36309 }

/-- The benefit amounts that go with the household's income year `year` taken as the **base taxation year**: those
of the benefit year July `year + 1` to June `year + 2` (ITA s. 122.6 "base taxation year"; round 7). -/
def benefitParams (year : Nat) : YP :=
  if year ≤ 2021 then y2022 else if year = 2022 then y2023 else if year = 2023 then y2024
  else if year = 2024 then { y2025 with gstTopUp := true } else y2026Benefits

/-- The year's parameters (2022-2025; later years use 2025, earlier 2022, and the output says so). -/
def ypFor (year : Nat) : YP :=
  if year ≤ 2022 then y2022 else if year = 2023 then y2023 else if year = 2024 then y2024 else y2025

-- CRA's maximum employee contributions follow from the parameters (base + first additional on YMPE − $3,500):
-- 2022 $3,499.80, 2023 $3,754.45, 2024 $3,867.50 (+ CPP2 $188), EI $952.74 / $1,002.45 / $1,049.12
#guard [y2022, y2023, y2024].map (fun y => (495 + y.cppFirstAddRate) * (y.cppYmpe - dol 3500) / 10000) = [349980, 375445, 386750]
#guard y2024.cpp2Rate * (y2024.cppYampe - y2024.cppYmpe) / 10000 = dol 188
#guard [y2022, y2023, y2024].map (fun y => y.eiRate * y.eiMie / 10000) = [95274, 100245, 104912]

end CaTax
