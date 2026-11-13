You are auditing candidate findings about US court decisions. The items in this directory are a MIX: some are
believed to be true instances of the pattern below and some are not. You are not told which. Judge every item only on
the decision text given in its file (and your own knowledge of the law and of the named cases where the file is
silent; say so in the explanation when you rely on it). Be strict: `confirmed` means every limb of the predicate is
shown; `not_confirmed` means a limb fails; `unclear` only when the text given cannot settle it.

Read every item file I*.txt in this directory in full. Use only the Read and Write tools; no web, no scripts, no other
files. Then write ONE file `answers.jsonl` in this directory, one JSON object per line, one line per item:

    {"id": "Inn", "verdict": "confirmed"|"not_confirmed"|"unclear", "departs": true|false, "bench": "panel"|"en_banc_or_full_court"|"unclear", "recognised_exception": true|false, "explanation": "<one line, <= 45 words: what the citing court did and why the limb holds or fails>"}

Reply only with the number of lines written.

# Pattern

PANEL OVERRULES PANEL WITHOUT EN BANC. Limbs: (1) departs: the later decision itself overrules, abrogates, recedes from, disapproves or refuses to follow the holding of an earlier published decision OF THE SAME COURT (same district or division where precedent binds only within it) - not merely distinguishes or limits it, and not a decision of a different court or district; (2) bench = panel: the later decision was decided by a panel, not by the court en banc / in bank / as a whole court (look at the judges line and any 'en banc' marking; a court whose every case is heard by all its judges is full court); (3) recognised_exception = false: the opinion gives no recognised ground for a panel to depart (intervening Supreme Court / higher-court / en banc authority, a change of statute or rule, circulation to or approval by the full court, the earlier case being contrary to even earlier binding precedent, dicta, unpublished); (4) the court followed a prior-panel rule and had an en banc procedure at the time (use your knowledge; if it did not, say so and answer not_confirmed). confirmed iff all hold.
