# Reader brief: overrulings stated with "those cases" / "that case" (round 7, class antecedent)

You read passages from US court opinions. In each item one sentence, the **ACT sentence**, uses a status-changing
word (overrule, disapprove, abrogate, recede from, repudiate, overturn, disavow, "no longer ... law/authority") and
refers to earlier decisions by a pointing phrase ("Those cases are overruled.", "To the extent they hold otherwise,
these decisions are disapproved.", "That case is overruled.", "... and it is overruled"). The decisions it points to
are usually named in the sentence or sentences just before it. You decide **whether the ACT sentence is the deciding
court's own act now, and which of the listed earlier decisions it acts on.**

Your pack file (`packs/pack_NNN.md`) holds ITEMS. Each item has:

- `### ITEM <id>`
- `ACTING:` the deciding decision (name, citation, court, date) and the opinion part (majority, per curiam,
  plurality) the ACT sentence is in;
- `TARGETS:` a numbered list `T1`, `T2`, ... of earlier decisions named near the ACT sentence: name, citation, date,
  court, how the passage names it (`cite "<citation>"` or `name "<words>"`), and WHERE: `before (gap N)` = in a
  sentence ending N characters before the ACT sentence; `in act` = in the ACT sentence itself; `earlier (far)` = named
  further back (more than 300 characters; listed for context only);
- `WINDOW:` the opinion text around the ACT sentence. The ACT sentence stands between `⟦` and `⟧`; each listed
  decision's name/citation is marked `[T1]`, `[T2]`, ... just after it (marks are not part of the opinion);
- `ACT:` the ACT sentence again.

Judge from the item's own text only. Do not use what you know about the cases, do not look anything up, and do not
open any other file of the project (in particular nothing under `gold/`, `round5/gold_fresh/`, `round5/tests/`,
`round6/shepardized/`, `round6/history/split/`, `events_v3/`, `eval/`), and do not call any external model or web
service. Read only your own pack files and this brief; write only your answer file.

## What to answer

One JSON object per item, one per line, in `ans/ans_<pack>.jsonl` (the folder named in your task):

    {"id": "5687:3028", "act": true, "targets": ["T1", "T2"], "kind": "overruled", "scope": "partialUnknown",
     "act_quote": "The earlier decisions, so far as they apply to cases like the present, must be considered as overruled.",
     "naming": {}, "confidence": 0.9, "why": "earlier decisions = Minor's R. 89 line (T1,T2); so far as = limit"}

- `id`: the text after `### ITEM `.
- `act`: **true only if all of these hold:**
  1. The ACT sentence is the deciding court's own act or declaration, made now, in this opinion: "we overrule", "...
     is/are (hereby) overruled", "... must be considered as overruled", "... is disapproved", "we disapprove", "...
     are abrogated", "we recede from", "... is repudiated", "... is no longer the law / no longer authority".
  2. Its object (active voice) or subject (passive voice) is the pointing phrase ("those cases", "that case", "these
     decisions", "they", "it", "them", "each of them", "the cases cited") or names the earlier decision(s) directly,
     and what it points to is one or more earlier **judicial decisions** (or their holding / language / rule).
  3. At least one decision it points to is in the TARGETS list (T-numbers you can name).
- `act` is **false** when the ACT sentence:
  - reports a past act ("those cases have been overruled", "that case was overruled in Smith", "we overruled them in
    1950", "they were disapproved by the legislature") or what another court did;
  - refuses, declines, postpones or doubts the act ("we do not overrule those cases", "we need not decide whether
    they are overruled", "if those cases hold otherwise they would have to be overruled", "it is unnecessary to
    overrule them"), or is a question, a hypothesis or a party's or the dissent's position ("appellant urges that
    those cases be overruled");
  - is a procedural ruling (an objection, motion, demurrer, exception, assignment, point of error, ground, plea or
    petition "is overruled"); rejects an argument, a contention or a reading; or acts on a statute, a rule of court,
    a contract, a verdict or the judgment under review in this very case;
  - points to something that is not an earlier decision (a rule of evidence in the abstract, a statute, an
    argument), or to decisions that are not in the TARGETS list at all;
  - is inside a quotation of another opinion, a syllabus or headnote, counsel's argument, a concurrence or a dissent
    (visible from the window: quotation marks around the passage, "Held:", "MR. JUSTICE X, dissenting", "I would").
- `targets`: when `act` is true, the T-numbers of the listed decisions that the ACT sentence acts on, all of them
  (a sentence that overrules several cases at once gets every one). Leave out a decision the passage names only as
  authority for the court's own view, as the case being followed, as the later case that departed from the
  overruled line, as the source of a quotation, or as a lower-court decision in this very case. A **companion case**
  named together with an overruled case ("Smith v. Jones and its companion, Doe v. Roe, ... Those cases are
  overruled") is a target too. A citation that is a parallel citation or the same case's later history (", aff'd",
  "rev'd on other grounds") is the same decision only if the list shows it as one T-number; do not add a T-number
  for the history of a target unless the act plainly reaches it. When `act` is false, `targets` is `[]`.
  `act` true with no listed target the sentence reaches is not allowed: answer `act: false` and say so in `why`.
- `kind`: `overruled` (overrule, repudiate, overturn, disavow, "no longer the law"), `disapproved` (disapprove),
  `abrogated` (abrogate), `recededFrom` (recede from). Use the word the ACT sentence uses.
- `scope`: `all` **only** when the act is on the whole of each chosen case with no limiting phrase anywhere in the ACT
  sentence. Any limiting phrase gives `partialUnknown`: "to the extent", "insofar as", "in so far as", "so far as",
  "in part", "on this point", "on this issue", "on other grounds", "as to", "in the field of", "to that extent",
  "pro tanto", "in so far as they conflict / are inconsistent with this opinion", "the language of", "the dictum
  in", "the holding that ...", "the rule announced in". If one sentence acts on several cases with one limiting
  phrase, every chosen case gets `partialUnknown`.
- `act_quote`: the exact text of the ACT sentence as printed in `ACT:` (copy it character for character; you may
  shorten it to a contiguous part that still holds the act word, the pointing phrase and any limiting phrase).
- `naming`: normally `{}`: the T-line's naming sentence is used. Fill it only when the passage names a chosen
  target more clearly in another sentence that ends at most 300 characters before the ACT sentence: `{"T2": "<exact
  text copied from the WINDOW, holding T2's citation or name words>"}`.
- `confidence`: 0 to 1. `why`: at most 25 words (what the pointing phrase refers to, any limit).

Be strict: when the pointing phrase could refer to more than one group of listed decisions and the passage does not
make clear which, choose only those the passage makes clear; if none is clear, `act: false` with why "unclear
referent". Answer every item of your packs; do not stop early.
