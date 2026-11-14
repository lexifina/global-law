"""diag step 4: merge the reader shards and the D table into scdb66.tsv (+ scdb66_pairs.tsv) and print the counts.

    python merge.py

Inputs (all under round5/diag/): pairs.tsv, shard_1..4.jsonl (readers' answers per (Y, X)), text/<node>.md,
nodes_meta.tsv, and the hand-reviewed D table below (from d_witness.tsv, d_notes.tsv, dsearch_hits.tsv,
dsearch_y_hits.tsv). Every own_sentence and every D snippet is checked to be a substring of the cached text
(whitespace runs compared as one space); a failed check is printed and marked in the note.
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

# targets found by the readers for the decisions with no listed target (idx -> node, name)
EXTRA_X = {
    18: ("5943980", "People v. Central Railroad, 12 Wall. 455 (1871)"),
    39: ("6035581", "Ohio v. Wyandotte Chemicals Corp., 401 U.S. 493, 498 n. 3 (1971) (statement)"),
    58: ("5985485", "International Salt Co. v. United States, 332 U.S. 392 (1947)"),
    59: ("6194005", "Stenberg v. Carhart, 530 U.S. 914 (2000)"),
    60: ("6025122", "School Comm. of Boston v. Board of Education, 389 U.S. 572 (1968)"),
    61: ("5945085", "United States v. Cruikshank, 92 U.S. 542 (1876)"),
    63: ("6259892", "Martinez v. Ryan, 566 U.S. 1 (2012)"),
    64: ("6218074", "Grutter v. Bollinger, 539 U.S. 306 (2003)"),
    65: ("6226403", "Sosa v. Alvarez-Machain, 542 U.S. 692 (2004)"),
}

# D, strict: a later Supreme Court opinion of the Court says, with "overrul" / "abrogat" (the provisional
# `recognised` cue list), that Y overruled X. (Y, X) -> (W, snippet, both_named, note)
D_STRICT = {
    ("5945927", "5945089"): ("5947923", "but in tbe subsequent case of Fairfield v. County of Gallatin, 100 U. S. 47, that decision was overruled", 1,
                             "installed witness row tw:5945927:5945089:25828:5947923; X named earlier in the same sentence"),
    ("5946204", "5944522"): ("5948300", "this court, at October term, 1880, by a unanimous opinion, overruled its decision in Mitchell v. Tilghman", 0,
                             "W is the second appeal in Tilghman v. Proctor; Y named only as 'October term, 1880' (a later sentence has '102 TJ. S. 707', OCR); not an installed witness row"),
    ("5950449", "5943925"): ("5959259", "it must be regarded as overruled by Pollock v. Farmers’ Loan & Trust Co., 158 U. S. 601, 627, 628, 637", 0,
                             "target is Collector v. Hubbard, 12 Wall. 1 (named in the sentences before and after), NOT the CRS target Hylton; installed witness row tw:5950449:5943925:59311:5959259"),
    ("6008121", "5988307"): ("6011415", "this Court’s decision in Mapp v. Ohio, 367 U. S. 643, overruling Wolf v. Colorado, 338 U. S. 25", 1,
                             "earliest found; the installed witness row uses Schmerber (6020097, 1966-06-20)"),
    ("6009464", "5983464"): ("6323819", "effectively overruling in part Colegrove, 328 U. S. 549", 1,
                             "Dobbs list of overrulings: 'Baker v. Carr, 369 U. S. 186 (1962) (...), effectively overruling in part Colegrove'; not an installed witness row"),
    ("6040491", "6035581"): ("6077819", "The Court in Illinois v. Milwaukee found it necessary to overrule this statement, see 406 U. S., at 102, n. 3.", 0,
                             "target is a statement (Wyandotte n. 3), quoted in the sentence before; also International Paper v. Ouellette (6105697, 1987): 'thus overruling the contrary suggestion in Wyandotte'; not an installed witness row"),
    ("6043664", "5986747"): ("6110802", "Braden v. 30th Judicial Circuit Court of Kentucky, 410 U. S. 484 (1973), overruling Ahrens v. Clark, 335 U. S. 188 (1948)", 1,
                             "installed witness row tw:6043664:5986747:3720:6110802, but its stored quote is the first item of the list ('Monell ... overruling Monroe v. Pape'), which names neither X nor Y"),
    ("6055982", "5977806"): ("6129139", "Virginia State Bd. of Pharmacy v. Virginia Citizens Consumer Council, Inc., 425 U. S. 748 (1976) (overruling Valentine v. Chrestensen, 316 U. S. 52 (1942))", 1,
                             "Payne v. Tennessee n. 1; installed witness row. Weaker earlier statements: 6091863 (1984) 'we rejected that broad conclusion'; 6156535 (1995) 'we repudiated that position'"),
    ("6091837", "5947965"): ("6129139", "Pennhurst State School and Hospital v. Halderman, 465 U. S. 89 (1984) (overruling in part Rolston v. Missouri Fund Comm’rs, 120 U. S. 390 (1887))", 1,
                             "Payne v. Tennessee n. 1; installed witness row; none found for the four other CRS targets of Pennhurst"),
    ("6225347", "6074209"): ("6239478", "We overruled Roberts in Crawford by restoring the unavailability and cross-examination requirements.", 1,
                             "Davis v. Washington; installed witness row quotes 'Crawford, in overruling Roberts' from the same decision"),
}

# D, weak: a later opinion of the Court says something short of that (another verb, the doctrine not the case,
# Y or X not named). Not counted in D. (Y, X or "") -> (W, snippet, why)
D_WEAK = {
    ("5947811", "5945248"): ("5956532", "a view which- was later repudiated. Wabash, St. L. & P. Railway Co. v. Illinois, 118 U. S. 557.",
                             "verb 'repudiated' (not in the recognised cue list); installed witness row. Earlier: Covington Bridge (5950194, 1894) 'they must be considered as overruled', conditional and X only by anaphora"),
    ("6015544", "5946700"): ("6023529", "in rejecting the reasoning of that case, we stated “Pace represents a limited view of the Equal Protection Clause which has not withstood analysis in the subsequent decisions of this Court.” McLaughlin v. Florida, supra, at 188.",
                             "Loving v. Virginia: 'rejecting the reasoning', not 'overruled'"),
    ("6185746", "5950736"): ("6320578", "Although Mille Lacs stopped short of explicitly overruling Race Horse, it methodically repudiated that decision’s logic.",
                             "Herrera v. Wyoming: says Mille Lacs did NOT explicitly overrule; Herrera itself then acts ('Race Horse is repudiated to the extent ...')"),
    ("6129135", "6011607"): ("6134280", "Justice O’Connor puts aside our overruling of Fay v. Noia’s standard in procedural default cases",
                             "Keeney v. Tamayo-Reyes: Y not named in the sentence (credited to 'Wainwright, Coleman, and other cases'); Martinez v. Ryan (2012): 'Fay v. Noia ..., overruled in part by Sykes'"),
    ("6052884", "5942377"): ("6239737", "when we abrogated the admiralty rule of divided damages in favor of proportional liability",
                             "Exxon Shipping v. Baker: about the rule (doctrine), The Catharine not named"),
    ("6239456", "5985485"): ("6290724", "relying on that legislative change to overrule antitrust decisions about tying and to adopt the same standard",
                             "Kimble v. Marvel: 'antitrust decisions about tying', no case named"),
}

# later opinions of the Court that credit the overruling of X to ANOTHER decision Z (Y, X) -> text
D_OTHER = {
    ("5958396", "5955841"): "later Court credits Motion Picture Patents (1917), not Y: United Shoe (1922) 'Henry v. Dick Co. ... was specifically overruled'; Mercoid (1944) 'was overruled by Motion Picture Co.'",
    ("6068144", "6008222"): "later Court credits Taylor v. Louisiana (1975), not Y: Payne (1991) 'Taylor v. Louisiana ... (overruling in effect Hoyt v. Florida)'; J. E. B. (1994); Dobbs (2022)",
    ("6120905", "5954716"): "later Court credits Continental Ore (1962), not Y: Morrison (2010) 'Continental Ore overruled the holding of American Banana'",
    ("6033635", "5951175"): "later Court credits Collins v. Youngblood (1990) with overruling Thompson v. Utah (another point): Payne (1991) n. 1; Carmell (2000)",
    ("5979159", "5977813"): "same case: later Courts cite 316 U.S. 584 as 'vacated ... per curiam, 319 U. S. 103' (1969) / 'reversed on rehearing' (1947 dissent)",
}


# my final calls where I differ from the reader on A_kind (idx -> (kind, reason)). Rule applied to all 66: `operative`
# needs a verb of lost authority whose object is X itself (the case, its decision, its language).
OVERRIDE = {
    40: ("operative", "lead call: 'we can no longer view that decision as establishing ...' is a no-longer act on the named decision (reader: contrary); borderline"),
    46: ("contrary", "lead call: the verb ('no longer justify', 'should be modified') has the rule as object, not Hawkins (reader: operative, borderline)"),
    53: ("contrary", "lead call: the object of 'eliminate' is the distinction, not Fay (reader: operative, borderline)"),
}


def norm(s):
    return re.sub(r"\s+", " ", s.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")).strip()


_texts = {}


def text(node):
    if node not in _texts:
        p = os.path.join(HERE, "text", node + ".md")
        _texts[node] = norm(open(p, encoding="utf-8", newline="").read()) if os.path.exists(p) else None
    return _texts[node]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    meta = {}
    with open(os.path.join(HERE, "nodes_meta.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            meta[p[0]] = p
    with open(os.path.join(HERE, "pairs.tsv"), encoding="utf-8", newline="") as f:
        pairs = list(csv.DictReader(f, delimiter="\t"))
    ans = {}
    for k in (1, 2, 3, 4):
        p = os.path.join(HERE, "shard_%d.jsonl" % k)
        if not os.path.exists(p):
            print("MISSING", p)
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    ans[(int(d["idx"]), str(d["by_node"]), str(d["target_node"]))] = d
    bad = []
    prow = []
    for pr in pairs:
        idx, y, x = int(pr["idx"]), pr["by_node"], pr["target_node"]
        d = ans.get((idx, y, x))
        if d is None:
            bad.append("no answer for idx %d %s %s" % (idx, y, x))
            continue
        xname = pr["target_name"] + (" " + pr["target_cite"] if pr["target_cite"] else "")
        x_src = "crs"
        if x == "-1":
            x_src = "reader"
            if idx in EXTRA_X:
                x, xname = EXTRA_X[idx]
            else:
                xname = d.get("target_name", "")
        s = d.get("own_sentence", "") or ""
        s = re.sub(r"\s+", " ", s).strip()
        ok = (not s) or (norm(s) in (text(y) or ""))
        if not ok:
            bad.append("own_sentence not found: idx %d %s" % (idx, y))
        kind = d.get("A_kind", "none")
        if idx in OVERRIDE and kind != "none":
            kind = OVERRIDE[idx][0]
            d["note"] = d.get("note", "") + " [" + OVERRIDE[idx][1] + "]"
        ds = D_STRICT.get((y, x))
        dw = D_WEAK.get((y, x))
        prow.append({
            "idx": idx, "by_node": y, "target_node": x, "label": meta[y][6] + " / " + xname, "x_src": x_src,
            "A": 1 if kind == "operative" else 0, "A_contrary": 1 if kind == "contrary" else 0,
            "B": int(d.get("B", 0)), "C": int(d.get("C", 0)), "D": 1 if ds else 0,
            "own_sentence": s, "own_ok": ok,
            "D_w": ds[0] if ds else "", "D_snip": ds[1] if ds else "", "D_both": ds[2] if ds else "",
            "D_note": ds[3] if ds else "", "D_weak": 1 if dw else 0,
            "D_weak_w": dw[0] if dw else "", "D_weak_snip": dw[1] if dw else "", "D_weak_note": dw[2] if dw else "",
            "D_other": D_OTHER.get((y, x), ""),
            "doctrine": d.get("doctrine", ""), "field": d.get("field", ""), "x_in_majority": d.get("x_in_majority", ""),
            "past_report": int(d.get("past_report", 0)), "sep_says": int(d.get("sep_says", 0)),
            "syllabus_says": int(d.get("syllabus_says", 0)), "gold_doubt": int(d.get("gold_doubt", 0)),
            "note": re.sub(r"\s+", " ", d.get("note", "")),
        })
    # strict D rows whose target is not a listed pair (Pollock / Collector v. Hubbard): add as an extra pair row
    have = {(r["by_node"], r["target_node"]) for r in prow}
    for (y, x), ds in D_STRICT.items():
        if (y, x) not in have:
            idx = next(r["idx"] for r in prow if r["by_node"] == y)
            prow.append({"idx": idx, "by_node": y, "target_node": x, "label": meta[y][6] + " / " + meta[x][6] + " " + meta[x][5].split("|")[0],
                         "x_src": "later-court", "A": 0, "A_contrary": 0, "B": 0, "C": 0, "D": 1, "own_sentence": "",
                         "own_ok": True, "D_w": ds[0], "D_snip": ds[1], "D_both": ds[2], "D_note": ds[3], "D_weak": 0,
                         "D_weak_w": "", "D_weak_snip": "", "D_weak_note": "", "D_other": "", "doctrine": "", "field": "",
                         "x_in_majority": "not_read", "past_report": 0, "sep_says": 0, "syllabus_says": 0,
                         "gold_doubt": 0, "note": "target named only by the later Court; Y's text not read for it"})
    for (y, x), dw in D_WEAK.items():
        if (y, x) not in have:
            bad.append("weak D key without a pair: %s %s" % (y, x))
    # verify D snippets
    for r in prow:
        for wk, sk in (("D_w", "D_snip"), ("D_weak_w", "D_weak_snip")):
            if r[wk]:
                t = text(r[wk])
                if t is None or norm(r[sk]) not in t:
                    bad.append("D snippet not found: %s in %s" % (r[sk][:50], r[wk]))
    for r in prow:
        r["E"] = 0 if (r["A"] or r["B"] or r["C"] or r["D"]) else 1
        r["primary"] = "A" if r["A"] else "BC" if (r["B"] or r["C"]) else "D" if r["D"] else "E"
        r["primary5"] = ("A" if r["A"] else "A~" if r["A_contrary"] else "BC" if (r["B"] or r["C"]) else
                         "D" if r["D"] else "E")
    prow.sort(key=lambda r: (r["idx"], r["x_src"] != "crs", int(r["target_node"]) if r["target_node"].lstrip("-").isdigit() else 0))

    def wdate(w):
        return meta[w][4] if w in meta else ""

    def wname(w):
        return meta[w][6] if w in meta else ""

    cols = ["by_node", "target_node", "label", "A", "B", "C", "D", "E", "primary", "own_sentence", "D_witness_node",
            "D_witness_date", "D_snippet", "note",
            # extra columns
            "idx", "A_contrary", "A_kind", "D_both_named", "D_weak", "D_weak_witness", "D_weak_snippet", "doctrine",
            "field", "x_in_majority", "past_report", "sep_says", "syllabus_says", "gold_doubt", "target_source",
            "n_targets", "primary5"]

    def note_of(r):
        parts = [r["note"]]
        if r["D_note"]:
            parts.append("D: %s (%s)" % (r["D_note"], wname(r["D_w"])))
        if r["D_weak_note"]:
            parts.append("weak D: %s (%s %s)" % (r["D_weak_note"], wname(r["D_weak_w"]), wdate(r["D_weak_w"])))
        if r["D_other"]:
            parts.append(r["D_other"])
        if not r["own_ok"]:
            parts.append("QUOTE NOT VERIFIED")
        return " | ".join(p for p in parts if p)

    def line_of(r, n_targets, tnode=None, label=None, note=None):
        kind = "operative" if r["A"] else "contrary" if r["A_contrary"] else "none"
        v = [r["by_node"], tnode or r["target_node"], label or r["label"], r["A"], r["B"], r["C"], r["D"], r["E"],
             r["primary"], r["own_sentence"], r["D_w"], wdate(r["D_w"]), r["D_snip"], note or note_of(r),
             r["idx"], r["A_contrary"], kind, r["D_both"], r["D_weak"], r["D_weak_w"], r["D_weak_snip"],
             r["doctrine"], r["field"], r["x_in_majority"], r["past_report"], r["sep_says"], r["syllabus_says"],
             r["gold_doubt"], r["x_src"], n_targets, r["primary5"]]
        return "\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in v)

    with open(os.path.join(HERE, "scdb66_pairs.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for r in prow:
            f.write(line_of(r, 1) + "\n")
    # decision level
    by = defaultdict(list)
    for r in prow:
        by[r["idx"]].append(r)
    order = {"A": 0, "A~": 1, "BC": 2, "D": 3, "E": 4}
    dec = []
    for idx in sorted(by):
        rs = by[idx]
        a = {k: max(r[k] for r in rs) for k in ("A", "A_contrary", "B", "C", "D", "D_weak", "past_report", "sep_says",
                                               "syllabus_says")}
        a["A_contrary"] = 0 if a["A"] else a["A_contrary"]
        a["gold_doubt"] = min(r["gold_doubt"] for r in rs if r["x_src"] != "later-court")
        listed = [r for r in rs if r["x_src"] != "later-court"]
        best = min(listed, key=lambda r: order[r["primary5"]])
        dbest = [r for r in rs if r["D"]]
        dbest.sort(key=lambda r: wdate(r["D_w"]))
        wbest = [r for r in rs if r["D_weak"]]
        m = dict(best)
        m.update(a)
        m["E"] = 0 if (a["A"] or a["B"] or a["C"] or a["D"]) else 1
        m["primary"] = "A" if a["A"] else "BC" if (a["B"] or a["C"]) else "D" if a["D"] else "E"
        m["primary5"] = ("A" if a["A"] else "A~" if a["A_contrary"] else "BC" if (a["B"] or a["C"]) else
                         "D" if a["D"] else "E")
        for k in ("D_w", "D_snip", "D_both", "D_note"):
            m[k] = dbest[0][k] if dbest else ""
        for k in ("D_weak_w", "D_weak_snip", "D_weak_note"):
            m[k] = wbest[0][k] if wbest else ""
        m["doctrine"] = "; ".join(sorted({r["doctrine"] for r in rs if r["doctrine"]}))
        m["field"] = "; ".join(sorted({r["field"] for r in rs if r["field"]}))
        m["D_other"] = " ".join(sorted({r["D_other"] for r in rs if r["D_other"]}))
        tnode = ";".join(r["target_node"] for r in rs)
        if len(rs) > 1:
            names = "; ".join(r["label"].split(" / ", 1)[1] for r in rs)
            label = meta[m["by_node"]][6] + " / " + names
            note = " || ".join("[%s %s] %s" % (r["target_node"], r["primary5"], note_of(r)) for r in rs)
        else:
            label, note = None, None
        m["x_src"] = ",".join(sorted({r["x_src"] for r in rs}))
        dec.append((m, len(rs), tnode, label, note))
    with open(os.path.join(HERE, "scdb66.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for m, n, tnode, label, note in dec:
            f.write(line_of(m, n, tnode, label, note) + "\n")
    # counts
    D = [m for m, *_ in dec]
    print("decisions", len(D), "pair rows", len(prow))
    for k in ("A", "A_contrary", "B", "C", "D", "D_weak", "E", "past_report", "sep_says", "syllabus_says", "gold_doubt"):
        print("%-14s %d" % (k, sum(m[k] for m in D)))
    print("primary (A > B/C > D > E)", dict(Counter(m["primary"] for m in D)))
    print("primary5 (A > A~ > B/C > D > E)", dict(Counter(m["primary5"] for m in D)))
    S = lambda f: sum(1 for m in D if f(m))
    print("reach D", S(lambda m: m["D"]), "| D both named", S(lambda m: m["D"] and m["D_both"] == 1),
          "| D or weak D", S(lambda m: m["D"] or m["D_weak"]))
    print("reach A", S(lambda m: m["A"]), "| A or A~", S(lambda m: m["A"] or m["A_contrary"]))
    print("reach A or D", S(lambda m: m["A"] or m["D"]), "| A, A~ or D", S(lambda m: m["A"] or m["A_contrary"] or m["D"]),
          "| A, A~, D or weak D", S(lambda m: m["A"] or m["A_contrary"] or m["D"] or m["D_weak"]))
    print("only B/C (no A, no D)", S(lambda m: (m["B"] or m["C"]) and not m["A"] and not m["D"]),
          "| only B/C (no A, A~, D)", S(lambda m: (m["B"] or m["C"]) and not m["A"] and not m["A_contrary"] and not m["D"]))
    print("nothing: no A, B, C, D", S(lambda m: m["E"]), "| and no A~", S(lambda m: m["E"] and not m["A_contrary"]),
          "| and no weak D", S(lambda m: m["E"] and not m["A_contrary"] and not m["D_weak"]))
    print("E & A~ & gold_doubt", S(lambda m: m["E"] and m["A_contrary"] and m["gold_doubt"]),
          "| no-words (no A~) & gold_doubt", S(lambda m: m["E"] and not m["A_contrary"] and m["gold_doubt"]),
          "| no-words & sep_says", S(lambda m: m["E"] and not m["A_contrary"] and m["sep_says"]),
          "| no-words & past_report", S(lambda m: m["E"] and not m["A_contrary"] and m["past_report"]),
          "| no-words, no doubt", S(lambda m: m["E"] and not m["A_contrary"] and not m["gold_doubt"]))
    print("no-words list:", [(m["idx"], m["gold_doubt"], m["sep_says"], m["past_report"], m["D_weak"]) for m in D if m["E"] and not m["A_contrary"]])
    print("combos", sorted(Counter("".join(k[0] if k != "A_contrary" else "a" for k in ("A", "A_contrary", "B", "C", "D")
                                           if m[k]) or "E" for m in D).items()))
    print("B or C", sum(1 for m in D if m["B"] or m["C"]))
    print("D among non-A", sum(1 for m in D if m["D"] and not m["A"]))
    print("E with weak D", sum(1 for m in D if m["E"] and m["D_weak"]),
          "E with gold_doubt", sum(1 for m in D if m["E"] and m["gold_doubt"]),
          "E with sep_says", sum(1 for m in D if m["E"] and m["sep_says"]),
          "E with past_report", sum(1 for m in D if m["E"] and m["past_report"]))
    print("x_src", Counter(m["x_src"] for m in D))
    print("x_in_majority (pairs)", Counter(r["x_in_majority"] for r in prow))
    for b in bad:
        print("CHECK:", b)


if __name__ == "__main__":
    main()
