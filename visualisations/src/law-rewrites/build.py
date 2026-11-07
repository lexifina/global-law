"""rw.tpl.html + rw-data.json + ../geo/countries-50m.json -> ../../law-rewrites-and-ages.html"""
from pathlib import Path

here = Path(__file__).parent
page = (here / "rw.tpl.html").read_text(encoding="utf-8")
page = page.replace("__DATA__", (here / "rw-data.json").read_text(encoding="utf-8").strip(), 1)
page = page.replace("__ATLAS__", (here.parent / "geo" / "countries-50m.json").read_text(encoding="utf-8").strip(), 1)
(here.parent.parent / "law-rewrites-and-ages.html").write_text(page, encoding="utf-8", newline="\n")
