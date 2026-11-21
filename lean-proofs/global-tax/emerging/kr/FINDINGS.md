# South Korea (KR), tax year 2025: findings

Model: `lean/KrTax` (exe `krtax`), Seoul resident, 소득세법 법률 제20615호 (in force 2025-01-01), 조세특례제한법 제21138호,
지방세법 제20630호, social decrees for 2025 (`lean/KrTax/Basic.lean` lists every source). Texts: law.go.kr (official),
fetched with `scripts/lawgo.py` into `refs/lawgo/`; tables from law.go.kr 별표 PDFs (`refs/pdf/`). The Global law
corpus holds 소득세법 and 법인세법 (current text only, without the statute's tables: they are images on law.go.kr) but not
조세특례제한법, 지방세법, the decrees or the social acts (`list_jurisdictions "south korea"`: "Four core acts with dated
version histories and 500 additional acts with one current consolidated text each; normative source images remain
deferred", record to 2026-11-05).

### F1 The OECD's Korean Taxing Wages families have two children under 8 at home, not 6 and 11
- kind: gov-error (OECD model; a convention if the OECD's children are meant to be "aged between 6 and 11" and both
  were chosen under 8)
- households: SP67, M100_0, M100_100, M100_67 (all types with children), 2025 (CTGG = 4,800,000 in every year 2022-2025)
- amounts: OECD CTGG 4,800,000 = 2 children × (아동수당 100,000 + 양육수당 100,000) × 12. For the harness children
  (6 and 11) the statute gives 아동수당 for the 6-year-old only (1,200,000; 아동수당법 §4① "8세 미만"), no 양육수당 for a
  pupil of 11, and a 자녀세액공제 of 250,000 for the 11-year-old (소득세법 §59의2① "8세 이상 … 1명인 경우: 연 25만원")
  with 25,000 less 지방소득세. The OECD's own policy description (TaxBEN Korea 2025 §6, `refs/oecd/taxben.txt` l.1709-1715)
  lists that credit "from children aged 8 or above", yet Taxing Wages applies none: national tax 250,000 too high for
  M100_100 and M100_67; for SP67 and M100_0 the 자녀장려금 absorbs the credit (STA §100의30②, STAD §100의31②: the 장려금
  is reduced by the 자녀세액공제), so only their 지방소득세 is 25,000 too high.
- check: the eight families with children aged 6 and 7 and `krHomeCare` reproduce the OECD's CTGG, CTC (1,654,000;
  1,276,000) and SLT (`results/oecd_check_variant.json`).
- provisions: 아동수당법 §4①, 영유아보육법 §34의2, 소득세법 §59의2①, 조특법 §100의30②
- Lean: `KrTax.childBenefits`, `KrTax.childCredit`, `KrTax.ctc`
- status: confirmed; issue text drafted in USEFUL.md (for the OECD Taxing Wages team), not sent

### F2 law.go.kr's text of the top income-tax bracket drops "3억8,406만원 +"
- kind: gov-error (publication)
- the §55① rate table is an image (flSeq 123278409). The image reads "10억원 초과 | 3억8,406만원 + (10억원을 초과하는 금액의
  45퍼센트)" (checked visually, `refs/img/s55.bin`); the text law.go.kr publishes with it (the image's `alt` text, read by
  screen readers and scrapers) is "10억원 초과 … 10억원을 초과하는 금액의 45퍼센트": a top-bracket tax 384,060,000 won too
  low. Same in the 2025 and the current (2026-07-01) version. The local-tax twin (지방세법 §92①) reads "3천840만6천원 + …"
  correctly. The Global law corpus text of §55 has no table at all.
- households: any 과세표준 above 10억원 computed from the text
- provisions: 소득세법 §55①
- Lean: `KrTax.natSched` (from the image)
- status: confirmed (image vs text); note for 법제처 drafted in USEFUL.md

### F3 The 근로장려금 산정표 pays one-earner families more than the statute's formula below 4 million won
- kind: statute-fault (table ≠ formula; the table governs, STA §100의5⑤)
- STA §100의5①2가: 홑벌이 가구 "총급여액등 × 700분의285" below 700만원. 조특법 시행령 별표 11 (<개정 2025. 2. 28.>) prints, for
  홑벌이 rows from 70,000 to 4,000,000 won, the 단독가구 amounts (slope 165/400 = 0.4125 > 285/700 = 0.4071): 40 of 447
  rows disagree with the formula under the table's own rounding rule (every other cell of both tables equals the formula's
  largest value on the row, rounded up to 1,000 won, nil under 15,000). Largest gap 21,000 won (row 3,900,000-4,000,000:
  table 1,650,000, formula 1,629,000).
- provisions: 조특법 §100의5①⑤, 시행령 §100의6⑤ 별표 11
- also 2 split rows (21,770,000-21,800,000 and 21,881,900-21,900,000, where the 단독 amount crosses 3만/1만5천원): the
  홑벌이 cell repeats the whole 100,000-won row's amount (1,631,000; 1,615,000) instead of the rule's 1,620,000 / 1,603,000,
  while the 맞벌이 cell is recomputed. So 42 홑벌이 cells disagree with the rule, all in the household's favour.
- Lean (kernel-checked): `eitc_single_dual_follow_rule` (단독 and 맞벌이: every cell), `eitc_one_earner_exceptions`
  (exactly 42, of which 40 below 4M print the 단독 amount), `eitc_one_earner_table_higher`, `ctc_follows_rule`
  (자녀장려금: every cell)
- status: proved

### F4 The 자녀장려금 산정표 stops 10 won short of 7,000만원
- kind: statute-fault (minor)
- 별표 11의2 (<개정 2024. 2. 29.>) last row "69,500,000 이상 69,999,990 미만 | 506,000 | 506,000"; STA §100의28①2 admits total
  income "7천만원 미만". A family with 총급여액 등 of 69,999,990 to 69,999,999 won falls in no row: nil instead of 506,000
  per child (1,012,000 for two).
- Lean: `ctc_table_gap`, `ctc_contiguous`; in money `Walls.wall_ctc_gap`: a couple with children 6 and 11 and wages
  69,999,990 has 761,999 won less than at 69,999,989 (the 자녀장려금 cliff of §100의28 arrives 10 won early)
- status: proved

### F5 The monthly withholding table still uses the 2024 child credit
- kind: gov-error (amount not updated when a related amount changed)
- 소득세법 시행령 별표 2 근로소득 간이세액표 (<개정 2024. 2. 29.>; unchanged in the decree of 2025-02-28 and in the current one
  of 2026-02-27) note 3: for children aged 8-20 the monthly tax is reduced by 12,500 / 29,160 / 29,160 + 25,000 per
  further child: the credit of 소득세법 §59의2① as in 법률 제19933호 (2024: 15만 / 35만 / +30만 a year, ÷ 12). From 2025 the
  credit is 25만 / 55만 / +40만 (법률 제20615호): 20,833 / 45,833 / +33,333 a month. An employee with two such children is
  over-withheld 16,670 won a month (200,040 a year), refunded only at the 연말정산.
- provisions: 소득세법 §59의2①, §134, 시행령 §189 별표 2
- Lean: the table is `whtRows` (F8); note 3's amounts are not used by `whtModel`
- status: confirmed (texts of both versions)

### F6 The OECD's 장기요양 premium uses the rounded ratio 12.95 %
- kind: gov-error (OECD; trivial) / convention
- 노인장기요양보험법 §9①: premium = health premium × (장기요양보험료율 / 건강보험료율) = 0.9182 / 7.09 = 12.9506 %; the OECD
  uses 12.95 % (employee 0.459078 % vs 0.4591 % of wages): 21 won a year too little at 1.67 AW.
- Lean: `KrTax.ltcEmployee` vs `KrTax.socialOecd`
- status: confirmed

### F7 The pension base is cut to the 1,000 won (OECD: not)
- kind: model-fix (convention difference with the OECD)
- 국민연금법 시행령 §5①: 기준소득월액 = 신고 소득월액 "천원 미만을 버린 금액"; the OECD applies 4.5 % to annual wages. Up to
  12 × 45 = 540 won a year. With the OECD's conventions (`krConvention: "oecd"`) the model reproduces the OECD's lines
  to ±3 won (41 of 48 within 1 won; the rest are the OECD's fractional carries).
- status: done

### F8 The monthly withholding table is computed with the 2014 근로소득세액공제 and the 2017 pension ceiling
- kind: gov-error (decree table inconsistent with the act and with its own note 1)
- 소득세법 시행령 별표 2 (<개정 2024. 2. 29.>, in force for all of 2025, unchanged in the decree of 2026-02-27) says its
  amounts reflect "「소득세법」에 따른 … 근로소득세액공제" and gives its method (note 1). Recovered rule, checked by the
  kernel on all 7,106 cells (646 rows × 11 family sizes): the row's midpoint × 12; §47 근로소득공제; 150만원 per family
  member; note 1's special-deduction formula; 국민연금 4.5 % of the midpoint cut to the 1,000 won **capped at 4,490,000**
  (the 기준소득월액 ceiling of July 2017 - June 2018; 2025: 6,170,000 / 6,370,000); the §55 rates of 2023 on; and the
  근로소득세액공제 of §59 **as in 법률 제12169호 (2014)**: 55 % of the 산출세액 up to 50만원, 30 % above; limit 66만원 to
  총급여 5,500만원, then 66만 − ½ × excess but ≥ 63만원, above 7,000만원 ≥ 50만원 — not the law since 법률 제13315호
  (2015-05-13: kink at 130만원; limits 74만 / 66만 / 50만 / 20만원); ÷ 12, cut to the 10 won, nil under 1,000 won (§86).
  7,098 cells equal this rule; the other 8 are exactly 10 won above it (rounding not recovered).
- effect: against the same note-1 computation under the 2025 law, the table is never lower and is higher in 3,790 of
  7,106 cells: 12,840 won a month for one person at 3,000,000-3,020,000 (154,080 a year), 4,120 at the OECD average-wage
  row 4,720,000-4,740,000 (49,440 a year), up to 28,040 a month (336,480 a year) at 9,960,000-10,000,000. The excess
  comes back at the 연말정산 (no tax is lost), but it is an interest-free loan to the state and has kept the 2015 relief
  out of monthly pay for ten years. (Employees may choose 80/100/120 % of the table, 시행령 §194.)
- also in the table: above 10,000천원 a month the printed formula adds a flat 25,000 won ("… + (25,000원)"): one won of
  monthly pay above 10,000,000 raises that month's withholding by 25,000 won.
- provisions: 소득세법 §59 (법률 제12169호 vs 제20615호), §86, §134; 시행령 §189 별표 2; 국민연금법 시행령 §5
- Lean: `KrTax.whtModel`, `wht_chunk0` … `wht_chunk12` (every cell), `wht_exceptions_differ`, `wht_aw_row`,
  `wht_3m_row`; Python twin `scripts/wht_model.py`
- status: proved; note for 기획재정부/국세청 drafted in USEFUL.md

### F9 자녀장려금: eligibility counts dividends, the amount does not — a 1,750,000-won cliff
- kind: loophole-new (cliff; METR 1,550 % over 0.002 AW)
- STA §100의28①2 tests 연간 총소득 (wages, business, interest, dividends, pensions) < 7천만원; §100의29 sets the amount by
  총급여액 등 (earnings only). A one-earner couple with children 6 and 11, 56,749,797 won of dividends and 13,250,202 won
  of wages gets the full 2 × 1,000,000 less the 250,000 자녀세액공제 = 1,750,000 won; one won more of wages (or of
  interest) and it gets nothing. The 7천만원 cliff exists for every family (761,999 net for an earner with two children,
  METR 709 % over 1.232-1.234 AW) but is largest where earnings are low and capital income high.
- found by: the kernel METR scanner (`results/search/metr.md`, couple_1earner_2|dividends_1AW), unprompted
- Lean: `Walls.wall_ctc_dividends` (net difference 1,749,999 won, kernel-evaluated on the whole model)
- known? the 7천만원 limit is public (NTS 장려금 guidance); the dividend interaction was not found in the 2 press sources
  read for this work (nocutnews.co.kr/news/5272140, economist.co.kr ecn202412180053): a candidate, not claimed novel
- status: confirmed

### F10 The 근로소득세액공제 limit pushes the marginal rate to 79 % and 96 %
- kind: loophole-new (phase-out bands; the rule is public, the rates are quantified here)
- ITA §59② withdraws the limit at ½ won per won: 66만 → 50만원 between 70,000,000 and 70,320,000, and (since the
  2022-12-31 amendment) 50만 → 20만원 between 120,000,000 and 120,600,000. Where the limit binds (every employee there)
  the rate rises by 50 points: single METR 78.7 % and 95.8 %, against the 48.84 % statutory top combined rate. Net gain
  from 320,000 won more pay at 70M: 68,562; from 600,000 more at 120M: 25,525.
- found by: METR and phase-out scanners (bands above the top rate, stacked with 지방소득세)
- Lean: `Theorems.earnedCreditLimit_slope` (all pay in the band), `earnedCreditLimit_antitone`, `earnedCreditLimit_continuous`
- status: proved

### F11 근로장려금 starts with a 100,000-won step and ends with a 30,000-won cliff
- kind: loophole-new (notches made by the 결정 rules; small)
- STA §100의7③ raises a phase-in amount of 1만5천-10만원 to 10만원, a phase-out amount of 1만5천-3만원 to 3만원, and nils
  anything under 1만5천원; the 산정표 starts at 40,000 won. A single person earning 40,000 won gets 100,000 won (99,999
  net more than at 39,999); at the end each household type drops from 30,000 won to nil in one won (단독 21,881,900;
  홑벌이 31,905,300; 맞벌이 43,877,300 won 총급여액 등).
- Lean: `Walls.wall_eitc_start` (99,999), `Walls.wall_eitc_end` (29,999); `Incentive.eitcDecide`
- status: proved

### F12 A few won of wages cut the health premium on capital income
- kind: loophole-known (직장가입자 vs 지역가입자), recreated
- 국민건강보험법 §71 and 시행규칙 §44: an employee pays the 보수 외 소득월액보험료 only on other income above 연간
  2천만원 (이자·배당 counted only above 1천만원); a person without wages (지역가입자) pays on all of it. With 56.7M won of
  dividends the first won of wages saves 3,090,296 won (METR scanner, single|dividends_1AW at 0). A genuine employment is
  required; the property part of the 지역 premium (not modelled) widens the gap. The 1천만원 rule is a cliff for
  지역가입자: 10,000,001 won of interest adds about 800,000 won of premium.
- Lean: `KrTax.nhiOtherIncome`, `healthOnOther`
- status: confirmed

### F13 Owner-manager: a company, salary, and dividends up to the 2천만원 threshold
- kind: loophole-known (법인 전환, 급여 vs 배당), recreated
- `scripts/owner_manager.py` (법인세법 §55① 9 % / 19 % + 법인지방소득세 one tenth, employer social, krtax for the owner):
  for profits of 1-10 AW the best split keeps dividends at about 2천만원 (the 종합과세 threshold, ITA §14③6, where the NHI
  보수외소득 premium also starts) and pays the rest as salary. Net gain over a sole proprietor (사업소득, 지역 social):
  4.6M won at 1 AW, 10.2M at 2 AW, 14.9M at 3 AW, 31.2M at 10 AW (`results/owner_manager.json`). Retaining the profit
  defers personal tax entirely. For a company under 법인세법 §60의2①1 (부동산임대업 주업 등; 19 % from the first won,
  §55①2) the gain at 3 AW falls from 14.9M to 13.1M (`results/owner_manager_rental.json`).
- status: confirmed (scenario model; 산재 premium, 성실신고 and advisory costs not modelled)

### F14 Marriage penalty from the household 장려금 test
- kind: loophole-known (structure), amounts from the model
- income tax is individual, but the 장려금 add the spouses' incomes (STA §100의3①2, §100의5③). The filing-unit scanner:
  42 % of couple grid points pay a penalty for marrying; largest 4,080,000 won (couple at 1.25 AW, 85/15 split, two
  children: unmarried, the claimant alone keeps the 자녀장려금). `results/search/unit.md`.
- status: confirmed

### F15 The 2천만원 financial-income threshold costs a basic-rate earner nothing in income tax — it costs NHI premium
- kind: loophole-new (observation; timing)
- an employee at AW with 40M won of dividends in one year and none the next pays exactly the same income and local tax
  over the two years (14,253,440 won) as with 20M + 20M: the §62 comparison makes 종합과세 in the 15 % bracket equal to the
  14 % withholding plus the Gross-up credit. The whole 1,601,640-won difference is the 보수 외 소득월액보험료 on the 20M
  above 2천만원. "Spread dividends to save income tax" is wrong for basic-rate earners; it saves NHI premium.
- status: confirmed (krtax runs; households T40/T20/T0 in PROGRESS.md)

### F16 Low-wage pension floor (model artefact)
- kind: model-fix
- the 기준소득월액 floor (390,000/400,000 won) makes a person with tiny annual wages pay 210,600 won of pension in the
  model (METR 104.7 % at 0 AW). Short-hours workers are not 사업장가입자 (국민연금법 시행령 §2), so this is an artefact of
  annual inputs; stated, not changed.
