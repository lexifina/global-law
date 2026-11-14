2026-11-14 07:04:29 GMTST start; read BRIEF, DESIGN12 §0/§4, COMMON; df /c 20G free
07:06:09 fetched 7 new Journal PDFs (jnl10-13, Jnl15, Jnl17, Jnl18) each into own dl/<name>/ folder
07:09:13 ligature: Jnl18-25 fonts' ToUnicode maps codes 174 /fi and 175 /fl (Encoding Differences) to 'f'; wrote glyph-name-aware extractor pdf2txt_lig.py (remaps CMap in memory; same lines). Re-fetched Jnl19-25 (7 req; 14 total)
07:13:10 glyph-aware texts of 14 Journals verified: same line counts, only f->ligature substitutions (Jnl19-25: 489-658 per Term; Jnl18 619; Jnl17 12; Jnl15 4; jnl10-13 0). PDFs deleted after sha256 check; texts copied to data_orders/journal/
07:14:43 step 1 done: parse effect 0 class/docket/node flips; 2,781 entry texts (1,314 captions) changed; 57/1045 node texts changed (21 captions) -> CHANGED.tsv; residual check on unrefetched jnl04-09/jnl14/Jnl16: 0 drops. LIGATURE_READY + HANDOFF.md written.
07:15:07 step 2: parsed 7 new Terms (jnl10-13, Jnl15, Jnl17, Jnl18); running validation on 2012-03 and 2018-11
07:15:58 step 2 done: validation 2012-03 (652/660 matched, 648 same date, gvr 13/13) and 2018-11 (367/379, 366 same date); append over all held+new entries: 0 added, 1,771 candidates covered (615 from new Terms). DATA_READY_A written. Next: step 3 (2005 long lists).
07:16:27 step 3: longlist_diag.py over 2005 node-class Journal entries vs their corpus nodes (h0 file for counting only)
07:16:54 step 3 finding: 2005 GVR entries' corpus nodes are multi-docket lists (docket field + text print up to 356 other dockets, e.g. node 6230687 2005-01-24 Booker list); 711/840 entries in nodes printing >=10 other dockets; h0 (count only) misses: long 97, mid 5, short 15. Checking other years.
07:18:15 step 3: finding written to HANDOFF.md; append_longlist.py run (k main 10, low 3)
07:18:44 step 3 built: 826 r12:longlist nodes (k>=10: 764 = 2005 711 + 2012 53; 3<=k<10: 62 = 2005 37, 2011 2, 2012 23); loader nodes12.activate OK (1,871 nodes); counts.tsv written. Writing README/VALIDATION/FORMAT.
07:20:23 README, VALIDATION, FORMAT, counts, HANDOFF done; DATA_READY written. Intermediates cleaned (agent folder now small). Requests: 14 (all 200).
07:20:31 nodes12.py --check passes (1,871 nodes, 0 missing/bad texts). Reporting to lead. df /c 17G.
