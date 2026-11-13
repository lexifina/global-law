"""Which holdings of a target an overruling act reaches (partial overruling), for acts whose words limit their scope.

    python reach.py [--treatments]   (v1 acts by default; --treatments reads data/treatments.tsv once the reader writes it)
reads events_v3/acts.tsv (by, target, pattern, window) + the target's holdings in raw_*.jsonl;
writes data/holdings_work/raw_reach.jsonl; assemble_reach() writes data/holdings_reach.tsv:
    by_node, target_node, scope (all|issues:k1,k2|partialUnknown), src, confidence
"""
import json, os, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm, text

DATA = os.path.join(text.WORK, "caselaw-lean-2", "data")
OUT = os.path.join(DATA, "holdings_work")
LIMIT = re.compile(r"(?i)\b(?:to the extent|in part|insofar|in so far|so far as|on other grounds|only (?:as|to|insofar|in)|"
                   r"as to (?:the|its|their)|with respect to|regarding|in that respect|that portion|the holding (?:in|of)|"
                   r"in this respect|on this point|on that point|this point|that part)\b")
SYSTEM = """A later court's passage treats (overrules, disapproves, abrogates, recedes from) an earlier decision. You get the passage and the earlier decision's holdings, numbered.
Say which of those holdings the treatment reaches: scope "all" if the passage overrules the decision without limitation; "some" with the reached holding numbers if the passage limits the treatment to a point, rule or issue that matches particular holdings; "unclear" if it is limited but matches none of the listed holdings. confidence 0-1."""
SCHEMA = {"type": "object", "properties": {"scope": {"type": "string", "enum": ["all", "some", "unclear"]},
                                           "reached": {"type": "array", "items": {"type": "integer"}},
                                           "confidence": {"type": "number"}}, "required": ["scope", "reached", "confidence"]}


def holdings_of():
    h = {}
    for fn in [f"raw_{g}.jsonl" for g in ("scotus", "scotus_plur", "scotus_mini", "scotus_luna", "treat", "treat_mini", "treat_luna")]:
        p = os.path.join(OUT, fn)
        if not os.path.exists(p):
            continue
        for l in open(p, encoding="utf-8"):
            r = json.loads(l)
            hs = (r.get("out") or {}).get("holdings") or []
            if r["nid"] not in h and "error" not in (r.get("out") or {}):
                h[r["nid"]] = hs
    return h


def main():
    hold = holdings_of()
    acts = []
    for l in open(os.path.join(text.WORK, "events_v3", "acts.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        by, tg, pat, win = int(f[0]), int(f[1]), f[2], f[3] if len(f) > 3 else ""
        acts.append((by, tg, pat, win))
    path = os.path.join(OUT, "raw_reach.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(json.loads(l)["by"], json.loads(l)["target"]) for l in open(path, encoding="utf-8")}
    todo = [a for a in acts if LIMIT.search(a[3]) and len(hold.get(a[1]) or []) >= 1 and (a[0], a[1]) not in done]
    seen = set()
    todo = [a for a in todo if not ((a[0], a[1]) in seen or seen.add((a[0], a[1])))]
    print("acts", len(acts), "limited with target holdings", len(todo), flush=True)
    lock = threading.Lock()
    with open(path, "a", encoding="utf-8", newline="\n") as fo:
        def go(a):
            by, tg, pat, win = a
            hl = "\n".join(f"[{i}] ({h['issue']}) {h['proposition']}" for i, h in enumerate(hold[tg]))
            prompt = f"Passage:\n{win}\n\nEarlier decision's holdings:\n{hl}\n\nReturn JSON."
            try:
                out, u = llm.call(prompt, SCHEMA, SYSTEM, max_tokens=400, job="reach")
            except Exception as e:
                return
            with lock:
                fo.write(json.dumps({"by": by, "target": tg, "n": len(hold[tg]), "model": u.get("model"), "out": out}) + "\n")
        with ThreadPoolExecutor(150) as ex:
            list(ex.map(go, todo))
    assemble_reach()


def _conf(o):
    c = o.get("confidence") if isinstance(o, dict) else 0
    try:
        return float(c or 0)
    except (TypeError, ValueError):
        return 0.0


def assemble_reach():
    """Map reached raw holding indices to the issue keys assemble.py gives them (d<nid>.i<idx>, deduplicated by label)."""
    labels = {}
    for fn in [f"raw_{g}.jsonl" for g in ("scotus", "scotus_plur", "scotus_mini", "scotus_luna", "treat", "treat_mini", "treat_luna")]:
        if not os.path.exists(os.path.join(OUT, fn)):
            continue
        for l in open(os.path.join(OUT, fn), encoding="utf-8"):
            r = json.loads(l)
            if r["nid"] in labels or "error" in (r.get("out") or {}):
                continue
            keys, lk = [], {}
            for idx, h in enumerate((r.get("out") or {}).get("holdings") or []):
                lab = re.sub(r"\s+", " ", h.get("issue") or "").strip()[:80].lower()
                keys.append(lk.setdefault(lab, f"d{r['nid']}.i{idx}"))
            labels[r["nid"]] = keys
    with open(os.path.join(DATA, "holdings_reach.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for l in open(os.path.join(OUT, "raw_reach.jsonl"), encoding="utf-8"):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            o = r.get("out") or {}
            keys = labels.get(r["target"], [])
            if o.get("scope") == "all":
                scope = "all"
            elif o.get("scope") == "some" and o.get("reached"):
                ks = sorted({keys[i] for i in o["reached"] if 0 <= i < len(keys)})
                scope = "issues:" + ",".join(ks) if ks else "partialUnknown"
            else:
                scope = "partialUnknown"
            f.write(f"{r['by']}\t{r['target']}\t{scope}\treach:{r.get('model')}\t{_conf(o):.2f}\n")


if __name__ == "__main__":
    if sys.argv[1:] == ["assemble"]:
        assemble_reach()
    else:
        main()
