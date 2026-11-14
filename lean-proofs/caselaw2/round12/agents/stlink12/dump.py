"""stlink12: print the start of D and T texts for inspection.  python -X utf8 dump.py D T [chars]"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from diag import L  # noqa: E402

n, j = int(sys.argv[1]), int(sys.argv[2])
k = int(sys.argv[3]) if len(sys.argv) > 3 else 2500
t = L.fetch_texts([n, j])
for x in (n, j):
    print("=" * 30, x)
    print(t[x][1][:k])
