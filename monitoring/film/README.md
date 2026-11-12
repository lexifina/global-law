# Monitoring film: where every figure comes from

The 24 second film explains the [monitoring page](../README.md). Every
number in it is taken from one snapshot of the repository, **2026-11-11 20:11:55 UTC**, the `generated` time of
`data/status.json` at that moment. This page says how each number was obtained and which parts of the picture are
drawn for illustration.

There are two cuts of the same film: 1920x1080 for this repository and 1080x1920 for vertical players. They show
the same figures.

## The snapshot

| File | Used for |
| --- | --- |
| `data/freshness.tsv` | one row per corpus: path, level, status, number of acts, pinned commit, newest commit |
| `data/status.json` | corpora updated, corpora held back |
| `.gitmodules` | the repository behind each corpus path |

Copies of the three files as used are in [data/](data/).

## Scene 1: every change in the law is a commit

| On screen | Value | How it was obtained |
| --- | ---: | --- |
| corpora | 982 | rows in `data/freshness.tsv` |
| commits | 15,606,307 | sum over the 982 corpus repositories of the commits reachable from that corpus's `newest` commit |
| in 24 hours | 10,892 | of those commits, the ones with a committer date from 2026-11-10 20:11:55 UTC to 2026-11-11 20:11:55 UTC |

Both commit figures count commits in the corpus repositories only (`lexifina/<country>-law` and the like). Commits in
`global-law` itself, which only move the pins, are **not** counted. For that reason the 24 hour figure is not the
`published_last_24h.commits` value in `data/status.json` (692): that value is the number of commits made in
`global-law` in the period.

`figures.py` reproduces both figures. For each corpus it asks the GitHub GraphQL API for
`repository.object(oid: <newest>)`, then `history.totalCount` and
`history(since: …, until: …).totalCount`. It writes the totals and the two counts for every corpus to
[figures.json](figures.json).

```
python figures.py data/freshness.tsv data/gitmodules.txt 2026-11-11T20:11:55Z figures.json
```

Things to know about these counts:

- **Committer date, not author date.** In a corpus repository the author date of a commit is the day the change took
  effect. The committer date is when the pipeline made the commit, so the 24 hour figure uses the committer date.
- **Made, not pushed.** A commit made earlier and pushed inside the 24 hours is not in the 24 hour figure. GitHub does
  not give a push time for each commit.
- **Rebuilds count.** When a pipeline rebuilds a corpus, its commits are made again and get new committer dates. Five
  corpora account for 8,706 of the 10,892: `montenegro/national/acts` (3,505), `united-states/new-york/acts` (1,592),
  `croatia/national/acts` (1,302), `bulgaria/national/acts` (1,206) and `brazil/minas-gerais/acts` (1,101).
- **322 corpora** had at least one commit in the 24 hours.
- **Newest, not pinned.** The count is taken at the `newest` commit, so it includes commits that were published but
  held back or not yet pinned. Counted at the pinned commits the total is 15,024,472.
- The history of a repository can be rewritten after the snapshot. Run later, the script still reads the commits
  named in the snapshot for as long as GitHub keeps them.

## Scene 2: every commit is pinned to real legislation

| On screen | Value | Source |
| --- | ---: | --- |
| every 15 minutes | | the monitoring page |
| corpora updated | 106 | `published_last_24h.corpora_moved` in `data/status.json` |

The snapshot also lists two corpora held back by a check (`singapore-law`, `united-states-missouri-law`). The film
does not show them.

## Scene 3: the same toolset across every jurisdiction

| On screen | Value | Source |
| --- | ---: | --- |
| tools | 18 | the tools table in [MCP.md](../../MCP.md) |
| corpora | 982 | rows in `data/freshness.tsv` |

The 18 names on screen are the tools of `tools/mcp_server.py`, which answer the same questions for any corpus in the
tree: `read_law`, `search_law`, `find_provision`, `list_provisions`, `list_jurisdictions`, `law_details`,
`provision_history`, `who_wrote`, `phrase_history`, `compare_dates`, `changes_between`, `laws_between`,
`search_changes`, `world_on_date`, `applies_to_case`, `check_precedent`, `resolve_citations`, `what_else_changes`.
What a tool can answer for a corpus depends on what that corpus's record holds: `check_precedent`, for example,
needs case law that cites the provision.

## Scene 4: every commit always pins to a live official source

| On screen | Value | Source |
| --- | ---: | --- |
| official sources | 4,396 | 610 publishers and 3,786 courts, counted as set out below |
| corpora | 982 | rows in `data/freshness.tsv` |

**Publishers: 610.** The different `official_source` names in `data/freshness.tsv`; 947 of the 982 corpora name one.

**Courts: 3,786.** A case-law corpus files each decision under the court that gave it, one folder per court under
`decisions/`. `courts.py` lists those folders for the 241 case-law corpora at their `newest` commits and writes them
to [courts.tsv](courts.tsv), 4,177 rows. From those:

- 158 folders named by year (Finland, Brazil) are not courts and are left out;
- a court that sits in several corpora of one country is counted once.

That leaves 3,786 courts: 2,865 in the United States, 355 in Poland, 353 in France, 119 in Switzerland, 83 in the
Netherlands, 6 in Germany and 5 in Finland. Things to know about this count:

- A court is the source of its own decisions, but the corpus may read them through a publisher that gathers many
  courts. Most United States decisions, for example, are read from the Caselaw Access Project, which is one of the
  610 publishers.
- Some folders are bodies that decide cases without being courts, such as Swiss federal offices.
- Folder names are cut at 50 characters, so two courts whose names share their first 50 characters would count as
  one.

The list holds 56 publisher names, each beside the corpus read from it, and 14 courts of the United States named
from their folders. `build_data.py` chooses them: up to two per
country in path order, where the name is 12 to 44 characters, fits the row beside its path and uses only characters
in the film's fonts. Each name is listed once. Rows whose source is a mirror or a private collection, not the
publisher itself, are left out of the list; they still count in the 610 publishers.

Where a corpus's official source comes from, in this order (`official_source` in `tools/freshness.py`):

| Rule | Corpora |
| --- | ---: |
| the corpus's own `publisher` in `manifest.json` | 661 |
| the `publisher` of its `source` in `manifest.json` (case law names it there) | 199 |
| [data/official-sources.tsv](../../data/official-sources.tsv): the source named in the corpus's record note or README, for corpora whose own description carries no publisher yet | 87 |
| none named | 35 |

The 35 without a name: 27 Swiss case law corpora, which gather many courts and name no single publisher; six
Canadian provinces held as metadata only, with no law text read from the official site; and Costa Rica and Tuvalu,
which hold no law text yet. Before the second and third rules were added the film showed 527 sources named by 661
corpora.

"Checked against it on a schedule" is the rule in FRESHNESS.md: a check falls due 7 days after the last one for
national law and 30 days after for a state or city.

## What is drawn for illustration

- **The disc.** Each of the 982 corpora is an arc of dots. National corpora are on the three inner rings and
  sub-national corpora on the four outer rings. The number of dots grows with the square root of the corpus's number
  of acts. Which ring a corpus sits on within its group is arbitrary.
- **The streaks in scene 1.** 692 streaks are drawn, so each one stands for about 16 commits. They land only on the
  322 corpora that had commits in the 24 hours, more often on those with more commits. The counter is the real figure.
- **The corpora that turn green in scene 2.** The snapshot does not name the 106 corpora whose pins moved. The film
  uses the 106 corpora with the most commits in the 24 hours.
- **The waves in scene 3.** Each tool name lights in turn and a wave crosses every ring. No tool is being run; the
  wave shows that the tool reaches every corpus.
- **The lines in scene 4.** The line from each source to its corpus, and the light running along it, show that the
  corpus is read from that source. They are not a measurement of traffic.

## Files

| File | What it is |
| --- | --- |
| `film.html` | the film: one canvas, drawn for any frame number |
| `data.js`, `build_data.py` | the snapshot as the film reads it, built from `data/freshness.tsv` and `figures.json` |
| `figures.py`, `figures.json` | the commit counts |
| `courts.py`, `courts.tsv` | the courts in every case-law corpus |
| `render.mjs` | renders the frames in Chromium and encodes them: `FMT=jpeg node render.mjs video out.mp4 2`; with `LAYOUT=landscape` it renders the 1920x1080 cut |

The film's typefaces are Source Serif 4, IBM Plex Sans and IBM Plex Mono. They are not kept here: put their
`latin` woff2 files in `fonts/` as `ss500`, `ss600`, `ps400`, `ps500`, `pm400` and `pm500` before rendering.
