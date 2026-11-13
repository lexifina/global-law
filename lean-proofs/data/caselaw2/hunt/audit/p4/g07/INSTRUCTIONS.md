You are auditing candidate findings about US court decisions. The items in this directory are a MIX: some are
believed to be true instances of the pattern below and some are not. You are not told which. Judge every item only on
the decision text given in its file (and your own knowledge of the law and of the named cases where the file is
silent; say so in the explanation when you rely on it). Be strict: `confirmed` means every limb of the predicate is
shown; `not_confirmed` means a limb fails; `unclear` only when the text given cannot settle it.

Read every item file I*.txt in this directory in full. Use only the Read and Write tools; no web, no scripts, no other
files. Then write ONE file `answers.jsonl` in this directory, one JSON object per line, one line per item:

    {"id": "Inn", "verdict": "confirmed"|"not_confirmed"|"unclear", "applies_superseded_holding": true|false, "notes_statute": true|false, "conduct_after_effective": "yes"|"no"|"unknown", "explanation": "<one line, <= 45 words: what the citing court did and why the limb holds or fails>"}

Reply only with the number of lines written.

# Pattern

SUPERSEDED HOLDING APPLIED TO LATER CONDUCT (two-date error). A statute overrode a Supreme Court holding for conduct (or claims, or filings, as the statute provides) on or after a date. Limbs: (1) applies_superseded_holding: the citing court applies the very holding the statute overrode (see SCOPE) to decide the case - not an unaffected holding of the same decision, not history; (2) conduct_after_effective = yes: the conduct / claim / filing governed is on or after the date from which the statute applies (read the dates in the opinion); (3) notes_statute = false: the opinion does not account for the statute on that point. confirmed iff 1 holds, 2 is yes and 3 is false.
