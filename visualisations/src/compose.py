"""Compose Law in Motion: findings tab (refreshed + four new figures) and the research agenda tab -> law-in-motion.html"""
import json, re
from pathlib import Path

T = Path("motion_template.html").read_text(encoding="utf-8")
A = Path("agenda.html").read_text(encoding="utf-8")
NEWF = Path("part_new_figs.html").read_text(encoding="utf-8")
NEWJS = Path("part_new_js.js").read_text(encoding="utf-8")
GLOBF = Path("part_global_figs.html").read_text(encoding="utf-8")
GLOBJS = Path("part_global_js.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r5.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r5.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r6.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r6.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r6b.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r6b.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r7.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r7.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r8.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r8.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r9.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r9.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r10.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r10.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r11.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r11.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r12.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r12.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r13.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r13.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r14.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r14.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r15.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r15.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r16.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r16.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r17.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r17.js").read_text(encoding="utf-8")
GLOBF += Path("part_global_figs_r18.html").read_text(encoding="utf-8")
GLOBJS += Path("part_global_js_r18.js").read_text(encoding="utf-8")


def sub(s, a, b, count=1):
    assert a in s, a[:80]
    return s.replace(a, b, count)


# Refreshed German numbers (history now runs to the 69th amendment, 2025)
T = sub(T, "<h2>The Basic Law has doubled in length, mostly in six afternoons</h2>", "<h2>The Basic Law has doubled in length, mostly in six afternoons</h2>")
T = sub(T, "Words in force, amendment by amendment. Of the 64 amending laws, six account for more than half of everything added.",
        "Words in force, amendment by amendment, up to the 69th amendment in 2025. Of 71 amending commits, six account for more than half of everything added.")
T = sub(T, "It now carries the debt brake in 293.", "It now carries the debt brake, reformed again in 2025, in 392.")
T = sub(T, "The Bundestag's vote on each of the 55 amendments with a recorded tally.", "The Bundestag's vote on each of the 57 amendments with a recorded tally.")
T = sub(T, "Bigger reforms draw more opposition: the 2006 federalism reform and the 2009 debt brake are among the five lowest.",
        "Bigger reforms draw more opposition. The 2006 federalism reform, the 2009 debt brake and its 2025 reform are among the five lowest.")
T = sub(T, "Unterzeichnet trailers on 64 amending commits", "Unterzeichnet trailers on 71 amending commits")
T = sub(T, '"words in the German Basic Law, 1949 to its last amendment in 2017"', '"words in the German Basic Law, 1949 to its 69th amendment in 2025"')
T = sub(T, "Word count of artikel/*.md at each commit in lexifina/grundgesetz", "Word count of artikel/*.md at each commit in lexifina/grundgesetz (germany-law)")
T = sub(T, "const x = d3.scaleUtc([P(\"1949-01-01\"), P(\"2019-01-01\")], [m.l, W - m.r]);\n  const y = d3.scaleLinear([0, 24000], [H - m.b, m.t]);",
        "const x = d3.scaleUtc([P(\"1949-01-01\"), P(\"2027-01-01\")], [m.l, W - m.r]);\n  const y = d3.scaleLinear([0, 30000], [H - m.b, m.t]);")
T = T.replace('t: P("2019-01-01") }', 't: P("2027-01-01") }')
T = sub(T, "const PLACE = { 7: [-46, true], 17: [52, true], 21: [-58, true], 42: [-50, false], 52: [-78, false], 57: [52, false] };",
        "const PLACE = { 7: [-46, true], 17: [52, true], 42: [-50, false], 52: [-64, false], 57: [52, false], 62: [-34, false] };")
T = sub(T, "const NAMES = { 4: \"1954 defence\",", "const NAMES = { 69: \"2025 debt-brake reform\", 4: \"1954 defence\",")
T = sub(T, "const VPLACE = { 4: [10, 0, \"start\"], 17: [10, 0, \"start\"], 45: [10, 0, \"start\"], 52: [-10, -14, \"end\"], 57: [-10, 16, \"end\"] };",
        "const VPLACE = { 4: [10, 0, \"start\"], 17: [10, 0, \"start\"], 45: [10, 0, \"start\"], 52: [-10, -14, \"end\"], 57: [-10, 16, \"end\"], 69: [-10, 0, \"end\"] };")
T = sub(T, "const V = S.votes.map(v => ({ ...v, t: P(v.date) })), W = 960, H = 340, m = { l: 52, r: 20, t: 20, b: 30 };\n  const svg = d3.select(\"#f-votes\").attr(\"viewBox\", `0 0 ${W} ${H}`);\n  const x = d3.scaleUtc([P(\"1949-01-01\"), P(\"2019-01-01\")], [m.l, W - m.r]);",
        "const V = S.votes.map(v => ({ ...v, t: P(v.date) })), W = 960, H = 340, m = { l: 52, r: 20, t: 20, b: 30 };\n  const svg = d3.select(\"#f-votes\").attr(\"viewBox\", `0 0 ${W} ${H}`);\n  const x = d3.scaleUtc([P(\"1949-01-01\"), P(\"2027-01-01\")], [m.l, W - m.r]);")
T = sub(T, "const x = d3.scaleLinear([1949, 2019], [m.l, W - m.r]);", "const x = d3.scaleLinear([1949, 2027], [m.l, W - m.r]);")
T = sub(T, "The US Code history begins with the 2017 edition and the Swiss history with 2019, so earlier changes there are not shown.",
        "The US Code history begins with the 2017 edition and the Swiss history with 2019, so earlier changes there are not shown. The other repositories were still being built during the run, so later rebuilds may shift a figure slightly.")

T = sub(T, "German constitutional amendments take about two months.", "German constitutional amendments take about seven weeks.")
# New figure copy fixes found while checking the numbers
NEWF = sub(NEWF, " German text written by amendment changes faster than the 1949 original, because the federal–state finance articles are rewritten again and again.",
           " The German curve stops at 76 years because the Basic Law is that old. The finance and federalism articles account for most of the German rewrites.")
NEWF = sub(NEWF, "<span class=\"eyebrow\">Four jurisdictions, three languages</span>", "<span class=\"eyebrow\">Five jurisdictions, three languages</span>")
NEWF = sub(NEWF, "Median words per sentence, comparing a provision's first wording with wording written later by amendment. <b>In every system, amendments write longer sentences</b>: a quarter longer in Germany, half again in Luxembourg, and from 55 to 69 words in a US Code sentence.",
           "Median words per sentence in the founding text against every wording written later by amendment. <b>In every system, amendments write longer sentences</b>: a quarter longer in Germany, a third in Switzerland, from 55 to 64 words in the US Code, and 7–10% in the constitutions of Liechtenstein and Luxembourg.")
NEWF = sub(NEWF, "For the US, \"original\" means sections as they stood in the 2017 edition.", "Founding text means the constitution as adopted. For Switzerland and the US it means the text at the start of our history (2019 and the 2017 edition).")

# Agenda pieces
astyle = A[A.index("<style>") + 7:A.index("</style>")]
astyle = astyle[astyle.index(".plate {"):]  # component rules only; base rules come from the findings page
astyle = astyle.replace("main { max-width: 1040px;", "/* main */ .unused {")
amain = A[A.index("<main>") + 6:A.index("</main>")]
amain = re.sub(r"<header>.*?</header>", """<header class="tabhead"><span class="eyebrow">Literature review · 28 Oct 2026</span><h2 class="big">What to do with a holistic dataset of law</h2>
    <p class="lede">Thirteen lines of research that measure or picture legal change, what each one did, and what we could do better. Most published work studies one country, one level or one snapshot. Our dataset has every provision, in every jurisdiction, at every in-force date, with the law that changed it. That makes several long-standing questions answerable for the first time. Four of them are already run on the Findings tab: wording survival, readability of amendments, the temporary-law detector and constitutional growth.</p></header>""", amain, flags=re.S)
ajs = A[A.rindex("<script>") + 8:A.rindex("</script>")]
ajs = ajs.replace('id="${s.id}"', 'id="a-${s.id}"').replace('href="#${id}"', 'href="#a-${id}"')

# Tokens the agenda uses
for blockstart in [":root {\n  --bg: #f5f6f8;", "  --bg: #11151c; --plate: #181e27;"]:
    pass
T = sub(T, "--de: #b5801a; --ch: #c23f38; --gb: #24807c; --us: #3a5fbf; --hi: #c23f38;",
        "--de: #b5801a; --ch: #c23f38; --gb: #24807c; --us: #3a5fbf; --hi: #c23f38; --accent: #3a5fbf; --now: #24807c; --later: #b5801a; --c5: #6b5bd2; --c6: #6f8a2a; --c7: #b8447a;")
T = T.replace("--de: #e0aa45; --ch: #ec6b62; --gb: #4fb6b0; --us: #7d9cf0; --hi: #f07c73; color-scheme: dark }",
              "--de: #e0aa45; --ch: #ec6b62; --gb: #4fb6b0; --us: #7d9cf0; --hi: #f07c73; --accent: #7d9cf0; --now: #4fb6b0; --later: #e0aa45; --c5: #a99cf5; --c6: #a8c25a; --c7: #e47bab; color-scheme: dark }")
assert T.count("--accent: #7d9cf0") == 2

TABCSS = """
[hidden] { display: none !important; }
.tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--rule); }
.tabs a { font: 500 14px var(--body); color: var(--muted); text-decoration: none; padding: 10px 14px; border-bottom: 2px solid transparent; margin-bottom: -1px; min-height: 40px; display: inline-flex; align-items: center; }
.tabs a[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--ink); }
.panel { display: grid; gap: 28px; }
.divider { display: grid; gap: 8px; padding-top: 12px; border-top: 2px solid var(--ink); max-width: 76ch; }
.divider p { color: var(--muted); font-size: 14.5px; }
h2.big { font: 600 1.7rem/1.15 var(--display); }
.tabhead { display: grid; gap: 12px; max-width: 68ch; }
"""
T = T.replace("</style>", TABCSS + astyle + "\n</style>", 1)

# Structure: header, tabs, findings panel, agenda panel
T = sub(T, "  </header>\n\n  <div class=\"facts\" id=\"facts\"></div>",
        "  </header>\n\n  <nav class=\"tabs\" role=\"tablist\" aria-label=\"Sections\"><a href=\"#findings\" role=\"tab\" id=\"tab-findings\" aria-selected=\"true\" aria-controls=\"findings\">Findings</a><a href=\"#agenda\" role=\"tab\" id=\"tab-agenda\" aria-selected=\"false\" aria-controls=\"agenda\">Research agenda</a></nav>\n\n  <section class=\"panel\" id=\"findings\" role=\"tabpanel\" aria-labelledby=\"tab-findings\">\n  <div class=\"facts\" id=\"facts\"></div>")
T = sub(T, "  <footer>", GLOBF + "\n" + NEWF + "\n  <footer>")
T = sub(T, '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>',
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>\n<script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>')
T = sub(T, "  </footer>\n</main>", "  </footer>\n  </section>\n\n  <section class=\"panel\" id=\"agenda\" role=\"tabpanel\" aria-labelledby=\"tab-agenda\" hidden>" + amain + "</section>\n</main>")

ROUTE = """
// Tabs: #agenda (or any anchor inside it) shows the agenda; everything else shows the findings
function route() {
  const h = decodeURIComponent(location.hash.slice(1));
  const el = h && document.getElementById(h);
  const agenda = h === "agenda" || (el && el.closest("#agenda"));
  document.getElementById("findings").hidden = !!agenda;
  document.getElementById("agenda").hidden = !agenda;
  document.getElementById("tab-findings").setAttribute("aria-selected", String(!agenda));
  document.getElementById("tab-agenda").setAttribute("aria-selected", String(!!agenda));
  if (el && h !== "agenda" && h !== "findings") requestAnimationFrame(() => el.scrollIntoView({ block: "start" }));
}
window.addEventListener("hashchange", route);
route();
"""
j = T.rindex("</script>")
T = T[:j] + NEWJS + "\n" + GLOBJS + "\n" + ajs + ROUTE + "\n" + T[j:]

# Data
S = json.loads(Path("story_page.json").read_text(encoding="utf-8"))
a = json.loads(Path("analysis2.json").read_text(encoding="utf-8"))
K7 = [k for k in ("de", "sk", "lu", "li", "mc", "si", "ee", "fi", "hr", "gi", "dk", "kg", "it", "pt", "mg", "rw") if k in a["const_growth"]]
S["const_growth"] = {k: a["const_growth"][k] for k in K7}
S["survival_const"] = {k: {kk: a["survival_const"][k][kk] for kk in ("curve", "n", "events", "median_days", "max_days")} for k in K7 if k in a["survival_const"]}
S["read_groups"] = json.loads(Path("read_groups.json").read_text(encoding="utf-8"))
S["episodes"] = json.loads(Path("episodes.json").read_text(encoding="utf-8"))
b3 = json.loads(Path("analysis3.json").read_text(encoding="utf-8"))
S["calendar"] = b3["calendar"]; S["malta"] = {"months": b3["malta"]["months"], "n": b3["malta"]["n"]}
S["elect"] = a["elect"]
S["obligations"] = json.loads(Path("analysis4.json").read_text(encoding="utf-8"))
S["malta_hot"] = json.loads(Path("analysis5.json").read_text(encoding="utf-8"))
S["hubs"] = json.loads(Path("analysis6.json").read_text(encoding="utf-8"))
S["r4"] = json.loads(Path("analysis7.json").read_text(encoding="utf-8"))
S["readiness"] = json.loads(Path("analysis8.json").read_text(encoding="utf-8"))
S["r5"] = json.loads(Path("analysis9.json").read_text(encoding="utf-8"))
S["r10"] = json.loads(Path("analysis10.json").read_text(encoding="utf-8"))
S["a11"] = json.loads(Path("analysis11.json").read_text(encoding="utf-8"))
for v in S["r5"]["lag"].values(): v.pop("sample", None)
S["atlas"] = json.loads(Path("geo/countries-50m.json").read_text(encoding="utf-8"))
S["round"] = json.loads(Path("round.json").read_text(encoding="utf-8"))
for k in S["survival_const"]:
    c = S["survival_const"][k]["curve"]
    S["survival_const"][k]["curve"] = [[t, round(v, 4)] for t, v in c]
print("episodes", len(S["episodes"]), "const", K7)
data = json.dumps(S, ensure_ascii=False).replace("</", "<" + "\\" + "/")
html = T.replace("__DATA__", data)
Path(".build/law-in-motion.html").write_text(html, encoding="utf-8")
OUT = Path.home() / "Documents" / "lexifina" / "scripts" / "global-law" / "repo" / "visualisations"; OUT.mkdir(exist_ok=True)
STANDALONE = ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
              '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n' + html + "\n</html>\n")
(OUT / "law-in-motion.html").write_text(STANDALONE, encoding="utf-8")
i = html.rfind("<script>"); Path(".build/check.js").write_text(html[i + 8:html.rfind("</script>")], encoding="utf-8")
print("ok", len(html))
