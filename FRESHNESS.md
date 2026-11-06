# Freshness: how current each corpus is

<!-- freshness-summary -->
**619 of 714 corpora current**, 0 pending a change, 81 stale, 14 unverified; 85.3% checked against their official source in the last 7 days, 98.0% in the last 30 (as of 2026-11-06).
<!-- /freshness-summary -->

Every corpus records when it was last checked against its official source: one row each in
[data/freshness.tsv](data/freshness.tsv), totals in [data/freshness.json](data/freshness.json). When you ask about a
date on or after that check, the MCP server's answers say how current the text is.

```
python tools/freshness.py <corpus or provision path>    status, last check, official source
python tools/freshness.py --stale                       corpora past their threshold
python tools/freshness.py --summary
```

| Status | Meaning |
| --- | --- |
| `current` | checked within its threshold (7 days for national law, 30 for sub-national), and the newest commit is pinned |
| `pending-change` | the corpus has a newer commit than the one pinned here |
| `stale` | not checked within its threshold |
| `unverified` | never checked against its source after it was built |
| `source-unavailable` | due for a check, but the official source is not answering |

Corpora that check every act publish a row per act, with any change the source reports that is not here yet
([Romania](https://github.com/lexifina/romania-law#how-current-is-it)); `tools/freshness.py` reads them for a
provision in a checked-out corpus. Only each country's official publication has legal force.
