# Precedent reference implementation: notes

`precedent_ref.py` is an independent Python reference for the rules of precedent in caselaw-lean-2. It exists
for differential testing against the Lean model (DESIGN.md "REVISED DESIGN" D4). It was written from
`research/doctrine.md`, `SCHEMA.md` and DESIGN.md's revised-design section only. The only part of LEAN.md
read was its "Outputs" section. No Lean under `LegalProofs/CaseLaw2/` was read.

Every place where the doctrine had to be read one way rather than another is listed below as R1, R2 and so
on, with the doctrine section it rests on. The code cites the same R numbers. **[Ambiguous]** marks readings
where the doctrine itself leaves the answer open. When the Lean output disagrees with the reference on one of
these, the cause is a reading to triage, not necessarily a bug on either side.

## Files

| File | What it is |
|---|---|
| `precedent_ref.py` | the reference: `force`, `canChangeStatus`, `status`, certificate checks, splits, findings, and the TSV runner |
| `diff.py` | compares Lean and reference outputs; buckets every disagreement by file, field and rule |
| `gen.py` | random SCHEMA universes for differential testing; a mutant self-test; a 6.9M-row scale test |
| `REF_NOTES.md` | this file |

## Running

```bash
cd global-law-lean/lean-proofs/tools/caselaw2/ref
W=~/Documents/us-caselaw-lean-work/caselaw-lean-2

# Reference outputs: status.tsv, findings.tsv, certs.tsv, splits.tsv and ref_stats.tsv
python precedent_ref.py run --data $W/fixtures/data --edges $W/fixtures/edges --out $W/fixtures/ref_out
python precedent_ref.py run --data $W/data --edges ~/Documents/us-caselaw-lean-work/lean-in-v3 --out $W/ref_out

# Single queries
python precedent_ref.py force  --data D NODE HOLDING|- DST_COURT T U [--unit N] [--firm]
python precedent_ref.py status --data D NODE HOLDING|- T U
python precedent_ref.py can    --data D BY_NODE TARGET_NODE [ISSUE]

# Compare Lean with the reference. Exit status 1 if they disagree; --tsv writes every disagreement.
python diff.py $W/out $W/ref_out [--map labels.json] [--tsv diff.tsv] [--examples 3]

# Differential random testing: generate a universe, run the reference, run run_lean.sh, then diff
python gen.py --seed 1 --rounds 200 --n 100 --out /tmp/drt --ref --lean --diff
python gen.py --mutants --rounds 20 --out /tmp/mut     # self-test: diff catches each broken variant
python gen.py --big 6900000 --out /tmp/big             # scale test
```

### Scale

On 6.9M decisions and the 48M v1 citation edges (16 `edges-*.tsv` files), a full run takes 54 s. Of that,
loading decisions2 takes 19 s and streaming the edges takes 35 s. Peak memory is about 150 MB. Decisions are
held in flat arrays of about 15 bytes each. Text SHAs are kept only for nodes that own a certificate. Edges
are streamed, and only those whose cited node has a negative status are kept.

### Firm and all

The run uses two rule instances, as DESIGN D2 specifies. `all` uses every row. `firm` drops every row tagged
`U` in courts2, succession, adoption, system_rules and marks. Output rows come from `all`, with `firm=1` when
the `firm` instance produces the same row.

## Output formats

These follow LEAN.md's "Outputs (planned)" section. The column meanings below are my reading of it.

- **`status.tsv`**: `node, issue, holding, from, to, status, kind, by, conduct_from, firm`.
  - There is one block of rows for each target node that has an admitted event: same-case history, a
    treatment, or a supersession.
  - The anonymous issue ⊤ of §8.2 is written as `issue=- holding=-`. Each admitted holding of the node gets
    its own block.
  - `[from, to)` is an asOf interval. `to=99999999` means open-ended.
  - In each asOf interval, rows are conduct pieces. A row applies to conduct dates from `conduct_from` up to
    the next row's `conduct_from`. `0` means all conduct.
  - Intervals in which every piece is `none` are left out. Inside an interval that is written, `none` pieces
    are written too.
  - `status` takes one of three values (D5):
    - `negative`: a negative treatment is admitted;
    - `none`: nothing is admitted;
    - `unknown`: undecided, with the reason in `kind`.
  - `kind` is the event kind, such as `overruled`, `withdrawn` or `supersededByEnactment`. It has the suffix
    `:partial` when the event touches only part of ⊤. For `unknown` rows, `kind` holds the reason, for
    example `temporal`, `inferred:overruled` or `power:horizontal.missing`.
  - `by` is the treating or same-case node, `lc:<id>` for a law change, or `-1` when unknown.
- **`findings.tsv`**: `kind, citing, cited, extra, firm`. `extra` is `<eventKind>:<by>[:<issue>|:allHoldings]`.
  For `citesUnpublishedAsBinding` it is the computed force; for `atRisk` it is the reason.
- **`certs.tsv`**: `file, id, ok|reason`. `file` is one of `treatments.tsv`, `history.tsv` or `holdings.tsv`.
- **`splits.tsv`**: `issue, court1, court2, answer1, answer2, date`.
  - The pair is ordered by `(court, answer)`.
  - `date` is the earliest date on which the split exists, which is the later of the two holdings' dates.
  - There is one row per issue and court pair. When both holdings are from the same court, they must come
    from different units.

- **`status_lines.tsv`** (round 2, DEVIATIONS 75): `status.tsv`'s ten columns plus a last column `line` (`orig` or an
  adopter court id). Rows exist only for decisions with a line-limited effect in the all-tables run: per decision, one
  block per pure view (`orig`, then the adopters named in its reaches, ascending), each over the anonymous issue and
  the admitted holdings. Always written, possibly empty. `status.tsv` is unchanged.
- **`horty.tsv`** (round 2, DEVIATIONS 78): `family, court, verdict, cases, firm`. `court` is `id` or `id/unit`;
  `verdict` is `consistent` or `inconsistent`; `cases` is the holding ids sorted as strings, comma-joined; `firm` is
  always 1. Always written, empty without factor rows.

`diff.py` compares status timelines **as functions**. It evaluates both sides at every breakpoint either side
uses, so two equivalent but differently segmented outputs agree. It treats `to=99991231` and `to=99999999` as
the same open end. If the Lean runner uses different labels, pass `--map`.

## Coverage of doctrine rules

| Doctrine | Where | Notes |
|---|---|---|
| §9.10 graded force scale | `FORCE_RANK`, `fmin`, `fmax`, `agree` | plus `unknown` (D5) |
| F1 SCOTUS binds all courts on federal law | `rel` | |
| F2 summary affirmance | `decision_caps` | binding, no extra cap |
| F3 cert denied, no effect | `effects` | |
| F3 / S-TX writ or petition refused: promotion | `holders`, `tx_promotes` (R24, L5) | Texas civil intermediate only, by era and wording |
| F4 vacatur, GVR | `effects` | |
| F5 equally divided | `decision_caps` | forces `none` |
| F6 plurality, *Marks* | `decision_caps`, `splits` | `resultOnly` unless a marks row exists |
| F7 prior-panel rule, en banc, circulation | `rel`, `power`, `bench_ok` | |
| F8 en banc grant vacates the panel opinion | `effects` | uses `enBancGrantVacatesPanel` |
| F9 unpublished opinions, date cut-offs, per publication kind | `unpub_cap` (R4, R8) | |
| F10 / F11 adoption (*Bonner*, Unit B, *McMorris*, *South Corp.*) | `holders` (R5–R7) | |
| F11(b) Federal Circuit subject-matter reach | `rel`, `power` | |
| F12 *Golsen* | `rel` | needs `decisions2_extra.tsv` venue, otherwise `unknown` |
| F13 / §4.4 trial courts never bind; BAP persuasive | `rel` | |
| F14 abrogation | `effects` (treatment kind `abrogated`), `at_risk` (contrary binding holding) | |
| E1 *Erie*: 25 Apr 1938, *West*, *King*, corollary | `rel` | |
| E2 certified answer | `decision_caps` | handled as an ordinary decision of the high court |
| E3 state courts on federal law; `stateFollowsCircuit` | `rel` (R11) | |
| H1 / H2 last resort, dual last resort | `rel`, `power` (R23) | |
| H3 succession, dated tier | `holders` (R7) | |
| H4 commissions | adoption filters, `notation_filter`, `decision_caps` (L4) | from `commission.tsv` when present, else `unknown` (R5) |
| §4.1 horizontal rule (strong, soft, none, withinUnitOnly) | `rel`, `power` (R9) | |
| §4.1 vertical rule (`trialScope`) | `trial_scope` | |
| S-TX TRAP 41.3 transfer | `rel` | needs `decisions2_extra.tsv` `transfer_from` |
| S-CA review granted (2016 cut-off) | `effects` (R16), `force` | |
| S-CA depublished | `effects` | |
| S-FL receded from, sister DCA | `effects`, `power` | |
| T1 / T2 who may change status | `can_change`, `power` | |
| T3 revival | `_eval` (R15) | |
| TM1 effective on filing | everywhere | dates are decision dates |
| TM2 *Sunburst* / *Harper* temporal scope | `temporal_ranges` (R14) | |
| TM3 withdrawal: overrulings lapse | `_eval` | |
| TM5 date cut-offs | data rows | |
| AB1 supersession by enactment | `effects` | effective date, retroactive date, issue scope |
| HD4 "on other grounds" | `scope_applies` | |
| §8.2 anonymous issue ⊤ | `scope_applies` | `:partial` |
| §9.22 `force` | `force` / `authority` | |
| §9.23 `canChangeStatus` | `can_change` | |
| §9.24 splits | `splits` | |
| §9.25 two-date queries | `status` | |
| §9.27 findings | `findings` | |
| DESIGN layer 4 certificates | `check_cert` (R19–R22) | |

### Not modelled

- **GA physical precedent (S-GA).** The schema has no concurrence-pattern column.
- **AEDPA filter (F1).** The schema has no proceeding type.
- **Dicta and necessity (HD1, HD3).** `holdings.tsv` holds holdings only.
- **Syllabus rules (HD5).** These are a matter for extraction.
- **Conflict resolver (§9.24).** Modelled since the five-limits revision (L3): `conflicts_asof.tsv`.
- **Kansas quasi-exception (H1).** Not modelled.
- **9th Cir. "clearly irreconcilable" standard (F7 table).** Not modelled except as an F14 `atRisk` finding.
- **Bankruptcy courts bound by BAP (F13).** Persuasive by default.

## Interpretive choices

### Force

- **R1 — Unknown attributes are enumerated, not defaulted (D5).** An unknown publication, form, or issue
  domain is evaluated over every value it could take:
  - publication: published or unpublished;
  - form: full, plurality, or equally divided;
  - domain: federalGeneral, stateLaw of each system involved, and federalPatent if the Federal Circuit is
    involved.

  If the results agree, the answer is definite; otherwise it is `unknown:ambiguous:<attribute>`. A date of 0
  gives `unknown:date` unless the court has only one epoch. **[Ambiguous]** The doctrine says "no silent
  defaults" but does not say how unknowns compose.
- **R2 — Force combines over holders by the strongest route** (`fmax`). An unknown route is definite only
  against a binding route. Caps (publication, form, an adoption's force) are applied with `fmin`.
- **R3 — Where `resultOnly` sits on the scale.** It ranks between `persuasiveStrong` and `persuasive`, because
  it binds as to result. `physicalPrecedent` ranks equal to `persuasive` (§9.10 says ≈). A plurality without
  a *Marks* row is capped at `resultOnly`, for a named holding and for ⊤ alike. **[Ambiguous]** §8.2 step 3
  says "`resultOnly` or `persuasive`".
- **R4 — Unpublished decisions with no `unpubForce` row are capped at `persuasive`.** DESIGN layer 1:
  "unpublished never binds"; F9 tables. `unpubForce` is read for the deciding court, court-level row first,
  and keyed on **the precedent's date** (§9.15). A `form=memorandum` decision is capped the same way as a
  `memorandum` publication.
- **R8 — `unpubForce` values may carry a publication prefix.** A value `<publication>:<force>` (for example
  `memorandum:persuasive`) applies to that publication kind only; a plain value applies to every
  non-published kind. A specific value wins over a plain one at the same level, and a court-level row wins
  over a system-level row. This reads the courts agent's rows; SCHEMA gives the value only as "Force".
- **R9 — Which date keys each rule.**
  - `horizontal`: the precedent's date. S-MI keys on the precedent; TM5 says authority attaches by the date
    of the precedent.
  - `unpubForce`: the precedent's date.
  - `trialScope` and `stateFollowsCircuit`: the date of the question `t`. The Nebraska 1996–2007 rows
    describe the courts' practice in that period.
  - `enBancGrantVacatesPanel`: the grant date.
  - `circulationCountsAsEnBanc`: the circulating decision's date.

  **[Ambiguous]** Only MI and §9.15 state their date.
- **R10 — SCOTUS on a state-law issue.** It binds lower *federal* courts and is persuasive to state courts.
  F1 says it does not bind the state's highest court, and E1's corollary says federal decisions never bind
  state courts on state law. **[Ambiguous]** The doctrine is silent on lower federal courts.
- **R11 — `stateFollowsCircuit` applies only to the court of appeals of the circuit the state lies in** (E3).
  The state is found from the names of the system's courts; the circuit comes from 28 U.S.C. § 41
  geography. If the circuit cannot be found and a row exists, the result is `unknown`. District courts stay
  persuasive. **[Ambiguous]** The table gives no circuit.
- **R12 — Only listed relations bind.** Any relation the doctrine does not list as binding is `persuasive`.
  This covers:
  - another state's courts on that state's law (choice of law);
  - two separate intermediate courts of one system (PA Superior and Commonwealth, AL Civil and Criminal,
    TX courts of appeals other than in transfer cases);
  - an intermediate court towards its own court of last resort.

  **[Ambiguous]** The doctrine does not cover choice of law.
- **R13 — A state high court's ruling on a federal issue binds the lower courts of its own system.** H1 binds
  "on that system's law"; vertical binding within the system is the general practice. A dual court of last
  resort (H2) binds all lower courts, because the schema has no case-kind field. **[Ambiguous]**
- **Federal Circuit after 1 Oct 1982.** On a `federalPatent` issue, a regional circuit is persuasive to its
  district courts (F11(b) exclusive jurisdiction). Before *Erie*, a federal decision on state law is
  `unknown` for the local-versus-general distinction (E1), whether the federal decision or a state high
  court decision is the source.

### Court identity

- **R5 — Adoption filters.**
  - `all`: every decision.
  - `unitB`: decision unit 2. **[Ambiguous]** SCHEMA does not define the encoding.
  - `unitA`: unit 1.
  - `unit:<n>`: unit n.
  - `issue:<d>`: the issue domain is `d`; `localLaw` also matches stateLaw of the adopter's system.
  - `notTrialDivision`, `opinionAdopted`, `holdingApproved`, `judgmentAdopted`, `none`: the schema cannot
    see these, so the adopted route is `unknown` (H4: weights uncertain).
- **R6 — Adoption grants binding force, but power only to an adopter of equal or higher tier.** An adopter
  may overrule adopted decisions only when its tier at `t` is at least the decision's dated tier.
  - The 11th Cir. en banc may overrule pre-split 5th Cir. law (*Bonner*). So may the Federal Circuit for the
    CCPA and Court of Claims, and the D.C. Court of Appeals for pre-1971 D.C. Cir. decisions.
  - The new Kentucky Court of Appeals may **not** overrule its last-resort predecessor (SCR 1.030(8)(a)).
- **R7 — Succession and adoption together** (H3, F10).
  - A rename, replace or absorb moves the authority to the successor. The deciding court's dated tier is
    kept (H3: "the dated tier for the deciding court at decision time").
  - After a `split`, the old court keeps the authority too while it still exists. The 5th Cir. keeps its
    pre-split law.
  - Self-renames (`old = new`) are no-ops.
  - Where an adoption row covers the same (new, old) pair, **the adoption row governs and the succession row
    adds nothing**. So *McMorris* (219←430, persuasive) beats the 430→219 split, and the H4 notation rows
    beat 2948→2927.
  - A court that has the same id and the same tier is "the same court"; the same id with a different tier is
    a different court. This is how the Kentucky 918 or 913 epochs work.
- **R23 — A court of last resort and its own precedent** (H1, §4.3 DC, F7).
  - Without a horizontal rule it is not bound and may overrule with any bench: force `persuasiveStrong`,
    power `yes`.
  - A court-level horizontal row (for example `-2906 soft`) applies to it.
  - The system-level row applies only when no other court in the system has an intermediate epoch. This is
    D.C.: divisions are bound and only en banc overrules, per *M.A.P. v. Ryan*.
  - Elsewhere the system-level horizontal row describes the system's intermediate court (§4.3).
- **R24 — Writ or petition refused (S-TX, F3 exception).** From the notation's date, the opinion is also held
  by the system's civil (or `all`) court of last resort, with tier L and no overruling power. **[Ambiguous]**
  The schema gives no writ/petition era split; both promote.

### Horizontal and vertical

- **`horizontal`.** `strong` gives `binding`; `soft` gives `persuasiveStrong` ("adheres but may overrule");
  `none` gives `persuasive`. `withinUnitOnly` gives `binding` when the decision's unit equals the destination
  unit (including both 0) and `persuasive` otherwise. A missing row for an intermediate, BAP or special
  court gives `unknown:horizontal.missing`.
- **`trialScope`.**
  - `statewide`: `binding`.
  - `statewideChooseOnConflict`: `bindingAbsentConflict`.
  - `ownUnitThenAny`: own unit `binding`, another unit `bindingAbsentConflict`.
  - `ownUnitOnly`: own unit `binding`, another unit `persuasive`.

  Unit 0 on either side, under a unit-dependent rule, gives `unknown:unit`.
- **Units.** The destination unit is the citing decision's unit when one is known; otherwise it is the
  courts2 unit of the destination court.
- **Appellate divisions of trial courts (§4.4).** They bind the trial courts of the same unit.

### canChangeStatus

These rules follow §9.23, T1 and T2.

- The overruling decision must not be earlier than its target.
- **Power over any holder suffices.** The doctrine says the treating court must have power over the target.
  With adopted decisions this can be relative: the 11th Cir. overruling pre-split 5th Cir. law does not
  change 5th Cir. law, but `status.tsv` has no court column. **[Ambiguous]**
- **`soft` and `none` let any bench overrule.** §9.23 says `requiredBench = panel` for both. For `none` this
  sits uneasily with S-CA ("at most persuasive"). **[Ambiguous]** I followed §9.23 as written.
- **`strong` needs an en-banc-equivalent bench.** That means `enBanc`, `limitedEnBanc`, `conflictPanel` or
  `wholeCourt`, or `circulated` where `circulationCountsAsEnBanc=1`. `withinUnitOnly` needs the same unit
  plus the same bench rule; a sister unit has no power (S-FL "sister DCA").
- **Trial courts never change status,** not even their own decisions' (F13: no binding status to change).
  **[Ambiguous]**
- **SCOTUS** has power over every federal target, and over state targets on federal issues only (F1, F14;
  T2 for state law).

### Status

- **R14 — Temporal scope** (TM2).
  - `retroactive`: all conduct.
  - `prospectiveFrom:d`: conduct from `d`.
  - `pureProspective`: conduct from the day after the decision ("conduct occurring after the date of this
    opinion").
  - `unknown` on a federal-domain issue: all conduct (*Harper*, *Griffith*).
  - `unknown` otherwise: `negative` for conduct on or after the decision date, `unknown:temporal` before it.
    Every reading except a later `prospectiveFrom` agrees for conduct on or after the decision.

  **[Ambiguous]**
- **R15 — Revival** (T3, TM3). While an overruling decision B is withdrawn, vacated, substituted, depublished
  or en-banc-vacated, its overruling lapses and the target is restored. The check is made over the same
  issues the overruling covered; a partial lapse gives `unknown`. If B is reversed, the overruling is
  `unknown:revival:reversed`. If B is itself overruled, it is `unknown:revival:notAutomatic`: "revival is not
  automatic". If B's review was granted, it is `unknown:revival:reviewPending`. B being superseded by statute
  leaves the overruling standing. Reinstatement of B revives the overruling.
- **R16 — `reviewGranted`.** It suspends status (S-CA) only for California courts, or where a
  `reviewGrantedSuspends=1` system rule exists. The suspension ends on `reviewDismissed`, `affirmed`,
  `modified` or `reversed`. **[Ambiguous]** The doctrine describes only California.
- **Same-case restorers.**
  - `reinstated` ends withdrawn, vacated, depublished, en-banc-vacated, substituted and review-granted
    effects.
  - `rehearingEnBancGranted` vacates only if `enBancGrantVacatesPanel=1`. With no row, it is `unknown`.
  - On the same day, negative events are applied before restorers, so a same-day reinstatement wins.
    **[Ambiguous]**
- **Withdrawal (TM3).** A withdrawn opinion is a nullity *from the withdrawal date*, not ab initio. This is
  the option TM3 says to choose, with a flag.
- **Scope.**
  - `all`: every holding.
  - `issues:K`: holdings whose issue is in K. For ⊤ this gives `<kind>:partial`.
  - `partialUnknown`, or history scope `unknown`: `unknown:unknownScope:<kind>` for a named holding,
    `<kind>:partial` for ⊤.
  - `otherGrounds`: `unknown:otherGrounds:<kind>` for a named holding, `<kind>:partial` for ⊤. **[Ambiguous]**
    HD4 says the cited proposition stays good law, but which extracted holding is "other" is unknown.
- **Admission.**
  - A treatment or history row counts only if its certificate passes.
  - `explicit=0` negative treatments and supersessions are `unknown:inferred:<kind>`. §9.26 says they never
    prove status; I did not count them as `none` either. **[Ambiguous]**
  - A negative treatment with `canChangeStatus=no` is a claim (T2). It is not admitted, but appears in
    `atRisk`.
  - With `canChangeStatus=unknown` the result is `unknown:power:<reason>`.
- **Supersession** (§7 AB1, schema `supersessions.tsv`).
  - The effect starts on asOf `enacted` (or `effective` when there is no enacted date), for conduct from
    `retroactive_to`, or else `effective`.
  - Issue `-` covers the node's admitted holdings whose `issues.usc` matches the law's `usc_block`, compared
    equal or by subsection prefix. If none match, it is `partialUnknown`.
  - Evidence `laterCourtSays:<tid>` needs that treatment's certificate to pass.
  - A `supersededByEnactment` *treatment* with no linked supersession row is `negative` for conduct from its
    date and `unknown:supersessionEffectiveUnknown` before that. Its asOf start is the treatment's date, so
    the recognising decision acts as evidence, the F14 analogue. **[Ambiguous]**
- **Effective dates.** A treatment's `date` column is used; if it is 0, the treating decision's date is used
  (TM1). F14 abrogations rely on `by_node` being the abrogating decision. A lower court that only
  *recognises* an abrogation has no power and lands in `atRisk:claim`.
- **R17 — Which kind and `by` to report.** When several effects are active, a `negative` wins over `unknown`,
  which wins over `none`. Among equals, the earliest start wins, then the kind order withdrawn,
  substitutedBy, vacated, depublished, rehearingEnBancGranted, reversed, overruled, recededFrom, disapproved,
  abrogated, supersededByEnactment, reviewGranted, then the lowest `by`. This affects only the `kind` and
  `by` columns.

### Certificates

These are written from SCHEMA's CERT definition and DESIGN layer 4. Checks run in this order, and the first
failure is the reason given.

1. `noDecision`: the owner node is missing.
2. `shaMismatch`: the cert's sha is not the owner's `text_sha`. The owner is: `by_node` for treatments (the
   by-decision states it itself); `node` for holdings; target or `by_node` for history.
3. `offsets`: `0 ≤ start < end` fails.
4. `quoteLength`: the normalised quote's length is not `end − start`. Normalisation: `\r\n`→`\n`, then tabs and
   newlines → spaces.
5. `noWindow` or `quoteMismatch`: no `cert_text.tsv` window for the sha covers `[start, end)` with
   `len(window) = end0 − start0`, or the window slice does not equal the quote.
6. `noVerb` (**R20**): the lower-cased quote contains no verb of the asserted kind. The verb list is
   `VERBS`, built from the §5 and T4 detection phrases. `followed` accepts follow, rely, adopt, "bound by",
   binding, controlling, "governed by", apply. History kind `other` needs no verb.
7. `noTarget` (**R21**).
   - `cite:<c>`: `c`, reduced to lower-case letters and digits, must occur in the quote reduced the same way.
     Whether the citation resolves to the target is not checked, because the fixtures use v1 node ids that
     do not match their citations.
   - `name:<tokens>`: **every** token must appear as a word in the quote. **[Ambiguous]** "All" rather than
     "any".
   - History certificates taken from the target's own text need no target. Holdings need none.
8. `part` (**R22**): `part` is not one of majority, plurality, perCuriam. A holding with a `role` outside those
   gives `role`.

**R19.** A holding whose certificate fails is not admitted. It gets no status block and is not used for
scopes, splits or `atRisk`.

### Splits (§9.24, DESIGN layer 5)

- Holdings qualify if they are admitted, answer yes or no, have an issue with a question, and are not
  plurality holdings without a *Marks* row.
- A pair of holdings with opposite answers, from different courts or different units of one court, is a
  split when all of these hold at `date = max(d1, d2)`:
  - both holdings have status `none` at `(date, date)`;
  - each decision's force on the other's court and unit is definite and below `bindingAbsentConflict`;
  - no good-law, non-trial holding on the question, dated on or before `date`, binds both courts. A later
    resolving holding does not remove the row; the row records when the split arose.
- Rows with an unknown force are not emitted.

### Findings (§9.27)

These come from citation edges `citing\tcited`, evaluated at `t = u = citing.date`. **[Ambiguous]** No
conduct date is available for the citing case, so its decision date stands in for it. A citing decision
that is itself the `by` of the event is skipped.

- **`citesOverruled`** (overruled, disapproved, recededFrom, abrogated), **`citesVacated`** (vacated,
  withdrawn, substitutedBy, depublished, en-banc-vacated) and **`appliesSupersededHolding`** follow the same
  coverage rule:
  - a whole-decision event (non-partial ⊤) is always a finding;
  - a partial event is a finding only if the citing decision has an admitted holding on an affected issue
    (`extra …:<issue>`), or the citing decision has no holdings and **every** holding of the cited decision
    is negative (`…:allHoldings`).

  Otherwise HD4 keeps the cited proposition good law. `reversed` produces no finding.
- **`citesUnpublishedAsBinding`**: an admitted `followed` treatment of a decision whose publication is
  non-published, where the decision's force on the citing court is definite and below `binding`.
- **`pluralityTreatedAsBinding`**: an admitted `followed` treatment of a `form=plurality` decision with no
  *Marks* rows, where the decision would have been `binding` on the citing court as a majority opinion.
- **`panelDepartsWithoutEnBanc`**: an admitted negative or `declinedToFollow` treatment by the same court, as
  holder, under `strong` or `withinUnitOnly` (same unit), with a panel or division bench (or circulated where
  circulation does not count), while the target is still `none`.
- **`atRisk`**, at the time of the treatment, while the target ⊤ is not negative:
  - `soft:<kind>`: an admitted limited, questioned, criticized or declinedToFollow treatment;
  - `claim:<kind>`: a negative treatment without power (T2);
  - `inferred:<kind>`: an `explicit=0` negative treatment;
  - `possiblySuperseded` (citing = `lc:<id>`): an `explicit=0` supersession;
  - `contraryBinding:<holding>`: for each holding, the earliest later contrary holding that binds its court
    (F14).

## Differential-testing harness

`gen.py` builds universes of courts covering these cases:

- SCOTUS; the 1st Cir.; a 2d Cir. created by a split with an adoption row (all and unitB); the Federal
  Circuit; districts; the Court of Federal Claims; the Tax Court;
- Maine, with a U-tagged `stateFollowsCircuit` row;
- California: Supreme Court, Court of Appeal with units, superior courts, an appellate division;
- a Kentucky-style epoch change with replace succession and self-adoption;
- Texas: dual courts of last resort and two courts of appeals.

Rules are random and dated, and tags are random S, L or U. Decisions have random bench, publication
(including unknown) and form (including plurality, equally divided and unknown). Each universe also has
issues of every domain, holdings (some plurality, some invalid roles), *Marks* rows, treatments of every
kind, scope and temporal value, same-case history aimed at overruling decisions (for revival), law changes
and supersessions (some via `laterCourtSays`), Golsen venues, and edges.

Every decision has a real text and sha, so certificates are genuinely checkable. About 15% of certificates
are corrupted (offset, sha, quote or target), and some carry dissent, concurrence or unknown parts. 40% of
treatments are drawn from scenario court pairs (`SCENARIOS`) so that named rules are exercised: H3, R6, F10,
horizontal rules, F1/F14/T2, H1/H2, F11 and F7.

The mutant self-test (`--mutants`) runs ten deliberately broken variants of the reference, selected with
`PREF_MUTANT`, in the spirit of DESIGN D3. Over 20 rounds of 120 decisions, `diff.py` caught every one: Erie
both ways in 15/20 rounds; panel overrules panel 9/20; ignore unpublished 20/20; ignore partial scope 18/20;
retroactive supersession 20/20; revival ignored 16/20; certificate accepts dissent 18/20; temporal scope
ignored 19/20; succession ignored 10/20; vacatur ignored 20/20.

## Episodes replayed against the real court tables

These ran against `data/courts2`, `succession`, `adoption` and `system_rules` as of 2026-11-12.

- Old Kentucky Court of Appeals (913) → new Court of Appeals (914): `binding`. → Supreme Court of Kentucky:
  not bound. The new Court of Appeals en banc cannot overrule the old court; the Supreme Court can.
- 5th Cir. 1975 → 11th Cir.: `binding` (*Bonner*). A Unit B decision after the split: `binding`. Unit A:
  `persuasive`. The 5th Cir. keeps pre-split law.
- 8th Cir. 1920 → 10th Cir.: `persuasive` (*McMorris*).
- D.C. Cir. 1965 → D.C. Court of Appeals in 1980: `binding`. A division of that court cannot overrule it; the
  court en banc can. D.C. Cir. 1975 → D.C. Court of Appeals: `persuasive` (*M.A.P. v. Ryan*).
- CCPA → Federal Circuit: `binding` (*South Corp.*).
- New Jersey Court of Errors and Appeals → the new Supreme Court of New Jersey: its own precedent, not bound.
- Fixtures:
  - Betts/Gideon and Bowers/Lawrence: overruled; findings `citesOverruled 17→2`.
  - The partial overruling in Georgia: only the notice holding.
  - Ledbetter: superseded for asOf ≥ 2009-01-29 and conduct ≥ 2007-05-28.
  - The 5th Cir. unpublished cut-off: `citesUnpublishedAsBinding 16→15`.
  - The *Auto Equity* split: `ca.clause 524/524`.
  - Two regex false positives rejected by certificate (`noTarget`; one also from a dissent).

## Revisions after differential testing (D4, 2026-11-12)

The Lean and this reference were diffed on the fixtures, on 15,000+ generated universes and on the real data
(caselaw-lean-2/DIFFTEST.md). Each disagreement was triaged as Lean wrong, reference wrong, doctrine ambiguous, or
data. Where the reference was wrong, or where an ambiguous reading was settled, the change is listed here. Each was
argued from doctrine.md, not from the Lean code. The same readings are in caselaw-lean-2/DEVIATIONS.md, items 30–53.
**These entries replace the earlier text of the R-numbers they name.**

### Reference errors fixed (triage b)

- **R25, same-case power (new).** §5.1A: a history event acts on the target's own judgment. It is admitted only if
  its deciding decision is the target's court, a successor court (H3), a higher court of its system that reviews it
  (federal: its own circuit, or the Federal Circuit, never the Court of Federal Claims), or SCOTUS. A deciding
  decision of unknown court or date is admitted, like `by = -1`.
- **R26, inferred rows (§9.26).** An `explicit = 0` treatment or supersession changes no status. It is `atRisk` only.
  It was `unknown:inferred`.
- **R10, SCOTUS on state law.** Persuasive everywhere. F1 binds "on federal questions only". It was binding on lower
  federal courts.
- **Power over a multi-issue treatment.** For ⊤, the treatment reaches ⊤ partially if the court has power over some
  named issue, each issue judged on its own domain. It was one domain for all the named issues, else `unknown`.
- **Restorers.** `reinstated` also closes `reversed` and an unknown en banc grant. Restorers now close
  `unknownScope:`/`otherGrounds:` effects of their kind.
- **Destination unit 0.** A destination unit of 0 means unknown, so the court's courts2 unit is used.
- **Lapse breakpoints.** The overruling decision's lapse dates are breakpoints of the target's timeline, even where its
  own reported kind does not change.
- **Panel departures.** Not made when the treating decision is earlier than its target (T1), or has power by another
  route (review, adoption).
- **Treatment findings.** Need the target not to be later than the treating decision.
- **Citation findings.** Issue-level findings apply whenever the whole decision is not wholly negative (partial or
  unknown). The self-citation test (the citing decision is itself the cause) looks at every live effect of the top
  severity, not only the reported one.
- **`atRisk possiblySuperseded`.** Not made when its `laterCourtSays` evidence fails its certificate.
- **`firm` (D2).** Judged as the same verdict (class and negative kind) at each row's first diagonal point. Status
  rows are cut where the firm timeline changes. A finding is firm when the firm tables produce the same finding (and,
  for atRisk, the same family; for citations, the same kind of status). It was row/tuple identity.

### Readings settled (triage c)

- **R1 (revised).** An unknown publication reads as published and an unknown form as a full opinion. They are named
  in the reason, not enumerated. An unknown issue domain is still enumerated, for force (`agree`) and for power. An
  unknown result now carries an upper bound (`upper`): "below binding under every reading" is decidable. Findings
  and splits use that bound.
- **R31 (new), power fallbacks.** An unknown bench is a panel. A missing `circulationCountsAsEnBanc` row means not en
  banc. A missing `horizontal` row requires en banc (as strong) for power; for force it is soft (`persuasiveStrong`).
  An appellate division over a trial court with an unknown unit has no power.
- **Missing `trialScope` row:** statewide (§4.3 majority rule). **Unknown unit under `ownUnit*`:** not the own unit.
  **Appellate division, unknown unit:** persuasive. **Tax Court with no case venue:** persuasive (a national special
  court). **E3 with no derivable state circuit:** persuasive.
- **R3 / HD6.** A majority or per curiam holding of a plurality decision binds. An equally divided decision caps at
  none whatever the holding's role. A `form=memorandum` decision caps at persuasive, separately from the publication
  table.
- **R12 (narrowed).** A state court's ruling on a third system's law binds the system's own lower courts (vertical
  stare decisis), as R13 does for federal law.
- **Pre-*Erie*.** Federal decisions on state law before 25 Apr 1938 are persuasive in federal courts, the deciding
  circuit included. A state high court's decision is persuasive in federal courts before *Erie*. It was `unknown`.
- **R14 (revised).** An unknown temporal scope is retroactive for state law too. Retroactivity is the general rule, and
  a prospective overruling must say so (TM2 detection).
- **R15 (revised), revival.** An overruling lapses while the overruling decision is withdrawn, substituted, vacated
  (including a vacating en banc grant), depublished, or reversed, each as a whole. It revives on reinstatement. A
  partial event, review granted, an unknown en banc rule, or the overruler being overruled leaves the overruling
  standing (T3: revival is not automatic). It was `unknown:revival:*`.
- **R16 (revised).** S-CA review granted is read only from the approved `reviewGrantedForce` system rule (DESIGN D9).
  Force ≤ notCitable gives `reviewGrantedDepublished`; otherwise `reviewGranted` (a persuasive cap). There is no
  name-based California default.
- **R17 (revised).** The reported kind is the most severe live effect, then the earliest start, then `KIND_ORDER`. A
  whole-decision effect is reported before a partial one.
- **R23 (revised).** A system-level `horizontal` row never applies to a court of last resort; only a court-level row
  does. The D.C. Court of Appeals' divisional rule needs a court-level row (data note).
- **R27 (new).** A `supersededByEnactment` treatment alone changes no status (no law change, so no dates or block). A
  supersessions row carries the event.
- **R28 (new).** History kind `other` has no verb, so it cannot be certified.
- **R29 (new).** `reversed` gives `citesVacated`: the reversed opinion lost force on the reversed issues.
- **R30 (new), `retroactive_to = 1`** (SCHEMA): the law governs cases pending on its effective date, whatever the
  conduct date. Pending-ness is not in the data, so it is **approximated** as known from the effective date
  (asOf t >= effective), for all conduct.
- **R32 (new).** On ⊤ any event, negative or unknown, that reaches only part of the decision is reported with the
  suffix `:partial`. An unknown whole-decision event outranks a partial one.
- **Findings.**
  - `citesUnpublishedAsBinding` uses the decision's own force (status excluded), below `bindingAbsentConflict` under
    every reading.
  - `pluralityTreatedAsBinding` needs `binding` as a majority opinion under every domain.
  - `panelDepartsWithoutEnBanc` covers status-changing kinds only, not `declinedToFollow`.
  - `atRisk` skips targets that are already wholly negative (a partial event leaves them at risk).
- **`splits_asof.tsv` (new output).** The splits that exist on the run's `--asof` date (default 20261112), by the same
  test as `splits.tsv`, with a bounded-unknown force counted when its bound is below `bindingAbsentConflict`.

### Comparison layer

- `diff.py` reads either side's format (Lean or reference) into one canonical form. `labels.json` is the label map.
- `gen.py --rounds N --ref --lean --diff` runs rounds 8 at a time with the compiled Lean runner and aggregates the
  canonical diff into `drt_diff.tsv`.
- `regress.py` runs the regression universes in `caselaw-lean-2/fixtures/regress/` and fails on any disagreement.
- `drt_show.py` prints one node of a universe for triage.
- **R24 (narrowed).** A `writRefused` notation promotes only a state intermediate court's opinion (S-TX). On a federal
  or other court it is a data error: it had given a circuit decision SCOTUS-like force.

### Real-data revisions (D4, 12 Nov evening)

- **R21 (revised again).** Target evidence may be in the quote or in any well-formed covering window. Names are
  whole words of at least 3 characters.
- **R20.** The cue table is the Lean's. **R33.** Phrase disqualifiers. Both tables are shared with the Lean.
- `holdings_cert_text.tsv` is read.
- **Same-case power.** A BAP reviews its circuit's bankruptcy courts. In the federal system only a court of appeals
  otherwise reviews (a bankruptcy court reviews no district court). A state special court is trial-level for
  vertical review and force.
- **Open:** the D.C. Court of Appeals' tier change (DEVIATIONS 60).

## Revisions: five limits (12 Nov, evening)

The reference now covers every finding kind the Lean defines except `inconsistentBindingBase` (Horty; no reference),
plus three optional SCHEMA files and the H4 / S-TX force rules. Each reading below is from doctrine.md (and SCHEMA /
COURTS.md); no Lean was read. Labels L1-L7 are cited in the code.

### New outputs and comparison keys

| Output | Format | Canonical key in `diff.py` |
|---|---|---|
| `findings.tsv` | `ignoresBindingInUnit, treating, target, <treatment kind>, firm` | `('ignoresBindingInUnit', treating, target)` (pair finding) |
| `findings.tsv` | `atRisk, citing, cited, citesLaterNegated:<status kind>, firm` | `('atRisk:citesLaterNegated', citing, cited)` |
| `findings.tsv` | `atRisk, source, subject, soft:<kind>` / `claim:<kind>` / `contraryBinding:<holding id>`, `firm` (unchanged) | `('atRisk:soft' / 'atRisk:claim' / 'atRisk:contraryBinding', source, subject)`; the kind or holding id is **not** in the key |
| `conflicts_asof.tsv` (new) | `issue, court, unit ('-' for 0), answers ('no,yes'), firm` | `('conflict', issue, court, unit)`; answers and firm compared |
| `certs.tsv` | new reason `windowHash` | labels.json reason `hash` |

The Lean's `conflict` rows in `splits.tsv` (court as `123` or `123/4`, unit 0 read as `-`) are compared with
`conflicts_asof.tsv` in a new `conflicts` file of the diff. The uncompared list is now only Lean
`inconsistentBindingBase` and the Lean's force-based `citesNotCitable`.

### Readings

- **L1, `ignoresBindingInUnit`** (§9.27 "a trial court departs from its own unit, ownUnit rules"; §4.1 V, §4.3,
  §4.4, T2). An admitted treatment (text certificate passed, target not later than the treating decision) of kind
  `declinedToFollow` or a status-changing kind (overruled, disapproved, recededFrom, abrogated), where:
  - the treating court is trial-level in a state system (tier T, S or D) and has no power over the target
    (`canChangeStatus = no`);
  - the target is good law on the diagonal at the treatment date (status `none` on the anonymous issue);
  - its force on the treating court and unit is `binding`;
  - and that force comes through the treating court's **own unit**: a holder of the target is an intermediate court
    of the same system and unit under `trialScope` `ownUnitThenAny` or `ownUnitOnly`, or an appellate division
    (tier D) of the same unit binding a trial court (§4.4, the "own court"). A `statewide` rule binds too, but not
    through the unit, so it is not this finding. An unknown unit (0 on the decision and on the court) is not the own
    unit.
- **L2, `atRisk citesLaterNegated`** (T1(c), §9.26, F14). Over the citation edges, C (decided t) cites X when:
  - X's anonymous issue is wholly negative on asOf (diagonal asOf = conduct) and not wholly negative on (t, t)
    (partial or unknown at t counts as "not negative");
  - and some live wholly negative effect on asOf comes from a decision B (not C) whose holding force on C's court
    and unit, at B's date, is `binding`.
  - A supersession (a law change) and a same-case event with an unknown deciding decision are not "a court that
    binds C". Only the anonymous issue is examined (no per-holding rows). The detail is the reported status kind.
- **L3, `conflict`** (§9.24 resolver, F7 conflict resolution, §4.1 V, S-CA *Auto Equity*, S-FL, S-NY).
  - Destinations follow the contract: each (court, unit) of a decision with a qualifying holding on the question
    issue, plus the first courts2.tsv row (file order) of tier T with the system (federal: also the circuit) of
    each holding decision's epoch, live on asOf, crossed with every unit among the holding decisions (0 = "no
    unit"; the force then uses the court's own unit, b6). Qualifying holdings are those of splits: admitted, yes/no,
    question issue, dated on or before asOf, plurality only with a Marks row.
  - Candidates: good-law holdings (status `none` at (asOf, asOf)) with force `binding` or `bindingAbsentConflict`
    on the destination. An unknown force whose bound may reach `bindingAbsentConflict` leaves the destination
    undecided: no row.
  - Resolver, in order: (1) **vertical hierarchy**: a candidate whose deciding court and unit another candidate
    binds, without being bound back, is displaced (SCOTUS over a state high court on federal law, a high court over
    its IAC); (2) a `binding` candidate displaces `bindingAbsentConflict` ones (own unit first, `ownUnitThenAny`);
    (3) **first in time**: among one source court's candidates, if its `firstInTimeControls` rule is 1 on asOf, only
    the earliest-dated stay; (4) the answers left are the permissible set. A row is written when it is {yes, no}.
  - **[Ambiguous]** Two binding holdings of one court of last resort that disagree, with no first-in-time row, give a
    conflict: doctrine gives no "last in time" rule, and a later contrary holding changes status only when admitted
    as a treatment (F14, §9.26).
  - The destination list is computed once (all tables) and evaluated by both rule instances; `firm` = the S/L-only
    tables produce the same row.
- **L4, commission opinions** (H4, §3.2 TX / MO / NY, COURTS.md `commission.tsv`, `adoption.tsv` 2927←2948).
  - With `commission.tsv` present, the adoption filters `opinionAdopted / holdingApproved / judgmentAdopted / none`
    are decided from the decision's notation (first row per node):
    - `opinionAdopted`, `opinionApproved` and `adoptedAsOpinionOfCourt` → `opinionAdopted` ("opinion approved"
      approves the whole opinion, reasoning and result, which is what "opinion adopted" carries);
    - `judgmentAdopted` → `judgmentAdopted`; `holdingApproved` (no such notation in the data yet) → `holdingApproved`;
    - no row → `none`;
    - `other` (a notation whose wording was not classified) → **unknown** (D5): the adopted route is `unknown`,
      bounded by the adopter's force. **[Ambiguous]**
    - Without the file every notation filter stays unknown, as before (R5).
  - The forces are the adoption rows': opinion adopted binding (Supreme Court authority), holding approved binding
    (the questions discussed are not separable in the data), judgment adopted `resultOnly`, none `persuasive`.
  - Commissioner opinions of other courts (CCA "opinion approved by the Court", Missouri "adopted as the opinion of
    the court", and Commission opinions filed under the Supreme Court of Texas's id) were filed as the court's own
    opinions: they keep the court's force whatever the notation, **except** `judgmentAdopted`, which caps any
    decision at `resultOnly` (H4: judgment only → resultOnly).
  - **`resultOnly` on the scale** (R3 kept): binding as to the result only, so for the question this model asks
    (does a holding's proposition bind a court) it is non-binding: ranked below `persuasiveStrong` and above
    `persuasive`, and so below `bindingAbsentConflict`. Every compared output (splits, conflicts, findings)
    thresholds at `bindingAbsentConflict` or `binding`, so there it behaves as `persuasive`, as the Lean's
    DEVIATIONS 5 folds it.
- **L5, Texas writ / petition notations** (S-TX "Supreme Court review notations", F3, §5.1 A). R24 is narrowed
  again. An admitted `writRefused` history row (decided by a court with same-case power, R25) promotes a decision to
  Supreme Court of Texas force (held by the civil court of last resort, from the notation's date, without power)
  only when all of these hold:
  - the decision is of a Texas intermediate court (tier A, system whose courts are named Texas); any other court,
    federal or state, gets nothing (the real data has Louisiana "writ refused" rows);
  - the notation's date is known; the era is keyed on it (the date the Supreme Court acted);
  - the quote's wording is a refusal, "writ ref'd / writ refused / writ of error refused" or "pet. ref'd / petition
    refused / petition for review refused", and is not n.r.e. / "no reversible error", denied, dismissed (incl.
    w.o.j.), or a PDR / "discretionary review" (criminal);
  - **writ wording dated before 1 Sept 1997**: the writ of error was civil, so the wording shows a civil case. Writ
    wording dated on or after that day promotes nothing;
  - **petition wording dated on or after 1 Sept 1997**, with the refusing decision a decision of the Supreme Court of
    Texas (the system's civil court of last resort). Civil is shown only that way, because criminal PDR refusals are
    also cited "pet. ref'd". Petition wording before 1997 is a criminal PDR refusal: nothing. With the refusing
    decision unknown (`by = -1`) petition wording promotes nothing;
  - a known refusing decision of any other court (the Court of Criminal Appeals, a court of appeals) promotes
    nothing in either era.
- **L6, citation index** (SCHEMA addition `cite_index.tsv`). When present, a `cite:<c>` target evidence also needs
  `index[compact(c)] == target node`. The index is built over compact keys (lowercase ASCII letters and digits); a
  key with two or more distinct nodes is ambiguous and resolves to nothing. Failure reason `noTarget`. History quotes
  from the target's own text stay exempt; `name:` evidence is unchanged; absent file → old rule.
- **L7, window hashes** (SCHEMA addition `window_sha.tsv`). When present, a window from `cert_text.tsv` or
  `holdings_cert_text.tsv` is usable (for the quote check and for target-evidence context) only if a row with its
  (text_sha, start0, end0) exists and `sha1(window as stored, UTF-8)` equals its sha1hex (any row of that key).
  Rejection order: `noWindow` (no covering window at all), then `windowHash` (a well-formed covering window exists
  but none is hash-consistent), then `quoteMismatch`. Holdings use the same rule.

### Generator and harness

- `gen.py` draws everything new from a second `random.Random(seed * 1000003 + 977)` and only **appends** courts,
  rules, adoption rows, decisions (node ids after the old ones), rows, edges and files. The original stream is
  consumed exactly as before:
  - `gen.py --legacy` reproduces old universes byte for byte (checked on 4 seeds against the old generator);
  - without `--legacy`, every old file's rows are an unchanged prefix and every old edge is kept. The optional files
    (cite index, window hashes) can change the certificate verdicts of old rows; that is the coverage they add.
- The layer adds:
  - the Texas Commission of Appeals (2948) with adoption rows 701←2948 (701 is the generator's Supreme Court of
    Texas; the four filters, tagged S/U/U/U as in data/adoption.tsv);
  - Missouri (801, 802) and Florida (901 L, 902 DCA with units, 903 trial) courts and rules;
  - `commission.tsv` (85% of universes) with every notation, on 2948, CCA, Missouri and Texas Supreme Court decisions;
  - Texas writ/petition rows with every wording, both eras, refused by the Supreme Court, the CCA or unknown, on
    Texas and non-Texas targets;
  - FL, CA and TX question holdings with intra-court disagreement;
  - trial courts declining or purporting to overrule own-unit precedent, and claims by courts without power;
  - later negations of cited decisions by binding courts, and contrary later binding holdings;
  - `cite_index.tsv` (75%: 85% right, 5% wrong target, 10% missing, 5% compact-collision variants) and
    `window_sha.tsv` (67%: 90% right, 5% corrupted, 5% missing).
- `gen.py --jobs` goes up to 16. `run_lean` falls back to `lake env lean --run LegalProofs/CaseLaw2/Run.lean` (cwd
  lean-proofs) when the compiled runner cannot be launched (OSError, e.g. Application Control) or with
  `CASELAW2_INTERP=1`; `build_lean` warns instead of failing.
- `regress.py --ref-only` runs the reference alone over the regression set; `regress.py --seeds ... --legacy` adds
  universes from the pre-layer generator.
- `fixtures/regress/gen120-30984` (seed 30984, n = 120, old generator) is the DIFFTEST §4 firm residual. Decision 37
  is wholly vacated under all tables by a rehearing en banc grant whose `enBancGrantVacatesPanel` row (court -502) is
  U-tagged; under the S/L tables only its single holding is vacated; decisions 76 and 105 cite it.
- Checks run (reference only, no Lean):
  - 300 universes (n = 60) and 100 (n = 120) with the layer: no exceptions;
  - the regression set (111 universes): clean;
  - a Lean-format round trip of the reference outputs through `diff.py`: 0 disagreements over 7,506 keys
    (105 conflict keys); an injected conflict firm flip is caught.

## Revisions after the five-limits differential run (coordinator, 2026-11-12)

Triage of the first generated sweeps (seeds 50000-50299) against the Lean; each is a reference change (b) or a
reading now shared with the Lean (c, DEVIATIONS 61-67):
- (b) `at_risk`: soft and claim rows only when the target is not later than the treating decision (T1: a data error,
  not a risk), as panel departures already did.
- (b) Conflicts, `_resolve.binds`: a decision held by binding adoption is displaced only by a holding that also binds
  its adopter (an adopted Commission of Appeals opinion is the Supreme Court of Texas's, H4); a court whose tier
  changed does not bind its own decisions from a higher dated tier (H3, Kentucky 1976).
- (b) `ignoresBindingInUnit`: a decision promoted by a writ/petition notation binds as the court of last resort's, not
  through the unit rule.
- (c) `rel`: a special court (tier S: the Tax Court, a state special court such as the Commission of Appeals)
  follows its own precedent as persuasiveStrong (`F12.self`), not under its system's horizontal rule.
- (c) `notation_filter`: no `commission.tsv`, or an unclassified notation, reads as `none`: an adoption that is not
  shown is no adoption (L4 revised).

## Revisions: hunt fixes (H2, H3b, H4) and real-data triage (b1, b2)

Each change is marked in `precedent_ref.py` with its tag. `status.tsv`, splits and conflicts are computed as before
(H4 changes citation findings only; b1 and b2 change force and power where they apply).

- **b1, domain candidates** (`authority`, `can_change`). With an unknown issue domain the candidate domains (and
  circuits) come from the holders whose `via != 'adoption'` plus the destination / treating court. An adopter's
  system is no longer a candidate. A `writRefused` holder is not an adoption holder and still counts (its system is
  the decision's own).
- **b2, F11b.reach** (`rel`). A Federal Circuit source binds by reach only a circuit-13 destination whose tier is in
  `FED_LOWER`. A circuit-13 appellate destination other than the source court falls through to
  `persuasive, F7.otherCircuit`.
- **H3b, `panelDepartsWithoutEnBanc`** (`_panel_departs`). Emitted only when the treating bench is `panel` or
  `division` (never `unknown` or `circulated`, whatever `circulationCountsAsEnBanc` says), and the treating court's
  own horizontal rule on the treating date, `horizontal(be.system, court(B), be.tier, bd)`, is `strong` or
  `withinUnitOnly`, in addition to the rule keyed on the precedent's date. A missing row at either date: no finding.
  `power`, `bench_ok` and `can_change` are unchanged.
- **H2, superseded holdings** (`_finding_kind`, `_edge_findings`, `_sup_effects`). SCHEMA has no conduct date for a
  citing decision, so `appliesSupersededHolding` is never emitted. `_finding_kind('supersededByEnactment')` is None.
  A whole decision whose top status on (t, t) is wholly superseded falls through to the holdings, for the new row
  only; every other whole-decision kind returns early as before.
  New row `('atRisk', C, X, 'supersededConductUnknown:' + issue key)`, once per (C, X, issue key), for each admitted
  holding `h` of X whose status on (t, t) is negative with kind `supersededByEnactment`, when C has an admitted
  holding on `h`'s issue, or on an issue whose `usc` matches (`_usc_match`) the `usc_block` of a supersession row on X
  that is explicit, admitted, live on (t, t) and reaches `h`'s issue. The "no holdings in C, all cited holdings
  negative" fallback does not apply to it. Section C of `effects` moved to `_sup_effects` so both use one rule.
  Readings: "reaches" means the row's effect on the keyset {h's issue} is `negative supersededByEnactment` (scope
  `full`; an unknown-scope row does not count); the status is the one relative to C (H4), so a holding that is also
  overruled for C's line reports the overruling, not this row.
- **H4, status per heir after an adoption cut-off.** Treatment effects carry a reach (9th element of the effect row;
  history and supersession effects have none = ALL).
  - `_heirs(X)`: adoption rows whose source is X's own court (no succession walk), `date(X) <= up_to`, force exactly
    `binding`, adopter != X's court, and filter `all` / `-` / empty, or `unitB` with X's unit 2. Any other filter is
    never an heir.
  - `_reach(X, B, bd)`: as specified; `bd` is the treatment's date (the row's date, else B's). ALL when there are no
    heirs, an epoch is missing, B's court is SCOTUS, or the original line and every heir are reached.
  - `_applies(reach, Ce, t)`: Ce is the citing court's epoch at the citing date; a citing date of 0 or no epoch:
    applies. Tier ranks are `TIER_RANK`.
  - `status_citing(C, X, holding, t, u)`: when every effect of X applies to C it is the global status; otherwise
    `_eval` over the applicable effects at the point (t, u) (the same value a timeline of those effects would give).
    Used for every status the citation-edge code asks: `_edge_findings` (whole decision, holdings, `_only_by`),
    `_cites_later_negated` (asOf, (t, t), `_live_negative_citing`) and the H2 status. The filtered effects are not
    cached per citing decision; X's unfiltered effects are cached under `('effs', X, keyset)` for decisions with heirs.
  - A two-row adopter (102 <- 101 `all` to the cut-off and `unitB` open) can be in both the reached and the unreached
    set; the reached row wins, as the applicability formula reads.
  - The firm flag of a citation finding can change: the firm engine has its own adoption rows, so its heirs differ.

### Generator

`gen.py` has a third stream, `random.Random(seed * 1000003 + 1979)` (`hunt_layer`), appended after the five-limits
layer. Treatments and holdings sit only in its own new decisions.
- Courts: D.C. Circuit 1101 (circuit 12), its district court 1104, D.C. Court of Appeals 1102 (system 51, L), Superior
  Court 1103, Supreme Court of Ohio 1001, Court of Appeals of Ohio 1002 (system 36).
- Adoption: 1102 <- 1101 `all` `binding` to a drawn cut-off; sometimes a non-heir row (`issue:localLaw` or `unitA`,
  open) and a `persuasive` row (1001 <- 1101).
- Rules: system 36 horizontal `strong` / `withinUnitOnly` from d1 to d2 - 1 (nothing before d1), sometimes another
  value from d2; sometimes `circulationCountsAsEnBanc` on -1002; sometimes a dated court-level horizontal row on -1101.
- H4: for 101 -> 102 and 1101 -> 1102, a source-court decision before the cut-off, an explicit overruling by the
  source court (after, sometimes before, the cut-off), the adopter or SCOTUS, then citing decisions from the source
  court and its district court, the adopter and its lower court, an outside court, and two dated before the treatment.
- H3b: Ohio and D.C. Circuit decisions overruled by the same court, benches panel / division / unknown / circulated /
  enBanc, dates on both sides of the rule dates.
- H2: issues `fed.c` (usc `42:2000e-5(e)(1)`) and `fed.d` (usc `42:1983`); explicit (85%) supersession rows on new
  decisions holding `fed.a` / `fed.b`, issue named or `-`; citing decisions before and after the law change holding
  the same issue, `fed.c` / `fed.d`, an unrelated issue, or nothing.
- Old seeds: `--legacy` and the new `--no-hunt` (`generate(..., hunt=False)`) reproduce the earlier universes byte for
  byte (6 seeds checked against the previous `gen.py`). By default every earlier file's rows are an unchanged prefix
  and every earlier edge is kept.

### Self-check (reference before and after, no Lean)

- `fixtures/` and the 111 regression universes: only `findings.tsv` differs, in 60 universes. Removed: 93
  `appliesSupersededHolding`, 14 `panelDepartsWithoutEnBanc` (8 circulated, 4 unknown, 1 division and 1 panel with no
  binding rule on the treating date), 3 `citesOverruled` (H4). Added: 20 `atRisk supersededConductUnknown`.
- 200 generated universes (seeds 60000-60199, n = 60, hunt layer on): only `findings.tsv` differs. Removed: 674
  `appliesSupersededHolding`, 764 `citesOverruled` (H4), 196 `panelDepartsWithoutEnBanc` (81 unknown, 70 circulated,
  27 panel, 18 division), 23 `citesLaterNegated` (H4). Added: 475 `supersededConductUnknown`, 12 `citesLaterNegated`
  (b1: the negating decision now binds the citing court). Firm flag only (1 to 0): 4 `citesOverruled`, 4
  `panelDepartsWithoutEnBanc`.

### After the WSL real-data run (12 Nov, real15)

- **b3, `same_case_power`.** A state special court (tier S) reviews no court: it is trial-level for review as it is
  for force. The real row was a New York Surrogate's Court "vacating" a decision of the New York Supreme Court (the
  general trial court); the reference admitted it because `TIER_RANK` puts S above T. Lean was right.
- **H3b, federal courts of appeals.** `EN_BANC_STATUTE = 19480901` (28 U.S.C. § 46(c)): a panel of a federal court
  of appeals deciding before that date makes no `panelDepartsWithoutEnBanc` row (no en banc procedure to go to). The
  same constant is in the Lean (`enBancStatuteDate`). Ohio and Louisiana are dated in `system_rules.tsv`
  (`tools/caselaw2/rule_dates_fix.py`).
- **gen.py.** `day_after`: the hunt layer stepped a cut-off with `+ 1`, which is not a date at a month end.

- **b4, conflict displacement** (`_resolve`). "A decision held by binding adoption is displaced only by a holding
  that also binds its adopter" now counts only an adopter in whose line the destination court stands (the adopter
  itself or a court below it, H4's line test). At a court outside that line the adoption is not what the decision's
  force rests on: at the D.C. federal district court a later California Supreme Court holding displaces a D.C.
  Circuit reading of California law, although it does not bind the D.C. Court of Appeals, which adopted that
  decision. The Lean has the same change. Found by the hunt-layer sweep (seeds 52060 ff.).
- **H6 for adopted decisions** (`rel`, `power`, `_panel_departs`). For a decision a court of last resort holds by
  adoption, the court-level (divisional) horizontal row is keyed on the question or treating date, not on the
  precedent's date: *M.A.P. v. Ryan* binds the divisions to pre-1971 D.C. Circuit decisions, which a row dated 1971
  does not cover by their own dates. With no such row the court is free at any bench (H1), which the Lean now
  follows too (it had asked for an en banc bench).

## Revisions: round 2 (per-line status everywhere)

Written from DEVIATIONS 73-79 only. Tags `R2-73` ... `R2-78` mark the code.

### Implemented

- **R2-73** (`holders`). A `split` succession row passes nothing: the new court is not pushed as a holder, in either
  run. Rename, replace and absorb are unchanged.
- **R2-74** (`_view`, `_in_view`, `_applies`, `_view_effects`, `status_view`). A view is `None` (date 0 or no epoch:
  every effect reaches), a court epoch with a date, or a frozenset of adopter ids for a pure view. `_reach` is
  unchanged from H4.
- **R2-75** (`line_views`, `timeline_view`, `line_rows`, `firm_of_line`). `status_lines.tsv`. `timeline` now calls
  `_segments`, which the per-view timelines share.
- **R2-76**. `_panel_departs`, `_ignores_binding_in_unit`, `at_risk` (soft, claim, inferred) read the target in the
  treating decision's view; `contraryBinding` reads X and Y in the view of X's court on Y's date.
- **R2-77**. `conflicts_at` reads good law in the view of the bound court on asOf. `_split_pair` and `_resolved` read
  the views of the two courts. `splits.tsv` (history dates) uses the same test at each candidate date, so it is
  consistent with `splits_asof.tsv`.
- **R2-78** (`horty`). Binding bases only; no self bases and no findings rows.
- `diff.py`: files `lines` and `horty`; either is skipped silently when one side lacks the file.
- `gen.py`: `lines_layer`, stream `random.Random(seed * 1000003 + 2026)`, after the hunt layer and only with it;
  `--no-lines` / `generate(..., lines=False)`. `LEAN_HEADERS` has `status_lines` and `horty`; `drt.py` `FILES` too.
- Debug switch `PREF_UNION_VIEWS=1`: every effect reaches every view. For self-tests only.

### Readings chosen where 73-79 were open

1. **73, old court gone** (revised after the first sweep). A split passes nothing on, so a court whose only
   successors are splits stays a holder of its own decisions (via own, with its dated tier), whether or not it still
   has an epoch on the question date, exactly as a court with no successor does. Adoption rows add adopters as
   before. After a rename, replace or absorb the successor holds instead, as before. The deciding court's own system
   and circuit (its epoch on the decision's date) are candidate domains for an unknown issue domain in `authority`
   and `can_change` (b1).
2. **73, adoption sources.** A split successor is not a court the decision "passed through", so an adoption row whose
   source is the split successor does not cover the old court's decisions.
3. **74, line-limited.** A reach whose original line and every heir are reached is `all` (as in H4). A decision whose
   only reaches are of that form has no `status_lines.tsv` rows. If the Lean keeps `lines(true, heirs, [])` as
   line-limited it will write blocks equal to the union status, which the diff reports as `lines` disagreements.
4. **75, which effects.** "Has a line-limited effect" and the adopter list are taken over the effects of the
   anonymous issue and of each admitted holding.
5. **76, dates.** The view is of the treating court on the treating decision's date; the status point stays the
   treatment row's date (else the decision's). The two dates are equal on every real row and every generated row.
6. **77, "force is known".** In the new disjunct a force is known when its label is definite. A bounded unknown below
   bindingAbsentConflict still counts as not binding (as before); any other unknown blocks the split.
7. **78, force.** A case is in a base only when its force label is definite and at least bindingAbsentConflict. The
   force is the holding's own (`authority` on the holding's issue and role, not the family key), status excluded.
8. **78, input rows.** `factors.tsv` needs exactly 4 columns and `factor_cases.tsv` exactly 11; no numeric checks.
   Factor ids compare as strings. `inReason` is true only for `1`; a side other than `pi` is delta.
9. **78, no plurality filter.** Every admitted holding with factor rows is a case, whatever its role.
10. **78, examined court without an epoch on asOf.** View unknown (union status) and force unknown: no base.

### Generator layer

Courts: Fifth Circuit 1201 (ends at the cut-off in half the universes; sometimes starts in 1920), Eleventh Circuit
1202 (starts the day after), districts 1203 and 1204, sometimes a successor 1205 (replace or split); in 60% an
Alabama-style division 1221 -> 1222 and 1225 with one trial court 1223 and supreme court 1224. Per source/adopter
group (101/102, 1101/1102, 1201/1202, 1221): one or two pre-cut-off source holdings on a federal question issue
(often opposite answers), one or two certified explicit en banc overrulings (source after or before the cut-off, an
adopter, SCOTUS, the state supreme court), post-cut-off holdings by the source, adopters and both lower courts, soft
and inferred treatments, claims and panel departures from each line, sometimes a later SCOTUS contrary holding,
decisions dated outside their court's epoch (citing, treating, target), and `factors.tsv` / `factor_cases.tsv` rows
(own issue or family key; replaced, ignored and flipped rows).

### Self-check (reference only)

- `--no-lines` against the previous `gen.py`: byte-identical on 8 seeds at n = 60 and 120; with the layer on every
  earlier file is an unchanged prefix.
- Fixtures (before the per-line fixture case was added) and the 111 regression universes, before and after:
  `status.tsv`, findings, certs, `splits_asof.tsv` and conflicts identical. One row differs: `gen-114` `splits.tsv`,
  split `tx.a 101/102` dated 19810726 instead of 19930703 (the 1925 First Circuit holding was abrogated in the Second
  Circuit's line only, so it still stands for the First Circuit). 19 universes have `status_lines.tsv` rows.
- 200 universes (seeds 60000-60199): no exceptions. Non-empty `status_lines.tsv` in 198; a Horty family with more than
  one base in 110; against `PREF_UNION_VIEWS=1`: splits differ in 47, conflicts in 40, Horty in 100, findings in 194;
  `status.tsv` never. "Original court gone" fired in 64 universes, a treating decision outside its epoch in 116, a
  target outside its epoch in 16.
- `diff.py`: identical directories exit 0; a flipped Horty verdict and a removed line row are each reported; a
  Lean-format rendering of the reference's two files gives 0 disagreements over 1,637 line keys and 550 Horty keys.
- Real data without edges: 105 `status_lines.tsv` rows for 41 decisions; 44 Horty bases, 43 consistent, 1
  inconsistent (`horty:preemption_express`).
