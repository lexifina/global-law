"""Generate Lean facts for every reference flag in ../vulnerabilities/data/flags.parquet.

For each flag (references to repealed placeholders, references to deleted provisions, dead fines) it rebuilds the dated
history of the citing and the target provision from the corpus record, and writes LegalProofs/Generated/*.lean:
the histories as `RefFlag` values, plus one theorem per chunk stating which flags Lean certifies. The same verdicts go
to tools/out/certificates.json, so the report is exactly what Lean checked.

Reads (never writes): the flags file in this repository, and a local legal-exploits workspace with the corpus index and
read-only corpus mirrors (LE_HOME, default ~/Documents/legal-exploits).

    python tools/gen_facts.py [--today 20261109] [--chunk 300]
"""
from __future__ import annotations
import argparse, collections, json, os, re, subprocess
from pathlib import Path
import duckdb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent
LE = Path(os.environ.get("LE_HOME", Path.home() / "Documents" / "legal-exploits"))
FLAGS = REPO / "vulnerabilities" / "data" / "flags.parquet"
GEN = ROOT / "LegalProofs" / "Generated"
OUT = HERE / "out"
CATS = ("References to repealed placeholders", "References to deleted provisions", "Dead fines (Germany)")
GONE = re.compile(r"(?i)\b(weggefallen|aufgehoben|revogad[oa]|derogad[oa]|abrogé|abrogée|abrogato|abrogata|repealed|deleted|"
                  r"omitted|mülga|upphävd|upphävs|kumottu|ophævet|opphevet|утратил|утратила|zrušen|zrušeno|uchylony|uchylona|"
                  r"razveljavljen|brisan|çıxarılmışdır|sin contenido|suprimid[oa]|vervallen|ingetrokken|annullato|soppresso|"
                  r"ուժը կորցրել|ձdeleted|ძალადაკარგ)")
FLAGS_NO = 0x08000000 if os.name == "nt" else 0


def is_placeholder(text: str) -> bool:
    body = re.sub(r"(?m)^#.*$", "", text).strip()
    head = text.split("\n", 1)[0]
    return (len(body) < 220 and bool(GONE.search(body or head))) or (not body and bool(GONE.search(head)))


def target_of(cat: str, path: str, reference: str) -> str | None:
    if "→" in reference:
        return reference.split("→", 1)[1].strip()
    m = re.match(r"§\s*(\d+)([a-z]?)", reference)          # dead fines: "§ 12 Abs. 2: section repealed"
    if m:
        return f"{path.split('/')[0]}/{int(m.group(1)):04d}{m.group(2)}.md"
    return None


def ymd(s: str) -> int:
    return int(s[:10].replace("-", ""))


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--today", type=int, default=20261109); ap.add_argument("--chunk", type=int, default=100)
    a = ap.parse_args()
    pins = json.loads((LE / "pins.json").read_text(encoding="utf-8"))
    repo_of = {c["path"]: c["repo"] for c in pins["corpora"]}
    con = duckdb.connect()
    flags = con.execute(f"select id, category, corpus, path, reference from '{FLAGS.as_posix()}' where category in {CATS}").fetchall()
    by_repo = collections.defaultdict(list)
    for fid, cat, corpus, path, ref in flags:
        t = target_of(cat, path, ref or "")
        if t and corpus in repo_of:
            by_repo[repo_of[corpus]].append((fid, cat, corpus, path, t))
    I = (LE / "index").as_posix()
    records = []
    for repo, items in sorted(by_repo.items()):
        f = LE / "index" / "changes" / f"{repo}.parquet"
        if not f.exists():
            continue
        paths = sorted({p for it in items for p in (it[3], it[4])})
        con.execute("create or replace temp table want(path varchar)")
        con.executemany("insert into want values (?)", [(p,) for p in paths])
        rows = con.execute(f"""select ch.path, r.in_force, left(ch.status, 1), ch.new_blob from '{f.as_posix()}' ch
            join '{I}/root.parquet' r on r.corpus_commit = ch.commit join want w on w.path = ch.path
            where r.in_force is not null and r.in_force <> '' order by ch.path, r.in_force""").fetchall()
        blobs = sorted({b for _, _, st, b in rows if st != "D" and b and set(b) != {"0"}})
        text = {}
        if blobs:
            p = subprocess.run(["git", "cat-file", "--batch"], cwd=LE / "sources" / "corpus" / f"{repo}.git",
                               input=("\n".join(blobs) + "\n").encode(), capture_output=True, creationflags=FLAGS_NO).stdout
            pos = 0
            for b in blobs:
                nl = p.index(b"\n", pos); head = p[pos:nl].split()
                if len(head) < 3 or head[1] != b"blob":
                    pos = nl + 1; continue
                size = int(head[2]); text[b] = p[nl + 1: nl + 1 + size].decode("utf-8", "replace"); pos = nl + 2 + size
        hist = collections.defaultdict(list)
        for path, inf, st, b in rows:
            exists = st != "D" and not is_placeholder(text.get(b, ""))
            h = hist[path]
            d = ymd(inf)
            if h and h[-1][0] == d:
                h[-1] = (d, exists)
            elif not h or h[-1][1] != exists:
                h.append((d, exists))
        for fid, cat, corpus, path, t in items:
            records.append({"id": fid, "category": cat, "corpus": corpus, "citing_path": path, "target_path": t,
                            "citing": list(reversed(hist.get(path, []))), "target": list(reversed(hist.get(t, [])))})

    def at(h, d):
        for t, v in h:
            if t <= d:
                return v
        return False

    for r in records:
        tgt, cit = r["target"], r["citing"]
        dead = bool(tgt) and not tgt[0][1]
        r["dead_from"] = tgt[0][0] if dead else None
        r["certified"] = bool(dead and tgt[0][0] <= a.today and at(cit, a.today))
        r["reenacted"] = bool(dead and cit and cit[0][1] and tgt[0][0] < cit[0][0])

    GEN.mkdir(parents=True, exist_ok=True)
    for old in GEN.glob("*.lean"):
        old.unlink()
    lean_list = lambda h: "[" + ", ".join(f"({d}, {'true' if v else 'false'})" for d, v in h) + "]"
    lean_bools = lambda xs: "[" + ", ".join("true" if x else "false" for x in xs) + "]"
    names = []
    for k in range(0, len(records), a.chunk):
        part = records[k:k + a.chunk]; n = len(names)
        name = f"Chunk{n:03d}"; names.append(name)
        body = ",\n  ".join(f"⟨{lean_list(r['citing'])}, {lean_list(r['target'])}⟩" for r in part)
        (GEN / f"{name}.lean").write_text(
            "import LegalProofs.History\n\n"
            "-- Generated by tools/gen_facts.py from the corpus record. Do not edit.\n"
            f"namespace Legal.Generated.{name}\n\n"
            f"def flags : List RefFlag := [\n  {body}]\n\n"
            "/-- Lean evaluates every certificate itself; the right-hand side is the generator's verdict. -/\n"
            f"theorem certified : flags.map (·.certified {a.today}) = {lean_bools([r['certified'] for r in part])} := by decide\n\n"
            f"theorem reenacted : flags.map (·.reenacted) = {lean_bools([r['reenacted'] for r in part])} := by decide\n\n"
            f"end Legal.Generated.{name}\n", encoding="utf-8", newline="\n")
    (ROOT / "LegalProofs" / "Generated.lean").write_text(
        "-- Generated by tools/gen_facts.py.\n" + "".join(f"import LegalProofs.Generated.{n}\n" for n in names),
        encoding="utf-8", newline="\n")
    OUT.mkdir(exist_ok=True)
    (OUT / "certificates.json").write_text(json.dumps({"today": a.today, "flags": records}, ensure_ascii=False), encoding="utf-8")
    c = collections.Counter((r["category"], r["certified"]) for r in records)
    print(len(records), "flags,", len(names), "chunks;", sum(r["certified"] for r in records), "certified;",
          sum(r["reenacted"] for r in records), "re-enacted;", dict(c))


if __name__ == "__main__":
    main()
