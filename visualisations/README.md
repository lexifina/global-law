# Visualisations

Graphs drawn from the corpora in this repository, rebuilt every half hour while the analysis runs.

- `law-in-motion.html` is one self-contained page with two tabs. Open it in a browser; it loads its fonts and the d3 charting library from the web.
  - **Findings:** the German Basic Law since 1949, the US Code since 2017, Swiss, UK and Maltese law, and the constitutions and companion acts of Croatia, Denmark, Estonia, Finland, Gibraltar, Hong Kong, Liechtenstein, Luxembourg, Monaco, Slovakia and Slovenia.
  - **Research agenda:** the published research each analysis builds on.
- `legal-system-bridges.html` matches provisions that do the same legal job in different jurisdictions (German, Swiss, UK and US law). It covers 308 judged bridges, evaluated against Constitute's topic tags and a hand-written answer key. Its pipeline is in `scripts/global-law/bridges` in the Lexifina repository.
- `the-shape-of-waiting.png` is a still of one chart from `law-in-motion.html`: how long each jurisdiction's law waits between adoption and entry into force. The main README shows it.
- `src/` holds the scripts that produce it, the JSON each analysis writes, and `geo/` (Natural Earth country shapes from world-atlas). The scripts read the corpus checkouts in `~/Documents` and never write to them. The Basic Law is read from a separate clone at `~/Documents/law-in-motion/corpora/grundgesetz`, because the German repositories are rebuilt in place. Scratch output, such as screenshots and logs, goes to `src/.build/`.

<!-- stills:begin -->

## The charts

Still images of every chart, rendered from the two pages by `src/stills.mjs`. Open the HTML pages for the interactive versions and the full text.

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

![Constitutions grow, at very different speeds](stills/law-in-motion-55-constitutions-grow-at-very-different-speeds.png)

![Constitutional wording lasts 7 years in Croatia and 88 in Luxembourg](stills/law-in-motion-56-constitutional-wording-lasts-7-years-in-croatia-an.png)

![Amended law is harder to read than the original](stills/law-in-motion-57-amended-law-is-harder-to-read-than-the-original.png)

![Temporary law, found without being told where to look](stills/law-in-motion-58-temporary-law-found-without-being-told-where-to-lo.png)

![Switzerland and Denmark start their law on 1 January. Most others start it any day](stills/law-in-motion-59-switzerland-and-denmark-start-their-law-on-1-janua.png)

![A whole statute book, month by month](stills/law-in-motion-60-a-whole-statute-book-month-by-month.png)

![The rules for winning power change faster than the constitution](stills/law-in-motion-61-the-rules-for-winning-power-change-faster-than-the.png)

![Constitutions forbid, ordinary laws oblige](stills/law-in-motion-62-constitutions-forbid-ordinary-laws-oblige.png)

![Where Malta's law actually changes](stills/law-in-motion-63-where-malta-s-law-actually-changes.png)

![The articles everything points to are the ones that keep changing](stills/law-in-motion-64-the-articles-everything-points-to-are-the-ones-tha.png)

![Most amending acts change one or two provisions](stills/law-in-motion-65-most-amending-acts-change-one-or-two-provisions.png)

![Law changes in bursts](stills/law-in-motion-66-law-changes-in-bursts.png)

![Articles that are always rewritten together](stills/law-in-motion-67-articles-that-are-always-rewritten-together.png)

### Legal system bridges (`legal-system-bridges.html`)

![The bridge map](stills/legal-system-bridges-01-the-bridge-map.png)

![A closer match is not the same rule](stills/legal-system-bridges-02-a-closer-match-is-not-the-same-rule.png)

![Reranking finds the counterpart more often](stills/legal-system-bridges-03-reranking-finds-the-counterpart-more-often.png)

![Substance versus legal machinery](stills/legal-system-bridges-04-substance-versus-legal-machinery.png)

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
