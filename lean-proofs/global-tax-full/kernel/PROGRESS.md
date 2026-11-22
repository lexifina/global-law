# Kernel, harness, searches, report: PROGRESS

Updated: 2026-11-19 13:10 CET (38-country phase, final: all four deliverables done)

## 38-country phase (CONTRACT38.md)

| # | Deliverable | Status |
|---|---|---|
| 1 | Kernel 1.2 for the 18 + harness discovery | DONE: `TaxKernel/Multiplier.lean`, `TaxKernel/Family.lean`, `Theorems/Parts38.lean` (12 theorems, no sorry, axioms audited), toy calls `examples/Parts38.lean` (#guard); API.md §4b, §7b; `common20.py` knows all 38 (OWNERS38, selectors new38 / family names / twenty); toy `zztax` rebuilds; backups of the 1.1 files in `kernel/.bak12/`, `harness/.bak38/` |
| 2 | Referee data | DONE: OECD TW 2026 (2025) for the 13 members merged into `harness/data/oecd/tw_cou_xdc.json` (20 entries unchanged, checked); `params.json` AW/PPP/FX for all 38 (20 unchanged); Eurostat earn_nt_net / taxwedge / lowwtrp / unemtrp in `harness/data/eurostat/`; `oecd_check38.py` (`--referee auto|oecd|eurostat|both`); `eurostat_calibrate.py` + `harness/runs/eurostat38/CALIBRATION.md` (Eurostat is a sanity bound only: K9) |
| 3 | Generic searches on the 18 + company.json | DONE (all 18 done; refresh_all.sh run on all 38, 0 scanner errors; owner.py on all 18 with statute-cited company sides from the agents for CY GR MT BG RO SK HR FI IS EE LV LT, open-data entries kept for AT CH LU BE SI HU and marked partial; conflicts recorded per entry and in K11; watch38.py stopped): `harness/search/company38.py` adds the 18 to company.json from open OECD/Eurostat data (CIT_C 2025, dividend table, employer effective rates from TW ERCSSCPT or Eurostat labour cost; marked partial, a family entry wins; CY CIT not in the OECD table: not computed); `harness/search/watch38.py` (nohup, state watch38.json, stop file watch38.stop) runs referee + scanners + owner + leads + report on every new or changed exe of the 18 once it is stable 5 min; regression on UK/DE numerically identical, attribution order made deterministic (REGRESSION.md) |
| 4 | Report 38 (USEFUL38 hook, CROSS38.md, USEFUL38.md, refresh_all.sh for 38) | DONE: report/CROSS38.md (synthesis, owner table, referees, Needs checking from spotcheck.py), report/USEFUL38.md (14 ranked items), 38-juris-research.html rebuilt; build_report.py reads USEFUL38.md (else USEFUL20.md, heading says which), CROSS38.md (else CROSS.md), shows CONTRACT38; cross_tables.py and spotcheck.py take the 38 from common20 (parts Table/Multiplier/Family counted; Eurostat row for non-OECD); refresh_all.sh runs all built of the 38. CROSS38/USEFUL38: at the end |

Done 4/4. Kernel 1.2.1 (Multiplier, Family, Tariff, Extra38). Open: see report/CROSS38.md section 7.
Resume: `bash cmp20/report/status.sh` shows each family's state; kernel sources edited in place on the build server (`lake build` in cmp20/kernel).

INBOX handled (12:45 CET): CY, GR, MT company sides entered in company.json from the agents' cited values (hand entries, not regenerated); SI confirmed; GR's married OECD lines use 1.1 x the single wage (agent's own check_gr.py); SI kernel gaps (rank-based means-tested benefit, deemed expenses taxed finally, an allowance passed between parents, mid-year parameter changes) noted for CROSS38.

## 20-country phase (done)


| # | Deliverable | Status |
|---|---|---|
| 1 | API.md + TaxKernel builds + toy country by path | DONE (parts: Basic, Rounding, Schedule, Allowance/Taper, Credit, Surcharge, Unit, Dual, Social, Canon, Country; `examples/zz/lean`); 14 of the 15 new models require TaxKernel (AU does not) |
| 2 | Generic theorems | DONE (TaxKernel/Theorems/Schedule.lean, Parts.lean, Rounding.lean; no sorry; all instantiated for the toy in examples/zz/lean/ZzTax/Theorems.lean) |
| 3 | Kernel fidelity (UK, DE) | DONE: fidelity/RESULTS.md: UK 10,279 households, income tax / Class 1 / child benefit net of HICBC equal to the penny 10,279/10,279 each; DE 2,926 units: § 32a tariff, Soli, RV/AV/KV/PV all equal |
| 4 | OECD TW 2025 data for 20 + oecd_check20.py + params | DONE: harness/data/oecd (five-country values reproduced 3,520/3,520), params.json (AW, PPP, FX for 20), oecd_check20.py (lines + take-home pay from contract net and from mapped lines); run on all 20 (harness/runs/oecd20) |
| 5 | Harness run20/tax20 | DONE: harness/common20.py, run20.py, tax20, auto-discovers <cc>tax; all 20 exes run |
| 6 | Generic searches | DONE: harness/search/{metr,phaseouts,timing,edges,unit,income_type,run_all,leads}.py; regression on the five in harness/search/REGRESSION.md (13 known features re-found); first pass on all 15 new countries; leads per country in kernel/LEADS.md |
| 7 | Report + CROSS.md | DONE: CROSS.md final (all 15 new countries done; 247 finding blocks indexed; 'Needs checking' from report/spotcheck.py), report/USEFUL20.md (ranked, rendered at the top of the HTML), report/refresh_all.sh run on the final exes of all 20 (scanners, OECD checks, leads, cross tables, HTML) |

Done 7/7. Kernel 1.1 (adds `Table`, `perPeriod`).
Resume: sources in cmp20/kernel (the agent edits a local copy and uploads); `lake build` and `lake build kfid` in cmp20/kernel.
To refresh everything: `cd cmp20/harness && python3 oecd_check20.py US FR UK DE JP CA AU IE NZ SE NO DK IT ES NL PT PL CZ KR MX --quiet; cd search && python3 run_all.py <same list>; python3 leads.py; python3 cmp20/report/build_report.py`.

Milestone 10: harness/search/company.json filled for all 20 (cited; 16 computed, FR IT PT CA not computed for missing
employer/corporate parameters, DE JP MX PL ES partial), harness/search/owner.py (best salary/dividend split, run by run_all.py),
reproduces the UK, SE, NO, KR agents' own results (REGRESSION.md); CROSS.md section 3b + Needs checking (AU K9, ES F13,
NL K1, CZ L04, PL); USEFUL20 item 11; CA and AU unit scans rerun after their models read `cohabiting` (no marriage effect).
- 2026-11-20 00:45 UTC: 1.3.0 `TaxKernel.World` for the world expansion (API.md §4c); the 33 kernel-built models of the 38 rebuilt against it in a copy (world/kcheck): all build, output byte-identical.
- 2026-11-20 02:00 UTC: 1.4.0 `TaxKernel.World2` (column tariffs, coefficient-indexed amounts; API.md §4d); world reference wages and scanner routing in the harness (§7c). All 49 kernel-built models rebuilt in a copy: byte-identical.
