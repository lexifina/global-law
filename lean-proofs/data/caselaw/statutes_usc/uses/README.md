# Further uses of the statute record

Results behind section 8 of "Formalizing all US case law in Lean". Each folder has the BLOG.md draft, PROGRESS.md
(how it was run) and the results; scripts are in `tools/caselaw/uses/<name>/` and `tools/caselaw/usc_watch.py`,
`usc_xrefs*.py`; Lean models in `LegalProofs/USCaseLaw/{Overrides,AmendmentCheck,CrossRefs,Recodification,Watch}.lean`
with runners `Run*.lean`.

- `overrides/`: decisions followed by the first law to rewrite the words they cited, with evidence (the law or a
  committee report names the decision, or the decision quoted words the law struck); `overrides.tsv`, `confirmed.tsv`,
  recall against Christiansen & Eskridge (2014) and Hasen (2013), audits.
- `amendments/`: every amending instruction in the 812 public laws of 2013-2026 (GovInfo USLM), run against the record;
  `data/results.tsv.gz`, `out/summary.json`, audits; `bills/`: five pending 119th-Congress bills dry-run.
- `xrefs/`: cross-references in every version of every section, resolved against the Code on each day; dangling today,
  history, duplicates, laws that broke references, audits.
- `recodification/`: titles 36, 40, 41, 46, 51, 54 checked against the official disposition tables.
- `watch/`: watch-list demos (an opinion, practice lists, top-cited digest) and timing.
- `visual/`: the four-panel figure's tables (change per Congress, growth, authorship, citations after a rewrite).

Large intermediates (Lean inputs, scans, candidate rows) are not kept; the scripts rebuild them from the record.
