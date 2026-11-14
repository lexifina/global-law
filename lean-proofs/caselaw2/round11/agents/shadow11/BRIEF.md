# Agent `shadow11` (round 11): Shadow Docket — rows on the newly staged order-list nodes, and a narrower C2/C9

Read `round11/DESIGN11.md` (§0 and §4) and `round11/agents/COMMON.md` first. Folder `round11/agents/shadow11/`
(NOTES.md, a line every 10 minutes). Audit letter `k`. You may read `benchmarks/shadow_docket/SOURCE.md`,
`MAPPING.md`, `DISAGREEMENTS.md` and the h0 files (`round10/results/v10d/bench/shadow_docket.h0.cases.tsv`,
`round11/results/*/bench/`) only. Never the closed keys.

## Background
v10d Shadow h0: recall 514/1,059 = 48.5%, precision 92.0%, clean 99.9%. Round 10 (`round10/agents/shadow10/`:
NOTES.md, `cap10.py`, `build10.py`, `wide10.py`, `remand10.py`, `verify_remand.py`, `work/`) installed C6 (GVR order →
the unique decision below with both caption sides and the full printed name; 126 rows, 0.963) and the §4 remand-bridge
evidence table (316 lines). Not installed: C2 (no full name, 0.625: same-surname people, other suits of one party,
earlier judgments), C9 (C6 with widened candidates, 0.702: the "full name" was a frequent litigant — union,
official, diocese — so the unique hit was another suit of that party). Round 9 `shadow9` and round 8 `orderdock`
hold the earlier rules (remandtext v2, remandcap, "Reported below"). 281 h0 NEG orders are not in the corpus.

## Do — two parts
**A. The new order nodes (main lever).** Agent `orders11` is fetching the missing order lists (2006–09, 2020–25) into
`round11/data_orders/` (`nodes.tsv`, `text/`, markers `DATA_READY_PARTIAL` / `DATA_READY`); agent `infra11` makes
them stageable (`stage11.py --nodes round11/data_orders`, overlay `round11/nodes11.py`, marker `round11/NODES_READY`).
While they work: port the C6 linker (and the remandtext / remand-bridge B-decision tie, and "Reported below" when
printed) to run over an order node given as (docket, caption as printed, date, disposition text, lower court named
in the remand clause) instead of a corpus node, so it runs the moment the data lands; test it on corpus order nodes
of 2010–19 (it must reproduce round-10's C6 links there). Then build rows `by` = the new order node → the decision
below, certify (`certify11.py` with the nodes overlay), stage with `--nodes`, run, score `noold`. The C6 bar still
holds: a new class (C6 on fetched order nodes) gets a fresh corpus-wide audit (≥ 80; auditors see the order node's
text and the candidate decision). Report the h0 effect and how many of the 281 gap orders now link (and why the rest
do not).
**B. While waiting: a narrower C2 / C9 sub-rule** (DESIGN11 move 6). Find a sub-rule that removes C2/C9's failure
modes by a principled test — e.g. the person-name side must be a natural person's full name (given + surname, not an
organisation, office or frequent litigant); a second tie (the lower docket printed in the order list or in the
decision below, the lower court's date) — designed from round 10's failure descriptions in shadow10's NOTES and on
corpus text, NOT by re-reading r10k02 / r10k03 items. Fresh audit excluding r10k01–03 samples. Install bar ~0.90.
Report: rows per class, audits with intervals, delta folders, h0 effect vs v10d, gap orders linked, headroom left.
