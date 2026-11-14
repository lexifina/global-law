"""state8: split the rows of answers_to_rows.py (round-7 antecedent tool, reused) into the delta classes.

    python -X utf8 split_rows.py work/rows_raw.jsonl

  rows.jsonl         one-sentence and joined rows of single-target answers (class R8S, rule state8:R8S:<form>)
  rows_multi.jsonl   rows of answers choosing >= 2 targets (one act on several cases: agent multicase's class)
  rows_window.jsonl  plain rows whose evidence is only in the +-400 window (round 7 did not install this form: 0.857)
Rule names carry the repair tag of the item (rescue tag). No answer-key file is read.
"""
import collections, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ans = {}
for p in sorted(glob.glob(os.path.join(HERE, "ans", "*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            ans[r["id"]] = r
tag = {}
for line in open(os.path.join(HERE, "work", "rcands.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    tag[r["id"]] = r["tag"].split(">")[-1].split(":")[0]
out = {k: open(os.path.join(HERE, k + ".jsonl"), "w", encoding="utf-8", newline="\n")
       for k in ("rows", "rows_multi", "rows_window")}
st = collections.Counter()
for line in open(sys.argv[1], encoding="utf-8"):
    row = json.loads(line)
    iid = row["note"].split()[1]
    a = ans.get(iid, {})
    form = row["rule"].split(":")[1]
    t = tag.get(iid, "?")
    row["rule"] = "state8:R8S:%s:%s" % (form, t)
    row["reader"] = "claude-subagent:state8"
    row["note"] = row["note"].replace("antecedent ", "state8 ", 1)
    if len(a.get("targets") or []) >= 2:
        k = "rows_multi"
    elif form == "window":
        k = "rows_window"
    else:
        k = "rows"
    st[k] += 1
    st[k + ":" + form + ":" + t] += 1
    out[k].write(json.dumps(row, ensure_ascii=False) + "\n")
for f in out.values():
    f.close()
for k, v in sorted(st.items()):
    print(v, k)
