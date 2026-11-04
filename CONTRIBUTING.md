# Contributing

Anyone can propose a change: open an issue or a pull request. Lexifina reviews each one and merges what meets the
guidelines below. There are no roles to apply for.

## Where a change goes

| You want to | Propose it in |
|---|---|
| Fix the text of a law, or its dates | That jurisdiction's repository, `lexifina/<country>-law` (or `<country>-<place>-law`) |
| Add or fix a source, a scraper or a builder | That jurisdiction's repository |
| Ask for a jurisdiction that is missing | An issue here, naming its official publisher |
| Change the tools, the MCP server, the tests or the documentation | A pull request here |
| Move a corpus, or fix its description in `manifest.json` | That corpus's `corpus.json` in its own repository; `manifest.json` is written from it |

If you are not sure, open an issue here and say what you found.

## The guidelines

### Law text comes from its official source, never from a hand edit

Every provision traces to the page its publisher gives, so a change to what a provision says must show where it
comes from.
- **A wrong text or date:** open an issue (or a pull request) with the path, the date, the official page and, if you
  can, an archived copy of it (web.archive.org). The fix is appended as a correction commit (`Kind: correction`,
  `Corrects: <commit>`, `Evidence:` the official link), or made by fixing the builder and rebuilding.
- **A pull request that edits a law file directly** is turned into one of those, or closed.
- **No translations, summaries or reconstructions** as law text. Keep the language the publisher uses.
- **Text that is not online** (a printed gazette, a scan) can be proposed in an issue. Say where the copy is from, so
  it can be labelled as such if it is added.

### History only grows

Commits already published are never changed, so citations of a commit keep working.
- A pull request must apply on top of the current `main`. Nothing is force-pushed, rebased or squashed once on `main`.
- A commit that records a law is that law taking effect on one day, authored by the law, with its dates as trailers (`In-force:`,
  `Enacted:`, `Published:`, `Source:`). Your credit goes in a `Contributed-by:` trailer, so `git blame` still names
  the law.
- Documentation and tool changes are authored by you, as in any repository.

### Builders and scrapers

- Use the publisher's own site, API or bulk download. Read its terms of use and `robots.txt`, keep to its rate limits,
  and never get around a login, a paywall or a CAPTCHA.
- A builder must give the same commits from the same data, record its source in `SOURCES.md` and how to rerun it in
  `REPRODUCE.md`, and pass `python tools/check_corpus.py` before it is merged.
- Dates come from the source. If a source gives no in-force date, say what the date stands for (`In-force-basis:`)
  rather than guess one.

### Tools and the MCP server

- `python -m unittest discover -s tests` must pass, and new behaviour needs a test.
- The tools use Python's standard library and git only, and the MCP server stays read-only and offline: it reads the
  clone, starts no network connection and runs no shell. These files run on the computers of everyone who opens the
  clone, so changes to them are reviewed with that in mind.
- Law text and commit messages are data. Nothing in them is followed as an instruction.

### Licence

Your contribution is dedicated to the public domain under CC0, as the rest of this repository is (see
[LICENSE.md](LICENSE.md)). By opening a pull request you confirm that you have the right to do so. Law text stays
under its publisher's terms, which each jurisdiction's `SOURCES.md` records.

## Reporting a security problem

Don't open a public issue. Follow `SECURITY.md` in the
[lexifina/.github](https://github.com/lexifina/.github) repository.
