# calpart9 -> lean9 (via the lead): readings of DESIGN9 section 4 from the real zone table

Table: `round9/agents/calpart9/zone_delta/part_zone_delta.tsv` (5 columns, no header, LF; built by
`build_zones.py` = `partzone.zones`: reader `common.part_map2` for every text + rules PJ / PJ-V of `partfix.py`;
zones cover [0, len(text)) of each text-owner node, touching, never overlapping; adjacent zones of one part merged).
Text owner per D9-4: treatments `by`; the witness node for a row with a `treatment_witness.tsv` line (6,607 rows);
history `by`, or `target` when the row's `text_sha` is the target's (0 such rows in v8e: every v8e history row's
text_sha is the by node's). Every v8e quote (230,594 main + joined) equals `norm(text[start:end])` of git HEAD and
the row's text_sha equals the git-HEAD sha, so the offsets are the zone offsets.

## Facts the Lean side needs

1. **Straddles exist and are real** (200 admitted v8e history rows, src `hist-regex-v2:long:*`, federal courts of
   appeals 1920s-2000s): the quote runs from the head matter ("... Before X, Y and Z, Circuit Judges.") across the
   `## Majority` heading line into the opinion. The cue is in the opinion part in all 200 (7 also in the head).
   Fix on the data side (calpart9 rule RC, `recut.py`): 137 re-cut to the opinion part and re-certified
   (`cert_recut/`, 15 of them anchored on the head-matter part), the 137 old ids removed (`cert_recut/remove_ids.txt`).
   63 stay refused by the zone check (`partZone`): their evidence is only in the head matter, > 400 characters away.
   No Lean change needed: refusing a quote that straddles is the intended reading (mutant 1).
2. **Part names across the court's opinion**: 14 admitted SCOTUS history rows say `majority` where the zone says
   `perCuriam` (slip opinions with the running head "Per Curiam"). The zone is right; calpart9 supplies replacement
   lines with part `perCuriam` (`cert_recut/replace_part.tsv`, `--replace`). No Lean change needed (strict equality
   stays). If the lead prefers not to replace rows, the alternative is a Lean reading "majority / perCuriam /
   plurality are one class for the zone check" — not requested.
3. **Syllabus quotes**: 6 history + 3 treatments admitted rows quote the SCOTUS slip syllabus (zone `headmatter`,
   running head "Syllabus") with part `majority`. The zone check refuses them; that is right (the syllabus is not the
   court's act). Listed in `zone_delta/refused.tsv`.
4. **Joined quotes**: all 503 admitted joined quotes lie in one zone of their `j_part`.
5. **Footnotes** are not separate zones: the part map has no footnote boundary; a footnote printed inside the
   opinion of the court is in the majority zone (the readers treat it the same way). No reading needed.
6. **Anchors / bridges**: not zone-checked (DESIGN9 section 4); their nodes get zones only when they own a main quote.
7. Zone count summary (final rule PJ + PJ-V; v8e + calpart9's deltas cert_pjt, cert_pjr, cert_recut; sha1
   27465595e7c076ea8d96aef85f9e65009a2bfbbf): 208,590 nodes, 582,418 zones; parts other 208,596, majority 192,588,
   headmatter 132,945, dissent 20,151, concurrence 14,004, perCuriam 12,817, plurality 1,317; src pm2 575,197,
   pm2hw 3,960, pm2+PJ 3,261; 0 malformed, 0 overlapping. The zones of the 208,557 v8e nodes are identical to the
   first drop (sha1 42a65470...); 33 nodes added for the delta rows. All 175 delta quotes (main + joined) lie in a
   zone of their part.
8. Mutant data for tests: `zone_delta/refused.tsv` lists every admitted v8e quote the check refuses (real
   straddles, part mismatches) with row and zone parts.

Expected effect on v8e (+ RC rows, + part replacement): the zone check refuses 63 + 9 = 72 admitted quotes
(0.03% of 220,955), all of them quotes whose cue or evidence is outside the opinion of the court.
