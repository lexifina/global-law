"""missing_paragraph (Germany): a provision refers to 'Absatz N' of its own § (or '§ X Absatz N' of the same law)
but that § has no paragraph N in the current text.
python detectors/subref_de.py RUN -> findings/RUN/missing_paragraph.jsonl"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from common import FINDINGS, CORPUS, FLAGS, pins, lower_priority

C = [c for c in pins()["corpora"] if c["repo"] == "germany-law"][0]
GIT = CORPUS / "germany-law.git"
PARA = re.compile(r"^\((\d+[a-z]?)\)\s*$|^\((\d+[a-z]?)\)\s", re.M)
EXT = re.compile(r"^\s*(?:Satz\s+\d+\s*,?\s*)?(?:(?:Nummer|Nr\.)\s+\d+[a-z]?\s*,?\s*)?(?:Buchstabe\s+[a-z]\s*)?(?:des|der|im|in der|aus dem)\s+(?!vorliegenden)(?!dieses)(?!dieser)", re.I)
REF_OWN = re.compile(r"(?<![§\w.] )(?<!§ \d)(?<!§\d)\b(?:Absatz|Abs\.)\s+(\d+[a-z]?)\b")
REF_SEC = re.compile(r"§\s*(\d+[a-z]?)\s+(?:Absatz|Abs\.)\s+(\d+[a-z]?)\b")
LAWNAME = re.compile(r"(?:des|der|dem|im|in der)\s+(?:[A-ZÄÖÜ][\w-]*(?:gesetz|gesetzes|gesetzbuch|gesetzbuchs|gesetzbuches|ordnung|buch|buchs|buches|verordnung|abkommens|übereinkommens|richtlinie|vertrags|statuts|regelung)\b|[A-ZÄÖÜ]{2,}[\w-]*\b|Verordnung|Richtlinie|Gesetzes|Buches|Artikels)")
NOTE = re.compile(r"(?i)(\+\+\+|Fußnote|Textnachweis|Stand:|aufgehoben|weggefallen|\(XXXX\)|Inkrafttreten|in der bis zum|in der am .* geltenden|in der vor dem|alter Fassung|a\.F\.)")


def key(n: str) -> str:
    m = re.match(r"(\d+)([a-z]*)", n)
    return f"{int(m.group(1)):04d}{m.group(2)}"


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    ls = subprocess.run(["git", "-C", str(GIT), "ls-tree", "-r", "-z", "--format=%(objectname) %(path)", C["sha"]],
                        capture_output=True, creationflags=FLAGS).stdout.decode("utf-8", "replace").split("\0")
    files = {}
    for x in ls:
        if not x:
            continue
        sha, path = x.split(" ", 1)
        m = re.match(r"([^/]+)/(\d{4}[a-z]*)\.md$", path)
        if m:
            files[path] = sha
    shas = list(files.values())
    p = subprocess.run(["git", "-C", str(GIT), "cat-file", "--batch"], input=("\n".join(shas) + "\n").encode(), capture_output=True, creationflags=FLAGS).stdout
    text, pos = {}, 0
    for path, sha in files.items():
        nl = p.index(b"\n", pos); size = int(p[pos:nl].split()[2]); text[path] = p[nl + 1: nl + 1 + size].decode("utf-8", "replace"); pos = nl + 2 + size
    paras = {path: {a or b for a, b in PARA.findall(t)} for path, t in text.items()}
    out = []
    for path, t in text.items():
        law = path.split("/")[0]
        own = paras[path]
        for line in t.splitlines():
            if NOTE.search(line) or line.startswith("#") or "|" in line:
                continue
            for m in REF_SEC.finditer(line):
                tail = line[m.end(): m.end() + 80]
                clause = re.split(r"[;.]|§", line[m.end():] + ";", 1)[0]
                if EXT.match(tail) or LAWNAME.search(clause):
                    continue
                tp = f"{law}/{key(m.group(1))}.md"
                if tp in paras and paras[tp] and m.group(2) not in paras[tp]:
                    out.append({"path": path, "ref": m.group(0), "target": tp, "target_paras": sorted(paras[tp]), "line": line.strip()[:600]})
            for m in REF_OWN.finditer(line):
                pre = line[max(0, m.start() - 14): m.start()]
                sent_start = max(line.rfind(". ", 0, m.start()), line.rfind("; ", 0, m.start()))
                clause = re.split(r"[;]|\.\s", line[m.end():] + ";", 1)[0]
                if "§" in line[sent_start + 1: m.start()] or LAWNAME.search(clause) or LAWNAME.search(line[sent_start + 1: m.start()]):
                    continue
                if "§" in pre or re.search(r"(Artikel|Art\.)\s*\d+\s*$", pre):
                    continue
                tail = line[m.end(): m.end() + 80]
                if EXT.match(tail) or re.match(r"\s*(?:Satz\s+\d+\s*)?(?:des|der)\s", tail):
                    continue
                if own and len(own) >= 2 and m.group(1) not in own:
                    out.append({"path": path, "ref": m.group(0), "target": path, "target_paras": sorted(own), "line": line.strip()[:600]})
    dst = FINDINGS / run / "missing_paragraph.jsonl"
    with dst.open("w", encoding="utf-8") as fh:
        for r in out:
            r["corpus"] = C["path"]
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("missing_paragraph", len(out), "in", len({r['path'] for r in out}), "files")


if __name__ == "__main__":
    main()
