# Agent `shadow12` (round 12): Shadow Docket — the order nodes that do not link, the 2005 long lists, rows on round 12's new nodes

Read `round12/DESIGN12.md` (§0 and §4) and `round12/agents/COMMON.md` first. Folder `round12/agents/shadow12/`
(NOTES.md, a line every 10 minutes). Audit letter `k`. You may read `benchmarks/shadow_docket/SOURCE.md`,
`MAPPING.md`, `DISAGREEMENTS.md` and the h0 files (`round11/results/v11d/bench/shadow_docket.h0.cases.tsv`,
`round12/results/*/bench/`) only. Never the closed keys.

## Background
v11d Shadow h0: recall 688/1,059 = 65.0%, precision 93.2%; h1 716/1,093 = 65.5%. Round 11 (`round11/agents/shadow11/`:
NOTES.md, `build11.py`, `olink11.py`, `gap11.py`, `h0check.py`, `buildc11.py`, `work/`) installed olist-C6 (395, 1.000)
+ olist-K9 (36, 0.972) on the round-11 order nodes and olist2 (28, 0.964). Left (shadow11 NOTES 05:56, 06:25): 87 h0
gap orders whose node does not link — **several full-name candidates 39**, no both-sides caption candidate 43, C6/K9
disagree 4, no disposition parsed 1 — plus 2 gap orders without a node; ~260 in-corpus misses (no remand decision,
**2005 long lists not parsed** (`round9/agents/shadow9/NOTES.md`: 61), different-party captions); not installed:
C2 (0.625), C9 (0.702), C11 (0.850). Round 10 (`round10/agents/shadow10/NOTES.md` 04:00–04:01) measured a rule C8 on
non-key truths: **full-name / both-sides candidates all on one docket → the latest dated before 1 July after the
order's docket-number year: 226/242 = 93.4%** (not built then: too close to the bar).

## Do
1. **Several full-name candidates (main item).** A principled pick among several candidates that all carry the full
   printed name: C8's test (same lower docket / same case; the latest decision of the court named in the order's
   remand clause, dated before the end of the order's docket-term year; en banc / rehearing-denial entries are not
   the judgment). Build on corpus orders AND the order nodes; measure on non-key truths as round 10 did, read a
   diagnosis sample of unlinked items with opus readers (corpus text only), then certify, audit fresh (≥ 80, exclude
   r10k01–03 and r11k01–04 samples: `make_packs12 --exclude <their sample.tsv>`), install bar 0.90.
2. **No both-sides caption tie (43).** Diagnose the cause (caption forms: "In re", "Warden", substituted officers,
   compound surnames, Journal title-case forms, the dropped ligature — agent `orders12` repairs it, see its
   `round12/data_orders/LIGATURE_READY` / `CHANGED.tsv`). Fix what is a parse defect by a general caption rule; do not
   loosen the identity test (C2/C9 failed on exactly that).
3. **The 2005 long lists.** The corpus's 2005 S. Ct. order nodes print many dockets in one node. Either split the
   corpus long-list text into entries (positional caption / disposition pairing; rows `by` the corpus node, anchor and
   disposition inside the entry) or use `orders12`'s per-entry Journal nodes (`src` r12:longlist; its HANDOFF.md says
   what it finds) — pick the one that certifies under the existing Lean and say why. Same identity rules (C6/K9/C8).
4. **New and changed nodes.** When `round12/data_orders/DATA_READY_A` / `DATA_READY` appear: run olist-C6/K9 (+ your
   new rule) over the appended nodes; re-certify the round-11 olist rows on nodes listed in `CHANGED.tsv` (stage with
   `--drop` of the h11 rows they replace — one row per rule and pair). New-node rows of an audited rule get their own
   whole-class / ≥ 80 fresh audit (as r11k04 did).
5. Certify (`certify12.py`, nodes overlay), stage (only you and the lead stage with `--nodes`: one live `--nodes`
   variant at a time, ~870 MB + ~1.2 GB WSL — clean it as soon as scored), run NOBUILD, `score12.sh noold` vs v11d.
   Shadow h0 precision / clean, SCDB clean, holdout notes must not drop.
Report: rows per class, audits with intervals, delta folders (+ any `--drop` file), h0 effect vs v11d, how many of the
87 + 2 gap orders and of the in-corpus misses now link (and why the rest do not), headroom left.
