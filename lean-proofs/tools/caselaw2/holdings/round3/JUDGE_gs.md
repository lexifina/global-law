# Judging task: do these two court-of-appeals passages answer the same question differently?

You are given a file of items. Each item has a yes/no question about a US Code section, and two passages, each from
a different federal court of appeals opinion. In each passage one sentence is marked `>>> ... <<<`; it is the
sentence recorded as stating that court's holding. Each court has a recorded answer (yes or no) to the question.

Some items are wrong on purpose: a passage may be about a different question on the same section, or a recorded
answer may be wrong. Judge every item on its own, strictly, from the passages only. Read only the file you are given.
Do not use the web. Do not rely on your memory of the cases.

For each item decide:

- `same_question`: true only if BOTH passages address the stated question (the same legal question about the
  statute), not merely the same section or a related point.
- `answers_as_recorded`: true only if, on that question, court 1's passage gives the recorded answer of court 1 and
  court 2's passage gives the recorded answer of court 2 (so the courts really answer it differently).
- `both_holdings`: true only if in each passage the answer is the court's own holding or conclusion (not a
  description of another court's view, not a party's argument, not an aside), as far as the passage shows.
- `note`: a few words when any of the three is false.

Write one JSON object per line, one line for every item, to the output file you are told:

    {"id":"A00","same_question":true,"answers_as_recorded":true,"both_holdings":true,"note":""}

Final reply: number of items and how many have all three true. Nothing else.
