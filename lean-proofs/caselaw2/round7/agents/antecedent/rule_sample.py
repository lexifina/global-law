"""Round 7, agent `antecedent`: a random sample of tier-A candidates with the deterministic rule's picks, for the
agent's own reading (step 2: the rule's precision).

    python -X utf8 rule_sample.py [--n 40] [--seed 11] [--tier A] -> rule_sample_<tier>.md
"""
import argparse, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anterule as R  # noqa: E402

NL = chr(10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--tier", default="A")
    a = ap.parse_args()
    cs = [json.loads(l) for l in open(os.path.join(HERE, "sel_%s.jsonl" % a.tier), encoding="utf-8")]
    sm = random.Random(a.seed).sample(cs, min(a.n, len(cs)))
    out = []
    for k, c in enumerate(sm, 1):
        rel = c["s"][0] - c["wt0"]
        r = R.rule(c)
        out.append("## %d. %s  %s (%s)" % (k, c["id"], c["by_name"][:70], c["by_date"]))
        out.append("CTX: " + c["wt"][max(0, rel - 700):rel].replace(NL, " / "))
        out.append("ACT: " + c["act"])
        for x in c["targets"]:
            mark = "*" if r and x["t"] in r["targets"] else " "
            out.append("  %s %s %s %s | %s | gap %d | base %s" % (mark, x["where"], x["t"], x["name"][:60], x["ev"],
                                                                 c["s"][0] - x["span"][1], ",".join(x["base"]) or "-"))
        out.append("RULE: %s" % (json.dumps({k2: r[k2] for k2 in ("kind", "scope", "targets")}) if r else "none"))
        out.append("")
    with open(os.path.join(HERE, "rule_sample_%s.md" % a.tier), "w", encoding="utf-8", newline=NL) as f:
        f.write(NL.join(out))
    print(len(sm))


if __name__ == "__main__":
    main()
