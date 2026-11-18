# How Japan writes its income tax

**Layers.** The 所得税法 (1965) holds the permanent rules and tables (別表第五: 1,175 rows of 4,000 yen that *are* the law for
salaries under 6.6 M yen). Each spring one act amends it and the 租税特別措置法, the overlay for everything temporary or
special: the 2025 基礎控除 is 580,000 in 第86条 plus 370,000 / 300,000 / 100,000 / 50,000 in 措置法第41条の16の2 for 2025–26
only; the flat 20.315 % on investment income and the new 22.5 % floor above 330 M yen are 措置法 too. Cabinet orders define
terms; ministerial notices publish the withholding table and a computer formula; NTA booklets add roundings the acts omit.
The 2.1 % 復興特別所得税 is a separate act with its own rounding. The 10 % 住民税 (地方税法, on last year's income) has its own
deduction amounts (基礎控除 430,000, not 580,000), a 2007 調整控除 table bridging the two, exemptions in 附則 and ward
ordinances, and a national 森林環境税 collected with it. Social-insurance grades sit in other acts, one completed by a
cabinet order.

**Change.** e-Gov lists 10 revisions of the 所得税法 taking effect in 2025 (8 in 2024, 9 in 2026) and 15 of the 措置法. Each
year's reform takes effect on **1 December of the year it governs** (2025-12-01; 2026-12-01 for the 740,000-yen minimum of
2026): the text in force for eleven months is not the text that computes the tax, and the pre-reform withholding tables are
settled in the December 年末調整.

**Executable specification?** None for the annual tax. The 告示 formula covers monthly withholding only (and was pre-reform in
2025); the NTA's Excel sheet and e-Tax site are calculators. The model proves the NTA's printed table equals the statute's,
and the combined withholding table equals the statute's × 102.1 % in all 1,960 cells.

**Hard to formalise.** Choosing the text (FINDINGS F1); steps written as arithmetic ("lowered to 50,000 k − 30,000",
第83条の2); roundings spread over four sources; the 住民税's dead, sex-dependent and missing 調整控除 rows (F2–F4); choices left
to households (who claims a child, how dividends are taxed); walls that live in three bodies of law at once (F5).

**I would change.** Define each threshold once (580,000 yen is written into at least five provisions; the 調整控除 row kept the
old figure); write steps as tables; make 別表第五 and 第28条第3項 agree (the OECD uses the formula); start reforms on 1 January.

**Counts.** About 85 provisions in 11 acts and orders. Lean: 2,162 hand-written lines in 16 files + 1,674 lines of
machine-extracted statute tables; about 120 tax parameters and 170 social-insurance grade values. 162 theorems: 42 for all
inputs, 47 kernel-checked facts about named figures, 73 checks of statute-table chunks. 173,000 random households agree with an
independent NTA-procedure calculator on every field.
