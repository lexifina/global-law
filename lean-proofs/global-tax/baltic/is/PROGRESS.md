# Iceland (IS, Reykjavík), income year 2025: PROGRESS

Owner: ICELAND worker of the Nordic + Baltic family. Contracts: ~/cmp20/CONTRACT38.md, ~/cmp20/CONTRACT20.md.
Kernel: ~/cmp20/kernel (API 1.1, kernel 1.2). Writes only inside ~/cmp20/baltic/is/.

## Status (2026-11-19, milestone 8: done)
| # | Step | Status |
|---|---|---|
| 0 | read contracts, kernel API, NO/SE/DK quality bar | done |
| 1a | parameters 2025 with citations (`refs/PARAMS.md`, P1-P23); statute editions 154c-158a from github.com/althingi-net/lagasafn-xml (althingi.is behind a bot challenge) | done |
| 1b | Lean model `lean/IsTax` (lib `IsTax`, exe `istax`) on TaxKernel by path | done: 685 lines, 72 definitions, 38 theorems, 0 sorry |
| 2 | validation | done: OECD 48/48 exact (OECD conventions, `oecd_map.py`); statute default THP 8/8 within 1 %, gaps fully explained; RSK barnabætur calculator 26/26; RSK staðgreiðsla calculator 13/14 (1 kr.); published figures 5/5 |
| 3 | proofs | done (`lean/IsTax/Theorems.lean`) |
| 4 | known loopholes | done: `CATALOGUE.md`, 20 catalogued, 11 recreated (5 blind), 9 not modelled |
| 5 | new loopholes | done: F3 levy cliff, F4 barnabætur stacking, F11 second-earner penalty in the band transfer, F12 shared-residence bonus, F17 timing |
| 6 | gov errors / statute faults | done: gov-error F5, F7, F8, F13, F14 (F6 convention); statute-fault F1, F2, F9 (reading), F15 |
| 7 | `USEFUL.md`, `FAMILY_NOTES.md`, `results/summary.json` | done |

Done 8/8.

## How to rerun
- build: `cd ~/cmp20/baltic/is/lean && export PATH=$HOME/.elan/bin:$PATH && lake build`
- OECD: `python3 ~/cmp20/baltic/harness/b38.py oecd IS --out ~/cmp20/baltic/is/results`
- statute vs OECD and published figures: `cd validation && python3 published_and_oecd.py`
- RSK calculators (polite, 3 s apart; answers already saved): `python3 tools/rskcalc.py barn|stad cases.jsonl out.jsonl`,
  then `cd validation && python3 compare_calc.py`
- generic scans: `python3 ~/cmp20/baltic/harness/b38.py scan IS --out ~/cmp20/baltic/is/results/search`
- Iceland scans: `cd results/is_scans && python3 ../../harness/scan_is.py && python3 ../../harness/scan_owner_is.py`
- options of istax: `--average-utsvar` / `"region":"average"`, `--levies-assessment-2025` / `"levies":"assessment2025"`,
  `--no-band-transfer`, `--no-credit-transfer`, `--separate`, `--literal-67A`; inputs `cohabiting`, `closelyHeld`,
  `dividendsUnlisted`, `gainsUnlisted`, `sharedResidence`; `"mode":"stadgreidsla"` with `monthlyWage`, `sereignBp`,
  `creditPct`, `spouseCreditPct`.

## Notes for the family lead / kernel
- the kernel owner-manager data for IS (company.json in ~/cmp20/harness/search) takes precedence over
  `~/cmp20/baltic/is/company.json` in b38.py; ours adds the closely-held dividend (no 300.000 kr. exemption) and the
  reiknað endurgjald minima; our own scan is `harness/scan_owner_is.py`.
- kernel gaps listed in `results/summary.json` and `FAMILY_NOTES.md`; nothing written to ~/cmp20/kernel/INBOX.md
  (outside this folder).

## Open issues
- the 4. tölul. cap is not published for 2025 (F7); modelled as half the middle band (5.118.730 kr.).
- barnabætur income measure: capital income counted gross (incl. the exempt half of rent): a reading of "tekjur skv.
  II. kafla"; the RSK calculator only says capital income is included.
- the odd króna when a couple's barnabætur are halved is given to the first parent (model assumption).
- vaxtabætur, children's income, home-stay letting, birth-year barnabætur: not modelled (`unsupported`).
- "Skattar og ójöfnuður" (2021) and althingi.is bill commentaries could not be read (bot checks); novelty claims rest on
  the official pages read and 2 web searches (1 of 3 searches left unused).
