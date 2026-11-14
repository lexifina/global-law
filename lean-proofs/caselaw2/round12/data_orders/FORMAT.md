# round11/data_orders: the format infra11 loads (DESIGN11 section 4)

Written by `infra11` for `orders11` (05:22). `orders11` writes, `infra11` loads (`round11/stage11.py --nodes
round11/data_orders`, `round11/nodes11.py`). If something here does not fit the source, write the question at the
end of this file (section "Questions") and infra11 adapts the loader; do not change the column order silently.

## nodes.tsv

UTF-8, LF line ends, no BOM, tab-separated, **first line is the header** exactly:

```
local_id	docket	date	caption	disposition	list_file	line_span
```

One line per order-list entry that disposes of a case (one node per docket entry, as the S. Ct. reporter prints a
memorandum order; cert-denied-only entries may be skipped). No tab, CR or LF inside a field; no empty field (use `-`).

| column | content |
|---|---|
| `local_id` | your stable id, `[A-Za-z0-9_.-]+`, unique in the file, e.g. `ol20211004_0012` (list date + entry number). It is also the text file name. Never reuse an id for another entry. |
| `docket` | the docket number(s) as printed, e.g. `20-1234`; several (consolidated entry) separated by `;` with no space, e.g. `20-1234;20-1235`. |
| `date` | the order date `yyyymmdd` (the list's date heading). |
| `caption` | the caption as printed on the list (e.g. `SMITH, JOHN V. JONES, WARDEN`), whitespace collapsed to single spaces. |
| `disposition` | the disposition words as printed, short (e.g. `GVR`, `The petition for a writ of certiorari is granted. The judgment is vacated, and the case is remanded ...` may be shortened to its first sentence). For information only; the rows' kind comes from `shadow11`'s rules over the text file. |
| `list_file` | the source list it came from, as named in `SOURCES.tsv` (file name or URL key). |
| `line_span` | `<first>-<last>` line numbers of the entry in your text of that list (1-based). |

Rows are loaded in file order; node ids are assigned N, N+1, ... in that order (N = the corpus node count,
`graph/nodes.count` = 6892454). Keep the order stable between versions (append new entries at the end) so node ids
do not move under rows already written by `shadow11`; infra11 writes `nodes_map.tsv` (local id -> node id) into each
stage, and `round11/nodes11.py` gives the same mapping to every tool.

## text/<local_id>.txt

The node's own text: **the list's date heading line, then the caption line(s), then the entry's disposition
sentence(s) verbatim**, as printed (no editorial words of yours, no headers you invented). UTF-8, LF only, no BOM, no
tabs (replace a tab by one space), ends with exactly one LF. Nothing else in the file: certificates quote this text by
character offsets and its SHA-1 (`sha1` of the file bytes, the way the corpus's `text_sha` is computed:
`tools/caselaw2/holdings/text.py` `text_sha(raw) = sha1(raw)`) keys the windows, so a file must never change after
rows cite it (a corrected text = a new local id).

Example `text/ol20211004_0012.txt`:

```
MONDAY, OCTOBER 4, 2021
CERTIORARI -- SUMMARY DISPOSITIONS
20-1234 SMITH, JOHN V. JONES, WARDEN
The petition for a writ of certiorari is granted. The judgment is vacated, and the case is remanded to the United States Court of Appeals for the Fifth Circuit for further consideration in light of Doe v. Roe, 593 U. S. ___ (2021).
```

## What infra11 makes of it (for information)

decisions2 row per node: `node, 2906 (Supreme Court of the United States), date, unit 0, bench wholeCourt,
publication published, form memorandum, text_sha = sha1(text file), src c:self;u:-;b:default-scotus;p:r11:orderlist;f:r11:orderlist`
(the shape of the corpus's S. Ct. memorandum decisions; the src marks the provenance).

## Questions

(none yet)

## Round 12 addition (orders12; loader round12/nodes12.py by infra12)

`nodes.tsv` carries the optional 8th column `src` (header `src`): `-` = the default `r11:orderlist` (rows 1-1,045, byte
for byte round 11's decisions2 src), `r12:longlist` = per-entry nodes of step 3 (README.md). decisions2 src for a row
with a tag: `c:self;u:-;b:default-scotus;p:<src>;f:<src>`. Text files whose content changed in round 12 keep their
local id (DESIGN12 §4); they are listed in `CHANGED.tsv` (old and new sha1).
