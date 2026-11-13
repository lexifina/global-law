"""Score a blind audit: precision per kind and for target resolution, with Wilson 95% intervals.

    python -X utf8 audit_score.py <pack.jsonl> <verdicts.jsonl> [<pack2> <verdicts2> ...]

Verdict lines: {"audit_id", "own_act": "yes|no|unclear", "kind": "<kind or none>", "target": "yes|no|unclear",
"scope": "<all|issues|partialUnknown|otherGrounds|unknown>", "note": "..."}.
A treatment row is correct when the reviewer says own_act=yes, the reviewer's kind equals the claimed kind, and
target=yes. Target precision is measured over rows the reviewer judged own_act=yes. For rejected candidates, the
reader's rejection is right unless the reviewer finds an own act about a listed candidate.
"""
import collections, json, math, sys


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, (c - r) / d, (c + r) / d)


def fmt(k, n):
    p, lo, hi = wilson(k, n)
    return f"{k}/{n} = {p:.3f} [{lo:.3f}, {hi:.3f}]"


def main():
    a = sys.argv[1:]
    packs, verd = {}, {}
    for i in range(0, len(a), 2):
        for l in open(a[i], encoding="utf-8"):
            r = json.loads(l)
            packs[r["audit_id"]] = r
        for l in open(a[i + 1], encoding="utf-8"):
            l = l.strip()
            if l:
                v = json.loads(l)
                verd[v["audit_id"]] = v
    by = collections.defaultdict(lambda: [0, 0])
    tgt = [0, 0]
    act = [0, 0]
    scope = [0, 0]
    rej = [0, 0]
    hist = collections.defaultdict(lambda: [0, 0])
    errs = collections.Counter()
    for i, p in packs.items():
        v = verd.get(i)
        if v is None:
            errs["no-verdict"] += 1
            continue
        if p["type"] == "treatment":
            k = p["claim"]["kind"]
            ok_act = v["own_act"] == "yes"
            ok = ok_act and v.get("kind") == k and v.get("target") == "yes"
            by[k][1] += 1
            by[k][0] += ok
            by["ALL"][1] += 1
            by["ALL"][0] += ok
            act[1] += 1
            act[0] += ok_act
            if ok_act:
                tgt[1] += 1
                tgt[0] += v.get("target") == "yes"
                if v.get("kind") == k:
                    scope[1] += 1
                    scope[0] += v.get("scope", "").split(":")[0] == p["claim"]["scope"].split(":")[0]
            if not ok:
                errs["treat:" + ("not-own-act" if not ok_act else "kind" if v.get("kind") != k else "target")] += 1
        elif p["type"] == "candidate":
            rej[1] += 1
            rej[0] += not (v["own_act"] == "yes" and v.get("target") == "yes")
        elif p["type"] == "history":
            k = p["claim"]["kind"]
            ok = v["own_act"] == "yes" and v.get("kind") == k and v.get("target") == "yes"
            hist[k][1] += 1
            hist[k][0] += ok
            hist["ALL"][1] += 1
            hist["ALL"][0] += ok
    out = {"treatment_precision_by_kind": {k: fmt(*x) for k, x in sorted(by.items())},
           "own_act_precision": fmt(*act), "target_precision_given_own_act": fmt(*tgt),
           "scope_agreement_given_act_and_kind": fmt(*scope), "rejection_precision": fmt(*rej),
           "history_precision_by_kind": {k: fmt(*x) for k, x in sorted(hist.items())}, "errors": dict(errs)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
