# orders11b NOTES

- 2026-11-14 05:38 start: read BRIEF, orders11 BRIEF, FORMAT.md, SOURCES.tsv. df /c 21G free. 12 Journal texts inherited (OT05-09, OT19-25).
- 05:39 checked 12 Journal texts vs PDFs: page counts equal, sha256 = SOURCES.tsv; deleted the 12 PDFs in orders11/dl/jnl*/ (~80 MB). Layout: sitting-date heading, sections (Certiorari—Summary Dispositions etc.), entries 'No. 07–1154. Caption. On petition ... Judgment vacated, and case remanded ...'; soft hyphens U+00AD at line ends; running head + page no. after form feeds.
- 05:41 corpus 2906 by month (v10d decisions2): 2006-01/02 memorandum 889/778, from 2006-03 none; 2020-01..05 ~400-650/mo, 2020-06 thin (72), 2020-07+ none. Range used: 2006-03-01..2009-12-31 and 2020-07-01..2025-12-31. Writing parser scripts/parse_jnl.py.
- 05:44 parser v1 runs on jnl08; fixing caption split ('et al. Appeal from').
- 05:46 parser v2: plain-hyphen dehyphenation (old Journals print 'Judg- ment'), granted_remanded class, court fallback. Reviewing classes.
- 05:47 parser v3: '(24A1122)' docket parentheticals (~500 entries were merged), judgment-phrase regex widened, 'affrmed' (missing fi ligature).
- 05:51 parser v4 + make_nodes.py: trial 980 nodes in work/trial (gvr 932, order_vacated 22, affirmed 14, vacated 10, granted_remanded 2). Next: write data_orders + PARTIAL.
- 05:51 wrote data_orders/nodes.tsv (980), text/ (980), counts.tsv, opinion_entries.tsv, journal/ (12 texts, 20 MB), README.md; DATA_READY_PARTIAL written (all years). Next: validation on an OT2010-18 Journal.
- 05:52 validation: fetched Jnl16.pdf (1 request, 200, 4.2 MB; logged in SOURCES.tsv), converted, PDF deleted; parsed.
- 05:54 validation OT2016 (Oct16-Jun17): 6,773 journal entries, 6,684 docket-matched to corpus 2906 nodes (6,667 same date), 7,324/7,359 corpus nodes matched; caption overlap>=.5 6,046; journal GVR 51 -> 51 corpus nodes same date, corpus text GVR-worded 48 (3 have separate writings).
- 05:55 wrote data_orders/VALIDATION.md and DATA_READY (980 nodes, unchanged). Agent folder 78 MB, data_orders 22 MB, df /c 22G free. Reporting.
- 06:04 follow-up from lead: append nodes for GVR/vacated/affirmed entries whose docket is not a corpus 2906 node within +-10 days, all held Journal months; fetch OT2004 + OT2014.
- 06:06 fetched jnl04 + jnl14 (2 requests, 200; PDFs deleted). append_nodes.py: 65 rows appended after the 980 (first 980 lines byte-identical).
- 06:06 counts.tsv regenerated (all held years), README updated, append_report.tsv + DATA_READY2 written. Reporting to lead.
