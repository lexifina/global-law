"""notarget: label the rows of answers_to_rows.py (round-7 antecedent tool, reused) for the delta class NT8.

    python -X utf8 split_rows.py work/rows_raw.jsonl

  rows.jsonl         one-sentence and joined rows (class NT8, rule notarget:NT8:<form>:<tag>:<nt>, nt = 1 or m for
                     answers choosing one / several targets)
  rows_window.jsonl  plain rows whose evidence is only in the +-400 window (form not installed in round 7)
No answer-key file is read.
"""
import collections, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ans = {}
for p in sorted(glob.glob(os.path.join(HERE, "ans", "*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            ans[r["id"]] = r
tag = {}
for line in open(os.path.join(HERE, "work", "ntcands.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    tag[r["id"]] = r["tag"].split(">")[-1].split(":")[0]
out = {k: open(os.path.join(HERE, k + ".jsonl"), "w", encoding="utf-8", newline="\n")
       for k in ("rows", "rows_window")}
st = collections.Counter()
for line in open(sys.argv[1], encoding="utf-8"):
    row = json.loads(line)
    iid = row["note"].split()[1]
    a = ans.get(iid, {})
    form = row["rule"].split(":")[1]
    t = tag.get(iid, "?")
    nt = "m" if len(a.get("targets") or []) >= 2 else "1"
    row["rule"] = "notarget:NT8:%s:%s:%s" % (form, t, nt)
    row["reader"] = "claude-subagent:notarget"
    row["note"] = row["note"].replace("antecedent ", "notarget ", 1)
    k = "rows_window" if form == "window" else "rows"
    st[k] += 1
    st[k + ":" + form + ":" + t + ":" + nt] += 1
    out[k].write(json.dumps(row, ensure_ascii=False) + "\n")
for f in out.values():
    f.close()
for k, v in sorted(st.items()):
    print(v, k)
