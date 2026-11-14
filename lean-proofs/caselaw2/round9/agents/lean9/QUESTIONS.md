# lean9: questions for the lead (continuing on the stated readings; LEAN9.md §0)

- Q1 (L9-1, 02:15) Whose zones apply to a witness row of `treatment_witness.tsv`? Reading: the witness W's (its text is
  the one the certificate quotes; W is the acting court of the statement). calpart9 then needs zones for W nodes too,
  otherwise those rows stay unchecked (`zone_missing_rows`). A history row whose quote is from the target's own text
  (selfText) has no zone (its offsets are not in the acting node's text); v8e has 0 such rows.
- Q2 (L9-6, 02:15) The zone test also gates the row's text check (events), the doctrine-uniqueness table and the
  `laterCourtSays:` supersession evidence (a refused certificate asserts nothing). A round-8 failure, including
  `doctrineAmbiguous`, keeps its reason.
- 02:19 Q1, Q2 answered (INBOX 02:18; D9-4). Readings L9-1, L9-5, L9-6, L9-9 updated to D9-4.
- Q3 (02:19) D9-4 (2) "partZone runs only on a row whose complete round-8 verdict is `ok`": the Lean reads `ok` as
  every admitted verdict (`ok`, `okUnverifiedBy`, `okRecognised`, `okRecognisedUnverifiedBy`), since D9-4 (3) zone-checks
  recognised rows. A literal `ok` would leave power-unknown rows unchecked.
- Q4 (02:19) INBOX 02:18 says a zone-refused row has "no doctrine-uniqueness entry"; D9-4 (2) says "a zone failure never
  removes an ambiguity" (the uniqueness table on round-8 text checks). The Lean follows D9-4 (binding text): the table
  is decided without zones; a zone-refused doctrine row still makes a label ambiguous. 17 doctrine rows in v8e.
- Q5 (02:56) Timeline: §4's gates (r9_final.sh) are in the regressions (a, a2 byte-identical; b, c, then the v8e
  reproduction left): §4 LEAN_READY ~03:08. Batch 2 (§5+§6+§8+§7) is built and proved in a staging copy (all
  theorems, guards, mutant diagonal compiling; runner build running); its own gates after §4's take ~30 min run
  sequentially (build 5, audit+lock 4, fixtures 2, regressions a/a2/b/c 20, v8e 5) -> ~03:40. To reach ~03:25 I would
  run the four regressions as two parallel pairs (a+a2, b+c, 8 procs each) alongside the v8e reproduction: 3 Lean runs
  of mine at once, against COMMON's "one Lean run per agent". Doing it sequentially unless you say otherwise in INBOX.
  -> answered 02:56 (INBOX): parallel allowed, <= 3 runs, PAR=4, < 30 GB; wsl/r9_final2.sh does that.
- Q6 (03:21) URGENT: C: is full and the WSL filesystem is read-only (vhdx on a full host disk). Needs the lead / user:
  free space on C: and restart WSL (`wsl --shutdown`; I will not do it: it kills every agent's runs). After that I rerun
  regressions a2 and c (`r7_lean_base.sh a2 c`, ~6 min) and write batch-2 LEAN_READY. Should I write LEAN_READY now
  on the passed gates (a, b, v8e byte-identical) and mark a2/c pending?
  -> 03:25: space freed and WSL restarted by someone else; rerunning a2 and c myself.
