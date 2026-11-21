# AD progress

**Status (2026-11-20 02:40 UTC): built** — Lean model `ad/lean` (`adtax`, kernel `TaxKernel.World`, worldMain), 148 lines, 5 theorems, 0 sorry. Next: software phase, then datasets (coordinator / test role).

Access tier A. Steps: 1 statute (done), 2 validation (statute's own printed amounts checked in Lean; official checks deferred: build-only phase), 3 proofs (done), 4-6 generic scanners (done, statutory scale), 7 USEFUL (done).

## Sources read (dated)

- Global law andorra/national/acts/lleis/2014-005 (Llei 5/2014 IRPF, as enacted) and every law modifying it found in the corpus: 2015-008, 2017-017, 2018-006, 2019-018 (DF 8a), 2022-042, 2023-005, 2023-011, 2025-004, 2025-005
- Global law lleis/2008-017 (Llei 17/2008 de la seguretat social) arts. 100, 103 as replaced by lleis/2014-018 arts. 26, 29

## Registry correction

Correct (Llei 5/2014 IRPF). The corpus is as enacted: amendments are separate laws (read for the articles used). Effective tariff 0 % to 24 000, 5 % to 40 000, 10 % above.

## Resume

`cd ~/cmp20/world/B04-europe-rest/ad/lean && lake build`; scanners: `python3 ~/cmp20/world/tools/scan_world.py AD` (scale: 40 000 EUR = the end of the 5 % effective band, `scale.json`).

- 2026-11-20 W5 review pass 4: CASS general branch employee rate 2 % -> 3 % (Llei 17/2008 art. 100.1 as replaced by Llei 2/2016 DF 6a, in force 2016-03-31); FINDINGS W5R4-1. Rebuilt (#guards pass), `world/w5/review4/check4.py AD` with `adCassGeneral2014: true` 0 / 300 differ from the pre-change exe, rescanned.
