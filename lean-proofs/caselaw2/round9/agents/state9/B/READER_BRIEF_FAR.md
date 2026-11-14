# Reader brief: does the court itself overrule / disapprove an earlier decision in this sentence? (round 9, state9 part B: targets named further back)

You read passages from US court opinions. In each item one sentence, the **ACT sentence**, uses a status-changing
word (overrule, disapprove, abrogate, recede from) in a form such as "X is overruled", "X is, on review, expressly
overruled", "we, therefore, disapprove ...", "it is our duty to overrule it", "we have no hesitation in overruling
it", "X should be overruled in so far as ...", "the ruling in X ... is overruled". You decide **whether the ACT
sentence is the deciding court's own act now, and which of the listed earlier decisions it acts on.**

Your pack file (`packs/pack_NNN.md`) holds ITEMS. Each item has:

- `### ITEM <id>`
- `ACTING:` the deciding decision (name, citation, court, date) and the opinion part the ACT sentence is in;
- `TARGETS:` a numbered list `T1`, `T2`, ... of earlier decisions named near the ACT sentence: name, citation, date,
  court, how the passage names it (`cite "<citation>"` or `name "<words>"`), and WHERE: `before (gap N)` = named
  in a sentence ending N characters before the ACT sentence (here N is usually more than 300: the decision is named
  some sentences or a paragraph earlier, and the ACT sentence may point back to it with "it", "that case", "the
  case", "such decisions", or name it again only by a short word);
- `WINDOW:` the opinion text around the ACT sentence. The ACT sentence stands between `⟦` and `⟧`; each listed
  decision's name/citation is marked `[T1]`, `[T2]`, ... just after it (marks are not part of the opinion);
- `ACT:` the ACT sentence again.

Judge from the item's own text only. Do not use what you know about the cases, do not look anything up, and do not
open any other file of the project (in particular nothing under `gold/`, `benchmarks/`, `round5/gold_fresh/`,
`round5/tests/`, `round6/shepardized/`, `round6/history/split/`, `round7/heldout/`, `events_v3/`, `eval/`), and do
not call any external model or web service. Read only your own pack files and this brief; write only your answer
file. No subagents.

## What to answer

One JSON object per item, one per line, in the answer file named in your task:

    {"id": "5687:3028", "act": true, "targets": ["T1"], "kind": "overruled", "scope": "partialUnknown",
     "act_quote": "Smith v. Jones, 12 Ga. 3, is overruled in so far as it conflicts with this ruling.",
     "naming": {}, "confidence": 0.95, "why": "court's own passive act on T1; in so far as = limit"}

- `id`: the text after `### ITEM `.
- `act`: **true only if all of these hold:**
  1. The ACT sentence is the deciding court's own act or declaration, made now, in this opinion ("X is (hereby)
     overruled", "we overrule X", "X is, on review, expressly overruled", "X must be, and hereby is, overruled",
     "X is disapproved", "we disapprove X", "it is our duty to overrule it", "we have no hesitation in overruling it",
     "X should be overruled in so far as ..." when the court itself says so as its conclusion, "we think X should be
     and it is overruled").
  2. Its object / subject is an earlier **judicial decision** (or its holding, ruling, language, dictum or rule),
     named in the sentence or pointed to ("it", "that case", "the same", "that decision") with the decision named
     just before.
  3. That decision is in the TARGETS list, and the ACT sentence plainly points to THAT decision (not to another
     decision named between it and the ACT sentence).
- `act` is **false** when the ACT sentence:
  - reports a past act or another court's act ("X was overruled in Y", "X has been overruled", "the court of
    appeals disapproved X", "in Y we overruled X", "X, overruled on other grounds by Y", "X is overruled by Y" where
    Y is another decision);
  - is a party's, counsel's or the dissent's position, a request, a question, a hypothesis, a refusal or doubt
    ("appellant urges that X be overruled", "if X holds otherwise it would have to be overruled", "we need not
    overrule X", "we decline to overrule", "unless X is overruled");
  - is procedural: an objection, motion, demurrer, exception, plea, assignment / point / ground of error, petition,
    certiorari, or the judgment / ruling / decision of the trial court or the court below in this very case "is
    overruled" (overruling the lower court's ruling in this case is not overruling a precedent);
  - acts on a statute, a rule, an argument or a contention, not on an earlier decision;
  - is inside a quotation of another opinion, a syllabus or headnote, a concurrence or a dissent (visible from the
    window: quotation marks, "I would", "I concur", "dissenting");
  - points to no decision in the TARGETS list, or it is unclear which earlier decision the ACT sentence points to.
- `targets`: the T-numbers the act reaches; `[]` when `act` is false. Leave out a
  decision named only as authority for the court's view or as the case followed.
- `kind`: `overruled` (overrule), `disapproved` (disapprove), `abrogated` (abrogate), `recededFrom` (recede from):
  the word the ACT sentence uses.
- `scope`: `all` **only** when the act is on the whole case with no limiting phrase anywhere in the ACT sentence;
  else `partialUnknown` ("to the extent", "insofar as", "in so far as", "so far as", "in part", "on this point",
  "as to", "the language of", "the holding that ...", "the ruling in X that ...", "any holding in X ...", "the third
  ground of", "in so far as it conflicts with ...").
- `act_quote`: the exact text of the ACT sentence as printed after `ACT:` (copy it character for character; you may
  shorten it to a contiguous part that still holds the act word, the target's name/citation or pointing word, and
  any limiting phrase).
- `naming`: `{}` normally. Only when a chosen target is `before` and the passage names it more clearly in another
  sentence ending at most 300 characters before the ACT sentence: `{"T2": "<exact text from the WINDOW>"}`.
- `confidence`: 0 to 1. `why`: at most 25 words.

Be strict: when you are unsure that the court itself acts now on a listed earlier decision, answer `act: false`.
Answer every item of your packs, in order; do not stop early. Reply at the end with only: number of items, number
with act true.
