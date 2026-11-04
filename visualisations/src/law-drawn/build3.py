"""data3.json + growth.json + copy.json -> DATA3, merged with section3.html/js into law-drawn.html (part two of the page)."""
import json, re, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
d3 = json.loads((HERE / "data3.json").read_text(encoding="utf-8"))
d3["growth"] = json.loads((HERE / "growth.json").read_text(encoding="utf-8"))
K = json.loads((HERE / "copy.json").read_text(encoding="utf-8"))


def plain(s):
    return "".join(ch for ch in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(ch))


# Each shared article gets the template family it belongs to, from its own wording
THEMES = [("Borrowing from the province", r"leasing|reprogramac|fondo especial|asistencia[s]? financiera|emergencia|674/20|800/20|prestamo|banco de la provincia"
                                          r"|programa provincial de desarrollo|instituto de la vivienda|aporte financiero|coparticipacion"),
          ("Municipal tax codes", r"ordenanza fiscal|impositiva|contribuyente|gravamen|tasa |determinativa|repeticion|ingresos brutos|derechos de construccion|declaracion jurada"),
          ("Town charters (Brazil)", r"$^"),
          ("Commune rules (Switzerland)", r"$^")]
theme_of = {}
for s in K["shared"]:
    t = plain(s["text"] + " " + " ".join(s.get("titles", [])))
    th = next((name for name, rx in THEMES if re.search(rx, t)), "Other")
    if th == "Other" and all(c.startswith("brazil-") for c in s["cities"]): th = "Town charters (Brazil)"
    if th == "Other" and all(c.startswith("switzerland-") for c in s["cities"]): th = "Commune rules (Switzerland)"
    theme_of[s["h"]] = th
pairs = defaultdict(Counter)
for s in K["shared"]:
    cs = s["cities"]
    for i, a in enumerate(cs):
        for b in cs[i + 1:]: pairs[(a, b)][theme_of[s["h"]]] += 1
shared_by = Counter(c for s in K["shared"] for c in s["cities"])
cities = K["cities"]
GROUP = {"argentina": "Argentina", "brazil": "Brazil", "switzerland": "Switzerland", "mexico": "Mexico"}
nodes = [{"id": c, "name": cities[c]["name"], "group": GROUP.get(cities[c]["country"], cities[c]["country"]), "shared": n} for c, n in shared_by.items()]
links = [[a, b, sum(t.values()), t.most_common(1)[0][0]] for (a, b), t in pairs.items()]
by_theme = Counter(theme_of.values())
towns_theme = {th: len({c for s in K["shared"] if theme_of[s["h"]] == th for c in s["cities"]}) for th in by_theme}
d3["copy"] = {"nodes": nodes, "links": links, "themes": [t for t, _ in THEMES] + ["Other"], "labelMin": sorted((n["shared"] for n in nodes), reverse=True)[min(14, len(nodes) - 1)]}
print("nodes", len(nodes), "links", len(links), "shared articles", len(K["shared"]), dict(by_theme))
print("towns per theme", towns_theme)
print("by country", Counter(n["group"] for n in nodes))
print("most connected", sorted(((n["shared"], n["name"]) for n in nodes), reverse=True)[:8])
top = max(K["shared"], key=lambda s: len(s["cities"]))
print("widest article", len(top["cities"]), "towns", theme_of[top["h"]], top["text"][:200])
yrs = Counter(dt[:4] for s in K["shared"] if theme_of[s["h"]] == "Borrowing from the province" for dt in s["dates"])
print("borrowing years", sorted(yrs.items()))

DATA3 = json.dumps(d3, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
page = HERE / "law-drawn.html"
t = page.read_text(encoding="utf-8")
sec, js = (HERE / "section3.html").read_text(encoding="utf-8"), (HERE / "section3.js").read_text(encoding="utf-8")
# Replace an earlier part two if this script has run before, so the page can be rebuilt
t = re.sub(r"\n<!-- part2:begin -->.*<!-- part2:end -->\n", "\n", t, flags=re.S)
t = re.sub(r"\n<script id=\"part2\">.*?</script>\n", "\n", t, flags=re.S)
t = t.replace("<footer>", f"<!-- part2:begin -->{sec}<!-- part2:end -->\n\n<footer>", 1)
t = t.replace("</body>", f'<script id="part2">\nconst DATA3 = {DATA3};\n{js}\n</script>\n</body>', 1)
page.write_text(t, encoding="utf-8", newline="\n")
print("law-drawn.html", page.stat().st_size, "bytes")
