"""Generic step: for a TSV of (citing, cited[, actor]) rows, fetch each citing decision from git, find where it cites
the cited decision, and record the passages plus regex flags.

    python passages.py <in.tsv> <out.jsonl> <citing col> <cited col> [<actor col>] [--workers 8]

Flags per row:
  hits        number of places the citing text cites the cited decision (by citation, else by name)
  ack_word    a negative-history word within the window (overrul, abrogat, disapprov, recede, supersed, vacat, rev'd,
              reversed, no longer good law, questioned, called into doubt, limited)
  ack_actor   the negating decision (actor) is cited within the window
  actor_any   the negating decision is cited anywhere in the citing text
  binding_lang binding-language cue within 300 chars (bound by, binding, controlling, must follow, compels, ...)
  unpub_lang  'unpublished' / 'not for publication' / 'table' within 300 chars
"""
import json, os, re, sys
from multiprocessing import Pool
import hcommon as C

ACK = re.compile(r"overrul|abrogat|disapprov|recede|receded|supersed|vacat|rev'd|revd|reversed|no longer good law|"
                 r"questioned|called into doubt|limited by|repudiat|abandon|rejected by|no longer (?:the )?law|"
                 r"no longer valid|no longer viable|no longer controlling|no longer follow|modified by", re.I)
BIND = re.compile(r"\bbound by\b|\bbinding\b|\bcontrolling\b|\bcontrols\b|\bmust follow\b|\bare bound\b|\bis bound\b|"
                  r"\bcompels?\b|\bforeclose[sd]?\b|\bwe (?:are|remain) (?:obliged|obligated|required) to\b|"
                  r"\bprecedent(?:ial)?\b|\bgoverns?\b|\bdispositive\b|\bstare decisis\b", re.I)
UNPUB = re.compile(r"unpublished|not (?:selected |designated )?for publication|table decision|\(table\)|"
                   r"non-?precedential|nonprecedential|unreported|slip op|memorandum (?:opinion|decision)|"
                   r"summary order|not precedential|without published opinion", re.I)


def work(args):
    items, metas, cites = args
    texts = C.fetch(metas)
    res = []
    for it in items:
        citing, cited, actor = it["citing"], it["cited"], it.get("actor")
        t = texts.get(citing)
        if t is None:
            res.append(dict(it, hits=-1))
            continue
        b = C.body(t)
        md = metas.get(cited)
        locs = C.locate(b, cites.get(cited, []), md["name"] if md else "", width=900) if md else []
        apats = C.cite_patterns(cites.get(actor, [])) if actor else []
        actor_any = any(rx.search(b) for rx in apats)
        win = locs[0][2] if locs else ""
        flags = dict(hits=len(locs), ack_word=0, ack_actor=0, actor_any=int(actor_any), binding_lang=0, unpub_lang=0)
        for s, e, w in locs:
            if ACK.search(w):
                flags["ack_word"] = 1
            if any(rx.search(w) for rx in apats):
                flags["ack_actor"] = 1
            near = b[max(0, s - 300):e + 300]
            if BIND.search(near):
                flags["binding_lang"] = 1
            if UNPUB.search(near):
                flags["unpub_lang"] = 1
        windows = [b[max(0, s - 900):e + 900] for s, e, _ in locs[:3]]
        res.append(dict(it, **flags, windows=windows, textlen=len(b)))
    return res


def run(rows, out_path, workers=8, chunk=300):
    """rows: list of dicts with citing, cited, (actor) ints plus anything else to carry."""
    ids = set()
    for r in rows:
        ids.add(r["citing"]); ids.add(r["cited"])
        if r.get("actor"):
            ids.add(r["actor"])
    meta = C.nodes(ids)
    cites = C.cites_of(ids)
    # also the node's own cite strings from nodes.tsv (cite_index lacks some)
    for n, m in meta.items():
        for c in m["cite"].split("|"):
            cc = re.sub(r"[.,]", "", c).lower()
            cc = re.sub(r"\s+", " ", cc).strip()
            if cc and cc not in cites[n]:
                cites[n].append(cc)
    rows = [r for r in rows if r["citing"] in meta]
    rows.sort(key=lambda r: (meta[r["citing"]]["repo"], r["citing"]))
    jobs = []
    for k in range(0, len(rows), chunk):
        part = rows[k:k + chunk]
        need = {r["citing"] for r in part} | {r["cited"] for r in part} | {r["actor"] for r in part if r.get("actor")}
        jobs.append((part, {n: meta[n] for n in need if n in meta}, {n: cites.get(n, []) for n in need}))
    n = 0
    with open(out_path, "w", encoding="utf-8", newline="\n") as f, Pool(workers) as pool:
        for res in pool.imap_unordered(work, jobs):
            for r in res:
                f.write(json.dumps(r) + "\n")
            n += len(res)
            if n % 3000 < len(res):
                C.log("passages", n, "/", len(rows))
    return n


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    workers = 8
    if "--workers" in sys.argv:
        workers = int(sys.argv[sys.argv.index("--workers") + 1])
    inp, out, ccol, dcol = a[0], a[1], a[2], a[3]
    acol = a[4] if len(a) > 4 else None
    rows = []
    with open(inp, encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        for line in f:
            p = line.rstrip("\n").split("\t")
            d = dict(zip(hdr, p))
            d["citing"] = int(d[ccol]); d["cited"] = int(d[dcol])
            if acol:
                d["actor"] = int(d[acol]) if d[acol].lstrip("-").isdigit() else None
            rows.append(d)
    run(rows, out, workers)


if __name__ == "__main__":
    main()
