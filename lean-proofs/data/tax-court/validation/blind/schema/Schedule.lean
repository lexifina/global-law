import LegalProofs.USTax.TaxCourt.Params

/-!
# The regular tax: §1 schedules, the §3 Tax Table, and §1(h) for qualified dividends and capital gain (2012–2024)

* `scheduleTax p f ti` — the rate schedule, exact in mills, rounded once to the dollar.
* `tableTax p f ti` — the Tax Table (2012–2024 Form 1040 instructions): lines "at least X but less than Y" of $5/$10/
  $10 up to $25, $25 up to $3,000 and $50 up to $100,000; the entry is the schedule tax on the line's midpoint, rounded
  half up. The same construction as the 2025 model (`TaxCode.Individual.C.Table`); checked against every printed row
  of the nine years' tables by `tools/taxcourt/check_tables.lean` (see the findings in `LegalProofs/USTax/TaxCourt.lean`).
* `taxOn p f ti` — Form 1040 line 16, ordinary case: the Table below $100,000, the schedule from $100,000.
* `regularTax p f ti pref` — the Qualified Dividends and Capital Gain Tax Worksheet (2012–2024 editions; same line
  structure each year), `pref` being qualified dividends plus net capital gain (§1(h)(11), §1(h)(3)). Before 2018 the
  0% and 15% ceilings are the tops of the 15% and 35% brackets (2012: no 20% rate, so no 15% ceiling); from 2018 they are the §1(j)(5)(B) amounts.
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual

/-- Tax from the rate schedule, in whole dollars (rounded half up from exact mills). -/
def scheduleTax (p : Params) (f : Filing) (ti : Int) : Int := roundDollar ((p.sched f).mills ti) 1000

/-- Twice the midpoint of the Tax Table line containing `ti` (0 ≤ ti < 100,000). -/
def midpoint2 (ti : Int) : Int :=
  if ti < 5 then 5
  else if ti < 15 then 20
  else if ti < 25 then 40
  else if ti < 3000 then 2 * (ti / 25 * 25) + 25
  else 2 * (ti / 50 * 50) + 50

/-- The schedule in mills on half-dollar amounts: `mills2 s m` is the tax on `m / 2` dollars, times 2. -/
def RateSched.mills2 (s : RateSched) (m : Int) : Int :=
  let d : RateSched := ⟨2 * s.e1, 2 * s.e2, 2 * s.e3, 2 * s.e4, 2 * s.e5, 2 * s.e6, s.r1, s.r2, s.r3, s.r4, s.r5,
    s.r6, s.r7, 2 * s.b1, 2 * s.b2, 2 * s.b3, 2 * s.b4, 2 * s.b5, 2 * s.b6⟩
  d.mills m

/-- The Tax Table entry: the schedule tax on the line's midpoint, rounded half up. -/
def tableTax (p : Params) (f : Filing) (ti : Int) : Int :=
  if ti ≤ 0 then 0 else roundDollar ((p.sched f).mills2 (midpoint2 ti)) 2000

/-- Form 1040 line 16, ordinary case. -/
def taxOn (p : Params) (f : Filing) (ti : Int) : Int :=
  if ti < 100000 then tableTax p f ti else scheduleTax p f ti

/-- The Qualified Dividends and Capital Gain Tax Worksheet, lines 1–25 (each line rounded to the dollar).
`ti` taxable income; `pref` qualified dividends plus the smaller of Schedule D lines 15 and 16 (not below zero). -/
def regularTax (p : Params) (f : Filing) (ti pref : Int) : Int :=
  if pref ≤ 0 then taxOn p f ti else
  let l1 := ti
  let l4 := pref
  let l5 := pos (l1 - l4)
  let l7 := min l1 (p.cg0 f)
  let l8 := min l5 l7
  let l9 := l7 - l8                     -- taxed at 0%
  let l10 := min l1 l4
  let l12 := l10 - l9
  -- 2012: no 20% rate (§1(h)(1)(C) as then in force): everything above the 0% band is taxed at 15%
  let l14 := if p.year ≤ 2012 then l1 else min l1 (p.cg15 f)
  let l15 := l5 + l9
  let l16 := pos (l14 - l15)
  let l17 := min l12 l16                -- taxed at 15%
  let l18 := pctRound l17 1500
  let l20 := l10 - l9 - l17             -- taxed at 20%
  let l21 := pctRound l20 2000
  let l22 := taxOn p f l5
  min (l18 + l21 + l22) (taxOn p f l1)

/-! ## Tests: printed base amounts (Tables 1–4 of each revenue procedure) -/

/-- The parameters of a covered year (tests only; outside 2012–2024 it is all zeros). -/
def P (y : Nat) : Params := (params? y).getD default

-- Rev. Proc. 2015-53 Table 3 (2016 single): over $413,350 → $119,934.75; over $415,050 → $120,529.75
#guard (rateSched 2016 .single).mills 413350 = 119934750 ∧ (rateSched 2016 .single).mills 415050 = 120529750
-- Rev. Proc. 2016-55 Table 2 (2017 HoH): over $444,550 → $126,950
#guard (rateSched 2017 .hoh).mills 444550 = 126950000
-- Rev. Proc. 2018-18 Table 1 (2018 joint): over $600,000 → $161,379
#guard (rateSched 2018 .mfj).mills 600000 = 161379000
-- Rev. Proc. 2018-57 Table 4 (2019 separate): over $306,175 → $82,354.75
#guard (rateSched 2019 .mfs).mills 306175 = 82354750
-- Rev. Proc. 2019-44 Table 3 (2020 single): over $518,400 → $156,235
#guard (rateSched 2020 .single).mills 518400 = 156235000
-- Rev. Proc. 2020-45 Table 2 (2021 HoH): over $523,600 → $156,355
#guard (rateSched 2021 .hoh).mills 523600 = 156355000
-- Rev. Proc. 2021-45 Table 1 (2022 joint): over $647,850 → $174,253.50
#guard (rateSched 2022 .mfj).mills 647850 = 174253500
-- Rev. Proc. 2022-38 Table 4 (2023 separate): over $346,875 → $93,300.75
#guard (rateSched 2023 .mfs).mills 346875 = 93300750
-- Rev. Proc. 2023-34 Table 3 (2024 single): over $609,350 → $183,647.25
#guard (rateSched 2024 .single).mills 609350 = 183647250

/-! ## Tests: Tax Table rows printed in each year's Form 1040 instructions (columns single, MFJ, MFS, HoH) -/

def tableRow (y : Nat) (ti : Int) : List Int := [Filing.single, .mfj, .mfs, .hoh].map (tableTax (P y) · ti)

-- 2016 instructions: 48,500–48,550 → 7,903 / 6,351 / 7,903 / 6,616; 99,950–100,000 → 21,030 / 16,536 / 21,486 / 19,291
#guard tableRow 2016 48500 = [7903, 6351, 7903, 6616]
#guard tableRow 2016 99950 = [21030, 16536, 21486, 19291]
-- 2017: 77,000–77,050 → 14,995 / 10,734 / 15,009 / 13,509
#guard tableRow 2017 77000 = [14995, 10734, 15009, 13509]
-- 2018: 48,500 → 6,615 / 5,442 / 6,615 / 5,551; 99,950 → 18,284 / 13,874 / 18,284 / 16,892
#guard tableRow 2018 48500 = [6615, 5442, 6615, 5551]
#guard tableRow 2018 99950 = [18284, 13874, 18284, 16892]
-- 2019: 77,000 → 12,804 / 8,855 / 12,804 / 11,384
#guard tableRow 2019 77000 = [12804, 8855, 12804, 11384]
-- 2020: 48,500 → 6,466 / 5,428 / 6,466 / 5,541
#guard tableRow 2020 48500 = [6466, 5428, 6466, 5541]
-- 2021: 99,950 → 18,015 / 13,492 / 18,015 / 16,563
#guard tableRow 2021 99950 = [18015, 13492, 18015, 16563]
-- 2022: 77,000 → 12,563 / 8,832 / 12,563 / 11,063
#guard tableRow 2022 77000 = [12563, 8832, 12563, 11063]
-- 2023: 48,500 → 5,983 / 5,383 / 5,983 / 5,509
#guard tableRow 2023 48500 = [5983, 5383, 5983, 5509]
-- 2024: 99,950 → 17,048 / 12,101 / 17,048 / 15,354; first lines 15–25 → 2, 1,000–1,025 → 101
#guard tableRow 2024 99950 = [17048, 12101, 17048, 15354]
#guard tableRow 2024 15 = [2, 2, 2, 2] ∧ tableRow 2024 1000 = [101, 101, 101, 101]

/-! ## Tests: capital gain worksheet -/

-- All income qualified dividends inside the 0% band: no tax (2024 single, $40,000 taxable income).
#guard regularTax (P 2024) .single 40000 40000 = 0
-- 2017 single, $50,000 taxable income of which $10,000 qualified dividends: $40,000 ordinary is taxed from the Table
-- (40,000–40,050 → $5,745 single, 2017 Tax Table), $37,950 − $40,000 < 0 so nothing at 0%; $10,000 at 15% = $1,500.
#guard taxOn (P 2017) .single 40000 = 5745
#guard regularTax (P 2017) .single 50000 10000 = 5745 + 1500

end Legal.USTax.TaxCourt
