"""Order-language pass for decisions whose form is still `unknown` (limit 13 in courts_validation.md).

    python orders_scan.py <cand.tsv> <out.tsv> [procs]

<cand.tsv>: node, repo, HEAD:<path> (one row per candidate; every candidate has under 600 characters of opinion text, or
it would be `full`). Each blob is read once with `git cat-file --batch` (no checkout), grouped by repo, `procs`
repos at a time (default 10). Output: node, op_len, code, evidence, where code is
  order   the opinion text (head matter excluded) is under 1,500 characters and states a disposition or an order
          (ORDER_RX below);
  none    no order language (e.g. an empty stub, a headnote-only entry, a citation line).
Only labels are written, never text beyond a 60-character evidence snippet.
"""
import os, re, subprocess, sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan import parse_fm, SEC, sec_kind, ev  # noqa: E402

REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
MAX_ORDER = 1500
# a disposition or an order made by this court: the verb forms courts use for short dispositive orders
ORDER_RX = re.compile(
    r"\b(?:it\s+is\s+(?:hereby\s+|therefore\s+|further\s+)?ordered|(?:is|are|be|was|were|stands?|hereby)\s+(?:hereby\s+)?"
    r"(?:affirmed|reversed|dismissed|denied|granted|vacated|modified|remanded|quashed|overruled|sustained|discharged|"
    r"refused|transferred|withdrawn|stricken|annulled|set\s+aside)|^\s*(?:the\s+)?(?:judgments?|orders?|decrees?|"
    r"petitions?|motions?|applications?|appeals?|writs?|rehearing|certiorari|review|leave\s+to\s+appeal)?[^\n.]{0,60}?"
    r"\b(?:affirmed|reversed|dismissed|denied|granted|vacated|modified|remanded|quashed|refused|discharged)\b|"
    r"^\s*(?:ORDER|PER CURIAM ORDER|ORDER OF (?:DISMISSAL|AFFIRMANCE|REVERSAL))\b|\bORDERED\b|\bSO ORDERED\b|"
    r"\b(?:affirm|reverse|dismiss|deny|grant|vacate|remand)\s*(?:ed)?\s+(?:on|upon|without|for\s+the\s+reasons?|"
    r"in\s+accordance|per\s+curiam)|\bwrit\s+(?:of\s+\w+\s+)?(?:denied|refused|granted|issued|dismissed|recalled)\b|"
    r"\b(?:affirmance|reversal|dismissal)\s+(?:is\s+)?(?:ordered|directed)\b)",
    re.I | re.M)


def opinion_text(text):
    fm, body = parse_fm(text)
    b = body.lstrip("\n")
    if b.startswith("# "):
        nl = b.find("\n")
        b = b[nl + 1:] if nl >= 0 else ""
    secs = [(m.start(), m.end(), m.group(1)) for m in SEC.finditer(b)]
    if not secs:
        return b
    parts = []
    if secs[0][0] > 0 and b[:secs[0][0]].strip():
        parts.append(b[:secs[0][0]])
    for i, (s, e, h) in enumerate(secs):
        nxt = secs[i + 1][0] if i + 1 < len(secs) else len(b)
        if sec_kind(h) not in "Hh":
            parts.append(b[e:nxt])
    return "\n".join(parts)


def classify(text):
    op = opinion_text(text).strip()
    if not op:
        return 0, "none", "-"
    if len(op) >= MAX_ORDER:
        return len(op), "none", "long"
    m = ORDER_RX.search(op)
    if not m:
        return len(op), "none", "-"
    return len(op), "order", ev(op[max(0, m.start() - 20):m.end() + 20])


def one_repo(args):
    repo, items = args
    p = subprocess.Popen(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=0x08000000 if os.name == "nt" else 0)
    import threading

    def feed():
        for _, sha in items:
            p.stdin.write((sha + "\n").encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    out = []
    for node, _ in items:
        header = p.stdout.readline().split()
        if len(header) < 3 or header[1] == b"missing":
            out.append((node, 0, "none", "missing"))
            continue
        data = p.stdout.read(int(header[2]))
        p.stdout.read(1)
        n, code, e = classify(data.decode("utf-8", "replace").replace("\r\n", "\n"))
        out.append((node, n, code, e))
    p.wait()
    return repo, out


def main(cand, outp, procs=10):
    by = {}
    for line in open(cand, encoding="utf-8"):
        n, repo, sha = line.rstrip("\n").split("\t")
        by.setdefault(repo, []).append((n, sha))
    jobs = []
    for repo, items in by.items():  # big repos in chunks so the pool stays busy
        for i in range(0, len(items), 20000):
            jobs.append((repo, items[i:i + 20000]))
    jobs.sort(key=lambda x: -len(x[1]))
    with open(outp + ".part", "w", encoding="utf-8", newline="\n") as fo, \
            ProcessPoolExecutor(int(procs)) as ex:
        for repo, rows in ex.map(one_repo, jobs):
            for r in rows:
                fo.write("%s\t%d\t%s\t%s\n" % r)
            print(repo, len(rows), flush=True)
    os.replace(outp + ".part", outp)


if __name__ == "__main__":
    main(*sys.argv[1:])
