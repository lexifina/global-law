# uses/amendments — progress

Task: (5) run real laws' amending instructions against the record and classify each; (7) dry-run pending bills.
Status (2026-11-12): done. Draft write-up in `BLOG.md`. No figure (the table carries it).

## Pipeline
- Source: GovInfo PLAW USLM XML, all 812 record laws of the 113th-119th Congresses (cached in `cache/`; hits copied
  read-only from the US Code history build's cache). Pre-113th: no PLAW USLM; enrolled-bill XML exists for some laws
  only (112th HR 3630 yes; 110th HR 4986, 111th HR 3590 no). Out of scope.
- `tools/uslm_laws.py`: vendored lexifina `services/us_code_history/laws.py`, LOCAL edits marked (hyphen/en-dash
  section hrefs, "striking X before Y", "adding after subsection (b)", "the first place it appears", capital "In").
- `tools/billdtd.py`: GPO bill DTD -> USLM translator. Check: enrolled S. 2938 vs Pub. L. 117-159 USLM, 61/62
  instructions identical (other: heading punctuation in quoted text).
- `tools/record.py`: record markdown -> lines with designation paths (indent depth + list-continuity scoring).
- `tools/build_input.py`: lowers ops, Act-cite prefixes ("Section 8(a) of the Act (22 U.S.C. 9307)"), heading /
  sentence scopes, "both places"; picks the record versions before/after each law; writes Lean input (4 shards).
- Lean: `LegalProofs/USCaseLaw/AmendmentCheck.lean` (checks clean with `lake env lean`) and
  `LegalProofs/USCaseLaw/RunAmendmentCheck.lean`. Run via `tools/run_lean.sh` with a private olean in `olean/`
  (no lake build; the runner needs AmendmentCheck's olean, which lives only in `olean/` until the import is wired).
- `tools/pipeline.sh [skip-extract]` -> `data/results.tsv` (one row per operation, Lean's outcome).
- `tools/tabulate.py [--samples]` -> `out/summary.json`, `out/sample_*.tsv`.
- `tools/olrc_notes.py` -> `data/olrc_notes.tsv` (OLRC "could not be executed" / "probable intent" notes, 2023+2024
  editions); `tools/olrc_xcheck.py` -> `out/olrc_xcheck.json`, `out/olrc_agree_examples.tsv`.
- `tools/bills.py` -> `bills/ops.json`, `bills/summary.json` (5 bills).
- Audit helpers: `tools/show.py`, `tools/law_text.py`.

## Headline (final run; main scope = law credited with a change to the section: 39,666 ops, 11,294 law-section pairs)
- applied+record shows 30,325 (76.5%); applied, record differs 3,709 (9.4%); no_target 1,582 (4.0%); not_found 1,198
  (3.0%); ambiguous 404 (1.0%); wrong_target 260 (0.7%); unsupported 2,083 (5.3%); unchecked 105.
- Whole-section replay == record: 6,075 / 11,294 (54%).
- Positive-law titles: 83.5% applied+matches, 1.2% not found; other titles 72.1%, 4.1%.
- OLRC "could not be executed" pairs in run: 86; Lean flags a failure class in 69 (80%).
- All ops: 50,010 from 48,762 instructions (incl. chapter-level, section not in record, no law commit).

## Audit (20 per class; agents read Act + record)
- Round 2 (final run): applied_matches 20/20 correct; record_differs 12/20 real (10 editorial, 2 record);
  wrong_target 9/20 real (6 drafting); ambiguous 7/20 real (all drafting). Files `out/audit_*.tsv`.
- Round 1 (previous run, before word boundaries / heading+sentence scope / case-folded check): not_found 18/20 real
  (16 Code editorial text, 1 drafting, 1 record); no_target 4/20 real (2 drafting); applied_matches 20/20. Files in
  `out/audit_round1/`. The current `out/sample_not_found.tsv` / `sample_no_target.tsv` are unaudited redraws.
- Drafting estimate ~440 (Wilson-bound sum 166-1,123).

## Known weaknesses (not fixed, to keep the audit valid for the reported run)
- "after/before the semicolon" when a provision ends "; and"; redesignations inside parentheticals; title-wide renames.
- Title Case fold heuristic makes "The Secretary" case-insensitive (spurious ambiguity).
- Inline designations not split; whole-section add/repeal and sentence rewrites unsupported.
- Bills' status not verified on congress.gov (found by search; believed in committee).
