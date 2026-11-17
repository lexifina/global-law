2026-11-17T15:57:28Z step 1/3: started; reading RESULTS/FINDINGS and harness; survey next. ETA total ~4h
2026-11-17T16:02:57Z step 1/3: survey via GitHub/GitLab APIs + 8 web searches; 20 candidates listed; installing node (Publicodes), R (INES), dotnet (EUROMOD). ETA step1 +40min
2026-11-17T16:07:49Z step 2/3: Publicodes adapter+harness written (impl_common/impl_score); running publicodes on 4 benchmarks. Survey 20 candidates so far. ETA all ~3h
2026-11-17T16:10:16Z step 2/3: Publicodes scored on bareme/examples/random/bound/saved-sim (classes: widow QF cap, no rounding, 157 bis absent, uncapped décote report). Next: INES (R). ETA ~2.5h
2026-11-17T16:18:33Z step 2/3: INES R wrapper runs (07_impot_revenus chain on box tables); scoring INES bareme/examples/bound/sim. ETA ~2h
2026-11-17T16:23:43Z step 2/3: INES rerun (per-year dico, overtime input concept, PFU timing excluded); Publicodes done. ETA ~1.5h
2026-11-17T16:29:26Z step 2/3: production simulator, 8 requests (impl classes) under flock
2026-11-17T16:31:29Z step 2/3: production answers: 8/8 side with Lean/M (pub widow cap x2; INES W+T parts, 2020 overtime cap, widow shared custody, 0AP compl. reduction, RFR 2OP, RFR 6DD). Next: EUROMOD/2016 Python attempts, then report. ETA 1h
2026-11-17T16:34:41Z step 2/3: EUROMOD runs on Linux (pythonnet+.NET 8); scoring tin_fr vs Lean tableTax on training data FR_2021-2025
2026-11-17T16:37:43Z step 3/3: writing IMPLEMENTATIONS.md (survey 20 entries, 3 run head to head: Publicodes, INES, EUROMOD; 8 production requests). ETA 30 min
2026-11-17T16:39:46Z step 3/3: IMPLEMENTATIONS.md written; copying to the local mirror. Done.
