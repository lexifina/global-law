# How the German income tax is written

**A formula in the statute.** § 32a (1) EStG prints no brackets: five formulas with cent coefficients, e.g. for 2025
"(176,64 • z + 2 397) • z + 1 015,13" with "z ... ein Zehntausendstel des 17 443 Euro übersteigenden Teils", the income
rounded down to the euro (Satz 1) and the tax rounded down (Satz 6). The marginal rate rises linearly from 14 % to
42 % (`N_step_z2`, `N_step_z3`); the rounded coefficients leave the formula 9,41 cent short at 68 480 € (`boundaries`),
and splitting's two roundings can cost a couple 1 € (`splitting_costs_one_euro`).

**Executable pseudo-code from the ministry.** For withholding the BMF publishes each year the PAP as a flow chart and as
XML pseudo-code (Java BigDecimal), plus a calculator interface "für die automatisierte, maschinelle Prüfung" of other
programs — because, in its own words, the decimal rules "lassen ... oft Spielraum für unterschiedliche
Interpretationen". Its tariff routine is exactly § 32a (`uptab25_eq_est`); its class V/VI routine is not quite
(`pap_class5_cents`). For the assessment itself (§ 2: Einkünfte → Gesamtbetrag → Einkommen → zvE) there is only prose.

**Parameters every year.** The BMF's Datensammlung lists 34 tariffs since 1958 and a new one every year from 2013 to
2026, driven by the government's reports on the tax-free subsistence minimum and on "kalte Progression"; 2024's was
changed retroactively in December 2024 (BGBl. 2024 I Nr. 386), 2025's and 2026's were set together (BGBl. 2024 I
Nr. 449). The PAP had three versions for 2024 and two for 2025 (22.11.2024, 22.1.2025). Contributions take four more
instruments a year (Rechengrößen-VO, PV-Beitragssatz-VO, RV Bekanntmachung, average Zusatzbeitrag) and the Midijob
factor F; Kindergeld went from 255 € (2025) to 259 € (2026).

**Hard or ambiguous.** Today's text only on gesetze-im-internet.de (2025's came from an archive); the Midijob formulas
are images in the official XML; definitions by reference (the Soli base is a hypothetical second assessment; § 2 (5b)
silently removes 25 %-taxed capital income from "Einkünfte" — GETTSIM missed it); the child-by-child order of the
Kindergeld test is administrative practice, not statute; § 24a's table is keyed by "das auf die Vollendung des
64. Lebensjahres folgende Kalenderjahr" (GETTSIM is one year off); decisions taken on rounded taxes flip 29 times
around the Kindergeld crossover, and the BMF prints the last flip as "dauerhaft günstiger" (`kg_permanent_joint`).

**What I would change.** Integer arithmetic with one stated rounding and continuous coefficients; "2 × T(⌊X/2⌋)" in so
many words; the comparison order in § 31; a direct Soli base; formulas as text; a dated text per year; and an official
pseudo-code for the assessment, as there already is for withholding.

**Counts.** About 50 provisions (EStG §§ 2, 9a, 10, 10b, 10c, 20 (9), 22 Nr. 1, 24a, 24b, 26b, 31, 32, 32a, 32d, 39b,
51a, 66; SolZG §§ 3, 4; SGB III, IV, V, VI, XI on contributions; four 2025 instruments). 2 262 lines of Lean (model
and exe 938, PAP 234, theorems 894, tests 196). Parameters for 2025: 13 tariff coefficients, about 40 amounts and rates,
three 54-row tables. 70 theorems, no `sorry`.
