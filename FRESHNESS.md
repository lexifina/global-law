# Freshness: is it true right now?

Law changes after a corpus is built. Every corpus here records when it was last checked against its official source,
so an answer about today's law can say how current it is.

<!-- freshness-summary -->
**794 of 980 corpora current** on 2026-11-11: 45.0% checked against their official source in the last 7 days, 98.6% in the last 30.

| | Corpora | Current | Pending a change | Stale | Unverified | Checked in 7 days |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All | 980 | 794 | 5 | 167 | 14 | 45.0% |
| National | 379 | 201 | 3 | 167 | 8 | 53.3% |
| Subnational | 601 | 593 | 2 | 0 | 6 | 39.8% |

National law longest since a check: `aland/national/acts` (2026-10-28), `angola/national/acts` (2026-10-28), `armenia/national/acts` (2026-10-28), `austria/bund/acts` (2026-10-28), `azerbaijan/national/acts` (2026-10-28), `bermuda/national/acts` (2026-10-28).

Never checked: `andorra/national/acts`, `bangladesh/national/acts`, `costa-rica/national/acts`, `germany/bund/acts`, `pakistan/national/acts`, `san-marino/national/acts`, `switzerland/bund/acts`, `tuvalu/national/acts` and 6 more.
<!-- /freshness-summary -->

## Check one

```
python tools/freshness.py united-states/federal/usc                  a corpus: status, last check, official source
python tools/freshness.py <corpus>/<path to a provision>             a provision: its act's own row, where published
python tools/freshness.py --stale                                    every corpus past its threshold
```

The MCP server does this for you: when the date asked is on or after a corpus's last check, `read_law` ends with a note
such as "united-states/federal/usc: stale, last checked against its official source on 2026-10-27 (10 days ago); later
changes may be missing".

## What the statuses mean

| Status | Meaning | What to do |
| --- | --- | --- |
| `current` | checked within its threshold, and its newest commit is pinned here | rely on it as far as any consolidated text goes |
| `pending-change` | the corpus has a newer commit than the one pinned here | read the corpus's own repository, or wait for the next pass |
| `stale` | not checked within its threshold (7 days for national law, 30 for sub-national) | confirm against the official source |
| `unverified` | never checked against its source after it was built | confirm against the official source |
| `source-unavailable` | due for a check, but the official source is not answering | confirm once the source is back |

`last_verified` is the day of the last check (`act-checks`: every act checked, as
[Romania](https://github.com/lexifina/romania-law#how-current-is-it) does; `source-retrieval`: the day the build read
the source; `stated`: the day the corpus states). Rows: [data/freshness.tsv](data/freshness.tsv); totals:
[data/freshness.json](data/freshness.json). Only each country's official publication has legal force.

To replace build dates with daily checks, each corpus can watch its official source for changes: see
[WATCHING.md](WATCHING.md).
