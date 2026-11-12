# (11) Watch lists — progress

Goal: alert a user when a US Code section they depend on changes; show the diff and the law that made it. Feeds a
new subsection of the blog post (BLOG.md here).

## Pieces
- `tools/caselaw/usc_watch.py` (lean-proofs): watch list or document in; terminal report, `--json`, `--html`,
  `--digest FROM TO`. Reads versions.tsv + usc-full.git (git cat-file --batch), the law's own per-section notes from
  the commit message, word diffs, repeal / removal / move detection.
- `LegalProofs/USCaseLaw/Watch.lean`: `alerts`, `notices`, `alert`, theorems `alerts_mono`, `alert_mono`,
  `alert_byLaw`, `alert_mem_lawChanges`, `no_law_no_alert`, `no_alert_same_words`, `no_alert_subDiffers`,
  `no_alert_wordsDiffer`; `#guard` examples. No sorry. Checked with `lake env lean`.
- `LegalProofs/USCaseLaw/RunWatch.lean`: batch runner (`lake env lean --run`). Needs Watch.olean: built with
  `lake env lean -o .lake/build/lib/lean/LegalProofs/USCaseLaw/Watch.olean -i ...Watch.ilean LegalProofs/USCaseLaw/Watch.lean`
  (no `lake build`). Rebuild that olean after any change to Watch.lean.

## Status
- [x] Lean model + proofs + runner
- [x] usc_watch.py (list, document, digest; text/JSON/HTML)
- [x] demos: opinion (Texas v. United States, 809 F.3d 134), firearms/drug sentencing list, bankruptcy list,
      top-25 and top-100 digests for the last 12 months of the record
- [x] timing (timing/)
- [x] figure (figure.svg, from figure.py), BLOG.md

## Layout
- lists/: the watch lists. demo_opinion/, demo_practice/, demo_top25/: .txt (terminal), .json, .html per demo.
- run_demos.sh re-runs every demo. timing/: JSON of the timed runs, timing.md the numbers.
- Not committed anywhere (per instructions).

## Known weaknesses
- Alerts depend on the record's credit: undated law changes are credited to editions (21 U.S.C. 841(b)(1)(A), First
  Step Act -> 2018 edition) and appear only as notices; notices changing >= 20 words are flagged "review".
- Below the subsection, designations are found by heuristics on the printed text (shallowest match, sibling or
  shallower line ends it; "(l)" read as "(1)"; "553(b)(3)(A)" read as "(b)(A)"); on failure the parent is watched.
- Moves are detected (same-day new section with >= 60% word overlap) but not followed into the new section.
- "No alert" theorem needs the history in date order (runner reports it: always true so far).
- Watch.olean is built by hand (lake env lean -o); RunWatch fails if it is stale or missing.
