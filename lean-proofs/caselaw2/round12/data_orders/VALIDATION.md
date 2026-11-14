# Validation (orders12, round 12, 2026-11-14)

No key read. Parser = round 11's `parse_jnl.py` unchanged (copy in `round12/agents/orders12/scripts/`); per-row files
in `round12/agents/orders12/work/val/`, `work/ligm/`.

## 1. Ligature repair (re-extraction)
- Jnl19-Jnl25 re-fetched: every sha256 equals round 11's (same files). Glyph-aware texts vs round 11's texts: same line
  count in every Term; every difference is one "f" that became U+FB01 / U+FB02 (Jnl19 658, Jnl20 580, Jnl21 601,
  Jnl22 567, Jnl23 494, Jnl24 511, Jnl25 586 substitutions on 489-637 lines per Term); 0 other differences.
- New Terms vs a plain extraction of the same PDF: Jnl18 619 substitutions, Jnl17 12, Jnl15 4, jnl10-13 0; 0 other
  differences.
- After the repair: 0 occurrences of "affrmed", "Offce", "fle", "Griffn" in any repaired text (before: e.g. Jnl22
  21 / 44 / 215 / 9).
- Not re-extracted (jnl04-09, jnl14, Jnl16, held by round 11): residual check = tokens with an "f" seen <= 3 times in all
  held Journals that become a word seen >= 5 times when one "f" is read "fi" or "fl": 0 real cases (one name "Raff"
  in jnl09 / jnl14); the same check on repaired Jnl25: 0.
- Re-parse of all held Journals (100,413 entries) with the repaired texts: 0 class changes, 0 docket changes, 0 node /
  not-node flips, entry ids unchanged; 2,781 entries' texts changed (captions 1,314, court-below names 163,
  disposition words 28), all in Jnl19-25.

## 2. New Terms (OT2010-13, OT2015, OT2017-18): parser vs corpus S. Ct. nodes, two months
| measure | 2012-03 (jnl11) | 2018-11 (Jnl18, repaired) |
|---|---|---|
| Journal entries of the month | 660 | 379 |
| entries whose docket(s) match a corpus 2906 node of the month | 652 (98.8%) | 367 (96.8%) |
| ... same date | 648 (99.4%) | 366 (99.7%) |
| corpus 2906 nodes of the month / matched by an entry | 628 / 627 | 429 / 426 |
| caption party-name overlap >= 0.5 | 529 of 652 | 336 of 367 |
| class agreement vs a crude word classifier on the corpus text | 596 of 652 | 337 of 367 |
| Journal GVR entries -> corpus text GVR-worded | 13 of 13 | (no GVR that month) |

Unmatched Journal entries are argued-case "other" entries (oral argument days: the corpus holds the opinion, not an
argument order) and original-jurisdiction dockets ("140, Original" vs the corpus "140"): the same pattern round 11 saw
on OT2016. Disagreements are mostly "other" Journal entries (motions printed with cert denials in one corpus text) and
Opinion-section entries whose corpus text is the opinion.

## 3. Loader check
`round12/nodes12.py` `activate('round12/data_orders')`: 1,871 nodes, node count 6,894,325 (= 6,892,454 + 1,871); every
text file UTF-8, LF, one final LF, no tab / CR / BOM; local ids unique; rows 1-1,045 have round 11's local id, docket,
date, list_file and line_span in the same order (checked with `diff` against `round11/data_orders/nodes.tsv`).
