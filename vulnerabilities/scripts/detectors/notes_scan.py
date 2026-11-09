"""publisher_flag: editorial notes in which the publisher itself says an amendment failed, a reference is wrong,
or two provisions share a number. git grep on the read-only mirrors at the pinned sha.

python detectors/notes_scan.py RUN -> findings/RUN/publisher_flag.jsonl
"""
from __future__ import annotations
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from common import GIT_GREP_THREADS, FINDINGS, CORPUS, FLAGS, pins, lower_priority, WORKERS

PAT = "|".join([
    r"could not be executed", r"was not executed", r"cannot be executed", r"could not be given effect",
    r"[Ss]o in original", r"probably should be", r"[Tt]wo (sections|subsections|paragraphs|subpars?\.|subsecs?\.|pars?\.|secs?\.) ",
    r"[Nn]o (section|subsection|paragraph) .{1,20} has been enacted",
    r"nicht ausführbar", r"nicht ausgeführt werden", r"ging ins Leere", r"gegenstandslos",
    r"n.a pu être (exécutée|intégrée|appliquée)", r"non exécutable", r"modification (n'a pas été|non) (effectuée|intégrée)",
    r"no (pudo|ha podido) (ser )?(incorporad|realizar|ejecutar)", r"(no|non) puede ser incorporad",
    r"non (è stata|e' stata) (recepita|apportata)", r"non (può|puo') essere (recepita|apportata)",
    r"(kon|kan) niet worden (verwerkt|aangebracht|doorgevoerd)", r"niet uitvoerbaar",
    r"kunde inte genomföras", r"kan inte genomföras",
    r"não (pôde|pode) ser (efetuad|incorporad|realizad)",
    r"\[sic\]", r"\(sic\)",
])


def one(c):
    repo = CORPUS / (c["repo"] + ".git")
    if not repo.exists():
        return []
    p = subprocess.run(["git", "-C", str(repo), "grep", "--threads", GIT_GREP_THREADS, "-I", "-n", "-E", "-i", PAT, c["sha"], "--"],
                       capture_output=True, creationflags=FLAGS)
    out = []
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        try:
            _, path, ln, text = line.split(":", 3)
        except ValueError:
            continue
        out.append({"corpus": c["path"], "repo": c["repo"], "path": path, "line": int(ln), "text": text[:600]})
    return out


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    f = FINDINGS / run; f.mkdir(parents=True, exist_ok=True)
    cs = [c for c in pins()["corpora"] if not c["repo"].startswith(("united-kingdom", "romania"))]
    n = 0
    with ThreadPoolExecutor(WORKERS) as ex, (f / "publisher_flag.jsonl").open("w", encoding="utf-8") as fh:
        for rows in ex.map(one, cs):
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
    print("publisher_flag", n)


if __name__ == "__main__":
    main()
