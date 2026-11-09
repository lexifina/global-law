"""dead_fine (Germany): an administrative-offence catalogue ('ordnungswidrig handelt, wer ... entgegen § X Absatz Y')
points to a § or paragraph of the same law that does not exist or is repealed. A fine needs an exact statutory basis
(Art. 103(2) GG, § 3 OWiG), so the item cannot be enforced.
python detectors/owi_de.py RUN -> findings/RUN/dead_fine.jsonl"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from common import FINDINGS, CORPUS, FLAGS, pins, lower_priority

C = [c for c in pins()["corpora"] if c["repo"] == "germany-law"][0]
GIT = CORPUS / "germany-law.git"
PARA = re.compile(r"^\((\d+[a-z]?)\)", re.M)
SEC = re.compile(r"§\s*(\d+[a-z]?)(?:\s+(?:Absatz|Abs\.)\s+(\d+[a-z]?))?")
ABS = re.compile(r"^\s*(?:[a-z]{1,2}\)|\d+\.)?\s*(?:Absatz|Abs\.)\s+(\d+[a-z]?)")
LAWNAME = re.compile(r"(?:des|der|dem|im|in der|nach der|nach dem)\s+(?:[A-ZÄÖÜ][\w-]*(?:gesetz|gesetzes|gesetzbuch|gesetzbuchs|gesetzbuches|ordnung|buch|buchs|buches|verordnung|abkommens|übereinkommens|richtlinie|vertrags|statuts)\b|[A-ZÄÖÜ]{2,}[\w-]*\b|Verordnung|Richtlinie|Durchführungsverordnung|Delegierten|Anlage|Anhang)")
GONE = re.compile(r"(?i)^\s*(?:#.*)?\(?(weggefallen|aufgehoben)\)?\s*$|^\s*-\s*$")


def key(n):
    m = re.match(r"(\d+)([a-z]*)", n)
    return f"{int(m.group(1)):04d}{m.group(2)}"


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    ls = subprocess.run(["git", "-C", str(GIT), "ls-tree", "-r", "-z", "--format=%(objectname) %(path)", C["sha"]],
                        capture_output=True, creationflags=FLAGS).stdout.decode("utf-8", "replace").split("\0")
    files = {}
    for x in ls:
        if x:
            sha, path = x.split(" ", 1)
            if re.match(r"[^/]+/\d{4}[a-z]*\.md$", path):
                files[path] = sha
    p = subprocess.run(["git", "-C", str(GIT), "cat-file", "--batch"], input=("\n".join(files.values()) + "\n").encode(),
                       capture_output=True, creationflags=FLAGS).stdout
    text, pos = {}, 0
    for path in files:
        nl = p.index(b"\n", pos); size = int(p[pos:nl].split()[2]); text[path] = p[nl + 1: nl + 1 + size].decode("utf-8", "replace"); pos = nl + 2 + size
    paras = {k: {m for m in PARA.findall(t)} for k, t in text.items()}
    gone = {k for k, t in text.items() if len(t.strip().splitlines()) <= 3 and re.search(r"(?i)weggefallen|aufgehoben", t)}
    out = []
    for path, t in text.items():
        if not re.search(r"ordnungswidrig handelt|Ordnungswidrig im Sinne|wird bestraft, wer", t):
            continue
        law = path.split("/")[0]
        last_sec = None
        for line in t.splitlines():
            if line.startswith("#") or "|" in line:
                continue
            ms = list(SEC.finditer(line))
            clause_has_law = bool(LAWNAME.search(line))
            if ms:
                for m in ms:
                    clause = re.split(r"[;,]\s|§", line[m.end():] + ";", 1)[0]
                    if LAWNAME.search(clause) or "entgegen" not in line[max(0, m.start() - 60): m.start()] and "nach" not in line[max(0, m.start() - 12): m.start()]:
                        continue
                    tp = f"{law}/{key(m.group(1))}.md"
                    if tp == path:
                        continue
                    if tp not in text:
                        out.append({"path": path, "ref": m.group(0), "problem": "section missing", "line": line.strip()[:500]})
                    elif tp in gone:
                        out.append({"path": path, "ref": m.group(0), "problem": "section repealed", "line": line.strip()[:500]})
                    elif m.group(2) and paras[tp] and m.group(2) not in paras[tp]:
                        out.append({"path": path, "ref": m.group(0), "problem": f"paragraph missing (has {','.join(sorted(paras[tp]))})", "line": line.strip()[:500]})
                last = ms[-1]
                last_sec = None if clause_has_law else last.group(1)
            else:
                a = ABS.match(line)
                if a and last_sec and not clause_has_law:
                    tp = f"{law}/{key(last_sec)}.md"
                    if tp in text and paras[tp] and a.group(1) not in paras[tp]:
                        out.append({"path": path, "ref": f"§ {last_sec} Absatz {a.group(1)}", "problem": f"paragraph missing (has {','.join(sorted(paras[tp]))})", "line": line.strip()[:500]})
    with (FINDINGS / run / "dead_fine.jsonl").open("w", encoding="utf-8") as fh:
        for r in out:
            r["corpus"] = C["path"]; fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("dead_fine", len(out), "in", len({r['path'] for r in out}), "files")


if __name__ == "__main__":
    main()
