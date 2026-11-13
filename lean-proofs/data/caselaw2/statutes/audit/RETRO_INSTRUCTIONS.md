# Hand read: when does a law's amendment of one US Code section take effect, and does it reach back?

Each item names a public law, one US Code section it amended, and the local file holding the law's text (govinfo HTML;
read it with the Read tool, in parts if long; search it with Grep for "effective", "apply", "applies", "pending",
"as if", "take effect", the section number, and the amending section). Do not fetch anything from the web.

For each item:
1. Find the law section(s) that amend that US Code section.
2. Find every effective-date / applicability / savings provision that covers that amendment (by "the amendments made by
   this section/subsection/title/Act", or by naming the amending section). If none, the amendment takes effect on the
   approval date ("Approved ..." at the end of the law).
3. Record:
   - `effective_date`: YYYY-MM-DD the amendment takes effect.
   - `retro_class`, one of:
     - `prospectiveOnly`: the law limits the amendment to conduct, claims, cases, filings or taxable years on or after a date at or after enactment, or says it does not apply to pending cases;
     - `appliesToPendingCases`: it applies to cases or claims pending on (or after) some date, reaching conduct before enactment;
     - `retroactiveToDate`: it reaches back to a date before enactment ("as if enacted on ...", taxable years beginning before enactment, conduct "before, on, or after");
     - `asIfIncluded`: a technical or conforming correction effective as if included in an earlier law;
     - `noProvision`: nothing on timing covers it (default: effective on enactment).
   - `retroactive_to`: YYYY-MM-DD, the earliest conduct/claim date reached when earlier than enactment, else "".
   - `quote`: the deciding words (<= 300 chars) or "".
   - `why`: one sentence.
Write a JSON list of objects with keys `key, effective_date, retro_class, retroactive_to, quote, why` (copy `key` exactly)
to the output file you were given. Reply with only a count of classes.
