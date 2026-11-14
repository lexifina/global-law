# ref9 notes, continued (NOTES.md and every file in this folder older than 03:36 are frozen by round9/FREEZE.md)

- 03:32 LEAN_READY (runner 22bab5cd, §4 + batch 2). difftest9.sh setup rc=0 (snapshot ~/caselaw2/r9ref/lp).
- 03:33-03:37 first differential (reference f5ed26d3, before D9-13), results/ r9kept1, r9sw1 (94000 x20), r9sw1p
  (95000 x10 probe), r9sw1f (96000 x10 fuzz K=8), r9reg1 (534 earlier universes): one new class only - rows the Lean
  writes noAuthority whose zones fail lose their findings in the Lean (atRisk:claim, panelDepartsWithoutEnBanc,
  ignoresBindingInUnit), kept them in the reference. Lead ruling D9-13: the Lean is right.
- 03:36-03:42 reference changes (tools/caselaw2/ref/precedent_ref.py, final sha1 7432cbed): `zone_apply(..., key)`
  records a row kept at targetLater / noAuthority whose quote fails its zone in `zone_mute`; such rows stay out of
  adm_treat / adm_hist (no findings), verdict unchanged. (A counter experiment for recognised-claim witness rows was
  tried and reverted: the remaining counter differences all belong to the W class below.)
- 03:37-03:43 differential with difftest9b.sh (= difftest9.sh writing results2/, fail2/), final runs r9kept4,
  r9sw4, r9sw4p, r9sw4f (reference 7432cbed, runner 22bab5cd):
  | tag | universes | disagreeing | what |
  |---|---|---|---|
  | r9kept4 (9 kept) | 9 | 1 | z90001 tr1: W class (Lean noAuthority / ref witnessNoStanding), certs + classes |
  | r9sw4 main 94000-94019 | 20 | 1 | z94016 tr1: W class (Lean partZone / ref witnessNoStanding, reason only) -> zone_checked / zone_failed +1 |
  | r9sw4p probe 95000-95009 | 10 | 1 | y95009 tr6: W class -> certs, classes, atRisk:inferred, zone_checked +1 |
  | r9sw4f fuzz K=8 96000-96009 | 10 | 1 | x96001 tr8: W class -> certs, classes, atRisk:inferred, zone_missing +1 |
  | r9reg1 (534 earlier, no round-9 table) | 534 | 12 | the 12 known W universes, as in round 8 |
  W class = round-5 witness rows whose target has date 0 (or the standing test): the Lean's witness check passes
  (ok / noAuthority / then partZone), the reference says witnessNoStanding; the zone counters follow the Lean's
  verdict of these rows. Every round-9 rule (zones incl. text owner, bad lines, overlap, straddle, other part,
  joined quotes, D9-13; joinedFar gap / window / key incl. straddling keys; implicitReject soft kinds and
  implicitBadKind; §8 judge strings; NJ) agrees in every universe. Self-check r9sw4: 7,009 expectations / 720 case
  expectations 0 differ (counters: make_r9.py's RTEXT counting, frozen at 03:36, overcounts 15 in sweeps - a
  generator artefact, the differential is the authority); probe y95002 pr_far_key_straddle: the generator's extra
  window can end inside the straddling citation, both engines then admit (consistent with Q9-14).
- 03:43 check_regress9.sh regress9c (reference 7432cbed): 534/534 bytes the same as the stored round-8 reference
  output; canonical diff vs the stored round-8 Lean: the 12 W universes only. Mirror reference synced (7432cbed).
- 03:44 WSL scratch removed (~/caselaw2/r9ref, 489 MB). Windows: fail/ (39 MB, frozen), fail2/ (29 MB), results2/.
