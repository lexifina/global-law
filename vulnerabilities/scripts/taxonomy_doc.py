"""Writes the taxonomy document from taxonomy.py (the definitions) and the released flags (the counts).
python taxonomy_doc.py OUT.md [OUT.html]"""
import collections, html, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import taxonomy as T  # noqa: E402

RELEASE = ROOT.parent / "data" / "flags.parquet"
OLD_NAMES = {"lapsed_limit": "Lapsed time limits", "repeal_gap": "Repeal gaps", "dead_currency": "Dead currencies",
             "placeholder_ref": "References to repealed placeholders", "same_day_conflict": "Same-day conflicts",
             "retroactive_date": "Retroactive or pre-publication dates", "dead_act_ref": "Citations of repealed acts (Spain)",
             "stale_amount": "Stale amounts", "dup_label": "Duplicate numbering", "late_extension": "Empty periods",
             "missing_paragraph": "Missing paragraphs (Germany)", "publisher_flag": "Failed amendments",
             "dangling_ref": "References to deleted provisions", "authority_gap": "Missing enabling power",
             "organic_reserve": "Organic-law reserve (Spain)", "dead_fine": "Dead fines (Germany)"}


def counts():
    import duckdb
    cols = [d[0] for d in duckdb.sql(f"describe select * from '{RELEASE.as_posix()}'").fetchall()]
    by = collections.Counter(); old_new = collections.Counter()
    for r in duckdb.sql(f"select * from '{RELEASE.as_posix()}'").fetchall():
        d = dict(zip(cols, r)); code, v = T.classify(d["detector"], d)
        by[(code, v)] += 1; old_new[(d["detector"], code)] += 1
    return by, old_new


def tests_section():
    return [
        "## How the taxonomy was tested",
        "",
        "Two kinds of test, both rerun after every change (`python -m unittest discover -s tests`, `python bench/taxonomy_bench.py`).",
        "",
        "**Structural tests** (`tests/test_taxonomy.py`) check the definitions on paper: every category has every field; codes are "
        "unique and family-prefixed; every released detector maps to a category; every exclusion either names another category "
        "or says the case is not a defect; the ten boundaries most likely to blur (A1/A2, A1/A3, A1/A4, A2/A4, A3/E5, B1/B2, B2/B3, "
        "B2/E4, E1/B2, E2/A3, C1/C4) are stated from both sides; the conditional rules in `classify()` behave as written; every "
        "older review verdict maps to a verdict here; every confirmed case sits in a defect family. On draft 1 they caught two "
        "real mistakes: B1 sent corpus date errors to the wrong category, and B1 never said where it stopped and B2 began.",
        "",
        "**Agreement test** (`bench/taxonomy_bench.py`). A language model is given only the written definitions and files 331 "
        "items: up to 20 real flags per detector (two thirds already reviewed, one third not) and all 25 confirmed cases. It "
        "returns a category, a verdict, a second-best category, whether the definitions failed to decide between the two, and, "
        "if nothing fits, what category is missing. Its answers are compared with the mechanical mapping (`classify()`) and, "
        "for confirmed cases, with the category intended for each.",
        "",
        "| Draft | What changed | Category agreement | Confirmed cases | Verdict agreement | 'No category fits' |",
        "|---|---|---|---|---|---|",
        "| 1 | one label per flag; 'corpus error' as a category | 53% | 24/25 | – | 110 |",
        "| 2 | category and verdict separated; B1+B2 merged; A2 widened to all sanctions; A4 widened to any other act | 84% | 24/25 | 60% | 13 |",
        "| 3 | cost recovery is not a sanction (A2 → A1); new E5 for garbled text; publisher notes split between A3 and E5; older 'artefact' reviews may be corpus or detector errors | 87% | 25/25 | 95% | 8 |",
        "| 3 (final) | E4 widened to moot or spent provisions | 85% | 25/25 | 95% | 3 |",
        "",
        "Labelling noise: the same items filed twice with near-identical definitions got the same category 317 times out of 331 "
        "(96%), so differences of 2-3 points between runs are noise. Two limits: the model, not a lawyer, applies the "
        "definitions; and the sample has at most 20 items per detector, so rare boundaries (B3, C3, C4) are barely exercised.",
        "",
        "What remains of the disagreements is understood:",
        "- 16 flags from the earlier Germany-only fine detector point at another act's section ('§ 60 LFGB'). The model files "
        "them as A4, which is what they allege; they are detector errors that the new `dead_fine.py` no longer produces.",
        "- 5 references to repealed provisions sit inside sanction provisions that the mechanical rule's keyword list misses; "
        "`classify()` should use `dead_fine.is_penal()` (94% precision, 74% recall) instead of a keyword list.",
        "- 3 items allege nothing at all (an index entry, a quoted rule with no problem in it). That is correct: a pure "
        "detector error has a verdict and no category.",
    ]


def write(out_md, out_html=None):
    by, old_new = counts()
    L = ["# Vulnerability taxonomy (draft 3)", "",
         "This document defines the kinds of defect the vulnerability list reports. It is generated from "
         "`scripts/taxonomy.py`, which is also what the tests and the release use, so the definitions here and the labels in "
         "the data cannot drift apart.", "",
         "## Two labels for every flag", "",
         "- **Category**: what kind of defect the flag alleges, decided from the text before anyone knows whether it is real. "
         "It never names a detector or a country.",
         "- **Verdict**: whether it holds. The verdicts are:", ""]
    L += [f"  - `{k}`: {v}" for k, v in T.VERDICTS.items()]
    L += ["", "Draft 1 had a single label, with 'corpus error' as one of the categories. The agreement test showed that most "
          "disagreements were verdicts filed as categories ('no category fits: this one is lawful'), so the two are now separate. "
          "A flag about a lapsed currency that a conversion law cures is category D2, verdict not_a_defect, not 'no category'.", "",
          "## Design rules", "",
          "1. A category names a kind of legal defect. Detectors map to categories; one detector can feed several through "
          "conditional rules, and several detectors can feed one category.",
          "2. Families A-D are defects in the law as published. Family E holds kinds of irregularity that are usually how a "
          "corpus was built; an E flag that review shows is real is re-filed under A-D, as its exclusions say.",
          "3. Categories are mutually exclusive: each lists boundary rules naming the neighbour and which one wins.",
          "4. Every category states the legal rule it breaches, its effect if real, what confirming it needs, and an example.",
          "", "## Effects, strongest first", ""]
    L += [f"- **{k}**: {v}" for k, v in T.EFFECTS.items()]
    L += ["", "## Families and categories", ""]
    L += ["| Code | Category | Effect | Severity (1 = worst) | Flags | Candidates | Confirmed | Not a defect | Corpus or detector error |",
          "|---|---|---|---|---|---|---|---|---|"]
    conf = collections.Counter(T.CONFIRMED.values())
    for code, c in T.C.items():
        n = sum(v for (k, _), v in by.items() if k == code)
        L.append(f"| {code} | {c['name']} | {c['effect']} | {c['severity']} | {n:,} | {by[(code, 'candidate')]:,} | {conf[code]} | "
                 f"{by[(code, 'not_a_defect')]:,} | {by[(code, 'corpus_error')] + by[(code, 'detector_error')]:,} |")
    L += ["", "Flags, candidates, not-a-defect and errors are the released list (74,301 flags) re-filed by `classify()`; "
          "confirmed are the 25 cases checked against official sources. Unreviewed flags are the remainder of each row.", ""]
    for f, (fname, fdesc) in T.FAMILIES.items():
        L += [f"### {f}. {fname}", "", fdesc, ""]
        for code, c in T.C.items():
            if c["family"] != f:
                continue
            L += [f"#### {code} · {c['name']}", "", c["definition"], "",
                  f"- **Rule breached:** {c['rule']}",
                  f"- **Effect if real:** {c['effect']} ({T.EFFECTS[c['effect']]}); severity {c['severity']} of 5",
                  "- **Includes:** " + "; ".join(c["include"]),
                  "- **Excludes:** " + ("; ".join(c["exclude"]) or "–"),
                  f"- **To confirm, check:** {c['confirm']}",
                  f"- **Example:** {c['example']}",
                  "- **Fed by:** " + (", ".join(f"`{d}`" for d in c["detectors"]) or "no detector yet"),
                  f"- **Status:** {c['status']}", ""]
    L += ["## From the released categories to this taxonomy", "",
          "| Released category (detector) | Now filed under | Flags |", "|---|---|---|"]
    for (det, code), n in sorted(old_new.items(), key=lambda kv: -kv[1]):
        L.append(f"| {OLD_NAMES.get(det, det)} (`{det}`) | {code} {T.C[code]['name']} | {n:,} |")
    L += [""] + tests_section() + [""]
    md = "\n".join(L) + "\n"
    Path(out_md).write_text(md, encoding="utf-8", newline="\n")
    print("wrote", out_md, len(md))
    if out_html:
        Path(out_html).write_text(to_html(md), encoding="utf-8", newline="\n"); print("wrote", out_html)


def to_html(md: str) -> str:
    import re
    out, in_table, in_list = [], False, False
    def inline(s):
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s); s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        return s
    for line in md.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            if not in_table:
                out.append("<div class=tw><table>"); in_table = True; tag = "th"
            else:
                tag = "td"
            out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>"); continue
        if in_table:
            out.append("</table></div>"); in_table = False
        if line.startswith(("- ", "  - ", "1. ", "2. ", "3. ", "4. ")):
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{inline(re.sub(r'^(\s*-|\d\.)\s+', '', line))}</li>"); continue
        if in_list:
            out.append("</ul>"); in_list = False
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            out.append(f"<h{len(m.group(1))}>{inline(m.group(2))}</h{len(m.group(1))}>")
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    css = ("<style>:root{--bg:#f5f3ee;--surface:#fffdf9;--ink:#1d1f22;--muted:#5d6066;--rule:#dcd8cf;--accent:#2f5d8a}"
           "@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#16181b;--surface:#1e2125;--ink:#e8e6e1;--muted:#a2a5ab;--rule:#33373d;--accent:#8db8e3}}"
           "body{margin:0;background:var(--bg);color:var(--ink);font:400 15px/1.6 'IBM Plex Sans',system-ui,sans-serif}"
           ".wrap{max-width:980px;margin:0 auto;padding:36px 16px 72px}h1,h2,h3{font-family:'Source Serif 4',Georgia,serif}"
           "h1{font-size:32px}h2{font-size:24px;border-top:1px solid var(--rule);padding-top:14px;margin-top:36px}h3{font-size:19px;margin-top:28px}"
           "h4{font-size:15px;margin:22px 0 4px;color:var(--accent)}code{font:13px 'IBM Plex Mono',monospace}"
           ".tw{overflow-x:auto;background:var(--surface);border:1px solid var(--rule);border-radius:8px;margin:10px 0}"
           "table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{text-align:left;vertical-align:top;padding:6px 9px;border-bottom:1px solid var(--rule)}"
           "th{color:var(--muted);font-weight:600}li{margin:3px 0}</style>")
    fonts = '<link rel=stylesheet href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono&display=swap">'
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width, initial-scale=1'>"
            f"<title>Vulnerability Taxonomy</title>{fonts}{css}</head><body><div class=wrap>" + "\n".join(out) + "</div></body></html>")


if __name__ == "__main__":
    write(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
