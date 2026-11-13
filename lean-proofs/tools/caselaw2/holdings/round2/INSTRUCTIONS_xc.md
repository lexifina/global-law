# Reading task: is this pair of court-of-appeals decisions a circuit split?

You are given a batch file of pairs. Each pair has a later decision **B** (a federal court of appeals) that says it
declines to follow or disagrees with an earlier decision **T** of a different circuit. For each decision you see some
numbered sentences of the court's own opinion (`B<number>:` and `T<number>:`). The sentences are a selection, not the
whole opinion.

For every pair decide whether B and T are a genuine split on a question of federal statutory law:

1. Both courts decide the **same legal question**, which you can state as one yes/no question about what a federal
   statute (US Code section) means or requires.
2. B's court gives its **own holding** on that question (not a remark in passing, not a description of someone else's
   view), and one of the shown B sentences states that holding or the conclusion that carries it.
3. T's court **held the opposite**, and one of the shown T sentences states T's holding on that question. If no shown T
   sentence states it, the pair is NOT accepted (answer `split: false`, reason `T holding not shown`). Do not rely on
   B's description of T alone, and do not rely on your memory of the cases for the sentence choice.
4. The disagreement is about the statute's meaning, not about facts, the record, a state-law point, the Constitution
   alone, a procedural rule (FRCP/FRAP/Fed. R. Evid.) alone, or the Sentencing Guidelines alone. If the question is
   real but not about a US Code section, answer `split: false`, reason `not statutory`.

Write one JSON object per line, one line for EVERY pair id in the batch, to the output file you are told, using this
shape exactly (all keys present; use "" or 0 where not applicable):

    {"pid":"X0000","split":true,"reason":"","question":"Does 18 U.S.C. § 924(c)(1) require ...?","usc":"18:924(c)","b_answer":"no","b_sent":"B14","b_prop":"Section 924(c)(1) does not require ...","t_answer":"yes","t_sent":"T42","t_prop":"Section 924(c)(1) requires ...","conf":0.85}

Rules for the fields:

- `question`: one neutral yes/no question, naming the section, under 300 characters. `b_answer` and `t_answer` are the
  courts' answers to that question (`yes` or `no`) and must differ when `split` is true.
- `usc`: `title:section(subsection)` using the first-level subsection when the question is about one (for example
  `18:924(c)`, `42:2000e-3(a)`, `28:1292(a)`), or `title:section` when it is about the whole section (`42:1983`). The
  section must be one named in the shown sentences or in the "US Code citations near it" line. If the statute is
  cited only by its Act section (for example "§ 10(b) of the Act") and you are not sure of the US Code section, give
  `split: false`, reason `usc unknown`.
- `b_sent` / `t_sent`: the id of ONE shown sentence (for example `B14`, `T42`) that states that court's holding on the
  question. Pick the sentence that states the rule or conclusion, not a citation string.
- `b_prop` / `t_prop`: the court's holding in your own words, one sentence, under 300 characters.
- `conf`: your confidence from 0 to 1 that this is a genuine split as defined above with the right sentences.
- `reason` (when `split` is false): a few words: `T holding not shown`, `not statutory`, `not same question`,
  `B does not hold`, `T not contrary`, `usc unknown`, or another short reason.

Be strict. An accepted pair will be recorded as two certified holdings with opposite answers, so a wrong acceptance is
worse than a missed one. Do not read any other file in the project. Write the output file with the Write tool (or a
short script). Your final reply: number accepted, number rejected by reason.
