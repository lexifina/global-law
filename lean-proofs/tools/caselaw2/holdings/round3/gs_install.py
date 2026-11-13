"""Append the staged round-3 gold-section split rows to a data directory, as a DELTA (BRIEF rule 12).

    python gs_install.py <data dir> [--live] [--drop drop.json] [--merge-1546]

Appends to holdings.tsv (14 columns), issues.tsv, holdings_cert_text.tsv; writes <data dir>/window_sha.splits_round3.tsv
(text_sha, start0, end0, sha1(window), corpus). Without --live (private copy) the hash rows are also appended to that
directory's window_sha.tsv and hard links are broken first. With --live: takes C2/data/.install.lock, re-reads the live
files, writes <name>.tmp and renames; saves <name>.pre_round3.tsv once; refuses to run twice.
The delta itself is saved to work/round3/splits/delta/ (holdings.add.tsv, issues.add.tsv, holdings_cert_text.add.tsv,
window_sha.add.tsv, and holdings.replace.tsv for --merge-1546).
--merge-1546: the duplicate question usc:18:1546(a):x0 is merged into usc:18:1546(a):q35 (holdings rows of x0 get the
issue key q35; the x0 issue row stays, unused). Same polarity: both ask whether the clause requires an oath.
"""
import collections, hashlib, json, os, shutil, sys, time
HT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HT)
import text

C2 = os.path.join(text.WORK, "caselaw-lean-2")
PRIV = os.path.join(C2, "work", "round3", "splits")
OLD, NEW = "usc:18:1546(a):x0", "usc:18:1546(a):q35"


def main():
    data = sys.argv[1]
    live = "--live" in sys.argv
    merge = "--merge-1546" in sys.argv
    drop = set()
    if "--drop" in sys.argv:
        drop = set(json.load(open(sys.argv[sys.argv.index("--drop") + 1], encoding="utf-8")))
    d = json.load(open(os.path.join(PRIV, "w", "staged.json"), encoding="utf-8"))
    rows = [r for r in d["rows"] if r["issue"] not in drop and r["hid"] not in drop]
    circ = collections.defaultdict(set)
    for r in rows:
        circ[r["issue"]].add(r["circ"])
    rows = [r for r in rows if len(circ[r["issue"]]) >= 2]
    keep = {r["issue"] for r in rows}
    issues = [i for i in d["issues"] if i[0] in keep]
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
    dd = os.path.join(PRIV, "delta")
    os.makedirs(dd, exist_ok=True)
    for name, lines in (("holdings.add.tsv", hl), ("issues.add.tsv", il), ("holdings_cert_text.add.tsv", cl),
                        ("window_sha.add.tsv", wl)):
        with open(os.path.join(dd, name), "w", encoding="utf-8", newline="\n") as f:
            f.writelines(lines)
    lock = os.path.join(data, ".install.lock")
    if live:
        for _ in range(60):
            try:
                os.mkdir(lock)
                break
            except FileExistsError:
                time.sleep(5)
        else:
            sys.exit("install lock busy")
        with open(os.path.join(lock, "owner"), "w") as f:
            f.write("splits\n")
    try:
        hp = os.path.join(data, "holdings.tsv")
        have = set()
        merged = []
        old = []
        with open(hp, encoding="utf-8", newline="") as f:
            for l in f:
                c = l.split("\t", 3)
                have.add(c[0])
                if merge and c[2] == OLD:
                    merged.append(l)
                    l = "\t".join([c[0], c[1], NEW, c[3]])
                old.append(l)
        if any(r["hid"] in have for r in rows):
            sys.exit("already installed (a staged holding id is present)")
        if merge:
            with open(os.path.join(dd, "holdings.replace.tsv"), "w", encoding="utf-8", newline="\n") as f:
                f.write("# rows whose issue_key was changed from %s to %s (original rows below)\n" % (OLD, NEW))
                f.writelines(merged)

        def put(name, lines, whole=None):
            p = os.path.join(data, name)
            if live:
                bak = os.path.join(data, name.replace(".tsv", ".pre_round3.tsv"))
                if not os.path.exists(bak):
                    shutil.copy2(p, bak)
            tmp = p + ".tmp"
            if whole is not None:
                with open(tmp, "w", encoding="utf-8", newline="") as f:
                    f.writelines(whole)
                    f.writelines(lines)
            else:
                shutil.copyfile(p, tmp)
                with open(tmp, "a", encoding="utf-8", newline="\n") as f:
                    f.writelines(lines)
            os.replace(tmp, p)   # replaces the name: a hard-linked private copy no longer shares the live file

        put("holdings.tsv", hl, whole=old)
        put("issues.tsv", il)
        put("holdings_cert_text.tsv", cl)
        with open(os.path.join(data, "window_sha.splits_round3.tsv"), "w", encoding="utf-8", newline="\n") as f:
            f.writelines(wl)
        if not live:
            p = os.path.join(data, "window_sha.tsv")
            shutil.copyfile(p, p + ".tmp")
            with open(p + ".tmp", "a", encoding="utf-8", newline="\n") as f:
                f.writelines(wl)
            os.replace(p + ".tmp", p)
    finally:
        if live:
            try:
                os.remove(os.path.join(lock, "owner"))
                os.rmdir(lock)
            except OSError:
                pass
    print(json.dumps({"holdings_rows": len(hl), "issues": len(il), "windows": len(cl),
                      "merged_1546_rows": len(merged), "dropped": len(d["rows"]) - len(rows)}))
    json.dump({"rows": rows, "issues": issues}, open(os.path.join(PRIV, "w", "installed_rows.json"), "w", encoding="utf-8"),
              ensure_ascii=False)


if __name__ == "__main__":
    main()
