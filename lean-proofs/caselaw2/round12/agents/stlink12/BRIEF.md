# Agent `stlink12` (round 12): state review of uncited decisions below — a third tie for pairs matched on full names only (move 4)

Read `round12/DESIGN12.md` (§0 — rule 3: `benchmarks/brace_hall_state/` (and `songer_treat/`, `fedcir_dataset/`,
`bhk_enbanc/`) is CLOSED to you: never open, list, glob or grep it, not even its docs; you diagnose on corpus text
and dev keys only) and `round12/agents/COMMON.md`. Folder `round12/agents/stlink12/` (NOTES.md, a line every 10
minutes). Audit letter `t`. You may read `benchmarks/state_overruled_tables/` SOURCE.md / MAPPING.md / DISAGREEMENTS.md
and its h0 file under `round11/results/v11d/bench/` — side effects only.

## Background
Round 11 `stlink11` (`round11/agents/stlink11/`: NOTES.md, `ulink.py`, `ulink2.py`, `ties.py`, `feat.py`, `ident.py`,
`sample2.py`, `cycle.sh`, `deltas.py`, `work/`, `read2/`) installed U2 (543 rows: a state high court's decision D
reviewing an uncited intermediate decision T; full party names on both captions, T = the latest decision of that
court, plus a second tie — T's docket / citation / date printed in D; r11t01 0.963) and u2w (149, r11t05 0.963). Not
installed: u2n (0.800), u2e (0.863), u2q (caption-parse repair, 0.829). Headroom on the 9,459 uncited population:
**full names but no second tie 3,045** (read2: full names with no tie were 3/6 the same case — the other half are
other people / other proceedings), captions unmatched 3,247, surname-only 1,043, names mismatch 832, identified but
anchor fails 426.
**Not this round (pending user decisions): state T4 (§6 trial bridge) and the §5.2 identity lines — never stage
them.**

## Do
1. **A third tie for full-names-only pairs.** Candidates (measure each on corpus text): the trial judge's name printed
   in both D and T ("Judge X", "the Honorable X", "X, J." in T's head matter / D's "appeal from the … Court of …
   County, the Honorable X, judge"); the county / circuit / district of the trial court named in both; the trial-court
   docket number in both; the offence / cause of action and the trial date; T's author judge named in D ("Judge X,
   writing for the Court of Appeals"). Define each as an exact, general test (normalised token match in a stated text
   part of each node, with the forms you allow). Read a stratified diagnosis sample (~40: tie form × era × state) with
   opus readers (corpus text only) to see which ties hold the same case AND the decision under review (not an earlier
   round, not another prosecution of the same person — round 11's error modes).
2. Build the class (U2 identity with the third tie in place of docket / cite / date; anchor and disposition as U2 /
   u2w), certify (`certify12.py`), round-6 guard, stage, run NOBUILD, `score12.sh noold` vs v11d (holdout history,
   Shepardized dev, h0 keys must not drop).
3. Blind corpus-wide audit (≥ 80, two opus auditors, decoys; exclude r10t05, r11t01–t06 samples with `make_packs12
   --exclude`), stratified by tie form and era; install bar 0.90 on "right" (exact kind + scope — U2's scope errors:
   one party's part reversed).
Report: tie forms measured (counts, reader results), rows per class, audits with intervals, delta folder, side effects
vs v11d, headroom left.
