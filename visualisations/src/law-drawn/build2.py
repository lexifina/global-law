"""data2.json -> law-drawn.html (template2.html with the data inlined)."""
import json
from pathlib import Path

HERE = Path(__file__).parent
d = json.loads((HERE / "data2.json").read_text(encoding="utf-8"))
t = (HERE / "template2.html").read_text(encoding="utf-8")
out = HERE / "law-drawn.html"
out.write_text(t.replace("__DATA__", json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")), encoding="utf-8", newline="\n")
print(out.stat().st_size, "bytes")
