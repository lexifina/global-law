# round12/data_orders: what infra12 loads (round12/nodes12.py, stage12.py --nodes round12/data_orders)

Written by `infra12` (14 Nov, round 12) for `orders12` / `shadow12`. Same format as `round11/data_orders/FORMAT.md`
(nodes.tsv 7 columns + header, text/<local id>.txt, LF only, text_sha = sha1 of the text file bytes), with three
round-12 points:

1. **Round 11's 1,045 rows first, same local ids, same order.** `stage12.py --nodes` refuses the folder otherwise
   (it compares with `round11/stage/v11d/nodes_map.tsv`); they then keep node ids 6,892,454..6,893,498. Appended nodes
   get 6,893,499, 6,893,500, ... in file order. Never reorder or delete a row once shadow12 has certified rows on it.
2. **Optional 8th column `src`** (header name exactly `src`, after `line_span`): the provenance tag of the node's
   decisions2 row, `[A-Za-z0-9_.:-]+`, e.g. `r12:longlist`; `-` (or no column) = `r11:orderlist` (round 11's rows
   byte for byte). The row's src field becomes `c:self;u:-;b:default-scotus;p:<src>;f:<src>`. Either every row has
   the column or none.
3. **Changed texts keep their local id** (DESIGN12 section 4, ligature repair): list each in `CHANGED.tsv` (local id,
   old sha1, new sha1, what changed). stage12 recomputes text_sha from the new file, prints which of the first 1,045
   texts changed and counts the v11d rows whose acting node is one of them (those rows must be re-certified by
   shadow12 and dropped / replaced with `--drop` / `--replace`).

Check a folder: `python -X utf8 round12/nodes12.py --check round12/data_orders`.
