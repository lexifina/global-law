# Agent `ownact` (round 8, move 1): port and read the round-3 own-act queue

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/ownact/` (NOTES.md).

## Source
The largest unread source of courts' own overrulings: the round-3 own-act queue `work/round3/queue/` (packs
142–397 unanswered: 246 packs, ~20,443 items; packs 0–141 were answered in round 3). Its reader brief is
`work/round3/queue/SUBAGENT.md`; tools `check.py`, `snap.py`, `measure.py`, `install.py` (**install.py writes
`data/`: never run it**). Context: `round4/queue.md`, `round7/agents/queue/NOTES.md` + `INVENTORY.md` (where the 246
come from), and the round-7 reader briefs that encode the latest lessons:
`round7/agents/opwords/READER_BRIEF_OPWORDS7.md` (operative words; own-act markers; the bare state form "X is no
longer the law" fails; "whole" scope was right only 10/30), `round7/agents/antecedent/READER_BRIEF_ANTECEDENT.md`
(act in the next sentence: joined `antecedent` lines), and the round-7 audit results in `round7/ROUND7.md`
(weak verbs such as "no longer good law" 36/80 — not admitted; window-only naming 0.857 — not admitted).

## Do
1. Port (timebox ~30 min): read the unread items; re-anchor every quote to the git-HEAD text (UTF-8, CRLF → LF, as
   rounds 5–7; `round6/history/r6lib.py` has the text reader); drop items whose (acting, target) pair already has an
   admitted negative treatments row in v3 (`round7/stage/v3/treatments.tsv` + `round7/out/v3/certs.tsv` verdict ok)
   — keep them in a separate low-priority list; order the rest by expected yield, using the answered round-3 packs
   0–141 (their answers + what was certified) as the yield model (features: court level, era, cue strength, item
   type). Write new packs `packs8/pack_<nnn>.md` (≈ 80–100 items each) + `items8.jsonl.gz` + `index.tsv`.
2. Reader brief `READER_BRIEF_OWNACT8.md`: round-3 SUBAGENT.md upgraded with the round-7 lessons; one answer per
   item; the answer must give the round-7 row fields (DESIGN7 §4: kind, scope, main span = the act sentence by
   offsets or exact quote, evidence `cite:` / `name:`, part, and a joined `antecedent` line when the case is named in
   the previous sentence and the act sentence has only an anaphor). A sentence that overrules several cases gives one
   answer per case named (agent `multicase` owns the general multi-case rule; your readers simply answer each named
   case). Pilot the brief on 2 packs with 2 opus readers, check answers against certify8 (≥ 90% of "yes" answers must
   certify), fix the brief once, then fan out.
3. Read: spawn reader sub-agents (`model: "opus"`), each ~3–5 packs, its own answer file `ans/ans_<nnn>.jsonl`; up to
   ~20 at once, refill as they finish, highest-yield packs first. Track progress in NOTES (packs done / items / yes).
4. Certify with `round8/certify8.py` (after `round8/INFRA_READY`) into `cert/` (delta folder), in batches so the
   audit can start on the first ~half while reading continues. Record per-stratum counts (court federal/state,
   decade, verb strength, scope) for the audit.
5. Audit (after `round8/audit/READY`, per `round8/audit/HOWTO.md`): one blind audit of ≥ 80 rows drawn at random
   from the whole certified class (stratified), with decoys. If a sub-rule clearly fails (as weak verbs did in
   round 7), cut it by a stated rule and re-audit the rest on a FRESH sample. Installed only at about ≥ 90%.
6. Measure: stage `ownact_v1` on v3, run with NOBUILD=1, score with score8.sh (dev + h0 keys). Leak check is in
   score8.sh (`check_no_leak.py`) — it must exit 0.

Final report: items read / yes / certified / Lean-admitted, audit (k/n, Wilson, decoys right), the delta folder,
the dev and h0 effect, what was not read and why.
