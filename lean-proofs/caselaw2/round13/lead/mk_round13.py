"""round13 lead: derive the round-13 tools from the round-12 files (round-12 files are only read).

    python -X utf8 round13/lead/mk_round13.py [--force]

Same method as round12/agents/infra12/mk_round12.py. Token replacements: base round11/stage/v11d -> round12/stage/v12a
(out, results likewise), node folder round11/data_orders -> round12/data_orders (the 1,871 nodes v12a holds), WSL data
dir data_r11_v11d -> data_r12_v12a, base mirror base_r12_v11d -> base_r13_v12a; then round12 -> round13, tool modules
xxx12 -> xxx13, ids t12:/h12: -> t13:/h13:, R12_* -> R13_*, r12_ -> r13_. The frozen binary (round-11 s51,
caselaw2_r11v11d) is unchanged. Hand edits afterwards are listed in round13/LOG.md.
"""
import os
import re
import sys

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODS = ["certify12_claims", "certify12", "certify_recog12", "certify_opwords12", "stage12", "zones12", "nodes12",
        "old_by_class12", "summary12", "score12", "clean12", "freeze12", "sealed_lines12", "shep_sealed12",
        "score_sealed12", "audit12lib", "decoys12", "make_packs12", "more_text12", "score_audit12", "selftest12",
        "AUDITOR_BRIEF12"]

PROT = [  # (round-12 source string, final round-13 string), applied first and shielded from the later replacements
    ("round11/stage/v11d", "round12/stage/v12a"), ('"round11", "stage", "v11d"', '"round12", "stage", "v12a"'),
    ("round11/out/v11d", "round12/out/v12a"), ('"round11", "out", "v11d"', '"round12", "out", "v12a"'),
    ("round11/results/v11d", "round12/results/v12a"), ('"round11", "results", "v11d"', '"round12", "results", "v12a"'),
    ("round11/data_orders", "round12/data_orders"), ('"round11", "data_orders"', '"round12", "data_orders"'),
    ("data_r11_v11d", "data_r12_v12a"), ("base_r12_v11d", "base_r13_v12a"),
    ("caselaw2_r11v11d", "caselaw2_r11v11d"), ("r11v11d", "r11v11d"),
]


def conv(s):
    ph = {}
    for i, (a, b) in enumerate(PROT):
        k = "\x01%02d\x02" % i
        s = s.replace(a, k)
        ph[k] = b
    s = s.replace("round12", "round13")
    for m in MODS:
        s = re.sub(r"\b%s\b" % re.escape(m), m.replace("12", "13"), s)
    for a, b in (("R12_NODES", "R13_NODES"), ("R12BIN", "R13BIN"), ("r12_", "r13_"), ("t12:", "t13:"),
                 ("h12:", "h13:"), ("DESIGN12", "DESIGN13"), ("round-12 ", "round-13 "), ("Round 12", "Round 13"),
                 ("r12<letter>", "r13<letter>"), ("r12a01", "r13a01")):
        s = s.replace(a, b)
    for k, b in ph.items():
        s = s.replace(k, b)
    return s


FILES = [
    ("round12/certify12.py", "round13/certify13.py"),
    ("round12/certify12_claims.py", "round13/certify13_claims.py"),
    ("round12/stage12.py", "round13/stage13.py"),
    ("round12/zones12.py", "round13/zones13.py"),
    ("round12/nodes12.py", "round13/nodes13.py"),
    ("round12/old_by_class12.py", "round13/old_by_class13.py"),
    ("round12/summary12.py", "round13/summary13.py"),
    ("round12/score12.sh", "round13/score13.sh"),
    ("round12/clean12.sh", "round13/clean13.sh"),
    ("wsl/r12_clean.sh", "wsl/r13_clean.sh"),
    ("wsl/r12_run.sh", "wsl/r13_run.sh"),
    ("round12/freeze12.py", "round13/freeze13.py"),
    ("round12/sealed_lines12.py", "round13/sealed_lines13.py"),
    ("round12/shep_sealed12.py", "round13/shep_sealed13.py"),
    ("round12/score_sealed12.sh", "round13/score_sealed13.sh"),
    ("round12/audit/audit12lib.py", "round13/audit/audit13lib.py"),
    ("round12/audit/make_packs12.py", "round13/audit/make_packs13.py"),
    ("round12/audit/more_text12.py", "round13/audit/more_text13.py"),
    ("round12/audit/score_audit12.py", "round13/audit/score_audit13.py"),
    ("round12/audit/AUDITOR_BRIEF12.md", "round13/audit/AUDITOR_BRIEF13.md"),
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
    print("written", dst)
