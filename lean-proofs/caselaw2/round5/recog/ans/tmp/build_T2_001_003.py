# -*- coding: utf-8 -*-
"""Build and verify answers for pack_T2_001..003 (reader judgments are hard-coded below)."""
import io, json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PACKS = os.path.join(BASE, "packs")
ANS = os.path.join(BASE, "ans")
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
BANNED = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "argu", "contend", "urge",
          "dissent", "question", "doubt"]


def T(kind, scope, start, end, conf, fl="", doc=""):
    return dict(states=True, kind=kind, scope=scope, start=start, end=end, conf=conf, fl=fl, doc=doc)


def F(reason, conf):
    return dict(states=False, reason=reason, conf=conf)


A = {}
A["pack_T2_001"] = {
    "r167672": T("overruled", "all", "Chappell v. State", "Ryal v. State", 0.95),
    "r124849": T("overruled", "all", "United States v. Fimmano", "United States v. Stuckey", 0.95),
    "r153575": T("overruled", "partialUnknown", "State v. Humphrey", "State v. Hardy", 0.95,
                 fl="in so far as it purported to define the elements necessary for proof of the corpus delicti"),
    "r159549": T("overruled", "all", "Landi v. Gray", "overruled by Aubrey", 0.9),
    "r153632": T("overruled", "all", "Stubblefield v. Fed. Res. Bank", "Marquardt v. Kansas City Southern Railway Co.", 0.95),
    "r187667": T("abrogated", "all", "State v. Ross", "State v. Bond", 0.95),
    "r143570": T("overruled", "all", "Langley v. Langley", "Shapiro v. Shapiro", 0.9),
    "r186055": T("overruled", "all", "Burns was specifically overruled", "Martin v. State", 0.95),
    "r151617": T("overruled", "all", "Williams v. Clay County", "Easterling", 0.9),
    "r128188": T("disapproved", "all", "Taylor v. State", "Franklin v. State", 0.9),
    "r108722": T("disapproved", "otherGrounds", "J. A. Thompson & Sons", "Cross v. Pacific Gas & Elec. Co.", 0.85),
    "r108980": T("disapproved", "otherGrounds", "J.A. Thompson & . Sons", "Cross v. Pacific Gas & Elec. Co.", 0.55),
    "r135853": T("disapproved", "partialUnknown", "Rhoades v. State", "disapproving of Snowe", 0.9,
                 fl="[t]o the extent that the court in Snowe applied the [wrong] standard of review"),
    "r147091": F("otherDecision", 0.55),
    "r136945": T("disapproved", "all", "Harrington v. State", "Cook v. State", 0.95),
    "r139246": T("overruled", "all", "State v. Davis", "overruled by Ford", 0.9),
    "r136823": F("notOverruling", 0.9),
    "r154989": T("overruled", "all", "Marvin v. Weider", "Perry v. Baker", 0.9),
    "r150491": T("overruled", "all", "Lee v. Miss. Dep't of Transp.", "Little v. Miss. Dep't of Transp.", 0.95),
    "r151234": F("cannotTell", 0.55),
    "r190276": T("disapproved", "partialUnknown", "State v. Perry", "State v. Musgrave", 0.75,
                 fl="its form, as there given"),
    "r120346": T("overruled", "all", "Smith v. State, 991 A.2d 1169", "Brooks v. State", 0.95),
    "r120351": T("overruled", "all", "Smith v. State, 991 A.2d 1169", "overruled by Brooks", 0.95),
    "r168248": F("notOverruling", 0.95),
    "r167886": F("otherDecision", 0.9),
    "r3783": F("otherDecision", 0.85),
    "r136414": F("otherDecision", 0.9),
    "r192892": T("overruled", "all", "McGinnis v. State", "Elliott v. State", 0.95),
    "r114754": T("disapproved", "all", "Stalcup v. Superior Court", "People v. Dixon", 0.7),
    "r136548": F("otherDecision", 0.85),
    "r114392": F("question", 0.55),
    "r172587": T("abrogated", "all", "Commonwealth v. Copenhefer", "Commonwealth v. Rizzuto", 0.95),
    "r144378": F("negation", 0.9),
    "r109964": T("disapproved", "all", "Vega v. Western Employers Ins. Co.", "Moradi-Shalal", 0.95),
    "r145935": T("overruled", "all", "Cook’s Case", "Colarullo’s Case", 0.6),
    "r155975": T("recededFrom", "all", "Sturrock v. State", "Lisle v. State", 0.6),
    "r189449": F("argument", 0.95),
    "r142140": T("overruled", "all", "State ex rel. Ikerd v. Judge", "Hollingsworth & Jackson", 0.9),
    "r136742": T("overruled", "partialUnknown", "Fritz v. State", "Woodworth v. State", 0.85, fl="reasoning"),
    "r169650": T("overruled", "all", "Peterson v. State Ind. Acc. Comm.", "Eggiman", 0.9),
    "r155526": T("overruled", "all", "94 Nev. 212, 577 P.2d 867 (1978)", "overruled by Braunstein", 0.9),
    "r155560": T("overruled", "all", "Findley v. State", "Braunstein v. State", 0.95),
    "r153487": T("overruled", "all", "Carpenter v. McDavitt & Cottingham", "Haymaker & Crookshanks v. Adams & Son", 0.95),
    "r190715": F("otherDecision", 0.9),
    "r136407": F("otherDecision", 0.65),
    "r142139": F("otherDecision", 0.9),
    "r128420": T("recededFrom", "all", "H & F Land, Inc.", "receded from by Blanton", 0.9),
    "r193402": T("overruled", "all", "Byrnes v. Harper", "overruled by Essex", 0.95),
    "r80565": T("overruled", "otherGrounds", "United States v. Baldwin", "United States v. Parker", 0.9,
                fl="in unrelated part"),
}
A["pack_T2_002"] = {
    "r139985": T("overruled", "all", "Ingram v. Commonwealth", "Commonwealth v. Burge", 0.95),
    "r151591": T("overruled", "all", "City of Pascagoula v. Tomlinson", "Easterling", 0.95),
    "r166254": F("argument", 0.95),
    "r3749": T("overruled", "all", "Briggs v. T. C. I. Co.", "L. & N. v. Handley, 174 Ala. 593", 0.9),
    "r6612": T("disapproved", "all", "Salaz v. City of Tucson", "State ex rel. Miller", 0.85),
    "r10491": T("disapproved", "all", "In re H & W Enterprises, Inc.", "Johnson v. First National Bank of Montevideo", 0.9),
    "r109017": T("disapproved", "otherGrounds", "Freeman v. Donohoe", "Jefferson v. J. E. French Co.", 0.9),
    "r136603": T("overruled", "all", "State, ex rel., v. Boice", "Walsh v. State", 0.95),
    "r136605": T("overruled", "all", "State, ex rel., v. Boice", "Walsh v. State", 0.6),
    "r115118": T("overruled", "all", "150 Cal.App.3d 865", "39 Cal.App.4th 1007", 0.85),
    "r136712": T("disapproved", "all", "Lockridge v. State", "Pointon v. State", 0.9),
    "r116694": T("disapproved", "all", "People v. Orona", "People v. Harlan", 0.95),
    "r3860": F("argument", 0.95),
    "r139955": T("disapproved", "partialUnknown", "Hammershoy v. Commonwealth", "Cleaver v. Commonwealth", 0.5),
    "r137847": T("abrogated", "partialUnknown", "530 N.W.2d 678", "Wells Dairy", 0.9,
                 fl="to the extent they adopted something other than the following test for work product"),
    "r186533": T("overruled", "all", "Clewis v. State", "Brooks v. State", 0.95),
    "r169517": T("abrogated", "partialUnknown", "State v. Moore, 247 Or App 39", "Moore II, 354 Or 493", 0.65),
    "r161829": T("overruled", "all", "State v. Gonzales", "147 N.M. 45", 0.9),
    "r173573": F("otherDecision", 0.9),
    "r172676": T("overruled", "all", "Commonwealth v. Davenport", "Commonwealth v. Perez", 0.9),
    "r172756": T("overruled", "all", "Commonwealth v. Davenport", "Commonwealth v. Perez", 0.95),
    "r190213": T("abrogated", "all", "Gaeta v. Seattle City Light", "Jewels v. City of Bellingham", 0.95),
    "r139616": F("otherDecision", 0.9),
    "r139626": F("otherDecision", 0.9),
    "r166205": T("overruled", "all", "State v. Perry", "State v. Mumford", 0.9),
    "r114150": T("overruled", "all", "Royal Insurance Co. v. Mazzei", "26 Cal.2d 213", 0.95),
    "r133492": F("otherDecision", 0.85),
    "r134848": T("abrogated", "all", "People v. Cole", "People v. Grabbe", 0.9),
    "r167179": T("overruled", "partialUnknown", "Bradley v. Mansfield Rapid Transit", "Bahm v. Pittsburgh & Lake Erie Rd. Co.", 0.9,
                 fl="partially"),
    "r128199": T("disapproved", "all", "Fidelity and Cas. Ins. Co. v. Taylor", "Kujawa, 541 So.2d 1168", 0.9),
    "r186018": F("otherDecision", 0.6),
    "r134039": F("otherDecision", 0.95),
    "r153548": F("otherDecision", 0.9),
    "r153927": T("abrogated", "all", "Hutchison v. State", "Mallow v. State", 0.9),
    "r138519": T("overruled", "all", "Prendiville v. Contemporary Homes, Inc.", "David v. Hett", 0.7),
    "r138988": T("overruled", "all", "Prendiville v. Contemporary Homes, Inc.", "overruled by David", 0.95),
    "r4247": T("overruled", "all", "Consolidated Stores, Inc. v. Gargis", "Bleier v. Wellington Sears Co.", 0.8),
    "r121818": T("overruled", "all", "United States v. Burton", "United States v. McCallister", 0.6),
    "r80414": T("overruled", "all", "Santos v. Kolb", "Padilla v. Kentucky", 0.95),
    "r111229": F("otherDecision", 0.95),
    "r145288": T("overruled", "all", "Stevenson v. Balt. Baseball Club, Inc.", "Marchesi, 283 Md. 131", 0.95),
    "r138708": T("overruled", "all", "State v. Moffitt", "State v. Underwood", 0.95),
    "r133584": T("overruled", "all", "Colligan v. Cousar", "Graham v. General U.S. Grant Post No. 2665", 0.9),
    "r6933": T("overruled", "all", "Pierce v. Phelps Dodge Corp.", "Matter of Mitchell, 61 Ariz. 436", 0.9),
    "r112807": F("argument", 0.95),
    "r115227": F("negation", 0.9),
    "r147047": F("question", 0.95),
    "r139156": T("abrogated", "all", "State v. Kirkpatrick", "abrogated by Sampson", 0.9),
    "r110436": T("overruled", "partialUnknown", "Hurtado v. Statewide Home Loan Co.", "44 Cal.3d 474", 0.9,
                 fl="on this very point"),
}
A["pack_T2_003"] = {
    "r154992": T("disapproved", "partialUnknown", "Walker v. Klopp", "Stevens v. Luther", 0.9,
                 doc="violation of statutory provisions is negligence as a matter of law"),
    "r135350": T("overruled", "all", "People v. Walden", "People v. Sharpe", 0.9),
    "r7477": T("disapproved", "all", "La Tourette v. La Tourette", "Mortensen v. Knight", 0.9),
    "r139692": F("cannotTell", 0.6),
    "r132763": T("abrogated", "all", "State v. Woolery", "Missouri v. McNeely", 0.9),
    "r137067": T("overruled", "partialUnknown", "Comstock v. City of Eagle Grove", "Koontz v. City of Centerville", 0.75,
                 fl="The dictum to the contrary"),
    "r28365": F("notMajority", 0.6),
    "r114461": T("overruled", "all", "People v. Hartman", "172 Cal. 762", 0.8),
    "r131220": T("disapproved", "all", "Mobley v. State, 262 Ga. 808", "265 Ga. 292", 0.9),
    "r145243": T("abrogated", "all", "Leizear v. Butler", "Broadloom Rugs, Inc.", 0.9),
    "r114394": T("overruled", "all", "Ex parte Bernert", "Ex parte Joseph Reed", 0.6),
    "r138218": T("abrogated", "all", "State v. Tonn", "State v. Hagen", 0.9),
    "r153442": T("overruled", "otherGrounds", "Thomas and Thomas v. Relfe", "Lessing v. Vertrees", 0.8),
    "r139705": F("question", 0.95),
    "r167433": F("otherDecision", 0.95),
    "r52285": T("abrogated", "all", "In re Najafi", "310 F.3d 308", 0.9),
    "r108354": T("disapproved", "otherGrounds", "Marin v. City of San Rafael", "Bunch v. Coachella Valley Water Dist.", 0.9),
    "r142162": F("argument", 0.9),
    "r156073": T("recededFrom", "all", "Michelsen v. Harvey", "receded from in Horgan", 0.9),
    "r186076": T("overruled", "all", "Childs v. State", "Ward v. State", 0.95),
    "r114258": F("question", 0.7),
    "r130810": F("negation", 0.9),
    "r114430": T("disapproved", "partialUnknown", "Warren v. Warren", "Foster v. Foster", 0.9,
                 fl="a similar statement in"),
    "r114374": T("disapproved", "all", "Yoakam v. White", "Brodribb v. Tibbets", 0.7),
    "r167977": F("otherDecision", 0.55),
    "r5457": F("otherDecision", 0.9),
    "r169694": T("overruled", "partialUnknown", "McConnell v. Herron", "264 Or 447", 0.95, fl="in this respect"),
    "r134036": T("disapproved", "all", "People v. Garcia", "People v. Lucente", 0.9),
    "r104486": T("overruled", "all", "Schencks v. United States", "Brinegar v. United States", 0.9),
    "r185970": F("negation", 0.9),
    "r157897": T("overruled", "all", "Flaherty v. Safran", "overruled by Johnson, supra, 376 N.J.Super.", 0.95),
    "r173549": T("abrogated", "all", "325 S.C. 367", "Carolina Marine Handling, Inc. v. Lasch", 0.9),
    "r145037": T("overruled", "all", "Cohn v. Cohn", "overruled by Frey v. Frey", 0.95),
    "r137280": T("overruled", "partialUnknown", "State v. Rojas-Cardona", "State v. Hogrefe", 0.9,
                 fl="on issue of what evidence can prove deception"),
    "r165419": T("overruled", "all", "State v. Foust", "State v. Diaz", 0.85),
    "r107190": T("overruled", "partialUnknown", "Continental III. Nat", "Komatsu Mfg. Co. v. United States", 0.9,
                 fl="interest judgment"),
    "r190270": F("otherDecision", 0.9),
    "r175545": T("overruled", "all", "Wofford v. Scott", "McCarthan v. Director of Goodwill Industries", 0.95),
    "r168632": F("negation", 0.85),
    "r165297": T("overruled", "all", "State v. Jarrette", "Woodson v. North Carolina", 0.9),
    "r137591": T("overruled", "all", "State v. Stallings", "State v. Feregrino", 0.95),
    "r119158": F("otherDecision", 0.9),
    "r157660": F("argument", 0.85),
    "r51190": T("overruled", "all", "Baumgartner v. Harrisburg Hous. Auth.", "overruled by Buckhannon", 0.95),
    "r147213": T("overruled", "all", "People v Newsome", "400 Mich 253", 0.95),
    "r169626": T("overruled", "partialUnknown", "Farrell v. Port of Portland", "Port of Astoria", 0.9,
                 doc="doctrine taught by Farrell v. Port of Portland"),
    "r117569": T("abrogated", "all", "41 P.3d 666", "abrogated by Esparza", 0.9),
    "r158158": F("otherDecision", 0.95),
    "r185247": F("otherDecision", 0.9),
}


def parse_pack(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read().replace("\r\n", "\n")
    items = []
    for block in re.split(r"(?m)^### ITEM ", text)[1:]:
        lines = block.split("\n")
        iid = lines[0].strip()
        wi = lines.index("WINDOW:")
        ni = lines.index("NOTE AT:")
        window = "\n".join(lines[wi + 1:ni])
        head = "\n".join(lines[1:wi])
        items.append((iid, window, head))
    return items


def span(window, start, end):
    best = None
    i = window.find(start)
    while i != -1:
        j = window.find(end, i + len(start) if end != start else i)
        if j != -1:
            q = window[i:j + len(end)]
            if OVR.search(q) and (best is None or len(q) < len(best)):
                best = q
        i = window.find(start, i + 1)
    return best


def main():
    ok = True
    for pack, answers in sorted(A.items()):
        items = parse_pack(os.path.join(PACKS, pack + ".md"))
        ids = [i for i, _, _ in items]
        if ids != list(answers.keys()):
            ok = False
            print("ORDER/ID MISMATCH", pack, [x for x in ids if x not in answers], [x for x in answers if x not in ids])
            if set(ids) != set(answers):
                continue
        out = []
        for iid, window, head in items:
            a = answers[iid]
            if a["states"]:
                q = span(window, a["start"], a["end"])
                if q is None:
                    ok = False
                    print("NO SPAN", pack, iid, a["start"], "|", a["end"])
                    q = ""
                row = dict(id=iid, states=True, kind=a["kind"], scope=a["scope"], field_limit=a["fl"],
                           doctrine=a["doc"], quote=q, confidence=a["conf"])
                if a["fl"] and a["fl"] not in window:
                    ok = False
                    print("FIELD LIMIT NOT IN WINDOW", pack, iid, a["fl"])
            else:
                row = dict(id=iid, states=False, reason=a["reason"], kind="", scope="", field_limit="",
                           doctrine="", quote="", confidence=a["conf"])
            out.append(row)
        dest = os.path.join(ANS, "ans_" + pack + ".jsonl")
        with io.open(dest, "w", encoding="utf-8", newline="\n") as f:
            for row in out:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        # verify from the written file
        with io.open(dest, "r", encoding="utf-8", newline="") as f:
            raw = f.read()
        assert "\r" not in raw
        rows = [json.loads(l) for l in raw.split("\n") if l]
        assert [r["id"] for r in rows] == ids, pack
        wmap = {i: w for i, w, _ in items}
        ntrue = 0
        for r in rows:
            if not r["states"]:
                continue
            ntrue += 1
            q, a = r["quote"], answers[r["id"]]
            probs = []
            if not q or q not in wmap[r["id"]]:
                probs.append("not substring")
            if len(q) > 400:
                probs.append("len %d" % len(q))
            if not OVR.search(q):
                probs.append("no overruling word")
            if a["start"] not in q or a["end"] not in q:
                probs.append("anchor missing")
            ban = [b for b in BANNED if b in q.lower()]
            if probs:
                ok = False
            if probs or ban or "-v" in sys.argv:
                print(pack, r["id"], len(q), probs, "BANNED:%s" % ban if ban else "")
                print("   ", q)
        print("%s: items=%d true=%d" % (pack, len(rows), ntrue))
    print("ALL OK" if ok else "PROBLEMS")


if __name__ == "__main__":
    main()
