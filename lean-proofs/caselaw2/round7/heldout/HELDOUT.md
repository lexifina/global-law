# Round 7 held-out test: time split of Supreme Court judgments, 2021 onward

Agent `heldout`, 13 Nov 2026. This file holds counts only; the key itself (`key/`) and the raw records
(`src_scdocket/`) are private to this folder. **No reader, linker, candidate generator, brief writer or auditor
may read `round7/heldout/key/`, `round7/heldout/src_scdocket/` or `round7/heldout/work/`** (the lead is asked to add
this folder to DESIGN7 §0.2).

## 1. What the test is and why it is clean

**Test:** for each Supreme Court merits judgment in the corpus dated **2021-01-01 or later**, the lower-court
decision it reviewed and what the Court did to it — reversed, vacated, mixed (in part), affirmed, certiorari
dismissed as improvidently granted (`reviewDismissed`), or certiorari denied (for opinions respecting the denial of
certiorari, which the corpus holds as Supreme Court nodes). The model is scored on its same-case history of the
lower decision: is there an admitted history row by the Supreme Court decision on that lower decision, of the right
kind, with the right status effect.

**Source (the answers):** the Supreme Court's own docket record for each docket number
(`supremecourt.gov/RSS/Cases/JSON/<docket>.json`; public domain, US government work): the lower court, the lower
docket number(s), the date of the lower decision, the party titles, and the Clerk's judgment entry ("Judgment
REVERSED and case REMANDED.", "Adjudged to be AFFIRMED.", "Petition DENIED.", …). Fetched 2026-11-13 (SOURCES.md).
This is an administrative record, independent of the opinion texts the model reads and of every citator.

**Why 2021 (the cutoff), and why it is clean:**
- No round-5/6/7 rule, cue list or reader brief was written against a 2021+ decision. A search of every
  `.md/.json/.py/.txt` file of rounds 5–7 and of the reader and cue folders for post-2020 citation forms (F.4th,
  U.S. volumes 592+, S. Ct. volumes 141+) finds no history brief, cue list or rule note using such a decision as an
  example; the only brief hit is READER_BRIEF3, which quotes a 2022 slip-opinion page header ("Cite as: 597 U. S.
  ____ (2022)") as page-furniture to skip, not a disposition.
- The development keys stop earlier: the Shepardized Courts of Appeals Database (round-6 dev) ends in 2002; the
  history rules were developed on it and on corpus-wide audits.
- The docket JSON had never been used in the project (only `round6/research/lower_court_sources.md` mentions it).
- Some 2021+ decisions were nevertheless *seen*: round-5 diagnosis texts, round-6 history audit texts, reading
  packs. `seen_nodes.py` collects every 6–7 digit number from the working files people and sub-agents read
  (notes, briefs, logs, audit packs and texts, diagnosis files, reading packs and answers, decoy pools, the fresh
  dev half; bulk tables of more than 5,000 numbers and model-output row files left out; the sealed folders
  `round5/gold_fresh/sealed` and `round6/history/split` not walked). 115 of the 614 corpus Supreme Court nodes
  dated 2021+ are in that set. **Every key pair whose Supreme Court node or lower node is in the set is dropped**
  (73 pairs by the Supreme Court node, 9 by the lower node).
- Not a Shadow Docket Database key: that database (downloaded first, see §7) is now owned by the `benchmarks`
  agent and was not used.

## 2. Corpus coverage (what the corpus can hold)

- Supreme Court: the corpus holds order lists and opinions through 2020 (7–9 thousand nodes a year; none in
  2006–2009 except ~100–160 a year), and from 2021 only the opinions: 107, 101, 96, 93, 121, 96 nodes for
  2021–2026 (614; 512 carry a docket number).
- Lower federal courts: decisions to 2026. State courts: decisions only to about mid-2019 (Montana, Georgia,
  Wisconsin, New York, Colorado checked: the last year is 2019 with a part-year count). So state decisions reviewed
  in 2021+ are almost never in the corpus: the key is federal (255 of 256 pairs).

## 3. Linking (no model output read)

`build_timesplit.py` reads only the docket records, the round-6 cache metadata (node, date, court2 id, docket,
title, parties) and the court tables of `round6/history/stage/final2` (`courts2.tsv`, `court_alias.tsv`).

- **Supreme Court side.** Every corpus Supreme Court node dated ≥ 2021-01-01 with a docket number; each docket on the
  node is looked up in the docket records (509 records fetched, all HTTP 200). The judgment is the Clerk's entry
  **dated the same day as the node**. Dispositions split by docket or by party ("as to No. …", "as to
  respondent …") are not keyed. If the party titles share no name token with the node's caption, the docket is not
  keyed (3).
- **Lower side.** Lower court name → court2 id(s) (courts2 / court_alias names, with "Court of Appeals of X" ↔ "X
  Court of Appeals" and district/division qualifiers dropped); lower docket number(s) → digit skeletons; candidates =
  corpus decisions of that court with a matching docket, dated before the Supreme Court node, whose caption shares a
  name token with the docket's party titles; then **exactly one** candidate on the lower decision date
  (`exactDate`), else exactly one within ±7 days (`nearDate`); otherwise no pair.
- One line per (Supreme Court node, lower node); a pair keyed with two different kinds would be dropped (none).

Match rates (dockets on 2021+ Supreme Court nodes: 512; with a judgment entry on the node date: 493):

| expected kind | dockets with judgment | lower linked (exact / near) | not linked: docket not in corpus | date not matched | ambiguous | unparsed / no id / unmapped |
|---|---|---|---|---|---|---|
| reversed | 168 (153 fed., 15 state) | 115 (114 / 1) | 30 (16 fed., 14 state) | 15 | 2 | 4 |
| vacated | 81 (75 / 6) | 62 (62 / 0) | 14 (8 / 6) | 2 | 2 | 1 |
| mixed | 8 | 6 (5 / 1) | 1 | 0 | 0 | 1 |
| affirmed | 86 (80 / 6) | 62 (61 / 1) | 14 (10 / 4) | 6 | 2 | 2 |
| reviewDismissed (DIG) | 9 | 6 (5 / 1) | 0 | 3 | 0 | 0 |
| certDenied | 141 (106 fed., 33 state, 2 none) | 87 (86 / 1) | 33 (9 / 24) | 10 | 1 | 9 |
| **all** | **493** | **338** (69% of dockets with a judgment) | 92 | 36 | 7 | 17 |

The other 3 dockets (2 reversed, 1 certDenied) failed the Supreme Court caption check. 19 dockets had no judgment
entry on the node date. By system: federal 337 of 431 dockets with a judgment linked (78%); state 1 of 60 (the
state corpus ends in 2019); 2 dockets had no lower court.

After dropping builder-seen nodes (82 pairs): **256 pairs, 256 Supreme Court nodes** (every keyed node is
"complete": all its dockets linked). Spot check of 8 random pairs (lower caption, date and docket against the
docket record): 8/8 right.

## 4. The key (sizes only)

`key/timesplit_key.tsv` (sha1 0dcd46414f4b51ac3d0063840a3a91fc8dae603e): columns order_node, lower_node, kind, sub,
order_date, lower_date, lower_court2, system, link, sc_docket. `key/timesplit_orders.tsv` (sha1
121129d5faca727f122822af2ab64f1c9b2529bb). `key/timesplit_stats.tsv` (aggregate counts).

| order year | reversed | vacated | mixed | affirmed | reviewDismissed | certDenied | total |
|---|---|---|---|---|---|---|---|
| 2021 | 23 | 8 | 0 | 6 | 2 | 20 | 59 |
| 2022 | 16 | 6 | 0 | 6 | 0 | 10 | 38 |
| 2023 | 7 | 7 | 2 | 7 | 0 | 11 | 34 |
| 2024 | 9 | 9 | 1 | 8 | 1 | 9 | 37 |
| 2025 | 15 | 8 | 0 | 7 | 1 | 16 | 47 |
| 2026 | 13 | 9 | 0 | 12 | 0 | 7 | 41 |
| **total** | **83** | **47** | **3** | **46** | **4** | **73** | **256** |

Sub-kinds: affirmed 45 + 1 by an equally divided Court; mixed 3 (affirmed/vacated, reversed/vacated in part).
Lower decisions dated 2018–2025 (2018: 4, 2019: 16, 2020: 30, 2021: 21, 2022: 22, 2023: 26, 2024: 27, 2025: 14);
federal 255, state 1; link exactDate 252, nearDate 4. Negative pairs (reversed + vacated): 130.

## 5. The scorer: `score_heldout.py`

```
python -I round7/heldout/score_heldout.py --status <out>/status.tsv --history <stage>/history.tsv \
       --certs <out>/certs.tsv --label <name>
```

Measures (Wilson 95% intervals throughout; aggregate output only, written to `results/<label>/tables.tsv`):
- **link**: an admitted history row (certs.tsv first verdict `ok…`) by the Supreme Court node O on the lower node L;
- **kind**: such a row of the right kind (mixed: a reversed/vacated/affirmed/modified row whose scope is not `all`);
- **effect (row)**: the admitted rows O→L give NEG (negative kind, scope all), PART (negative kind, other scope) or
  NONE; expected NEG for reversed/vacated, PART for mixed (lenient NEG or PART), NONE for affirmed / DIG / denied;
- **effect (status at d)**: L's decision-level status line covering the order date d — strict: `neg:*`
  (reversed/vacated) or `unknown:*` (mixed) on path `history` with actor O; lenient: `neg:*`/`unknown:*` on path
  `history` with any actor; for affirmed / DIG / denied: no history-path negative or unknown status with actor O;
- tables by expected kind, by lower-court system and by order year (negative kinds), by link method; the status
  class of L at d and the row-effect counts per kind;
- **precision side** (complete orders only): of all admitted history rows by a key Supreme Court node, the share
  that point to a key lower decision of that node (the rest point to another decision), by row kind and by rule
  family (src prefix); of rows on a key pair, the share with the right kind; count of negative-kind rows on an
  affirmed / dismissed / denied pair.

Every run appends one line to `RUNS.log`: time, label, arguments, sha1 of key, status, history and certs, sha1 of
the result tables. Guards on the real key: refused unless `round7/FREEZE.md` exists; refused when `RUNS.log`
already has a run of this key on the same `status.tsv` unless `--again '<reason>'`.

**Tested only on a synthetic fixture** (`fixture/make_and_check.py`: made-up 8-digit node ids, 9 pairs covering
every kind, rejected rows, wrong targets, wrong kinds, another actor, a non-history path, an issue-level line, an
incomplete order): 36 checks pass. The fixture runs are the `fixture-selftest` lines in `RUNS.log`; one refused
guard test (no FREEZE.md) read nothing and wrote nothing. **No real model output has been scored.**

## 6. Rule: scored once

The lead runs the scorer **once on the round-6 frozen build and once on the round-7 frozen build**, after
`round7/FREEZE.md`, and on nothing else:

```
python -I round7/heldout/score_heldout.py --status round6/history/out/final2/status.tsv \
  --history round6/history/stage/final2/history.tsv --certs round6/history/out/final2/certs.tsv --label r6-final2
python -I round7/heldout/score_heldout.py --status round7/out/<frozen>/status.tsv \
  --history round7/stage/<frozen>/history.tsv --certs round7/out/<frozen>/certs.tsv --label r7-<frozen>
```

No per-pair output exists or may be produced; results are not used to change any rule. A further run needs the
lead's decision and is logged with its reason.

Known limits: small for mixed (3) and DIG (4); federal only; 2021+ Supreme Court nodes are opinions, so order-list
GVRs are not in the test; the "seen" filter is generous (it drops any node number named in a read file).

## 7. Shadow Docket Database (handed over)

Downloaded first (CC0 1.0, Harvard Dataverse doi:10.7910/DVN/89VEX8; files and sha1 in SOURCES.md), then handed
over on the lead's ruling (22:56): the `benchmarks` agent owns that key. Only an order-side exploration was run
(aggregate counts); `build_key.py` was never run and no Shadow key exists.
