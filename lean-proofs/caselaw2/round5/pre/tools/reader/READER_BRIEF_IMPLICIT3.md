# Reader brief: later statements that a decision is no longer good law (round 3, `explicit = 0` witness tier)

Your pack file holds ITEMS. Each item is a passage of a court opinion (the STATING decision): a numbered list of
CANDIDATE earlier decisions named near the sentence (T1, T2, ...), a WINDOW of the opinion text and the FOCUS sentence.
Judge only from the item's text. Do not use outside knowledge of what happened to any case, do not read other files,
no external model or web.

Question: does the FOCUS sentence (read with the window) state, as a fact the stating court accepts, that an earlier
decision X is no longer good law: that X was overruled, abrogated, repudiated, overturned or disapproved, or "is no
longer good law / no longer the law / no longer controlling"? And which earlier decision Y, if any, does the passage
name as the decision that did it? Typical forms: "X was overruled by Y", "X, overruled by Y", "in Y we overruled X",
"Y (overruling X)", "Y overruled X sub silentio", "X is no longer good law after Y", "X has been repudiated. See Y",
"the doctrine of X was abandoned in Y", "X did not survive Y".

Answer `states: false` when: the sentence is the stating court's own present act ("we overrule X", "X is overruled",
"today we hold X is no longer good law"); a refusal, a doubt or a question ("Y did not overrule X", "whether Y
overruled X", "X has been questioned / limited / criticised / distinguished" only); a party's argument or a lower
court's view the stating court does not accept; a dissent's or concurrence's view; a procedural ruling (objection,
motion, demurrer overruled); only a statute, rule or constitutional amendment displaced X and no decision is named
and the court does not say X is no longer good law; or X is not in the candidate list or cannot be told from the
window. A statement about a doctrine counts only when the passage ties the doctrine to the candidate X by name or
citation.

For each item write one JSON object per line, in pack order, to the answer file named in your task:

    {"id": "...", "states": true, "x": "T2", "y": "T1", "kind": "overruled", "scope": "all", "quote": "...",
     "confidence": 0.9}

- `x`: the decision that is no longer good law. `y`: the decision the passage names as having overruled / abrogated /
  repudiated it; "" when the passage names none or it is not in the candidate list. Ids from the list only. If one
  sentence states this for several X, answer for the first X and add `"more": [{"x": "T3", "y": "T1"}]`.
- `kind`: overruled | abrogated | disapproved (use `overruled` for "overturned", "repudiated", "no longer good law",
  "abandoned"; `abrogated` only when that word is used; `disapproved` only when that word is used).
- `scope`: `all`; `partialUnknown` ("in part", "to the extent", "insofar as", one point of several); `otherGrounds`
  ("overruled on other grounds").
- `quote`: copy EXACTLY (character for character) one contiguous span of the WINDOW, at most 350 characters, holding
  the words that state it and X's name or citation. "" when states is false.
- `id` is the text after `### ITEM `. Every item exactly once. Each line must parse as JSON.

Write the file with a short Python script or the Write tool (UTF-8, LF). Write no other file in the project
directories. Reply with only the number of items and the number with states true.
