# Japanese 2025 taxes in Lean — results (18 November 2026)

Model `lean/` (JpTax, exe `jptax`): 所得税 + 復興特別所得税 (令和7年分), 住民税 on 2025 income (令和8年度, Tokyo 23 wards),
employee social insurance for calendar 2025 (協会けんぽ 東京), 児童手当 2025. Findings F1–F15 in `FINDINGS.md`.
Build: `cd lean && lake build` (Lean 4.35, core only); every theorem kernel-checked, no `sorry`, no
`native_decide`; axioms only propext / Classical.choice / Quot.sound (`#print axioms` in Theorems.lean and Walls.lean).

## 1. Official tables and worked examples (kernel-checked `decide`)

| # | Benchmark | Source | Result |
|---|---|---|---|
| 1 | 別表第五 (給与所得控除後の給与等の金額), every row × every yen, 1,900,000–6,600,000 | 所得税法 別表第五, e-Gov XML (1,175 rows, machine-extracted) | 1,175 / 1,175 rows (`beppyo5_eq_table`) |
| 2 | The NTA's printed copy of the same table | 年末調整のしかた 令和7年分 pp.47–54 | identical to the statute on 1,175 / 1,175 rows (script) |
| 3 | 年末調整のしかた worked figures: p.36 (7,654,321 → 5,788,888), p.37 (26,544; max 150,000), p.38 (172,100), p.55 速算表 (11 points), p.55 配偶者控除・特別控除 一覧表 (33 cells + 20 salary limits + 5 claimant limits), p.56 基礎控除 (17 points), 特定親族特別控除 (32 points), 扶養控除等 (9), p.4 所得要件 (4) | NTA, 令和7年分 年末調整のしかた | all equal (`Tests.lean`, 18 theorems, ~170 figures) |
| 4 | The booklet's 設例 (p.57–58): 給与 8,970,000 → 7,020,000; 調整控除 47,000; 6,973,000; 控除合計 4,786,102; 課税 2,186,000; 121,100; 44,600; 年調年税額 45,500 | NTA p.57–58 | 8 / 8 (`nc_p57_example`) |
| 5 | タックスアンサー No.2260 (7,000,000 → 974,000; 復興 20,454), No.1600 (公的年金 65+, 3,500,000 → 2,350,000) | NTA | 3 / 3 |
| 6 | 協会けんぽ 東京 令和7年度 保険料額表 (rates, 折半額 rounding note ①, grade boundaries), MHLW 雇用保険料率 R6/R7 | kyoukaikenpo.or.jp xlsx; mhlw.go.jp | all equal (`kk_r7_tokyo`, `kk_grades`, `mh_koyo`) |
| 7 | 月額表: NTA combined table = statute 別表第二 × 102.1 % rounded to 10 yen | 所得税法 別表第二 (e-Gov) and 令和7年分 源泉徴収税額表 (NTA) | 1,960 / 1,960 cells (`gessaku_combined_all`) |
| 8 | 月額表 vs the 告示 formula (電算機計算の特例, 令和7年分) at each row's midpoint | 平成24年財務省告示第116号 (令和5年改正), NTA p.18 | within 70 yen in 1,960 / 1,960 cells; equal in 1,586 (`gessaku_denshi_within_70`) |

## 2. Referee A — independent calculator from the NTA's procedure (`referee/nta_referee.py`)
Written from the NTA booklet's printed tables (not the statute text), the 協会けんぽ xlsx (not the statute's grades), the
MHLW and こども家庭庁 pages. Random contract households (`referee/gen_households.py`: 1–2 adults aged 20–79, wages from 0 to 60,000,000 including
every threshold ±1 yen, pensions for those over 60, 0–4 children aged 0–22, working children with wages; the full and rich
profiles add every other contract field). Comparison: `referee/compare_full.py`; log `runs/all_run.log`.

| profile (seeds) | households | 所得税 | 復興 | 住民税 | social | 児童手当 |
|---|---|---|---|---|---|---|
| wage (1–7): wages, pensions, children with wages | 63,000 | all equal | all equal | all equal | all equal | all equal |
| full (11–15, 99): + self-employment and losses, rental, interest, dividends (both regimes), gains, gifts, iDeCo | 60,000 | all equal | all equal | all equal | all equal | all equal |
| rich (21–23): the same up to billions; 9,302 households pay the 措置法第41条の19 floor | 30,000 | all equal | all equal | all equal | all equal | all equal |
| full (31) and rich (41) with all regimes (確定申告不要 / 総合課税 / 申告分離 dividends; withheld / declared gains) | 20,000 | all equal | all equal | all equal | all equal | all equal |
| **total** | **173,000** | **173,000** | **173,000** | **173,000** | **173,000** | **173,000** |

One correction to the model came out of these runs (FINDINGS L1: the 住民税 配当控除 is now computed exactly; it had been
rounded to hundredths of a yen, 2 households in 70,000 ended 100 yen apart). The table is after the correction.

Limits: referee A shares the author's reading of the statute where no NTA table exists (住民税, dependants' allocation); it
checks transcription and arithmetic, not interpretation. Referees B and C are independent of the author.

## 3. Referee B — OpenFisca-Japan v2.2.0 (`referee/ofjp_compare.py`)
Married couples and single adults (unmarried couples skipped), 3 seeds, 20,770 households, 33,319 adults.

| field | as is (seed 2, 14,446 adults) | like for like (OpenFisca fed the model's 合計所得金額 and 社会保険料控除) |
|---|---|---|
| 合計所得金額 | 3,473 equal (2020 給与所得控除, no 別表第五, float32) | 13,905 (the rest: float32 rounding above 16.7 M) |
| 基礎控除 | 13,156 | 14,436 (10: float32 at 23.5 M / 25 M) |
| 配偶者控除 / 特別控除 | 13,650 / 13,688 | 14,369 / 14,369 (77: 48万 threshold) |
| 扶養控除 | 14,111 | 14,328 (118: 48万 threshold, claimant) |
| ひとり親控除 | 14,404 | 14,422 (24: child-income test) |
| 社会保険料控除 | 0 (national rates, no grades, 国民年金 imputed) | 14,446 (input) |
| 住民税所得割 | 3,882 | 3,731; the 10,715 others: household 調整控除 7,919, truncations 2,188, 非課税 405, deductions 203 |
| 住民税均等割 | 10,555 | 10,555; the 3,891 others: OpenFisca has no 均等割 exemption |
| 児童手当 | **9,047 / 9,047** | **9,047 / 9,047** |
Over the three seeds every difference is classified; OpenFisca-Japan has no 所得税 at all. Findings F14 (a)–(h).

## 4. Referee C — OECD Taxing Wages 2026, Japan, tax year 2025 (`lean/JpTax/Oecd.lean`, `refs/oecd/tw_cou_2025.csv`)
Same salary and the OECD's own employee contribution (14.7 %) as the 社会保険料控除:

| household | OECD taxable / 所得税 / with 復興 | model | difference and cause |
|---|---|---|---|
| single, 167 % AW (9,524,074) | 5,751,000 / 722,700 / 737,800 | 5,751,000 / 722,700 / 737,800 | **exact** |
| single, 100 % AW (5,703,038) | 2,604,000 / 162,900 / 166,300 | 2,601,000 / 162,600 / 166,000 | OECD uses 第28条第3項's formula, not 別表第五 |
| single, 67 % AW (3,821,035) | 1,175,000 / 58,750 / 59,900 | 1,174,000 / 58,700 / — | same |
| couple + 2 children, 100 % AW + 0 | 2,224,000 / 124,900 / 127,500 | 2,221,000 / 124,600 / 127,200 | same |
| single parent + 2 children, 67 % AW | 1,175,000 / 58,750 (HFTA 0) | 824,000 / 41,200 | OECD omits the ひとり親控除 (所得税法第81条) |
住民税 (SLT 286,900 at AW): reproduced once the OECD's single rounding of the two 所得割 and its exclusion of the 1,000-yen
森林環境税 are applied. The OECD figures are not used to change the model; in each difference the statute decides.

## 5. Properties proved for all inputs (42 theorems; 162 theorems in all)
第89条: monotone, 5 %–45 % per 1,000-yen step, exact on 1,000-yen bases, ≤ 45 %, the 速算表 equals the bracket sum for every
amount (`tax89c_eq_quick`); 給与所得 monotone (table and formula), never above the formula, at most one row's step below it,
equal to every row of 別表第五 (`beppyo5_eq_table`), the 4,000-yen steps (`beppyo5_step`); 給与所得 after the 所得金額調整控除
monotone (`kyuyoAdj_mono`); income tax monotone in the salary for fixed deductions (`salaryTax_mono`); 基礎控除 antitone;
spouse deductions antitone in the claimant's income; the 配偶者特別控除 formula is the 5万-step table; the 児童手当 table of
第6条 equals the birth-order rule for every family (`teateTable_eq_rank`); 調整控除 row (7) is dead (`chosei_row7_dead`); the
top combined marginal rate is exactly 55.945 % (`top_marginal_rate`); the spouse deductions are flat at 380,000 up to a
spouse income of 950,000 (`spouseDeduction_flat`), a student's at 630,000 up to 850,000 (`studentDeduction_flat`), and a
16–18-year-old's fall from 380,000 to nothing at 580,001 (`highschool_cliff`).

## 6. The walls (`Walls.lean`, 13 theorems on whole households; scan in `runs/walls.txt`)
103万 and 123万 (spouse): gone (+1 yen). 106万: −154,945. 110万: −4,999. 123万 for a child of 16–18: −71,797; for a student
19–22: −499. 150万 / 188万 (student): −1,020 / −6,062. 160万+ (spouse): −2,041, −7,104, −10,104 per step. 合計所得 132万:
−2,930. Single mother at 2,044,000: −31,999. Every 標準報酬 grade: about −9,000 to −28,000 (income tax falls while net falls:
`incomeTax_not_monotone`). Top rate on a whole household: 11,189 yen per 20,000 (`top_rate_household`). Dividend regimes for
a retiree: 406,300 / 336,288 / 143,500 yen (`dividend_regimes_retiree`).

## 7. Speed
`jptax`: 10,000 households in 0.8 s on one core (about 80 µs each, JSON included).
