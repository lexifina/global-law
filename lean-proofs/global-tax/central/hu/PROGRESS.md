# Hungary (HU), tax year 2025: progress

Owner: central/hu worker. Folder `~/cmp20/central/hu/` only. Exe `hutax` (Lake project `lean/`, lib `HuTax`).
Updated: 2026-11-19 12:45 UTC. **Status: done (7/7 steps).**

| # | Step | Status | Where |
|---|---|---|---|
| 1 | Model: Szja tv. 2025 annual return with all base allowances in § 29/H order (mothers of 4 / of 3 from October, under 25, under-30 mothers, personal, first marriage, family), family allowance pooled between partners + Tbj. § 34 contribution allowance, TB 18.5 %, capital Szja 15 % + szocho with the § 2 (2) ceiling, átalány and KATA options, Cst. családi pótlék | done | `lean/HuTax/{Params,Model,Household,Main}.lean` |
| 2 | Validation: OECD TW 2025 56/56 exact (also via harness 8/8 THP); 45 NAV worked figures exact; NAV calculator source reviewed | done | `results/oecd_check*.md`, `lean/HuTax/Tests.lean`, FINDINGS F1, F12 |
| 3 | Proofs: kernel Schedule/Family/Rounding instantiated; closed form of the family allowance + TB spill; youth allowance has no notch; findings households by `decide` | done | `Theorems.lean`, `Findings.lean` (41 theorems, 0 sorry, no native_decide) |
| 4 | Known loopholes: 14 catalogued, 12 recreated (5 blind), 2 not modelled | done | `CATALOGUE.md` |
| 5 | New loopholes: F4 (mothers of three, Q4 2025), F5 (25th-birthday month), F6 (2025 -> 2026 family frame), F9 (interest vs gains szocho) | done | `FINDINGS.md`, `results/own/`, `results/search/` |
| 6 | Government / statute: F3 NAV 73 example (error), F2 "667 %" (statute), F11 családi pótlék frozen since <= 2009 (statute), F12 calculator clean | done | `FINDINGS.md` |
| 7 | USEFUL.md | done | `USEFUL.md` |

Done: 7/7. Web searches used: 3 of 3.

## Open
- Not modelled: CSED/GYED allowance (2025. évi XVI. tv.), itemised-cost sole traders (vállalkozói kivét), TBSZ,
  pension-savings credits (§§ 44/A-44/C), monthly withholding; children 18+ only via `huStudents`.
- The 2026 comparison (F6) uses 2025 rules except the 2026 family-allowance table.
- company.json HU (kernel-owned) lacks the active member's minimum bases and KIVA (sent to kernel INBOX).

## How to resume
- Build: `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build` (exe `.lake/build/bin/hutax`).
- OECD: `python3 ~/cmp20/central/oecd/check.py HU`; `python3 ~/cmp20/harness/oecd_check20.py HU --out results`.
- Scanners: `python3 ~/cmp20/harness/search/run_all.py HU --out results/search`; own scans `python3 tools/scan_hu.py`.
- Statute copies: `refs/jogtar/*.txt` (net.jogtar.hu versions: Szja tv. 2024.I.1, 2025.I.1, 2025.I.2, 2025.VII.1,
  2025.X.1, 2026.X.1; Tbj. 2025.I.1 and VII.1; Szocho tv. 2025.I.1; Cst. 2009.I.1 and 2025.I.1; 2025. évi XV. tv.;
  KIVA; KATA). njt.hu refused connections from lean1 and the laptop. NAV booklets `refs/nav/`, calculator `refs/navcalc/`.
