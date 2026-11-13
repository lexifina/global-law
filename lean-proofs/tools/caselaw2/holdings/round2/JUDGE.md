# Judging task (independent check of claims about court decisions)

You are an independent judge. Each item gives passages copied from court opinions and one or two CLAIMS about them.
Some claims are wrong on purpose. Judge each claim strictly from the passages shown (you may use general legal
knowledge to understand them, but a claim passes only if the passage supports it). Do not read any other file.

## Items whose id starts with A (one Supreme Court decision, one CLAIM)

Return for each item:

    {"id":"A000","decides":true,"answer_ok":true,"sentence_ok":true,"note":""}

- `decides`: true if the Supreme Court decision, as its holding, decides the QUESTION as posed (a more general holding
  that necessarily answers the question counts). False if it only touches a nearby point, leaves the question open,
  or the passage is not the Court's own holding (for example a description of a party's argument or of a lower
  court's view, or dicta).
- `answer_ok`: true if the Court's answer to the QUESTION, exactly as the question is worded, is the answer the CLAIM
  states. Check the polarity carefully (compare with the YES-side and NO-side holdings shown).
- `sentence_ok`: true if the marked sentence (between >>> and <<<) itself states the holding or the conclusion that
  carries it, in the Court's own voice.
- `note`: a few words when any field is false.

## Items whose id starts with B (two court-of-appeals decisions, two CLAIMS)

Return for each item:

    {"id":"B000","same_question":true,"c1_ok":true,"c2_ok":true,"statutory":true,"genuine_split":true,"note":""}

- `same_question`: true if both decisions address the QUESTION as posed (the same legal question).
- `c1_ok`: true if CLAIM 1 is right: the court in DECISION 1 holds (its own holding, not dicta, not a description of
  another court's view) the stated answer, and the passage shows it.
- `c2_ok`: the same for CLAIM 2 and DECISION 2.
- `statutory`: true if the QUESTION is about the meaning or requirements of the cited US Code provision (not only
  about the Constitution, a court rule, the Sentencing Guidelines, state law, or facts).
- `genuine_split`: true only if all of the above hold, so that the two courts of appeals gave opposite answers to the
  same statutory question.
- `note`: a few words when any field is false.

Write one JSON object per line, one line for EVERY item in your batch file, to the output file you are told (Write
tool or a short script). Final reply: how many items you judged and how many failed.
