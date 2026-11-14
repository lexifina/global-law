# caselaw-lean-2, round 5: overrulings that are not self-announced (design and decisions)

This file is the contract for round 5. The Lean sources, the Python reference (written from this file, not from the
Lean), the reader and the scorers all follow it. Every decision is numbered (R5-n) and listed again at the end.

## 0. The problem

*Brown v. Board of Education*, 347 U.S. 483, 494-95, never says "overrule". It says "Any language in Plessy v.
Ferguson contrary to this finding is rejected" and "in the field of public education the doctrine of 'separate but
equal' has no place". Through round 4 a holding changed status only when a court with power said so in words we can
quote, and the words had to be the overruling court's own. Plessy therefore shows as good law with an "at risk" row.

Five kinds of non-announced overruling:

| | kind | round 5 |
|---|---|---|
| A | the court acts on a named case with an operative verb other than "overrule" | class `operativeWords` (§3) |
| B | the target is a doctrine or a line of cases | display only; one narrow rule (§4) |
| C | the effect is limited to a field | display only (§4) |
| D | a LATER court with power says X was overruled by Y | class `recognised`: changes status (§2) |
| E | pure inconsistency, no words anywhere | out of scope, stays out |

The principle is kept: a status changes only on certified words of a court with power. Round 5 widens *whose* words
(D: a later court that itself has power over X) and *which* words (A), never to no words (E).

## 1. Round-5 mode and the baseline (R5-1)

- New optional table `data/treatment_class.tsv`. **Its presence turns round-5 mode on.** Absent: the runner and the
  reference produce the round-4 output byte for byte (same columns, same rows, same strings).
- `treatment_class.tsv`: no header, 5 tab-separated columns:
  `treatment_id`, `claim` (`recognised` | `operativeWords`), `field_limit` (display text or `-`), `doctrine`
  (display text or `-`), `src`. A line with fewer than 5 fields, an unknown claim, or an id that is not in
  `treatments.tsv` is ignored (counted in `summary` as `class_bad_rows`). If an id occurs twice the first line wins.
- A `recognised` claim is only meaningful on a witness row (a treatments row with a line in
  `treatment_witness.tsv`); on any other row it is ignored (the row is checked as in round 4).
  An `operativeWords` claim is only meaningful on a non-witness row; on a witness row it is ignored.

## 2. Recognised overruling (D)

### 2.1 What it says

A treatments row with a witness line (round-4 layout, unchanged: by_node = Y, target = X, date = date(Y),
explicit = 0, the certificate is from W's text, `treatment_witness.tsv` gives W and the evidence naming Y) and a
`recognised` claim says: *a majority sentence of W, a decision of a court that itself has power to overrule X, states
that X was overruled (abrogated) by Y*.

### 2.2 The recognised check (both engines; R5-2)

Run on a witness row with a `recognised` claim. Let `base` be the round-4 witness verdict of the row (unchanged
rules, round-4 cue and disqualifier tables). The row is **recognised** iff all of the following hold; otherwise its
verdict is `base` (so a failed claim falls back to the round-4 "at risk" tier, or to nothing, exactly as if the
claim were absent):

1. the round-4 witness checks pass *in recognised text mode*, i.e. with these three changes to the text checks:
   - cue: the quote (normalised, lower-cased) contains a phrase of the cue table's list `recognised`
     (instead of the kind's list);
   - disqualifiers: the quote contains no phrase of the list `disqualify_recognised` (instead of the
     `disqualify_treat` list: "overruled by" is the normal form here, not a disqualifier);
   - **X and Y are both named in the quote itself**: the target evidence and the by-evidence are resolved against
     the normalised quote only, not against the window (same resolution rules otherwise: a `cite:` must occur
     compacted in the compacted quote and resolve through `cite_index.tsv` to X, resp. Y; a `name:` needs every
     token of length >= 3 as a whole word of the quote);
   all other steps are as in round 4 and in the same order: `witnessBadRow`, `shaUnknown`, `noWindow`, `windowHash`,
   `quoteMismatch`, `noCue`, `disqualified`, `targetUnresolved`, `partNotMajority`, `byUnresolved`, `targetLater`,
   `witnessEarlier`, `witnessNoStanding`, then Y's power over X (`noAuthority` / unverified).
2. `power`: **W has power over X**, not mere standing: `powerAnyDomain(W, X) == true` (the test used for an
   overruling decision whose issue domain is unknown: W could overrule X on every domain the issue could have).
   A same-court panel under a strong horizontal rule has standing but no power: not recognised.
3. `datesKnown`: date(X), date(Y) and date(W) are all non-zero. (With step 1: date(X) <= date(Y) <= date(W).)
4. the compacted by-evidence differs from the compacted target evidence (text after `cite:` / `name:`).

Verdict strings in `certs.tsv`: `okRecognised` (Y's power over X verified), `okRecognisedUnverifiedBy` (Y's power
unknown); otherwise the string of `base`. `result_all` and `result_firm` are computed separately with the two
rule sets as for every row.

### 2.3 Effect on status (R5-3)

New unknown reason `Unk.recognisedLater` (index 3; rank 4: the most severe unknown, below every negative). Output
string `unknown:recognisedLater`, class `unknown`.

A row recognised under a rule set yields, for each event the round-4 splitting by issue/power would yield for an
explicit row with the same scope (`issues yes` with power known; `issues unk` / `someOf unk` with
`powerKnown = false`), **two effects**:

| | eff | start | lapse | scope, conductFrom, reach, actor |
|---|---|---|---|---|
| e1 | `unknown recognisedLater` if powerKnown else `unknown powerUnknown` | date(Y) | first lapse of Y on or after date(Y) | as an explicit row by Y would have; actor = Y |
| e2 | `neg overruled` (`neg abrogated` if kind = abrogated) if powerKnown else `unknown powerUnknown` | date(W) | the earlier of: first lapse of Y on or after date(Y); first lapse of W on or after date(W) | same; actor = Y |

- "lapse" is `lapseOfDecision` (vacated, withdrawn, substituted, depublished or reversed on every issue; an en banc
  grant that vacates under the court's rule counts, read through the *lapsing decision's own* court: Y's for Y, W's
  for W).
- No revival: a recognised effect does not come back when Y or W is reinstated (deviation, conservative).
- rule id of both effects: `recognised` (new `RuleId.recognised`; path string `recognised`).
- `src` = the treatments row; the status row's `witness_row` column shows the row id (`tw:Y:X:start:W`), `actor` Y.
- So, with no other event: X is `good` before date(Y); `unknown:recognisedLater` from date(Y) to date(W)-1;
  `neg:overruled` from date(W). If date(Y) = date(W) the unknown interval is empty.
- A partial scope behaves as for any effect: on the whole decision (issue `-`) it gives `unknown:partialScope`
  from date(Y) on and never a negative.
- A witness row that is not recognised has no status effect (round 4, unchanged).

### 2.4 Theorems to prove (stated before proving; names final unless a statement proves false)

Spec (`Spec/Recognised.lean`):
1. `recognised_never_neg_before_witness`: for a row with `recog = some r`, any list `l`, `t < r.date`: if
   `status (recogEffects .. ++ l) k t u = neg n` then `status l k t u = neg n` (a negative before date(W) is never
   the recognised row's doing).
2. `recognised_needs_power`: `r.power = false -> recogEffects .. = []`.
3. `witness_without_claim_no_effect`: `tr.recog = none -> recogEffects .. = []`.
4. `recognised_not_explicit`: `tr.explicit = true -> recogEffects .. = []` (a row is explicit or recognised, never
   both; with `inferred_treatment_no_effect` each row has at most one source of effects).
5. `status_append_comm`: `status (a ++ b ++ l) = status (b ++ a ++ l)` (order independence across recognised and
   other effects; a corollary of `status_perm`, which is unchanged).
6. `explicit_recognised_agree_from_witness`: an explicit row and a recognised row for the same (Y, X, kind, scope,
   temporal, powerKnown) give the same status for every `t >= date(W)`, when neither Y nor W has lapsed.
7. `recognised_never_weakens`: `rank (status l) <= rank (status (recogEffects .. ++ l))`.
8. `recognised_unknown_between`: with `powerKnown`, scope `all`, no lapse, `date(Y) <= t < date(W)`,
   `conductFrom <= u`: `status (recogEffects ..) k t u = unknown recognisedLater`.
9. `recognised_neg_from_witness`: same hypotheses but `t >= date(W)`: the status is `neg overruled` / `neg abrogated`.
10. `demoted_never_neg` (§3): an effect whose scope is `demote s` never contributes a negative.
Checker (`Certificate.lean`):
11. `checkRecognised_sound`: a recognised verdict implies: the claim was made, the witness checks pass in recognised
    text mode (so cue, no disqualifier, X and Y in the quote, majority, dates ordered, standing), `power`,
    `datesKnown`.
12. `checkRecognised_fallback`: a verdict that is not recognised is the round-4 witness verdict.
13. `checkRecognised_no_claim`: without a claim the verdict is the round-4 witness verdict.
14. `checkOperative_sound` (§3).
Findings (`Spec/Findings.lean`):
15. `recognisedLater_not_citesOverruled`: a citation whose cited status is `unknown recognisedLater` is flagged
    `citedRecognisedLater` and is not `citesOverruled`, `citesVacated` or `citesWithdrawn`.
Examples: `plessy_timeline` (the three intervals, by `decide`), `recognised_row_effect_needs_power`.

### 2.5 Findings (R5-4)

- A citation i -> X whose cited status (whole decision, in the citing court's line, on the citing date) is
  `unknown:recognisedLater`, and which is not the citing decision's own doing (`selfCaused`, as for the other
  citation findings): new finding `atRisk  i  X  -  recognisedLater`. firm = the firm rule set gives the same.
- From date(W) on the status is negative, so the existing `citesOverruled` fires unchanged.
- A row that is recognised under the full rule set emits no `inferredRejection` finding (its status rows carry it).
  A witness row that is not recognised emits it as in round 4.

## 3. Operative words beyond "overrule" (A)

### 3.1 What it says (R5-5)

An ordinary explicit row (explicit = 1, by_node = the acting court's decision, certificate from its own text) with an
`operativeWords` claim says: *the court, in its own majority words, rejects / repudiates / disapproves / declares no
longer law the named case, or "the language / doctrine / rule / holding of" the named case*. Kind must be
`disapproved`.

### 3.2 The operative check (R5-6)

The round-4 certificate check with these changes (same order, same reason codes):
- `operativeBadRow` (first, before `shaUnknown`): kind is not `disapproved`, or explicit = 0.
- cue: the quote contains a phrase of the list `operative`;
- disqualifiers: `disqualify_treat` and `disqualify_operative` (the court "rejects" arguments, contentions, claims,
  readings, invitations constantly: those objects disqualify);
- the target is named **in the quote itself** (as in §2.2).
A row whose claim fails is not admitted (no fallback: the plain round-4 check is not tried).

### 3.3 Partial unless the whole case is disposed of (R5-7)

`whole` = the quote contains a phrase of the list `operative_whole` ("is no longer good law", "must be regarded as
overthrown", ...). If `whole` is false, every event the row yields has its scope **demoted**:
`all -> someIssue`, `issues ks -> someOf ks`, `someIssue` and `someOf` unchanged. A demoted effect contributes
`unknown partialScope` at most (theorem 10): the target is "partly negative", never overruled. If `whole` is true
the scope stands as written and the effect is that of a `disapproved` row (`neg overruled`).
Demotion applies to the events after the round-4 issue/power splitting (so `all` expands to the issue list first,
then becomes `someOf` that list; with no holdings it is `someOf [0]`, i.e. the anonymous issue only).

Precisely: let `evs` be the events round 4 would build for the row; if the claim is admitted and `whole` is false,
replace each event's scope `s` by `demote s`, where `demote all = someIssue`, `demote (issues ks) = someOf ks`.

### 3.4 Legacy rows

Rows already in the round-4 tables whose quote has an operative verb and no "overrul" (rounds 2-3 admitted
"repudiate", "no longer follow", ... as `overruled`) are **not** re-checked and keep their effect; they are only
*classified* `operativeWords` (§5). Recorded as a deviation: the strict check applies to rows that claim the class.

## 4. Doctrines and field limits (B, C) (R5-8)

- `field_limit` and `doctrine` in `treatment_class.tsv` are displayed (copied to `classes.tsv`), never reasoned on.
- One narrow rule, in the reader not in Lean: a doctrine is accepted as a target only when the quote ties it to
  exactly one named case ("the separate-but-equal doctrine of Plessy", "the rule of X"). The row then targets that
  case, with partial scope (the act is on the doctrine, not on the case as a whole) and the doctrine as label.
  A "line of cases" resolves to nothing unless each case is named, and then each needs its own row.
- A field limit ("in the field of public education", "as respects ...") always makes the scope partial.

## 5. Classes (R5-9)

Every treatments row of a status-changing kind has exactly one class, computed by the engines (not read from the
reader):

| class | rule |
|---|---|
| `recognised` | witness row recognised under the full rule set (§2.2) |
| `atRiskWitness` | any other row with explicit = 0 (witness row not recognised; old-format implicit row) |
| `selfAnnounced` | explicit = 1 and the normalised lower-cased quote contains a phrase of the list `self_announced` (`overrul`, `disapprov`, `reced`, `abrogat`) |
| `operativeWords` | explicit = 1 otherwise |

Other kinds have class `-`. Order for ties: `selfAnnounced` < `operativeWords` < `recognised` < `atRiskWitness`.

### 5.1 Output in round-5 mode only

- `classes.tsv` (new; header `id	class	claim	verdict	field_limit	doctrine	witness`): one line per treatments
  row of a status-changing kind whose row parses: id, class, the claim (`-` if none), `result_all` as in certs.tsv,
  field_limit and doctrine from the class table (`-` if none), W's node (`-` if not a witness row).
- `status.tsv` and `status_lines.tsv`: one more column at the end, `oclass`: the least class (order above) among
  the effects that make the row's status, i.e. effects `e` with `e.contrib == status`, status not good, and rule
  `treatment`, `prospective` or `recognised`; the class of such an effect is `recognised` for rule `recognised`,
  else the class of its row. `-` when there is none (good law; history; supersession).
- `findings.tsv`: one more column at the end, `oclass`:
  - citation findings on a status (`citesOverruled`, `citesVacated`, `citesWithdrawn`, `citesNotCitable`,
    `appliesSupersededHolding`): the `oclass` of the cited status the finding reads (same issue, citing date,
    citing court's line);
  - `atRisk citesLaterNegated:*`: the `oclass` of the as-of status it reads;
  - `atRisk recognisedLater`: `recognised`;
  - treatment-level findings (`panelDepartsWithoutEnBanc`, `ignoresBindingInUnit`, `atRisk claim:*`,
    `atRisk inferredRejection`): the row's class;
  - everything else: `-`.
- `summary`: extra lines `class_rows`, `class_bad_rows`, `recognised_rows`, `operative_rows`.
- The headers written by `run_lean.sh` gain `oclass` in round-5 mode.

Scores "with and without a class" are reported two ways: by the `oclass` tag, and for the headline figures by
ablation (re-running with the class's rows removed), which is exact.

## 6. Cue table additions (R5-10)

`tools/caselaw2/cues/cue_table.json` (still the single table) gains: `self_announced`, `recognised`,
`disqualify_recognised`, `operative`, `operative_whole`, `disqualify_operative`. The lists are data; they are fixed
after the dev-set audits and frozen in `FREEZE.md`. The round-4 lists are not changed.

## 7. Where candidates come from, and what is forbidden

- `recognised` candidates: later-court statements found in the corpus text, restricted to the `feed` set of
  `round5/tests` (the speaker has power over the target). Statements outside `feed` never enter the model.
- `operativeWords` candidates: the acting decision's own text.
- Never used to pick candidates: SCDB, CRS / Constitution Annotated, Christiansen-Eskridge, Hasen, and
  `round5/gold_fresh/sealed/`. `gold_fresh/dev/` is used for diagnosis and scoring only.
- All reading by Claude subagents; no external model API.

## 8. Decisions

| id | decision |
|---|---|
| R5-1 | Round-5 mode is switched by the presence of `treatment_class.tsv`; without it the output is round 4's, byte for byte. |
| R5-2 | Recognition needs W's *power* over X, both names in the quote, a recognition cue, known dates; a failed claim falls back to the round-4 witness verdict. |
| R5-3 | Timeline: good before Y; `unknown:recognisedLater` from Y to W; negative from W, actor Y. Two effects joined; no revival. |
| R5-4 | Citation between Y and W: `atRisk recognisedLater`; after W: `citesOverruled`. A recognised row emits no `inferredRejection`. |
| R5-5 | Operative-words rows are kind `disapproved` with an `operativeWords` claim. |
| R5-6 | Operative check: operative cue, extra disqualifiers, target in the quote; no fallback. |
| R5-7 | Without a whole-case phrase the scope is demoted: the target is partly negative, never overruled. |
| R5-8 | Field limits and doctrine labels are display text; a doctrine is a target only when tied to exactly one named case in the quote. |
| R5-9 | Four classes, computed by the engines; `oclass` on status and findings rows; `classes.tsv`. |
| R5-10 | New cue lists in the single cue table; frozen before the sealed test. |
| R5-11 | E (inconsistency without words) stays out: no row, no finding. |

## 9. Rulings made after the reference agent listed what this file left open (13 Nov, 12:45)

The reference was written from sections 0-8 alone; its author listed 31 points the text did not settle
(`ref/NOTES.md` (b), A-1 to A-31). Most were read the same way on both sides. The ones that needed a ruling:

| point | ruling |
|---|---|
| class table line | exactly 5 fields, as every other table; any other count is a bad row |
| duplicate id in the class table | the first valid line wins; a later line is ignored and is not counted as a bad row |
| `operative_rows` counter | rows whose `operativeWords` claim is admitted under the full rule set (`ok` or `okUnverifiedBy`) |
| which date is date(Y) | always the by-decision's date in `decisions2.tsv`; the row's own date column is never used, for any row |
| "first lapse on or after d" | the earliest lapse event dated >= d; an earlier lapse event is ignored (round-4 rule) |
| `firm` on status rows | the round-4 rule, unchanged: two unknowns agree iff both or neither are `partialScope` |
| `laterCourtSays:<id>` supersessions | need the round-4 plain text check of that row, as before; a recognised verdict does not count |
| a demoted event | contributes `unknown:partialScope` to every issue it reaches, whatever its power reason |
| order of unknown reasons | partialScope < enBancRuleUnknown < powerUnknown < recognisedLater |
| whole-case test (§3.3), added 12:50 | `whole` = the quote has a phrase of `operative_whole` AND no phrase of the new list `operative_limit` ("to the extent", "insofar", "in the field of", ...) |
| cue lists | `recognised` and `self_announced` use " reced" (word start: "preceded" must not match); the recognition disqualifiers use whole forms (argues, argued, urges ...) instead of `argu`, `urge` |
