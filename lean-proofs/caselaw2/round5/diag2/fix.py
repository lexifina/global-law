"""diag2: lead's spot-check corrections, written to fixes.jsonl (merge2.py lets it override the shard lines).

39 Brown / Plessy: the 1970 span is Justice Black's solo opinion announcing the judgments in Oregon v. Mitchell,
   not an opinion of the Court -> weak. First clean statement by the Court: Dobbs (2022).
65 Chicago, M., St. P. & P. R. Co. / Lynah: the 1999 span sits in a four-Justice plurality part of Del Monte Dunes
   and says "on other grounds" -> weak; D = 0; fixable by operative words (partial only).
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
got = {}
for fn in sorted(glob.glob(os.path.join(HERE, "shard_*.jsonl"))):
    for line in open(fn, encoding="utf-8"):
        if line.strip():
            o = json.loads(line)
            got[o["idx"]] = o
out = []
o = got[39]
o["later_weak_W"], o["later_weak_date"], o["later_weak_span"] = o["later_W"], o["later_W_date"], o["later_span"]
o["later_W"], o["later_W_date"], o["later_form"] = 6323819, "20220624", "Y overruled X"
o["later_span"] = ("In so doing, the Court overruled the infamous decision in Plessy v. Ferguson, 163 U. S. 537 (1896), "
                   "along with six other Supreme Court precedents that had applied the separate-but-equal rule. "
                   "See Brown, 347 U. S., at 491.")
o["note"] = ("Brown: Plessy's language 'is rejected'; 'in the field of public education the doctrine of separate but "
             "equal has no place' (B, C). Oregon v. Mitchell 1970 is Black, J., alone announcing the judgments (weak); "
             "Casey 1992 @51930 'repudiation of ... Plessy by Brown' (no clean form); first clean Court statement: "
             "Dobbs 2022.")
out.append(o)
o = got[65]
o["later_weak_W"], o["later_weak_date"], o["later_weak_span"] = o["later_W"], o["later_W_date"], o["later_span"]
o["later_W"], o["later_W_date"], o["later_span"], o["later_form"] = "", "", "", ""
o["D"] = 0
o["fixable_by"] = "operative"
out.append(o)
with open(os.path.join(HERE, "fixes.jsonl"), "w", encoding="utf-8", newline="\n") as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("fixes", len(out))
