"""authority_gap: a regulation cites an enabling provision that, per the record, did not exist when the regulation took effect,
never appears in the record, or lacks the cited paragraph. Reads index/authority/_done.jsonl (model-extracted citations).

python detectors/authority.py RUN -> findings/RUN/ranked_authority_gap.parquet (+ authority_resolution.parquet stats)
"""
from __future__ import annotations
import json, re, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
import duckdb, pyarrow as pa, pyarrow.parquet as pq
from common import CORPUS, FINDINGS, FLAGS, INDEX, pins

ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10, "xi": 11, "xii": 12, "xiii": 13, "xiv": 14}
REPO = {c["path"]: c for c in pins()["corpora"]}


def slug(s: str, umlaut: str = "_") -> str:
    s = s.lower().replace("ß", "ss")
    for u, t in (("ä", "a"), ("ö", "o"), ("ü", "u")):
        s = s.replace(u, umlaut if umlaut == "_" else t)
    parts = re.split(r"[^a-z0-9_]+", s)
    return "_".join(str(ROMAN.get(p, p)) for p in parts if p).strip("_")


def resolve_act(repo: str, act_id: str, act_name: str, dirs: set[str], es_titles: list[tuple[str, str]]) -> str | None:
    a = (act_id or "").strip()
    if repo == "germany-law":
        years = [int(y) for y in re.findall(r"\b(1[89]\d\d|20\d\d)\b", act_name or "")]
        for s in dict.fromkeys([slug(a, "_"), slug(a, "t")]):
            if not s:
                continue
            exact = [f"{s}_{y}" for y in years] + [f"{s}{y}" for y in years] + [f"{s}_{y+1}" for y in years] + [f"{s}{y+1}" for y in years]
            for e in exact:
                if e in dirs:
                    return e
            cands = sorted(d for d in dirs if re.fullmatch(re.escape(s) + r"_?\d{4}", d))
            if s in dirs and not cands:
                return s
            if s in dirs and years and cands:
                return None  # several editions and none matches the cited date: ambiguous
            if len(cands) == 1 and not years:
                return cands[0]
            if s in dirs:
                return s
        return None
    if repo == "switzerland-law":
        if a in dirs:
            return a
        m = re.search(r"(?<![0-9.])([0-9]{1,3}(?:[.][0-9]+)+)(?![0-9.])", a + " " + (act_name or ""))
        return m.group(1) if m and m.group(1) in dirs else None
    if repo == "sweden-law":
        m = re.search(r"(\d{4}):(\d+)", a + " " + (act_name or ""))
        return f"{m.group(1)}/{m.group(2)}" if m and f"{m.group(1)}/{m.group(2)}" in dirs else None
    if repo == "spain-law":
        m = re.search(r"(?i)(ley org[aá]nica|real decreto legislativo|real decreto-ley|real decreto|decreto legislativo|ley|decreto|orden)\s+(\d+/\d{4}|[A-Z]+/\d+/\d{4})", a + " " + (act_name or ""))
        if not m:
            return None
        key = f"{m.group(1).lower()} {m.group(2)}"
        hits = [p for t, p in es_titles if t.lower().startswith(key + ",") or t.lower().startswith(key + " ")]
        return hits[0] if len(hits) == 1 else None
    return None


_U = "cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis diecisiete dieciocho diecinueve veinte veintiuno veintidos veintitres veinticuatro veinticinco veintiseis veintisiete veintiocho veintinueve".split()
_T = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
_C = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos", 6: "seiscientos", 7: "setecientos", 8: "ochocientos", 9: "novecientos"}


def es_words(n: int) -> str:
    if n < 30:
        return _U[n]
    if n < 100:
        t, u = divmod(n, 10)
        return _T[t] + ("y" + _U[u] if u else "")
    if n == 100:
        return "cien"
    if n < 1000:
        c, r = divmod(n, 100)
        return _C[c] + (es_words(r) if r else "")
    return str(n)


_ORD = {"primero": 1, "segundo": 2, "tercero": 3, "cuarto": 4, "quinto": 5, "sexto": 6, "séptimo": 7, "septimo": 7,
        "octavo": 8, "noveno": 9, "décimo": 10, "decimo": 10, "undécimo": 11, "duodécimo": 12, "único": 1, "unico": 1}
_ESW = {}


def es_number(w: str) -> int | None:
    w = w.lower().strip(" .")
    if w.isdigit():
        return int(w)
    if w in _ORD:
        return _ORD[w]
    if not _ESW:
        for n in range(1, 1000):
            _ESW[es_words(n)] = n
    return _ESW.get(w.replace(" ", "").replace("-", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u"))


def heading_key(repo: str, heading: str) -> str | None:
    h = heading.strip()
    if repo == "spain-law":
        m = re.match(r"(?i)art[íi]culo\s+([0-9]+|[a-záéíóúñ\- ]+?)(?:\s*(bis|ter|quater))?[.\s:]", h + " ")
        if m:
            n = es_number(m.group(1))
            return f"{n}{(m.group(2) or '').lower()}" if n else None
        return None
    m = re.match(r"(?i)(?:art\.?|artikel|§+)\s*(\d+)\s*([a-z]{0,9})(?![a-z])", h)
    return f"{int(m.group(1))}{m.group(2).lower()}" if m else None


def cite_key(repo: str, prov: str) -> str | None:
    p = prov or ""
    if repo == "spain-law":
        m = re.search(r"(?i)\bart(?:[íi]culo|\.)\s*(\d+)\s*(bis|ter|quater)?", p)
        return f"{int(m.group(1))}{(m.group(2) or '').lower()}" if m else None
    if repo == "sweden-law":
        return None
    m = re.search(r"(?i)(?:art\.?|artikel|§+)\s*(\d+)\s*([a-z]{0,9})(?![a-z])", p)
    if m and m.group(2).lower() in ("abs", "absatz", "satz", "nr", "bst", "lit"):
        return str(int(m.group(1)))
    return f"{int(m.group(1))}{m.group(2).lower()}" if m else None


def provision_file(repo: str, prov: str) -> tuple[str | None, str | None]:
    """-> (relative file path inside the act folder, paragraph token to look for in its text)"""
    p = prov or ""
    para = None
    m = re.search(r"(?i)\b(?:Abs\.?|Absatz|apartado|al\.)\s*(\d+[a-z]?)", p)
    if m:
        para = m.group(1)
    if repo == "germany-law":
        m = re.search(r"§+\s*(\d+)\s*([a-z]?)\b", p)
        return (f"{int(m.group(1)):04d}{m.group(2)}.md", para) if m else (None, para)
    if repo == "switzerland-law":
        m = re.search(r"(?i)Art\.?\s*(\d+)([a-z]{0,9})(?![a-z])", p)
        return (f"art-{int(m.group(1)):03d}{m.group(2).lower()}.md", para) if m else (None, para)
    if repo == "spain-law":
        m = re.search(r"(?i)\bart(?:[íi]culo|\.)\s*(\d+)(?:\.(\d+))?", p)
        if m and m.group(2) and not para:
            para = m.group(2)
        return (f"a{int(m.group(1))}.md", para) if m else (None, para)
    if repo == "sweden-law":
        m = re.search(r"(?i)(\d+\s*[a-z]?)\s*kap\.?\s*(\d+\s*[a-z]?)\s*§", p)
        if m:
            return (f"kap-{m.group(1).replace(' ', '')}/{m.group(2).replace(' ', '')}.md", para)
        m = re.search(r"(\d+\s*[a-z]?)\s*§", p)
        return (f"{m.group(1).replace(' ', '')}.md", para) if m else (None, para)
    return None, para


def para_present(repo: str, text: str, para: str) -> bool:
    if repo == "germany-law":
        return f"({para})" in text
    if repo == "spain-law":
        return bool(re.search(rf"(?m)^\s*{re.escape(para)}[.)]\s", text))
    if repo == "switzerland-law":
        return bool(re.search(rf"(?m)^\s*(?:<sup>)?{re.escape(para)}(?:</sup>)?[.)]?\s", text))
    return True


def main() -> None:
    run = sys.argv[1] if len(sys.argv) > 1 else "run1"
    out = FINDINGS / run
    con = duckdb.connect()
    recs = [json.loads(l) for l in (INDEX / "authority" / "_done.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rows, stats = [], {}
    for repo in {r["repo"] for r in recs}:
        corpus = next(r["corpus"] for r in recs if r["repo"] == repo)
        ch = (INDEX / "changes" / f"{repo}.parquet").as_posix()
        ev = con.sql(f"""select ch.path, left(ch.status,1) st, ch.new_blob, r.in_force, r.law, r.kind
                         from '{ch}' ch join '{(INDEX/'root.parquet').as_posix()}' r on r.corpus_commit = ch.commit
                         where r.kind in ('law','baseline') order by r.in_force""").fetchall()
        hist: dict[str, list] = {}
        for path, st, blob, inf, law, kind in ev:
            hist.setdefault(path, []).append((inf, st, blob, law))
        dirs = {p.rsplit("/", 1)[0] for p in hist if "/" in p}
        hk: dict[tuple[str, str], str] = {}
        hp = (INDEX / "headings" / f"{repo}.parquet").as_posix()
        for path, heading in con.sql(f"""select distinct ch.path, h.heading from '{ch}' ch join '{hp}' h on h.blob = ch.new_blob""").fetchall():
            k = heading_key(repo, heading or "")
            if k and "/" in path:
                hk.setdefault((path.rsplit("/", 1)[0], k), path)
        if repo == "sweden-law":
            dirs |= {"/".join(p.split("/")[:2]) for p in hist if p.count("/") >= 2}
        dir_start: dict[str, str] = {}
        for p, h in hist.items():
            for d in {p.rsplit("/", 1)[0], "/".join(p.split("/")[:2])}:
                if d not in dir_start or h[0][0] < dir_start[d]:
                    dir_start[d] = h[0][0]
        es_titles = []
        if repo == "spain-law":
            tsv = subprocess.run(["git", "show", f"{REPO[corpus]['sha']}:normas.tsv"], cwd=CORPUS / f"{repo}.git",
                                 capture_output=True, creationflags=FLAGS).stdout.decode("utf-8", errors="replace")
            for line in tsv.splitlines()[1:]:
                f = line.split("\t")
                if len(f) >= 9:
                    es_titles.append((f[8], f[2]))
        st = stats.setdefault(repo, {"cites": 0, "act_resolved": 0, "file_resolved": 0, "tested": 0, "flagged": 0})
        cat = subprocess.Popen(["git", "cat-file", "--batch"], cwd=CORPUS / f"{repo}.git", stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, creationflags=FLAGS)

        def text_of(blob: str) -> str:
            cat.stdin.write(blob.encode() + b"\n"); cat.stdin.flush()
            head = cat.stdout.readline().split()
            if len(head) < 3:
                return ""
            d = cat.stdout.read(int(head[2])); cat.stdout.read(1)
            return d.decode("utf-8", errors="replace")

        for r in recs:
            if r["repo"] != repo:
                continue
            D = r["act_first_in_force"]
            ph = hist.get(r["preamble_path"], [])
            if ph and ph[-1][0] and (not D or ph[-1][0] > D):
                D = ph[-1][0]  # the current preamble wording only speaks from the day it took effect
            for c in r["cites"]:
                if c["role"] != "enabling_power":
                    continue
                st["cites"] += 1
                act = resolve_act(repo, c["act_id"], c["act_name"], dirs, es_titles)
                if not act or act == r["act_dir"]:
                    continue
                st["act_resolved"] += 1
                fname, para = provision_file(repo, c["provision"])
                if not fname:
                    continue
                path = f"{act}/{fname}"
                ck = cite_key(repo, c["provision"])
                if path not in hist and ck and (act, ck) in hk:
                    path = hk[(act, ck)]
                if repo == "spain-law" and path not in hist:
                    m_ = re.match(r"a(\d+)\.md$", fname)
                    if m_:
                        alt = f"{act}/a{es_words(int(m_.group(1)))}.md"
                        if alt in hist:
                            path = alt
                st["file_resolved"] += 1
                h = hist.get(path, [])
                start = dir_start.get(act)
                issue, detail, blob_at = None, "", None
                if not (start and D and D > start):
                    st["not_testable"] = st.get("not_testable", 0) + 1  # regulation predates the cited act's record
                    continue
                if not h:
                    issue = "never_in_record"
                    detail = f"{path} never appears in the record of {act} (record from {start}), yet the regulation of {D} cites it"
                else:
                    before = [e for e in h if e[0] <= D]
                    if not before:
                        issue = "not_yet_in_force"
                        detail = f"{path} first appears {h[0][0]} ({h[0][3]}), after the regulation took effect {D}"
                    elif before[-1][1] == "D":
                        issue = "already_repealed"
                        detail = f"{path} was removed {before[-1][0]} by {before[-1][3]}, before the regulation took effect {D}"
                    else:
                        blob_at = before[-1][2]
                st["tested"] += 1
                if not issue and para and blob_at and repo == "germany-law":
                    t = text_of(blob_at)
                    if re.search(r"(?i)zuk(ü|ue)nftig in kraft|\(weggefallen\)|noch nicht in kraft", t) or len(t) < 120:
                        st["placeholder"] = st.get("placeholder", 0) + 1  # corpus holds a placeholder, not text
                    elif t and not para_present(repo, t, para):
                        issue = "paragraph_absent"
                        detail = f"cited {c['provision']} but the version of {path} in force then has no paragraph ({para})"
                if issue:
                    st["flagged"] += 1
                    rows.append({"corpus": corpus, "regulation": r["act_dir"], "preamble_path": r["preamble_path"],
                                 "in_force": D, "cited_act": c["act_id"], "cited_act_dir": act, "provision": c["provision"],
                                 "cited_path": path, "issue": issue, "detail": detail, "record_start": start,
                                 "removed_by": before[-1][3] if issue == "already_repealed" else None})
        cat.stdin.close(); cat.wait()
    weight = {"paragraph_absent": 0.9, "not_yet_in_force": 0.85, "already_repealed": 0.8, "never_in_record": 0.4}
    for x in rows:
        x["score"] = weight[x["issue"]]
        x["why"] = x["detail"]
    t = pa.Table.from_pylist(rows) if rows else pa.table({"corpus": pa.array([], pa.string())})
    pq.write_table(t, out / "ranked_authority_gap.parquet", compression="zstd")
    (out / "authority_stats.json").write_text(json.dumps(stats, indent=1), encoding="utf-8")
    print(json.dumps(stats, indent=1))
    if rows:
        import collections
        print(collections.Counter((x["corpus"], x["issue"]) for x in rows))


if __name__ == "__main__":
    main()
