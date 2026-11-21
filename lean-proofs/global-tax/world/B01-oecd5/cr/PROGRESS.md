# CR progress

**Status (2026-11-20 01:48 UTC): built** — Lean model `cr/lean` (`crtax`, kernel 1.3.0 `TaxKernel.World`, worldMain), 188 lines, 7 theorems, 0 sorry. Next: software phase (coordinator / test role, TESTING.md), then datasets.

Access tier A. Steps: 1 statute (done), 2 validation (deferred), 3 proofs (done), 4-6 scanners (done), 7 USEFUL (done).

## Sources read (dated)

- Global law: corpus empty (metadata only); official publisher SINALEVI / SCIJ (Procuraduría General de la República) through its own search and full-text endpoint (tools/sinalevi.py)
- Ley 7092 del Impuesto sobre la Renta (version 83 of 83): art. 1, 15, 28 bis, 29, 29 bis, 31 ter, 32-36
- Decreto Ejecutivo 44772-H (2025 amounts: salary scale, credits, profits scale, art. 7 'Rige a partir del primero de enero de dos mil veinticinco')
- Ley 2412 (aguinaldo, art. 1-2); Reglamento del Seguro de Salud art. 62; Reglamento IVM art. 33 + Transitorio XI table (image); Ley 4351 art. 5

## Registry correction

Registry row correct (Ley 7092, schedular). Global law corpus empty: source SINALEVI (IdFichaNorma 10969). Unit individual; territorial (art. 1).

## Resume

`cd /home/lean/cmp20/world/B01-oecd5/cr/lean && lake build`; samples: see FINDINGS; scanners: `python3 /home/lean/cmp20/world/B01-oecd5/tools/scan_b01.py CR`.
