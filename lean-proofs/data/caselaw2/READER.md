# Treatment and same-case history reader (caselaw-lean-2)

Outputs: `treatments.tsv`, `history.tsv` and `cert_text.tsv`, as specified in `../SCHEMA.md`. Also written: `reader_stats.json`, `reader_rejects.tsv`, `treatments_items.tsv` (row → candidate id → how the quote was chosen), and `reader_usage.json` (tokens and cost per stage). The code is in `global-law-lean/lean-proofs/tools/caselaw2/reader/`, and the working files are in `reader_work/`, which holds no full texts.

## Held-out rule

- **Inputs used:** decision texts read from git (`git cat-file --batch`), `graph/{nodes,cite_index,courts,edges.bin}.tsv` and `lean-in-v3/courts_named.tsv` (tiers, joined by court name).
- **Never read:** `events_v3/reports.tsv` and `lean-in-v3/reports.tsv`.
- **Later courts' notes are recognised only to reject them.** Examples are "X, overruled [on other grounds] by Y", "(abrogated by Y)", "superseded by statute as stated in Y", "(overruling X)", "X was overruled in Y", and citator-style ", superseded by statute, ch. 63" straight after a citation (`rules.REPORT`, `rules.CITATOR_BEFORE`). None of them is ever kept as evidence.
- **Treatments** are asserted only from the treating decision's own act-shaped words: we/this court + present verb, the present passive "is/are (hereby) Xed", "to the extent/insofar as … Xed", and "superseded by statute/rule/amendment" stated by the court itself.
- **History** comes only from the reviewing decision's own present-tense disposition. Citation-string history of other cases is rejected.

## Pipeline

1. **`scan.py`: candidate pass.** It covers 152 repos and 6,931,555 files (39,101 parallel-reporter copies have no node), with 0 UTF-8 decode failures.
   - It looks for literal anchors, then runs the family regexes locally: overrule, disapprove, recede from, abrogate, supersede, limited to its facts, question/doubt/continued validity, decline to follow, and repudiate/abandon/no longer follow.
   - It splits each file into parts from its `##` headings (Majority, Per Curiam, Lead/Plurality, Concurrence, Dissent, Head matter, Combined). Inside Majority/Combined sections, a short judge line ending "dissenting"/"concurring" starts a separate opinion (part suffix `~`, exported as the base part).
   - Output: 2,576,683 treatment candidates and 2,351,591 disposition sentences. History candidates were kept only when the decision cites a case bearing its own party names.
2. **`resolve.py`: cheap filters and targets.** Filtering left 65,822 candidates for the model. Rejections:

   | reason | count |
   |---|---|
   | procedural ("objection/point of error … overruled") | 1,205,556 |
   | not act-shaped | 757,372 |
   | report | 240,926 |
   | separate opinion | 155,099 |
   | narrated past act | 98,922 |
   | no resolvable target | 43,636 |
   | head matter | 9,223 |

   - **Target candidates** come from citations in the ±400 window (via `cite_index`), plus names of the decisions the treating decision cites (as v1 did). For soft kinds (limited, questioned, declinedToFollow), the target must be named in the sentence itself.
   - **History targets** are cited decisions that satisfy all of the following:
     - they share two party tokens with the reviewing decision (or one, if a name has only one);
     - they are dated within 8 years before it;
     - they come from a lower court of the same system (or the same court, for withdrawn, reinstated and rehearing en banc granted); SCOTUS may review state courts;
     - they match the body the sentence names (court of appeals, trial court, or an agency, which is rejected).
3. **`classify.py`: model reading.**
   - gpt-5.4-mini (Azure US East 2): 65,576 items, 5 per call, JSON schema.
   - The model returns own_act, kind, targets (ids from the resolved list only; 82 invented ids were dropped), scope, issue labels, temporal and an exact quote.
   - **Hard subset re-read by gpt-6.1-sol** (`hard.py`): status-changing kinds where the model chose among two or more candidates, had confidence below 0.95, scoped the act to issues, or the sentence names another court acting. That is 16,395 items; its answers override the small model's.
   - gpt-6-sol was never used.
4. **`certify.py`: certificates.** For each row it checks:
   - the quote is found exactly in the window (only whitespace runs and quote-mark styles are tolerated, and the window's own text is used);
   - `text[start:end]` equals the quote (asserted);
   - the quote contains a cue of the kind (`rules.CUES`); otherwise the focus sentence is used if that sentence has the cue;
   - the quote is not inside another court's quotation (curly-quote check; a quote starting `“` or `[T]`);
   - the target evidence (`cite:` normalised citation, or `name:` token) occurs in text[start-400:end+400].

   Offsets are characters of the git-HEAD text, UTF-8 decoded with CRLF→LF. The quote and window are normalised tab/newline→space (one for one). Duplicate (by, target, kind, scope) rows keep the most confident one.

   **Authority (court power) is not filtered.** 519 rows have a lower court treating a SCOTUS decision, and 154 rows have SCOTUS as the treating court. Lean decides.

### Cue table (what `certify.py` requires in a quote)

| kind | cues |
|---|---|
| overruled | overrul, repudiat, abandon, no longer follow, no longer good law, no longer the law, no longer be followed, no longer adhere |
| disapproved | disapprov |
| recededFrom | reced |
| abrogated | abrogat |
| supersededByEnactment | supersed, legislatively overruled, abrogat |
| limited | limit |
| questioned | question, doubt, no longer good law, no longer valid, continued/continuing validity/vitality |
| criticized | criticiz, criticis |
| declinedToFollow | decline, refuse, not follow, no longer follow, no longer be followed, not be followed, not adhere, unwilling, not inclined |
| distinguished | distinguish |
| followed | follow |

History cues are affirm, revers, vacat/set aside/quash/annul, modif, denied, granted, dismiss, en banc, withdr, reinstat, refused and publish.

### Field mapping

- **scope:** `all`, `issues:<slugs>`, `partialUnknown` ("to the extent inconsistent…") or `otherGrounds`.
- **temporal:** `unknown` unless the opinion says otherwise. "Prospective" with no date becomes `prospectiveFrom:<treating decision date>`.
- **explicit:** always 1.
- **reader:** `gpt-5.4-mini` or `gpt-6.1-sol`.
- **confidence:** the model's own figure.
- **history src:** `hist-regex-v2:<mode>:<verb>`. The mode records where the target evidence sits:

  | mode | meaning |
  |---|---|
  | `win` | the target citation is in the ±400 window |
  | `long` | the quote runs from the target citation to the disposition (≤2,500 characters) |
  | `remote` | the target is cited elsewhere; the evidence is a shared party-name token inside the window |

## Counts (certification at writing time; the driver re-certifies once the hard pass ends)

**treatments.tsv: 32,809 rows.**

By kind:

| kind | rows |
|---|---|
| overruled | 16,262 |
| disapproved | 7,206 |
| declinedToFollow | 7,151 |
| recededFrom | 877 |
| limited | 593 |
| supersededByEnactment | 513 |
| questioned | 102 |
| abrogated | 81 |
| followed | 14 |
| distinguished | 9 |
| criticized | 1 |

By scope:

| scope | rows |
|---|---|
| partialUnknown | 14,225 |
| all | 11,563 |
| issues | 6,924 |
| otherGrounds | 97 |

Other figures:
- The per kind × scope breakdown is in `reader_stats.json`.
- Temporal (main pass): about 400 rows are prospective and about 90 retroactive; the rest are unknown.
- Parts: almost all rows are majority, about 1.6k per curiam, and 3 plurality.
- Target evidence: about 57% name tokens, 43% citations.

**history.tsv: 54,940 rows.**

| kind | rows |
|---|---|
| affirmed | 26,783 |
| reversed | 15,163 |
| certDenied | 4,506 |
| vacated | 3,809 |
| writRefused | 2,288 |
| withdrawn | 680 |
| modified | 583 |
| reviewDismissed | 495 |
| reviewGranted | 470 |
| reinstated | 135 |
| rehearingEnBancGranted | 28 |

By evidence mode: win 25,313; remote 22,199; long 7,428.

**cert_text.tsv:** 80,571 windows.

## Precision (frozen held-out audit, blind)

Rules were frozen before the main run. Development samples dev1, dev2, dev3 and devh were used to fix rules, and their ids were excluded from this audit.

- **Sample:** 160 admitted treatments (stratified by kind), 40 rejected candidates (20 rejected by the model or the certificate check, 20 by the cheap filters) and 40 history rows (stratified by kind).
- **Reviewers:** five subagents read them shuffled, without the reader's kind or scope. They read the full git text when the window was not enough.
- **Files:** `reader_work/audit/heldout/` (packs, `blind_*.jsonl`, `verdicts_*.jsonl`, `score.json`).
- **Intervals:** Wilson 95%. Weighted figures reweight the strata by the rows of each kind.

**Treatments** (a row counts as right when its own act, kind and target are all right):

| measure | estimate | 95% interval |
|---|---|---|
| corpus-weighted | 0.82 | 0.73–0.91 |
| unweighted, stratified | 111/160 = 0.69 | 0.62–0.76 |
| own act (ignoring kind) | 141/160 = 0.88 | 0.82–0.92 |
| target, given an own act | 129/141 = 0.915 | 0.86–0.95 |
| own act + right target (ignoring kind), weighted | 0.84 | 0.75–0.93 |
| scope agreement, given act and kind | 64/120 = 0.53 | 0.44–0.62 |

Treatments by kind:

| kind | right | estimate | 95% interval |
|---|---|---|---|
| disapproved | 18/19 | 0.95 | 0.75–0.99 |
| questioned | 12/14 | 0.86 | 0.60–0.96 |
| overruled | 21/26 | 0.81 | 0.62–0.92 |
| limited | 11/14 | 0.79 | 0.52–0.92 |
| declinedToFollow | 14/19 | 0.74 | 0.51–0.88 |
| supersededByEnactment | 11/15 | 0.73 | 0.48–0.89 |
| recededFrom | 10/14 | 0.71 | 0.45–0.88 |
| distinguished | 6/9 | 0.67 | 0.35–0.88 |
| followed | 5/14 | 0.36 | 0.16–0.61 |
| abrogated | 3/15 | 0.20 | 0.07–0.45 |

Notes on the weak kinds:
- **abrogated:** 7 of the 12 errors are the court abrogating its *own* precedent, which the reviewers call overruled. That is still a correct status change, but the label is wrong.
- **followed:** "X will no longer be followed" was labelled `followed`. It is now mapped to overruled in `certify.py` (8 rows in the current files).

**Rejection precision:** 39/40 = 0.975 (0.87–0.996). One miss: "We no longer follow lex loci contractus … Simmons is factually distinct".

**History:**

| measure | estimate | 95% interval |
|---|---|---|
| corpus-weighted (own act + kind + target) | 0.74 | 0.47–1.0 |
| unweighted | 27/40 = 0.675 | 0.52–0.80 |

- Weak kinds: modified, reinstated and rehearingEnBancGranted (1/3 each).
- The rows that matter most hold up: certDenied 4/4, writRefused 3/3, reviewDismissed 3/3, affirmed 3/4, reversed 5/8.
- History errors are mostly the wrong earlier proceeding in the same litigation, or narration in footnotes.

## Known gaps

- **Recall is unmeasured.** Only 40 rejected candidates were reviewed (1 miss). Not-act-shaped sentences (757k) are rejected by rule, without reading.
- **distinguished, followed and criticized** are not extracted at corpus scale. They appear only incidentally.
- **Content-filtered items:** a few batches were refused by Azure's content filter. Those items (and 14 with no answer) are not yet retried one at a time.
- **Issue scope labels** are the model's short free-text slugs, not `issues.tsv` keys. Agreement on scope is only 53%.
- **History has three blind spots.** First, decisions that review an unpublished or non-corpus lower judgment yield nothing. Second, SCOTUS memorandum orders with no "reported below" citation yield nothing. Third, head-matter or front-matter history notes are not used. 36,254 history rows were dropped because the target was cited too far from the disposition and no shared party name appears in the window.
- **Temporal** is read only from the window plus up to two prospectivity sentences of the same opinion.
- **Parts:** inferred parts (inside Combined or Majority sections) are exported as plain majority/dissent/concurrence. The `~` marker is kept only in `reader_work`.
- 2026-11-12 coordinator: treatments.tsv scope for partialUnknown/issues rows replaced by holdings_reach.tsv canonical issue keys (issues:<issue_key>) or 'all' where the reach step mapped the act; original kept as treatments.pre_reach.tsv.
- 2026-11-12 data fix (limit 9): 2,287 of the 2,288 writRefused rows were Louisiana Supreme Court 'Writ refused.' (refusal to review), relabelled kind other; 1 Texas row kept. See COURTS.md.

## Round 2 (2026-11-12, agent `recall`): see `../round2/recall.md`

- 596 explicit rows with reader `claude-subagent` (Claude subagents read the v1 prompt plus the round-2 wordings;
  no Azure call): round-2 part map, eight new scan families, 14 new act shapes, wider target resolution
  (`scan2.py`, `rules2.py`, `resolve2.py`, `pack2.py`, `certify2.py`). Read so far: every Supreme Court item and
  960 items of courts of last resort.
- 880 existing rows repaired (`fix_round2.py`): 172 name evidences in the checker's word form, 646 "no longer
  follow" rows relabelled declinedToFollow -> overruled (the court's own or a lower court's decision), 62 quotes cut
  to the act clause.
- 21 rows of the implicit tier: `explicit = 0`, reader `claude-subagent:implicit`, id `ti:<stating decision>:
  <target>:<offset>:<overruling decision>`. NOT held out: the evidence is a later decision of the overruling court
  saying the target was overruled. `by_node` is that later decision. atRisk only.
- `explicit` is therefore no longer always 1, and `reader` has two new values.
- Blind audit: new explicit rows 30/30 own act and target (0.89-1.00); relabelled rows 22/25 (0.70-0.96);
  implicit rows 21/21 (0.85-1.00).
