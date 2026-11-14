2026-11-14 07:04:50 start; read BRIEF; df 20G free
2026-11-14 07:06:35 FLP citator benchmark search (1/25): not released. Leaning to FJC IDB residual (appeals not in CCAD crosswalk)
2026-11-14 07:07:41 SOURCE PICK (fetches used 1/25):
  CHOSEN: FJC IDB appeals, the RESIDUAL population never in any key: appeal records that the CCAD idb_crosswalk does
    NOT attach to any published opinion (neither primary nor alt row). fjc_idb_appeals' unit is by definition a
    crosswalked record (its MAPPING 'Unit'), so these rows were never keyed; songer/shepardized/bhk/fedcir test
    published appellate opinions or decisions below published Songer-sample opinions. Test = same-case: published
    district/bankruptcy decision reversed/vacated (NEG_HIST) vs affirmed (CLEAN) in an appeal decided without a
    published opinion (unpublished / F. App'x / judgment order). US government work, no login; CCAD crosswalk CC BY 4.0.
    Value: corpus holds ~286k F. App'x-cited appellate nodes, so the reviewing unpublished opinion is often in the
    corpus; a secondary 'reviewed' population (appellate node found by appeal docket + date that cites the district
    decision) isolates where history is possible. Disjointness from fjc_idb_appeals enforced by construction: any
    district node whose (DDIST, docket) matches ANY crosswalked record is dropped.
    Effort: low - builders of fjc_idb_appeals are the model (copied, adapted); 3-4 fetches.
  REJECTED: FLP citator benchmark (not released; search 1/25); Epstein-Landes-Liptak (no licence, small, SCDB flag);
    Hansford-Spriggs (by request only); Songer Phase II (same cases as SCDB lcDisposition); CCAD is_enbanc
    (778 MB > 300 MB cap; machine-coded); Federal Circuit docket data (same project family as fedcir_dataset);
    California review-granted (no cites, post-2020, scraping); Lindquist (DUA); Gibson&Nelson/Ash&MacLeod/Amato
    (rejected by bench11: no disposition var / no cites); pre-1930 tables (same family as state_overruled_tables).
2026-11-14 07:08:25 downloaded 5 files (+2 HEAD, fetches 8/25); sha256 identical to fjc_idb_appeals/SOURCE.md
2026-11-14 07:10:24 parse_source.py: 1,911,672 residual IDB rows (not crosswalked, not published PUBSTAT); 321,345 excluded dockets. MAPPING.md written before any linking.
2026-11-14 07:14:01 build_corpus (app docket index 791k keys) done; link.py written; first link run
2026-11-14 07:15:05 link run 1: 17,944/630,275 key items linked -> 16,254 district units (1,699 reviewed). Read 30 sampled pairs (20 random + 10 reviewed; corpus+source only): identities all sound; 2 are earlier rulings in the docket (known docket-population caveat, reviewed population handles it). No amendment. No model row read.
2026-11-14 07:16:54 score.py (adapted from fjc_idb_appeals; --out/--data required) self-test on synthetic build fake/ (make_fake.py, check_fake.py): 0 failures incl. expired/issue-level/future decoys, unadmitted history, 50 unknown node ids >= 9,000,000. SOURCE.md written. REPORT.md refused by the harness (subagent report-file rule) - link figures in link_summary.json + final message. READY written; 'fjc_idb_unpub' appended to round12/FRESH_KEYS.txt. Web requests 8/25. No model output read, no build scored, nothing committed. df ~19G free.
