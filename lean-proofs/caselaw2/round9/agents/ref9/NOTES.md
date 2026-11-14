# Round 9, agent `ref9`: the Python reference for round-9 rules (part zones, DESIGN9 §4; later sections by INBOX)

Written from `round9/DESIGN9.md` and the round-8 reference / harness (`round8/agents/ref8/`). No `.lean` file, nothing
under `LegalProofs/`, not `round9/LEAN9.md`, not `round8/LEAN8.md` is opened. Open readings: `REF_QUESTIONS9.md`.

## Log (clock times from `date`)

- 02:10 started; read BRIEF, COMMON, DESIGN9, round-8 ref8 NOTES / BRIEF.
- 02:11 backup: `tools/caselaw2/ref/*.py`, `REF_NOTES.md`, `labels.json` -> `round9/pre/ref/` (precedent_ref.py sha1
  da8e17ce, the round-8 final).
- 02:12-02:18 DESIGN9 §4 in the reference (`Data` loads `part_zone.tsv`: bad lines, poisoned / overlapping nodes;
  `Engine.zone_result` / `zone_apply`; counters zone_nodes, zone_lines, zone_bad_nodes, zone_bad_rows,
  zone_checked_rows, zone_failed_rows, zone_missing_rows in ref_stats.tsv only with a line); `labels.json`
  partZone; `diff.py` SUMMARY_KEYS9 (+ `bad_rows part_zone.tsv`). Readings Q9-1..Q9-10 in `REF_QUESTIONS9.md`.
- 02:16-02:18 `make_r9.py` (gen / check / empty / report): make_r7 universe + make_r8 overlay + a part_zone.tsv built
  from the rows' quotes (node flavours good/missing/overlap/dup/eq/gt/badpart/elsewhere/badline_keep/zeros/touch_all,
  cluster mutations inside/exact/otherpart/straddle/shift/short/touch_split/none, target-only and unknown-node lines,
  bad lines, CRLF / BOM / no final newline); expectations from the round-8 verdicts + an independent model of §4.
- 02:19 INBOX: D9-4 (text-owner zones; after the full round-8 verdict incl. power). 02:19-02:23 `powercheck.py`:
  which rows the round-8 Lean writes targetLater / noAuthority (stored r8ref universes): treatments targetLater =
  date(by) < date(target) both known (witness: date(Y) < date(X)); noAuthority = NEG_TREAT kind and can_change(scope
  domain) no; history noAuthority = same_case_power no. Reference changed: text owner (W / target for own text),
  the gate `lean_cert_passes`, recognised rows zone-checked (Q9-11). Self-check 4 universes: 1,259 expectations / 28
  counters, 0 differ.
- 02:24-02:26 `check_regress9.sh regress9a` (WSL snapshot ~/caselaw2/r9ref/lp, ref 3bb763b2): the current reference,
  no round-9 table, on 534 stored universes of ~/caselaw2/r8ref (435 earlier + 9 round-8 kept + 90 round-8 sweep):
  bytes against the stored round-8 reference output 534/534 the same; canonical diff against the stored round-8 Lean:
  only the 12 known witness-class W universes (u90001, u94016, u94043, u94052, p95009, p95013, p95028, v84006,
  v84024, v84039, g86000, g86013), as at the end of round 8. `results/regress9a.txt`.
- 02:27 kept universes `universes/` (z90000-90003 main, y91000-91002 probe, x92000-92001 fuzz K=8): self-check 1,741
  expectations / 49 counters, 0 differ (`check_kept_cases.txt`); `empty` (part_zone absent / empty / blank against
  `round9/pre/ref`; unknown-node + bad lines only: all files but ref_stats the same): 9 universes, 0 differing files
  (`check_empty.txt`). `difftest9.sh` (setup / refsync / regress / kept / sweep / dirs / all) ready for LEAN_READY.
- 02:26 started: real-data zone verdicts (`zone_verdicts9.py`, Data + admit only) on base_r9_v8e + calpart9's
  02:17 zone table, against calpart9's refused.tsv (223).
- 02:26-02:29 real data (`zone_verdicts9.py`, Data + admit, ~3 min): base_r9_v8e + calpart9's 02:17 zone table
  (582,968 lines, 208,557 nodes): zone_bad_nodes 0, zone_bad_rows 0, zone_checked_rows 220,455, zone_failed_rows
  223, zone_missing_rows 0; the reference's 223 partZone rows (220 history, 3 treatments) = calpart9's refused.tsv,
  223/223 both, none on one side only. (`~/caselaw2/r9ref/real/zv_calpart9_0217.{txt,tsv}`)
- 02:28 INBOX: DESIGN9 §5 joinedFar and §7 implicitReject (D9-5). 02:30-02:33 implemented: CLAIMS += joinedFar,
  implicitReject; JOINED_FAR_MAX / IMPLICIT_REJECT (cue_table.json first, else DESIGN9's values); `far_gap`
  (joinedFarGap / Window / Para / Key); `check_cert(extra_cues=)`; implicitBadKind; labels.json (5 reasons).
  Readings Q9-12..Q9-18 (REF_QUESTIONS9.md): Q9-13 (a window cannot hold a LF: joinedFarPara is vacuous on TSV data)
  and Q9-16 (soft kinds = limited, questioned, criticized, declinedToFollow) need a ruling.
- 02:33-02:38 generator: §5 / §7 cases in the make_r7 stage (far_* gaps 301 / 700 / 1200 / 1201, no claim, window
  none / bad / hash, keys other / target / ambiguous / after / straddling, noana / nocue / j_part / noauth; imp_* each
  soft kind, no claim, plain cue, no cue, bad kinds, part, noauth, joined, witness), each with DESIGN9's expectation,
  checked against the zone-free reference. Kept universes regenerated: 1,897 zone expectations / 49 counters / 183
  never-negative targets, 0 differ; 218 round-9 case expectations, 0 differ; `empty` (no zones, no round-9 claims vs
  round9/pre/ref): 9 universes, 0 differing files.
- 02:39-02:41 INBOX 02:33 / 02:37: D9-7 (§5 without the paragraph test: removed from far_gap), D9-9 (§8 judge-form
  strings under anchorWide: ANCHOR_WIDE9, JSON `anchor_wide9` else the three strings), D9-6 (NJ: data only; to verify
  on real data). Generator: `aw9_*` cases (district / magistrate / trial judge, upper case, no claim, 'judge of the
  court'); `empty` now also drops anchorWide claim lines and the joinedFar / implicitReject class lines. Kept
  universes regenerated: 1,939 zone expectations / 49 counters / 183 never-negative, 0 differ; 272 round-9 case
  expectations (§5, §7, §8), 0 differ; empty: 9 universes, 0 differing files.
- 02:41 started `check_regress9.sh regress9b` (534 stored universes, current reference).
- 02:41-02:42 `check_regress9.sh regress9b` (reference with §5 / §7 / §8): 534/534 bytes the same as the stored
  round-8 reference output; canonical diff against the stored round-8 Lean: the same 12 W universes only.
  REF_NOTES.md: round-9 section. Mirror reference synced (~/caselaw2/lean-proofs/tools/caselaw2/ref, ref/ only;
  precedent_ref.py f5ed26d3; cue table identical to Windows).
- 02:42 started real-data NJ check (D9-6): stage `ref9_nj` (stage9.py, = nj_test's args: v8e + round9/nj adoption /
  succession), `NOBUILD=1 wsl/r9_run.sh ref9_nj ref` (frozen round-8 binary; NJ is data only).
- 02:43 wider self-check (scratch/wide: 20 main seeds 97000-97019 + 10 probe 98000-98009): 8,795 zone expectations / 210 counters / 602 never-negative, 0 differ; 909 round-9 case expectations, 0 differ.
- 02:42-02:49 real data NJ (D9-6): `NOBUILD=1 wsl/r9_run.sh ref9_nj ref` (frozen round-8 binary 3b8d3e4d; current
  reference): diff.txt (`round9/out/ref9_nj/diff.txt`) 0 disagreements in every file (status 525,406 keys, findings
  318,868, certs 490,398, classes 37,373, summary 25): the 2 NJ witness rows and t8:4058244:4016514:17127 of round 8
  now agree. Reference unchanged for §6 (data only), as D9-6 says. Log `results/r9run_ref9_nj.log`.
- 03:03 INBOX 03:02 (v9a staged). lean9's lean9_z real run (v8e + calpart9 zones, §4 runner 65bbc36d): checked 220,452,
  failed 223 (the same 223 ids), missing 0; the reference's 220,455 checked: the 3 extra are the 3 NJ rows that the
  Lean (v8e tables, no NJ adoption) writes noAuthority and the reference ok (round-8's known class; with the NJ tables
  they agree, ref9_nj). Started `PAR=4 R9BIN=~/caselaw2/r9_bin/caselaw2_lean9 NOBUILD=1 r9_run.sh v9a ref` (mirror
  reference f5ed26d3).
- 03:10 the v9a run collided with the lead's own v9a run (same difftest/r9_v9a dir: the Lean certs were half
  overwritten, 245,513 vs 491,023 lines) -> its diff.txt (round9/out/v9a/diff.txt, written by my run at 03:10) is
  INVALID; the lead's own outputs in round9/out/v9a may have been overwritten by mine too (lean files copied 03:10).
  Rerun under my own name: round9/stage/ref9_v9a = hard-link copy of v9a; `r9_run.sh ref9_v9a ref` started 03:11.
- 03:11-03:18 real data v9a (as `ref9_v9a`, §4 runner 65bbc36d, PAR=4, mirror reference f5ed26d3): diff.txt
  (`round9/out/ref9_v9a/diff.txt`) 0 disagreements in every file: status 525,876 keys, findings 320,805, certs
  491,023, classes 37,396, summary 32 (incl. the zone counters: nodes 209,669, lines 585,526, checked 221,076, failed
  72, missing 0, bad nodes 0, bad rows 0). NOTE for the lead: round9/out/v9a/ was overwritten at 03:10 by my
  collided run (zone binary, half-clobbered Lean certs); rerun v9a if those files are needed.
- 03:26 lead msg: WSL restarted ~03:33 (C: full). Cleaned my WSL scratch (r9ref/a, r9ref/real, data_r9_ref9_*, difftest/r9_ref9_*), the big tsvs of round9/out/ref9_v9a (diff.txt, RUN.txt, summary.tsv kept) and stage ref9_v9a; scratch/wide, t1, t2. Lead ran v9a with the §4 binary: clean too; v9b real data by the lead. Waiting for LEAN_READY.
- 03:32 LEAN_READY (03:32, binary 22bab5cd, §4 + batch 2). Lead: v9b real data with it + my reference: 0 disagreements. difftest9.sh setup (snapshot ~/caselaw2/r9ref/lp, cue_table 69b4a0ca, ref f5ed26d3) rc=0; started kept r9kept1, sweeps r9sw1 (94000 x20), r9sw1p (95000 x10 probe), r9sw1f (96000 x10 fuzz K=8), regress r9reg1 (534).
- 03:34 kept r9kept1 (9 universes, runner 22bab5cd): status / splits / conflicts / lines / horty / summary 0;
  certs 1 + classes 1 = known round-5 W witness row (z90001 tr1, Lean noAuthority / ref witnessNoStanding); findings
  54 onlyB, all one class (classify9.py): rows the Lean writes noAuthority whose zones fail — the Lean drops their
  findings (atRisk:claim 48, panelDepartsWithoutEnBanc 5, ignoresBindingInUnit 1), the reference keeps them (D9-4 (2)
  literal: a non-ok row is not zone-checked). Asked the lead to rule (message).
- 03:35 sweeps on 22bab5cd (before D9-13): r9sw1 20 main, r9sw1p 10 probe, r9sw1f 10 fuzz: status 0 everywhere;
  findings all onlyB in the same class (noAuthority rows failing zones), plus the known round-5 W witness rows (certs /
  classes 1 each in y95009 tr6, x96001 tr8; their atRisk:inferred onlyA) and zone counter differences of 1 in three
  universes (z94016, y95009, x96001; to attribute). Self-check r9sw1: 7,009 expectations / 140 counters, 0 differ;
  720 round-9 case expectations, 0 differ.
- lead ruling D9-13 (Lean right): a row kept at targetLater / noAuthority whose quote fails its zone feeds no findings.
  Reference: zone_apply records such rows in zone_mute (cert verdict unchanged), and they are left out of adm_treat /
  adm_hist. Self-check of kept universes unchanged (1,939 / 49 / 183; 272 case expectations, 0 differ).
