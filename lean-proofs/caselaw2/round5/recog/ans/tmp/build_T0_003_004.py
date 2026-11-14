# -*- coding: utf-8 -*-
import json, os, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "argu", "contend", "urge",
          "dissent", "question", "doubt"]
WORDS = ["overrul", "abrogat", "disapprov", "reced"]

OG, PU, ALL = "otherGrounds", "partialUnknown", "all"
OV, AB = "overruled", "abrogated"


def T(i, kind, scope, start, end, x, y, conf=0.95, field="", doctrine=""):
    return dict(id=i, states=True, kind=kind, scope=scope, start=start, end=end, x=x, y=y,
                conf=conf, field=field, doctrine=doctrine)


def F(i, reason, conf=0.85):
    return dict(id=i, states=False, reason=reason, conf=conf)


P3 = [
    T("w091", OV, ALL, "Knapp v. Schweitzer", "378 U. S. 52", "Knapp", "Murphy", 0.97),
    F("w092", "notOverruling", 0.8),
    T("w093", OV, PU, "Brimson\u2019s holding", "391 U. S. 194", "Brimson", "Bloom", 0.9,
      doctrine="no right to jury trial in criminal contempt proceedings"),
    F("w094", "notOverruling", 0.85),
    T("w095", OV, OG, "Williams v. United States, 307 F.2d 366", "394 U.S. 217", "Williams", "Kaufman"),
    F("w096", "notOverruling", 0.85),
    T("w097", OV, ALL, "Chimel v. California", "331 U. S. 145", "Harris", "Chimel", 0.93),
    T("w098", OV, ALL, "United States v. Rabinowitz", "395 U. S. 752", "Rabinowitz", "Chimel"),
    T("w099", OV, OG, "Atkinson v. Sinclair Refining Co.", "398 U. S. 235", "Atkinson", "Boys Markets"),
    T("w100", OV, ALL, "Ramos was based upon", "Supreme Court in Mitchell", "Ramos", "Mitchell", 0.85),
    T("w101", OV, ALL, "Dunn v. Blumstein", "193 U. S. 621", "Pope", "Dunn"),
    T("w102", OV, ALL, "Lehnhausen v. Lake Shore", "277 U. S. 389", "Quaker City Cab", "Lehnhausen"),
    T("w103", OV, ALL, "Braden v. 30th Judicial", "335 U. S. 188", "Ahrens", "Braden"),
    T("w104", OV, ALL, "Miller v. California", "383 U. S. 413", "Memoirs", "Miller"),
    F("w105", "negation", 0.85),
    T("w106", OV, ALL, "Virginia State Bd. of Pharmacy", "316 U. S. 52", "Valentine", "Virginia State Bd."),
    T("w107", OV, ALL, "Machinists v. Wisconsin", "336 U. S. 245", "Auto Workers", "Machinists"),
    T("w108", OV, ALL, "Complete Auto Transit", "340 U. S. 602", "Spector", "Complete Auto"),
    T("w109", OV, ALL, "Continental T. V., Inc. v. GTE Sylvania", "388 U. S. 365", "Arnold", "Continental"),
    T("w110", OV, PU, "Fay v. Noia", "overruled in part by Sykes", "Fay", "Sykes", 0.93),
    F("w111", "notOverruling", 0.85),
    T("w112", AB, OG, "Ultracashmere House", "Moses H. Cone, 460 U.S.", "Ultracashmere", "Moses H. Cone"),
    T("w113", OV, PU, "Pennhurst State School", "120 U. S. 390", "Rolston", "Pennhurst"),
    T("w114", OV, OG, "United States v. Cook", "469 U.S. 38", "Cook", "Luce"),
    T("w115", OV, PU, "United States v. Miller, 471", "121 U. S. 1", "Bain", "Miller"),
    T("w116", AB, OG, "United States v. Cobb", "476 U. S. 321", "Cobb", "Henderson"),
    T("w117", AB, OG, "United States v. Novak", "by Henderson", "Novak", "Henderson", 0.93),
    T("w118", OV, ALL, "overruled Linkletter", "479 U. S. 314", "Linkletter", "Griffith"),
    T("w119", OV, ALL, "overruled by Griffith", "388 U. S. 293", "Stovall", "Griffith", 0.85),
    T("w120", AB, ALL, "Parker v. Randolph", "481 U. S. 186", "Parker", "Cruz"),
    T("w121", OV, OG, "In re American Mariner", "484 U. S. 365", "American Mariner", "Timbers"),
    T("w122", OV, OG, "Grundy Nat. Bank", "484 U. S. 365", "Grundy", "Timbers"),
    T("w123", AB, OG, "Partlow v. Jewish", "493 U. S. 165", "Partlow", "Hoffmann-La Roche"),
    T("w124", OV, ALL, "Collins v. Youngblood", "170 U. S. 343", "Thompson v. Utah", "Collins"),
    T("w125", AB, OG, "Llaguno v. Mingey", "500 U.S. 44", "Llaguno", "County of Riverside"),
    T("w126", AB, OG, "United States v. Chadwick", "500 U. S. 565", "Chadwick", "Acevedo"),
    T("w127", OV, ALL, "California v. Acevedo", "442 U. S. 753", "Sanders", "Acevedo"),
    F("w128", "notOverruling", 0.85),
    T("w129", AB, OG, "United States v. Schneiderman", "511 U.S. 513", "Schneiderman", "Things"),
    T("w130", OV, ALL, "Johnson v. Carter", "115 S.Ct. 2227", "Johnson v. Carter", "Lamagno"),
    T("w131", AB, OG, "Toussaint v. McCarthy", "515 U.S. 472", "Toussaint", "Sandin"),
    F("w132", "otherDecision", 0.5),
    T("w133", AB, OG, "United States v. Calverley", "520 U.S. 461", "Calverley", "Johnson"),
    T("w134", AB, OG, "In re Valenti", "520 U. S. 953", "Valenti", "Rash"),
    T("w135", OV, OG, "UMC Elecs. Co.", "525 U.S. 55", "UMC", "Pfaff"),
]

P4 = [
    T("w136", OV, OG, "Bullington v. United Air Lines", "536 U.S. 101", "Bullington", "Morgan"),
    T("w137", OV, OG, "Calderon v. United States Dist. Court", "538 U. S. 202", "Calderon", "Woodford", 0.9),
    T("w138", OV, PU, "Grutter implicitly overruled", "Hopwood", "Hopwood", "Grutter", 0.9,
      doctrine="categorical prohibition"),
    T("w139", OV, ALL, "Crawford, in overruling", "Roberts", "Roberts", "Crawford", 0.92),
    T("w140", OV, ALL, "United States v. Koch", "overruled by Booker", "Koch", "Booker", 0.75),
    T("w141", AB, OG, "Agins v. City of Tiburon", "544 U. S. 528", "Agins", "Lingle"),
    T("w142", OV, PU, "Chavez-Valenzuela was partially overruled", "544 U.S. 93", "Chavez-Valenzuela", "Muehler", 0.8),
    T("w143", AB, OG, "820 F.2d 1245", "547 U.S. 250", "820 F.2d 1245", "Hartman"),
    T("w144", AB, ALL, "Poole was abrogated", "547 U. S. 250", "Poole", "Hartman", 0.7),
    T("w145", OV, OG, "Arrowhead Indus. Water", "MedImmune, 549 U.S.", "Arrowhead", "MedImmune"),
    T("w146", AB, OG, "Lum v. Bank of Am.", "by Twombly, 550 U.S.", "Lum", "Twombly"),
    T("w147", AB, OG, "Forsyth v. Fed", "550 U.S. 618", "Forsyth", "Ledbetter"),
    T("w148", AB, OG, "United States v. Williams, 456 F.3d 1353", "128 S.Ct. 558", "Williams", "Kimbrough"),
    T("w149", OV, OG, "Am. Laser Vision", "552 U.S. 576", "Laser Vision", "Hall St."),
    T("w150", OV, ALL, "Pearson v. Callahan", "533 U. S. 194", "Saucier", "Pearson"),
    T("w151", OV, ALL, "Santos v. Kolb", "130 S.Ct. 1473", "Santos", "Padilla"),
    F("w152", "notOverruling", 0.85),
    T("w153", OV, OG, "al-Kidd v. Ashcroft, 580 F.3d 949", "131 S.Ct. 2074", "580 F.3d 949", "Ashcroft v. al-Kidd"),
    T("w154", AB, OG, "United States v. Tsosie", "131 S.Ct. 2382", "Tsosie", "Tapia"),
    T("w155", AB, OG, "Untied States v. Cepero", "132 S.Ct. 641", "Cepero", "Gonzalez v. Thaler"),
    F("w156", "notMajority", 0.7),
    F("w157", "notOverruling", 0.85),
    T("w158", AB, OG, "United States v. Farrior", "575 U.S. 348", "Farrior", "Rodriguez"),
    T("w159", AB, OG, "Begay v. United States", "576 U. S. 591", "Begay", "Johnson"),
    T("w160", OV, PU, "United States v. Killip", "Musacchio v. United States", "Killip", "Musacchio", 0.9),
    T("w161", OV, PU, "United States v. Cronic", "Musacchio v. United States", "Cronic", "Musacchio", 0.9),
    T("w162", OV, PU, "United States v. Romero", "Musacchio v. United States", "Romero", "Musacchio", 0.9),
    T("w163", OV, ALL, "United States v. Hurlburt", "137 S. Ct. 886", "Hurlburt", "Beckles"),
    T("w164", AB, PU, "King v. Governor of New Jersey", "585 U. S. 755", "King v. Governor", "Becerra"),
    T("w165", OV, OG, "Ex parte Duffy", "988 S.W.2d 770", "Duffy", "Hernandez"),
    T("w166", AB, OG, "Black v. Bayer", "972 F.2d 1364", "Black v. Bayer", "Middle Bucks"),
    T("w167", OV, OG, "In re Tutu Wells", "267 F.3d 331", "Tutu Wells", "Comuso"),
    T("w168", AB, OG, "W.B. v. Matula", "Jersey City Pub. Schs., 486 F.3d", "Matula", "Jersey City"),
    F("w169", "notOverruling", 0.85),
    T("w170", AB, OG, "United States v. Grana", "Virgin Islands v. Martinez, 620 F.3d", "Grana", "Martinez"),
    T("w171", AB, OG, "United States v. Cartwright", "726 F.3d 418", "Cartwright", "Caraballo-Rodriguez"),
    T("w172", OV, ALL, "Peters v. Shreveport", "overruling Jiffy June", "Jiffy June", "Peters", 0.85),
    T("w173", AB, OG, "Jones v. Bell Helicopter", "820 F.2d 134", "Bell Helicopter", "Popovich"),
    T("w174", OV, OG, "McGill v. Goff", "20 F.3d 1362", "McGill", "Kansa"),
    T("w175", AB, OG, "Lavespere v. Niagra", "37 F.3d 1069", "Lavespere", "Liquid Air"),
    T("w176", OV, OG, "Boeing Co. v. Shipman", "107 F.3d 331", "Boeing", "Gautreaux"),
    T("w177", OV, OG, "Gordy v. Burns", "Castellano v. Fragozo, 352 F.3d", "Gordy", "Castellano"),
    T("w178", AB, OG, "United States v. Brown", "454 F.3d 468", "Brown", "Candia"),
    T("w179", OV, OG, "Demette v. Falcon", "589 F.3d 778", "Demette", "Grand Isle"),
]


def parse_pack(path):
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read().replace("\r\n", "\n")
    items = []
    for block in text.split("### ITEM ")[1:]:
        lines = block.split("\n")
        iid = lines[0].strip()
        wi = lines.index("WINDOW:")
        ni = lines.index("NOTE AT:")
        window = "\n".join(lines[wi + 1:ni])
        items.append((iid, window))
    return items


def run(pack, answers):
    items = parse_pack(os.path.join(BASE, "packs", pack + ".md"))
    ids = [i for i, _ in items]
    aids = [a["id"] for a in answers]
    assert ids == aids, (pack, [i for i in ids if i not in aids], [i for i in aids if i not in ids])
    out = []
    problems = []
    ntrue = 0
    for (iid, window), a in zip(items, answers):
        if not a["states"]:
            out.append(dict(id=iid, states=False, reason=a["reason"], kind="", scope="", field_limit="",
                            doctrine="", quote="", confidence=a["conf"]))
            continue
        s = window.find(a["start"])
        if s < 0:
            problems.append((iid, "start not found"))
            continue
        e = window.find(a["end"], s)
        if e < 0:
            problems.append((iid, "end not found"))
            continue
        q = window[s:e + len(a["end"])]
        if q not in window:
            problems.append((iid, "not substring"))
        if len(q) > 400:
            problems.append((iid, "too long %d" % len(q)))
        if "\n" in q:
            problems.append((iid, "newline in quote"))
        ql = q.lower()
        if not any(w in ql for w in WORDS):
            problems.append((iid, "no overruling word"))
        for fb in FORBID:
            if fb in ql:
                problems.append((iid, "forbidden: " + fb))
        if a["x"] not in q:
            problems.append((iid, "x missing"))
        if a["y"] not in q:
            problems.append((iid, "y missing"))
        ntrue += 1
        out.append(dict(id=iid, states=True, kind=a["kind"], scope=a["scope"], field_limit=a["field"],
                        doctrine=a["doctrine"], quote=q, confidence=a["conf"]))
    dest = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    if not problems:
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            for o in out:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    return len(items), ntrue, problems, out, dict(items)


def verify(pack, windows):
    dest = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with open(dest, "rb") as f:
        raw = f.read()
    assert b"\r" not in raw
    rows = [json.loads(l) for l in raw.decode("utf-8").split("\n") if l]
    assert [r["id"] for r in rows] == list(windows.keys())
    bad = 0
    for r in rows:
        if r["states"]:
            q = r["quote"]
            ok = q in windows[r["id"]] and len(q) <= 400 and any(w in q.lower() for w in WORDS)
            if not ok:
                bad += 1
                print("BAD", r["id"])
    return len(rows), sum(1 for r in rows if r["states"]), bad


if __name__ == "__main__":
    show = len(sys.argv) > 1
    for pack, answers in (("pack_T0_003", P3), ("pack_T0_004", P4)):
        n, nt, problems, out, windows = run(pack, answers)
        print(pack, "items", n, "true", nt, "problems", problems)
        if not problems:
            print("  verify (rows, true, bad):", verify(pack, windows))
        if show:
            for o in out:
                if o["states"]:
                    print(o["id"], len(o["quote"]), "|", o["quote"].encode("ascii", "replace").decode())
