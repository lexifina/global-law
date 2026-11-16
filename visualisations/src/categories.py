"""The category pages: cuts the full pages in src/pages/ into pages of at most 20 charts, one folder per category
(categories.json), and writes each category's README and the category list in the folder README.

    python -X utf8 categories.py          (from visualisations/src/, after the pages are built and stills.mjs has run)

A category page is its full page with the other charts hidden once the page has drawn them, so every chart keeps the
code and data it was built with. src/figures.json (written by stills.mjs) gives each chart's id, title and still.
"""
import json, re
from pathlib import Path

SRC = Path(__file__).resolve().parent
VIZ = SRC.parent
CAT = json.loads((SRC / "categories.json").read_text(encoding="utf-8"))
FIGS = json.loads((SRC / "figures.json").read_text(encoding="utf-8"))
MAX = CAT["max_per_page"]
BEGIN, END = "<!-- categories:begin -->", "<!-- categories:end -->"


def keep_script(keep, cat, page):
    banner = (f'<a href="../README.md">Visualisations</a> &rsaquo; <a href="README.md">{cat["title"]}</a> &rsaquo; {page["title"]}')
    return ("<script>(function(){var KEEP=" + json.dumps(keep) + ";"
            "function cut(){var fs=document.querySelectorAll('figure');for(var i=0;i<fs.length;i++){var k=fs[i].id||('#'+i);"
            "if(KEEP&&KEEP.indexOf(k)<0)fs[i].style.display='none';}"
            "if(KEEP)document.querySelectorAll('.divider,h2.part').forEach(function(e){e.style.display='none'});"
            "document.querySelectorAll('nav.tabs,#agenda').forEach(function(e){e.style.display='none'});"
            "if(!document.getElementById('cat-banner')){var b=document.createElement('div');b.id='cat-banner';"
            "b.style.cssText='font:13px/1.5 system-ui,sans-serif;padding:8px 16px;border-bottom:1px solid rgba(128,128,128,.3)';"
            "b.innerHTML=" + json.dumps(banner) + ";document.body.insertBefore(b,document.body.firstChild);}}"
            "window.addEventListener('load',function(){cut();setTimeout(cut,800);setTimeout(cut,2500);});})();</script>")


def figs_of(page):
    fs = FIGS[page["from"]]
    if page["keep"] == "all":
        return fs
    by = {f["id"]: f for f in fs}
    missing = [k for k in page["keep"] if k not in by]
    if missing:
        raise SystemExit(f"{page['file']}: no figure {missing} in {page['from']}")
    return [by[k] for k in page["keep"]]


rows, seen = [], {}
for cat in CAT["categories"]:
    d = VIZ / cat["dir"]
    d.mkdir(exist_ok=True)
    md = [f"# {cat['title']}", "", f"[Visualisations](../README.md) · {cat['about']}", "",
          "Open a page in a browser; each is one file with its data inside, and loads only its fonts and the d3 library from the web.", ""]
    n_cat = 0
    for page in cat["pages"]:
        fs = figs_of(page)
        if len(fs) > MAX:
            raise SystemExit(f"{page['file']}: {len(fs)} charts, more than {MAX}")
        for f in fs:
            seen.setdefault((page["from"], f["id"] or f["title"]), []).append(page["file"])
        html = (SRC / "pages" / page["from"]).read_text(encoding="utf-8")
        keep = None if page["keep"] == "all" else page["keep"]
        script = keep_script(keep, cat, page)
        html = html.replace("</body>", script + "</body>", 1) if "</body>" in html else html + script
        (d / page["file"]).write_text(html, encoding="utf-8", newline="\n")
        n_cat += len(fs)
        md += [f"## {page['title']} ([`{page['file']}`]({page['file']}), {len(fs)} charts)", ""]
        for f in fs:
            md += [f"![{f['title'].replace('[', '').replace(']', '')}](../stills/{f['still']})", ""] if f.get("still") else [f"- {f['title']}", ""]
    (d / "README.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    rows.append((cat, n_cat))

total = sum(len(v) for v in FIGS.values())
dupes = {k: v for k, v in seen.items() if len(v) > 1}
if len(seen) != total or dupes:
    raise SystemExit(f"{len(seen)} of {total} charts placed; twice: {dupes}")

lines = [BEGIN, "", "| Category | Pages | Charts |", "| --- | --- | ---: |"]
for cat, n in rows:
    pages = ", ".join(f"[{p['title']}]({cat['dir']}/{p['file']})" for p in cat["pages"])
    lines.append(f"| [{cat['title']}]({cat['dir']}/README.md): {cat['about']} | {pages} | {n} |")
lines += ["", END]
readme = VIZ / "README.md"
t = readme.read_text(encoding="utf-8")
t = t[:t.index(BEGIN)] + "\n".join(lines) + t[t.index(END) + len(END):]
readme.write_text(t, encoding="utf-8", newline="\n")
print(f"{len(rows)} categories, {sum(len(c['pages']) for c in CAT['categories'])} pages, {total} charts")
