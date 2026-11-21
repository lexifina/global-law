# Slovakia (SK), tax year 2025: progress

Owner: SK worker of the Central Europe family. Folder `~/cmp20/central/sk/` only. Contracts: `~/cmp20/CONTRACT38.md`,
`~/cmp20/CONTRACT20.md`; kernel `~/cmp20/kernel/API.md`. Updated 2026-11-19.

## Status: done (7/7 steps); open items below

| Step | State | Where |
|---|---|---|
| 1 Model | done | `lean/` (SkTax, exe `sktax`), builds clean, 0 sorry, no native_decide; TaxKernel by path (Schedule, Rounding.divR, sumInts, Canon/Out/Country, kernel theorems) |
| 2a OECD TW 2025 | done | 56/56 lines exact (within 1 €), THP 8/8: `results/oecd_check.md` (central/oecd/check.py) and `results/oecd_check_SK.md` (harness oecd_check20.py); cent-level differences explained (F1) |
| 2b Official worked examples | done | Finančná správa 2025 bonus pages (790897, 272586, 476621): 18/18 exact in `Tests.lean` (+ 2 third-party podnikajte.sk examples) |
| 3 Proofs | done | `Theorems.lean` (schedule via kernel, § 11 bands, spouse band, § 33 ods. 11 per-child step for any n, § 32a dead), `Findings.lean` |
| 4 Known loopholes | done | `CATALOGUE.md`: 15 catalogued, 13 recreated, 2 not modelled, 4 found blind by the generic scanners |
| 5 New loopholes | done | F5 (lower earner claims the bonus), F6 (METR > 100 % with 8 children), F7 (bunching), F11 (two 19 % bands), F14 (lead); scanners in `results/search/` (harness run_all.py SK) |
| 6 Gov errors / statute faults | done | F3 (§ 33 ods. 8/11 gap of 1. 1. 2025, closed 15. 3. 2025), F4 (stale § 52zzp ods. 6), F12 (§ 32a dead); F13 Finančná správa reading/convention (not an error); no error found in the 18 official examples or the OECD lines |
| 7 USEFUL.md | done | `USEFUL.md` |

## Open
- The OECD's employer rate (32,2 %) vs the statute's 35,2 % is not explained (F2; employer side is outside the contract).
- SZČO contributions in steady state (no lag of the base by a year, no first-year exemption, no part-year insurance).
- Not modelled: tax losses (§ 30), alternating bonus claimants within a year, the 110 € school-entry supplement and the
  príplatok k prídavku, § 33 ods. 9 (90 % domestic income), employee in-kind exemptions, the minimum CIT (daňová licencia,
  § 46b) in `tools/owner_sk.py` (it does not bind for profits ≥ 3 400 €).
- `~/cmp20/harness/search/company.json` "SK" is the kernel's OECD-based placeholder (CIT 24 %, employer 32,2 %); the
  statute-cited company side is in `tools/owner_sk.py` (CIT 10/21/24 %, employer 35,2 %, dividends 7 %/10 %) and
  `results/company_SK.json` for the kernel agent to copy.
- F14 (token salary vs self-payer health minimum) is a lead to confirm with insurer practice; F12's start year unverified.

## How to resume
- Build: `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build` (exe `lean/.lake/build/bin/sktax`; options
  `--statute-taper` = § 33 as worded on 1. 1. 2025).
- OECD: `python3 ~/cmp20/central/oecd/check.py SK`; `python3 ~/cmp20/harness/oecd_check20.py SK --out results`.
- Scanners: `python3 ~/cmp20/harness/search/run_all.py SK --out results/search` (7 s).
- Owner-manager: `python3 tools/owner_sk.py` → `results/owner_sk.{md,json}`. Lean counts: `python3 tools/stats.py`.
- Statute copies: `refs/slovlex/*.txt` (fetch more with `tools/h2t.py` from https://static.slov-lex.sk/static/SK/ZZ/<year>/<no>/<yyyymmdd>.html, 1,5 s apart).
- Web searches used: 2 of 3.
