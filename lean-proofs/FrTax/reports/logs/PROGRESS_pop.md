2026-11-17 14:25:38 step 1/4: start; reading project files; boxes.csv (2042-nat 2006-2024) found locally
2026-11-17 14:34:38 step 1/4: data found: 2042-nat (data.economie, 2006-2024), IRCOM 2024+2025 national (data.gouv), DGFiP Statistiques n32/n41/n53 + 6 IR tables (impots.gouv), VMT2 PLF2026; next: Lean box probe + targets; ETA step 1 done ~15:15
2026-11-17 14:41:31 step 2/4: generator harness/pop_gen.py + runner harness/pop_run.py working (5000-case smoke test); next: calibration script; ETA pool runs ~15:20
2026-11-17 14:44:36 step 2/4: generating 250000 households for income 2024
2026-11-17 14:44:44 step 3/4: running 250000 households (2024) through Lean and M (12 jobs)
2026-11-17 14:48:20 step 4/4 (prep): coverage (harness/pop_coverage.py: Lean reads 93.9 % of declared income amounts 2024, 90 % of credits, 31 % of reductions) and published-count arithmetic (harness/pop_scale.py) done; 2024 pool M run at ~500/625 chunks; ETA calibrated totals ~15:15
2026-11-17 14:48:33 step 2/4: calibrating 2024: 247844 accepted by M, 2156 refused
2026-11-17 14:52:31 step 2/4: generating 250000 households for income 2023
2026-11-17 14:52:34 step 3/4: running 250000 households (2023) through Lean and M (12 jobs)
2026-11-17 14:53:33 step 2/4: first 2024 calibration fits 273/275 margins within 5 % but weights too uneven (max 335k, ESS 7k); stopped the 2023 run; fixing the generator (rentes viagères by age, 6DE, 1AP, 3VG...) and adding RFR-bracket post-stratified base weights; rerun ETA ~15:25
2026-11-17 14:57:35 step 2/4: generating 250000 households for income 2024
2026-11-17 14:57:38 step 3/4: running 250000 households (2024) through Lean and M (12 jobs)
2026-11-17 15:00:34 step 2/4: calibrating 2024: 248090 accepted by M, 1910 refused
2026-11-17 15:01:36 step 2/4: calibration switched to bounded logit (Deville-Särndal, w/d in [0.05,20]) from RFR-post-stratified design weights; testing on first 2024 pool; new 2024 pool running in M (M done); ETA both years calibrated ~15:30
2026-11-17 15:11:46 step 2/4: 2024 pool (250 000; 248 090 accepted by M, 1 910 refused = IM2102 only) calibrating with bounded logit (11 min so far); 2023 pool next; ETA ~15:40
2026-11-17 15:17:32 step 2/4: 2024 calibration rerun with more margins (IRCOM salary/pension amounts per RFR group, RFR-per-part deciles: households, parts, RFR; CI beneficiaries per decile) on 2 cores while the 2023 pool runs in M (12 jobs); new: Lean refunds the 2AB foreign-securities credit, M caps it at the tax
2026-11-17 15:17:51 step 3/4: (re)running the 2023 pool through Lean and M (10 jobs); the first attempt was terminated at chunk 200/625
2026-11-17 15:19:02 step 2/4: waiting on the 2024 calibration (2 cores) and the 2023 M run (M chunks 225/625); POPULATION.md sources section drafted; ETA results ~15:50
2026-11-17 15:20:47 step 2/4: calibrating 2023: 245664 accepted by M, 4336 refused
2026-11-17 15:26:02 step 2/4: 2023 calibrated
2026-11-17 15:26:03 step 2/4: dense calibration too slow; restarted both years with a sparse matrix, 6 cores each (taskset 18-23, 24-29)
2026-11-17 15:26:14 step 2/4: (the '2023 calibrated' line above was written when that run was stopped; ignore it)
2026-11-17 15:38:54 step 2/4: both calibrations running 13 min (L-BFGS, up to 30 000 iterations); ETA ~15:55, then step 3/4 report
2026-11-17 15:45:24 step 2/4: 2024 calibrated in 1161 s
2026-11-17 15:45:25 step 2/4: 2023 calibrated in 1162 s
2026-11-17 15:45:34 step 3/4: 2024 calibrated: 360 margins, 357 within 5 %, all within 10 %; weights 0.48-4 778 (ESS 60 530); running the report
2026-11-17 15:47:35 step 3/4: reports for 2024 and 2023 written (runs/pop/<year>/report.txt, report.json); Lean net tax +23 % over published, gap located in RFR > 50 k; next: write POPULATION.md
2026-11-17 15:50:58 step 4/4: writing POPULATION.md (totals, scale table, limits); new Lean/M differences found: 2AB refunded by Lean (M caps it), 6GP without the 25 % increase in Lean; ETA ~16:30
2026-11-17 15:53:13 step 4/4: POPULATION.md written (sources, calibration fit, totals 2023/2024, decile decomposition, Lean-M classes incl. new 2AB and 6GP, scale table, limits); copying to the local mirror
2026-11-17 15:53:26 step 4/4: done. Superseded first-draft runs (runs/pop/old2024, runs/pop/t) removed; mirror copied to ~/Documents/the build server-work/fr
