"""Probe a candidate reporter alias on the corpus: for every text occurrence of "<vol> <FORM> <page>" in the given repos,
test "<vol> <target token> <page>" against the citation index and check the name printed before it.

    python -X utf8 alias_probe.py --form-rx "Kel(?:ly|\\.)" --target ga --repos georgia [--vol-max 3] [--show 20]

Writes nothing unless --out. Evidence of agreement = a party word (>= 4 letters, not a stop word) of the indexed node's
name within the 120 characters before the citation, or the citation's parenthetical/nearby year = node year +-1.
No answer-key file is read.
"""
import argparse, collections, json, os, random, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common8 import L, load_index, party_tokens  # noqa: E402

REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--form-rx", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--repos", required=True)
    ap.add_argument("--vol-min", type=int, default=1)
    ap.add_argument("--vol-max", type=int, default=9999)
    ap.add_argument("--vol-offset", type=int, default=0, help="target volume = form volume + offset")
    ap.add_argument("--show", type=int, default=15)
    ap.add_argument("--out")
    a = ap.parse_args()
    idx = load_index()
    rx = re.compile(r"\b(\d{1,3})\s+(?:" + a.form_rx + r")\s*,?\s*(\d{1,4})\b")
    occ = []
    for repo in a.repos.split(","):
        res = subprocess.run(["git", "-C", os.path.join(REPOS, repo), "grep", "-n", "-E", "-e",
                              r"[0-9] +(" + a.form_rx.replace("(?:", "(") + r")", "HEAD"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        for line in res.splitlines():
            parts = line.split(":", 3)
            if len(parts) < 4:
                continue
            path, body = parts[1], parts[3]
            for m in rx.finditer(body):
                v, p = int(m.group(1)), m.group(2)
                if not (a.vol_min <= v <= a.vol_max):
                    continue
                occ.append((repo, path, v, p, body[max(0, m.start() - 160):m.end() + 40]))
    stat = collections.Counter()
    rows = []
    nodecache = {}
    for repo, path, v, p, ctx in occ:
        key = "%d %s %s" % (v + a.vol_offset, a.target, p)
        n = idx.get(key)
        if n is None:
            stat["no_key"] += 1
            rows.append((repo, path, key, None, "no_key", ctx))
            continue
        if n not in nodecache:
            nodecache[n] = L.node_row(n)
        nr = nodecache[n]
        toks = [t for t in party_tokens(nr[6]) if len(t) >= 4]
        pre = ctx[:170]
        ok = any(re.search(r"\b" + re.escape(t[:6]), pre, re.I) for t in toks)
        yr = nr[4][:4]
        yok = bool(re.search(r"\b(?:%d|%s|%d)\b" % (int(yr) - 1, yr, int(yr) + 1), ctx)) if yr.isdigit() else False
        if ok or yok:
            v_ = "agree"
        elif not toks:
            v_ = "unverifiable"
        else:
            # verifiable only when some capitalised name precedes the citation
            v_ = "disagree" if re.search(r"[A-Z][a-z]+\s+(?:v\.|vs\.?)\s+[A-Z]", pre[-120:]) else "unverifiable"
        stat[v_] += 1
        rows.append((repo, path, key, n, v_, ctx, nr[6]))
    print(json.dumps(dict(stat)), "occurrences", len(occ))
    vol = collections.Counter(r[2].split()[0] for r in rows)
    print("by target volume", sorted(vol.items(), key=lambda kv: int(kv[0]))[:20])
    random.seed(7)
    for kind in ("disagree", "agree", "no_key", "unverifiable"):
        sel = [r for r in rows if r[4] == kind]
        print("==", kind, len(sel))
        for r in random.sample(sel, min(a.show, len(sel))):
            print("  ", r[2], "->", r[3], (r[6] if len(r) > 6 else ""), "|", r[5].replace("\n", " ")[-200:])
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write("\t".join(str(x) for x in r[:5]) + "\t" + (r[6] if len(r) > 6 else "-") + "\t" +
                        r[5].replace("\t", " ").replace("\n", " ") + "\n")


if __name__ == "__main__":
    main()
