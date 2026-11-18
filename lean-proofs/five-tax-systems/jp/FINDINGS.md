# Japanese individual taxes, 令和7年分 (2025), in Lean — findings

Model: `lean/JpTax` (exe `jptax`), written from 所得税法, 租税特別措置法, 復興財源確保法, 地方税法, 森林環境税法, 児童手当法,
健康保険法, 厚生年金保険法 and 労働保険徴収法 as served by the e-Gov 法令API v2 at the as-of date that governs each tax
(`law/*.info.json` names every revision). Referees: A = an independent Python calculator written from the NTA's year-end
adjustment booklet and printed tables (`referee/nta_referee.py`); B = OpenFisca-Japan v2.2.0 (project-inclusive, Aug 2026);
C = OECD Taxing Wages 2026 (tax year 2025, SDMX API). Each finding: what the law says, what the other side does, who is
affected, the evidence, who is right and on what authority. Theorem names refer to `lean/JpTax/*.lean`.

## F1. The 2025 reform governs the whole year but took effect on 1 December 2025
- 所得税法等の一部を改正する法律 (令和7年法律第13号, promulgated 2025-03-31) changed 第28条第3項 (給与所得控除 minimum
  550,000 → 650,000 yen), 第86条 (基礎控除 480,000 → 580,000), 第2条第1項第33号・第34号 (同一生計配偶者 / 扶養親族
  48万 → 58万) and created 第84条の2 (特定親族特別控除). e-Gov's revision history (`law/shotoku_revisions.json`) dates
  these texts from **2025-12-01** (revision 340AC0000000033_20251201_507AC0000000013); the text in force from January to
  November 2025 still has 550,000 / 480,000 (`law/shotokuzeiho_2025-11-30.xml`). 措置法第41条の16の2 (the 2025–2026
  addition of 370,000 / 300,000 / 100,000 / 50,000 yen to the 基礎控除) is absent from the 2025-11-21 text and present on
  2025-12-31.
- The monthly withholding instruments were not changed for 2025: the NTA's 「令和7年分 源泉徴収税額表」 says "令和2年1月以後
  「税額」は改正されていません", and the 告示 formula (平成24年財務省告示第116号, 令和5年改正) still deducts 40,000 yen a
  month (480,000 a year) of 基礎控除 and 31,667 yen per dependant (theorem `denshi_prereform`). The reform reached employees
  through the December 年末調整 (NTA, 年末調整のしかた 令和7年分 p.7: "改正前の源泉徴収税額表等によって源泉徴収した税額との
  精算も行うこととなります").
- It recurs: the 令和8年度 reform (令和8年法律第12号) raises the minimum 給与所得控除 to 740,000 yen for 令和8年分・令和9年分 with
  effect from **2026-12-01** (タックスアンサー No.1410, read 2026-11-18; e-Gov lists that revision as not yet in force), and
  from 2027 cuts 復興特別所得税 to 1.1 % beside a new 1 % 防衛特別所得税 (No.2260).
- Consequence for anyone formalising "the law of 2025": the statute text in force on most days of 2025 is not the text that
  computes the 2025 tax. The model uses the text in force on 2025-12-31 for 所得税 and the 令和8年度 text (as of 2026-06-01)
  for the 住民税 on 2025 income.

## F2. 調整控除 row (7) of 地方税法第37条 / 第314条の6 cannot apply from 令和8年度 (dead text)
- The table of 人的控除額の差 has a row (7) for a 配偶者特別控除 spouse "前年の合計所得金額が五十五万円未満である者に限る"
  (50,000 yen; 30,000 from 500,000 yen). Since the 令和7年 amendment a spouse with 580,000 yen or less is a 同一生計配偶者
  (第292条第1項第7号), so the 配偶者特別控除 needs more than 580,000 yen (第314条の2第1項第10号の2): no spouse satisfies both.
  Proved for every income: `chosei_row7_dead`.
- History: the row was written in 2007 for the bracket just above the then 380,000-yen threshold (40万円 / 45万円), moved by
  +100,000 in 令和2年 (50万円 / 55万円), and was not moved again when the threshold became 580,000.
- Effect: a claimant whose spouse earns just above the new threshold (580,001–650,000, the position the row served before)
  gets no row-(7) amount: up to 2,500 yen less 調整控除 (50,000 × 5 %) than the analogous family under the 2024 text.
  Confidence high that the row is unreachable; moderate that it is an omission rather than a choice.

## F3. The 住民税 調整控除 still depends on a single parent's sex
- Since 2020 the ひとり親控除 is sex-neutral (所得税法第81条: 350,000; 地方税法第314条の2第1項第8号の2: 300,000). But the
  調整控除 table gives "(3) 寡婦又はひとり親で政令で定めるもの 1万円" and "(4) ひとり親で政令で定めるもの 5万円", and the cabinet
  order fills them by sex: "ひとり親のうち父である者" → (3), "ひとり親のうち母である者" → (4) (地方税法施行令第7条の16の2,
  第48条の7の2). A single father with taxable income up to 2,000,000 yen pays 2,000 yen more 住民税 than an identical
  single mother. The model asks for the sex (`jpSingleParentSex`, default "F"); OpenFisca-Japan models it too.

## F4. The new 特定親族特別控除 has no row in the 調整控除 table: a 500-yen wall at 1,230,000 yen for students
- Above a salary of 1,230,000 yen a 19–22-year-old's parent's 特定扶養控除 (630,000; 住民税 450,000) becomes a 特定親族特別控除
  of the same amounts (第84条の2第1項第1号; 地方税法第314条の2第1項第12号イ): the reform removed the student wall. But the
  調整控除 table has a row for a 特定扶養親族 (180,000) and none for a 特定親族, so the parent's 調整控除 falls:
  `wall_123_student` (net −499 yen for one more yen of the child's pay).

## F5. The walls that remain in 2025 (each proved on a whole household in `Walls.lean`)
| wall | who | net income for one more yen | cause | theorem |
|---|---|---|---|---|
| 103万 | spouse | +1 (gone) | 同一生計配偶者 up to 1,230,000 | `wall_103_gone` |
| 123万 | spouse | +1 (gone) | 配偶者控除 380,000 → 配偶者特別控除 380,000 | `wall_123_spouse_gone` |
| 106万 | any earner at a large employer | −154,945 | employee insurance from 88,000 yen a month (健康保険法第3条第1項第9号ロ) | `wall_106` |
| 110万 | single earner | −4,999 | 均等割 + 森林環境税 above 合計所得金額 450,000 (第295条第3項, 施行令第47条の3) | `wall_110` |
| 123万 | child aged 16–18 | −71,797 | parent loses 扶養控除 380,000 / 330,000; no 特定親族特別控除 below 19 | `wall_123_highschool` |
| 123万 | student aged 19–22 | −499 | F4 | `wall_123_student` |
| 150万 | student | −1,020 | 特定親族特別控除 630,000 → 610,000 | `wall_150_student` |
| 188万 | student | −6,062 | 30,000 → 0 | `wall_188_student` |
| 160万, 165万, 170万 … | spouse | −2,041, −7,104, −10,104 … | 配偶者特別控除 steps per 50,000 of the spouse's income | `wall_160_spouse` |
| 合計所得 132万 | spouse's own tax | −2,930 per 1,000 yen at 2,004,000 | spouse's own 基礎控除 950,000 → 880,000 | `notch_132` |
| 合計所得 135万 | single mother, salary 2,044,000 | −31,999 | 住民税 exemption of 第295条第1項第2号 ends | `wall_single_parent_135` |
| 標準報酬 grades | every insured employee | −9,000 to −28,000 at each grade (−14,721 at 2,340,000) | contributions jump a grade | `incomeTax_not_monotone` |

For every income, not only these households: the spouse deductions total 380,000 yen for any spouse income up to 950,000
(`spouseDeduction_flat`), a 19–22-year-old's 630,000 up to 850,000 (`studentDeduction_flat`), and a 16–18-year-old's 380,000
falls to nothing at 580,001 (`highschool_cliff`).

The "130万の壁" (loss of 被扶養者 status, then 国民年金 + 国民健康保険) applies to part-timers at small employers; the model
assumes a large employer, where the wall is at 106万. The scan (`runs/walls.txt`: salaries 0–3,000,000 yen in 1,000-yen
steps plus every threshold ±1) finds 28 falling steps for the second earner of a couple and 22 for a single person.

## F6. The income tax is not monotone in pay once social insurance is counted
- For fixed deductions the income tax is non-decreasing in the salary (`salaryTax_mono`, for every salary: 4,000-yen rows,
  所得金額調整控除 and the shrinking 基礎控除 included). But the 社会保険料控除 moves in steps with the 標準報酬月額: at
  2,340,000 yen a year (195,000 a month) health insurance and 厚生年金 both move from the 190,000 to the 200,000 grade; the
  employee pays 16,937 yen more, the income tax falls by 700 yen and net income by 14,721 yen (`incomeTax_not_monotone`).

## F7. 別表第五: the statute's table is a closed form, and its rows are notches
- 第28条第4項 makes the table, not the formula of 第28条第3項, the law below 6,600,000 yen. Each of its 1,175 rows (1,900,000
  to 6,600,000 yen, 4,000 yen wide) gives the 第3項 result at the row's lower end; proved for every published row and every
  yen in it (`beppyo5_eq_table`, rows machine-extracted from e-Gov). The table gives at most 2,799 / 3,199 yen less income
  than the formula (`kyuyoShotoku_le_formula`, `formula_sub_table_lt`).
- One more yen at a row boundary adds 2,800 yen of 給与所得 (3,200 from 3,600,000) (`beppyo5_step`); inside a row the
  marginal rate is nil. For a single employee that is a net fall of about 450 yen per boundary (1,903,999 → 1,904,000: −453).
- The NTA's printed table in the 年末調整のしかた (pp.47–54) equals the statute's on all 1,175 rows (`scripts/gessaku_check.py`).

## F8. Steps written as arithmetic
- 第83条の2第1項第1号ロ writes the 配偶者特別控除 steps as "380,000 less the spouse's income above 930,001 yen, lowered to a
  number of the form 50,000 k − 30,000"; 第84条の2第1項第2号 writes the 特定親族特別控除 steps as "630,000 less twice the
  income above 840,001, lowered to 100,000 k − 80,000". Proved to be the NTA's tables (`tokubetsuBase_table`,
  `tokubetsuBase_steps`, `tokuteiShinzoku_steps`, `nc_p55_spouse_table`, `nc_p56_tokutei_shinzoku`).

## F9. Withholding: three official instruments, all pre-reform in 2025
- The NTA's combined 月額表 (所得税 + 復興特別所得税) equals the statute's 別表第二 (所得税 only) × 102.1 % rounded to 10 yen in
  all 245 × 8 甲欄 cells from 88,000 to 740,000 yen (`gessaku_combined_all`): the statutory table is not used as printed.
- The 告示 formula (電算機計算の特例) at each row's midpoint is within 70 yen of the table in every cell and equal in 1,586 of
  1,960 (`gessaku_denshi_within_70`; up to 320 yen apart at row ends). Both are lawful alternatives.

## F10. A statute table that is wrong without its cabinet order
- 厚生年金保険法第20条第1項 lists 31 grades up to 620,000 yen; 令和2年政令第246号 第1条 adds "第三二級 六五〇、〇〇〇円" from
  September 2020 under 第20条第2項. Read alone, the act undercharges every employee paid 635,000 yen a month or more by
  2,745 yen a month. The model follows the order (`kk_grades`).

## F11. 措置法第41条の19 (new from 2025): a 22.5 % floor above 330,000,000 yen
- Additional 所得税 = max(0, 22.5 % × (基準所得金額 − 330,000,000) − 基準所得税額); the 基準所得金額 includes listed-share
  dividends and gains even when left to withholding (第2項第2号・第7号). A salary of 30,000,000 with 2,000,000,000 yen of
  listed-share gains: +74,374,450 yen, so the 所得税 is exactly 22.5 % of the excess (382,061,250 yen).

## F12. The exact top rate
- Above 40,000,000 yen of taxable income: 45 % × 1.021 + 10 % = 55.945 % (`top_marginal_rate`: every 20,000 yen costs exactly
  11,189 yen; `top_rate_household` on a whole household). Health and pension contributions are capped (1,390,000 / 650,000
  yen a month); 雇用保険 (5.5/1000) is not.

## F13. 所得金額調整控除 goes to both parents; NTA roundings not in the statute
- 措置法第41条の3の11第1項 needs only "年齢二十三歳未満の扶養親族を有する"; タックスアンサー No.1411: "扶養控除と異なり ... その
  夫婦双方が、この控除の適用を受けることができます". The model gives it to every adult over 8,500,000 yen in such a household.
- The 1-yen fraction of 給与所得 above 6,600,000 is cut and that of the 所得金額調整控除 rounded up (年末調整のしかた
  pp.36–37; `nc_p36_kyuyo`, `nc_p37_adjust`): NTA practice, in the taxpayer's favour, followed by the model.

## F14. OpenFisca-Japan v2.2.0 (referee B): no income tax, and 2025 only half applied
Found on 30,000 random households (`runs/big_run.log`); the statute is right in each case.
- (a) **No 所得税 variable**: it models deductions, 住民税 and benefits for eligibility screening; it cannot referee 所得税 or
  復興特別所得税.
- (b) **給与所得控除 of 2020–2024 for 2025** (minimum 550,000; 40 % − 100,000 up to 1,800,000) instead of 第28条第3項 as amended
  (650,000 up to 1,900,000): 合計所得金額 up to 100,000 yen too high. It also uses the formula, not 別表第五 (第28条第4項).
- (c) **48万 thresholds** for 同一生計配偶者 and 扶養親族 (statute 580,000), 配偶者特別控除 from 480,000; no 特定親族特別控除.
  A spouse aged 70+ with 480,001–580,000 yen gets 380,000 instead of the 老人控除対象配偶者's 480,000.
- (d) **float32**: 23,500,001 and 25,000,001 yen are read as 23,500,000 and 25,000,000 and get the 基礎控除 of the bracket
  below (e.g. 160,000 instead of 0).
- (e) **ひとり親 without the child test** of 所得税法施行令第11条の2第2項 ("...の合計額が五十八万円以下の子").
- (f) **Claimant of dependants**: the member with the highest income, children included; 施行令第219条 lets the declarations
  decide and falls back to the largest 総所得金額等. The model restricts claimants to adults (reading R1).
- (g) **住民税**: 均等割 charged to everyone (no 第295条 / 施行令第47条の3 exemption: 3,891 of 14,446 adults); 調整控除 computed on
  the household and given to its top earner, without the 50,000-yen floor of 第37条第2号 / 第314条の6第2号; no truncation of
  the base to 1,000 yen or the 所得割 to 100 yen (第20条の4の2); no 附則第3条の3 exemption or relief.
- (h) **Social insurance**: national-average rates, no 標準報酬月額 grades, 国民年金 imputed to everyone not insured.
- Like for like (OpenFisca fed the model's 合計所得金額 and 社会保険料控除), every remaining 住民税所得割 difference is one of (g)
  or (c): seed 2 — household 調整控除 7,919, truncations 2,188, 非課税 405, deductions 203; the 2 cases the classifier left
  open on seed 3 are a 200-yen truncation and a 調整控除 OpenFisca gave to a child out-earning the parent. 児童手当 agrees on
  every household (20,770 of 20,770, both modes).

## F15. OECD Taxing Wages 2026 (referee C): the formula instead of the table, and no ひとり親控除
- Above 6,600,000 yen the model reproduces the OECD exactly (167 % AW = 9,524,074 yen: taxable 5,751,000, 所得税 722,700,
  with 復興 737,800; `oecd_single_aw167`).
- Below 6,600,000 the OECD applies the formula of 第28条第3項 (WRETA 1,580,607.70 at 100 % AW) where 第28条第4項 makes 別表第五 the
  law: at the average wage taxable income 2,604,000 instead of 2,601,000, 所得税 162,900 instead of 162,600 (`oecd_single_aw100`);
  at 67 % AW 58,750 instead of 58,700 (`oecd_single_aw67`). The statute is right.
- Single parent, two children, 67 % AW: the OECD reports no head-of-family allowance (HFTA 0) and the childless person's tax.
  所得税法第81条 gives a ひとり親 350,000 yen (住民税 300,000): taxable 824,000 and 所得税 41,200 instead of 1,175,000 and 58,750
  (`oecd_single_parent_aw67`). The statute is right; the OECD omits the deduction.
- 住民税: the OECD rounds the two 所得割 together (≤ 100 yen) and leaves out the 森林環境税 (1,000 yen, a national tax collected
  with the 均等割); with those conventions and its 給与所得 its SLT is reproduced (286,900 at AW).

## F16. The dividend regime is the taxpayer's choice, and the default is the dearest at low incomes
- Listed-share dividends may be left to withholding (措置法第8条の5: 20.315 %, final), declared separately (第8条の4: 15 % +
  2.1 % + 5 %, counted in 合計所得金額, with unused 所得控除 set against them: 第8条の4第3項第3号; 地方税法附則第33条の2) or
  taxed with the other income (総合課税, with the 配当控除 of 所得税法第92条 and 地方税法附則第5条). For a retiree aged 70 with
  a 1,500,000-yen pension and 2,000,000 yen of dividends the three cost 406,300, 336,288 and 143,500 yen
  (`dividend_regimes_retiree`). The law leaves the optimisation to the household; since 令和6年度 the 住民税 must follow the
  same choice. The model offers all three (`jpDividends`: "separate" default, "declared", "aggregate"; `jpGains`:
  "withheld" default, "declared").

## R. Readings and conventions (not findings)
- R1. Dependants are claimed by the adult with the larger 総所得金額等 (施行令第219条第2項第2号), the spouse by the higher earner;
  one unmarried adult with a child is a ひとり親; two unmarried adults are a de facto couple.
- R2. 住民税 on 2025 income = the 令和8年度 tax, Tokyo 23 wards, standard rates; 均等割 exemption at the cabinet order's 1級地
  standard (350,000 / 210,000), which the wards' ordinances adopt.
- R3. Social insurance: Tokyo 協会けんぽ, premiums for the 12 months of 2025, 12 equal monthly payments, no bonus, insured from
  88,000 yen a month (large employer); a non-insured spouse under 1,300,000 yen is a 被扶養者.
- R4. 復興特別所得税 per person at 2.1 % cut to the yen; the amount payable (所得税 + 復興, cut to 100 yen, 復興財源確保法第24条
  第2項 / 第30条) is `detail.persons[].nationalPayableRounded100`.
- R5. Dividends default to 確定申告不要 (20.315 %); `jpDividends: "aggregate"` = 総合課税 with 配当控除, `"declared"` = 申告分離課税.
  Interest 源泉分離; listed-share gains in a 特定口座 with withholding, or `jpGains: "declared"`. Deductions left over after the
  総所得金額 come off declared gains first, then declared dividends (the order of the 申告書 第三表; immaterial except for the
  1,000-yen rounding, as both bear the same rates).
- R6. 児童手当: ages on 31 December for the whole year; 0–18 paid; 19–22 counted for the birth order.

## L. Corrections to the Lean model found by the referees
- L1. 住民税 配当控除 (地方税法附則第5条, 1.2 % + 1.6 %) was rounded down to hundredths of a yen, and the relief of 附則第3条の3
  第2項・第5項 floored separately; referee A (exact fractions) found 2 households in 70,000 where the 所得割 ended 100 yen
  higher than the statute's exact arithmetic gives. Now exact (thousandths of a yen, one floor at the end:
  `haitoLocal1000`, `afterRelief`). No other difference between the model and referee A in 173,000 households (wage, full and rich profiles, all dividend
  and gains regimes).

## Not modelled
医療費・生命保険料・地震保険料控除; 障害者・寡婦・勤労学生控除; 住宅借入金等特別控除; 青色申告特別控除; 寄附金 税額控除 (措置法第41条の
18の2・の3) and the 住民税 寄附金税額控除 (ふるさと納税); 国民年金・国民健康保険・後期高齢者医療 premiums; 児童扶養手当; 退職・山林・
一時・譲渡 (other than listed shares) income; foreign tax credits; loss carry-forward; NISA.
