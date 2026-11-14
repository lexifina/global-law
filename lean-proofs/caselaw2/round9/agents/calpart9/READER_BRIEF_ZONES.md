# Reader brief: whose text is this? (round 9)

You read the opening (or a short passage) of US court decisions. In each item a line is marked `▶MARK◀`: a short
line naming one or more judges with a word such as "concurring", "concur", "dissent", "dissenting", "Concurrence by".
You decide **what the text right after that line is**.

Your pack file holds ITEMS. Each item has `### ITEM <id>`, the decision's court and date, and `TEXT:` = the passage:
the section heading (lines starting with `##` are headings added by the publisher of the text file), the lines
before the marked line, the marked line, and up to about 1,200 characters after it. `[...]` marks text left out.
Where the passage stops at another heading or another judge's line, that is shown.

Judge from the item's own text only. Do not use what you know about the cases, do not look anything up, and do not
open any other file of the project. Read only this brief and your pack file; write only your answer file. No
subagents, no external model or web service.

## What to answer

One JSON object per item, one per line, in the answer file named in your task:

    {"id": "p001", "after": "court", "mark": "vote", "confidence": 0.9, "why": "line lists judges joining; text after is 'We affirm'"}

- `after`: what the text right after the marked line is:
  - `"court"` — the opinion of the court (or the court's order / judgment / per curiam), e.g. "This case
    concerns ...", "We affirm", "The judgment is affirmed", a byline of the judge writing for the court followed by the
    court's opinion; also when nothing but further vote lines or the end of the passage follows the marked line;
  - `"separate"` — a separate opinion of the judge(s) named in the marked line (a concurrence or a dissent written by
    them: "I concur ...", "I respectfully dissent", "While I agree with the majority ...");
  - `"unclear"` — you cannot tell from the passage.
- `mark`: what the marked line itself is:
  - `"vote"` — a note recording how judges voted or joined ("X and Y, JJ., concurring.", "All concur, except Z,
    J., dissenting.", "Z, J., dissents."), or an index of the opinions filed ("Opinion by Judge A; Concurrence by
    Judge B");
  - `"heading"` — the heading of a separate opinion that starts right there ("Z, J., dissenting." followed by Z's
    own dissent);
  - `"unclear"`.
- `confidence`: 0 to 1. `why`: a few words.

Answer every item. Write the file once, at the end, as JSON lines.
