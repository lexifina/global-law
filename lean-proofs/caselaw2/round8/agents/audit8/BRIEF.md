# Agent `audit8` (round 8): blind-audit tooling

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Your output folder is `round8/audit/` (NOTES.md there).

Port `round7/audit/` (`audit7lib.py`, `make_packs7.py`, `decoys7.py`, `more_text7.py`, `score_audit7.py`,
`selftest7.py`, `AUDITOR_BRIEF7.md`, decoy pools, NOTES.md) to round 8:
1. `round8/audit/make_packs8.py` etc.: same behaviour, reading certified rows from round-8 delta folders (ids `t8:` /
   `h8:` from `round8/certify8.py`; also round-7 style folders), base `round7/stage/v3`; random sample by fixed seed
   from the whole class (`--match` filters by row fields only), stratification (federal/state, decade), `--exclude`
   earlier samples, decoys ≥ 10% from the decoy pools (known right / known wrong items from audited earlier classes;
   extend the pools with round-7 audited items if useful), the answer key of the audit kept apart from the pack.
   Both forms: treatments rows (did the acting court itself overrule / disapprove / … the target, scope) and history
   rows (did the acting court itself reverse / vacate / … the target decision; link right? effect?). Add a two-quote
   pair form for the agent `contradict` if simple (both quotes shown unlabelled in text order; question: what did the
   court do to the target as its own act).
2. `score_audit8.py`: k/n, Wilson 95%, decoy accuracy, per stratum, and the measures used in round 7 (link + effect,
   link + kind, extent).
3. Selftest (synthetic class) and one dry run on a round-7 class (e.g. 20 items of r7a17) with ONE opus auditor to
   confirm the round trip; record it.
4. `round8/audit/HOWTO.md`: the exact commands for a track agent: build pack(s) (80 items + decoys, split into packs
   of ~20–40 for parallel auditors), spawn blind auditors (`model: "opus"`, prompt = only "read
   AUDITOR_BRIEF8.md and pack file X, write answers to Y"), score. Rules: the sample is drawn by the script, never by
   hand; one fresh sample per decision; a re-audit after a cut uses `--exclude` of every earlier sample; the auditor
   brief says nothing about rules, classes or expected answers. Then write `round8/audit/READY`.

Final report: tools, selftest/dry-run result, HOWTO path.
