"""dup_label: one current file holds two live units with the same label (two '§ 3º', two 'Artículo 9 Bis').
Usually two amending laws each inserted 'the next number'. python detectors/dup_labels.py RUN -> findings/RUN/dup_label.jsonl"""
from __future__ import annotations
import collections, json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from common import FINDINGS, CORPUS, FLAGS, pins, lower_priority, WORKERS

LAB = re.compile(r"^\s*(?:#+\s*|\*\*|- )?(§+\s*\d+[º°o]?(?:[-‑ ]?[A-Z]{1,2}\b)?|(?:Art\.|Artigo|Artículo|Article|Articolo|Artikel|Art)\s+\d+[º°o]?(?:[-‑ ]?(?:[A-Z]{1,2}|bis|ter|quater|quáter|quinquies|sexies|septies|octies|nonies|decies))?\b"
                 r"|Par[áa]grafo [úu]nico|Párrafo\s+\d+[º°o]?)", re.I)
REVOKED = re.compile(r"(?i)revogad|derogad|abrogad|repealed|aufgehoben|\(vetado\)|vetad|suprimid|\.{3,}|…")


def one(c):
    repo = CORPUS / (c["repo"] + ".git")
    if not repo.exists():
        return []
    ls = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "-z", "--format=%(objectname) %(path)", c["sha"]],
                        capture_output=True, creationflags=FLAGS).stdout.decode("utf-8", "replace").split("\0")
    items = [x.split(" ", 1) for x in ls if x.endswith(".md") and not x.rsplit("/", 1)[-1].startswith(("README", "index", "REPRO"))]
    if not items:
        return []
    p = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"], input=("\n".join(s for s, _ in items) + "\n").encode(),
                       capture_output=True, creationflags=FLAGS).stdout
    out, pos = [], 0
    for sha, path in items:
        nl = p.index(b"\n", pos); size = int(p[pos:nl].split()[2]); body = p[nl + 1: nl + 1 + size].decode("utf-8", "replace"); pos = nl + 2 + size
        seen = collections.defaultdict(list)
        for i, line in enumerate(body.splitlines()):
            m = LAB.match(line)
            if m and not REVOKED.search(line[:160]) and len(line.strip()) > len(m.group(0)) + 15:
                k = re.sub(r"[\s‑-]+", " ", m.group(1).lower()).replace("°", "º").replace("art.", "art").strip()
                seen[k].append((i, line.strip()[:400]))
        for k, v in seen.items():
            if len(v) > 1:
                out.append({"corpus": c["path"], "repo": c["repo"], "path": path, "label": k, "n": len(v),
                            "lines": [x[1] for x in v[:4]]})
    return out


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    f = FINDINGS / run
    cs = [c for c in pins()["corpora"] if not c["repo"].startswith(("united-kingdom", "romania"))]
    n = 0
    with ThreadPoolExecutor(WORKERS) as ex, (f / "dup_label.jsonl").open("w", encoding="utf-8") as fh:
        for rows in ex.map(one, cs):
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
    print("dup_label", n)


if __name__ == "__main__":
    main()
