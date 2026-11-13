"""Append the staged round-2 split rows to a data directory (SCHEMA formats, LF, UTF-8).

    python install.py <data dir> [--drop work/drop.json] [--live]

Appends to holdings.tsv (14 columns), issues.tsv (new split questions), holdings_cert_text.tsv (one window per new
certificate, as assemble.py writes them). Writes <data dir>/window_sha.splits_round2.tsv (text_sha, start0, end0,
sha1 of the window, src=corpus) for the new windows; without --live it also appends those rows to the directory's
window_sha.tsv (private copy only: window_sha.tsv is not owned by this agent).
--live: for C2/data: each file is written as <name>.tmp (old content + new rows) and renamed; the original is saved
once as <name>.pre_round2.tsv. Refuses to run twice (a staged holding id already present).
Also writes round2 tables next to the staged file: splits_resolved_links.tsv, splits_new_questions.tsv."""
import os, sys, json, hashlib, shutil, collections
import common as C


def main():
    data = sys.argv[1]
    live = "--live" in sys.argv
    drop = set()
    if "--drop" in sys.argv:
        drop = set(json.load(open(sys.argv[sys.argv.index("--drop") + 1], encoding="utf-8")))
    W = os.path.join(C.PRIV, "work")
    tag = os.environ.get("RES_TAG", "")
    d = json.load(open(os.path.join(W, "staged%s.json" % tag), encoding="utf-8"))
    rows = [r for r in d["rows"] if r["hid"] not in drop and r["issue"] not in drop]
    # a question needs both sides: drop xc questions left with one answer
    ans = collections.defaultdict(set)
    for r in rows:
        if r["stream"] == "xc":
            ans[r["issue"]].add(r["answer"])
    rows = [r for r in rows if r["stream"] != "xc" or len(ans[r["issue"]]) == 2]
    keep_issues = {r["issue"] for r in rows if r["stream"] == "xc"}
    issues = [i for i in d["issues"] if i[0] in keep_issues]
    have = set()
    with open(os.path.join(data, "holdings.tsv"), encoding="utf-8") as f:
        for l in f:
            have.add(l.split("\t", 1)[0])
    if any(r["hid"] in have for r in rows):
        sys.exit("already installed (a staged holding id is present)")
    hl, cl, wl = [], [], []
    wseen = set()
    for r in rows:
        hl.append("\t".join([r["hid"], str(r["node"]), r["issue"], r["prop"].replace("\t", " "), r["answer"], r["role"],
                             r["sha"], str(r["start"]), str(r["end"]), r["quote"], r["tev"], r["role"], "claude-subagent",
                             str(r["conf"])]) + "\n")
        w0, w1, w = r["window"]
        if (r["sha"], w0, w1) not in wseen:
            wseen.add((r["sha"], w0, w1))
            cl.append("%s\t%d\t%d\t%s\n" % (r["sha"], w0, w1, w))
            wl.append("%s\t%d\t%d\t%s\tcorpus\n" % (r["sha"], w0, w1, hashlib.sha1(w.encode("utf-8")).hexdigest()))
    il = ["\t".join(x.replace("\t", " ") for x in i) + "\n" for i in issues]

    def append(name, lines):
        p = os.path.join(data, name)
        if live:
            bak = os.path.join(data, name.replace(".tsv", ".pre_round2.tsv"))
            if not os.path.exists(bak):
                shutil.copy2(p, bak)
            tmp = p + ".tmp"
            shutil.copyfile(p, tmp)
            with open(tmp, "a", encoding="utf-8", newline="\n") as f:
                f.writelines(lines)
            os.replace(tmp, p)
        else:
            with open(p, "a", encoding="utf-8", newline="\n") as f:
                f.writelines(lines)

    append("holdings.tsv", hl)
    append("issues.tsv", il)
    append("holdings_cert_text.tsv", cl)
    with open(os.path.join(data, "window_sha.splits_round2.tsv"), "a" if tag else "w", encoding="utf-8", newline="\n") as f:
        f.writelines(wl)
    if not live:
        p = os.path.join(data, "window_sha.tsv")
        if os.stat(p).st_nlink > 1:   # break the hard link to the shared file first
            shutil.copyfile(p, p + ".own")
            os.replace(p + ".own", p)
        with open(p, "a", encoding="utf-8", newline="\n") as f:
            f.writelines(wl)
    print(json.dumps({"holdings_rows": len(hl), "res": sum(1 for r in rows if r["stream"] == "res"),
                      "xc": sum(1 for r in rows if r["stream"] == "xc"), "issues": len(il), "windows": len(cl),
                      "dropped": len(d["rows"]) - len(rows)}))
    with open(os.path.join(W, "installed_rows%s.json" % tag), "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "issues": issues}, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
