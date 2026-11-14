# orderdock LEAN_REQUEST (optional; the rows do not wait for it)

Written 14 Nov 2026 00:47. Status: **not blocking**. Every orderdock row certifies under the round-7 checker as it is
(history rows; `name:` evidence = party-name tokens the order's caption shares with the target's title, found in the
order's own text within 400 characters of the disposition quote; `cite:` evidence for "Reported below" entries,
alias forms through the existing `alias` path; claim `orderHead` for head-matter orders >= 2013). What the checker
cannot verify today is *why* the target is the decision below when the link comes from a bridge text. This request
would let it verify that.

## Finding (why not `docket:`)

The corpus gives a Supreme Court order only its own docket number ("No. 15-1052."), never the lower court's; the
lower decisions carry their own docket (cache meta). A docket number links the two only through a third text, and
such texts are rare: of 52,264 subsequent-history strings in the 738,887 decisions dated >= 2013, about 200 links
use a Supreme Court docket number ("cert. denied, No. 15-375 (U.S. ...)"); the rest name the order by its page
("cert. denied, 136 S. Ct. 890"). So a `docket:<no>` evidence form would carry very few rows; the general bridge is
the subsequent-history string.

## Rule

Evidence `bridge:<W>:<s>:<e>` on a history row (by = order O, target = X): a quote [s, e) of a third decision W
(any court, dated after O), read and hash-checked like any quote (`cert_text` / `window_sha`), such that
1. the quote is one citation clause (no ";"), at most 600 characters;
2. it contains the compact citation of X (the index maps it to X; `cite_index`, as `anchorResolves`);
3. after that citation, a history cue of the row's kind (new cue-table list `bridge_cue`: certDenied "cert. denied",
   "certiorari denied"; vacated "vacated", "judgment vacated"; reversed "rev'd", "reversed"; affirmed "aff'd",
   "affirmed"; reviewDismissed "cert. dismissed", "appeal dismissed");
4. after the cue, a compact citation that is one of O's own citations (decisions2 citations of O) or O's docket
   number ("No. <docket of O>"), and no other Supreme Court citation in a reporter O carries;
5. the row's main quote is still O's own disposition (plain / orderHead checks unchanged): the act is the acting
   court's words; the bridge only identifies the decision below.

## Check / effect / theorem

- New table `history_bridge.tsv` (id, W, s, e, quote, src), joined like `history_anchor`; absent table => output
  byte-identical to `round7/out/v3`.
- Effect: the ~6,300 new bridge rows (orderdock `cert_bridge`) would carry a verified link instead of a linker note.
- Theorem `bridge_sound`: an admitted row with a bridge line has a W-quote that resolves X by citation, holds a cue of
  the row's kind after it and resolves O by one of O's own citations / its docket after the cue; `bridge_no_table`:
  without the table nothing changes. Mutants: accept another order's page on the same reporter page; drop the cue;
  accept the order citation before X's citation; accept a ";" inside the clause.
