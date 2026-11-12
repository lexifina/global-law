"""Extract every amending instruction from the cached public laws (USLM) of the record's laws.

    python tools/extract.py <lo congress> <hi congress> <out.jsonl>

One JSON line per instruction: law label, title, section, path, ops, wording, effective date, order.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fetch  # noqa: E402

HERE = Path(__file__).resolve().parents[1]


def titles_in(xml: bytes) -> list[int]:
    return sorted({int(t) for t in re.findall(rb'href="/us/usc/t(\d+)', xml)})


def one(label: str):
    import uslm_laws as L
    c, n = (int(x) for x in label.replace("Pub. L. ", "").split("-"))
    xml = fetch.fetch(fetch.plaw_uslm(c, n), offline=True)
    if xml is None:
        return label, None, []
    mods = fetch.fetch(fetch.plaw_mods(c, n), offline=True)
    out = []
    approved = ""
    for t in titles_in(xml):
        try:
            law = L.parse_law(xml, mods, congress=c, number=n, url=fetch.plaw_uslm(c, n), sha256="", fetched_at="", title=t)
        except Exception as e:  # noqa: BLE001
            out.append({"law": label, "title": t, "error": repr(e)[:300]})
            continue
        approved = law.approved
        for i in law.instructions:
            out.append({
                "law": label, "title": t, "section": i.section, "path": i.path, "id": i.identifier, "label": i.label,
                "ops": [{"kind": o.kind, "args": o.args} for o in i.ops], "unparsed": i.unparsed,
                "effective": i.effective, "order": i.order, "heading": i.heading, "text": i.text[:3000],
            })
    return label, approved, out


def main():
    lo, hi, outp = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    laws = set()
    with open(HERE.parents[1] / "usc/versions.tsv", encoding="utf-8") as f:
        for r in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r[2] == "law":
                laws.add(r[3])
    todo = sorted(l for l in laws if lo <= int(l.replace("Pub. L. ", "").split("-")[0]) <= hi)
    nlaw = ninst = nmiss = 0
    with open(outp, "w", encoding="utf-8", newline="\n") as f, ProcessPoolExecutor(4) as ex:
        for label, approved, rows in ex.map(one, todo, chunksize=4):
            if approved is None and not rows:
                nmiss += 1
                f.write(json.dumps({"law": label, "missing": True}) + "\n")
                continue
            nlaw += 1
            f.write(json.dumps({"law": label, "approved": approved, "header": True}) + "\n")
            for r in rows:
                ninst += 1
                f.write(json.dumps(r, default=str) + "\n")
    print(f"laws {nlaw} (no text {nmiss}); instructions {ninst}")


if __name__ == "__main__":
    main()
