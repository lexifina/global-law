"""infra10: port round9/audit/ to round10/audit/ by textual replacements (round-9 files are only read).

    python -X utf8 round10/agents/infra10/mk_audit10.py

Copies audit9lib, make_packs9, score_audit9, more_text9, decoys9, selftest9 (.py) and AUDITOR_BRIEF9.md with the
round-10 names and paths, the base stage round9/stage/v9c, ids t10:/h10: in the self-test, the neutral-name example
r10a01 and the round-10 telling words; decoys10.py also reads the round-9 audits (round9/audit/r9*/, judged with the
same rules as the round-7 audits). The decoy pools are then rebuilt by running decoys10.py (not copied). HOWTO.md is
written by hand.
"""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
S = os.path.join(C2, "round9", "audit")
D = os.path.join(C2, "round10", "audit")
GEN = [
    ("round9/audit", "round10/audit"),
    ("audit9lib", "audit10lib"), ("make_packs9", "make_packs10"), ("score_audit9", "score_audit10"),
    ("more_text9", "more_text10"), ("decoys9", "decoys10"), ("selftest9", "selftest10"),
    ("AUDITOR_BRIEF9", "AUDITOR_BRIEF10"),
    ('os.path.join(C2, "round8", "stage", "v8e")', 'os.path.join(C2, "round9", "stage", "v9c")'),
    ("round8/stage/v8e", "round9/stage/v9c"),
    ("round9/out/", "round10/out/"), ("round9/certify9.py", "round10/certify10.py"),
    ("t9:st", "t10:st"), ("h9:st", "h10:st"), ("(`t9:` / `h9:` ids", "(`t10:` / `h10:` ids"),
    ("r9a01", "r10a01"),
    ("round-9 audit", "round-10 audit"), ("Round-9 audit", "Round-10 audit"), ("Round-9 blind audit", "Round-10 blind audit"),
    ("round-9 blind audit", "round-10 blind audit"), ("Round-9 auditor briefs", "Round-10 auditor briefs"),
    ("Round 9 blind audit", "Round 10 blind audit"), ("certify9 / certify8 / certify7", "certify10 / certify9 / certify8 / certify7"),
    ("round-9 rows", "round-10 rows"), ("round-9 row ids", "round-10 row ids"), ("not round-9\n", "not round-10\n"),
]
SPECIFIC = {
    "make_packs10.py": [
        ('''              "zone", "part", "gvr", "jersey", "succes", "judgm", "implic", "pool", "phrase", "lean", "line")''',
         '''              "zone", "part", "gvr", "jersey", "succes", "judgm", "implic", "pool", "phrase", "lean", "line",
              # round 10 (infra10): words of the round-10 tracks and classes ("state", "remand" are listed above)
              "syllab", "recut", "bridge", "named", "bare", "footnote", "review")'''),
    ],
    "decoys10.py": [
        ('''"""Round 10 blind audit: the decoy pools (items whose right answer is known from earlier audits). Port of
round7/audit/decoys7.py (round-5 and round-6 pools rebuilt the same way) plus the round-7 audited rows.

    python -X utf8 round10/audit/decoys10.py [--min-conf medium] [--out-dir round10/audit] [--no-r7]
''', '''"""Round 10 blind audit: the decoy pools (items whose right answer is known from earlier audits). Port of
round9/audit/decoys9.py (= round7/audit/decoys7.py: round-5 and round-6 pools rebuilt the same way, plus the round-7
audited rows) plus the round-9 audited rows (round9/audit/r9*/, same reading as the round-7 rows below; ids
`r9:<run>:<item>`, families `r9:<run>:<class>`). With --no-r9 the output is round 9's pools byte for byte.

    python -X utf8 round10/audit/decoys10.py [--min-conf medium] [--out-dir round10/audit] [--no-r7] [--no-r9]
'''),
        ('''def r7_pool(min_conf):
    import score_audit10 as S
    out, seen_rows = [], set()
    for sp in sorted(glob.glob(os.path.join(A.R7A, "r7a*", "sample.tsv"))):''',
         '''def r7_pool(min_conf, root=None, pat="r7a*", tag="r7"):
    """Round-7 audits (round 10: also the round-9 audits, root round9/audit, pat r9*, tag r9)."""
    import score_audit10 as S
    out, seen_rows = [], set()
    for sp in sorted(glob.glob(os.path.join(root or A.R7A, pat, "sample.tsv"))):'''),
        ('''            out.append({"did": "r7:%s:%s" % (run, i), "type": k["type"], "family": "r7:%s:%s" % (run, k["class"]),''',
         '''            out.append({"did": "%s:%s:%s" % (tag, run, i), "type": k["type"],
                        "family": "%s:%s:%s" % (tag, run, k["class"]),'''),
        ('''    ap.add_argument("--no-r7", action="store_true")
''', '''    ap.add_argument("--no-r7", action="store_true")
    ap.add_argument("--no-r9", action="store_true", help="round 10: without the round-9 audits (= round 9's pools)")
'''),
        ('''        for d in r7_pool(a.min_conf):
            (pa if d["type"] == "A" else pb).append(d)
''', '''        for d in r7_pool(a.min_conf):
            (pa if d["type"] == "A" else pb).append(d)
    if not a.no_r9:
        for d in r7_pool(a.min_conf, root=os.path.join(A.C2, "round9", "audit"), pat="r9*", tag="r9"):
            if d["type"] in ("A", "B"):
                (pa if d["type"] == "A" else pb).append(d)
'''),
    ],
}
NAMES = {"audit9lib.py": "audit10lib.py", "make_packs9.py": "make_packs10.py", "score_audit9.py": "score_audit10.py",
         "more_text9.py": "more_text10.py", "decoys9.py": "decoys10.py", "selftest9.py": "selftest10.py",
         "AUDITOR_BRIEF9.md": "AUDITOR_BRIEF10.md"}
os.makedirs(D, exist_ok=True)
for src, dst in NAMES.items():
    s = open(os.path.join(S, src), "rb").read().decode("utf-8")
    assert "\r" not in s, src
    for a, b in GEN:
        s = s.replace(a, b)
    for a, b in SPECIFIC.get(dst, []):
        assert s.count(a) == 1, (dst, a[:60], s.count(a))
        s = s.replace(a, b)
    open(os.path.join(D, dst), "wb").write(s.encode("utf-8"))
    print("written round10/audit/" + dst)
