"""roses.tpl.html + roses-data.json + roses2-data.json -> ../../law-roses.html"""
from pathlib import Path

here = Path(__file__).parent
page = (here / "roses.tpl.html").read_text(encoding="utf-8")
page = page.replace("__DATA__", (here / "roses-data.json").read_text(encoding="utf-8").strip(), 1)
page = page.replace("__DATA2__", (here / "roses2-data.json").read_text(encoding="utf-8").strip(), 1)
(here.parent.parent / "law-roses.html").write_text(page, encoding="utf-8", newline="\n")
