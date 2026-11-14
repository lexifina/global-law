"""Round 7: build a complete data directory for one variant, without touching data/, round5/ or round6/.

    python -X utf8 round7/stage7.py <name> [--delta DIR ...] [--remove FILE ...] [--drop FILE ...]
                                    [--replace FILE ...] [--claims FILE ...] [--keep-ids FILE] [--force-write]

Base = round6/history/stage/final2 (the frozen round-6 build, which contains round 5; DESIGN7). Output:
round7/stage/<name>/ with
  - the ten tables a variant may change: treatments, treatment_witness, treatment_class, history, history_anchor,
    history_claim, joined, cert_text, window_sha, cite_index. A table that ends up byte-identical to the base is a
    hard link to the base file; any other is written in full (never through a link: a temporary file replaces it).
    history_claim.tsv and joined.tsv (new in round 7) are always written, empty when no line was staged.
  - every other *.tsv of the base as a hard link (decisions2.tsv is never copied).

--delta DIR     a folder written by round7/certify7.py, round6/history/certify6.py, round5/recog/certify_recog.py or
                round5/opwords/certify_opwords.py; any of
                  treatments_delta.tsv (16 columns), treatment_witness_delta.tsv (4), treatment_class_delta.tsv (5),
                  history_delta.tsv (13), history_anchor_delta.tsv (6), history_claim_delta.tsv (3),
                  joined_delta.tsv (9), cert_text_delta.tsv, window_sha_delta.tsv, cite_index_delta.tsv
                appended in the order of the --delta options. Rules (as round5/stage.py and round6 stage6.py):
                  treatments / history row whose id is present: skipped, counted;
                  witness / class line: only for a treatments row present, first line per id;
                  anchor line: only for a history row present, first line per id;
                  history_claim line: only for a history row present, first line per (id, claim) (a row may carry
                  orderHead and setAside; LEAN7 L7-7);
                  joined line: only for a row of the named table, at most two lines per id (Lean keeps two);
                  cert_text / window_sha line whose (text_sha, start0, end0) is present with other content: skipped,
                  counted (the earlier one stands);
                  cite_index line that would give a compact key a second node: skipped, counted (Lean drops such a
                  key, which would un-resolve rows that were resolving).
                A non-empty remove_ids.txt in a delta folder is NOT applied (pass it with --remove); it is reported.
--remove FILE   ids (first column) removed from the BASE before the deltas (treatments or history ids), with their
                witness, class, anchor, claim and joined lines.
--claims FILE   extra claim lines: 5 columns -> treatment_class.tsv (first line per id), 3 columns -> history_claim.tsv
                (first line per (id, claim)); only for a row present.
--replace FILE  whole rows that replace the row with the same id: 16 columns -> treatments, 13 -> history (the scope
                rule of DESIGN7 section 6 uses it). A replacement whose id is no row is counted, not added.
--drop FILE     ids removed AFTER the deltas, claims and replacements, with every line that hangs on them.
--keep-ids FILE restrict every delta's treatments / history rows to the ids listed (ablations).
--force-write   write every table in full even when it equals the base (self-test of the write path).
Order: remove, deltas, claims, replace, drop. Lines are bytes split on LF only, so an untouched table is
byte-identical to the base. Writes round7/stage/<name>/MANIFEST.txt with counts and sha1 of the ten tables.
No answer-key file is read.
"""
import argparse
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
BASE = os.path.join(C2, "round6", "history", "stage", "final2")
STAGE = os.path.join(HERE, "stage")
TEN = ["treatments", "treatment_witness", "treatment_class", "history", "history_anchor", "history_claim", "joined",
       "cert_text", "window_sha", "cite_index"]
NEW = ("history_claim", "joined")
NCOL = {"treatments": 16, "treatment_witness": 4, "treatment_class": 5, "history": 13, "history_anchor": 6,
        "history_claim": 3, "joined": 9}
_NON = re.compile(b"[^a-z0-9]")


def read_lines(p):
    if not os.path.exists(p):
        return []
    with open(p, "rb") as f:
        return [l for l in f.read().split(b"\n") if l]


def first_col(p):
    return {l.split(b"\t")[0].strip() for l in read_lines(p)}


def compact(b):
    """Lean `Cert.compact` on bytes: ASCII letters lower-cased, then ASCII letters and digits only."""
    return _NON.sub(b"", b.lower())


def key3(l):
    p = l.split(b"\t", 3)
    return (p[0], p[1], p[2]) if len(p) >= 4 else None


def ncols(l):
    return l.count(b"\t") + 1


def sha1_file(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


class Stage:
    def __init__(self, base, log):
        self.log = log
        self.base = base
        self.tabs = {t: read_lines(os.path.join(base, t + ".tsv")) for t in TEN}
        self.changed = {t: False for t in TEN}
        log.append("base: %s" % os.path.relpath(base, C2).replace(os.sep, "/"))
        log.append("base rows: " + ", ".join("%s %d" % (t, len(self.tabs[t])) for t in TEN))
        self.reindex()

    def reindex(self):
        T = self.tabs
        self.tid = {l.split(b"\t")[0] for l in T["treatments"]}
        self.hid = {l.split(b"\t")[0] for l in T["history"]}
        self.one = {t: {self.okey(t, l) for l in T[t]}
                    for t in ("treatment_witness", "treatment_class", "history_anchor", "history_claim")}
        self.jn = {}
        for l in T["joined"]:
            i = l.split(b"\t")[0]
            self.jn[i] = self.jn.get(i, 0) + 1
        self.jlines = set(T["joined"])
        self.ct = {key3(l): l for l in T["cert_text"]}
        self.ws = {key3(l): l for l in T["window_sha"]}
        self.ci_lines = set(T["cite_index"])
        self.ci = {}
        for l in T["cite_index"]:
            p = l.split(b"\t")
            if len(p) >= 2:
                self.ci.setdefault(compact(p[0]), set()).add(p[1])

    @staticmethod
    def okey(t, l):
        """The key a line is unique by: (id, claim) for history_claim (LEAN7 L7-7), the id for the others."""
        p = l.split(b"\t")
        return (p[0], p[1] if len(p) > 1 else b"") if t == "history_claim" else p[0]

    def filter_ids(self, ids, what):
        """Remove rows (treatments / history) with these ids and every line that hangs on them."""
        for t in ("treatments", "treatment_witness", "treatment_class", "history", "history_anchor", "history_claim",
                  "joined"):
            before = len(self.tabs[t])
            self.tabs[t] = [l for l in self.tabs[t] if l.split(b"\t")[0] not in ids]
            if len(self.tabs[t]) != before:
                self.changed[t] = True
                self.log.append("%s: %s -%d" % (what, t, before - len(self.tabs[t])))
        self.reindex()

    def add_rows(self, t, lines, keep, tag):
        add = dup = bad = notkept = 0
        ids = self.tid if t == "treatments" else self.hid
        for l in lines:
            if ncols(l) != NCOL[t]:
                bad += 1
                continue
            i = l.split(b"\t")[0]
            if keep is not None and i not in keep:
                notkept += 1
                continue
            if i in ids:
                dup += 1
                continue
            ids.add(i)
            self.tabs[t].append(l)
            add += 1
        if add:
            self.changed[t] = True
        self.log.append("%s%s +%d (id present %d, wrong column count %d%s)" % (
            tag, t, add, dup, bad, ", not kept %d" % notkept if keep is not None else ""))
        if bad:
            sys.exit("%s: %d lines of %s without %d columns" % (tag, bad, t, NCOL[t]))

    def add_one(self, t, lines, tag):
        """witness / class (on treatments rows) and anchor (on history rows): first line per id; history_claim: first
        line per (id, claim)."""
        rows = self.tid if t in ("treatment_witness", "treatment_class") else self.hid
        add = norow = second = bad = 0
        for l in lines:
            if ncols(l) != NCOL[t]:
                bad += 1
                continue
            i = l.split(b"\t")[0]
            k = self.okey(t, l)
            if i not in rows:
                norow += 1
            elif k in self.one[t]:
                second += 1
            else:
                self.one[t].add(k)
                self.tabs[t].append(l)
                add += 1
        if add:
            self.changed[t] = True
        self.log.append("  %s%s +%d (no row %d, second line for an id%s %d, wrong column count %d)" % (
            tag, t, add, norow, " and claim" if t == "history_claim" else "", second, bad))

    def add_joined(self, lines, tag):
        add = norow = extra = same = bad = 0
        for l in lines:
            p = l.split(b"\t")
            if len(p) != NCOL["joined"] or p[1] not in (b"treatments", b"history"):
                bad += 1
                continue
            rows = self.tid if p[1] == b"treatments" else self.hid
            if p[0] not in rows:
                norow += 1
            elif l in self.jlines:
                same += 1
            elif self.jn.get(p[0], 0) >= 2:
                extra += 1
            else:
                self.jn[p[0]] = self.jn.get(p[0], 0) + 1
                self.jlines.add(l)
                self.tabs["joined"].append(l)
                add += 1
        if add:
            self.changed["joined"] = True
        self.log.append("  %sjoined +%d (no row %d, same line %d, third line for an id %d, malformed %d)" % (
            tag, add, norow, same, extra, bad))

    def add_windows(self, d):
        for t, m in (("cert_text", self.ct), ("window_sha", self.ws)):
            add = clash = 0
            for l in read_lines(os.path.join(d, t + "_delta.tsv")):
                k = key3(l)
                if k is None:
                    sys.exit("%s_delta.tsv in %s: malformed line" % (t, d))
                if k in m:
                    if m[k] != l:
                        clash += 1
                    continue
                m[k] = l
                self.tabs[t].append(l)
                add += 1
            if add:
                self.changed[t] = True
            self.log.append("  %s +%d (key present with other content %d)" % (t, add, clash))
        add = amb = 0
        for l in read_lines(os.path.join(d, "cite_index_delta.tsv")):
            if l in self.ci_lines:
                continue
            p = l.split(b"\t")
            if len(p) < 2:
                sys.exit("cite_index_delta.tsv in %s: malformed line" % d)
            c = compact(p[0])
            cur = self.ci.get(c)
            if cur is not None and len(cur) == 1 and p[1] not in cur:
                amb += 1
                continue
            self.ci.setdefault(c, set()).add(p[1])
            self.ci_lines.add(l)
            self.tabs["cite_index"].append(l)
            add += 1
        if add:
            self.changed["cite_index"] = True
        self.log.append("  cite_index +%d (skipped, would make a resolving key ambiguous %d)" % (add, amb))

    def delta(self, d, keep):
        if not os.path.isdir(d):
            sys.exit("no delta folder %s" % d)
        dn = os.path.relpath(os.path.abspath(d), C2).replace(os.sep, "/")
        files = [f for f in os.listdir(d) if f.endswith("_delta.tsv")]
        self.log.append("delta %s: %s" % (dn, " ".join(sorted(files)) or "(no delta file)"))
        self.add_rows("treatments", read_lines(os.path.join(d, "treatments_delta.tsv")), keep, "  ")
        self.add_rows("history", read_lines(os.path.join(d, "history_delta.tsv")), keep, "  ")
        for t in ("treatment_witness", "treatment_class", "history_anchor", "history_claim"):
            self.add_one(t, read_lines(os.path.join(d, t + "_delta.tsv")), "")
        self.add_joined(read_lines(os.path.join(d, "joined_delta.tsv")), "")
        self.add_windows(d)
        rid = read_lines(os.path.join(d, "remove_ids.txt"))
        if rid:
            self.log.append("  NOTE: %s/remove_ids.txt lists %d ids; not applied (pass it with --remove)" % (
                dn, len(rid)))

    def claims(self, f):
        five = [l for l in read_lines(f) if ncols(l) == 5]
        three = [l for l in read_lines(f) if ncols(l) == 3]
        other = len(read_lines(f)) - len(five) - len(three)
        self.log.append("claims %s: %d class lines, %d history claim lines, %d malformed" % (
            os.path.relpath(os.path.abspath(f), C2).replace(os.sep, "/"), len(five), len(three), other))
        self.add_one("treatment_class", five, "")
        self.add_one("history_claim", three, "")

    def replace(self, f):
        rep = {"treatments": {}, "history": {}}
        bad = 0
        for l in read_lines(f):
            n = ncols(l)
            if n == 16:
                rep["treatments"][l.split(b"\t")[0]] = l
            elif n == 13:
                rep["history"][l.split(b"\t")[0]] = l
            else:
                bad += 1
        for t, m in rep.items():
            if not m:
                continue
            n = 0
            seen = set()
            for k, l in enumerate(self.tabs[t]):
                i = l.split(b"\t")[0]
                if i in m:
                    seen.add(i)
                    if m[i] != l:
                        self.tabs[t][k] = m[i]
                        n += 1
            if n:
                self.changed[t] = True
            self.log.append("replace %s: %s %d rows changed, %d identical, %d ids not present" % (
                os.path.relpath(os.path.abspath(f), C2).replace(os.sep, "/"), t, n, len(seen) - n, len(m) - len(seen)))
        if bad:
            self.log.append("  replace: %d lines with neither 16 nor 13 columns ignored" % bad)

    def doctrine_check(self):
        """DESIGN7 2.4: report doctrine labels that two staged rows give different targets (Lean fails them all)."""
        tgt = {l.split(b"\t")[0]: l.split(b"\t")[2] for l in self.tabs["treatments"]}
        lab = {}
        n = 0
        for l in self.tabs["treatment_class"]:
            p = l.split(b"\t")
            if len(p) >= 4 and p[1] == b"doctrine":
                n += 1
                lab.setdefault(compact(p[3]), set()).add(tgt.get(p[0], b"?"))
        amb = sorted(k.decode() for k, v in lab.items() if len(v) > 1)
        self.log.append("doctrine class lines %d; compact labels with two targets %d%s" % (
            n, len(amb), (": " + ", ".join(amb[:10])) if amb else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--delta", action="append", default=[])
    ap.add_argument("--remove", action="append", default=[])
    ap.add_argument("--drop", action="append", default=[])
    ap.add_argument("--replace", action="append", default=[])
    ap.add_argument("--claims", action="append", default=[])
    ap.add_argument("--keep-ids")
    ap.add_argument("--force-write", action="store_true")
    ap.add_argument("--base", default=BASE, help=argparse.SUPPRESS)
    a = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", a.name) or a.name.strip(".") == "":
        sys.exit("bad stage name")
    out = os.path.join(STAGE, a.name)
    os.makedirs(out, exist_ok=True)
    log = []
    S = Stage(a.base, log)
    rem = set()
    for f in a.remove:
        rem |= first_col(f)
    if rem:
        have = S.tid | S.hid
        log.append("remove: %d ids listed, %d not in the base" % (len(rem), len(rem - have)))
        S.filter_ids(rem, "remove from base")
    keep = first_col(a.keep_ids) if a.keep_ids else None
    for d in a.delta:
        S.delta(d, keep)
    for f in a.claims:
        S.claims(f)
    for f in a.replace:
        S.replace(f)
    drop = set()
    for f in a.drop:
        drop |= first_col(f)
    if drop:
        log.append("drop: %d ids listed, %d not staged" % (len(drop), len(drop - (S.tid | S.hid))))
        S.filter_ids(drop, "drop")
    amb = sum(1 for v in S.ci.values() if len(v) > 1)
    log.append("cite_index compact keys with two nodes: %d" % amb)
    S.doctrine_check()
    for t in ("treatments", "history"):
        pre = {}
        for l in S.tabs[t]:
            k = l.split(b":", 1)[0]
            pre[k] = pre.get(k, 0) + 1
        log.append("%s rows by id prefix: %s" % (t, ", ".join("%s %d" % (k.decode(), v) for k, v in sorted(pre.items()))))
    for t in TEN:
        p = os.path.join(out, t + ".tsv")
        bp = os.path.join(a.base, t + ".tsv")
        if not S.changed[t] and os.path.exists(bp) and not a.force_write:
            if os.path.exists(p):
                if os.path.samefile(p, bp):
                    log.append("%s.tsv\t%d rows\tsha1 %s\tbase (hard link)" % (t, len(S.tabs[t]), sha1_file(p)))
                    continue
                os.remove(p)
            os.link(bp, p)
            log.append("%s.tsv\t%d rows\tsha1 %s\tbase (hard link)" % (t, len(S.tabs[t]), sha1_file(p)))
            continue
        tmp = p + ".tmp"
        h = hashlib.sha1()
        with open(tmp, "wb") as f:
            for l in S.tabs[t]:
                f.write(l + b"\n")
                h.update(l + b"\n")
        os.replace(tmp, p)
        log.append("%s.tsv\t%d rows\tsha1 %s\twritten" % (t, len(S.tabs[t]), h.hexdigest()))
    n = 0
    for fn in sorted(os.listdir(a.base)):
        if not fn.endswith(".tsv") or fn[:-4] in TEN:
            continue
        dst = os.path.join(out, fn)
        src = os.path.join(a.base, fn)
        if os.path.exists(dst):
            if os.path.samefile(dst, src):
                continue
            os.remove(dst)
        try:
            os.link(src, dst)
            n += 1
        except OSError as e:
            log.append("link failed %s: %s" % (fn, e))
    log.append("hard links made for the other tables: %d" % n)
    with open(os.path.join(out, "MANIFEST.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("stage %s\nargs: %s\n" % (a.name, " ".join(sys.argv[1:])) + "\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
