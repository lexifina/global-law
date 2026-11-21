# CL progress

**Status (2026-11-20 01:48 UTC): built** — Lean model `cl/lean` (`cltax`, kernel 1.3.0 `TaxKernel.World`, worldMain), 274 lines, 10 theorems, 0 sorry. Next: software phase (coordinator / test role, TESTING.md), then datasets.

Access tier B. Steps: 1 statute (done), 2 validation (deferred: build-only phase), 3 proofs (done), 4-6 scanners (done), 7 USEFUL (done).

## Sources read (dated)

- Global law corpus chile/national/acts (BCN LeyChile), as in force on 2025-07-01: LIR (DL 824) art. 17, 20, 42, 42 bis, 43, 44, 46, 47, 50, 52, 52 bis, 54, 55, 55 bis, 56, 57, 57 bis, 75; DL 3.500 art. 16, 17, 84, 85; Ley 19.728 art. 5, 6
- SII (official secondary): UTM/UTA and IPC 2025 (utm2025.htm, utm2024.htm), UF daily values (uf2024.htm, uf2025.htm), correccion2025.htm
- Superintendencia de Pensiones resolutions in the Diario Oficial, found by a scan of the daily index (tools/do_scan.py): Res. ex. 47 and 48 (17-01-2025: 131,8 and 87,8 UF from 1 January) and Res. ex. 253 and 254 (18-02-2025: 131,9 and 87,8 UF from 1 February, definitive INE index 4,2 %)

## Registry correction

Registry row correct (DL 824, UTM/UTA). Global law act path chile/national/acts/dl-824 (dated versions; official link https://www.bcn.cl/leychile/navegar?idNorma=6368). Type: monthly final wage tax (impuesto único) with an annual global overlay; individual.

## Resume

`cd /home/lean/cmp20/world/B01-oecd5/cl/lean && lake build`; samples: see FINDINGS; scanners: `python3 /home/lean/cmp20/world/B01-oecd5/tools/scan_b01.py CL`.
