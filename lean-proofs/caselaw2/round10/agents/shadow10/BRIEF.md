# Agent `shadow10` (round 10): Shadow Docket — remand-bridge evidence table and the post-2013 orders with no remand decision (move 5)

Read `round10/DESIGN10.md` (§0 and §4) and `round10/agents/COMMON.md` first. Folder `round10/agents/shadow10/`
(NOTES.md). Audit letter `k`. You may read `benchmarks/shadow_docket/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md`
and the h0 files (`round9/results/v9c/bench/shadow_docket.h0.cases.tsv`, `round10/results/*/bench/`) only. Never
anything about `songer_treat` or `brace_hall_state`.

## Background
v9c Shadow Docket h0: recall 475/1,059 = 44.9%, precision 91.5%, clean 99.9%. Round 9 (`round9/agents/shadow9/`:
NOTES.md, `remandtext.py`, `build9.py`, `rules9.py`, `diag.py`, `agree*.py`, `work/`, `LEAN_REQUEST.md`) installed
`cert_remandtext_v2` (335 GVR rows: order + caption-tied decision below + remand decision B on the same docket tied to
the order; audit 79/80); round 8 installed 32 `remandcap` rows of the same shape. Open: (1) the evidence for WHY the
target is the decision below (B) is audited, not checked — DESIGN10 §4 now specifies `history_remand.tsv` and the
check `remandBridge` (agent `lean10` implements it); (2) **44 post-2013 h0 orders with the order in the corpus but no
remand decision** (and ~102 post-2013 "no signal" misses overall); (3) 279–281 h0 orders not in the corpus (data gap:
order lists for 2006–09 and 2020–25 missing) — not fixable by rules; quantify only.

## Do
1. **Data for §4**: write `history_remand.tsv` lines (id, b_node, b_start, b_end, docket) for every v9c row of the
   remandtext-v2 and remandcap classes, plus the `cert_text.tsv` / `window_sha.tsv` lines for B's quotes (as round-8
   bridge quotes). Pre-check them yourself with a Python implementation of §4 (court, dates, docket token on both,
   cue + "supreme court" in B's quote ≤ 600 chars, tie to the order) and report how many pass and why others fail —
   before `lean10`'s build lands, so the lead can settle readings (e.g. the docket field the runner loads; if the
   runner has none, say so early in NOTES.md and the lead decides with lean10).
2. **The orders with no remand decision**: read a stratified sample (~30) with opus readers (corpus text: the order,
   candidate decisions below); find general rules that link the GVR order to the decision below without B: the
   order's own text ("judgment vacated … remanded to the United States Court of Appeals for the Ninth Circuit for
   further consideration in light of X"), the caption + circuit + the decision below's date (the last decision of that
   circuit with both parties' tokens before the petition), the docket of the case below printed in the order list,
   a later decision citing the order. Rows checkable by the round-9 Lean (orderHead claim, name evidence, anchors);
   else `LEAN_REQUEST.md`.
3. Certify, stage, run (NOBUILD), score (`noold`): precision / clean must not drop.
4. Blind audit each status-changing class (≥ 80 or the whole class, two auditors, decoys; link + effect); install at
   ≥ ~90%.
Report: the §4 table (rows, pre-check pass/fail by reason), new rules/rows/audits, delta folders, h0 effect, the data
gap count. Time box ~100 minutes.
