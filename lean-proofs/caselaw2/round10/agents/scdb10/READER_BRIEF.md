# Reader brief (scdb10, round 10): where a Supreme Court decision cites the decision it reviews

You read United States Supreme Court decisions (plain-text files from a case-law corpus; line breaks, page markers and
OCR artefacts are as printed in the file; in older files the footnotes are printed, without their numbers, after the
end of the opinion). For each decision you are given, answer from the text of the file only. Do not use outside
knowledge, the web, or any other file.

Folder: `~\Documents\us-caselaw-lean-work\caselaw-lean-2\round10\agents\scdb10\work\read\`.
Your pack file lists the decision numbers (one per line); the text of decision N is `<N>.txt` in that folder. Long
files: read them in parts (offset/limit) until you have the answers.

For each decision, write one JSON object per line (JSON Lines, UTF-8) to your answer file, with these fields:

- `n`: the decision number (the file name without `.txt`).
- `below_court`: the court whose judgment this Court reviews (as the text names it); `""` if unclear.
- `below_cite`: the citation (volume, reporter, page) of that court's decision under review as printed, or `""` if the
  text never cites it.
- `cite_places`: a list of every place the text gives that citation, each
  `{"where": W, "quote": "<verbatim words: the citation and up to ~250 characters before it>"}` with W one of
  `head_matter` (caption / syllabus / "certiorari to ..." / "Reported below" lines before the opinion), `opening`
  (the first paragraphs of the Court's opinion, the procedural history), `body` (later in the Court's opinion),
  `footnote` (a footnote, including the unnumbered footnote block printed after the opinion), `judgment_line`,
  `separate_opinion` (a concurrence or dissent).
- `tie`: for the place in the Court's own opinion (not head matter, not a separate opinion) that best shows the
  citation is the judgment under review: the verbatim words that tie the citation to that court's judgment (e.g. "The
  Court of Appeals affirmed. 123 F. 2d 456."; "It reversed the judgment ... 87 F. 2d 243."; a footnote "123 F. 2d 456."
  whose position you can relate to a sentence naming the court), and `tie_kind`: one of `same_sentence` (the sentence
  holding the citation names the court or "the court below"), `prev_sentences` (the court is named 1-3 sentences
  before, the citation's sentence speaks of what that court did: "It held ...", "That court ..."), `footnote_block`
  (the citation is only in the footnotes; say in `notes` what sentence it most plausibly belongs to), `case_name` (only
  the case name + citation, the court not named nearby), `quote_support` (the citation supports a quotation or a
  fact, not the judgment), `none`.
- `other_same_court`: other citations of decisions of the same lower court in THIS litigation (rehearing denial,
  earlier appeal, decision on remand), each `{"cite": "...", "role": "..."}`.
- `notes`: short; anything a careful text reader needs (court named only as "CA5", case decided below under another
  name, several judgments reviewed, ...).
- `confidence`: `high`, `medium` or `low`.

Write every answer, even when unsure (say so). Do not write anything other than your answer file.
