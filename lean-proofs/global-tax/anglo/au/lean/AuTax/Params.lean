import AuTax.Basic

/-!
# The numbers for the income years 2024-25 and 2025-26

Every amount is copied from the provision that fixes it (text as in force for the year; Global law record
`australia/federal/acts`, official text on legislation.gov.au), or, where the statute holds only an indexed base
amount, from the agency page that publishes the indexed figure (archived official page, URL in `refs/SOURCES.md`).
Money in whole dollars unless the name ends in `C` (cents); rates in basis points.

| Number | Provision | Set by |
|---|---|---|
| resident rates 16 / 30 / 37 / 45 %, thresholds 45,000 / 135,000 / 190,000 | Income Tax Rates Act 1986 (ITRA) Sch 7 Pt I cl 1 table "2024-25 year of income or a later" (from 2025-03-28: "2024-25 or 2025-26") | Treasury Laws Amendment (Cost of Living Tax Cuts) Act 2024 |
| tax-free threshold $18,200 | ITRA s. 3(1) "tax-free threshold" | - |
| LITO $700; -5 % over $37,500; $325 -1.5 % over $45,000; nil above $66,667 | ITAA 1997 s. 61-110(1)(b), 61-115(1) | 2020-21 onwards |
| Medicare levy 2 % | Medicare Levy Act 1986 (MLA) s. 6(1) | - |
| low-income threshold 27,222 / phase-in limit 34,027 (2024-25); 28,011 / 35,013 (2025-26) | MLA s. 3(1) "threshold amount", "phase-in limit" (c) | TLA (More Cost of Living Relief) Act 2025 (No. 28) / TLA (Delivering an Efficient and Trusted Tax System) Act 2026 (No. 58) |
| shade-in 10 % of the excess | MLA s. 7(2) | - |
| family income threshold 45,907 + 4,216 per child (2024-25); 47,238 + 4,338 (2025-26) | MLA s. 8(5) | same Acts |
| family reduction 2 % x FIT - 0.08 x (FI - FIT) | MLA s. 8(2) (formula, official epub alt text) | - |
| MLS 1 / 1.25 / 1.5 % | MLA ss. 8B(2)-(4), 8C, 8D(3), (4A), (4B) | - |
| MLS singles tiers 97,000 / 113,000 / 151,000 (2024-25); 101,000 / 118,000 / 158,000 (2025-26); family x2, +1,500 per child after the first | PHI Act 2007 ss. 22-35, 22-40, 22-45 (indexed) | ATO "Medicare levy surcharge income, thresholds and rates" (archived) |
| MLS married own-income floor 27,222 (2024-25) / 28,011 (2025-26) | MLA s. 8D(3)(c) | same Acts |
| franking gross-up and offset (corporate rate 30 %) | ITAA 1997 ss. 207-20(1)-(2), 67-25 (refundable) | - |
| CGT discount 50 % | ITAA 1997 ss. 115-25, 115-100(a) | - |
| concessional contributions cap 30,000; contributions tax 15 %; Div 293 threshold 250,000, 15 % | ITAA 1997 ss. 291-20, 295-160 / ITRA s. 26; Div 293 (s. 293-20) | ATO Div 293 page (archived) |
| FTB rates (indexed) | FA Act 1999 Sch 1 cll 7, 8, 25-28, 29-33, 38A, 38L-38N (base amounts), Sch 4 (indexation) | DSS Family Assistance Guide 3.6.1, 3.6.3 (archived) |
| HELP 2024-25 bands; 2025-26 marginal 15 % / 17 % / 10 % of total | HESA 2003 ss. 154-5, 154-10, 154-20 | ATO "Study and training loan repayment thresholds and rates" (archived) |
-/

namespace AuTax

structure Params where
  label : String
  /-- ITRA s. 3(1): the tax-free threshold, $18,200. -/
  taxFree : Int
  /-- ITRA Sch 7 Pt I cl 1, table: thresholds above the tax-free threshold and the rates. -/
  brackets : List (Int × Int)
  /-- ITAA 1997 s. 61-115(1): $700; less 5 % of the excess over $37,500; $325 less 1.5 % of the excess over
  $45,000; s. 61-110(1)(b): nil if taxable income exceeds $66,667. -/
  litoMax : Int
  litoT1 : Int
  litoR1 : Int
  litoMid : Int
  litoT2 : Int
  litoR2 : Int
  litoCeiling : Int
  /-- ITAA 1997 s. 61-107 low and middle income tax offset: in force for 2018-19 to 2021-22 only (ATO, "LMITO ended
  on 30 June 2022"). Only the 2021-22 parameter set turns it on. -/
  lmito : Bool := false
  /-- MLA s. 6(1): "The rate of levy ... is 2%". -/
  mlRate : Int
  /-- MLA s. 3(1) "threshold amount" (c) and "phase-in limit" (c). -/
  mlThreshold : Int
  mlPhaseIn : Int
  /-- MLA s. 7(2): "shall not exceed 10% of the amount of the excess". -/
  mlShadeRate : Int
  /-- MLA s. 8(5): family income threshold and the increase per dependent child. -/
  mlFamily : Int
  mlFamilyChild : Int
  /-- MLA s. 8(2) formula: 0.08 x (family income - threshold). -/
  mlFamilyTaper : Int
  /-- PHI Act 2007 s. 22-35 (indexed under s. 22-45): singles tier 1 / 2 / 3 thresholds. Family thresholds are
  double (s. 22-40(1)-(3)), plus $1,500 for each dependent child after the first (s. 22-40(4), ATO table). -/
  mlsT1 : Int
  mlsT2 : Int
  mlsT3 : Int
  mlsChildStep : Int
  /-- MLA s. 8D(3)(c): a married person's own income for surcharge purposes must exceed this. -/
  mlsMarriedFloor : Int
  /-- MLA ss. 8B(2), (3), (4): 1 %, plus 0.25 and 0.5 of a percentage point. -/
  mlsRate1 : Int
  mlsRate2 : Int
  mlsRate3 : Int
  /-- ITAA 1997 s. 291-20: the concessional contributions cap. -/
  concessionalCap : Int
  /-- ITRA s. 26 / ITAA 1997 s. 295-160: 15 % tax on a fund's assessable contributions. -/
  contribTaxRate : Int
  /-- ITAA 1997 s. 293-20: Division 293 threshold $250,000; rate 15 %. -/
  div293Threshold : Int
  div293Rate : Int
  /-- FTB (FA Act 1999 Sch 1), annual amounts in cents (= fortnightly rate x 365 / 14, DSS guide 3.6.1). -/
  ftbAUnder13C : Int
  ftbA13plusC : Int
  ftbABaseC : Int
  ftbASuppC : Int
  /-- Sch 1 cl 38A(1A): the supplement is nil if adjusted taxable income is more than $80,000 (not indexed). -/
  ftbASuppLimit : Int
  /-- Energy supplement Part A (grandfathered, ceased for new claimants 20 March 2017; cl 6A): max per child
  (under 13 / 13+) and base, in cents a year. -/
  esAUnder13C : Int
  esA13plusC : Int
  esABaseC : Int
  /-- Sch 1 cl 38N (lower income free area, indexed) and cl 2 (higher income free area, indexed); tapers 20 %
  (cl 38M step 5) and 30 % (cl 28 step 5). -/
  ftbALIFA : Int
  ftbAHIFA : Int
  ftbATaper1 : Int
  ftbATaper2 : Int
  /-- FTB B standard rate (cl 30, indexed): youngest under 5 / 5 or over; supplement (cl 31A); ES B (cl 31B). -/
  ftbBUnder5C : Int
  ftbB5plusC : Int
  ftbBSuppC : Int
  esBUnder5C : Int
  esB5plusC : Int
  /-- cl 28B(1): nil if ATI is more than $100,000 (indexed: primary earner income limit); cl 33: income free area
  $4,000 (indexed); cl 32 step 5: 20 %. -/
  ftbBPrimaryLimit : Int
  ftbBFreeArea : Int
  ftbBTaper : Int
  /-- HELP: 2024-25 whole-income bands (lower bound of repayment income, rate bp); 2025-26 marginal. -/
  helpMarginal : Bool
  helpBands : List (Int × Int)
  helpMin : Int
  helpMid : Int
  helpMidBase : Int
  helpR1 : Int
  helpR2 : Int
  helpTop : Int
  helpTopRate : Int
  deriving Repr

/-- Income year 2024-25 (the OECD's "2025" for Australia). -/
def p2025 : Params := {
  label := "2024-25"
  taxFree := 18200
  brackets := [(18200, 1600), (45000, 3000), (135000, 3700), (190000, 4500)]
  litoMax := 700, litoT1 := 37500, litoR1 := 500, litoMid := 325, litoT2 := 45000, litoR2 := 150,
  litoCeiling := 66667
  mlRate := 200, mlThreshold := 27222, mlPhaseIn := 34027, mlShadeRate := 1000
  mlFamily := 45907, mlFamilyChild := 4216, mlFamilyTaper := 800
  mlsT1 := 97000, mlsT2 := 113000, mlsT3 := 151000, mlsChildStep := 1500, mlsMarriedFloor := 27222
  mlsRate1 := 100, mlsRate2 := 125, mlsRate3 := 150
  concessionalCap := 30000, contribTaxRate := 1500, div293Threshold := 250000, div293Rate := 1500
  -- DSS guide 3.6.1 Table 1 (1/07/2024): $222.04 / $288.82 pf; Table 2: $71.26 pf, HIFA $115,997;
  -- Table 3: $916.15 p.a.; Table 4: ES A $3.50 / $4.48 / base $1.40 pf; LIFA $65,189.
  ftbAUnder13C := 578890, ftbA13plusC := 752995, ftbABaseC := 185785, ftbASuppC := 91615, ftbASuppLimit := 80000
  esAUnder13C := 9125, esA13plusC := 11680, esABaseC := 3650
  ftbALIFA := 65189, ftbAHIFA := 115997, ftbATaper1 := 2000, ftbATaper2 := 3000
  -- DSS guide 3.6.3 (1/07/2024): $188.86 / $131.74 pf, income free area $6,789, primary limit $117,194;
  -- supplement $448.95 p.a.; ES B $73.00 / $51.10 p.a.
  ftbBUnder5C := 492385, ftbB5plusC := 343465, ftbBSuppC := 44895, esBUnder5C := 7300, esB5plusC := 5110
  ftbBPrimaryLimit := 117194, ftbBFreeArea := 6789, ftbBTaper := 2000
  -- ATO table 2 (2024-25): repayment income from which each rate applies.
  helpMarginal := false
  helpBands := [(54435, 100), (62851, 200), (66621, 250), (70619, 300), (74856, 350), (79347, 400),
    (84108, 450), (89155, 500), (94504, 550), (100175, 600), (106186, 650), (112557, 700), (119310, 750),
    (126468, 800), (134057, 850), (142101, 900), (150627, 950), (159664, 1000)]
  helpMin := 54435, helpMid := 0, helpMidBase := 0, helpR1 := 0, helpR2 := 0, helpTop := 0, helpTopRate := 0 }

/-- Income year 2025-26 (rates unchanged: ITRA Sch 7 table "2024-25 or 2025-26 year of income"). -/
def p2026 : Params := { p2025 with
  label := "2025-26"
  mlThreshold := 28011, mlPhaseIn := 35013, mlFamily := 47238, mlFamilyChild := 4338
  mlsT1 := 101000, mlsT2 := 118000, mlsT3 := 158000, mlsMarriedFloor := 28011
  -- DSS guide 3.6.1 / 3.6.3 (1/07/2025): $227.36 / $295.82 / base $72.94 pf; supplement $938.05; LIFA $66,722;
  -- HIFA $118,771; FTB B $193.34 / $134.96 pf, supplement $459.90, free area $6,935, primary limit $120,007.
  ftbAUnder13C := 592760, ftbA13plusC := 771245, ftbABaseC := 190165, ftbASuppC := 93805
  ftbALIFA := 66722, ftbAHIFA := 118771
  ftbBUnder5C := 504065, ftbB5plusC := 351860, ftbBSuppC := 45990
  ftbBPrimaryLimit := 120007, ftbBFreeArea := 6935
  -- HESA s. 154-10 ($67,000) and ATO table 1 (2025-26): 15c over $67,000; $8,700 + 17c over $125,000;
  -- 10 % of all repayment income from $179,286.
  helpMarginal := true, helpBands := [], helpMin := 67000, helpMid := 125000, helpMidBase := 8700,
  helpR1 := 1500, helpR2 := 1700, helpTop := 179285, helpTopRate := 1000 }


/-! ## Income years 2021-22, 2022-23 and 2023-24 (round 2; OECD years 2022, 2023, 2024)

Each set differs from 2024-25 only where shown; LITO ($700 / $37,500 / 5 % / $325 / $45,000 / 1.5 % / $66,667) is the
same since 2020-21, the Medicare levy rate 2 % and shade-in 10 %, the Division 293 threshold $250,000, the FTB taper
rates, the FTB A supplement income limit $80,000 and the (closed, unindexed) energy supplement rates are unchanged.
Sources (saved with sha256 in `~/cmp20/improve-anglo/refs/au/` or `~/cmp20/anglo/au/refs/`):
* ITRA 1986 Sch 7 Pt I cl 1, before the Treasury Laws Amendment (Cost of Living Tax Cuts) Act 2024 (which applies
  from 2024-25): 19 % from $18,200, 32.5 % from $45,000, 37 % from $120,000, 45 % from $180,000 (ATO "Tax rates -
  Australian residents", 2021-22 to 2023-24 tables, `refs/ato_rates.txt`).
* LMITO 2021-22 (ITAA 1997 s. 61-107 as increased by $420 by the Treasury Laws Amendment (Cost of Living Support and
  Other Measures) Act 2022): ATO "Low and middle income earner tax offsets" (`refs/ato_lito.txt`): "$37,000 or less
  $675; From $37,001 to $48,000 $675 plus 7.5 cents for every dollar above $37,000, up to a maximum of $1,500; From
  $48,001 to $90,000 $1,500; From $90,001 to $126,000 $1,500 minus 3 cents for every dollar above $90,000";
  "You will not receive it if your taxable income is $126,000 or more."
* Medicare Levy Act 1986 s. 3(1) "threshold amount" (c), "phase-in limit" (c) and s. 8(5) "family income threshold",
  compilations of 1 April 2022 ($23,365 / $29,206; $39,402 + $3,619), 24 June 2023 ($24,276 / $30,345; $40,939 +
  $3,760) and 6 March 2024 ($26,000 / $32,500; $43,846 + $4,027) (legislation.gov.au, Word versions,
  `improve-anglo/refs/au/mla_*.docx`).
* MLS tiers (PHI Act 2007 s. 22-35): $90,000 / $105,000 / $140,000 for 2021-22 and 2022-23, $93,000 / $108,000 /
  $144,000 for 2023-24 (ATO "Medicare levy surcharge income, thresholds and rates", 2022-23 and 2023-24 tables,
  `refs/ato_mls_thresholds.txt`).
* FTB (A New Tax System (Family Assistance) Act 1999 Sch 1), DSS Family Assistance Guide 3.6.1 and 3.6.3 historical
  rate tables (`refs/dss_3_6_1.txt`, `refs/dss_3_6_3.txt`), rates from 1 July of the income year, per fortnight
  (annual = fortnightly x 365/14, as for 2024-25):
  FTB A maximum under 13 / 13-19: $191.24 / $248.78 (2021), $197.96 / $257.46 (2022), $213.36 / $277.48 (2023);
  base rate $61.46 / $63.56 / $68.46; LIFA $56,137 / $58,108 / $62,634; HIFA $99,864 / $103,368 / $111,398; FTB A
  supplement $788.40 / $817.60 / $879.65 a year. FTB B under 5 / 5-18: $162.54 / $113.54 (2021), $168.28 / $117.46
  (2022), $181.44 / $126.56 (2023); income free area $5,840 / $6,059 / $6,497; primary earner limit $100,900 /
  $104,432 / $112,578; supplement $383.25 / $397.85 / $430.70 a year.
* Concessional contributions cap $27,500 in all three years (ITAA 1997 s. 291-20, indexed; $30,000 from 2024-25).
* HELP repayment bands of these years are not set (the 2024-25 bands are kept; the output flags a HELP debtor).
-/

/-- A fortnightly rate (cents) as an annual amount (cents): x 365/14, rounded half up. -/
def pfC (c : Int) : Int := (2 * c * 365 + 14) / 28

def p2024 : Params := { p2025 with
  label := "2023-24"
  brackets := [(18200, 1900), (45000, 3250), (120000, 3700), (180000, 4500)]
  mlThreshold := 26000, mlPhaseIn := 32500, mlFamily := 43846, mlFamilyChild := 4027
  mlsT1 := 93000, mlsT2 := 108000, mlsT3 := 144000, mlsMarriedFloor := 26000
  concessionalCap := 27500
  ftbAUnder13C := pfC 21336, ftbA13plusC := pfC 27748, ftbABaseC := pfC 6846, ftbASuppC := 87965
  ftbALIFA := 62634, ftbAHIFA := 111398
  ftbBUnder5C := pfC 18144, ftbB5plusC := pfC 12656, ftbBSuppC := 43070
  ftbBPrimaryLimit := 112578, ftbBFreeArea := 6497 }

def p2023 : Params := { p2024 with
  label := "2022-23"
  mlThreshold := 24276, mlPhaseIn := 30345, mlFamily := 40939, mlFamilyChild := 3760
  mlsT1 := 90000, mlsT2 := 105000, mlsT3 := 140000, mlsMarriedFloor := 24276
  ftbAUnder13C := pfC 19796, ftbA13plusC := pfC 25746, ftbABaseC := pfC 6356, ftbASuppC := 81760
  ftbALIFA := 58108, ftbAHIFA := 103368
  ftbBUnder5C := pfC 16828, ftbB5plusC := pfC 11746, ftbBSuppC := 39785
  ftbBPrimaryLimit := 104432, ftbBFreeArea := 6059 }

def p2022 : Params := { p2023 with
  label := "2021-22", lmito := true
  mlThreshold := 23365, mlPhaseIn := 29206, mlFamily := 39402, mlFamilyChild := 3619, mlsMarriedFloor := 23365
  ftbAUnder13C := pfC 19124, ftbA13plusC := pfC 24878, ftbABaseC := pfC 6146, ftbASuppC := 78840
  ftbALIFA := 56137, ftbAHIFA := 99864
  ftbBUnder5C := pfC 16254, ftbB5plusC := pfC 11354, ftbBSuppC := 38325
  ftbBPrimaryLimit := 100900, ftbBFreeArea := 5840 }

-- the 2024-25 annual amounts are the fortnightly rates x 365/14 (DSS 3.6.1: $222.04, $288.82, $71.26; 3.6.3: $188.86, $131.74)
#guard pfC 22204 = 578890 && pfC 28882 = 752995 && pfC 7126 = 185785 && pfC 18886 = 492385 && pfC 13174 = 343465

/-- The household's `year` is the year the income year ends (2025 = 2024-25, as the OECD's 2025). -/
def paramsFor (year : Nat) : Params :=
  if year ≥ 2026 then p2026 else if year = 2025 then p2025 else if year = 2024 then p2024
  else if year = 2023 then p2023 else p2022

/-! Fortnightly-to-annual identities (DSS guide fortnightly rates x 365 / 14 = the annual amounts above, exact
in cents). -/
#guard 22204 * 365 / 14 = 578890 ∧ 22204 * 365 % 14 = 0
#guard 28882 * 365 / 14 = 752995 ∧ 7126 * 365 / 14 = 185785
#guard 18886 * 365 / 14 = 492385 ∧ 13174 * 365 / 14 = 343465
#guard 350 * 365 / 14 = 9125 ∧ 448 * 365 / 14 = 11680 ∧ 140 * 365 / 14 = 3650
#guard 22736 * 365 / 14 = 592760 ∧ 29582 * 365 / 14 = 771245 ∧ 7294 * 365 / 14 = 190165
#guard 19334 * 365 / 14 = 504065 ∧ 13496 * 365 / 14 = 351860

end AuTax
