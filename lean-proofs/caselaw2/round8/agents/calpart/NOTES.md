# calpart notes (round 8): opinions of the court mislabelled `concurrence~` by the part map

## Log
- 01:05 Started. Read DESIGN8 §0, COMMON, BRIEF, state8 NOTES (its PF repair already re-classified
  `separate-opinion` rejects in a short (< 400 chars) majority head + `concurrence~` cut, 25 tagged candidates).
- 01:08 Where parts come from: reader `common.part_map` / `part_map2` (hard-wrapped texts): inside a Majority /
  Per Curiam / Combined section, a short line (<= 160 chars) with a judge mark and "concurring|concurrence|dissent..."
  and no opinion word (filed, joined, delivered, ...) opens `concurrence~` / `dissent~` to the next mark. Consumers:
  treatments reader candidates (`part` field; `separate-opinion` reject), round-6 history scan `r6scan.scan_text`
  (drops `cw` / `pw` / `h` records in `concurrence~`; zone `open` / `ends` take only opinion parts), so the history
  linkers never saw these decisions' disposition. Lean: the row's `part` is a row field checked to be in
  {majority, plurality, perCuriam} (certify6 PARTS); no text check, so no Lean change is needed for relabelled rows.
  Forms seen: (A) "Burnett, J., delivered the opinion of the Court / Terry, C. J., and Field, J., concurring."
  (old Cal.), "Shields, J.; / Voorhees and Powell, JJ., concurring." (Ohio App.), en banc vote line "CHIEF JUDGE HUG,
  ... concurring; ... concurring in parts I, II and IV, and in the judgment." (CA9); (B) index note "Opinion by Judge
  X; Concurrence by Judge Y." (CA9 F.3d head).
