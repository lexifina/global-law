# Estonia (EE) 2025: progress (resumable)

Owner: EE worker of the Nordic + Baltic family. Tax year 2025 (calendar). Writes only inside ~/cmp20/baltic/ee/.
Status: **done** (all 7 steps), 2026-11-19. Headline and counts: results/summary.json.

| step | status | where |
|---|---|---|
| 1 model | done: lib EeTax, exe eetax (Params, Model, Withholding, Basic, Theorems, Findings); cents inside, euros out; `"year": 2026` variant | lean/ |
| 2 validation | OECD TW 2025 48/48 mapped lines exact (oecd_map.py: F1 II pillar, F2 single-parent allowance); EMTA figures 7/7; § 42(1) = § 23(2)/12 proved | results/oecd_check_EE.md, runs/emta_checks.txt |
| 3 proofs | 31 theorems, no sorry, no native_decide: flat schedule, hump band 37.99 % (taper_marginal), monthly bounds, UI linear, concrete findings by decide | lean/EeTax/Theorems.lean, Findings.lean |
| 4 known loopholes | 16 catalogued, 12 recreated (6 blind by the generic scanners), 4 not modelled | CATALOGUE.md, runs/recreate.md, runs/retention.md |
| 5 new loopholes | F4 dividends in the hump income, F9 monthly vs annual, F12 2025->2026 timing | FINDINGS.md, runs/notches.md, runs/cross2026.md, results/search/ |
| 6 gov/statute errors | statute faults F13-F15, gov errors F16-F17, conventions F1-F2, history F18 | FINDINGS.md, runs/xref_tums_2025.tsv |
| 7 USEFUL.md | done; FAMILY_NOTES.md done | |

## How to rerun
- `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build`
- `python3 ~/cmp20/baltic/harness/b38.py oecd EE --out ~/cmp20/baltic/ee/results`
- `python3 ~/cmp20/baltic/harness/b38.py scan EE --out ~/cmp20/baltic/ee/results/search`
- `python3 tools/notches.py; python3 tools/recreate.py; python3 tools/retention.py; python3 tools/cross2026.py`
- statute: `cd refs && python3 ../tools/rtfetch.py TuMS 2025-01-01 2025-12-31` (Riigi Teataja public API:
  /public-api/api/v1/akt/{id}/blob-xml, /akt/{grupiId}/redaktsioonid, /akt/lyhendid); `python3 ../tools/xref.py tums_120122024005.txt`

## Sources fetched (refs/)
TuMS redactions 103122024004, 120122024005 (model text), 109012025031, 112072025028, 118122025017, 109072026067; amending
act RT I 08.07.2025, 1; SMS 127092024008; KoPS 103122024015/16; TKindlS 106072023111/103062025004; PHS 112122024013/14,
108042025002; UI-rate regulations 124092024004, 103102023019; EMTA pages refs/emta/*.txt; Sander et al. 2010 refs/lit/.
Web searches used: 2 of 3.

## Open issues
- Pension age approximated as age >= 65 (RPKS § 7: 64 y 9 m for those born 1961); II pillar set to 0 at pension age.
- Not modelled: investment account (§ 17^2), ELMS business account, fringe benefits, foreign income, capital losses,
  vanemahüvitis, FIE exceptions SMS § 2(6)-(10). Owner scan in the kernel harness uses the kernel's EE company entry
  (OECD-based 33.8 % employer) rather than company.json (board-member route); results identical in ranking.
- The act that repealed the 24 % rate of RT I 08.07.2025, 1 § 3 before 1.1.2026 was not identified (F18).
