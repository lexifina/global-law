"""infra11 Part C: round11/score_sealed11.sh from round10/score_sealed10.sh (ordered global replacements, then asserted
specific ones for the use counts and the closed keys). LEAD ONLY script; infra11 runs only --plan and the refusal path.

    python -X utf8 round11/agents/infra11/mk_score_sealed11.py [--force]
"""
import os
import sys

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
s = open(os.path.join(C2, "round10", "score_sealed10.sh"), "rb").read().decode("utf-8")
assert "\r" not in s
GLOB = [  # order matters: round-10 names first, then round-9 names become round-10 names
    ("round10/", "round11/"), ("sealed_lines10", "sealed_lines11"), ("shep_sealed10", "shep_sealed11"),
    ("freeze10", "freeze11"), ("score_sealed10", "score_sealed11"), ("r10-", "r11-"),
    ("--label round10", "--label round11"), ("round10.*", "round11.*"), ("results/round10.", "results/round11."),
    ("as round10", "as round11"), ("round-10", "round-11"), ("Round 10", "Round 11"), ("agent infra10", "agent infra11"),
    ("round9/out/v9c", "round10/out/v10d"), ("round9/stage/v9c", "round10/stage/v10d"), ("round9v9c", "round10v10d"),
    ("v9c", "v10d"),
]
for a, b in GLOB:
    assert a in s, a
    s = s.replace(a, b)
SPEC = [
    ("# (= round9/score_sealed9.sh on round-11 paths,", "# (= round10/score_sealed10.sh on round-11 paths,"),
    ("# 1. fresh lists, sealed half (SIXTH use; burned, D10-2)", "# 1. fresh lists, sealed half (SEVENTH use; burned, D11-2)"),
    ("# 2. Shepardized, sealed half (FIFTH use; burned, D10-2)", "# 2. Shepardized, sealed half (SIXTH use; burned, D11-2)"),
    ("# 3. the four round-8 keys, h1 halves, THIRD use:", "# 3. the four round-8 keys, h1 halves, FOURTH use:"),
    ("# 4. songer_treat and brace_hall_state (the round-9 keys), SECOND use, frozen build only, --label round11; h0, h1 and\n"
     "#    all logged (refused when benchmarks/<k>/results/round11.* exists). v10d's figures exist from round 9 (round9.*);\n"
     "#    v10d is not re-run.",
     "# 4. the closed keys: songer_treat and brace_hall_state (THIRD use) and fedcir_dataset (SECOND use), frozen build\n"
     "#    only, --label round11; h0, h1 and all logged (refused when benchmarks/<k>/results/round11.* exists). v10d's\n"
     "#    figures exist from round 10 (round10.*); v10d is not re-run. Their score.py is run by the CLI of\n"
     "#    benchmarks/CONTRACT.md; this script never opens their folders otherwise (only the results/round11.* refusal test\n"
     "#    and the json files the scorer itself writes, read by sealed_lines11.py)."),
    ('KEYS9="songer_treat brace_hall_state"', 'KEYS9="songer_treat brace_hall_state fedcir_dataset"'),
    ("--label r11-$N  (6th use)", "--label r11-$N  (7th use)"),
    ("--results $R/shep  (5th use)", "--results $R/shep  (6th use)"),
    ("(h1, 3rd use; h1 lines logged)", "(h1, 4th use; h1 lines logged)"),
    ("(2nd use; h0/h1/all logged)", "(songer / brace & hall 3rd use, fedcir 2nd use; h0/h1/all logged)"),
    ('echo "== 1. fresh lists, sealed half (sixth use)"', 'echo "== 1. fresh lists, sealed half (seventh use)"'),
    ('echo "- $ts fresh sealed, 6th use', 'echo "- $ts fresh sealed, 7th use'),
    ('echo "== 2. Shepardized, sealed half (fifth use)"', 'echo "== 2. Shepardized, sealed half (sixth use)"'),
    ('echo "- $ts Shepardized sealed, 5th use', 'echo "- $ts Shepardized sealed, 6th use'),
    ('echo "== 3. the four round-8 keys, h1 halves (third use; label round10)"',
     'echo "== 3. the four round-8 keys, h1 halves (fourth use; label round11)"'),
    ('echo "- $ts $k h1, 3rd use', 'echo "- $ts $k h1, 4th use'),
    ('echo "== 4. songer_treat and brace_hall_state (second use; $N as round11)"',
     'echo "== 4. songer_treat, brace_hall_state (third use) and fedcir_dataset (second use); $N as round11"'),
    ('already holds round11.* (second use already scored)', 'already holds round11.* (closed key already scored in round 11)'),
    ('  key_one "$k" "$OUT" "$DATA" round10 "$N" "fresh key, 1st use"',
     '  key_one "$k" "$OUT" "$DATA" round11 "$N" "fresh key, 1st use"'),
    ('  key_one "$k" "$OUT" "$DATA" round10 "$N" "round-9 key, 2nd use"',
     '  case $k in fedcir_dataset) use="closed key, 2nd use" ;; *) use="closed key, 3rd use" ;; esac\n'
     '  key_one "$k" "$OUT" "$DATA" round11 "$N" "$use"'),
]
for a, b in SPEC:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
p = os.path.join(C2, "round11", "score_sealed11.sh")
if os.path.exists(p) and "--force" not in sys.argv:
    sys.exit("exists (use --force)")
open(p, "wb").write(s.encode("utf-8"))
print("written round11/score_sealed11.sh")
for line in s.splitlines():
    for w in ("round10", "v9c", "round9", "sixth", "fifth", "SECOND use", "2nd use", "3rd use"):
        if w in line:
            print("CHECK:", line.strip()[:150])
            break
