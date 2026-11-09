"""Stage-wise benchmark of the detectors' core steps against model-labelled gold sets drawn at random from every corpus.

python bench/stage_bench.py sample  [--per 40]    draw samples      -> bench/data/{refs,placeholders,limits}.jsonl
python bench/stage_bench.py label                 label with a model (gold, resumable) -> bench/data/*_gold.jsonl
python bench/stage_bench.py score                 score the current code -> bench/out/stage_scores.json (+ printed table)

Stages:
  refs          same-act provision references in a line of law  (ingest/refscan.refs + the external-act filter)
  placeholders  is a short provision only a repeal placeholder   (detectors/placeholder_ref.GONE logic)
  limits        end dates of a rule's application in a line      (ingest/textscan.limits)
Gold labels are model judgements (gpt-6.1-sol), spot-checked by hand; scores are therefore estimates.
"""
from __future__ import annotations
import argparse, json, random, re, subprocess, sys, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ingest")); sys.path.insert(0, str(ROOT / "triage")); sys.path.insert(0, str(ROOT / "detectors"))
from common import CORPUS, FLAGS, pins  # noqa: E402

DATA, OUT = ROOT / "bench" / "data", ROOT / "bench" / "out"
SEED = 7
EXCLUDE = ("united-kingdom", "romania")
YEAR = re.compile(r"\b(19[5-9]\d|20[0-3]\d)\b")
DATEISH = re.compile(r"(?i)\b\d{1,2}[./-]\d{1,2}[./-](19|20)\d\d\b|\b(19|20)\d\d-\d\d-\d\d\b|\b\d{1,2}(\.|º|er)?\s+[a-zäöüéèûôáíóúñçãõ]{3,12}\.?\s+(de\s+)?(19|20)\d\d\b|"
                     r"\b[a-z]{3,9}\.?\s+\d{1,2},?\s+(19|20)\d\d\b")


def tree(c):
    ls = subprocess.run(["git", "-C", str(CORPUS / f"{c['repo']}.git"), "ls-tree", "-r", "-z", "--format=%(objectname) %(path)", c["sha"]],
                        capture_output=True, creationflags=FLAGS).stdout.decode("utf-8", "replace").split("\0")
    return [x.split(" ", 1) for x in ls if x.endswith(".md") and not x.rsplit("/", 1)[-1].lower().startswith(("readme", "index", "reproduce", "license", "changelog"))]


def cat(repo, shas):
    p = subprocess.run(["git", "-C", str(CORPUS / f"{repo}.git"), "cat-file", "--batch"], input=("\n".join(shas) + "\n").encode(),
                       capture_output=True, creationflags=FLAGS).stdout
    out, pos = [], 0
    for _ in shas:
        nl = p.index(b"\n", pos); hdr = p[pos:nl].split()
        if len(hdr) < 3 or hdr[1] != b"blob":
            out.append(""); pos = nl + 1; continue
        size = int(hdr[2]); out.append(p[nl + 1: nl + 1 + size].decode("utf-8", "replace")); pos = nl + 2 + size
    return out


def sample(per: int):
    random.seed(SEED)
    DATA.mkdir(parents=True, exist_ok=True)
    refs, holders, limits = [], [], []
    for c in pins()["corpora"]:
        if c["repo"].startswith(EXCLUDE) or not (CORPUS / f"{c['repo']}.git").exists():
            continue
        files = tree(c)
        if len(files) < 20:
            continue
        pick = random.sample(files, min(len(files), 400))
        texts = cat(c["repo"], [s for s, _ in pick])
        lines_ref, lines_lim, short = [], [], []
        for (sha, path), t in zip(pick, texts):
            body = "\n".join(l for l in t.splitlines()[1:] if l.strip())
            if 0 < len(body) < 400:
                short.append({"corpus": c["path"], "repo": c["repo"], "path": path, "text": t[:600]})
            for l in t.splitlines():
                l = l.strip()
                if len(l) < 25 or l.startswith(("#", "|")) or len(l) > 900:
                    continue
                if re.search(r"\d", l):
                    lines_ref.append({"corpus": c["path"], "repo": c["repo"], "path": path, "text": l})
                if YEAR.search(l) and DATEISH.search(l):
                    lines_lim.append({"corpus": c["path"], "repo": c["repo"], "path": path, "text": l})
        refs += random.sample(lines_ref, min(per, len(lines_ref)))
        limits += random.sample(lines_lim, min(per // 2, len(lines_lim)))
        holders += random.sample(short, min(per // 2, len(short)))
    for name, rows in (("refs", refs), ("limits", limits), ("placeholders", holders)):
        with (DATA / f"{name}.jsonl").open("w", encoding="utf-8") as fh:
            for i, r in enumerate(rows):
                fh.write(json.dumps({"i": i, **r}, ensure_ascii=False) + "\n")
        print(name, len(rows))


PROMPTS = {
    "refs": ("For each numbered line of law, list every reference it makes to a numbered provision (article, section, §, "
             "paragraph-level unit such as 'Art. 12', '§ 3a', 'artículo 45 bis', 'section 10(2)', 'madde 7') OF THE SAME ACT "
             "the line belongs to. Exclude references that belong to another act, code, regulation, directive or treaty (e.g. "
             "'§ 12 BGB', 'article 5 of Regulation (EU) 2016/679', 'artículo 3 de la Ley 30/1992'), and exclude numbers that are not "
             "provision references (amounts, dates, list items, years). Give the top-level unit number only, with its letter or "
             "Latin suffix ('12', '3a', '45bis'), not sub-units. If unsure whether a reference is to the same act, include it "
             "only if no other act is named nearby.",
             {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {"items": {"type": "array", "items": {
                 "type": "object", "additionalProperties": False, "required": ["i", "refs"], "properties": {
                     "i": {"type": "integer"}, "refs": {"type": "array", "items": {"type": "string"}}}}}}}),
    "placeholders": ("For each numbered provision text, say whether the provision is ONLY a repeal or empty placeholder (its "
                     "content is gone: 'Repealed', '(weggefallen)', 'Derogado', 'Revogado', '[Omitted]', 'Abrogé', 'Mülga', "
                     "'(void)', 'sin contenido' and equivalents in any language), as opposed to a provision with operative text.",
                     {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {"items": {"type": "array", "items": {
                         "type": "object", "additionalProperties": False, "required": ["i", "placeholder"], "properties": {
                             "i": {"type": "integer"}, "placeholder": {"type": "boolean"}}}}}}),
    "limits": ("For each numbered line of law, list the dates (ISO yyyy-mm-dd) that the line states as the END of a rule's "
               "application or validity: 'until 31 December 2025', 'bis zum 30. Juni 2024', 'hasta el 31 de diciembre de 2023', "
               "'jusqu'au 31 décembre 2026', 'no later than'-style deadlines do NOT count unless they end the rule's own "
               "application. Exclude dates of enactment, publication, entry into force, and past events. Empty list if none.",
               {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {"items": {"type": "array", "items": {
                   "type": "object", "additionalProperties": False, "required": ["i", "dates"], "properties": {
                       "i": {"type": "integer"}, "dates": {"type": "array", "items": {"type": "string"}}}}}}}),
}


def label():
    from llm import call
    for stage, (instr, schema) in PROMPTS.items():
        src = [json.loads(l) for l in (DATA / f"{stage}.jsonl").open(encoding="utf-8")]
        gp = DATA / f"{stage}_gold.jsonl"
        done = {json.loads(l)["i"] for l in gp.open(encoding="utf-8")} if gp.exists() else set()
        todo = [r for r in src if r["i"] not in done]
        batches = [todo[k:k + 10] for k in range(0, len(todo), 10)]
        lock = threading.Lock()

        def work(n, b):
            body = "\n\n".join(f"[{r['i']}] ({r['corpus']}, {r['path']})\n{r['text']}" for r in b)
            res = call(f"{instr}\n\n{body}", schema=schema, provider="azure-uk" if n % 2 else "azure", max_tokens=3000)
            return res["json"]["items"]

        with ThreadPoolExecutor(24) as ex, gp.open("a", encoding="utf-8") as fh:
            for fu in as_completed([ex.submit(work, n, b) for n, b in enumerate(batches)]):
                try:
                    items = fu.result()
                except Exception as e:
                    print("error", str(e)[:150]); continue
                with lock:
                    for it in items:
                        fh.write(json.dumps(it, ensure_ascii=False) + "\n")
        print(stage, "labelled", len(todo))


def gold(stage):
    g = {}
    for l in (DATA / f"{stage}_gold.jsonl").open(encoding="utf-8"):
        try:
            r = json.loads(l); g[r["i"]] = r
        except ValueError:
            pass
    return g


def normkey(s):
    m = re.match(r"(?i)\s*(\d{1,4})\s*[-‑ ]?([a-z]{0,8})", s.replace("º", "").replace("°", ""))
    return f"{int(m.group(1))}{m.group(2).lower()}" if m else None


SUB = r"(?:sub-?sections?|(?:sub)?paragraphs?|paras?\.|clauses?|sub-?clauses?|items?|absatz|abs\.|lid|leden|alinéas?|alineas?|párrafos?|incisos?|fracci[oó]n|ods\.|odst\.|odstav\w*|παρ\.?|stk\.|punto|numerale?s?|stav\w*|stavk\w*|stk\.|第[一二三四五六七八九十\d]+項|regulations?\s+\d+\s*\()"


def heading_only(text, k):
    """gold sometimes counts the provision's own heading ('Artículo 148.-', 'Madde 6 –', '§ 63.') as a reference."""
    num = re.match(r"\d+", k).group(0)
    occ = list(re.finditer(rf"(?<![\d.]){num}(?![\d])", text))
    head = re.match(rf"^\W{{0,4}}(?:[^\W\d_]+\.?\s*)?{num}\s*[a-z]?\s*(?:[.\-–—:º°]|$)", text.strip(), re.I)
    return bool(occ) and len(occ) == 1 and bool(head)


def subunit_only(text, k):
    """gold sometimes lists in-provision sub-units ('subsection (2)'); those are not provision-level references."""
    num = re.match(r"\d+", k).group(0)
    occ = list(re.finditer(rf"(?<![\d.]){num}(?![\d])", text))
    if not occ:
        return False
    return all(text[max(0, o.start() - 1):o.start()] == "(" or re.search(SUB + r"\s*\(?\s*(?:\d+\)?\s*(?:,|and|to|or|y|et)\s*\(?)?$",
                                                                          text[max(0, o.start() - 40):o.start()], re.I) for o in occ)


def predict_refs(text):
    import refscan
    from placeholder_ref import EXTERNAL
    keys = set()
    for k, ctx, tail in refscan.refs("# x\n" + text):
        if not EXTERNAL.match(tail):
            keys.add(k)
    return keys


def predict_placeholder(text):
    import placeholder_ref as P
    if hasattr(P, "is_placeholder"):
        return P.is_placeholder(text)
    body = re.sub(r"(?m)^#.*$", "", text).strip()           # the original rule
    head = text.split("\n", 1)[0]
    return bool((len(body) < 220 and P.GONE.search(body or head)) or (not body and P.GONE.search(head)))


def predict_limits(text):
    from textscan import limits
    try:
        return {d for d, _ in limits(text, deadlines=False)}
    except TypeError:                                         # the original code has no deadline switch
        return {d for d, _ in limits(text)}


def score():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    for stage in PROMPTS:
        src = {r["i"]: r for r in (json.loads(l) for l in (DATA / f"{stage}.jsonl").open(encoding="utf-8"))}
        g = gold(stage)
        per = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
        misses = []
        for i, r in src.items():
            if i not in g:
                continue
            j = r["corpus"].split("/")[0]
            if stage == "refs" and (re.search(r"\.md|\s\|\s", r["text"])):
                continue  # index listings and table headings, not law text
            if "**" in r["text"] or re.search(r"(^|/)[A-Z][A-Z_-]+\.md$", r["path"]) or re.search(r"(?i)\b(corpus|LiberLII|LesLII|archive|capture)\b", r["text"]):
                continue  # the corpus builders' own notes, not law
            if stage == "refs":
                truth = {k for k in (normkey(x) for x in g[i]["refs"]) if k and not subunit_only(r["text"], k) and not heading_only(r["text"], k)}
                pred = predict_refs(r["text"])
            elif stage == "limits":
                truth = {d[:10] for d in g[i]["dates"] if re.match(r"\d{4}-\d\d-\d\d", d)}
                pred = predict_limits(r["text"])
            else:
                truth = {"y"} if g[i]["placeholder"] else set()
                pred = {"y"} if predict_placeholder(r["text"]) else set()
            tp, fp, fn = len(truth & pred), len(pred - truth), len(truth - pred)
            for key in (j, "ALL"):
                per[key]["tp"] += tp; per[key]["fp"] += fp; per[key]["fn"] += fn
            if fn or fp:
                misses.append({"i": i, "corpus": r["corpus"], "text": r["text"][:300], "gold": sorted(truth), "pred": sorted(pred)})
        def pr(d):
            p = d["tp"] / (d["tp"] + d["fp"]) if d["tp"] + d["fp"] else None
            rc = d["tp"] / (d["tp"] + d["fn"]) if d["tp"] + d["fn"] else None
            return {**d, "precision": p, "recall": rc}
        report[stage] = {k: pr(v) for k, v in per.items()}
        (OUT / f"{stage}_misses.jsonl").write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in misses), encoding="utf-8")
        a = report[stage]["ALL"]
        f = lambda x: "  n/a" if x is None else f"{x:5.1%}"
        print(f"{stage:13s} precision {f(a['precision'])}  recall {f(a['recall'])}  (tp {a['tp']}, fp {a['fp']}, fn {a['fn']})")
        worst = sorted(((k, v) for k, v in report[stage].items() if k != "ALL" and (v["tp"] + v["fn"]) >= 5 and v["recall"] is not None),
                       key=lambda kv: kv[1]["recall"])[:6]
        print("   lowest recall:", ", ".join(f"{k} {v['recall']:.0%} ({v['tp']}/{v['tp'] + v['fn']})" for k, v in worst))
    (OUT / "stage_scores.json").write_text(json.dumps(report, indent=1), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["sample", "label", "score"]); ap.add_argument("--per", type=int, default=40)
    ap.add_argument("--set", default="tune", help="tune (seed 7, used while improving the code) or holdout (seed 11, never tuned on)")
    ap.add_argument("--code", default="current", help="current, or a folder holding older copies of refscan/textscan/placeholder_ref to score")
    a = ap.parse_args()
    if a.set == "holdout":
        SEED, DATA = 11, ROOT / "bench" / "data_holdout"
        OUT = ROOT / "bench" / ("out_holdout" if a.code == "current" else "out_holdout_" + Path(a.code).name)
    elif a.code != "current":
        OUT = ROOT / "bench" / ("out_" + Path(a.code).name)
    if a.code != "current":
        sys.path.insert(0, str(Path(a.code).resolve()))
    {"sample": lambda: sample(a.per), "label": label, "score": score}[a.cmd]()
