You are auditing candidate findings about US court decisions. The items in this directory are a MIX: some are
believed to be true instances of the pattern below and some are not. You are not told which. Judge every item only on
the decision text given in its file (and your own knowledge of the law and of the named cases where the file is
silent; say so in the explanation when you rely on it). Be strict: `confirmed` means every limb of the predicate is
shown; `not_confirmed` means a limb fails; `unclear` only when the text given cannot settle it.

Read every item file I*.txt in this directory in full. Use only the Read and Write tools; no web, no scripts, no other
files. Then write ONE file `answers.jsonl` in this directory, one JSON object per line, one line per item:

    {"id": "Inn", "verdict": "confirmed"|"not_confirmed"|"unclear", "earlier_negated_on_point": true|false, "relies": true|false, "acknowledges": true|false, "same_case": true|false, "explanation": "<one line, <= 45 words: what the citing court did and why the limb holds or fails>"}

Reply only with the number of lines written.

# Pattern

ZOMBIE PRECEDENT. The citing opinion relies on an earlier decision as authority for a legal proposition after that decision had been overruled, abrogated, disapproved, receded from, reversed or vacated, without acknowledging it. Limbs: (1) earlier_negated_on_point: before the citing opinion's date, the earlier decision was negated on the very proposition the citing opinion takes from it (or as a whole, e.g. reversed or vacated outright) - check the NEGATING DECISION EXCERPT; a negation limited to a different point fails this limb; (2) relies: the citing court uses it as authority for that proposition (not as history, a party's argument, a contrast, or something it distinguishes or rejects); (3) acknowledges = false: nowhere near the citation does the citing opinion note the negative history or cite the negating decision on the point; (4) same_case = false: the citing opinion is not part of the same litigation. confirmed iff 1 and 2 hold and 3, 4 are false.
