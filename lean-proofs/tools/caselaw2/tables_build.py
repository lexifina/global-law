"""Write succession.tsv, adoption.tsv and system_rules.tsv (caselaw-lean-2, agent: courts) from research/doctrine.md.

    python tables_build.py

Every row carries src (doctrine rule id / leading authority) and tag S|L|U as doctrine.md gives it; where doctrine.md
marks a gap, the row is our best reading, tagged U. Court ids come from data/courts2.tsv (run courts2_build.py first).
"""
import collections, json, os, sys

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
DATA = os.path.join(WORK, "caselaw-lean-2", "data")
WD = os.path.join(WORK, "caselaw-lean-2", "work", "courts")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "caselaw"))
from courts_map import SYS  # noqa: E402

D = 99991231


def load():
    names = collections.defaultdict(set)
    sysof = {}
    for line in open(os.path.join(DATA, "courts2.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        names[f[3]].add(int(f[0]))
        sysof[int(f[0])] = (int(f[4]), f[5])
    keys = json.load(open(os.path.join(WD, "court_keys.json"), encoding="utf-8"))
    return names, keys, sysof


NAMES, KEYS, SYSOF = load()


def cid(x):
    if x in KEYS["cid_of"]:
        return KEYS["cid_of"][x]
    if x in KEYS["unit_id"]:
        return KEYS["unit_id"][x]
    if x in KEYS["mo_old"]:
        return KEYS["mo_old"][x]
    ids = NAMES.get(x)
    if not ids or len(ids) != 1:
        raise KeyError("court %r -> %r" % (x, ids))
    return next(iter(ids))


CIRC = {k: "United States Court of Appeals for the %s Circuit" % w for k, w in
        ((1, "First"), (2, "Second"), (3, "Third"), (4, "Fourth"), (5, "Fifth"), (6, "Sixth"), (7, "Seventh"),
         (8, "Eighth"), (9, "Ninth"), (10, "Tenth"), (11, "Eleventh"))}
CIRC[12] = "CADC"
CIRC[13] = "CAFC"

# ------------------------------------------------------------------------------------------------ succession
SUCC = [
    # old, new, date, kind, src, tag
    ("CA5", CIRC[11], 19811001, "split", "doctrine F10 (Pub. L. 96-452; 11th Cir. created 1 Oct 1981)", "S"),
    (CIRC[8], CIRC[10], 19290228, "split", "doctrine F10 (Act of 28 Feb 1929, 45 Stat. 1346)", "L"),
    ("CCPA", "CAFC", 19821001, "absorb", "doctrine F11 (Pub. L. 97-164)", "L"),
    ("CTCL", "CAFC", 19821001, "split", "doctrine F11 (appellate functions to the Fed. Cir.)", "L"),
    ("CTCL", "CFC", 19821001, "split", "doctrine F11(c) (trial division became the Claims Court)", "L"),
    ("CFC", "CFC", 19921029, "rename", "doctrine F11(c) (Claims Court -> Court of Federal Claims)", "L"),
    ("CIT", "CIT", 19801101, "rename", "doctrine F11(c) (Customs Court -> Court of International Trade)", "L"),
    ("TAX", "TAX", 19421021, "rename", "doctrine F12 (Board of Tax Appeals -> Tax Court of the United States)", "L"),
    ("TAX", "TAX", 19691230, "rename", "doctrine F12 (Article I United States Tax Court)", "L"),
    ("CADC", "CADC", 19340607, "rename", "Court of Appeals of D.C. -> U.S. Court of Appeals for D.C.", "L"),
    ("CADC", "CADC", 19480901, "rename", "-> U.S. Court of Appeals for the D.C. Circuit (Judicial Code 1948)", "L"),
    ("CAAF", "CAAF", 19941005, "rename", "Court of Military Appeals -> CAAF", "L"),
    ("CCA-ARMY", "CCA-ARMY", 19941005, "rename", "Court of Military Review -> Court of Criminal Appeals", "L"),
    ("CCA-AF", "CCA-AF", 19941005, "rename", "Court of Military Review -> Court of Criminal Appeals", "L"),
    ("CCA-NMC", "CCA-NMC", 19941005, "rename", "Court of Military Review -> Court of Criminal Appeals", "L"),
    ("CCA-CG", "CCA-CG", 19941005, "rename", "Court of Military Review -> Court of Criminal Appeals", "L"),
    ("CAVC", "CAVC", 19990301, "rename", "Court of Veterans Appeals -> CAVC", "L"),
    ("SCDC", "United States District Court for the District of Columbia", 19360618, "rename",
     "Supreme Court of D.C. renamed District Court of the U.S. for D.C. (1936; day uncertain)", "U"),
    ("DCCA", "DCCA", 19630101, "rename", "doctrine §3.2 DC; Pub. L. 87-873, 76 Stat. 1171 (approved 23 Oct 1962; effective date computed from its 60-day clause)", "U"),
    ("DCCA", "DCCA", 19710201, "rename", "doctrine §3.2 DC (becomes court of last resort, 1 Feb 1971)", "S"),
    # states
    ("AL-COA", "AL-CIV", 19691001, "split", "doctrine §4.3 AL; Act No. 987 (1969), eff. 1 Oct 1969 (verified)", "S"),
    ("AL-COA", "AL-CRIM", 19691001, "split", "Act No. 987 (1969): the former Court of Appeals became the Court of Criminal Appeals, eff. 1 Oct 1969 (verified)", "S"),
    ("CT-SC", "CT-SC", 19651230, "rename", "doctrine §3.2 CT (Supreme Court of Errors -> Supreme Court; day uncertain)",
     "U"),
    ("DE-CEA", "DE-SC", 19510101, "replace", "doctrine §3.2 DE (1951 constitutional amendment; day uncertain)", "L"),
    ("HI-REP", "HI-TERR", 19000614, "replace", "doctrine §3.2 HI (Organic Act; Republic -> Territory)", "U"),
    ("HI-TERR", "Supreme Court of the State of Hawaii", 19590821, "replace", "doctrine §3.2 HI (statehood)", "U"),
    ("KY-OLDCOA", "Supreme Court of Kentucky", 19760101, "replace", "doctrine §3.2 KY / H3 (SCR 1.030(8)(a))", "S"),
    ("MD-COA", "MD-COA", 20221214, "rename", "doctrine §3.2 MD (Court of Appeals -> Supreme Court of Maryland; verified)", "S"),
    ("MD-CSA", "MD-CSA", 20221214, "rename", "doctrine §3.2 MD (Court of Special Appeals -> Appellate Court of Maryland; verified)",
     "S"),
    ("MA-PROV", "Massachusetts Supreme Judicial Court", 17800101, "replace",
     "provincial Superior Court of Judicature -> SJC (1780 constitution; date uncertain)", "U"),
    ("High Court of Errors and Appeals of Mississippi", "Mississippi Supreme Court", 18700101, "replace",
     "doctrine §3.2 MS (1869/70)", "L"),
    ("FL-DCA|2", "FL-DCA|6", 20230101, "split", "doctrine S-FL (6th DCA effective 1 Jan 2023)", "L"),
    ("FL-DCA|2", "FL-DCA|4", 19650701, "split", "doctrine S-FL (4th DCA 1965; parent district uncertain)", "U"),
    ("FL-DCA|1", "FL-DCA|5", 19790701, "split", "doctrine S-FL (5th DCA 1979; parent districts uncertain)", "U"),
    ("MO-OLD|1", "MO-COA|1", 19720101, "absorb", "doctrine S-MO (St. Louis CoA -> Eastern District)", "L"),
    ("MO-OLD|2", "MO-COA|2", 19720101, "absorb", "doctrine S-MO (Kansas City CoA -> Western District)", "L"),
    ("MO-OLD|3", "MO-COA|3", 19720101, "absorb", "doctrine S-MO (Springfield CoA -> Southern District)", "L"),
    ("NJ-CEA", "NJ-SC", 19480915, "replace", "doctrine §3.2 NJ (1947 constitution, eff. 15 Sept 1948)", "L"),
    ("NJ-OLDSC", "NJ-AD", 19480915, "replace",
     "doctrine §3.2 NJ (old Supreme Court abolished; appellate work to the Superior Court, Appellate Division)", "U"),
    ("New Jersey Court of Chancery", "New Jersey Superior Court, Chancery Division", 19480915, "replace",
     "doctrine §3.2 NJ (Court of Chancery abolished 1948)", "L"),
    ("NY-CORR", "New York Court of Appeals", 18470705, "replace", "doctrine §3.2 NY (1846 constitution)", "L"),
    ("NY-JUD", "NY-GT", 18470705, "replace", "doctrine §3.2 NY (Supreme Court of Judicature -> Supreme Court)", "U"),
    ("NY-GT", "NY-AD", 18960101, "replace", "doctrine §3.2 NY (General Term -> Appellate Division, 1 Jan 1896)", "L"),
    ("OK-CCA", "OK-CCA", 19590101, "rename", "doctrine H2 (Criminal Court of Appeals -> Court of Criminal Appeals)", "U"),
    ("IND-TERR", "OK-SC", 19071116, "absorb", "Indian Territory courts end at Oklahoma statehood", "L"),
    ("DAK-SC", "North Dakota Supreme Court", 18891102, "split", "doctrine §3.2 ND (one-to-many succession)", "U"),
    ("DAK-SC", "South Dakota Supreme Court", 18891102, "split", "doctrine §3.2 SD", "U"),
    ("SC-OLDCOA", "Supreme Court of South Carolina", 18680101, "replace", "1868 constitution (date uncertain)", "U"),
    ("South Carolina Court of Errors", "Supreme Court of South Carolina", 18680101, "replace",
     "1868 constitution (date uncertain)", "U"),
    ("Supreme Court of Errors and Appeals of Tennessee", "Tennessee Supreme Court", 18350101, "replace",
     "1834 constitution (date uncertain)", "U"),
    ("TX-CCA", "TX-CCA", 18910801, "rename", "doctrine H2 (Court of Appeals -> Court of Criminal Appeals, 1891)", "L"),
    ("TX-COA", "TX-COA", 19810901, "rename", "doctrine S-TX (Courts of Civil Appeals -> Courts of Appeals)", "L"),
    ("TX-COMM", "TX-SC", 19450901, "absorb", "doctrine §3.2 TX (Commission of Appeals abolished 1945; day uncertain)", "U"),
    ("IN-COA", "IN-COA", 19720101, "rename", "doctrine §4.3 IN (Appellate Court -> Court of Appeals, 1971)", "U"),
    ("CA-COA", "CA-COA", 19661108, "rename", "doctrine S-CA (District Courts of Appeal -> Courts of Appeal)", "U"),
    ("VA-SC", "VA-SC", 18310101, "rename", "Court of Appeals -> Supreme Court of Appeals (1830 constitution)", "U"),
    ("VA-SC", "VA-SC", 19710701, "rename", "doctrine §3.2 VA (Supreme Court of Appeals -> Supreme Court)", "L"),
    ("PR-TA", "PR-TA", 20030701, "rename", "doctrine §4.3 PR (renamed 2003; day uncertain)", "U"),
    ("Territorial Court of the Virgin Islands", "Superior Court of the Virgin Islands", 20041029, "rename",
     "V.I. Territorial Court renamed Superior Court (2004; day uncertain)", "U"),
    ("NAV-COA", "NAV-SC", 19850101, "rename", "Navajo Nation Court of Appeals -> Supreme Court (1985)", "L"),
    ("CO-OLDCOA", "Colorado Supreme Court", 19170101, "absorb", "earlier Colorado Courts of Appeals abolished", "U"),
    ("KS-OLDCOA", "Kansas Supreme Court", 19020101, "absorb", "Kansas Court of Appeals (1895-1901) abolished", "U"),
]

# ------------------------------------------------------------------------------------------------ adoption
# adopter, source, up_to_date, filter, force, src, tag
ADOPT = [
    (CIRC[11], "CA5", 19810930, "all", "binding", "doctrine F10: Bonner v. City of Prichard, 661 F.2d 1206, 1209 (en banc)",
     "S"),
    (CIRC[11], "CA5", 19821231, "unitB", "binding", "doctrine F10: Stein v. Reynolds Sec., 667 F.2d 33 (Unit B after "
     "30 Sept 1981); end date is the last Unit B decision we model", "L"),
    (CIRC[10], CIRC[8], 19290228, "all", "persuasive", "doctrine F10: Estate of McMorris, 243 F.3d 1254, 1258 (10th Cir. "
     "not bound by pre-1929 8th Cir. law)", "S"),
    ("CAFC", "CCPA", 19820930, "all", "binding", "doctrine F11(a): South Corp. v. United States, 690 F.2d 1368 (en banc)",
     "L"),
    ("CAFC", "CTCL", 19820930, "notTrialDivision", "binding", "doctrine F11(a) (trial-division decisions excluded; "
     "not separable in the data)", "L"),
    ("DCCA", "CADC", 19710131, "all", "binding", "doctrine §3.2 DC: M.A.P. v. Ryan, 285 A.2d 310, 312 (D.C. 1971)", "S"),
    ("KY-COA", "KY-OLDCOA", 19751231, "all", "binding", "doctrine H3: SCR 1.030(8)(a) ('predecessor court')", "S"),
    ("Supreme Court of Kentucky", "KY-OLDCOA", 19751231, "all", "binding", "doctrine H3 (successor inherits)", "S"),
    ("NJ-SC", "NJ-CEA", 19480914, "all", "binding", "doctrine H3 (successor court of last resort)", "L"),
    ("New York Court of Appeals", "NY-CORR", 18470704, "all", "binding", "doctrine H3", "L"),
    ("New York Court of Appeals", "NY-COMM", 18751231, "all", "binding", "doctrine §3.2 NY / H4 (weight uncertain)", "U"),
    ("TX-SC", "TX-COMM", 19451231, "opinionAdopted", "binding", "doctrine §3.2 TX / H4: McKenzie v. Withers, 206 S.W. 503",
     "S"),
    ("TX-SC", "TX-COMM", 19451231, "holdingApproved", "binding", "doctrine H4: binding on the questions discussed only "
     "(holdingApproved); weight uncertain", "U"),
    ("TX-SC", "TX-COMM", 19451231, "judgmentAdopted", "resultOnly", "doctrine H4 (judgment adopted/approved)", "U"),
    ("TX-SC", "TX-COMM", 19451231, "none", "persuasive", "doctrine H4 (no adoption notation)", "U"),
    ("DE-SC", "DE-CEA", 19501231, "all", "binding", "doctrine H3", "L"),
    ("Mississippi Supreme Court", "High Court of Errors and Appeals of Mississippi", 18691231, "all", "binding",
     "doctrine H3", "L"),
    ("Supreme Court of the State of Hawaii", "HI-TERR", 19590820, "all", "binding",
     "doctrine §3.2 HI (territorial decisions treated as the court's own)", "U"),
    ("Supreme Court of the State of Hawaii", "HI-REP", 19000613, "all", "binding", "doctrine §3.2 HI", "U"),
    ("North Dakota Supreme Court", "DAK-SC", 18891101, "all", "binding", "doctrine §3.2 ND (Dakota Territory)", "U"),
    ("South Dakota Supreme Court", "DAK-SC", 18891101, "all", "binding", "doctrine §3.2 SD (Dakota Territory)", "U"),
    ("Supreme Court of South Carolina", "SC-OLDCOA", 18671231, "all", "binding", "doctrine H3", "U"),
    ("Supreme Court of South Carolina", "South Carolina Court of Errors", 18671231, "all", "binding", "doctrine H3", "U"),
    ("Tennessee Supreme Court", "Supreme Court of Errors and Appeals of Tennessee", 18341231, "all", "binding",
     "doctrine H3", "U"),
    ("OK-SC", "IND-TERR", 19071115, "all", "persuasive", "Indian Territory decisions after statehood (weight unknown)",
     "U"),
    ("FL-DCA|6", "FL-DCA|2", 20221231, "all", "persuasive",
     "doctrine S-FL: 6th DCA reportedly treats 2d DCA precedent as persuasive, not binding", "U"),
    ("MO-COA|1", "MO-OLD|1", 19711231, "all", "binding", "doctrine S-MO (district inherits its predecessor court)", "U"),
    ("MO-COA|2", "MO-OLD|2", 19711231, "all", "binding", "doctrine S-MO", "U"),
    ("MO-COA|3", "MO-OLD|3", 19711231, "all", "binding", "doctrine S-MO", "U"),
    ("AL-CIV", "AL-COA", 19690930, "all", "binding", "successor intermediate courts (civil)", "U"),
    ("AL-CRIM", "AL-COA", 19690930, "all", "binding", "successor intermediate courts (criminal)", "U"),
    ("Supreme Court of Puerto Rico", CIRC[1], 19610829, "issue:localLaw", "persuasiveStrong",
     "doctrine §3.2 PR (1st Cir. reviewed P.R. decisions until 30 Aug 1961; current weight uncertain)", "U"),
    ("Supreme Court of Guam", CIRC[9], 20041029, "issue:localLaw", "persuasive",
     "doctrine §3.2 GU (9th Cir. certiorari over Guam until Pub. L. 108-378)", "U"),
    ("VI-SC", CIRC[3], 20121228, "issue:localLaw", "persuasiveStrong",
     "doctrine §3.2 VI: Banks, 55 V.I. 967 (2011) (3d Cir. readings of V.I. law yield unless not manifestly erroneous)",
     "S"),
    ("Supreme Court of the United States", "Supreme Court of the United States", 0, "-", "-", "placeholder", "-"),
]

# ------------------------------------------------------------------------------------------------ system rules
ST = {a: SYS[b] for a, b in (("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"),
                             ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"), ("DE", "Delaware"),
                             ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"), ("ID", "Idaho"), ("IL", "Illinois"),
                             ("IN", "Indiana"), ("IA", "Iowa"), ("KS", "Kansas"), ("KY", "Kentucky"),
                             ("LA", "Louisiana"), ("ME", "Maine"), ("MD", "Maryland"), ("MA", "Massachusetts"),
                             ("MI", "Michigan"), ("MN", "Minnesota"), ("MS", "Mississippi"), ("MO", "Missouri"),
                             ("MT", "Montana"), ("NE", "Nebraska"), ("NV", "Nevada"), ("NH", "New Hampshire"),
                             ("NJ", "New Jersey"), ("NM", "New Mexico"), ("NY", "New York"), ("NC", "North Carolina"),
                             ("ND", "North Dakota"), ("OH", "Ohio"), ("OK", "Oklahoma"), ("OR", "Oregon"),
                             ("PA", "Pennsylvania"), ("RI", "Rhode Island"), ("SC", "South Carolina"),
                             ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"), ("UT", "Utah"),
                             ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"), ("WV", "West Virginia"),
                             ("WI", "Wisconsin"), ("WY", "Wyoming"), ("DC", "District of Columbia"),
                             ("PR", "Puerto Rico"), ("GU", "Guam"), ("VI", "Virgin Islands"), ("AS", "American Samoa"),
                             ("MP", "Northern Mariana Islands"))}
T43 = "doctrine §4.3"
# state, horizontal, trialScope, src/tag for H, src/tag for V
STATE_HV = {
    "AL": ("strong", "statewide", "Ala. R. App. P. 15 (doctrine §4.2 Other states)", "S", T43, "L"),
    "AK": ("soft", "statewide", "Joseph v. State, 293 P.3d 488 (Alaska App. 2012)", "S", T43, "L"),
    "AZ": ("soft", "statewide", "doctrine S-AZ: State v. Patterson (2009)", "S", "doctrine S-AZ (secondary)", "S"),
    "AR": ("soft", "statewide", T43 + " marks H '?'; best reading", "U", T43, "L"),
    "CA": ("none", "statewideChooseOnConflict", "doctrine S-CA (Gourley; Shaban)", "S", "doctrine S-CA: Auto Equity Sales "
           "(1962)", "L"),
    "CO": ("none", "statewide", T43 + ": 'one division is not bound by another' (C.R.S. 13-4-106; Mitchell v. Ryder)",
           "U", T43 + " ('statewide ?')", "U"),
    "CT": ("soft", "statewide", "State v. Thompson, 839 A.2d 622 (Conn. App. 2004)", "S", T43, "L"),
    "FL": ("withinUnitOnly", "ownUnitThenAny", "doctrine S-FL (State v. Hayes; Fla. R. App. P. 9.331)", "S",
           "doctrine S-FL: Pardo v. State, 596 So. 2d 665 (1992)", "S"),
    "GA": ("strong", "statewide", "doctrine S-GA (Ga. Ct. App. R. 33.2; binding test date-ranged, physical precedent)",
           "S", T43, "L"),
    "HI": ("soft", "statewide", T43 + " marks H 'soft ?'", "U", T43, "L"),
    "ID": ("soft", "statewide", "Klosterman v. Rogers, 973 P.2d 161 (Idaho App. 1999)", "S", T43, "L"),
    "IL": ("none", "ownUnitThenAny", "doctrine S-IL: O'Casek (2008); Carpenter (2008)", "L",
           "doctrine S-IL: State Farm v. Yapejian (1992)", "S"),
    "IN": ("soft", "statewide", "Leatherwood v. State, 880 N.E.2d 315 (Ind. App. 2008)", "S", T43, "L"),
    "IA": ("soft", "statewide", T43 + " marks H '?'; best reading", "U", T43, "L"),
    "KS": ("soft", "statewide", "doctrine §4.2: In re Cray (strong) vs Leben 2025 (disagree, not overrule); treat soft",
           "U", T43, "L"),
    "KY": ("strong", "statewide", "SCR 1.030(7)(d) (doctrine §4.2 Other states)", "S", T43, "L"),
    "LA": ("withinUnitOnly", "ownUnitOnly", "doctrine S-LA: Orillion v. Allstate (1997)", "S",
           "doctrine S-LA (presumed)", "U"),
    "MD": ("soft", "statewide", "Montgomery Cnty. Career Fire Fighters, 62 A.3d 287 (Md. App. 2013)", "S", T43, "L"),
    "MA": ("soft", "statewide", T43 + " (Walker n.65)", "S", T43, "L"),
    "MN": ("soft", "statewide", T43 + " marks H '?'; best reading", "U",
           T43 + " (published opinions binding on district courts on filing)", "S"),
    "MS": ("soft", "statewide", T43 + " marks H '?'; best reading", "U", T43 + " (Bevis 2003)", "S"),
    "MO": ("soft", "statewide", "doctrine S-MO: Mo. Sup. Ct. OR 22.01 (en banc within district to depart)", "S",
           "doctrine S-MO (Akins; exact wording uncertain)", "U"),
    "NE": ("soft", "statewide", T43 + " marks H '?'; best reading", "U", T43 + " (date-ranged; see rows)", "S"),
    "NV": ("soft", "statewide", T43 + " marks H '?'; best reading", "U", T43, "L"),
    "NJ": ("none", "statewideChooseOnConflict", "doctrine S-NJ: David v. GEICO (2003)", "S", "doctrine S-NJ", "L"),
    "NM": ("soft", "statewide", T43 + " marks H '?'; best reading", "U", T43 + " (McNeill 2006)", "S"),
    "NY": ("withinUnitOnly", "ownUnitThenAny", "doctrine S-NY (none across departments; within a department panels "
           "follow)", "S", "doctrine S-NY: Mountain View Coach Lines v. Storms (1984)", "S"),
    "NC": ("strong", "statewide", "In re Civil Penalty, 324 N.C. 373 (1989)", "L", T43, "L"),
    "ND": ("soft", "statewide", T43 + " marks H '?' (temporary court)", "U", T43, "L"),
    "OH": ("withinUnitOnly", "ownUnitOnly", "doctrine S-OH: State v. George (1975) (soft within, none across)", "S",
           "doctrine S-OH: Stapleton v. Holstein (1998)", "S"),
    "OK": ("strong", "statewide", "Bays Expl. v. Jones, 230 P.3d 907 (Okla. Civ. App. 2010)", "S", T43, "L"),
    "OR": ("soft", "statewide", "State v. Roberts, 172 P.3d 651 (Or. App. 2007)", "S", T43, "L"),
    "PA": ("strong", "statewide", "doctrine S-PA (strong within each court; none across Superior/Commonwealth)", "L",
           T43 + " (per subject)", "L"),
    "SC": ("soft", "statewide", T43 + " marks H '?'; best reading", "U", T43 + " (Cheeks 2012)", "S"),
    "TN": ("strong", "statewide", "Tenn. Sup. Ct. R. 4(G)(2)", "S", T43, "S"),
    "TX": ("withinUnitOnly", "ownUnitOnly", "doctrine S-TX: Owen v. Jim Allee Imports (2012); TRAP 41.3 transfer", "S",
           "doctrine S-TX ('own court ?')", "U"),
    "UT": ("soft", "statewide", "State v. Tenorio, 156 P.3d 854 (Utah App. 2007)", "S", T43, "L"),
    "VA": ("strong", "statewide", "Collins v. Commonwealth, 517 S.E.2d 277 (Va. App. 1999)", "S", T43, "L"),
    "WA": ("none", "statewideChooseOnConflict", "doctrine S-WA: In re Pers. Restraint of Arnold (2018)", "S",
           "doctrine S-WA marks V '?'; best reading", "U"),
    "WV": ("soft", "statewide", T43 + " marks H '?' (ICA from 1 July 2022)", "U", T43, "L"),
    "WI": ("strong", "statewide", "Cook v. Cook, 208 Wis. 2d 166 (1997)", "L", T43, "L"),
    "DC": ("strong", "statewide", "doctrine §4.3 DC: M.A.P. v. Ryan (divisions bound; only en banc overrules)", "S",
           T43, "S"),
    "PR": ("soft", "statewide", T43 + " marks PR '?'; best reading", "U", T43, "U"),
}
NO_IAC = ["DE", "ME", "MT", "NH", "RI", "SD", "VT", "WY", "GU", "VI", "AS", "MP"]
# unpublished force rows: state -> [(from, to, value, src, tag)]
UNPUB = {
    "AL": [(0, D, "none", "Ala. R. App. P. 53(d) (no-opinion affirmances)", "L")],
    "AK": [(0, D, "persuasive", "Alaska App. R. 214(d) (memorandum opinions not precedent)", "L")],
    "AZ": [(0, 20141231, "notCitable", "Ariz. R. Sup. Ct. 111(c)", "L"), (20150101, D, "persuasive", "R. 111(c)", "L")],
    "AR": [(0, 20090630, "notCitable", T43 + " (Sup. Ct. R. 5-2)", "U"),
           (20090701, D, "binding", T43 + " (all opinions precedential from 1 July 2009)", "U")],
    "CA": [(0, D, "notCitable", "Cal. Rules of Court 8.1115(a)", "S")],
    "CO": [(0, D, "notCitable", T43 + " (C.A.R. 35)", "U")],
    "CT": [(0, D, "persuasive", T43 + " (memorandum decisions)", "U")],
    "FL": [(0, D, "none", "Dep't of Legal Affairs v. DCA, 434 So. 2d 310 (Fla. 1983) (PCAs)", "L")],
    "GA": [(0, D, "notCitable", "Ga. Ct. App. R. 33.2(b) (unreported: neither physical nor binding)", "S")],
    "HI": [(0, 20080630, "notCitable", T43 + " (HRAP 35)", "U"), (20080701, D, "persuasive", T43 + " (HRAP 35)", "U")],
    "ID": [(0, D, "citableNoWeight", T43, "L")],
    "IL": [(0, 20201231, "notCitable", "Ill. S. Ct. R. 23(e)(1)", "S"),
           (20210101, D, "persuasive", "Ill. S. Ct. R. 23(e)(1) (Rule 23(b) orders from 1 Jan 2021)", "S")],
    "IN": [(0, 20221231, "notCitable", "Ind. App. R. 65(D)", "S"), (20230101, D, "persuasive", "Ind. App. R. 65(D)", "S")],
    "IA": [(0, D, "persuasive", "Iowa R. App. P. 6.904(2)(c)", "L")],
    "KS": [(0, D, "persuasive", "Kan. Sup. Ct. R. 7.04", "L")],
    "KY": [(0, 20021231, "notCitable", T43 + " (RAP 41)", "U"), (20030101, D, "persuasive", T43 + " (RAP 41)", "U")],
    "LA": [(0, D, "persuasive", "no rule in doctrine.md; best reading", "U")],
    "MD": [(0, 20230630, "notCitable", "Md. Rule 1-104", "S"),
           (20230701, D, "persuasive", "Md. Rule 1-104 (if no reported authority; per curiam excluded)", "S")],
    "MA": [(0, 20080224, "citableNoWeight", T43 + " (Rule 1:28 before Chace v. Curran)", "U"),
           (20080225, D, "memorandum:persuasive", "Chace v. Curran, 71 Mass. App. Ct. 258 (2008)", "L"),
           (20080225, D, "persuasive", "Rule 23.0 (formerly 1:28)", "L")],
    "MI": [(0, D, "persuasive", "MCR 7.215(C)(1)", "L")],
    "MN": [(0, D, "persuasive", "Minn. Stat. § 480A.08(3)", "S")],
    "MS": [(0, D, "persuasive", "no rule in doctrine.md; best reading", "U")],
    "MO": [(0, D, "notCitable", "no rule in doctrine.md; best reading (unpublished orders)", "U")],
    "NE": [(0, D, "persuasive", "no rule in doctrine.md; best reading", "U")],
    "NV": [(0, 20151231, "notCitable", "NRAP 36(c)(3)", "L"), (20160101, D, "persuasive", "NRAP 36(c)(3)", "L")],
    "NJ": [(0, D, "citableNoWeight", "N.J. R. 1:36-3", "L")],
    "NM": [(0, D, "persuasive", "N.M. R. App. P. 12-405", "L")],
    "NY": [(0, D, "persuasive", "no unpublished channel in doctrine.md; best reading", "U")],
    "NC": [(0, D, "persuasive", "N.C. R. App. P. 30(e)(3)", "L")],
    "ND": [(0, D, "persuasive", "no rule in doctrine.md; best reading", "U")],
    "OH": [(0, 20020430, "persuasive", "doctrine S-OH (weight of unreported opinions before 2002 varied)", "U"),
           (20020501, D, "binding", "doctrine S-OH (Rep.Op.R.: all opinions citable from 1 May 2002)", "U")],
    "OK": [(0, D, "notCitable", "Okla. Sup. Ct. R. 1.200 (published COCA opinions are themselves only persuasive)", "S")],
    "OR": [(0, D, "persuasive", "no rule in doctrine.md; best reading", "U")],
    "PA": [(0, 20190430, "notCitable", "Pa.R.A.P. 126(b) (Superior Court)", "S"),
           (20190501, D, "persuasive", "Pa.R.A.P. 126(b) (Superior Court memoranda after 1 May 2019)", "S")],
    "SC": [(0, D, "citableNoWeight", "SCACR 268(d)(2)", "L")],
    "TN": [(0, D, "persuasive", "Tenn. Sup. Ct. R. 4(G)(1)", "S")],
    "TX": [(0, 20021231, "notCitable", "TRAP 47.7 (older 'do not publish' civil opinions)", "L"),
           (20030101, D, "citableNoWeight", "TRAP 47.7(a) (criminal 'do not publish'; civil memorandum opinions are "
            "published)", "L"), (20030101, D, "memorandum:binding", "TRAP 47.7(b) (civil memorandum opinions)", "L")],
    "UT": [(0, D, "persuasive", T43 + " ('limited')", "U")],
    "VA": [(0, D, "persuasive", "Va. R. 5A:1(f)", "L")],
    "WA": [(0, 20130228, "notCitable", "GR 14.1", "L"), (20130301, D, "persuasive", "GR 14.1", "L")],
    "WV": [(0, D, "memorandum:persuasive", "State v. McKinley, 234 W. Va. 143 (2014) (R.A.P. 21 memorandum decisions)",
            "L"), (0, D, "persuasive", "best reading", "U")],
    "WI": [(0, 20090630, "notCitable", "Wis. Stat. § 809.23(3)", "L"),
           (20090701, D, "persuasive", "Wis. Stat. § 809.23(3) (authored opinions)", "L")],
    "DC": [(0, D, "persuasive", "no rule in doctrine.md; best reading", "U")],
    "PR": [(0, D, "persuasive", "no rule in doctrine.md; best reading", "U")],
}
COURT_UNPUB = {  # court-level overrides
    "Commonwealth Court of Pennsylvania": [(0, 20080114, "notCitable", "Pa.R.A.P. 126(b)", "S"),
                                           (20080115, D, "persuasive", "Pa.R.A.P. 126(b) (after 15 Jan 2008)", "S")],
    "TAX": [(0, D, "memorandum:persuasive", "doctrine F12 (memorandum and summary opinions not precedential)", "L")],
}
FOLLOW = {"ME": ("binding", "Littlefield v. State, 480 A.2d 731, 737 (Me. 1984) (Walker)", "U"),
          "NH": ("binding", "Desmarais v. Joy Mfg., 538 A.2d 1218, 1220 (N.H. 1988) (Walker)", "U"),
          "SD": ("binding", "Cloud v. Leapley, 521 N.W.2d 118, 122 (S.D. 1994) (Walker)", "U"),
          "NE": ("binding", "Anderson v. HMO Neb., 1993 WL 61839 (Neb. Ct. App.) (Walker; intermediate court)", "U"),
          "SC": ("persuasiveStrong", "one 2013 SC Court of Appeals statement that 4th Cir. binds (contested)", "U"),
          "TN": ("persuasiveStrong", "historical Fourth Amendment carve-out (Walker)", "U")}
# federal circuits: horizontal, firstInTime, circulation, enBancVacates
FED = {
    1: ("strong", ("1", "U", "doctrine F7 table marks conflicting panels [U]"), ("1", "U", "doctrine F7 (1st Cir. may "
        "circulate before departing) [U]"), ("1", "U", "best reading (1st Cir. R. 35)")),
    2: ("strong", ("1", "U", "doctrine F7 [U]"), ("1", "L", "doctrine F7 'mini en banc' (Jaldhi; Parkes)"),
        ("0", "U", "best reading")),
    3: ("strong", ("1", "L", "Holland v. N.J. Dep't of Corr., 246 F.3d 267, 278 n.8"), ("0", "U", "best reading"),
        ("1", "L", "3d Cir. I.O.P. 9.5.9")),
    4: ("strong", ("1", "L", "McMellon v. United States, 387 F.3d 329, 333 (en banc)"), ("0", "U", "best reading"),
        ("1", "L", "4th Cir. R. 35(c)")),
    5: ("strong", ("1", "L", "Rios v. City of Del Rio, 444 F.3d 417, 425 n.8"), ("0", "U", "best reading"),
        ("1", "L", "5th Cir. R. 41.3")),
    6: ("strong", ("1", "L", "Darrah v. City of Oak Park, 255 F.3d 301, 309-10"), ("0", "U", "best reading"),
        ("1", "U", "6th Cir. R. 35(b) (now under FRAP 40)")),
    7: ("soft", ("1", "U", "doctrine F7 [U]"), ("1", "S", "7th Cir. R. 40(e) (Walker n.54)"), ("1", "U", "best reading")),
    8: ("strong", ("1", "L", "Mader v. United States, 654 F.3d 794, 800 (en banc)"), ("0", "U", "best reading"),
        ("1", "U", "best reading")),
    9: ("strong", ("1", "U", "doctrine F7 [U]"), ("0", "U", "best reading"),
        ("1", "U", "9th Cir. Gen. Order 5.5(d) (panel opinion not citable)")),
    10: ("strong", ("1", "U", "doctrine F7 [U]"), ("1", "L", "en banc footnote: United States v. Meyers, 200 F.3d 715, "
         "721 n.3"), ("1", "L", "10th Cir. R. 35.6")),
    11: ("strong", ("1", "S", "United States v. Dixon, 901 F.3d 1322, 1347 (quoting Dailey)"), ("0", "U", "best reading"),
         ("1", "L", "11th Cir. R. 35-11")),
    12: ("strong", ("1", "U", "doctrine F7 [U]"), ("1", "L", "Irons v. Diamond, 670 F.2d 265, 268 n.11"),
         ("1", "U", "best reading")),
    13: ("strong", ("1", "L", "Newell Cos. v. Kenney Mfg., 864 F.2d 757, 765"), ("0", "U", "best reading"),
         ("1", "U", "best reading")),
}
FED_H_SRC = {7: ("De Leon Castellanos v. Holder, 652 F.3d 762, 765; Russ v. Watts, 414 F.3d 783, 788", "S")}
FED_UNPUB = {  # circuit -> [(from, to, value, src, tag)]
    1: [(0, D, "persuasive", "1st Cir. R. 32.1.0(a)", "L")],
    2: [(0, 20061231, "notCitable", "2d Cir. R. 32.1.1 (formerly § 0.23)", "S"),
        (20070101, D, "citableNoWeight", "2d Cir. R. 32.1.1 (summary orders: no precedential effect)", "S")],
    3: [(0, D, "persuasive", "3d Cir. I.O.P. 5.7", "S")],
    4: [(0, 20061231, "citableNoWeight", "4th Cir. R. 32.1 (pre-2007 disfavored)", "S"),
        (20070101, D, "persuasive", "4th Cir. R. 32.1", "L")],
    5: [(0, 19951231, "binding", "5th Cir. R. 47.5.3 (unpublished before 1 Jan 1996 are precedent)", "S"),
        (19960101, D, "persuasive", "5th Cir. R. 47.5.4", "S")],
    6: [(0, D, "persuasive", "6th Cir. R. 32.1(b)", "L")],
    7: [(0, 20061231, "notCitable", "7th Cir. R. 32.1(b), (d)", "S"),
        (20070101, D, "persuasive", "7th Cir. R. 32.1(b) ('orders are not precedents')", "S")],
    8: [(0, 20061231, "citableNoWeight", "8th Cir. R. 32.1A", "S"), (20070101, D, "persuasive", "8th Cir. R. 32.1A", "S")],
    9: [(0, 20061231, "notCitable", "9th Cir. R. 36-3", "S"), (20070101, D, "persuasive", "9th Cir. R. 36-3", "S")],
    10: [(0, D, "persuasive", "10th Cir. R. 32.1(A)", "S")],
    11: [(0, D, "persuasive", "11th Cir. R. 36-2", "S")],
    12: [(0, 20011231, "notCitable", "D.C. Cir. R. 32.1(b)(1)", "S"),
         (20020101, D, "persuasiveStrong", "D.C. Cir. R. 32.1(b)(1)(B) ('may be cited as precedent') vs R. 36(e)(2)", "U")],
    13: [(0, 20061231, "citableNoWeight", "Fed. Cir. R. 32.1(d) (pre-2007 discouraged)", "S"),
         (20070101, D, "persuasive", "Fed. Cir. R. 32.1(d)", "S")],
}


def main():
    def resolve(x):
        return cid(x) if isinstance(x, str) else x
    n = 0
    with open(os.path.join(DATA, "succession.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for old, new, date, kind, src, tag in SUCC:
            f.write("\t".join(str(x) for x in (resolve(old), resolve(new), date, kind, src, tag)) + "\n")
            n += 1
    print("succession", n)
    n = 0
    with open(os.path.join(DATA, "adoption.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for a, s, upto, flt, force, src, tag in ADOPT:
            if src == "placeholder":
                continue
            f.write("\t".join(str(x) for x in (resolve(a), resolve(s), upto, flt, force, src, tag)) + "\n")
            n += 1
    print("adoption", n)
    rows = []
    for st, sysid in ST.items():
        if st in STATE_HV:
            h, v, hs, ht, vs, vt = STATE_HV[st]
            if st == "MI":
                pass
            rows.append((sysid, "horizontal", h, 0, D, hs, ht))
            if st == "NE":
                rows.append((sysid, "trialScope", v, 0, 19960218, "Nebraska: statewide before Metro Renovation", "S"))
                rows.append((sysid, "trialScope", v, 20070921, D, "State v. Nelson, 739 N.W.2d 199 (Neb. 2007) restored "
                             "vertical force (1996-2007 gap: published CoA decisions declared non-binding)", "S"))
            else:
                rows.append((sysid, "trialScope", v, 0, D, vs, vt))
        for a, b, val, src, tag in UNPUB.get(st, []):
            rows.append((sysid, "unpubForce", val, a, b, src, tag))
        val, src, tag = FOLLOW.get(st, ("persuasive", "doctrine E3 (Johnson v. Williams; Walker ¶23): state courts "
                                        "bound only by SCOTUS on federal law", "S" if st not in NO_IAC + ["DC", "PR"]
                                        else "L"))
        rows.append((sysid, "stateFollowsCircuit", val, 0, D, src, tag))
        if st in NO_IAC:
            rows.append((sysid, "horizontal", "none", 0, D, "no intermediate appellate court (doctrine §4.3); trial "
                         "courts do not bind each other (§4.4)", "L"))
    mi = ST["MI"]
    rows.append((mi, "horizontal", "soft", 0, 19901031, "MCR 7.215(J)(1): published opinions before 1 Nov 1990 do not "
                 "bind later panels (keyed on the precedent's date)", "S"))
    rows.append((mi, "horizontal", "strong", 19901101, D, "MCR 7.215(J)(1) (conflict panel, J(3)-(5))", "S"))
    rows.append((mi, "trialScope", "statewide", 0, D, "doctrine S-MI", "S"))
    rows.append((mi, "circulationCountsAsEnBanc", "0", 0, D, "Michigan uses the conflict-panel procedure instead", "S"))
    # Missouri / Florida / Georgia court-level procedures
    rows.append((ST["FL"], "enBancGrantVacatesPanel", "0", 0, D, "best reading (Fla. R. App. P. 9.331)", "U"))
    for name, rr in COURT_UNPUB.items():
        c = cid(name)
        for a, b, val, src, tag in rr:
            rows.append((-c, "unpubForce", val, a, b, src, tag))
    # federal circuits (court-level rows; system = -court_id)
    for k, (h, fit, circ, vac) in FED.items():
        c = cid(CIRC[k])
        hs, ht = FED_H_SRC.get(k, ("doctrine F7 (Walker 2022 nn.50-54)", "S"))
        rows.append((-c, "horizontal", h, 0, D, hs, ht))
        rows.append((-c, "firstInTimeControls", fit[0], 0, D, fit[2], fit[1]))
        rows.append((-c, "circulationCountsAsEnBanc", circ[0], 0, D, circ[2], circ[1]))
        rows.append((-c, "enBancGrantVacatesPanel", vac[0], 0, D, vac[2], vac[1]))
        for a, b, val, src, tag in FED_UNPUB[k]:
            rows.append((-c, "unpubForce", val, a, b, src, tag))
    # the federal system as a whole
    rows.append((0, "horizontal", "none", 0, D, "doctrine F13: district courts do not bind themselves or each other "
                 "(Camreta v. Greene, 563 U.S. 692, 709 n.7)", "L"))
    rows.append((-cid("Supreme Court of the United States"), "horizontal", "soft", 0, D,
                 "doctrine F1/H1: the Supreme Court may overrule its own precedent", "L"))
    for name, k in (("United States Bankruptcy Appellate Panel for the First Circuit", 1),
                    ("United States Bankruptcy Appellate Panel for the Sixth Circuit", 6),
                    ("United States Bankruptcy Appellate Panel for the Eighth Circuit", 8),
                    ("United States Bankruptcy Appellate Panel for the Ninth Circuit", 9),
                    ("United States Bankruptcy Appellate Panel for the Tenth Circuit", 10)):
        try:
            c = cid(name)
        except KeyError:
            continue
        rows.append((-c, "horizontal", "soft", 0, D, "doctrine F13: BAP panels treat earlier BAP decisions as "
                     "near-binding", "U"))
    with open(os.path.join(DATA, "system_rules.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    print("system_rules", len(rows))


if __name__ == "__main__":
    main()
