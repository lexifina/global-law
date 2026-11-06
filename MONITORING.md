# Monitoring: whether updates are running

<!-- status-summary -->
**Updates: running**, last published 2026-11-06 15:49 UTC; 0 corpus updates in the last 24 hours, 0 held back by a check; 619 of 714 corpora current (as of 2026-11-06).
<!-- /status-summary -->

Each country's pipeline publishes new law as commits dated the day it takes effect. Every 15 minutes a pass here
checks each new commit (`tools/check_corpus.py`; one that fails is held back), moves the pins forward, rewrites the
freshness and status files, and verifies the history (`tools/verify.py`). If no pin moves, the status is still
refreshed within the hour.

[data/status.json](data/status.json) is the public record: `updates` (`running` or `stalled`), `last_published`,
`published_last_24h`, `held_back` (corpora whose newest commit failed a check) and `official_sources_unavailable`.

`python tools/freshness.py --health` fails when the status has not been refreshed for 2 hours, updates have stalled,
or freshness has not been recomputed for a day.
