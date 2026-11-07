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

Court decisions sit beside the law, one file and one commit per published decision, dated the day it was decided:
- **Switzerland:** `switzerland/bund/caselaw` (the federal courts and bodies) and `switzerland/<canton>/caselaw` (each
  canton's courts).
- **The Netherlands:** `netherlands/<court>/caselaw` (the Hoge Raad, the Raad van State, the Centrale Raad van Beroep,
  the College van Beroep voor het bedrijfsleven, the courts of appeal and the district courts), each decision filed by
  its ECLI.
- **France:** `france/<court>/caselaw` (the Cour de cassation, the cours d'appel, the Conseil d'État and the
  administrative courts, the Conseil constitutionnel), each decision filed by its DILA id, with its pourvoi or decision
  number and ECLI in the corpus's `decision-index.tsv`. These come from DILA's open data under the Licence Ouverte 2.0,
  which requires naming the source and the date of its last update: each corpus states that credit in its corpus.json,
  and `read_law` and `list_jurisdictions` give it as a `Credit:` line.
- **Germany:** `germany/<court>/caselaw` (the Bundesverfassungsgericht, Bundesverwaltungsgericht, Bundesfinanzhof,
  Bundesarbeitsgericht, Bundespatentgericht and Bundesgerichtshof), each decision filed by its ECLI (or Aktenzeichen),
  with its Aktenzeichen in the corpus's `decision-index.tsv`. The Bundesgerichtshof's runs from 2000 (CE-BGH), with its
  criminal senates' decisions of 1950-1999 (BGH-Strafsachen-20Jhd, read from scans). The Bundessozialgericht has no
  open bulk source yet, so its case law is not here.
- **Poland:** `poland/<court group>/caselaw` (the Sąd Najwyższy, the Trybunał Konstytucyjny, the Krajowa Izba
  Odwoławcza and the common courts by appellate region; SAOS carries no administrative-court judgments), from SAOS, each judgment filed by its case
  number (sygnatura) and SAOS id, with the sygnatura in the corpus's `decision-index.tsv`. The KIO's decisions after
  SAOS's last (6 September 2018) come from the UZP portal orzeczenia.uzp.gov.pl, filed by sygnatura and portal id
  (`UZP 30001`). SAOS's record of the Sąd Najwyższy ends on 22 June 2016 and of the Trybunał Konstytucyjny on 9 December
  2015: their own sites (sn.pl, ipo.trybunal.gov.pl) cannot be read by a program, and the administrative courts'
  database (orzeczenia.nsa.gov.pl) forbids crawling its search in robots.txt, so those are not here. Judgments are
  official documents outside copyright (Art. 4 of the Polish Copyright Act).
- **The United States:** `united-states/<court>/caselaw` (the Supreme Court; the courts of appeals `ca1` to `ca11`,
  `cadc` and `cafc`), from the Caselaw Access Project (CC0), each decision filed by its official reporter citation
  (`410-U-S-113.md`), with every parallel citation (`93 S. Ct. 705`) and its docket number in the corpus's
  `decision-index.tsv`.
- **Finland:** `finland/<court>/caselaw` (the Korkein oikeus, the Korkein hallinto-oikeus and the other courts Finlex
  publishes), each decision filed by its identifier (`KKO-2023-8.md`), with its ECLI and diary number in the corpus's
  `decision-index.tsv`, Finnish text and the Swedish text where published. From finlex.fi under CC BY 4.0, credited to
  Finlex, Ministry of Justice of Finland (the `Credit:` line).
- **Austria:** `austria/<court>/caselaw` (the Verfassungsgerichtshof first; the OGH, the VwGH and the administrative
  courts as they are fetched), each decision text filed by its RIS document number, with its Geschäftszahl and ECLI in
  the corpus's `decision-index.tsv`; the Rechtssätze (headnote summaries) are not taken. From RIS under CC BY 4.0
  ("Datenquelle: RIS", the `Credit:` line). Citations of the B-VG and the DSG link to austria-law, which holds those two.

Each commit is a court ruling, not a law (`Kind: court`), so the tools credit it as one and leave it out of everything
about law (`laws`, searches, change lists) unless you name case law. Each case-law corpus also files, under the law's own
paths, the decisions that cite each article, with the version of the law in force on the day decided, and, where the
court names it (Dutch decisions often do), the version it applied:

```
python tools/countries.py add switzerland/caselaw                   a country's case law (not added with switzerland)
python tools/countries.py add netherlands/caselaw
python tools/countries.py add france/caselaw
python tools/countries.py add germany/caselaw
python tools/countries.py add poland/caselaw
python tools/countries.py add united-states/caselaw
python tools/law.py show 2024-01-01 switzerland/bund/caselaw/<decision>.md
python tools/law.py laws 2024-01-01 2024-01-31 netherlands/caselaw   decisions given in a window
```

From an assistant, `check_precedent` lists the decisions that applied a provision and says whether the text each one
applied is still the text in force; `what_else_changes` counts them; `find_provision` and `law_details` take an ECLI
(`ECLI:NL:HR:2019:1234`), a Dutch zaaknummer or LJN (`19/00135`, `200.123.456/01`, `LJN BK1234`), a Swiss docket (`4A_123/2024`), a BGE reference (`BGE 142 II 307`), a French pourvoi
(`n° 18-12.345`), Conseil constitutionnel decision (`n° 2019-791 QPC`), DILA id (`JURITEXT000041234567`), German
Aktenzeichen (`1 BvR 123/20`, `VI ZR 123/20`, `KZR 46/19`, `AnwZ (Brfg) 12/20`, `2 C 12.19`, the Bundessozialgericht's `B 2 U 1/20 R`) or Polish sygnatura (`III KK 198/16`, `K 1/12`, `KIO 1039/16`)
or SAOS id (`SAOS 245361`) or UZP portal id (`UZP 30001`); `resolve_citations` reads Dutch citations by abbreviation
(`artikel 6:162 BW`, `art. 8:69 Awb`), French ones by code (`article 1240 du code civil`, `art. L. 1235-3 C. trav.`,
`article 66 de la Constitution`) and German ones by official abbreviation (`§ 823 Abs. 1 BGB`, `§§ 280, 281 BGB`,
`§ 13 SGB V`) as it reads Swiss ones (`Art. 336 OR`).

## How it is made

The repository's history only grows: each commit adds corpora, moves their pins forward, or changes the tools and
documentation. `tools/verify.py` checks it. Up to 29 October 2026 it was built from scratch as one commit per law in
the order the changes took force; that history is kept, frozen, and [REPRODUCE.md](REPRODUCE.md) records how it was
made.

## More

- [FEATURES.md](FEATURES.md): every feature, and what every corpus here must support (`git blame`, `law.py`, the MCP tools)
- [FAQ.md](FAQ.md): questions and answers · [CONTRIBUTING.md](CONTRIBUTING.md): proposing changes · [MCP.md](MCP.md): the MCP server · [REPRODUCE.md](REPRODUCE.md): how it was built · [CHANGELOG.md](CHANGELOG.md)
- [FRESHNESS.md](FRESHNESS.md): how current each corpus is · [MONITORING.md](MONITORING.md): whether updates are running
- [performance/](performance/): how fast the tools are, measured
- [visualisations/](visualisations/): charts and bridges across the world's law
- Tests: `python -m unittest discover -s tests`

## Videos

https://github.com/user-attachments/assets/6020acb1-53f3-4b65-94a4-fe132b867358

https://github.com/user-attachments/assets/3e3076d7-cfb4-4e0a-8552-2926a630fc8e

## License

This repository is [CC0](LICENSE.md). The law text is in each country's repository, under that repository's own terms.
