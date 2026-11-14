# Agent `orderdock` (round 8, move 2): Supreme Court orders linked by docket number; Shadow Docket h0 weak spots

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/orderdock/` (NOTES.md).
You may read `benchmarks/shadow_docket/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files under
`round8/results/*/bench/` only (never `benchmarks/shadow_docket/key.tsv` or its `work/`, `raw/`, `results/`).

## Background
- Round 7: `round7/agents/orderhead/` (NOTES.md, `build_orderhead.py`): 8,166 head-matter Supreme Court order rows
  certified (claim `orderHead`, DESIGN7 §3.1: SC, date ≥ 2013, order-line cue, ≤ 400 chars): certDenied 7,960,
  vacated 110 (GVR), reviewDismissed 95, affirmed 1. Blind audit r7a10 67/80 = 0.838 and GVR r7a12 67/80: the
  caption-only links failed (cap-2t 11/59 wrong). Not installed. The Lean rule is in place.
- Round 6: `round6/history/rules/memo` (SC memorandum orders → decision below by "Reported below" or caption + lower
  court + 30–600-day window).
- Shadow Docket DISAGREEMENTS (round 6): misses whose order is in the corpus — combined orders listing many captions
  (Booker 2005, Dorsey 2012 GVR lists) whose "Reported below: 95 Fed. Appx. 376" line is not attached (the corpus
  files the decision as "F. App'x"; positional caption/citation pairing inside long lists); head-matter-only orders
  with no "Reported below" line; corrupted citations ("639 P. 3d 315" for 639 F.3d 315).

## Do
1. Docket linking for the head-matter orders: find what docket information the corpus gives (decision metadata in
   `round7/stage/v3/decisions2.tsv` / the corpus records, the order text's "No. 12-3456", lower-court docket numbers
   in the decision below's own head matter, later texts citing "No. 12-3456", the round-7 b4rehear docket index
   `round7/agents/b4rehear/` …) and build a general link: order → the decision below **by docket number** (+ lower
   court, + date window), unique match only; caption only as a tie-check, never alone. Re-certify the orderHead rows
   that a docket link supports (certify8, claim `orderHead`), and report how many of the 8,166 (and of the 110 GVR /
   status-changing ones) survive. If the Lean certificate needs a docket-number evidence form that the round-7
   checker cannot verify (the target evidence must resolve in the quote: `cite:` or `name:`), write
   `LEAN_REQUEST.md` (e.g. `docket:<no>` evidence resolved through a docket table) and report early — the lead will
   decide quickly; meanwhile produce the rows.
2. Shadow Docket h0 diagnosis (after `round8/bench_h0/READY`): from `round8/results/v3/bench/shadow_docket.h0.cases.tsv`
   take the h0 NEG misses whose order is in the corpus, read ~30 (corpus texts only), classify, and write general
   rules for (a) combined GVR orders: pair each caption with its own "Reported below" line inside a list (parse the
   list into entries by the order-list grammar "No. … v. … C. A. … Reported below: …"), normalise "Fed. Appx." ↔
   "F. App'x" (and other reporter variants: check the round-6 `citeforms/` aliases first), and (b) orders with no
   "Reported below" line (docket / lower court / caption + date, unique only). Post-2013 orders are head matter
   (orderHead claim); pre-2013 combined lists may be opinion text — check part.
3. Certify (certify8) into delta folders per sub-rule; measure with stage/run/score (Shadow Docket h0 recall and
   clean, Shepardized dev SC vacated, SCDB h0 precision). Status-changing rows (vacated / reversed) need the blind
   audit (`round8/audit/HOWTO.md`) — ≥ 80, fresh sample, link + effect; certDenied rows change no status but still
   go through one audit for link precision if you want them installed.

Final report: link rule(s), counts, audits, delta folders, h0/dev effect, any LEAN_REQUEST.
