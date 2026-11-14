# notarget NOTES

- 01:21 start; read DESIGN8, COMMON, BRIEF. Timebox 50 min (to ~02:11).
- 01:22 Source = state8 work/rescue/*.jsonl, reason no-target. nt_cands.py (state8 rescue_cands.build +
  round-7 antecands resolution reused unchanged; drop when any near/in-act target pair has a v3 admitted row or a row
  in ownact/multicase/state8 cert/) running -> work/ntcands.jsonl, work/profile.json. Reader brief
  READER_BRIEF_NOTARGET.md = state8 READER_BRIEF_RESCUE.md (same item layout, same act rules). Audit run name r8n01.
- 01:25 nt_cands done (work_ntcands.log, work/ntcands_stats.json, work/profile.json): no-target 43,312
  (state8's 41,889 + queue/ante/multi); not status-kind shape 20,827 (18,922 carry no status verb at all: "law"/limit
  tags, procedural "assignments ... overruled" etc.); queue 1,255, r7ante 42, multi 126 -> 21,062 sentences in
  18,847 decisions -> 21,055 records. Resolution (best target): none 16,898; far cite 3,060; far name 854; near cite
  82; near name 79; in-act name 82. Candidates (>=1 near/in-act target, no pair already in v3 or round-8 certs): 224
  (19 dropped for an existing pair). 224 by repo: tex-app 38, okla 17, tex 14, ca7 11, haw 10, ca5 9 ...; decades
  spread 1870-2020. Packs packs/pack_001-006 (antepack.py reused, 38/pack); 6 opus readers launched -> ans/.
- 01:25 Own yield read (seed 11, 40 random of the 21,062 status-kind no-target sentences, read by me):
  ~4/40 are a court's own act on an earlier decision ("We therefore recede from Gerrits ...", "... to this extent is
  accordingly overruled" on "this decision" earlier, "Anything to the contrary in Thomas or Cooperstein is
  specifically disapproved", one on agency decisions); the other ~36 are procedural (assignments / issues / objections /
  motions / exceptions overruled), statute text, reports, a dissent ("I recede"). So the pool is ~90% procedural; the
  real acts mostly fall in resolution none/far (target citation unresolved, no power edge, or named > 300 chars
  before). Subclass chosen: the 224 candidates with a near (<= 300 chars, DESIGN7 2.2 joined) or in-act target
  (plain), i.e. what the round-7 certificate can check; far (3,914) needs a longer joined gap (not in the Lean).
- 01:26 Readers done (6 opus, 223 answers, 62 act true; pack 6 = Texas App procedural, 1/34). answers_to_rows
  (round-7 tool) -> work/rows_raw.jsonl: 54 one-sentence + 2 joined + 4 window; rejects joinedGap 4, duplicate 4,
  noAnaphor 1. split_rows.py -> rows.jsonl 56 (class NT8, rule notarget:NT8:<form>:<tag>:<1|m>), rows_window 4 (not
  installed form). certify8 -> cert/: 56 in, 51 admitted (overruled 46, disapproved 5; 2 joined), 5 already v3 rows.
  Staged notarget_v1 = v3 + cert/.
- 01:30 Lean (NOBUILD, frozen v3 checker) notarget_v1: my 51 rows ok 39, noAuthority 12 (panels).
  score8.sh notarget_v1 started (score_v1.log). Blind audit r8n01: make_packs8.py --class NT8 --cert
  round8/agents/notarget/cert --lean-certs round8/out/notarget_v1/certs.tsv --n 80 --pack-size 30 --out
  round8/audit/r8n01/ -> whole class 39 Lean-admitted rows + 4 known-wrong + 2 known-right decoys = 45 items, 2 packs
  [23, 22]; 2 blind opus auditors per pack launched (HOWTO prompt verbatim).
- 01:32 Audit r8n01 scored (score_audit8.py; 2 blind opus auditors per pack, strict): NT8 (39 Lean-admitted
  rows, read in full) right 38/39 = 0.974 [0.868, 0.996]; right + extent 38/39 same; link 39/39. Decoys 12/12 (every
  reader 3/3). One failure, both readers: t8:5475824:5472862:6902 (state, 1910s) "If it was intended in said decisions
  to lay down a rule ... then we disapprove and refuse to follow such rule" read as a conditional limit, not a
  disapproval. Note: auditor ans_2 reported its first search of the shared scratchpad folder previewed file names /
  matches from other sessions; it says it used none of it (its 19/19 equals reader ans_2_b's).
  => NT8 passes the bar on the point estimate (interval reaches below 0.90 because the class is small). Ready to stage.
- score8 notarget_v1 vs v3 (score_v1.log): fresh dev strict 51/165, lenient 111/165 (unchanged); holdout notes
  precedent Y-named strict 771 -> 772/12,354, alsoInFeed negOrPartly 1,038 -> 1,039/2,640, holdoutOnly negOrPartly
  574 -> 578/6,734; Shepardized dev 140/254 unchanged; the four h0 per-case files identical to v3 (no h0 effect);
  no-leak exit 0. No (by, target) pair overlap with any other round-8 agent's cert*/treatments_delta.tsv.

## State / deliverables
- Delta folder: round8/agents/notarget/cert/ (class NT8, 51 certify8-admitted treatments rows: overruled 46,
  disapproved 5, joined 2; Lean admits 39, 12 noAuthority). Variant notarget_v1 = v3 + cert/.
- Left: rows_window.jsonl (4 window-only rows, form not installed). Resolution none (16,898) / far (3,914) of the
  no-target pool: ~90% procedural; real acts there need either a longer joined gap (far: Lean change) or citation
  forms the index does not key (e.g. "33 Texas Crim. Rep., 128"; state8's alias work) or are quotations of another
  court's act. Not built.
