# Reading task: does this Supreme Court decision decide this circuit-split question?

Each pair in the batch file gives:

- a yes/no QUESTION about a US Code provision on which federal courts of appeals have answered differently, with
  example holdings on the YES side and the NO side;
- selected numbered sentences (`S<number>:`) from the opinion of the Court in a later US Supreme Court decision. The
  sentences are a selection (opening, concluding, cue and topical sentences), not the whole opinion.

For every pair decide, from the shown sentences:

- `decides`:
  - `"yes"` — the Supreme Court's holding answers this very question (as posed), one way or the other. A holding that
    is stated more generally but necessarily answers the question also counts.
  - `"partly"` — the Court addresses the provision and a nearby point, or answers only part of the question, or its
    answer depends on a condition the question does not state; or the Court expressly leaves the question open.
  - `"no"` — the Court does not decide the question.
- `answer`: when `decides` is `yes`, the Court's answer to the QUESTION exactly as worded: `"yes"` or `"no"`. Check the
  polarity against the YES-side and NO-side examples: the Court's answer should agree with one side.
- `sent`: when `decides` is `yes`, the id of ONE shown sentence that states the Court's holding on the question (for
  example `"S212"`). Pick the sentence stating the rule or conclusion in the Court's own voice, not a citation, not a
  description of a party's argument or of a lower court's view. If no shown sentence states it, use `decides:
  "partly"` and say `holding sentence not shown` in `note`.
- `prop`: the Court's holding on the question in your own words, one sentence, under 300 characters.
- `conf`: 0 to 1, your confidence that the decision decides this question with that answer and that the sentence
  states it.
- `note`: a few words when `decides` is not `yes` (why), else "".

Base the sentence choice on the shown text only. You may use what you know of the decision to understand the
sentences, but do not accept a pair whose holding you cannot point to in a shown sentence.

Write one JSON object per line, one line for EVERY pair id in the batch, to the output file you are told:

    {"pid":"P0116","decides":"yes","answer":"no","sent":"S212","prop":"The anti-retaliation provision is not limited to ...","conf":0.9,"note":""}

Be strict: an accepted pair is recorded as a Supreme Court holding that resolves the circuit split. Read no other
files in the project. Final reply: counts of yes / partly / no.
