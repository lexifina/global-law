"""infra12: round-12 use counts / labels in the generated round12/score_sealed12.sh."""
import os
C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(C2, "round12", "score_sealed12.sh")
s = open(p, encoding="utf-8").read()
R = [
 ("Written by agent infra11; NOT run by it.", "Written by agent infra12; NOT run by it."),
 ("# (= round10/score_sealed10.sh on round-12 paths, SEALED_LOG figures", "# (= round11/score_sealed11.sh on round-12 paths, use counts +1, bhk_enbanc added; SEALED_LOG figures"),
 ("(SEVENTH use; burned, D11-2)", "(EIGHTH use; burned, D12-2)"),
 ("(SIXTH use; burned, D11-2)", "(SEVENTH use; burned, D12-2)"),
 ("h1 halves, FOURTH use:", "h1 halves, FIFTH use:"),
 ("""# 4. the closed keys: songer_treat and brace_hall_state (THIRD use) and fedcir_dataset (SECOND use), frozen build
#    only, --label round12; h0, h1 and all logged (refused when benchmarks/<k>/results/round12.* exists). v10d's
#    figures exist from round 10 (round10.*); v10d is not re-run.""",
  """# 4. the closed keys: songer_treat and brace_hall_state (FOURTH use), fedcir_dataset (THIRD use) and bhk_enbanc
#    (SECOND use), frozen build only, --label round12; h0, h1 and all logged (refused when
#    benchmarks/<k>/results/round12.* exists). v11d's figures exist from round 11 (round11.*); v11d is not re-run."""),
 ("--label round10v10d, and on", "--label round11v11d, and on"),
 ("(refused when benchmarks/<k>/results/round10v10d.* or round12.* exists)", "(refused when benchmarks/<k>/results/round11v11d.* or round12.* exists)"),
 ('KEYS9="songer_treat brace_hall_state fedcir_dataset"', 'KEYS9="songer_treat brace_hall_state fedcir_dataset bhk_enbanc"'),
 ("    refuse if benchmarks/<k>/results/round10v10d.* or round12.* exists for the keys in round12/FRESH_KEYS.txt",
  "    refuse if benchmarks/<k>/results/round11v11d.* or round12.* exists for the keys in round12/FRESH_KEYS.txt"),
 ("--label r11-$N  (7th use)", "--label r12-$N  (8th use)"),
 ("--results $R/shep  (6th use)", "--results $R/shep  (7th use)"),
 ("(h1, 4th use; h1 lines logged)", "(h1, 5th use; h1 lines logged)"),
 ("(songer / brace & hall 3rd use, fedcir 2nd use; h0/h1/all logged)", "(songer / brace & hall 4th use, fedcir 3rd use, bhk_enbanc 2nd use; h0/h1/all logged)"),
 ("--label round10v10d, then --out $OUT", "--label round11v11d, then --out $OUT"),
 ("(closed key already scored in round 11)", "(closed key already scored in round 12)"),
 ('compgen -G "benchmarks/$k/results/round10v10d.*"', 'compgen -G "benchmarks/$k/results/round11v11d.*"'),
 ("already holds round12.* or round10v10d.* (fresh key", "already holds round12.* or round11v11d.* (fresh key"),
 ('echo "== 1. fresh lists, sealed half (seventh use)"', 'echo "== 1. fresh lists, sealed half (eighth use)"'),
 ('--data "$DATA" --label "r11-$N" >', '--data "$DATA" --label "r12-$N" >'),
 ('echo "- $ts fresh sealed, 7th use (score_fresh7 --split test, label r11-$N,', 'echo "- $ts fresh sealed, 8th use (score_fresh7 --split test, label r12-$N,'),
 ('echo "== 2. Shepardized, sealed half (sixth use)"', 'echo "== 2. Shepardized, sealed half (seventh use)"'),
 ('Shepardized sealed, 6th use (compare.py', 'Shepardized sealed, 7th use (compare.py'),
 ('echo "== 3. the four round-8 keys, h1 halves (fourth use; label round12)"', 'echo "== 3. the four round-8 keys, h1 halves (fifth use; label round12)"'),
 ('$k h1, 4th use (benchmarks', '$k h1, 5th use (benchmarks'),
 ('echo "== 4. songer_treat, brace_hall_state (third use) and fedcir_dataset (second use); $N as round12"',
  'echo "== 4. songer_treat, brace_hall_state (fourth use), fedcir_dataset (third use), bhk_enbanc (second use); $N as round12"'),
 ('  case $k in fedcir_dataset) use="closed key, 2nd use" ;; *) use="closed key, 3rd use" ;; esac',
  '  case $k in fedcir_dataset) use="closed key, 3rd use" ;; bhk_enbanc) use="closed key, 2nd use" ;; *) use="closed key, 4th use" ;; esac'),
 ('echo "== 5. round-12 fresh keys (first and only use; v10d as round10v10d, $N as round12)"',
  'echo "== 5. round-12 fresh keys (first and only use; v11d as round11v11d, $N as round12)"'),
 ('  key_one "$k" round11/out/v11d round11/stage/v11d round10v10d v10d "fresh key, 1st use"',
  '  key_one "$k" round11/out/v11d round11/stage/v11d round11v11d v11d "fresh key, 1st use"'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
