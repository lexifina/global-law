"""infra11: round11/audit/HOWTO.md from round10/audit/HOWTO.md (exact replacements; the round-10 file is only read)."""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
s = open(os.path.join(C2, "round10", "audit", "HOWTO.md"), "rb").read().decode("utf-8")
assert "\r" not in s
HEAD_OLD = s[:s.index("## Rules (DESIGN10 sections 0 and 3)")]
HEAD_NEW = """# Round 11: how to run a blind audit (for track agents)

Tools in `round11/audit/` (agent `infra11`; port of `@R10A@`, same behaviour, self-test PASS). Run everything
from the `caselaw-lean-2` folder (Git Bash: `cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2`).
Rules first, commands after. What changed against round 10: paths and names (`*11.py`, `AUDITOR_BRIEF11.md`), the
base stage for base rows is `round10/stage/v10d`, the self-test uses `t11:` / `h11:` ids, more telling words in the
run-name guard (uncited, docket, fedcir, federal, circuit, claims, list, rehearing, banc, tie, caption; order, dock
and rehear were already there); the decoy pools are round 10's plus the items of the round-10 audits
`@R10A@r10*/` whose answer is known (every reader right with extent and high confidence, or every reader
wrong as round 7's rule; `decoys11.py --no-r10` rebuilds round 10's pools byte for byte): type A 1,053 -> 1,056
decoys, type B 2,279 -> 3,212. Order-list nodes (DESIGN11 section 4): with `R11_NODES=round11/data_orders` (or
`--nodes`, see section 1) the packs and `more_text11.py` show the order node's own text (`round11/nodes11.py`).
`--exclude <run>/sample.tsv` (round 11 fix) excludes the sample's row ids AND every row with the same identity (table,
by node, target node, kind) as one of its real rows, so a round-10 sample (`h10:` / `t10:` ids) excludes the same row
re-certified under an `h11:` / `t11:` id; the count is printed ("rows excluded by identity ... only"). Exclude every
earlier sample of the class, round-10 runs included.

"""
REPS = [
    (HEAD_OLD, HEAD_NEW, 1),
    ("## Rules (DESIGN10 sections 0 and 3)", "## Rules (DESIGN11 sections 0 and 3)", 1),
    ("round10/audit/", "round11/audit/", None),
    ("make_packs10.py", "make_packs11.py", None),
    ("more_text10.py", "more_text11.py", None),
    ("score_audit10.py", "score_audit11.py", None),
    ("decoys10.py", "decoys11.py", None),
    ("selftest10.py", "selftest11.py", None),
    ("selftest10/", "selftest11/", None),
    ("r10<letter><nn>", "r11<letter><nn>", None),
    ("""   `make_packs11.py` refuses a path carrying the class name or a telling word (round 9's list -- round 8's plus
   zone, part, gvr, jersey, succes, judgm, implic, pool, phrase, lean, line -- plus syllab, recut, bridge, named,
   bare, footnote, review). Use `round11/audit/r11<letter><nn>/` with your letter:

   | agent | letter | agent | letter |
   |---|---|---|---|
   | fjc10 | f | stlink10 | t |
   | scdb10 | b | lead | a |
   | syl10 | y | infra10 | x |
   | shadow10 | k | | |

   (e.g. `r10f01`, `r10f02`, ...; never `round11/audit/syllab01/`.)""",
     """   `make_packs11.py` refuses a path carrying the class name or a telling word (round 10's list -- round 8's plus
   zone, part, gvr, jersey, succes, judgm, implic, pool, phrase, lean, line, syllab, recut, bridge, named, bare,
   footnote, review -- plus uncited, docket, fedcir, federal, circuit, claims, list, rehearing, banc, tie, caption).
   Use `round11/audit/r11<letter><nn>/` with your letter (DESIGN11 section 3):

   | agent | letter | agent | letter |
   |---|---|---|---|
   | stlink11 | t | fjc11 | f |
   | fedcir11 | c | scdb11 | b |
   | shadow11 | k | lead | a |
   | orders11 | o | infra11 | x |

   (e.g. `r11t01`, `r11t02`, ...; never `round11/audit/caption01/`.)""", 1),
    ("Certify first (`round10/certify10.py`, `round10/certify_recog10.py`, `round10/certify_opwords10.py`), then:",
     "Certify first (`round11/certify11.py`, `round11/certify11_claims.py` for joinedFar / implicitReject rows,\n"
     "`round11/certify_recog11.py`, `round11/certify_opwords11.py`), then:", 1),
    ("--cert round10/agents/<you>/", "--cert round11/agents/<you>/", None),
    ("--pairs round10/agents/<you>/pairs.tsv", "--pairs round11/agents/<you>/pairs.tsv", 1),
    ("--lean-certs round10/out/<variant>/certs.tsv", "--lean-certs round11/out/<variant>/certs.tsv", 1),
    ("#   a certify9 folder holds both tables", "#   a certify11 folder holds both tables", 1),
    ("either row as --cert (the base stage round9/stage/v9c for base rows).",
     "either row as --cert (the base stage round10/stage/v10d for base rows).", 1),
    ("--cert round9/stage/v9c --n 40", "--cert round10/stage/v10d --n 40", 1),
    ("(DESIGN10 section 3;", "(DESIGN11 section 3;", 1),
    ("""- `python -X utf8 round11/audit/decoys11.py`: rebuilds the decoy pools (round 9's sources + the round-9 audits;
  `--no-r9` gives round 9's pools byte for byte). Do not rerun during audits.""",
     """- `python -X utf8 round11/audit/decoys11.py`: rebuilds the decoy pools (round 10's sources + the round-10 audits;
  `--no-r10` gives round 10's pools byte for byte). Do not rerun during audits.""", 1),
    ("- Agent `infra10` or the lead can run an audit for you: ask the lead.",
     "- Agent `infra11` or the lead can run an audit for you: ask the lead.", 1),
]
for a, b, n in REPS:
    c = s.count(a)
    assert (c == n) if n else c >= 1, (a[:70], c, n)
    s = s.replace(a, b)
for w in ("round10/", "infra10", "r10", "DESIGN10"):
    for line in s.splitlines():
        if w in line and "round10/stage/v10d" not in line and "round10/audit/r10*" not in line and "r10*" not in line \
                and "round10/audit/`" not in line and "--no-r10" not in line:
            print("CHECK:", line)
s = s.replace("@R10A@", "round10/audit/")
open(os.path.join(C2, "round11", "audit", "HOWTO.md"), "wb").write(s.encode("utf-8"))
print("written round11/audit/HOWTO.md")
