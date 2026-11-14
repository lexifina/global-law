import io, json, os, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "contend",
          "dissent", "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]
WORD = re.compile(r"overrul|abrogat|disapprov|(?<=\s)reced")


def T(i, kind, scope, starts, ends, x, y, conf, fl="", doc=""):
    return dict(id=i, states=True, kind=kind, scope=scope, fl=fl, doc=doc,
                starts=starts if isinstance(starts, list) else [starts],
                ends=ends if isinstance(ends, list) else [ends], x=x, y=y, conf=conf)


def F(i, reason, conf):
    return dict(id=i, states=False, reason=reason, conf=conf)


O, A, D = "overruled", "abrogated", "disapproved"
ALL, OG, PU = "all", "otherGrounds", "partialUnknown"

ANS = {
 "pack_T1v_001": [
  T("s00007", O, OG, "Foster v. Neilson, 2 Pet. 253, 315", "7 Pet. 51", "Foster v. Neilson", "7 Pet. 51", 0.95),
  T("s00325", O, OG, "License Cases, 5 How. 504", "135 U.S. 100", "5 How. 504", "Leisy v. Hardin", 0.9),
  T("s01150", O, ALL, "Collector v. Day, 11 Wall. 113", "306 U. S. 466", "Collector v. Day", "306 U. S. 466", 0.95),
  T("s00436", O, PU, "Pollock v. Farmers", "that holding of Hubbard", "Hubbard", "Pollock", 0.9,
    doc="taxation of undistributed partnership income (that holding of Hubbard)"),
  T("s00186", O, ALL, "Town of Concord v. Portsmouth", "that decision was overruled", "Town of Concord",
    "Fairfield v. County of Gallatin", 0.95),
  T("s00681", A, OG, "Ex parte Siebold, 100 U. S. 371", "225 U. S. 420", "Siebold", "Glasgow v. Moyer", 0.9),
  T("s03036", O, OG, "Kring v. Missouri, 107 U. S. 221", "497 U. S. 37", "Kring v. Missouri", "Collins v. Youngblood", 0.95),
  T("s01500", O, ALL, ["Brown v. Board of Education, 347 U. S. 483", "347 U. S. 483"], ["163 U. S. 537", "Plessy v. Ferguson"],
    "Plessy v. Ferguson", "347 U. S. 483", 0.95),
  T("s00950", O, ALL, "Blackstone v. Miller, 188 U. S. 189. That", "280 U. S. 204", "Blackstone v. Miller", "280 U. S. 204", 0.85),
  T("s00951", O, ALL, "That decision was overruled by the Farmers Loan", "based on Blackstone v. Miller",
    "Blackstone v. Miller", "Farmers Loan", 0.9),
  T("s01228", O, OG, "United States v. Lynah, 188 U. S. 445", "312 U. S. 592", "Lynah", "312 U. S. 592", 0.95),
  T("s01898", O, ALL, "Jones the Court did hold", "203 U. S. 1", "Hodges v. United States", "Jones", 0.85),
  T("s01693", O, ALL, "Betts was overruled by Gideon", "378 U. S. 1", "Twining", "Malloy v. Hogan", 0.95),
  T("s01632", O, PU, "American Banana was squarely decided", "370 U. S. 690", "American Banana", "Continental Ore", 0.75,
    doc="antitrust laws have no extraterritorial application"),
  T("s01049", D, PU, "United States v. Stevenson, 215 U. S. 190", "296 U. S. 188", "Stevenson", "Hastings", 0.6,
    doc="review under the Criminal Appeals Act of statutory construction not the sole basis of the judgment"),
  T("s00758", O, ALL, "Motion Picture Patents Co. v. Universal Film Manufacturing Co., supra", "was specifically overruled",
    "Henry v. Dick", "Motion Picture Patents", 0.9),
  T("s00891", D, PU, "Baltic Mining Co. v. Massachusetts had sometimes", "disapproved by Alpha Portland Cement Co. v. Mass",
    "Baltic Mining", "Alpha Portland Cement", 0.7,
    doc="a tax burdening interstate commerce may be sustained if relatively small"),
  T("s00892", O, OG, "Baltic Mining Co. v. Massachusetts, 231 U. S. 68, 88", "268 U. S. 203", "Baltic Mining", "Alpha Portland Cement", 0.9),
  T("s01611", O, OG, "Weeks v. United States, 232 U.S. 383", "367 U.S. 643", "Weeks v. United States", "Mapp v. Ohio", 0.95),
  T("s01216", O, ALL, "Hammer v. Dagenhart. It was decided", "312 U. S. 100", "Hammer v. Dagenhart", "Darby", 0.8),
  T("s01236", O, ALL, "overruled the earlier decision of this Court in Toledo", "Nye v. United States",
    "Toledo Newspaper", "Nye v. United States", 0.9),
  T("s01238", O, PU, "overruled in Nye v. United States, 313 U. S. 33", "Cf. Toledo Newspaper Co. v. United States",
    "Toledo Newspaper", "Nye v. United States", 0.8, doc="broad construction of the Act of 1831 on summary contempt"),
  T("s01110", O, ALL, "the Court explicitly overruled only the Gillespie", "Mountain Producers", "Gillespie", "Mountain Producers", 0.8),
  T("s01167", O, PU, "Although the case was after-wards overruled", "reliance in Miles", "Miles", "Woodrough", 0.85,
    fl="on this point"),
  T("s01046", D, PU, "Executor v. United States, 295 U. S. 602", "the expressions in Myers", "Myers", "295 U. S. 602", 0.8,
    doc="President's inherent power to remove members of quasi-judicial bodies"),
  T("s01233", O, ALL, "Ribnik v. McBride was overruled", "313 U. S. 236", "Ribnik v. McBride", "Olsen v. Nebraska", 0.95),
  T("s01712", D, OG, "United States v. Murdock, 284 U. S. 141", "378 U. S. 52", "284 U. S. 141", "378 U. S. 52", 0.95),
  T("s01299", O, ALL, "Grovey was overruled", "321 U. S. 649", "Grovey", "Smith v. Allwright", 0.9),
  T("s01188", O, ALL, "These cases were expressly overruled by Helvering v. Hallock", "St. Louis Trust and Becker cases",
    "Becker", "Helvering v. Hallock", 0.85),
  T("s01084", O, PU, "West Coast Hotel Co. v. Parrish, 300 U. S. 379, overruled", "298 U. S. 587", "Morehead v. Tipaldo",
    "West Coast Hotel", 0.9, fl="as to power to enact minimum wage laws"),
  T("s01957", O, ALL, "Benton v. Maryland, 395 U. S. 784", "302 U. S. 319", "Palko v. Connecticut", "Benton v. Maryland", 0.95),
  T("s01830", O, ALL, "Katz v. United States, 389 U. S. 347 (1967), overruled", "316 U. S. 129", "316 U. S. 129", "Katz v. United States", 0.95),
  T("s01643", O, ALL, "Gideon v. Wainwright, 372 U. S. 335 (1963), however", "Betts was overruled", "Betts", "Gideon v. Wainwright", 0.95),
  T("s01947", O, ALL, "Chimel v. California, 395 U. S. 752", "331 U. S. 145", "Harris v. United States", "Chimel v. California", 0.95),
  T("s01697", O, ALL, "The Malloy case overruled", "332 U. S. 46", "Adamson v. California", "Malloy", 0.95),
  T("s01616", O, PU, "Mapp v. Ohio, 367 U. S. 643 (1961), we held", "338 U. S. 25", "Wolf v. Colorado", "Mapp v. Ohio", 0.95,
    fl="to the extent that it failed to apply the exclusionary rule to the States"),
  T("s02401", O, ALL, "Burks we held that once", "Bryan v. United States, 338 U. S. 552", "Bryan v. United States", "Burks", 0.85),
  T("s01653", O, ALL, "Darr v. Burford, 339 U. S. 200", "372 U. S. 391", "Darr v. Burford", "Fay v. Noia", 0.95),
  F("s02108", "notOverruling", 0.8),
  T("s01846", O, ALL, "Marchetti, which overruled", "345 U. S. 22", "Kahriger", "Marchetti", 0.95),
  T("s01710", O, ALL, "Jackson", "346 U. S. 156", "Stein v. New York", "Jackson", 0.85),
  T("s01711", O, OG, "Stein v. New York, 346 U. S. 156", "378 U. S. 368", "Stein v. New York", "Jackson v. Denno", 0.95),
  T("s02932", O, OG, "Wilko v. Swan, 346 U. S. 427", "490 U. S. 477", "Wilko v. Swan", "Rodriguez de Quijas", 0.95),
  T("s02934", O, ALL, "overruled Wilko and", "490 U. S. 477", "Wilko", "Rodriguez de Quijas", 0.9),
  T("s01551", O, PU, ["Kinsella v. Krueger, 351 U. S. 470", "351 U. S. 470 (1956); Reid"], "354 U. S. 1", "351 U. S. 470", "354 U. S. 1", 0.7,
    doc="Constitution applies with full force only in the States and incorporated Territories"),
 ],
 "pack_T1v_002": [
  T("s01552", O, PU, "Reid v. Covert, 351 U. S. 487", "354 U. S. 1", "351 U. S. 487", "354 U. S. 1", 0.7,
    doc="Constitution applies with full force only in the States and incorporated Territories"),
  T("s01776", O, OG, "Cicenia v. Lagay, 357 U. S. 504", "384 U. S. 436", "Cicenia v. Lagay", "Miranda v. Arizona", 0.95),
  T("s01792", O, OG, "Cohen v. Hurley, in other respects", "385 U. S. 511", "Cohen v. Hurley", "Spevack v. Klein", 0.85),
  T("s01793", O, OG, "Cohen v. Hurley, 366 U.S. 117", "385 U.S. 511", "Cohen v. Hurley", "Spevack v. Klein", 0.95),
  T("s03263", O, ALL, "Parden v. Terminal R. Co.", "see Seminole Tribe", "Parden", "Seminole Tribe", 0.5),
  F("s03370", "otherDecision", 0.75),
  T("s03151", O, PU, "Bellas Hess linked", "Court in Quill overruled", "Bellas Hess", "Quill", 0.8, fl="due process holding"),
  T("s02831", O, ALL, "overruled by Griffith", "388 U. S. 293", "Stovall v. Denno", "Griffith", 0.8),
  T("s02235", O, ALL, "Hudgens we made it clear", "Logan Valley was overruled", "Logan Valley", "Hudgens", 0.65),
  T("s03167", O, PU, "Casey overruled the holdings", "462 U. S. 416", "Akron v. Akron Center", "Casey", 0.9, fl="On this point"),
  T("s03311", O, ALL, ["Agostini v. Felton, 521 U. S. 203", "521 U. S. 203"], ["473 U. S. 373", "Grand Rapids v. Ball"],
    "Grand Rapids v. Ball", "521 U. S. 203", 0.9),
  T("s03173", O, ALL, "Casey and once again", "476 U. S. 747", "Thornburgh", "Casey", 0.65),
  T("s03482", O, ALL, "overruled Bowers", "539 U. S. 558", "Bowers", "Lawrence v. Texas", 0.95),
  T("s03113", O, ALL, "Payne v. Tennessee, 501 U. S. 808", "490 U. S. 805", "South Carolina v. Gathers", "Payne v. Tennessee", 0.95),
  T("s03272", O, ALL, "Seminole Tribe, of course", "491 U. S. 1", "Pennsylvania v. Union Gas", "Seminole Tribe", 0.95),
  T("s03460", O, OG, "Walton v. Arizona, 497 U. S. 639", "536 U. S. 584", "Walton v. Arizona", "Ring v. Arizona", 0.95),
  T("s03461", O, ALL, "overruled our earlier decision in Walton", "relying on Ring", "Walton v. Arizona", "Ring", 0.85),
  T("s03462", O, OG, "Walton, supra, overruled", "536 U. S. 584", "Walton", "Ring v. Arizona", 0.9),
  T("s03612", O, PU, "Citizens United v. Federal Election Comm", "540 U. S. 93", "McConnell v. Federal Election", "Citizens United", 0.95),
 ],
}


def parse(path):
    txt = io.open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    items = []
    for blk in re.split(r"(?m)^### ITEM ", txt)[1:]:
        iid = blk.split("\n", 1)[0].strip()
        m = re.search(r"\nWINDOW:\n(.*?)\nNOTE AT:\n", blk, re.S)
        items.append((iid, m.group(1)))
    return items


def pick(win, a):
    best = None
    for s in a["starts"]:
        i = win.find(s)
        if i < 0:
            continue
        for e in a["ends"]:
            j = win.find(e, i)
            if j < 0:
                continue
            q = win[i:j + len(e)]
            if len(q) <= 400:
                return q
            best = best or q
    return best


ok = True
for pack, answers in ANS.items():
    items = parse(os.path.join(BASE, "packs", pack + ".md"))
    ids = [i for i, _ in items]
    if ids != [a["id"] for a in answers]:
        print("ORDER/ID MISMATCH", pack, ids, [a["id"] for a in answers])
        ok = False
        continue
    wins = dict(items)
    out = []
    ntrue = 0
    for a in answers:
        if not a["states"]:
            out.append({"id": a["id"], "states": False, "reason": a["reason"], "kind": "", "scope": "",
                        "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]})
            continue
        win = wins[a["id"]]
        q = pick(win, a)
        probs = []
        if q is None:
            probs.append("anchor not found")
            q = ""
        if q not in win or not q:
            probs.append("not substring")
        if len(q) > 400:
            probs.append("too long %d" % len(q))
        if not WORD.search(q):
            probs.append("no overruling word")
        if a["x"] not in q:
            probs.append("x missing")
        if a["y"] not in q:
            probs.append("y missing")
        low = q.lower()
        for f in FORBID:
            if f in low:
                probs.append("forbidden: " + f)
        if probs:
            ok = False
        sys.stdout.buffer.write(("%s [%d] %s\n   %s\n" % (a["id"], len(q), "; ".join(probs) or "ok", q)).encode("utf-8"))
        ntrue += 1
        out.append({"id": a["id"], "states": True, "kind": a["kind"], "scope": a["scope"], "field_limit": a["fl"],
                    "doctrine": a["doc"], "quote": q, "confidence": a["conf"]})
    dst = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    # re-read and re-verify
    rows = [json.loads(l) for l in io.open(dst, encoding="utf-8").read().split("\n") if l]
    assert [r["id"] for r in rows] == ids
    for r in rows:
        if r["states"]:
            assert r["quote"] in wins[r["id"]] and len(r["quote"]) <= 400 or not ok, r["id"]
    print("%s: items=%d true=%d" % (pack, len(rows), ntrue))
print("ALL OK" if ok else "PROBLEMS")
