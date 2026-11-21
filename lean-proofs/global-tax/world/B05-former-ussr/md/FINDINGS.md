# Moldova (MD) findings, B05-former-ussr (rescue pass, 2026-11-20T11:11Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 Personal exemption withdrawn in full at 360,000 lei: a 3,565-lei notch
- kind: loophole-new (literature not searched: no web search budget)
- Art. 33(1) grants 29,700 lei only to a resident whose annual taxable income is below 360,000 lei. At 12 % the exemption is worth 3,564 lei, so the tax jumps from 39,635 to 43,200 lei at 360,000 and net income does not recover until 364,050 lei. Generic scanner: METR 210 % over 358,200-360,000 for every family, two notches for a two-earner couple. Timing (moving a bonus across 31 December) or splitting income with a spouse avoids it.
- provisions: Codul fiscal art. 33(1) (Law 214/2024)
- Lean: MdTax.pe, MdTax.tax1 (#guard)
- status: model result

### F2 The 360,000-lei test is circular as written
- kind: statute-fault
- Art. 12 pct. 4 defines 'venit impozabil' as gross income less deductions and exemptions (art. 33-35); art. 33(1) conditions the exemption on 'venit anual impozabil' < 360,000, which would include the exemption itself. The model reads it as income before the personal exemption; the other reading moves the limit to 389,700 lei of income after deductions.
- provisions: Codul fiscal art. 12 pct. 4, 12; art. 33(1)
- Lean: MdTax.pe
- status: model result

### F3 No rule on which parent claims a dependant
- kind: statute-fault
- Art. 35 grants 9,900 lei per dependant to 'the taxpayer' and defines dependants by kinship to the taxpayer or the spouse, but states no rule for two parents claiming the same child. The model gives each child to one parent (the higher earner); with a flat rate the choice matters only when one parent's income is below the exemptions.
- provisions: Codul fiscal art. 35(1),(2)
- Lean: MdTax.out
- status: model result

### F4 The Codul fiscal is hard to read from official servers
- kind: gov-error
- legis.md (the State Register) answers 403 to scripts from two networks and Global law holds only the 2019 table of contents; the text in force was reached only through the Ministry of Finance's link to a private publisher (weblex.md) whose text loads by script. The consolidated text there is current (last change in force 01.11.2026) with dated notes, which is how the 2025 wording was established.
- provisions: -
- Lean: -
- status: access note

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 3,565 MDL for one leu at 360,000. exe and #guard L1MD.F1. Evidence: exe + Lean `L1MD.F1` (`world/loopholes/rest/lean/L1MD.lean`, 1 #guard): it(b)-it(a) = 3565; statute re-read: `law/rescue/weblex_cf_current.txt`. Known/new: **known**: Monitorul Fiscal (State Tax Service), Q&A 29.2.3.66 and 'Cum determinăm plafonul de 360 mii lei', states that the exemption is lost at 360,000 lei or more; web search 9. |
| F2 | statute-fault | explained | Circular test; reading recorded. |
| F3 | statute-fault | explained | No claimant rule; the model's choice. |
| F4 | gov-error | explained | Access note. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/MD.json`): METR 210 % and notches 3,564 = F1 (couples at 1.67 / 2.5 x scale); timing 7,130 (couple) = F1.
