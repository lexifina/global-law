# Monitoring: does it keep up?

https://github.com/user-attachments/assets/6119b018-5f5b-4bab-a2da-0aad30ef585f

[How each figure in the film was counted](film/).

New law reaches this repository in two steps. Each country's pipeline reads its official source and publishes each
change as a commit dated the day it takes effect. Then, every 15 minutes, a pass here checks every new commit, pins it,
and publishes the result below.

<!-- status-summary -->
**Updates: running**: last published 2026-11-23 21:34 UTC; status refreshed 2026-11-23 21:34 UTC.

| | |
| --- | --- |
| Last 24 hours | 76 commits: 7 corpus updates, 0 corpora added |
| Last successful pass | 2026-11-23 21:34 UTC |
| Not pinned yet | `romania-law` (held by the maintainers, since 2026-11-04), `austria-bundesverwaltungsgericht-caselaw` (held by the maintainers, since 2026-11-07), `austria-justiz-caselaw` (held by the maintainers, since 2026-11-07), `austria-landesverwaltungsgerichte-caselaw` (held by the maintainers, since 2026-11-07), `austria-oberster-gerichtshof-caselaw` (held by the maintainers, since 2026-11-07), `austria-verfassungsgerichtshof-caselaw` (held by the maintainers, since 2026-11-07), `austria-verwaltungsgerichtshof-caselaw` (held by the maintainers, since 2026-11-07), `united-states-law` (its history was rewritten: the new commit does not follow the pinned one, since 2026-11-22) and 13 more |
| Official sources not answering | none |
| Freshness | 606 of 991 corpora current, 355 stale, 16 unverified ([FRESHNESS.md](../FRESHNESS.md)) |
<!-- /status-summary -->

## What each pass does

1. Finds every corpus with a newer commit, makes sure the new commit follows the pinned one (read from a commits-only
   clone of the corpus, so even the largest corpora get an answer) and checks it (`tools/check_corpus.py`). A commit
   that fails is held back, and the last good one stays pinned. Every corpus not moved is listed in the table above
   and in `holds` in [data/status.json](../data/status.json), with its reason and the day it was first held.
2. Moves the pins forward, rewrites [data/freshness.tsv](../data/freshness.tsv), [data/status.json](../data/status.json) and
   these pages in the same commit, and verifies the history (`tools/verify.py`: pins only move forward).
3. If no pin moved, it still refreshes the status within the hour, so an old timestamp always means a stall.

## Each country's own trail

This page watches the step from a country's repository to global-law. The step before it, reading the official source,
is recorded by each country's own pipeline: every read, when, what was read and what was added, changed or removed.
Czechia is the first to keep this trail: [czechia-law monitoring/](https://github.com/lexifina/czechia-law/tree/main/monitoring)
(pages in Czech and English, a monthly log, `Kind: check` commits) and its records for programs,
[data/checks/](https://github.com/lexifina/czechia-law/tree/main/data/checks) (JSON Lines, schema `lexifina-check/1`).

## Check it yourself

```
python tools/freshness.py --health
```

It fails when the status has not been refreshed for 2 hours, updates have stalled, or freshness has not been
recomputed for a day, and lists any official source that is not answering. `updates` in
[data/status.json](../data/status.json) is `running` while a pass has succeeded in the last 45 minutes.

## Vulnerability scan (off by default)

The detectors in [vulnerabilities/](../vulnerabilities/) can also check new law as it arrives, so a fine that points at a
deleted rule, a reference to a repealed article or a rule renewed after it ran out is flagged on the day the change is
picked up, not months later. This is **off by default**: the 15-minute pass does not run it.

When switched on, each pass would add one step after moving the pins:

1. For every corpus whose pin moved, take the files the new commits changed (`git diff --name-only OLD NEW`).
2. Run the detectors on those files and on the files that refer to them: references to deleted or "(repealed)"
   provisions, fine lists pointing at deleted sections, end dates extended after they had run out, in-force dates
   earlier than publication.
3. Compare with the published list in [vulnerabilities/data/](../vulnerabilities/data/) and record only new flags, with the
   commit that introduced them.
4. Optionally pass new flags to the model review, which sorts out corpus build errors before anyone looks at them.

A flag never holds back a pin: the law is published as the official source has it, and the flag is a note for a reader.

To check new legislation by hand today, run the scripts in [vulnerabilities/scripts/](../vulnerabilities/scripts/) (see its
README) against the corpora you have just updated.
