"""Depth-1 clones (current text only) of every municipal corpus (*-city-law) -> text/<repo>. Reruns pull instead."""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
TX = HERE / "text"; TX.mkdir(exist_ok=True)
urls = [l.split("=", 1)[1].strip() for l in (HERE / "gitmodules.txt").read_text(encoding="utf-8").splitlines() if l.strip().startswith("url") and "-city-law" in l]


def one(url):
    repo = url.rstrip("/").removesuffix(".git").split("/")[-1]; d = TX / repo
    cmd = ["git", "-C", str(d), "pull", "-q", "--depth", "1"] if d.exists() else ["git", "clone", "-q", "--depth", "1", url, str(d)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    print(repo, "ok" if r.returncode == 0 else "FAILED " + r.stderr.strip()[:80], flush=True)


with ThreadPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 6) as ex:
    list(ex.map(one, urls))
print(len(urls), "municipal corpora")
