# round12/data_orders: Supreme Court order nodes from the Journal of the Supreme Court (round 12)

Owner: `orders12`. Base: `round11/data_orders` (README there: source, node classes, text format). Format:
`FORMAT.md` (round 11's + the optional `src` column). Scripts: `round12/agents/orders12/scripts/` (all run with
`python -I`; downloads were kept in `round12/agents/orders12/dl/<name>/`, one fresh folder per request, PDFs deleted
after their sha256 was checked against SOURCES.tsv and the text written).

## Contents
| file | what |
|---|---|
| `nodes.tsv` | 1,871 rows: rows 1-1,045 = round 11's nodes (same local ids, order, docket, date, list_file, line_span; `src` `-`); rows 1,046-1,871 = 826 `r12:longlist` nodes (step 3) |
| `text/` | one text per row (round 11's bytes except the 57 in `CHANGED.tsv`) |
| `CHANGED.tsv` | the 57 round-11 nodes whose text changed (local id, old sha1, new sha1, what changed) |
| `journal/` | Journal texts changed or added in round 12: Jnl19-Jnl25 (ligature-repaired), jnl10, jnl11, jnl12, jnl13, Jnl15, Jnl17, Jnl18 (new). jnl04-09, jnl14, Jnl16 are read in place from `round11/data_orders/journal/` (unchanged) |
| `SOURCES.tsv` | round 11's 20 lines + 14 round-12 requests (all 200) |
| `counts.tsv` | per year: every parsed entry by class, node-class entries by court below, nodes by provenance |
| `longlist_report.tsv` | step 3 decision per candidate entry (corpus node, other dockets in its docket field, outcome) |
| `VALIDATION.md`, `HANDOFF.md`, markers `LIGATURE_READY`, `DATA_READY_A`, `DATA_READY` | |

## Step 1: the dropped ligature (repaired by re-extraction)
**Cause.** In Jnl17-Jnl25 (and a few fonts of Jnl15) the embedded Type1 fonts' `/Encoding /Differences` name code
174 `/fi` and code 175 `/fl` (the ligature glyphs that are drawn), but the fonts' `/ToUnicode` CMaps map both codes to
"f". Every extractor that trusts ToUnicode (PyMuPDF, pdftotext) prints "affrmed", "fle", "Offce", "Griffn", "Rife"
(Rifle), "Netfix". The "ff" ligature was not affected (separate letters), "fi" and "fl" were.

**Rule (glyph-aware re-extraction, `pdf2txt_lig.py`).** For each font dict that has both a `/Differences` array and a
ToUnicode CMap, each code whose glyph name is a ligature (ff, fi, fl, ffi, ffl) and whose ToUnicode target is neither
the ligature code point nor its letters is remapped to the ligature code point (U+FB01 / U+FB02), in memory only; the
text is then extracted with exactly round 11's call (`get_text('text', sort=False)`, form-feed page lines), so lines
and line numbers are identical and the parser's existing ligature expansion (ﬁ -> fi) gives the words. Jnl19-Jnl25
were re-fetched for this (7 requests; sha256 identical to round 11's), Jnl15/17/18 are new. Remapped CMap entries:
Jnl18 590, Jnl19 714, Jnl20 796, Jnl21 734, Jnl22 792, Jnl23 2,092, Jnl24 866, Jnl25 726,
Jnl17 76, Jnl15 10, jnl10 2 (unused codes), jnl11-13 0. The vocabulary rule of the brief was not needed; it would
also have mis-repaired names (e.g. "Sharif" -> "Sharifi", "Steinfeld" -> "Steinfield" are real repairs here that a
vocabulary rule cannot decide).

**Counts.** Jnl19-25: 3,997 words repaired (507 distinct). Re-parse of all held Journals: 0 class changes, 0 docket
changes, 0 node / not-node flips (the parser already accepted "affrmed"), so no node appears or disappears; 2,781
entries' texts changed (1,314 captions, 163 court-below names, 28 disposition words). Nodes: **57 of 1,045** texts
changed (21 captions, 25 disposition-word columns updated in nodes.tsv) -> `CHANGED.tsv`; same local ids (DESIGN12 §4).
Journals not re-extracted (jnl04-09, jnl14, Jnl16): no residual drop found (VALIDATION.md).

20 examples (round 11 text -> round 12 text; seeded random sample of the 507 distinct repairs):

| round 11 | round 12 | where |
|---|---|---|
| `Affliated` | `Affiliated` | Jnl22 line 11204 |
| `Cofeld,` | `Cofield,` | Jnl25 line 8663 |
| `Goffn,` | `Goffin,` | Jnl21 line 662 |
| `Hatfeld` | `Hatfield` | Jnl19 line 13881 |
| `Hempfing,` | `Hempfling,` | Jnl22 line 22226 |
| `Malftano,` | `Malfitano,` | Jnl19 line 29306 |
| `Medfeld,` | `Medfield,` | Jnl25 line 20621 |
| `Moffte,` | `Moffite,` | Jnl20 line 12382 |
| `Pacifc,` | `Pacific,` | Jnl20 line 11588 |
| `Pfieger.` | `Pflieger.` | Jnl20 line 6485 |
| `Pfugner` | `Pflugner` | Jnl22 line 29571 |
| `Rife` | `Rifle` | Jnl19 line 732 |
| `Salf,` | `Salfi,` | Jnl24 line 3262 |
| `Sharif` | `Sharifi` | Jnl22 line 1054 |
| `Steinfeld` | `Steinfield` | Jnl23 line 27532 |
| `Teoflo` | `Teofilo` | Jnl19 line 17687 |
| `Traffc` | `Traffic` | Jnl21 line 22019 |
| `Warterfeld,` | `Warterfield,` | Jnl21 line 15489 |
| `exemplifed` | `exemplified` | Jnl21 line 22702 |
| `fnally` | `finally` | Jnl22 line 18643 |

## Step 2: missing Journal Terms
Fetched OT2010 (jnl10), OT2011 (jnl11), OT2012 (jnl12), OT2013 (jnl13), OT2015 (Jnl15), OT2017 (Jnl17), OT2018 (Jnl18),
file names from the `/orders/journal.aspx` page round 11 fetched (`round11/agents/orders11/dl/idx2/`). Parsed with round
11's parser (53,511 entries; node classes: gvr 581, affirmed 18, vacated 11, granted_remanded 3, order_vacated 2 =
615). Round 11's rule (an entry of a node class becomes a node when one of its dockets has no corpus court-2906 node
within +-10 days), run over every held Journal (153,924 entries): **0 nodes added**; all 615 new node-class entries
(and 1,156 of the held Terms, as in round 11) have a corpus S. Ct. node of every docket within +-10 days: the corpus
holds the S. Ct. memorandum orders of 2010 - mid 2020. Parser validation on 2012-03 and 2018-11: VALIDATION.md.

## Step 3: the 2005 long lists (src `r12:longlist`)
**Finding.** All 840 node-class Journal entries of 2005 (all GVR) have a corpus S. Ct. node of their docket on the same
date, but those corpus nodes are mostly one text for a printed list of many cases: the node's docket field (and text)
lists many other dockets (97 distinct nodes; per entry, the most other dockets of a corpus node of its docket within
+-10 days, counted in the docket field: 0-2: 92 entries, 3-9: 37, >= 10: 711; node 6230687 of 2005-01-24, the Booker GVR list,
holds 357 dockets and covers 344 entries). Other years with corpus S. Ct. orders: >= 10 only in 2012 (53 entries; the
node 6262190 of 2012-06-29 holds 40 of them), 3-9 in 2011 (2) and 2012 (23); 0-2 elsewhere. h0 (counted only; never
read by the rule): of the 2005 NEG / PART GVR orders missed by v11d, 97 of 117 are in a corpus node of >= 10 other
dockets (the agree rate there is 172 of 265, 65%).

**Rule.** A node-class Journal entry that is not already a node, every docket of which has a corpus court-2906 node
within +-10 days, and one of whose dockets' corpus nodes within +-10 days lists **k >= 10** other docket numbers in its
docket field, becomes a per-entry node (the Journal entry's own text, as for every node), `src` `r12:longlist`. Rows
1,046-1,809 (764: 2005 711, 2012 53) are the k >= 10 group; rows 1,810-1,871 (62: 2005 37, 2011 2, 2012 23) are the
3 <= k <= 9 group, appended last so a consumer that wants only k >= 10 can cut `nodes.tsv` after row 1,809 (and drop
those 62 text files) without moving any node id. Not added (k <= 2): 945 entries. Every long-list node's corpus list
node is named in `longlist_report.tsv`.

## Lower courts named (node-class entries, all held Terms)
federal circuit 2,283, federal district 36, state 467, none 30 (per year in counts.tsv). The 826 long-list nodes:
federal circuit 814 (2005 744, 2012 70), state 12 (2005 4, 2011 2, 2012 6). Remand reasons printed: "in light of United
States v. Booker" 739 (2005), "Dorsey v. United States" 53 (2012), others <= 8 each.
