# Reader brief: "X was overruled by Y", as stated by a later court (round 5, recognised overruling)

Your pack file holds ITEMS. Each item gives a later decision **W** (the stating decision), an earlier decision **X**,
a decision **Y**, a WINDOW of W's opinion text, NOTE AT (the place in the window where the statement is thought to
be) and sometimes INTRO (how the paragraph or footnote around the window begins). Judge only from the item's text. Do not use what you know about any of these cases, do not open other files,
no web, no external model.

## The question

Does the opinion OF THE COURT in W state, as a fact the court accepts, that **X was overruled / abrogated /
disapproved / receded from BY Y**?

Typical true forms: "X, 12 Cal. 3d 45, overruled by Y, 30 Cal. 3d 100", "X (overruled on other grounds by Y)",
"X was overruled by this court in Y", "in Y we overruled X", "Y, which overruled X", "Y (overruling X)",
"Y, overruling X", "X has been overruled. See Y", "X, abrogated by Y", "X, disapproved on another point in Y",
"we receded from X in Y", "Y overruled X sub silentio".

The item names X and Y for you. They were paired mechanically (in some packs simply because both are mentioned
near an overruling word), so many items are not statements at all: the passage may overrule something else, or X
and Y may be the other way round, or W may be overruling X itself. Answer for the item's X and Y only, in that
direction.

Answer `states: false` (with a short `reason`) when:

- `notMajority`: the item's opinion part is not majority / perCuriam / plurality, or the statement stands in the part
  of the window that belongs to a dissent or concurrence (see the CAUTION line, if any);
- `quotation`: the words are a quotation of a party, of a lower court or of another court, or the court only
  reports someone else's view or doubt;
- `argument`: a party argues, contends or urges it and the court does not adopt it;
- `negation`: "Y did not overrule X", "X has not been overruled", "X survives Y";
- `question`: "whether Y overruled X", "it has been questioned / doubted", "Y may have overruled X";
- `refusal` / `would`: "we decline to hold that ...", "would overrule", "should be overruled";
- `ownAct`: W itself overrules X now ("we overrule X", "X is hereby overruled") and Y is not the actor;
- `wrongDirection`: the passage says Y was overruled (by X or by anything else), not X;
- `otherDecision`: X was overruled, but by a decision other than Y, by a statute, a rule or an amendment, or the
  passage names no decision;
- `notOverruling`: only "reversed", "vacated", "modified", "superseded by statute", "limited", "distinguished",
  "criticised", "questioned", "not followed";
- `cannotTell`: X or Y cannot be identified in the window;
- `notInOneSpan`: the court does state it, but no single span of at most 400 characters of the WINDOW holds all
  three things the quote needs (below).

## The quote (this is what the checker verifies; be exact)

`quote` is copied EXACTLY, character for character, from the WINDOW: one contiguous span, at most 400 characters.
It must contain, all three INSIDE the span:

1. an overruling word: overrul... (overruled, overruling), abrogat..., disapprov..., reced... (receded from; the
   word "receded" must not be the first word of the quote: the checker looks for it after a blank);
2. X's name or X's citation (a distinctive party name as printed, such as "Lustgarten" or "Fleet Corporation v.
   Lustgarten", or the reporter citation such as "280 U. S. 320");
3. Y's name or Y's citation.

"supra", "id.", "that case", "the former decision" do not name a case. If X or Y is named only that way inside
every possible span, answer `states: false`, `reason: "notInOneSpan"`.

Keep the quote as short as it can be: begin at X's name or citation (or at Y's, when Y comes first) and end right
after the last of the three. Do not add neighbouring sentences.

The mechanical checker refuses a quote that contains any of these strings (anywhere, even inside another word):
`not overrul`, `n't overrul`, `never overrul`, `not been overrul`, `never been overrul`, `not abrogat`,
`n't abrogat`, `not been abrogat`, `not disapprov`, `whether`, `without overruling`, `rather than overrul`,
`declin`, `refus`, `would overrule`, `should be overruled`, `should overrule`, `to overrule`, `contend`,
`dissent`, `question`, `doubt`, `argues`, `argued`, `arguing`, `argument`, `urges`, `urged`, `urging`.
If such a word governs the statement, the answer is `states: false` anyway. If it only stands nearby (in a
parenthetical about what X held, in the next clause), cut the quote so that it stays outside. If it stands between
the three things and cannot be cut out, still answer truthfully with the shortest quote: the checker will set the
row aside.

## Lists and footnotes (the INTRO field)

Some statements are entries of a list: a footnote or a string of parentheticals such as "Y (overruling X); Y2
(overruling X2); ...". How the list begins can change what each entry means. When the start of the paragraph,
footnote or list lies before the window, the item shows it as INTRO.

- Read INTRO (or the start of the list, when it is inside the window) before judging. If it says the listed cases
  were overruled "in whole or in part", "wholly or partly" or the like, then `scope` is `partialUnknown` for every
  entry, unless the entry itself says that X was overruled as a whole.
- If INTRO shows that the list is something else (cases a party relies on, cases that were questioned, cases the
  court declines to overrule, a dissent's catalogue quoted by the court), judge accordingly.
- INTRO is context only. The quote is still one contiguous span of the WINDOW holding the overruling word and both
  names; never quote from INTRO.

## The other fields

- `kind`: the word the court uses for X: `overruled` | `abrogated` | `disapproved` | `recededFrom`.
- `scope`:
  - `otherGrounds` for "overruled on other grounds", "on another point", "on a different ground";
  - `partialUnknown` for "in part", "to the extent", "insofar as", "as to ...", "on this point", "so far as it
    holds ...", and whenever the statement is limited to a field or speaks of a doctrine or rule of X rather than
    of X itself;
  - `all` otherwise.
- `field_limit`: the words of the passage that limit the effect to a field ("in the field of public education",
  "as applied to criminal cases"), copied; "" when there is none.
- `doctrine`: a short label when the sentence speaks of "the doctrine / rule / principle of X" ("separate but
  equal"); "" otherwise.
- `confidence`: 0-1, your confidence that the court states it and that X and Y are the two decisions of the item
  in that direction.

## Output

One JSON object per line, in pack order, every item exactly once, to the answer file named in your task
(`round7/agents/queue/ans/ans_<pack name>.jsonl`):

    {"id": "r12345", "states": true, "kind": "overruled", "scope": "otherGrounds", "field_limit": "", "doctrine": "", "quote": "Metcalf v. Bochco, 294 F.3d 1069, 1074 (9th Cir. 2002) (...), overruled on other grounds by Skidmore, 952 F.3d  1051", "confidence": 0.9}
    {"id": "r12346", "states": false, "reason": "negation", "kind": "", "scope": "", "field_limit": "", "doctrine": "", "quote": "", "confidence": 0.9}

- `id` is the text after `### ITEM `.
- Copy the quote from the WINDOW as it stands (spacing, punctuation, misprints, quote marks). Do not write "(...)"
  for left-out text as the example above does for brevity: a quote is contiguous.
- Each line must parse as JSON (escape `"` and `\` inside strings).

Write the file with the Write tool or a short Python script (UTF-8, LF). Write no other file. Reply with only the
number of items and the number with `states: true`.
