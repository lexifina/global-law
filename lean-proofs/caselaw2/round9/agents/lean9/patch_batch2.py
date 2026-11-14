"""lean9, round 9 batch 2 (DESIGN9 sections 5 and 7, D9-5): append the cue-table keys and the generator lists.
Run once (it refuses to run twice). The Lean sources are edited with the editor, not here."""
import json
import os
import sys

LP = sys.argv[1]  # the lean-proofs tree (or a staging copy of its layout)
CUES = os.path.join(LP, "tools", "caselaw2", "cues")

IMPLICIT = ["cannot agree", "do not agree", "unpersuaded", "not convinced", "wrongly decided", "incorrectly decided",
            "erroneously decided", "unsound", "erroneous", "incorrect", "mistaken", "undermined", "eroded",
            "discredited", "called into question", "contrary to", "depart from", "departs from"]

p = os.path.join(CUES, "cue_table.json")
s = open(p, encoding="utf-8", newline="").read()
assert "joined_far_max" not in s
T = json.loads(s)
assert s.endswith("\n}") or s.endswith("\n}\n"), repr(s[-5:])
tail = "\n}\n" if s.endswith("\n}\n") else "\n}"
body = s[: -len(tail)]
add = {"_note_round9": "Round 9 (round9/DESIGN9.md sections 5, 7, 8; D9-5, D9-9): joined_far_max (far antecedent "
                       "joined quotes under a joinedFar claim); implicit_reject (cue phrases of a soft row under an "
                       "implicitReject claim); anchor_wide9 (judge-form anchor cues under an anchorWide claim, added to "
                       "anchor_wide without changing it).",
       "joined_far_max": 1200,
       "implicit_reject": IMPLICIT,
       "anchor_wide9": ["district judge", "magistrate judge", "trial judge"]}
parts = []
for k, v in add.items():
    txt = json.dumps({k: v}, indent=1, ensure_ascii=False)
    inner = txt[2:-2]  # drop "{\n" and "\n}"
    parts.append(inner)
s2 = body + ",\n" + ",\n".join(parts) + tail
json.loads(s2)
assert s2.startswith(body)
open(p, "w", encoding="utf-8", newline="").write(s2)
print("cue_table.json: appended", list(add))

g = os.path.join(CUES, "gen_cues.py")
s = open(g, encoding="utf-8", newline="").read()
assert "R9 =" not in s


def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)


rep('''R8_NAT = [("bridgeMaxLen", "bridge_max_len",
           "Round 8: the longest bridge quote (DESIGN8 section 4, step 1).")]
''', '''R8_NAT = [("bridgeMaxLen", "bridge_max_len",
           "Round 8: the longest bridge quote (DESIGN8 section 4, step 1).")]
# round 9 (round9/DESIGN9.md sections 5 and 7): far antecedents, implicit rejection (appended)
R9 = [("implicitRejectCues", "implicit_reject",
       "Round 9: cue phrases a soft row may use under an `implicitReject` claim (DESIGN9 section 7)."),
      ("anchorWide9Cues", "anchor_wide9",
       "Round 9: judge-form anchor cues, used with `anchor_wide` under an `anchorWide` claim (DESIGN9 section 8).")]
R9_NAT = [("joinedFarMax", "joined_far_max",
           "Round 9: the most characters between a far `antecedent` joined quote and the main quote under a "
           "`joinedFar` claim (DESIGN9 section 5).")]
''')
rep('''          "  [" + ", ".join("(%d, %d, %d)" % tuple(t) for t in T["old_circuit"]) + "]", ""]
    o += ["end CaseLaw2.Cert", ""]''', '''          "  [" + ", ".join("(%d, %d, %d)" % tuple(t) for t in T["old_circuit"]) + "]", ""]
    # round 9: appended
    for name, key, doc in R9:
        o += ["/-- %s -/" % doc, "def %s : List String :=" % name, "  " + llist(T[key]), ""]
    for name, key, doc in R9_NAT:
        o += ["/-- %s -/" % doc, "def %s : Nat := %d" % (name, int(T[key])), ""]
    o += ["end CaseLaw2.Cert", ""]''')
rep('''    o.append("OLD_CIRCUIT = %r" % (tuple(tuple(t) for t in T["old_circuit"]),))
    o.append("")''', '''    o.append("OLD_CIRCUIT = %r" % (tuple(tuple(t) for t in T["old_circuit"]),))
    # round 9: appended
    for _, key, _ in R9:
        o.append("%s = %r" % (key.upper(), tuple(T[key])))
    for _, key, _ in R9_NAT:
        o.append("%s = %d" % (key.upper(), int(T[key])))
    o.append("")''')
open(g, "w", encoding="utf-8", newline="").write(s)
print("gen_cues.py: R9, R9_NAT appended")
