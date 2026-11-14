# Agent `fedcir12` (round 12): Federal Circuit — district-court targets and opinions whose review row sits on another target (move 3)

Read `round12/DESIGN12.md` (§0 — rule 3: `benchmarks/fedcir_dataset/` (and `songer_treat/`, `brace_hall_state/`,
`bhk_enbanc/`) is CLOSED to you: never open, list, glob or grep it, not even its docs; you diagnose on corpus text
only) and `round12/agents/COMMON.md`. Folder `round12/agents/fedcir12/` (NOTES.md, a line every 10 minutes). Audit
letter `c`. You may read `benchmarks/fjc_idb_appeals/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and its h0 per-case
file (`round11/results/v11d/bench/fjc_idb_appeals.h0.cases.tsv`) — only to check side effects.

## Background
Round 11 `fedcir11` (`round11/agents/fedcir11/`: NOTES.md, `fedcir_link.py`, `pop.py`, `anat.py`, `split.py`,
`uncited.py`, `deltas.py`, `cycle11.sh`, `work/pop.tsv`, `read1/`) installed the tribunal-anchor class (claim
`anchorTribunal`, 359 rows, r11c02 0.912; in v11d). Not installed: existing-cue class (r11c01 0.841: CCPA cites of an
earlier separate Customs suit whose record was incorporated; mixed judgments) and rule R (r11c03 0.883: the cited
ruling is the affirmed part of a mixed judgment). Left (NOTES 05:25):
- **District targets**: of 206 v10d-unmarked neg-judgment cited cap-2 Fed Cir → district pairs only 7 now link; losses
  no_court_phrase 90 / two_candidates 34 / later_events 30.
- **~236 opinions whose base review row sits on another target** (skip:base_row: CFC 94, district 81, CIT 48, CCPA 13):
  D already has a v10d review row on a different reviewed-tribunal decision.
- Same-target 'affirmed' rows while D's judgment line is negative (rule R population; 0.883).

## Do
1. **District targets.** Port the round-10 FJC head-line identity (`round10/agents/fjc10b/fjc10_link.py`: form h — the
   appeal's head matter "Appeal from the United States District Court for the District of Delaware in No. 1:10-cv-…,
   Judge …" tied to the district decision by docket + caption + date; rule P for partial scope) to Federal Circuit
   opinions; the anchor "the district court …" in the majority text. Diagnose `no_court_phrase` / `two_candidates` /
   `later_events` on corpus text (a stratified ~30-item reader sample) and fix by general rules (latest ruling of the
   docket dated before the appeal's decision that matches the judgment's subject; never an earlier ruling — the FJC
   lesson: a district docket carries many rulings).
2. **Other-target opinions (~236).** For each D whose existing review row sits on T' while the identity rules pick T:
   decide by the acting text which decision is under review (the head-matter appeal-from line, the judgment line, the
   citation of T vs T'). Classes: (i) add the row on T when T' is a different, also-reviewed decision (consolidated
   appeals) — no removal; (ii) T' is not under review (an earlier / related decision) → new row on T + `--remove` the
   T' row (type C audit as scdb11's R1: removals audited too). Status-changing rows only count; report status-neutral
   ones separately.
3. Mixed judgments (rule R's error mode) only if cheap: a part test (the cited ruling's subject vs the reversed part)
   on a fresh sample — not a priority.
4. Certify (`certify12.py`; rows needing `anchorTribunal` use `certify12_claims`), stage, run NOBUILD (the s51 binary
   accepts the claim), `score12.sh noold` vs v11d: FJC h0 precision / clean, Shepardized dev precision / CLEAN and
   holdout history must not drop. Blind corpus-wide audit per status-changing class (≥ 80 or whole class, two opus
   auditors, decoys; exclude r11c01–c03 samples with `make_packs12 --exclude`); install bar 0.90 on "right".
Report: population and miss anatomy (counts), rules, rows per class, audits with intervals, delta folders (+ any
`--remove` file), side effects vs v11d, headroom left (what cannot be linked and why).
