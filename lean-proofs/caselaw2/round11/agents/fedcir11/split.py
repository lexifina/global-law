"""split rows_<tag>.jsonl by anchor cue class: rows_<tag>_lean.jsonl (claim -) / rows_<tag>_trib.jsonl (claim anchorTribunal)"""
import json, sys
t = sys.argv[1]
lean = open("rows_%s_lean.jsonl" % t, "w", encoding="utf-8", newline="\n")
trib = open("rows_%s_trib.jsonl" % t, "w", encoding="utf-8", newline="\n")
n = [0, 0]
for l in open("rows_%s.jsonl" % t, encoding="utf-8"):
    r = json.loads(l)
    if "cue=lean:" in r["note"]:
        lean.write(json.dumps(r, ensure_ascii=False) + "\n"); n[0] += 1
    else:
        r["claim"] = "anchorTribunal"
        trib.write(json.dumps(r, ensure_ascii=False) + "\n"); n[1] += 1
print("lean", n[0], "trib", n[1])
