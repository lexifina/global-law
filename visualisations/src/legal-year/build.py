"""legal-year.tpl.html + legal-year-data.json -> ../../legal-year-variants.html"""
from pathlib import Path

here = Path(__file__).parent
page = (here / "legal-year.tpl.html").read_text(encoding="utf-8")
page = page.replace("__DATA__", (here / "legal-year-data.json").read_text(encoding="utf-8").strip(), 1)
(here.parent.parent / "legal-year-variants.html").write_text(page, encoding="utf-8", newline="\n")
