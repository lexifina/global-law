# Reader brief: a court rejects a named doctrine that it ties to one earlier case (round 9 state9 part C; round-7 brief reused)

You read passages of US court opinions and decide, for each item, two things:

1. **REJECT**: in the marked MAIN sentence, does the DECIDING court itself, in its own words in this opinion, reject,
   abandon, repudiate, discard, disapprove or declare no longer law **the doctrine D** (the label given in the item)
   — as a whole or within a stated field?
2. **TIE**: does the marked TIE sentence, in this same opinion, tie the doctrine D to **exactly the earlier case X**
   named in the item, as the case that announced / established / laid down / is the source of D?

The model item is *Brown v. Board of Education*, 347 U.S. 483 (1954):
MAIN "We conclude that in the field of public education the doctrine of “separate but equal” has no place."
TIE "... the so-called “separate but equal” doctrine announced by this Court in Plessy v. Ferguson, 163 U. S. 537."
Answer: reject yes, tie yes, field limit "in the field of public education".

## The item

Your pack file (`packs/pack_NNN.md`) holds items. Each item has:

- `### ITEM <id>`
- `ACTING:` the deciding decision W (name, citation, court, date);
- `TARGET:` the earlier case X (name, citation, court, date);
- `LABEL:` the doctrine label D (lower case);
- `MAIN WINDOW:` about 700 characters of W's opinion on each side of the MAIN sentence, which stands between `⟦` and
  `⟧` (the marks are not part of the opinion); `MAIN:` the sentence again;
- `TIE WINDOW:` the same for the TIE sentence; `TIE:` the sentence again. (MAIN and TIE may be the same sentence.)

Judge from the item's own text only. Do not use what you know about the cases, do not look anything up, do not open
any other file of the project (in particular nothing under `gold/`, `round5/gold_fresh/`, `round6/shepardized/`,
`round6/history/split/`, `round7/heldout/`, `benchmarks/`, `eval/`, `events_v3/`, `lean-in-v3/`), and do not call any external model or web service.

## What to answer

One JSON object per item, one per line, in `ans/pack_NNN.jsonl` (same NNN as the pack):

    {"id": "5994537:14044", "reject": true, "tie": true, "field_limit": "in the field of public education",
     "main_quote": "We conclude that in the field of public education the doctrine of “separate but equal” has no place.",
     "tie_quote": "In each of the cases other than the Delaware case, a three-judge federal district court denied relief to the plaintiffs on the so-called “separate but equal” doctrine announced by this Court in Plessy v. Ferguson, 163 U. S. 537.",
     "why": "present rejection of the doctrine in a field; tie names Plessy as its source", "confidence": 0.95}

- `reject` is **true only if all hold** for the MAIN sentence:
  1. it is the deciding court's own act or declaration, made now, in this opinion ("we reject / abandon / repudiate /
     discard / disapprove / no longer follow / no longer adhere to D", "D is rejected / is abandoned / should be
     abandoned / must be discarded", "D has no place in <field>", "D is no longer the law / no longer good law",
     "we have decided that D ... should be abandoned");
  2. the thing rejected is the doctrine D itself (its grammatical object in the active voice, its subject in the
     passive voice or with "has no place" / "is no longer"), not something else in the sentence;
  3. the court discards D as law it would otherwise follow, in whole or within a stated field or class of cases.
- `reject` is **false** when the MAIN sentence:
  - only holds that D does not apply to these facts or this kind of case where it never applied ("D has no place in
    the application of the clause where the defendant himself ends the trial" when D was never a rule for that
    situation), distinguishes D, or declines to extend it;
  - rejects a party's or a lower court's argument, contention, reading, request or reliance on D ("we reject
    petitioner's argument that D applies"), or a version, extension or misreading of D rather than D;
  - reports what another court, an earlier decision, a statute, commentators or a dissent did or said ("in Y we
    abandoned D", "D was rejected in Y", "the legislature abolished D", "the amendments were designed to override
    D", "many courts have rejected D"), or what happened in the past ("did this Court abandon D");
  - says D is no longer law because of a statute, a rule or another decision (an intervening cause), not because
    this court now discards it;
  - refuses, declines, postpones, conditions or merely contemplates the act ("we do not abandon D", "we need not
    decide whether D survives", "to overrule D now would ...", "whether D should be abandoned");
  - is a quotation of another opinion, or sits in a syllabus, headnote, counsel's argument, a concurrence or a
    dissent (visible from the window: "Held:", "MR. JUSTICE X, dissenting", "I would").
  - the label D in the item is not the doctrine the sentence talks about (for example D is "related doctrine" or
    "sixth exception" — a phrase that is not the name of a doctrine — or "that rule" in the sentence refers to a
    different rule).
- `tie` is **true only if** the TIE sentence, in the deciding court's own words, says or plainly presents D as the
  doctrine / rule / test of case X: "the D doctrine announced in X", "the doctrine of D ... in the case of X", "the D
  test of X", "X's D rule", "the D test announced in that decision [= X, named in the sentence]". X must be named in
  the sentence (by name or citation). `tie` is **false** when the sentence ties D to another case (or to several
  cases without singling X out as its source), only mentions that X applied, followed or discussed D, quotes a
  dissent's or a party's tie, or names X for something else.
- `field_limit`: the words of the MAIN sentence that limit the rejection to a field or class of cases ("in the field
  of public education", "as applied to ...", "insofar as ...", "to the extent ..."), copied exactly; `""` when the
  rejection is unlimited.
- `main_quote`: copy the MAIN sentence exactly as printed in `MAIN:` (you may shorten it to a contiguous part that
  still holds D and the rejecting words; copy character for character, keep the opinion's quote marks).
- `tie_quote`: copy the TIE sentence exactly as printed in `TIE:` (you may shorten it to a contiguous part that still
  holds D, the tying words and the name or citation of X).
- `why`: at most 20 words. `confidence`: 0 to 1.

When `reject` or `tie` is false, still give both quotes as printed (unshortened). Answer every item of your pack.
Write the answer file with the Write tool (UTF-8). Do not edit the pack.
