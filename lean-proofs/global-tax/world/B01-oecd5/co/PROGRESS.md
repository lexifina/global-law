# CO progress

**Status (2026-11-20 01:48 UTC): built** — Lean model `co/lean` (`cotax`, kernel 1.3.0 `TaxKernel.World`, worldMain), 216 lines, 7 theorems, 0 sorry. Next: software phase (coordinator / test role, TESTING.md), then datasets.

Access tier B. Steps: 1 statute (done; SMMLV missing), 2 validation (deferred), 3 proofs (done), 4-6 scanners (done), 7 USEFUL (done).

## Sources read (dated)

- Global law corpus colombia/national/acts (Secretaría del Senado, basedoc), as in force on 2025-07-01: ET art. 36-1, 55, 56, 103, 206, 241 (text), 242, 254-1, 330-337, 387; Ley 100 de 1993 art. 18, 20, 27, 204
- Senate basedoc official compilation (estatuto_tributario_pr008/pr010/pr014/pr015.html; art. 241 table = image graficas/estatuto_tributario_obj_20.gif, read as an image); Ley 2381 de 2024 page (art. 94 suspended, Sentencia C-264-26)
- DIAN normograma (found through its own search API): Resolución 000193 de 2024 art. 1, UVT 2025 = 49.799 (official secondary)
- Not reached: Decreto of the 2025 minimum wage (SMMLV); the 2008 decree adding one point to the pension rate under Ley 100 art. 20 inc. 4

## Registry correction

Registry row: 'cedular system' is right in form, but since Ley 2277 de 2022 (art. 331) the cédulas general, pensiones and dividendos are summed into one art. 241 base (only ganancias ocasionales stay apart). Act path colombia/national/acts/decreto/1989/624.

## Resume

`cd /home/lean/cmp20/world/B01-oecd5/co/lean && lake build`; samples: see FINDINGS; scanners: `python3 /home/lean/cmp20/world/B01-oecd5/tools/scan_b01.py CO`.

- 2026-11-20 W5 pattern A (contributions agent 2): pension rate 16 % (employee 4 %), base capped at 25 SMMLV for pension and health, Fondo de Solidaridad Pensional 1 % from 4 SMMLV plus 0.2-1 % from 16 SMMLV (INCR); SMMLV 2025 = 1.423.500. Provision: Ley 797 de 2003 arts. 5 (Ley 100 art. 18), 7 (art. 20), 8 (art. 27) (Global law repo); Decreto 4982 de 2007 art. 1 (16 %); Decreto 1572 de 2024 art. 1 (SMMLV) (Colpensiones normogram). Rebuilt (#guards pass), check `w5/pa/check.py CO` 0 / 300 differ with the switch off, rescanned (`scan_world.py CO`).
