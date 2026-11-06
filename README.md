# Git for Global Law

**The world's law in one git history. Every word traced to the law that wrote it for any country and any date.**

An expansion of the same for the US Code, [#1 on Hacker News (28/10/26)](https://news.ycombinator.com/item?id=50268380).
Semantic, searchable law on a global scale.

[![monitor](https://github.com/lexifina/global-law/actions/workflows/monitor.yml/badge.svg)](https://github.com/lexifina/global-law/actions/workflows/monitor.yml)

<!-- status-summary -->
**Updates: running**, last published 2026-11-06 15:15 UTC, 31 corpus updates in the last 24 hours ([data/status.json](data/status.json)). **Freshness:** 619 of 714 corpora current, 0 pending a change, 81 stale, 14 unverified; 85.3% checked against their official source in the last 7 days ([data/freshness.tsv](data/freshness.tsv)).
<!-- /status-summary -->

**Is it true right now?** Every corpus records when it was last checked against its official source, and every answer
about today's law says how current it is: [how current is it](#how-current-is-it). **Does it keep up?** Each country's
pipeline publishes new law as it takes effect, and this repository picks it up every 15 minutes, watched hourly from
GitHub: [is it being updated](#is-it-being-updated).

https://github.com/user-attachments/assets/f24f3411-24d9-416a-8c45-9cebc817c64e

**Free to use: [CC0](LICENSE.md).** Fork it, build on it, ship it in a product: no permission or credit needed. The law text
sits in each country's repository, under that repository's own terms.

Each jurisdiction's law is its own repository, `lexifina/<country>-law`, where every commit is one law taking effect,
written by that law. This repository holds them all as submodules, arranged by jurisdiction, and moves each one forward
to its latest commit. The tools read the `In-force` date of every commit, so they give the law of any country on any
date.

```
global-law/
├── manifest.json              every corpus: path, repository, coverage and dates
├── jurisdiction.json          the world, and the jurisdictions in it
├── germany/bund/acts/         a country's law (submodule)
├── brazil/bahia/acts/         a state's
├── brazil/bahia/salvador/acts/  a city's
└── …
```

## Start

```sh
git clone --depth 1 https://github.com/lexifina/global-law && cd global-law
python3 tools/countries.py add united-states/federal/usc   # one corpus; every country is several GB
python3 tools/law.py show 2022-05-01 united-states/federal/usc/title-11/1182.md
```

On Windows, type `py` or `python` where these say `python3`.

`--depth 1` downloads the index without its whole history, a fraction of the size. The tools never read that
history, so they work the same. To have it without its file contents, clone with `--filter=blob:none` instead. For
every country, add `--recurse-submodules`. Don't clone a country's repository with `--depth`: its dates are read from
its whole history, and `countries.py add` fetches all of it.

## From an AI model (MCP)

`tools/mcp_server.py` is a Model Context Protocol server with <!-- fig:tools -->18<!-- /fig --> read-only tools: find a provision, read it on a date,
who wrote each word, compare dates, a provision's history, search the text and the changes, and check a case or a
brief against the law in force. It needs only Python 3.9+ and git, runs on your machine and makes no network calls.

The clone carries the setup for Claude Code, Cursor, VS Code and Codex, so the server starts when you open the folder.
For another client:

```json
{ "mcpServers": { "global-law": { "command": "git", "args": ["-C", "/path/to/global-law", "-c", "alias.global-law-mcp=!sh tools/mcp.sh", "global-law-mcp"] } } }
```

Then ask, for example, "What did 11 U.S.C. §1182(1) say on 1 May 2022, and which law last changed it?" [MCP.md](MCP.md)
has every tool and the details.

## Command line

```
python tools/law.py world 2022-05-01                       every corpus on that day
python tools/law.py show 2022-05-01 <path>                 a provision on a date
python tools/law.py blame 2022-07-01 <path>                the law behind each line
python tools/law.py words 2022-07-01 <path>                the law behind each word
python tools/law.py diff 2022-05-01 2022-07-01 <path>      what changed between two dates
python tools/law.py laws 1990-01-01 1990-12-31 germany     the laws that took effect
```

Dates are YYYY-MM-DD. The first read of a corpus indexes its history once and keeps the index in
`.git/global-law-cache`.

- A corpus moved to a new folder still answers under its old path (`data/moved-paths.tsv`). After a pull that moves
  corpora, run `git submodule sync` and `git submodule update --init`.
- `manifest.json` and the `jurisdiction.json` files are written by `tools/describe.py`.

## How current is it

Law changes after a corpus is built, so every corpus says when it was last checked against its official source.
`data/freshness.tsv` has one row per corpus: its status, the day of its last check (`last_verified`), how it was
checked, when the next check is due, the commit pinned here and, for corpora that check every act (Romania), the acts by
status. Answers from the MCP server about a date on or after a corpus's last check say how current it is.

<!-- freshness-summary -->
Checked against the official sources: 85.3% of 714 corpora in the last 7 days, 98.0% in the last 30 ([data/freshness.json](data/freshness.json), as of 2026-11-06).
<!-- /freshness-summary -->

```
python tools/freshness.py romania/national/acts                        a corpus: status, last check, official source
python tools/freshness.py romania/national/acts/lege/2009/287/art-1112.md   a provision: its act's own row, if published
python tools/freshness.py --stale                                      corpora not checked within their threshold
python tools/freshness.py --summary
```

| Status | Meaning |
| --- | --- |
| `current` | checked within its threshold, and this repository holds the corpus's newest commit |
| `pending-change` | the corpus has a newer commit than the one pinned here (held back by a check, or not yet pinned) |
| `stale` | last checked longer ago than its threshold |
| `unverified` | never checked against its official source after it was built |
| `source-unavailable` | due for a check, but the official source is not answering |

The threshold is 7 days for a country's own law and 30 days for sub-national and municipal law, unless a corpus states
its own. The tool works offline from these files: to be certain, open the official source it names.

How each corpus is checked (`method`):

| Method | What it means |
| --- | --- |
| `act-checks` | the corpus checks every act against its official source and publishes a row per act: status, last check, the newest change the source reports and whether it is in the record yet, and the official link. [Romania's repository](https://github.com/lexifina/romania-law#how-current-is-it) does this today; once a pinned commit carries those rows, `tools/freshness.py <path>` and the MCP answers give a provision's own act row |
| `source-retrieval` | the day the corpus's build last read its official source; a change published at the source after that day is not known until the next read |
| `stated` | the day the corpus states it was last checked |

From an AI model: `read_law` adds a note whenever the date asked is on or after the record's last check, for example
"united-states/federal/usc: stale, last checked against its official source on 2026-10-27 (10 days ago); later changes
may be missing", or, for a Romanian act, its status, the change the official source reports that is not here yet, and
the official link to check by hand.

Only each country's official publication has legal force; no text here does.

### Is it being updated?

New law reaches this repository in two steps, and both are watched:

1. **Each country's pipeline** reads its official source and publishes each new act or change as a commit dated the
   day it takes effect. Where a pipeline polls its source (from every 3 hours to daily, by source), its checks show
   in the freshness data above; a corpus whose source has not been read again within its threshold shows as `stale`,
   never as `current`.
2. **Every 15 minutes, a pass here** finds every corpus with a newer commit, checks that commit
   (`tools/check_corpus.py`: a commit that breaks the record is held back, never pinned), moves the pins forward,
   rewrites `data/freshness.tsv`, `data/freshness.json`, `data/status.json` and the status line at the top of this
   page in the same commit, and then verifies the whole history (`tools/verify.py`: pins only move forward).

[data/status.json](data/status.json) is the public record of that loop:

| Field | Meaning |
| --- | --- |
| `updates` | `running` while a pass has succeeded in the last 45 minutes, else `stalled` |
| `last_published`, `last_successful_pass` | when the newest commit reached this repository, and the last pass that worked |
| `published_last_24h` | commits, corpora moved and corpora added in the last 24 hours |
| `held_back` | corpora whose newest commit failed a check, so this repository keeps the last good one |
| `freshness` | the corpora by status, as in `data/freshness.tsv` |
| `official_sources_unavailable` | official sources a corpus's pipeline reports as not answering, and since when |

The [monitor](.github/workflows/monitor.yml) runs every hour on GitHub, apart from the machines that publish:
`python tools/freshness.py --health` fails when `data/status.json` has not been refreshed for 2 hours, updates have
stalled, or freshness has not been recomputed for a day. A failure alerts the maintainers and turns the badge at the
top of this page red. You can run the same check on any clone.

## How it is made

The repository's history only grows: each commit adds corpora, moves their pins forward, or changes the tools and
documentation. `tools/verify.py` checks it. Up to 29 October 2026 it was built from scratch as one commit per law in
the order the changes took force; that history is kept, frozen, and [REPRODUCE.md](REPRODUCE.md) records how it was
made.

## More

- [FAQ.md](FAQ.md): questions and answers · [CONTRIBUTING.md](CONTRIBUTING.md): proposing changes · [MCP.md](MCP.md): the MCP server · [REPRODUCE.md](REPRODUCE.md): how it was built · [CHANGELOG.md](CHANGELOG.md)
- [performance/](performance/): how fast the tools are, measured
- [visualisations/](visualisations/): charts and bridges across the world's law
- Tests: `python -m unittest discover -s tests`

## Videos

https://github.com/user-attachments/assets/6020acb1-53f3-4b65-94a4-fe132b867358

https://github.com/user-attachments/assets/3e3076d7-cfb4-4e0a-8552-2926a630fc8e

## License

This repository is [CC0](LICENSE.md). The law text is in each country's repository, under that repository's own terms.
