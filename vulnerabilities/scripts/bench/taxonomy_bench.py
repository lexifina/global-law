"""Does the written taxonomy work? A model gets only the category definitions (taxonomy.py) and files a stratified
sample of real flags plus every confirmed case. Disagreement with the mechanical mapping, low confidence, two codes that
both fit, or 'NONE' show where a definition is unclear or a category is missing.

python bench/taxonomy_bench.py sample [--per 20]   -> bench/data/taxonomy.jsonl
python bench/taxonomy_bench.py label               -> bench/data/taxonomy_gold.jsonl (resumable)
python bench/taxonomy_bench.py score               -> bench/out/taxonomy_report.json and a printed report
"""
from __future__ import annotations
import argparse, collections, json, random, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "triage"))
import taxonomy as T  # noqa: E402

DATA = ROOT / "bench" / "data"; OUT = ROOT / "bench" / "out"
RELEASE = ROOT.parent / "data"
CODES = sorted(T.C) + ["NONE"]
VERDICTS = sorted(T.VERDICTS)


def definitions() -> str:
    out = []
    for f, (fname, fdesc) in T.FAMILIES.items():
        out.append(f"FAMILY {f}. {fname}: {fdesc}")
        for code, c in T.C.items():
            if c["family"] != f:
                continue
            out.append(f"  {code} {c['name']}: {c['definition']}\n     includes: {'; '.join(c['include'])}\n"
                       f"     excludes: {'; '.join(c['exclude']) or '-'}")
    return "\n".join(out)


SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["code", "second", "verdict", "confidence", "both_fit", "missing_category", "reason"],
          "properties": {"code": {"type": "string", "enum": CODES}, "second": {"type": "string", "enum": CODES},
                         "verdict": {"type": "string", "enum": VERDICTS},
                         "confidence": {"type": "number"}, "both_fit": {"type": "boolean"},
                         "missing_category": {"type": "string"}, "reason": {"type": "string"}}}
PROMPT = """You are testing a taxonomy of defects in published legislation. Give the item two labels, using ONLY these
definitions (their includes/excludes decide boundaries):
- code: the category of defect the flag ALLEGES (what kind of problem it would be if real), even if it turns out not to be
  real. NONE only if no category describes what is alleged; then describe the missing category in missing_category
  (else "").
- verdict: whether it holds, from the evidence given: {verdicts}
'second' is the next best code (NONE if none). both_fit = true if the definitions do not decide between code and second.

{defs}

ITEM
jurisdiction: {jur}
provision: {prov}
what was flagged: {summary}
reference / instrument: {ref}
review verdict: {review}
review note: {note}"""


def sample(per):
    import duckdb
    random.seed(13)
    rows = duckdb.sql(f"select * from '{(RELEASE / 'flags.parquet').as_posix()}'").fetchall()
    cols = [d[0] for d in duckdb.sql(f"describe select * from '{(RELEASE / 'flags.parquet').as_posix()}'").fetchall()]
    by = collections.defaultdict(list)
    for r in rows:
        d = dict(zip(cols, r)); by[d["detector"]].append(d)
    items = []
    for det, rs in by.items():
        rev = [r for r in rs if r["review"]]; unrev = [r for r in rs if not r["review"]]
        pick = random.sample(rev, min(per * 2 // 3, len(rev)))
        pick += random.sample(unrev, min(per - len(pick), len(unrev)))
        for r in pick:
            code, v = T.classify(det, r)
            items.append({"kind": "flag", "detector": det, "expected": code, "expected_verdict": v, "jur": r["jurisdiction"],
                          "prov": r["path"], "summary": (r["summary"] or "")[:600], "ref": r["reference"] or "",
                          "review": r["review"] or "not reviewed", "note": (r["review_note"] or "")[:300]})
    conf = json.load(open(RELEASE / "confirmed.json", encoding="utf-8"))
    for (name, code), x in zip(T.CONFIRMED.items(), conf):
        items.append({"kind": "confirmed", "detector": "-", "expected": code, "expected_verdict": "confirmed", "name": name, "jur": x["jurisdiction"],
                      "prov": x["provision"], "summary": x["finding"][:900], "ref": "", "review": "confirmed against official sources",
                      "note": x.get("kind", "")})
    DATA.mkdir(parents=True, exist_ok=True)
    with (DATA / "taxonomy.jsonl").open("w", encoding="utf-8") as fh:
        for i, it in enumerate(items):
            fh.write(json.dumps({"i": i, **it}, ensure_ascii=False) + "\n")
    print(len(items), "items")


def label():
    from llm import call
    src = [json.loads(l) for l in (DATA / "taxonomy.jsonl").open(encoding="utf-8")]
    gp = DATA / "taxonomy_gold.jsonl"
    done = {json.loads(l)["i"] for l in gp.open(encoding="utf-8")} if gp.exists() else set()
    defs = definitions(); lock = threading.Lock()

    def work(n, it):
        res = call(PROMPT.format(defs=defs, verdicts="; ".join(f"{k} = {v}" for k, v in T.VERDICTS.items()), **{k: it[k] for k in ("jur", "prov", "summary", "ref", "review", "note")}),
                   schema=SCHEMA, provider="azure-uk" if n % 2 else "azure", max_tokens=800)
        return {"i": it["i"], **res["json"]}
    with ThreadPoolExecutor(24) as ex, gp.open("a", encoding="utf-8") as fh:
        for fu in as_completed([ex.submit(work, n, it) for n, it in enumerate(src) if it["i"] not in done]):
            try:
                rec = fu.result()
            except Exception as e:
                print("error:", str(e)[:150]); continue
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()


def score():
    src = {r["i"]: r for r in (json.loads(l) for l in (DATA / "taxonomy.jsonl").open(encoding="utf-8"))}
    gold = [json.loads(l) for l in (DATA / "taxonomy_gold.jsonl").open(encoding="utf-8")]
    conf = collections.Counter(); per = collections.defaultdict(lambda: [0, 0]); both = collections.Counter()
    none, lowc, rows = [], [], []
    for g in gold:
        it = src[g["i"]]; ok = g["code"] == it["expected"]
        per[it["expected"]][0] += ok; per[it["expected"]][1] += 1
        if not ok:
            conf[(it["expected"], g["code"])] += 1
        if g["both_fit"]:
            both[tuple(sorted((g["code"], g["second"])))] += 1
        if g["code"] == "NONE" or g["missing_category"]:
            none.append({**it, **g})
        if g["confidence"] < 0.6:
            lowc.append({**it, **g})
        rows.append({**it, **g, "agree": ok})
    n = len(gold); a = sum(r["agree"] for r in rows)
    print(f"agreement with the mechanical mapping: {a}/{n} = {a / n:.0%}")
    cr = [r for r in rows if r["kind"] == "confirmed"]
    print(f"confirmed cases filed as intended: {sum(r['agree'] for r in cr)}/{len(cr)}")
    rv = [r for r in rows if r["expected_verdict"] not in ("flagged",)]
    ok_v = lambda r: r["verdict"] == r["expected_verdict"] or (r["expected_verdict"] == "corpus_error" and r["verdict"] in T.ARTEFACT_EITHER)
    print(f"verdict agreement where a review exists: {sum(ok_v(r) for r in rv)}/{len(rv)} "
          f"(an older 'artefact' review counts as corpus or detector error)")
    print("\nper expected category (agree/total):")
    for k in sorted(per):
        print(f"  {k}  {per[k][0]}/{per[k][1]}")
    print("\nmost common disagreements (expected -> model):")
    for (e, m), c in conf.most_common(12):
        print(f"  {e} -> {m}: {c}")
    print("\npairs the definitions did not decide (both_fit):")
    for p, c in both.most_common(10):
        print(f"  {p[0]} / {p[1]}: {c}")
    print(f"\nNONE or missing category suggested: {len(none)}; confidence < 0.6: {len(lowc)}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "taxonomy_report.json").write_text(json.dumps({"rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["sample", "label", "score"]); ap.add_argument("--per", type=int, default=20)
    a = ap.parse_args()
    {"sample": lambda: sample(a.per), "label": label, "score": score}[a.cmd]()
