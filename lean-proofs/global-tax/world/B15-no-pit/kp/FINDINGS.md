# Democratic People's Republic of Korea (KP) findings, B15-no-pit (rescue pass 2, 2026-11-20T13:10Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 The only text for the absence of income tax is a constitutional statement in translation
- kind: fact
- Art. 25 of the 2016 text states that taxes 'have been abolished'. The 1974 abolition law and the post-2016 constitutional revisions were not reached; contributions withheld from wages (if any) are outside the text.
- provisions: Constitution of the DPRK (rev. 2016) art. 25
- Lean: KpTax.out
- status: model result

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | fact | explained | Constitutional statement. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/KP.json`): no lead.
