"""One record per provision (HEAD text) -> provisions.jsonl"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, ".")
D = Path.home() / "Documents"
PATS = {
    "de": ("grundgesetz", re.compile(r"^artikel/(\w+)\.md$")),
    "ch": ("swiss-law", re.compile(r"^(bv|dsg|schkg)/art-(\w+)\.md$")),
    "gb": ("uk-law-history", re.compile(r"^(ukpga|uksi)/\d+/\d+/(section|regulation)/(\w+)\.md$")),
    "us": ("us-code-history", re.compile(r"^title-(\d+)/(\w+)\.md$")),
}
import subprocess
from extract import prov_id
out = open("provisions.jsonl", "w", encoding="utf-8")
n = 0
for code, (repo, pat) in PATS.items():
    for f in subprocess.run(["git", "-C", str(D / repo), "ls-files"], capture_output=True, text=True, encoding="utf-8").stdout.splitlines():
        m = pat.match(f)
        if not m: continue
        text = (D / repo / f).read_text(encoding="utf-8", errors="ignore").strip()
        first = text.splitlines()[0].lstrip("# ").strip() if text else ""
        if len(re.sub(r"\s+", "", text)) < 40 or re.search(r"(?i)aufgehoben|repealed|\[reserved\]", text[:300]) and len(text) < 400:
            continue  # repealed or empty stubs carry no meaning to match on
        out.write(json.dumps({"id": f"{code}|{prov_id(code, m)}", "corpus": code, "file": f, "heading": first, "text": text[:7000]}, ensure_ascii=False) + "\n"); n += 1
print(n, "provisions")
