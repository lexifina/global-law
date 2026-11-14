# Agent `calpart9` (round 9): the part map — old-California headers, and the zone table for the Lean (move 3)

Read `round9/DESIGN9.md` (§0–4; §4 is the Lean rule your zone table feeds) and `round9/agents/COMMON.md`. Folder
`round9/agents/calpart9/` (NOTES.md). Round 8's `round8/agents/calpart/` (NOTES.md, `scan_parts.py`, `partfix.py`,
`work/`) went silent at 01:11 without a report: resume from what it left, but verify everything.

## Background
The reader's part map (`common.part_map` / `part_map2`; consumers: treatments reader `part` field and
`separate-opinion` rejects, round-6 history scan `r6scan.scan_text`, which drops records in `concurrence~`) opens a
false separate opinion on header vote notes: old California "Burnett, J., delivered the opinion of the Court / Terry,
C. J., and Field, J., concurring."; Ohio App. "Shields, J.; / Voorhees and Powell, JJ., concurring."; CA9 en banc vote
lines; CA9 F.3d head notes "Opinion by Judge X; Concurrence by Judge Y.". Round 8 found 607 decisions with candidate
sentences lost this way. Today the Lean checks a row's `part` only as a field (in {majority, plurality, perCuriam}),
never against the text.

## Do
1. A general part-map fix: a vote/concurrence note that is part of the head matter or the opinion's opening
   attribution (short line, judge marks, "concurring" with no opinion text following before the next opinion mark /
   before the court's text resumes) does not open a separate opinion. Measure corpus-wide how many decisions'
   zones change and how (`old → new` part of characters), and read a stratified sample (~40, opus readers) of the
   changed decisions: is the new zone right?
2. Rows recovered: re-run the readers/linkers that consume parts (treatments reader candidates with
   `separate-opinion` rejects; round-6 history scan) on the changed decisions only; certify (`round9/certify9.py`);
   blind audit the new rows (≥ 80 or all, two auditors, decoys); install at ≥ ~90%.
3. The zone table for DESIGN9 §4: `part_zone.tsv` (node, z_start, z_end, part, src) with the FIXED part map, for
   every acting node of every row in `round8/stage/v8e` (treatments + history) and in your own delta; offsets in the
   same space as the rows' start/end (verify on a sample that every admitted v8e row's quote text equals the text at
   its offsets and that the row's part equals the zone's part; report the disagreements: how many v8e rows would the
   zone check refuse, by part pair and court, and read ~30 of them: is the row's part field or the zone wrong?).
   Put it in a delta folder as `part_zone_delta.tsv` (stage9 treats it as an extra table). Write the readings you
   need from the Lean side (e.g. zones that do not cover a quote, quotes across a zone boundary, footnotes) into
   `LEAN_REQUEST.md`; the lead passes them to `lean9`.
Report: the fix, zone-change counts, sample readings, recovered rows + audit, the zone table + v8e disagreement counts.
