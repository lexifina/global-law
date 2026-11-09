# Monitoring: does it keep up?

New law reaches this repository in two steps. Each country's pipeline reads its official source and publishes each
change as a commit dated the day it takes effect. Then, every 15 minutes, a pass here checks every new commit, pins it,
and publishes the result below.

<!-- status-summary -->
**Updates: running**: last published 2026-11-09 03:31 UTC; status refreshed 2026-11-09 03:31 UTC.

| | |
| --- | --- |
| Last 24 hours | 91 commits: 19 corpus updates, 137 corpora added |
| Last successful pass | 2026-11-09 03:31 UTC |
| Held back by a check | none |
| Official sources not answering | none |
| Freshness | 822 of 972 corpora current, 135 stale, 14 unverified ([FRESHNESS.md](FRESHNESS.md)) |
<!-- /status-summary -->

## What each pass does

1. Finds every corpus with a newer commit and checks it (`tools/check_corpus.py`). A commit that fails is held back,
   and the last good one stays pinned.
2. Moves the pins forward, rewrites [data/freshness.tsv](data/freshness.tsv), [data/status.json](data/status.json) and
   these pages in the same commit, and verifies the history (`tools/verify.py`: pins only move forward).
3. If no pin moved, it still refreshes the status within the hour, so an old timestamp always means a stall.

## Check it yourself

```
python tools/freshness.py --health
```

It fails when the status has not been refreshed for 2 hours, updates have stalled, or freshness has not been
recomputed for a day, and lists any official source that is not answering. `updates` in
[data/status.json](data/status.json) is `running` while a pass has succeeded in the last 45 minutes.
