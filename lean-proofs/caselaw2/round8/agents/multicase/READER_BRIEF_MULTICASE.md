# Reader brief: one sentence that overrules or disapproves several earlier cases (round 8, multicase)

You read passages from US court opinions. In each item one sentence, the **ACT sentence**, uses a status-changing
word (overrule, disapprove, abrogate, recede from, repudiate, disavow, overturn) and names, or points to, two or
more earlier decisions ("The rulings in A v. B, C v. D, and E v. F ... are overruled in so far as they hold ...",
"A, B and the cases following them are disapproved", "To the extent that A and B hold otherwise, they are
overruled", "We overrule A and B."). You decide **whether the ACT sentence is the deciding court's own act now, and
which of the listed earlier decisions it acts on.**

Your pack file (`packs/pack_NNN.md`) holds ITEMS. Each item has:

- `### ITEM <id>`
- `ACTING:` the deciding decision (name, citation, court, date) and the opinion part (majority, per curiam,
  plurality) the ACT sentence is in;
- `TARGETS:` a numbered list `T1`, `T2`, ... of earlier decisions the passage names: name, citation, date, court,
  how the passage names it (`cite "<citation>"` or `name "<words>"`), and WHERE: `in act` = in the ACT sentence
  itself, `before` = only in the sentence just before the ACT sentence;
- `WINDOW:` the opinion text around the ACT sentence. The ACT sentence stands between `⟦` and `⟧`; each listed
  decision's name/citation is marked `[T1]`, `[T2]`, ... just after it (marks are not part of the opinion);
- `ACT:` the ACT sentence again.

Judge from the item's own text only. Do not use what you know about the cases, do not look anything up, and do not
open any other file of the project (in particular nothing under `gold/`, `round5/gold_fresh/`, `round5/tests/`,
`round6/shepardized/`, `round6/history/split/`, `round7/heldout/`, `benchmarks/`, `events_v3/`, `eval/`), and do not
call any external model or web service. Read only your own pack files and this brief; write only your answer file.

## What to answer

One JSON object per item, one per line, in the answer file named in your task:

    {"id": "5687:3028", "act": true, "targets": ["T1", "T2", "T3"], "kind": "overruled", "scope": "partialUnknown",
     "act_quote": "", "confidence": 0.9, "why": "rulings in T1-T3 overruled 'in so far as they hold'; own act"}

- `id`: the text after `### ITEM `.
- `act`: **true only if all of these hold:**
  1. The ACT sentence is the deciding court's own act or declaration, made now, in this opinion: "we overrule",
     "... is/are (hereby) overruled", "... must be considered (as) overruled", "... are disapproved", "we disapprove",
     "... are abrogated", "we recede from", "... are repudiated", "... should be and are overruled".
  2. Its object (active voice) or subject (passive voice) is a list of earlier **judicial decisions** (or their
     holdings / rulings / language / rule) named in the sentence, or a pointing phrase ("those cases", "they",
     "both", "each of them") whose referents are named in the sentence just before.
  3. At least one decision it acts on is in the TARGETS list.
- `act` is **false** when the ACT sentence:
  - reports a past act or another court's act ("A and B have been overruled", "A was overruled in B", "B, which
    overruled A", "the Court of Appeals disapproved A and B", "see A (overruling B)", "A, overruled on other
    grounds, B") — in particular a citation string whose parentheticals or history phrases say "overruling",
    "overruled by", "disapproved in";
  - refuses, declines, postpones or doubts the act ("we do not overrule A or B", "we need not decide whether A and
    B are overruled", "if A and B hold otherwise they would have to be overruled"), or is a question, a hypothesis,
    or a party's or the dissent's position ("appellant urges that A and B be overruled");
  - is a procedural ruling (an objection, motion, demurrer, exception, assignment, point of error, ground, plea or
    petition "is overruled"); rejects an argument, a contention or a reading; or acts on a statute, a rule of court,
    a contract, a verdict or the judgment under review in this very case;
  - is a legislature's statement quoted by the court ("It is the intent of the legislature to overrule A and B");
  - is inside a quotation of another opinion, a syllabus or headnote, counsel's argument, a concurrence or a dissent
    (visible from the window: quotation marks around the passage, "Held:", "MR. JUSTICE X, dissenting", "I would").
- `targets`: when `act` is true, the T-numbers of **every** listed decision the ACT sentence acts on (this is the
  point of the item: a sentence that overrules three cases gets all three). Leave out a decision the sentence names
  only as authority for the court's own view, as the case being followed or reaffirmed ("we follow A and overrule
  B": only B), as the later case that already departed from the overruled line, as the source of a quotation, or as
  a lower-court decision in this very case. A citation that is a parallel citation of a target or the same case's
  later history (", aff'd", "rev'd") is not a separate target unless the act plainly reaches it. Check that each
  T-line's name matches the case the passage names at its mark: if the list gives a different case than the one the
  text names there (a citation that points to the wrong decision), leave that T out and say so in `why`.
  When `act` is false, `targets` is `[]`. `act` true with no listed target the sentence reaches is not allowed:
  answer `act: false` and say so in `why`.
- `kind`: `overruled` (overrule, repudiate, overturn, disavow), `disapproved` (disapprove), `abrogated` (abrogate),
  `recededFrom` (recede from). Use the word the ACT sentence uses for these targets. If the sentence uses two
  different acts for different targets ("A is overruled and B is disapproved"), answer `"kinds": {"T1": "overruled",
  "T2": "disapproved"}` in addition to `kind`.
- `scope`: `all` **only** when the act is on the whole of each chosen case with no limiting phrase anywhere in the
  ACT sentence. Any limiting phrase gives `partialUnknown`: "to the extent", "insofar as", "in so far as", "so far
  as", "in part", "on this point", "on this issue", "on other grounds", "as to", "in the field of", "to that
  extent", "pro tanto", "in so far as they conflict / are inconsistent with this opinion", "the language of", "the
  dictum in", "the holding that ...", "the rulings in ... in so far as they hold ...". One limiting phrase over the
  whole list gives every chosen case `partialUnknown`. If the sentence limits only some targets, answer
  `"scopes": {"T1": "all", "T2": "partialUnknown"}` in addition to `scope`.
- `act_quote`: normally `""` (the ACT sentence as marked is used). Fill it only when the marked ACT sentence is cut
  wrongly (it starts or ends in the middle of the real sentence, or runs into the next sentence): then copy the exact
  text of the real act sentence from the WINDOW, character for character, holding the act word, every chosen
  target's name or citation, and any limiting phrase.
- `confidence`: 0 to 1. `why`: at most 25 words (who acts, which cases, any limit).

Be strict: when it is unclear which listed decisions the act reaches, choose only those the passage makes clear; if
none is clear, `act: false` with why "unclear referent". Answer every item of your packs; do not stop early.
