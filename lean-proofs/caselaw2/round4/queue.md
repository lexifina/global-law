# Round 4 item 6: reader queue, the 11 answered packs (fork `queue4`, 23:17-23:20, 12 Nov 2026)

- `packs/ans_142.jsonl` (59 of 80) renamed `ans_142.partial`; `check.py`: files 152, bad = [].
- `t:6865583:6852906:48056` was already absent from live data at the start (its reject line was present).
  `install.py` re-certifies every answer and re-added it; removed again under the lock. `install.py` has no
  exclusion list: any later run re-adds audit-removed rows (also the two below) unless they are filtered.
- `install.py` (certify2.py unchanged): 2,700 certified over 152 packs, all kept after the window recut.

| Live file | Before | After install | After removals |
|---|---|---|---|
| treatments.tsv | 35,021 | 35,185 | 35,182 |
| treatments_items.tsv | 35,021 | 35,185 | 35,182 |
| cert_text.tsv | 82,454 | 82,599 | 82,599 |
| window_sha.tsv | 339,060 | 339,204 | 339,204 |
| reader_rejects.tsv | 51,013 | 51,749 | 51,751 |
| cite_index.tsv | 45,650 | 45,724 | 45,724 |

- Net new rows from the 11 packs: 161 (163 before the audit): overruled 136, disapproved 12, declinedToFollow 9,
  questioned 2, abrogated 1, distinguished 1. Backup of the file before this item: `work/round4/treatments.pre_queue4.tsv`.

## Blind audit F (20 of the 163 new rows; `work/round4/queue/F_pack_{0,1}.txt`, `F_key.tsv`)

Read by the fork itself from the window text before opening the key (a fork cannot spawn subagents).

- Own act of a court speaking for itself: 18/20 (Wilson 95%: 70%-97%). Wrong: `t:301338:795345:4481` (First Circuit
  says a Fourth Circuit case is "no longer authority" after *Jones & Laughlin*) and `t:1462123:1686799:46379`
  (Ninth Circuit: the California *Broughton-Cruz* rule "no longer viable post-Concepcion"). Both labelled
  `overruled`; neither court has power, so both would only have been `noAuthority` / `claim` rows. Both removed,
  reject lines `audit / not-own-act:queue-audit-round4` added.
- Target right: 20/20 (84%-100%).
- Kind equal: 13/20 (43%-82%). Overruled-vs-disapproved confusion: 0 of 20. The 5 other differences are one shape:
  a circuit panel says its own precedent "is no longer good law" in light of an intervening Supreme Court decision;
  the row says `overruled`, the auditor says `abrogated` (items 3, 5, 12, 18, 19). Status effect is the same, but
  each such row is a likely `panelDepartsWithoutEnBanc` finding that is not a departure (item 7).

## Left
- 246 unread packs (incl. 142). Not measured (`measure.py` not run).
