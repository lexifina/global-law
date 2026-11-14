"""state9 part A: rows_raw.jsonl (imp_rows.py) -> rows_plain.jsonl (quote has a plain cue of its soft kind: certifiable
today, claim "-") and rows_claim.jsonl (no plain cue: claim implicitReject, DESIGN9 §7); stats to split_stats.json.
No answer key is read.
"""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)


def main():
    import sys
    sfx = sys.argv[1] if len(sys.argv) > 1 else ""  # "2" for rule v2: rows2_raw.jsonl -> rows2_plain / rows2_claim
    st = collections.Counter()
    plain, claim = [], []
    for line in open(os.path.join(HERE, "rows%s_raw.jsonl" % sfx), encoding="utf-8"):
        r = json.loads(line)
        pc = r.pop("plain_cue", 0)
        st["kind_" + r["kind"]] += 1
        if pc:
            r["rule"] = r["rule"].replace("imp9:", "imp9:plain:")
            plain.append(r)
            st["plain"] += 1
        else:
            r["claim"] = "implicitReject"
            r["rule"] = r["rule"].replace("imp9:", "imp9:claim:")
            claim.append(r)
            st["claim"] += 1
    for name, rs in (("rows%s_plain.jsonl" % sfx, plain), ("rows%s_claim.jsonl" % sfx, claim)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline=NL) as f:
            for r in rs:
                f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "split%s_stats.json" % sfx), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(st), f, indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
