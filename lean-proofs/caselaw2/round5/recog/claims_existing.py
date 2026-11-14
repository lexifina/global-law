"""Round 5, agent `recog`: a `recognised` claim line (treatment_class.tsv layout, 5 columns) for each row of
data/treatment_witness.tsv as it stands. The checker decides which pass (both names in the quote, W's power, ...).

    python -X utf8 claims_existing.py

Writes claims_existing.tsv: treatment_id, recognised, -, -, src (the witness line's own src + ";round5-claim").
"""
import os
import sys

import recog_common as R


def main():
    rows = []
    for p in R.read_rows(os.path.join(R.DATA, "treatment_witness.tsv"), 4):
        rows.append([p[0], "recognised", "-", "-", p[3] + ";round5-claim"])
    R.write_rows(os.path.join(R.HERE, "claims_existing.tsv"), rows)
    print("claims", len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
