"""Extract the precedent facts from one US case-law repo of global-law (CAP / CourtListener build).

    python tools/caselaw/extract.py <repo-dir> <out-dir>

Reads every decision file at HEAD through `git cat-file --batch` (the repos have no checkout) and writes, per repo:
  <name>.nodes.tsv      path, court, decided, decision_type, citations (|), cap_id, docket, name, cites (|)
  <name>.overrul.jsonl  every sentence of the opinion text that mentions overruling, with its offset
  <name>.relations.tsv  the repo's decision-relations.tsv (parallel-reporter copies)
Only front matter and the overruling sentences are kept; full texts are not copied.
"""
import json, os, re, subprocess, sys, threading

FM_KEYS = ("court", "decided", "decision_type", "citations", "cap_id", "docket", "parties", "cites_cases")
OVR = re.compile(r"overrul|disapprov", re.I)
SENT_END = re.compile(r"(?<=[.;:!?])\s+(?=[A-Z\"“(\[])")


def parse_fm(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm = {}
    for line in text[3:end].splitlines():
        k, sep, v = line.partition(":")
        if not sep or k not in FM_KEYS:
            continue
        v = v.strip()
        try:
            fm[k] = json.loads(v)
        except Exception:
            fm[k] = v.strip('"')
    return fm, text[end + 4:]


def sentences_with(body):
    """A window around each mention of overruling: 500 characters before, 400 after (sentence splitting breaks on
    the abbreviations of case names and reporters, so the window is cut later, by the classifier)."""
    out = []
    last = -1
    for m in OVR.finditer(body):
        if m.start() < last:
            continue
        s0, s1 = max(0, m.start() - 500), min(len(body), m.end() + 400)
        out.append((m.start() - s0, s0, body[s0:s1].replace("\n", " ")))
        last = s1 - 300
    return out


def clean(x):
    return str(x).replace("\t", " ").replace("\n", " ").strip()


def main(repo, outdir):
    name = os.path.basename(os.path.normpath(repo))
    os.makedirs(outdir, exist_ok=True)
    tree = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "HEAD", "--", "decisions"], capture_output=True, check=True).stdout.decode("utf-8")
    items = []
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        _, typ, sha = meta.split()
        if typ == "blob" and path.endswith(".md"):
            items.append((sha, path))
    rel = subprocess.run(["git", "-C", repo, "show", "HEAD:decision-relations.tsv"], capture_output=True)
    with open(os.path.join(outdir, name + ".relations.tsv"), "wb") as f:
        f.write(rel.stdout if rel.returncode == 0 else b"")
    p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    nodes = open(os.path.join(outdir, name + ".nodes.tsv.part"), "w", encoding="utf-8", newline="\n")
    ovr = open(os.path.join(outdir, name + ".overrul.jsonl.part"), "w", encoding="utf-8", newline="\n")
    n = 0

    def feed():
        for sha, _ in items:
            p.stdin.write((sha + "\n").encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    if True:
        for sha, path in items:
            header = p.stdout.readline().split()
            size = int(header[2])
            data = p.stdout.read(size)
            p.stdout.read(1)
            text = data.decode("utf-8", "replace")
            fm, body = parse_fm(text)
            parties = fm.get("parties") or []
            title = ""
            m = re.search(r"^# (.+)$", body, re.M)
            if m:
                title = m.group(1)
            row = [path, clean(fm.get("court", "")), clean(fm.get("decided", "")), clean(fm.get("decision_type", "")),
                   "|".join(clean(c) for c in (fm.get("citations") or [])), clean(fm.get("cap_id", "")),
                   clean(fm.get("docket", "")), clean(title or (parties[0] if parties else ""))[:200],
                   "|".join(clean(c) for c in (fm.get("cites_cases") or []))]
            nodes.write("\t".join(row) + "\n")
            if "verrul" in body or "isapprov" in body:
                heads = [(m.start(), m.group(1).strip()) for m in re.finditer(r"^## (.+)$", body, re.M)]
                for at, off, s in sentences_with(body):
                    sec = ""
                    for hpos, h in heads:
                        if hpos <= off + at:
                            sec = h
                        else:
                            break
                    ovr.write(json.dumps({"path": path, "off": off, "at": at, "sec": sec[:80], "s": s},
                                         ensure_ascii=False) + "\n")
            n += 1
    p.wait()
    nodes.close(); ovr.close()
    os.replace(os.path.join(outdir, name + ".nodes.tsv.part"), os.path.join(outdir, name + ".nodes.tsv"))
    os.replace(os.path.join(outdir, name + ".overrul.jsonl.part"), os.path.join(outdir, name + ".overrul.jsonl"))
    print(name, n, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
