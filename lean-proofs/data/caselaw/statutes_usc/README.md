# Statute check over the whole US Code (section 7 of "Formalizing all US case law in Lean")

Every decision in the US case law of global-law decided since 1995-01-04 (2,264,938), read for the US Code sections it
cites (`tools/caselaw/usc_extract.py`, the citation reader `usc_cite.py` of global-law's judgment overlays), against
every version of every section in lexifina/united-states-law (main a4c5f91, all 53 titles from the 1994 edition;
`usc_versions.py`). `usc_encode.py` gives Lean each section's versions (day, made by a law or an edition, ids of the
words of the section and of the cited subsection); `LegalProofs/USCaseLaw/RunStatuteText.lean` answers, for each
citation on 2026-11-12: amended since by a law, the section's words differ, the cited subsection's words differ.
`usc_results.py` and `usc_figure.py` aggregate.

- `citations_verdicts.tsv.gz`: decision id (line of the graph's nodes.tsv), decided, section, subsection cited, amended
  since by a law (0/1), number of such laws, first law since, section words differ, cited words differ.
- `section_versions.tsv.gz`: section file, commit, law|edition, law, in force (yyyymmdd), blob, short title.
- `summary.json`, `changed_words.json` (citations whose cited words a law has since rewritten; by year; laws),
  `laws.tsv`, `sections.tsv`, `titles.tsv`, `survival.tsv` (share of cited sections not yet amended N years after).
- `audit/`: 100 citations Lean flags and 50 at random, read by an agent (`usc2_audit_in_*` given, `usc2_audit_out_*`
  readings, `usc2_audit_key.json`); `audit_summary.json` tallies them. `make_audit.py` drew the sample.
