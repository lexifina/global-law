# TR progress

**Status (2026-11-20 01:48 UTC): built** — Lean model `tr/lean` (`trtax`, kernel 1.3.0 `TaxKernel.World`, worldMain), 285 lines, 16 theorems, 0 sorry. Next: software phase (coordinator / test role, TESTING.md), then datasets.

Access tier A. Steps: 1 statute (done), 2 validation (official checks deferred: build-only phase), 3 proofs (done), 4-6 scanners (done), 7 USEFUL (done).

## Sources read (dated)

- Global law corpus turkey/national/acts (Mevzuat Bilgi Sistemi): GVK 193 art. 21, 22, 23, 31, 63, 74, 75, 86, 92, 94, 103, 104 (current-only consolidation of 2026-10-28; 2025 wording established from the amendment notes, none dated 2025)
- Tebliğ 41166 = Gelir Vergisi Genel Tebliği (Seri No: 329), in force 1/1/2025: 2025 tariff and revalued amounts
- Tebliğ 42582 = Gelir Vergisi Genel Tebliği (Seri No: 331): gross minimum wage 26.005,50 TL and the 2025 SGK ceiling 195.041,40 TL (official secondary)
- 5510 art. 81 (rates), 82 (ceiling 7,5 × minimum wage; 9 × only from 1/1/2026, Kanun 7566 per the 5510 yürürlük list), dipnotlar 141, 155, 156
- 4447 art. 49 (unemployment premium 1 %, deductible); 488 Damga Vergisi Kanunu (1) sayılı tablo IV-1 (b) 7,59 ‰ and (2) sayılı tablo IV-34 minimum-wage exemption

## Registry correction

Registry row correct (GVK 193, progressive, individual). Add: wage tariff differs from the general one (27 % band to 1.200.000 TRY in 2025); 2025 amounts are in Tebliğ 41166 (GVK Genel Tebliği Seri 329), not in the consolidated act; Global law act path turkey/national/acts/law/1960/193 (current-only).

## Resume

`cd /home/lean/cmp20/world/B01-oecd5/tr/lean && lake build`; samples: see FINDINGS; scanners: `python3 /home/lean/cmp20/world/B01-oecd5/tools/scan_b01.py TR`.
