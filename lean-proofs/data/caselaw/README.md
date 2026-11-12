# Data behind "Formalizing all US case law in Lean"

The rules of precedent in Lean (`../../LegalProofs/USCaseLaw/`) run over the US case law of global-law: 6,892,454
decisions and 48,318,876 citations between them. The scripts are in `../../tools/caselaw/`. The reader of the decisions
was frozen before the held-out checks (v2, lean-proofs commit f9c37b4baa6); the published run is v3 (125708fb16c), v2 plus
combined opinion texts and rehearing opinions.

## Pipeline

1. `tools/caselaw/extract.py <repo> <out>` reads each case-law repo at HEAD (front matter, cited cases, and a window around
   every "overrul" or "disapprov").
2. `tools/caselaw/graph.py` builds the citation index (parallel citations and parallel-reporter copies merged) and the
   citation edges; `tools/caselaw/courts_map.py` places every court in a system, tier and circuit.
3. `tools/caselaw/events.py` sorts the windows into **acts** (a decision overruling or disapproving an earlier one in its
   own majority opinion: the facts given to Lean) and **reports** (later courts' notes that a decision was overruled:
   held back, to test against).
4. `tools/caselaw/encode.py` writes the Lean inputs; `lake env lean --run LegalProofs/USCaseLaw/Run.lean` decides which
   acts are valid, checks every citation, and answers every report.
5. `tools/caselaw/results.py` and `figure.py` aggregate; `LegalProofs/USCaseLaw/RunStatutes.lean` runs the statute check.

## Files

- `results/summary.json`: totals (decisions, citations, acts and their validity, report verdicts, by system).
- `results/graph_stats.json`, `results/court_table.tsv` (3,160 court names with system, tier, circuit, rule),
  `results/court_unmapped.tsv` (26 courts, 1,285 decisions).
- `results/by_system.json`: per court system, decisions, accepted overrulings, notes naming the overruling decision, and
  notes Lean agrees with.
- `results/corroborated_overrulings.tsv`: the 4,355 overrulings stated by the overruling court, valid in Lean, and named
  by at least one later court; `results/cited_after_overruled.tsv`: citations of each after it was overruled by a court
  binding the citing court (54,560 in all); `results/corroborated.json`.
- `events/acts.tsv` (overruling decision id, overruled id, form, passage), `events/reports.tsv` (deciding id, decision
  said to be overruled, overruling decision named or empty, qualifier, passage), `events/counts.json`.
- `lean/acts_verdicts.tsv` (validity of each act), `lean/reports_verdicts.tsv` (match / other / none for each report),
  `lean/courts.tsv` and `courts_named.tsv` (the court table by era, as given to Lean).
- `audit/`: the samples and the agents' readings: `reports_*` (blind reading of 120 named overrulings), `acts_*` (120 acts,
  development audit of reader v1), `acts2_*` (120 acts Lean accepts, held-out audit of reader v2), `citing*` (citations
  of overruled decisions: `citing2_*` uses the corroborated set).
- `reference/crs2016.tsv`: the Constitution Annotated table of Supreme Court decisions overruled by later decisions (2016
  revision, GPO), transcribed: 236 entries, 322 pairs.
- `statutes/`: every decision's applied US Code section with its version (`statutes_rows_pl.tsv`), the section histories
  (`section_versions_pl.tsv`) and Lean's answer (`statutes_out_pl.tsv`: changed since, number of changes, first change).

Decision ids are the line numbers of the graph's `nodes.tsv` (repo, path, court, date, citations, name), rebuilt by step 2.
Court opinions are public domain; the source data is CC0.
