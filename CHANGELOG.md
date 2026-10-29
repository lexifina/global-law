# Changelog and improvement log

What has changed in how the corpora in this tree are collected, stored and checked, what testing found, and where each finding stands. The newest entries are first. Each entry names the corpus it concerns: the US (`united-states/federal/usc`), Germany (`germany/bund/acts`, the Grundgesetz until 28 October 2026), the UK (`united-kingdom/uk/legislation`, earlier `gb/uk/send`), Switzerland (`switzerland/bund/acts`, the whole SR since 28 October 2026), another named country, or all.

Status words:
- **Fixed:** done in the corpus build or here.
- **Adopted:** a rule every corpus now follows.
- **Open:** found and reported, not yet fixed.
- **Checked:** a test that passed.

## 28 October 2026

- **Open (Armenia).** A letters-and-digits check against ARLIS's raw pages found that capitalised article headings ("ՀՈԴՎԱԾ 58.") were not recognised, so runs of articles were folded into a neighbouring file, and in one law duplicated (0.014% missing and 0.019% extra text over 500 sampled texts). The corpus is being rebuilt; this tree pins the old head until the next build.
- **Fixed (Germany, Switzerland).** Both corpora were rebuilt in full and force-pushed: Germany to every federal act (6f3913a, at `germany/bund/acts`, the Grundgesetz in `grundgesetz/` inside it), and Switzerland to the whole SR (06696ea, at `switzerland/bund/acts`, one folder per SR number). The builder accepts a rewrite only at the exact head announced for it (`REWRITES_AGREED`), and checks every other corpus as append-only. Old paths such as `de/bund/grundgesetz/artikel/001.md` still resolve in the MCP server.
- **Fixed (all).** For a corpus without a corpus.json, the preflight check now reads the in-force trailer named by the builder, so Germany's `In-Kraft` dates are no longer reported missing.
- **Adopted (all).** `history: current-only` in corpus.json marks a record that holds only today's text (Fiji). `law.py` then warns on earlier dates that each law shows as last updated, not as it was in force then.
- **Fixed (Germany).** In the first full federal build, 3,118 commit authors were named `index.md`, because a file loop reused the author variable. The rebuild fixed it, now at 6f3913a35, and every corpus is now tested for author names that look like file names or paths.
- **Adopted (all).** A history larger than about 150 MB can fail to push to GitHub in one go (HTTP/2 CANCEL, curl 18). Push ancestors in steps to a temporary branch, then `push --force --mirror`.
- **Fixed (France).** LEGI links name the text that made an article version as a verb link with `sens="cible"` or a noun link with `sens="source"`. Reading a `sens="source"` verb link that way credits the wrong law.
- **Adopted (large dumps).** One process reading a gzip tar is the bottleneck (about 25,000 files a minute while the parse pool sits idle). Read the many small daily archives one per process.

- **Fixed (UK). Appending instead of rebuilding.** `gitwrite.py --append` streams only the days after the last day written onto the existing `main`, starting from `from refs/heads/main^0`.
  - The writer's state (the last version written per document, temporary-change tracking, the pre-1970 counter and the last day written) is kept in the store's `writer` table.
  - A new version dated on or before the last day written would change published commits, so the append refuses and asks for a full rebuild.
  - **Checked:** appending the later days to a history built from a cut-off store gives the same head commit hash as a full build.
- **Checked (UK). Welsh-language text cannot enter the English history.** legislation.gov.uk's default address serves English (`dc:language` en, no Welsh words in the text), and the Welsh is only at `/welsh`, which the harvest never requests. As a guard, every version read is refused unless its `dc:language` is `en`: the Welsh version of 2018 anaw 2 is refused, the English accepted. There is one version per document per date, by key.
- **Fixed (UK). Whole documents are preferred.** The harvest chooses by estimated time, so whole documents are now preferred over provision-by-provision reading. For the Children and Families Act 2014 that is 38 requests and 50 s against about 1,100 requests, and whole documents are the publisher's exact text. That brings the full harvest down from over a week to about two days at six requests a second.

- **Fixed (UK). Modifications not in the register are recorded by hand.** These are changes that leave the words alone and were made by notice rather than legislation. The s. 42 notices are the first: 1–31 May (signed 28 April), 1–30 June and 1–31 July 2020, under the Coronavirus Act 2020 s. 38 and Sch. 17 para. 5(6). They follow gitlaw-contracts' proposed shape:
  - Empty commits, authored by the Secretary of State for Education, with `Modifies: <provision> | modified | <from>..<to> | <effect> | set-by <authority>`, `Words-changed: no` and `Curated: yes`, plus the sources.
  - A closing commit on 1 August 2020 with `Modification-ended:`.
  - The source data is `tools/curated/modifications.json`, and `uklaw.py on` notes a modification in force on the date asked about.
  - Consecutive notices end once, after the last.
- **Fixed (UK). A version check that only looks at days with a commit hides mismatches.** A published version that changes nothing in a document has no commit of its own day. The check now compares it with the latest commit up to that day. That raised the UK test from 91 to 130 versions checked, and it found 2 real mismatches. Both were days when only a heading or the arrangement changed, which the writer did not commit. Those are now committed under legislation.gov.uk, and all 130 match. The check reads through one `git cat-file --batch`, following Germany's advice. **Every corpus should check every published version, not just the days it committed.**
- **Open (UK, in progress).** The UK corpus is being rebuilt to cover all UK legislation on legislation.gov.uk (about 200,000 documents: Acts of the UK, Scottish, Welsh and NI legislatures, older Acts, local Acts, and UK, Scottish, Welsh and NI statutory instruments). The layout is one file per document at its URI (`ukpga/2014/6.md`), written by `git fast-import`. The harvest is resumable and rate-limited. Until the rebuild is pushed, `gb/uk/send` stays pinned as it is.
- **Fixed (UK, in the rebuild).** First commits carry `Enacted:`, `Made:` or `Text-as-at:`, never `In-force:`. A temporary change that ends is credited to its instrument, with `Temporary-change-ended:`. A register entry that names no provision ("blanket amendment", "Act") can explain any provision of its document that changed that day. Subjects are cut to 72 characters. The README gives `--before="YYYY-MM-DDT23:59:59Z"` and points to `tools/uklaw.py on <date> <doc> [provision]`, which picks the version by trailer.
- **Checked (UK).** The writer's `--verify` check: at the end of each day, every changed document equals the publisher's version for that day. On a five-document test (108 commits), 101 of 101 versions were identical.
- **Fixed (UK).** Large documents are built provision by provision and then compared with legislation.gov.uk's own whole-document text for every dated version. For the Children and Families Act 2014, all 34 versions match in words and structure. Three faults were found and fixed: a provision before its first dated version takes its earliest revised text; a provision inserted later is absent before then; a provision published only as prospective reads as now. One kind of difference remains: whether a provision is marked as not yet in force before its first dated version (s. 130, 9 of 34 versions). The two provision-level files give no reliable way to tell those cases apart, so the rate will be measured on a sample and reported in REPRODUCE.md.
- **Adopted (UK).** From the US finding: a listed version that does not load is recorded in the document's metadata (`missing_versions`), never silently replaced by another version.
- **Fixed (UK, partly).** Savings and transitional provisions now use the grouped scope shape. The harvest keeps each register entry's `Savings` and `CommencementAuthority` references (87 and 94 of the Children and Families Act 2014's 674 entries). Each commit carries `Applies: <provision> | subset: as a saving or transitional provision allows | set-by <saving's URL>` and `Commenced-by: <URL>`. **Still open:** the conditions themselves (dates, classes of case) are in the words of the saving provisions and are not yet parsed into `commenced_before` / `pending_on` kinds.
- **Adopted (UK).** The README tells clones to run `git fetch --force --tags origin && git reset --hard origin/main` after a rebuild, from gitlaw-contracts' tag finding.

### Germany (de/bund/grundgesetz; federal law to follow)

- **Fixed (Germany).** Rebuilt and force-pushed at `5bb57fa`. The source is now DocPatch's own repository (c3e/grundgesetz-dev) instead of its 2018 generated snapshot. The snapshot lacked Arts. 104c and 143e–g, created by the 62nd amending law, and the 63rd amending law.
- **Fixed (Germany).** DocPatch's text was compared with the official consolidated text (Gesetze im Internet) at the same point, the 63rd amending law in 2019. 43 articles differed. Examples:
  - Art. 3(3) lacks the 1994 disability sentence.
  - Art. 76 has "drei Monaten" where the official text has "sechs Wochen".
  - Art. 104a keeps a sentence the 2006 reform deleted.
  - Art. 143c lacks its paragraph 4.
  - Art. 120 has 1969 for 1965.

  For each, the official text replaces DocPatch's from the article's last change on. Every case is listed in KORREKTUREN.md.
- **Fixed (Germany).** The 64th to 69th amending laws come from the official text in QuantLaw's daily archive, article by article, with dates from the Bundestag's Datenhandbuch (ch. 13.2) checked against the laws. The final text matches today's official Grundgesetz in all 206 articles.
- **Fixed (Germany).** The expiry of Art. 143h on 31 December 2020 (Art. 2 Satz 2 of the 65th amending law, BGBl. I 2020 S. 2048) is a commit of its own. The Datenhandbuch's "31.12.2021" is an error. Gesetze im Internet's later fix of its own text (Art. 87a, 14 September 2022: "für die Bundeswehr" restored) is folded back into the version of the law that wrote it, with a correction note.
- **Fixed (Germany).** Trailer keys are ASCII (`Verkuendet:`). The `ü` had made git reject every trailer (reported by gitlaw-contracts). Subjects are now 72 characters or fewer.
- **Adopted (Germany).**
  - REPRODUCE.md is generated by the builder.
  - `--docs-date` is required.
  - The builder refuses a non-empty foreign target and keeps `origin`.
  - Two builds gave an identical HEAD.
- **Checked (Germany).** `tools/stand_am.py` answers correctly for 8 articles at 9 dates: Art. 23 is absent on 3 October 1990 and back in 1993; Art. 143h is absent in 2021 and present in 2025.
- **Open (Germany).** Versions older than each article's last change before 2019 are DocPatch's transcription, not checked against the Bundesgesetzblatt.
- **Open (Germany, in progress).** All German federal law, about 6,600 acts, from QuantLaw's archive of Gesetze im Internet. History starts at its first real scrape, 10 June 2019 (the 2018 "init" commit is empty). The history is written with `git fast-import`. Each change is credited to the amending law in the act's "Stand" note, and a change with no new Stand note gets its own label.

### US (us/federal/usc)

- **Open (US).** Building the whole Code, titles 1 to 54 (53 is reserved; the appendices are left out), with every fix below. It runs as two resumable workers, and the repository will be rebuilt, force-pushed and repinned here when they finish.
- **Fixed (US, lands with the full-Code rebuild).** A file's indentation now follows each provision's designation ("(1)(B)(i)" is three deep), not the printed level. GovInfo's 2020 and 2021 editions print 11 U.S.C. §1182(1) one level shallower than 2019 and 2022, so line blame credited the re-indent instead of the law (reported by lexifina-49).
- **Fixed (US, lands with the full-Code rebuild).** An amendment carried over from an earlier edition window (one that edition did not show) is now kept only if it brings the replay closer to the newer edition. Before this, Pub. L. 115-141's 2018 amendment of 2 U.S.C. §160 was re-applied in the 2021–22 window to the wrong paragraph; the edition check missed it because that paragraph differed anyway. It affected 72 of 4,957 law-and-section pairs.
- **Checked (US).** 503 changes are in force before their law was enacted. Every one is a retroactive date written in the law's own note ("shall take effect as of December 2, 2002"; fiscal-year starts), not a parsing error.
- **Adopted (US).** Cause proposals for unexplained changes run 8 at a time and are reused from the last build when the texts and candidate laws are unchanged. Title 42 had sat for 30 minutes making one model call at a time.
- **Fixed (US regulations).** The CFR builder dropped text sitting in the same block as a table (table titles, notes) and printed a nested table's rows twice. It now walks each table's own rows only and keeps the surrounding text in reading order (from the Spain build's word-for-word check).
- **Open (US states).** Sources checked for all 50 states, DC and Puerto Rico (scripts/us-law-sources/states-*.md). Builds have started for DC (from the DC Council's GitHub XML; its website disallows ClaudeBot), Missouri, Minnesota, Florida, California (bulk zips only; leginfo is `Disallow: /`), New Jersey, Montana, Iowa and Connecticut. Repos will be `lexifina/united-states-<state>-law`, corpus `us/<state-name>/statutes`. Blocked or needing permission: Ohio's Revised Code and Oklahoma (robots.txt), and Mississippi, Georgia and Arkansas (Lexis-only codes). Several state hosts refuse non-US connections; those are left until they can be read from a US host.
- **Fixed (US).** The §104 dollar-adjustment parser filed every older Federal Register notice under the newest (87 F.R. 6625). Each entry now stops at the next "By notice dated", so the 2019 notice, 84 F.R. 3488 effective 1 April 2019, is its own entry. Adjusted amounts stay out of the text, because the Code prints the enacted amounts.
- **Fixed (US).** When the newest release point is listed before its files are published (119-136, whose files returned 404), the build silently dropped it and the release point before it, so titles ended at an older version. It now falls back to the newest release point that loads.
- **Fixed (US, also in the reader).** A printed version can hold a change waiting on a condition, a live change and a sunset of the first. The text on a date was replayed only up to the first change not in force, which also threw away the live change after it (11 U.S.C. §1325 in 2022). Every step is now replayed, with the step that inserted and the step that removed each line tracked, and the lines whose changes are in force are shown. All tags now match the printed text except where a change was printed before it took effect (edition-2019).
- **Fixed (US).** A section that leaves the Code keeps a file saying so, credited to the law that repealed it, instead of disappearing (3 U.S.C. §2 and §14).
- **Fixed (US).** Markdown formatting characters in the text are escaped, so "the symbol \*M\*" in 17 U.S.C. §909 no longer renders in italics.
- **Adopted (US).** `tools/uscode.py` (`on`, `diff`, `log`, `commit`) reads the history by In-force trailer, so date queries don't depend on time zone or time of day. It also handles dates before the history starts.
- **Adopted (US).** `Applies:` trailers, one line per group of cases with every condition and the provision that set it, for example `Applies: 11 U.S.C. §1182(1) | commenced-on-or-after 2020-03-27; commenced-before 2022-06-21; pending-on 2022-06-21 | set-by Pub. L. 117-151, §2(h)(2)`.
- **Adopted (US).** The generator works one section at a time with a content store on disk, refuses a target folder that is neither empty nor an earlier build, and puts the data in a release archive when it is too large to commit. The checker reads through `git cat-file --batch` and checks the nine titles in 23 seconds.

### Switzerland (lexifina/swiss-law)

- **Fixed (Switzerland).** On-date reads on the future-changes branch `kuenftig` returned future text for days between the build and the change, because the merge of `main` into `kuenftig` is dated the build day but already holds the later changes. `tools/stand_am.py` and `tools/check_repo.py` now use `git log --no-merges`.
- **Checked (Switzerland).** Every article version is read back from git on the day it took effect, and the version before it on the day before, then compared with the reader's data. With three acts: 767 checks, 0 mismatches. A second build from the same data gave identical hashes for `main` and `kuenftig`.
- **Fixed (Switzerland).** Publisher typesetting no longer counts as a change: "..." against "…", a literal "[tab]", and old `<sup>1)</sup>` footnote markers. Before the fix, these produced 28 false changes, some credited to whichever act took effect that day.
- **Fixed (Switzerland).** A change is dated by its own entry into force, from the footnote on that article or Fedlex's impact record for that article, not by the consolidated version where it first appears. For acts with structured text for only some versions, the two can be a year or more apart: SchKG Art. 6 is in force from 1 January 2020 and first appears in the version of 20 October 2020.
- **Adopted (Switzerland).** Where the wording changed but no impact record or footnote names an act, the change is labelled a correction by the publisher, committed by `Bundeskanzlei (Fedlex)` and never credited to a law.
- **Adopted (Switzerland).** The first structured version of each act has a `Consolidated:` trailer, not `In-force:`, because nothing came into force that day. Commit subjects longer than 72 characters become "N Artikel".
- **Fixed (Switzerland).** Fedlex SPARQL limits:
  - A filter on an impact's target address scans every impact, and the firewall answers HTTP 400. Impacts are read through `jolux:legalResourceSubdivisionIsPartOf`.
  - A single query over every consolidated version answers HTTP 500, so versions are read a year at a time.
- **Open (Switzerland).** Moving from three acts to the whole Classified Compilation: about 5,900 acts and treaties with German Akoma Ntoso versions, 12,182 versions in all. The repository will use one folder per SR number and git fast-import, with a tag for each amending act only.
- **Open (Switzerland).** Transitional rules (Übergangsbestimmungen) are not modelled. They will come from the amending acts' Official Compilation texts in Akoma Ntoso, stored as scope groups.

### Applicability: who a change applies to

- **Adopted (all).** Applicability is stored as groups of conditions, not as one date.
  - Each change has `in_force`; `applies_from` when application starts later than entry into force (the EU's EV and MA dates, such as the GDPR's 24 May 2016 and 25 May 2018); and `scope`, a list of groups.
  - Each group is `{conditions: [{kind, date}], words, set_by}`. Kinds are `commenced_on_or_after`, `commenced_before`, `pending_on` and `subset` (a described class of cases).
  - A case is covered if it meets every condition in at least one group: groups are alternatives (OR), conditions within a group all apply (AND).
  - Corpora write one trailer per group: `Applies: <provision> | <condition>; <condition> | set-by <provision>`.
  - "Shall not apply to cases commenced before D" is stored as `commenced_on_or_after D`.
  - Why groups: Pub. L. 117-151 §2(h)(2) reaches (a) cases commenced on or after 27 March 2020, or (b) cases commenced between that day and 20 June 2022 that were still pending on 21 June 2022. A flat list would make "pending" a condition on every case.
  - The shape follows Akoma Ntoso's `scopeMod` and `efficacyMod`. No official source surveyed publishes such conditions as data: the EU types its dates only, LegalDocML.de marks validity periods, and Fedlex JOLux gives an entry-into-force date and status.
- **Fixed (US).** 16 changes from 3 laws had a condition in the effective-date note that the structured data dropped:
  - Pub. L. 117-151 §2(h)(2), "pending on June 21, 2022".
  - Pub. L. 118-42 §544(b)(2): the §507(d) change does not apply to cases commenced before 9 March 2024. It is now `commenced_on_or_after 2024-03-09`.
  - Pub. L. 116-136.
- **Fixed (US).** Effective-date notes were attached to every change a law made in a section, even when the note concerns a different provision.
  - The CARES Act note "shall apply to any case commenced before, on, or after the date of enactment" (§1113(b)(1)(D)(i), for §101(10A)) sat on the §101(51D)(B)(iii) change made by §1113(a)(4). That would have made the 51D change retroactive.
  - Notes now reach only the changes they name. **All corpora:** key effective-date and commencement rules to the provision they name, not the section or the Act.
- **Open (Switzerland).** Transitional rules (Übergangsbestimmungen) are not modelled yet. They will come from the amending acts' Official Compilation texts in Akoma Ntoso, in the shape above.
- **Open (UK).** Commencement savings and transitional provisions should be checked against the same shape.

### Same words, different law

- **Fixed (UK).** The s. 42 "reasonable endeavours" notices are now three empty commits, for May, June and July 2020, each authored "Secretary of State for Education" with `In-force:`, `Modifies:`, `Words-changed: no` and `Curated: yes`. The authority is the Coronavirus Act 2020 s. 38 and Sch. 17 para. 5(6), a power in force from 25 March 2020 until it expired early on 9 December 2021 (S.I. 2021/1399). A closing commit on 1 August 2020 carries `Modification-ended:` and `Modifies: … | ended | …`. The data, with sources, is in `tools/curated/modifications.json`, and `uklaw.py on 2020-06-15 …` notes the modification.
- **Fixed (US, lands with the full-Code rebuild).** Each §104 notice is an empty commit on its effective date, authored "Judicial Conference of the United States", with `Words-changed: no` and one `Modifies: … | amount-adjusted | …` line per provision (several amounts joined by "; "). Files keep the printed amounts; `tools/uscode.py on DATE PATH` prints the applicable amounts on stderr. The rebuild also carries the adjustment parser fix, so each notice gets its own clauses (2019: 84 F.R. 3488). Each range closes the day before the next notice for the same provision (for example 2022-04-01..2025-03-31 under 87 F.R. 6625, then 2025-04-01.. under 90 F.R. 8941); only the newest stays open. For corpora that only append, the latest effect per provision and kind wins.
- **Proposed (all; gitlaw-global to settle).** A `Modifies:` trailer for law that changes while its words stay the same, one line per effect: `Modifies: <provision> | <modified|disapplied|amount-adjusted|applied-with-modifications> | <from>..<until|open> | <effect in words> | set-by <source>`. It goes on an empty commit on the start date, with `Words-changed: no`; an open-ended effect gets a closing empty commit when it ends. The UK implementation adds an `ended` kind for closing commits and a `Curated: yes` trailer for effects entered by hand from cited sources. Reach-backs use the existing `Applies:` groups. Empty commits do not appear in `git log -- <path>`, so tools index the trailer instead (`git log --grep`). For the MCP server's read_law: on a date, list every `Modifies:` effect that covers it and every later change whose `Applies:` groups reach back over it.

- **Open (all).** The text in force is not always the whole law, so a reader keyed to text versions alone gives the wrong answer in these cases:
  - **UK.** The s. 42 duty was reduced to "reasonable endeavours" by notices from the Secretary of State for May to July 2020, while its words stayed the same.
  - **US.** The 2022 reach-back changes the answer for cases filed in the 2022 gap, without any change to the text in force on those days.
  - **US.** The §104 notices change dollar amounts that the Code prints at their base value.
  - Readers should warn when a power to modify, or a later reach-back, covers the date asked about.
- **Fixed (US), see the US section above.** The §104 dollar adjustments were recorded but misfiled. The note parser runs one Federal Register entry into the next, so every older notice is filed under 87 F.R. 6625 (effective 1 April 2022).
  - In §101(51D) that covers 2019, 2016, 2013, 2010 and 2007; §109(e) has nine notices filed this way.
  - The 2019 notice is 84 F.R. 3488, effective 1 April 2019.
  - The US git repo leaves adjusted amounts out of its text for this reason.

### Dates and commands

- **Adopted (all).** README date commands must not depend on the reader's clock or time zone. `git rev-list --before=YYYY-MM-DD` uses the current time of day, and commits are dated noon, so the answer for the day a law took effect flips at noon. Use `--before="YYYY-MM-DDT23:59:59Z"` or an explicit offset, or a tool that picks the version by its `In-force` trailer. Fixed in Germany (b0d346e).
- **Open (UK).** The README still has `--before="D 23:59"` (local time) and bare dates.
- **Adopted (all).** Give a PowerShell form wherever a command uses `$(…)`, because PowerShell splits `git show $(…):path` into two arguments.
- **Adopted (all).** A tag named after a printed edition holds the text in force on that date, not the printed text. They differ wherever a change was printed before it took effect (28 sections in the US 2019 edition), so say so or tag both.
- **Adopted (all).** A retroactive in-force date puts a commit before its law existed (6 US changes). Keep the in-force date, show the enacted date, and explain it.
- **Adopted (Switzerland).** A branch of changes not yet in force must never be merged back into `main`. The merge commit, dated the build day, carried future text into every on-date answer. On-date tools use `--no-merges`.

### Building and pinning

- **Adopted (all).** Build and pin from the published repositories, never from a local checkout. A local build pinned an unpushed commit, and fresh clones broke.
- **Adopted (all).** The documentation commit is dated by the data's build or retrieval day, given as a required argument, so a rebuild on another day keeps the same hashes.
- **Adopted (all).** Builders refuse a non-empty target that is not an earlier build (a UK build into an existing folder doubled its history), and keep `origin` across rebuilds.
- **Adopted (all).** REPRODUCE.md is generated by each builder, with pins, counts and blob hashes filled in. US, Germany, Switzerland and this tree came out identical hash for hash on rebuild.
- **Fixed (here).** The UK pin was one commit behind `gb/uk/send` (e295f40 against 9ed31ef, documentation only). It was repinned in a150ef0.
- **Open (here).** Switzerland is not yet in the tree. Decide how first: the full SR build is about 5,900 acts, so consider a shallow submodule or a separate corpus path. Its first versions carry `Consolidated:`, which the builder must read as their date.

### This tree (global-law): deep test of real use

A fresh clone was used the way a reader would, with plain git and with `tools/law.py`, and checked against the official texts.

- **Fixed (here).** `law.py` compared dates as text, so `2022-5-1` read as December 2022, and `2022-13-45` and `yesterday` gave answers instead of errors. Dates are now checked; `today` and a time after the date are accepted.
- **Fixed (here).** A date past the end of a record gave stale text without a word: the Grundgesetz "today" was the 2017 text. Each corpus now has `record_to` and `record_note` in `manifest.json`, and every command prints a note on stderr when a date is before a record starts or after it ends.
- **Fixed (here).** "Not in force or outside the record" covered four different cases. Now each gets its own answer:
  - a mistyped path, with the closest names suggested
  - a date before the record
  - a provision not yet in force, with its first date
  - a provision repealed
- **Fixed (here).** Paths written `./us/…` or with Windows backslashes were refused.
- **Fixed (here).** `diff` from a date before a record started said "No change". It now shows the whole text arriving.
- **Fixed (here).** A reversed window for `laws` printed nothing, and a missing argument gave a traceback.
- **Fixed (here).** `law.py words` (word-level authorship, new today) took 16 s on 17 U.S.C. §115, which the Music Modernization Act rewrote whole. Unchanged lines are now matched first, and large rewrites are paired line to line, so it takes 1.3 s.
- **Fixed (here).** The tests imported the UK builder and left `__pycache__` inside the UK checkout, which then blocked `git checkout` of an older state. Tests no longer write bytecode, and the tree has a `.gitignore`.
- **Fixed (site).** Changes too close together on the /watch/global-law timeline could not be clicked apart. They now share one mark that steps through them.
- **Open (here).** Time travel with plain git is fragile:
  - `git checkout <old commit>` with `git submodule update` (or `--recurse-submodules`) leaves the folders of corpora not yet in the record, with today's files in them.
  - `tools/` disappears, because it is only in the last commit.
  - Switching back can fail.

  For now use `law.py`, or `git worktree add ../then <commit>` and `git submodule update --init` in that worktree. Possible fixes: carry the tools from the first commit, or pin each corpus from the first commit at an empty "before the record" commit.
- **Open (here).** Plain git cannot take dates before 1970. `git log --before=1960-01-01` silently returns the newest commit. The tools use the `In-force` trailer, and the README now warns plain-git users.
- **Open (here).** `git blame` and `git log -- <provision>` do not cross into a submodule from the root. Use `law.py`, or run git inside the corpus folder at its pinned commit.
- **Open (here).** The top of `git log --first-parent` shows each corpus's documentation commits ("Lexifina"), not laws. Consider keeping documentation commits out of the chronology.
- **Fixed (Germany, repinned here in 1b11b21).** The records barely overlapped: the Grundgesetz ended in 2017, and the US starts in 2018. The Grundgesetz is now rebuilt to 28 October 2026 and equals the official text, so today, at 1b11b21, all three records are current from 12 January 2018. Art. 104c (2017) is now there, and Art. 143h reads correctly: in force 8 Oct to 31 Dec 2020, then again from 25 Mar 2025. An earlier note here called it "inserted 2019", which was wrong.
- **Fixed (here).** The README now warns about plain-git time travel and dates before 1970, and says to use a worktree.
- **Fixed (here).** A provision that lapsed and came back was reported as "repealed or removed". The message now gives the day it was removed and the day it is in force again, for example Art. 143h on 2023-01-01.
- **Fixed (here).** The Grundgesetz reader test fetched tags only when there were none, so an older clone kept the tags from before Germany's force-push and compared against old text. It now force-fetches the corpus's tags (`git fetch --force --tags`). Clone users should do the same after any corpus is rebuilt; see the README.
- **Adopted (here).** A test fails if any pin is not on its corpus's published main, which catches a corpus force-push before a fresh clone breaks. A test checks that git's own trailer parser reads every in-force date. Germany passes since its ASCII-key rebuild.
- **Open (US).** Quotation marks are straight (`"debtor"`), where the official text has curly quotes. The words match.
- **Open (here).** Scale: one root commit per corpus commit, and full submodule clones. The all-UK (about 200,000 documents) and full-SR builds will need one root commit per corpus per day, and shallow or partial submodules.
- **Open (here).** No reading "as applied to a case filed on a date" yet. It waits on the US `Applies:` trailers.
- **Checked (here).**
  - A fresh clone with submodules is 4.5 MB and takes seconds. Every command answers in 0.2 to 0.6 s.
  - `git grep --recurse-submodules <term> <commit>` searches all the law in force at a world commit, across countries.
  - `git diff --submodule=diff <commit> <commit>` shows every change in every country between two dates.
  - 11 U.S.C. §1182(1) and §101(51D) today match the published Code word for word.

### Trailers

- **Fixed (Germany, 5bb57fa).** Git read no trailers on any of the 66 commits, because the key `Verkündet:` contains a non-ASCII letter and git then rejects the whole trailer block. The key is now `Verkuendet:`. `git interpret-trailers --parse` reads 72 of 73 commits, the exception being the documentation commit, and `%(trailers:key=In-Kraft)` works.
- **Fixed (here, 1b11b21).** The Germany rebuild was force-pushed, so the pin b0d346e was no longer in the corpus's history. Repinned to 5bb57fa; the UK is repinned to 9ed31ef. Every pin now matches its corpus's head. Repin to 5bb57fa before GitHub garbage-collects the old commit and fresh `git submodule update --init` fails. Test proposed: each pin must be an ancestor of its corpus's published `main`.
- **Adopted (all).** Trailer keys are ASCII letters, digits and hyphens only. Every corpus commit except the baseline and documentation commits must pass `git interpret-trailers --parse` with its date trailer present. Commits git can parse today: Switzerland 22/23, UK 11/15, US 43/45, Germany 0/66.
- **Adopted (US).** All trailer keys are ASCII, including `Applies:`. The 2017-edition baseline commit carries `Consolidated: 2018-01-12` and `Printed-in: 2017` and no `In-force:`. Both are in the US generator and land with the full-Code rebuild, which changes the US hashes, so this tree needs a repin.
- **Open (UK).** The first commit, the Royal Assent of the Children and Families Act 2014, carries `In-force: 2014-03-13`, although nothing came into force that day. Use `Enacted:` alone, or `Consolidated:` as Switzerland does.

### MCP server

- **Adopted (here).** `tools/mcp_server.py` is a Model Context Protocol server for the tree. It uses only the standard library and git, reads the repository and changes nothing; MCP.md has the setup. It offers 15 read-only tools:
  - finding things: `list_jurisdictions`, `find_provision`, `list_provisions`
  - reading the law: `read_law`, `world_on_date`, `who_wrote`, `compare_dates`
  - history: `provision_history`, `laws_between`, `changes_between`
  - search: `search_law`, `search_changes`, `phrase_history`
  - cases and records: `applies_to_case`, `law_details`

  Every answer carries the notes on where a record starts or ends. `read_law` and `provision_history` give each change's official sources to cite.
- **Checked (here).** `tests/test_mcp.py` (25 tests) speaks to the server as a client does: the handshake, every tool, errors, resources, and the applicability rules with the agreed `Applies:` format.
- **Checked (here).** Blind tests: a model given only the MCP tools answered 14 of 14 questions with known answers. Among them:
  - the law that wrote the $7.5 million in §1182(1)
  - the reach-back of Pub. L. 117-151 to a case filed in the 2022 gap
  - the amendment that wrote Art. 16a(1)
  - the change to reg. 13(3) in May 2020
  - which changes were temporary
  - and, correctly, that the record could not answer for Art. 143h at the time
- **Fixed (here), from the blind tests.**
  - `find_provision` falls back to the text when headings are only numbers (Grundgesetz "Artikel 16a"), so a topic such as "Asylrecht" finds Art. 16a.
  - `laws_between` counts the provisions each law changed.
  - `law_details` cuts long messages, with `max_message_chars` to raise the limit.
  - The server's instructions say coverage is partial and what each date means.
- **Fixed (here), from the third blind test.**
  - A plain search matches typographic dashes, quotes and spacing, so "COVID-19" finds the Code's "COVID–19". Plain queries are literal; regular expressions are opt-in.
  - `law_details` accepts a jurisdiction prefix such as `de`.
  - Where a change has no `Applies:` data, `applies_to_case` shows the scope the record states in words for that provision, for example Pub. L. 117-151's "Applies to any case that is commenced under title 11 on or after March 27, 2020".
- **Fixed (here), from the fourth blind test (adversarial questions).**
  - `applies_to_case` reads the common worded scopes in change notes ("commenced on or after March 27, 2020", "before, on, or after") as conditions, and says when it did. For 11 U.S.C. §1182(1) on 2022-07-01:
    - a case commenced on 2020-01-15 gets the text of 2020-02-19, since neither the CARES text nor Pub. L. 117-151's reaches it
    - a case commenced on 2022-05-01 gets the $7.5 million text
  - Answers no longer point to `law.py`, which a model using MCP cannot run; they name the matching tool.
  - Numeric arguments are checked, and 8-digit dates such as 20220101 are read.
- **Checked (here).** Fourth blind round, 6 of 6. The model declined to describe US privacy law the record does not hold. It found the debt brake in Arts. 109 and 115 although the word "Schuldenbremse" is not in the text. It traced Art. 143h through insertion (2020), expiry and a new Art. 143h (2025), and gave reg. 13's extent as England and Wales only.
- **Fixed (here), from the fifth blind test (a research memo).**
  - New tool `phrase_history`: when words came into the law and when they left it, at any date. For example, "COVID" entered the Grundgesetz on 2020-10-08 (Art. 143h, 65th amendment) and left on 2020-12-31. The $7,500,000 in §1182(1) was added and removed twice.
  - A search with no hits in the text now looks in the change notes and says what it found.
- **Checked (here).** Fifth blind round: a 350-word memo on subchapter V eligibility from 2019 to today, with five dated changes, laws and govinfo links, and the definition for a case commenced on 2021-06-01. All correct.
- **Fixed (here).** Popular names: `aliases.json` maps names the text never uses to provisions, each with a note:
  - Schuldenbremse → Arts. 109, 115, 143d
  - Ewigkeitsklausel → Art. 79
  - subchapter V → §§1181 ff.
  - automatic stay → §362
  - EHC plan → s. 37 and reg. 13
  - and others

  `find_provision` checks them first, and an exact name ranks above heading matches. Add entries as they come up.
- **Adopted (here).** `read_law` says when the words in force are not the whole answer:
  - when a later change reaches back over the date. In the 2022 gap, Pub. L. 117-151 reaches cases commenced on or after 2020-03-27.
  - when a `Modifies:` effect (gitlaw-contracts' proposed trailer) covers the date. It takes the latest open effect per provision and kind, honours `ended`, and says when an effect was entered by hand (`Curated: yes`).
- **Adopted (here).** A project `.mcp.json` in the tree, so Claude Code offers the server in any clone.
- **Adopted (here), 2026-10-28.** Several additions to the MCP server:
  - It serves both MCP eras: the stateless revision 2026-07-28 (`server/discover`, `_meta` versions, error -32022, `resultType`, cache hints) and the legacy `initialize` versions.
  - New tools:
    - `what_else_changes`: citations, and multi-word defined terms, per file layout or from a corpus's declared `citation` rule.
    - `check_precedent`: whether the text a decision applied is still in force, the first step of the judgment overlay. It reads `judgments/<provision>.jsonl` when a corpus carries one.
  - Three prompts, and a resource template for a provision on a date.
- **Fixed (here), security review.**
  - Paths, commits, text and regular expressions are validated; regexes that could take exponential time are refused.
  - Git calls time out, lists are capped, and internal errors no longer echo details.
  - JSON-RPC batches follow the specification: an empty batch, or a member that is not a request, gets "Invalid Request".
  - A hostile-input test suite, and a 400-call fuzz run with no crash, internal error or leak.
- **Adopted (here), to match other law MCP servers.**
  - `read_law` with `include_text: false` is a cheap metadata check.
  - An opt-in audit log (`GLOBAL_LAW_AUDIT_DIR`): one line per call with a hash of the arguments, never the arguments.
  - Against legalize-mcp: the same questions plus reading by date, comparing dates, word-level authorship, every country on a date, case scope and precedent checks, with no token or network access.
- **Fixed (here), from the seventh blind test.**
  - `find_provision` reads citation forms: "11 U.S.C. § 1101" and "17 USC 107" narrow to the title. Abbreviations in `aliases.json` with a `scope` ("GG", "CFA", "SEND Regulations", "BV", "DSG", "SchKG") narrow to their Act.
  - A jurisdiction scope narrower than a corpus (`us/federal/usc/title-11`) no longer returns nothing.
  - `what_else_changes` lists a provision that defines the same term itself apart from those that rely on the definition. For "debtor in possession", 15 provisions rely on §1101 and §1182 defines it itself.
- **Adopted (here), case law.** `judgments/` holds the first judgment overlay: five judgments on the Children and Families Act 2014 s. 42, from 2020 to 2026. Each was found on Find Case Law and read individually to confirm it deals with s. 42. Only citation details are recorded, under the Open Justice Licence, which does not permit computational analysis without a licence. `check_precedent` reads it.
- **Fixed (here), found by that data.** `check_precedent` compares only the words of the law. The UK files' metadata header (extent, version, source) had made every pre-2021 decision on s. 42 look "worded differently". Changes that left the words alone are named as such, e.g. S.I. 2021/1399, "modified, words unchanged".
- **Adopted (here), from a comparison with 12 other law MCP servers.** `resolve_citations` reads every citation in a brief or judgment ("11 U.S.C. § 1182(1)", "Art. 16a Abs. 1 GG", "s. 42(2) of the Children and Families Act 2014", "reg. 13 SEND Regulations 2014", "Art. 10a BV"). It resolves each to its provision with its state on a date, and says plainly when a citation is outside the record.
- **Fixed (here), from the eighth blind test.** Each change now says what it did to the provision, in the record's own words: `what` on `provision_history`, `applies_to_case` and `read_law`. Examples: "11 U.S.C. §1182(1). Temporary change ended.", "reg. 13: temporarily amended", "Geändert: Art. 87a". Without it, a model took the 2022 and 2024 sunsets of §1182(1) for republications.
- **Fixed (here), scale.** `find_provision` no longer reads every file:
  - numbers match file names
  - words match heading lines through `git grep`
  - headings are read only for the best hits

  HEAD and the corpus pins are cached. A first search takes 0.3 s and later ones 0.04 s (was 1.2 s and 0.5 s), ready for the all-UK and full-Code corpora.
- **Checked (here).** Seventh blind round, 3 of 3:
  - 16 provisions rely on "debtor in possession"
  - a decision of 2023-03-15 on §1182(1) applied text changed since by Pub. L. 117-151 on 2024-06-21
  - a 1995 decision on Art. 16a applied words still in force
- **Fixed (here), found by tracing a blind run.** Claude Code gives the model a tool's `structuredContent`, not its text, when both are present. Explanations that existed only in the text, such as the period-by-period reading and the "not the whole answer" notes, never reached the model. It then compared a case's text with today's and wrongly concluded that a reach-back changed nothing. Every structured answer now leads with `summary`, the full explanation.
- **Adopted (here).** `applies_to_case` gives a case its own timeline: a bottom line, then each period with its text and the changes from the period before. It also looks ahead to later laws that reach back to the case, showing what they change. For a §1182 case commenced on 2022-05-01 there are three periods:
  - the gap text
  - the $7.5 million text from 2022-06-21, by Pub. L. 117-151's reach-back
  - the text after the 2024 sunset, whose reach to pending cases is not recorded
- **Checked (here).** Three blind rounds before that, 20 of 20 answers right. The model also said correctly where the record could not answer, for example that no official link is recorded for a Grundgesetz amendment, only its BGBl. citation.
- **Open (here).** `applies_to_case` reads `Applies:` trailers, but no corpus has them yet; the US full-Code rebuild adds them. Until then it says no scope is recorded and follows the general rule.
- **Checked (here), independent security review, 28 October 2026.** The review found no way to run code, write to the tree, read outside it or pass an option to git. It did find ways to stop or stall the server, each now fixed and tested:
  - Process exits:
    - bytes that are not UTF-8, JSON nested 100,000 deep, and an id over 4,300 digits now get a parse error;
    - a corpus that is not checked out (law.py's `SystemExit`) now narrows the answer and is named.
  - Hangs:
    - `phrase_history` re-ran a model's regex in Python's backtracking engine, and `(a|a)*`-style patterns got past the check. Git now does all the matching (`git grep -c` before and after each change), and the check refuses any repeated group holding a quantifier, an alternation or another group.
    - `resolve_citations` had a citation pattern quadratic in whitespace (206 s of CPU for a 50 KB brief) and looked up every citation before applying the limit. The pattern is now linear, and each provision is looked up once, up to 100.
  - Unbounded work: `search_changes` read every matching commit before applying its limit, and wildcard paths (`usc/*`) walked every commit. Each tool call now has 120 s of git in total, limits apply before the per-commit work, and wildcards are refused.
  - textconv: a filter that a checkout's attributes name and the user's git config defines ran during `compare_dates` and `phrase_history`. Git now runs with `--no-textconv --no-ext-diff`. Plain git ran a test filter 6 times; the server ran it 0 times.
  - Smaller fixes:
    - unknown arguments and non-string, non-integer ids are refused;
    - `read_law` on a folder says so;
    - `law_details` reads only commits in the pinned history;
    - the audit log's hash is keyed (HMAC), so short arguments cannot be recovered;
    - the instructions say that law text and notes are data.
- **Adopted (here).** Readable country folders. The server reads old ISO paths and scopes (`us/federal/usc/...`, `"de"`, `gb/uk/send/...`) through each corpus's `iso_path` and `code` in the manifest, and answers in the tree's current naming. Links, aliases.json and models that learned the old paths keep working.
- **Adopted (here).** Fixes from recorded Claude Code sessions using the server (real terminal captures, read against each session's transcript):
  - `who_wrote` credited the 2019 words of 11 U.S.C. §1182(1) to the CARES Act, because they came back when its temporary change ended. Words that already stood in an earlier version now go to the law that first wrote them, with `restored_by` and `restored_on`.
  - A model reading §1182 on 1 May 2022 guessed from the later laws that today's text differs; it does not. `read_law` now says whether the words are the same at the end of the record (`latest`: same, different or gone). It compares words, not layout, because the restored item is re-indented.
  - `applies_to_case` says when a later law's scope covers the case from the day it was commenced (Pub. L. 117-151 for a case filed in May 2022), and leaves to the amending law whether its text governs matters decided as of that day (`reaches_back_to_commencement`).
  - `what_else_changes` reports a definition's scope ("In this subchapter"). Where another provision defines the same term (§1101 for chapter 11), uses nearer that definition by section number are listed apart as probably governed by it. No corpus records chapter boundaries yet, so this is a labelled hint.
  - `phrase_history` marks words already in the record's first text (the 2017 edition of the US Code) as `present_at_start`, not "added": they entered the law before the record begins.
  - `law_details` returns `trailers_all`, every value of a repeated trailer (Malta's `Affecting:`, the UK's `Effect-id`).
  - The three Swiss acts move to the full SR under SR numbers (`ch/bund/swiss-law/bv` to `ch/bund/acts/101`, DSG to `235.1`, SchKG to `281.1`). Old paths, citations ("Art. 8 BV") and aliases resolve to the new folders once the old corpus is gone.
  - Second recording: the model asked `who_wrote` for lines, which still credited the CARES Act; restored lines now keep their first author too. The model also said a period that a reach-back law covers was shown as settled; such periods now carry `reached_back_over_by` and say they are not settled. Asked what relies on §1182's definitions, it ran text searches instead of `what_else_changes`; the tool's description now names that question.
  - Third and fourth recordings, the second against a fresh clone of lexifina/global-law main (12 corpora):
    - The model still did not pick `what_else_changes`: Claude Code shows a model only the names of MCP tools until it searches for them. The server's instructions now map questions to tools, and `search_law` for a section number points to `what_else_changes`.
    - `who_wrote` now gives the record's limits and whether the words still stand (`latest`); without them, the model filled the gap from memory.
    - Asked for Art. 8 BV on 1 January 2000, `read_law` said "not yet in force", and the citation check said Fedlex "last changed" it. The record's first version is the consolidated text of 2021, not an enactment. Before a baseline, the answer now says that is where the record starts, not the day the provision came into force. A baseline reads "First version in the record", and `resolve_citations` says "before the record starts for it". law.py's history now keeps the US baseline row as well; §101 had started at 2019.
  - Fifth recording, on Malta's whole statute book:
    - `changes_between` with a scope inside a corpus (`mt/national/malta-law/cap/586`) said nothing had changed. Scopes inside a corpus (a Chapter, a US title) now work in `changes_between`, `laws_between`, `search_changes` and `phrase_history`.
    - `phrase_history` read file names only, so L.N. 259 of 2025 renaming Annex II to the Third Schedule looked like an addition, and the annex never lost the words. Renames are now followed: lines that came along are `moved`, and the rest are added or removed.
    - Fourteen queued `read_law` calls on Malta passed Claude Code's 120-second tool limit, at 12 to 17 s a read. Each provision's history is now read once per HEAD, not two or three times a call. MCP.md suggests changed-path commit graphs, about three times faster for path-limited logs. Reads now take 1 to 3 s.
  - Sixth recording: asked to list the instruments made under Cap. 586 and when each changed, the model had no tool for it, and fell back to file globbing and shell git. `list_provisions` now takes the start of a folder name (`mt/national/malta-law/sl/586.`) or `by_folder`, and gives one row per act or instrument: its title (read from title.md where that has no heading), its number of files, and its last change or "first version in the record". It reads headings only for the folders that match.
  - Seventh recording: to see what L.N. 235 of 2026 did, the model made about 20 `compare_dates` calls, one provision at a time. It then judged the rest "likely a reprint" and missed real changes, such as the new extension of reg. 15's 40-day period. `law_details` now gives each changed provision's effect on its words: `words changed` (with a word diff), `layout only`, `text moved between provisions` (a consolidation re-split at new boundaries), `added` or `removed`. That covers up to 60 provisions in one call. The eighth recording showed that page furniture from print still read as changed words, and the model went back to comparing provisions one by one. Words are now compared without it: running heads ("[S.L.586.08", "CAP. 586]"), page numbers, a symbol font's private-use spaces (U+F020), hyphens inside words, and the same words in another order. For L.N. 235 that gives 3 changed (reg. 15, a footnote and the title), 13 moved and 23 layout only, where it had been 33 changed.
  - Ninth recording: L.N. 235 took one `law_details` call and 4 checks, where it had taken about 20 calls. Act XII of 2021 took one call. The model could not name Cap. 387: `find_provision "Cap. 387"` found s. 387 of Cap. 12. Malta's citation forms now resolve. "Cap. 387" and "S.L. 586.08" give the Act's title page and title ("Arbitration Act"). "Article 11 of Cap. 586" and "reg. 15 of S.L. 586.08" resolve in `find_provision` and `resolve_citations`. "Chapter 11" is left alone, because in a US question it is a chapter of title 11. `list_provisions` on one Act's folder now opens with the Act as a whole: its first version in the record and its last change.
  - A probe report from another session (git-smol-countries-3) gave five more fixes:
    - `applies_to_case` counted the US record's baseline (the 2017 edition) as a change after a 2004 commencement, and gave "the text in force on 2004-06-01", which the record does not hold. BAPCPA 2005 was invisible, and the answer read as complete. A baseline is no longer a change. A case commenced before the record starts gets a "Gap:" line and a first period marked not in the record.
    - Payloads: `applies_to_case` was 126 KB. Every structured answer carried the law's text twice: once in `summary`, because the answer ends with it, and once as `text`. The summary now stops before the text. Period texts come only with `include_period_texts`. `laws_between` gives 12-character commits.
    - `compare_dates` on a wrong path (`art-115.md` for `artikel/115.md`) said "no difference". It is now an error that suggests the right path.
    - `find_provision`: a heading line with all the words, or the phrase, outranks a line with one of them ("automatic stay" now finds §362 first). A file whose first heading is only structure ("PART III") shows the heading line that matched.
    - The Malta code found its corpus by a literal path. It now uses the manifest's country code, which survives the move to `malta/national/acts`.
    - Smaller: `law_details` accepts a commit of this tree (a root commit) and reads the corpus commit it moved to.
  - Retest and tenth recording:
    - `who_wrote` sent §362 three times over (80 KB). The runs list now comes only with `include_runs`, because the marked text carries the same attribution.
    - A file's heading score is its best heading line, not the sum of all of them, so §922 "Automatic stay of enforcement" now ranks second for "automatic stay".
    - A broad regex `search_law` across all 12 corpora was 70 KB, past Claude Code's limit for a tool result. It now lists at most 200 matching paths, with `provision_count`. Every structured answer is kept under 60,000 characters by halving its longest list and saying what was cut.
  - **Security (reported by git-smol-countries-3):** `safe_regex` accepted bounded repetitions. POSIX ERE compiles `{m,n}` into n copies of the automaton, and git grep builds one per thread, so `.{1,32000}x` took git past 8 GB of memory in 15 seconds. A model can be steered into such a pattern by text in a document, and a hostile corpus.json could supply one too. Now refused:
    - counts over 20, or more than 40 in all;
    - more than 4 repetition operators;
    - `?` inside a repeated group;
    - a `{` that does not open a count (git refuses `x{1, 1000}`, which Python reads as text).

    Every git grep that runs a pattern from a model or a manifest uses `--threads=1`. The `global-law://law/` resource template now has the same git budget as a tool call, and law.py's errors there are reported as invalid parameters.
  - On lexifina/global-law d3dead026f (54 corpora), from a fresh clone:
    - The Grundgesetz is now one folder of all German federal law (`germany/bund/acts/grundgesetz`), and Malta is `mt/national/acts`. Old paths still resolve, and the Malta code finds its corpus by country code.
    - "Art. 16a" prefers article-numbered files to a § 16a of another act.
    - `search_law`'s 200-path list takes paths from each corpus in turn; cut alphabetically, `united-states/` never appeared.
    - `changes_between` across 21 changed corpora was 340 KB. Every corpus now stays listed with its counts, and the provisions and laws shown share one budget. The answer is now 47 KB.
    - `list_jurisdictions` gives `complete_to`: the later of a record's last date and the day it was checked. Croatia is checked to 2026, though its last change is from 2013.
    - The tests find paths through the server's own mapping, so they hold on both layouts.

### Large builds

- **Fixed (Switzerland), measured; check every corpus.** Profile one unit with cProfile, sorted by `tottime`, before scaling. Each item below showed up in the first profile.
  - Word-level `difflib.SequenceMatcher` over a whole provision is quadratic, and long provisions such as the Constitution's transitional Art. 197 dominate the build. Match line by line first, then word by word only inside the line blocks that changed. Same result; one act went from 94 s to 15 s.
  - `unicodedata.category()` per character, used to strip control and format characters, took a third of the parse time. One precompiled regex of those ranges does the same.
  - `etree.QName(e).localname` on every element was a hot spot (72,000 calls per act). `t[t.rfind('}') + 1:]` on `e.tag` replaces it. Together with the two fixes above, a three-act build went from 84 s to 12 s.
  - Redlines and derived text are not computed at build time. The reader works them out when a page asks, which also makes the data files smaller.
  - Independent units (acts, titles) are built in a process pool with an ordered `imap`, and one writer streams to `git fast-import` in input order. Hashes are identical with 1 and with 3 workers.
  - Remote concurrency is capped. Parallel Fedlex SPARQL queries slowed every query until they timed out; the build now runs 3 at a time, 75 items per `VALUES` block, with a 300 s timeout. Every response is cached on disk, so a restart resumes for free.

- **Fixed (UK).** `gitwrite --append` starts from `refs/heads/main^0` and adds the new days after the existing documentation commit, so `release.py --append` pushes fast-forward, without `-f`.
- **Adopted (all).** Tags name fixed points only. A tag that moves (such as a `law-head` tag rewritten on every write) goes stale in existing clones, just as a force-push does; use a branch for any moving pointer.
- **Adopted (all, settled by gitlaw-global).** Documentation commits are appended and never replaced, and this tree keeps pinning each corpus's `main` head. Sent to Germany, the UK, the US, Switzerland, the Estonia/Baltics builds and Malta.
- **Open (Germany, UK; here; now resolved by the rule above).** Appending is designed to give the same head hash as a full build. But re-adding the documentation commit at the tip, by rebuilding from the last law commit, orphans the previous documentation commit, which this tree pins, so the pin-ancestry test fails after every append. Agree on one: documentation commits are appended and never replaced, or this tree pins a `law-head` tag (the last law commit). Separately, ordering commits by when the archive first saw a change can make commit dates run backwards, when a change seen late was in force earlier. Run the backwards-date check as well as the equivalence test, because two identical builds can be equally wrong. A removal is dated by the first day the act went missing or by its repealing law, not by the day the 14-day wait ends.

- **Adopted (all, from the US; download rate up from about 6 to 26 documents a minute).**
  - Run several workers on one queue. Each claims a unit with an atomic `mkdir <out>/.claim-<unit>` and marks it done with a file, so no unit is built twice and runs stop and restart freely. Order the queue largest first.
  - Run independent remote calls in a bounded pool (summaries 4 at a time, lookups 8 at a time) and apply the results in their original order, so the output stays deterministic.
  - Cache every lookup on disk.
  - Commit through one streamed `git fast-import`: the same hashes, 2.5 times faster.

- **Adopted (all, from Germany).** Snapshot archives have gaps (one day was missing 3,646 files). Treat an item as repealed only if it never reappears in a later snapshot; otherwise a gap becomes a false repeal and a false re-enactment.

### Tags after a force-push

- **Open (all).** A force-pushed corpus leaves stale tags in existing clones, because `git fetch --tags` does not overwrite a tag that already exists. Tools that read tags then serve the old build. After the Germany rebuild (5bb57fa), an older clone had `in-kraft/2017-07-20` at d8366ff against 023d361 on GitHub, and this tree's reader check failed 32/33. Fix: `git fetch --force --tags` (or `--prune --prune-tags`) whenever pins change, in the tests and in each README.
- **Adopted (US).** README ("How it is built") and REPRODUCE.md ("Changes to this history") say that a rebuild replaces hashes and tags, and that an existing clone runs `git fetch --force --tags origin && git reset --hard origin/main`. This lands with the full-Code rebuild.
- **Checked (Germany).** The new build is correct for Art. 143d: BGBl. I 2009 S. 2248 has "(1) Artikel 109 und 115 …" with no "Die", and BGBl. I 2017 S. 2347 has "auf Grund einer extremen Haushaltsnotlage". The old wording came from the DocPatch transcription that c3e inherited. For the text in force on 20 July 2017, 47 articles differ between the builds. Four are the articles the old build lacked (104c, 143e, 143f, 143g). 43 come from reconciliation with the official text, including content differences: Art. 3(3) 1994, Art. 76 "sechs Wochen", Art. 104a, Art. 143c(4). Each is listed in KORREKTUREN.md.
- **Open (Germany).** Reconciliation covers each article from its last change before 2019 onward. Older versions are still the DocPatch transcription; for example, Art. 143d keeps "Die Artikel" from 2009 to 2017. Checking those against the Gazette is next.
- **Adopted (all, from Germany).** Third-party transcriptions are not the law. Reconcile every version against the official gazette, and record each correction with its words, as Germany's KORREKTUREN.md does. A transcription can be wrong in substance as well as in spelling.

### Country repositories

- **Checked (small countries, independent word audit).** Independent checks already existed for LI, SK, SI, GI, HR, DK, GL and HK, which re-ran with 0 mismatches. New check_words.py for EE, LU, MC, FI, AX, KG and RW: 0 mismatches, except Luxembourg, where an empty `<mod class="mod-start"/>` marker glued words together ("dusixième") from 2021-09-15. That was fixed by appended correction 1252a0c, authored by Legilux, with 18 `Corrects:` spans, CORRECTIONS.md and `correction_trailer`. DK, GL and AU now declare `history: "replayed"`; DK 0217682 checked. Limits: Estonia was checked on each version's first day only, and replayed intermediate versions only for the amending words appearing.
- **Open (here, corrections).** A correction commit that also carries `In-force:` is classified as a law: build.py and law.py read the correction trailer only when `In-force` is absent, and nothing reads `Kind: correction`. Luxembourg 1252a0c therefore shows as a law in force on 2026-08-29. Asked gitlaw-global to let `Kind: correction` win, and the small-country builder to pick one dating convention for corrections.
- **Checked (South Africa, Czechia).** south-africa-law (5e4b50e, 6 commits: the Constitution and the 16th to 18th Amendment Acts) and czechia-law (35e53bb, 33,641 commits) pass the preflight with no warnings. Czechia's force-push over its scaffold (691c50a to 35e53bb) is its first final build, announced to gitlaw-global beforehand: 52,732/52,732 versions byte-identical, 9,641 repeals, two hash-identical rebuilds, a 139-commit `future` branch and 242 tags. It is append-only from 35e53bb. Corrections will be source-authored commits with `Corrected:`, declared as `correction_trailer` in the next documentation commit.
- **Adopted (all replays, from South Africa).** Amending-act markup is incomplete (6 of the 17th Amendment's 12 quoted passages were wrong), so a replay checked only at its end can be wrong at intermediate dates. `corpus.json` gains `history: "replayed"` with a `verification` note that readers show as a caveat; Finland, Åland and Rwanda use it. Rwanda appended it as one documentation commit and passes the preflight.
- **Checked (Georgia).** georgia-law's real build (11,818 commits) replaced the work-in-progress commit with fresh history, as asked, and passes the preflight. Its first citation rule used lookbehind and `\d`, which `git grep -E` rejects; the preflight warned, and the builder appended a POSIX ERE version (ef77971). All 20 published citation rules are now POSIX ERE. (`citation.file` is matched with Python `re`, so `\d` is fine there.)
- **Adopted (small countries).** SMALL-COUNTRY-BRIEF.md requires an independent word-stream check: casefolded letters and digits from the raw source through a separate minimal extractor. An auditor is classifying all 15 published small-country repos and appending fixes, without force-pushing.
- **Open (all, corrections).** Appended text corrections are invisible to global-law if authored "Lexifina" (build.py treats that as documentation and law.py's history skips it), or if they carry no `In-force` and the corpus declares no `correction_trailer`. Author corrections by the source, date them with `Corrected: <day>` declared as `correction_trailer` in corpus.json, and record the span of past dates that still read the wrong words (`Corrects:` and a KORREKTUREN-style list), because an appended fix only corrects from the tip onward.
- **Adopted (all, from Spain and Czechia).** Check text against the source's own words through a path independent of your renderer. A check that renders both sides with the same code passes even when the renderer is wrong: Czechia passed 52,732/52,732 byte checks while a letters-and-digits comparison against the raw HTML found headings regrouped out of order in 11,843 versions and leaked Word conditional comments; Spain lost text inside `<blockquote>`/`<div>` in 536 versions. Sent to the US, Germany, Switzerland, the small-country builder and Armenia/Georgia. **Open (UK):** gitlaw-UK's session has ended, so whoever resumes the UK should confirm `--verify` does not share the provision renderer.
- **Open (tooling).** scripts/test_noon.py (an untracked scratch check) counts every in-force day on the last Sunday of March or October as bad even at a correct 12:00 local, applies EU daylight-saving rules before 1996, and should clamp only below 1970-01-01. Reported by Spain and Czechia. It is not a gate; don't rely on its counts.
- **Open (here, Switzerland; repin in progress).** `main` pins `ch/bund/swiss-law` at 965d882, which the full-SR force-push to switzerland-law (06696ea, 11,509 commits) orphaned. gitlaw-global's rebuild in progress pins Switzerland at 06696ea (`ch/bund/acts`) and Germany at 6f3913a (`de/bund/acts`), with `.gitmodules` on the switzerland-law and germany-law URLs.
- **Checked (Germany, 6f3913a).** The all-federal-law rebuild (3,305 commits, corpus `de/bund/acts`) passes the preflight with no warnings: `modifies.kinds` is empty, and it has a `citation` rule, `language` de, and no comma-joined `Affecting:` lines.
- **Adopted (US).** The citation rule is in the US Code generator's corpus.json and ships with the 53-title rebuild, announced to gitlaw-global first. The CFR corpus has one too, and the US state brief requires a citation rule and a passing check_corpus.py before any push.
- **Fixed (check_corpus.py).** `previous_pins()` matched pins by the repo name in `.gitmodules`, so a renamed repo read as "not yet pinned" and skipped the append-only check. It now keys each pin by the old name, the repo's current GitHub name (following the rename redirect) and `path:<corpus path>`, and switzerland-law correctly fails as rewritten against 965d882. build.py's new `REWRITES_AGREED` excuses an announced full rebuild only at the exact head it was announced with (Switzerland 06696ea).
- **Checked (Kyrgyzstan, Rwanda, Switzerland).** kyrgyzstan-law (17 commits) and rwanda-law (7) pass the preflight with no warnings; switzerland-law's full-SR build passes with no warnings apart from the orphaned pin above. spain-law is still a placeholder.
- **Checked (all, preflight sweep).** `check_corpus.py` on 21 repos: 18 pass with 0 problems. Fails: germany-law (no corpus.json and no `In-force:` commits until its rebuild lands; it is pinned in the old layout), georgia-law (a single "Work in progress" commit; its real build must start from scratch), and spain-law (placeholder). **Open:** the US, UK and Germany have no `citation` rule, while every small country now does; ten small-country repos lack `language`; Armenia lacks `record_to` and `in_force_trailer`. Each was sent to its builder.
- **Checked (Armenia, Malta, Åland).** Armenia and Malta each appended one `citation` rule commit, as did Denmark and Croatia (checked against their earlier heads). Åland's first real build (3a38e6d, 9 commits: Hemvårdsstöd from Ålex) has no merges or backwards dates, and its citation rule followed as an appended commit (07c66c1). Its 2 comma-joined `Affecting:` lines stay, because it is append-only from 3a38e6d; later commits use one line per value.
- **Checked (Greenland).** greenland-law is append-only from its first final build 46aaf2e, with the citation rule appended as ba692ec. It passes the history checks and has `citation`, `default_reach` and `when_absent`. Its 10 comma-joined `Affecting:` lines stay, because that build started before the rule reached the brief; one line per value applies from its next law commit.
- **Checked (11 small-country repos).** Each `corpus.json` gained a `citation` rule as one appended documentation commit (scripts/add_citation_rule.py): Estonia, Luxembourg, Liechtenstein, Slovakia, Slovenia, Monaco, Gibraltar, Hong Kong, Denmark, Croatia and Finland. All are appends of exactly one commit on the previous head, and Finland's global-law pin is still in its history. The small-country brief (scripts/SMALL-COUNTRY-BRIEF.md) now requires one trailer line per value for new builds (IE, KG, GL, AX, RW).
- **Fixed (here; MCP still open).** `trailers()` kept only the first value of a repeated key, losing all but one `Affecting:`/`Also-cited:` line in 230 Malta commits and repeated `Effect-id`s in the UK. New `trailers_all()` in build.py and tools/law.py keeps every value in order and, like `git interpret-trailers`, reads only the last paragraph; site events carry `affecting` as a list. **Open:** mcp_server.py still returns `law.trailers()`; global-MCP is asked to switch.
- **Adopted (all).** One trailer line per value: `Affecting:` gets one line per provision, never comma-joined, because provision names contain commas. Comma-joined today: Denmark 41 lines, Slovakia 35, Estonia 31, Switzerland 9, Finland 3. Append-only repos switch at their next append and keep their old commits; Switzerland, Slovakia and Slovenia switch in their next full build. global-law reads both shapes.
- **Checked (Armenia, Denmark, Croatia, Finland, Gibraltar, Hong Kong).** No merges, no dates running backwards, no future dates, and author and committer dates agree. Every law commit's date equals its `In-force` day, except laws in force before 1970 (Armenia 10, Denmark 1), which are clamped to 1970-01-01 as agreed. Armenia appended (14,422 to 14,424). `Consolidated:` holds a URL or archive path in Denmark, Finland and Hong Kong, but a date in Switzerland. global-law reads it as a date only when a corpus names it as its baseline label, and only on commits without `In-force`, so nothing is misread.
- **Checked (all, 28 October, evening).** All 12 pins on `main` are in their corpus's published history: 10 at the head, UK 1 and Malta 2 documentation commits behind. All 15 published `corpus.json` files have `scope.default_reach` and `scope.when_absent`, and none uses `modifies.kinds` outside the shared vocabulary. The published `.gitmodules` still names `lexifina/swiss-law`; the builder already uses `switzerland-law`, so the next build corrects it. `aland-law` (one commit, no README) and `georgia-law` (no REPRODUCE.md) are still placeholders.
- **Fixed (UK, 2d4137c).** `corpus.json` appended, without a force-push, in the shared shape. `default_reach` is the presumption against retrospective effect (Interpretation Act 1978 s. 16; L'Office Cherifien v Yamashita-Shinnihon [1994] 1 AC 486), with `decided_here: false`. The all-UK harvest runs at legislation.gov.uk's robots.txt Crawl-delay of 5 seconds, which takes about a month unless the publisher agrees to bulk access.
- **Adopted (all).** Repositories use country names: grundgesetz is now germany-law, uk-law-history is now united-kingdom-law, us-code-history is now united-states-law. GitHub redirects the old names, but `.gitmodules`, site links and local remotes should use the new ones, because a redirect breaks if a repo is ever created under the old name.
- **Fixed (Switzerland).** swiss-law is renamed to switzerland-law, so the /watch page link resolves and GitHub redirects the old name. `corpus.json` comes with the full-SR build: noon Zurich, the `Consolidated:` and `Corrected:` trailers, `Applies:` grouping, `scope.when_absent`, `default_reach` (the bar on retroactivity, with transitional rules deciding; `decided_here: false`), the future branch `future`, and the citation pattern. No `Modifies:` kinds yet, because the Swiss data has no changes that leave the words unchanged.
- **Open (South America).** Paraguay was force-rewritten twice more (bc6e488 to 49195df: 50 commits on the new side, 32 dropped from the old). None of the 12 South American repos has `corpus.json`, although each has README.md and REPRODUCE.md. They are built on another machine, and their work sits on this repo's `wip-south-america` branch, which shares no history with `main`. Nothing on `main` pins them, so no pin is broken. They need `corpus.json` and the append-only rule before they are added to `main`.
- **Fixed (Germany, in the builder; not yet pushed).** `corpus.json` comes with the full rebuild (the one force-push agreed for the new layout, as germany-law), with `default_reach` = Rückwirkungsverbot (Art. 20(3) GG; Art. 103(2) for criminal law), `decided_here: false`. But its `modifies.kinds` (changed, added, removed) are ordinary text changes, which clashes with the shared meaning of `Modifies:` (changes that leave the words unchanged). It should be `[]`, with text-change kinds under another key. The builder now writes `modifies.kinds: []` and puts changed, added and removed under a separate `changes` key. **Adopted (here):** `test_corpus_json_follows_the_shared_rules` checks every pinned `corpus.json` against the shared vocabulary.
- **Fixed (Switzerland).** `corpus.json` comes with the full-SR build. The US, Malta, Estonia, Luxembourg, Liechtenstein, Slovakia, Slovenia and Monaco have it. Every corpus has README.md and REPRODUCE.md (compliance sweep, 28 October 2026).

- **Checked (Malta, 1540d73).** First full build: 7,440 commits. No merges, no backwards or future dates, trailers parse, and `corpus.json` is present. Changes no law explains are authored "Legislation Unit (legislation.mt)" and labelled. From here it is append-only.

- **Fixed (Estonia, Luxembourg, Liechtenstein).** `corpus.json` was added by replacing the documentation commit, after the append-only rule was adopted. That was the last rewrite: from 8adfdce, 19a8492 and 18410b0 these repos are append-only. Slovakia, Slovenia and Monaco are force-pushed only until their first final build.
- **Open (country placeholders).** Two sessions wrote to the same repo: research pushed a placeholder to monaco-law, and a real build later replaced it. A placeholder script must refuse to push to any repo with commits it did not create, and a real build that replaces a placeholder starts from scratch.

- **Adopted (all, from research).** About 201 private placeholder repos (`lexifina/<country>-law`) record each country's official sources, what a build would need, and the transcription warning, before any law is added. Countries already being built (Estonia, Liechtenstein, Luxembourg, Malta) and the existing corpora were skipped, so no names clash.
- **Open (all placeholders).** Each placeholder's first commit is dated 2026-10-28. A real build must replace that history from scratch and force-push; it must never append, or dates on `main` run backwards and every date lookup breaks.

### Sources: PDF and language

- **Adopted (all, from Malta).** Letter-spaced justified PDF lines extract as "m a k e re g u l a t i o n s", because there is a real space glyph after every letter. Read character boxes (pymupdf `rawdict`) and keep a space only where there is a visible gap (over 0.5 pt). Treat units whose text is equal once all whitespace is removed as unchanged, so re-typesetting never becomes a commit.
- **Adopted (all, from Malta).** Official sites sometimes serve the other language's version at one language's address, and upload the same date more than once: 212 of 5,079 Maltese laws. Detect the language from the text itself (for Maltese, ħ ġ ż ċ) and keep one version per date, or thousands of false "changes" get credited to old laws. This applies to any bilingual or multilingual source: Welsh on legislation.gov.uk, French and Italian on Fedlex, Irish, Canadian French.

### Reading tools (MCP)

- **Adopted (all MCP servers, from global-MCP).** Claude Code shows the model an MCP tool's `structuredContent`, not its text content (proved with stream-json traces). Put the explanation inside the structured data; global-law's server leads every answer with `summary`.
- **Fixed (here).** `read_law` reports `beyond_the_words`: the latest open `Modifies:` effect per provision and kind, with `ended` closing an effect and `Curated: yes` noted. Scope taken from the law's words rather than data is labelled as such.
- **Fixed (here).** `applies_to_case` splits a case into periods. A §1182 case filed 2022-05-01 gets the gap text, then $7.5M from 2022-06-21 by Pub. L. 117-151's reach-back.
- **Adopted (all, settled by gitlaw-global).** `corpus.json` at each corpus root, in the US shape, is the per-corpus standard for the date convention, `Applies:` grouping, `Modifies:` kinds and `scope.when_absent` / `scope.default_reach` (with `decided_here`). This tree reads it.
- **Adopted (US; proposed for all).** A missing `Applies:` line means only that no scope note was found. It does not mean the change reaches every case. Reach is then a question of law: in the US, the presumption against retroactivity (Landgraf v. USI Film Products, 511 U.S. 244 (1994)), with procedural and jurisdictional changes often excepted. The history does not decide it. The US ships `corpus.json` at its root with `scope.when_absent` and `scope.default_reach` = `{rule, meaning, authority, decided_here: false}`, plus the date convention, the `Applies:` grouping and the `Modifies:` kinds. Each corpus should declare its own. Tools report "reach not recorded; presumption …" and do not compute an answer.

### Checks

- **Checked (here, 6a7bb70).** A fresh clone with `git submodule update --init` passes all 61 tests (`tests/test_law.py` and `tests/test_mcp.py`). Every pin equals its corpus's main, and `main` has no merges, no future-dated commits and no backwards dates.

- **Checked (all, 28 October 2026).** On every corpus's `main`:
  - no merge commits
  - commit dates never go backwards along `--first-parent`
  - no commit dated in the future
  - pins for the US (c9591ac) and Germany (b0d346e) match their heads.
- **Checked (US).** A rules-as-code version of 11 U.S.C. §1182(1) agrees with this tree. `tools/law.py show` gives the same wording on all five dates the provision changed: 19 February 2020, 27 March 2020, 27 March 2022, 21 June 2022 and 21 June 2024.
- **Checked (US).** Every change was verified on its in-force day: the new text present that day and the old text the day before. 274 of 274 passed.
- **Recommended (all).**
  - A mutation test of any test suite that encodes the law: in one trial, 6 of 18 deliberate errors survived, all at exact boundaries. Test the day before and the day of every in-force date.
  - A blind test: an agent given only the clone and seven questions with known answers.
