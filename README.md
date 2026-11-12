# Git for Global Law

**The world's law in one git history. Every word traced to the law that wrote it for any country and any date.**

An expansion of the same for the US Code, [#1 on Hacker News (28/10/26)](https://news.ycombinator.com/item?id=50268380).
Semantic, searchable law on a global scale.

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

## Case law

Court decisions sit beside the law in `<country>/<court>/caselaw`, one file and one commit per published decision,
dated the day it was decided. `manifest.json` gives each corpus's court, coverage and gaps; where a source's licence
asks for credit, the tools show it as a `Credit:` line.

A decision is a ruling, not a law (`Kind: court`), so the tools leave case law out of everything about law (`laws`,
searches, change lists) unless you name it. Each corpus also files, under the law's own paths, the decisions that cite
each article, with the version of the law in force on the day decided.

```
python tools/countries.py add netherlands/caselaw                   a country's case law (not added with the country)
python tools/law.py laws 2024-01-01 2024-01-31 netherlands/caselaw   decisions given in a window
python tools/law.py caselaw-index                                   after a pull: index the case law checked out
```

From an assistant, `check_precedent` lists the decisions that applied a provision and says whether the text each one
applied is still in force, and `what_else_changes` counts them. `find_provision` and `law_details` take a court's own
references (an ECLI, a docket or case number, a reporter citation), and `resolve_citations` reads citations of law in
each country's usual form (`Art. 336 OR`, `§ 823 Abs. 1 BGB`, `article 1240 du code civil`).

## More

- [FEATURES.md](FEATURES.md): every feature, and what every corpus here must support (`git blame`, `law.py`, the MCP tools)
- [FAQ.md](FAQ.md): questions and answers · [CONTRIBUTING.md](CONTRIBUTING.md): proposing changes · [MCP.md](MCP.md): the MCP server · [REPRODUCE.md](REPRODUCE.md): how it was built · [CHANGELOG.md](CHANGELOG.md)
- [FRESHNESS.md](FRESHNESS.md): how current each corpus is · [MONITORING.md](MONITORING.md): whether updates are running · [WATCHING.md](WATCHING.md): how each official source is watched for changes
- [performance/](performance/): how fast the tools are, measured
- [visualisations/](visualisations/): charts and bridges across the world's law
- [Vulnerabilities](vulnerabilities/): Mistakes in legislation as published
- Tests: `python -m unittest discover -s tests`

## Videos

[See all videos](videos/)

https://github.com/user-attachments/assets/6020acb1-53f3-4b65-94a4-fe132b867358

https://github.com/user-attachments/assets/3e3076d7-cfb4-4e0a-8552-2926a630fc8e

How updates are checked and pinned every 15 minutes ([MONITORING.md](MONITORING.md)); [how each figure in the film was counted](tools/monitoring-film/):

https://github.com/user-attachments/assets/ebfea880-c7f7-4310-b8fb-b64849811fe3

## License

This repository is [CC0](LICENSE.md). The law text is in each country's repository, under that repository's own terms.
