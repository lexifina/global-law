# Argentina (AR) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 'Incrementar en 3,8 veces' means 4.8 times
- kind: statute-fault
- art. 30 (c) 2 says the special deduction is the art. 30 (a) amount 'incrementar … en tres coma ocho (3,8) veces'; ARCA's 2025 figure (21,636,026.50) is 4.8 × 4,507,505.52: the wording reads as 'increase by 3.8 times'. A drafting ambiguity settled by ARCA's table; checked by #guard.
- provisions: art. 30 (c) 2
- Lean: ArTax #guard
- status: proved (#guard)

### F2 Contributions with no ceiling in the model
- kind: model-fix
- The maximum contribution base (Ley 24.241 art. 9, updated by ANSES) was not reached: contributions and taxable income are wrong above it (flagged).
- provisions: Ley 24.241 art. 9
- Lean: ArTax.contribRate
- status: open

### F3 Generic scan: no notch, max METR 46 %
- kind: model-fix
- b02scan.
- provisions: -
- Lean: results/search/b02scan.md
- status: scan done


### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Ley 24.241 art. 9 (texto Ley 26.222), ANSES Resoluciones 1247/2024, 66, 145, 179, 211, 237, 251, 278, 298, 317, 338, 359/2025 art. 3 (Boletín Oficial)
- SIPA 11 % computed monthly on wages / 12 capped at the ANSES maximum base of each 2025 month (2.910.574,49 in January to 3.731.212,01 in December); INSSJP and obra social 3 % + 3 % stay on all wages. Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: maximum base applied to the 11 % only (INSSJP / obra social cap not established); minimum base and the SAC cap not applied.
- status: fixed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | proved | LIG art. 30 c) 2 re-read ('Tres coma ocho (3,8) veces'); ArTax #guard on ARCA's 21,636,026.50 (model build). Drafting ambiguity, settled by ARCA. Evidence: exe + Lean `L1AR.F1` (`world/loopholes/rest/lean/L1AR.lean`, 1 #guard): it(a) = 0; statute re-read: `law/lig_actualizado.txt`. |
| F2 | record | withdrawn | Superseded by W5A-1 (SIPA 11 % capped at the ANSES maximum base of each month). |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| L1 | loophole | confirmed | 406,707 ARS of tax for one peso of the spouse's pay with the main earner at 40 M; 1,609,626 at 100 M (35 % x 4,245,166 + effects). Found blind by the fresh METR scan (second earner, 345.8 %; notch 873,796 on the scan's household); exe and #guard L1AR.L1. Whether 'ingresos netos' is before or after the spouse's own contributions moves the edge (the model compares wages): a reading. Evidence: exe + Lean `L1AR.L1` (`world/loopholes/rest/lean/L1AR.lean`, 2 #guard): tot(b)-tot(a) = 406707; tot(d)-tot(c) = 1609626; statute re-read: `law/lig_actualizado.html`. Known/new: **new**: The condition is published (iProfesional 'Cuándo se puede deducir al cónyuge en Ganancias', CONICET deductions summary 2025, ARCA deductions page); no hit describes that one peso over the limit loses the whole deduction; web search 4 + Crossref. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/AR.json`): METR 345.8 % (second earner) and notch 873,796 = L1 (new); timing 873,798 = L1; marriage bonus 1,609,626 = the spouse deduction itself; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.

### L1 The spouse deduction (cargas de familia) is lost in full once the spouse's income passes the art. 30 a) amount: one peso costs the other spouse up to about 1.6 M ARS
- kind: loophole (found blind by the L1 re-scan)
- amounts: 406,707 ARS of tax for one peso of the spouse's pay with the main earner at 40 M; 1,609,626 at 100 M (35 % x 4,245,166 + effects)
- who: one-earner couples where the second spouse earns about 4.5 M ARS a year (2025)
- provisions: LIG art. 30 b) ('no tengan en el año ingresos netos superiores a ...'), b) 1 (cónyuge)
- Lean: `L1AR.L1` in `world/loopholes/rest/lean/L1AR.lean` (#guard on the model's `country.compute`)
- status: confirmed (Found blind by the fresh METR scan (second earner, 345.8 %; notch 873,796 on the scan's household); exe and #guard L1AR.L1. Whether 'ingresos netos' is before or after the spouse's own contributions moves the edge (the model compares wages): a reading.)
- novelty: new: The condition is published (iProfesional 'Cuándo se puede deducir al cónyuge en Ganancias', CONICET deductions summary 2025, ARCA deductions page); no hit describes that one peso over the limit loses the whole deduction; web search 4 + Crossref.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Model fix (statute)**: LIG art. 30 (c) 2 special deduction now capped by the person's net wages (it went in full to self-employment income once wages > 0). `ArTax/Basic.lean` #guards, lake build ok, LESSONS.md 2026-11-21.
- **AR (model fix)** One peso of wages gave the whole 3.8 x MNI special deduction (21.6 M ARS) to self-employment income. Money: up to 14 % of income at 0.5 AW before the fix (mix.py). Lean: `world/loopholes/round2/v/lean/R2AR.lean` (ArTax/Basic.lean #guards (2)); exe check `round2/v/out/AR.json`. Provision: LIG art. 30 (c) 2 'cuando se trate de ganancias netas comprendidas en los incisos a), b) y c) del artículo 82' (law/lig_actualizado.txt:255-259). Status: statute fault in the model, fixed and rebuilt. Known/new: n/a (model error) (`round2/v/novelty/`).
- mix.py (wage vs fee split): model fixed (LIG art. 30 (c) 2, see top); the gain left comes from autonomous contributions the model does not charge: explained.
- ceilings.py: ceiling at 0.66 AW (contribution rate 17.0 -> 11.8 %, combined marginal 18 -> 21 %); ceiling at 0.86 AW (contribution rate 7.2 -> 6.0 %, combined marginal 24 -> 24 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
