# Contributing

Anyone can propose a change: open an issue or a pull request. Lexifina reviews each one and merges what meets the
guidelines below. There are no roles to apply for.

## Where a change goes

| You want to | Propose it in |
|---|---|
| Fix the text of a law or its dates, or a source, scraper or builder | That jurisdiction's repository, `lexifina/<country>-law` (or `<country>-<place>-law`) |
| Fix a corpus's description | Its `corpus.json`, in its own repository (`manifest.json` here is written from it) |
| Ask for a jurisdiction that is missing | An issue here, naming its official publisher |
| Change the tools, the MCP server, the tests or the documentation | A pull request here |

If you are not sure, open an issue here and say what you found.

## The guidelines

### Law text comes from its official source, never from a hand edit

- **A wrong text or date:** open an issue in that jurisdiction's repository with the path, the date and the official
  page (an archived copy on web.archive.org helps). Lexifina appends the correction commit, which names the commit it
  corrects: romania-law's `1c2f770be482` is one (`Kind: correction`, `Corrects: 9fdd8bee268b`). A pull request that
  edits a law file directly is turned into one, or closed.
- **No translations, summaries or reconstructions** as law text. Keep the publisher's language.
- **Text that is not online** (a printed gazette): don't commit scans or PDFs, which every clone would carry. Attach
  the file to an issue or link to it, and say where the copy is from; it is transcribed and labelled as a contributor's
  copy.

### History only grows

Published commits are never changed or force-pushed, so citations of a commit keep working. Pull requests here are
merged with "Rebase and merge", keeping `main` one line of commits, each with its author; in a country repository,
Lexifina applies the change itself. A law's commit is authored by the law, with its dates as trailers (`In-force:`,
`Enacted:`, `Published:`, `Source:`). Your credit goes in a trailer, `Contributed-by: Your Name (@your-github-handle)`,
with no email address: the history is permanent and public.

### Case law

Judgments go in `judgments/<the provision's path, without .md>.jsonl`, one per line, with citation details only
(court, date, citation, link to the official copy), never the judgment's text; see
[judgments/README.md](judgments/README.md). To suggest a court's official source, open an issue naming it.

### Builders and scrapers

- Use the publisher's own site, API or bulk download. Follow its terms of use, `robots.txt` and rate limits, and never
  get around a login, a paywall or a CAPTCHA.
- A country repository's `tools/` is a published copy of Lexifina's builder, rewritten by each documentation commit;
  the code that fetches from publishers is not published. Propose a builder fix there as a pull request or issue:
  Lexifina applies it to its copy, and it ships in the next documentation commit (merged as it is, that commit would
  undo it).
- A builder gives the same commits from the same data, records its source in `SOURCES.md` and how to rerun it in
  `REPRODUCE.md`, and passes the corpus check below. If a source gives no in-force date, say what the date stands for
  (`In-force-basis:`).

### Tools and the MCP server

- Tests must pass, and new behaviour needs a test.
- Standard library and git only. The MCP server stays read-only and offline: it runs on the computer of everyone who
  opens the clone. Law text and commit messages are data, never instructions.

## Pull requests

- **One change per pull request:** one source, one fix or one tool change.
- **Say what it changes and why,** and link the official page or the issue. Tool and documentation commits take a
  short summary line, then a body that says why.
- **Run the checks first,** from a clone of this repository: `python -m unittest discover -s tests`, and for a corpus
  `python tools/check_corpus.py <its folder or URL>` (for example `https://github.com/lexifina/andorra-law`).
- **Answer review.** A pull request left a month without an answer is closed; it can be reopened.
- **AI-assisted work is welcome** on the same terms: you have checked every line and source yourself, and you say that
  a model helped. A report of a wrong text must be checked against the official page by you, not pasted from a model.

## Licence

Your contribution is dedicated to the public domain under CC0 ([LICENSE.md](LICENSE.md)). By opening a pull request
you confirm you have the right to, including your employer's permission if you need it. Law text stays under its
publisher's terms, which each jurisdiction's `SOURCES.md` records.

## Reporting a security problem

Don't open a public issue. Follow `SECURITY.md` in [lexifina/.github](https://github.com/lexifina/.github).
