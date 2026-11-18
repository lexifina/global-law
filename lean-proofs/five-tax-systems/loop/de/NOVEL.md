# Germany VZ 2025: bounded novel search

Scripts: `novel.py` (N1-N3), `analyse.py` (cause attribution by switching one feature off), `n2_clean.py` (clean grid
for N2). Raw output: `runs/novel_n1.json`, `runs/novel_n2.json`, `runs/novel.log`. CPU used: about 25 CPU-minutes
(16 processes; the exe runs ~40 000 households/s). Classification: **novel** (not found documented), **known**
(documented: statute, FINDINGS, the comparison or literature), **artefact** (rounding or model assumption, not a planning
lever).

## N1. Net income falling with one more euro of gross (1-euro grids)

952 scans, 4,7 million households: married second earner 0-40 000 € against seven primary incomes (0-300 000 €),
0-3 children, second earner aged 40 or 66, with and without 9 % church tax; single earners 0-300 000 € (0-3 children,
aged 40/66/68, church tax or not); pensioners (pension 4 000-48 000 €, single or married, church tax or not) with
dividends 0-60 000 €.

**Results.** Net income falls by more than 5 € for one more euro of gross only at the Minijob limit (6 672 → 6 673 €:
88 married and 6 single profiles; worst −2 630 € for a second earner married to 300 000 € with church tax; −1 509 € at
the average wage in the comparison). **Known** (the comparison's cliffs, `../../compare/charts/cliffs_summary.json`; § 8 (1) Nr. 1 SGB IV, § 40a (2) EStG).

All other one-euro drops (3,04 million of 4,7 million steps) are 0,01-1,73 €: the tariff tax moves in whole euros
(§ 32a (1) Satz 6; one euro of zvE costs 0 or 1 €, FINDINGS S1 `est_step`), and **2 € at a time for couples** (§ 32a (5)
doubles the rounded tax on the halved, rounded-down income, so the joint tax steps by 0 or 2 € every euro: 45 499
drops of 1,5-2 €), plus cent-rounded contributions and Soli. **Artefact** of the statute's rounding; over any 100 €
the rate is far below 100 %.

Highest 100-euro marginal burden away from the Minijob limit: **68,4 %** for a second earner in the Übergangsbereich
(18 900-21 400 € a year) married to a 150 000 € earner with 9 % church tax (63-66 % without church tax or at
300 000 €): 42 % × (1 + 5,5 % + 9 %) of the joint marginal tax on the part not offset by deductible contributions, plus
the employee contribution rising faster than the wage in the Übergangsbereich (SGB IV § 20 (2a): from 0 at 556 € to the
full 21,55 % at 2 000 €/month). **Known** (the second-earner wall is in the comparison,
`../../compare/charts/walls_second_earner.json.gz`; the Übergangsbereich slope is by design of § 20 (2a)); it is not above 100 %.

Pensioners with dividends: no drop above 1 € (the § 32d (6) switch is continuous because it takes the minimum of the
two ways, FINDINGS S7). No marginal rate above 100 % from Soli Freigrenze, Kindergeld flips, § 32d (6), church tax
or § 24a found beyond whole-euro rounding.

## N2. Joint assessment more expensive than individual assessment by more than the 2 € tariff bound (FINDINGS S3)

320 000 random couples (rich in capital income, pensioners, losses), each with and without church tax: joint
burden > individual burden + 2 € in **45 963 of 640 000** runs (7,2 %; the draw is far richer in capital income than
Germany's population).

Attribution (`analyse.py` on the first 3 000 hits by switching one feature off; decomposition of all 45 963 hits by the
component that differs most):

| Cause | hits (largest component) | largest saving from § 26a | classification |
|---|---|---|---|
| Soli Freigrenze/Milderungszone per spouse (SolZG § 3 (3), § 4) | 29 035 (15 932 with identical income tax) | 1 509 € | known |
| § 32d (6) Satz 3: option only for all capital income of both spouses | 14 886 (income tax) | 4 529 € | known rule, little-documented lever |
| Kindergeld/Freibetrag Günstigerprüfung per parent (§ 31, § 32 (6) halves) | 1 352 | 764 € | known in principle |
| Church tax follows the above | 690 | | — |
| § 10b cap per spouse, § 24a | 55 | 237 € | known |

**Soli per spouse — clean example** (wages only, no children, no church): 250 000 € + 90 000 € wages. Income tax is
the same both ways (106 728 €; both spouses' zvE, 232 733 € and 73 346 €, lie in the linear 42 % zone, so splitting
gains nothing), but jointly the whole tax bears the full 5,5 % Soli (joint tax far above 74 190 €), while individually
the 90 000 € spouse's tax (19 893 €) stays under the 19 950 € Freigrenze: Soli 5 870,04 € vs 4 775,92 €, **1 094 €
saved by Einzelveranlagung**. The saving is at most 5,5 % of 19 950 € ≈ 1 097 € plus Milderungszone effects (largest
seen 1 509 € with capital income). Documented: Haufe, Frotscher/Geurts EStG § 26 Rz. 56 ("Durch die Rückführung des
Solidaritätszuschlags ... ist ein erhöhter Grenzsteuersatz entstanden, der bei der Zusammenveranlagung zu einem
Steuernachteil führen kann") and an ELSTER forum thread. **Known**; this search gives its size and where it applies
(both spouses in zone 4, one spouse's own tax ≤ about 37 000 €).

Residual: in a few mixed cases the tariff tax differs by up to ~70 € because the model's Vorsorgeaufwendungen per spouse
(§ 10 (3)/(4) caps under § 26a) differ slightly from the joint sum; not investigated further (model-internal).

**Clean example** (`n2_clean.py`, 39 600 grid couples, all 8 008 hits vanish with `--no-32d6`): one spouse 17 500 €
wages, the other none, 105 000 € dividends owned half each, no church tax, both 40. Jointly the couple must choose
the Abgeltungsteuer or the tariff for *all* capital income (§ 32d (6) Satz 3: "Bei zusammenveranlagten Ehegatten kann
der Antrag nur für sämtliche Kapitalerträge beider Ehegatten gestellt werden"): the flat 25 % wins, and 8 000 € of the
joint Grundfreibetrag is wasted. Assessed individually (§ 26a), the spouse without wages puts her 52 500 € into the
tariff (about 22 % average), the other keeps the flat rate: **2 237 € less** (individual assessment loses no splitting
advantage worth mentioning here because the wage is small). With church tax and a 20 000 € rental loss (absorbed by
the tariff-assessed spouse instead of wasting the joint Grundfreibetrag): up to **4 529 €** (35 000 € wages,
120 000 € dividends, both 70).

* Cause: § 32d (6) Satz 3 (all-or-nothing option for jointly assessed spouses) × § 26a (each spouse decides alone)
  × § 2 (5b) (capital income at the flat rate does not absorb losses or use the Grundfreibetrag).
* Documented? The Satz 3 rule is statute; one search (see sources in the final report) found no guidance that
  recommends Einzelveranlagung for this, while commentary (Haufe on § 26) says § 26a only wins when "allowances are used
  once under joint assessment but fully by each spouse". **Classification: known rule, little-documented
  Gestaltung — novel as a quantified planning lever** (caveat: it needs capital income split between the spouses,
  which the model assumes and couples can arrange by ownership).

## N3. Child-by-child vs all-together Günstigerprüfung

In the same 640 000 runs the child-by-child rule (§ 31, WD 4-3000-065/24) never cost more than the all-together
comparison (0 cases > 0,50 €). Reason: taking, child by child, the larger of Kindergeld and the Freibetrag saving is
at least the all-Kindergeld and at least the all-Freibetrag result. **Known/confirming** (FINDINGS G7, O1).

## L29 (also a search). Progressionsvorbehalt and Einzelveranlagung

Six couples with one spouse on Elterngeld (§ 32b (1) Nr. 1 j): individual assessment wins in 2 (by 122 € and 337 €:
balanced low incomes, where joint assessment lets the Elterngeld raise the rate on both incomes) and loses in 4 (by up
to 3 573 €). **Known** (Steuerratgeber advice: test § 26a when one spouse had Lohnersatzleistungen).

## 2026 tariff: the candidate jump at 69 878 € (first seen in a separate experiment, not published here)

**Confirmed in the formula, immaterial after rounding.** EStG § 32a (1) Satz 2 for VZ 2026 (gesetze-im-internet.de,
fetched 2026-11-18): zone 3 "von 17 800 Euro bis 69 878 Euro: (173,10 • z + 2 397) • z +
1 034,87", zone 4 "von 69 879 Euro bis 277 825 Euro: 0,42 • x – 11 135,63": the coefficients are exactly those of
`DeTax.t2026`. At 69 878 € the zone-3 formula gives 18 213,0630 €; the zone-4 line there would give 18 213,13 €:
the line starts **+6,70 cent above** the end of zone 3 (2025: −9,41 cent at 68 480 €, FINDINGS S1). So the
unrounded tax rises by 48,70 cent from 69 878 € to 69 879 €, above the 45 % top rate. Satz 6 ("auf den nächsten vollen
Euro-Betrag abzurunden") absorbs it: 18 213 € on both sides; over 0-400 000 € every one-euro step of the rounded 2026
tax is 0 € or 1 € (239 471 and 160 530 steps). Lean: `jump2026_gap`, `jump2026_step`, `jump2026_step_gt_top`,
`jump2026_rounded`, `jump2026_local_steps` in `lean/LoopDe/Loopholes.lean`. The zone-2/3 boundary at 17 799 € has a −0,20 cent gap (2025: +0,16 cent). Classification: **real feature
of the statute text, not exploitable** (no taxpayer pays more than 1 € per euro anywhere); not found documented.
