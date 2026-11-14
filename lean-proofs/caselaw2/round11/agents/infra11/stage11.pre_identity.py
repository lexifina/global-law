"""Round 11: build a complete data directory for one variant, without touching data/ or earlier rounds' folders.
(= round10/stage10.py as patched by the round-10 lead (history_remand 12 columns, history_tbridge) with base
round10/stage/v10d, output round11/stage/<name>/, zones from round11/zones11.py; agent infra11.)
(= round9/stage9.py with base round9/stage/v9c, output round10/stage/<name>/, EXTRA_TABLES history_bridge +
part_zone + history_remand (DESIGN10 section 4), adoption / succession listed in TABLES.txt, and part zones added
for the acting text nodes of staged rows that have none (round10/zones10.py, calpart9's builder);
round9/stage9.py = round8/stage8.py with --table; round8/stage8.py = round7/stage7.py with extra tables.)

    python -X utf8 round11/stage11.py <name> [--delta DIR ...] [--remove FILE ...] [--drop FILE ...]
                                      [--replace FILE ...] [--claims FILE ...] [--keep-ids FILE] [--force-write]
                                      [--extra-table NAME ...] [--table NAME=FILE ...] [--no-zones] [--procs N]

Base = round10/stage/v10d (the frozen round-10 build, which contains rounds 5-10; DESIGN11 D11-1), used in place,
read-only. Output: round11/stage/<name>/ with
  - the ten tables a variant may change: treatments, treatment_witness, treatment_class, history, history_anchor,
    history_claim, joined, cert_text, window_sha, cite_index. A table that ends up byte-identical to the base is a
    hard link to the base file; any other is written in full (never through a link: a temporary file replaces it).
    history_claim.tsv and joined.tsv (new in round 7) are always written, empty when no line was staged.
  - EXTRA tables (round 8): a table a round-8 Lean rule reads (e.g. a docket index) is named ONCE, in EXTRA_TABLES
    below (or for a trial with --extra-table NAME). Its lines come from `<NAME>_delta.tsv` in the delta folders
    (appended in order; an exact line already present is skipped, counted); the base's <NAME>.tsv, when the base has
    one, is the start. An extra table that ends up empty and is not in the base is NOT written (round-8 mode by
    presence: absent => round-7 behaviour). --remove / --drop do not touch extra tables (their keys are the rule's).
  - TABLES.txt: one line per staged table (name, rows, sha1, base|written); wsl/r11_run.sh copies exactly these
    tables into the variant's data dir (so a new extra table needs no edit of the run script).
  - every other *.tsv of the base as a hard link (decisions2.tsv is never copied).

--delta DIR     a folder written by round11/certify11.py, round10/certify10.py, round9/certify9.py, round7/certify7.py, round6/history/certify6.py, round5/recog/certify_recog.py or
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
--table NAME=FILE  (round 9) the base's non-row table NAME.tsv (e.g. adoption, succession) is replaced by a copy of
                FILE (non-empty, LF only), listed in TABLES.txt (how = table) so wsl/r11_run.sh copies it and freeze11.py
                hashes it. Refused for the ten row tables, decisions2 and the extra tables.
Order: remove, deltas, claims, replace, drop. Lines are bytes split on LF only, so an untouched table is
byte-identical to the base. Writes round11/stage/<name>/MANIFEST.txt with counts and sha1 of the staged tables.
Round 10 additions:
  - part zones (DESIGN9 section 4, v9c's part_zone.tsv covers every round-9 row): after remove / deltas / claims /
    replace / drop, every staged row's acting text node (treatments: `by`, or the witness node; history: `by` when
    decisions2's text_sha of `by` equals the row's, else `target`) that has no part_zone line gets its zone lines
    from round11/zones11.py (= round10/zones10.py = round9/agents/calpart9/build_zones.py's per-node builder, same rules, same line
    format). --no-zones skips this (logged). --procs N (default 8) for the zone builder.
  - adoption / succession (v9c's New Jersey tables) are listed in TABLES.txt (how = base, or table with --table).
Round 11 addition (infra11, DESIGN11 section 4):
  --nodes DIR     order-list nodes (DIR/nodes.tsv + DIR/text/<local id>.txt, format round11/data_orders/FORMAT.md;
                  loaded by round11/nodes11.py): node ids N, N+1, ... (N = corpus node count 6,892,454) in nodes.tsv
                  order; decisions2.tsv is written as a NEW file (base bytes + one row per node: court 2906, date,
                  0 wholeCourt published memorandum, text_sha = sha1 of the text file; about 873 MB) and listed in
                  TABLES.txt (how = nodes); decisions2_nodes.tsv (those rows), nodes.count (wsl/r11_run.sh passes it
                  to the runner) and nodes_map.tsv (local id, node, date, docket, text_sha) are written. Loaded before
                  the deltas, so the zone step sees the nodes (zones11: an order text whose builder zones are all
                  `other` gets no zone line). Without --nodes none of this exists (v10d byte for byte).
No answer-key file is read.
"""
import argparse
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
BASE = os.path.join(C2, "round10", "stage", "v10d")
STAGE = os.path.join(HERE, "stage")
TEN = ["treatments", "treatment_witness", "treatment_class", "history", "history_anchor", "history_claim", "joined",
       "cert_text", "window_sha", "cite_index"]
NEW = ("history_claim", "joined")
# Round 8/9/10: tables a Lean rule may add. List a new table HERE (one place); stage10 stages it from
# `<name>_delta.tsv` files and lists it in TABLES.txt, and wsl/r10_run.sh copies whatever TABLES.txt lists.
# history_remand: DESIGN10 section 4 (id, b_node, b_start, b_end, docket); absent or empty => not written
# (round-9 mode by presence).
# history_bridge: D8-3 (in the v8e base). part_zone: DESIGN9 section 4 (node, z_start, z_end, part, src); absent
# or empty => not written (round-8 mode by presence).
EXTRA_TABLES = ["history_bridge", "part_zone", "history_remand", "history_tbridge"]
XCOL = {"part_zone": 5, "history_remand": 12, "history_tbridge": 3}  # lead 04:31: D10-7 (12 columns), section 6 table  # lines of an extra table with another column count are reported
# round 10: base non-row tables listed in TABLES.txt (hard links, how = base) so r10_run.sh / freeze10.py see them
LISTED = ["adoption", "succession"]
STAGED = list(TEN)  # TEN + the extra tables of this run (set in main)
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
        self.tabs = {t: read_lines(os.path.join(base, t + ".tsv")) for t in STAGED}
        self.changed = {t: False for t in STAGED}
        self.xlines = {t: set(self.tabs[t]) for t in STAGED if t not in TEN}
        log.append("base: %s" % os.path.relpath(base, C2).replace(os.sep, "/"))
        log.append("base rows: " + ", ".join("%s %d" % (t, len(self.tabs[t])) for t in STAGED))
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
        for t in STAGED:
            if t not in TEN:
                self.add_extra(t, read_lines(os.path.join(d, t + "_delta.tsv")))
        unknown = sorted(f[:-10] for f in files if f[:-10] not in STAGED and f[:-10] != "treatments_items")
        if unknown:
            self.log.append("  NOTE: delta files of tables that are not staged (not in EXTRA_TABLES): %s" %
                            " ".join(unknown))
        rid = read_lines(os.path.join(d, "remove_ids.txt"))
        if rid:
            self.log.append("  NOTE: %s/remove_ids.txt lists %d ids; not applied (pass it with --remove)" % (
                dn, len(rid)))

    def add_extra(self, t, lines):
        """Round 8: an extra table: append each line not yet present (exact bytes)."""
        add = same = 0
        for l in lines:
            if l in self.xlines[t]:
                same += 1
                continue
            self.xlines[t].add(l)
            self.tabs[t].append(l)
            add += 1
        if add:
            self.changed[t] = True
        self.log.append("  %s (extra) +%d (same line present %d)" % (t, add, same))
        if t in XCOL:
            bad = sum(1 for l in lines if l.count(b"\t") + 1 != XCOL[t])
            if bad:
                self.log.append("  NOTE: %s: %d delta lines without %d columns (staged as given; Lean ignores / "
                                "counts them)" % (t, bad, XCOL[t]))

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
    ap.add_argument("--extra-table", action="append", default=[],
                    help="trial only: stage one more extra table (the permanent list is EXTRA_TABLES)")
    ap.add_argument("--table", action="append", default=[], metavar="NAME=FILE",
                    help="round 9: replace the base's non-row table NAME.tsv by a copy of FILE (listed in TABLES.txt)")
    ap.add_argument("--base", default=BASE, help=argparse.SUPPRESS)
    ap.add_argument("--no-zones", action="store_true", help="round 10: do not add part zones for new rows' nodes")
    ap.add_argument("--procs", type=int, default=8, help="round 10: processes of the zone builder")
    ap.add_argument("--nodes", help="round 11: a DESIGN11 section-4 order-node folder (nodes.tsv + text/), e.g. "
                                    "round11/data_orders: decisions2.tsv gets their rows (a new file), nodes.count and "
                                    "nodes_map.tsv are written")
    a = ap.parse_args()
    # round 11 (infra11): order nodes (round11/nodes11.py) are loaded before the deltas, so the zone step sees them
    if a.nodes:
        sys.path.insert(0, HERE)
        import nodes11
        nn = nodes11.activate(a.nodes)
        if not nn:
            sys.exit("--nodes %s: no node in nodes.tsv" % a.nodes)
    # round 9 (lead, 14 Nov): --table NAME=FILE replaces a base non-row table (e.g. adoption, succession) by a copy of
    # FILE. Refused for the ten row tables, decisions2 and the extra tables; FILE must be non-empty, LF only.
    repl = {}
    for spec in a.table:
        if "=" not in spec:
            sys.exit("--table wants NAME=FILE, got %s" % spec)
        t, f = spec.split("=", 1)
        if not re.fullmatch(r"[a-z0-9_]+", t) or t in TEN or t == "decisions2" or t in EXTRA_TABLES + a.extra_table:
            sys.exit("--table %s refused: a row table, decisions2 or an extra table" % t)
        if t in repl:
            sys.exit("--table %s given twice" % t)
        if not os.path.isfile(f):
            sys.exit("--table %s: no file %s" % (t, f))
        data = open(f, "rb").read()
        if not data or b"\r" in data or not data.endswith(b"\n"):
            sys.exit("--table %s: %s is empty, has CR or does not end with LF" % (t, f))
        if not os.path.exists(os.path.join(a.base, t + ".tsv")):
            print("NOTE: --table %s: the base has no %s.tsv (the table is added)" % (t, t))
        repl[t] = (f, data)
    for t in EXTRA_TABLES + a.extra_table:
        if not re.fullmatch(r"[a-z0-9_]+", t) or t in ("decisions2",):
            sys.exit("bad extra table name %s" % t)
        if t not in STAGED:
            STAGED.append(t)
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
    # round 10: part zones for the acting text nodes of staged rows that have none (zones11.py = zones10.py)
    if a.no_zones:
        log.append("part zones: --no-zones (not checked, none added)")
    else:
        import zones11
        zl, zinfo = zones11.missing_zone_lines(S.tabs, os.path.join(a.base, "decisions2.tsv"), procs=a.procs)
        log.append("part zones: " + zinfo)
        if zl:
            S.add_extra("part_zone", zl)
    amb = sum(1 for v in S.ci.values() if len(v) > 1)
    log.append("cite_index compact keys with two nodes: %d" % amb)
    S.doctrine_check()
    for t in ("treatments", "history"):
        pre = {}
        for l in S.tabs[t]:
            k = l.split(b":", 1)[0]
            pre[k] = pre.get(k, 0) + 1
        log.append("%s rows by id prefix: %s" % (t, ", ".join("%s %d" % (k.decode(), v) for k, v in sorted(pre.items()))))
    tables = []
    for t in STAGED:
        p = os.path.join(out, t + ".tsv")
        bp = os.path.join(a.base, t + ".tsv")
        if t not in TEN and not S.tabs[t] and not os.path.exists(bp):
            if os.path.exists(p):
                os.remove(p)
            log.append("%s.tsv\t0 rows\textra table, empty: not written" % t)
            continue
        if not S.changed[t] and os.path.exists(bp) and not a.force_write:
            if os.path.exists(p):
                if os.path.samefile(p, bp):
                    h = sha1_file(p)
                    log.append("%s.tsv\t%d rows\tsha1 %s\tbase (hard link)" % (t, len(S.tabs[t]), h))
                    tables.append((t, len(S.tabs[t]), h, "base"))
                    continue
                os.remove(p)
            os.link(bp, p)
            h = sha1_file(p)
            log.append("%s.tsv\t%d rows\tsha1 %s\tbase (hard link)" % (t, len(S.tabs[t]), h))
            tables.append((t, len(S.tabs[t]), h, "base"))
            continue
        tmp = p + ".tmp"
        h = hashlib.sha1()
        with open(tmp, "wb") as f:
            for l in S.tabs[t]:
                f.write(l + b"\n")
                h.update(l + b"\n")
        os.replace(tmp, p)
        log.append("%s.tsv\t%d rows\tsha1 %s\twritten" % (t, len(S.tabs[t]), h.hexdigest()))
        tables.append((t, len(S.tabs[t]), h.hexdigest(), "written"))
    for t, (f, data) in sorted(repl.items()):
        p = os.path.join(out, t + ".tsv")
        tmp = p + ".tmp"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, p)  # replaces the directory entry: a hard link to the base file is never written through
        h = hashlib.sha1(data).hexdigest()
        rows = data.count(b"\n")
        log.append("%s.tsv\t%d rows\tsha1 %s\treplaced by --table from %s" % (
            t, rows, h, os.path.relpath(os.path.abspath(f), C2).replace(os.sep, "/")))
        tables.append((t, rows, h, "table"))
    for t in LISTED:  # round 10: v9c's adoption / succession are listed (how = base) unless --table replaced them
        bp = os.path.join(a.base, t + ".tsv")
        if t in repl or not os.path.exists(bp):
            continue
        p = os.path.join(out, t + ".tsv")
        if os.path.exists(p) and not os.path.samefile(p, bp):
            os.remove(p)
        if not os.path.exists(p):
            os.link(bp, p)
        h = sha1_file(p)
        rows = len(read_lines(p))
        log.append("%s.tsv\t%d rows\tsha1 %s\tbase (hard link, listed)" % (t, rows, h))
        tables.append((t, rows, h, "base"))
    # round 11 (infra11, DESIGN11 section 4): order nodes -> decisions2.tsv = the base file + their rows (a NEW file,
    # never written through the base link), decisions2_nodes.tsv (those rows alone: wsl/r11_run.sh rebuilds the data
    # dir's decisions2 from its base mirror + this file and checks the sha1), nodes.count, nodes_map.tsv. Without
    # --nodes none of these exist (round-10 data byte for byte).
    for fn in ("decisions2_nodes.tsv", "nodes.count", "nodes_map.tsv"):
        if os.path.exists(os.path.join(out, fn)):
            os.remove(os.path.join(out, fn))
    if a.nodes:
        dl = [x.encode("utf-8") for x in nodes11.decisions_lines()]
        bp = os.path.join(a.base, "decisions2.tsv")
        p = os.path.join(out, "decisions2.tsv")
        tmp = p + ".tmp"
        h = hashlib.sha1()
        rows = 0
        with open(bp, "rb") as fi, open(tmp, "wb") as fo:
            for chunk in iter(lambda: fi.read(1 << 22), b""):
                h.update(chunk)
                fo.write(chunk)
                rows += chunk.count(b"\n")
            for l in dl:
                h.update(l + b"\n")
                fo.write(l + b"\n")
        rows += len(dl)
        if rows != nodes11.count():
            os.remove(tmp)
            sys.exit("--nodes: decisions2 would have %d rows, node count %d (base rows != corpus node count?)" % (
                rows, nodes11.count()))
        if os.path.exists(p):
            os.remove(p)
        os.replace(tmp, p)
        with open(os.path.join(out, "decisions2_nodes.tsv"), "wb") as fo:
            fo.write(b"".join(l + b"\n" for l in dl))
        with open(os.path.join(out, "nodes.count"), "w", encoding="utf-8", newline="\n") as fo:
            fo.write("%d\n" % nodes11.count())
        with open(os.path.join(out, "nodes_map.tsv"), "w", encoding="utf-8", newline="\n") as fo:
            fo.write("local_id\tnode\tdate\tdocket\ttext_sha\n" + "".join(x + "\n" for x in nodes11.map_lines()))
        log.append("decisions2.tsv\t%d rows\tsha1 %s\twritten (base + %d order nodes %d..%d from %s; %.0f MB new file)"
                   % (rows, h.hexdigest(), len(dl), nodes11.base_count(), nodes11.count() - 1,
                      os.path.relpath(nodes11.folder(), C2).replace(os.sep, "/"), os.path.getsize(p) / 1048576))
        log.append("nodes.count %d; nodes_map.tsv %d lines" % (nodes11.count(), len(dl)))
        tables.append(("decisions2", rows, h.hexdigest(), "nodes"))
    n = 0
    for fn in sorted(os.listdir(a.base)):
        if not fn.endswith(".tsv") or fn[:-4] in STAGED or fn[:-4] in repl or (a.nodes and fn == "decisions2.tsv"):
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
    with open(os.path.join(out, "TABLES.txt"), "w", encoding="utf-8", newline="\n") as f:
        for t, n, h, how in tables:
            f.write("%s\t%d\t%s\t%s\n" % (t, n, h, how))
    print("\n".join(log))


if __name__ == "__main__":
    main()
