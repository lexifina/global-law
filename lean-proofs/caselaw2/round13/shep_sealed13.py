"""Round 13 (= round11/shep_sealed11.py with round13/FREEZE.md and round13/SEALED_LOG.md; agent infra12): the
Shepardized sealed run through round 6's compare.py, with the freeze check pointed at round13/FREEZE.md.

compare.py (round 6, not edited) checks round6/history/FREEZE.md, which hashes the round-6 Lean sources; later rounds
changed those sources on purpose, so that check refuses. This wrapper imports compare.py, points FREEZE at
round13/FREEZE.md (same "<sha1>  <path>" format, every round-13 model file) and SEALED_LOG at round13/SEALED_LOG.md, and
runs compare.main() with the given arguments (which must include --split sealed). Nothing else changes.

    python -I round13/shep_sealed13.py --split sealed --out <abs out dir> --data <abs data dir> --results <abs dir>
"""
import importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("compare_r6", os.path.join(C2, "round6", "shepardized", "compare.py"))
cmp = importlib.util.module_from_spec(spec)
sys.argv = [os.path.join(C2, "round6", "shepardized", "compare.py")] + sys.argv[1:]
spec.loader.exec_module(cmp)
cmp.FREEZE = os.path.join(HERE, "FREEZE.md")
cmp.SEALED_LOG = os.path.join(HERE, "SEALED_LOG.md")
if "--split" not in sys.argv or sys.argv[sys.argv.index("--split") + 1] != "sealed":
    sys.exit("shep_sealed13.py is for --split sealed only")
cmp.main()
