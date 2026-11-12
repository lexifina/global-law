# Monitoring short: where every figure comes from

The 45 second film explains the [monitoring page](../README.md). Every
number in it is taken from one snapshot of the repository, **2026-11-11 20:11:55 UTC**, the `generated` time of
`data/status.json` at that moment. This page says how each number was obtained and which parts of the picture are
drawn for illustration.

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

## Scene 2: a pass checks every new commit

| On screen | Value | Source |
| --- | ---: | --- |
| every 15 minutes | | the monitoring page |
| corpora updated | 105 | `published_last_24h.corpora_moved` in `data/status.json` is 106; the film shows one of them, Missouri, as held back |
| held back | 2 | `held_back` in `data/status.json`: `singapore-law`, `united-states-missouri-law` |

## Scene 3: pins only move forward

The three rows are real corpora and the commit hashes are their `pinned` values in `data/freshness.tsv`:
`albania/national/acts` f07de17, `united-states/federal/usc` a4c5f91, `united-states/missouri/acts` 66f2343. For
Missouri the `newest` commit (63117d6) differs from the pinned one, which is what held back means.

## Scene 4: an old timestamp means a stall

| On screen | Source in the monitoring page |
| --- | --- |
| 15 min, the next pass | "every 15 minutes, a pass here checks every new commit" |
| 45 min, updates have stalled | "`updates` is `running` while a pass has succeeded in the last 45 minutes" |
| 2 hours, the status is too old | the health check "fails when the status has not been refreshed for 2 hours" |
| the status is still refreshed within the hour | "If no pin moved, it still refreshes the status within the hour" |
| `python tools/freshness.py --health` fails | it fails when updates have stalled or the status is 2 hours old |

The stall in this scene is a demonstration. Updates were running at the snapshot.

## Scene 5: every corpus says how current it is

| On screen | Value | Source |
| --- | ---: | --- |
| current | 798 | rows with status `current` in `data/freshness.tsv` |
| stale | 168 | status `stale` |
| unverified | 14 | status `unverified` |
| 7 days for national law, 30 days for a state or city | | the thresholds in FRESHNESS.md |

The two remaining corpora are `pending-change` and are drawn in white.

## What is drawn for illustration

- **The disc.** Each of the 982 corpora is an arc of dots. National corpora are on the three inner rings and
  sub-national corpora on the four outer rings. The number of dots grows with the square root of the corpus's number
  of acts. Which ring a corpus sits on within its group is arbitrary.
- **The streaks in scene 1.** 692 streaks are drawn, so each one stands for about 16 commits. They land only on the
  322 corpora that had commits in the 24 hours, more often on those with more commits. The counter is the real figure.
- **The corpora that turn green in scene 2.** The snapshot does not name the 106 corpora whose pins moved. The film
  uses the 105 corpora with the most commits in the 24 hours, plus Missouri.
- **Singapore.** `singapore-law` is held back and has no row in `data/freshness.tsv`, so it is drawn waiting on the
  outer circle and is not one of the 982.
- **The commit dots in scene 3.** The number of dots on each row is not the corpus's real number of commits.

## Files

| File | What it is |
| --- | --- |
| `film.html` | the film: one canvas, drawn for any frame number |
| `data.js` | the snapshot as the film reads it, built from `data/freshness.tsv` and `figures.json` |
| `figures.py`, `figures.json` | the commit counts |
| `render.mjs` | renders the frames in Chromium and encodes them: `FMT=jpeg node render.mjs video out.mp4 2` |

The film's typefaces are Source Serif 4, IBM Plex Sans and IBM Plex Mono. They are not kept here: put their
`latin` woff2 files in `fonts/` as `ss500`, `ss600`, `ps400`, `ps500`, `pm400` and `pm500` before rendering.
