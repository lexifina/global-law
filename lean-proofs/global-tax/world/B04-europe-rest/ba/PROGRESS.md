# BA progress

**Status (2026-11-20 02:40 UTC): built** — Lean model `ba/lean` (`batax`, kernel `TaxKernel.World`, worldMain), 150 lines, 7 theorems, 0 sorry. Next: software phase, then datasets (coordinator / test role).

Access tier A. Steps: 1 statute (done), 2 validation (statute's own printed amounts checked in Lean; official checks deferred: build-only phase), 3 proofs (done), 4-6 generic scanners (done, statutory scale), 7 USEFUL (done).

## Sources read (dated)

- Global law bosnia-and-herzegovina/federation/acts/zakon/2008/sn010-d2c23a (Zakon o porezu na dohodak, SN FBiH 10/08) and amendments 9/10, 44/11, 7/13, 65/13
- Global law .../zakon/2008/sn014-e1da71 (Zakon o izmjenama i dopunama Zakona o doprinosima 14/08: član 10 rates)
- Global law .../zakon/2025/sn033-dc3da3 (Zakon o doprinosima 33/25: employer rates from 1 July 2025)

## Registry correction

Correct (FBiH Law on income tax, flat 10 %). Default entity: Federation of BiH; Republika Srpska and Brčko not modelled. The corpus is as enacted: the amending laws are separate acts.

## Resume

`cd ~/cmp20/world/B04-europe-rest/ba/lean && lake build`; scanners: `python3 ~/cmp20/world/tools/scan_world.py BA` (scale: 36 000 BAM = 10 × the basic personal deduction, `scale.json`).
