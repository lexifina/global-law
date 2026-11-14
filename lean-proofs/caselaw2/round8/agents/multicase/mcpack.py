"""Round 8, agent `multicase`: reader packs from cands.jsonl.gz.

    python -X utf8 mcpack.py [--per 40]

Reads cands.jsonl.gz (mccands.py). An item is read unless every resolved target already has an admitted explicit
status row for the pair in v3 (`base`). Items are ordered by acting court group (state first, then federal, then
the Supreme Court), then by id, and cut into packs of --per items: packs/pack_NNN.md, packs/index.tsv (item id,
pack), packs/map.jsonl (item id -> T-number -> target record). No answer key is read.
"""
import argparse, collections, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402
C = L.reader_common()
NL = chr(10)
PART_LABEL = {"majority": "majority", "majority~": "majority", "perCuriam": "per curiam", "plurality": "plurality"}


def view_of(text):
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    return C.unwrap_view(text, body0) if C.hard_wrapped(text, body0) else text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=40)
    ap.add_argument("--append", action="store_true",
                    help="add packs after the existing ones for items not yet in packs/index.tsv")
    a = ap.parse_args()
    F = L.Facts()
    items = []
    st = collections.Counter()
    done, npk0 = set(), 0
    if a.append:
        for l in open(os.path.join(HERE, "packs", "index.tsv"), encoding="utf-8"):
            i, pk = l.rstrip(NL).split("\t")
            done.add(i)
            npk0 = max(npk0, int(pk.split("_")[1]))
    with gzip.open(os.path.join(HERE, "cands.jsonl.gz"), "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["id"] in done:
                st["skip_already_packed"] += 1
                continue
            if r["targets"] and all(t["base"] for t in r["targets"]):
                st["skip_all_base"] += 1
                continue
            if not r["targets"]:
                st["skip_no_target"] += 1
                continue
            items.append(r)
    st["items"] = len(items)

    def grp(r):
        c = r["by_court"]
        if F.is_scotus(c):
            return 2
        return 1 if F.system(c) == 0 else 0
    items.sort(key=lambda r: (grp(r), r["n"], r["s"][0]))
    texts = {}
    nodes = sorted({r["n"] for r in items})
    for k in range(0, len(nodes), 2000):
        texts.update(L.fetch_texts(nodes[k:k + 2000]))
        print("texts", len(texts), file=sys.stderr, flush=True)
    os.makedirs(os.path.join(HERE, "packs"), exist_ok=True)
    mode = "a" if a.append else "w"
    idx = open(os.path.join(HERE, "packs", "index.tsv"), mode, encoding="utf-8", newline=NL)
    mp = open(os.path.join(HERE, "packs", "map.jsonl"), mode, encoding="utf-8", newline=NL)
    npk = npk0
    for k in range(0, len(items), a.per):
        npk += 1
        name = "pack_%03d" % npk
        out = ["# %s (%d items)" % (name, len(items[k:k + a.per])), ""]
        for r in items[k:k + a.per]:
            if r["n"] not in texts:
                st["no_text"] += 1
                continue
            v = view_of(texts[r["n"]][1])
            s0, s1 = r["s"]
            p0 = r["p"][0] if r["p"][1] > r["p"][0] else s0
            w0 = max(0, min(p0, s0) - 600)
            w1 = min(len(v), s1 + 400)
            marks = []
            tmap = {}
            tl = []
            for i, t in enumerate(r["targets"], 1):
                tn = "T%d" % i
                tmap[tn] = t
                marks.append((t["hit"][1], "[%s]" % tn))
                d = str(t["date"])
                tl.append("- %s: %s, %s, %s-%s-%s, court %s; %s %s; %s" % (
                    tn, t["name"] or "?", t["cite"] or "?", d[:4], d[4:6], d[6:8], F.court_name(t["court"]),
                    t["how"], json.dumps(t["ev"][5:] if t["how"] == "cite" else v[t["hit"][0]:t["hit"][1]],
                                         ensure_ascii=False),
                    "in act" if t["where"] == "act" else "before"))
            ins = sorted([(s0, "⟦"), (s1, "⟧")] + [m for m in marks if w0 <= m[0] <= w1], key=lambda x: x[0])
            buf, pos = [], w0
            for off, tok in ins:
                buf.append(v[pos:off])
                buf.append(tok)
                pos = off
            buf.append(v[pos:w1])
            win = "".join(buf).replace("\r", "")
            d = str(r["by_date"])
            out += ["### ITEM %s" % r["id"],
                    "ACTING: %s, %s, %s, %s-%s-%s; part: %s" % (r["by_name"] or "?", r["by_cite"] or "?",
                                                               F.court_name(r["by_court"]), d[:4], d[4:6], d[6:8],
                                                               PART_LABEL.get(r["part"], r["part"])),
                    "TARGETS:"] + tl + ["WINDOW:", "```", win, "```", "ACT: " + L.norm(v[s0:s1]), ""]
            idx.write("%s\t%s\n" % (r["id"], name))
            mp.write(json.dumps({"id": r["id"], "n": r["n"], "s": r["s"], "p": r["p"], "part": r["part"],
                                 "flags": r["flags"], "own": r["own"], "by_court": r["by_court"],
                                 "by_date": r["by_date"], "by_system": r["by_system"], "targets": tmap},
                                ensure_ascii=False) + NL)
        with open(os.path.join(HERE, "packs", name + ".md"), "w", encoding="utf-8", newline=NL) as f:
            f.write(NL.join(out) + NL)
    idx.close()
    mp.close()
    st["packs"] = npk
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
