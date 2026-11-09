"""Check one provision with Lean: every flagged reference from it, as a theorem.

    python tools/check.py germany/bund/acts awaffv/0034.md

Reads tools/out/certificates.json (run gen_facts.py first), writes tools/out/Check.lean with one theorem per reference,
runs Lean on it, and prints what was proved. Nothing outside tools/out/ is written.
"""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def iso(n: int) -> str:
    s = str(n); return f"{s[:4]}-{s[4:6]}-{s[6:]}"


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    corpus, path = sys.argv[1], sys.argv[2]
    data = json.loads((HERE / "out" / "certificates.json").read_text(encoding="utf-8"))
    today = data["today"]
    hits = [r for r in data["flags"] if r["corpus"] == corpus and r["citing_path"] == path]
    if not hits:
        sys.exit(f"no flagged references from {corpus} {path}")
    lst = lambda h: "[" + ", ".join(f"({d}, {'true' if v else 'false'})" for d, v in h) + "]"
    out = ["import LegalProofs.History", "", "open Legal", ""]
    for i, r in enumerate(hits):
        out += [f"-- {r['citing_path']} refers to {r['target_path']}",
                f"def f{i} : RefFlag := ⟨{lst(r['citing'])}, {lst(r['target'])}⟩"]
        if r["certified"]:
            out += [f"theorem dead{i} : ∀ d, {r['dead_from']} ≤ d → f{i}.rule.applicable d = false := by",
                    f"  have h : f{i}.target = ({r['dead_from']}, false) :: _ := rfl",
                    f"  exact dead_reference f{i}.rule {r['dead_from']} (by rw [show f{i}.rule.pointsAt = f{i}.target.toProvision from rfl, h]; exact History.gone_from _ _)",
                    f"theorem stillCited{i} : f{i}.citing.at {today} = true := by decide", ""]
        else:
            out += [f"theorem notCertified{i} : f{i}.certified {today} = false := by decide", ""]
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "Check.lean").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    lake = Path.home() / ".elan" / "bin" / ("lake.exe" if os.name == "nt" else "lake")
    p = subprocess.run([str(lake), "env", "lean", str(HERE / "out" / "Check.lean")], cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout, p.stderr); sys.exit("Lean rejected a theorem")
    print(f"{corpus} {path}: {len(hits)} flagged reference(s), all theorems checked by Lean")
    for r in hits:
        if r["certified"]:
            extra = "; the citing provision was rewritten after that and kept the reference" if r["reenacted"] else ""
            print(f"  PROVED  points at {r['target_path']}, gone since {iso(r['dead_from'])}: "
                  f"cannot apply on any date from then on, yet still in force on {iso(today)}{extra}")
        else:
            print(f"  NOT A DEFECT ON THIS RECORD  {r['target_path']}: its record does not end with it gone")


if __name__ == "__main__":
    main()
