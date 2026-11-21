# NL (Netherlands, belastingjaar 2025): progress

Owner: NL worker (continental family). Contract: `~/cmp20/CONTRACT20.md`. Updated: 2026-11-19 (final).

## Status: done (7/7)

| Step | What | Status / files |
|---|---|---|
| 1 | Model `lean/` (lib NLTax, exe nltax, on TaxKernel) + OECD validation | DONE: 32/40 OECD lines to the cent (`--oecd`), rest explained |
| 2 | Other referees | DONE: Belastingdienst rekenvoorschriften 2025 (withholding rekenregel, `NLTax/Withholding.lean`, `results/lb_grid.*`); no usable official calculator without JS (not tried further); no open model used |
| 3 | Proofs | DONE: `NLTax/Theorems.lean`, 27 theorems, no sorry |
| 4 | Known loopholes | DONE: `CATALOGUE.md` (21 catalogued, 13 recreated, 7 not modelled), `harness/recreate.py`, `runs/recreate.json` |
| 5 | New loopholes | DONE: `NOVEL.md`; own scanners `harness/scan.py`, `harness/box3.py`; kernel scanners `results/search/SUMMARY.md` |
| 6 | Government / statute errors | DONE: FINDINGS F2-F8, F11-F15 |
| 7 | `USEFUL.md` | DONE |

Files: `FINDINGS.md` (F1-F18), `CATALOGUE.md`, `NOVEL.md`, `USEFUL.md`, `results/summary.json`, `law/` (statute texts),
`refs/` (rekenvoorschriften 2025 PDFs and text), `oecd_map.py`.

## How to run
* Build: `cd ~/cmp20/continental/nl/lean && export PATH=$HOME/.elan/bin:$PATH && lake build`
* Exe: `.lake/build/bin/nltax [--oecd|--oecd-pension|--band-sum] [--split-half] < households.jsonl` (contract JSONL;
  extensions: adult `wagesExact`, household `nlBank`, `nlOtherAssets`, `nlDebts`, `nlBox2`, `nlUrencriterium`).
  Detail includes `loonheffingAnnual` (the withholding table) per adult.
* OECD: `python3 ~/cmp20/continental/harness/oecd_check.py NL --args=--oecd`; to the cent:
  `python3 harness/oecd_exact.py [--args=--oecd|--args=--oecd-pension]`
* Withholding vs statute: `python3 harness/lb_grid.py`; scans: `harness/scan.py [--fine]`, `harness/box3.py`,
  `harness/recreate.py`; kernel scanners: `cd ~/cmp20/harness/search && python3 run_all.py NL --out ~/cmp20/continental/nl/results/search`

## Validation
* OECD TW 2025 at unrounded wages, `--oecd`: 40 lines, 32 to the cent, 40 within 1 %. Explained: kinderbijslag
  (OECD −5,12, F2), kgb drempelinkomen (€ 0,02, F3), S167 (€ 0,05-0,13, F4, open). Statute table mode: OECD +0,63 /
  +0,95 per taxpayer (F5). Family harness (rounded wages): 56 lines, 48 within € 1, 56 within 1 %.
* Loonbelastingtabellen 2025 (rekenregel) vs statute, 2 396 table wages: table − statute in [−2,64, +0,06]; proved
  bound [−3,05, +0,30] (`lb_vs_statute`).

## Family-lib / kernel gaps (also in summary.json)
Kernel `Out` has no cents; the statute's tariff tables (rounded cumulative kolom III) are not band sums and not
monotone (reported to `~/cmp20/kernel/INBOX.md`); pcm rates; korting split tax/premie and cross set-off; art. 2.17
allocation optimiser; box-3 wealth not in the contract; owner-manager scanner has no NL company parameters.
ContCommon not used.

## Open (if anyone resumes)
* F4 (OECD S167 € 0,18 arbeidskorting) unexplained.
* Not modelled: toeslagen, box-3 tegenbewijs, eigen woning / Wet Hillen, lijfrente jaarruimte, starters' aftrek,
  jonggehandicaptenkorting, groene beleggingen, periodieke giften, AOW age reached during the year.
* Web searches used: 4 of 7.

## Round 3 testing (2026-11-19, improve-continental)
- Belastingjaren 2022-2024 added (NLTax/Years.lean, ypFor; dated wetten.overheid.nl texts in law/hist/; years.json
  in this folder): art. 2.10, 8.10, 8.11, 8.14a, 8.17, 8.18, AKW art. 12, Wkb art. 1-2. 2.10a, box 2/3, Zvw and the
  --oecd pension convention keep 2025 values. Dev TW 2022-24: statute 36 exact of 240 covered (pension convention
  gap as in 2025), convention 95 exact / 230 within 1 %. Log: ~/cmp20/improve-continental/IMPROVE.md (Round 3).
- Round 5: art. 2.10a tables 2022-2024 (born before 1946) added to Years.lean. Still 2025 values before 2025: box 2/3,
  Zvw, the --oecd pension convention.
- Round 9: Zvw 2022-2024 (Regeling zorgverzekering art. 5.1-5.3), box 2 2022-2024 (art. 2.12), box 3 2022 (old
  rendementsklassen vs Wet rechtsherstel box 3, the lower). No dev score change (no such inputs in the dev sets).
- Round 10: 2022 box 3 for partners per allocated share (art. 5.2 lid 2; rechtsherstel art. 3 lid 4; the lower per partner).
