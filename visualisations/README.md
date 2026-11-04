# Visualisations

Graphs drawn from the corpora in this repository, rebuilt every half hour while the analysis runs.

- `law-in-motion.html` is one self-contained page with two tabs. Open it in a browser; it loads its fonts and the d3 charting library from the web.
  - **Findings:** the German Basic Law since 1949, the US Code since 2017, Swiss, UK and Maltese law, and the constitutions and companion acts of Croatia, Denmark, Estonia, Finland, Gibraltar, Hong Kong, Liechtenstein, Luxembourg, Monaco, Slovakia and Slovenia.
  - **Research agenda:** the published research each analysis builds on.
- `legal-system-bridges.html` matches provisions that do the same legal job in different jurisdictions (German, Swiss, UK and US law). It covers 308 judged bridges, evaluated against Constitute's topic tags and a hand-written answer key. Its pipeline is in `scripts/global-law/bridges` in the Lexifina repository.
- `law-drawn.html` (Law, Drawn) has ten charts: Spain's legal calendar and paired amendments, each country's busiest year, Spain's executive-made statute book, the French Code civil, global-law's growth, the world's 612 histories, federations' regional calendars, Russia's December wave and towns that copy their laws.
- `life-of-a-provision.html` (The Life of a Provision) has five charts on how individual provisions are amended and survive, the EU law each country cites, and each country's biggest day in law.
- `romanian-law-drawn.html` (Romanian Law, Drawn) has 26 charts on Romania: who makes its law (Parliament or the government's ordinances), its codes, the Constitutional Court, the Fiscal Code, the Official Gazette, and Romania against its neighbours, Spain and all of global law.
- `the-romanian-record.html` (The Romanian Record) has four more: the 1991 Constitution against its 2003 revision, the Official Gazette's issue numbers since 1991, the ministries named in government decisions, and the lines of Romania's codes.
- `the-shape-of-waiting.png` is a still of one chart from `law-in-motion.html`: how long each jurisdiction's law waits between adoption and entry into force. The main README shows it.
- `src/` holds the scripts that produce it, the JSON each analysis writes, and `geo/` (Natural Earth country shapes from world-atlas). The scripts read the corpus checkouts in `~/Documents` and never write to them. The Basic Law is read from a separate clone at `~/Documents/law-in-motion/corpora/grundgesetz`, because the German repositories are rebuilt in place. Scratch output, such as screenshots and logs, goes to `src/.build/`.
- `src/law-drawn/` holds the scripts and data behind the Law, Drawn and Life of a Provision pages (`pass.py`, `analyse*.py`, then `build*.py` and `patch*.py`), and `src/law-drawn/romania/` those behind the two Romania pages (`part*_data.py` and `page2_data.py` write the JSON; `build_ro.py` and `build_page2.py` assemble the pages). The Romania scripts read a checkout of `romania-law` in `tip/` beside them. Intermediate files over 1 MB (such as `lives.json`) are not kept; rerun the analysis scripts to recreate them.

<!-- stills:begin -->

## The charts

Still images of every chart, rendered from the pages by `src/stills.mjs`. Open the HTML pages for the interactive versions and the full text.

### Law in Motion (`law-in-motion.html`)

![The Basic Law has doubled in length, mostly in six afternoons](stills/law-in-motion-01-the-basic-law-has-doubled-in-length-mostly-in-six-.png)

![The rewriting happens in the money articles](stills/law-in-motion-02-the-rewriting-happens-in-the-money-articles.png)

![Two-thirds is the rule, and it has never been close](stills/law-in-motion-03-two-thirds-is-the-rule-and-it-has-never-been-close.png)

![Emergency law switches itself off, sometimes before anyone is ready](stills/law-in-motion-04-emergency-law-switches-itself-off-sometimes-before.png)

![From passed to in force: three days in Britain, over a year in Switzerland](stills/law-in-motion-05-from-passed-to-in-force-three-days-in-britain-over.png)

![Copyright law gets changed by defence bills](stills/law-in-motion-06-copyright-law-gets-changed-by-defence-bills.png)

![Who put their name to the constitution's changes](stills/law-in-motion-07-who-put-their-name-to-the-constitution-s-changes.png)

![How much of the world's law can become a history today](stills/law-in-motion-08-how-much-of-the-world-s-law-can-become-a-history-t.png)

![Most of what is loaded is European, and much of it small](stills/law-in-motion-09-most-of-what-is-loaded-is-european-and-much-of-it-.png)

![Eighty years of amending acts on one timeline](stills/law-in-motion-10-eighty-years-of-amending-acts-on-one-timeline.png)

![Constitutional lifelines](stills/law-in-motion-11-constitutional-lifelines.png)

![How long the world waits for a new law to apply](stills/law-in-motion-12-how-long-the-world-waits-for-a-new-law-to-apply.png)

![Three whole statute books, side by side](stills/law-in-motion-13-three-whole-statute-books-side-by-side.png)

![How a Georgian law decides when it starts](stills/law-in-motion-14-how-a-georgian-law-decides-when-it-starts.png)

![Old constitutions are not the stable ones](stills/law-in-motion-15-old-constitutions-are-not-the-stable-ones.png)

![Where constitutions change fastest](stills/law-in-motion-16-where-constitutions-change-fastest.png)

![Two families of constitution: rewritten every decade, or almost never](stills/law-in-motion-17-two-families-of-constitution-rewritten-every-decad.png)

![How long is a constitution?](stills/law-in-motion-18-how-long-is-a-constitution.png)

![Amendments make constitutions harder to read, almost everywhere](stills/law-in-motion-19-amendments-make-constitutions-harder-to-read-almos.png)

![The global history of law loaded so far](stills/law-in-motion-20-the-global-history-of-law-loaded-so-far.png)

![How far back each history reaches](stills/law-in-motion-21-how-far-back-each-history-reaches.png)

![Thirty-seven years of law-making, country by country](stills/law-in-motion-22-thirty-seven-years-of-law-making-country-by-countr.png)

![From adoption to application, every country that records both](stills/law-in-motion-23-from-adoption-to-application-every-country-that-re.png)

![Which day of the week law starts](stills/law-in-motion-24-which-day-of-the-week-law-starts.png)

![The legal year: when law takes effect, month by month](stills/law-in-motion-25-the-legal-year-when-law-takes-effect-month-by-mont.png)

![Two centuries of law-making](stills/law-in-motion-26-two-centuries-of-law-making.png)

![Who is legislating faster than a decade ago](stills/law-in-motion-27-who-is-legislating-faster-than-a-decade-ago.png)

![Is law getting faster to apply?](stills/law-in-motion-28-is-law-getting-faster-to-apply.png)

![The days law is passed](stills/law-in-motion-29-the-days-law-is-passed.png)

![The December rush](stills/law-in-motion-30-the-december-rush.png)

![Every history at a glance](stills/law-in-motion-31-every-history-at-a-glance.png)

![The first of the month](stills/law-in-motion-32-the-first-of-the-month.png)

![The shape of waiting](stills/law-in-motion-33-the-shape-of-waiting.png)

![Breadth against depth](stills/law-in-motion-34-breadth-against-depth.png)

![A map of waiting](stills/law-in-motion-35-a-map-of-waiting.png)

![Where law starts on the first of the month](stills/law-in-motion-36-where-law-starts-on-the-first-of-the-month.png)

![Each country's busiest month for new law](stills/law-in-motion-37-each-country-s-busiest-month-for-new-law.png)

![Do busier legislatures make law wait less?](stills/law-in-motion-38-do-busier-legislatures-make-law-wait-less.png)

![Four calendar styles of law-making](stills/law-in-motion-39-four-calendar-styles-of-law-making.png)

![The legal year](stills/law-in-motion-40-the-legal-year.png)

![Law that applies before it is passed](stills/law-in-motion-41-law-that-applies-before-it-is-passed.png)

![Law that applies the day it is passed](stills/law-in-motion-42-law-that-applies-the-day-it-is-passed.png)

![Where law starts at the weekend](stills/law-in-motion-43-where-law-starts-at-the-weekend.png)

![How far back each country's history reaches](stills/law-in-motion-44-how-far-back-each-country-s-history-reaches.png)

![How much dated law each history holds](stills/law-in-motion-45-how-much-dated-law-each-history-holds.png)

![Who legislated more in 2025 than usual](stills/law-in-motion-46-who-legislated-more-in-2025-than-usual.png)

![Who makes the law: parliaments or governments?](stills/law-in-motion-47-who-makes-the-law-parliaments-or-governments.png)

![The executive's share of new law](stills/law-in-motion-48-the-executive-s-share-of-new-law.png)

![Has the executive's share of new law grown?](stills/law-in-motion-49-has-the-executive-s-share-of-new-law-grown.png)

![Do decrees apply faster than laws?](stills/law-in-motion-50-do-decrees-apply-faster-than-laws.png)

![Every day of the legal year](stills/law-in-motion-51-every-day-of-the-legal-year.png)

![The world's busiest start dates](stills/law-in-motion-52-the-world-s-busiest-start-dates.png)

![How few dates carry the law](stills/law-in-motion-53-how-few-dates-carry-the-law.png)

![Where law starts on 1 July](stills/law-in-motion-54-where-law-starts-on-1-july.png)

![Which countries keep the same legal calendar](stills/law-in-motion-55-which-countries-keep-the-same-legal-calendar.png)

![How predictable is the day new law starts?](stills/law-in-motion-56-how-predictable-is-the-day-new-law-starts.png)

![Constitutions grow, at very different speeds](stills/law-in-motion-57-constitutions-grow-at-very-different-speeds.png)

![Constitutional wording lasts 7 years in Croatia and 88 in Luxembourg](stills/law-in-motion-58-constitutional-wording-lasts-7-years-in-croatia-an.png)

![Amended law is harder to read than the original](stills/law-in-motion-59-amended-law-is-harder-to-read-than-the-original.png)

![Temporary law, found without being told where to look](stills/law-in-motion-60-temporary-law-found-without-being-told-where-to-lo.png)

![Switzerland and Denmark start their law on 1 January. Most others start it any day](stills/law-in-motion-61-switzerland-and-denmark-start-their-law-on-1-janua.png)

![A whole statute book, month by month](stills/law-in-motion-62-a-whole-statute-book-month-by-month.png)

![The rules for winning power change faster than the constitution](stills/law-in-motion-63-the-rules-for-winning-power-change-faster-than-the.png)

![Constitutions forbid, ordinary laws oblige](stills/law-in-motion-64-constitutions-forbid-ordinary-laws-oblige.png)

![Where Malta's law actually changes](stills/law-in-motion-65-where-malta-s-law-actually-changes.png)

![The articles everything points to are the ones that keep changing](stills/law-in-motion-66-the-articles-everything-points-to-are-the-ones-tha.png)

![Most amending acts change one or two provisions](stills/law-in-motion-67-most-amending-acts-change-one-or-two-provisions.png)

![Law changes in bursts](stills/law-in-motion-68-law-changes-in-bursts.png)

![Articles that are always rewritten together](stills/law-in-motion-69-articles-that-are-always-rewritten-together.png)

### Legal system bridges (`legal-system-bridges.html`)

![The bridge map](stills/legal-system-bridges-01-the-bridge-map.png)

![A closer match is not the same rule](stills/legal-system-bridges-02-a-closer-match-is-not-the-same-rule.png)

![Reranking finds the counterpart more often](stills/legal-system-bridges-03-reranking-finds-the-counterpart-more-often.png)

![Substance versus legal machinery](stills/legal-system-bridges-04-substance-versus-legal-machinery.png)

### Law, Drawn (`law-drawn.html`)

![Spanish law keeps a calendar: twenty times as many acts start on 1 January as on an average day](stills/law-drawn-01-spanish-law-keeps-a-calendar-twenty-times-as-many-.png)

![Spain amends its laws in pairs: social security with the Workers' Statute, corporate tax with income tax](stills/law-drawn-02-spain-amends-its-laws-in-pairs-social-security-wit.png)

![When each country made the most law](stills/law-drawn-03-when-each-country-made-the-most-law.png)

![Three quarters of Spain's statute book was issued by the government](stills/law-drawn-04-three-quarters-of-spain-s-statute-book-was-issued-.png)

![Since 1994 France has rewritten most of its Code civil, but almost never the law of property](stills/law-drawn-05-since-1994-france-has-rewritten-most-of-its-code-c.png)

![global-law grew sixfold in four days, mostly below the national level](stills/law-drawn-06-global-law-grew-sixfold-in-four-days-mostly-below-.png)

![The world's law, now in 612 histories](stills/law-drawn-07-the-world-s-law-now-in-612-histories.png)

![Each federation's regions keep a different calendar](stills/law-drawn-08-each-federation-s-regions-keep-a-different-calenda.png)

![Russia's regions publish their law in a December wave](stills/law-drawn-09-russia-s-regions-publish-their-law-in-a-december-w.png)

![Towns copy their laws, mostly from the province's templates](stills/law-drawn-10-towns-copy-their-laws-mostly-from-the-province-s-t.png)

### The Life of a Provision (`life-of-a-provision.html`)

![A few provisions take most of the amendments, and they are usually the law's plumbing](stills/life-of-a-provision-01-a-few-provisions-take-most-of-the-amendments-and-t.png)

![Five years after it is written, 94% of Spanish provisions are still untouched. In Romania, 53% are](stills/life-of-a-provision-02-five-years-after-it-is-written-94-of-spanish-provi.png)

![Each country's biggest day in law](stills/life-of-a-provision-03-each-country-s-biggest-day-in-law.png)

![Spain's law cites the GDPR most. Czechia's cites the rule on notifying technical standards](stills/life-of-a-provision-04-spain-s-law-cites-the-gdpr-most-czechia-s-cites-th.png)

![Spain's widest-reaching laws arrive on New Year's Day](stills/life-of-a-provision-05-spain-s-widest-reaching-laws-arrive-on-new-year-s-.png)

### Romanian Law, Drawn (`romanian-law-drawn.html`)

![The government writes four acts for every law Parliament passes](stills/romanian-law-drawn-01-the-government-writes-four-acts-for-every-law-parl.png)

![Every government rules by emergency ordinance, some three times as often as others](stills/romanian-law-drawn-02-every-government-rules-by-emergency-ordinance-some.png)

![An emergency ordinance applies at once. Parliament takes a median of 319 days to rule on it](stills/romanian-law-drawn-03-an-emergency-ordinance-applies-at-once-parliament-.png)

![Three days after publication: the Constitution's default start day](stills/romanian-law-drawn-04-three-days-after-publication-the-constitution-s-de.png)

![The four new codes rewired the rest of Romanian law](stills/romanian-law-drawn-05-the-four-new-codes-rewired-the-rest-of-romanian-la.png)

![The Constitutional Court's red pen falls hardest on criminal procedure](stills/romanian-law-drawn-06-the-constitutional-court-s-red-pen-falls-hardest-o.png)

![The Fiscal Code changes about twenty times a year, and an emergency ordinance makes most of the changes](stills/romanian-law-drawn-07-the-fiscal-code-changes-about-twenty-times-a-year-.png)

![The Official Gazette corrects its own text, usually two months later](stills/romanian-law-drawn-08-the-official-gazette-corrects-its-own-text-usually.png)

![Elsewhere an emergency decree lapses if Parliament does not act. In Romania it does not](stills/romanian-law-drawn-09-elsewhere-an-emergency-decree-lapses-if-parliament.png)

![Romania issues nine times as many emergency laws as Spain, but Spain's Parliament passes far fewer laws](stills/romanian-law-drawn-10-romania-issues-nine-times-as-many-emergency-laws-a.png)

![Romania and Bulgaria give a new law three days. Their neighbours give it a week or two](stills/romanian-law-drawn-11-romania-and-bulgaria-give-a-new-law-three-days-the.png)

![Romanian law starts any day of the month, and rarely at the weekend](stills/romanian-law-drawn-12-romanian-law-starts-any-day-of-the-month-and-rarel.png)

![From adoption to force, Romanian law waits six days, as French law does](stills/romanian-law-drawn-13-from-adoption-to-force-romanian-law-waits-six-days.png)

![The Official Gazette is a weekday paper, busiest on Thursdays and in December](stills/romanian-law-drawn-14-the-official-gazette-is-a-weekday-paper-busiest-on.png)

![Prefects change everywhere, coats of arms cluster inside the Carpathians, and property means Bucharest](stills/romanian-law-drawn-15-prefects-change-everywhere-coats-of-arms-cluster-i.png)

![Parliament now mostly approves the government's ordinances and amends its own laws; new law is about one in seven](stills/romanian-law-drawn-16-parliament-now-mostly-approves-the-government-s-or.png)

![One article in five of the Fiscal Code still reads as it did in 2015](stills/romanian-law-drawn-17-one-article-in-five-of-the-fiscal-code-still-reads.png)

![The government rewrites Romania's tax and health law; Parliament rewrites its education, labour and pension law](stills/romanian-law-drawn-18-the-government-rewrites-romania-s-tax-and-health-l.png)

![The Fiscal Code promises six months' notice of a change by law. It gave it four times](stills/romanian-law-drawn-19-the-fiscal-code-promises-six-months-notice-of-a-ch.png)

![Half the corpus exists only to amend the other half, and most law in force dates from after 2014](stills/romanian-law-drawn-20-half-the-corpus-exists-only-to-amend-the-other-hal.png)

![Parliament reaches further back than the government: it is still rewriting the law of the 1990s](stills/romanian-law-drawn-21-parliament-reaches-further-back-than-the-governmen.png)

![Government decisions amend only each other, while laws and emergency ordinances rewrite one another](stills/romanian-law-drawn-22-government-decisions-amend-only-each-other-while-l.png)

![An emergency ordinance is rewritten mostly by more emergency ordinances, and no act is rewritten mostly by ordinance](stills/romanian-law-drawn-23-an-emergency-ordinance-is-rewritten-mostly-by-more.png)

![Romania's is the second-largest record in global law, after France's](stills/romanian-law-drawn-24-romania-s-is-the-second-largest-record-in-global-l.png)

![Romanian law takes effect on any day of the year, more evenly than in any other country with enough dates to tell](stills/romanian-law-drawn-25-romanian-law-takes-effect-on-any-day-of-the-year-m.png)

![By the days its law takes effect, Romania belongs with Spain and France, and furthest from Sweden](stills/romanian-law-drawn-26-by-the-days-its-law-takes-effect-romania-belongs-w.png)

### The Romanian Record (`the-romanian-record.html`)

![The 2003 revision added Europe and NATO and renumbered most of the Constitution, but kept 67 articles word for word](stills/the-romanian-record-01-the-2003-revision-added-europe-and-nato-and-renumb.png)

![The Official Gazette now prints five times as many issues a year as in 1991](stills/the-romanian-record-02-the-official-gazette-now-prints-five-times-as-many.png)

![When a government decision names a ministry, it is usually handing over land or buildings](stills/the-romanian-record-03-when-a-government-decision-names-a-ministry-it-is-.png)

![Romania kept its 19th-century codes into the 2010s, and each code that replaced one changes faster than its predecessor did](stills/the-romanian-record-04-romania-kept-its-19th-century-codes-into-the-2010s.png)

<!-- stills:end -->

## Rebuilding

Run from `src/`, in this order:

1. `python -I -X utf8 inventory.py`: which corpora are new or changed since the last saved round.
2. `stories.py`, then `story_data.py`: findings from the German, Swiss, UK and US histories.
3. The cross-jurisdiction analyses, each writing its own JSON:
   - `analysis2.py`: wording survival, readability, temporary law and constitution growth.
   - `analysis3.py`: the in-force calendar and Malta's monthly activity.
   - `analysis4.py`: obligation and prohibition words.
   - `analysis5.py`: Malta's most-amended chapters.
   - `analysis6.py`: hub articles and the size of amending acts.
   - `analysis7.py`: activity by year and co-amendment.
   - `analysis8.py`: the world readiness map.
   - `analysis9.py`: the global start delay and whole statute books.
   - `analysis10.py`: per-constitution wording life, length and readability.
   - `analysis11.py`: every repository's metadata in one pass, for the bubble map, coverage spans, heatmap and calendar.
   - `episodes.py`: groups the temporary-law results.

   `analysis2.py` caches each repository's results in `.build/a2cache` by HEAD commit, so a round only recomputes repositories that changed. The Basic Law and Malta are read from stable clones in `~/Documents/law-in-motion/corpora`, because their working repositories are rebuilt in place.
4. `compose.py` assembles `law-in-motion.html` from `motion_template.html`, `part_new_figs.html`, `part_new_js.js` and `agenda.html`.
5. `node shot_el.cjs <playwright path> ../law-in-motion.html <figure ids>` screenshots charts for checking.

Every caption number is checked against the analysis output before a rebuild is kept. The Constitute topic tags used for the bridge answer key come from `constitute_parse.py` and the Comparative Constitutions Project.
