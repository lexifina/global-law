You are auditing candidate findings about US court decisions. The items in this directory are a MIX: some are
believed to be true instances of the pattern below and some are not. You are not told which. Judge every item only on
the decision text given in its file (and your own knowledge of the law and of the named cases where the file is
silent; say so in the explanation when you rely on it). Be strict: `confirmed` means every limb of the predicate is
shown; `not_confirmed` means a limb fails; `unclear` only when the text given cannot settle it.

Read every item file I*.txt in this directory in full. Use only the Read and Write tools; no web, no scripts, no other
files. Then write ONE file `answers.jsonl` in this directory, one JSON object per line, one line per item:

    {"id": "Inn", "verdict": "confirmed"|"not_confirmed"|"unclear", "cited_is_unpublished": true|false, "treats_as_binding": true|false, "same_case": true|false, "explanation": "<one line, <= 45 words: what the citing court did and why the limb holds or fails>"}

Reply only with the number of lines written.

# Pattern

UNPUBLISHED OPINION TREATED AS BINDING. Limbs: (1) cited_is_unpublished: the cited decision really is an unpublished / non-precedential / table / summary-order / memorandum disposition that its court's rules make non-binding (check the CITED DECISION block: a full reasoned opinion printed in an official reporter is published, whatever our data says); (2) treats_as_binding: the citing court says or plainly treats it as binding or controlling precedent it must follow ("we are bound by", "controls", "forecloses", "under our precedent in"), not merely as persuasive, illustrative or consistent authority; (3) same_case = false (not law of the case / res judicata in the same litigation). confirmed iff 1 and 2 hold and 3 is false.
