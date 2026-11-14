"""Select the hard subset for a second reading by gpt-6.1-sol.

    python -X utf8 hard.py <main results jsonl (under reader_work/)> <out ids.tsv> [max]

Hard = the small model admitted a status-changing act (overruled, disapproved, recededFrom, abrogated,
supersededByEnactment) and either it had to choose among two or more candidate targets, or its confidence was below
0.95, or the sentence names another court acting ("the Court of Appeals in X overruled"), or the act is scoped to
issues. Ordered by confidence (lowest first), capped at `max` (default 20,000).
"""
import gzip, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK  # noqa: E402

STATUS = {"overruled", "disapproved", "recededFrom", "abrogated", "supersededByEnactment"}
OTHER_COURT = re.compile(r"\b(?:the\s+)?(?:supreme\s+court|court\s+of\s+appeals?|appellate\s+division|circuit|legislature|"
                         r"congress)\b[^.]{0,80}\b(?:overruled|disapproved|abrogated|receded|superseded)\b", re.I)


def main():
    res_path, out = sys.argv[1], sys.argv[2]
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
    res = {}
    for line in open(os.path.join(WORK, res_path), encoding="utf-8"):
        r = json.loads(line)
        x = r.get("r")
        if x and x["own_act"] and x["kind"] in STATUS and x["targets"]:
            res[r["id"]] = (r["repo"], x)
    want = {}
    for f in glob.glob(os.path.join(WORK, "res", "*.items.jsonl.gz")):
        for line in gzip.open(f, "rt", encoding="utf-8"):
            i = line[8:line.index('"', 8)]
            if i not in res:
                continue
            it = json.loads(line)
            x = res[i][1]
            sent = it["w"][it["s0"] - it["w0"]:it["s1"] - it["w0"]]
            why = []
            if len(it["targets"]) >= 2:
                why.append("choice")
            if float(x.get("confidence", 0)) < 0.95:
                why.append("lowconf")
            if OTHER_COURT.search(sent):
                why.append("othercourt")
            if x["scope"] == "issues":
                why.append("issues")
            if why:
                want[i] = (float(x.get("confidence", 0)), res[i][0], "+".join(why))
    pick = sorted(want.items(), key=lambda kv: (kv[1][0], kv[0]))[:cap]
    with open(out, "w", encoding="utf-8", newline="\n") as fo:
        for i, (c, repo, why) in pick:
            fo.write(f"{i}\t{repo}\t{why}\n")
    print("status-changing admitted:", len(res), "hard:", len(want), "selected:", len(pick))


if __name__ == "__main__":
    main()
