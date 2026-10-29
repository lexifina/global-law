"""Pull amendment edges and cross-references from the four local law repos into kg.json."""
import json, re, subprocess, sys
from pathlib import Path
from collections import Counter

DOCS = Path.home() / "Documents"
OUT = Path(sys.argv[1]) if __name__ == "__main__" else None

CORPORA = {
    "de": ("grundgesetz", "Germany", "Grundgesetz", re.compile(r"^artikel/(\w+)\.md$")),
    "ch": ("swiss-law", "Switzerland", "BV · DSG · SchKG", re.compile(r"^(bv|dsg|schkg)/art-(\w+)\.md$")),
    "gb": ("uk-law-history", "United Kingdom", "SEND law (CFA 2014 Pt 3, SEND Regs 2014)", re.compile(r"^(ukpga|uksi)/\d+/\d+/(section|regulation)/(\w+)\.md$")),
    "us": ("us-code-history", "United States", "US Code (9 titles)", re.compile(r"^title-(\d+)/(\w+)\.md$")),
}
DOC_AUTHORS = {"Lexifina", "Lexifina Watch"}
DATE_RE = re.compile(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", re.M)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(DOCS / repo), *args], capture_output=True, text=True, encoding="utf-8").stdout


def prov_id(code, m):
    g = m.groups()
    if code == "de":
        return "Art. " + g[0].lstrip("0")
    if code == "ch":
        return f"{g[0].upper()} Art. {g[1].lstrip('0')}"
    if code == "gb":
        return ("CFA s." if g[0] == "ukpga" else "SEND Reg ") + g[2]
    return f"{g[0]} USC § {g[1]}"


def main():
    data = {"corpora": {}, "laws": [], "xrefs": {}}
    for code, (repo, country, name, pat) in CORPORA.items():
        files = [f for f in git(repo, "ls-files").splitlines() if pat.match(f)]
        provisions = [prov_id(code, pat.match(f)) for f in files]
        log = git(repo, "log", "--reverse", "--format=\x1e%an\x1f%ad\x1f%B\x1d", "--date=short", "--name-only")
        laws = []
        for chunk in log.split("\x1e")[1:]:
            head, _, names = chunk.partition("\x1d")
            author, adate, body = head.split("\x1f", 2)
            if author in DOC_AUTHORS:
                continue
            m = DATE_RE.search(body)
            date = m.group(1) if m else adate
            if date.startswith("1970"):
                y = re.search(r"\((\d{4})\)", author)
                date = f"{y.group(1)}-06-30" if y else date
            touched = [prov_id(code, pat.match(f)) for f in names.split() if pat.match(f)]
            if touched:
                laws.append({"corpus": code, "law": author, "date": date, "provisions": touched})
        data["laws"] += laws
        data["corpora"][code] = {"country": country, "name": name, "provisions": len(provisions),
                                 "laws": len(laws), "first": laws[0]["date"] if laws else None,
                                 "last": laws[-1]["date"] if laws else None,
                                 "hot": Counter(p for l in laws for p in l["provisions"]).most_common(6)}

        # Cross-references at HEAD
        edges = Counter()
        for f in files:
            src = prov_id(code, pat.match(f))
            text = (DOCS / repo / f).read_text(encoding="utf-8", errors="ignore")
            if code == "de":
                for mm in re.finditer(r"Artikel[n]?\s+((?:\d+[a-z]?(?:\s*(?:,|und|bis|oder)\s*)?)+)", text):
                    for n in re.findall(r"\d+[a-z]?", mm.group(1)):
                        edges[(src, "Art. " + n)] += 1
            elif code == "us":
                for t, s in re.findall(r"section\s+(\w+)\s+of\s+title\s+(\d+)", text):
                    edges[(src, f"title {s}")] += 1
                title = src.split()[0]
                for s in re.findall(r"section\s+(\d+\w*)\s+of\s+this\s+title", text):
                    edges[(src, f"{title} USC § {s}")] += 1
            elif code == "ch":
                law = src.split()[0]
                for n in re.findall(r"Art(?:ikel|\.)\s+(\d+[a-z]*)", text):
                    edges[(src, f"{law} Art. {n}")] += 1
        data["xrefs"][code] = [[a, b, c] for (a, b), c in edges.items() if a != b]

    OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    for c, v in data["corpora"].items():
        print(c, v["provisions"], v["laws"], v["first"], v["last"], v["hot"][:3], "xrefs", len(data["xrefs"].get(c, [])))

if __name__ == "__main__":
    main()
