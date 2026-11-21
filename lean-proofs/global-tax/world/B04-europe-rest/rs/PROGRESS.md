# RS progress

**Status (2026-11-20 02:40 UTC): built** — Lean model `rs/lean` (`rstax`, kernel `TaxKernel.World`, worldMain), 142 lines, 6 theorems, 0 sorry. Next: software phase, then datasets (coordinator / test role).

Access tier B. Steps: 1 statute (done), 2 validation (statute's own printed amounts checked in Lean; official checks deferred: build-only phase), 3 proofs (done), 4-6 generic scanners (done, statutory scale), 7 USEFUL (done).

## Sources read (dated)

- Global law serbia/national/acts/zakon/2001/24-1 (Zakon o porezu na dohodak građana) as in force 2025-07-01; provision_history of čl. 15a
- Global law serbia/national/acts/zakon/2004/84-37 (Zakon o doprinosima za obavezno socijalno osiguranje) čl. 37-44

## Registry correction

Correct (schedular salary tax + annual citizens' income tax). Add: the annual tax needs the year's average annual salary (statistics), and contributions have minimum/maximum bases published by the minister: neither reached.

## Resume

`cd ~/cmp20/world/B04-europe-rest/rs/lean && lake build`; scanners: `python3 ~/cmp20/world/tools/scan_world.py RS` (scale: 1 364 304 RSD = 12 × 4 × the monthly non-taxable amount 28 423, `scale.json`).
