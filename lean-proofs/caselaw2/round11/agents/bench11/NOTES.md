2026-11-14 05:14:00 start: read brief, contract; df 24G free
2026-11-14 05:14:58 probe: 4 Dataverse metadata fetches (Gibson&Nelson K9VIEW, Amato OYW9GT, Ash&MacLeod GVEU25, BHK 2EJIZJ); fetches used 4/25
2026-11-14 05:15:17 fetched Gibson&Nelson codebook + case tab (fetches 6/25) into benchmarks/gibson_nelson_state/raw (tentative)
2026-11-14 05:15:40 REJECT Gibson&Nelson: only LexisNexis cites (no reporter cite / docket), no disposition var (only have/have-not winner direction); tentative folder removed. Fetched BHK zip to probe (fetches 7/25)
2026-11-14 05:16:24 SOURCE PICK (fetches used 7/25, all Harvard Dataverse API):
  CHOSEN: Beim, Hirsch & Kastellec, replication data "Signaling and Counter-Signaling in the Judicial Hierarchy" (AJPS 2016),
    doi:10.7910/DVN/2EJIZJ, termsOfUse "made available under a Creative Commons CC0 license" (no added terms), no restricted file.
    bhk_main_data.csv: 5,589 panel decisions 1986-2002 with p_cite (panel F.2d/F.3d cite), eb_grant, eb_reverse, eb_cite.
    Fresh population = the 771 rows from source_of_cases bhk_ebs (327) + clark_ebs (444): published panel opinions
    later reheard en banc. Test = same-case: the panel opinion should carry negative history (vacated/superseded on
    rehearing en banc) -> NEG_HIST; eb_reverse=1 (en banc changed the result) is the primary sub-population.
    Why: human-collected, CC0, cheap (one 1.1 MB zip), reporter cites on both sides, and the population (en banc-reheard
    panel opinions outside the Songer random sample) is in no earlier key; Shepardized COAENBANC covers only Songer-sample
    cases, IDB/FJC key scores district decisions. Songer-sample rows (4,797, source songer_*) are NOT used (Shepardized/Songer
    population) and any en banc row whose panel cite is a Songer case will be dropped.
  REJECTED: Gibson & Nelson state supreme courts 1990-2015 (CC0) - only LexisNexis cites, no disposition variable;
    Ash & MacLeod 1947-94 - judge-year panel, no case outcomes; Amato ten states 2000-20 - 356 MB RData of opinion text, no
    labels; Larsen en banc (author asks to be contacted); Lindquist (DUA); California review-granted list (no cites, post-2020,
    page scraping); Epstein-Landes-Liptak Roberts Court precedents (off-Dataverse, no licence stated, overruled flag = SCDB);
    Fowler & Jeon (SCDB/CRS lineage); pre-1930 IA tables (same family as state_overruled_tables, heavy OCR).
2026-11-14 05:17:28 set up benchmarks/bhk_enbanc (raw/dataset_json, raw/bhk_zip, raw/bhk_zip_x); codebook read; en banc rows 771 (bhk 327, clark 444), casenum_songer_original empty for all of them (not Songer-sample cases); writing MAPPING.md before any linking
2026-11-14 05:19:16 MAPPING.md written; parse_source.py -> 771 items (R 511, S 242, U 18); running link.py
2026-11-14 05:19:58 link run 1: 691/771 items linked (690 panel units; 595 confirmed by en banc citation). Read 30 sampled pairs (all sound) + 28 caption-mismatch pairs: 7 eb_cite apparently wrong -> Amendment 1 (recall_by_enbanc on confirmed units only). No model row read.
2026-11-14 05:22:10 score.py self-test on synthetic build (fake/ via make_fake.py, check_fake.py): 0 failures, incl. unknown node ids >= 9,000,000, expired/issue-level decoys, unadmitted history rows. SOURCE.md written (sha256 of every file; zip MD5 = Dataverse MD5). REPORT.md refused by the harness (subagent report-file rule), same as round 10; link figures in link_summary.json and in the final message. READY written; 'bhk_enbanc' appended to round11/FRESH_KEYS.txt. Web fetches used: 7/25. No model output read, no build scored, nothing committed. df: 24G free.
