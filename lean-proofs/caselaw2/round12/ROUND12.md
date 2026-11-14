# Round 12: Shadow Docket order nodes (ligature repair, 2005 long lists, several-candidate pick), en banc, Federal Circuit district / other-target, Brace & Hall third tie

14 Nov 2026, 06:58–07:46. Contract and decisions: `DESIGN12.md` (D12-1 … D12-7). Log: `LOG.md`. Freeze: `FREEZE.md`
(variant `v12a`, 2,101 file hashes, 07:43). Sealed runs: `SEALED_LOG.md` (one run, 07:43). Nothing installed in
`data/` or `out/`. With no round-12 table present, the round-12 tools and the frozen binary reproduce
`round11/out/v11d` byte for byte (and the round-11 tools still reproduce v10d / v9c / v8e). Nothing committed. All
reading and auditing by local Claude sub-agents (opus); no external model. **No Lean change** this round: the frozen
binary is round 11's s51 (a1cc4296); the Python reference (precedent_ref 987f5266) on v12a: **0 disagreements in every
table** (status 532,252, findings 328,755, certs 498,050, classes 37,448).

Scope as briefed: no SCDB or state-overruled-table work, no FJC "which ruling" reader; state T4, SCDB R2 v3 and the
§5.2 identity lines left out (pending user decisions).

## What was built

- **Order data (`orders12`; `round12/data_orders/`, 27 MB text).** 14 HTTP requests to supremecourt.gov (≥ 3 s apart,
  generic user agent, all 200, nothing blocked; URL + time + bytes + sha256 in `data_orders/SOURCES.tsv`; PDFs deleted
  after conversion):
  - **The dropped ligature, repaired by re-extraction (documented rule).** Cause: in the Jnl17–Jnl25 PDFs (and a few
    fonts in Jnl15) the fonts name codes 174 `/fi` and 175 `/fl` but their ToUnicode maps both to "f". A glyph-name-
    aware extractor (`agents/orders12/scripts/pdf2txt_lig.py`) restores them; same lines, only f → fi/fl. Jnl19–25
    were re-fetched (7 requests; same sha256 as round 11). 3,997 words repaired (507 distinct). A vocabulary rule was
    rejected (it cannot decide "Sharif"/"Sharifi"). Parse effect: 0 class / docket / node-or-not changes (the parser
    already accepted "affrmed"); 2,781 entry texts, 57 of the 1,045 node texts changed (21 captions) → `CHANGED.tsv`.
  - **Missing Terms OT2010–13, OT2015, OT2017–18** (7 requests): 53,511 entries, 615 node-class; round 11's rule adds
    **0 nodes** (the corpus holds every one of those orders). Parser validation 2012-03 98.8%, 2018-11 96.8% of
    entries docket-matched, 99%+ same date.
  - **2005 long lists.** The 840 GVRs of 2005 all have a corpus node, but most sit in one multi-docket list node (the
    Booker list, node 6230687, prints 357 dockets). Rule: an entry whose corpus node within ±10 days lists ≥ k other
    dockets gets its own Journal node, `src` `r12:longlist`: 764 nodes at ≥ 10 (2005 711, 2012 53) + 62 at 3–9.
    `nodes.tsv` = 1,871 (round 11's 1,045 first, same ids).
- **Infrastructure (`infra12`)**: certify12 / stage12 (`--nodes` refuses a reordered prefix; `--drop` of base rows) /
  r12_run / score12 / clean12 / audit12 / freeze12 / score_sealed12 / live page section 99b + "Round 12" row.
  **Audit exclusion fixed from the start:** `make_packs12 --exclude` matches by (table, by, target, kind) — by (by,
  target) for kind-less files — whatever the id prefix; self-test 80/80 excluded for an h11 sample, synthetic h10/h11
  ids and kind-less t10 ids. Self-tests: v11d reproduced byte for byte (stage, Lean twice, score).
- **New held-out key (`bench12`, isolated; scored only after the freeze, first use):** `fjc_idb_unpub` — FJC IDB
  appeal records that the CCAD crosswalk attaches to no published opinion (rows disjoint from `fjc_idb_appeals`;
  docket overlap guard); 630,275 items, 17,944 linked; main group (reviewing decision in corpus, cites the district
  decision) h0 848 / h1 851 units. Caveat: the relation (district decision reversed on appeal) is one the model was
  tuned on through `fjc_idb_appeals` h0, so it tests generalisation to new rows more than a new relation.

## Classes, blind audits (Wilson 95%; two opus auditors per pack; decoys all answered right) — "right" = same case, the acting court itself disposed of the target, exact kind and scope

| class (agent) | rows | audit ("right") | installed |
|---|---|---|---|
| State u2t: U2 identity + a **third tie** (full date in both bodies / trial judge / trial county / lower docket; strict names; no earlier docket- or cite-tied candidate) — date-tie rows (stlink12) | 386 | r12t01 76/80 = 0.950 [0.878, 0.980] | yes |
| State u2t, judge / county / docket-tie rows | 16 | r12t02 whole class 15/16 = 0.938 [0.717, 0.989] | yes |
| Shadow C8: several full-name candidates all on one lower docket → the latest ≥ 60 days before the order and before 1 July after the docket year; post-judgment orders set aside (shadow12) | 67 | r12k01 whole class 64/67 = 0.955 [0.876, 0.985] | yes |
| Shadow C6/K9 on the new long-list nodes and ligature-repaired nodes | 321 | r12k02 77/80 = 0.963 [0.895, 0.987] | yes |
| Shadow re-certified rows on repaired nodes (same pair and rule as v11d; `--drop` the 14 h11 rows) | 14 | (audited class, r11k02) | yes |
| Shadow sub-captions of consolidated entries | 17 | r12k03 whole class 13/17 = 0.765 | no |
| En banc EB12 v5: E's own words say the panel opinion was vacated → row on P, never on the grant order (enbanc12) | 117 | r12e01 65/80 = 0.812 [0.713, 0.883] | no |
| En banc EB12 v6 (cut on r12e01's errors: P ≥ 2,000 chars; caption-only links need the docket and ≤ 1,000 days) | 101 | fresh remainder r12e02 26/27 = 0.963 [0.817, 0.993]; biased r12e01 items 64/67 | **no — user decision (D12-4)** |
| En banc OP12: a corpus order granting rehearing en banc vacates P in its own words | 7 | r12e03 whole class 5/6 = 0.833 | no |
| Federal Circuit form M (earlier merged ruling under the same negative judgment) + other-target form L (fedcir12) | 49 status | r12c01 whole class 25/49 = 0.510 [0.375, 0.644] (M 16/39, L 9/10) | no (L split post hoc, D12-7) |

Every audit excluded the earlier samples of its family by identity (r10t05, r11t01–06; r10k01–03, r11k01–04; r11b03–04,
r12e01–02; r11c01–03): overlaps found and excluded where present.

## Scores: round-11 `v11d` → round-12 `v12a`

Round-8 keys (h0 = tuning half; **h1 = fifth use**, after the freeze):

| key | h0 v11d → v12a | h1 v11d → v12a (**fifth use**) |
|---|---|---|
| Shadow Docket, recall | 688/1,059 = 65.0% → **707 = 66.8% [63.9, 69.5]** | 716/1,093 = 65.5% → **735 = 67.2% [64.4, 70.0]** |
| … precision / clean | 93.2% / 43,770 → 93.4% / 43,770 of 43,811 | 94.5% → **94.5%** (735/778) / 43,576 → 43,574 of 43,613 |
| SCDB disposition, recall | 1,838/2,407 = 76.4% (=) | 1,836/2,400 = 76.5% (=) |
| FJC appeals, recall | 1,595/2,832 = 56.3% (=) | 1,632/2,864 = 57.0% (=) |
| State tables, recall | 18/132 (=) | 11/142 (=) |

Closed keys:

| key (use) | v11d | v12a |
|---|---|---|
| Brace & Hall (**fourth use**), recall (cited population) | 942/1,670 = 56.4% | **942/1,670 = 56.4%** (=) |
| … recall_all (incl. uncited decisions below) / precision_all / clean | 955/1,853 = 51.5% / 93.6% / 1,195/1,253 | **967/1,853 = 52.2% [49.9, 54.5]** / 967/1,032 = 93.7% / 1,195/1,253 (=) |
| Songer TREAT (**fourth use**), recall all | 101/228 = 44.3% | 101/228 (=) |
| Federal Circuit (**third use**), recall cited all | 168/300 = 56.0% | 168/300 (=) |
| bhk_enbanc (**second use**), recall all | 325/690 = 47.1% | 325/690 = 47.1% [43.4, 50.8] (=) |

New key (**first use**, both halves untouched; v11d and v12a scored together after the freeze):

| key | v11d | v12a |
|---|---|---|
| fjc_idb_unpub, main group recall (h0 / h1) | 91/142 = 64.1% [55.9, 71.5] (42/71, 49/71); precision 91/96; clean 1,433/1,441 | identical |
| … all linked decisions | recall 99/1,201 = 8.2%; clean 14,318/14,332 | identical |

Existing keys:

| measure | v11d | v12a |
|---|---|---|
| Fresh lists dev (165): lenient / strict model / strict attributed | 112 / 52 / 82 | 112 / 52 / 82 |
| Fresh lists sealed (127), **eighth use (burned)** | 77 / 32 / 57 | 77 / 32 / 57 |
| Holdout notes, history | 5,236/6,347 = 82.5% | 5,252/6,373 = 82.4% |
| Holdout notes, holdoutOnly neg or partly / alsoInFeed | 670 / 1,068 | 670 / 1,068 |
| Shepardized dev NEG strict / precision / CLEAN | 146/254 / 93.6% (146/156) / 9,694 | 146/254 / **93.0% (146/157)** / **9,693** |
| Shepardized sealed (252), **seventh use (burned)** NEG strict / precision / CLEAN | 128 = 50.8% / 92.8% / 9,577 | **129 = 51.2%** / 92.8% (129/139) / 9,577 |
| Old lists (burned) | 146/178; 167/199 | 146/178; 167/199 |
| Leak check | exit 0 | exit 0 |

**Reading the numbers.** Shadow Docket +1.8 points on h0 and **+1.7 on h1** (716 → 735), precision flat at 94.5%,
clean −2 on h1 (and one Shepardized-dev CLEAN case, *United States v. Williams*, 314 F.3d 552, turned negative by one
2005 long-list C6 row — the item an r12k02 auditor marked "unsure"; left in, rules not rows). The state third tie
moves Brace & Hall only on its uncited population (recall_all +12 cases, precision up, clean unchanged) — the primary
cited-population recall does not move, as expected for a rule about uncited decisions. Nothing installed acts on en
banc rehearing, Federal Circuit review or FJC appeals, so those keys and Songer do not move. The new key is a baseline.
Nothing was re-tuned after the sealed run.

## Not installed, cut, open

- Below 0.90 "right": Shadow sub-captions (0.765), EB12 v5 (0.812), OP12 (0.833), Federal Circuit M + L (0.510).
- **EB12 v6 (D12-4)**: above the bar on its fresh items (26/27) but only 27 fresh of 101 (the cut was designed on
  r12e01's errors) — installable only with a fresh ≥ 80 sample, which the class cannot supply. Overlaps SCDB R2 v3 in
  12 pairs. To the user.
- Federal Circuit form L (26 rows, 10 status): 9/10 in a split chosen after the class was read (D12-7); zero h0/dev
  effect anyway.
- Pending decisions left out as instructed: state T4, SCDB R2 v3, the 139 §5.2 identity lines.
- Side finding (stlink12): 16 of round 11's installed U2 pairs rest on a non-strict name tie (role phrase or "X et al"
  read as a full name); they also hold a docket / cite / date tie and were audited 0.963; not touched.
- Process: all 7 agents reported within ~45 minutes; none went silent; disk 20 → 15–18 GB; every variant except
  `v12a` cleaned (one `--nodes` variant live at a time).

## Plateau analysis (h1 / blind recall, points per round)

| key | r9 | r10 | r11 | r12 | now | remaining headroom and why | verdict |
|---|---|---|---|---|---|---|---|
| Shadow Docket (h1) | +7.5 | +2.0 | +17.0 | **+1.7** | 67.2% | ~3–4 pts in identifiable pieces: same person, second docket (~11 gap orders; C8's one-docket test refuses them); officer-successor captions (~17); agency acronyms (~8); 46 unlinked 2005 per-entry nodes; 38 2005 cases that are vacated but turned back to good by the circuit's reinstatement (status semantics, not rows); ~3,200 orders with no natural-person caption side (no principled tie) | **continue only as a small leftover batch** (each piece a new audited rule; ~1–2 pts); otherwise maxed |
| SCDB disposition (h1) | +0.1 | +0.6 | +0.4 | 0.0 | 76.5% | coding / link artefacts, partial judgments | **stop: maxed out** |
| State overruled tables (h1) | 0.0 | 0.0 | 0.0 | 0.0 | 7.7% | tables' own errors, implicit rejections | **stop: maxed out** |
| FJC appeals (h1) | +1.2 | +1.1 | 0.0 | 0.0 | 57.0% | 1,495 h0 misses never cite the district decision; ties name earlier rulings | **stop: maxed out for tie rules**; the only lever left is the expensive "which ruling" reader |
| Brace & Hall (cited recall / recall_all) | 0.0 | +5.3 | +1.1 | 0.0 / +0.6 | 56.4% / 52.2% | 2,345 full-name pairs with no third tie (about half other people), 3,247 captions unparsed (repair audited 0.829), 1,043 surname-only; T4 (245 rows) waits for the decision | **stop: maxed out** for identity-tie rules; only the T4 decision is left |
| Songer (all) | +5.2 | +3.1 | 0.0 | 0.0 | 44.3% | follows FJC | **stop: maxed out** |
| Federal Circuit (all) | – | 0.0 | +3.3 | 0.0 | 56.0% | CAP Fed. Cir. texts carry no "Appeal from … in No." head line (1 hit corpus-wide), so the district docket identity is unavailable; ~180 other-target pairs are earlier merged rulings the measure does not count as disposed of (audit 0.41); 58 mixed judgments (rule R, 0.883) | **stop: maxed out** (a rule-R part test might add a handful) |
| En banc (bhk_enbanc, all) | – | – | baseline | 0.0 | 47.1% | 2,416 of 3,763 unmarked panel pairs have no acting text (mostly not real pairs: Delaware in banc, docket collisions); panels vacated as unpublished slips (not nodes); partial reinstatement (118, needs part-scope rows); EB12 v6 waits on the user | **stop after the v6 decision** (one possible small rule: re-select the next opinion when the docket's latest node is the grant order, ~55 pairs) |
| fjc_idb_unpub (new) | – | – | – | baseline | 64.1% | follows FJC | stop (with FJC) |

**Is a round 13 worth it?** Not as a general round. Round 12 moved blind recall on two keys only
(+1.7 Shadow h1, +0.6 B&H recall_all; zero on the other seven), and four of its five tracks ended at "the measure or the corpus
blocks the next rule" rather than "a rule is missing". What is left is (a) the user decisions below, which are cheap
to act on, (b) a Shadow leftover batch worth ~1–2 points, and (c) the FJC "which ruling" reader — the one remaining
large lever (~5–15 points nominal on FJC, with Songer and the new key following), expensive and uncertain. Recommendation:
**stop the round series here**, unless the user wants (a) applied (a short install round) or wants to fund (c) as a
dedicated project.

## Decisions for the user

1. State T4 (§6 trial bridge, 245 rows; right 0.850, link+effect 0.925): install on link+effect, or keep the bar?
   (carried from rounds 10–11)
2. SCDB R2 v3 (88 rows, 44/49 = 0.898 on a fresh sample under 80): keep out? (carried)
3. §5.2 identity evidence: install the 139 lines with the §5.2 binary (ea2e1d7e)? (carried; status-neutral)
4. **New: EB12 v6** (101 en banc rows; fresh 26/27 = 0.963, biased 64/67): install despite under-80 fresh items, or
   keep the strict rule (as for R2 v3)? It overlaps R2 v3 in 12 pairs — decide 2 and 4 together.
5. The 47 OT2025 orders dated Jan–Jun 2026 (carried, still in the build).
6. Data hygiene (status-neutral): 41 wrong base "affirmed" rows at the Federal Circuit; duplicate CCPA node
   (2044572 = 1927432); the 16 round-11 U2 pairs on non-strict name ties (new). Fix? (carried + new)
7. Carried from rounds 9–10: New Jersey court attribution (1,607 decisions), Songer/Shepardized overlap.
8. Closed this round: the "fi" ligature (round-11 decision 5) — repaired by re-extraction, no parse change.

## Next moves, ranked (value / effort) — or stop

1. Act on decisions 1–4 (a short install round: no new rules; T4 rides on round 10's §6 trial-bridge table, `history_tbridge`).
2. Shadow leftover batch: officer-successor captions, agency acronyms, same person / second docket (each its own
   audit); ~1–2 points h1.
3. FJC "which ruling" reader — the only large lever left; a separate, expensive project.
**Stop: maxed out** — SCDB, state overruled tables, Brace & Hall tie rules, Federal Circuit rule linking, Songer;
en banc after decision 4.
