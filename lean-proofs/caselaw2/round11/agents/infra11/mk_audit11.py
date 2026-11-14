"""infra11: port round10/audit/ to round11/audit/ by textual replacements (round-10 files are only read).

    python -X utf8 round11/agents/infra11/mk_audit11.py [--force]

Copies audit10lib, make_packs10, score_audit10, more_text10, decoys10, selftest10 (.py) and AUDITOR_BRIEF10.md with
the round-11 names and paths, the base stage round10/stage/v10d, ids t11:/h11: in the self-test, the neutral-name
example r11a01 and the round-11 telling words; decoys11.py also reads the round-10 audits (round10/audit/r10*/,
judged with the same rules as the round-7 / round-9 audits; --no-r10 gives round 10's pools byte for byte). The
decoy pools are then rebuilt by running decoys11.py (not copied). HOWTO.md: mk_howto11.py.
"""
import os
import sys

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
S = os.path.join(C2, "round10", "audit")
D = os.path.join(C2, "round11", "audit")
GEN = [
    ("round10/audit", "round11/audit"),
    ("audit10lib", "audit11lib"), ("make_packs10", "make_packs11"), ("score_audit10", "score_audit11"),
    ("more_text10", "more_text11"), ("decoys10", "decoys11"), ("selftest10", "selftest11"),
    ("AUDITOR_BRIEF10", "AUDITOR_BRIEF11"),
    ('os.path.join(C2, "round9", "stage", "v9c")', 'os.path.join(C2, "round10", "stage", "v10d")'),
    ("round9/stage/v9c", "round10/stage/v10d"),
    ("round10/out/", "round11/out/"), ("round10/certify10.py", "round11/certify11.py"),
    ("t10:st", "t11:st"), ("h10:st", "h11:st"), ("(`t10:` / `h10:` ids", "(`t11:` / `h11:` ids"),
    ("r10a01", "r11a01"),
    ("round-10 audit", "round-11 audit"), ("Round-10 audit", "Round-11 audit"), ("Round-10 blind audit", "Round-11 blind audit"),
    ("round-10 blind audit", "round-11 blind audit"), ("Round-10 auditor briefs", "Round-11 auditor briefs"),
    ("Round 10 blind audit", "Round 11 blind audit"),
    ("certify10 / certify9 / certify8 / certify7", "certify11 / certify10 / certify9 / certify8 / certify7"),
    ("round-10 rows", "round-11 rows"), ("round-10 row ids", "round-11 row ids"), ("not round-10\n", "not round-11\n"),
]
SPECIFIC = {
    "make_packs11.py": [
        ('''              "syllab", "recut", "bridge", "named", "bare", "footnote", "review")''',
         '''              "syllab", "recut", "bridge", "named", "bare", "footnote", "review",
              # round 11 (infra11): words of the round-11 tracks and classes ("order", "dock", "rehear" are above)
              "uncited", "docket", "fedcir", "federal", "circuit", "claims", "list", "rehearing", "banc", "tie",
              "caption")'''),
    ],
    "decoys11.py": [
        ('''"""Round 11 blind audit: the decoy pools (items whose right answer is known from earlier audits). Port of
round9/audit/decoys9.py''', '''"""Round 11 blind audit: the decoy pools (items whose right answer is known from earlier audits). Port of
round10/audit/decoys10.py plus the round-10 audited rows (round10/audit/r10*/, the same reading; ids
`r10:<run>:<item>`, families `r10:<run>:<class>`); with --no-r10 the output is round 10's pools byte for byte.
Round 10: port of round9/audit/decoys9.py'''),
        ('''    python -X utf8 round11/audit/decoys11.py [--min-conf medium] [--out-dir round11/audit] [--no-r7] [--no-r9]
''', '''    python -X utf8 round11/audit/decoys11.py [--min-conf medium] [--out-dir round11/audit] [--no-r7] [--no-r9]
                                              [--no-r10]
'''),
        ('''    ap.add_argument("--no-r9", action="store_true", help="round 10: without the round-9 audits (= round 9's pools)")
''', '''    ap.add_argument("--no-r9", action="store_true", help="round 10: without the round-9 audits (= round 9's pools)")
    ap.add_argument("--no-r10", action="store_true", help="round 11: without the round-10 audits (= round 10's pools)")
'''),
        ('''        for d in r7_pool(a.min_conf, root=os.path.join(A.C2, "round9", "audit"), pat="r9*", tag="r9"):
            if d["type"] in ("A", "B"):
                (pa if d["type"] == "A" else pb).append(d)
''', '''        for d in r7_pool(a.min_conf, root=os.path.join(A.C2, "round9", "audit"), pat="r9*", tag="r9"):
            if d["type"] in ("A", "B"):
                (pa if d["type"] == "A" else pb).append(d)
    if not a.no_r10:  # round 11 (infra11): the round-10 audits, same reading
        for d in r7_pool(a.min_conf, root=os.path.join(A.C2, "round10", "audit"), pat="r10*", tag="r10"):
            if d["type"] in ("A", "B"):
                (pa if d["type"] == "A" else pb).append(d)
'''),
    ],
}
NAMES = {"audit10lib.py": "audit11lib.py", "make_packs10.py": "make_packs11.py", "score_audit10.py": "score_audit11.py",
         "more_text10.py": "more_text11.py", "decoys10.py": "decoys11.py", "selftest10.py": "selftest11.py",
         "AUDITOR_BRIEF10.md": "AUDITOR_BRIEF11.md"}
os.makedirs(D, exist_ok=True)
for src, dst in NAMES.items():
    s = open(os.path.join(S, src), "rb").read().decode("utf-8")
    assert "\r" not in s, src
    for a, b in GEN:
        s = s.replace(a, b)
    for a, b in SPECIFIC.get(dst, []):
        assert s.count(a) == 1, (dst, a[:60], s.count(a))
        s = s.replace(a, b)
    p = os.path.join(D, dst)
    if os.path.exists(p) and "--force" not in sys.argv:
        print("exists, kept (use --force): round11/audit/" + dst)
        continue
    open(p, "wb").write(s.encode("utf-8"))
    print("written round11/audit/" + dst)
