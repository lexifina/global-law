"""infra10: round10/audit/HOWTO.md from round9/audit/HOWTO.md (exact replacements; the round-9 file is only read)."""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
s = open(os.path.join(C2, "round9", "audit", "HOWTO.md"), "rb").read().decode("utf-8")
assert "\r" not in s
REPS = [
    ("""# Round 9: how to run a blind audit (for track agents)

Tools in `round9/audit/` (agent `infra9`; port of `round8/audit/`, same behaviour, self-test PASS). Run everything
from the `caselaw-lean-2` folder (Git Bash: `cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2`).
Rules first, commands after. What changed against round 8: paths and names (`*9.py`, `AUDITOR_BRIEF9.md`), the base
stage for base rows is `round8/stage/v8e`, the self-test uses `t9:` / `h9:` ids, more telling words in the run-name
guard; the decoy pools are round 8's, copied byte for byte (`decoys9.py` rebuilds them identically).

## Rules (DESIGN9 sections 0 and 3)""",
     """# Round 10: how to run a blind audit (for track agents)

Tools in `round10/audit/` (agent `infra10`; port of `round9/audit/`, same behaviour, self-test PASS). Run everything
from the `caselaw-lean-2` folder (Git Bash: `cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2`).
Rules first, commands after. What changed against round 9: paths and names (`*10.py`, `AUDITOR_BRIEF10.md`), the
base stage for base rows is `round9/stage/v9c`, the self-test uses `t10:` / `h10:` ids, more telling words in the
run-name guard (syllab, recut, bridge, named, bare, footnote, review; state and remand were already there); the decoy
pools are round 9's (= round 8's) plus the items of the round-9 audits `@R9A@r9*/` whose answer is known
(every reader right with extent and high confidence, or every reader wrong as round 7's rule; `decoys10.py --no-r9`
rebuilds round 9's pools byte for byte): type A 944 -> 1,053 decoys, type B 1,902 -> 2,279.

## Rules (DESIGN10 sections 0 and 3)"""),
    ("round9/audit/", "round10/audit/", None),
    ("`make_packs9.py`", "`make_packs10.py`", None),
    ("make_packs9.py", "make_packs10.py", None),
    ("score_audit9.py", "score_audit10.py", None),
    ("more_text9.py", "more_text10.py", None),
    ("decoys9.py", "decoys10.py", None),
    ("selftest9.py", "selftest10.py", None),
    ("selftest9/", "selftest10/", None),
    ("round9/certify9.py", "round10/certify10.py", None),
    ("round9/certify_recog9.py", "round10/certify_recog10.py", None),
    ("round9/certify_opwords9.py", "round10/certify_opwords10.py", None),
    ("round8/stage/v8e", "round9/stage/v9c", None),
    ("round9/out/", "round10/out/", None),
    ("round9/agents/", "round10/agents/", None),
    ("r9<letter><nn>", "r10<letter><nn>", None),
    ("DESIGN9 section 3", "DESIGN10 section 3", None),
    ("""   `make_packs10.py` refuses a path carrying the class name or a telling word (round 8's list plus zone, part, gvr,
   jersey, succes, judgm, implic, pool, phrase, lean, line). Use `round10/audit/r10<letter><nn>/` with your letter:

   | agent | letter | agent | letter |
   |---|---|---|---|
   | fjc9 | f | state9 | s |
   | scdb9 | b | nj9 | j |
   | calpart9 | p | lead | a |
   | shadow9 | k | infra9 | x |

   (e.g. `r9f01`, `r9f02`, ...; never `round10/audit/zone01/`.)""",
     """   `make_packs10.py` refuses a path carrying the class name or a telling word (round 9's list -- round 8's plus
   zone, part, gvr, jersey, succes, judgm, implic, pool, phrase, lean, line -- plus syllab, recut, bridge, named,
   bare, footnote, review). Use `round10/audit/r10<letter><nn>/` with your letter:

   | agent | letter | agent | letter |
   |---|---|---|---|
   | fjc10 | f | stlink10 | t |
   | scdb10 | b | lead | a |
   | syl10 | y | infra10 | x |
   | shadow10 | k | | |

   (e.g. `r10f01`, `r10f02`, ...; never `round10/audit/syllab01/`.)"""),
    ("- `python -X utf8 round10/audit/decoys10.py`: rebuilds the decoy pools (round 8's sources; output identical to the\n  copied pools). Do not rerun during audits.",
     "- `python -X utf8 round10/audit/decoys10.py`: rebuilds the decoy pools (round 9's sources + the round-9 audits;\n  `--no-r9` gives round 9's pools byte for byte). Do not rerun during audits."),
    ("- Agent `infra9` or the lead can run an audit for you: ask the lead.", "- Agent `infra10` or the lead can run an audit for you: ask the lead."),
]
for r in REPS:
    a, b = r[0], r[1]
    n = r[2] if len(r) > 2 else 1
    if n is None:
        s = s.replace(a, b)
    else:
        assert s.count(a) == n, (a[:70], s.count(a))
        s = s.replace(a, b)
s = s.replace("@R9A@", "round9/audit/")
left = [ln for ln in s.splitlines() if "9" in ln and ("round9" in ln or "r9" in ln or "9.py" in ln or "infra9" in ln)
        and "round9/stage/v9c" not in ln and "round9/audit/r9*" not in ln and "round 9's" not in ln
        and "round-9 audits" not in ln and "round9/audit/`" not in ln]
open(os.path.join(C2, "round10", "audit", "HOWTO.md"), "wb").write(s.encode("utf-8"))
print("written round10/audit/HOWTO.md")
for ln in left:
    print("CHECK:", ln)
