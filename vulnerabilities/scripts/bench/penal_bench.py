"""How well dead_fine.is_penal() recognises penalty provisions (offences, fines, administrative infractions) in every
language, against model-labelled gold drawn from every corpus. The step decides which provisions dead_fine reads at all,
so its recall caps the detector's recall outside Germany.

python bench/penal_bench.py sample --set tuning|holdout [--per 12]   -> bench/data[_holdout]/penal.jsonl
python bench/penal_bench.py label  --set tuning|holdout               -> bench/data[_holdout]/penal_gold.jsonl (resumable)
python bench/penal_bench.py score  --set tuning|holdout               -> bench/out/penal_scores_<set>.json, misses, table

Each corpus gives up to PER/2 provisions that contain a loose penalty word and PER/2 drawn at random, so both precision
(penalty words in non-penal rules) and recall (penalty provisions phrased in ways the cues miss) are measured.
"""
from __future__ import annotations
import argparse, json, random, re, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ingest")); sys.path.insert(0, str(ROOT / "triage")); sys.path.insert(0, str(ROOT / "detectors"))
sys.path.insert(0, str(ROOT / "bench"))
from common import CORPUS, pins  # noqa: E402
from refscan import path_key  # noqa: E402
from stage_bench import tree, cat, EXCLUDE  # noqa: E402

SEEDS = {"tuning": 7, "holdout": 11}
LOOSE = re.compile(r"(?i)strafe|bu(ss|ß)e|ordnungswidrig|bestraft|übertretung|amende|puni|sanction|infraction|contravention|"
                   r"multa|pena\b|penas|sanci|infracci|infraç|punid|reclus|detenç|fine\b|fined|penalty|penalties|offen[cs]e|"
                   r"conviction|imprisonment|boete|gestraft|straff|böter|sakko|ceza|kazn|trest|pokut|bauda|sod[ai]|τιμωρ|πρόστιμ|"
                   r"cərimə|штраф|наказ|罰|处罚|ปรับ|จำคุก|غرامة|عقوبة")
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["penalty", "reason"],
          "properties": {"penalty": {"type": "boolean"}, "reason": {"type": "string"}}}
PROMPT = """Does this provision of law itself make some conduct punishable: an offence, a crime, a fine, an administrative
infraction or contravention, or a list of such infractions (including a catalogue that says 'it is an offence / an
infraction to ...' and refers to other provisions for the duty)? Answer true only if this text creates or lists the
punishable conduct or its penalty. Answer false for procedure, sentencing rules, tax surcharges or interest, definitions,
references to penalties elsewhere, and rules that merely mention a penalty.

PROVISION ({corpus} · {path}):
{text}"""


def paths(set_name):
    d = ROOT / "bench" / ("data" if set_name == "tuning" else "data_holdout")
    d.mkdir(parents=True, exist_ok=True)
    return d / "penal.jsonl", d / "penal_gold.jsonl"


def sample(set_name, per):
    random.seed(SEEDS[set_name])
    src, _ = paths(set_name)
    rows = []
    for c in pins()["corpora"]:
        if c["repo"].startswith(EXCLUDE) or not (CORPUS / f"{c['repo']}.git").exists():
            continue
        files = [(s, p) for s, p in tree(c) if path_key(p)]
        if len(files) < 20:
            continue
        pick = random.sample(files, min(len(files), 600))
        texts = cat(c["repo"], [s for s, _ in pick])
        cand = [(p, t) for (_, p), t in zip(pick, texts) if 80 <= len(t) <= 4000]
        loose = [x for x in cand if LOOSE.search(x[1])]
        other = [x for x in cand if not LOOSE.search(x[1])]
        got = random.sample(loose, min(per // 2, len(loose)))
        got += random.sample(other, min(per - len(got), len(other)))
        rows += [{"corpus": c["path"], "repo": c["repo"], "path": p, "text": t} for p, t in got]
    with src.open("w", encoding="utf-8") as fh:
        for i, r in enumerate(rows):
            fh.write(json.dumps({"i": i, **r}, ensure_ascii=False) + "\n")
    print(set_name, len(rows), "provisions sampled")


def label(set_name):
    from llm import call
    src, gp = paths(set_name)
    rows = [json.loads(l) for l in src.open(encoding="utf-8")]
    done = {json.loads(l)["i"] for l in gp.open(encoding="utf-8")} if gp.exists() else set()
    todo = [r for r in rows if r["i"] not in done]
    lock = threading.Lock()

    def work(n, r):
        res = call(PROMPT.format(corpus=r["corpus"], path=r["path"], text=r["text"][:4000]), schema=SCHEMA,
                   provider="azure-uk" if n % 2 else "azure", max_tokens=600)
        return {"i": r["i"], **res["json"]}
    with ThreadPoolExecutor(24) as ex, gp.open("a", encoding="utf-8") as fh:
        for fu in as_completed([ex.submit(work, n, r) for n, r in enumerate(todo)]):
            try:
                rec = fu.result()
            except Exception as e:
                print("error:", str(e)[:160]); continue
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
    print(set_name, "labelled", len(todo))


def score(set_name):
    from dead_fine import is_penal
    src, gp = paths(set_name)
    rows = {r["i"]: r for r in (json.loads(l) for l in src.open(encoding="utf-8"))}
    gold = {g["i"]: g for g in (json.loads(l) for l in gp.open(encoding="utf-8"))}
    per, misses = {}, []
    for i, g in gold.items():
        r = rows[i]; pred = is_penal(r["text"]); truth = g["penalty"]
        for k in ("ALL", r["corpus"].split("/")[0]):
            d = per.setdefault(k, {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
            d["tp" if pred and truth else "fp" if pred else "fn" if truth else "tn"] += 1
        if pred != truth:
            misses.append({"i": i, "corpus": r["corpus"], "path": r["path"], "gold": truth, "pred": pred,
                           "reason": g["reason"], "text": r["text"][:500]})

    def pr(d):
        p = d["tp"] / (d["tp"] + d["fp"]) if d["tp"] + d["fp"] else None
        rc = d["tp"] / (d["tp"] + d["fn"]) if d["tp"] + d["fn"] else None
        return {**d, "precision": p, "recall": rc}
    rep = {k: pr(v) for k, v in per.items()}
    out = ROOT / "bench" / "out"; out.mkdir(parents=True, exist_ok=True)
    (out / f"penal_scores_{set_name}.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    (out / f"penal_misses_{set_name}.jsonl").write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in misses), encoding="utf-8")
    f = lambda x: "  -  " if x is None else f"{x:.0%}"
    a = rep["ALL"]
    print(f"penal ({set_name}): precision {f(a['precision'])}  recall {f(a['recall'])}  (tp {a['tp']}, fp {a['fp']}, fn {a['fn']}, tn {a['tn']})")
    worst = sorted(((k, v) for k, v in rep.items() if k != "ALL" and v["tp"] + v["fn"] >= 2 and v["recall"] is not None),
                   key=lambda kv: kv[1]["recall"])[:15]
    for k, v in worst:
        print(f"  {k:28s} recall {f(v['recall'])}  precision {f(v['precision'])}  (tp {v['tp']}, fn {v['fn']}, fp {v['fp']})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["sample", "label", "score"])
    ap.add_argument("--set", default="tuning", choices=list(SEEDS)); ap.add_argument("--per", type=int, default=12)
    a = ap.parse_args()
    {"sample": lambda: sample(a.set, a.per), "label": lambda: label(a.set), "score": lambda: score(a.set)}[a.cmd]()
