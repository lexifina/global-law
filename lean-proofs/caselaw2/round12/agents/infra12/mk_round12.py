"""infra12: derive the round-12 tools from the round-11 files (round-11 files are only read).

    python -X utf8 round12/agents/infra12/mk_round12.py [--force]

Global token replacements (round11 paths -> round12, tool module names xxx11 -> xxx12, ids t11:/h11: -> t12:/h12:,
R11_* env -> R12_*, r11_ WSL names -> r12_, base round10/stage/v10d -> round11/stage/v11d, round10/out/v10d ->
round11/out/v11d); the round-12 specifics (nodes default, --nodes from the corpus rows, exclusion by identity, use
counts, summary columns, run script base mirror) are hand edits afterwards (see NOTES.md), so re-running with
--force overwrites them: run it only once, before the hand edits.
"""
import os
import re
import sys

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

MODS = ["certify11_claims", "certify11", "certify_recog11", "certify_opwords11", "stage11", "zones11", "nodes11",
        "old_by_class11", "summary11", "score11", "clean11", "freeze11", "sealed_lines11", "shep_sealed11",
        "score_sealed11", "audit11lib", "decoys11", "make_packs11", "more_text11", "score_audit11", "selftest11",
        "AUDITOR_BRIEF11", "live11", "mk_audit11", "mk_howto11", "INFRA_READY", "selftest11"]


def conv(s):
    s = s.replace("round10/stage/v10d", "round11/stage/v11d").replace('"round10", "stage", "v10d"',
                                                                      '"round11", "stage", "v11d"')
    s = s.replace("round10/out/v10d", "round11/out/v11d").replace('"round10", "out", "v10d"', '"round11", "out", "v11d"')
    s = s.replace("round10/results/v10d", "round11/results/v11d")
    # round11 paths -> round12 (the base strings above became round11/... first: protect them)
    prot = {"round11/stage/v11d": "\x01A", '"round11", "stage", "v11d"': "\x01B", "round11/out/v11d": "\x01C",
            '"round11", "out", "v11d"': "\x01D", "round11/results/v11d": "\x01E"}
    for k, v in prot.items():
        s = s.replace(k, v)
    s = s.replace("round11", "round12")
    for k, v in prot.items():
        s = s.replace(v, k)
    for m in MODS:
        s = re.sub(r"\b%s\b" % re.escape(m), m.replace("11", "12"), s)
    for a, b in (("R11_NODES", "R12_NODES"), ("R11BIN", "R12BIN"), ("r11_", "r12_"), ("t11:", "t12:"),
                 ("h11:", "h12:"), ("DESIGN11", "DESIGN12"), ("round-11 ", "round-12 "), ("Round 11", "Round 12"),
                 ("r11<letter>", "r12<letter>"), ("r11a01", "r12a01")):
        s = s.replace(a, b)
    return s


FILES = [
    ("round11/certify11.py", "round12/certify12.py"),
    ("round11/certify11_claims.py", "round12/certify12_claims.py"),
    ("round11/certify_recog11.py", "round12/certify_recog12.py"),
    ("round11/certify_opwords11.py", "round12/certify_opwords12.py"),
    ("round11/stage11.py", "round12/stage12.py"),
    ("round11/zones11.py", "round12/zones12.py"),
    ("round11/nodes11.py", "round12/nodes12.py"),
    ("round11/old_by_class11.py", "round12/old_by_class12.py"),
    ("round11/summary11.py", "round12/summary12.py"),
    ("round11/score11.sh", "round12/score12.sh"),
    ("round11/clean11.sh", "round12/clean12.sh"),
    ("wsl/r11_clean.sh", "wsl/r12_clean.sh"),
    ("wsl/r11_run.sh", "wsl/r12_run.sh"),
    ("round11/freeze11.py", "round12/freeze12.py"),
    ("round11/sealed_lines11.py", "round12/sealed_lines12.py"),
    ("round11/shep_sealed11.py", "round12/shep_sealed12.py"),
    ("round11/score_sealed11.sh", "round12/score_sealed12.sh"),
    ("round11/lead/live11.py", "round12/lead/live12.py"),
    ("round11/audit/audit11lib.py", "round12/audit/audit12lib.py"),
    ("round11/audit/decoys11.py", "round12/audit/decoys12.py"),
    ("round11/audit/make_packs11.py", "round12/audit/make_packs12.py"),
    ("round11/audit/more_text11.py", "round12/audit/more_text12.py"),
    ("round11/audit/score_audit11.py", "round12/audit/score_audit12.py"),
    ("round11/audit/selftest11.py", "round12/audit/selftest12.py"),
    ("round11/audit/AUDITOR_BRIEF11.md", "round12/audit/AUDITOR_BRIEF12.md"),
    ("round11/audit/HOWTO.md", "round12/audit/HOWTO.md"),
]

for src, dst in FILES:
    s = open(os.path.join(C2, src), "rb").read().decode("utf-8")
    assert "\r" not in s, src
    t = conv(s)
    p = os.path.join(C2, dst)
    if os.path.exists(p) and "--force" not in sys.argv:
        print("exists, kept:", dst)
        continue
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(t.encode("utf-8"))
    if src.endswith(".sh"):
        os.chmod(p, 0o755)
    print("written", dst)
