"""One local HTML page for the statute-record work (items 5-8, 10, 11, 17-20): what each piece found, its figure,
its Lean model and theorems, where the data and scripts live, and the full write-up drafts.

    python make_report.py ~/Documents/html-reports/us-code-uses.html
"""
import base64, html, json, os, re, sys
from pathlib import Path

U = Path(__file__).resolve().parent
LP = Path.home() / "Documents/global-law-lean/lean-proofs"
MEDIA = Path.home() / "lexweb-build/public/blog-media/formalizing-all-us-case-law-in-lean"
BLOG = "http://localhost:3100/blog/formalizing-all-us-case-law-in-lean"

WORK = [
    {
        "key": "overrides", "n": "10", "title": "Spotting congressional overrides",
        "lede": "Decisions followed by the first law to rewrite the exact words they cited, with evidence that Congress had the decision in mind.",
        "stats": [("6,069", "decision–law candidate pairs (Lean)"), ("20 / 24", "known Supreme Court overrides found, of those the record can reach"),
                  ("34", "overrides confirmed by reading"), ("19", "of them not on the published lists")],
        "fig": "overrides-congress.svg", "lean": ["Overrides", "RunOverrides"], "slide": "overrides",
        "files": ["overrides.tsv", "confirmed.tsv", "results.json", "recall.tsv", "per_congress.tsv", "audit", "gold", "scripts"],
        "tools": ["tools/caselaw/uses/overrides/"],
    },
    {
        "key": "amendments", "n": "5 + 7", "title": "Running amending instructions, and what a bill would touch",
        "lede": "Every amending instruction in the 812 public laws of 2013–2026 run against the Code; five pending bills dry-run.",
        "stats": [("50,010", "operations parsed"), ("76%", "carried out exactly as the record shows"),
                  ("69 / 86", "“could not be executed” notes Lean also flags"), ("≈440", "drafting errors that cannot be carried out (170–1,100)")],
        "fig": None, "lean": ["AmendmentCheck", "RunAmendmentCheck"], "slide": "amendments",
        "files": ["data/results.tsv", "out/summary.json", "out/olrc_xcheck.json", "out", "bills/summary.json", "bills/ops.json", "tools"],
        "tools": ["tools/caselaw/uses/amendments/"],
    },
    {
        "key": "xrefs", "n": "6", "title": "Checking cross-references",
        "lede": "Every explicit reference in every version of every section since 1995, resolved against the Code as it stood that day.",
        "stats": [("152,597", "references in force today"), ("3,278", "point at nothing (2.1%)"), ("≈2,200", "real errors (68% in a held-out audit)"),
                  ("181", "duplicate designations today")],
        "fig": "cross-references.svg", "lean": ["CrossRefs", "RunCrossRefs"], "slide": "cross-references",
        "files": ["summary.json", "dangling_today.tsv", "dangling_by_title.tsv", "dangling_episodes.tsv", "laws.tsv", "duplicates_today.tsv", "by_year.tsv", "audit"],
        "tools": ["tools/caselaw/usc_xrefs.py", "tools/caselaw/usc_xrefs_report.py", "tools/caselaw/usc_xrefs_figure.py"],
    },
    {
        "key": "recodification", "n": "8", "title": "Recodification checks",
        "lede": "Titles 36, 40, 41, 46, 51 and 54: every provision in force at the old locations, checked against the official disposition tables.",
        "stats": [("2,721", "old provisions checked"), ("1", "in no table row (40 U.S.C. 207b-2)"), ("1", "table typo caught by Lean (16 U.S.C. 458a)"),
                  ("1", "apparent silent drop (Glacier Bay fee cap)")],
        "fig": "recodification.svg", "lean": ["Recodification", "RunRecodification"], "slide": "recodification",
        "files": ["results", "data", "audit", "tools"], "tools": ["tools/caselaw/uses/recodification/"],
    },
    {
        "key": "watch", "n": "11", "title": "Watch lists",
        "lede": "Give it a list of citations or any document and a date; it reports every law that changed the words watched since, with a diff.",
        "stats": [("3–6 s", "for 100 sections since 2015"), ("8 / 22", "firearms provisions with an alert since 2015"),
                  ("4 / 49", "provisions of Texas v. United States changed by a law since"), ("0", "editions that raise an alert (proved)")],
        "fig": "watch.svg", "lean": ["Watch", "RunWatch"], "slide": "watch",
        "files": ["demo_opinion/watch.html", "demo_practice/firearms.html", "demo_practice/bankruptcy.html", "demo_top25", "timing/timing.md", "lists"],
        "tools": ["tools/caselaw/usc_watch.py"],
    },
    {
        "key": "visual", "n": "17–20", "title": "The Code since 1994, in one figure",
        "lede": "How fast it changes, how it grows, who wrote it, and what courts do after a rewrite.",
        "stats": [("13% → 2%", "sections changed per Congress, 1995–96 to 2023–24"), ("+66%", "words since 1994"),
                  ("41%", "of today’s words written by laws since 1995"), ("+28%", "citations after a rewrite (4% to 62%)")],
        "fig": "code-dynamics.svg", "lean": [], "slide": "code-dynamics",
        "files": ["p1_heat.tsv", "p2_complexity.tsv", "p3_credit.tsv", "p4_event.tsv", "p4_effect.json", "extract.py", "analyze.py", "figure.py"],
        "tools": ["tools/caselaw/uses/visual/"],
    },
]


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\w)", r"<i>\1</i>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md(text):
    """A small Markdown reader: headings, paragraphs, lists, tables, rules, comments."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out, para, lst, tbl = [], [], [], []

    def flush():
        nonlocal para, lst, tbl
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
        if lst:
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in lst) + "</ul>")
        if tbl:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl if not re.match(r"^\s*\|?\s*:?-{2,}", r)]
            if rows:
                h = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
                b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
                out.append(f'<div class="tw"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>')
        para, lst, tbl = [], [], []
    for line in text.splitlines():
        s = line.rstrip()
        if not s.strip():
            flush(); continue
        m = re.match(r"^(#{1,6})\s+(.*)", s)
        if m:
            flush(); lv = min(5, max(3, len(m.group(1)) + 1))
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>"); continue
        if s.strip() == "---":
            flush(); out.append("<hr>"); continue
        if s.lstrip().startswith("|"):
            if para or lst:
                flush()
            tbl.append(s); continue
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*)", s)
        if m:
            if para or tbl:
                flush()
            lst.append(m.group(1)); continue
        if lst and line.startswith("  "):
            lst[-1] += " " + s.strip(); continue
        if tbl:
            flush()
        para.append(s.strip())
    flush()
    return "\n".join(out)


def svg_uri(p):
    return "data:image/svg+xml;base64," + base64.b64encode(Path(p).read_bytes()).decode()


def theorems(mod):
    f = LP / "LegalProofs/USCaseLaw" / f"{mod}.lean"
    if not f.exists():
        return [], 0
    t = f.read_text(encoding="utf-8")
    return re.findall(r"^\s*(?:private\s+)?theorem\s+([^\s:(]+)", t, re.M), len(t.splitlines())


def link(p, label=None):
    p = Path(p)
    return f'<a href="{p.as_uri()}">{html.escape(label or p.name)}</a>' if p.exists() else f"<span class=missing>{html.escape(label or p.name)}</span>"


def main(out):
    nav = "".join(f'<a href="#{w["key"]}"><span>{w["n"]}</span>{html.escape(w["title"])}</a>' for w in WORK)
    rows = "".join(
        f'<tr><td class=num>{w["n"]}</td><td><a href="#{w["key"]}">{html.escape(w["title"])}</a></td>'
        f'<td>{html.escape(w["stats"][0][0])} {html.escape(w["stats"][0][1])}; {html.escape(w["stats"][1][0])} {html.escape(w["stats"][1][1])}</td>'
        f'<td>{", ".join(f"<code>{m}.lean</code>" for m in w["lean"] if not m.startswith("Run")) or "—"}</td>'
        f'<td>{link(U / w["key"], "uses/" + w["key"])}</td></tr>' for w in WORK)
    secs = []
    for w in WORK:
        d = U / w["key"]
        cards = "".join(f'<div class=card><div class=v>{html.escape(v)}</div><div class=l>{html.escape(l)}</div></div>' for v, l in w["stats"])
        fig = ""
        if w["fig"] and (MEDIA / w["fig"]).exists():
            fig = f'<figure><a href="{(MEDIA / w["fig"]).as_uri()}"><img src="{svg_uri(MEDIA / w["fig"])}" alt="{html.escape(w["title"])}"></a></figure>'
        lean = ""
        for m in w["lean"]:
            th, ln = theorems(m)
            f = LP / "LegalProofs/USCaseLaw" / f"{m}.lean"
            if m.startswith("Run"):
                lean += f'<p class=small>Runner: {link(f, f"LegalProofs/USCaseLaw/{m}.lean")} ({ln} lines)</p>'
            else:
                chips = "".join(f"<code>{html.escape(t)}</code>" for t in th)
                lean += (f'<p>{link(f, f"LegalProofs/USCaseLaw/{m}.lean")}: {ln} lines, {len(th)} theorems, no <code>sorry</code>.</p>'
                         f'<div class=chips>{chips}</div>')
        files = " · ".join(link(d / f, f) for f in w["files"])
        tools = " · ".join(link(LP / t, t) for t in w["tools"])
        blog = md((d / "BLOG.md").read_text(encoding="utf-8")) if (d / "BLOG.md").exists() else ""
        prog = md((d / "PROGRESS.md").read_text(encoding="utf-8")) if (d / "PROGRESS.md").exists() else ""
        secs.append(f'''
<section id="{w["key"]}">
  <div class=kicker>Item {w["n"]}</div>
  <h2>{html.escape(w["title"])}</h2>
  <p class=lede>{html.escape(w["lede"])}</p>
  <div class=cards>{cards}</div>
  {fig}
  <div class=grid>
    <div><h3>Lean</h3>{lean or "<p>No Lean model: this is measurement over the record.</p>"}</div>
    <div><h3>Where it lives</h3>
      <p>Work: {link(d, str(d))}</p>
      <p>Files: {files}</p>
      <p>Scripts (repo): {tools}</p>
      <p>Repo copy of results: {link(LP / "data/caselaw/statutes_usc/uses" / w["key"], "data/caselaw/statutes_usc/uses/" + w["key"])}</p>
      <p>In the post: <a href="{BLOG}#{w["slide"]}">section 7 slide</a></p>
    </div>
  </div>
  <details open><summary>Full write-up (draft)</summary><div class=md>{blog}</div></details>
  <details><summary>How it was run (PROGRESS.md)</summary><div class=md>{prog}</div></details>
</section>''')
    anat = MEDIA / "law-anatomy.svg"
    anat_html = (f'<section id="three"><div class=kicker>Context</div><h2>Three formalisms side by side</h2>'
                 f'<p class=lede>The tax code formalism of the earlier posts, the US Code models above, and the case-law model. '
                 f'They share no code.</p><figure><img src="{svg_uri(anat)}" alt="Three formalisms"></figure>'
                 f'<p class=small>Extractor {link(LP / "tools/LawAnatomy.lean", "tools/LawAnatomy.lean")}, figure '
                 f'{link(LP / "tools/caselaw/law_anatomy.py", "tools/caselaw/law_anatomy.py")}.</p></section>') if anat.exists() else ""
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>US Code uses</title>
<style>
:root{{--bg:#f6f3ee;--fg:#1b1d21;--mut:#5b5f66;--card:#fff;--bd:#e2dcd2;--acc:#c2410c;--code:#efe9df}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#0f1720;--fg:#e8ecf1;--mut:#9aa6b5;--card:#16212c;--bd:#26323f;--acc:#ff8a65;--code:#1d2a37}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 "IBM Plex Sans",system-ui,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:32px 16px 80px}}
header h1{{font-size:2rem;margin:0 0 .25rem}} header p{{color:var(--mut);margin:.25rem 0}}
nav{{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 28px}} nav a{{border:1px solid var(--bd);border-radius:999px;padding:6px 12px;color:var(--fg);text-decoration:none;font-size:.9rem;background:var(--card)}}
nav a span{{color:var(--acc);font-weight:600;margin-right:6px}}
table{{border-collapse:collapse;width:100%;font-size:.92rem}} th,td{{text-align:left;padding:8px 10px;border-top:1px solid var(--bd);vertical-align:top}} thead th{{border-top:0}}
.tw{{overflow-x:auto;margin:12px 0}} .num{{white-space:nowrap;color:var(--acc);font-weight:600}}
section{{margin-top:56px;padding-top:24px;border-top:1px solid var(--bd)}} .kicker{{font:600 .75rem/1 "JetBrains Mono",ui-monospace,monospace;letter-spacing:.08em;color:var(--acc);text-transform:uppercase}}
h2{{font-size:1.6rem;margin:.4rem 0}} h3{{font-size:1.05rem;margin:0 0 .5rem}} .lede{{color:var(--mut);font-size:1.05rem;margin:.25rem 0 1rem}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin:16px 0}}
.card{{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:12px 14px}} .card .v{{font-size:1.5rem;font-weight:600}} .card .l{{color:var(--mut);font-size:.85rem;line-height:1.35}}
figure{{margin:16px 0}} figure img{{width:100%;height:auto;border-radius:12px;display:block}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:16px 0}} @media (max-width:760px){{.grid{{grid-template-columns:1fr}}}}
.grid p{{margin:.3rem 0;overflow-wrap:anywhere}} .chips{{display:flex;flex-wrap:wrap;gap:4px}} code{{background:var(--code);border-radius:5px;padding:1px 5px;font:.82rem "JetBrains Mono",ui-monospace,monospace;overflow-wrap:anywhere}}
details{{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:10px 16px;margin:12px 0}} summary{{cursor:pointer;font-weight:600}}
.md{{max-width:760px}} .md h3,.md h4,.md h5{{margin:1.4rem 0 .4rem}} .md h3{{font-size:1.2rem}} .md h4{{font-size:1.05rem}} .md h5{{font-size:.95rem}} td code{{white-space:nowrap}} .small{{font-size:.88rem;color:var(--mut)}} a{{color:var(--acc)}} .missing{{color:var(--mut);text-decoration:line-through}}
</style></head><body><div class=wrap>
<header><h1>US Code uses: the six workstreams</h1>
<p>Items 5–8, 10, 11 and 17–20 from the list of uses for the Lean US Code, built 12 November 2026. Everything here is local; nothing is pushed.</p>
<p>In the post: <a href="{BLOG}#statutes">section 7 slideshow</a> · local commits in global-law: <code>1f0c482312a</code>, <code>d9ad435983f</code></p></header>
<nav>{nav}<a href="#three"><span>+</span>Three formalisms</a></nav>
<div class=tw><table><thead><tr><th>Item</th><th>Work</th><th>Headline</th><th>Lean</th><th>Folder</th></tr></thead><tbody>{rows}</tbody></table></div>
{"".join(secs)}
{anat_html}
</div></body></html>'''
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(page, encoding="utf-8", newline="\n")
    print(out, len(page))


if __name__ == "__main__":
    main(os.path.expanduser(sys.argv[1]))
