# Round 7: joined certificates, a stronger reader, the queued reading, scope, dates, same-case history

Design and contract. Lead: one agent; started 13 Nov 2026 22:37. Log: `LOG.md`. State: `PROGRESS.md`.
Base: the round-6 frozen build `round6/history/stage/final2` (data) and `round6/history/out/final2` (Lean output),
which already contains round 5. Every decision is numbered D7-n (section 9).

## 0. Binding rules (every agent; read this section before anything else)

1. **Rules, never rows.** A fix is a general rule of a reader, linker or candidate generator that runs over the
   whole corpus (6.9 million decisions). No list of cases, no special-casing of a citation, party, docket, label.
2. **Answer keys are for scorers only.** No reader, linker, candidate generator, brief writer or auditor may read
   any answer-key field: `round5/gold_fresh/` (dev or sealed), `gold/`, `round6/shepardized/`, `round6/history/split/`,
   SCDB / CRS files under `eval/` or `data_src`, `round5/tests/split/holdout*`, `events_v3/reports.tsv`,
   `lean-in-v3/reports.tsv`, the Shadow Docket Database, `round7/heldout/` (the new time-split key), `benchmarks/`. The feed side of the notes
   (`round5/tests/split/feed_ids.tsv` joined to `gold/reports_typed.tsv` **through `round5/recog/` tooling only**) is
   the one sanctioned exception, as in round 5 (DESIGN5 §7): it is where recognised candidates come from.
3. **Dev only.** Diagnosis and per-case looks use dev halves only (`round5/gold_fresh/dev/`, Shepardized `--split
   dev`). Never open `round5/gold_fresh/sealed/` or `round6/history/split/sealed.tsv`, never run a scorer on a sealed
   split. The lead scores sealed exactly once after `round7/FREEZE.md`.
4. **Evidence = the acting court's own words** (overrulings: the overruling court, or a later court with power for
   `recognised`; history: the acting court or the target's own text).
5. **No external model.** All reading and auditing is by local Claude sub-agents. No Azure OpenAI, no API calls.
6. **Do not touch:** `data/`, `out/`, the round-4/5/6 output folders and tables (write new files under `round7/`),
   blog/website folders, other sessions' Lean files (`LegalProofs/USTax/**`, `tools/hunt/`, `tools/taxcode/`).
   Nothing is committed or pushed. Stop only processes you started.
7. **One writer on the Lean tree** (`global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`, `tools/caselaw2/cues/`,
   `CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`): the agent `lean`. Others ask the lead.
   The Python reference (`tools/caselaw2/ref/`) has one writer: the agent `ref`, who never reads the Lean sources.
8. Lean runs only in WSL Ubuntu: `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc '…'`. Do not change Windows
   security settings. Python files are written with the Write tool, LF endings. Big scans use all cores
   (`--procs 22`); the round-6 cache `round6/history/cache` (see `round6/history/r6scan.py`, `r6lib.py`) holds
   zones, citation windows and disposition sentences for every decision and should be reused before rescanning.
9. Every agent works in its own folder `round7/agents/<name>/` (or the folder named in its brief), keeps a
   `NOTES.md` there (what was done, counts, files, open points; truthful clock times from `date`), and makes its work
   resumable. Copies of anything changed outside `round7/` go to `round7/pre/` first (`pre_round7`).

## 1. Round-7 mode and byte reproducibility (D7-1)

New optional tables (all no header, tab-separated, LF):

| table | columns | turns on |
|---|---|---|
| `joined.tsv` | `id`, `table` (`treatments`\|`history`), `rel`, `j_start`, `j_end`, `j_quote`, `j_part`, `label`, `src` (9) | joined certificates (§2) |
| `history_claim.tsv` | `id`, `claim` (`orderHead`\|`setAside`), `src` (3) | relaxed checks for claimed history rows (§3) |

and one new claim value `doctrine` in the existing `treatment_class.tsv` (§2.4).

**When `joined.tsv` and `history_claim.tsv` are absent (or empty) and no class line has claim `doctrine`, the
runner's and the reference's output is byte-identical to the round-6 frozen output `round6/history/out/final2`**, and
the round-4 and round-5 regressions of `LEAN6.md` §3 stay byte-identical. A malformed line (wrong field count,
non-numeric offset, unknown `table`/`rel`/`claim`) is not a line and is counted (`bad_rows <table> n` in
`summary.tsv`); a line whose id is no row of the named table is counted (`joined_unknown_ids`,
`hclaim_unknown_ids`). Summary counters are written only when the table has at least one line.

## 2. The joined certificate (A1)

### 2.1 Form

A row (treatments or history) may carry **one or two** joined lines. Each joined line is a further quote from
**the same text as the row's own certificate** (same `text_sha`; read through the windows supplied for that text in
`cert_text.tsv`, hash-checked against `window_sha.tsv` exactly as the main quote is) plus a relation `rel` between
that quote and the row's main quote. The first two valid lines for an id are kept; further lines are ignored and
counted (`joined_extra`). A row with joined lines is checked by `checkJoined`; a row without is checked exactly as
before (plain / operative / recognised / anchored, unchanged).

`checkJoined` = (first failure is the reason):
1. `joinedMismatch` — every joined quote is non-empty, `j_start < j_end`, and is the text of a usable window of the
   row's own text at that offset (well formed, hash-consistent; as `quoteOk`);
2. `joinedPart` — every joined quote's part is `majority`, `plurality` or `perCuriam` (never `headmatter`, never a
   separate opinion);
3. `joinedDisqualified` — no joined quote (normalised, lower-cased) contains a phrase of the kind's disqualifier
   list (as for the main quote) or of the new list `disqualify_joined`;
4. `joinedRelation` — the relation of every joined line holds (2.2, 2.3);
5. `joinedUnresolved` — the row's target evidence resolves **inside one joined quote alone** (not in a window, not
   in the main quote; same rules as `anchorResolves`: compact citation in the compact quote and, with the index, the
   index maps it to the target; `name:` every token of ≥ 3 characters as a whole word);
6. the row's own check on its main quote with the target evidence taken as given (`selfText := true`), in the mode
   that applies to the row (plain for an explicit row; operative for an `operativeWords` claim; doctrine for a
   `doctrine` claim, 2.4): hash, window, quote, cue, disqualifiers, part, date order, authority. A row whose joined
   check fails is rejected; there is no fall-back to the one-quote check.

Treatments rows only in this round (`table = treatments`); a `history` joined line is parsed, counted and ignored
(`joined_history_ignored`) — reserved.

### 2.2 Relation `antecedent` (class (i): an overruling stated across two adjacent sentences)

- the joined quote ends before the main quote starts: `j_end ≤ start`, and the gap `start − j_end ≤ 300`
  characters (`joinedGap` constant, in the cue table JSON as `joined_gap_max`, default 300);
- the main quote (normalised, lower-cased) contains a phrase of the new list `anaphor` ("those cases", "these
  cases", "that case", "those decisions", "these decisions", "that decision", "such cases", "those opinions",
  "those holdings", "both cases", "each of them", "they are overruled", "it is overruled", …; the list is data);
- the main quote has a cue of the row's kind (the plain cue list) — the act is in the main quote.
Effect: that of an explicit row of the kind and scope written (no change to `Spec/Status.lean`).

### 2.3 Relation `doctrineTie` (class (ii): doctrine targets)

- `label` is the doctrine phrase D (≥ 2 words, ≥ 8 characters after normalising; lower-cased, normalised);
- D occurs (lower-cased, normalised) in the main quote **and** in the joined quote;
- the joined quote contains a phrase of the new list `doctrine_tie` ("doctrine of", "doctrine announced",
  "doctrine established", "rule of", "rule announced", "rule laid down", "announced in", "established in",
  "adopted in", "laid down in", "the rule in", "first announced", "originated in", …);
- no distance bound (both quotes are in an opinion-of-the-court part of the same opinion: check 2).
Only on a row with a `doctrine` claim (2.4); a `doctrineTie` line on any other row fails `joinedRelation`.

### 2.4 The doctrine row and its effect

A treatments row with `explicit = 1`, kind `disapproved`, and a class line with claim `doctrine` (the class line's
`doctrine` column = D, its `field_limit` column = the limiting field phrase as display text or `-`). Check:
- `doctrineBadRow` (first): kind not `disapproved`, `explicit = 0`, or the row has no `doctrineTie` joined line;
- the joined check of 2.1 with relation `doctrineTie`; the main quote's mode is **doctrine**: cue list
  `doctrine_reject` ("has no place", "is rejected", "we reject", "repudiate", "abandon", "is overruled", "no longer",
  "discard", "disapprove", …) and disqualifiers `disqualify_treat` + `disqualify_operative`;
- **uniqueness** (`doctrineAmbiguous`): after every doctrine row has been checked, if two rows that pass have the
  same compact label and different targets, every row with that label fails. (The linker guarantees corpus-wide
  uniqueness of the tie; the checker guarantees it inside the table.)

Effect: always **demoted** (`demote`, DESIGN5 §3.3): the target becomes at most `unknown:partialScope` on the
issues reached, never negative, whatever the written scope. The class of the row is a new `OClass.doctrine`
(output string `doctrine`); `classes.tsv` shows the doctrine and field limit columns. The tie order for `oclass`
puts `doctrine` after `recognised` and before `atRiskWitness`.

### 2.5 Theorems (stated in `round7/LEAN7.md` §1 before proving; existing statements unchanged)

At least: `checkJoined_sound` (admitted ⇒ every joined quote at its offset in a usable window of the row's own
text, allowed part, no disqualifier, its relation holds, the evidence in one joined quote, and the main check with
`selfText := true` admits); `checkJoined_admitted_iff`; `checkJoined_bounded` (1 ≤ joined lines ≤ 2);
`checkJoined_cite_index`; `checkJoined_window_hash`; `antecedent_gap` (admitted antecedent ⇒ `j_end ≤ start ∧
start − j_end ≤ 300` and an anaphor cue in the main quote); `doctrineTie_label` (label in both quotes, tie cue in
the joined quote); `doctrine_never_neg` (the effects of a doctrine row never make a status negative: for any list
`l`, if `status (doctrineEffects ++ l) = neg n` then `status l = neg n`; and alone they give at most
`unknown partialScope`); `doctrine_unique` (two admitted doctrine rows with the same compact label have the same
target); `no_joined_no_change` (the step without joined lines or claims is the round-6 step).

## 3. History claims (A1 (iii), B4 (c), B4 (d))

`history_claim.tsv` claims change one check of a history row's plain or anchored certificate, under stated
conditions that the checker verifies; without a claim nothing changes.

### 3.1 `orderHead`: Supreme Court orders whose disposition is only in head matter

The part rule (`partNotMajority`) admits `part = headmatter` **only if all hold** (else the row fails
`orderHeadNotAllowed`):
- the acting decision's court is the Supreme Court of the United States (the court id the court table gives it);
- its date ≥ 2013-01-01 (`order_head_from` in the cue table JSON: 20130101; the corpus prints post-2012 order-list
  entries as head matter only);
- the row's kind is one of `certDenied`, `vacated`, `reversed`, `affirmed`, `reviewDismissed`;
- the quote (normalised, lower-cased) contains a phrase of the new list `order_line` for that kind (the order-list /
  judgment-line forms: "certiorari denied", "petition for writ of certiorari denied", "certiorari granted, judgment
  vacated", "judgment vacated, and case remanded", "judgment reversed", "judgment affirmed", "appeal dismissed",
  "certiorari dismissed", "writ of certiorari dismissed", …; the JSON key is `order_line` → kind → list);
- the quote is at most 400 characters long.
Every other check is unchanged. The linker (not Lean) states the decision has no opinion-of-the-court part at all;
the blind audit covers it.

### 3.2 `setAside`: "set aside" as a vacatur cue

For a row of kind `vacated` with a `setAside` claim, the cue test uses the plain `vacated` list **plus** the new
list `set_aside` ("set aside", "sets aside", "is set aside", "are set aside", "be set aside"); every other check is
unchanged (in particular the disqualifiers, which already refuse a dissent's or a lower court's words). Without the
claim the cue list is unchanged (round-4/5/6 output byte-identical).

### 3.3 Theorems
`orderHead_sound` (an admitted row with part `headmatter` has the claim, court = Supreme Court, date ≥ cutoff, a
listed kind, an `order_line` cue of its kind, length ≤ 400); `orderHead_no_claim` (without the claim, `headmatter`
fails as before); `setAside_only_vacated`; `setAside_no_claim`.

### 3.4 Mutants (one per new rule, each killed by a stated property)
Drop the gap bound; drop the anaphor test; resolve the evidence in the window (or the main quote) instead of the
joined quote; drop the tie cue; drop the label-in-both test; doctrine row not demoted; drop doctrine uniqueness;
accept a third joined line; joined quote from another text; orderHead without the court test; orderHead without
the date test; orderHead without the order-line cue; setAside on a kind other than vacated.

## 4. Linker / reader rows for round 7 (input of `round7/certify7.py`)

One JSON object per line:

```
{"rule": "<class>:<variant>", "table": "treatments" | "history",
 "by": <acting/stating node W>, "target": <node X>, "kind": "<TKind or HKind>", "scope": "<SCHEMA scope>",
 "main": [s, e], "part": "<part of the main quote>",
 "ev": "cite:<key>" | "name:<tokens>",
 "joined": [ {"rel": "antecedent" | "doctrineTie", "span": [s, e], "part": "<part>", "label": "<D or ->"} ],
 "claim": "-" | "doctrine" | "operativeWords" | "orderHead" | "setAside",
 "doctrine": "<D or ->", "field_limit": "<text or ->",
 "anchor": [a0, a1] | null, "anchor_part": "<part>",     (history rows, as round 6)
 "note": "<free text>"}
```

Offsets are characters of the git-HEAD text (UTF-8, CRLF → LF), as in rounds 5–6. `certify7.py` cuts the quotes
(tab/newline → space), runs the same checks in the same order with the same string functions as Lean, writes the
deltas (`treatments_delta.tsv`, `treatment_class_delta.tsv`, `history_delta.tsv`, `history_anchor_delta.tsv`,
`history_claim_delta.tsv`, `joined_delta.tsv`, `cert_text_delta.tsv`, `window_sha_delta.tsv`,
`cite_index_delta.tsv`), `rejects.tsv`, `stats.json`. Treatment row ids: `t7:<by>:<target>:<start>`; history ids as
round 6 (`h6:` rows keep their ids; new ones `h7:<by>:<target>:<kind>`).

Recognised rows (B1) keep the round-5 pipeline: answers → `round5/recog/certify_recog.py` (run with a round-7 output
folder) → deltas. Operative rows (A2) keep `round5/opwords/certify_opwords.py` (round-7 output folder).

## 5. Building and scoring a variant

- `python -X utf8 round7/stage7.py <name> --delta DIR … [--remove FILE] [--drop FILE] [--replace FILE]` →
  `round7/stage/<name>/` : base `round6/history/stage/final2`; every table a delta touches is rewritten in full;
  the rest hard-linked. `MANIFEST.txt` with counts and sha1.
- `wsl/r7_run.sh <name> [ref]` → Lean runner (and the reference, and `diff.py`) → `round7/out/<name>/`.
- `bash round7/score7.sh <name>` → `round7/results/<name>/`: fresh dev (both date views, §6), no-leak, holdout notes,
  behaviour, SCDB/CRS (burned, non-blind), Shepardized dev (`round6/shepardized/compare.py --split dev`).
- After each scored variant: `python round5/report/make_overturned.py` (the lead).

## 6. Scope and dates (B2, B3)

- **Scope rule (B2).** From the overruling sentence itself, never from a key: a whole-case act on the named case
  with no limiting phrase → scope `all`; a limiting phrase ("to the extent", "insofar", "in so far", "in part",
  "on this point", "on other grounds", "so far as", "as to", "in the field of", "to that extent", …) → partial.
  Applied as a general rewrite (`--replace`) of rows whose reader scope was unknown, and audited blind before it is
  installed.
- **Date views (B3).** The model's timeline is unchanged (R5-3: a recognised overruling is negative from date(W)).
  The scorer adds a reporting view "as attributed today": a negative status of path `recognised`, actor Y, counts
  as if it started at date(Y). Strict and lenient are reported under both views, side by side; neither replaces
  the other. No status semantics change.

## 7. Audits

Blind, by Claude sub-agents who get the acting text and the target's identity, not the rule, the class, the
expected answer or why an item was picked. Per new class ≥ 80 items, stratified (federal/state, decade), with
decoys (≥ 10% of each pack: items known wrong or known right from another class, to measure the auditor). Wilson
95%. A status-changing class below about 90% (point estimate) is not installed; the interval is reported.

## 8. Held-out tests

- Fresh lists sealed half: scored twice before this round (`round5/gold_fresh/sealed/TEST_RUNS.log`, read by the
  lead only for its line count); the round-7 run is its third use. The report says so.
- Shepardized sealed half: second use.
- New: a clean held-out key scored once after the freeze (time split or the Shadow Docket Database, §D7 list). Its
  scorer is written by an agent that never shares its contents with linkers.

## 9. Decisions (running list; the lead adds to it)

- D7-1 Round-7 mode by presence of `joined.tsv`, `history_claim.tsv` or a `doctrine` class line; absent ⇒ round-6
  output byte for byte.
- D7-2 Joined certificates for treatments rows only this round; at most two joined lines per row.
- D7-3 "set aside" is claim-gated (`setAside`) so that the earlier rounds' output does not move.
- D7-4 Doctrine quotes both come from the acting court's own opinion (the court that rejects the doctrine has power
  over the case it ties the doctrine to, checked as authority on the row); a tie stated only in another opinion
  is not used this round.
- D7-5 Phase order: Phase A agents are launched first and get reading priority; Phase B preparation that touches
  no Phase A file (inventory of queued packs, scorers, the new held-out key) starts while Phase A runs.
- D7-6 (23:04) The Lean agent's readings L7-1 … L7-12 (`LEAN7.md` §0) are accepted as the contract: joined lines on
  a witness row ignored and counted; a doctrine claim on a witness row fails `doctrineBadRow`; D = the joined
  line's label (class `doctrine` column is display); uniqueness decided once on the text check (power taken as
  verified) and applied under both rule sets; joined-quote disqualifiers = the kind's plain list + `disqualify_joined`;
  0 or > 2 joined lines → `joinedMismatch`; history claims are a set per id (repeats counted); orderHead court =
  the acting decision's epoch is the Supreme Court (court 2906), date from decisions2.tsv (0 fails), length ≤ 400
  characters (`order_head_max_len`); class `doctrine` whatever the verdict; setAside on another kind has no effect;
  unknown-id test first for joined lines of both tables. Sent to the `ref` agent.
- D7-7 (23:04) B1 reading order: P1 shards first (pairs with no admitted row), then P2 if time allows. The round-3
  own-act queue (20,443 items) is out of B1's class; a port is a separate decision (see LOG 23:02).
- D7-8 (23:17) `anaphor` cue list extended to the antecedent agent's proposal (`agents/antecedent/anaphor_proposal.json`:
  pronoun / back-reference phrases incl. "overrule it", "to the extent that it", "insofar as they", "said case";
  3,710 of 4,798 queued act sentences vs 2,066 with the DESIGN7 examples). Rule-based data; the class is blind-audited.
- D7-10 (23:21) An `antecedent` line needs a plain cue of the row's kind in the main quote, also on an operativeWords
  row (DESIGN7 2.2 as written; reference Q7-15 reads the same). No operative rows carry joined lines this round.
- D7-11 (23:22) B1 reading: the T1F tier (Supreme Court loose items the smaller model pre-screened as "no") gave
  0 positives in its first 200 items read by the main model; the remaining T1F shards (S007-S015, ~1,800 items) are
  held behind the antecedent reading (≈ 50% yield) and are read only if slots remain. P2/P3 (pairs that already
  have an admitted row) stay last.
- D7-12 (23:41) Doctrine cue lists widened (append-only): `doctrine_reject` += depart(ing) from, unsound, overrule,
  abolish, expressly/therefore/accordingly/hereby reject, be rejected, no proper place, recede from, decline to
  follow, renounce, jettison, cannot survive, not the law; `doctrine_tie` += test of, adopted by, established by,
  first adopted, principle of, presumption of (not "standard of"). Corpus counts: agents/doctrine/work/cue_counts.json.
  The doctrine ambiguity rule stays strict (a label tied to two decisions anywhere = no row), as stated in §2.4.
