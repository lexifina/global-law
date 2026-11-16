# Visualisations

Charts drawn from the corpora in this repository: 175 charts in six categories, at most 20 to a page.

- **[Countries](COUNTRIES.md)**: which countries have chart pages of their own in their repositories, and which are placeholders for now.
- **Categories**: below. Each category's README shows a still of every chart; open a page in a browser for the interactive charts and their full text. Each page is one file with its data inside and loads only its fonts and the d3 library from the web.

## Categories

<!-- categories:begin -->

| Category | Pages | Charts |
| --- | --- | ---: |
| [When law is made and when it starts](when-law-starts/README.md): The legal calendar: the days, weeks and months law is passed, published and put in force, and how long it waits in between. | [The legal calendar](when-law-starts/the-legal-calendar.html), [The busiest start dates](when-law-starts/start-dates.html), [Roses of the law](when-law-starts/roses-of-the-law.html), [The legal year, five ways](when-law-starts/the-legal-year-five-ways.html) | 52 |
| [Constitutions](constitutions/README.md): How constitutions grow, how fast they change, how they are amended and how long their wording lasts. | [Constitutions](constitutions/constitutions.html) | 15 |
| [How law changes](how-law-changes/README.md): Amending acts and what they touch: who makes law, which provisions keep changing, how often each country rewrites its law and how old its law in force is. | [Amending acts and who makes law](how-law-changes/amending-acts.html), [Rewrites and ages](how-law-changes/rewrites-and-ages.html), [The life of a provision](how-law-changes/the-life-of-a-provision.html) | 31 |
| [The record itself](the-record/README.md): What global-law holds: how much of the world's law is loaded, how far back each history reaches and how fast it grows. | [What is loaded](the-record/the-record.html), [Law, drawn](the-record/law-drawn.html) | 21 |
| [Country studies](country-studies/README.md): One country at a time: Romania in depth, and seventeen countries' own chart pages set side by side. | [Romanian law, drawn (1 of 2): who makes the law](country-studies/romanian-law-drawn-1.html), [Romanian law, drawn (2 of 2): the Gazette, the codes and the corpus](country-studies/romanian-law-drawn-2.html), [The Romanian record](country-studies/the-romanian-record.html), [Seventeen countries, one at a time (1 of 2): calendars and lawmaking](country-studies/seventeen-countries-1.html), [Seventeen countries, one at a time (2 of 2): constitutions, money and the records](country-studies/seventeen-countries-2.html) | 52 |
| [Legal system bridges](bridges/README.md): Provisions that do the same legal job in different jurisdictions (German, Swiss, UK and US law), matched and judged. | [Legal system bridges](bridges/legal-system-bridges.html) | 4 |

<!-- categories:end -->

## How the pages are made

Each chart is drawn once, on one of ten full pages in `src/pages/` (Law in Motion, Law Drawn, The Life of a Provision, Roses of the Law, Rewrites and Ages, The Legal Year Five Ways, Romanian Law Drawn, The Romanian Record, Seventeen Countries One at a Time, Legal System Bridges). A category page is one of those pages with the charts of other categories hidden, so every chart keeps the code and data it was built with. `src/categories.json` says which chart goes where.

- `the-shape-of-waiting.png` is a still of one chart from `src/pages/law-in-motion.html`: how long each jurisdiction's law waits between adoption and entry into force. The main README shows it.
- `src/` holds the scripts that produce the pages, the JSON each analysis writes, and `geo/` (Natural Earth country shapes from world-atlas). The scripts read the corpus checkouts in `~/Documents` and never write to them. The Basic Law is read from a separate clone at `~/Documents/law-in-motion/corpora/grundgesetz`, because the German repositories are rebuilt in place. Scratch output, such as screenshots and logs, goes to `src/.build/`.
- `src/law-roses/` holds the scripts and data behind Roses of the Law: `roses_prep.py` turns `analysis11.json` into `roses-data.json`; `roses2_scan.py` reads the law repositories in `~/Documents` (about three minutes) and `roses2_prep.py` turns its output into `roses2-data.json`; `build.py` fills `roses.tpl.html` with both and writes `law-roses.html`.
- `src/law-rewrites/` holds the page behind Rewrites and Ages: `rw_prep.py` turns `../law-roses/roses2-data.json` into `rw-data.json`, and `build.py` fills `rw.tpl.html` with it and the shapes in `geo/countries-50m.json`.
- `src/legal-year/` holds the page behind The Legal Year, Five Ways: `ly_prep.py` turns `analysis11.json` into `legal-year-data.json`, and `build.py` fills `legal-year.tpl.html` with it.
- `src/seventeen/` holds the page behind Seventeen Countries, One at a Time: `prep.py` reads, from local clones of the seventeen country repositories, each page’s `visualisations/README.en.md` and `visualisations/src/.build/data.json` and writes `seventeen-data.json`; `build.py` fills `seventeen.tpl.html` with it; `stills.cjs` renders the page’s stills.
- `src/law-drawn/` holds the scripts and data behind the Law, Drawn and Life of a Provision pages (`pass.py`, `analyse*.py`, then `build*.py` and `patch*.py`), and `src/law-drawn/romania/` those behind the two Romania pages (`part*_data.py` and `page2_data.py` write the JSON; `build_ro.py` and `build_page2.py` assemble the pages). The Romania scripts read a checkout of `romania-law` in `tip/` beside them. Intermediate files over 1 MB (such as `lives.json`) are not kept; rerun the analysis scripts to recreate them.

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
4. `compose.py` assembles `pages/law-in-motion.html` from `motion_template.html`, `part_new_figs.html`, `part_new_js.js` and `agenda.html`.
5. `node shot_el.cjs <playwright path> pages/law-in-motion.html <figure ids>` screenshots charts for checking.
6. `node stills.mjs` renders a still of every chart in `pages/` into `../stills/` and lists them in `figures.json`.
7. `python -X utf8 categories.py` cuts the full pages into the category pages (at most 20 charts each, as set in `categories.json`) and writes each category's README and the table above. A chart that is in no category, or in two, stops it.

Every caption number is checked against the analysis output before a rebuild is kept. The Constitute topic tags used for the bridge answer key come from `constitute_parse.py` and the Comparative Constitutions Project.
