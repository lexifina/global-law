# HANDOFF orders12 -> shadow12 / infra12

## Step 1 (LIGATURE_READY)
- `nodes.tsv` rows 1-1045 = round 11's nodes: same local ids, order, docket, date, list_file, line_span.
- 57 node texts changed by the ligature repair (sha1 old/new in `CHANGED.tsv`); 21 captions, 25 disposition-word columns
  updated in nodes.tsv for those rows. No class, docket or node/not-node change anywhere. Rows of v11d citing these 57
  nodes need re-certifying (their text_sha changes).
- Journal texts repaired: `journal/` holds Jnl19-25 (repaired) plus the new terms' texts; jnl04-09, jnl14, Jnl16 are
  read in place from `round11/data_orders/journal/` (unchanged; no residual ligature drop found there).

## Step 2 (DATA_READY_A)
- New Terms OT2010-13, OT2015, OT2017-18 fetched, parsed (entries in `round12/agents/orders12/work/p_terms/`), Journal
  texts in `journal/`. Under round 11's rule they add **no node**: all 615 node-class entries (gvr 581, affirmed 18,
  vacated 11, granted_remanded 3, order_vacated 2) have a corpus S. Ct. node of every docket within +-10 days.
  nodes.tsv is still the 1,045 rows after step 2.

## Step 3 finding (2005 long lists) — written before the nodes are built
- Every 2005 Journal node-class entry (840, all GVR) has a corpus S. Ct. node of its docket on the same date, but those
  nodes are mostly multi-docket list texts: the corpus node's docket field (and its text) lists many other dockets.
  Per entry, the most other dockets listed by a corpus node of its docket within +-10 days: 0: 56, 1-2: 24 (field)
  / 3-9: 49, >= 10: 711 (field). Distinct corpus nodes: 97 (4 with >= 50 other dockets; one, node 6230687 of
  2005-01-24, the Booker GVR list, holds 357 dockets and covers 344 Journal entries).
- Same measure in the other years with corpus S. Ct. orders: >= 10 only in 2012 (53 entries; one list); 3-9 in 2011 (2)
  and 2012 (23); everything else 0-2.
- h0 (counted only, never used by the rule), 2005 NEG gvr orders by the measure of the corpus node of their docket on the
  order date (text count): long (>= 10) 172 agree / 93 miss (+ PART 4 miss), mid (3-9) 12 / 5, short (<= 2) 15 / 15.
  So long lists hold ~83% of the 2005 h0 GVR misses (97 of 117); they are not the only cause (short-node misses are
  as frequent per order).
- Rule (src `r12:longlist`): a node-class Journal entry not already a node, all of whose dockets have a corpus 2906
  node within +-10 days, and one of whose dockets' corpus nodes within +-10 days lists >= k other dockets in its docket
  field, becomes a per-entry node. k = 10 rows first, then 3 <= k < 10 rows, so cutting the file after the k >= 10
  block keeps all node ids. shadow12 picks: these nodes, or splitting the corpus long-list text itself.

## Step 3 built (DATA_READY)
- nodes.tsv now has the 8th column `src` (`-` for rows 1-1,045; `r12:longlist` for rows 1,046-1,871).
- Rows 1,046-1,809: 764 nodes with k >= 10 (2005 711, 2012 53). Rows 1,810-1,871: 62 nodes with 3 <= k <= 9 (2005 37,
  2011 2, 2012 23). To use only k >= 10: keep the header + the first 1,809 data rows (no node id moves).
  (Counts in the docket field, per entry: 2005 0-2 = 92, 3-9 = 37, >= 10 = 711; the text-count figures above differ
  slightly because texts also print cited dockets.)
- `longlist_report.tsv`: per candidate entry the corpus list node and its other-docket count; 29 distinct corpus list
  nodes are split (6230687, the 2005-01-24 Booker list, into 344 entries; 6262190, 2012-06-29 Dorsey list, 40).
- All 826 are GVR entries (remand reasons: Booker 739, Dorsey 53, others <= 8); courts below: federal circuit 814, state 12.
- Every text is the Journal entry's own words (date heading, section, caption line(s), body), as round 11's nodes.
- Loader check: `nodes12.activate('round12/data_orders')` = 1,871 nodes, count 6,894,325.
- Parsed entries of all held + new Journals (ids = local ids): `round12/agents/orders12/work/entries_all.jsonl`.
