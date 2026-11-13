# Reading task: what does this court of appeals HOLD about a US Code section?

You are given one batch file of windows. Each window is a set of numbered sentences from ONE federal court of
appeals opinion (only the court's own opinion; a selection around its citations of one US Code section, not the
whole opinion). Read only that batch file. Do not read any other file in the project and do not search the web.
Use only the shown sentences, not your memory of the case.

For every window say what this court itself HOLDS about the meaning or legal rule of the named section (the round-2
extraction brief):

1. `interprets`: true only if this court itself decides a question about what the section (or a subsection of it)
   means or requires: its elements, scope, a term's meaning, who or what it covers, the standard it sets, how it
   interacts with another provision. Citing it in passing, reciting a standard without deciding anything contested,
   or only applying settled law to facts is false.
2. For each such holding (at most 3) give:
   - `question`: a general yes/no QUESTION about the section that any federal court of appeals could answer, naming
     the section, without party names or case facts, under 300 characters, at the level of generality at which
     courts disagree (for example "Does 18 U.S.C. § 924(c)(3)(B)'s residual clause apply to conspiracy to commit
     Hobbs Act robbery?").
   - `answer`: this court's answer, `yes` or `no`.
   - `usc`: `title:section(subsection)` with the first-level subsection when the holding is about one (`18:924(c)`),
     else `title:section`. The section must be the window's section.
   - `s`: the number of the ONE shown sentence that states the holding most directly (the rule or conclusion, not a
     citation string, not a description of another court's view).
   - `kind`: `holding` or `alternative`.
   - `proposition`: the holding as a rule, in your words, one sentence, under 300 characters.
   - `confidence`: 0-1 that this is the court's own holding (not dicta, not another court's view) and the answer is
     right.
3. `conflict`: true if the sentences say other circuits disagree or are divided on the question.

Be strict: a wrong holding is worse than a missed one. If no shown sentence states the holding, do not record it.

Write one JSON object per line, one line for EVERY window id in the batch, to the output file you are told, in this
shape exactly:

    {"wid":"W0000","interprets":true,"conflict":false,"holdings":[{"s":7,"question":"Does 18 U.S.C. § 924(c)(1) require ...?","answer":"no","usc":"18:924(c)","kind":"holding","proposition":"Section 924(c)(1) does not require ...","confidence":0.85}]}

A window with no holding: `{"wid":"W0001","interprets":false,"conflict":false,"holdings":[]}`.

Write the file with the Write tool (plain UTF-8, one JSON object per line, nothing else). Your final reply: the
number of windows, and how many have interprets true. Nothing else.
