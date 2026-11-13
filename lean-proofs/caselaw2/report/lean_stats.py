"""Count the caselaw-lean-2 Lean sources: lines, declarations by kind, theorems, #guard checks.

Usage: python lean_stats.py            (prints JSON)
Imported by make_report.py.

Declarations are counted with a regex over the source (a line that starts, after attributes and modifiers, with
def/theorem/lemma/abbrev/structure/inductive/class/instance/opaque/axiom), not by elaborating Lean. `example`s are
counted separately. Theorem names come from Registry.lean (the statement lock), which audit.py generates.
"""
import json
import re
from pathlib import Path

LP = Path.home() / "Documents" / "global-law-lean" / "lean-proofs" / "LegalProofs"
ROOT = LP / "CaseLaw2"
TOP = LP / "CaseLaw2.lean"
V1_DIR = LP / "USCaseLaw"

DECL = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|partial|unsafe|nonrec|scoped)\s+)*"
    r"(def|theorem|lemma|abbrev|structure|inductive|class|instance|opaque|axiom|example)\b")
GENERATED = {"Registry.lean", "Audit.lean"}


def file_stats(p: Path):
    kinds = {}
    guards = 0
    guard_msgs = 0
    lines = 0
    in_comment = 0
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        lines += 1
        s = line.strip()
        # skip block comments (doc strings start with /-- and module docs with /-!)
        if in_comment:
            if "-/" in s:
                in_comment = 0
            continue
        if s.startswith("/-"):
            in_comment = 0 if "-/" in s[2:] else 1
            continue
        m = DECL.match(line)
        if m:
            kinds[m.group(1)] = kinds.get(m.group(1), 0) + 1
        if re.match(r"#guard(?!_msgs)", s):
            guards += 1
        if s.startswith("#guard_msgs"):
            guard_msgs += 1
    return {"lines": lines, "kinds": kinds, "guards": guards, "guard_msgs": guard_msgs}


def registry():
    p = ROOT / "Registry.lean"
    out = []
    if not p.exists():
        return out
    for m in re.finditer(r'\("([^"]+)",\s*"([^"]*)",\s*"((?:[^"\\]|\\.)*)"\)', p.read_text(encoding="utf-8")):
        out.append({"name": m.group(1), "module": m.group(2), "desc": m.group(3).replace('\\"', '"')})
    return out


def stats():
    files = sorted(ROOT.rglob("*.lean"))
    per = {}
    for f in files:
        per[f.relative_to(ROOT).as_posix()] = file_stats(f)
    if TOP.exists():
        per["../CaseLaw2.lean"] = file_stats(TOP)
    tot_kinds = {}
    tot_kinds_handwritten = {}
    for name, s in per.items():
        for k, v in s["kinds"].items():
            tot_kinds[k] = tot_kinds.get(k, 0) + v
            if Path(name).name not in GENERATED:
                tot_kinds_handwritten[k] = tot_kinds_handwritten.get(k, 0) + v
    decl = sum(v for k, v in tot_kinds.items() if k != "example")
    reg = registry()
    v1 = None
    if V1_DIR.exists():
        v1f = [V1_DIR / n for n in ("Courts.lean", "Precedent.lean") if (V1_DIR / n).exists()]
        v1per = {f.name: file_stats(f) for f in v1f}
        v1 = {"files": len(v1f), "lines": sum(s["lines"] for s in v1per.values()),
              "per_file": {k: v["lines"] for k, v in v1per.items()}}
    return {
        "root": str(ROOT),
        "files": len(per),
        "lines": sum(s["lines"] for s in per.values()),
        "lines_handwritten": sum(s["lines"] for n, s in per.items() if Path(n).name not in GENERATED),
        "kinds": tot_kinds,
        "declarations": decl,
        "declarations_handwritten": sum(v for k, v in tot_kinds_handwritten.items() if k != "example"),
        "theorems_in_source": tot_kinds.get("theorem", 0) + tot_kinds.get("lemma", 0),
        "theorems_registered": len(reg),
        "guards": sum(s["guards"] for s in per.values()),
        "guard_msgs": sum(s["guard_msgs"] for s in per.values()),
        "per_file": per,
        "registry": reg,
        "v1_usc_caselaw_dir": v1,
    }


if __name__ == "__main__":
    s = stats()
    s.pop("registry")
    print(json.dumps(s, indent=1))
