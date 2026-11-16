"""seventeen.tpl.html + seventeen-data.json -> ../pages/seventeen-countries-one-at-a-time.html"""
from pathlib import Path

here = Path(__file__).parent
page = (here / "seventeen.tpl.html").read_text(encoding="utf-8")
assert page.count("/*DATA*/null") == 1
page = page.replace("/*DATA*/null", (here / "seventeen-data.json").read_text(encoding="utf-8").strip(), 1)
(here.parent / "pages" / "seventeen-countries-one-at-a-time.html").write_text(page, encoding="utf-8", newline="\n")
print("seventeen-countries-one-at-a-time.html written")
