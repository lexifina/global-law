# Reader brief: later statements that a decision was overruled (round 2, `explicit = 0` tier)

Your pack file holds ITEMS. Each item is a passage of a court opinion (the STATING decision): a numbered list of
CANDIDATE earlier decisions named near the sentence (T1, T2, ...), a WINDOW of the opinion text and the FOCUS sentence.
Judge only from the item's text. Do not use outside knowledge, do not read other files, no external model or web.

Question: does the FOCUS sentence (read with the window) state, as a fact the stating court accepts, that an earlier
decision X was overruled, abrogated or disapproved BY another earlier decision Y? Typical forms: "X was overruled by
Y", "X, 16 Pet. 1, overruled by Y, 304 U.S. 64", "in Y we overruled X", "Y (overruling X)", "Y overruled X",
"X has been overruled (Y)".

Answer `states: false` when: the sentence is this court's own present act ("we overrule X"); a refusal or a question
("Y did not overrule X", "whether Y overruled X"); a party's argument; a dissent's or concurrence's view; a
procedural ruling (objection, motion overruled); the overruling body is a statute or rule, not a decision; or X or Y
is not in the candidate list or cannot be told from the window.

For each item write one JSON object per line, in pack order, to the answer file named in your task:

    {"id": "...", "states": true, "x": "T2", "y": "T1", "kind": "overruled", "scope": "all", "quote": "...",
     "confidence": 0.9}

- `x`: the decision that was overruled; `y`: the decision that overruled it. Ids from the list only.
- `kind`: overruled | abrogated | disapproved (the word used).
- `scope`: `all`; `partialUnknown` ("in part", "to the extent", "insofar as", one point of several); `otherGrounds`
  ("overruled on other grounds").
- `quote`: copy EXACTLY (character for character) one contiguous span of the WINDOW, at most 350 characters, holding
  the overruling word and X's name or citation. "" when states is false.
- `id` is the text after `### ITEM `. Every item exactly once. Each line must parse as JSON.

Write the file with a short Python script or the Write tool (UTF-8, LF). Write no other file in the project
directories. Reply with only the number of items and the number with states true.
