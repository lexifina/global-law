# Cross-references in the US Code over time (uses/xrefs)

Status: done (2026-11-12). Final run = v3 (`v3frozen/` is the frozen copy the held-out audit was drawn from; a re-run
reproduces it byte for byte). BLOG.md drafted; figure `xrefs.svg`.

## Pipeline (`run_all.sh` re-runs everything, ~3 minutes, 4 workers)
1. `tools/caselaw/usc_xrefs.py scan` (in global-law-lean/lean-proofs): every distinct (section, text) in
   `usc/versions.tsv` (126,137) from `usc-full.git`: designation tree (repairs misprinted indents; inline "(A)...(B)"
   as soft paths; per-line designations for an indent-free check), duplicates, explicit references. `data/scan.pkl`.
2. `usc_xrefs.py build`: one row per (referring section, target section, designation path) ever made (195,773), with
   the referring section's dated versions (makes it or not) and the target's (live; which of the named paths it has,
   by tree or by reading designations in order). `data/lean_in_{0..3}.tsv`, `data/rows.tsv`.
3. `run_lean.sh`: compiles `LegalProofs/USCaseLaw/CrossRefs.lean` into `olean/` (no `lake build`), runs
   `RunCrossRefs.lean` on 4 shards: status on the first day judged and every day the source or target has a
   version (the only days it can change, by `status_stable`), plus each year end.
4. `tools/caselaw/usc_xrefs_report.py`: episodes, causes, tables. `tools/caselaw/usc_xrefs_figure.py`: the figure.

## Headline (v3)
- 152,597 references in force on 2026-11-12; 3,278 dangle (2.15%). 1996: 2,113 of 94,776 (2.23%).
- Today's dangling by reason: designation missing 1,311; target repealed 678; file removed 602; never in record 573;
  designation repealed 101; transferred 8; vacant 4; reserved 1. By class: at record start 1,164; broken later
  1,269 (law 656, edition 613); written dangling 845 (law 544, edition 301).
- Episodes since 1995: 3,566 broken later (300 laws), 2,928 written dangling, 2,824 at start. Broken: median 343 days
  to end, 2,110 ended by the referring text changing, 187 by the target coming back.
- Top: Pub. L. 113-287 (title 54) broke 726 in one day, 693 rewritten 2015-01-05, 32 open. Still-open breaks:
  Dodd-Frank 32, title 54 law 32, TCJA 29, ACA 24, Farm Bill 2014 23, HERA 22.
- Duplicates today: 181 in 151 sections; 642 ever.
- 28 U.S.C. § 2255 (Pub. L. 110-177 relettering): 8 Code references into § 2255, all to the whole section; none broken.
- Example: 18 U.S.C. § 2101(b) "subparagraph (A), (B), (C), or (D) of paragraph (1) of subsection (a)", dangling since
  Pub. L. 104-294 (1996-10-11); official Code footnotes it "So in original" (checked on law.cornell.edu, which
  reproduces the OLRC text). Encoded as a `#guard` example in CrossRefs.lean.

## Audit (audit/)
- v1 sample 60 (`sample_dangling_today.tsv`, verdicts A1-A60): 37 real, 13 tree, 9 parser, 1 other. Fixes after it:
  sibling-class indent repair (v2), in-order designation check, lists "(j)(2)(A)(i), (ii)", chain applies to the
  first section only, case-insensitive targets, digit-only ranges, "as such sections are in effect", bracketed
  translations. Still flagged in v3: 43, of which 35 real. `score.py` scores it.
- Held-out 40 from frozen v3 (`sample_heldout.tsv`, `verdicts_H.tsv`): 27 real (68%, Wilson 52-80%). sec/usc/bare
  24/29; sub 3/11 (bare "subsection (x)" naming another section mentioned earlier).
- So in original: of 64 real, 2 "So in original", 53 explained by an editorial note, 9 unmarked.
- Duplicates (20): 13 real; 7 record indent artifacts. Of the 14 still flagged in v3, 13 real.
- Broken-later episodes (20): all resolved the day before; cause confirmed 18; 4 dating artifacts (one law, two
  dates in the record); 1 wrong end.

## Known weaknesses
- Bare "subsection (x)" that belongs to another section named earlier (main parser error).
- Record indentation errors; record lacks pre-1995 repealed sections and deletes some omitted ones.
- DEAD_HEAD reads a caption starting "Transferred ..." (26 U.S.C. 6901 "Transferred assets", 22 U.S.C. 3671) as a transferred stub: all 8 "transferred" today are wrong.
- Not read: relative refs ("paragraph (2)", "of this paragraph"), chapters, other Acts. Definitions-scope (task 5)
  not done.
- Pre-2017 record dates are enactment dates; some editions carry changes the record cannot credit to a law.
- Label quirk: versions.tsv short title for Pub. L. 104-208 reads "Magnuson-Stevens ..." (it is the Omnibus
  Consolidated Appropriations Act, 1997).
