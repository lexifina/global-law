"""Round 13 blind audit, step 1: a stratified sample of the admitted rows of ONE class, as blind packs with decoys.
Port of round7/audit/make_packs7.py (same behaviour) plus the pair form (--pairs, item type C).

    python -X utf8 round13/audit/make_packs13.py --class <name> --cert <delta folder or rows file> [--cert ...]
           --out round13/audit/<run>/ [--n 80] [--exclude <earlier run>/sample.tsv ...] [--ids FILE] [--pairs FILE]
           [--match FIELD=REGEX ...] [--lean-classes round13/out/<v>/classes.tsv] [--seed 7] [--pack-size 40]
           [--decoy-share 0.12] [--decoy-wrong-share 0.6] [--decoy-families REGEX] [--pad-min 500] [--pad-max 1600]
           [--dry-run] [--force] [--mark-selftest]

--cert      a delta folder of certify13 / certify10 / certify9 / certify8 / certify7 / certify_recog / certify_opwords / certify6 (treatments_delta.tsv
            or history_delta.tsv with their side tables: treatment_witness, treatment_class, joined, history_anchor,
            history_claim), a stage folder (e.g. round12/stage/v12a), or one rows file in SCHEMA layout (its folder's
            side tables are used). Several --cert: the first one that has an id wins. One run = one table
            (treatments -> item type A, history -> item type B).
--ids       keep only the row ids listed (first column) -- e.g. the rows a `--replace` file rewrites.
--pairs     pair form (item type C, history rows only): a TSV whose lines are `<row id 1> <TAB> <row id 2>` (a
            header line whose first field is not a row id of the inputs is skipped). Row 1 is the row being judged
            (e.g. the newer row), row 2 the row it is compared with (e.g. the base row it would replace); both must
            have the same acting decision and target and are looked up in every --cert (give the base stage folder
            for base rows). The item shows the acting text around both rows' quotes (and anchors), unlabelled, in
            text order, and asks the type-B questions (what did the acting court itself do to the target); the
            auditor brief is brief B. --match / --ids / --exclude apply to row 1. score_audit13 scores both rows.
--match     keep only rows whose FIELD matches REGEX (re.search); FIELD in id, src, kind, scope, claim (the
            treatment_class claim or the history claim), rel (joined relations, comma-joined), evidence, part,
            witness (1|0), explicit, table (treatments|history). Repeatable (all must match).
--lean-classes  keep only treatments rows whose verdict in that classes.tsv starts with `ok` (admitted by Lean).
--lean-certs    keep only rows (either table; for pairs row 1) whose result_all in that certs.tsv
                (round13/out/<v>/certs.tsv) starts with `ok`.
--exclude   a sample.tsv of ANY earlier round's run (repeatable): its row ids (and decoys) are not drawn again, and
            (round 12, infra12, DESIGN13 section 3) every row with the same identity as a real row of that file
            (row 1 and row 2), WHATEVER the id prefix (t10/h10/t11/h11/t12/h12/...): (table, by node, target node,
            kind), table / by / target / kind taken from the columns table, by_node, target_node, kind (kind2 for
            row 2) or, when a column is missing, parsed from the row id (<p>:<by>:<target>:<kind> for history ids;
            a treatments id <p>:<by>:<target>:<start> carries no kind); a file that gives no kind for a row excludes
            by (by node, target node) alone. Prints, per file, its real rows and how many rows of this class it
            excluded (by id / by identity), and the excluded rows left in the draw (must be 0).

Population = the rows left; one (speaking decision, target) pair is drawn once.
Strata   = acting court federal | state  x  decade of the acting (speaking) decision.
Sample   = --n rows, spread evenly over federal / state, then evenly over the decades, as far as the data allow;
           simple random sampling inside a stratum; a row whose text or quote cannot be found at git HEAD is replaced
           from its stratum.
Decoys   = from decoy_pool_A.jsonl / decoy_pool_B.jsonl (decoys13.py): items whose answer is known from the round-5 /
           round-6 audits, known wrong and known right; per pack at least max(ceil(real/9), share x real) of them
           (>= 10% of the pack), about --decoy-wrong-share of them known wrong. A decoy never shares its speaking
           decision or target with a sampled row.

Writes into the run folder:
  pack_<k>.md        the blind items: who speaks, the decision asked about, passages of the speaking decision's text
                     (each quote's paragraph and one paragraph on each side, bounded; quotes NOT marked); type B also
                     the acting and target decisions and the opening of the text shown. Nothing about the rule, the
                     class, the row's kind or scope, why the item was picked, or decoys.
  BRIEF.md           the brief for this run's item type (from AUDITOR_BRIEF13.md)
  answers/           where auditors write ans_<k>.jsonl (or ans_<k>_<tag>.jsonl for a second reader)
  sample.tsv         THE KEY (header line): never shown to an auditor
  strata.tsv         class, stratum, population, sampled (weights for score_audit13.py)
  store/             index.tsv + the texts, read by more_text13.py only
  manifest.json      arguments, input hashes, counts
"""
import argparse
import json
import math
import os
import re
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit13lib as A  # noqa: E402

KEY_COLS = ["item", "pack", "role", "type", "class", "stratum", "row_id", "table", "shown_node", "by_node",
            "target_node", "y_node", "kind", "scope", "effect", "claim", "joined_rels", "src", "evidence", "y_cites",
            "y_name", "decoy_id", "decoy_family", "decoy_how", "decoy_why", "relocated", "row2_id", "kind2", "scope2",
            "src2", "quote_order"]
# words a run path must not carry (it is printed in the packs and the brief)
TELL_WORDS = ("doctrine", "antecedent", "joined", "recog", "opword", "operative", "orderhead", "order", "setaside",
              "aside", "scope", "decoy", "overrul", "vacat", "revers", "affirm", "cert", "withdr", "rehear", "enbanc",
              "below", "memo", "self", "wrong", "right", "contra", "pair", "base", "new", "old", "multi", "state",
              "ownact", "dock", "shadow", "fjc", "scdb", "same", "remand", "dismiss", "deni", "modif",
              # round 9 (infra9): words of the round-9 tracks and classes
              "zone", "part", "gvr", "jersey", "succes", "judgm", "implic", "pool", "phrase", "lean", "line",
              # round 10 (infra10): words of the round-10 tracks and classes ("state", "remand" are listed above)
              "syllab", "recut", "bridge", "named", "bare", "footnote", "review",
              # round 11 (infra11): words of the round-13 tracks and classes ("order", "dock", "rehear" are above)
              "uncited", "docket", "fedcir", "federal", "circuit", "claims", "list", "rehearing", "banc", "tie",
              "caption",
              # round 12 (infra12): words of the round-13 tracks and classes ("banc", "rehearing" are above)
              "panel", "superseded", "judge", "county", "district", "journal", "ligature")
OPENING_CHARS = 1200


def waterfill(quota, caps, rnd):
    alloc = [0] * len(caps)
    left = min(quota, sum(caps))
    while left > 0:
        opened = [i for i, c in enumerate(caps) if alloc[i] < c]
        share = left // len(opened)
        if share == 0:
            for i in rnd.sample(opened, left):
                alloc[i] += 1
            left = 0
        else:
            for i in opened:
                g = min(share, caps[i] - alloc[i])
                alloc[i] += g
                left -= g
    return alloc


def allocate(cells, quota, rnd):
    systems = sorted({s for s, _ in cells})
    a_sys = waterfill(quota, [sum(c for (s, _), c in cells.items() if s == sy) for sy in systems], rnd)
    out = {}
    for sy, q in zip(systems, a_sys):
        decs = sorted(d for s, d in cells if s == sy)
        for d, n in zip(decs, waterfill(q, [cells[(sy, d)] for d in decs], rnd)):
            out[(sy, d)] = n
    return out


def field(r, name):
    if name == "claim":
        return (r["claim"][0] if r.get("claim") else r.get("hclaim")) or "-"
    if name == "rel":
        return ",".join(j[0] for j in r.get("joined") or [])
    if name == "witness":
        return "1" if r.get("witness") else "0"
    return str(r.get(name, ""))


def speaker_of(r):
    if r["table"] == "treatments":
        return r["witness"][0] if r.get("witness") else r["by"]
    return r["by"] if r["by"] >= 0 else r["target"]


def spans_of(r):
    """[(s, e, quote)] of a row: the main quote first, then joined / anchor quotes; for a pair (type C) the second
    row's quote and anchor follow."""
    out = [(r["start"], r["end"], r["quote"])]
    for j in r.get("joined") or []:
        out.append((j[1], j[2], j[3]))
    if r.get("anchor"):
        out.append((r["anchor"][0], r["anchor"][1], r["anchor"][2]))
    r2 = r.get("row2")
    if r2:
        out.append((r2["start"], r2["end"], r2["quote"]))
        if r2.get("anchor"):
            out.append((r2["anchor"][0], r2["anchor"][1], r2["anchor"][2]))
    return out


def brief_for(typ, run):
    p = os.path.join(A.HERE, "AUDITOR_BRIEF13.md")
    txt = open(p, encoding="utf-8").read()
    m = re.search(r"<!-- BRIEF %s -->(.*?)<!-- END BRIEF %s -->" % (typ, typ), txt, re.S)
    if not m:
        sys.exit("AUDITOR_BRIEF13.md has no brief %s" % typ)
    return m.group(1).strip().replace("<run>", run) + A.NL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--cert", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=80)
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--ids")
    ap.add_argument("--pairs")
    ap.add_argument("--match", action="append", default=[])
    ap.add_argument("--lean-classes")
    ap.add_argument("--lean-certs")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--nodes", help="round 11: order-node folder (e.g. round13/data_orders; or env R13_NODES) so rows "
                                    "by / on order nodes show the node's own text and caption")
    ap.add_argument("--pack-size", type=int, default=40)
    ap.add_argument("--decoy-share", type=float, default=0.12)
    ap.add_argument("--decoy-wrong-share", type=float, default=0.6)
    ap.add_argument("--decoy-families", default="")
    ap.add_argument("--pad-min", type=int, default=500)
    ap.add_argument("--pad-max", type=int, default=1600)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--mark-selftest", action="store_true")
    a = ap.parse_args()
    if a.nodes:  # round 11 (infra11): DESIGN13 section 4 order nodes
        A.nodes13().activate(A.resolve(a.nodes))
    A.utf8_stdout()
    if not re.fullmatch(r"[A-Za-z0-9_.:/+\-]+", a.cls):
        sys.exit("--class: letters, digits and _ . : / + - only")
    rnd = A.seeded(a.seed, "sample", a.cls)
    warn = []

    # ---- population
    want = None
    if a.ids:
        want = {p[0] for p in A.read_tsv(A.resolve(a.ids))}
    pairs_in = None
    if a.pairs:
        pairs_in = [(p[0].strip(), p[1].strip()) for p in A.read_tsv(A.resolve(a.pairs), 2)]
        if want is not None:
            pairs_in = [pq for pq in pairs_in if pq[0] in want]
        want = {x for pq in pairs_in for x in pq}
    rows, seen, inputs = [], set(), []
    for c in a.cert:
        rs, info = A.load_cert(A.resolve(c), want)
        kept = 0
        for r in rs:
            if r["id"] not in seen:
                seen.add(r["id"])
                rows.append(r)
                kept += 1
        info.update({"cert": A.resolve(c).replace("\\", "/"), "rows": len(rs), "kept": kept})
        inputs.append(info)
    if pairs_in is not None:
        byid = {r["id"]: r for r in rows}
        rows, nmiss, nbad, used1 = [], 0, 0, set()
        for i1, i2 in pairs_in:
            r1, r2 = byid.get(i1), byid.get(i2)
            if r1 is None or r2 is None:
                nmiss += 1
                continue
            if r1["table"] != "history" or r2["table"] != "history" or (r1["by"], r1["target"]) != \
                    (r2["by"], r2["target"]) or i1 == i2 or i1 in used1:
                nbad += 1
                continue
            used1.add(i1)
            r = dict(r1)
            r["row2"] = r2
            rows.append(r)
        if nmiss:
            warn.append("pairs: %d lines whose rows are not both in the inputs (a header line counts here)" % nmiss)
        if nbad:
            warn.append("pairs: %d lines skipped (not two history rows of one acting / target pair, or row 1 "
                        "repeated)" % nbad)
    n_in = len(rows)
    for m in a.match:
        if "=" not in m:
            sys.exit("--match FIELD=REGEX")
        f, rx = m.split("=", 1)
        if f not in ("id", "src", "kind", "scope", "claim", "rel", "evidence", "part", "witness", "explicit", "table"):
            sys.exit("--match: unknown field " + f)
        cr = re.compile(rx)
        rows = [r for r in rows if cr.search(field(r, f))]
    tables = {r["table"] for r in rows}
    if len(tables) > 1:
        sys.exit("one run audits one table; the rows hold %s (add --match table=treatments or table=history)"
                 % sorted(tables))
    if not rows:
        sys.exit("no rows left (inputs: %d)" % n_in)
    table = tables.pop()
    typ = "A" if table == "treatments" else "B"
    if pairs_in is not None:
        typ = "C"
    dtyp = "A" if typ == "A" else "B"   # decoy pool / item layout / brief: a pair item is a type-B item
    if a.lean_classes:
        ok = {p[0] for p in A.read_tsv(A.resolve(a.lean_classes))[1:] if len(p) >= 4 and p[3].startswith("ok")}
        rows = [r for r in rows if r["id"] in ok]
    if a.lean_certs:
        cr = A.read_tsv(A.resolve(a.lean_certs))
        ic, vc = (cr[0].index("id"), cr[0].index("result_all")) if cr and "id" in cr[0] else (1, 2)
        ok = {p[ic] for p in cr[1:] if len(p) > vc and p[vc].startswith("ok")}
        rows = [r for r in rows if r["id"] in ok]
    excluded = set()
    excluded_keys = set()  # round 11 (infra11): (table, by, target, kind) of the excluded samples' rows
    excluded_pairs = set()  # round 12 (infra12): (by, target) of excluded rows whose file gives no kind
    xfiles = []  # round 12: per file (name, ids, keys, pairs, real rows) for the per-file counts

    def _xrow(d, rid_col, row2=False):
        """(table, by, target, kind|None) of one real sample row (row 2 when row2): columns first, else the row id."""
        rid = d.get("row2_id" if row2 else rid_col, "") or ""
        pp = rid.split(":")
        tab = d.get("table") or ""
        if not tab and len(pp) >= 4:
            tab = "history" if pp[0].startswith("h") else "treatments" if pp[0].startswith("t") else ""
        by = str(d.get("by_node") or (pp[1] if len(pp) >= 4 else ""))
        tg = str(d.get("target_node") or (pp[2] if len(pp) >= 4 else ""))
        kind = d.get("kind2" if row2 else "kind") or None
        if kind is None and tab == "history" and len(pp) >= 4:
            kind = pp[3]
        return tab, by, tg, kind

    for e in a.exclude:
        kr = A.read_tsv(A.resolve(e))
        f_ids, f_keys, f_pairs, f_real = set(), set(), set(), 0
        if kr:
            h = kr[0]
            col = h.index("row_id") if "row_id" in h else 0
            f_ids |= {p[col] for p in kr[1:] if len(p) > col and p[col]}
            for p in kr[1:]:
                d = dict(zip(h, p + [""] * (len(h) - len(p))))
                if "role" in h and d["role"] != "real":
                    continue
                f_real += 1
                for r2 in ((False, True) if d.get("row2_id") else (False,)):
                    tab, by, tg, kind = _xrow(d, h[col], r2)
                    if not by or not tg or not by.lstrip("-").isdigit() or not tg.lstrip("-").isdigit():
                        continue
                    if kind:
                        f_keys.add((tab, by, tg, kind))
                    else:
                        f_pairs.add((by, tg))
            for cname in ("decoy_id", "row2_id"):
                if cname in h:
                    dc = h.index(cname)
                    f_ids |= {p[dc] for p in kr[1:] if len(p) > dc and p[dc]}
        excluded |= f_ids
        excluded_keys |= f_keys
        excluded_pairs |= f_pairs
        xfiles.append((e, f_ids, f_keys, f_pairs, f_real))
    L = A.r6lib()
    F = L.Facts()
    nn = len(F.court)
    pop = []
    for r in rows:
        sp = speaker_of(r)
        if not (0 <= r["target"] < nn and 0 <= sp < nn) or (r["by"] >= nn):
            continue
        r["speaker"] = sp
        ref = sp if typ == "A" else (r["by"] if r["by"] >= 0 else r["target"])
        d = int(F.date[ref]) or r["date"]
        sy = "fed" if F.system(int(F.court[ref])) == 0 else "state"
        r["stratum"] = "%s|%s" % (sy, ("%ds" % (d // 100000 * 10)) if d > 0 else "undated")
        pop.append(r)
    popn = {}
    for r in pop:
        popn[r["stratum"]] = popn.get(r["stratum"], 0) + 1
    def rkey(r):
        return (r["table"], str(r["by"]), str(r["target"]), r["kind"])

    def xhit(r, ids, keys, prs):
        """0 = not excluded, 1 = by id, 2 = by identity (table, by, target, kind), 3 = by (by, target) only."""
        for x in [r] + ([r["row2"]] if r.get("row2") else []):
            if x["id"] in ids:
                return 1
        for x in [r] + ([r["row2"]] if r.get("row2") else []):
            if rkey(x) in keys:
                return 2
            if (str(x["by"]), str(x["target"])) in prs:
                return 3
        return 0
    n_xkey = sum(1 for r in pop if xhit(r, excluded, excluded_keys, excluded_pairs) in (2, 3))
    print("class %s: %d rows in the inputs (%s), %d after filters, %d with valid nodes; %d strata; excluded ids %d; "
          "rows excluded by identity (table, by, target, kind) only %d"
          % (a.cls, n_in, table, len(rows), len(pop), len(popn), len(excluded), n_xkey))
    for e, f_ids, f_keys, f_pairs, f_real in xfiles:  # round 12: per-file counts
        hh = [xhit(r, f_ids, f_keys, f_pairs) for r in pop]
        print("  --exclude %s: %d real rows (%d identities with kind, %d (by, target) pairs without); excluded %d rows "
              "of this class (by id %d, by identity %d, by (by, target) %d)"
              % (e, f_real, len(f_keys), len(f_pairs), sum(1 for x in hh if x), hh.count(1), hh.count(2), hh.count(3)))

    # ---- allocation and draw
    avail, pairs = {}, set()
    for r in sorted(pop, key=lambda r: r["id"]):
        pair = (r["speaker"], r["target"])
        if r["id"] in excluded or (r.get("row2") and r["row2"]["id"] in excluded) or pair in pairs:
            continue
        if xhit(r, excluded, excluded_keys, excluded_pairs):
            continue
        pairs.add(pair)
        sy, dec = r["stratum"].split("|")
        avail.setdefault((sy, dec), []).append(r)
    al = allocate({k: len(v) for k, v in avail.items()}, a.n, rnd)
    sample, reserve = [], {}
    for k in sorted(al):
        lst = list(avail[k])
        rnd.shuffle(lst)
        sample += lst[:al[k]]
        reserve["%s|%s" % k] = lst[al[k]:]
    left = sum(1 for v in avail.values() for r in v if xhit(r, excluded, excluded_keys, excluded_pairs))
    print("excluded rows left in the draw: %d" % left)  # round 12: must be 0
    if a.dry_run:
        for s in sorted(popn):
            print("  %-16s population %6d  sampled %3d" % (s, popn[s], al.get(tuple(s.split("|")), 0)))
        print("dry run: %d rows would be sampled" % len(sample))
        return
    out = A.resolve(a.out, must_exist=False)
    A.must_be_under_audit(os.path.join(out, "x"))
    if os.path.exists(os.path.join(out, "sample.tsv")) and not a.force:
        sys.exit("%s already holds a sample; pick another --out or pass --force" % out)
    # the run path (relative to round13/audit) is printed in the packs and the brief: it must not tell the reader
    # the class, the rule, the agent or the form
    run = os.path.relpath(os.path.normpath(out), A.HERE).replace("\\", "/")
    low = run.lower()
    tell = [w for w in re.split(r"[^a-z0-9]+", a.cls.lower()) if len(w) >= 4 and w in low]
    tell += [w for w in TELL_WORDS if w in low]
    if tell and not a.mark_selftest:
        sys.exit("run path %r tells the readers something (%s): use a neutral name such as r13a01"
                 % (run, ", ".join(sorted(set(tell)))))

    # ---- texts
    texts = {}

    def need(nodes):
        miss = [n for n in set(nodes) if 0 <= n < nn and n not in texts]
        if miss:
            for n, st in L.fetch_texts(miss).items():
                texts[n] = st
            for n in miss:
                texts.setdefault(n, None)

    def prepare(spec):
        """Fix the shown node and the spans at HEAD; False when the text or a quote is missing."""
        cands = [spec["speaker"]] if typ == "A" else [x for x in (spec["by"], spec["target"]) if x >= 0]
        need(cands + [spec["target"]])
        if texts.get(spec["target"]) is None:
            return False
        order = sorted(cands, key=lambda n: 0 if texts.get(n) and texts[n][0] == spec["text_sha"] else 1)
        for n in order:
            if texts.get(n) is None:
                continue
            sha, t = texts[n]
            got, moved = [], False
            for s, e, q in spec["spans"]:
                if sha != spec["text_sha"] and not q:
                    got = None
                    break
                sp, mv = A.locate(t, s, e, q)
                if sp is None:
                    got = None
                    break
                got.append(sp)
                moved |= mv
            if got:
                spec["shown"], spec["at"], spec["relocated"] = n, got, int(moved or sha != spec["text_sha"])
                return True
        return False

    def spec_of_row(r):
        return {"role": "real", "row": r, "speaker": r["speaker"], "by": r["by"], "target": r["target"],
                "text_sha": r["text_sha"], "spans": spans_of(r)}

    specs = []
    for r in sample:
        sp = spec_of_row(r)
        while not prepare(sp):
            lst = reserve.get(r["stratum"], [])
            if not lst:
                sp = None
                warn.append("stratum %s: a row without text / quote and no replacement" % r["stratum"])
                break
            r = lst.pop(0)
            sp = spec_of_row(r)
        if sp:
            specs.append(sp)
    real_n = len(specs)

    # ---- decoys
    pool_path = os.path.join(A.HERE, "decoy_pool_%s.jsonl" % dtyp)
    pool = A.read_jsonl(pool_path)
    if not pool:
        sys.exit("no decoy pool %s: run decoys13.py first" % pool_path)
    fam_rx = re.compile(a.decoy_families) if a.decoy_families else None
    used_nodes = {s["speaker"] for s in specs} | {s["target"] for s in specs} | {s["by"] for s in specs}
    pop_ids = {r["id"] for r in pop} | {r["row2"]["id"] for r in pop if r.get("row2")}
    pop_pairs = {(r["speaker"], r["target"]) for r in pop}
    cand = {"wrong": [], "right": []}
    seen_pair = set()
    for d in sorted(pool, key=lambda d: d["did"]):
        sp = d["speaker"] if typ == "A" else (d["by"] if d["by"] >= 0 else d["target"])
        pair = (sp, d["target"])
        if (fam_rx and not fam_rx.search(d["family"])) or d["did"] in excluded or d["row_id"] in pop_ids \
                or pair in pop_pairs or pair in seen_pair or sp in used_nodes or d["target"] in used_nodes:
            continue
        seen_pair.add(pair)
        cand[d["truth"]].append(d)
    for t in cand:  # round-robin over families after a seeded shuffle
        rnd.shuffle(cand[t])
        byf = {}
        for d in cand[t]:
            byf.setdefault(d["family"], []).append(d)
        fams = sorted(byf)
        rnd.shuffle(fams)
        rr = []
        while any(byf.values()):
            for f in fams:
                if byf[f]:
                    rr.append(byf[f].pop(0))
        cand[t] = rr
    real_per_pack = max(1, int(round(a.pack_size * (1 - a.decoy_share))))
    npack = max(1, int(round(real_n / float(real_per_pack))))
    rsh = A.seeded(a.seed, "packs", a.cls)
    rsh.shuffle(specs)
    packs = [specs[k::npack] for k in range(npack)]
    made = {"wrong": 0, "right": 0}
    short = []
    dec_nodes = set()
    for k, pk in enumerate(packs):
        r_k = len(pk)
        d_k = max(int(math.ceil(r_k / 9.0)), int(round(a.decoy_share * r_k)), 2 if r_k >= 4 else 1)
        w_k = max(1, int(round(d_k * a.decoy_wrong_share)))
        want_k = {"wrong": w_k, "right": max(0, d_k - w_k)}
        for t in ("wrong", "right"):
            got = 0
            while got < want_k[t] and cand[t]:
                d = cand[t].pop(0)
                sp = d["speaker"] if typ == "A" else (d["by"] if d["by"] >= 0 else d["target"])
                if sp in dec_nodes or d["target"] in dec_nodes:
                    continue
                spec = {"role": "decoy_" + t, "decoy": d, "speaker": sp, "by": d["by"], "target": d["target"],
                        "text_sha": d["text_sha"],
                        "spans": [(s, e, q) for (s, e), q in zip(d["spans"], d.get("quotes") or [""] * 9)]}
                if not prepare(spec):
                    continue
                dec_nodes |= {sp, d["target"]}
                pk.append(spec)
                got += 1
                made[t] += 1
            if got < want_k[t]:
                short.append("pack %d: %d of %d known-%s decoys" % (k + 1, got, want_k[t], t))
        nd = sum(1 for s in pk if s["role"] != "real")
        if nd * 10 < len(pk):
            short.append("pack %d: decoys %d of %d items (< 10%%)" % (k + 1, nd, len(pk)))
    warn += short

    # ---- facts of every node shown or keyed
    ys = set()
    for s in specs:
        r = s["row"]
        if typ == "A" and r.get("witness"):
            ys.add(r["by"])
    for pk in packs:
        for s in pk:
            if s["role"] != "real" and s["decoy"].get("y", -1) >= 0:
                ys.add(s["decoy"]["y"])
    fx = {}
    for pk in packs:
        for s in pk:
            for n in {s["shown"], s["target"]} | ({s["by"]} if s["by"] >= 0 else set()):
                if n not in fx:
                    fx[n] = A.node_facts(n, F, L, texts[n][1] if texts.get(n) else None)
    for y in ys:
        if y not in fx:
            fx[y] = A.node_facts(y, F, L, None)

    # ---- item ids, pack text, store
    taken = A.taken_item_ids()
    rid = A.seeded(a.seed, "ids", a.cls, run, time.time())
    all_items = [s for pk in packs for s in pk]
    for s, i in zip(all_items, A.new_ids(len(all_items), rid, taken)):
        s["item"] = i
    rpad = A.seeded(a.seed, "pad", a.cls, run)
    index, store = [], {}
    brief_name = "BRIEF.md"
    for k, pk in enumerate(packs, 1):
        rsh.shuffle(pk)
        out_md = ["# Audit pack %d of run %s (%d items)" % (k, run, len(pk)), "",
                  "Read `round13/audit/%s/%s` first. Answer every item, in this order, one JSON line each, into "
                  "`round13/audit/%s/answers/ans_%d.jsonl`." % (run, brief_name, run, k), ""]
        for s in pk:
            s["pack"] = k
            sha, t = texts[s["shown"]]
            b0 = A.body_start(t)
            wins = A.passage_bounds(t, [sp for sp in s["at"]], rpad, b0, a.pad_min, a.pad_max)
            out_md.append("## ITEM %s" % s["item"])
            out_md.append("")
            if typ == "A":
                out_md.append("SPEAKING DECISION (whose text is shown): " + A.label(fx[s["shown"]]))
                out_md.append("DECISION X (the decision asked about): " + A.label(fx[s["target"]]))
            else:
                act = s["by"] if s["by"] >= 0 else s["target"]
                if act == s["target"]:
                    out_md.append("ACTING DECISION: the target decision itself (see below)")
                else:
                    out_md.append("ACTING DECISION: " + A.label(fx[act], docket=True))
                out_md.append("TARGET DECISION: " + A.label(fx[s["target"]], docket=True))
                out_md.append("TEXT SHOWN IS FROM: %s" % (
                    "the acting decision" if s["shown"] == act and act != s["target"] else
                    "the target decision"))
                op = t[b0:b0 + OPENING_CHARS]
                if wins and wins[0][0] <= b0 + OPENING_CHARS:
                    op = t[b0:wins[0][0]] if wins[0][0] > b0 else ""
                if op.strip():
                    op = op if len(op) < OPENING_CHARS else op[:A._word_right(op, OPENING_CHARS - 40)] + " [...]"
                    out_md += ["", "[OPENING OF THE TEXT SHOWN]", op.rstrip(), "[END OF OPENING]"]
            for j, (pa, pb) in enumerate(wins, 1):
                parts = A.part_labels(t, pa, pb)
                out_md.append("")
                out_md.append("[PASSAGE %d of %d%s]" % (j, len(wins), (" -- opinion part (machine label, can be wrong; "
                                                                      "headings in the text govern): " +
                                                                      " -> ".join(parts)) if parts else ""))
                lead = "[...] " if pa > b0 and t[pa - 1] != A.NL else ""
                tail = " [...]" if pb < len(t) and t[pb] != A.NL else ""
                out_md.append(lead + t[pa:pb].strip(A.NL) + tail)
                out_md.append("[END OF PASSAGE %d]" % j)
            out_md.append("")
            store[sha] = t
            tsha, tt = texts[s["target"]]
            store[tsha] = tt
            index.append([s["item"], sha, b0, ";".join("%d-%d" % w for w in wins), tsha, A.body_start(tt)])
        A.write_text(os.path.join(out, "pack_%d.md" % k), A.NL.join(out_md) + A.NL)
    for sha, t in store.items():
        A.write_text(os.path.join(out, "store", "text", sha + ".txt"), t)
    A.write_tsv(os.path.join(out, "store", "index.tsv"), sorted(index))
    os.makedirs(os.path.join(out, "answers"), exist_ok=True)
    A.write_text(os.path.join(out, brief_name), brief_for(dtyp, run))

    # ---- key
    whole_phr = A.operative_whole_phrases()

    def pair_cols(s):
        r2 = s["row"].get("row2")
        if not r2:
            return ["", "", "", "", ""]
        i2 = 1 + len(s["row"].get("joined") or []) + (1 if s["row"].get("anchor") else 0)
        q1, q2 = s["at"][0], s["at"][i2]
        order = "1<2" if q1[0] < q2[0] else "2<1" if q2[0] < q1[0] else "same"
        return [r2["id"], r2["kind"], r2["scope"], r2["src"], order]
    key = [KEY_COLS]
    for s in sorted(all_items, key=lambda s: (s["pack"], s["item"])):
        if s["role"] == "real":
            r = s["row"]
            y = r["by"] if (typ == "A" and r.get("witness")) else -1
            if typ == "A":
                eff, _dem = A.a_effect(r["kind"], r["scope"], r.get("claim"), r.get("witness"), r["quote"], whole_phr)
            else:
                eff = "status" if r["kind"] in A.H_STATUS else "other"
            claim = (r["claim"][0] if r.get("claim") else r.get("hclaim")) or "-"
            key.append([s["item"], s["pack"], "real", typ, a.cls, r["stratum"], r["id"], table, s["shown"], r["by"],
                        r["target"], y, r["kind"], r["scope"], eff, claim,
                        ",".join(j[0] for j in r.get("joined") or []) or "-", r["src"], r["evidence"],
                        " | ".join(fx[y]["all_citations"]) if y >= 0 else "", fx[y]["name"] if y >= 0 else "",
                        "", "", "", "", s["relocated"]] + pair_cols(s))
        else:
            d = s["decoy"]
            y = d.get("y", -1)
            eff = d["effect"] if typ == "A" else ("status" if d["kind"] in A.H_STATUS else "other")
            key.append([s["item"], s["pack"], s["role"], dtyp, "decoy", "decoy", "decoy:" + d["did"], table,
                        s["shown"], d["by"], d["target"], y, d["kind"], d["scope"], eff, "-", "-", "-", "-",
                        " | ".join(fx[y]["all_citations"]) if y >= 0 else "", fx[y]["name"] if y >= 0 else "",
                        d["did"], d["family"], d["how"], d["why"], s["relocated"], "", "", "", "", ""])
    A.write_tsv(os.path.join(out, "sample.tsv"), key)
    samp = {}
    for s in specs:
        samp[s["row"]["stratum"]] = samp.get(s["row"]["stratum"], 0) + 1
    st = [["class", "stratum", "population", "sampled"]]
    for s_ in sorted(popn):
        st.append([a.cls, s_, popn[s_], samp.get(s_, 0)])
    A.write_tsv(os.path.join(out, "strata.tsv"), st)
    man = {"run": run, "class": a.cls, "type": typ, "brief": dtyp, "table": table, "self_test": bool(a.mark_selftest),
           "created": time.strftime("%Y-%m-%d %H:%M:%S"), "args": vars(a), "inputs": inputs,
           "population": len(pop), "real": real_n, "decoys_wrong": made["wrong"], "decoys_right": made["right"],
           "packs": {"pack_%d.md" % k: {"items": len(pk), "real": sum(1 for s in pk if s["role"] == "real"),
                                        "decoys": sum(1 for s in pk if s["role"] != "real")}
                     for k, pk in enumerate(packs, 1)},
           "relocated_quotes": sum(s["relocated"] for s in all_items),
           "decoy_pool": {"path": pool_path.replace("\\", "/"), "sha1": A.sha1_file(pool_path)},
           "warnings": warn}
    A.write_text(os.path.join(out, "manifest.json"), json.dumps(man, indent=1, ensure_ascii=False) + A.NL)
    if a.mark_selftest:
        A.write_text(os.path.join(out, "SELF_TEST.txt"),
                     "Self-test run of the round-13 audit tools on a synthetic input; verdicts written by the tool"
                     + A.NL + "author's self-test, not by blind auditors. Its numbers say nothing about any rule." + A.NL)
    print("wrote %s: %d items (%d real, %d known-wrong decoys, %d known-right decoys) in %d packs %s" % (
        out, len(all_items), real_n, made["wrong"], made["right"], npack, [len(pk) for pk in packs]))
    for w in warn:
        print("warning: " + w)


if __name__ == "__main__":
    main()
