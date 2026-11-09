"""Compare two certificate runs: what became certified, what stopped being certified.

    cp tools/out/certificates.json tools/out/certificates.prev.json   # before updating the corpora
    python tools/gen_facts.py && lake build                             # after: Lean re-checks everything
    python tools/diff.py tools/out/certificates.prev.json tools/out/certificates.json

A flag that stops being certified usually means the law or the corpus record changed: the target came back, the citing
provision was repealed or fixed. A newly certified flag is a new dead reference.
"""
from __future__ import annotations
import json, sys


def load(p):
    d = json.load(open(p, encoding="utf-8"))
    return {r["id"]: r for r in d["flags"]}


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    old, new = load(sys.argv[1]), load(sys.argv[2])
    gained = [r for i, r in new.items() if r["certified"] and not old.get(i, {}).get("certified")]
    lost = [r for i, r in old.items() if r["certified"] and not new.get(i, {}).get("certified")]
    print(f"{len(gained)} newly certified, {len(lost)} no longer certified")
    for label, rs in (("NEW", gained), ("GONE", lost)):
        for r in rs[:200]:
            print(f"  {label}  {r['corpus']} {r['citing_path']} -> {r['target_path']}")


if __name__ == "__main__":
    main()
