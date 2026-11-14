"""infra9: port round8/audit/ to round9/audit/ by textual replacements (round-8 files are only read).

    python -X utf8 round9/agents/infra9/mk_audit9.py

Copies audit8lib, make_packs8, score_audit8, more_text8, decoys8, selftest8 (.py) and AUDITOR_BRIEF8.md with the
round-9 names and paths, the base stage round8/stage/v8e, ids t9:/h9: in the self-test, the neutral-name example r9a01
and extra telling words for the round-9 classes; copies the decoy pools byte for byte. HOWTO.md is written by hand.
"""
import os
import shutil

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
S = os.path.join(C2, "round8", "audit")
D = os.path.join(C2, "round9", "audit")
GEN = [
    ("round8/audit", "round9/audit"),
    ("audit8lib", "audit9lib"), ("make_packs8", "make_packs9"), ("score_audit8", "score_audit9"),
    ("more_text8", "more_text9"), ("decoys8", "decoys9"), ("selftest8", "selftest9"),
    ("AUDITOR_BRIEF8", "AUDITOR_BRIEF9"),
    ('os.path.join(C2, "round7", "stage", "v3")', 'os.path.join(C2, "round8", "stage", "v8e")'),
    ("round7/stage/v3", "round8/stage/v8e"),
    ("round8/out/", "round9/out/"), ("round8/certify8.py", "round9/certify9.py"),
    ("t8:st", "t9:st"), ("h8:st", "h9:st"), ("(`t8:` / `h8:` ids", "(`t9:` / `h9:` ids"),
    ("r8a01", "r9a01"),
    ("round-8 audit", "round-9 audit"), ("Round-8 audit", "Round-9 audit"), ("Round-8 blind audit", "Round-9 blind audit"),
    ("round-8 blind audit", "round-9 blind audit"), ("Round-8 auditor briefs", "Round-9 auditor briefs"),
    ("Round 8 blind audit", "Round 9 blind audit"), ("certify8 / certify7", "certify9 / certify8 / certify7"),
    ("round-8 rows", "round-9 rows"), ("round-8 row ids", "round-9 row ids"), ("not round-8\n", "not round-9\n"),
]
SPECIFIC = {
    "make_packs9.py": [
        ('''              "ownact", "dock", "shadow", "fjc", "scdb", "same", "remand", "dismiss", "deni", "modif")''',
         '''              "ownact", "dock", "shadow", "fjc", "scdb", "same", "remand", "dismiss", "deni", "modif",
              # round 9 (infra9): words of the round-9 tracks and classes
              "zone", "part", "gvr", "jersey", "succes", "judgm", "implic", "pool", "phrase", "lean", "line")'''),
    ],
}
NAMES = {"audit8lib.py": "audit9lib.py", "make_packs8.py": "make_packs9.py", "score_audit8.py": "score_audit9.py",
         "more_text8.py": "more_text9.py", "decoys8.py": "decoys9.py", "selftest8.py": "selftest9.py",
         "AUDITOR_BRIEF8.md": "AUDITOR_BRIEF9.md"}
os.makedirs(D, exist_ok=True)
for src, dst in NAMES.items():
    s = open(os.path.join(S, src), "rb").read().decode("utf-8")
    assert "\r" not in s, src
    for a, b in GEN:
        s = s.replace(a, b)
    for a, b in SPECIFIC.get(dst, []):
        assert s.count(a) == 1, (dst, a[:60])
        s = s.replace(a, b)
    open(os.path.join(D, dst), "wb").write(s.encode("utf-8"))
    print("written round9/audit/" + dst)
for f in ("decoy_pool_A.jsonl", "decoy_pool_B.jsonl", "decoy_pool_summary.tsv"):
    shutil.copyfile(os.path.join(S, f), os.path.join(D, f))
    print("copied round9/audit/" + f)
