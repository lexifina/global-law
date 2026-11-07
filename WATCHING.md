# Watching the sources: has anything changed?

[FRESHNESS.md](FRESHNESS.md) says when each corpus was last checked against its official source. For most corpora
that check is the day the corpus was built. To turn a build date into a real, repeated check without rebuilding
anything, every corpus can have a **change detector**: a cheap daily look at the one official page that announces new
law or new decisions.

The detectors are built and tested, but **not switched on yet**. When they are, each poll counts as a check in
FRESHNESS.md.

## How a detector works

1. **One page per source.** Most official publishers have a page that lists what is new, such as a gazette feed, an
   edition or issue list, a "recently changed" API, a sitemap or a dated list. Many corpora share one page. For example,
   one national gazette feed can cover a country and all of its regions.
2. **A daily poll.** The detector reads that page once a day, politely: it respects robots.txt, waits between requests
   and asks only whether the page has changed since the last poll.
3. **A short answer.** The poll records either "nothing new since *date*" or a list of the new items.
4. **What follows.** "Nothing new" is recorded as a fresh check for the corpus. "Something new" marks the corpus as
   due for an update.

## Two separate tracks

Legislation and case law change in different ways, so each has its own detectors and its own rules.

| | Legislation | Case law |
| --- | --- | --- |
| The question | Has the source published a new act, an amendment, a repeal or a new consolidation? | Have the courts published decisions newer than the newest one held here? |
| Where it looks | Gazette feed or edition list, a "recently changed" API, a consolidation list | Court decision feed, open-data delta, a "modified since" API, a bulk release |
| What a hit means | Text held here may now be out of date: the corpus is `pending-change` until it is rebuilt | New decisions to add; nothing held here becomes wrong, because a decision does not change once published |
| When it counts as stale | No check for 7 days (national law) or 30 days (sub-national law) | The gap to the court's newest decision, measured against how often that court publishes |

## Current coverage

As of 7 November 2026, detectors cover 649 of 816 corpora: 568 of 733 legislation corpora and 81 of 83 case-law
corpora. Each one passed a live check against its official source.

Every other corpus has a recorded reason why it isn't covered:

- **The source doesn't answer from our current network** (about 125 corpora). These detectors are written and may work
  from another network.
- **The source blocks automated readers**, or its robots.txt forbids the only list of new law (about 30).
- **The only list of new law is a search form** (a handful). Reading it needs a different kind of request.
- **Excluded for now** (2), and a few sources with no official list of new law at all.

Each detector has a test, so a source that changes its page shape shows up as a failing test, not a silent gap.

## What's left before it runs

- Run the detectors daily alongside the 15-minute update pass described in [MONITORING.md](MONITORING.md).
- Count each poll as a check in [FRESHNESS.md](FRESHNESS.md).
- Cover the remaining sources: other networks, and support for search forms.

Only each country's official publication has legal force. A detector only says *whether* something changed; the text
always comes from the official source.
