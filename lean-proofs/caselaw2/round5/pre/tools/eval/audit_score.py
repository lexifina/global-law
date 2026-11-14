"""Score the blind audits against their keys (after the readers have answered).

    python tools/caselaw2/eval/audit_score.py gold-notes|notes-blind

gold-notes: reads eval/audits/gold-notes/out_*.json and key.json and reports agreement on target, treating decision,
            kind and scope, per kind.
notes-blind: reads eval/audits/notes-blind/out_*.json and key.json and reports how often the named decision itself
            states the treatment (express/implicit/mentions/absent), per kind and scope, and v1's agreement on the same
            pairs (lean-out-v3): of the notes v1 agreed with, how many the decision states; of the express ones, how
            many v1 found. When out/status.tsv exists it does the same for v2.
Writes eval/audits/<audit>/score.json.
"""
import collections, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "caselaw"))
from graph import norm_cite  # noqa: E402
from score import C2, W, iint, rows  # noqa: E402


def load(audit):
    d = os.path.join(C2, "eval", "audits", audit)
    ans = {}
    for f in glob.glob(os.path.join(d, "out_*.json")):
        for a in json.load(open(f, encoding="utf-8")):
            ans[int(a["id"])] = a
    kf = os.path.join(d, "key_rebuilt.json") if os.path.exists(os.path.join(d, "key_rebuilt.json")) else         os.path.join(d, "key.json")  # key_rebuilt: the same notes looked up in the rebuilt gold (absent = dropped)
    key = {int(k["id"]): k for k in json.load(open(kf, encoding="utf-8"))}
    return d, ans, key


def cite_node(c, idx):
    m = re.search(r"(\d{1,4})\s+([A-Za-z][A-Za-z0-9.'’ ]{0,30}?)\s+(\d{1,5})", c or "")
    if not m:
        return None
    k = norm_cite(f"{m.group(1)} {m.group(2)} {m.group(3)}")
    return idx.get(k) if k else None


def gold_notes():
    d, ans, key = load("gold-notes")
    idx = {}
    for line in open(os.path.join(W, "graph", "cite_index.tsv"), encoding="utf-8"):
        k, v = line.rstrip("\n").split("\t")
        idx[k] = int(v)
    per = collections.defaultdict(collections.Counter)
    bad = []
    for i, k in key.items():
        a = ans.get(i)
        if a is None:
            per[k["kind"]]["unanswered"] += 1
            continue
        c = per[k["kind"]]
        c["n"] += 1
        if a.get("kind") == "notANote":
            c["notANote"] += 1
            bad.append((i, k["kind"], "notANote", a.get("why", "")))
            continue
        tn = cite_node(a.get("target_cite"), idx)
        t_ok = tn is not None and tn == iint(k["target"])
        if not t_ok:  # same volume and page as the key's citation (reporter abbreviations differ)
            m1 = re.match(r"(\d+)\D.*?(\d+)\s*$", a.get("target_cite") or "")
            m2 = re.match(r"(\d+)\D.*?(\d+)\s*$", (k.get("target_meta") or {}).get("cite", ""))
            t_ok = bool(m1 and m2 and m1.groups() == m2.groups())
        c["target_ok"] += t_ok
        c["target_unresolvable"] += tn is None
        bkey, bans = iint(k["by"]), a.get("by_cite", "-")
        if bkey < 0:
            b_ok = bans in ("-", "", None) or cite_node(bans, idx) is None
        else:
            b_ok = cite_node(bans, idx) == bkey
        c["by_ok"] += b_ok
        c["kind_ok"] += a.get("kind") == k["kind"]
        c["scope_ok"] += a.get("scope") == k["scope"]
        c["all_ok"] += t_ok and b_ok and a.get("kind") == k["kind"]
        if not (t_ok and b_ok and a.get("kind") == k["kind"]):
            bad.append((i, k["kind"], f"t={t_ok} b={b_ok} kind={a.get('kind')}", a.get("why", "")))
    tot = collections.Counter()
    for c in per.values():
        tot.update(c)
    res = {"per_kind": per, "total": tot, "disagreements": bad}
    json.dump(res, open(os.path.join(d, "score.json"), "w", encoding="utf-8", newline="\n"), indent=1, default=dict)
    return res


def notes_blind():
    d, ans, key = load("notes-blind")
    v1 = set()
    for l in open(os.path.join(W, "lean-out-v3", "00.acts.tsv"), encoding="utf-8"):
        y, x, v = l.rstrip("\n").split("\t")
        if v == "1":
            v1.add((int(y), int(x)))
    v2 = None
    st = rows(os.path.join(C2, "out", "status.tsv"),
              ["node", "issue", "holding", "from", "to", "status", "kind", "by", "conduct_from", "firm"])
    if st is not None:
        v2 = {(iint(r["by"]), iint(r["node"])) for r in st if r.get("status") not in ("good", "-", "")}
    verd = collections.Counter()
    per = collections.defaultdict(collections.Counter)
    models = {"v1": v1, "v2": v2}
    mres = {m: collections.Counter() for m in models if models[m] is not None}
    for i, k in key.items():
        a = ans.get(i)
        if a is None:
            verd["unanswered"] += 1
            continue
        v = a.get("verdict", "?")
        verd[v] += 1
        per[f"{k['kind']}:{k['scope']}"][v] += 1
        pair = (iint(k["by_node"]), iint(k["target_node"]))
        for m, s in models.items():
            if s is None:
                continue
            agree = pair in s
            mres[m][f"model_agrees:{v}"] += agree
            mres[m][f"model_misses:{v}"] += not agree
    out = {"verdicts": verd, "per_kind_scope": per}
    for m, c in mres.items():
        ag = sum(n for k_, n in c.items() if k_.startswith("model_agrees"))
        out[m] = {**c, "agreements": ag,
                  "agreements_stated_express": c["model_agrees:express"],
                  "express_found": f"{c['model_agrees:express']}/{verd['express']}"}
    json.dump(out, open(os.path.join(d, "score.json"), "w", encoding="utf-8", newline="\n"), indent=1, default=dict)
    return out


if __name__ == "__main__":
    r = gold_notes() if sys.argv[1] == "gold-notes" else notes_blind()
    print(json.dumps(r, indent=1, default=dict)[:5000])
