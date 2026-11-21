# XK progress

**Status (2026-11-20 02:40 UTC): built** — Lean model `xk/lean` (`xktax`, kernel `TaxKernel.World`, worldMain), 126 lines, 8 theorems, 0 sorry. Next: software phase, then datasets (coordinator / test role).

Access tier A. Steps: 1 statute (done), 2 validation (statute's own printed amounts checked in Lean; official checks deferred: build-only phase), 3 proofs (done), 4-6 generic scanners (done, statutory scale), 7 USEFUL (done).

## Sources read (dated)

- Global law kosovo/national/acts/ligje/05-l-028 (Ligji 05/L-028, in force 2015-09-01)
- Global law kosovo/national/acts/ligje/08-l-142 (Ligji 08/L-142, published 23.08.2024, neni 5 replaces neni 6 of 05/L-028)
- gzk.rks-gov.net ActDetail ActID=11014 (lists 08/L-142 as the only amending act)
- Ligji 04/L-101 neni 6.2 (5 % employee pension contribution); Ligji 05/L-116 neni 37.2 (not taxable)

## Registry correction

Correct (Law 05/L-028); add the amending Law 08/L-142 (rate table from 23 August 2024): 0 % to 3 000, 8 % to 5 400, 10 % above.

## Resume

`cd ~/cmp20/world/B04-europe-rest/xk/lean && lake build`; scanners: `python3 ~/cmp20/world/tools/scan_world.py XK` (scale: 10 800 EUR = 2 × the start of the 10 % band, `scale.json`).
