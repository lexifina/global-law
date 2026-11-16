"""visualisations/COUNTRIES.md: every country repository's own visualisations/ folder, and whether it holds a chart page yet.

    python -X utf8 countries_list.py          (from visualisations/src/; reads GitHub with the gh command line)

A country is one of global-law's top-level jurisdiction folders with a lexifina/<folder>-law repository. Its folder holds
a page when it has an .html file; a README alone is either a placeholder (it starts "TODO.") or describes a page that is
not published yet.
"""
import base64, json, subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

VIZ = Path(__file__).resolve().parent.parent
GL = VIZ.parent
NAMES = {"cote-divoire": "Côte d'Ivoire", "dr-congo": "DR Congo", "republic-of-congo": "Republic of the Congo",
         "bosnia-and-herzegovina": "Bosnia and Herzegovina", "guinea-bissau": "Guinea-Bissau", "timor-leste": "Timor-Leste",
         "sao-tome-and-principe": "São Tomé and Príncipe", "aland": "Åland", "eurasian-economic-union": "Eurasian Economic Union",
         "european-union": "European Union", "united-arab-emirates": "United Arab Emirates", "united-kingdom": "United Kingdom",
         "united-states": "United States", "vatican-city": "Vatican City", "isle-of-man": "Isle of Man"}
SMALL = {"and", "of", "the"}


def gh(path):
    r = subprocess.run(["gh", "api", path], capture_output=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def name(c):
    return NAMES.get(c) or " ".join(w if w in SMALL and i else w.capitalize() for i, w in enumerate(c.split("-")))


repos = {r["name"] for page in range(1, 20) for r in (gh(f"orgs/lexifina/repos?per_page=100&page={page}") or [])}
folders = sorted(p.name for p in GL.iterdir() if p.is_dir() and (p / "jurisdiction.json").exists()) if (GL / "README.md").exists() else []
if not folders:  # a sparse checkout: read the tree's top level from GitHub
    folders = sorted(x["name"] for x in gh("repos/lexifina/global-law/contents?ref=main") if x["type"] == "dir")
countries = [c for c in folders if f"{c}-law" in repos]


def status(c):
    items = gh(f"repos/lexifina/{c}-law/contents/visualisations?ref=main") or []
    pages = [x["name"] for x in items if x["name"].endswith(".html")]
    if pages:
        return c, "page", pages
    if not items:
        return c, "none", []
    readme = gh(f"repos/lexifina/{c}-law/contents/visualisations/README.md?ref=main")
    text = base64.b64decode(readme["content"]).decode("utf-8") if readme else ""
    return c, ("placeholder" if "TODO." in text else "described"), []


with ThreadPoolExecutor(8) as ex:
    rows = list(ex.map(status, countries))
by = {k: [r for r in rows if r[1] == k] for k in ("page", "described", "placeholder", "none")}
link = lambda c, f="": f"https://github.com/lexifina/{c}-law/tree/main/visualisations{f}"
out = ["# Countries", "", "[Visualisations](README.md) · Each country repository has a `visualisations/` folder for charts drawn from "
       "that repository alone. This page lists which already hold a chart page and which are placeholders for now. The charts "
       "drawn across countries are in this folder's [categories](README.md#categories).", "",
       f"Of {len(rows)} country repositories, {len(by['page'])} have a chart page, {len(by['described'])} have their page "
       f"described but not yet published, and {len(by['placeholder'])} are placeholders.", ""]
out += [f"## With a chart page ({len(by['page'])})", "", "| Country | Page |", "| --- | --- |"]
for c, _, pages in by["page"]:
    out.append(f"| {name(c)} | " + ", ".join(f"[{p}]({link(c, '/' + p)})" for p in pages) + " |")
out += ["", f"## Described, page not yet published ({len(by['described'])})", "",
        "The folder's README describes the page; the page itself is still to be pushed.", "",
        ", ".join(f"[{name(c)}]({link(c)})" for c, _, _ in by["described"]), "",
        f"## Placeholders ({len(by['placeholder'])})", "", "The folder holds a README that says no charts have been drawn yet.", "",
        ", ".join(f"[{name(c)}]({link(c)})" for c, _, _ in by["placeholder"]), ""]
if by["none"]:
    out += [f"## No folder yet ({len(by['none'])})", "", ", ".join(name(c) for c, _, _ in by["none"]), ""]
out += [f"Read from GitHub on {date.today():%d %B %Y} by `src/countries_list.py`.", ""]
(VIZ / "COUNTRIES.md").write_text("\n".join(out), encoding="utf-8", newline="\n")
print({k: len(v) for k, v in by.items()})
