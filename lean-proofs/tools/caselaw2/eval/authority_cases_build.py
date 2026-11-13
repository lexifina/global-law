"""Write caselaw-lean-2/gold/authority_cases.tsv: hand-checked authority unit tests.

Each row is a `force src dst t` test (expected = Force value) or a `canChangeStatus` test
(expected = 1/0; the citing court is the would-be overruler and cited_bench is the bench of
the overruling decision). Facts come from caselaw-lean-2/research/doctrine.md; tags S/L/U are
inherited from it. Court ids are v1 ids (lean-in-v3/courts_named.tsv); nodes are graph/nodes.tsv
ids, checked by hand against nodes.tsv and lean-in-v3/decisions.tsv (court, date).

cited_publication may carry ';'-separated qualifiers after the publication value:
  form=equallyDivided | vacated=yyyymmdd | reviewGranted=yyyymmdd
Run: python authority_cases_build.py
"""
import csv
import os

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
OUT = os.path.join(WORK, "caselaw-lean-2", "gold", "authority_cases.tsv")
COURTS = os.path.join(WORK, "lean-in-v3", "courts_named.tsv")

HEADER = ["id", "test", "citing_court", "citing_court_id", "citing_date", "citing_unit",
          "cited_node", "cited_cite", "cited_court", "cited_court_id", "cited_date", "cited_unit",
          "cited_publication", "cited_bench", "domain", "expected", "rule", "source", "tag"]

# Display names where the v1 name is ambiguous.
NAME_OVERRIDE = {
    913: "Court of Appeals of Kentucky (court of last resort, before 1976)",
    914: "Kentucky Court of Appeals (intermediate, from 1976)",
    892: "Ballard Circuit Court (Ky. trial court)",
    688: "Florida District Court of Appeal",
    729: "Florida Circuit Court",
    1022: "Michigan Circuit Court",
}

# Nodes (graph/nodes.tsv) -> (cite, v1 court id, date)
N = {
    426892: ("661 F.2d 1206", 241, 19811103),   # Bonner v. City of Prichard (en banc)
    426959: ("667 F.2d 33", 241, 19820204),     # Stein v. Reynolds Securities
    956015: ("618 F.2d 272", 346, 19800602),    # Thaggard v. City of Jackson (former 5th)
    958121: ("657 F.2d 727", 346, 19810930),    # NLRB v. Decibel Products (Unit A, decided 30 Sept 1981)
    958131: ("657 F.2d 790", 346, 19811001),    # United Gas Pipe Line v. FERC (no unit; 1 Oct 1981)
    958185: ("659 F.2d 1314", 346, 19811026),   # Mississippi River Grain Elevator (Unit A, post-split)
    958245: ("660 F.2d 1028", 346, 19811112),   # United States v. Freeman (Unit B, post-split)
    959602: ("699 F.2d 1291", 346, 19830301),   # United States v. Texas Educ. Agency (new 5th)
    1612455: ("690 F.2d 1368", 520, 19821028),  # South Corp. v. United States (en banc)
    1968887: ("614 F.2d 1273", 654, 19800123),  # Miami Tribe v. United States (Ct. Cl.)
    1968890: ("615 F.2d 1335", 654, 19800220),  # Gens v. United States (Ct. Cl.)
    1927518: ("610 F.2d 786", 655, 19791206),   # In re Theis (CCPA; v1 decisions.tsv maps it to 3160)
    1615134: ("43 F.3d 1451", 520, 19950105),   # Baylin v. United States (Fed. Cir.)
    1681498: ("57 Cal. 2d 450", 522, 19620322),  # Auto Equity Sales
    1738291: ("243 Cal. App. 4th 151", 534, 20151123),  # United Riggers (2d Dist., Div. 1)
    1691517: ("243 Cal. App. 4th 525", 530, 20151230),  # Heckart (4th Dist., Div. 1)
    1691543: ("244 Cal. App. 4th 1229", 532, 20160218), # In re Kocontes (4th Dist., Div. 3)
    2119313: ("596 So. 2d 665", 680, 19920326),  # Pardo v. State
    2205105: ("333 So. 2d 51", 688, 19760611),   # State v. Hayes (4th DCA)
    3061597: ("503 S.W.2d 706", 913, 19740104),  # Woods v. Mills (old Ky. Ct. App.)
    3072133: ("57 S.W.3d 839", 914, 20001117),   # Smith v. Vilvarajah (Ky. App.)
    3064261: ("782 S.W.2d 625", 917, 19900118),  # Berry v. Commonwealth (Ky.)
    3615001: ("174 Mich. App. 1", 1043, 19890103),   # American Casualty v. Costello
    3618116: ("208 Mich. App. 278", 1043, 19950117), # Hanaway v. Hanaway
    991992: ("280 F. App'x 356", 346, 20080603),
    1423009: ("132 F. App'x 738", 479, 20050601),
    1444738: ("326 F. App'x 420", 479, 20090603),
    551545: ("65 F. App'x 361", 272, 20030602),
    566367: ("379 F. App'x 101", 272, 20100601),
    818864: ("64 F. App'x 396", 307, 20030602),
    1574181: ("13 F. App'x 4", 514, 20010612),
    1575195: ("66 F. App'x 207", 514, 20030610),
    718150: ("382 F. App'x 125", 289, 20100602),
    451728: ("380 F. App'x 930", 241, 20100601),
    1202787: ("134 F. App'x 86", 408, 20050606),
    1308621: ("280 F. App'x 552", 430, 20080602),
    6117255: ("490 U.S. 477", 2906, 19890515),  # Rodriguez de Quijas
    5973080: ("304 U.S. 64", 2906, 19380425),   # Erie
    1412782: ("335 F.3d 889", 479, 20030709),   # Miller v. Gammie (en banc)
    729485: ("879 F.3d 504", 289, 20180111),    # Karns v. Shanahan
    810272: ("163 F.3d 860", 307, 19981218),    # Williams v. Taylor (4th)
    993884: ("548 F.3d 375", 346, 20081110),    # Jacobs v. NDIC
    1517238: ("351 F. Supp. 2d 992", 493, 20050106),  # United States v. Leung (C.D. Cal.)
    486870: ("873 F. Supp. 1519", 262, 19950117),     # Kyser-Smith (M.D. Ala.)
    1298429: ("223 F.3d 898", 430, 20000822),   # Anastasoff (vacated 235 F.3d 1054, 18 Dec 2000)
    6298389: ("579 U.S. 547", 2906, 20160623),  # United States v. Texas (4-4)
    6298347: ("578 U.S. 1", 2906, 20160329),    # Friedrichs (4-4)
    6025471: ("390 U.S. 404", 2906, 19680318),  # Biggers v. Tennessee (4-4)
}

# Source strings
KY = "SCR 1.030(8)(a), https://www.courtrules.net/kentucky/kentucky-supreme-court-rules/rule-1-030; Smith v. Vilvarajah, 57 S.W.3d 839, 841 (Ky. App. 2000)"
KYH3 = "doctrine H3; SCR 1.030(8)(a); Ky. Const. Judicial Article (eff. 1 Jan 1976)"
BON = "Bonner v. City of Prichard, 661 F.2d 1206, 1209 (11th Cir. 1981) (en banc), https://openjurist.org/661/f2d/1206"
BONEB = "Bonner v. City of Prichard, 661 F.2d 1206, 1209-11 (11th Cir. 1981) (en banc)"
UNITB = "Stein v. Reynolds Securities, Inc., 667 F.2d 33, 34 (11th Cir. 1982)"
SOUTH = "South Corp. v. United States, 690 F.2d 1368, 1370 (Fed. Cir. 1982) (en banc)"
F11B = "doctrine F11(b); 28 U.S.C. § 1295; South Corp., 690 F.2d at 1370"
GOURLEY = "People v. Gourley, 130 Cal. Rptr. 3d 181, 186 (App. Dep't Super. Ct. 2011); In re Marriage of Shaban, 88 Cal. App. 4th 398, 409 (2001)"
AUTOEQ = "Auto Equity Sales, Inc. v. Superior Court, 57 Cal. 2d 450, 455-56 (1962)"
CA8115 = "Cal. Rules of Court 8.1115, https://www.courts.ca.gov/cms/rules/index/eight/rule8_1115"
PARDO = "Pardo v. State, 596 So. 2d 665, 666 (Fla. 1992)"
HAYES = "State v. Hayes, 333 So. 2d 51, 53 (Fla. 4th DCA 1976), quoted in Pardo v. State, 596 So. 2d 665, 666 (Fla. 1992)"
FL9331 = "Fla. R. App. P. 9.331"
MCRJ1 = "MCR 7.215(J)(1)"
FJC = "FJC table (Reagan 2007), 241 F.R.D. 328, https://www.fjc.gov/sites/default/files/2012/CitRules.pdf"
FRAP = "FRAP 32.1, https://www.law.cornell.edu/rules/frap/rule_32-1"
RDQ = "Rodriguez de Quijas v. Shearson/American Express, 490 U.S. 477, 484 (1989)"
ERIE = "Erie R.R. v. Tompkins, 304 U.S. 64, 78 (1938)"
CAMRETA = "Camreta v. Greene, 563 U.S. 692, 709 n.7 (2011)"
F5 = "Neil v. Biggers, 409 U.S. 188, 192 (1972); Hertz v. Woodman, 218 U.S. 205, 213-14 (1910)"

# (test, citing_id, t, citing_unit, node|-1, cited_cite(if -1), cited_id(if -1), cited_date(if -1),
#  cited_unit, publication, bench, domain, expected, rule, source, tag)
R = []
def f(cid, t, cu, node, unit, pub, bench, dom, exp, rule, src, tag, cite="", ccid=None, cdate=None):
    R.append(("force", cid, t, cu, node, cite, ccid, cdate, unit, pub, bench, dom, exp, rule, src, tag))
def c(cid, t, cu, node, unit, pub, bench, dom, exp, rule, src, tag, cite="", ccid=None, cdate=None):
    R.append(("canChangeStatus", cid, t, cu, node, cite, ccid, cdate, unit, pub, bench, dom, str(exp), rule, src, tag))

KYD = "stateLaw:KY"
# ---- Kentucky
f(914, 19850601, "-", 3061597, "-", "published", "unknown", KYD, "binding",
  "pre-1976 Court of Appeals (then last resort) binds the modern Court of Appeals as predecessor-court precedent", KY, "S")
f(892, 19900601, "-", 3061597, "-", "published", "unknown", KYD, "binding",
  "pre-1976 last-resort decision binds Kentucky trial courts", KYH3 + "; doctrine H1", "S")
f(917, 19900601, "-", 3061597, "-", "published", "unknown", KYD, "persuasiveStrong",
  "pre-1976 Court of Appeals is the Supreme Court's predecessor: last resort to successor = persuasiveStrong (not bound)", KYH3 + "; doctrine H1 (highest court not bound by itself)", "L")
f(917, 20050601, "-", 3072133, "-", "published", "panel", KYD, "persuasive",
  "post-1976 Court of Appeals decision does not bind the Supreme Court of Kentucky", "doctrine H1, §3.2 Kentucky row; SCR 1.030(8)(a)", "L")
f(914, 20050601, "-", 3072133, "-", "published", "panel", KYD, "binding",
  "post-1976 Court of Appeals published panel binds a later panel (KY horizontal = strong)", "doctrine §4.3 KY row; SCR 1.030(7)(d)", "L")
f(892, 20050601, "-", 3072133, "-", "published", "panel", KYD, "binding",
  "post-1976 Court of Appeals binds Kentucky trial courts (V = statewide)", "doctrine §4.3 KY row", "L")
f(914, 19950601, "-", 3064261, "-", "published", "fullCourt", KYD, "binding",
  "Supreme Court of Kentucky binds the Court of Appeals", KY, "S")
c(914, 19850601, "-", 3061597, "-", "published", "panel", KYD, 0,
  "modern Court of Appeals panel cannot overrule its predecessor court's decision", KY, "S")
c(914, 19850601, "-", 3061597, "-", "published", "wholeCourt", KYD, 0,
  "even the whole modern Court of Appeals is bound by predecessor-court precedent", KY, "S")
c(917, 19900601, "-", 3061597, "-", "published", "unknown", KYD, 1,
  "Supreme Court of Kentucky, as successor court of last resort, may overrule pre-1976 Court of Appeals decisions", KYH3, "S")
c(914, 20050601, "-", 3072133, "-", "published", "panel", KYD, 0,
  "post-1976 Court of Appeals panel cannot overrule a prior published panel (strong horizontal)", "doctrine §4.3 KY row; SCR 1.030(7)(d)", "L")

FED = "federalGeneral"
# ---- Bonner / 11th Circuit
f(241, 19900601, "-", 956015, "-", "published", "panel", FED, "binding",
  "former Fifth Circuit decision before 1 Oct 1981 binds the 11th Circuit", BON, "S")
f(268, 19950601, "-", 956015, "-", "published", "panel", FED, "binding",
  "former Fifth Circuit decision binds district courts of the 11th Circuit", BON, "S")
f(241, 19900601, "-", 958121, "unitA", "published", "panel", FED, "binding",
  "decided 30 Sept 1981 (before close of business on the cutoff day): binds the 11th Circuit, Unit A or not", BON + "; doctrine TM5", "S")
f(241, 19900601, "-", 958131, "-", "published", "panel", FED, "persuasive",
  "5th Circuit decision of 1 Oct 1981, not Unit B: after the cutoff, other-circuit law for the 11th", BON + "; doctrine F10 (Unit A after the split is 5th Cir. law)", "L")
f(241, 19900601, "-", 958185, "unitA", "published", "panel", FED, "persuasive",
  "post-split Unit A decision (26 Oct 1981) is 5th Circuit law, persuasive in the 11th", "doctrine F10 (Unit A after the split is 5th Cir. law)", "L")
f(241, 19900601, "-", 958245, "unitB", "published", "panel", FED, "binding",
  "Unit B decision issued after 30 Sept 1981 binds the 11th Circuit", UNITB, "L")
f(346, 19900601, "-", 956015, "-", "published", "panel", FED, "binding",
  "the 5th Circuit keeps pre-split Fifth Circuit law as its own (prior-panel rule)", "doctrine F10; Jacobs v. Nat'l Drug Intelligence Ctr., 548 F.3d 375, 378 (5th Cir. 2008)", "L")
c(241, 19900601, "-", 956015, "-", "published", "panel", FED, 0,
  "an 11th Circuit panel cannot overrule former Fifth Circuit precedent", BONEB, "L")
c(241, 19900601, "-", 956015, "-", "published", "enBanc", FED, 1,
  "the 11th Circuit en banc may overrule former Fifth Circuit precedent", BONEB, "L")
c(241, 19900601, "-", 958245, "unitB", "published", "panel", FED, 0,
  "an 11th Circuit panel cannot overrule an adopted Unit B decision (adopter en banc only)", UNITB + "; doctrine F10 Lean note", "L")
c(346, 19900601, "-", 956015, "-", "published", "enBanc", FED, 1,
  "5th Circuit en banc may overrule pre-split Fifth Circuit law for the 5th Circuit", "doctrine F10, F8", "L")
c(241, 19900601, "-", 959602, "-", "published", "enBanc", FED, 0,
  "11th Circuit has no power over a post-split 5th Circuit decision (a circuit acts only within its own circuit)", "doctrine F10; LEAN canChangeStatus", "L")

PAT = "federalPatent"
# ---- South Corp. / Federal Circuit
f(520, 19900601, "-", 1968887, "-", "published", "panel", FED, "binding",
  "Court of Claims decision before 1 Oct 1982 binds the Federal Circuit", SOUTH, "L")
f(520, 19900601, "-", 1927518, "-", "published", "panel", PAT, "binding",
  "CCPA decision before 1 Oct 1982 binds the Federal Circuit", SOUTH, "L")
f(493, 20050601, "-", 1927518, "-", "published", "panel", PAT, "binding",
  "adopted CCPA patent holding binds a district court nationwide on patent law", SOUTH + "; " + F11B, "L")
f(656, 20000601, "-", 1968890, "-", "published", "panel", FED, "binding",
  "adopted Court of Claims decision binds the Court of Federal Claims", SOUTH + "; " + F11B, "L")
f(656, 20000601, "-", 1615134, "-", "published", "panel", FED, "binding",
  "Federal Circuit binds the Court of Federal Claims", F11B, "L")
f(493, 20050601, "-", 1615134, "-", "published", "panel", FED, "persuasive",
  "Federal Circuit on a non-patent issue does not bind a district court in a regional circuit", "doctrine F11(b); Panduit Corp. v. All States Plastic Mfg., 744 F.2d 1564, 1574-75 (Fed. Cir. 1984)", "L")
c(520, 19900601, "-", 1968887, "-", "published", "panel", FED, 0,
  "a Federal Circuit panel cannot overrule an adopted Court of Claims decision", SOUTH, "L")
c(520, 19900601, "-", 1927518, "-", "published", "enBanc", PAT, 1,
  "the Federal Circuit en banc may overrule an adopted CCPA decision", SOUTH, "L")

CAD = "stateLaw:CA"
# ---- California
f(534, 20170601, "2/1", 1681498, "-", "published", "fullCourt", CAD, "binding",
  "Supreme Court of California binds every Court of Appeal", AUTOEQ + "; doctrine H1", "S")
f(536, 20170601, "2/3", 1738291, "2/1", "published", "panel", CAD, "persuasive",
  "another division of the same district: persuasive only (horizontal = none)", GOURLEY, "S")
f(530, 20170601, "4/1", 1738291, "2/1", "published", "panel", CAD, "persuasive",
  "another district: persuasive only", GOURLEY, "S")
f(530, 20180601, "4/1", 1691517, "4/1", "published", "panel", CAD, "persuasive",
  "no horizontal stare decisis even within one division", "doctrine S-CA (H = none, 'nor within one'); " + GOURLEY, "S")
f(547, 20180601, "-", 1691543, "4/3", "published", "panel", CAD, "bindingAbsentConflict",
  "any published Court of Appeal decision binds every superior court; with conflicting decisions the trial court chooses", AUTOEQ, "L")
f(547, 20170601, "-", -1, "2/3", "published;reviewGranted=20170301", "panel", CAD, "persuasive",
  "published opinion with review granted on/after 1 July 2016: no binding effect pending review, citable for persuasive value",
  CA8115 + "(e)(1)", "S", cite="(synthetic) Cal. App. 5th opinion, review granted 1 Mar 2017", ccid=533, cdate=20161201)
f(547, 20150601, "-", -1, "2/3", "published;reviewGranted=20150301", "panel", CAD, "notCitable",
  "review granted before 1 July 2016 automatically depublished the opinion",
  "former Cal. Rules of Court 8.1105(e)(1); doctrine S-CA review-granted rule", "S", cite="(synthetic) Cal. App. 4th opinion, review granted 1 Mar 2015", ccid=533, cdate=20141201)
f(547, 20120601, "-", -1, "2/3", "unpublished", "panel", CAD, "notCitable",
  "unpublished Court of Appeal opinions must not be cited or relied on in other actions", CA8115 + "(a)-(b)", "S",
  cite="(synthetic) unpublished Court of Appeal opinion", ccid=533, cdate=20100601)

FLD = "stateLaw:FL"
# ---- Florida
f(688, 20000601, "1", 2119313, "-", "published", "fullCourt", FLD, "binding",
  "Supreme Court of Florida binds every District Court of Appeal", PARDO + "; doctrine H1", "S")
f(688, 19900601, "1", 2205105, "4", "published", "panel", FLD, "persuasive",
  "a sister DCA's decision is merely persuasive to another DCA", HAYES, "S")
f(729, 19900601, "2", 2205105, "4", "published", "panel", FLD, "bindingAbsentConflict",
  "absent interdistrict conflict, a DCA decision binds trial courts in every district", PARDO, "S")
f(729, 19900601, "4", 2205105, "4", "published", "panel", FLD, "binding",
  "a DCA binds trial courts of its own district (they follow it even with an interdistrict conflict)", PARDO + "; doctrine S-FL V = ownUnitThenAny", "L")
f(688, 19900601, "4", 2205105, "4", "published", "panel", FLD, "binding",
  "within a DCA, panels are bound by prior panels (only the court en banc may recede)", FL9331 + "; doctrine S-FL H = withinUnitOnly", "L")
c(688, 19900601, "4", 2205105, "4", "published", "panel", FLD, 0,
  "a 4th DCA panel cannot recede from 4th DCA precedent", FL9331, "L")
c(688, 19900601, "4", 2205105, "4", "published", "enBanc", FLD, 1,
  "the 4th DCA en banc may recede from its own precedent", FL9331, "L")
c(688, 19900601, "1", 2205105, "4", "published", "enBanc", FLD, 0,
  "the 1st DCA, even en banc, has no power over a 4th DCA decision", HAYES + "; doctrine S-FL (withinUnitOnly)", "L")
c(680, 19920326, "-", 2205105, "4", "published", "fullCourt", FLD, 1,
  "Supreme Court of Florida may overrule (disapprove) a DCA decision", "Fla. Const. art. V § 3(b)(3)-(4); doctrine H1, S-FL vocabulary", "L")

MID = "stateLaw:MI"
# ---- Michigan
f(1043, 20000601, "-", 3618116, "-", "published", "panel", MID, "binding",
  "published Court of Appeals opinion issued on or after 1 Nov 1990 binds later panels", MCRJ1, "S")
f(1043, 20000601, "-", 3615001, "-", "published", "panel", MID, "persuasiveStrong",
  "published opinion issued before 1 Nov 1990 does not bind later panels (soft horizontal)", MCRJ1 + "; doctrine S-MI", "S")
f(1043, 20000601, "-", -1, "-", "published", "panel", MID, "binding",
  "cutoff day: opinion issued 1 Nov 1990 binds later panels", MCRJ1, "S",
  cite="(synthetic) Mich. App. opinion issued 1 Nov 1990", ccid=1043, cdate=19901101)
f(1043, 20000601, "-", -1, "-", "published", "panel", MID, "persuasiveStrong",
  "day before the cutoff: opinion issued 31 Oct 1990 does not bind later panels", MCRJ1, "S",
  cite="(synthetic) Mich. App. opinion issued 31 Oct 1990", ccid=1043, cdate=19901031)
f(1022, 19950601, "-", 3615001, "-", "published", "panel", MID, "binding",
  "the 1990 rule is horizontal only: a pre-1990 published opinion still binds trial courts (V = statewide)", "doctrine S-MI V = statewide", "L")
f(1043, 20100601, "-", -1, "-", "unpublished", "panel", MID, "persuasive",
  "unpublished Court of Appeals opinions are not precedentially binding", "MCR 7.215(C)(1)", "U",
  cite="(synthetic) unpublished Mich. App. opinion", ccid=1043, cdate=20050601)
c(1043, 20000601, "-", 3618116, "-", "published", "panel", MID, 0,
  "a panel must follow a post-1 Nov 1990 published opinion; it cannot overrule it", MCRJ1, "S")
c(1043, 20000601, "-", 3618116, "-", "published", "conflictPanel", MID, 1,
  "a 7-judge special (conflict) panel may resolve the conflict and its decision binds", "MCR 7.215(J)(3), (J)(5)", "S")
c(1043, 20000601, "-", 3615001, "-", "published", "panel", MID, 1,
  "a panel is not bound by a pre-1 Nov 1990 opinion and may depart from it", MCRJ1 + "; doctrine S-MI", "S")

# ---- Unpublished opinions, per circuit and date
f(346, 20100601, "-", 991992, "-", "unpublished", "panel", FED, "persuasive",
  "5th Cir. unpublished opinion issued on/after 1 Jan 1996 is not precedent (citable)", "5th Cir. R. 47.5.4; " + FJC, "S")
f(346, 20000601, "-", -1, "-", "unpublished", "panel", FED, "binding",
  "5th Cir. unpublished opinion issued before 1 Jan 1996 is precedent", "5th Cir. R. 47.5.3; " + FJC, "S",
  cite="(synthetic) 5th Cir. unpublished opinion, 15 Jun 1995", ccid=346, cdate=19950615)
f(346, 20000601, "-", -1, "-", "unpublished", "panel", FED, "persuasive",
  "5th Cir. unpublished opinion issued 2 Jan 1996 (after the cutoff) is not precedent", "5th Cir. R. 47.5.4; " + FJC, "S",
  cite="(synthetic) 5th Cir. unpublished opinion, 2 Jan 1996", ccid=346, cdate=19960102)
f(479, 20100601, "-", 1423009, "-", "unpublished", "panel", FED, "notCitable",
  "9th Cir. unpublished disposition issued before 1 Jan 2007 may not be cited", "9th Cir. R. 36-3; " + FJC, "S")
f(479, 20120601, "-", 1444738, "-", "unpublished", "panel", FED, "persuasive",
  "9th Cir. unpublished disposition issued on/after 1 Jan 2007 is citable but not precedent", "9th Cir. R. 36-3; " + FRAP, "L")
f(272, 20080601, "-", 551545, "-", "summaryOrder", "panel", FED, "notCitable",
  "2d Cir. summary order before 1 Jan 2007: citation prohibited (no precedential effect)", "2d Cir. R. 32.1.1; " + FJC, "S")
f(272, 20120601, "-", 566367, "-", "summaryOrder", "panel", FED, "persuasive",
  "2d Cir. summary order after 2007: citable, no precedential effect", "2d Cir. R. 32.1.1; " + FRAP, "L")
f(307, 20100601, "-", 818864, "-", "unpublished", "panel", FED, "persuasive",
  "4th Cir. pre-2007 unpublished opinion: not binding; citation disfavored unless no published opinion serves as well", "4th Cir. R. 32.1; " + FJC, "U")
f(514, 20050601, "-", 1574181, "-", "unpublished", "panel", FED, "notCitable",
  "D.C. Cir. unpublished disposition entered before 1 Jan 2002 is not to be cited as precedent", "D.C. Cir. R. 32.1(b)(1); " + FJC, "L")
f(514, 20050601, "-", 1575195, "-", "unpublished", "panel", FED, "binding",
  "D.C. Cir. unpublished disposition entered on/after 1 Jan 2002 'may be cited as precedent' (but R. 36(e)(2): panel saw no precedential value)", "D.C. Cir. R. 32.1(b)(1), 36(e)(2); " + FJC, "U")
f(289, 20120601, "-", 718150, "-", "unpublished", "panel", FED, "persuasive",
  "3d Cir. not-precedential opinion does not bind (not circulated to the full court)", "3d Cir. I.O.P. 5.7; " + FJC, "L")
f(241, 20120601, "-", 451728, "-", "unpublished", "panel", FED, "persuasive",
  "11th Cir. unpublished opinion is not binding precedent but may be cited as persuasive authority", "11th Cir. R. 36-2; " + FJC, "S")
f(408, 20100601, "-", 1202787, "-", "unpublished", "panel", FED, "notCitable",
  "7th Cir. unpublished order issued before 1 Jan 2007 may not be cited (except preclusion / law of the case)", "7th Cir. R. 32.1(b), (d); " + FJC, "S")
f(430, 20100601, "-", 1308621, "-", "unpublished", "panel", FED, "persuasive",
  "8th Cir. unpublished opinion after 2007: citable (FRAP 32.1) but not precedent", "8th Cir. R. 32.1A; " + FRAP, "L")

# ---- Basics
f(479, 20000601, "-", 6117255, "-", "published", "fullCourt", FED, "binding",
  "SCOTUS binds every federal court on federal law", RDQ, "S")
f(522, 20000601, "-", 6117255, "-", "published", "fullCourt", FED, "binding",
  "SCOTUS binds state courts on federal law", RDQ + "; doctrine F1 scope", "S")
f(680, 20000601, "-", -1, "-", "published", "fullCourt", FLD, "persuasive",
  "a SCOTUS reading of state law does not bind the state's highest court", "doctrine F1 scope; LEAN SCOTUS rule", "L",
  cite="(synthetic) SCOTUS decision on a Florida-law issue", ccid=2906, cdate=19900601)
f(268, 19950601, "-", 2119313, "-", "published", "fullCourt", FLD, "binding",
  "Erie: the state's highest court binds federal courts on that state's law (t >= 25 Apr 1938)", ERIE, "L")
f(268, 19380425, "-", -1, "-", "published", "fullCourt", FLD, "binding",
  "Erie decision day: a Florida Supreme Court decision binds a federal court on Florida law", ERIE + "; doctrine TM5", "L",
  cite="(synthetic) Fla. Supreme Court decision on a general common-law issue", ccid=680, cdate=19350601)
f(268, 19380424, "-", -1, "-", "published", "fullCourt", FLD, "persuasive",
  "day before Erie: on a general common-law issue the federal court exercised independent judgment (Swift); local law would be binding",
  ERIE + "; Swift v. Tyson, 41 U.S. (16 Pet.) 1 (1842); doctrine E1 Lean note", "U",
  cite="(synthetic) Fla. Supreme Court decision on a general common-law issue", ccid=680, cdate=19350601)
f(268, 19950601, "-", 2205105, "4", "published", "panel", FLD, "persuasiveStrong",
  "an intermediate state appellate decision is a datum the federal court must not disregard (Erie)", "West v. AT&T, 311 U.S. 223, 237 (1940); doctrine E1", "L")
f(522, 20050601, "-", 1412782, "-", "published", "enBanc", FED, "persuasive",
  "lower federal courts do not bind state courts on federal law", "Johnson v. Williams, 568 U.S. 289, 305 (2013); doctrine E3", "L")
f(2927, 19950601, "-", -1, "-", "published", "panel", "stateLaw:TX", "persuasive",
  "federal decisions on state law never bind state courts", "doctrine E1 corollary", "L",
  cite="(synthetic) 5th Cir. Erie decision on a Texas-law issue", ccid=346, cdate=19900601)
f(289, 20200601, "-", 729485, "-", "published", "panel", FED, "binding",
  "prior-panel rule: a published panel decision binds later panels of the same circuit", "Karns v. Shanahan, 879 F.3d 504, 514-15 (3d Cir. 2018); 3d Cir. I.O.P. 9.1", "S")
f(493, 20050601, "-", 1412782, "-", "published", "enBanc", FED, "binding",
  "a circuit's decision binds the district courts of that circuit", "doctrine F7; Miller v. Gammie, 335 F.3d 889, 899-900 (9th Cir. 2003) (en banc)", "S")
f(346, 20050601, "-", 1412782, "-", "published", "enBanc", FED, "persuasive",
  "another circuit's decision is persuasive only", "doctrine F7 (law of the circuit)", "L")
f(479, 20200601, "-", 729485, "-", "published", "panel", FED, "persuasive",
  "another circuit's decision is persuasive only", "doctrine F7 (law of the circuit)", "L")
f(493, 20100601, "-", 1517238, "-", "published", "panel", FED, "persuasive",
  "a district court decision does not bind the same district", CAMRETA, "L")
f(241, 20000601, "-", 486870, "-", "published", "panel", FED, "persuasive",
  "a district court decision does not bind its court of appeals", CAMRETA + "; doctrine F13", "L")
f(430, 20001101, "-", 1298429, "-", "published;vacated=20001218", "panel", FED, "binding",
  "Anastasoff before its vacatur: a published 8th Cir. panel opinion binds later panels", "doctrine F7; Anastasoff v. United States, 223 F.3d 898 (8th Cir. 2000)", "L")
f(430, 20010601, "-", 1298429, "-", "published;vacated=20001218", "panel", FED, "none",
  "a vacated opinion loses precedential effect (Anastasoff vacated as moot en banc, 235 F.3d 1054, 18 Dec 2000)",
  "County of Los Angeles v. Davis, 440 U.S. 625, 634 n.6 (1979); doctrine F4", "L")
f(346, 20170601, "-", 6298389, "-", "published;form=equallyDivided", "fullCourt", FED, "none",
  "affirmance by an equally divided Court has no precedential weight (United States v. Texas, 4-4)", F5, "L")
f(373, 19700601, "-", 6025471, "-", "published;form=equallyDivided", "fullCourt", FED, "none",
  "Biggers v. Tennessee (4-4) decided nothing for other cases", "Neil v. Biggers, 409 U.S. 188, 192 (1972)", "L")
f(479, 20100601, "-", -1, "-", "published;form=equallyDivided", "enBanc", FED, "none",
  "an equally divided en banc court of appeals sets no circuit precedent", "doctrine F5 scope, F8", "L",
  cite="(synthetic) 9th Cir. en banc, equally divided", ccid=479, cdate=20050601)
c(479, 20000601, "-", 6117255, "-", "published", "enBanc", FED, 0,
  "only the Supreme Court may overrule its own decisions", RDQ, "S")
c(2906, 20000601, "-", 6117255, "-", "published", "fullCourt", FED, 1,
  "SCOTUS may overrule its own precedent", RDQ, "S")
c(289, 20200601, "-", 729485, "-", "published", "panel", FED, 0,
  "a later panel cannot overrule a prior precedential panel opinion", "3d Cir. I.O.P. 9.1; Karns v. Shanahan, 879 F.3d 504, 514-15 (3d Cir. 2018)", "L")
c(289, 20200601, "-", 729485, "-", "published", "enBanc", FED, 1,
  "the court en banc may overrule a panel decision", "3d Cir. I.O.P. 9.1; doctrine F8", "L")
c(479, 20100601, "-", 1412782, "-", "published", "panel", FED, 0,
  "a 9th Cir. panel cannot overrule an en banc decision", "doctrine F7, F8; Miller v. Gammie, 335 F.3d 889, 899-900 (9th Cir. 2003) (en banc)", "L")
c(493, 20100601, "-", 1412782, "-", "published", "panel", FED, 0,
  "a district court cannot overrule its circuit", "doctrine F7, F13", "L")
c(346, 20100601, "-", 1412782, "-", "published", "enBanc", FED, 0,
  "a circuit (even en banc) has no power over another circuit's decision", "doctrine F7; LEAN canChangeStatus", "L")


def main():
    names = {}
    with open(COURTS, encoding="utf-8") as fh:
        for row in csv.reader(fh, delimiter="\t"):
            names[int(row[0])] = row[1]
    name = lambda i: NAME_OVERRIDE.get(i, names[i])
    out = ["\t".join(HEADER)]
    for k, (test, cid, t, cu, node, cite, ccid, cdate, unit, pub, bench, dom, exp, rule, src, tag) in enumerate(R, 1):
        if node != -1:
            cite, ccid, cdate = N[node]
        cells = [f"AC{k:03d}", test, name(cid), str(cid), str(t), cu, str(node), cite, name(ccid), str(ccid),
                 str(cdate), unit, pub, bench, dom, exp, rule, src, tag]
        assert all("\t" not in x and "\n" not in x for x in cells), cells
        assert tag in ("S", "L", "U")
        if test == "force":
            assert exp in ("none", "notCitable", "citableNoWeight", "persuasive", "persuasiveStrong",
                           "bindingAbsentConflict", "binding"), exp
        else:
            assert exp in ("0", "1")
        assert t >= cdate, (k, t, cdate)
        out.append("\t".join(cells))
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print(len(R), "rows ->", OUT)


if __name__ == "__main__":
    main()
