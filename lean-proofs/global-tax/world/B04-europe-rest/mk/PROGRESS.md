# MK progress

**Status (2026-11-20 02:40 UTC): built** — Lean model `mk/lean` (`mktax`, kernel `TaxKernel.World`, worldMain), 113 lines, 5 theorems, 0 sorry. Next: software phase, then datasets (coordinator / test role).

Access tier B. Steps: 1 statute (done), 2 validation (statute's own printed amounts checked in Lean; official checks deferred: build-only phase), 3 proofs (done), 4-6 generic scanners (done, statutory scale), 7 USEFUL (done).

## Sources read (dated)

- Global law north-macedonia/national/acts/zakon/2018/sv241-43203 (ЗДЛД 241/2018, as enacted) + 2019/sv275-51389, 2020/sv290-54430, 2021/sv085-55742, 2022/sv274-61525
- ujp.gov.mk/mk/regulativa/opis/425 ('Ажуриран со ... 274 од 20.12.2022', 'Важи од 01.01.2023')
- Global law zakon/2018/sv247-43202 (ЗПЗСО 247/2018: член 25 rates), 2022/sv251-61235, 2025/sv003-68970, 2025/sv267-72553 (from 2026)
- UJP consolidated ЗПЗСО text 07/2026 (ujp.gov.mk/files/attachment/0000/1616/...; mk/src/zpzso_ujp_2026-07.txt), used to locate articles only

## Registry correction

Correct (flat 10 %). Correction: the Global law corpus holds this act as enacted (not dated versions); the amendments are separate acts.

## Resume

`cd ~/cmp20/world/B04-europe-rest/mk/lean && lake build`; scanners: `python3 ~/cmp20/world/tools/scan_world.py MK` (scale: 960 000 MKD = 10 × the tax reduction printed in the act, `scale.json`).
