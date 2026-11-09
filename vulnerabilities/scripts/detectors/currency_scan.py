"""dead_currency: current text that states an amount in a currency that has since been replaced.
python detectors/currency_scan.py RUN -> findings/RUN/dead_currency.jsonl
"""
from __future__ import annotations
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from common import GIT_GREP_THREADS, FINDINGS, CORPUS, FLAGS, pins, lower_priority

NUM = r"[0-9][0-9.,' ]*"
CUR = (r"(australes?|pesos? (moneda nacional|ley 18\.188)|pesetas?|escudos?|francos?|francs? (français|fran.ais)|"
       r"lire|liras?|marcos?|deutsche mark|reichsmark|DM\b|sucres?|cruzeiros?|cruzados?|intis?|"
       r"bol[ií]vares fuertes|córdobas oro|zaires?|kwanzas reajustados|lei vechi|zlotych starych|"
       r"tolar(jev|ja|ev)?|kroon|krooni|litų|latu|lati|drachm(ae|as|es)|δραχμ|кроны|leva? stari|dinara?)")
PAT = rf"{NUM}\s*{CUR}|{CUR}\s*{NUM}"


def one(c):
    repo = CORPUS / (c["repo"] + ".git")
    if not repo.exists():
        return []
    p = subprocess.run(["git", "-C", str(repo), "grep", "--threads", GIT_GREP_THREADS, "-I", "-n", "-i", "-P", PAT, c["sha"], "--", "*.md"],
                       capture_output=True, creationflags=FLAGS)
    out = []
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        try:
            _, path, ln, text = line.split(":", 3)
        except ValueError:
            continue
        out.append({"corpus": c["path"], "repo": c["repo"], "path": path, "line": int(ln), "text": text[:700]})
    return out


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    f = FINDINGS / run; f.mkdir(parents=True, exist_ok=True)
    cs = [c for c in pins()["corpora"] if not c["repo"].startswith(("united-kingdom", "romania"))]
    n = 0
    with ThreadPoolExecutor(8) as ex, (f / "dead_currency.jsonl").open("w", encoding="utf-8") as fh:
        for rows in ex.map(one, cs):
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
    print("dead_currency", n)


if __name__ == "__main__":
    main()
