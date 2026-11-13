"""Round 3 candidate pass: scan2.py (round-2 part map and wording families) on HARD-WRAPPED decisions only, with
sentences cut on the unwrapped view (common.unwrap_view) and patterns matched on the de-hyphenated string
(common.dehyphen). Offsets stay offsets of the original git text.

    python -X utf8 scan3.py <repo>        -> data/reader_work/cand3/<repo>.jsonl.gz

A decision is hard-wrapped by its line-length statistics (common.hard_wrapped). Other decisions are skipped: rounds 1
and 2 read them with the right sentences. Candidates carry "hw": 1.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import scan  # noqa: E402
import scan2  # noqa: E402,F401  (adds the round-2 families and the round-2 part map to `scan`)

scan.HW_MODE = True
scan.HW_ONLY = True
scan.CAND_DIR = os.path.join(common.WORK, "cand3")

if __name__ == "__main__":
    scan.main(sys.argv[1])
