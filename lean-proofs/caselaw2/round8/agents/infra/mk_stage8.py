"""infra: derive round8/stage8.py from round7/stage7.py by exact replacements (kept for the record)."""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src = open(os.path.join(C2, "round7", "stage7.py"), "rb").read().decode("utf-8")
reps = [
 ('''"""Round 7: build a complete data directory for one variant, without touching data/, round5/ or round6/.

    python -X utf8 round7/stage7.py <name> [--delta DIR ...] [--remove FILE ...] [--drop FILE ...]
                                    [--replace FILE ...] [--claims FILE ...] [--keep-ids FILE] [--force-write]

Base = round6/history/stage/final2 (the frozen round-6 build, which contains round 5; DESIGN7). Output:
round7/stage/<name>/ with''',
  '''"""Round 8: build a complete data directory for one variant, without touching data/ or earlier rounds' folders.
(= round7/stage7.py with base round7/stage/v3, output round8/stage/<name>/, and an extensible staged-table list.)

    python -X utf8 round8/stage8.py <name> [--delta DIR ...] [--remove FILE ...] [--drop FILE ...]
                                    [--replace FILE ...] [--claims FILE ...] [--keep-ids FILE] [--force-write]
                                    [--extra-table NAME ...]

Base = round7/stage/v3 (the frozen round-7 build, which contains rounds 5 and 6; DESIGN8 D8-1). Output:
round8/stage/<name>/ with'''),
 ('''  - every other *.tsv of the base as a hard link (decisions2.tsv is never copied).
''',
  '''  - EXTRA tables (round 8): a table a round-8 Lean rule reads (e.g. a docket index) is named ONCE, in EXTRA_TABLES
    below (or for a trial with --extra-table NAME). Its lines come from `<NAME>_delta.tsv` in the delta folders
    (appended in order; an exact line already present is skipped, counted); the base's <NAME>.tsv, when the base has
    one, is the start. An extra table that ends up empty and is not in the base is NOT written (round-8 mode by
    presence: absent => round-7 behaviour). --remove / --drop do not touch extra tables (their keys are the rule's).
  - TABLES.txt: one line per staged table (name, rows, sha1, base|written); wsl/r8_run.sh copies exactly these
    tables into the variant's data dir (so a new extra table needs no edit of the run script).
  - every other *.tsv of the base as a hard link (decisions2.tsv is never copied).
'''),
 ("byte-identical to the base. Writes round7/stage/<name>/MANIFEST.txt with counts and sha1 of the ten tables.",
  "byte-identical to the base. Writes round8/stage/<name>/MANIFEST.txt with counts and sha1 of the staged tables."),
 ('BASE = os.path.join(C2, "round6", "history", "stage", "final2")', 'BASE = os.path.join(C2, "round7", "stage", "v3")'),
 ('''NEW = ("history_claim", "joined")
''', '''NEW = ("history_claim", "joined")
# Round 8: tables a round-8 Lean rule may add. List a new table HERE (one place); stage8 stages it from
# `<name>_delta.tsv` files and lists it in TABLES.txt, and wsl/r8_run.sh copies whatever TABLES.txt lists.
EXTRA_TABLES = []
STAGED = list(TEN)  # TEN + the extra tables of this run (set in main)
'''),
 ('''        self.tabs = {t: read_lines(os.path.join(base, t + ".tsv")) for t in TEN}
        self.changed = {t: False for t in TEN}
        log.append("base: %s" % os.path.relpath(base, C2).replace(os.sep, "/"))
        log.append("base rows: " + ", ".join("%s %d" % (t, len(self.tabs[t])) for t in TEN))''',
  '''        self.tabs = {t: read_lines(os.path.join(base, t + ".tsv")) for t in STAGED}
        self.changed = {t: False for t in STAGED}
        self.xlines = {t: set(self.tabs[t]) for t in STAGED if t not in TEN}
        log.append("base: %s" % os.path.relpath(base, C2).replace(os.sep, "/"))
        log.append("base rows: " + ", ".join("%s %d" % (t, len(self.tabs[t])) for t in STAGED))'''),
 ('''        self.add_windows(d)
        rid = read_lines(os.path.join(d, "remove_ids.txt"))''',
  '''        self.add_windows(d)
        for t in STAGED:
            if t not in TEN:
                self.add_extra(t, read_lines(os.path.join(d, t + "_delta.tsv")))
        unknown = sorted(f[:-10] for f in files if f[:-10] not in STAGED and f[:-10] != "treatments_items")
        if unknown:
            self.log.append("  NOTE: delta files of tables that are not staged (not in EXTRA_TABLES): %s" %
                            " ".join(unknown))
        rid = read_lines(os.path.join(d, "remove_ids.txt"))'''),
 ('''    def claims(self, f):''',
  '''    def add_extra(self, t, lines):
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

    def claims(self, f):'''),
 ('''    ap.add_argument("--force-write", action="store_true")
    ap.add_argument("--base", default=BASE, help=argparse.SUPPRESS)
    a = ap.parse_args()''',
  '''    ap.add_argument("--force-write", action="store_true")
    ap.add_argument("--extra-table", action="append", default=[],
                    help="trial only: stage one more extra table (the permanent list is EXTRA_TABLES)")
    ap.add_argument("--base", default=BASE, help=argparse.SUPPRESS)
    a = ap.parse_args()
    for t in EXTRA_TABLES + a.extra_table:
        if not re.fullmatch(r"[a-z0-9_]+", t) or t in ("decisions2",):
            sys.exit("bad extra table name %s" % t)
        if t not in STAGED:
            STAGED.append(t)'''),
 ('''    for t in TEN:
        p = os.path.join(out, t + ".tsv")
        bp = os.path.join(a.base, t + ".tsv")''',
  '''    tables = []
    for t in STAGED:
        p = os.path.join(out, t + ".tsv")
        bp = os.path.join(a.base, t + ".tsv")
        if t not in TEN and not S.tabs[t] and not os.path.exists(bp):
            if os.path.exists(p):
                os.remove(p)
            log.append("%s.tsv\\t0 rows\\textra table, empty: not written" % t)
            continue'''),
 ('''                if os.path.samefile(p, bp):
                    log.append("%s.tsv\\t%d rows\\tsha1 %s\\tbase (hard link)" % (t, len(S.tabs[t]), sha1_file(p)))
                    continue
                os.remove(p)
            os.link(bp, p)
            log.append("%s.tsv\\t%d rows\\tsha1 %s\\tbase (hard link)" % (t, len(S.tabs[t]), sha1_file(p)))
            continue''',
  '''                if os.path.samefile(p, bp):
                    h = sha1_file(p)
                    log.append("%s.tsv\\t%d rows\\tsha1 %s\\tbase (hard link)" % (t, len(S.tabs[t]), h))
                    tables.append((t, len(S.tabs[t]), h, "base"))
                    continue
                os.remove(p)
            os.link(bp, p)
            h = sha1_file(p)
            log.append("%s.tsv\\t%d rows\\tsha1 %s\\tbase (hard link)" % (t, len(S.tabs[t]), h))
            tables.append((t, len(S.tabs[t]), h, "base"))
            continue'''),
 ('''        os.replace(tmp, p)
        log.append("%s.tsv\\t%d rows\\tsha1 %s\\twritten" % (t, len(S.tabs[t]), h.hexdigest()))''',
  '''        os.replace(tmp, p)
        log.append("%s.tsv\\t%d rows\\tsha1 %s\\twritten" % (t, len(S.tabs[t]), h.hexdigest()))
        tables.append((t, len(S.tabs[t]), h.hexdigest(), "written"))'''),
 ('''        if not fn.endswith(".tsv") or fn[:-4] in TEN:''', '''        if not fn.endswith(".tsv") or fn[:-4] in STAGED:'''),
 ('''    print("\\n".join(log))''',
  '''    with open(os.path.join(out, "TABLES.txt"), "w", encoding="utf-8", newline="\\n") as f:
        for t, n, h, how in tables:
            f.write("%s\\t%d\\t%s\\t%s\\n" % (t, n, h, how))
    print("\\n".join(log))'''),
]
for a_, b_ in reps:
    assert src.count(a_) == 1, a_[:80]
    src = src.replace(a_, b_)
open(os.path.join(C2, "round8", "stage8.py"), "wb").write(src.encode("utf-8"))
print("written")
