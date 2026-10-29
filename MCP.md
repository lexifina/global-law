# Using the tree from an AI model (MCP)

`tools/mcp_server.py` is a Model Context Protocol server for this repository. It answers the questions
`tools/law.py` answers, with the limits of each record stated on every answer. It uses only Python's standard library
and git, reads the repository and changes nothing.

## Set up

```sh
git clone --recurse-submodules https://github.com/lexifina/global-law && cd global-law
claude mcp add global-law -- python tools/mcp_server.py
```

The repository also carries a project `.mcp.json`, so Claude Code offers the server in any clone without that
second command; approve it when asked.

On large corpora (Malta has about 7,000 commits and 67,000 files), a provision's history is a path-limited `git log`.
Writing each corpus's commit graph with changed-path filters makes it about three times faster. This writes only
git's own index under `.git`, never the law files:

```sh
git submodule foreach --quiet 'git commit-graph write --reachable --changed-paths'
```

Any other MCP client works the same way: the server speaks newline-delimited JSON-RPC over stdio. For a project file:

```json
{ "mcpServers": { "global-law": { "command": "python", "args": ["/path/to/global-law/tools/mcp_server.py"] } } }
```

## Tools

To browse a large corpus by act, give `list_provisions` the start of a folder name, for example
`mt/national/malta-law/sl/586.` for every instrument under Malta's Data Protection Act. You get one row per act, with
its title and last change.

| Tool | What it answers |
| --- | --- |
| `list_jurisdictions` | Every jurisdiction and body of law, how far each record reaches, how many provisions, and an example path. Start here. |
| `find_provision` | The path of a provision from its number ("1182", "Art. 16a", "reg 13"), a popular name from `aliases.json` ("Schuldenbremse", "automatic stay", "EHC plan") or a topic found in the text. |
| `list_provisions` | The provisions under a corpus or folder, with headings, as in force on a date. |
| `read_law` | (`include_text: false` for a cheap check of dates, laws and sources.) A provision's text on a date, with the law that last changed it, the next change, sources to cite and the record's limits. It says whether the words are still the same at the end of the record (`latest`). It adds "not the whole answer" notes where a later law reaches back over the date, or an effect changes how the provision applies without changing its words (`Modifies:`). |
| `world_on_date` | Every jurisdiction on one date: the last change in force in each, and the next. |
| `who_wrote` | Which law wrote each word (or line), with words per law. Words brought back when a temporary change ended stay with the law that first wrote them (`restored_by` names the law that brought them back). |
| `compare_dates` | A word-level diff between two dates and the laws that took effect in between. |
| `provision_history` | Every law that changed a provision, with its in-force, enacted or made, and published dates and its sources. |
| `laws_between` | Every law that took effect in a window, with how many provisions each changed. |
| `search_law` | Search the text of all the law in force on a date. |
| `changes_between` | Every provision whose text differs between two dates, with the laws that changed them. |
| `search_changes` | Search the record of changes (the commit messages) rather than the text. |
| `what_else_changes` | The provisions that rely on this one: those that cite it, and those that use a multi-word term it defines. It gives a scoped definition's scope ("In this subchapter"), and lists apart uses nearer another definition of the same term. |
| `resolve_citations` | Every citation in a piece of text (a brief, a judgment), resolved to its provision, with its state on a date. |
| `check_precedent` | For case law: which recorded judgments apply a provision, and is the text each court applied on the day it decided still the text in force? If not, which laws changed it. Compares the words of the law only, and names changes that left the words alone. |
| `phrase_history` | When words came into the law and when they left it, at any date: for things no longer in force. Words already in a record's first text are `present_at_start`. |
| `applies_to_case` | For a case commenced on a date, which later changes reach it, from any scope the record holds. |
| `law_details` | The full record of one law's change: every trailer and every provision it changed. |

Resources: `global-law://README.md`, `REPRODUCE.md`, `CHANGELOG.md` and `manifest.json`.

Prompts (ready-made research tasks): `provision_on_a_date`, `case_timeline` and `what_changed`. A resource template
`global-law://law/{path}?date={date}` gives any provision as in force on a date.

## Protocol

The server speaks both eras of MCP. Modern clients (revision 2026-07-28) send their protocol version in each request's
`_meta` and need no handshake; the server answers `server/discover`, marks results `resultType: "complete"`, names
itself in each result's `_meta`, gives cache hints on list and read results, and answers an unsupported version with
error -32022 listing the versions it supports. Legacy clients (2025-11-25 back to 2024-11-05) open with `initialize`
and are served as before.

## Security

The server is read-only and local. It reads the git repository it sits in, never uses the network and never runs a
shell, so it has no port to attack and costs nothing per call; each user runs their own copy over stdio. It writes
nothing unless you set `GLOBAL_LAW_AUDIT_DIR`. Then it appends one line per tool call to `global-law-mcp.jsonl` there,
holding the time, the tool, a keyed hash (HMAC-SHA-256) of the arguments, the duration and the status. The arguments
themselves are never written. The key is fresh for each process, or `GLOBAL_LAW_AUDIT_KEY` if you want repeats matched
across sessions; without a key, short arguments such as a date could be recovered by hashing guesses. Each git call is
an argument list, with every user value passed as a value (`-e`, `--`), so nothing a client sends is run as a command or
an option.

- Paths must stay inside the tree: no `..`, absolute paths, drive letters, colons or wildcards.
- Commit hashes must be hexadecimal, and `law_details` reads only commits in the history the tree pins, never another
  branch or an unreachable draft in a maintainer's clone.
- Text arguments are limited to 300 characters with no control characters. Arguments a tool's schema does not name are
  refused, as are ids that are not strings or integers.
- Only git runs a model-supplied regular expression, never Python's backtracking engine. Patterns that could still take
  exponential time are refused: a repeated group that holds a quantifier, an alternation or another group, or a
  back-reference.
- Git never runs a text-conversion filter or an external diff driver (`--no-textconv --no-ext-diff`), even when a
  checkout's attributes name one that your git config defines.
- Each tool call has 120 seconds of git in total, after which it stops and says so. Lists are capped and say when they
  were cut. Searches look at no more commits than they show, and `resolve_citations` looks up at most 100 provisions.
- A message is limited to 1 MB. Bytes that are not UTF-8, JSON nested too deep and numbers too long to read are
  answered with a parse error. A corpus that is not checked out narrows an answer and is named; it does not stop the
  server. An internal error reports only its type, and the details go to stderr.
- Law text, change notes and judgment notes are passed on as data. The instructions tell the model they are never
  instructions.
- The tests include a hostile-input suite and the cases an independent review found (October 2026), each now a test. A
  fuzz run of 400 random calls gave no crash, no internal error and no leaked detail.

## What to tell the user

Coverage is partial. Each corpus holds only the law its description names, over a stated period, so "nothing found"
means nothing in the record. Every answer carries notes where a date falls before a record starts or after it ends;
pass them on. Dates are the dates each record gives a change: the day it took effect, or for a first version the day it
was enacted or made. `applies_to_case` uses the scope a record holds, as data (`Applies:`) or in the change notes' words, and says
which. Where no scope is recorded it says the reach to pending cases is not recorded and names the corpus's default rule
(for the US, the presumption against retroactivity), without deciding it.

## Compared with other law MCP servers

Checked 28 October 2026 against the published descriptions of each server:
- legalize-mcp and lawyer-mcp (the legalize.dev corpus)
- legislation-gov-uk-mcp and uk-legal-mcp
- law-scrapper-mcp (Poland)
- CourtListener's MCP and court-listener-mcp
- GovInfo's MCP
- LexAPI and mcp-eu-sparql (EU)
- Open Legal Data and de-eli-mcp (Germany)

Several of them read a law's text on a date and compare versions (legalize.dev, the UK legislation servers). None of
them offers:
- authorship by word
- when words entered or left the law
- which cases a change reaches (`applies_to_case`)
- what else relies on a provision
- separate in-force, enacted and published dates. Choosing a version by date does not say whether it was in force; legalize.dev itself warns of this.

Where others are ahead:
- **Coverage.** legalize.dev has 32 jurisdictions; the UK servers have all UK legislation.
- **Freshness.** Change feeds and pending amendments.
- **Case law.** CourtListener, Open Legal Data and uk-legal-mcp have case law with citation networks and "cited by". This tree has only a first, hand-checked sample of judgments (`judgments/`, read by `check_precedent`).
- **Parliamentary history.**
- **Hosted access.** Some run as hosted servers with OAuth, while this one runs locally from a clone.

## Tests

```sh
python -m unittest tests.test_mcp -v
```

The tests speak to the server the way a client does: the handshake, every tool, errors, resources, and the
applicability rules on their own. The server was also tested blind, in four rounds: a model given only these tools answered 26 of 26 questions correctly, including
adversarial ones, and said where the record could not answer.
