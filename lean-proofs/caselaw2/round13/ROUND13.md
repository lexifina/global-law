# Round 13: Shadow Docket leftover batch (second docket, officer successor, agency acronym) + three held classes installed on the user's decision

14 Nov 2026, 11:30–12:10. Contract: `DESIGN13.md` (D13-1 … D13-3). Log: `LOG.md`. Freeze: `FREEZE.md` (variant
`v13a`, 159 file hashes, 12:04). Sealed runs: `SEALED_LOG.md` (one run, 12:04). Nothing installed in `data/` or `out/`;
nothing committed. Round-12 outputs only read. **No Lean change**: frozen binary s51 (a1cc4296), NOBUILD; the Lean tree
still builds in WSL (`lead/lean_check13.sh`: lake build LegalProofs.CaseLaw2 + Run OK; `audit.py check`: **305
theorems**, 0 statement changes, 0 problems; no sorry / native_decide / axiom). Python reference on v13a: **0
disagreements in every table** (status 532,639, findings 329,990, certs 498,507, classes 37,448). Self-test: the
round-13 tools with no delta reproduce `round12/out/v12a` byte for byte. All reading and auditing by local Claude
sub-agents (opus); no external model.

## Shadow leftover rules (each audited on its own; whole classes; earlier Shadow samples r10k01–r12k03 excluded by identity)

| rule | rows | audit ("right") | installed |
|---|---|---|---|
| D, same person, second docket: full-name candidates on >= 2 dockets; a judgment (C8 v2 judgment test, >= 60 days, before the docket-term bound) in the filing window of the order's docket number (from 1 July of the year before); exactly one docket in the window -> its latest | 16 | r13k01 14/15 = **0.933** [0.702, 0.988]; + 1 row read right in r11k01 (15/16) | yes |
| S, officer successor: no both-sides tie; name tie on the natural-person side (full name in the target's head) and the same public office on the other side with another holder (FRAP 43(c)(2), S. Ct. R. 35.3) | 11 | r13k02 9/9 = **1.000** [0.701, 1.000]; + 2 read right in r11k01 (11/11) | yes |
| A, agency acronym: one side an acronym of 3–6 capitals = initials of the other text's side (NLRB, SEC, FTC, FERC, NRC) | 8 | r13k03 8/8 = **1.000** [0.676, 1.000] | yes |
| N, name form (item 4: the unlinked 2005 per-entry nodes; middle names / hyphens) | – | dev only: 9/13 = 0.69 on non-key truths, 4 v12a disagreements (other people of the same name form) | no (no principled rule found) |

Decoys 4/4 in every audit. D's one error: a Londono-Gonzalez order linked to a Gonzalez-Diaz decision (another
petitioner). Dev checks before the audits: D agrees with v12a's own row on all 34 orders that already had one (16
corpus + 18 nodes), and with the non-key truths 3/3 (the no-window variant was 3/9).

## Held classes installed on the user's decision (below bar) — DESIGN13 section 3

| class | rows | earlier audit | Lean |
|---|---|---|---|
| State T4 (section-6 trial bridge, trialBridge claim + history_tbridge) | 245 | r10t04 right 0.850, link+effect 0.925 | 245/245 ok (tbridge lines 245, bad 0) |
| SCDB R2 v3 | 88 − 12 = 76 | r11b04 44/49 = 0.898 | 76/76 ok |
| En banc EB12 v6 | 101 | r12e02 fresh 26/27; biased 64/67 | 100 ok, 1 partZone (as round 12) |

**Overlap (D13-2):** R2 v3 and EB12 v6 share 12 identical (acting decision, target) pairs: 7 both `vacated` (a
double row), 5 R2 v3 `rehearingEnBancGranted` (from a citation note) vs EB12 `vacated` (E's own words). Resolved by
dropping the 12 R2 v3 rows (`lead/drop_r2v3_overlap.txt`): one row per pair, the acting court's own vacatur words.
A 13th shared target (459355) has two different acting decisions; both kept. T4 overlaps neither.

## Scores

Dev / h0 (before the freeze): v12a → v13h (held classes only) → v13a (frozen = v13h + D/S/A)

| measure | v12a | v13h | v13a |
|---|---|---|---|
| Shadow h0 recall / precision / clean | 707/1,059 = 66.8% / 93.4% / 43,770 | = | **721 = 68.1%** / 93.5% (721/771) / 43,770 |
| SCDB h0 recall / precision / clean | 1,838 / 97.6% / 1,997 | **1,840** / 97.6% / 1,997 | 1,840 |
| FJC h0 / state tables h0 | 1,595 / 18 of 132 | = | = |
| Fresh dev lenient / strict / attributed | 112 / 52 / 82 | = | = |
| Holdout history | 5,252/6,373 | 5,284/6,414 | 5,284/6,415 = 82.4% |
| Shepardized dev NEG / precision / CLEAN | 146/254 / 146/157 / 9,693 | = | = |
| Old lists (burned) / leak | 146/178; 167/199 / exit 0 | – | = / exit 0 |

Sealed, once, after the freeze (round-12 `v12a` → round-13 `v13a`):

| key (use) | v12a | v13a | moved by |
|---|---|---|---|
| **Shadow Docket h1 (6th)** recall | 735/1,093 = 67.2% | **747/1,093 = 68.3%** | D/S/A (+12; held classes move no Shadow h0 row) |
| … precision / clean | 735/778 = 94.5% / 43,574 | **747/790 = 94.6%** / 43,574 (=) | |
| SCDB h1 (6th) | 1,836/2,400 = 76.5%, prec 97.2% | = | – |
| FJC appeals h1 (6th) | 1,632/2,864 = 57.0% | = | – |
| State tables h1 (6th) | 11/142 | = | (T4 reaches no h1 case) |
| Brace & Hall (5th) recall / recall_all | 942/1,670 = 56.4% / 967/1,853 | **949/1,670 = 56.8% / 974/1,853 = 52.6%** | T4 |
| … precision / precision_all / clean | 93.5% / 93.7% / 1,195/1,253 | 949/1,014 = 93.6% / 974/1,039 = 93.7% / **1,194**/1,253 (−1) | T4 |
| bhk_enbanc (3rd) recall all | 325/690 = 47.1% | **365/690 = 52.9%** (h0 176→195, h1 149→170) | EB12 v6 + R2 v3 |
| Songer (5th) / Federal Circuit (4th) / fjc_idb_unpub (2nd) | 101/228 / 168/300 / 91/142 | = / = / = | – |
| Fresh sealed (9th, burned) | 77 / 32 / 57 | = | – |
| Shepardized sealed (8th, burned) NEG strict / precision / CLEAN | 129/252 / 92.8% / 9,577 | **131/252 = 52.0%** / 131/141 = 92.9% / 9,577 | en banc subclasses (enbanc_different 7→8, sc_vacated+enbanc 0→1): held classes |

Precision held everywhere (Shadow h1 94.5 → 94.6%, B&H 93.5 → 93.6%, Shepardized sealed 92.8 → 92.9%, SCDB =);
one B&H clean case turned negative through T4. Nothing re-tuned after the sealed run.

## Benchmarks
`benchmarks/existing/run_existing.py --label round13 --only shep,fresh,scdb`, the fresh-list views
(`gold_fresh/runs/views/round13`), `fold_round.py --round 13 --variant v13a --prev round12 --shep-use 8 --fresh-use 9`;
`graph/uses.tsv` + round 13 in `make_graph.py` (build list, colour, gain step; gain columns now fit eight steps; page
note); unified graph redrawn: `~/Documents/html-reports/benchmarks.html/.svg/.png` (backups in `round13/pre/`).

## Disk
C: 16 → 15 GB free (peak extra ~1 GB: one variant at a time, stages hard-linked to v12a; WSL mirror base_r13_v12a
hard links). Cleaned: v12a_check, v13h (stage, out, WSL), the v13a reference outputs. Kept: frozen v13a (KEEP.txt).

## Left for the user
1. The 38 reinstated-2005 cases (vacated, then turned back to good by the circuit's reinstatement): a status-semantics
   question, not targeted.
2. Item 4 (46 unlinked 2005 per-entry nodes): no principled rule found (name-form relaxation 0.69 on dev); left.
3. Still pending as before: the 139 section-5.2 identity lines, the 47 OT2025 orders of Jan–Jun 2026 (still in the
   build), data hygiene (41 Federal Circuit "affirmed" rows, duplicate CCPA node, 16 non-strict U2 ties), New Jersey
   attribution, Songer/Shepardized overlap.
4. Shadow h1 is now 68.3%; what is left there is the reinstatement question and orders with no natural-person
   caption side (~3,200): no further principled caption rule. Recommendation: stop the Shadow series.
