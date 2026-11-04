"""page2_data.json + page2 pieces -> the-romanian-record.html (page body, as the artifact pages are written), plus a standalone copy with a document wrapper."""
import json
from pathlib import Path

HERE = Path(__file__).parent
T = (HERE / "template_ro.html").read_text(encoding="utf-8").split("\n")
head = "\n".join(T[:65]).replace("<title>Romanian Law, Drawn</title>", "<title>The Romanian Record</title>")
helpers = "\n".join(T[157:167])
data = json.dumps(json.loads((HERE / "page2_data.json").read_text(encoding="utf-8")), ensure_ascii=False, separators=(",", ":")).replace("</", r"<\/")
page = f"""{head}

<main>
{(HERE / "page2_header.html").read_text(encoding="utf-8")}
{(HERE / "page2_figs.html").read_text(encoding="utf-8")}
<footer>
  <p>Data: the public history of <a href="https://github.com/lexifina/romania-law">lexifina/romania-law</a> on 3 November 2026 (37,819 commits, 18,825 acts) and its data tables, which rebuild the Ministry of Justice's legislative portal. The corpus is still growing, so counts of acts in it are lower bounds. A companion page, Romanian Law, Drawn, holds 26 more charts.</p>
</footer>
</main>
<div id="tip" role="status" aria-live="polite"></div>
<script>
const DATA = {data};
{helpers}
{(HERE / "page2.js").read_text(encoding="utf-8")}
</script>
"""
(HERE / "the-romanian-record.html").write_text(page, encoding="utf-8", newline="\n")
wrap = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>\n'
        + page + "\n</body></html>\n")
dst = HERE.parents[2] / "the-romanian-record.html"  # visualisations/
dst.write_text(wrap, encoding="utf-8", newline="\n")
print(HERE / "the-romanian-record.html", len(page), "|", dst, len(wrap))
