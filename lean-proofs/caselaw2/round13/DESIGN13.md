# Round 13: the Shadow Docket leftover batch (+ three held classes installed on the user's decision)

Design and contract. Lead: one agent (no track agents; blind auditors are opus sub-agents); started 14 Nov 2026 11:30.
Log: `LOG.md`. State: `PROGRESS.md`. Base: the round-12 frozen build `round12/stage/v12a` (1,871 order nodes, history
192,303) and `round12/out/v12a` (frozen binary s51 a1cc4296, NOBUILD). Round-12 analysis that sets the scope:
`round12/ROUND12.md` (plateau analysis, Shadow row; next moves item 2).

## 0. Binding rules (as DESIGN12 section 0, on round-13 paths)
1. Rules, never rows: every rule is general, runs over the whole corpus (all corpus GVR orders of the round-6 memo
   parse and all 1,871 order-list nodes v12a holds), no case list.
2. Answer keys for scorers only; diagnosis may read only the h0 per-case files of the round-8 keys
   (`round12/results/v12a/bench/<key>.h0.cases.tsv`) and the keys' SOURCE / MAPPING / DISAGREEMENTS notes. No rule
   tests key membership. Dev agreement uses only non-key truths (round-9 `agree.truths`: Reported below, bridge strings,
   list rows) and agreement with v12a's own rows.
3. Closed keys (songer_treat, brace_hall_state, fedcir_dataset, bhk_enbanc, and from this round fjc_idb_unpub) are
   never opened by a model-building step; they are scored once, after `round13/FREEZE.md`.
4. Dev only before the freeze: round-8 h0 halves, old dev halves. After the freeze, once: h1 halves (sixth use),
   Songer and Brace & Hall (fifth use), Federal Circuit (fourth use), bhk_enbanc (third use), fjc_idb_unpub (second
   use), fresh sealed (ninth use, burned), Shepardized sealed (eighth use, burned). Logged in `round13/SEALED_LOG.md`.
5. Evidence = the acting court's own words (order-list nodes: the Journal entry).
6. No external model; all reading and auditing by local Claude sub-agents (opus).
7. Write only under `round13/` (and `wsl/r13_*.sh`, the WSL dirs `data_r13_*`, `difftest/r13_*`, `base_r13_v12a`,
   `r13_bin`). Nothing installed in `data/` or `out/`; round-12 outputs read or copied only. Nothing committed.
8. No Lean change planned. The Lean tree must still build in WSL (`round13/lead/lean_check13.sh`).
9. Disk: C: ~16 GB free at the start; peak extra under ~6 GB; one staged variant at a time; `clean13.sh` after
   scoring; refuse under 8 GB.

## 1. Tools (round13/lead/mk_round13.py: the round-12 tools with base v12a)
certify13 / certify13_claims (ids t13: / h13:, base v12a, node overlay round12/data_orders by default), stage13 (base
v12a; without --nodes v12a's decisions2 + 1,871 nodes are hard links), wsl/r13_run.sh (mirror base_r13_v12a built
from data_r12_v12a by hard links; frozen s51), score13.sh, clean13.sh, freeze13.py, score_sealed13.sh,
audit/make_packs13 (exclusion by identity), score_audit13. Self-test: `v12a_check` (no delta) must reproduce
round12/out/v12a.

## 2. Rules (agent folder round13/agents/shadow13/; each its own blind audit, >= 0.90 "right", whole class when small)
- **D, same person, second docket** (`d13.py`): C8's domain where the full-name candidates lie on two or more dockets
  of the court below. A judgment (C8 v2's judgment test, >= 60 days before the order, before the docket-term bound)
  must fall in the filing window of the order's docket number (on or after 1 July of the year before the docket
  year); exactly one docket may hold such a judgment -> its latest. Several dockets in the window -> no link.
- **S, officer successor** (`alt13.py`): no both-sides tie; one side pair ties by a name token and is the natural
  person whose full printed name is in the decision's head; the other pair names the same public office on both
  sides (attorney general, secretary, commissioner, warden, director, superintendent, sheriff, administrator,
  governor) with different holders (automatic substitution of officers, FRAP 43(c)(2), S. Ct. R. 35.3). Pick C6 / C8 v2.
- **A, agency acronym** (`alt13.py`): no both-sides tie; one side is an acronym of 3-6 capitals that equals the
  initials of the other text's side (of / the / and / for / on / & skipped), the other pair ties as memo side_match.
  Pick C6 / C8 v2.
- **N, name form** (`nf13.py`, item 4, exploratory): the full name with up to two middle names / initials or a
  hyphen variant. Built only if its dev agreement on non-key truths is near the bar.
- Not targeted (as briefed): the 38 reinstated-2005 cases (status semantics), orders without a natural-person side.

## 3. Held classes installed on the user's decision (coordinator message 11:33, from the user)
Recorded in FREEZE.md as "installed on user decision (below bar)"; no new audit; effects reported separately.
- State T4 (round10/agents/stlink10/delta_T4; 245 rows, trialBridge claim + history_tbridge; r10t04 right 0.850,
  link+effect 0.925).
- SCDB R2 v3 (round11/agents/scdb11/cert_r2v3; 88 rows; r11b04 44/49 = 0.898).
- En banc EB12 v6 (round12/agents/enbanc12/cert_eb12b; 101 rows; r12e02 fresh 26/27, biased 64/67).
- R2 v3 x EB12 v6 overlap (D13-2): 12 identical (by, target) pairs; the R2 v3 row is dropped
  (`--drop round13/lead/drop_r2v3_overlap.txt`), the EB12 v6 row kept: 7 pairs had the same kind (vacated; two rows
  for one pair would double the pair), 5 differed (R2 v3 `rehearingEnBancGranted` from a citation note vs EB12
  `vacated` in E's own words that the panel opinion is vacated: the acting court's own words win, and one row per
  pair). A 13th shared target (459355) has two different acting decisions (R2 v3 by 461401, EB12 by 461428): not a
  duplicate pair, both kept.

## 9. Decisions
- D13-1 Base v12a; NOBUILD frozen s51; no --nodes variant needed (every rule acts on nodes v12a holds).
- D13-2 R2 v3 x EB12 v6 overlap resolved as section 3.
- D13-3 Audit exclusion: every earlier Shadow sample (r10k01-03, r11k01-04, r12k01-03) excluded by identity. 3 rows
  (D 1, S 2) were already read in r11k01 (class C11, not installed), all right by both readers there; the whole-class
  audits read the rest.
