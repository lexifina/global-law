"""Round 5: write the strata file and the decoy file for a blind audit of a variant's new rows.

    python round5/audit_strata.py <variant> [--opwords]

Population = rows of round5/stage/<variant>/treatments.tsv that the Lean run (round5/out/<variant>/classes.tsv)
classes as below. Strata:
  recog-read-whole    class recognised, read by a Claude reader this round, scope all (these make a case negative)
  recog-read-part     class recognised, read this round, partial / other-grounds scope (partly negative)
  recog-pattern       class recognised, certified by pattern ("overruled on other grounds by"): partly negative
  recog-round4        class recognised, a round-4 witness row that passes the new check
  operative-new       an admitted operativeWords claim (only with --opwords)
  control-self        self-announced rows of round 4 (a control the auditors cannot tell apart by format)
Decoys: reader answers judged NOT to be statements (negation, question, argument, wrong direction, other decision).
Writes round5/audit/in_<variant>_strata.tsv and round5/audit/in_<variant>_decoys.jsonl.
"""
import glob
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
v = sys.argv[1]
opw = "--opwords" in sys.argv
cls = {}
with open(os.path.join(HERE, "out", v, "classes.tsv"), encoding="utf-8") as f:
    next(f)
    for l in f:
        p = l.rstrip("\n").split("\t")
        cls[p[0]] = p
rows = {}
with open(os.path.join(HERE, "stage", v, "treatments.tsv"), encoding="utf-8") as f:
    for l in f:
        p = l.rstrip("\n").split("\t")
        if len(p) >= 16:
            rows[p[0]] = p
strata = {}
for i, c in cls.items():
    r = rows.get(i)
    if r is None:
        continue
    reader, scope = r[14], r[5]
    if c[1] == "recognised":
        if reader == "pattern-r5":
            s = "recog-pattern"
        elif reader == "claude-subagent:recog":
            s = "recog-read-whole" if scope == "all" else "recog-read-part"
        else:
            s = "recog-round4"
    elif opw and c[2] == "operativeWords" and c[3].startswith("ok"):
        s = "operative-whole" if scope == "all" else "operative-part"
    elif c[1] == "selfAnnounced" and c[3] == "ok" and r[14].startswith("gpt") is False and r[7] == "1":
        s = "control-self"
    else:
        continue
    strata.setdefault(s, []).append(i)
rnd = random.Random(5)
out = os.path.join(HERE, "audit", "in_%s_strata.tsv" % v)
with open(out, "w", encoding="utf-8", newline="\n") as f:
    for s in sorted(strata):
        ids = sorted(strata[s])
        if s == "control-self":
            ids = rnd.sample(ids, min(30, len(ids)))
        for i in ids:
            f.write("%s\t%s\n" % (i, s))
        print(s, len(ids))
dec = []
for p in sorted(glob.glob(os.path.join(HERE, "recog", "ans", "ans_pack_*.jsonl"))):
    for l in open(p, encoding="utf-8"):
        try:
            a = json.loads(l)
        except ValueError:
            continue
        if a.get("states") is False and a.get("reason") in ("negation", "question", "argument", "wrongDirection",
                                                            "otherDecision", "refusal", "would"):
            dec.append(a["id"])
rnd.shuffle(dec)
with open(os.path.join(HERE, "audit", "in_%s_decoys.jsonl" % v), "w", encoding="utf-8", newline="\n") as f:
    for i in dec[:60]:
        f.write(json.dumps({"id": i}) + "\n")
print("decoys", len(dec[:60]), "of", len(dec))
