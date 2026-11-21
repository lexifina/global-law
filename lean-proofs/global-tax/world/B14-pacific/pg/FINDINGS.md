# Papua New Guinea (PG) findings, B14-pacific (rescue pass 2, 2026-11-20T13:10Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 The printed band edges leave one-kina gaps
- kind: statute-fault
- Table 1 reads 'Does not exceed K20,000.00 / exceeds K20,001.00 but does not exceed K33,000.00 / exceeds K33,001.00 ...': income between 20,000 and 20,001 (and between 33,000 and 33,001, etc.) is in no row, and 'exceeds K250,001.00' leaves 250,001 itself out. The model reads the rows as excesses over 20,000 / 33,000 / 70,000 / 250,000.
- provisions: Income Tax (Salary or Wages Tax)(Rates) Act 1979 Sch. 1 Part 7 Table 1 (Act No. 25 of 2023)
- Lean: PgTax.table1
- status: model result

### F2 From 2025 the fortnightly tables are administrative
- kind: fact
- New s. 1(5): 'the fortnightly tax tables for employees under Schedule 1, shall be issued administratively by the Commissioner General'. The Act now holds only the annual scale; what employers withhold each fortnight is set outside the Act.
- provisions: Act No. 18 of 2024 s. 1(c)
- Lean: -
- status: model result

### F3 Residents and non-residents: the tax-free band is the whole difference
- kind: fact
- From 2025 non-residents pay 30 % from the first kina (Table 2A) where residents pay 0 % to K20,000 and the same rates above: a flat K6,000 difference above K33,000.
- provisions: Tables 1 and 2A
- Lean: PgTax.table1
- status: model result

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | explained | Gaps read as excesses. |
| F2 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F3 | fact | explained | Non-resident difference (fact). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/PG.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (model taxes only wages).
