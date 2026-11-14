# Agent `shadow9` (round 9): Shadow Docket, post-2013 head-matter GVRs (move 4)

Read `round9/DESIGN9.md` and `round9/agents/COMMON.md` first. Folder `round9/agents/shadow9/` (NOTES.md). You may read
`benchmarks/shadow_docket/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files
(`round8/results/v8e/bench/shadow_docket.h0.cases.tsv`, `round9/results/*/bench/`) only.

## Background
v8e Shadow Docket h0 recall 412/1,059 = 38.9%, precision 90.3%, clean 99.9%. Round 8 (`round8/agents/orderdock/`:
NOTES.md, `dock.py`, `dres.py`, `hscan.py`, `listcite.py`, `listorder.py`, `build_rows.py`, `certify_bridge8.py`,
`validate.py`, `work/`) built bridges (a third text's subsequent-history clause "X, cite, cert. granted, judgment
vacated …, O's cite"), order lists, remand-docket links. Left: **post-2013 head-matter GVR orders with no "Reported
below" and no history string**: the court below's own remand opinions name the order (931 found by docket bridges,
but too weak alone: 21/26 right); and **281 h0 orders not in the corpus** (a data gap: report it, by year and
source, no rows).

## Do
1. Diagnose v8e h0 misses by stage (order in corpus? decision below identified by any text? which signal exists?).
2. A combined rule: the remand opinion's docket bridge PLUS a second independent signal (e.g. the remand opinion
   names the Supreme Court order's date / the GVR's reason case ("in light of X"), the caption ties on both sides,
   the court below's earlier decision cited in the remand opinion matches the docket and date window, the order's
   own head matter names the court below) — measure each signal's agreement on the 931, then read a stratified
   sample with opus readers. Rows must be checkable by the round-8 Lean (bridge evidence DESIGN8 §4, anchors,
   orderHead claim); otherwise LEAN_REQUEST.
3. Certify (`round9/certify9.py`), stage, NOBUILD run, score (Shadow h0, SCDB h0, Shepardized dev). Blind audit
   (≥ 80, two auditors, decoys; link + kind); install at ≥ ~90%.
4. The data gap: count and describe the h0 orders not in the corpus (year, order-list type), with no key row printed
   beyond counts.
Report: anatomy, rules, signal agreement, counts, audit with interval, delta folders, h0/dev effect, the data gap.
