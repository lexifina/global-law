# Cambodia (KH) findings, B03-asia-east-se (rescue pass, 2026-11-20T11:11Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 A spouse's first riel of earnings removes the homemaker-spouse relief
- kind: loophole-new (literature not searched: no web search budget)
- Sub-Decree 48/2024 art. 3(2)(b) reduces the base by 150,000 riel a month for a spouse 'who is only a homemaker'. Read literally, any earnings of the spouse end the relief: 1,800,000 riel of annual base, worth 90,000-360,000 riel of tax depending on the earner's band. The generic scanner finds a 36 % METR on the second earner's first 750,000 riel (second_earner_2: net lost 269,999 for the first riel at 15 %). The model treats a spouse with zero earnings as the homemaker; a reading that tolerates small earnings would move the cliff.
- provisions: Law on Taxation 2023 art. 46(2); Sub-Decree 48/2024 art. 3(2)(b)
- Lean: KhTax.wageTax (spA/spB)
- status: model result

### F2 Child relief claimed by one working spouse only: the choice is the taxpayer's
- kind: fact
- Art. 3(2) last sentence gives the child relief to one spouse only when both work, without saying which. The model takes the cheaper assignment (min of both); the gain from choosing well is up to 20 % x 150,000 x 12 per child a year when one spouse is below 1.5m a month and the other in the top band.
- provisions: Sub-Decree 48/2024 art. 3(2)
- Lean: KhTax.wageTax (min o1 o2)
- status: model result

### F3 The Law fixes the rates but leaves every band to a sub-decree
- kind: statute-fault
- Art. 47 of the 2023 Law lists the rates (0, 5, 10, 15, 20 %) and leaves the bands, and art. 46(2) the family reliefs, to a sub-decree. Three sub-decrees on the bands are listed by the GDT (09/2020, 196/2022, 48/2024); only the latest is in force. A reader of the Law alone cannot compute the tax.
- provisions: Law on Taxation 2023 arts. 46(2), 47; Sub-Decrees 09/2020, 196/2022, 48/2024 (GDT list)
- Lean: KhTax.sched
- status: model result

### F4 Sole proprietorships use the same five rates on annual bands 12 x the monthly ones
- kind: fact
- Sub-Decree 48/2024 art. 4: 18m/24m/102m/150m a year vs 1.5m/2m/8.5m/12.5m a month: identical to 12 x the monthly bands, so an employee and a sole proprietor with the same steady income pay the same; an uneven monthly salary pays more than the annual equivalent (no annual reconciliation for employees in the articles read).
- provisions: Sub-Decree 48/2024 arts. 3(1), 4
- Lean: KhTax.schedSP, KhTax.sched
- status: model result

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 180,000 KHR a year for an earner in the 10 % band, 360,000 in the 20 % band, for the spouse's first riel of pay. exe and #guard L1KH.F1; Khmer OCR re-read. A reading that tolerates small earnings would move the edge. Evidence: exe + Lean `L1KH.F1` (`world/loopholes/rest/lean/L1KH.lean`, 2 #guard): tot(b)-tot(a) = 180000; tot(d)-tot(c) = 360000; statute re-read: `law/rescue/sd48_khm_ocr.txt`. Known/new: **new**: The homemaker-spouse relief is published (KPMG Cambodia technical update 2024; DFDL example); no hit describes its loss on the spouse's first riel; web search 14 + Crossref. |
| F2 | fact | confirmed | Art. 3 (2) last sentence re-read ('ត្រូវបានផ្តល់ឱ្យតែសហព័ទ្ធម្នាក់ប៉ុណ្ណោះ'); the model takes the cheaper assignment. Evidence: exe + Lean `L1KH.F2` (`world/loopholes/rest/lean/L1KH.lean`, 1 #guard): it(a) = 24939996; statute re-read: `law/rescue/sd48_khm_ocr.txt`. |
| F3 | statute-fault | explained | Recorded statute-fault with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F4 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/KH.json`): notch 269,999 at 0 and the 36 % band (second earner) = F1.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **KH-R1** Salary tax and the tax on a sole proprietor's income are separate taxes, each with its own 0 % band (1.5 M riel a month; 18 M a year): paying half as salary and half as business income. Money: 14,700,000 KHR a year less on 300,000,000 (2 AW): 30.6 M vs 45.3 M either way (4.9 %). Lean: `world/loopholes/round2/v/lean/R2KH.lean` (R2KH.R1 (4 #guard)); exe check `round2/v/out/KH.json`. Provision: Law on Taxation 2023 (salary tax); Sub-decree 48/2024 art. 4 bands (model citation; Khmer OCR in law/rescue/sd48_khm_ocr.txt, provision not re-located). Status: model-proved. Known/new: new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point; web search 1 (PwC: consulting income outside salary tax and under the tax on income; both 0 % bands) found no description of the doubled band (`round2/v/novelty/`).
<!-- R2-SCANNERS:END -->
