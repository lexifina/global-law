# Round 7: joined certificates, a stronger reader, queued reading, scope, dates, same-case history

13 Nov 2026 22:37 – 14 Nov 00:10. Contract and decisions: `DESIGN7.md` (D7-1 … D7-12). Log: `LOG.md`. Freeze:
`FREEZE.md` (variant `v3`, 127 file hashes). Sealed runs: `SEALED_LOG.md`. Nothing installed in `data/` or `out/`;
the round-4/5/6 outputs are reproduced byte for byte by the round-7 Lean when the new tables are absent. Nothing
committed. All reading and auditing by local Claude sub-agents (about 110 agents); no external model.

## What was built

- **Lean** (`LEAN7.md`): one joined certificate (`joined.tsv`: a row's own quote + 1–2 further quotes of the same text,
  each hash/window/part/disqualifier-checked, with a checked relation: `antecedent` = names the target ≤ 300 chars
  before an act with an anaphor; `doctrineTie` = the rejected doctrine's label in both quotes and a tie cue); doctrine
  rows (claim `doctrine`, always demoted: at most `unknown:partialScope`, table-level uniqueness of the label);
  history claims `orderHead` (head-matter Supreme Court orders ≥ 2013, order-list cue, ≤ 400 chars) and `setAside`.
  Theorems 183 → 220 (22 stated before proving + 15 helpers; 0 earlier statements changed), mutants 40 → 53 (all
  killed, guarded diagonal), `audit.py check` green, no `sorry` / new axiom / `native_decide`. Regressions a/a2/b/c
  byte-identical; fixture `fixtures/joined` green.
- **Python reference** extended from DESIGN7 alone: 267 round-6 universes 0 disagreements; real `v3`: every round-7
  row agrees (the 2 remaining differences are the New Jersey witness rows known since round 5).
- **Fuzz/universe generator** extended (`agents/ref/make_r7.py`, 18 kept universes + sweeps; 1,061 expectations).
- **Scorers**: `score_fresh7.py` (two date views), `score7.sh`, `heldout/score_heldout.py` (time split),
  `freeze7.py`, `score_sealed7.sh`, `shep_sealed7.py`.

## Classes, blind audits (Wilson 95%; decoys in every run) and decisions

| class | rows | audit | installed |
|---|---|---|---|
| A2 operative words, part | 906 | 79/80 = 0.988 [0.932, 0.998] | yes |
| A2 operative words, whole | 30 | 10/30 = 0.333 | no |
| B1 recognised, newly read | 317 | 80/80 [0.954, 1] | yes |
| A1(i) overruling across two sentences (joined) | 489 | 79/80 = 0.988 [0.932, 0.998]; extent 76/80 | yes |
| A1(i)/B2 one-sentence acts found by the same scan | 574 | 78/80 = 0.975 [0.913, 0.993] | yes |
| … naming only in the window (plain) | 63 | 54/63 = 0.857 [0.750, 0.923] | no |
| … weak verbs ("no longer good law") | 179 | 36/80 = 0.450 | no |
| A1(ii) doctrine targets (partly negative only) | 19 (17 admitted by Lean) | 19/19 [0.832, 1] | yes |
| B2 scope → whole (from the sentence) | 56 | 54/56 extent = 0.964 [0.879, 0.990]; control 38/40 | yes |
| A1(iii)/B4(c) head-matter SC orders | 8,166 (GVR 110) | 67/80 = 0.838; GVR 67/80 = 0.838 | no |
| B4(a) R3 sole litigation decision (zone/hm/body) | 253 | first 71/80 (all R3); fresh re-audit without nozone/fn 76/80 = 0.950 | yes (288 rows of nozone/fn/modal left out) |
| B4(a) weak types passing R3 + modal judgment line | 297 | 73/80 = 0.912 [0.830, 0.957] | yes |
| B4(e) re-pointed shared-page citations | 208 | 72/80 = 0.900 [0.815, 0.949] | yes (at the bar) |
| B4(b) en banc act + grant orders | 748 | link+effect 79/80 = 0.988 | yes |
| B4(b) en banc silent | 55 | 54/55 | yes |
| B4(b) docket + date linked rehearing | 240 | link+effect 79/80 (link+kind 74/80) | yes |
| B4(d) "set aside" | 97 | link+effect 96/97 = 0.990 (link+kind 80/97) | yes |

## Scores before (round-6 frozen `final2`) → after (`v3`)

| measure | before | after |
|---|---|---|
| Fresh lists, open/dev half (165): lenient | 108 = 65.5% | 111 = 67.3% [59.8, 74.0] |
| … strict, model timeline | 50 = 30.3% | 51 = 30.9% [24.4, 38.3] |
| … strict, "as attributed today" | 80 = 48.5% | 81 = 49.1% [41.6, 56.6] |
| **Fresh lists, sealed half (127), third use: lenient** | 77 = 60.6% | **77 = 60.6% [51.9, 68.7]** |
| … strict, model / attributed | 32 = 25.2% / – | 32 = 25.2% / 57 = 44.9% [36.5, 53.6] |
| Held-out notes, also stated by a court with power (2,640) | 940 = 35.6% (round 5: 932) | 1,038 = 39.3% [37.5, 41.2] |
| Held-out notes, holdout speakers only (6,734) | 425 = 6.3% (round 5: 370) | 574 = 8.5% [7.9, 9.2] (own-words rows only; see LOG 00:04) |
| Shepardized dev: NEG strict (254) | 105 = 41.3% | 140 = 55.1% [49.0, 61.1] |
| **Shepardized sealed (252), second use: NEG strict** | 104 = 41.3% | **120 = 47.6% [41.5, 53.8]** |
| Shepardized precision dev / sealed | 94.6% / 92.0% | 140/149 = 94.0% / 120/130 = 92.3% |
| En banc different, dev / sealed | 3/27 / 0/33 | 14/27 / 6/33 |
| Panel withdrawn, dev / sealed | 5/27 / 3/25 | 9/27 / 5/25 |
| SC reversed, dev / sealed | 67/129 / 73/132 | 87/129 / 79/132 |
| CLEAN kept clean, dev / sealed | 9,698 / 9,579 | 9,695 / 9,577 |
| **New time split (SC merits judgments 2021+, 256 pairs), first use**: reversed found | 14/83 | 21/83 = 25.3% [17.2, 35.6] |
| … vacated found | 9/47 | 13/47 = 27.7% [16.9, 41.8] |
| … precision of rows on key orders | 39/42 | 60/65 = 92.3% |
| SCDB / CRS with recognised rows (burned, non-blind) | 175/278 / 195/292 | 178/278 / 198/292 |
| Leak check | exit 0 | exit 0 |

Dev and sealed did not move alike on the fresh lists (+3 vs 0 lenient) and moved in the same direction but less
on Shepardized (+35 vs +16). Nothing was re-tuned after the sealed runs.

## Not installed, cut, open

- Not installed: operative whole (0.33), antecedent window-plain (0.86), weak verbs (0.45), head-matter orders
  (0.84; the caption-only links fail), R3 nozone/fn/modal (re-audit showed the rest at 0.95).
- Cut: B1 P2/P3 reading (2,811 + 647 statements on pairs that already have an admitted row: they can add at most a
  second row) and T1F shards S007–S015 (1,800 loose Supreme Court items; 0 positives in the 650 read); the round-3
  own-act queue (20,443 items, 246 packs; needs a port); the behaviour test on v3; the base-row contradiction rule
  (436 pairs, proposal in `agents/b4sc/NOTES.md`).
- certify7 admitted 2 doctrine rows that Lean and the reference refuse (`joinedRelation`); the checker decides.
- `score_sealed7.sh` was edited after the freeze to call `shep_sealed7.py` (compare.py refused on round 6's Lean
  hashes); `freeze7.py --check` now reports that one script as changed. Logged in `SEALED_LOG.md`.
- The `heldout` agent's first scans walked `round5/gold_fresh/sealed/` before an exclusion was added (nothing printed
  or kept); recorded in LOG 23:17.
