2026-11-14 03:48:32 GMTST start: read brief, contract; df C: 27G avail
2026-11-14 03:51:52 GMTST source pick (web fetches used: 3 of 25; all Dataverse API).
  CHOSEN: Federal Circuit Dataset Project, document dataset (Rantanen, U. Iowa), Harvard Dataverse doi:10.7910/DVN/UQ2SF7,
    v9.0 (2026-07-06), licence CC0 1.0, no terms of use, no restricted files. File "2025-12-31 CAFC documents annual export.tab"
    (29,240 docs 2001-2025) + codebook docx. Variable: DispGeneral (human-coded CAFC disposition of the decision under review),
    with origin/TribOfOrigin. Test = same-case: decision below (CFC, CIT, CAVC, district courts) reversed/vacated vs affirmed.
    Why: human-coded, CC0, and the Federal Circuit + its tribunals of origin are outside every existing key's population
    (FJC IDB has no Federal Circuit; Songer/Shepardized are the regional circuits; Brace&Hall/state tables are state).
    Corpus: cafc repo to 2026; CFC (court 670) to 2018, CIT (671) to 2019, CAVC (665) to 2017, district courts to 2019.
  REJECTED: Lindquist (DUA); Beim-Hirsch-Kastellec en banc zip (contents/years unknown, small, partly CCAD-derived);
    Larsen en banc (author asks to be contacted; contents unconfirmed); California review-granted list (no citation,
    mostly post-2020, per-page scraping); Gibson&Nelson / Ash&MacLeod state supreme court deposits (contents unknown,
    disposition var unconfirmed, more effort); unused pre-1930 IA tables (heavy OCR, same family as state_overruled_tables);
    SCDB lcDisposition / CCAD disposition (same rows as used keys or model-coded).
2026-11-14 03:54:25 GMTST MAPPING.md written (before any linking); parse_source.py -> 7,161 key items; running link.py
2026-11-14 03:54:56 GMTST first link run: 1842/7161 linked (1314 cited). Read 36 sampled pairs: cited sound, 2/12 caption links wrong -> Amendment 1 (uncited two-sided: each side >= min(2,len) tokens). No model row read.
2026-11-14 03:56:47 GMTST Amendment-1 relink: 1811/7161 linked (1314 cited); 1724 units (h0 852, h1 872). score.py self-test on fake/ passed (check_fake.py 0 failures). SOURCE.md, REPORT.md, READY written. Web fetches used: 3/25. No model output read, no build scored, nothing committed.
2026-11-14 03:56:52 GMTST NOTE: REPORT.md not written - the harness refused the write (subagent report-file rule); link figures are in benchmarks/fedcir_dataset/link_summary.json and in the final message to the lead.
