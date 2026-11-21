# Korea 2025: what is most useful

Evidence: FINDINGS.md (F-numbers), the Lean model `lean/KrTax` (theorem names), the kernel scanners
`results/search/SUMMARY.md`.

## For a taxpayer
1. **Your monthly withholding is too high by design of an old table.** The 간이세액표 used all through 2025 applies the
   2014 근로소득세액공제 and the 2017 pension ceiling (F8): a single employee earning 3.0M won a month has 12,840 won a
   month (154,080 a year) more withheld than the 2025 law's own note-1 method gives; at 4.73M a month 4,120 (49,440 a
   year). It comes back at the 연말정산, so check it does: the refund is not a windfall. With children aged 8-20 the
   table also uses the 2024 child credit (F5: 16,670 won a month too much with two children).
2. **The 7,000만원 total-income line of the 자녀장려금 is a cliff, and dividends and interest count.** A family with
   two children loses about 762,000 won at 7,000만원 (F9, `wall_ctc_gap`); with large dividends and low wages up to
   1,750,000 won for one won (`wall_ctc_dividends`). The table even stops at 69,999,990 won (F4).
3. **Near 7,000만원 and 1.2억원 of pay, a raise is taxed at 79 % and 96 %** while the 근로소득세액공제 limit is
   withdrawn (70.0-70.32M; 120.0-120.6M, F10). Salary sacrifice into 연금저축/IRP (900만원 at 12-15 %) is worth most there.
4. **A spouse earning just over 500만원 of salary costs the family about 250,000 won** (the 기본공제 is lost:
   `wall_spouse_test`).
5. **Unmarried partners can get 장려금 a married couple cannot** (the household test adds a spouse's income; marriage
   penalty up to 4.08M won on the scan grid, F14).

## For an adviser
1. **Owner-managers:** salary plus dividends of about 2천만원 a year beat sole proprietorship by 4.6M won (1 AW of profit)
   to 31M won (10 AW) in 2025 (F13); the 2025 19 % rate for small rental companies (§55①2) narrows but does not close it.
2. **The 2천만원 financial-income threshold is about health insurance, not income tax, for basic-rate employees** (F15):
   the §62 comparison makes 종합과세 at 15 % cost the same; the NHI 보수 외 소득월액보험료 (8 % of the excess) is the cost.
3. **직장 vs 지역 health insurance** decides more than the tax for clients with capital income (F12: 3.09M won on 1 AW
   of dividends); 금융소득 of 10,000,001 won adds ~800,000 won for a 지역가입자.
4. **근로장려금 edges:** the first 40,000 won of earnings are worth 100,000 won; the last won before each end point
   (21,881,900 / 31,905,300 / 43,877,300) is worth 30,000 (F11). One-earner families below 4M won get the single-person
   amount from the table, more than the act's formula (F3).
5. **Who claims the children** in a two-earner couple barely matters for the credits (≤ 30,000 won on the grid); it can
   matter for the 장려금 and for itemised medical/card spending (not modelled).

## For the Korean government (and the OECD)
1. **Update 소득세법 시행령 별표 2** (F8): recompute the 간이세액표 with §59 as amended in 2015 (and 2022), the current
   국민연금 ceiling and the 2025 자녀세액공제 (F5). Draft note (not sent):
   > 근로소득 간이세액표(소득세법 시행령 별표 2, 2024. 2. 29. 개정)의 세액은 비고 1의 방법에 2014년 근로소득세액공제
   > (산출세액 50만원 이하 55%, 초과 30%; 한도 66만/63만/50만원)와 2017. 7.-2018. 6. 국민연금 기준소득월액 상한
   > (449만원)을 적용하여 7,106칸 중 7,098칸이 정확히 재현됩니다(나머지 8칸은 10원 차이). 현행 제59조(130만원 기준;
   > 한도 74만/66만/50만/20만원)와 현행 상한(617만/637만원)을 적용하면 3,790칸에서 세액이 낮아집니다(월 최대 28,040원).
   > 비고 3의 자녀 공제(12,500원/29,160원/25,000원)도 2025년 자녀세액공제(25만/55만/40만원)에 맞지 않습니다.
2. **Fix law.go.kr's text of 소득세법 §55①** (F2): the accessible text (image alt) of the top row omits "3억8,406만원 +".
   Draft note (not sent): "소득세법 제55조제1항 세율표 이미지의 대체텍스트 중 '10억원 초과' 행에 '3억8,406만원 +'가 누락되어
   있습니다(현행 및 2025. 1. 1. 시행본)."
3. **Close the 10-won gap of the 자녀장려금 산정표** (F4: last row "69,999,990 미만"; the act admits "7천만원 미만") and
   align the 근로장려금 산정표 with §100의5① for 홑벌이 below 400만원 (F3) — or amend the formula to say the table's rule.
4. **Smooth the cliffs**: the 자녀장려금 ends at 7천만원 of total income with up to 1,000,000 won per child left (F9);
   a taper on total income, or testing earnings for both eligibility and amount, removes a METR above 700 %.
5. **For the OECD (Taxing Wages Korea):** the published Korean families behave as two children under 8 at home
   (CTGG 4,800,000 = 2 × (아동수당 + 양육수당) × 12, no 자녀세액공제); with the standard children aged 6 and 11 the
   statute gives 아동수당 for one child (1,200,000) and a 250,000-won 자녀세액공제 for the 11-year-old (F1), as the OECD's
   own TaxBEN Korea 2025 description states. The long-term-care premium should use 0.9182/7.09, not 12.95 % (F6).
   Draft issue (not sent): "Taxing Wages 2026, Korea, families with children: CTGG 4,800,000 and the absence of the child
   tax credit (ITA art. 59-2, KRW 250,000 for one child aged 8+) imply children under 8; please state the ages used or
   apply ages 6 and 11 (child allowance for the 6-year-old only)."
