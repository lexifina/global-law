# Round 9: Shadow Docket remand links, FJC wide and judge-form anchors, part zones in Lean, state far joins and implicit rejections, New Jersey successor courts, two new fresh held-out keys

14 Nov 2026 02:04 – 03:40. Contract and decisions: `DESIGN9.md` (D9-1 … D9-13). Log: `LOG.md`. Freeze: `FREEZE.md`
(variant `v9c`, 190 file hashes; re-written once at 03:36, see "Incidents"). Sealed runs: `SEALED_LOG.md` (one run).
Nothing installed in `data/` or `out/`; `round8/out/v8e` is reproduced byte for byte by the round-9 Lean when the
round-9 tables and claims are absent. Nothing committed. All reading and auditing by local Claude sub-agents (11 track
agents, about 90 opus reader/auditor sub-agents); no external model.

## What was built

- **Lean** (`LEAN9.md`, agent `lean9`): part zones (§4: optional `part_zone.tsv`; a row's main and joined quotes must
  lie inside one zone of the row's part, in the text owner's offsets), far joined antecedents (§5, claim `joinedFar`,
  gap ≤ 1,200, no other index key in the gap, a covering window), implicit rejection at-risk only (§7, claim
  `implicitReject`, soft kinds only), judge-form anchor cues under `anchorWide` (§8), New Jersey successor authority
  (§6: data rows; theorems `adoptedSameTier_power` / `adopted_lowerTier_noPower` over the existing adoption rule).
  Theorems 245 → 272 (27 additions, 0 changed, 0 removed), mutants 63 → 74 (each killed; 3×3 and 8×8 diagonals),
  `audit.py check` green, no `sorry` / new axiom / `native_decide`; regressions a/a2/b/c byte-identical;
  `round8/out/v8e` reproduced byte for byte. Binary 22bab5cd. One process slip: §8's code was drafted three minutes
  before its statements were written in LEAN9.md (no statement changed after the build).
- **Python reference** (agent `ref9`, from DESIGN9 only): §4–§8. **Real-data differential v9a, v9b, v9c: 0
  disagreements in every table** (v9c: status 526,350 keys, findings 321,152, certs 491,540, classes 37,448). The New
  Jersey class open since round 5 is closed. Synthetic universes: one class surfaced (a non-ok row whose quote fails its
  zone: Lean drops its findings, reference kept them) — ruled for the Lean (D9-13), reference aligned (7432cbed).
  Final differential (runner 22bab5cd): kept 9, sweep 20, probe 10, fuzz 10, 534 earlier universes — every round-9
  rule agrees in every universe; the only differences are the known round-5 witness-class W rows (date-0 target; one
  universe each in kept/main/probe/fuzz, the 12 known W universes in the 534). The 534 are byte-identical to the
  stored round-8 reference output when no round-9 table is present. Details `agents/ref9/NOTES2.md`.
- **Infrastructure** (`infra9`): `certify9.py`, `stage9.py` (+ `--table NAME=FILE` for non-row tables), `wsl/r9_run.sh`
  (two run slots machine-wide), `score9.sh`, `freeze9.py`, `score_sealed9.sh` (log lines from the scorers' own files:
  round 8's empty-line bug fixed), `round9/audit/`, live page row + section 97.
- **Two new fresh held-out keys** (dataset agents `bench_bh`, `bench_songer`, isolated; MAPPING.md before linking;
  50/50 hash halves; never scored before the freeze): `benchmarks/brace_hall_state` (Brace & Hall State Supreme Court
  Data, 1995–98, CC0: state courts of last resort reversing/affirming intermediate appellate decisions; 3,322 units)
  and `benchmarks/songer_treat` (Songer Courts of Appeals Database + Kuersten–Haire update, `PRIORPUB`-linked district
  decisions; FJC-key overlaps excluded; 1,544 units).

## Classes, blind audits (Wilson 95%; two opus auditors per pack; decoys in every run) and decisions

| class (agent) | rows | audit | installed |
|---|---|---|---|
| Shadow Docket: GVR order + caption-tied decision below + remand decision on the same docket tied to the order (shadow9) | 335 | r9k01 79/80 = 0.988 [0.932, 0.998] (corpus-weighted 0.964); r9k02 (8 rows the revision adds) 8/8 | yes |
| FJC W: anchor widened to the court named up to 4,000 chars back in the same part (fjc9) | 199 (86 status-changing) | r9f02 72/80 = 0.900 [0.815, 0.949] | yes (at the bar) |
| FJC J: judge-form anchors "district / magistrate / trial judge" (§8) | 444 (176 status-changing) | r9f04 72/80 = 0.900 [0.815, 0.949], corpus-weighted 0.917 | yes (at the bar) |
| FJC G: guard exception for the decision under review's own narrative | 218 | r9f01 65/80 = 0.812 [0.713, 0.883] | no |
| FJC G2: G minus two exemptions + partial-scope rule | 180 | r9f03 67/80 = 0.838 [0.742, 0.902] | no |
| SCDB judgment readings (dfix / j / multi9) (scdb9) | 46 | r9b01 whole class 26/30 = 0.867 [0.703, 0.947] | no (D9-11: the cut that fixes it was designed on this audit's errors; no fresh sample left) |
| SCDB a9 / r4w / wfix | 4 (+1 base row removed) | r9b02 4/4 [0.510, 1] | yes |
| Part map PJ / PJ-V (header vote and index notes are not separate opinions) (calpart9) | 52,178 decisions' maps | 40/40 changed decisions read right [0.912, 1] | yes (feeds zones) |
| … PJT treatments rescued from separate-opinion rejects | 23 | r9p01 23/23 [0.857, 1] | yes |
| … PJR rehearing rows on re-scanned decisions | 14 | r9p03 13/14 = 0.929 [0.685, 0.987]; link+effect 14/14 | yes |
| … PJH below_other rows on re-scanned decisions | 36 | r9p02 26/36 = 0.722 [0.560, 0.842] | no |
| … re-cut of quotes that straddled head matter and opinion; perCuriam relabels | 137 + 14 | not separately audited (same conclusions as the replaced audited v8e rows) | yes |
| State A v1: implicit rejection, at-risk only (state9) | 36 | r9s02 25/36 = 0.694 [0.531, 0.820] | no |
| State A v2 (no "no longer" family; intervening-cause filter), fresh sample | 72 | r9s03 72/72 = 1.000 [0.949, 1] on "the court itself rejects/departs from X"; 28 rows understate the act (at-risk only) | yes (at-risk only, D9-12) |
| State B: far joined antecedents (`joinedFar`) | 52 | r9s01 52/52 = 1.000 [0.931, 1] (pack 1 re-read by a fresh pair: 26/26; the same 2 decoy labels contested by all 4 readers) | yes (49 admitted, 3 noAuthority) |
| State C: doctrine own-tie | 14/69 read yes → 3 new pairs | – | not built (below 25 rows) |
| New Jersey successor courts (nj9: 1947 Const. art. XI §IV; *In re Estate of Johnson*, 240 N.J. Super. 134; *Hagaman*, 112 N.J. Super. 221; *Collopy*, 27 N.J. 29; *Gruschow*, 56 N.J. Super. 146) | 2 adoption rows + 3 retags | data rule; 3 v8e rows change, as predicted | yes (D9-6) |
| Part zones in the Lean (§4) | 585,526 zones / 209,669 nodes | refuses 72 admitted quotes (63 head-matter-only straddles, 9 syllabus quotes) | yes |

## Scores: round-8 `v8e` → round-9 `v9c`

Round-8 keys (h0 = tuning half; **h1 = scored a second time, after the freeze — second use**):

| key | h0 v8e → v9c | h1 v8e (round 8) → v9c (**second use**) |
|---|---|---|
| FJC appeals, recall | 1,536/2,832 = 54.2% → 1,564 = 55.2% [53.4, 57.0] | 1,566/2,864 = 54.7% → **1,601 = 55.9% [54.1, 57.7]** |
| … precision / clean | 90.3% / 97.6% → 90.4% / 97.6% | 89.1% / 97.2% → 89.2% / 97.1% |
| Shadow Docket, recall | 412/1,059 = 38.9% → 475 = 44.9% [41.9, 47.9] | 426/1,093 = 39.0% → **508 = 46.5% [43.5, 49.4]** |
| … precision / clean | 90.3% / 99.9% → 91.5% / 99.9% | 91.4% / 99.9% → 92.7% / 99.9% |
| SCDB disposition, recall | 1,809/2,407 = 75.2% → 1,808 = 75.1% | 1,810/2,400 = 75.4% → **1,812 = 75.5% [73.7, 77.2]** |
| … precision / clean | 97.5% / 97.4% → 97.5% / 97.4% | 97.2% / 97.1% → 97.2% / 97.1% |
| State tables, recall | 17/132 = 12.9% → 18 = 13.6% [8.8, 20.5] | 11/142 = 7.7% → **11 = 7.7% [4.4, 13.3]** |

**New fresh held-out keys (first and only use; both halves untouched; v8e and v9c scored together after the freeze):**

| key | v8e | v9c |
|---|---|---|
| Songer TREAT (CoA reversing/vacating a district decision), recall, all (h0 / h1) | 82/228 = 36.0% [30.0, 42.4] (36/111, 46/117) | **94/228 = 41.2% [35.0, 47.7]** (43/111, 51/117) |
| … precision / clean | 96.5% / 581/583 | 96.9% / 581/583 |
| Brace & Hall (state supreme court reversing an intermediate appellate decision), recall, all (h0 / h1) | 835/1,670 = 50.0% [47.6, 52.4] (452/868, 383/802) | **835/1,670 = 50.0%** (unchanged) |
| … precision / clean | 93.1% / 1,207/1,253 = 96.3% | unchanged |

Existing keys:

| measure | v8e | v9c |
|---|---|---|
| Fresh lists dev (165): lenient / strict model / strict attributed | 112 / 52 / 82 | 112 / 52 / 82 |
| **Fresh lists sealed (127), fifth use (burned)**: lenient / strict / attributed | 77 / 32 / 57 | **76 / 31 / 56** |
| Held-out notes, also stated by a court with power (2,640), neg or partly | 1,057 = 40.0% | 1,068 = 40.5% |
| Held-out notes, holdout speakers only (6,734), neg or partly | 655 = 9.7% | 660 = 9.8% |
| Held-out notes, history | 4,982/6,014 = 82.8% | 5,033/6,121 = 82.2% |
| Shepardized dev NEG strict (254) / precision / CLEAN | 143 = 56.3% / 93.5% / 9,694 | 145 = 57.1% / 93.5% / 9,694 |
| **Shepardized sealed (252), fourth use (burned)** NEG strict / precision | 123 = 48.8% / 92.5% | **125 = 49.6% [43.5, 55.7] / 92.6%** |
| Old lists (burned): SCDB explicit / with recognised; CRS / with recognised | 146 / 178; 167 / 199 | 144 / 177; 164 / 198 |
| Leak check | exit 0 | exit 0 |

**Reading the numbers.** The h0 gains replicate on h1 for FJC (+1.0 / +1.2 points) and Shadow Docket (+6.0 / +7.5);
SCDB and the state tables barely move on either half. The new Songer key — the same relation as FJC, never seen —
moves +12 cases (+5.2 points, intervals overlap), with precision kept at 97%: the FJC rules generalise. Brace & Hall
does not move: no round-9 class targets state supreme courts' review of intermediate appellate decisions; it is a
fresh baseline (50.0% recall, 93.1% precision). The losses (fresh sealed −1, old burned lists −2/−1, SCDB h0 −1, FJC
−2 before the J rows) come from the part-zone check: it refuses quotes taken from the Supreme Court syllabus (the
reporter's words, not the Court's) and quotes whose only evidence is head matter. They are right refusals of the
evidence, but in at least one case (an overruling quoted from the syllabus, with no other row on the target) the
opinion itself states the same act and no reader row quotes it — next move 1. Nothing was re-tuned after the sealed
run.

## Not installed, cut, open

- Not installed: FJC G / G2 (0.81 / 0.84), SCDB judgment readings (0.867, D9-11), PJH (0.72), state A v1 (0.69),
  doctrine own-tie (3 pairs), shadow9's `history_remand.tsv` evidence (D9-10: rows admitted by the round-8 checks and
  audited; the evidence would move the link from audit to check — a later Lean change).
- Data gap (Shadow Docket): 281 h0 orders are not in the corpus (268 GVRs; the corpus lacks order lists for 2006–09 and
  2020–25).
- New Jersey: 1,607 decisions filed under the old Supreme Court (court 1095) carry the Court of Errors and Appeals'
  vote roll (a court-attribution error in decisions2, not staged). Under D9-6 the Appellate Division has power over the
  former and not the latter; only one admitted row touches such a decision (tw:4018149, whose status is true either way).
- scdb9 found a round-8 bug: `sc8sel.py` used an undefined `WEAK` (620 SC opinions produced no row); fixed in scdb9's copy.

## Incidents

- 03:21 C: filled (other sessions' writes plus round-9 stage/run copies); WSL Ubuntu's root went read-only. The lead
  deleted round-9 intermediates only, terminated Ubuntu (only idle sleeps and one wait loop were running), then
  `wsl --shutdown` (docker-desktop was already stopped) after a first start failed; Ubuntu came back read-write at
  ~03:25. The coordinator then freed ~15 GB of non-frozen round-5…8 intermediates. lean9 reran regressions a2/c.
- 03:36 the first FREEZE.md was refused by the sealed script's own check: ref9's generator `make_r9.py` (hashed as
  agent code) changed after the freeze. Nothing was scored; FREEZE.md was re-written (old copy
  `FREEZE_refused_0336.md`, identical except that hash) and the sealed pass ran once.
- ref9's first v9a reference run shared a difftest folder with the lead's v9a run; v9a's figures are interim only.

## Decisions for the user

1. Songer key: 2,383 of its 2,391 linked appellate decisions are units of the Shepardized key, which tested their own
   later history, not their treatment of the decision below; kept (strict exclusion would empty the key).
2. Two classes installed exactly at the 0.900 bar (FJC W and J); the state A class passed on the brief's measure
   (rejects/departs) but the audit scorer's soft-kind measure gives 0.611 because rows understate stronger acts.
3. The part-zone check trades three dev/burned hits for refusing syllabus/head-matter evidence; keep it (it is the
   round's soundness gain) and fix the readers (next move 1)?
4. New Jersey court attribution (1,607 mis-filed E&A decisions): a decisions2 change, not yet staged.

## Next moves, ranked (value / effort)

1. **Syllabus and head-matter quotes**: when a row's quote lies in the syllabus / head matter, find the same act in
   the opinion zone and re-cut (recovers the zone-refused overrulings; a few rows, cheap, whole-class audit).
2. **Brace & Hall misses** (state supreme courts reversing intermediate appellate decisions; 835 of 1,670 found):
   diagnose on a NEW tuning split carved from it only if the user agrees to retire one half; otherwise mirror its
   relation in a state-court analogue of the FJC linker (F1/W/J on state supreme court opinions).
3. **FJC**: the 282 "named other case" and 64 one-side-caption misses; a citation-level test of which ruling is under
   review (what G lacked).
4. **SCDB "cited without accepted anchor" (129)**: bare / footnote citations outside the history zone.
5. **Shadow Docket** remand-bridge evidence in the Lean (D9-10) and the 44 post-2013 orders with no remand decision.
6. State tables: the h0 implicit misses carry no rejection words naming X (state9 diagnostic) — a doctrine-level or
   holding-level reader, not a phrase rule; low value per effort.
