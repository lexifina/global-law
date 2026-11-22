import FrTax.Basic

/-!
# The amounts the Code général des impôts fixes for each income year

Two income years are modelled: **2024** (taxed in 2025; text as amended by loi n° 2025-127 du 14 février
2025, de finances pour 2025) and **2025** (taxed in 2026; text as amended by loi n° 2026-103 du 19 février
2026, de finances pour 2026). Each amount is copied from the article that fixes it, in its version in force
for that year (france-law history, files `codes/code-general-des-impots-cgi/<art>.md` at the commit named
in `law/<year>/<art>.md.src`).

Where an article prints last year's amount and an indexation rule instead of this year's amount
(art. 83, 3° for the salary allowance; art. 158, 5, a for the pension allowance), the amount here is the
one the indexation gives; `Indexation.lean` checks it.
-/

namespace FrTax

structure Params where
  year : Nat
  /-- art. 197, I, 1: the starts of the 11 %, 30 %, 41 % and 45 % slices of one part. -/
  b1 : Int
  b2 : Int
  b3 : Int
  b4 : Int
  /-- art. 197, I, 2, first paragraph: the most the quotient familial may save per half part. -/
  qfHalf : Int
  /-- art. 197, I, 2, second paragraph: cap for the part given for the first child of a single parent
  (art. 194, II). -/
  qfFirstChildSingle : Int
  /-- art. 197, I, 2, third paragraph: cap for the half part of art. 195, 1, a, b and e. -/
  qfCaseL : Int
  /-- art. 197, I, 2, fourth paragraph: the complementary reduction per half part of art. 195. -/
  qfComplement : Int
  /-- art. 197, I, 2, fifth paragraph: the complementary reduction for a widow(er)'s extra part. -/
  qfWidow : Int
  /-- art. 197, I, 4, a: the décote, `single - 45.25 % of the tax` (couples: `couple - ...`). -/
  decSingle : Int
  decCouple : Int
  /-- art. 83, 3°: the 10 % allowance on salaries, its minimum and its maximum (per person). -/
  salMin : Int
  salMax : Int
  /-- art. 158, 5, a: the 10 % allowance on pensions, its minimum (per pensioner) and its maximum (per
  household). -/
  penMin : Int
  penMax : Int
  /-- art. 157 bis: allowance for each member over 65 or disabled: `ageHi` if the revenu net global is at
  most `ageT1`, `ageLo` if it is at most `ageT2`. -/
  ageHi : Int
  ageLo : Int
  ageT1 : Int
  ageT2 : Int
  /-- art. 196 B: allowance per married (or parent) child attached to the household; art. 156, II, 2°
  caps the deductible alimony paid to an adult child at the same amount. -/
  attached : Int
  /-- art. 200, 1 ter: limit of gifts to aid organisations that get 75 %. -/
  giftsAidMax : Int
  /-- art. 81 quater, I: annual limit of tax-free overtime pay (7 500 € for income 2020 under loi n° 2020-473,
  5 000 € for 2021, 7 500 € from 2022 under loi n° 2022-1157). -/
  overtimeMax : Int := 7500
  /-- art. 200 quater B: childcare costs per child under six (2 300 €; 3 500 € from loi n° 2022-1726). -/
  childcareMax : Int := 3500
  /-- Box 7UJ, 75 % rate: gifts to religious associations within 554 € (2021) and 562 € (2022); from 2023 the box
  holds gifts to the upkeep of religious heritage, within 1 000 €; no such box in 2020. -/
  box7UJMax : Int := 1000
  deriving Repr

/-- Income 2024 (impôt 2025): loi n° 2025-127 du 14 février 2025. -/
def p2024 : Params where
  year := 2024
  b1 := 11497
  b2 := 29315
  b3 := 83823
  b4 := 180294
  qfHalf := 1791
  qfFirstChildSingle := 4224
  qfCaseL := 1069
  qfComplement := 1785
  qfWidow := 1993
  decSingle := 889
  decCouple := 1470
  salMin := 504
  salMax := 14426
  penMin := 450
  penMax := 4399
  ageHi := 2796
  ageLo := 1398
  ageT1 := 17510
  ageT2 := 28170
  attached := 6794
  giftsAidMax := 1000

/-- Income 2025 (impôt 2026): loi n° 2026-103 du 19 février 2026. -/
def p2025 : Params where
  year := 2025
  b1 := 11600
  b2 := 29579
  b3 := 84577
  b4 := 181917
  qfHalf := 1807
  qfFirstChildSingle := 4262
  qfCaseL := 1079
  qfComplement := 1801
  qfWidow := 2011
  decSingle := 897
  decCouple := 1483
  salMin := 509
  salMax := 14555
  penMin := 454
  penMax := 4439
  ageHi := 2822
  ageLo := 1411
  ageT1 := 17670
  ageT2 := 28430
  attached := 6855
  giftsAidMax := 2000


/-- Income 2020: CGI art. 197 as amended by the finance law for 2021; amounts of art. 83, 157 bis, 158, 196 B
from the DGFiP brochure pratique 2024 (aide-mémoire, revenus 2020–2023). -/
def p2020 : Params where
  year := 2020
  b1 := 10084
  b2 := 25710
  b3 := 73516
  b4 := 158122
  qfHalf := 1570
  qfFirstChildSingle := 3704
  qfCaseL := 938
  qfComplement := 1565
  qfWidow := 1748
  decSingle := 779
  decCouple := 1289
  salMin := 442
  salMax := 12652
  penMin := 394
  penMax := 3858
  ageHi := 2448
  ageLo := 1224
  ageT1 := 15340
  ageT2 := 24690
  attached := 5959
  giftsAidMax := 1000
  overtimeMax := 7500
  childcareMax := 2300
  box7UJMax := 0

/-- Income 2021: CGI art. 197 as amended by the finance law for 2022; amounts of art. 83, 157 bis, 158, 196 B
from the DGFiP brochure pratique 2024 (aide-mémoire, revenus 2020–2023). -/
def p2021 : Params where
  year := 2021
  b1 := 10225
  b2 := 26070
  b3 := 74545
  b4 := 160336
  qfHalf := 1592
  qfFirstChildSingle := 3756
  qfCaseL := 951
  qfComplement := 1587
  qfWidow := 1772
  decSingle := 790
  decCouple := 1307
  salMin := 448
  salMax := 12829
  penMin := 400
  penMax := 3912
  ageHi := 2484
  ageLo := 1242
  ageT1 := 15560
  ageT2 := 25040
  attached := 6042
  giftsAidMax := 1000
  overtimeMax := 5000
  childcareMax := 2300
  box7UJMax := 554

/-- Income 2022: CGI art. 197 as amended by the finance law for 2023; amounts of art. 83, 157 bis, 158, 196 B
from the DGFiP brochure pratique 2024 (aide-mémoire, revenus 2020–2023). -/
def p2022 : Params where
  year := 2022
  b1 := 10777
  b2 := 27478
  b3 := 78570
  b4 := 168994
  qfHalf := 1678
  qfFirstChildSingle := 3959
  qfCaseL := 1002
  qfComplement := 1673
  qfWidow := 1868
  decSingle := 833
  decCouple := 1378
  salMin := 472
  salMax := 13522
  penMin := 422
  penMax := 4123
  ageHi := 2620
  ageLo := 1310
  ageT1 := 16410
  ageT2 := 26400
  attached := 6368
  giftsAidMax := 1000
  overtimeMax := 7500
  childcareMax := 3500
  box7UJMax := 562

/-- Income 2023: CGI art. 197 as amended by the finance law for 2024; amounts of art. 83, 157 bis, 158, 196 B
from the DGFiP brochure pratique 2024 (aide-mémoire, revenus 2020–2023). -/
def p2023 : Params where
  year := 2023
  b1 := 11294
  b2 := 28797
  b3 := 82341
  b4 := 177106
  qfHalf := 1759
  qfFirstChildSingle := 4149
  qfCaseL := 1050
  qfComplement := 1753
  qfWidow := 1958
  decSingle := 873
  decCouple := 1444
  salMin := 495
  salMax := 14171
  penMin := 442
  penMax := 4321
  ageHi := 2746
  ageLo := 1373
  ageT1 := 17200
  ageT2 := 27670
  attached := 6674
  giftsAidMax := 1000
  overtimeMax := 7500
  childcareMax := 3500

def paramsFor (year : Nat) : Option Params :=
  match year with
  | 2020 => some p2020 | 2021 => some p2021 | 2022 => some p2022 | 2023 => some p2023
  | 2024 => some p2024 | 2025 => some p2025 | _ => none

end FrTax
