# Angola (AO) findings, B09-southern-africa (rescue pass 2, 2026-11-20T13:10Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 The 2025 table has two notches built into its fixed amounts
- kind: statute-fault
- Row 3 (150,001-200,000) starts at a 'parcela fixa' of 12,500 Kz while row 2 ends at 13 % of 49,999 = 6,499 Kz: one more kwanza of monthly base costs 6,001 Kz. Row 4 (200,001-300,000) starts at 31,250 while row 3 ends at 12,500 + 16 % of 49,999 = 20,499: a 10,751 Kz notch. Rows 5-12 continue to within a kwanza. Proved in Lean (notch_150001, notch_200001); the METR scanner reports peaks above 1,000 %.
- provisions: Lei 18/24 art. 20 n.º 3, Anexo I
- Lean: AoTax.monthTax; theorems notch_150001, notch_200001
- status: model result

### F2 The gazetted table is headed 'TABELA DO IRT (Proposta)'
- kind: gov-error
- Anexo I of the enacted OGE 2025 law keeps the bill's heading '(Proposta)' (DR I Série n.º 247 p. 13798). Its 'excesso de' column also prints 100 001, 150 001 ... as the base of the excess, so each row drops a kwanza (2,342,248 at the top row instead of 2,342,249 by continuity).
- provisions: Lei 18/24 Anexo I
- Lean: AoTax.table
- status: model result

### F3 The IRT table lives in the annual budget law, not in the code
- kind: fact
- The CIRT's art. 16 table was last replaced by Lei 28/20; since then each OGE law rewrites the exemption and annexes a table (Lei 15/23 for 2024 and Lei 18/24 for 2025: 100,000 Kz; Lei 14/25 for 2026: 150,000 Kz). A reader of the code alone gets the 2020 table (exempt to 70,000).
- provisions: CIRT art. 16; Lei 28/20 art. 3; Leis 15/23, 18/24, 14/25 art. 20
- Lean: AoTax.table (doc comment)
- status: model result

### F4 Monthly final settlement: bunching pay into one month costs more
- kind: fact
- Art. 10 settles Group A monthly with no annual reconciliation in the articles read; a bonus month moves pay into higher rows (invisible to the annual timing scanner, as B08/B10 found for DJ and RW).
- provisions: CIRT art. 10
- Lean: AoTax.yearIRT (perPeriod 12)
- status: model result

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/AoTax/Verify.lean` (imported by the `AoTax` library and built; each guard evaluates `AoTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/AO.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Two notches built into the 2025 IRT table: one kwanza of monthly base above 150,000 costs 6,000 a year of net (the 12,500 fixed amount where row 2 ends at 6,499), above 200,000 10,750 (31,250 vs 20,499). G: f1_notch_150001, f1_notch_200001 (gross 1,855,669 and 2,474,221 a year, after INSS 3 %); T: AoTax notch_150001, notch_200001, #guard monthTax 150000 = 6499 ∧ 150001 = 12500. S: law/rescue2/angolex_2820.txt:326, :336 (Lei 18/24 Anexo I fixed amounts 12.500 and 31.250). |
| F2 | explained | Table headed '(Proposta)': gov record. |
| F3 | explained | IRT table in the budget law: record. |
| F4 | explained | Monthly final settlement: same mechanism as DJ F1; rescan timing gain 296,004 (two earners) is F1's notches. |
| Leads | explained | Rescan bands above the top rate (2,708 %) at 2.47 M / 6.18 M = F1; the notch list misses them only because each falls in one month of an even annual wage. |
| Lead (2026) | lead | The 2026 table (Lei 14/25, PwC and AngoLEX copies) raises the exemption to 150,000 and starts the next row at 12,500 + 16 %: a 12,500 Kz notch per month at the exemption limit itself. Outside the 2025 model; for the 2026 update. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Two notches built into the 2025 IRT table's fixed amounts | cliff or notch | **new**: PwC Angola prints the 2026 table ('Up to 150,000 Exempt; Between 150,001 and 200,000 12,500 + 16%'; 'Between 200,001 and 300,000 31,250 + 18%'), whose fixed amounts make the jumps, without describing them; a web search found the tables (PLMJ, AngoLEX, KPMG, EY) but no account of the jumps. Note: in 2026 the first jump is 12,500 Kz a month at the exemption limit. | 2026-11-20: OpenAlex queries 'Angola IRT tabela 2025 Lei 18/24 parcela fixa'; 'Angola employment income tax table 2025' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (angola, 5 individual pages): 4 passages with the item's terms; Crossref IMF prefix 10.5089 'Angola tax policy personal income tax' (9161 records, titles only); web search: WebSearch 2026-11-20 'Angola IRT tabela 2025 Lei 18/24 parcela fixa 12.500 salto': PLMJ notes on OGE 2025, angolex.com tables and calculator, KPMG/EY/PwC notes on OGE 2026; no description of the jumps. Record: world/loopholes/africa_mena/search/AO-F1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **AO-R1** IRT Group A (employment table) and Group B (self-employed) taxed separately. Money: 107,952 AOA a year on 3,600,000 (1.5 AW) vs all wages (3 %). Lean: `world/loopholes/round2/v/lean/R2AO.lean` (R2AO.R1 (4 #guard)); exe check `round2/v/out/AO.json`. Provision: Código do IRT, Group B arts. 8-9 (law/rescue2/angolex_2820.txt:86-182); Group B rate as the model reads it. Status: model-proved. Known/new: new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point (`round2/v/novelty/`).
<!-- R2-SCANNERS:END -->
