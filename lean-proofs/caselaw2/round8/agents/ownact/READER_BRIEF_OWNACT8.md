# Reader brief, round 8: does the deciding court itself, now, overrule (or take the authority of) a named earlier case?

You read sentences from US court opinions. For each ITEM decide one thing: whether, in the FOCUS sentence, **the
deciding court itself, now, in its own opinion of the court, overrules, disapproves, recedes from, abrogates, or
otherwise takes away the authority of one or more listed earlier judicial decisions**, and which ones.

Most items are NOT such acts (procedural rulings, reports of what other courts or statutes did, quotations,
arguments, dissents). Earlier versions of this task failed their audits on one kind of error above all: sentences
like "X is no longer good law / no longer the law / cannot survive" where the reason was **a statute, an amendment, a
rule change, or another decision** — the court was *reporting* X's status, not acting on X. **When in doubt, answer
no.** A wrong yes costs far more than a wrong no.

## The pack

Your pack file (`packs8/pack_NNN.md`) holds about 80 ITEMS. Each item has:

- `### ITEM <id>`
- `ACTING:` the deciding decision (name, citation, court, year), a machine label of the opinion part, and the
  opinion section heading the sentence sits in (e.g. "Majority (HALL, Justice.)", "Dissent (BLACK, J.)").
- `TARGETS:` `T1`, `T2`, ... earlier decisions found near the sentence: name, court, year, citation, **how the text
  names it** (`cite "<citation key>"` or `name "<word(s)>"`), and where: `in act` (inside the FOCUS sentence),
  `before (gap N)` (named N characters before the FOCUS sentence starts), `after`.
- `WINDOW:` opinion text around the sentence. The FOCUS sentence stands between `⟦` and `⟧`; each listed decision's
  naming is followed by a mark `[T1]`, `[T2]`, ... The marks `⟦ ⟧ [Tk]` are **not** part of the opinion.
- `FOCUS:` the sentence again, without marks. (Sentence splitting is by machine: the FOCUS may be a fragment or run
  over two sentences; judge the act sentence it contains.)

Judge from the item's own text only. Do not use what you know about the cases, do not look anything up, do not open
any other file of the project (in particular nothing under `gold/`, `round5/gold_fresh/`, `round5/tests/`,
`round6/shepardized/`, `round6/history/split/`, `round7/heldout/`, `events_v3/`, `eval/`, `benchmarks/`), and do
not call any external model or web service. Read only this brief and your own pack files; write only your answer
files. Judge every item yourself by reading it: no script, regex or keyword rule may classify items (a script may
only write your answers and check the JSON and the count).

## The test: `own_act: true` only if ALL FIVE hold

### 1. An act word, as this court's present act

The FOCUS sentence carries one of:

- **overrule family** (`kind` = the verb's word): "we overrule X", "X is (hereby) overruled", "X should be, and is,
  overruled", "X must be (regarded / considered) as overruled" (said by this court of the effect of ITS OWN present
  decision), "our decision today overrules X", "we are constrained to overrule X", "to the extent X holds otherwise,
  it is overruled" → `overruled`; "X is disapproved", "we disapprove X" → `disapproved`; "we recede from X" →
  `recededFrom`; "we abrogate X", "X is abrogated" → `abrogated`.
- **strong other verbs** (`kind: "rejected"`): "we reject / repudiate / disavow / discard / abandon / overturn X (or
  X's holding, rule, language, reasoning, dictum)", "X ... is rejected / repudiated / disavowed", "X was wrongly
  decided" as this court's own present conclusion (and the court does not go on to keep X under stare decisis).
- **follow verbs** (`kind: "rejected"`): "X should not be / will no longer be / is not to be followed", "we decline
  to follow X", "we no longer adhere to X" — **only** with a conflict phrase tying it to this court's present holding
  ("to the extent X is inconsistent with this opinion / our holding today", "insofar as X holds otherwise") or an
  explicit statement that X was wrong. "We decline to follow X" after calling X distinguishable, inapposite or decided
  on other facts, or "we decline to follow X" about a court whose decisions simply do not bind this court (another
  state, a coordinate court) with no statement that X is wrong, is **no**.
- **state words** (`kind: "rejected"`, or `overruled` if the sentence also says overruled): "X is no longer the law /
  good law / authoritative / controlling", "X can no longer be regarded as authority", "X cannot survive", "X has no
  place": **only** when test 3 (cause) passes **and** the court makes the declaration now, with an own-act marker in
  the sentence or the clause before it ("we hold", "we conclude", "we now declare", "we are of the opinion", "hereby",
  "today", "in light of our holding", "to the extent inconsistent with this opinion", "therefore" when what comes
  before is this court's own reasoning). A bare present-tense report — "X is no longer the law in this state", "X is
  no longer good law", "the X ruling is no longer followed" — is **no**.

Not acts (answer no): reports of a past act ("X was overruled in Y", "in Y we overruled X", "we have since repudiated
X", "X, overruled on other grounds by Y", "(overruling X)", "X has been abrogated", "X must be regarded as overruled
by our later cases"); refusals and doubts ("we decline to overrule X", "we need not decide whether X survives", "if X
holds otherwise it would have to be overruled", "we do not overrule X", "it is unnecessary to overrule"); questions,
hypotheses, conditions ("X would not survive", "whether X is still good law"); "we limit / narrow / question /
criticise / explain / distinguish / decline to extend X" (these do not take X's authority away); "X is
distinguishable", "X is no authority for the present case", "X does not control here".

### 2. Not procedural

"overruled" is very often procedural. **No** when the thing overruled / rejected is an objection, motion, demurrer,
exception, plea, petition, assignment / point of error, ground, issue, complaint, contention, argument, request,
claim, the trial court's ruling or judgment in this same case, a verdict, a conviction, evidence, or testimony.

### 3. Object: an earlier judicial decision in the TARGETS list (or its own holding, rule, language, dictum)

The grammatical object (active voice) or subject (passive voice, state words) must be a listed earlier decision, or
something **of or in** it ("any language in Smith", "the rule of Smith", "the holding of Smith that ...", "Smith's
reasoning", "so far as Smith holds otherwise, it ..."), or a pointing phrase ("that case", "those cases", "these
decisions", "it", "they", "said case", "the cases cited") that plainly points to listed decisions named just before.

**No** when the object is: a statute, regulation, rule of court, ordinance, contract, instruction; a party's argument,
premise, reading or reliance (even one built on the case: "we reject the State's reading of Smith"); a reading of the
case by others ("to the extent Smith has been read as ...", "Smith as construed by the court below"); a doctrine or
"line of cases" not tied to a listed decision; a decision the sentence names only as the authority for the act or as
the case the overruled one conflicts with ("in light of Gideon, Betts is overruled": the target is Betts, not Gideon);
a case named only as followed, quoted or cited for support; a lower-court decision in this very case. If the
decision acted on is not listed, or you cannot tell which listed decision it is, answer no.

### 4. Cause: this opinion's own act

Read the FOCUS sentence, the rest of its paragraph and the text before it, and find the **reason** the earlier case
loses authority. **No** when the reason is a statute, amendment, code, enactment, repeal, constitutional amendment,
"the legislature", a change of court rules ("since the adoption of the Rules of Civil Procedure"), **another decision**
of this or any court, earlier or recent ("X is no longer good law after Y", "since Y", "in light of the Supreme
Court's decision in Y", "X was repudiated in Y ... X is therefore no longer the law", an intervening Supreme Court
decision that a lower court applies to its own old precedent), or anything else outside this opinion (a treatise, the
trend of authority). Yes only when the act is this opinion's own: the sentence itself is the act ("we overrule",
"is hereby overruled", "we reject", "is disapproved"), or the reason is this court's reasoning in this opinion. When
the court overrules or rejects with a strong verb of its own *and* mentions a supporting change ("we now expressly
overrule X; later cases had already eroded it"), that is still its own act. A state word ("is no longer the law")
with any outside reason is **no**.

### 5. Voice and part: the opinion of the court, in its own words

**No** when the sentence sits in a dissent, a concurrence, a separate statement, a syllabus / headnote / reporter's
summary, counsel's argument (look at the section heading, "dissenting", "concurring", "I would", "Held:",
"Syllabus", "Counsel for"); is a quotation of another opinion or of a brief (inside quotation marks, or introduced by
"as we said in", "the court stated"); or describes what another court, a party, the court below or the dissent says.

## The fields

One JSON object per item, in pack order, every item exactly once:

    {"id": "6605515:8668", "own_act": true, "targets": ["T1"], "kind": "overruled", "verb": "overrule",
     "scope": "partialUnknown", "quote": "to the extent that Smith v. Jones, 125 Tex. 577, holds otherwise, it is overruled",
     "naming": {}, "cause": "own", "confidence": 0.9, "reason": "court's own act on Smith, limited by 'to the extent'"}

- `id`: the text after `### ITEM `.
- `own_act`: true only if tests 1-5 all hold.
- `targets`: when `own_act` is true, the T-ids of **every** listed decision the act sentence acts on (a sentence that
  overrules several named cases gets each of them; a companion case named with the overruled case is a target too).
  Leave out decisions named only as authority, as followed, as quoted, or as later history (", aff'd", "rev'd on
  other grounds") unless the act plainly reaches them. When `own_act` is false: `[]`.
- `kind`: `overruled` | `disapproved` | `recededFrom` | `abrogated` (the verb of that family is in your quote) |
  `rejected` (strong other verbs, follow verbs, state words: no overrule-family verb in the act clause) | `none`
  (when `own_act` is false).
- `kinds` (optional): when one sentence uses different act verbs for different targets ("we overrule Wright and
  disapprove Wolff"), `kind` is the first target's and `kinds` gives the others: `{"T2": "disapproved"}`.
- `verb`: the act word as it stands, lower-case and short: "overrule", "disapprove", "recede", "abrogate", "reject",
  "repudiate", "disavow", "abandon", "overturn", "discard", "wrongly decided", "not be followed", "decline to follow",
  "no longer good law", "no longer the law", "no longer authority", "cannot survive", ... ("" when false).
- `scope`: `all` **only** when the act is on the whole of each chosen case with no limiting phrase anywhere in the act
  sentence; any limiting phrase gives `partialUnknown`: "to the extent", "insofar as", "in so far as", "so far as",
  "in part", "on this point / issue", "on other grounds", "as to", "in the field of", "to that extent", "pro tanto",
  "insofar as inconsistent with this opinion", "any language", "the language of", "the dictum in", "the holding
  that ...", "the rule announced in", "in that respect". An act on X's language, holding, rule, reasoning or dictum is
  always `partialUnknown`. `kind: "rejected"` is always `partialUnknown`.
- `quote` (own_act true; else ""): copy EXACTLY, character for character (odd spacing, OCR errors, punctuation), one
  contiguous span **of the FOCUS sentence**, at most 400 characters, holding the act word, any limiting words, and —
  when the target is named in the FOCUS sentence — the target's naming exactly as the TARGETS line gives it (the
  citation, e.g. `125 Tex. 577` for `cite "125 tex 577"`, or every name word, e.g. `Bowen` for `name "Bowen"`, as
  whole words). With several targets named in the sentence, the quote must hold every chosen target's naming. Leave
  out the marks `⟦ ⟧ [Tk]`. The checker refuses a quote holding any of: `point of error`, `assignment of error`,
  `issue is overruled`, `overrule appellant`, `overrule his `, `complaint is overruled`, `overruled by`,
  `overruled on other grounds by`, `abrogated by`, `disapproved by`, `receded from by`, `as stated in`,
  `as recognized in`, `decline to overrule`, `not overrule`, `would overrule`, `should not be overruled`,
  `urges us to overrule`, `asks us to overrule`; and for `kind: "rejected"` also: `argument`, `contention`, `contend`,
  ` claim`, `suggestion`, `invitation`, ` request`, ` motion`, `petition`, `objection`, `evidence`, `testimony`,
  `urges`, `asks us`, `would reject`, `not reject`, `need not`, ` reading of`, `reliance on`, `assertion`, `whether`,
  `we rejected`, `court rejected`, `rejected in`, `rejected by`, `repudiated in`, `repudiated by`, `abandoned in`,
  `abandoned by`, `overturned by`, `overturned in`, `has been rejected`, `was rejected`, `has been repudiated`,
  `was repudiated`, `has been abandoned`, `was abandoned`, `did not survive`. Cut the quote to the clause that
  carries the act (and the name); if the act cannot be quoted without such a phrase it is usually not an act on the
  case — answer no rather than force a quote.
- `naming`: normally `{}`. Fill it only when the act sentence does **not** name a chosen target and points to it with
  a pointing phrase ("that case is overruled", "those cases are disapproved", "it is overruled", "to the extent they
  hold otherwise, they are overruled"): then give, for that target, the exact text (copied from the WINDOW, no marks)
  of the sentence or clause just before that names it with its citation or name words: `{"T2": "<exact text>"}`. It
  must end at most 300 characters before the FOCUS sentence starts and hold no dissent / argument words. It must
  hold the target's naming exactly as its TARGETS line gives it (the citation or the name word(s)); a bare "Id. at
  517" or "supra" without that naming does not do. Only for
  the overrule family (`overruled`, `disapproved`, `recededFrom`, `abrogated`); a `rejected` act must name its target
  in the quote itself.
- `cause`: `own` | `statute` | `rule` | `decision` | `none` | `unclear` (test 4). `own_act` true requires `own`.
- `confidence`: 0 to 1, your probability that own_act, targets and kind are all right.
- `reason`: at most 25 words: for a yes, the act and its object (and any limit); for a no, the failing test
  ("procedural: objection", "report of Y's act", "cause: statute", "dissent", "quotation", "target not listed").

## Short examples (described, not to be matched)

- "The case of Flowers v Bitting, 45 Ala. 448, is in conflict with the views we have expressed, and on the point we
  have considered, is overruled." → yes, `overruled`, `partialUnknown` ("on the point"), quote holds `45 Ala. 448`.
- "Appellant's first point of error is overruled." → no (procedural).
- "Smith v. Jones, 12 F.2d 3 (5th Cir. 1950), overruled on other grounds by Doe v. Roe" → no (report).
- "Convictions that have been vacated ... are no longer valid convictions" → no (no act on a decision).
- "In light of the Supreme Court's decision in Y, our holding in X is no longer good law." → no (cause: decision).
- "X is no longer the law because of the 1978 amendment." → no (cause: statute).
- "We therefore hold that Brown was wrongly decided and should no longer be followed." → yes, `rejected`
  (own-act marker "we therefore hold", own reasoning), `partialUnknown`.
- "Smith v. Jones, 5 Ind. 4, and Doe v. Roe, 6 Ind. 7, are overruled." → yes, both targets, `overruled`, `all`.
- Previous sentence "The court so held in Doe v. Roe, 6 Ind. 7." then FOCUS "That case is overruled." → yes, target
  Doe v. Roe, `naming` = {"T1": "The court so held in Doe v. Roe, 6 Ind. 7."}.

## Output

Your task message names your packs and your answer file(s): `ans/ans_NNN.jsonl` for `pack_NNN.md` in the folder
`~\Documents\us-caselaw-lean-work\caselaw-lean-2\round8\agents\ownact\`. UTF-8, LF, one JSON object
per line, every line parseable (escape `"` and `\` inside strings), every item of the pack exactly once, in pack
order. Write with the Write tool or a short Python script (scripts go in your scratch directory, not in the
project). Read each pack completely (in chunks with offset/limit until its end). When done, reply with only: per
pack, the number of items, the number with `own_act` true, and the counts by kind.
