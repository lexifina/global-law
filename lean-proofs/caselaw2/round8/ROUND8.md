# Round 8: the own-act queue, links through later citations, rehearing, multi-case acts, state courts, new keys

14 Nov 2026 00:11 – 02:00. Contract and decisions: `DESIGN8.md` (D8-1 … D8-15). Log: `LOG.md`. Freeze: `FREEZE.md`
(variant `v8e`, 176 file hashes, 01:59). Sealed runs: `SEALED_LOG.md` (one run). Nothing installed in `data/` or
`out/`; `round7/out/v3` is reproduced byte for byte by the round-8 Lean when the round-8 tables and claims are absent.
Nothing committed. All reading and auditing by local Claude sub-agents (15 track agents and over 100 reader/auditor
sub-agents (opus; ownact alone ran 54 readers); no external model.

## What was built

- **Lean** (`LEAN8.md`, agent `lean8`): bridge evidence (`history_bridge.tsv`, DESIGN8 §4: a third text's
  subsequent-history clause "X, cite, cert. denied / vacated …, O's cite" identifies the decision below; ≤ 600 chars,
  no ";", X's citation → cue of the row's kind → no other index key before the cue (5b, D8-9) → first key after the
  cue maps to O; date(W) ≥ date(O)); claim `anchorWide` (wider anchor cues, §5); claim `oldCircuit` (old Fifth / Eighth
  Circuit power over Eleventh / Tenth Circuit district courts before 1981 / 1929, §6). Theorems 220 → 245 (8 stated
  before proving + 17 helpers; 0 earlier statements changed), mutants 53 → 63 (10×10 diagonal), `audit.py check`
  green, no `sorry` / new axiom / `native_decide`; regressions a/a2/b/c byte-identical; fixture `round8/fixtures/bridge`.
- **Python reference** (agent `ref8`, from DESIGN8 alone): kept 9 / probe 20 universes 0 disagreements; 435 earlier
  universes: only the 7 known round-5 witness (W) universes; real `v8e`: only the 2 known New Jersey witness rows and
  one ownact row of the same NJ successor-court class (Lean `noAuthority`, reference ok; the checker decides).
- **Infrastructure** (agent `infra`): `certify8.py`, `stage8.py`, `wsl/r8_run.sh` (frozen v3 checker copy), `score8.sh`,
  the **h0 benchmark shadow** `round8/bench_h0/` (verified to reproduce the published round-4/6 h0 figures exactly),
  `freeze8.py`, `score_sealed8.sh`; audit tooling `round8/audit/` (agent `audit8`, pair form, decoy pools).

## Classes, blind audits (Wilson 95%; two opus auditors per pack; decoys in every run) and decisions

| class (agent) | rows | audit | installed |
|---|---|---|---|
| Round-3 own-act queue, after cut (ownact) | 591 (Lean ok 278) | r8o01 76/80 (weighted 0.854) → cut → fresh r8o02 77/80 = 0.963 [0.895, 0.987] | yes |
| Rehearing grant orders → panel opinion (rehear8 G) | 299 | r8h01 link+kind 76/80 = 0.950 [0.878, 0.980]; link+effect 77/80 | yes |
| Undated docket rehearing acts (rehear8 N) | 368 | r8h02 72/80 = 0.900 [0.815, 0.949]; link+effect 74/80 | yes (D8-6 keeps reinstated) |
| SC orders by bridge, vacated/reversed (orderdock) | 235 of 6,326 | r8k01 79/80 = 0.988 [0.932, 0.998] | yes |
| SC orders by bridge, cert denied / dismissed | 6,091 | r8k03 79/80 = 0.988 [0.932, 0.998] | yes |
| SC order lists, v1 | 565 | r8k02 68/80 = 0.850 | no |
| SC order lists, v2 (caption tie-check, consolidated scope) | 568 | fresh r8k05 80/80 [0.954, 1] | yes |
| Remand-docket links (remandcap) | 32 | r8k04 32/32 [0.893, 1] | yes |
| Multi-case overruling sentences (multicase) | 706 (Lean ok 651) | r8m01 76/80 = 0.950 [0.878, 0.980] | yes |
| State reader repairs R8S (state8) | 151 (Lean ok 132) | r8s01 77/80 = 0.963 [0.895, 0.987] | yes |
| CoA → district decision F1 (fjc8), status-changing | 757 of 2,081 | r8f01 71/80 → fixes → r8f05 73/80 = 0.912 [0.830, 0.957] | yes |
| … F2 one-side captions | 448 | r8f02 62/80 = 0.775 | no |
| … S1 base scope rewrite | 29 | r8f03 24/29 = 0.828 | no |
| … oldCircuit claims on base rows | 183 status-changing | r8f04 63/80 = 0.787 (errors in the old base rows) | no (claims only on F1 rows) |
| SC judgment readings D1–D5 (scdb8) | 84 | r8b01 67/80 = 0.838 | no; D2/D2b modal sub-class 44/48 = 0.917 installed (D8-14, post-hoc split, near census) |
| SC anchors A5 + S6 | 111 | r8b02 72/80 = 0.900 [0.815, 0.949] | yes (at the bar) |
| SC trial court on direct review T1 | 34 | r8b03 32/34 = 0.941 | yes |
| Rehearing-denial re-pointing R4/R5 | 30 | r8b04 29/30 = 0.967 | yes (removes 13 v3 rows) |
| Wide anchor cues W (anchorWide claim) | 110 | r8b05 78/80 = 0.975 [0.913, 0.993] (decoys 16/18) | yes |
| Unresolved-target acts NT8 (notarget) | 51 (Lean ok 39) | r8n01 38/39 = 0.974 [0.868, 0.996] (whole class) | yes |
| Base-row replacement "final judgment line decides" (contradict) | 245 | r8c01 pairs: new right 27/40 = 0.675 | no |
| Doctrine dominance (doctrine8) | ≤ 15 est. | not built (under the 25-row bar) | no |

## Scores: round-7 `v3` → round-8 `v8e`

New keys (h0 = tuning half; **h1 = scored once, after the freeze**):

| key | h0 before → after | h1 before (round-7, benchmarks agent) → after (round 8) |
|---|---|---|
| FJC appeals, recall | 1,418/2,832 = 50.1% → 1,536 = 54.2% [52.4, 56.1] | 1,448/2,864 = 50.6% → **1,566 = 54.7% [52.9, 56.5]** |
| … precision / clean | 90.0% / 97.7% → 90.3% / 97.6% | 88.7% / 97.3% → 89.1% / 97.2% |
| Shadow Docket, recall | 156/1,059 = 14.7% → 412 = 38.9% [36.0, 41.9] | 175/1,093 = 16.0% → **426 = 39.0% [36.1, 41.9]** |
| … precision / clean | 82.5% / 99.9% → 90.3% / 99.9% | 83.3% / 99.9% → 91.4% / 99.9% |
| SCDB disposition, recall | 1,681/2,407 = 69.8% → 1,809 = 75.2% [73.4, 76.8] | 1,723/2,400 = 71.8% → **1,810 = 75.4% [73.7, 77.1]** |
| … precision / clean | 97.5% / 97.6% → 97.5% / 97.4% | 97.2% / 97.3% → 97.2% / 97.1% |
| State tables, recall | 13/132 = 9.8% → 17 = 12.9% [8.2, 19.7] | 10/142 = 7.0% → **11 = 7.7% [4.4, 13.3]** |

Existing keys:

| measure | v3 | v8e |
|---|---|---|
| Fresh lists dev (165): lenient / strict model / strict attributed | 111 / 51 / 81 | 112 / 52 / 82 |
| **Fresh lists sealed (127), fourth use (burned)**: lenient / strict / attributed | 77 / 32 / 57 | **77 / 32 / 57** (unchanged) |
| Held-out notes, also stated by a court with power (2,640), neg or partly | 1,038 = 39.3% | 1,057 = 40.0% |
| Held-out notes, holdout speakers only (6,734), neg or partly | 574 = 8.5% | 655 = 9.7% |
| Shepardized dev NEG strict (254) / precision | 140 = 55.1% / 94.0% | 143 = 56.3% / 93.5% |
| **Shepardized sealed (252), third use (burned)** NEG strict / precision | 120 = 47.6% / 92.3% | **123 = 48.8% [42.7, 55.0] / 92.5%** |
| Shepardized dev / sealed: en banc different, panel withdrawn, SC vacated | 14, 9, 30 / 6, 5, 30 | 16, 10, 31 / 7, 5, 31 |
| Old lists (burned): SCDB / CRS with recognised | 178 / 198 | 178 / 199 |
| Leak check | exit 0 | exit 0 |

**Dev vs sealed.** FJC (+4.1 h0 / +4.1 h1 points), Shadow Docket (+24.2 / +23.0) and SCDB (+5.4 / +3.6) replicate on h1.
The state tables did not: +4 on h0, +1 on h1 (n = 142; the h0 gain came from two list sentences and two repaired
reader rules, which h1 barely contains). Fresh-list sealed is unchanged (dev +1); Shepardized sealed +3 (dev +3).
Nothing was re-tuned after the sealed run. Shadow Docket h0 would read 426 without 31 Booker remand reinstatements
(rehear8 N, right as text; the key's MAPPING lists this as a mapping artefact; D8-6).

## Not installed, cut, open

- Not installed: base-row replacement (27/40), order lists v1, F2, S1, oldCircuit on base rows, SC readings D1/D3/D5,
  doctrine dominance, state8 reporter aliases (no h0 miss needs one), BENCH-3 (three-judge courts as whole court:
  a decisions2 data change, ~30 rows; D8-10), 4 window-only rows (state8, notarget).
- Cut: move 8 (statements on already-covered pairs: adds at most second rows); ownact's 15 "survive" packs (0/160 yes)
  and 9,787 items with no powered candidate; the bridge "own page" mode (circular, D8-7).
- `calpart` (old-California header "…, J., delivered the opinion / C. J., concurring" labels the court's opinion as a
  concurrence; 607 decisions with candidate sentences; the Lean checks a row's part as a field, not against the text)
  wrote nothing after 01:11 and did not report before the freeze; nothing of it is staged.
- `score_sealed8.sh` logged empty lines for the fresh and Shepardized runs (grep patterns); the figures were added to
  `SEALED_LOG.md` from the same run's output files. The benchmarks scorers wrote `benchmarks/<key>/results/round8.*`.

## Next moves, ranked (value / effort)

1. **FJC misses where the citation sentence does not name the court** (405 of 1,414 h0 misses) and the round-6
   earlier/later/interlocutory guards misfiring on federal procedural-history narrative (8 of 33 read): a guard
   exception + anchor widening, audited. Largest remaining same-case pool.
2. **SCDB**: "judgment line not read" (131) and decision below cited without an accepted anchor (160); fix D1/D3/D5
   (denial-of-rehearing citation inside the sentence; sole/latest test) and re-audit fresh; hyphenated "re- versed".
3. **Part map** (calpart's finding): header "concurring" notes opening a false separate opinion; and make the Lean
   check a row's part against the text's zone table (today a row field).
4. **Shadow Docket**: post-2013 head-matter GVRs with no "Reported below" and no history string (docket bridges via
   the court below's remand opinions, 931 found but too weak alone: 21/26); 281 h0 orders not in the corpus (data gap).
5. **State tables**: the remaining gap is implicit overruling (97 of 154 h0 pairs: no act sentence near X) — an
   implicit-overruling reader class with its own audit; plus the joined gap > 300 chars (notarget's 3,914 far items;
   a Lean change) and the doctrine own-tie rule (doctrine8: ~57 rows, needs per-court label uniqueness).
6. New Jersey successor-court authority (the one reference/Lean difference class, since round 5): settle the rule.
