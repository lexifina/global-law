# bench_songer notes (round 9)

- 2026-11-14 02:11:07 start; read BRIEF + CONTRACT; created benchmarks/songer_treat/
- 2026-11-14 02:11:48 downloaded cta96 + KH update stata zips and codebooks over http (TLS cert expired; no verification bypass), extracted with python -I
- 2026-11-14 02:12:22 read codebooks (PRIORPUB, TREAT, METHOD, SOURCE, ORIGIN); writing .dta reader
- 2026-11-14 02:14:44 parsed dta (18195 + 2160 rows); PRIORPUB reporter census done; reading corpus layout
- 2026-11-14 02:16:37 MAPPING.md written (classes, key items, LINKING, exclusions) before any linking; running link.py
- 2026-11-14 02:20:50 first link run: 4400 key items, 2457 linked; added identity check (amendment 1, source+corpus only); re-running
- 2026-11-14 02:26:36 SOURCE.md, score.py, fake/selftest.py written; link re-run still going (machine loaded)
- 2026-11-14 02:27:13 link re-run done: 4400 key items, 2391 linked, 1544 units (910 linked key items excluded for FJC overlap); running synthetic self-test
- 2026-11-14 02:27:59 self-test PASS on synthetic build (fake/); READY written. REPORT.md write blocked by the harness (report-file guard); link figures are in link_summary.json + link_report.tsv and in the final message. Done.
