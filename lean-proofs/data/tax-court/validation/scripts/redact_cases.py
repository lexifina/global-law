"""Apply hand-written redaction specs to Tax Court opinion texts.

Each spec lists the line ranges to keep (1-based, inclusive), exact-text replacements
(whitespace-flexible match; every one must hit), and the facts carried over from the
Opinion/Discussion part. Judgment lives in the specs, not in this code.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"~\Documents\tax-formalization-data\taxcourt")
SRC = ROOT / "cases" / "text"
OUT = ROOT / "validation" / "blind" / "redacted"
RA = "[REDACTED AMOUNT]"
RC = "[REDACTED CONCLUSION]"


def flex(s):
    parts = [re.escape(p) for p in s.split()]
    return re.compile(r"\s+".join(parts))


def apply(spec):
    cid = spec["id"]
    lines = (SRC / f"{cid}.txt").read_text(encoding="utf-8").splitlines()
    kept = []
    for a, b in spec["keep"]:
        kept.extend(lines[a - 1:b])
    text = "\n".join(kept)
    log = []
    for old, new, kind in spec["repl"]:
        pat = flex(old)
        text, n = pat.subn(lambda m: new, text)
        if n == 0:
            sys.exit(f"{cid}: no match for {old!r}")
        words = old.split()
        log.append({"original": " ".join(words[:25]), "replaced_with": new, "kind": kind})
    for item in spec.get("extra_log", []):
        log.append(item)
    facts = spec["facts"]
    text = text.rstrip() + "\n\n[OPINION / DISCUSSION REMOVED]\n\nFACTS FOUND IN THE DISCUSSION\n" + "".join(
        f"- {f}\n" for f in facts)
    (OUT / f"{cid}.txt").write_bytes(text.encode("utf-8"))
    meta = {"id": cid, "kept_sections": spec["kept_sections"], "removed_sections": spec["removed_sections"],
            "redactions": log, "facts_from_discussion": facts}
    if spec.get("notes"):
        meta["notes"] = spec["notes"]
    (OUT / f"{cid}.redactions.json").write_bytes(
        (json.dumps(meta, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(cid, "redactions:", len(log), "facts:", len(facts))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    from redaction_specs import SPECS
    for s in SPECS:
        apply(s)
