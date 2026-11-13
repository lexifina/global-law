"""Tiny synthetic fixtures that follow SCHEMA.md exactly (LF, tab-separated, no header).

Run: python make_fixtures.py   (writes into this folder: data/ and edges/)
Certificate offsets are computed from synthetic decision texts, so every quote is the exact substring of its
window at (start - start0). Node ids are fixture-local (0..N); court ids reuse v1 ids where they exist and use
>= 10000 for fixture-only courts.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
EDGES = os.path.join(HERE, "edges")


def norm(s):
    return s.replace("\r\n", "\n").replace("\t", " ").replace("\n", " ")


def write(name, rows, d=DATA):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


# --- courts2.tsv: court_id, epoch_from, epoch_to, name, system, tier, last_resort_for, circuit, unit, src, tag
SCOTUS, CA5, CA11, NDTEX, SDFLA = 2906, 346, 241, 367, 268
KYOLD, KYSUP = 918, 917            # Court of Appeals of Kentucky (L to 1975, A from 1976); Supreme Court of Kentucky
CASUP, CAAPP, CASUPER = 522, 524, 10000
GASUP, GAAPP = 10001, 10002
courts = [
    (SCOTUS, 0, 99999999, "Supreme Court of the United States", 0, "L", "all", 0, 0, "v1", "S"),
    (CA5, 0, 99999999, "United States Court of Appeals for the Fifth Circuit", 0, "A", "-", 5, 0, "v1", "S"),
    (CA11, 19811001, 99999999, "United States Court of Appeals for the Eleventh Circuit", 0, "A", "-", 11, 0, "v1", "S"),
    (NDTEX, 0, 99999999, "United States District Court for the Northern District of Texas", 0, "T", "-", 5, 0, "v1", "S"),
    (SDFLA, 0, 99999999, "United States District Court for the Southern District of Florida", 0, "T", "-", 11, 0, "v1", "S"),
    (KYOLD, 0, 19751231, "Court of Appeals of Kentucky", 17, "L", "all", 0, 0, "doctrine:3.2", "S"),
    (KYOLD, 19760101, 99999999, "Court of Appeals of Kentucky", 17, "A", "-", 0, 0, "doctrine:3.2", "S"),
    (KYSUP, 19760101, 99999999, "Supreme Court of Kentucky", 17, "L", "all", 0, 0, "doctrine:3.2", "S"),
    (CASUP, 0, 99999999, "Supreme Court of California", 5, "L", "all", 0, 0, "v1", "S"),
    (CAAPP, 19050101, 99999999, "California Court of Appeal", 5, "A", "-", 0, 0, "v1", "S"),
    (CASUPER, 0, 99999999, "Superior Court of California, Los Angeles County", 5, "T", "-", 0, 2, "fixture", "L"),
    (GASUP, 0, 99999999, "Supreme Court of Georgia", 11, "L", "all", 0, 0, "fixture", "S"),
    (GAAPP, 19070101, 99999999, "Court of Appeals of Georgia", 11, "A", "-", 0, 0, "fixture", "S"),
]
write("courts2.tsv", courts)

write("succession.tsv", [
    (KYOLD, KYSUP, 19760101, "replace", "SCR 1.030(8)(a)", "S"),
])
write("adoption.tsv", [
    (CA11, CA5, 19810930, "all", "binding", "Bonner 661 F.2d 1206", "S"),
    (CA11, CA5, 99999999, "unitB", "binding", "Stein 667 F.2d 33", "L"),
    (KYOLD, KYOLD, 19751231, "all", "binding", "SCR 1.030(8)(a)", "S"),
])
write("system_rules.tsv", [
    (0, "horizontal", "strong", 0, 99999999, "doctrine:F7", "S"),
    (5, "horizontal", "none", 0, 99999999, "doctrine:S-CA", "S"),
    (5, "trialScope", "statewideChooseOnConflict", 0, 99999999, "Auto Equity", "S"),
    (17, "horizontal", "strong", 0, 99999999, "doctrine:4.3 KY", "L"),
    (11, "horizontal", "strong", 0, 99999999, "doctrine:S-GA", "S"),
    (-CA5, "unpubForce", "binding", 0, 19951231, "5th Cir. R. 47.5.3", "S"),
    (-CA5, "unpubForce", "persuasive", 19960101, 99999999, "5th Cir. R. 47.5.4", "S"),
    (-CA5, "firstInTimeControls", 1, 0, 99999999, "Rios 444 F.3d 417", "L"),
    (-CA11, "firstInTimeControls", 1, 0, 99999999, "Dixon 901 F.3d 1322", "S"),
    (-CA11, "enBancGrantVacatesPanel", 1, 0, 99999999, "11th Cir. R. 35-11", "L"),
    (-CA5, "enBancGrantVacatesPanel", 1, 0, 99999999, "5th Cir. R. 41.3", "L"),
    (-CA5, "circulationCountsAsEnBanc", 0, 0, 99999999, "doctrine:F7", "U"),
    (20, "stateFollowsCircuit", "binding", 19840101, 99999999, "Littlefield 480 A.2d 731", "U"),
])

# --- decisions + synthetic texts
# (node, court, date, unit, bench, publication, form, text)
D = [
    (0, SCOTUS, 19420601, 0, "wholeCourt", "published", "full", "Betts v. Brady. Due process does not require appointed counsel in every state felony case."),
    (1, SCOTUS, 19630318, 0, "wholeCourt", "published", "full",
     "Gideon v. Wainwright. We accept the contention. Betts v. Brady, 316 U.S. 455, should be overruled. Reversed."),
    (2, SCOTUS, 19860630, 0, "wholeCourt", "published", "full", "Bowers v. Hardwick. The statute is upheld."),
    (3, SCOTUS, 20030626, 0, "wholeCourt", "published", "full",
     "Lawrence v. Texas. Bowers was not correct when it was decided. Bowers v. Hardwick, 478 U.S. 186, should be and now is overruled."),
    (4, KYOLD, 19700115, 0, "wholeCourt", "published", "full", "Old Court of Appeals of Kentucky. Contributory negligence bars recovery."),
    (5, KYOLD, 19900601, 0, "panel", "published", "full", "New Court of Appeals of Kentucky. We are bound by the predecessor court."),
    (6, CA5, 19750301, 0, "panel", "published", "full", "Former Fifth Circuit. The limitations period runs from discovery."),
    (7, CA11, 19900301, 0, "panel", "published", "full", "Eleventh Circuit. Under Bonner the former Fifth Circuit decision binds us."),
    (8, CAAPP, 20010101, 1, "panel", "published", "full", "Court of Appeal, First District. The clause is enforceable."),
    (9, CAAPP, 20050101, 2, "panel", "published", "full", "Court of Appeal, Second District. We disagree; the clause is unenforceable."),
    (10, CASUPER, 20100101, 2, "unknown", "unpublished", "full", "Superior Court. Faced with conflicting authority we choose."),
    (11, SCOTUS, 20070529, 0, "wholeCourt", "published", "full", "Ledbetter v. Goodyear. The charge was untimely; each paycheck is not a new violation."),
    (12, NDTEX, 20100601, 0, "unknown", "published", "full", "District court applying Ledbetter to conduct in 2006."),
    (13, GASUP, 19800101, 0, "wholeCourt", "published", "full", "Georgia Supreme Court. Holding one on venue; holding two on notice."),
    (14, GASUP, 19950101, 0, "wholeCourt", "published", "full",
     "Georgia Supreme Court. To the extent Smith v. Jones, 245 Ga. 1, held that notice is not required, it is overruled."),
    (15, CA5, 19990301, 0, "panel", "unpublished", "full", "Unpublished Fifth Circuit opinion. Pursuant to 5TH CIR. R. 47.5 not published."),
    (16, NDTEX, 20010101, 0, "unknown", "published", "full", "District court treating an unpublished opinion as binding."),
    (17, NDTEX, 20050101, 0, "unknown", "published", "full", "District court citing Bowers in 2005."),
    (18, GAAPP, 19960101, 0, "panel", "published", "full",
     "Court of Appeals of Georgia. The objection is overruled. Appellant's first point of error is overruled."),
    (19, GASUP, 19960601, 0, "wholeCourt", "published", "full", "Georgia Supreme Court. Vacated on rehearing, opinion withdrawn."),
    # round 2 (DEVIATIONS 74-78): status per line. A former Fifth Circuit decision (20) overruled by the Fifth Circuit
    # en banc after the Bonner cut-off (21): overruled in the original line, good law in the Eleventh Circuit's
    (20, CA5, 19760401, 0, "panel", "published", "full", "Former Fifth Circuit, Smith v. Roe. Laches bars the claim after two years."),
    (21, CA5, 19830301, 0, "enBanc", "published", "full",
     "Fifth Circuit en banc. Smith v. Roe, 530 F.2d 100, is hereby overruled. Laches does not bar the claim."),
    (22, CA11, 19900601, 0, "panel", "published", "full", "Eleventh Circuit. Laches does not bar this claim on these facts."),
    (23, SDFLA, 20000101, 0, "unknown", "published", "full", "Southern District of Florida citing Smith v. Roe as binding under Bonner."),
    (24, NDTEX, 20000101, 0, "unknown", "published", "full", "Northern District of Texas citing Smith v. Roe."),
]
texts = {n: norm(t) for (n, *_rest, t) in D}
sha = {n: hashlib.sha1(t.encode("utf-8")).hexdigest() for n, t in texts.items()}
write("decisions2.tsv", [(n, c, d, u, b, p, f, sha[n], "fixture") for (n, c, d, u, b, p, f, _t) in D])

cert_text = []


def cert(node, quote, evidence, part):
    """CERT columns for a quote inside node's text, and register its window."""
    t = texts[node]
    s = t.index(quote)
    e = s + len(quote)
    s0, e0 = max(0, s - 400), min(len(t), e + 400)
    cert_text.append((sha[node], s0, e0, t[s0:e0]))
    return (sha[node], s, e, quote, evidence, part)


treat = [
    (1, 1, 0, 19630318, "overruled", "all", "retroactive", 1,
     *cert(1, "Betts v. Brady, 316 U.S. 455, should be overruled", "cite:316 U.S. 455", "majority"), "regex-v2", 0.99),
    (2, 3, 2, 20030626, "overruled", "all", "retroactive", 1,
     *cert(3, "Bowers v. Hardwick, 478 U.S. 186, should be and now is overruled", "cite:478 U.S. 186", "majority"), "regex-v2", 0.99),
    (3, 14, 13, 19950101, "overruled", "issues:ga.notice", "retroactive", 1,
     *cert(14, "To the extent Smith v. Jones, 245 Ga. 1, held that notice is not required, it is overruled",
           "cite:245 Ga. 1", "majority"), "regex-v2", 0.9),
    # procedural "overruled": must be rejected by the disqualifier list
    (4, 18, 13, 19960101, "overruled", "all", "unknown", 1,
     *cert(18, "Appellant's first point of error is overruled", "name:Smith Jones", "majority"), "regex-v2", 0.4),
    # an intermediate court cannot overrule its supreme court: authority failure
    (5, 18, 13, 19960101, "overruled", "all", "unknown", 1,
     *cert(18, "The objection is overruled", "name:Smith Jones", "dissent"), "regex-v2", 0.3),
    (6, 16, 15, 20010101, "followed", "all", "unknown", 1,
     *cert(16, "treating an unpublished opinion as binding", "name:unpublished", "majority"), "gpt-5.4-mini", 0.7),
    # round 2: the Fifth Circuit en banc overrules the pre-split decision (reaches the original line only)
    (7, 21, 20, 19830301, "overruled", "all", "retroactive", 1,
     *cert(21, "Smith v. Roe, 530 F.2d 100, is hereby overruled", "cite:530 F.2d 100", "majority"), "regex-v2", 0.99),
]
write("treatments.tsv", treat)

hist = [
    (1, 19, -1, 19960701, "withdrawn", "all",
     *cert(19, "Vacated on rehearing, opinion withdrawn", "name:Georgia", "majority"), "fixture"),
]
write("history.tsv", hist)
write("cert_text.tsv", cert_text)

write("issues.tsv", [
    ("ga.venue", "venue for tort actions", "stateLaw:11", "-", "Is venue proper in the county of injury?", "fixture"),
    ("ga.notice", "ante-litem notice", "stateLaw:11", "-", "Is ante-litem notice required?", "fixture"),
    ("ca.clause", "arbitration clause enforceability", "stateLaw:5", "-", "Is the clause enforceable?", "fixture"),
    ("usc42:2000e-5(e)", "Title VII charge-filing period", "federalGeneral", "42:2000e-5(e)",
     "Does each paycheck restart the charge-filing period?", "fixture"),
    ("con.counsel", "right to appointed counsel", "federalGeneral", "-", "Does due process require appointed counsel?", "fixture"),
    # Horty fixtures (factors.tsv): two SCOTUS case bases, one inconsistent, one consistent
    ("fx.hortyA", "Horty fixture A (inconsistent base)", "federalGeneral", "-", "Does the plaintiff prevail?", "fixture"),
    ("fx.hortyB", "Horty fixture B (consistent base)", "federalGeneral", "-", "Does the plaintiff prevail?", "fixture"),
    # round 2: a question held both ways by the former Fifth Circuit (20, overruled in the Fifth's line) and the
    # Eleventh Circuit (22); with factors, so its Horty base differs by line
    ("fx.laches", "laches (per-line fixture)", "federalGeneral", "-", "Does laches bar the claim?", "fixture"),
])


def hcert(node, quote):
    return cert(node, quote, "name:x", "majority")


write("holdings.tsv", [
    ("h13a", 13, "ga.venue", "Venue lies in the county of injury.", "yes", "majority", *hcert(13, "Holding one on venue"), "fixture", 0.9),
    ("h13b", 13, "ga.notice", "Notice is not required.", "no", "majority", *hcert(13, "holding two on notice"), "fixture", 0.9),
    ("h8", 8, "ca.clause", "The clause is enforceable.", "yes", "majority", *hcert(8, "The clause is enforceable."), "fixture", 0.9),
    ("h9", 9, "ca.clause", "The clause is unenforceable.", "no", "majority", *hcert(9, "the clause is unenforceable."), "fixture", 0.9),
    ("h11", 11, "usc42:2000e-5(e)", "Each paycheck is not a new violation.", "no", "majority",
     *hcert(11, "each paycheck is not a new violation."), "fixture", 0.9),
    ("h0", 0, "con.counsel", "Due process does not require appointed counsel.", "no", "majority",
     *hcert(0, "Due process does not require appointed counsel"), "fixture", 0.9),
    # Horty fixtures: SCOTUS nodes 1 (Gideon) and 3 (Lawrence), both good law in 2026, so both are binding at SCOTUS
    ("hA1", 1, "fx.hortyA", "Plaintiff prevails.", "yes", "majority", *hcert(1, "We accept the contention."), "fixture", 0.9),
    ("hA3", 3, "fx.hortyA", "Defendant prevails.", "no", "majority",
     *hcert(3, "Bowers was not correct when it was decided."), "fixture", 0.9),
    ("hB1", 1, "fx.hortyB", "Plaintiff prevails.", "yes", "majority", *hcert(1, "We accept the contention."), "fixture", 0.9),
    ("hB3", 3, "fx.hortyB", "Defendant prevails.", "no", "majority",
     *hcert(3, "Bowers was not correct when it was decided."), "fixture", 0.9),
    # anchors: the runner examines a base only at courts holding on the issue (and one trial court per system/circuit),
    # and SCOTUS is not bound by its own holdings, so a Fifth Circuit holding on each issue makes CA5 an examined court;
    # at CA5 the SCOTUS holdings outrank it, so the base is exactly the SCOTUS cases (the anchor has no factors)
    ("hA6", 6, "fx.hortyA", "Plaintiff prevails.", "yes", "majority",
     *hcert(6, "The limitations period runs from discovery."), "fixture", 0.9),
    ("hB6", 6, "fx.hortyB", "Plaintiff prevails.", "yes", "majority",
     *hcert(6, "The limitations period runs from discovery."), "fixture", 0.9),
    # round 2: per-line fixture
    ("hL20", 20, "fx.laches", "Laches bars the claim.", "yes", "majority",
     *hcert(20, "Laches bars the claim after two years."), "fixture", 0.9),
    ("hL22", 22, "fx.laches", "Laches does not bar the claim.", "no", "majority",
     *hcert(22, "Laches does not bar this claim on these facts."), "fixture", 0.9),
])
write("cert_text.tsv", cert_text)  # rewrite including holding windows
write("marks.tsv", [])

# factors.tsv (optional, DESIGN D9): holding_id, factor, side (pi|delta), inReason (0/1). Factors: 1 security measures
# (pi), 2 agreed not to disclose (pi), 3 known to competitors (delta), 4 reverse-engineerable (delta).
# A: hA1 = <{1,2,3}, {1}, pi>, hA3 = <{1,3}, {3}, delta>: each reason is present in the other's facts, outcomes
#    differ -> inconsistent (Spec.Horty example cA/cC). Expect one `inconsistentBindingBase` finding on fx.hortyA.
# B: hB1 = <{1,2,3}, {1}, pi>, hB3 = <{2,4}, {4}, delta>: hB1's reason {1} is absent from hB3's facts (and 4 is absent
#    from hB1's) -> distinguishable, consistent. Expect no finding on fx.hortyB.
write("factors.tsv", [
    ("hA1", 1, "pi", 1), ("hA1", 2, "pi", 0), ("hA1", 3, "delta", 0),
    ("hA3", 1, "pi", 0), ("hA3", 3, "delta", 1),
    ("hB1", 1, "pi", 1), ("hB1", 2, "pi", 0), ("hB1", 3, "delta", 0),
    ("hB3", 2, "pi", 0), ("hB3", 4, "delta", 1),
    # round 2: hL20 = <{1,3}, {1}, pi>, hL22 = <{1,3}, {3}, delta>: they conflict. The base {hL20, hL22} exists only
    # in the Eleventh Circuit's line (hL20 is overruled in the Fifth's): expect one inconsistent base, at CA11
    ("hL20", 1, "pi", 1), ("hL20", 3, "delta", 0),
    ("hL22", 1, "pi", 0), ("hL22", 3, "delta", 1),
])

write("lawchanges.tsv", [
    ("lc1", "Pub. L. 111-2", "42:2000e-5(e)", 20090129, 20090129, 20070528, "Lilly Ledbetter Fair Pay Act s.6"),
])
write("supersessions.tsv", [
    ("s1", 11, "usc42:2000e-5(e)", "lc1", "lawNamesDecision", 1.0, 1, "fixture"),
])

# --- edges (citing, cited), two shards by citing id parity
edges = [(1, 0), (3, 2), (5, 4), (7, 6), (10, 8), (10, 9), (12, 11), (14, 13), (16, 15), (17, 2), (18, 13),
         (23, 20), (24, 20), (22, 20)]
write("edges-00.tsv", [e for e in edges if e[0] % 2 == 0], EDGES)
write("edges-01.tsv", [e for e in edges if e[0] % 2 == 1], EDGES)
print("fixtures written:", DATA, EDGES)
