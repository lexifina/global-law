# Features

Every feature of this repository, and the standard every corpus in it must support, whether it holds law or case law. A new corpus type is added only when each feature below still works on it (for example `git blame`, `law.py blame` and `who_wrote` crediting each line to the law or decision that wrote it), with a test per feature, and when none of the timed features in [performance/](performance/) gets slower.

Each entry gives the question it answers, how to call it, an example and its limits. Each id (for example `cli.show`, `mcp.read_law`) is the key used in the performance measurements.

## Words used

- **Act**: One law as passed, for example Argentina's Ley 25.326 or the US Bankruptcy Code.
- **Provision**: One article or section of an act. In the tree each provision is usually one file, for example `germany/bund/acts/grundgesetz/artikel/013.md`.
- **Amending law**: A later law that changes the words of a provision. In the record, each amending law is the author of the change.
- **In force**: The day a text starts to apply. Every date in this tree is that day, not the day the law was passed or published.
- **Corpus**: One body of law, usually one country's acts, kept as its own git history; a court's decisions are corpora too. `list_jurisdictions` and `tools/countries.py` count those the tree pins at the time of asking; a clone holds the ones you add.
- **Record starts**: Most corpora hold history only from some date. Before it, the answer is "the record does not reach back", not "no law".
- **Current only**: Some corpora hold today's text alone, because the publisher keeps no past versions. They answer what the law says now, not what it said.
- **As enacted**: Some corpora hold each law as first published, with later amendments not applied.
- **Future branch**: Changes already enacted that take effect later, kept beside the main history.

## Index

| Id | Feature | Question it answers |
|---|---|---|
| `cli.show` | law.py show | What did this provision say on that day? |
| `cli.log` | law.py log | Every time it changed, and by which law? |
| `cli.blame` | law.py blame | Which law wrote each line? |
| `cli.words` | law.py words | Which law wrote each word? |
| `cli.diff` | law.py diff | What changed between two dates? |
| `cli.today` | law.py today | Is the wording from that date still the wording now? |
| `cli.world` | law.py world | Where did every country's law stand on one day? |
| `cli.laws` | law.py laws | Which laws took effect in this window? |
| `mcp.list_jurisdictions` | list_jurisdictions | What can I ask about, and how far back does each record go? |
| `mcp.find_provision` | find_provision | Where is "Art. 16a" or "automatic stay"? |
| `mcp.list_provisions` | list_provisions | What is in this act, as it stood then? |
| `mcp.read_law` | read_law | What did it say, who last changed it, what changes next? |
| `mcp.world_on_date` | world_on_date | Every jurisdiction on one day? |
| `mcp.who_wrote` | who_wrote | Which law wrote these words? |
| `mcp.compare_dates` | compare_dates | How did it change between two dates? |
| `mcp.provision_history` | provision_history | Every law that changed it, with three dates? |
| `mcp.laws_between` | laws_between | What took effect in this window? |
| `mcp.search_law` | search_law | Where do these words appear in the law in force then? |
| `mcp.changes_between` | changes_between | What changed between two dates, everywhere? |
| `mcp.search_changes` | search_changes | Which changes mention "temporary" or "COVID"? |
| `mcp.phrase_history` | phrase_history | When did these words enter or leave the law? |
| `mcp.law_details` | law_details | What did this one law change? |
| `mcp.resolve_citations` | resolve_citations | Is every citation in my brief still good? |
| `mcp.check_precedent` | check_precedent | Has the text this court applied changed since? |
| `mcp.applies_to_case` | applies_to_case | Which text governs a case commenced on a date? |
| `mcp.what_else_changes` | what_else_changes | What relies on this provision? |
| `mcp.prompts` | 3 prompts | Ready-made research questions for an assistant |
| `mcp.resources` | 4 resources | The tree's own documents and manifest for an assistant |
| `countries` | countries.py | Which countries does my copy hold and serve? |
| `future` | Future branches | Is anything already enacted that will change it? |
| `viz.law-in-motion` | Law in Motion | How the world's law grows and waits, in charts |
| `viz.law-drawn` | Law, Drawn | Calendars and growth of law-making, in ten charts |
| `viz.life-of-a-provision` | The Life of a Provision | How single provisions are amended and survive |
| `readers` | /watch readers | Read and replay the law in a browser |
| `setup.mcp` | Assistant setup | How an assistant connects to a clone |

## Command line: tools/law.py

Eight commands that read the law, plus `law.py caselaw-index`, which indexes the case law checked out after a pull (see the README), run in a terminal inside a clone (`python tools/law.py …`). Standard library only, offline, plain text. Each answer ends with the record's limits that apply: where the record starts, current-only text, capture days, act ends and repeal notices.

### law.py show (`cli.show`)

*What did this provision say on that day?*

- **Call:** `law.py show <date> <path>`
- **Does:** Prints the version of the file with the latest in-force date on or before the date, whatever order the commits were made in. Corrections apply. A file whose text is only a repeal notice reads as repealed.
- **Example:** `law.py show 2022-05-01 united-states/federal/usc/title-11/1182.md`
- **Limits:** Before a record starts it says so rather than showing text. Metadata-only corpora give a catalogue entry, not text.

### law.py log (`cli.log`)

*Every time it changed, and by which law?*

- **Call:** `law.py log <path>`
- **Does:** Each dated version in in-force order, with the law, its enacted or made date and its published date, plus act ends, repeal notices and corrected credits.
- **Example:** `law.py log united-states/federal/usc/title-11/1182.md` gives 5 versions, 2020-02-19 to 2024-06-21.
- **Limits:** One file only: a provision renumbered into another file starts a new history. Exact renames are followed.

### law.py blame (`cli.blame`)

*Which law wrote each line?*

- **Call:** `law.py blame <date> <path>`
- **Does:** Credits each line to the law that wrote it, by in-force date. Uses git blame where the corpus was committed in order and gives the same answer, and replays versions otherwise.
- **Example:** `law.py blame 2022-07-01 united-states/federal/usc/title-11/1182.md`
- **Limits:** Lines are often whole paragraphs, so a one-word amendment takes the whole line.

### law.py words (`cli.words`)

*Which law wrote each word?*

- **Call:** `law.py words <date> <path>`
- **Does:** Word-level credit, with moves inside the file and an island rule. For long files the line matching uses git's histogram diff.
- **Example:** Grundgesetz Art. 13 today: 88 words from the Grundgesetz (1949), 256 from the 45th amendment (1998).
- **Limits:** A heuristic, not exact authorship. Current-only records credit every word to the starting text.

### law.py diff (`cli.diff`)

*What changed between two dates?*

- **Call:** `law.py diff <date a> <date b> <path>`
- **Does:** A word diff of the versions in force on each date.
- **Example:** `law.py diff 2022-05-01 2022-07-01 united-states/federal/usc/title-11/1182.md`
- **Limits:** One path: text moved to another file shows as removed.

### law.py today (`cli.today`)

*Is the wording from that date still the wording now?*

- **Call:** `law.py today <date> <path>`
- **Does:** Says "same", or gives a word diff against today's text.
- **Example:** `law.py today 2022-07-01 united-states/federal/usc/title-11/1182.md`
- **Limits:** Uses the pinned record and the local clock. After the record ends, "same" is not proof of no change.

### law.py world (`cli.world`)

*Where did every country's law stand on one day?*

- **Call:** `law.py world <date>`
- **Does:** The last law in force in each corpus on the date. Corpora not checked out, behind their pin or unreadable are named, not silently skipped.
- **Example:** `law.py world 1990-09-29`
- **Limits:** The first run indexes every checked-out corpus, which can take minutes on a large clone. It gives the last change per corpus, not a comparison of content.

### law.py laws (`cli.laws`)

*Which laws took effect in this window?*

- **Call:** `law.py laws <from> <to> [where]`
- **Does:** Laws by in-force day, filtered by folder, ISO code, alias or level. Publisher captures and starting texts are named as left out, not listed as laws.
- **Example:** `law.py laws 1990-01-01 1990-12-31 germany`
- **Limits:** Empty for current-only and baseline records, which hold no law events.

## AI assistant tools: tools/mcp_server.py

Eighteen read-only tools an assistant such as Claude, Codex, Cursor or VS Code calls in a clone. Standard library only, over stdio. Every answer states the limits of its record. Shared limits: a call stops at 120 seconds; lists stop at 500 items; answers stop at 60,000 characters, and long texts come in 40,000-character parts; queries, law names and paths are at most 300 characters.

### list_jurisdictions (`mcp.list_jurisdictions`)

*What can I ask about?*

- **Does:** Every jurisdiction and body of law in the tree: which are served by this clone, how far each record reaches, its history type, an example path, and what is left out and why. The tool to start with.
- **Arguments:** none
- **Limits:** Only checked-out corpora are served; the rest are listed with the command that adds them.

### find_provision (`mcp.find_provision`)

*Where is "Art. 16a" or "automatic stay"?*

- **Does:** Turns a number ("1182", "Art. 16a", "reg 13"), heading words ("debtor", "Asylrecht") or a popular name into a path. Reads citations through the same per-country registry as resolve_citations.
- **Arguments:** `query`, `jurisdiction`
- **Limits:** Popular names come from aliases.json, and the abbreviations lawyers and courts write for acts from the tables in `data/` (`de-`, `nl-`, `fr-`, `pl-`, `fi-` and `swiss-aliases.json`). The heading index covers up to 400,000 files, with a text search beyond.

### list_provisions (`mcp.list_provisions`)

*What is in this act, as it stood then?*

- **Does:** The provision files under a corpus or folder on a date, with headings. `by_folder` gives one row per act with its title and last change. A partial name lists folders that start with it (`malta/national/acts/sl/586.` lists every instrument made under Cap. 586).
- **Arguments:** `path`, `date`, `by_folder`
- **Limits:** No chapter or part boundaries: the record does not hold them.

### read_law (`mcp.read_law`)

*What did it say, who last changed it, what changes next?*

- **Does:** The text in force on a date, the law that last changed it, the next change (including enacted future changes), sources, a cite block, the latest text, and notes on what the answer does not cover.
- **Arguments:** `path`, `date`, `include_text`
- **Example:** `read_law path=argentina/national/acts/ley-25326/art-007.md date=2015-03-01`
- **Limits:** Before a consolidated record starts, `in_force` is null and the answer says where the record starts. Text comes in 40,000-character parts.

### world_on_date (`mcp.world_on_date`)

*Every jurisdiction on one day?*

- **Does:** For one date, the last change in force in each served corpus and the next one. A `jurisdiction` narrows it to one country or corpus (a question about France does not list every US court), and `kind` to laws or judgments.
- **Arguments:** `date`, `jurisdiction`, `kind`

### who_wrote (`mcp.who_wrote`)

*Which law wrote these words?*

- **Does:** Credits each word (or line) of a provision on a date to the law that wrote it, with a count of words per law. Words that come back when a temporary change ends are credited to their first author (`restored_by`).
- **Arguments:** `path`, `date`, `granularity`
- **Example:** 11 U.S.C. §1182(1): the CARES Act rewrote it on 2020-03-27; when that ended on 2022-03-27 the words returned to Pub. L. 116-54.
- **Limits:** Word credit up to 100,000 characters or 30 seconds, then line credit (`fell_back`). Restored-word tracing stops after 20 seconds.

### compare_dates (`mcp.compare_dates`)

*How did it change between two dates?*

- **Does:** A word diff between two dates and the laws that took effect in between.
- **Arguments:** `path`, `date_a`, `date_b`

### provision_history (`mcp.provision_history`)

*Every law that changed it, with three dates?*

- **Does:** Every law that changed a provision, oldest first, with in-force, enacted or made, and published dates and sources.
- **Arguments:** `path`
- **Limits:** One file only, as law.py log.

### laws_between (`mcp.laws_between`)

*What took effect in this window?*

- **Does:** Every law that took effect between two dates, in all jurisdictions or one, in order, with the number of provisions each changed.
- **Arguments:** `start`, `end`, `jurisdiction`, `max_results`
- **Limits:** Up to 500 laws.

### search_law (`mcp.search_law`)

*Where do these words appear in the law in force then?*

- **Does:** Searches the text of all law in force on a date, across every jurisdiction or one. Plain text matches typographic dashes and quotes; a regex is optional. A miss falls back to the change notes.
- **Arguments:** `query`, `date`, `jurisdiction`, `case_sensitive`, `max_results`
- **Limits:** Exact words or a regex, not meaning. 200 provisions, shared round-robin across corpora.

### changes_between (`mcp.changes_between`)

*What changed between two dates, everywhere?*

- **Does:** Every provision added, changed or removed between two dates, with the laws that changed them.
- **Arguments:** `date_a`, `date_b`, `jurisdiction`
- **Limits:** 300 provisions shown across corpora. Current-only corpora show nothing.

### search_changes (`mcp.search_changes`)

*Which changes mention "temporary" or "COVID"?*

- **Does:** Searches the record of changes (each commit message: the law, its dates, what it did), not the text of the law.
- **Arguments:** `query`, `start`, `end`, `jurisdiction`
- **Limits:** Change notes vary by corpus; many say only "Stand am …".

### phrase_history (`mcp.phrase_history`)

*When did these words enter or leave the law?*

- **Does:** Each change whose added or removed text contains the words, with in-force dates, in every jurisdiction or one. Renames are followed. Finds words no longer in force.
- **Arguments:** `query`, `jurisdiction`, `regex`
- **Example:** "datos sensibles": Chile 1999-08-28, Argentina 2000-11-11, Uruguay 2008-08-28, Peru 2011-07-04, Colombia 2012-10-18 (one country per call).
- **Limits:** 3,000 changed files per corpus. Across many corpora in one call it can reach the 120-second limit.

### law_details (`mcp.law_details`)

*What did this one law change?*

- **Does:** The full record of one law: its commit message with every trailer (enacted, in force, published, sources, scope), the provisions it changed, and what it did to each one's words (a word diff, "layout only" or "text moved between provisions").
- **Arguments:** `law` (for example "Pub. L. 117-151", "36. Änderung") and `corpus`
- **Limits:** 10 commits per corpus and word diffs for up to 60 provisions.

### resolve_citations (`mcp.resolve_citations`)

*Is every citation in my brief still good?*

- **Does:** Reads every citation in a text (a brief, a judgment, an email) and resolves each to its provision with its state on a date: in force or not, the law that last changed it, the next change. Citation forms are declared by country in one registry, so one country's form never takes another's citation. It also says how many it left out.
- **Arguments:** `text`, `date`
- **Covers:** law: US Code; Grundgesetz and German federal acts by abbreviation ("§ 823 BGB"); every Swiss federal act by abbreviation, in German, French or Italian; UK Children and Families Act 2014 and SEND Regulations 2014; Dutch acts ("artikel 6:162 BW"); French codes and the Constitution of 1958; Polish acts; Finnish acts; Austrian B-VG and DSG; Brazilian acts ("art. 1.022 do CPC"); Malta; Spain (including "art. 1.902 CC" and lists of articles); Romania; Moldova; Mexico; Australia's Corporations Regulations. Decisions: US reporter citations and docket numbers, Swiss BGE and dockets, German, French, Polish, Finnish, Austrian and Brazilian dockets, and ECLI for the countries whose case law the tree holds.
- **Limits:** Up to 50,000 characters and 100 provisions. Citations to acts outside the registry are not found and not reported as misses.

### check_precedent (`mcp.check_precedent`)

*Has the text this court applied changed since?*

- **Does:** Compares a provision's words on the day a court decided with a later date (today by default), and lists the laws that changed it. Also lists the judgments the record holds for that provision.
- **Arguments:** `path`, `decided`, `date`
- **Limits:** Judgments come from the overlay each case-law corpus keeps (`judgments/<law corpus>/<provision>.jsonl`, the decisions that cite a provision), for the case law your clone serves, plus the hand-checked sample in this tree's `judgments/`. The comparison works for any provision given a date. It compares words only.

### applies_to_case (`mcp.applies_to_case`)

*Which text governs a case commenced on a date?*

- **Does:** For a case commenced on one date, which later changes reach it, from any scope the record holds (Applies: data, or scope stated in words such as "cases commenced on or after"), and the text that applies.
- **Arguments:** `path`, `commenced`, `date`
- **Limits:** Structured scope only where the record holds it; a default rule in 71 corpora; a US fallback. It never decides the question.

### what_else_changes (`mcp.what_else_changes`)

*What relies on this provision?*

- **Does:** Provisions that cite this one, and provisions that use a term it defines (for example "debtor in possession"), with the definition's scope ("In this subchapter"), on a date.
- **Arguments:** `path`, `date`, `max_results`
- **Limits:** Within the same act or folder only. English definition forms only; one-word terms skipped.

## AI assistant prompts and resources

### Prompts (`mcp.prompts`)

*Ready-made research questions an assistant offers its user.*

- **Includes:** `provision_on_a_date` (a provision as in force on a date, who wrote it, what changed since and what relies on it), `case_timeline` (which text governs a case commenced on a date, period by period), `what_changed` (what changed between two dates).
- **Call:** MCP `prompts/list` and `prompts/get`

### Resources (`mcp.resources`)

*The tree's own documents, readable by an assistant.*

- **Includes:** `global-law://README.md` (how the tree is arranged and read), `REPRODUCE.md` (how it was built), `CHANGELOG.md` (what has changed and what is open), `manifest.json` (every corpus and its coverage).
- **Call:** MCP `resources/list` and `resources/read`

## Countries and coming changes

### countries.py (`countries`)

*Which countries does my copy hold and serve?*

- **Call:** `countries.py` (list), `add <names>`, `add --no-files <names>`, `only <names>`, `only --all`
- **Does:** Every jurisdiction: checked out, served, or neither. `add` downloads only the countries named; `--no-files` fetches the history without writing the files, which is all the tools need. `only` limits what the assistant server serves. Names can be a country folder, an ISO code, a level or a corpus path.
- **Limits:** The whole tree is several GB; one country is usually a few hundred MB or less.

### Future branches (`future`)

*Is anything already enacted that will change it?*

- **Does:** Where a corpus keeps a future branch, law.py and read_law read enacted changes that take effect later, beside the main history. `data/future-pins.tsv` (written by `tools/future_pins.py`) lists the branch tip for each.
- **Example:** Swiss BV Art. 127 para. 2bis (AS 2026 212) in force 2029-01-01; Czech 199/2026 Sb.
- **Limits:** 92 rows. Future branches are not fetched by default, and several lag their main branch.

## Chart pages: visualisations/

Self-contained pages built from the record. They load fonts and d3 from the web.

### Law in Motion (`viz.law-in-motion`)

*How the world's law grows and waits.*

- **Shows:** Two tabs: the Basic Law's growth, how long each jurisdiction waits between adoption and entry into force, constitutional change rates, global coverage, each with the research it builds on. `the-shape-of-waiting.png` is a still of one chart, shown in the README.

### Law, Drawn (`viz.law-drawn`)

*Calendars and growth of law-making.*

- **Shows:** Ten charts: Spain's legal calendar and paired amendments, each country's busiest year, Spain's executive-made statute book, the French Code civil, the tree's growth, the world's histories, federations' regional calendars, Russia's December wave, towns that copy their laws.

### The Life of a Provision (`viz.life-of-a-provision`)

*How single provisions are amended and survive.*

- **Shows:** Five charts: amendment and survival of provisions, the EU law each country cites, each country's biggest day in law.

## Readers and setup

### /watch readers (`readers`)

*Read and replay the law in a browser.*

- **Includes:** /watch/us-code, /watch/uk-law, /watch/swiss-law, /watch/grundgesetz and /watch/global-law on the Lexifina site (saas-webpage/app/watch). Text on a date, who wrote it and the change list per provision; the US reader steps through an amending law's instructions one by one.
- **Limits:** Part of the Lexifina site, not the global-law repository. Each covers its own corpora.

### Assistant setup (`setup.mcp`)

*How an assistant connects to a clone.*

- **Includes:** `.mcp.json` plus `.claude/settings.json`, `.codex/config.toml`, `.cursor/mcp.json` and `.vscode/mcp.json`, all starting `tools/mcp.sh`; opening the clone in one of those assistants offers the server.
- **Limits:** Needs a local clone with at least one country added.

---

Read from lexifina/global-law main 0afbd18 (6 November 2026): tools/law.py, tools/mcp_server.py (TOOLS, PROMPTS, resources, limits), tools/countries.py, tools/future_pins.py, data/future-pins.tsv, visualisations/README.md, MCP.md, and the saas-webpage /watch routes. Built 6 November 2026.
