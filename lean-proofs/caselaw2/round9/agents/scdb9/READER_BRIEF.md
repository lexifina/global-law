# Reader brief (scdb9, round 9): the judgment line and the decision under review in Supreme Court decisions

You read United States Supreme Court decisions (plain-text files from a case-law corpus; line breaks, page markers and
OCR artefacts such as words split by a hyphen at a line break, "re- versed", are as printed in the file). For each
decision you are given, answer from the text of the file only. Do not use outside knowledge, the web, or any other file.

Folder: `~\Documents\us-caselaw-lean-work\caselaw-lean-2\round9\agents\scdb9\work\read\`.
Your pack file lists the decision numbers (one per line); the text of decision N is `<N>.txt` in that folder. Long files:
read them in parts (offset/limit) until you have found both answers; the head matter (start of the file) and the end
of the Court's opinion (before any concurring / dissenting opinion) usually hold them.

For each decision, write one JSON object per line (JSON Lines, UTF-8) to your answer file, with these fields:

- `n`: the decision number (the file name without `.txt`).
- `judgment_quote`: the exact words (copied verbatim from the file, keep any hyphen split or line break as a space) of
  the sentence or line in which THIS Court states its own disposition of the judgment it reviews (for example
  "Reversed.", "The judgment of the Court of Appeals is vacated, and the case is remanded ...", "the decree below must be
  affirmed", "Judgment reversed."). Prefer the operative statement at the end of the Court's (majority / per curiam)
  opinion; if the only statement is in the head matter / syllabus, quote that and say so in `notes`. Empty string if the
  Court states no disposition (say why in `notes`).
- `judgment_where`: one of `end_of_opinion`, `head_matter`, `elsewhere`, `none`.
- `kind`: `reversed`, `vacated`, `affirmed`, `modified`, `dismissed`, `reversed_in_part`, `mixed` (several judgments with
  different dispositions), `other`, or `none`.
- `below_court`: the court whose judgment this Court reviews (as the text names it).
- `below_cite_quote`: the exact words (verbatim) of the sentence, line or parenthetical in which the text gives the
  citation (volume, reporter, page) of that court's decision under review, including the words around the citation that
  say it is the decision under review (e.g. "The Court of Appeals affirmed. 123 F. 2d 456.", "Reported below: 99 F.3d 1",
  "227 Fed. Rep. 93, reversed."). Empty string if the text never cites it.
- `below_cite`: the citation itself (e.g. "123 F. 2d 456"), or empty.
- `other_cites_same_court`: a list of other citations in the text of decisions of the same lower court in THIS
  litigation (e.g. an order denying rehearing or rehearing en banc, an earlier appeal, a decision on remand), each as
  `{"cite": "...", "role": "rehearing denied | earlier appeal | other ...", "quote": "verbatim words around it"}`.
- `notes`: anything that makes the judgment line or the citation hard to find for a careful text reader (a hyphen split
  in the judgment word, the disposition spread over two lines, several docket numbers with different dispositions, the
  citation only in a footnote, the citation in a "see" sentence, the court named only by an abbreviation such as
  "CA5", the decision below described but not cited, ...). Short.
- `confidence`: `high`, `medium` or `low`.

Write every answer, even when unsure (say so). Do not write anything other than your answer file.
