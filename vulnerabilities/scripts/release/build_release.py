"""Builds the public release of every flag the detectors raised, in one schema, in several formats.

python release/build_release.py OUTDIR
-> OUTDIR/flags.csv.gz, flags.jsonl.gz, flags.parquet   every flag (one row each)
   OUTDIR/reviewed.csv                                    flags a language model reviewed, with its verdict
   OUTDIR/confirmed.json, confirmed.csv                   cases checked by hand against official sources
   OUTDIR/by_category.csv, by_jurisdiction.csv            counts
   OUTDIR/html/index.html + html/<category>.html          the same list as browsable pages
   OUTDIR/README.md                                       what each file and column means
"""
from __future__ import annotations
import csv, glob, gzip, hashlib, html, io, json, sys
from collections import Counter, defaultdict
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
import os
PREV = Path(os.environ.get("LE_PREV_FINDINGS", ROOT / "findings"))       # earlier runs, for their model reviews
F1, F2, F3 = PREV / "run1", PREV / "run2", ROOT / "findings" / os.environ.get("LE_RUN", "run3")
sys.path.insert(0, str(ROOT))
import taxonomy as T  # noqa: E402


def latest(name):
    """the newest run that produced this output (run 3 re-ran the detectors whose code was improved)."""
    for d in (F3, F2, F1):
        if (d / name).exists():
            return d / name
    raise FileNotFoundError(name)
PINS = json.loads((ROOT / "pins.json").read_text(encoding="utf-8"))
REPO = {c["path"]: (c["repo"], c["sha"]) for c in PINS["corpora"]}

CATS = {  # detector key -> (category name, what it is)
    "lapsed_limit": ("Lapsed time limits", 'Text still applying a rule "until" a date that has passed'),
    "repeal_gap": ("Repeal gaps", "A provision repealed before its replacement took effect"),
    "dead_currency": ("Dead currencies", "Amounts still stated in pesetas, marks, lire, cruzeiros and the like"),
    "placeholder_ref": ("References to repealed placeholders", 'Provisions pointing at a section that survives only as "(repealed)"'),
    "same_day_conflict": ("Same-day conflicts", "Two amendments changing the same provision on the same day"),
    "retroactive_date": ("Retroactive or pre-publication dates", "Rules in force before they were made or published"),
    "dead_act_ref": ("Citations of repealed acts (Spain)", "Laws in force citing acts that are no longer in force"),
    "late_extension": ("Empty periods", "Time-limited rules extended only after they had run out"),
    "stale_amount": ("Stale amounts", "An amount changed in one place but not where it is repeated"),
    "dup_label": ("Duplicate numbering", "Two units with the same number in one provision"),
    "missing_paragraph": ("Missing paragraphs (Germany)", "References to a paragraph that the cited section does not have"),
    "publisher_flag": ("Failed amendments", "Publisher notes that an amendment could not be carried out"),
    "dangling_ref": ("References to deleted provisions", "Provisions pointing at a section that no longer exists"),
    "authority_gap": ("Missing enabling power", "Regulations citing a power that did not exist when they were made"),
    "organic_reserve": ("Organic-law reserve (Spain)", "Ordinary instruments changing an organic law"),
    "dead_fine": ("Dead fines (Germany)", "Fine catalogues pointing at deleted sections"),
}
COLS = ["id", "category", "detector", "taxonomy", "taxonomy_name", "verdict", "jurisdiction", "corpus", "path", "date",
        "reference", "summary", "score", "review", "review_note", "url"]


def s(v, n=600):
    if v is None:
        return ""
    t = str(v).replace("\r", " ").replace("\n", " ").strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def url(corpus, path):
    if corpus not in REPO or not path or path.startswith(("http", "build/")):
        return ""
    repo, sha = REPO[corpus]
    return f"https://github.com/lexifina/{repo}/blob/{sha}/{path}"


def rows_parquet(p):
    rel = duckdb.sql(f"select * from '{Path(p).as_posix()}'")
    cols = rel.columns
    return [dict(zip(cols, r)) for r in rel.fetchall()]


def rows_jsonl(p):
    out = []
    for l in Path(p).read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(l))
        except ValueError:
            pass
    return out


def run1_id(det, row):
    key = (f"{row['path']}>{row['ref']}" if det == "dangling_ref" else None) or row.get("path") or row.get("law") or \
        f"{row.get('regulation')}>{row.get('provision')}"
    d = row.get("in_force") or row.get("removed_on") or row.get("until")
    return f"{det}|{row['corpus']}|{key}|{d if d is None else str(d)}"


def collect():
    reviews = {}
    for r in (rows_jsonl(F1 / "triage.jsonl") if (F1 / "triage.jsonl").exists() else []):
        v, rb = r.get("verify") or {}, r.get("rebut") or {}
        verdict = v.get("verdict", "")
        if verdict == "candidate_defect":
            verdict = "candidate_defect, survived rebuttal" if rb.get("survives") else "candidate_defect, rebutted"
        reviews[r["id"]] = (verdict, s(v.get("reason"), 400))
    for r in (rows_jsonl(F2 / "dead_act_ref_triage.jsonl") if (F2 / "dead_act_ref_triage.jsonl").exists() else []):
        reviews[("dead_act_ref", r["row"]["path"], r["row"]["cited_id"])] = (r["j"]["verdict"], s(r["j"]["one_line"], 400))
    for r in (rows_jsonl(F2 / "late_extension_triage.jsonl") if (F2 / "late_extension_triage.jsonl").exists() else []):
        k = ("late_extension", r["row"]["corpus"], r["row"]["path"], r["row"]["old_until"])
        reviews[k] = (r["j"]["verdict"] + ("" if r["j"]["gap_real"] else ", gap not real"), s(r["j"]["one_line"], 400))
    for r in (rows_jsonl(F2 / "placeholder_triage.jsonl") if (F2 / "placeholder_triage.jsonl").exists() else []):
        reviews[("placeholder_ref", r["row"]["path"], r["row"]["ref"])] = (r["j"]["verdict"], s(r["j"]["one_line"], 400))

    out = []

    def add(det, corpus, path, date, ref, summary, score=None, rkey=None):
        rv = reviews.get(rkey, ("", "")) if rkey else ("", "")
        raw = f"{det}|{corpus}|{path}|{date}|{ref}|{summary[:80]}"
        out.append({
            "id": hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12], "category": CATS[det][0], "detector": det,
            "jurisdiction": corpus.split("/")[0], "corpus": corpus, "path": s(path, 300), "date": s(date, 40),
            "reference": s(ref, 300), "summary": s(summary), "score": None if score is None else round(float(score), 3),
            "review": rv[0], "review_note": rv[1], "url": url(corpus, path)})

    for f in sorted(glob.glob(str(F3 / "ranked_*.parquet"))):
        if Path(f).stem == "ranked_dead_act_ref":
            continue
        det = Path(f).stem.replace("ranked_", "")
        f = latest(Path(f).name)
        for r in rows_parquet(f):
            rk = run1_id(det, r)
            if det == "authority_gap":
                add(det, r["corpus"], r.get("preamble_path"), r.get("in_force"), f"{r.get('cited_act')} {r.get('provision') or ''}", r.get("why") or r.get("detail"), r.get("score"), rk)
            elif det == "retroactive_date":
                add(det, r["corpus"], "", r.get("in_force"), r.get("law"), r.get("why"), r.get("score"), rk)
            elif det == "dangling_ref":
                add(det, r["corpus"], r["path"], r.get("removed_on") or r.get("target_last_seen"), f"{r['ref']} → {r.get('target_path')}", r.get("why"), r.get("score"), rk)
            elif det == "repeal_gap":
                add(det, r["corpus"], r["path"], r.get("removed_on"), f"{r.get('removed_by')} → {r.get('back_by')}", r.get("why"), r.get("score"), rk)
            elif det == "same_day_conflict":
                add(det, r["corpus"], r["path"], r.get("in_force"), s(r.get("laws"), 300), r.get("why"), r.get("score"), rk)
            elif det == "lapsed_limit":
                add(det, r["corpus"], r["path"], r.get("until"), r.get("last_law"), r.get("why") or r.get("context"), r.get("score"), rk)
            elif det == "stale_amount":
                add(det, r["corpus"], r["path"], r.get("in_force"), f"{r.get('old')} → {r.get('new')}", r.get("why"), r.get("score"), rk)
    for r in rows_parquet(latest("ranked_dead_act_ref.parquet")):
        add("dead_act_ref", r["corpus"], r["path"], r.get("citing_last_change"), f"{r['cite']} ({r.get('cited_title')})", r.get("why"), r.get("score"),
            ("dead_act_ref", r["path"], r["cited_id"]))
    for r in rows_jsonl(latest("late_extension.jsonl")):
        add("late_extension", r["corpus"], r["path"], r["old_until"], r.get("law"),
            f"ran until {r['old_until']}; extended to {r['new_until']} by an amendment in force {r['extended_in_force']} ({r['gap_days']} days later)",
            None, ("late_extension", r["corpus"], r["path"], r["old_until"]))
    for fn, det in [("publisher_flag", "publisher_flag"), ("dead_currency", "dead_currency")]:
        for r in rows_jsonl(latest(f"{fn}.jsonl")):
            add(det, r["corpus"], r["path"], "", f"line {r.get('line')}", r.get("text"))
    for r in rows_jsonl(latest("dup_label.jsonl")):
        add("dup_label", r["corpus"], r["path"], "", f"{r['label']} ×{r['n']}", " | ".join(r.get("lines") or []))
    for r in rows_jsonl(latest("missing_paragraph.jsonl")):
        add("missing_paragraph", r["corpus"], r["path"], "", f"{r['ref']} → {r['target']} (has {','.join(r.get('target_paras') or [])})", r.get("line"))
    for r in rows_jsonl(latest("dead_fine.jsonl")):
        status = r.get("target_status") or r.get("problem", "")
        add("dead_fine", r["corpus"], r["path"], "", f"{r['ref']}: {status}" + (f" → {r['target']}" if r.get("target") else ""),
            r.get("line") or r.get("context"), r.get("score"))
    for r in rows_jsonl(latest("placeholder_ref.jsonl")):
        add("placeholder_ref", r["corpus"], r["path"], "", f"{r['ref']} → {r['target']}", f"{r.get('target_text')} | {r.get('context')}",
            None, ("placeholder_ref", r["path"], r["ref"]))
    for r in (rows_jsonl(latest("organic_reserve.jsonl")) if any((d / "organic_reserve.jsonl").exists() for d in (F3, F2)) else []):
        j = r.get("j") or {}
        out.append({"id": hashlib.sha1(f"organic_reserve|{r['law']}|{r['lo']}".encode()).hexdigest()[:12],
                    "category": CATS["organic_reserve"][0], "detector": "organic_reserve", "jurisdiction": "spain",
                    "corpus": "spain/national/acts", "path": r["lo"], "date": s(r.get("date"), 40), "reference": s(r["law"], 300),
                    "summary": s(f"{r['law']} changed {len(r.get('paths') or [])} file(s) of {r['lo']}"), "score": j.get("confidence"),
                    "review": j.get("verdict", ""), "review_note": s(j.get("reason"), 400), "url": url("spain/national/acts", r["lo"])})
    # one row per id (some detectors list the same hit twice)
    seen, uniq = set(), []
    for r in out:
        if r["id"] not in seen:
            seen.add(r["id"]); uniq.append(r)
    tr = {}
    trp = F3 / "taxonomy_review.jsonl"
    if trp.exists():
        for x in rows_jsonl(trp):
            tr[x["id"]] = x
    for r in uniq:
        code, v = T.classify(r["detector"], r)
        x = tr.get(r["id"])
        if x:
            code = x.get("category") or code
            v = x.get("final_verdict") or x.get("verdict") or v
            r["review"] = x.get("review_label", r["review"]); r["review_note"] = s(x.get("one_line") or x.get("reason"), 400)
        r["taxonomy"], r["taxonomy_name"], r["verdict"] = code, T.C[code]["name"] if code in T.C else "", v
    return uniq


DATA_README = """# Vulnerabilities: the full list

Every flag the detectors raised, one row per provision and issue. A flag is a candidate, not a confirmed defect: most are
corpus build errors, or lawful once read in context. The cases checked by hand against official sources are in
`confirmed.csv` / `confirmed.json`.

| File | What it holds |
|---|---|
| [confirmed.csv](confirmed.csv), [confirmed.json](confirmed.json) | Cases confirmed against official sources, with links to them |
| [by_category.csv](by_category.csv) | Flags per category, and how many a language model reviewed |
| [by_jurisdiction.csv](by_jurisdiction.csv) | Flags per jurisdiction and category |
| [reviewed.csv](reviewed.csv) | Flags a language model reviewed, with its verdict and a one-line note |
| flags.csv.gz, flags.jsonl.gz, flags.parquet | Every flag, in three formats |
| [html/index.html](html/index.html) | The same list as browsable pages, one per category (download and open in a browser) |

## Columns

| Column | Meaning |
|---|---|
| id | Stable identifier (hash of detector, corpus, provision, date, reference) |
| category, detector | The kind of defect, and the detector that found it |
| jurisdiction, corpus | Country, and the corpus path in this repository |
| path | The provision's file in the corpus repository |
| date | The date the flag turns on (end date, in-force date, removal date), where there is one |
| reference | What the provision points at, or the instrument involved |
| summary | Why it was flagged, or the line of text concerned |
| score | The detector's ranking score, 0 to 1, where it has one |
| review | A language model's verdict, where reviewed: artefact (corpus error), lawful, harmless or cured, candidate_defect |
| review_note | The model's one-line reason |
| url | The provision at the commit that was read |

The corpora were read at pinned commits and never written to.
"""

CONFIRMED = ROOT / "release" / "confirmed.json"


def write(outdir: Path, rows):
    outdir.mkdir(parents=True, exist_ok=True)
    order = list(CATS)
    rows.sort(key=lambda r: (order.index(r["detector"]), r["jurisdiction"], -(r["score"] or 0), r["path"]))
    buf = io.StringIO(); w = csv.DictWriter(buf, COLS, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    with open(outdir / "flags.csv.gz", "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as fh:
        fh.write(buf.getvalue().encode("utf-8"))
    with open(outdir / "flags.jsonl.gz", "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as fh:
        fh.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8"))
    con = duckdb.connect()
    con.execute("create table t (" + ", ".join(f'"{c}" {"double" if c == "score" else "varchar"}' for c in COLS) + ")")
    con.executemany("insert into t values (" + ",".join("?" * len(COLS)) + ")", [[r[c] for c in COLS] for r in rows])
    con.execute(f"copy t to '{(outdir / 'flags.parquet').as_posix()}' (format parquet, compression zstd)")
    rev = [r for r in rows if r["review"]]
    with (outdir / "reviewed.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, COLS, lineterminator="\n"); w.writeheader(); w.writerows(rev)
    cat = Counter(r["detector"] for r in rows)
    with (outdir / "by_category.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["category", "what_it_is", "flags", "reviewed_by_model"])
        for d, n in sorted(cat.items(), key=lambda x: -x[1]):
            w.writerow([CATS[d][0], CATS[d][1], n, sum(1 for r in rev if r["detector"] == d)])
    jur = Counter(r["jurisdiction"] for r in rows)
    with (outdir / "by_jurisdiction.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["jurisdiction", "flags"] + [CATS[d][0] for d in order])
        per = defaultdict(Counter)
        for r in rows:
            per[r["jurisdiction"]][r["detector"]] += 1
        for j, n in jur.most_common():
            w.writerow([j, n] + [per[j][d] for d in order])
    conf = json.loads(CONFIRMED.read_text(encoding="utf-8"))
    (outdir / "confirmed.json").write_text(json.dumps(conf, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    ck = ["jurisdiction", "provision", "kind", "finding", "status", "sources"]
    with (outdir / "confirmed.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, ck, lineterminator="\n"); w.writeheader()
        for c in conf:
            w.writerow({**{k: c[k] for k in ck if k != "sources"}, "sources": " ".join(c["sources"])})
    write_html(outdir / "html", rows, cat, jur, conf)
    (outdir / "README.md").write_text(DATA_README, encoding="utf-8", newline="\n")
    return cat, jur, len(rev)


CSS = """:root{--bg:#f5f3ee;--s:#fffdf9;--i:#1d1f22;--m:#5d6066;--r:#dcd8cf;--a:#2f5d8a}
@media (prefers-color-scheme:dark){:root{--bg:#16181b;--s:#1e2125;--i:#e8e6e1;--m:#a2a5ab;--r:#33373d;--a:#8db8e3}}
body{margin:0;background:var(--bg);color:var(--i);font:14px/1.5 system-ui,sans-serif}.w{max-width:1200px;margin:0 auto;padding:28px 16px 60px}
h1{font:600 28px/1.2 Georgia,serif;margin:0 0 8px}h2{font:600 20px Georgia,serif;margin:28px 0 8px}a{color:var(--a)}.m{color:var(--m)}
.t{overflow-x:auto;background:var(--s);border:1px solid var(--r);border-radius:8px}table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--r)}th{color:var(--m);position:sticky;top:0;background:var(--s)}
td{max-width:420px;overflow-wrap:anywhere}td.n{text-align:right;font-variant-numeric:tabular-nums}"""


def page(title, body):
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body><div class=w>{body}</div></body></html>\n")


def write_html(d: Path, rows, cat, jur, conf):
    d.mkdir(parents=True, exist_ok=True)
    E = html.escape
    slug = {k: k.replace("_", "-") for k in CATS}
    trs = "".join(f"<tr><td><a href='{slug[k]}.html'>{E(CATS[k][0])}</a></td><td>{E(CATS[k][1])}</td><td class=n>{n:,}</td></tr>"
                  for k, n in sorted(cat.items(), key=lambda x: -x[1]))
    jtr = "".join(f"<tr><td>{E(j)}</td><td class=n>{n:,}</td></tr>" for j, n in jur.most_common())
    ctr = "".join(f"<tr><td>{E(c['jurisdiction'])}</td><td>{E(c['provision'])}</td><td>{E(c['kind'])}</td><td>{E(c['finding'])}</td>"
                  f"<td>{' '.join(f'<a href=\"{E(u)}\">source</a>' for u in c['sources'])}</td></tr>" for c in conf)
    body = (f"<h1>Vulnerabilities in law: every flag</h1><p class=m>{sum(cat.values()):,} flags raised by the detectors across "
            f"{len(jur)} jurisdictions. A flag is a candidate, not a confirmed defect; most are corpus build errors or lawful once read in "
            f"context. The cases checked by hand against official sources are listed first.</p>"
            f"<h2>Confirmed against official sources ({len(conf)})</h2><div class=t><table><tr><th>Jurisdiction</th><th>Provision</th><th>Kind</th>"
            f"<th>Finding</th><th>Sources</th></tr>{ctr}</table></div>"
            f"<h2>By category</h2><div class=t><table><tr><th>Category</th><th>What it is</th><th>Flags</th></tr>{trs}</table></div>"
            f"<h2>By jurisdiction</h2><div class=t><table><tr><th>Jurisdiction</th><th>Flags</th></tr>{jtr}</table></div>")
    (d / "index.html").write_text(page("Vulnerabilities: every flag", body), encoding="utf-8", newline="\n")
    by = defaultdict(list)
    for r in rows:
        by[r["detector"]].append(r)
    for k, rs in by.items():
        tr = "".join(
            f"<tr><td>{E(r['jurisdiction'])}</td><td>{('<a href=\"' + E(r['url']) + '\">' + E(r['path']) + '</a>') if r['url'] else E(r['path'])}</td>"
            f"<td>{E(r['date'])}</td><td>{E(r['reference'][:120])}</td><td>{E(r['summary'][:160])}</td>"
            f"<td>{E(r['review'])}{(': ' + E(r['review_note'][:120])) if r['review_note'] else ''}</td></tr>" for r in rs)
        body = (f"<p class=m><a href='index.html'>← every flag</a></p><h1>{E(CATS[k][0])}</h1><p class=m>{E(CATS[k][1])}. {len(rs):,} flags.</p>"
                f"<div class=t><table><tr><th>Jurisdiction</th><th>Provision</th><th>Date</th><th>Reference</th><th>Detail</th><th>Model review</th></tr>{tr}</table></div>")
        (d / f"{slug[k]}.html").write_text(page(CATS[k][0], body), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    out = Path(sys.argv[1])
    rows = collect()
    cat, jur, nrev = write(out, rows)
    print(len(rows), "flags;", nrev, "reviewed;", len(jur), "jurisdictions")
    for k, n in cat.most_common():
        print(f"  {CATS[k][0]}: {n}")
