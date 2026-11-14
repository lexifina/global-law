## Classes in the frozen build (on top of round 12's frozen v12a)

| class | source | rows | audit | basis |
|---|---|---|---|---|
| Shadow D: same person, second docket (filing window, one docket) | round13/agents/shadow13/cert_D | 16 | r13k01 whole class 14/15 = 0.933 [0.702, 0.988] (+1 read right in r11k01) | audited, at or above the 0.90 bar |
| Shadow S: officer successor (same office, other holder) | round13/agents/shadow13/cert_S | 11 | r13k02 whole class 9/9 = 1.000 [0.701, 1.000] (+2 read right in r11k01) | audited, at or above the 0.90 bar |
| Shadow A: agency acronym spelled out | round13/agents/shadow13/cert_A | 8 | r13k03 whole class 8/8 = 1.000 [0.676, 1.000] | audited, at or above the 0.90 bar |
| State T4: section-6 trial bridge (trialBridge claim + history_tbridge) | round10/agents/stlink10/delta_T4 | 245 | r10t04 right 68/80 = 0.850 [0.756, 0.912]; link+effect 74/80 = 0.925 | **installed on user decision (below bar)**: link+effect basis |
| SCDB R2 v3: en banc vacatur / rehearing en banc notes | round11/agents/scdb11/cert_r2v3 minus round13/lead/drop_r2v3_overlap.txt | 88 - 12 = 76 | r11b04 44/49 = 0.898 [0.782, 0.956] (fresh sample under 80) | **installed on user decision (below bar)** |
| En banc EB12 v6: E's own words vacate the panel opinion | round12/agents/enbanc12/cert_eb12b | 101 | r12e02 fresh remainder 26/27 = 0.963; r12e01 biased 64/67 | **installed on user decision (below bar)**: fresh sample under 80 (D12-4) |

R2 v3 x EB12 v6 (D13-2): the 12 identical (acting decision, target) pairs keep the EB12 v6 row only (7 same kind, 5
`rehearingEnBancGranted` vs `vacated`: the acting court's own vacatur words win; one row per pair).
Not installed: rule N (name form, item 4; dev 9/13 on non-key truths, not audited). Pending user decisions left as
they are: the 139 section-5.2 identity lines, the 47 OT2025 orders of Jan-Jun 2026 (still in the build, as in v12a),
data hygiene, New Jersey attribution.
