# The web app

A page for reading the law tree in a browser: a provision as in force on any date, the law that wrote each word, what
changed and when, and what each record holds. It runs from this clone, offline.

```sh
python3 tools/web.py                 # serves http://127.0.0.1:8765 and opens it
python3 tools/web.py --port 9000 --no-browser
```

It reads the corpora checked out in this clone; add a country with `python3 tools/countries.py add <country>`. The
country picker lists every corpus in `manifest.json` and gives that command for the ones not yet here.

## How it is built

- `tools/web.py` is a standard-library HTTP server. It serves this folder and answers `POST /api/tool/<name>` with the
  structured answer of the MCP server's tool of that name (`tools/mcp_server.py`, `HANDLERS`), so the page and an AI
  client get the same answers, limits and refusals. `GET /api/corpora` lists the manifest's corpora and whether each is
  checked out.
- It changes nothing and makes no network calls. It listens on 127.0.0.1 only, answers only requests addressed to
  `127.0.0.1` or `localhost` (no other site's page can reach it through DNS), and sends a content security policy that
  lets the page load only its own files.
- The page is plain HTML, CSS and JavaScript modules, with no build step and no dependencies: `index.html`, `app.css`
  and `js/`:
  - `main.js`: the header and the routes (`#/`, `#/browse?path=`, `#/search?q=`, `#/read?path=&date=&mode=&b=`).
  - `reader.js`: the reader (timeline, word credit from `who_wrote`, what changed, compare dates, cite).
  - `views.js`: home, browse (`list_provisions`) and search (`find_provision`).
  - `picker.js`: the country picker.
  - `text.js`: lays out law text and diffs it word by word; law text is only ever set as text, never as markup.
  - `i18n.js`, `api.js`, `util.js`.

## Adding a language

The interface's words are in `i18n/`, one JSON file a language. To add one:

1. Copy `i18n/en.json` to `i18n/<code>.json`, where `<code>` is a BCP 47 language tag (`de`, `fr`, `pt-BR`).
2. Translate the values. Keep the keys, and keep each `{placeholder}` as it is. A value written as
   `{"one": "...", "other": "..."}` is a plural; give the forms your language uses (`zero`, `one`, `two`, `few`,
   `many`, `other`, as `Intl.PluralRules` names them), and always `other`.
3. Add the language to `i18n/index.json`: `{"code": "<code>", "name": "<its name in that language>"}`. For a language
   written right to left, add `"dir": "rtl"`.
4. Run `python -m unittest tests.test_web`: it checks that every language has every key and the same placeholders.

A key missing from a language shows the English text. Dates, numbers and country names need no translation: the
browser's `Intl` writes them in the chosen language. The page starts in the browser's language when it is listed, and
remembers the reader's choice.

What is not translated: the law text (always in its publisher's language) and the notes the engine writes on each
record's limits, which are in English and marked `EN`.
