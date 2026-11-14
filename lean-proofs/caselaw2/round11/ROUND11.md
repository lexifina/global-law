# Round 11: Supreme Court order lists as staged data, state review of uncited decisions below, a Federal Circuit tribunal linker, SCDB rehearing-denial targets

14 Nov 2026 05:06 – 06:56. Contract and decisions: `DESIGN11.md` (D11-1 … D11-11). Log: `LOG.md`. Freeze: `FREEZE.md`
(variant `v11d`, 1,296 file hashes, 06:53). Sealed runs: `SEALED_LOG.md` (one run, 06:53). Nothing installed in
`data/` or `out/`; with no round-11 table present the round-11 tools and binaries reproduce `round10/out/v10d` byte for
byte (and `round9/out/v9c`, `round8/out/v8e`). Nothing committed. All reading and auditing by local Claude sub-agents
(opus; 10 track agents + their reader/auditor sub-agents); no external model.

## What was built

- **Supreme Court order lists as staged data (DESIGN11 §4; agents `orders11` → `orders11b`, `infra11`, `shadow11`).**
  Source: the Journal of the Supreme Court (the Court's official minutes; a U.S. government work),
  `https://www.supremecourt.gov/orders/journal/jnlNN.pdf`, terms OT2004–09, OT2014, OT2016 (validation only) and
  OT2019–25. The per-term order-list index (`/orders/ordersofthecourt/<yy>`) only reaches back to OT2010 and a guessed
  2008 order-list PDF was 404, so the Journal is the source for the missing years. 21 HTTP requests in all (≥ 3 s
  apart, one connection, generic user agent), every one answered 200, nothing blocked or challenged; every URL, time,
  byte count and sha256 in `data_orders/SOURCES.tsv`; PDFs deleted after conversion (PyMuPDF). `round11/data_orders/`
  (28 MB, text only): `nodes.tsv` + `text/<id>.txt` = **1,045 order nodes** (GVR 994, vacated / order vacated 35,
  affirmed 14, granted-and-remanded 2) for 2006-03 … 2009-12 and 2020-07 … 2026-06, plus months the corpus covers only
  in part (an entry gets a node when a docket of it has no corpus S. Ct. node within ±10 days). Parser checked against
  the corpus without any key (OT2016 Journal vs the corpus's S. Ct. memorandum orders): docket match 98.7%, same date
  99.7%, GVRs 51/51. Staged with `stage11.py --nodes` as decisions2 rows N = 6,892,454 … in the corpus's own S. Ct.
  memorandum shape (court 2906; `text_sha` = sha1 of the text bytes, as for corpus nodes); **no Lean change was
  needed** (the runner takes the node count as an argument). Known defect: the later Journal PDFs drop the "fi"
  ligature in extraction ("affrmed"); kept verbatim (README).
- **Lean** (`LEAN11.md`, agent `lean11`): §5.1 claim `anchorTribunal` (Federal Circuit / CCPA anchors naming the
  tribunal: Court of International Trade, Customs Court, Court of Federal Claims, Claims Court, Veterans Court; a new
  presence-gated cue list, no existing list changed) and §5.2 optional identity-tie evidence table
  `history_identity.tsv` (a docket, citation or date of the decision below printed in both texts). Theorems 292 → 305
  (13 added, 0 changed, 0 removed), mutants 83 → 89 (each killed, diagonals guarded), `#guard`s 548 → 607,
  `audit.py check` 305/0/0; no `sorry` / new axiom / `native_decide`. Statements fixed before code (§5.1 05:24:10,
  §5.2 06:14:05, STATEMENTS.log). Regressions a/a2/b/c and `round10/out/v10d`, `round9/out/v9c`, `round8/out/v8e`
  reproduced byte for byte by both binaries. **No slip this round** (tree sha1s checked around every gate).
  **Frozen binary = §5.1 (a1cc4296).** §5.2 (ea2e1d7e) went green at 06:50, at the freeze deadline, after the build had
  been switched to §5.1; it is a ready capability (139 identity lines for the U2 rows wait for it; status-neutral by
  design).
- **Python reference** (`ref11`, from DESIGN11 only, never the Lean): §5.1 and §5.2. Real data: **0 disagreements in
  every table** on v10d alone, on v10d + the tribunal class, and on the frozen `v11d` (status 531,790 keys, certs
  497,260, findings 328,034, classes 37,448). Universes: kept 9 and probe 10: 0; sweep 20 and fuzz 10: one each, both
  pre-existing classes (they also show on the round-10 binary with round-11 inputs stripped); 552 earlier universes:
  the 14 known. §5.2 against the §5.2 binary: kept universes 0 disagreements; the 139 U2 identity lines pass 139/139.
- **Infrastructure** (`infra11`): certify11 (+ claims port incl. anchorTribunal), stage11 (+ `--nodes`, the
  `history_identity` extra table), `wsl/r11_run.sh` (base mirror by hard links, 0 bytes), score11, clean11 + KEEP,
  audit11 (decoy pools + round-10 audits; `--exclude` fixed mid-round to match earlier samples by (table, by, target,
  kind) — it had matched ids only), `nodes11.py` overlay, freeze11, score_sealed11, live page section 99 + "Round 11"
  row. Self-test: v10d reproduced byte for byte through the round-11 tools.
- **New held-out key** (`bench11`, isolated; scored only after the freeze): `benchmarks/bhk_enbanc` — Beim, Hirsch &
  Kastellec replication data on courts-of-appeals en banc rehearing, 1986–2002 (Harvard Dataverse
  doi:10.7910/DVN/2EJIZJ, CC0): published panel decisions later reheard en banc; 771 items, 691 linked, 690 units
  (h0 371 / h1 319); expected NEG_HIST.

## Classes, blind audits (Wilson 95%; two opus auditors per pack; decoys in every run, all answered right except one reader once) and decisions — measure "right" = same case, exact kind and scope

| class (agent) | rows | audit ("right") | installed |
|---|---|---|---|
| State U2: uncited intermediate decision; full party names on both captions, the latest decision of that court, and a second tie (docket / citation / date of T printed in D) (stlink11) | 543 | r11t01 77/80 = 0.963 [0.895, 0.987] (0 overlap with r10t05) | yes |
| State u2w: U2 identity; anchor = sentence naming T's court, extended to the party-name sentence | 149 | r11t05 77/80 = 0.963 [0.895, 0.987] | yes |
| State u2n (surname-only captions completed from both texts) | 10 | r11t02 8/10 = 0.800 | no |
| State u2e (cited but unmarked by round 6, U2 identity) | 370 | r11t03 69/80 = 0.863 [0.770, 0.921] | no (cut u2f not re-audited) |
| State u2q (caption-parse repair, U2 unchanged) | 41 | r11t06 34/41 = 0.829 [0.687, 0.915] | no |
| Federal Circuit tribunal anchors (claim anchorTribunal; mostly Claims / CFC / CIT / Customs targets) (fedcir11) | 359 (127 status) | r11c02 73/80 = 0.912 [0.830, 0.957] | yes (§5.1 binary) |
| Federal Circuit, existing-cue anchors | 186 (63 status) | r11c01 53/63 = 0.841 [0.732, 0.911] | no |
| Federal Circuit rule R (base "affirmed" row → negative when D's judgment line reverses) | 60 | r11c03 53/60 = 0.883 [0.778, 0.942] | no |
| Shadow olist-C6: GVR order node → the unique decision below with both caption sides and the full printed name (shadow11) | 395 | r11k02 80/80 = 1.000 [0.954, 1.000] | yes |
| Shadow olist-K9: remand-bridge port on order nodes | 36 | r11k03 35/36 = 0.972 [0.858, 0.995] | yes |
| Shadow olist2 (same rules on the 65 appended nodes) | 28 | r11k04 27/28 = 0.964 [0.823, 0.994] | yes |
| Shadow C11 (narrower C2/C9: natural-person side, unique full name, term-year bound) | 20 | r11k01 17/20 = 0.850 (fresh items 10/12) | no |
| SCDB R1: the Court's row on a court-of-appeals rehearing-denial order moved to the judgment it reviewed (scdb11) | 42 new + 45 removed | r11b01 40/41 = 0.976 [0.874, 0.996]; removals r11b02 44/44 [0.920, 1] | yes |
| SCDB R4: the same one level down (a state high court's refusal of review) | 4 new + 5 removed | r11b06 4/4, r11b07 5/5 (whole class) | yes |
| SCDB R2 v2 / v3 (en banc vacatur notes) | 196 / 88 | r11b03 0.512; r11b04 44/49 = 0.898 [0.782, 0.956] | no |
| SCDB R3 (bare "Reversed." → scope all) | 32 | r11b05 16/32 = 0.500 | no |
| FJC X2b: caption tie + judge or date tie, no docket tie, latest ruling, rules P/D/C (fjc11) | 531 (140 status) | r11f01 68/80 = 0.850 [0.755, 0.912] (fresh items 57/66) | no |
| FJC FU2: U2 ported to uncited district decisions | 245 | r11f02 0.673 [0.564, 0.766] | no |

## Scores: round-10 `v10d` → round-11 `v11d`

Round-8 keys (h0 = tuning half; **h1 = scored a fourth time, after the freeze**):

| key | h0 v10d → v11d | h1 v10d → v11d (**fourth use**) |
|---|---|---|
| Shadow Docket, recall | 514/1,059 = 48.5% → **688 = 65.0% [62.0, 67.8]** | 530/1,093 = 48.5% → **716 = 65.5% [62.6, 68.3]** |
| … precision / clean | 92.0% / 43,774 → 93.2% / 43,770 of 43,811 | 92.8% → **94.5%** (716/758) / 43,576 of 43,613 (=) |
| SCDB disposition, recall | 1,826/2,407 = 75.9% → **1,838 = 76.4% [74.6, 78.0]** | 1,827/2,400 = 76.1% → **1,836 = 76.5% [74.8, 78.2]** |
| … precision / clean | 97.5% / 1,998 → 97.6% / 1,997 of 2,052 | 97.2% → 97.2% (1,836/1,889) / 1,854 of 1,910 (=) |
| FJC appeals, recall | 1,595/2,832 = 56.3% → 1,595 (=) | 1,632/2,864 = 57.0% → **1,632 (=)** |
| State tables, recall | 18/132 → 18 | 11/142 → **11** |

Round-9 keys (**third use**, both halves) and the round-10 key (**second use**):

| key | v10d | v11d |
|---|---|---|
| Brace & Hall (state court of last resort reversing the decision below), recall all (h0 / h1) | 924/1,670 = 55.3% (500/868, 424/802) | **942/1,670 = 56.4% [54.0, 58.8]** (506/868 = 58.3%, 436/802 = 54.4%) |
| … precision / clean / part | 93.6% / 1,198/1,253 = 95.6% / 164/399 | 942/1,007 = 93.5% / 1,195/1,253 = 95.4% / 171/399 = 42.9% |
| Songer TREAT, recall all | 101/228 = 44.3% | **101/228 = 44.3%** (unchanged; precision 97.1%, clean 580/583) |
| Federal Circuit dispositions (fedcir_dataset), recall cited all (h0 / h1) | 158/300 = 52.7% (86, 72) | **168/300 = 56.0% [50.3, 61.5]** (90/150, 78/150) |
| … precision / clean / part | 89.8% / 735/742 / 124/256 | 168/186 = 90.3% / 735/742 (=) / 130/256 = 50.8% |

New key (**first use**, both halves untouched; v10d and v11d scored together after the freeze):

| key | v10d | v11d |
|---|---|---|
| CoA panel decisions later reheard en banc (bhk_enbanc), recall all (h0 / h1) | 325/690 = 47.1% [43.4, 50.8] (176/371, 149/319) | **325/690 = 47.1%** (unchanged) |

Existing keys:

| measure | v10d | v11d |
|---|---|---|
| Fresh lists dev (165): lenient / strict model / strict attributed | 112 / 52 / 82 | 112 / 52 / 82 |
| **Fresh lists sealed (127), seventh use (burned)**: lenient / strict / attributed | 77 / 32 / 57 | **77 / 32 / 57** |
| Held-out notes, also stated by a court with power (2,640), neg or partly | 1,068 | 1,068 |
| Held-out notes, holdout speakers only (6,734), neg or partly | 666 | 670 |
| Held-out notes, history | 5,204/6,305 = 82.5% | 5,236/6,347 = 82.5% |
| Shepardized dev NEG strict (254) / precision / CLEAN | 146 / 93.6% / 9,694 | 146 / 93.6% / 9,694 |
| **Shepardized sealed (252), sixth use (burned)** NEG strict / precision | 128 = 50.8% / 92.8% | **128 = 50.8% / 92.8%** |
| Old lists (burned): SCDB explicit / with recognised; CRS / with recognised | 146 / 178; 167 / 199 | 146 / 178; 167 / 199 |
| Leak check | exit 0 | exit 0 |

**Reading the numbers.** The order-list data is the round's lever: Shadow Docket +16.5 points on h0 and **+17.0 on
h1** (530 → 716), with h1 precision up (92.8 → 94.5%) and h1 clean unchanged — the rules are round 10's, the gain is
data. Of the 286 h0 gap cases (order not in the corpus), 192 now link right. Brace & Hall (built blind to U2; third
use) +1.1 points (+18 cases), clean −3 (95.6 → 95.4%), within U2's audited error rate. Federal Circuit (second use,
built blind to fedcir11) +3.3 points (+10 cases), precision up, clean unchanged — almost all Claims / CFC / CIT targets
the tribunal anchors now reach. SCDB +0.4 on h1. FJC, Songer, the state tables, the burned sealed lists and the new en
banc key do not move: nothing installed this round acts on courts-of-appeals review of district courts or on en banc
rehearing. Nothing was re-tuned after the sealed run.

## Not installed, cut, open

- Not installed (below 0.90 "right"): state u2n (0.800), u2e (0.863), u2q (0.829); Federal Circuit existing-cue class
  (0.841) and rule R (0.883); Shadow C11 (0.850); SCDB R2 v2 (0.512), R2 v3 (0.898 on 49 items, below the bar and
  under 80), R3 (0.500); FJC X2b (0.850) and FU2 (0.673).
- §5.2 identity evidence (139 lines on U2 rows): built, proved, reference-checked 139/139, not in the frozen build.
- Agents: `orders11` went silent at 05:16 after fetching and converting; `orders11b` resumed at 05:38 and delivered by
  05:55. Bug found and fixed: audit `--exclude` with round-10 samples matched nothing (h10 vs h11 ids); every round-11
  audit was then checked by (by, target) pair: C11 had 8 of 20 items in r10k03 (not installed either way), r11f01 had
  14 (reported on the fresh subset too; not installed), all others 0.
- Protocol: no model-building agent opened a closed key or the new key; the new key's name was kept out of LOG.md.
  Disk: C: 24 → 19–23 GB; every variant but `v11d` deleted after scoring; one order-node variant live at a time
  (each ~1.2 GB on C: + ~1.2 GB in WSL).

## Plateau analysis (h1 / blind recall, points per round; v10d → v11d for round 11)

| key | r8 | r9 | r10 | r11 | now | remaining headroom and why |
|---|---|---|---|---|---|---|
| Shadow Docket (h1) | +23.0 | +7.5 | +2.0 | **+17.0** | 65.5% | ~10–15 pts. The data gap is mostly closed (192 of 286 h0 gap cases link); left: 87 order nodes that do not link (39 with several full-name candidates, 43 with no both-sides caption tie), ~260 in-corpus misses (no remand decision, 2005 long lists unparsed, different-party captions), ~3,200 orders with no natural-person caption side (order lists print no lower docket, so no principled second tie). |
| SCDB disposition (h1) | +3.6 | +0.1 | +0.6 | +0.4 | 76.5% | **Stop: maxed out for this rule family.** ~570 h0 misses: SCDB coding / link artefacts, true partial judgments coded whole, no anchor / no disposition (two round-10 and two round-11 attempts failed audit). |
| State overruled tables (h1) | +0.7 | 0.0 | 0.0 | 0.0 | 7.7% | **Stop: maxed out** (the tables' own errors + implicit 19th-century rejections; would need a holding-level reader). |
| FJC appeals (h1) | +4.1 | +1.2 | +1.1 | 0.0 | 57.0% | ~15 pts nominal, blocked: 1,495 h0 misses are appeals that never cite the district decision, and a district docket carries many rulings, so caption / docket / date ties name earlier rulings (X2b 0.850, FU2 0.673). Needs a "which ruling" reader (the appeal-from clause typed against the district decision's kind). Plateau for tie-based linkers. |
| Brace & Hall (all) | – | 0.0 | +5.3 | +1.1 | 56.4% | ~8–10 pts: of 9,459 uncited court-named opinions 446 now link; 3,045 have full names but no second tie (about half other people), 3,247 captions unparsed (repair audited 0.83), 1,043 surname-only; T4 (trial-judgment reversals, 245 rows, link+effect 0.925) awaits the measure decision. Diminishing: hundreds of rows per point. |
| Songer (all) | – | +5.2 | +3.1 | 0.0 | 44.3% | Follows FJC; flat with it. |
| Federal Circuit (all) | – | – | 0.0 | +3.3 | 56.0% | ~5–10 pts: district targets barely reached (7 of 206 unmarked cited pairs), ~236 opinions whose base review row sits on another target, mixed judgments (rule R 0.883), CCPA incorporated-record cites (0.841). |
| En banc (new key, all) | – | – | – | baseline | 47.1% | Untargeted: no rule aims at an en banc court vacating its own panel's opinion; open front. |

**Is "maxed out" near?** SCDB and the state overruling tables: yes — stop. FJC (and Songer with it): plateau for
tie-based identity rules; more needs a new reader of which ruling is under review. Shadow Docket: the data lever paid
(+17 points); ~10 points remain, half linking of the new nodes, half caption identity. Brace & Hall and the Federal
Circuit: still moving, by 1–3 points a round. The new en banc key is an open, untargeted front. **Another round is
worth it, but a smaller, targeted one** (Shadow's unlinked order nodes, the en banc front, Federal Circuit district
and other-target cases, the T4 decision) — not SCDB or the state tables.

## Decisions for the user

1. State T4 (§6 trial bridge, 245 rows; right 0.850, link+effect 0.925): install on link+effect, or keep the "right"
   bar? (carried from round 10)
2. SCDB R2 v3 (88 rows, 44/49 = 0.898 on a fresh sample under 80): left out. Keep strict?
3. §5.2 identity evidence: install the 139 lines with the §5.2 binary (ea2e1d7e) at the start of the next round?
   (status-neutral; moves U2's identity ties from audited to checked)
4. The order nodes include 47 orders dated Jan–Jun 2026 (OT2025 Journal), kept since the as-of date is 2026-11-12.
   Keep?
5. Journal text defect: the later PDFs drop the "fi" ligature ("affrmed"); kept verbatim. Repair by rule, or keep?
6. Data hygiene (status-neutral): 41 base "affirmed" rows at the Federal Circuit are wrong ~95% of the time; a
   duplicate CCPA node (2044572 = 1927432). Fix?
7. Carried from rounds 9–10: New Jersey court attribution (1,607 decisions), Songer/Shepardized overlap.

## Next moves, ranked (value / effort)

1. **Shadow Docket: the 87 unlinked order nodes and the in-corpus misses** — a principled pick among several
   full-name candidates (latest decision of the named court before the order, bounded by the docket's term year;
   round 10's C8 read 93% on non-key truths), and the 2005 long lists. Rules exist; ~5 points.
2. **En banc front** (diagnosed on the corpus; the new key then on its second use): an en banc decision that vacates
   or supersedes its own panel's opinion → history row on the panel (same court, same case, cited or captioned).
3. **Federal Circuit**: district-court targets (port N/h+P with the "Appeal from … in No. …" head line) and the ~236
   other-target opinions; rule R with a mixed-judgment part test.
4. **Brace & Hall**: T4 after your decision; a third tie for full-names-only pairs (trial judge / county named in both
   texts); the caption-parse repair with a partial-scope cut (fresh audit).
5. FJC "which ruling" reader — expensive; only after 1–4.
**Stop: maxed out** — SCDB (this rule family) and the state overruled tables.
