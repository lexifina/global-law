# Using the tree from an AI model (MCP)

`tools/mcp_server.py` is a Model Context Protocol server for this repository. It answers the questions
`tools/law.py` answers, with the limits of each record stated on every answer. It uses only Python's standard library
and git, reads the repository and changes nothing.

## Set up

You need git and Python 3.9 or newer (macOS's own `python3` will do). Nothing else to install.

**One country.** The whole tree is many GB, but each country is its own git submodule, so you can download only
the law you need. For Romania:

```sh
git clone https://github.com/lexifina/global-law && cd global-law
python3 tools/countries.py add romania
claude      # or open the folder in Cursor, VS Code or Codex
```

The first command fetches the shared index of every country without any country's law (about 400 MB). The second
downloads Romania's history alone (about 1.7 GB on 4 November 2026, several minutes; most countries are far smaller). Ask
about Romanian law and the server answers from it; ask about a country you have not added and it tells
you the command that adds it. Add more countries at any time (`python3 tools/countries.py add france spain`); a
running server sees them within seconds. On Windows, run the script with `py` or `python`.

**Every country:**

```sh
git clone --recurse-submodules https://github.com/lexifina/global-law && cd global-law
claude
```

The clone carries each client's project config, all starting `tools/mcp.sh` through git, which runs it from the top of
the clone with a POSIX shell on every platform (Git for Windows brings one) and picks the first of `python3`, `python`
and `py` that is new enough:

| Client | File | First run |
|---|---|---|
| Claude Code | `.mcp.json`, approved by `.claude/settings.json` | Trust the folder when asked; the server and its read-only tools are then allowed |
| Cursor | `.cursor/mcp.json` | Turn the server on under MCP settings if Cursor lists it as off |
| VS Code (Copilot agent mode) | `.vscode/mcp.json` | Start it from the file's "Start" link or the MCP servers list |
| Codex | `.codex/config.toml` | Trust the project; Codex reads project config only in trusted projects |

`AGENTS.md` (and `CLAUDE.md`, which includes it) tells agents to answer questions about the law with these tools.
To start the server by hand, `sh tools/mcp.sh` speaks MCP on stdin and stdout.

The first answer after starting reads the whole timeline and lists every corpus, a few seconds on a full checkout. The
server does that as soon as it starts, so by the time a client asks, it is usually done.

On large corpora (Malta has about 7,000 commits and 67,000 files), a provision's history is a path-limited `git log`.
Writing each corpus's commit graph with changed-path filters makes it about three times faster. This writes only
git's own index under `.git`, never the law files:

```sh
git submodule foreach --quiet 'git commit-graph write --reachable --changed-paths'
```

Any other MCP client works the same way: the server speaks newline-delimited JSON-RPC over stdio. For a project file:

```json
{ "mcpServers": { "global-law": { "command": "git", "args": ["-C", "/path/to/global-law", "-c", "alias.global-law-mcp=!sh tools/mcp.sh", "global-law-mcp"] } } }
```

## Only some countries

The server serves the countries checked out in your clone and, if you choose some, only those. `tools/countries.py`
does both:

| Command | What it does |
|---|---|
| `python3 tools/countries.py` | Lists every body of law in the tree: served, checked out but not chosen, or not checked out |
| `python3 tools/countries.py add romania` | Checks it out; git downloads only that |
| `python3 tools/countries.py only romania` | Serves only these, checking out any not yet here |
| `python3 tools/countries.py only --all` | Serves every body of law checked out again |

A name is a country folder (`romania`, `"united kingdom"`), an ISO code (`ro`), a level (`united-states/federal`) or a
corpus path (`romania/national/acts`). A misspelt name gets a suggestion. `only` writes `global-law.jurisdictions` to
the clone's own `.git/config`, which is never committed. To narrow one client's server without changing the clone, set
`GLOBAL_LAW_JURISDICTIONS` (names separated by commas) in that server's environment; it takes precedence.

What the model sees:
- `list_jurisdictions` describes the bodies of law served, then names the others, why each is left out (not checked
  out, or not chosen) and the command that adds them.
- A corpus checked out but unreadable at the commit the tree pins (an interrupted clone with no commit yet, a checkout
  behind its pin after `git pull` without `git submodule update`, or a shallow clone) is not served either. Every
  answer over several corpora names it on a "Left out:" line with the command that fixes it, as `law.py world` does,
  and a path or `jurisdiction` in it gets that command as its error.
- An answer over every jurisdiction (a search, `laws_between`, `world_on_date`) ends with "Served here: 1 of the 107
  corpora in the tree; the other 106 were not searched", so "nothing found" is not read as nothing in the law.
- A path or `jurisdiction` in a country left out gets an error naming the command that adds it. `resolve_citations`
  marks such a citation `not served here`, and `find_provision` flags an alias that points to one.
- The server's instructions tell the model to pass that command to the user, not to answer from memory.

A provision's history needs only its own corpus, so dates, authorship and history are the same with one country as
with all of them.

## How a date is read

Each country's record is its own git history, and each commit there carries the day its change took effect. A
provision on a date is read from its own history, in the history the tree pins at HEAD: of the commits that touch it,
the one with the latest in-force date on or before that date, a later commit winning a tie. The order of commits does
not matter, because a country may append an older act after its tip.

A corpus that grows append-only (romania-law) fixes a wrong version by appending it again: a `Kind: correction`
commit with its own `In-force:` day and `Corrects: <commit>` (the text was wrong) or `Re-asserts: <commit>` (it was
right and is restated). That is an ordinary version under the rule above, the later commit winning its day, credited to
the law of the version it restates; `read_law` says that a correction applies. Such corrections may be written by the
maintainer (author `Lexifina`), whose other commits are documentation. Three more of its records are read:
- **Moves.** A commit that is not a law and renames files without changing them (romania-law's layout move of November
  2026, `codul-civil/` to `lege/2009/287/`) leaves each provision one history under its current path.
- **Withdrawals.** A commit that is not a law and deletes files (`Withdraws: <act>`: an act that never belonged in the
  record) takes the versions written before it out of the record on every day.
- **Credits.** When only the credited law was wrong, `data/credits.csv` (`act,in_force,provision,law,...`, labels in
  `data/laws.csv`) names the law each change is credited to; `provision_history`, `read_law` and `who_wrote` use it.

Then overlay corrections apply, file by file. An overlay correction commit carries `Kind: correction`, `In-force: <first day>`,
`Corrects: <act> <from>..<to>`, `Supersedes: <commit or none>`, `Reason:`, `Act-path: <the act's folder or file>` and one
`Files: <path>` trailer for each file it sets. Its text replaces the ordinary version of each file it names on every
day its range covers, even when git shows no change to that file (a late-found version can equal the text the tip
already has). An open range (`<from>..`) ends the day before the act's next ordinary commit, the next commit by
in-force date that touches `Act-path` (or, without it, the folders of its `Files`). The latest correction covering a
day wins, and `read_law` says that a correction applies, with what it supersedes and why.

The same rule holds for a whole country on a date (`search_law`, `list_provisions`, `changes_between`). A country whose
history is in in-force order with no corrections is read at its last commit on or before the date. Any other is read
as a tree of each file's version for the date, which the server builds in a temporary object directory, never in your
clone. `tools/check_corpus.py` reports commits appended after later-dated ones (end blocks) as a warning: they are
allowed. The timeline across countries (`laws_between`, `world_on_date`,
`search_changes`) merges the countries' histories by date.

Until 2 November 2026 the tree also wrote one dated root commit per law taking effect, and the tools read those. Since
then the tree only moves each country's pin forward (it grows by fast-forward alone, and a country's repository may be
rebuilt), so its root history ends there. The old root commits now only date a country commit that carries no date of
its own.

## How a corpus describes itself

The server reads every corpus the tree pins. `manifest.json` lists them all, written by `tools/describe.py` from each
corpus's own `corpus.json`, or else the `jurisdiction.json` and `data/repo.json` that the shared builder's repos ship
(name and code, with defaults for the rest), or else its path. Codes follow ISO 3166: a country's two letters, a
subdivision's ISO 3166-2 code (`US-CO`, `BR-BA`). Codes below the first level (`AR-B-ALBERTI`, a city in Buenos Aires
province) are built from the parent's code and the folder name, and are not ISO codes. `corpus.json` fields the
readers use:

| Field | Meaning |
|---|---|
| `corpus` | ISO path, `<iso2>/<level>/<kind>`, for example `de/bremen/acts` (required) |
| `name`, `language` | What it is, and its ISO 639-1 language |
| `coverage` | One line on what the record holds, for example "every Act in force since 1947" |
| `history` | `in-force` (each version from the day it took force), `current-only` (the source keeps no past versions), `replayed` (past versions rebuilt by applying each amending act), `as-enacted` (each law as first published, amendments not applied) or `metadata-only` (catalogue entries, no law text) |
| `history_from`, `record_to`, `checked_on` | Where the record starts, the day it is complete to, the day it was last checked |
| `record_note` | Anything a reader must know about the record |
| `in_force_trailer` | The trailer holding each change's in-force day (default `In-force`); `baseline_trailer` and `correction_trailer` if used |
| `citation` | `{"file": "<regex over the corpus path with groups (folder, number)>", "cites": "<git grep -E pattern, {n} for the number>"}` |
| `scope.default_reach` | Optional: how a change reaches pending cases where no scope is recorded |
| `repeal_notice` | Optional: regexes (one or a list) for a line that says only that a provision is gone, in the corpus's own wording, added to the built-in ones; `false` turns repeal notices off for the corpus |

Trailers named for a day (`In-force`, `Enacted`, `Made`, `Published`, `Corrected`, `Text-as-of` and the like) hold a
YYYY-MM-DD date; a link goes in `Source:` (or `Text-source:`). `Consolidated:` is canonically the day the publisher's
consolidated text took force, with its link in `Source:`. Most corpora built before 4 November 2026 wrote the link in
`Consolidated:` instead, and their history cannot change, so readers take either: a date there can date a version (as
the `baseline_trailer`), a link is cited as the version's source. A `baseline_trailer` or `correction_trailer` dates a
change only when it holds a date.

Four more records change the answers:
- **`Redates: <commit> [enacted] <YYYY-MM-DD>|no-date`.** An append-only corpus corrects a version's date without rewriting it:
  a later commit carries one `Redates:` line per version it corrects (the line may repeat), naming a commit above it
  (in full or by a prefix of 7 or more). A date becomes the version's in-force day, and for an overlay correction also
  the first day its text applies (`Corrects: <act> <from>..`); `no-date` says the source gives none, so a law's version
  becomes text as of its recorded day. `Redates: <commit> enacted <YYYY-MM-DD>|no-date` corrects instead the day
  its law was made (the value of its `Enacted:`, `Adopted:`, `Made:` ... trailer, which readers show and judge a
  doubtful date by), or says the record has none; its in-force day stands. Readers apply it only when the commit's
  author is the maintainer, `Lexifina`; anyone else's, a line in another form, or a commit not above it is ignored.
- **`Retroactive: yes; <provision>`.** The version took force before its act was made, as that provision says, so its
  date is not marked doubtful. On a `Redates:` commit it covers every version that commit redates. A value that does
  not start with `yes` is ignored.
- **`data/acts.json`.** `{"acts": [{...}, ...]}`, one row per act: `path` (the act's folder, `slug` in older corpora),
  `status` (`in force`, `not yet in force`, `repealed`, `expired` or `annulled`), and the days `in_force`, `repealed`,
  `expired` and `annulled` as YYYY-MM-DD, with `repealed_by`, `expired_by` and `annulled_by` naming the ending law or
  ruling. Readers end every file under an act that is `repealed`, `expired` or `annulled` on that day (an annulment
  ends it like a repeal, and the reader says "annulled"), unless its status is `in force` or `not yet in force`; with
  no valid day they say it has ended but not from when. One rule decides what happens after the end, the same in
  `show`, `log`, `blame`, `words`, `diff`, `world`, search, `laws` and the timeline: a version dated after the end
  brings the file back into force only if its law was enacted (`Enacted:`, `Made:`, `Signed:` ...) on or after the end
  day, is not the law that ended the act (`repealed_by` names it, by official id or name), and its text is not a
  repeal note (`Norma derogada ...`, `(Derogada)`, `Norma anulada ...`, `[Repealed]`: a note is the end restated, not
  a re-enactment). Any other later version never takes force, and the end's `log` row names it; a law none of whose
  versions takes force is not listed by `laws`. A real later amendment to an ended act does bring its file back, and
  `show` says so. A correction (`Corrects:`) stops the day before its file's act ends; one starting after the end
  applies only once a later version has brought the file back. `in_force` is named when a provision is asked for
  before the record starts.
- **A repeal notice as the text.** Where a publisher keeps a repealed provision's number and prints only that it is gone
  (Sweden's `16 § Har upphävts genom lag (2011:1252).`, Georgia's `# მუხლი 26. (ამოღებულია)`, Malta's `Repealed by Legal
  Notice 99 of 2026.`, Spain's `(Derogado)`, Germany's `§ 5 (weggefallen)`, Romania's `Abrogat.`), the version holding
  that notice ends the provision on its day, as a deletion would: `show` says "repealed on <day> by <law>, the record
  keeps its repeal notice" and quotes it, with the exit code of an ended provision; `log` labels the row `repealed`;
  `world` and search trees leave the file out; `diff` shows the text removed; `blame` and `words` stop. Where the notice
  is the first version the record holds (a current-only record: every Swedish one), `show` says only "repealed", as the
  record holds neither the text nor the day of the repeal (the notice names the law). A later version with other text
  brings it back. The rule is conservative: once heading lines, the provision's amendment-history lines (`- Amended by:
  ...`) and quoted editor's notes (`> Se deroga por ...`) are set aside, every remaining line (the headings, when
  nothing else is left; at most four) must be the provision's number, then a repeal word in the corpus's language
  (`upphävts`, `ამოღებულია`, `repealed`, `deleted`, `derogado`, `suprimido`, `aufgehoben`, `weggefallen`, `abrogat`,
  `abrogé`, `ophævet`, `kehtetu`, `утратил силу` and others), then at most the law that made the repeal (`by ...`,
  `genom ...`, `por ...`, a dash or a bracketed citation): at most 40 words, and no rule words such as "shall" or "may".
  A text with any law beside the notice (`1) Aufgehoben 2) Die Regierung ...`), a sentence repealing another law (`The X
  Act is repealed.`, `Genom lagen upphävs lagen ...`) or `(Sin contenido)` stays text. On 4 November 2026 this ended
  3,554 Swedish, 1,517 Georgian, 1,345 Maltese, 6,650 Spanish, 465 Liechtenstein and 30 Nauruan provisions that were
  shown in force that day; 148 of 148 notices checked by hand were notices, and 1,400 other files read the same as
  before. A corpus adds its own wording with `repeal_notice` in `corpus.json`. The act-end rule's repeal notes are read
  by the same detector; after an act's end a note need only start as one (`Norma derogada, excepto su art. 7 ...`).
  Builders should still remove a repealed provision in the repealing law's commit (with the notice, if kept, as the last
  wording): the rule reads the history already written.

`tools/check_corpus.py` checks a repo against this before it is pinned. A missing `corpus.json` is a warning when the
repo ships `jurisdiction.json` or `data/repo.json` (readers then use defaults for the rest), and is counted when several
corpora are checked at once (`python tools/check_corpus.py <global-law checkout>` checks every corpus checked out there).
A `Redates:` or `Retroactive:` that readers would ignore is a warning (the history cannot take it back; a later
`Redates:` can correct it), as is each kind of bad `data/acts.json` row, with a count; a version in force before its act
was made is judged by the act's day as `Redates: <commit> enacted` corrects it; an `acts.json` that does not
parse fails.

## Tools

To browse a large corpus by act, give `list_provisions` the start of a folder name, for example
`mt/national/malta-law/sl/586.` for every instrument under Malta's Data Protection Act. You get one row per act, with
its title and last change.

| Tool | What it answers |
| --- | --- |
| `list_jurisdictions` | Every jurisdiction and body of law, how far each record reaches, how many provisions, and an example path. Start here. |
| `find_provision` | The path of a provision from its number ("1182", "Art. 16a", "reg 13"), a popular name from `aliases.json` ("Schuldenbremse", "automatic stay", "EHC plan") or a topic found in the text. |
| `list_provisions` | The provisions under a corpus or folder, with headings, as in force on a date. |
| `read_law` | (`include_text: false` for a cheap check of dates, laws and sources.) A provision's text on a date, with the law that last changed it, the next change, sources to cite and the record's limits. It says whether the words are still the same at the end of the record (`latest`). `in_force` is `true` or `false`, or `null` with `in_record: false` and `record_starts` when the date is before the record's first version of the provision and that version is a consolidated text, not the law taking effect: the record does not know, so a program should not answer. It adds "not the whole answer" notes where a later law reaches back over the date, or an effect changes how the provision applies without changing its words (`Modifies:`). |
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
`global-law://law/{path}?date={date}&offset={n}` gives any provision as in force on a date.

## Citing the official text

This tree is a copy. Every `read_law` answer starts with where to read and cite the law itself: the publisher's own
page, then a pincite (`Cite as:`). The structured answer has the same as `cite`: `official_url`, `shows` (what that page
holds), `pincite`, `version_url` (the publisher's text of the act in force then), `law_url` (the law behind the version)
and `archived_copies`. `resolve_citations` gives the same for each citation in a text. The server's instructions tell
the model to cite that page, never this server or its repository.

| Publisher | `official_url` shows |
|---|---|
| legislation.gov.uk | the provision itself as in force on the date asked (`…/ukpga/2014/6/section/42/2020-06-01`) |
| legislatie.just.ro (Romania) | the official consolidated text of the act in force on the date, in which to find the article; the portal's article anchors are numbered per page, not by article, so they cannot be built from the record |
| fedlex.admin.ch (Switzerland) | the act as in force from the version's day (`…/eli/cc/1999/404/20210101/de`) |
| gesetze-im-internet.de (Germany) | the § or article, as in force today only; the answer says when that differs from the text read |
| govinfo.gov (US Code) | the section in the latest edition, with the Public Law behind the version as `law_url` |
| legislation.mt (Malta) | the Chapter or instrument as in force today |

Links are given as the publisher's: an archived copy the record was read from (web.archive.org) is unwrapped and named
apart as provenance, and Lexifina's own reader (`Reader:` links) is never given as a source. Where the record holds no
link for a version, the answer says so rather than offer this tree.

## Long provisions and long calls

- **Long texts come in parts.** `read_law`, `compare_dates` and `who_wrote` give at most 40,000 characters of text at a
  time (about 10,000 tokens; `max_chars` sets 1,000 to 100,000). A longer text says "Part: characters 0 to 39,958 of
  6,541,961. For the next part, call again with offset=39958", and the structured answer gives the same as
  `text_part`, `word_diff_part`, `marked_part` or `lines_part`. Parts end at a line break or a space. One Spanish order
  is 6.5 MB, and over a thousand files pass 100 KB. `read_law` with `include_text: false` gives the length
  (`text_chars`), so a model can go straight to the end of a long act.
- **Other answers stop at 60,000 characters**, at a line break, and say how to narrow the question.
- **No call runs past 120 seconds**, whether the time goes to git or to the server's own work, such as comparing
  versions. A git process still running then is killed.
- **`who_wrote` stays quick on long provisions.** It credits by word up to 100,000 characters, and by line (git blame)
  past that or when the word-by-word pass takes more than 30 seconds, and says so (`fell_back`). Tracing words brought
  back after a temporary change ended is skipped for long provisions with many versions and stopped after 20 seconds
  otherwise; the answer says so (`traced`).
- **The server keeps answering while a call runs.** Tool calls and resource reads run in order on a worker thread;
  everything else, `ping` included, is answered at once. `notifications/cancelled` stops the call it names: its git
  process is killed, the server's own loops stop at their next check, and it gets no answer.

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
- Each tool call has 120 seconds in all, in git and in the server's own work, after which it stops and says so. A
  client can cancel a call, and the server answers other requests while one runs. Long texts come in parts. Lists are
  capped and say when they were cut. Searches look at no more commits than they show, and `resolve_citations` looks up
  at most 100 provisions.
- A client that stops reading cannot keep the server alive: a broken pipe drops the remaining work, and after stdin
  closes a reply stalled for 10 seconds ends the process.
- A message is limited to 1 MB. Bytes that are not UTF-8, JSON nested too deep and numbers too long to read are
  answered with a parse error. A corpus that is not checked out, or not readable at its pin, narrows an answer and is
  named; it does not stop the server. An internal error reports only its type, and the details go to stderr.
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
