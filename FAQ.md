# Questions and answers

The questions people asked most when this repository was posted. Figures are as of 4 November 2026; `manifest.json`
and `python3 tools/countries.py` give the current ones. [README.md](README.md) says how to use it, [MCP.md](MCP.md) how to use it from an AI model,
[REPRODUCE.md](REPRODUCE.md) how it is made, and [LICENSE.md](LICENSE.md) what you may do with it.

- [What it is](#what-it-is)
- [Dates](#dates)
- [Who a commit is by](#who-a-commit-is-by)
- [What is covered](#what-is-covered)
- [Accuracy and sources](#accuracy-and-sources)
- [Keeping it current](#keeping-it-current)
- [Size and infrastructure](#size-and-infrastructure)
- [Using it](#using-it): on your machine, from an AI model, in your product
- [Opening the folder in an AI coding tool](#opening-the-folder-in-an-ai-coding-tool)
- [Licence](#licence)
- [Taking part](#taking-part)

## What it is

### What is this?

The law of many jurisdictions as git histories. Each body of law is its own repository: a country's national law is
`lexifina/<country>-law`, a state's or city's `lexifina/<country>-<place>-law`. This repository holds them all as git
submodules, arranged by jurisdiction, with an index of what each one holds.

Where a repository has the law's history, each commit is one law taking effect: the files are the text as it stood
after that law, the commit is dated by the day the change took force, and its author is the law that made it. So the
text can be read on any date, and `tools/law.py blame` names the law behind each line. Not every repository has that
history yet, which `manifest.json` says for each (`history`):
- 265 corpora (`in-force`, `replayed`) hold every version, each credited to the law that made it;
- 189 (`as-enacted`) hold each law as passed, not yet merged into the texts it amends;
- 161 (`current-only`) hold today's text only, dated by its latest version;
- 95 (`metadata-only`) hold a list of laws without their text.

Across the tree, about three commits in four are a law taking effect. The rest are starting texts (the text as first
found, credited to its publisher), changes the publisher shows without naming a law, and maintenance, each labelled
in its commit message.

### Why git?

Because the questions lawyers ask of legislation are the questions git answers: what this said on a date, which law
wrote these words, what changed between two dates, everything one law changed. Git also gives every version a content
hash, works offline and can be copied anywhere, so the record does not depend on any one website staying up.

Plain git answers by commit order. `tools/law.py` (`show`, `blame`, `diff`) and the MCP server answer by in-force
date, and give the in-force answer for every corpus. The two agree only where a corpus's commits are in in-force
order and none was corrected later. There, `git show` at the last commit in force on a day is the text on that day,
`git blame` names the law behind each line, and `git log --author` is everything one law changed. Some corpora append
commits out of in-force order (Canada's federal acts, Romania's national acts, partly Czechia's) or add
corrections to earlier versions later (Malta's), and there plain git gives the wrong text or the wrong law: on
sampled Canadian files, 135 of 147 days gave a different text and 38 of 50 blames a different law.

To see whether a corpus's commits are in in-force order, run this in it (Git Bash on Windows). It prints nothing
when they are, and the first date out of order when they are not:

```sh
git log --reverse --format='%(trailers:key=In-force,valueonly)' | grep . | sort -c
```

Use the corpus's own `in_force_trailer` from `manifest.json` where it is not `In-force`.
`python tools/check_corpus.py <corpus>` warns of commits appended out of order ("in force before a commit above
them"), but not of Malta's corrections, which this line catches. A date changed later by a `Redates:` commit passes
both, so use `law.py` whenever the answer matters.

### Isn't this already done?

Many publishers already offer versioned law: legislation.gov.uk, Austria's RIS and Germany's Gesetze im Internet
publish versions, and AustLII and others collect them. Some of it is on git already, such as `bundestag/gesetze`
(no longer updated) and DocPatch's Grundgesetz, which this repository builds on. What is new here is one format for
every jurisdiction: one commit per law per in-force day, the law as author, the same tools and the same dates
everywhere, so one query or one model can work across all of them. Each country's `SOURCES.md` names the publisher
and any earlier work its history is built from.

### Is it a legal database or legal advice?

Not yet a full legal database, and not legal advice. Today it is legislation and regulations, built from official
publishers, each provision at its own path so that a pinpoint citation leads to its text on any date, with its limits
stated. It says what the text was, when and by which law, not what the law means for a case. See
[Can I rely on it?](#can-i-rely-on-it-for-legal-work).

Case law comes next. The aim is the whole of the law in one record: legislation, regulations, case law and the
secondary authorities that interpret them, each linked to the provisions it applies.

## Dates

### Why do some commits say 1 January 1970?

Ignore the date git shows; the real dates are in the commit message. Every commit carries them as lines at the end:
`In-force:` (the day the change took effect; `In-Kraft:` in German law), `Enacted:`, `Published:` and so on. The
tools read only those lines, so a provision read on 1 June 1955 gives the text in force that day.

Git cannot record a date before 1 January 1970, so a law that took effect earlier shows 1 January 1970 on GitHub, one
second apart from its neighbours to keep them in order. 134 corpora reach back before 1970.

GitHub also once showed country folders here as "last changed 57 years ago". That came from this repository's first
build and stopped on 2 November 2026: a folder's date here is now the day its record last moved.

### Which date is the commit's date?

The day the change took force, usually at noon in the jurisdiction, so the day reads the same in every time zone. The other
dates are trailers in the commit message. A typical Romanian commit ends:

```
Law: Legea nr. 94/2026
Kind: law
Enacted: 2026-06-10
Published: 2026-06-10
In-force: 2026-06-13
Source: https://legislatie.just.ro/Public/DetaliiDocument/311297
Consolidated: https://web.archive.org/web/20260626113712id_/https://legislatie.just.ro/Public/DetaliiDocument/120611
```

`manifest.json` names the trailer each corpus uses for its in-force date. A law can be appended after a later one
(an older act found late), so the tools choose the version by `In-force:`, not by position in the history.

### What about laws passed but not yet in force?

Most corpora keep them on a `future` branch until their day; a few keep them on `main`, dated ahead, and the tools
show them only from that date. `manifest.json` says which (`future_branch`).

The readers (`tools/law.py` and the MCP tools) also read a corpus's future branch once a law on it is due: the tree
records each branch's tip beside the corpus's pin, in `data/future-pins.tsv`, written in the same commit as the pins,
so a reading stays reproducible. Each version still shows only from its in-force day. A branch that has fallen behind
main is not recorded, and a row made for an earlier pin is not read; in both cases, and when your clone lacks the
branch's commit, the reader shows main alone and says that due laws may be missing, with the command that fetches
them.

### What about commencement, transitional provisions and retroactive law?

Where the publisher gives a date per provision, each provision changes on its own day, so a law that commences in
stages is several commits. A change that applies to a period before it was made carries a `Retroactive:` trailer,
and `tools/check_corpus.py` flags any version dated before its act without one. Transitional rules (which text
applies to cases begun before a change) are recorded where the source states them, as `Applies:` trailers, and read
by the `applies_to_case` tool; few corpora have them yet.

## Who a commit is by

### Who is the author of a commit?

The law that made the change, with an address that cannot exist so that it is never mistaken for a person:
`Legea nr. 94/2026 <legea-94-2026@legislatie.invalid>`, `Pub. L. 116-136`, `S.I. 2020/471`. So `git blame` and
`git log --author` name laws. The committer is Lexifina, which built the record. A commit that is not a law (a
documentation change, a correction of the record) is by Lexifina, and its `Kind:` says what it is.

### Why does a German commit say Konrad Adenauer signed it off?

The Grundgesetz record lists the people who signed each amending law (`Unterzeichnet:`, `Signed-off-by:` in the
first version), because the official gazette prints them. It does not mean they wrote the text or made the commit;
the author is the law.

### Can I see who proposed or voted for a law?

Not in general. The Grundgesetz record carries the vote and who introduced each amendment (`Abstimmung:`,
`Initiative:`). Most publishers' legislation databases do not carry votes, so no other corpus does yet.

## What is covered

### How much is here?

On 4 November 2026, 710 corpora (bodies of law: a country's national law, a state's, a city's, or one court's or
agency's) from 208 countries and territories, about 306,000 acts and more than 650,000 commits; `manifest.json` has
today's figures. They are not all alike, and each says
which kind it is in `manifest.json` (`history`):

| Kind | Corpora | What it holds |
|---|---:|---|
| `in-force` | 259 | every version, each dated by the day it took force |
| `as-enacted` | 189 | each law as passed, not merged into the texts it amends |
| `current-only` | 161 | today's text only, as the publisher gives it |
| `metadata-only` | 95 | a list of the laws, without their text |
| `replayed` | 6 | past versions rebuilt by applying each amending act in turn, where the source publishes only amendments |

`coverage`, `history_from` and `record_to` give each corpus's span. A search that finds nothing means nothing in the
record, not nothing in the law; the tools say so on every such answer.

### My country, state or province is missing, or nearly empty.

Some are thin because their publisher is hard to read automatically, some because their turn has not come. For
example, Austria has only the Federal Constitution and the Data Protection Act so far, India 10 national acts and
Maharashtra's, and Quebec and Arizona are in the tree with little text. Wisconsin is missing because its publisher
refuses connections from outside the US. Three repositories (Nauru, Bermuda, Ontario) are being rebuilt from a few
acts to their whole statute book and are pinned again when done (`not_pinned`). `python3 tools/countries.py` lists
everything in the tree; to ask for a jurisdiction, open an issue naming its official publisher.

### Is "UK law" one jurisdiction?

No, and the tree does not treat it as one. The UK corpus keeps each legislature's Acts in its own folder: the UK
Parliament (`ukpga/`), the Scottish Parliament (`asp/`), Senedd Cymru (`anaw/`, `asc/`, `mwa/`) and the Northern
Ireland Assembly (`nia/`, with the earlier `apni/` and `mnia/`), as legislation.gov.uk files them. Each provision's
file has an `extent:` line (England and Wales, Scotland, Northern Ireland) where the publisher states it. Statutory
instruments are here only for one, the SEND Regulations 2014, part of nine provisions kept with a fuller history; the
rest are not here yet.

### Is case law included?

Not yet, beyond a first hand-checked sample of judgments in `judgments/`; it is the next thing to be added. For now
this is legislation and regulations. Some corpora record court decisions that change the text itself, such as a constitutional
court striking a provision down (`Kind:` court ruling), because they are part of the text's history. For case law,
see the Free Law Project (US), Find Case Law (England and Wales) and AustLII. The `check_precedent` tool takes a
judgment's own quotation of a provision and says whether the law still reads that way, which is where the two meet.
Case law can change what a provision means without changing a word, which a record of text cannot show.

### Are laws kept in their original language?

Yes: the text is in the language the official publisher gives, and nothing is machine-translated. Where a
jurisdiction publishes in more than one official language, the corpus says which it holds (`language` in
`manifest.json`, where set).

### Why are German folder names in lower case, when the abbreviations are not?

They are the identifiers the publisher itself uses in its addresses (`gesetze-im-internet.de/bgb/` is `bgb/`), kept
so that each folder maps to its official page and so the paths work on file systems that ignore case. The official
title is the first line of each act's `index.md`.

## Accuracy and sources

### Can I rely on it for legal work?

Use it to find, compare and trace text, then check the official source before relying on it. Every commit names the
page it was taken from (`Source:`), many link an archived copy of that page as fetched (`Consolidated:`), and each
country's `SOURCES.md` and `REPRODUCE.md` say how its record was obtained. Consolidated texts on official sites are
often themselves not the authoritative version, which a record built from them inherits.

### How do I cite it?

Cite the official text: every answer from the tools names the publisher's page and a pinpoint citation. To record the
exact version you read, give the repository and commit as well, for example `lexifina/romania-law@56122abd49ce`,
`lege/2015/227/art-004.md` (article 4 of the Fiscal Code). On GitHub, press `y` on a file to get its permanent link:
<https://github.com/lexifina/romania-law/blob/56122abd49cecb30312d69d341ab1ff895e0e4b6/lege/2015/227/art-004.md>.
Commits are never rewritten, so the link keeps showing the same text.

### How is it checked?

- Each country repository's `REPRODUCE.md` records how its history was built, from which source and on which day.
- `tools/check_corpus.py` warns of dates earlier than the act, a third of a corpus dated to one day (a download day
  posing as an in-force date), corrections without the commit they correct, and similar problems.
- `tools/verify.py` checks that every pin in this repository moves only forward and is held by its repository.
- The tests (`python -m unittest discover -s tests`) and [performance/](performance/) check the tools against small
  corpora built for the test and against each corpus's own tools.

### What happens when a publisher quietly fixes a typo, or the record is wrong?

Nothing is folded in silently. A change that no law explains gets its own commit, labelled (`Kind:`), and a mistake in
the record is fixed by a correction commit that names the commit it corrects (`Corrects:`), with its reason. The
history is never rewritten, so a citation of an older commit still resolves to what it said.

### How are repeals and renumbered provisions shown?

A repeal is a commit by the repealing law on the day it took force, which removes the provision's file (or, where the
publisher keeps a repealed provision's heading, leaves its status). Reading it afterwards says when and by which law
it went. A renumbering is a commit by the law that renumbered it, moving the text to its new path, so
`git log --follow` traces it; files moved by the record itself (a change of layout) keep one history under the new
path, and `data/moved-paths.tsv` maps corpora that moved folder.

### What about a law that changes another without naming it?

The record holds the text the publisher consolidates. Where the publisher shows a change but no law for it, the
commit says so (`Kind:` with no law named) rather than guessing one.

## Keeping it current

### How is it kept up to date?

In two layers. Each country repository is extended from its official publisher as the publisher releases new law,
appending commits and never rewriting earlier ones. How often depends on the country, and each corpus records how far
its record goes and when it was last checked (`record_to`, `checked_on` in `manifest.json`): 695 of the 710 were
checked between 28 October and 3 November 2026. This repository then moves each submodule's
pin forward to its repository's new commits, every few minutes, by fast-forward only.

### How do I know a record is current for my question?

Ask the tools: `list_jurisdictions`, and every answer, state where each record starts and ends. A provision read on a
date after `record_to` is the latest text in the record, which the answer says, not proof that nothing changed since.

### After `git pull`, some countries are behind.

The tree moves pins every few minutes, so a pull brings new pins that your checkouts do not have yet. Run
`git submodule update --init` (and `git submodule sync` after corpora move). The tools name any checkout that is
behind and leave it out of whole-tree answers instead of answering from old text.

## Size and infrastructure

### How big is it, and will GitHub cope?

Each body of law is its own repository, so no single repository holds the world. This repository is the index: about
370 MB of history without any law, or about 34 MB cloned with `--depth 1`, which is all the tools need. A
country is usually far smaller than Romania's 1.7 GB, and you download only the ones you add:

```sh
git clone --depth 1 https://github.com/lexifina/global-law && cd global-law
python3 tools/countries.py add romania france
```

Everything at once (`--recurse-submodules`) is many GB. `--filter=blob:none` instead of `--depth 1` keeps the index's
history without its file contents. Don't clone a country's repository with `--depth`: its dates are read from its whole
history. `countries.py add --no-files` fetches a history without writing its files, which is all the tools need.

### What if GitHub goes down?

Git does not need it. Every clone is a full copy that works offline and can be pushed anywhere else; the tools and
the MCP server read only the local clone.

### Can I download it as JSON, CSV or Parquet?

Not as a separate dataset yet: git is the format. The text is Markdown, one file per provision, and the dates, laws and
sources are in each commit's trailers. `manifest.json` describes every corpus as JSON, and many corpora also ship
tables in `data/` (`laws.csv`, `versions.json`, `commits.csv`; Romania's `acts.json`). There is no Parquet file or
Hugging Face dataset yet. The MCP server's answers are structured JSON, so it can serve as the export.

### Is there an index, so a program does not have to read everything?

Yes. `manifest.json` lists every corpus with its publisher, span, kind and the trailer holding its dates, and each
folder's `jurisdiction.json` names its level, its code and what is inside. The MCP server's `list_jurisdictions` and
`find_provision` answer from them before reading any law.

## Using it

### How do I use it on my own machine?

Clone the index, add the countries you want, and ask by date:

```sh
git clone --depth 1 https://github.com/lexifina/global-law && cd global-law
python3 tools/countries.py add united-states/federal/usc
python3 tools/law.py show 2022-05-01 united-states/federal/usc/title-11/1182.md     # the text on a date
python3 tools/law.py blame 2022-07-01 united-states/federal/usc/title-11/1182.md    # the law behind each line
python3 tools/law.py diff 2022-05-01 2022-07-01 united-states/federal/usc/title-11/1182.md
```

You need git and Python 3.9 or newer, nothing else, and it works offline. On Windows, type `py` or `python` where
these examples say `python3`. Each country's repository is also ordinary
git, so `git log`, `git blame` and `git grep` work on it directly; use `law.py` when the date or the law matters,
because it reads the `In-force:` lines rather than git's dates and commit order ([Why git?](#why-git)).
[README.md](README.md) lists every command.

### How do I use it from an AI model?

Through the MCP server in `tools/mcp_server.py`. MCP (the Model Context Protocol) is how AI assistants such as Claude,
Cursor, VS Code's Copilot and Codex call outside tools. Open the clone in one of them, agree to start the server (see
[below](#does-opening-the-clone-start-a-program)), and ask in plain words: "What did 11 U.S.C. §1182(1) say on
1 May 2022, and which law last changed it?" For any other MCP client, point it at the clone:

```json
{ "mcpServers": { "global-law": { "command": "git", "args": ["-C", "/path/to/global-law", "-c", "alias.global-law-mcp=!sh tools/mcp.sh", "global-law-mcp"] } } }
```

[MCP.md](MCP.md) has the setup for each client, and [lexifina.com/watch/global-law/mcp](https://lexifina.com/watch/global-law/mcp)
walks through using it for one country.

### What can it answer that a web search can't?

The server has 18 read-only tools. Besides finding a provision and reading it on any date, they answer:
- which law wrote each word (`who_wrote`), and when words entered or left the law (`phrase_history`);
- what changed between two dates, and which laws did it (`compare_dates`, `changes_between`, `laws_between`);
- what relies on a provision: what cites it and what uses a term it defines (`what_else_changes`);
- every citation in a brief or judgment, resolved to its provision on a date (`resolve_citations`);
- whether a judgment's quotation of a provision is still the text in force (`check_precedent`);
- which later changes reach a case begun on a date, where the record holds that (`applies_to_case`).

Every answer gives the publisher's own page to cite, not this repository, and states where the record starts and
ends, so the model can say when the record cannot answer. In blind tests, a model given only these tools answered 26
of 26 questions correctly and said where the record ran out.

### Can I build it into my own product?

Yes. The tools and this repository are CC0: use them in a product, paid or free, with no permission or credit needed.
The law text is under each country's repository's terms (see [Licence](#licence)), and a few restrict it: Kenya's
publisher licenses its text CC BY-NC (no commercial use) and asks for an agreement before bulk or AI use. Read a
country's `LICENSE` before shipping its text. Three ways in:
- **The MCP server**, for an AI feature. It speaks MCP over stdin and stdout, so any agent framework with an MCP
  client can start it as a subprocess. Run one process per user or per tenant, from a clone on your server.
  `GLOBAL_LAW_JURISDICTIONS=romania,france` limits it to the countries you serve, and `GLOBAL_LAW_AUDIT_DIR` logs each
  call (a keyed hash of the arguments, never the arguments).
- **`tools/law.py`**, for a backend or a batch job: the same answers as commands, standard library only.
- **The repositories themselves**, for your own index or search: plain git, with `manifest.json` describing every
  corpus and each commit's trailers giving its dates, its law and its source.

To stay current, run `git pull` and `git submodule update` on a schedule; the pins move every few minutes as countries
publish. Show your users the official page each answer cites, and the limits it states.

### Is there a hosted API?

No. The server runs where the clone is, which is why it needs no account, no key and no network, and costs nothing per
call. To offer it over the network, put it behind your own MCP gateway, one process per user, and keep its limits
(120 seconds a call, long texts in parts).

### How fast is it?

The first question indexes a corpus's history once (a few seconds on most; the index is kept in
`.git/global-law-cache`), and later ones are quick. For the largest corpora, writing git's commit graph speeds up
history queries about threefold (`git submodule foreach --quiet 'git commit-graph write --reachable --changed-paths'`).
[performance/](performance/) records the timings, run by run.

## Opening the folder in an AI coding tool

### Does opening the clone start a program?

It can, by design. The clone carries project settings for Claude Code (`.mcp.json`, approved by
`.claude/settings.json`), Cursor (`.cursor/mcp.json`), VS Code (`.vscode/mcp.json`) and Codex (`.codex/config.toml`)
that start this repository's MCP server, `tools/mcp.sh`, which runs `tools/mcp_server.py` with Python. Claude Code and
Codex read these settings only once you trust the folder; VS Code waits for you to start the server; Cursor may list
it as off until you turn it on.

What the server does, which you can check in those two files:
- It only reads. It runs `git ls-tree`, `show`, `cat-file`, `log`, `grep`, `blame` and `diff` on the clone, and the
  only thing it writes is its own index cache under `.git/global-law-cache` (and, if you set
  `GLOBAL_LAW_AUDIT_DIR`, a log of its calls there).
- It makes no network calls. It uses Python's standard library and git, and never fetches, pulls or pushes.
- It treats law text and commit messages as data to report, never as instructions (`AGENTS.md`).

To open the clone without it, don't trust the folder, turn the server off in your tool's MCP settings, or delete the
four settings files from your clone.

### Was this built with AI?

Yes. Most of the code was written by Claude Code, one session per country or group of countries. Each session read
the publisher's site or API, its robots.txt and terms of use, and wrote the scripts that download each version and
write the history. Lexifina set the goals, chose the sources and made the design decisions. That is why the checks
above exist, and why every answer the tools give is traced to a commit you can inspect.

## Licence

### Can you put the law under CC0?

Only our own work. [LICENSE.md](LICENSE.md) dedicates this repository (the jurisdiction tree, the manifest, the
tools, the tests, the documentation and the visualisations) to the public domain under CC0, to the extent the law
allows. The law text is not in this repository: it is in each country's repository, under that repository's
`LICENSE` and the terms its publisher gives, which `SOURCES.md` quotes. Official texts are free of copyright in many
countries but not all (Crown copyright, or annotated codes in some US states), and nothing here changes their status.

### Won't companies just take it?

They may. It is published so that anyone can use it, and the law should be freely readable by everyone.

## Taking part

### Can I add law, or report a mistake?

Yes. Anyone can propose a change, as an issue or a pull request, and Lexifina reviews each one.
[CONTRIBUTING.md](CONTRIBUTING.md) says where each kind of change goes and the few rules that keep the record
trustworthy: law text comes from its official source, never from a hand edit; history only grows, so a mistake is
fixed by appending a correction with its evidence; and builders respect each publisher's terms. For a mistake, the
quickest report is an issue with the path, the date and the official page it should match. For a missing
jurisdiction, an issue naming its official publisher.

### Will you model law formally, as code?

Not here. The text is kept as published, one unit per line, so it can be the input to such work.
