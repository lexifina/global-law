"""Build tools/out/report.html from the certificates Lean checked (run gen_facts.py and lake build first).

Sections: what Lean certified, by category and jurisdiction; the strongest leads (dead references the legislature kept
when it rewrote the citing provision), with the model review where there is one.
"""
from __future__ import annotations
import collections, html, json
from pathlib import Path
import duckdb

HERE = Path(__file__).resolve().parent
FLAGS = HERE.parent.parent / "vulnerabilities" / "data" / "flags.parquet"
E = html.escape


def iso(n): s = str(n); return f"{s[:4]}-{s[4:6]}-{s[6:]}"


def main() -> None:
    d = json.loads((HERE / "out" / "certificates.json").read_text(encoding="utf-8"))
    meta = {r[0]: r[1:] for r in duckdb.sql(f"select id, review, url, left(summary, 200) from '{FLAGS.as_posix()}'").fetchall()}
    fl = d["flags"]
    cert = [r for r in fl if r["certified"]]
    reen = [r for r in cert if r["reenacted"]]
    bycat = collections.Counter((r["category"], r["certified"]) for r in fl)
    byj = collections.Counter(r["corpus"].split("/")[0] for r in cert)
    leads = sorted([r for r in reen if meta.get(r["id"], ("",))[0] in ("", None)],
                   key=lambda r: (r["corpus"], -r["dead_from"]))
    cats = sorted({r["category"] for r in fl})
    rows_cat = "".join(f"<tr><td>{E(c)}</td><td class=r>{bycat[(c, True)] + bycat[(c, False)]:,}</td><td class=r>{bycat[(c, True)]:,}</td></tr>" for c in cats)
    rows_j = "".join(f"<tr><td>{E(j)}</td><td class=r>{n:,}</td></tr>" for j, n in byj.most_common())
    rows_l = "".join(
        f"<tr><td>{E(r['corpus'].split('/')[0])}</td><td><a href='{E(meta[r['id']][1] or '')}'>{E(r['citing_path'])}</a></td>"
        f"<td>{E(r['target_path'])}</td><td>{iso(r['dead_from'])}</td><td>{iso(r['citing'][0][0])}</td></tr>" for r in leads)
    page = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Lean Certificates</title><style>
:root{{--bg:#f5f3ee;--s:#fffdf9;--ink:#1d1f22;--m:#5d6066;--rule:#dcd8cf;--a:#2f5d8a}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#16181b;--s:#1e2125;--ink:#e8e6e1;--m:#a2a5ab;--rule:#33373d;--a:#8db8e3;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#16181b;--s:#1e2125;--ink:#e8e6e1;--m:#a2a5ab;--rule:#33373d;--a:#8db8e3;color-scheme:dark}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,sans-serif}}.w{{max-width:1100px;margin:0 auto;padding:32px 16px 64px}}
h1{{font:600 30px Georgia,serif;margin:0 0 6px}}h2{{font:600 21px Georgia,serif;margin:34px 0 8px}}.m{{color:var(--m);font-size:13px}}a{{color:var(--a)}}
.g{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:16px 0}}.s{{background:var(--s);border:1px solid var(--rule);border-radius:8px;padding:12px}}
.s b{{display:block;font:600 26px Georgia,serif}}.t{{overflow:auto;max-height:620px;background:var(--s);border:1px solid var(--rule);border-radius:8px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{text-align:left;padding:6px 9px;border-bottom:1px solid var(--rule);vertical-align:top}}th{{position:sticky;top:0;background:var(--s);color:var(--m)}}.r{{text-align:right}}
</style></head><body><div class=w>
<h1>Lean certificates</h1>
<p>Every flagged reference whose corpus record shows the target gone while the citing provision is still in force on {iso(d['today'])} is <b>certified</b>:
Lean evaluates the certificate itself, and the theorem <code>RefFlag.certified_sound</code> proves that a certified reference cannot apply on any date from the target's removal.
A certificate is about the corpus record: where the record is wrong (a corpus build error), so is the certificate.</p>
<div class=g><div class=s><b>{len(fl):,}</b>reference flags checked</div><div class=s><b>{len(cert):,}</b>certified by Lean</div>
<div class=s><b>{len(reen):,}</b>citing provision rewritten after the target had gone</div><div class=s><b>{len(leads):,}</b>of those never reviewed: next leads</div></div>
<h2>By category</h2><div class=t><table><tr><th>Category</th><th class=r>Flags</th><th class=r>Certified</th></tr>{rows_cat}</table></div>
<h2>Certified, by jurisdiction</h2><div class=t><table><tr><th>Jurisdiction</th><th class=r>Certified</th></tr>{rows_j}</table></div>
<h2>Leads: dead references kept when the citing provision was rewritten</h2>
<p class=m>The legislature amended the citing provision after its target had gone and left the reference in place. Not yet reviewed by a model or checked against official sources.</p>
<div class=t><table><tr><th>Jurisdiction</th><th>Citing provision</th><th>Points at</th><th>Target gone since</th><th>Citing rewritten</th></tr>{rows_l}</table></div>
</div></body></html>"""
    (HERE / "out" / "report.html").write_text(page, encoding="utf-8")
    print("wrote", HERE / "out" / "report.html", len(fl), len(cert), len(reen), len(leads))


if __name__ == "__main__":
    main()
