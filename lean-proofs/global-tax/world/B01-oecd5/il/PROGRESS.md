# IL progress

**Status (2026-11-20 01:48 UTC): built** — Lean model `il/lean` (`iltax`, kernel 1.3.0 `TaxKernel.World`, worldMain), 203 lines, 8 theorems, 0 sorry. Next: software phase (coordinator / test role, TESTING.md), then datasets.

Access tier B. Steps: 1 statute (done; NI ceiling missing), 2 validation (deferred), 3 proofs (done), 4-6 scanners (done), 7 USEFUL (done).

## Sources read (dated)

- Global law: Israel corpus holds the Basic Laws only; statute texts from Hebrew Wikisource (the publisher Global law uses for Israel) at the mid-2025 revisions: Income Tax Ordinance (rev. 2935650, 2025-05-27) s. 33א, 34, 36, 36א, 40, 66(ג), 120ב, 121, 121ב, 125ב; National Insurance Law (rev. 2946268) s. 334, לוח י׳, לוח י״א; National Health Insurance Law (rev. 2924411) s. 14
- National Insurance Institute page 'שיעורי דמי ביטוח לעובדים שכירים' (btl.gov.il; official secondary): employee rates with start dates
- gov.il (Tax Authority) answered 403 to scripts: not bypassed

## Registry correction

Registry row correct in substance (Income Tax Ordinance, credit points, surtax, health tax). Global law holds no tax law for Israel: source Hebrew Wikisource (publisher Global law uses for Israel) + NII. Unit: separate computation for spouses (s. 66).

## Resume

`cd /home/lean/cmp20/world/B01-oecd5/il/lean && lake build`; samples: see FINDINGS; scanners: `python3 /home/lean/cmp20/world/B01-oecd5/tools/scan_b01.py IL`.
