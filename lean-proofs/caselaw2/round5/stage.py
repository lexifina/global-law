"""Round 5: build a complete data directory for one model variant, without touching data/.

    python round5/stage.py <name> [--delta DIR ...] [--claims FILE ...] [--remove FILE ...] [--replace FILE ...]
                           [--keep-ids FILE] [--no-class]

Base = the round-4 tables (data/<t>.pre_round5.tsv when it exists, else data/<t>.tsv; nothing is installed in data/
until the end of the round). Output: round5/stage/<name>/ with
  - the six tables a variant may change, written in full: treatments.tsv, treatment_witness.tsv,
    treatment_class.tsv, cert_text.tsv, window_sha.tsv, cite_index.tsv
  - every other data/*.tsv as a hard link (so the scorers can be pointed at the folder).
--delta DIR     a folder with any of treatments_delta.tsv, treatment_witness_delta.tsv, treatment_class_delta.tsv,
                cert_text_delta.tsv, window_sha_delta.tsv, cite_index_delta.tsv (rows appended; a treatments /
                witness / class row whose id is already present is skipped and counted)
--claims FILE   extra treatment_class rows (5 columns)
--remove FILE   treatment ids to drop (first column), with their witness and class lines
--replace FILE  full treatments rows that replace the row with the same id (e.g. a corrected scope)
--keep-ids FILE restrict every delta's treatments rows to the ids listed (first column); used for ablations
--no-class      do not write treatment_class.tsv (round-4 mode on round-5 rows; for tests)
Writes round5/stage/<name>/MANIFEST.txt with the counts and sha1 of the six tables. LF line endings throughout.
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
DATA = os.path.join(C2, "data")
SIX = ["treatments", "treatment_witness", "treatment_class", "cert_text", "window_sha", "cite_index"]


def base_path(t):
    p = os.path.join(DATA, t + ".pre_round5.tsv")
    return p if os.path.exists(p) else os.path.join(DATA, t + ".tsv")


def read_lines(p):
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return [l.rstrip("\n").rstrip("\r") for l in f if l.strip("\r\n")]


def first_col(p):
    return {l.split("\t")[0] for l in read_lines(p)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--delta", action="append", default=[])
    ap.add_argument("--claims", action="append", default=[])
    ap.add_argument("--remove", action="append", default=[])
    ap.add_argument("--replace", action="append", default=[])
    ap.add_argument("--drop", action="append", default=[])
    ap.add_argument("--keep-ids")
    ap.add_argument("--no-class", action="store_true")
    a = ap.parse_args()
    out = os.path.join(HERE, "stage", a.name)
    os.makedirs(out, exist_ok=True)
    log = []
    tabs = {t: read_lines(base_path(t)) for t in SIX}
    log.append("base: " + ", ".join("%s %d" % (t, len(tabs[t])) for t in SIX))
    keep = first_col(a.keep_ids) if a.keep_ids else None
    # removals apply to the BASE tables first: a delta may bring a corrected row under the same id
    rem0 = set()
    for f in a.remove:
        rem0 |= first_col(f)
    if rem0:
        for t in ("treatments", "treatment_witness", "treatment_class"):
            before = len(tabs[t])
            tabs[t] = [l for l in tabs[t] if l.split("\t")[0] not in rem0]
            log.append("remove from base: %s -%d" % (t, before - len(tabs[t])))
    a.remove = []
    ids = {t: {l.split("\t")[0] for l in tabs[t]} for t in ("treatments", "treatment_witness", "treatment_class")}
    seen = {t: set(tabs[t]) for t in ("cert_text", "window_sha", "cite_index")}
    for d in a.delta:
        new_ids = set()
        rows = read_lines(os.path.join(d, "treatments_delta.tsv"))
        add = dup = dropped = 0
        for l in rows:
            i = l.split("\t")[0]
            if keep is not None and i not in keep:
                dropped += 1
                continue
            if i in ids["treatments"]:
                dup += 1
                continue
            ids["treatments"].add(i)
            new_ids.add(i)
            tabs["treatments"].append(l)
            add += 1
        log.append("delta %s: treatments +%d (dup %d, not kept %d)" % (d, add, dup, dropped))
        for t in ("treatment_witness", "treatment_class"):
            add = 0
            for l in read_lines(os.path.join(d, t + "_delta.tsv")):
                i = l.split("\t")[0]
                if i in ids[t] or (i not in new_ids and i not in ids["treatments"]):
                    continue
                if keep is not None and i not in keep:
                    continue
                ids[t].add(i)
                tabs[t].append(l)
                add += 1
            log.append("  %s +%d" % (t, add))
        for t in ("cert_text", "window_sha", "cite_index"):
            add = 0
            for l in read_lines(os.path.join(d, t + "_delta.tsv")):
                if l in seen[t]:
                    continue
                seen[t].add(l)
                tabs[t].append(l)
                add += 1
            log.append("  %s +%d" % (t, add))
    for f in a.claims:
        add = 0
        for l in read_lines(f):
            i = l.split("\t")[0]
            if i in ids["treatment_class"] or i not in ids["treatments"]:
                continue
            ids["treatment_class"].add(i)
            tabs["treatment_class"].append(l)
            add += 1
        log.append("claims %s: +%d" % (f, add))
    for f in a.replace:
        rep = {l.split("\t")[0]: l for l in read_lines(f)}
        n = 0
        for k, l in enumerate(tabs["treatments"]):
            i = l.split("\t")[0]
            if i in rep and rep[i] != l:
                tabs["treatments"][k] = rep[i]
                n += 1
        log.append("replace %s: %d rows changed" % (f, n))
    rem = set()
    for f in a.remove:
        rem |= first_col(f)
    if rem:
        for t in ("treatments", "treatment_witness", "treatment_class"):
            before = len(tabs[t])
            tabs[t] = [l for l in tabs[t] if l.split("\t")[0] not in rem]
            log.append("remove: %s -%d" % (t, before - len(tabs[t])))
    # --drop: ids removed AFTER the deltas (a new row found wrong), with their witness and class lines
    drop = set()
    for f in a.drop:
        drop |= first_col(f)
    if drop:
        for t in ("treatments", "treatment_witness", "treatment_class"):
            before = len(tabs[t])
            tabs[t] = [l for l in tabs[t] if l.split("\t")[0] not in drop]
            log.append("drop: %s -%d" % (t, before - len(tabs[t])))
    for t in SIX:
        p = os.path.join(out, t + ".tsv")
        if t == "treatment_class" and a.no_class:
            if os.path.exists(p):
                os.remove(p)
            continue
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            for l in tabs[t]:
                f.write(l + "\n")
        h = hashlib.sha1(open(p, "rb").read()).hexdigest()
        log.append("%s.tsv\t%d rows\tsha1 %s" % (t, len(tabs[t]), h))
    # hard links for everything else
    n = 0
    for fn in sorted(os.listdir(DATA)):
        if not fn.endswith(".tsv") or ".pre_" in fn or ".v1." in fn or fn[:-4] in SIX:
            continue
        dst = os.path.join(out, fn)
        if not os.path.exists(dst):
            try:
                os.link(os.path.join(DATA, fn), dst)
                n += 1
            except OSError as e:
                log.append("link failed %s: %s" % (fn, e))
    log.append("hard links made: %d" % n)
    with open(os.path.join(out, "MANIFEST.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("stage %s\nargs: %s\n" % (a.name, " ".join(sys.argv[1:])) + "\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
