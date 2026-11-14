# Round 10: a state-court review linker, FJC caption-tied rulings, SCDB court-as-actor anchors, Shadow Docket full-name links, the remand bridge and a trial-judgment bridge in Lean, a new held-out key (Federal Circuit)

14 Nov 2026 03:42 – 05:05. Contract and decisions: `DESIGN10.md` (D10-1 … D10-15). Log: `LOG.md`. Freeze:
`FREEZE.md` (variant `v10d`, 210 file hashes, 05:02). Sealed runs: `SEALED_LOG.md` (one run, 05:02). Nothing installed
in `data/` or `out/`; `round9/out/v9c` and `round8/out/v8e` are reproduced byte for byte by the round-10 Lean when the
round-10 tables and claims are absent. Nothing committed. All reading and auditing by local Claude sub-agents (10
track agents and their opus reader/auditor sub-agents); no external model.

## What was built

- **Lean** (`LEAN10.md`, agent `lean10`): §4 remand bridge (optional `history_remand.tsv`, 12 columns after D10-5 /
  D10-7: the remand decision B's court, date window, a docket token found in B's text AND the target's text, a remand
  cue, and a tie to the order — the order's citation key, its printed date, or the reason case named in both the
  order and B); §6 trial-judgment bridge (claim `trialBridge` + optional `history_tbridge.tsv`). Theorems 272 → 292
  (20 added, 0 changed, 0 removed), mutants 74 → 83 (each killed; diagonals guarded), `#guard`s 441 → 548, `audit.py
  check` green, no `sorry` / new axiom / `native_decide` (added theorems use propext, Quot.sound, Classical.choice);
  regressions a/a2/b/c byte-identical; `round9/out/v9c` and `round8/out/v8e` reproduced byte for byte. Binary
  e7e32592. One slip: at 04:22 a §6 patch script meant for a scratch copy wrote into the real Lean tree while the §4
  gates ran (the gates read only the WSL mirror; all gates were re-run on the final binary).
- **Python reference** (agent `ref10`, from DESIGN10 only, never the Lean): §4 and §6. Real data: **0 disagreements
  in every table** on v10b (§4 binary), v10c and v10d (final binary): v10d status 530,366 keys, certs 495,754, findings
  326,335, classes 37,448; remand rows 316 checked, 0 failed. Synthetic: 9 kept + 40 sweep universes and the 543
  earlier ones; the only disagreements are round 9's known witness-row class (the frozen round-9 binary shows them too).
  §6 is tested on universes only (no claimed row is installed).
- **Infrastructure** (`infra10`): certify10 (+ claims port), stage10 (hard links; adds part zones for new rows'
  nodes, rebuilt v9c's 209,669 nodes byte-identically), `wsl/r10_run.sh` (base mirror by hard links, 0 bytes; two
  slots; df guard), score10, clean10 + KEEP.txt, audit10 (decoy pools + round-9 audits), freeze10, score_sealed10,
  live page section 98 + "Round 10" row.
- **New held-out key** (`bench10`, isolated; never scored before the freeze): `benchmarks/fedcir_dataset` — Federal
  Circuit Dataset Project (Rantanen, Harvard Dataverse doi:10.7910/DVN/UQ2SF7 v9.0, CC0): Federal Circuit dispositions
  of district courts, Court of Federal Claims, Court of International Trade and CAVC decisions. 7,161 items, 1,811
  linked, 1,724 units (1,298 cited; h0 852 / h1 872).

## Classes, blind audits (Wilson 95%; two opus auditors per pack; decoys in every run) and decisions

| class (agent) | rows | audit ("right") | installed |
|---|---|---|---|
| Syllabus re-cut RO, treatments (syl10) | 3 | r10y02 3/3 [0.439, 1] | yes |
| Syllabus re-cut RO, history | 9 | r10y01 6/9 = 0.667 [0.354, 0.879] | no; RO-strict (the 6 read right) declined under D9-11 |
| SCDB a10: anchor extended back to the sentence naming the court below as actor (scdb10) | 75 | r10b01 70/75 = 0.933 [0.853, 0.971] | yes |
| SCDB a10t (same test on nozone / footnote R3 rows) | 86 | r10b02 70/80 = 0.875 [0.785, 0.931] | no |
| SCDB a10n (citation under another case name) | 81 | r10b03 66/80 = 0.825 [0.727, 0.893] | no |
| SCDB s10 scope (each court's judgment its own verb → scope all) | 9 (replace) | r10b04 9/9 [0.701, 1] | yes |
| Shadow C6: GVR order → the unique decision below with both caption sides and the full printed name (shadow10) | 126 | r10k01 77/80 = 0.963 [0.895, 0.987] | yes |
| Shadow C2 (without the full name) | 107 | r10k02 50/80 = 0.625 [0.515, 0.723] | no |
| Shadow C9 (C6 with widened candidates) | 57 | r10k03 40/57 = 0.702 [0.573, 0.805] | no |
| Shadow remand-bridge evidence (§4 lines on round-8/9 GVR rows) | 316 lines | Lean check 316/316 | yes (evidence only) |
| State review linker s1: F1/W ported to courts of last resort reviewing intermediate decisions (stlink10) | 1,014 | r10t01 74/80 = 0.925 [0.846, 0.965] | yes |
| State g2: round-6 guard words exempted when they describe the decision under review | 1,648 | r10t02 76/80 = 0.950 [0.878, 0.980] | yes |
| State D: judgment lines naming the intermediate court where round 6 read no disposition | 34 | r10t06 34/34 [0.898, 1] | yes |
| State T / T4: judgment names only the trial court, T affirmed (needs §6) | 322 / 245 | r10t03 0.762; r10t04 68/80 = 0.850 [0.756, 0.912] (link+effect 0.925) | no (D10-11) |
| State U: uncited intermediate decision named only by court | 1,343 | r10t05 59/80 = 0.738 [0.632, 0.821] | no |
| FJC N form h + rule P: district caption tied by the appeal's head-matter caption (fjc10b) | 1,317 | r10f13 73/80 = 0.912 [0.830, 0.957] (fresh sample after P) | yes |
| FJC N form h without P | 1,374 | r10f11 71/80 = 0.887 [0.800, 0.940] | no |
| FJC N forms x+s (docket / judge / date ties alone) | 1,486 | r10f12 57/80 = 0.713 [0.605, 0.800] | no |

## Scores: round-9 `v9c` → round-10 `v10d`

Round-8 keys (h0 = tuning half; **h1 = scored a third time, after the freeze**):

| key | h0 v9c → v10d | h1 v9c (round 9) → v10d (**third use**) |
|---|---|---|
| FJC appeals, recall | 1,564/2,832 = 55.2% → 1,595 = 56.3% [54.5, 58.1] | 1,601/2,864 = 55.9% → **1,632 = 57.0% [55.2, 58.8]** |
| … precision / clean | 90.4% / 97.6% → 90.5% / 97.5% | 89.2% / 97.1% → 89.4% / 97.1% |
| Shadow Docket, recall | 475/1,059 = 44.9% → 514 = 48.5% [45.5, 51.5] | 508/1,093 = 46.5% → **530 = 48.5% [45.5, 51.5]** |
| … precision / clean | 91.5% / 99.9% → 92.0% / 99.9% | 92.7% / 99.9% → 92.8% / 99.9% |
| SCDB disposition, recall | 1,808/2,407 = 75.1% → 1,826 = 75.9% [74.1, 77.5] | 1,812/2,400 = 75.5% → **1,827 = 76.1% [74.4, 77.8]** |
| … precision / clean | 97.5% / 97.4% → 97.5% / 97.4% | 97.2% / 97.1% → 97.2% / 97.1% |
| State tables, recall | 18/132 = 13.6% → 18 | 11/142 = 7.7% → **11 = 7.7%** |

Round-9 keys (**second use**; both halves; v9c figures from round 9):

| key | v9c | v10d |
|---|---|---|
| Brace & Hall (state court of last resort reversing the decision below), recall all (h0 / h1) | 835/1,670 = 50.0% [47.6, 52.4] (452/868, 383/802) | **924/1,670 = 55.3% [52.9, 57.7]** (500/868 = 57.6%, 424/802 = 52.9%) |
| … precision / clean / part | 93.1% / 1,207/1,253 = 96.3% / 35.8% | 924/987 = 93.6% / 1,198/1,253 = 95.6% / 164/399 = 41.1% |
| Songer TREAT, recall all (h0 / h1) | 94/228 = 41.2% [35.0, 47.7] (43, 51) | **101/228 = 44.3% [38.0, 50.8]** (48/111, 53/117) |
| … precision / clean | 96.9% / 581/583 | 97.1% / 580/583 |

New key (**first use**, both halves untouched; v9c and v10d scored together after the freeze):

| key | v9c | v10d |
|---|---|---|
| Federal Circuit dispositions (fedcir_dataset), recall cited, all (h0 / h1) | 158/300 = 52.7% [47.0, 58.2] (86/150, 72/150) | **158/300 = 52.7%** (unchanged) |
| … precision / clean / part | 89.8% / 735/742 = 99.1% / 122/256 = 47.7% | 89.8% / 99.1% / 124/256 = 48.4% |

Existing keys:

| measure | v9c | v10d |
|---|---|---|
| Fresh lists dev (165): lenient / strict model / strict attributed | 112 / 52 / 82 | 112 / 52 / 82 |
| **Fresh lists sealed (127), sixth use (burned)**: lenient / strict / attributed | 76 / 31 / 56 | **77 / 32 / 57** |
| Held-out notes, also stated by a court with power (2,640), neg or partly | 1,068 = 40.5% | 1,068 = 40.5% |
| Held-out notes, holdout speakers only (6,734), neg or partly | 660 = 9.8% | 666 = 9.9% |
| Held-out notes, history | 5,033/6,121 = 82.2% | 5,204/6,305 = 82.5% |
| Shepardized dev NEG strict (254) / precision / CLEAN | 145 = 57.1% / 93.5% / 9,694 | 146 = 57.5% / 93.6% / 9,694 |
| **Shepardized sealed (252), fifth use (burned)** NEG strict / precision | 125 = 49.6% / 92.6% | **128 = 50.8% [44.7, 56.9] / 92.8%** |
| Old lists (burned): SCDB explicit / with recognised; CRS / with recognised | 144 / 177; 164 / 198 | 146 / 178; 167 / 199 |
| Leak check | exit 0 | exit 0 |

**Reading the numbers.** Every h0 gain replicates on h1 (FJC +1.1 / +1.1 points, Shadow +3.6 / +2.0, SCDB +0.8 /
+0.6). Brace & Hall, built blind to the new state linker and used only once before, moves +5.3 points (+89 cases;
h0 +5.5, h1 +5.1) with precision up (93.1 → 93.6%) and clean down 9 cases (96.3 → 95.6%, the linker's audited error
rate). Songer moves +3.1 (the FJC rule N generalises). The new Federal Circuit key does not move: no round-10 rule
targets the Federal Circuit (its linkers work on regional circuits and state courts), so it is a fresh baseline
(52.7% recall, 89.8% precision). The round-9 syllabus losses on the burned lists are recovered (fresh sealed 76 → 77,
old lists +2/+1/+3/+1). Nothing was re-tuned after the sealed run.

## Not installed, cut, open

- Not installed: syllabus RO history (0.667) and RO-strict (D9-11), SCDB a10t (0.875) / a10n (0.825), Shadow C2
  (0.625) / C9 (0.702), state T4 (0.850 right, 0.925 link+effect; D10-11) and U (0.738), FJC form h without P (0.887)
  and forms x+s (0.713).
- Move 6 (state tables implicit misses) skipped (D10-4).
- Data gap (Shadow Docket): 281 h0 NEG orders not in the corpus (order lists 2006–09, 2020–25).
- §6 (trial bridge) is in the Lean but no claimed row is installed; tested on universes only.
- fjc10 went silent at 03:54 (its corpus run died; stopped by the coordinator at 04:44); fjc10b resumed from its files
  and delivered N/h+P by 04:57.
- Protocol notes: the new key's folder name was visible in `LOG.md`, which track agents read; shadow10, stlink10 and
  ref10 each said they opened nothing about it (no track touches the Federal Circuit). Disk: C: varied 20–27 GB (other
  sessions' writes); every variant but `v10d` was deleted after scoring.

## Plateau analysis (h1 / blind recall, points per round; v9c → v10d for round 10)

| key | r7 | r8 | r9 | r10 | now | remaining headroom (estimate) and why |
|---|---|---|---|---|---|---|
| FJC appeals (h1) | 0.0 | +4.1 | +1.2 | +1.1 | 57.0% | ~15–20 pts to a ~75% ceiling: of 30 disagreements read, 4 source errors, 3 link errors, 3 mapping artefacts; the rest are identity problems (named-other-case, one-side captions, guards) that now yield ~30 h0 cases per audited class. Diminishing, not maxed. |
| Shadow Docket (h1) | +0.5 | +23.0 | +7.5 | +2.0 | 48.5% | Ceiling ~73% with this corpus: 26.5% of h0 NEG orders are not in the corpus (data, not rules). ~260 in-corpus misses left (no remand decision, unparsed 2005 lists, different-party captions). Rules near plateau; a data fix (order lists 2006–09, 2020–25) is the big lever. |
| SCDB disposition (h1) | +9.5 | +3.6 | +0.1 | +0.6 | 76.1% | ~10 pts to a ~85–88% ceiling: 5 of 30 disagreements are SCDB coding errors; misses left are other-target (rehearing/en banc), no shared caption, no disposition read. Plateaued for this rule family. |
| State tables (h1) | +1.4 | +0.7 | 0.0 | 0.0 | 7.7% | Maxed for phrase rules: 10 of 30 disagreements are the tables' own errors; the rest are implicit/doctrinal rejections in 19th-century reporters (needs a holding-level reader, principle limit). |
| Brace & Hall (all) | – | – | 0.0 | +5.3 | 55.3% | Large: in the corpus, ~4,800–5,000 real misses among cited pairs before round 10, s1+g2 cover ~55%; left: ~9,500 uncited court-named-only opinions (~half under review; needs docket/full-name identity — U failed on same-surname cases), trial-judgment reversals (T4, 245 rows at 0.85), petition orders. |
| Songer (all) | – | – | +5.2 | +3.1 | 44.3% | Follows FJC; small n (228). |
| Federal Circuit (all) | – | – | – | 0.0 | 52.7% | Untargeted so far; open. |

**Is "maxed out" near?** For the Supreme Court keys (SCDB, the burned lists) and the state overruling tables: yes —
gains of ≤ 1 point per round for three rounds; the rest is source error, data absence or implicit reasoning. For FJC
and Shadow Docket: diminishing (1–2 points per round), with real headroom blocked by identity of the ruling under
review and by data gaps. For state review (Brace & Hall) and the Federal Circuit: not near — round 10 was the first
round aimed at state review and gave the round's largest blind gain.

## Decisions for the user

1. FJC N/h+P installed although FJC h0 clean drops 3 of 6,229 (precision rises); B&H clean drops 9 of 1,253 with the
   state linker — both within the audited error rates (D10-15, D10-11). Keep?
2. State T4 (§6 trial bridge, 245 rows): 0.850 on "right" (kind exact), 0.925 on link+effect (12 errors are
   reversed-vs-vacated, same status). Install on the link+effect measure, or keep the "right" bar (current)?
3. Syllabus RO-strict (6 history rows, each read right by both auditors, but the cut followed the audit): left out
   under D9-11. Keep the rule strict?
4. Shadow Docket's largest remaining gap is data (order lists 2006–09, 2020–25): add them to the corpus?
5. Carried from round 9: New Jersey court attribution (1,607 decisions), Songer/Shepardized overlap.

## Next moves, ranked (value / effort)

1. **State review, uncited opinions** (~9,500 opinions; ~half truly under review): link by docket + full party names
   + date (C6-style), fresh audit; then T4 under a decision on the measure. Tune on corpus text; B&H tests at the end.
2. **Federal Circuit**: port the FJC linker (F1/W/J/N) to Federal Circuit review of district courts, Claims and CIT
   — diagnosed on corpus text only (the new key stays held out).
3. **Shadow Docket data**: add the missing order lists (data, not rules), then the existing rules apply.
4. **FJC** forms x+s with a second identity tie (caption + docket), and a cut on consolidated/multi-defendant scope.
5. SCDB other-target misses (rehearing / en banc vs panel) — small.
