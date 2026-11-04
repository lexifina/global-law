"""data.json + Spain's amending acts -> life-of-a-provision.html (template.html with the data inlined)."""
import json, subprocess
from pathlib import Path

HERE = Path(__file__).parent
d = json.loads((HERE / "data.json").read_text(encoding="utf-8"))
log = subprocess.run(["git", "-C", str(Path.home() / "Documents/spain-law"), "log", "--date=short",
                      "--format=%ad\x1f%an\x1f%(trailers:key=Laws-changed,valueonly,separator=)\x1f%s"],
                     capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
pts = []
for l in log.splitlines():
    dd, an, n, s = l.split("\x1f")
    if not n.strip() or "texto inicial" in s or dd < "1979" or int(n) < 2: continue
    k = ("Other" if an.startswith("Sentencia") or s.startswith("Sentencia") else "Decree-law" if "Decreto-ley" in s
         else "Other" if "Decreto Legislativo" in s else "Law" if s.startswith("Ley ") else "Royal decree" if s.startswith("Real Decreto") else "Other")
    pts.append([dd, int(n), k, s.split(":")[0][:90]])
d["omnibus"]["pts"] = pts
d["omnibus"].pop("acts", None)
t = (HERE / "template.html").read_text(encoding="utf-8")
(HERE / "life-of-a-provision.html").write_text(t.replace("__DATA__", json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")),
                                               encoding="utf-8", newline="\n")
print(len(pts), "Spanish acts;", (HERE / "life-of-a-provision.html").stat().st_size, "bytes")
