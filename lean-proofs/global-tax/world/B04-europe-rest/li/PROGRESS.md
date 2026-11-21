# LI progress

**Status (2026-11-20 02:40 UTC): built** — Lean model `li/lean` (`litax`, kernel `TaxKernel.World`, worldMain), 153 lines, 3 theorems, 0 sorry. Next: software phase, then datasets (coordinator / test role).

Access tier B. Steps: 1 statute (done), 2 validation (statute's own printed amounts checked in Lean; official checks deferred: build-only phase), 3 proofs (done), 4-6 generic scanners (done, statutory scale), 7 USEFUL (done).

## Sources read (dated)

- gesetze.li konso/pdf/2010340000?version=33: Steuergesetz (SteG, LGBl. 2010 Nr. 340), 'Fassung: 01.01.2025' (includes LGBl. 2025 Nr. 541, applied to the 2025 assessment); version list on konso/2010340000/meta (01.01.2025 - 31.12.2025)
- gesetze.li konso 1952029000 version 58: AHVG 'Fassung: 01.01.2025', Art. 38 (4.025 %)
- gesetze.li konso 1960005000 version 42: IVG 'Fassung: 01.01.2024' (0.675 % each), next version not before 2026
- gesetze.li konso 2010452000 version 19: ALVG 'Fassung: 01.01.2023' (1 % shared, ceiling 126 000), next version 01.01.2026
- Global law liechtenstein/national/acts (current texts only) used to find the acts and their official links

## Registry correction

Correct (SteG 2010). Global law holds only the 2026-07-01 consolidation; the dated versions are on gesetze.li (konso/<id>/meta lists each Fassung, konso/pdf/<id>?version=N serves it; two placeholder 'DUMMY' versions exist for laws in force only from 2026).

## Resume

`cd ~/cmp20/world/B04-europe-rest/li/lean && lake build`; scanners: `python3 ~/cmp20/world/tools/scan_world.py LI` (scale: 79 300 CHF of pay (start of the 5 % row of Art. 19 Bst. a after expenses and contributions), `scale.json`).
