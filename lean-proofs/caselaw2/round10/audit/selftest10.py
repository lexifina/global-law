"""Self-test of the round-10 audit tools on a tiny SYNTHETIC run (one run per item type, A, B and the pair form C).
Port of round7/audit/selftest7.py with round-10 row ids and a pair run.

    python -X utf8 round10/audit/selftest10.py [--keep]

1. Synthetic inputs in round10/audit/selftest10/ (tool test only; the rows are earlier rounds' rows, not round-10
   output):
   cert_A/  treatments rows: round-5 operative rows (treatment_class operativeWords) and recognised rows (witness
            lines), ids rewritten to `t10:st:...`; one row gets a doctrine claim and a doctrineTie joined line, two rows
            an antecedent joined line (the sentence before the quote), so every effect class and span kind is shown.
   cert_B/  history rows: round-6 rows (snap/a3) with their anchors, ids rewritten to `h10:st:...`; two rows get a
            history claim.
   cert_B2/ for the pair run (type C): a second row for some cert_B rows (same acting decision and target, the
            sentence before the main quote as its quote, a kind of the other status effect), ids `h10:st2:...`;
            pairs.tsv (row 1, row 2) with a header line.
2. make_packs10.py on each (--n 12, small packs, --mark-selftest).
3. Planted answers written from the key (allowed here only): every 4th sampled row answered wrong (A: act
   `nothing`; B: not linked), one more A row answered right but with a wrong extent where whole is needed (or with a
   wrong other decision for a report row), the rest right; decoys answered by their truth except one known-wrong
   decoy confirmed; a second reader for pack 1 that differs on one sampled row.
4. score_audit10.py, then every number it reports is checked against the planted answers; the packs are checked for
   leaks (row ids, rule ids, class name, kinds, scopes, the word decoy); more_text10.py is run in both modes.
Writes selftest10/SELF_TEST_RESULT.txt. Exit status 0 = all checks passed.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit10lib as A  # noqa: E402

ST = os.path.join(A.HERE, "selftest10")
PY = [sys.executable, "-X", "utf8"]
NOWIN = 0x08000000 if os.name == "nt" else 0


def run(args):
    p = subprocess.run(PY + args, capture_output=True, text=True, encoding="utf-8", cwd=A.C2, creationflags=NOWIN)
    if p.returncode != 0:
        print(p.stdout)
        print(p.stderr)
        sys.exit("FAILED: %s" % " ".join(args))
    return p.stdout


def sentence_before(text, s):
    """(a, b) of the sentence that ends just before offset s (same paragraph), or None."""
    a = max(text.rfind(". ", 0, max(0, s - 2)), text.rfind("\n", 0, s))
    if a < 0 or s - a > 400 or s - a < 20:
        return None
    a += 1
    while a < s and text[a] == " ":
        a += 1
    b = s
    while b > a and text[b - 1] == " ":
        b -= 1
    return (a, b) if b - a >= 15 else None


def build_inputs():
    L = A.r6lib()
    da, db = os.path.join(ST, "cert_A"), os.path.join(ST, "cert_B")
    # ---- A: operative rows + recognised rows
    op = A.read_tsv(os.path.join(A.C2, "round5", "opwords", "cert", "treatments_delta.tsv"))[:60]
    rc = A.read_tsv(os.path.join(A.C2, "round5", "recog", "cert", "treatments_delta.tsv"))[:40]
    wit = {p[0]: p for p in A.read_tsv(os.path.join(A.C2, "round5", "recog", "cert", "treatment_witness_delta.tsv"))}
    tr, cl, wi, jo = [], [], [], []
    for p in op:
        nid = "t10:st:" + p[0]
        tr.append([nid] + p[1:])
        cl.append([nid, "operativeWords", "-", "-", "selftest:opwords"])
    for p in rc:
        if p[0] not in wit:
            continue
        nid = "t10:st:" + p[0]
        tr.append([nid] + p[1:])
        cl.append([nid, "recognised", "-", "-", "selftest:recog"])
        wi.append([nid] + wit[p[0]][1:])
    # joined lines: the sentence before the main quote, for 3 operative rows (one becomes a doctrine row)
    texts = L.fetch_texts([int(p[1]) for p in op[:12]])
    nj = 0
    for p in op[:12]:
        n = int(p[1])
        if n not in texts or nj >= 3:
            continue
        sha, t = texts[n]
        if sha != p[8]:
            continue
        sb = sentence_before(t, int(p[9]))
        if not sb:
            continue
        nid = "t10:st:" + p[0]
        if nj == 0:
            jo.append([nid, "treatments", "doctrineTie", sb[0], sb[1], A.clean(t[sb[0]:sb[1]]), "majority",
                       "selftest doctrine", "selftest"])
            for c in cl:
                if c[0] == nid:
                    c[1:4] = ["doctrine", "-", "selftest doctrine"]
            for r in tr:
                if r[0] == nid:
                    r[4] = "disapproved"
        else:
            jo.append([nid, "treatments", "antecedent", sb[0], sb[1], A.clean(t[sb[0]:sb[1]]), "majority", "-",
                       "selftest"])
            for c in cl:
                if c[0] == nid:
                    c[1] = "-"
        nj += 1
    A.write_tsv(os.path.join(da, "treatments_delta.tsv"), tr)
    A.write_tsv(os.path.join(da, "treatment_class_delta.tsv"), cl)
    A.write_tsv(os.path.join(da, "treatment_witness_delta.tsv"), wi)
    A.write_tsv(os.path.join(da, "joined_delta.tsv"), jo)
    # ---- B: round-6 rows with anchors
    snap = os.path.join(A.R6H, "snap", "a3")
    hr = A.read_tsv(os.path.join(snap, "history_delta.tsv"))[:80]
    an = {p[0]: p for p in A.read_tsv(os.path.join(snap, "history_anchor_delta.tsv"))}
    hh, ha, hc = [], [], []
    for p in hr:
        nid = "h10:st:" + p[0]
        hh.append([nid] + p[1:])
        if p[0] in an:
            ha.append([nid] + an[p[0]][1:])
    for p in hh[:2]:
        hc.append([p[0], "setAside", "selftest"])
    A.write_tsv(os.path.join(db, "history_delta.tsv"), hh)
    A.write_tsv(os.path.join(db, "history_anchor_delta.tsv"), ha)
    A.write_tsv(os.path.join(db, "history_claim_delta.tsv"), hc)
    return da, db, {"A_rows": len(tr), "A_joined": len(jo), "B_rows": len(hh), "B_anchor": len(ha)}


def build_pairs(db):
    """cert_B2 (second rows) and pairs.tsv for the pair run."""
    L = A.r6lib()
    hh = [A.hist_row(p) for p in A.read_tsv(os.path.join(db, "history_delta.tsv"))]
    hh = [r for r in hh if r and r["by"] >= 0]
    texts = L.fetch_texts({r["by"] for r in hh} | {r["target"] for r in hh})
    out, pairs = [], [["row_1", "row_2"]]
    for r in hh:
        hit = None
        for n in (r["by"], r["target"]):
            if n in texts and texts[n][0] == r["text_sha"]:
                hit = texts[n][1]
        if hit is None:
            continue
        sb = sentence_before(hit, r["start"])
        if not sb:
            continue
        k2 = "affirmed" if r["kind"] in A.H_STATUS else "reversed"
        nid = "h10:st2:" + r["id"].split(":", 2)[2]
        out.append([nid, r["target"], r["by"], r["date"], k2, "all", r["text_sha"], sb[0], sb[1],
                    A.clean(hit[sb[0]:sb[1]]), "selftest", "majority", "selftest-pair"])
        pairs.append([r["id"], nid])
    d2 = os.path.join(ST, "cert_B2")
    A.write_tsv(os.path.join(d2, "history_delta.tsv"), out)
    A.write_tsv(os.path.join(ST, "pairs.tsv"), pairs)
    return d2, os.path.join(ST, "pairs.tsv"), len(out)


# ---- planted answers ------------------------------------------------------------------------------------------------
def a_right_answer(k):
    eff = k["effect"]
    act = {"own_whole": "overrule", "own_part": "overrule", "doctrine": "reject_doctrine",
           "report_whole": "report_other", "report_part": "report_other", "limit": "limit"}[eff]
    y = k["y_cites"].split(" | ")[0] if k["y_cites"] else k["y_name"]
    return {"item": k["item"], "speaks_of_x": "yes", "act": act,
            "extent": "whole" if eff in A.A_NEEDS_WHOLE else "part", "own_opinion": "yes",
            "other_decision": y if eff.startswith("report") else "", "doctrine": "", "words": "planted",
            "confidence": "high", "note": "selftest"}


def a_wrong_answer(k):
    return {"item": k["item"], "speaks_of_x": "yes", "act": "nothing", "extent": "unclear", "own_opinion": "no",
            "other_decision": "", "doctrine": "", "words": "planted wrong", "confidence": "high", "note": "selftest"}


def b_right_answer(k):
    disp = sorted(A.B_COMPAT.get(k["kind"], {"other"}))[0]
    return {"item": k["item"], "same_case": "yes", "acted_on": "yes", "disposition": disp, "whole": "yes",
            "evidence": "planted", "confidence": "high", "note": "selftest"}


def b_wrong_answer(k):
    return {"item": k["item"], "same_case": "no", "acted_on": "no", "disposition": "none", "whole": "no",
            "evidence": "", "confidence": "high", "note": "selftest"}


def plant(rdir, typ):
    kr = A.read_tsv(os.path.join(rdir, "sample.tsv"))
    head = kr[0]
    keys = [dict(zip(head, r + [""] * (len(head) - len(r)))) for r in kr[1:]]
    right_f, wrong_f = (a_right_answer, a_wrong_answer) if typ == "A" else (b_right_answer, b_wrong_answer)
    exp = {"real_right": 0, "real_rext": 0, "real_n": 0, "dec_n": 0, "dec_acc": 0, "rows_wrong": [],
           "per_pack": {}}
    by_pack = {}
    reals = [k for k in keys if k["role"] == "real"]
    special = None
    for idx, k in enumerate(reals):
        if idx % 4 == 3:
            k["_plan"] = "wrong"
        elif special is None and typ == "A" and k["effect"] in ("own_whole", "report_whole", "report_part"):
            k["_plan"] = "near"  # right except extent (own_whole / report_whole) or other decision (report_part)
            special = k["item"]
        else:
            k["_plan"] = "right"
    missed = False
    for k in keys:
        if k["role"] == "real":
            if k["_plan"] == "wrong":
                ans = wrong_f(k)
            else:
                ans = right_f(k)
                if k["_plan"] == "near":
                    if k["effect"] == "report_part":
                        ans["other_decision"] = "Zzyzx v. Qwerty, 999 Q.Q. 999"
                    else:
                        ans["extent"] = "part"
        else:
            confirm = k["role"] == "decoy_right"
            if k["role"] == "decoy_wrong" and not missed and k["pack"] == "1":
                confirm, missed = True, True
                k["_missed"] = True
            if confirm:
                if typ == "A":
                    ans = a_right_answer(k)
                else:
                    ans = b_right_answer(k) if k["kind"] in A.B_COMPAT else dict(b_right_answer(k),
                                                                                  disposition="vacated")
            else:
                ans = wrong_f(k)
        by_pack.setdefault(k["pack"], []).append(ans)
        k["_ans"] = ans
    order = {}
    for p in sorted(os.listdir(rdir)):
        m = re.match(r"pack_(\d+)\.md$", p)
        if m:
            order[m.group(1)] = re.findall(r"^## ITEM (\S+)$", open(os.path.join(rdir, p), encoding="utf-8").read(),
                                           re.M)
    for pk, ans in by_pack.items():
        pos = {i: n for n, i in enumerate(order[pk])}
        ans.sort(key=lambda x: pos[x["item"]])
        A.write_text(os.path.join(rdir, "answers", "ans_%s.jsonl" % pk),
                     "".join(json.dumps(x, ensure_ascii=False) + A.NL for x in ans))
    # second reader on pack 1: flips the first right-planted sampled row to wrong
    second = [dict(x) for x in by_pack["1"]]
    flipped = None
    for x in second:
        k = next(k for k in keys if k["item"] == x["item"])
        if k["role"] == "real" and k["_plan"] == "right":
            second[second.index(x)] = wrong_f(k)
            flipped = k["item"]
            break
    A.write_text(os.path.join(rdir, "answers", "ans_1_b.jsonl"),
                 "".join(json.dumps(x, ensure_ascii=False) + A.NL for x in second))
    # expected numbers (strict reading: the flipped row is wrong)
    for k in reals:
        ok = k["_plan"] in ("right", "near") and k["item"] != flipped
        ext = k["_plan"] == "right" and k["item"] != flipped
        if k["_plan"] == "near" and k["effect"] == "report_part":
            ok = ext = False
        exp["real_n"] += 1
        exp["real_right"] += int(ok)
        exp["real_rext"] += int(ext)
    dec_answers = 0
    dec_ok = 0
    for k in keys:
        if k["role"] == "real":
            continue
        n_read = 2 if k["pack"] == "1" else 1
        dec_answers += n_read
        dec_ok += 0 if k.get("_missed") else n_read
    exp["dec_n"], exp["dec_acc"] = dec_answers, dec_ok
    exp["flipped"], exp["special"] = flipped, special
    exp["n_wrong_dec"] = sum(1 for k in keys if k["role"] == "decoy_wrong")
    exp["n_right_dec"] = sum(1 for k in keys if k["role"] == "decoy_right")
    return keys, exp


def leaks(rdir, keys, cls):
    bad = []
    runpath = os.path.relpath(rdir, A.HERE).replace("\\", "/")   # the self-test's own folder name is allowed
    for p in sorted(os.listdir(rdir)):
        if not p.startswith("pack_"):
            continue
        txt = open(os.path.join(rdir, p), encoding="utf-8").read().replace(runpath, "<run>")
        low = txt.lower()
        for k in keys:
            for f in ("row_id", "src", "decoy_id", "row2_id", "src2"):
                v = k.get(f, "")
                if v and v != "-" and v in txt:
                    bad.append("%s: %s %r" % (p, f, v))
        for w in ("decoy", "selftest", "t10:st", "h10:st", "operativewords", "recognised", "doctrinetie", "antecedent",
                  "partialunknown", "otherGrounds".lower(), cls.lower()):
            if w in low:
                bad.append("%s: word %r" % (p, w))
    br = open(os.path.join(rdir, "BRIEF.md"), encoding="utf-8").read().replace(runpath, "<run>").lower()
    for w in ("decoy", cls.lower(), "operativewords", "recognised"):
        if w in br:
            bad.append("BRIEF.md: word %r" % w)
    return bad


def pair_run(db, lines):
    """Type C: pairs of history rows (cert_B rows + cert_B2 second rows), nested run folder, planted answers:
    every 4th pair not linked, every 4th+1 answered by row 2's kind, the rest by row 1's kind; decoys by truth."""
    d2, pairs, n2 = build_pairs(db)
    rdir = os.path.join(ST, "nest", "run_C")
    out = run(["round10/audit/make_packs10.py", "--class", "selftest-pair", "--cert", db, "--cert", d2, "--pairs",
               pairs, "--n", "12", "--pack-size", "8", "--seed", "79", "--out", rdir, "--force", "--mark-selftest"])
    lines.append("make_packs10 C (%d second rows): %s" % (n2, out.strip().splitlines()[-1]))
    kr = A.read_tsv(os.path.join(rdir, "sample.tsv"))
    head = kr[0]
    keys = [dict(zip(head, r + [""] * (len(head) - len(r)))) for r in kr[1:]]
    reals = [k for k in keys if k["role"] == "real"]
    plan = {}
    by_pack = {}
    for idx, k in enumerate(reals):
        plan[k["item"]] = ("wrong", "row2", "row1", "row1")[idx % 4]
    for k in keys:
        if k["role"] == "real":
            if plan[k["item"]] == "wrong":
                ans = b_wrong_answer(k)
            elif plan[k["item"]] == "row2":
                ans = b_right_answer(dict(k, kind=k["kind2"]))
            else:
                ans = b_right_answer(k)
        elif k["role"] == "decoy_right":
            ans = b_right_answer(k) if k["kind"] in A.B_COMPAT else dict(b_right_answer(k), disposition="vacated")
        else:
            ans = b_wrong_answer(k)
        by_pack.setdefault(k["pack"], []).append(ans)
    for pk, ans in by_pack.items():
        A.write_text(os.path.join(rdir, "answers", "ans_%s.jsonl" % pk),
                     "".join(json.dumps(x, ensure_ascii=False) + A.NL for x in ans))
    run(["round10/audit/score_audit10.py", rdir])
    sc = json.load(open(os.path.join(rdir, "score.json"), encoding="utf-8"))
    c = sc["classes"]["selftest-pair"]["all"]
    n1 = sum(1 for v in plan.values() if v == "row1")
    n2_ = sum(1 for v in plan.values() if v == "row2")
    man = json.load(open(os.path.join(rdir, "manifest.json"), encoding="utf-8"))
    checks = [("type", sc["type"], "C"), ("brief", man.get("brief"), "B"),
              ("brief is B", "what did one court decision do to another" in
               open(os.path.join(rdir, "BRIEF.md"), encoding="utf-8").read().lower(), True),
              ("brief path nested", "round10/audit/selftest10/nest/run_C/answers" in
               open(os.path.join(rdir, "BRIEF.md"), encoding="utf-8").read(), True),
              ("answered", sc["items_answered"], len(keys)), ("problems", sc["problems"], []),
              ("real n", c["n"], len(reals)), ("row 1 right", c["right"]["k"], n1),
              ("row 2 right", c["row2_right"]["k"], n2_), ("only row 1", c["only1_right"]["k"], n1),
              ("only row 2", c["only2_right"]["k"], n2_), ("link", c["link"]["k"], n1 + n2_),
              ("decoys accurate", (sc["decoys"]["accuracy"]["k"], sc["decoys"]["accuracy"]["n"]),
               (len(keys) - len(reals),) * 2),
              ("quote order known", sorted({k["quote_order"] for k in reals}), ["2<1"]),
              ("two quotes shown", all(k["row2_id"] for k in reals), True),
              ("leaks", leaks(rdir, keys, "selftest-pair"), [])]
    for pk, info in man["packs"].items():
        checks.append(("%s decoys >= 10%%" % pk, info["decoys"] * 10 >= info["items"], True))
    it = reals[0]["item"]
    mt = run(["round10/audit/more_text10.py", it, "200"])
    checks.append(("more_text nested run", ">>> " in mt, True))
    good_all = True
    for name, got, want in checks:
        good = got == want
        good_all &= good
        lines.append("  %-4s C %-28s got %s, want %s" % ("ok" if good else "FAIL", name, got, want))
    return good_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    A.utf8_stdout()
    if os.path.isdir(ST) and not a.keep:
        shutil.rmtree(ST)
    da, db, counts = build_inputs()
    lines, ok = ["round-10 audit tools self-test", "inputs: %s" % counts], True
    for typ, cert, cls in (("A", da, "selftest-treat"), ("B", db, "selftest-hist")):
        rdir = os.path.join(ST, "run_" + typ)
        out = run(["round10/audit/make_packs10.py", "--class", cls, "--cert", cert, "--n", "12", "--pack-size", "8",
                   "--seed", "77", "--out", rdir, "--force", "--mark-selftest"])
        lines.append("make_packs10 %s: %s" % (typ, out.strip().splitlines()[-1]))
        keys, exp = plant(rdir, typ)
        run(["round10/audit/score_audit10.py", rdir])
        sc = json.load(open(os.path.join(rdir, "score.json"), encoding="utf-8"))
        c = sc["classes"][cls]["all"]
        d = sc["decoys"]
        checks = [
            ("type", sc["type"], typ),
            ("answered", sc["items_answered"], len(keys)),
            ("unanswered", len(sc["unanswered"]), 0),
            ("problems", len(sc["problems"]), 0),
            ("real n", c["n"], exp["real_n"]),
            ("right k", c["right"]["k"], exp["real_right"]),
            ("right_extent k", c["right_extent"]["k"], exp["real_rext"]),
            ("decoy answers", d["accuracy"]["n"], exp["dec_n"]),
            ("decoy accurate", d["accuracy"]["k"], exp["dec_acc"]),
            ("decoys wrong in key", d["in_key"]["wrong"], exp["n_wrong_dec"]),
            ("decoys right in key", d["in_key"]["right"], exp["n_right_dec"]),
            ("pack 1 has a missed decoy", d["per_pack"]["pack_1"]["accuracy"]["k"] < d["per_pack"]["pack_1"]
             ["accuracy"]["n"], True),
            ("readers", len(sc["readers"]), len([f for f in os.listdir(os.path.join(rdir, "answers"))])),
            ("agreement items", (sc["agreement"] or {}).get("items_read_twice"),
             sum(1 for k in keys if k["pack"] == "1")),
        ]
        p, lo, hi = A.wilson(exp["real_right"], exp["real_n"])
        checks.append(("wilson right", (round(lo, 4), round(hi, 4)), (c["right"]["lo"], c["right"]["hi"])))
        man = json.load(open(os.path.join(rdir, "manifest.json"), encoding="utf-8"))
        for pk, info in man["packs"].items():
            checks.append(("%s decoys >= 10%%" % pk, info["decoys"] * 10 >= info["items"], True))
        lk = leaks(rdir, keys, cls)
        checks.append(("leaks", lk, []))
        it = keys[0]["item"]
        mt = run(["round10/audit/more_text10.py", it, "200"])
        mt2 = run(["round10/audit/more_text10.py", it, "--target", "300"])
        checks.append(("more_text passages marked", ">>> " in mt and " <<<" in mt, True))
        checks.append(("more_text target", mt2.startswith("ITEM %s: the target" % it), True))
        errs = A.read_tsv(os.path.join(rdir, "errors.tsv"))
        n_read = lambda k: 2 if k["pack"] == "1" else 1  # noqa: E731
        want_err = sum(n_read(k) for k in keys if k["role"] == "real" and k["_plan"] != "right") \
            + (1 if exp["flipped"] else 0) + sum(n_read(k) for k in keys if k.get("_missed"))
        checks.append(("errors.tsv lines", len(errs) - 1, want_err))
        for name, got, want in checks:
            good = got == want
            ok &= good
            lines.append("  %-4s %s %-28s got %s, want %s" % ("ok" if good else "FAIL", typ, name, got, want))
        effs = sorted({k["effect"] for k in keys if k["role"] == "real"})
        lines.append("  %s effect classes in the sample: %s; joined/anchor spans: %d items with 2+ passages" % (
            typ, effs, sum(1 for pk in os.listdir(rdir) if pk.startswith("pack_")
                           for _ in re.findall(r"\[PASSAGE 2 of", open(os.path.join(rdir, pk),
                                                                         encoding="utf-8").read()))))
    # ---- joined rows only (doctrineTie / antecedent), excluding the first A run's rows and decoys
    rdir = os.path.join(ST, "run_A_joined")
    out = run(["round10/audit/make_packs10.py", "--class", "selftest-joined", "--cert", da, "--match", "rel=.",
               "--n", "5", "--seed", "78", "--out", rdir, "--force", "--mark-selftest",
               "--exclude", os.path.join(ST, "run_A", "sample.tsv")])
    lines.append("make_packs10 A joined: %s" % out.strip().splitlines()[-1])
    kj = A.read_tsv(os.path.join(rdir, "sample.tsv"))
    hj = kj[0]
    kj = [dict(zip(hj, r + [""] * (len(hj) - len(r)))) for r in kj[1:]]
    k1 = A.read_tsv(os.path.join(ST, "run_A", "sample.tsv"))
    first_ids = {r[6] for r in k1[1:]}
    checks = [("joined rows sampled", sorted(k["joined_rels"] for k in kj if k["role"] == "real"),
               sorted(["antecedent", "antecedent", "doctrineTie"])),
              ("doctrine effect", sorted(k["effect"] for k in kj if k["joined_rels"] == "doctrineTie"), ["doctrine"]),
              ("no overlap with run_A (rows, decoys)", sorted(first_ids & {k["row_id"] for k in kj}), []),
              ("leaks", leaks(rdir, kj, "selftest-joined"), [])]
    for name, got, want in checks:
        good = got == want
        ok &= good
        lines.append("  %-4s J %-28s got %s, want %s" % ("ok" if good else "FAIL", name, got, want))
    ok &= pair_run(db, lines)
    lines.append("RESULT: %s" % ("PASS" if ok else "FAIL"))
    A.write_text(os.path.join(ST, "SELF_TEST_RESULT.txt"), A.NL.join(lines) + A.NL)
    print(A.NL.join(lines))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
