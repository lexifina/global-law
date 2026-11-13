"""Build caselaw-lean-2's court table (courts2.tsv) and the name -> court epoch map (court_alias.tsv).

    python courts2_build.py            (reads ~/Documents/us-caselaw-lean-work/{graph,lean-in-v3}; writes caselaw-lean-2/data)

Court ids keep the v1 ids of lean-in-v3/courts.tsv (one id per court name and v1 era); a court known under several names
gets ONE canonical id (the v1 id of its main name) and the other names become aliases (court_alias.tsv). New courts,
courts split out of a v1 name by date, and the units of intermediate courts (district/division/department rows) get ids
>= 10000. Each canonical court has one row per epoch (name or role change); decisions are routed to an epoch by date.

Rules come from research/doctrine.md (rule ids in `src`, tags S|L|U) and research/data_audit.md §5 (the mis-tiering).
Rows that only restate the v1 mechanical mapping carry tag `-`.
"""
import collections, os, re, sys

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
OUT = os.path.join(WORK, "caselaw-lean-2", "data")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "caselaw"))
from courts_map import STATES, SYS, repo_state  # noqa: E402

D = 99991231
T1 = {"last": "L", "appellate": "A", "trial": "T", "special": "S"}
ORDN = {w: i + 1 for i, w in enumerate("First Second Third Fourth Fifth Sixth Seventh Eighth Ninth Tenth Eleventh Twelfth "
                                         "Thirteenth Fourteenth Fifteenth".split())}
ORDN.update({"1st": 1, "2nd": 2, "2d": 2, "3rd": 3, "3d": 3, "4th": 4, "5th": 5, "6th": 6, "7th": 7, "8th": 8, "9th": 9,
             "10th": 10, "11th": 11, "12th": 12, "13th": 13, "14th": 14, "15th": 15, "One": 1, "Two": 2, "Three": 3,
             "Four": 4, "Five": 5, "Six": 6, "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "I": 1, "II": 2,
             "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6})
S = SYS  # state name -> system id

# ------------------------------------------------------------------------------------------------ canonical courts
# key -> dict(system, id_name (v1 name whose id is reused; None = new id), circuit, epochs=[(from, to, name, tier, lrf,
# src, tag)]); epochs must tile 0..D.
CANON = {}


def canon(key, system, id_name, epochs, circuit=0, id_era=None):
    CANON[key] = dict(system=system, id_name=id_name, id_era=id_era, circuit=circuit, epochs=epochs)


# --- federal
canon("CA5", 0, "United States Court of Appeals for the Fifth Circuit",
      [(0, D, "United States Court of Appeals for the Fifth Circuit", "A", "-", "doctrine F7/F10", "L")], circuit=5)
canon("CA6", 0, "United States Court of Appeals for the Sixth Circuit",
      [(0, D, "United States Court of Appeals for the Sixth Circuit", "A", "-", "v1:circuit", "-")], circuit=6)
canon("CA9", 0, "United States Court of Appeals for the Ninth Circuit",
      [(0, D, "United States Court of Appeals for the Ninth Circuit", "A", "-", "v1:circuit", "-")], circuit=9)
canon("CADC", 0, "United States Court of Appeals for the District of Columbia Circuit",
      [(0, 19340606, "Court of Appeals of the District of Columbia", "A", "-",
        "doctrine §3.2 DC (Court of Appeals of D.C., 1893); rename Act of 7 June 1934", "L"),
       (19340607, 19480831, "United States Court of Appeals for the District of Columbia", "A", "-",
        "rename 1934; Judicial Code 1948", "L"),
       (19480901, D, "United States Court of Appeals for the District of Columbia Circuit", "A", "-",
        "Judicial Code of 1948 (eff. 1 Sept 1948)", "L")], circuit=12)
canon("CAFC", 0, "United States Court of Appeals for the Federal Circuit",
      [(0, D, "United States Court of Appeals for the Federal Circuit", "A", "-",
        "doctrine F11 (Pub. L. 97-164, created 1 Oct 1982)", "L")], circuit=13)
canon("CCPA", 0, "United States Court of Customs and Patent Appeals",
      [(0, D, "United States Court of Customs and Patent Appeals", "A", "-", "doctrine F11 (predecessor of Fed. Cir.)",
        "L")], circuit=13)
canon("CTCL", 0, "United States Court of Claims",
      [(0, D, "United States Court of Claims", "S", "-", "doctrine F11 (predecessor of Fed. Cir.; to 30 Sept 1982)",
        "L")], circuit=13)
canon("CFC", 0, "United States Court of Federal Claims",
      [(0, 19921028, "United States Claims Court", "S", "-", "doctrine F11(c) (Claims Court from 1 Oct 1982)", "L"),
       (19921029, D, "United States Court of Federal Claims", "S", "-", "doctrine F11(c) (renamed 29 Oct 1992)", "L")],
      circuit=13)
canon("CIT", 0, "United States Court of International Trade",
      [(0, 19801031, "United States Customs Court", "S", "-", "doctrine F11(c)", "L"),
       (19801101, D, "United States Court of International Trade", "S", "-", "doctrine F11(c) (1 Nov 1980)", "L")],
      circuit=13)
canon("TAX", 0, "United States Tax Court",
      [(0, 19421020, "United States Board of Tax Appeals", "S", "-", "doctrine F12 (Board of Tax Appeals 1924)", "L"),
       (19421021, 19691229, "Tax Court of the United States", "S", "-", "doctrine F12 (renamed 1942)", "L"),
       (19691230, D, "United States Tax Court", "S", "-", "doctrine F12 (Article I court 1969)", "L")])
canon("CAAF", 0, "United States Court of Appeals for the Armed Forces",
      [(0, 19941004, "United States Court of Military Appeals", "S", "-", "military; renamed 5 Oct 1994", "L"),
       (19941005, D, "United States Court of Appeals for the Armed Forces", "S", "-", "military", "L")])
for svc, cmr, cca in (("ARMY", "United States Army Court of Military Review", "United States Army Court of Criminal Appeals"),
                      ("AF", "United States Air Force Court of Military Review", "United States Air Force Court of Criminal Appeals"),
                      ("NMC", "United States Navy-Marine Corps Court of Military Review", "United States Navy-Marine Corps Court of Criminal Appeals"),
                      ("CG", "United States Coast Guard Court of Military Review", "United States Coast Guard Court of Criminal Appeals")):
    canon("CCA-" + svc, 0, cca, [(0, 19941004, cmr, "S", "-", "military intermediate court; renamed 5 Oct 1994", "L"),
                                 (19941005, D, cca, "S", "-", "military intermediate court", "L")])
canon("CAVC", 0, "United States Court of Appeals for Veterans Claims",
      [(0, 19990228, "United States Court of Veterans Appeals", "S", "-", "renamed 1 Mar 1999", "L"),
       (19990301, D, "United States Court of Appeals for Veterans Claims", "S", "-", "", "L")])
canon("SCDC", 51, "Supreme Court of the District of Columbia",
      [(0, D, "Supreme Court of the District of Columbia", "T", "-",
        "audit §5 (the 'United States Supreme Court of the District of Columbia' is this D.C. trial court)", "L")])

# --- D.C. local courts (doctrine §3.2 DC; M.A.P. v. Ryan)
canon("DCCA", 51, "District of Columbia Court of Appeals",
      [(0, 19621231, "Municipal Court of Appeals for the District of Columbia", "A", "-",
        "doctrine §3.2 DC (Municipal Court of Appeals, intermediate)", "L"),
       (19630101, 19710131, "District of Columbia Court of Appeals", "A", "-",
        "doctrine §3.2 DC; Pub. L. 87-873 (approved 23 Oct 1962; effective date computed from its 60-day clause); intermediate until 1 Feb 1971", "U"),
       (19710201, D, "District of Columbia Court of Appeals", "L", "all",
        "doctrine §3.2 DC: court of last resort from 1 Feb 1971 (D.C. Court Reform Act 1970; M.A.P. v. Ryan)", "S")])

# --- states: courts of last resort with renames / dual roles
canon("AL-COA", S["Alabama"], "Alabama Court of Appeals",
      [(0, D, "Alabama Court of Appeals", "A", "-", "doctrine §4.3 AL (Court of Appeals 1911-69; split 1969)", "L")])
canon("AL-CIV", S["Alabama"], "Alabama Court of Civil Appeals",
      [(0, D, "Alabama Court of Civil Appeals", "A", "-", "doctrine §4.3 AL (1969)", "L")])
canon("AL-CRIM", S["Alabama"], "Alabama Court of Criminal Appeals",
      [(0, D, "Alabama Court of Criminal Appeals", "A", "-",
        "audit §5 mis-tiered T; doctrine §4.3 AL (intermediate, 1969)", "L")])
canon("CT-SC", S["Connecticut"], "Connecticut Supreme Court",
      [(0, 19651229, "Supreme Court of Errors of the State of Connecticut", "L", "all",
        "doctrine §3.2 CT (Supreme Court of Errors until the 1965 constitution)", "L"),
       (19651230, D, "Connecticut Supreme Court", "L", "all", "doctrine §3.2 CT (renamed Dec 1965; day uncertain)", "U")])
canon("DE-CEA", S["Delaware"], "Delaware Court of Errors and Appeals",
      [(0, D, "Delaware Court of Errors and Appeals", "L", "all", "doctrine §3.2 DE (last resort until 1951)", "L")])
canon("DE-SC", S["Delaware"], "Delaware Supreme Court",
      [(0, 19501231, "Supreme Court of Delaware (before the 1951 amendment)", "L", "all",
        "doctrine §3.2 DE; pre-1951 role of this name uncertain", "U"),
       (19510101, D, "Delaware Supreme Court", "L", "all", "doctrine §3.2 DE (est. 1951; day uncertain)", "L")])
canon("HI-TERR", S["Hawaii"], "Supreme Court of the Territory of Hawaii",
      [(0, D, "Supreme Court of the Territory of Hawaii", "L", "all",
        "doctrine §3.2 HI (territorial court of last resort, 1900-1959); v1 had T", "L")])
canon("HI-REP", S["Hawaii"], "Supreme Court of the Republic of Hawaii",
      [(0, D, "Supreme Court of the Republic of Hawaii", "L", "all", "doctrine §3.2 HI (kingdom/republic era); v1 had T", "L")])
canon("KY-OLDCOA", S["Kentucky"], "Kentucky Court of Appeals",
      [(0, 19751231, "Court of Appeals of Kentucky (court of last resort before 1976)", "L", "all",
        "doctrine §3.2 KY / H3 (1975 Judicial Article, eff. 1 Jan 1976)", "S")], id_era="L")
canon("KY-COA", S["Kentucky"], "Kentucky Court of Appeals",
      [(19760101, D, "Kentucky Court of Appeals", "A", "-", "doctrine §3.2 KY (intermediate court from 1 Jan 1976)", "S")],
      id_era="A")
canon("MD-COA", S["Maryland"], "Court of Appeals of Maryland",
      [(0, 20221213, "Court of Appeals of Maryland", "L", "all", "doctrine §3.2 MD", "L"),
       (20221214, D, "Supreme Court of Maryland", "L", "all",
        "doctrine §3.2 MD (renamed 14 Dec 2022, verified mdcourts.gov press release; data ends 2019)", "S")])
canon("MD-CSA", S["Maryland"], "Court of Special Appeals of Maryland",
      [(0, 20221213, "Court of Special Appeals of Maryland", "A", "-", "doctrine §4.3 MD", "L"),
       (20221214, D, "Appellate Court of Maryland", "A", "-", "doctrine §4.3 MD (renamed 14 Dec 2022, verified)", "S")])
canon("MA-PROV", S["Massachusetts"], "Superior Court of Judicature of the Province of Massachusetts Bay",
      [(0, D, "Superior Court of Judicature of the Province of Massachusetts Bay", "L", "all",
        "provincial high court (predecessor of the SJC); v1 had T", "L")])
canon("MA-APP", S["Massachusetts"], "Massachusetts Appeals Court",
      [(0, D, "Massachusetts Appeals Court", "A", "-", "audit §5 mis-tiered T; doctrine §4.3 MA (1972)", "L")])
canon("MA-APPDIV", S["Massachusetts"], "Massachusetts Appellate Division",
      [(0, D, "Massachusetts Appellate Division", "D", "-",
        "doctrine §4.4 (District Court Appellate Division: appellate division of a trial court)", "S")])
canon("NJ-CEA", S["New Jersey"], "New Jersey Court of Errors and Appeals",
      [(0, 19480914, "New Jersey Court of Errors and Appeals", "L", "all",
        "doctrine §3.2 NJ (last resort before 15 Sept 1948)", "L")] + [
       (19480915, D, "New Jersey Court of Errors and Appeals", "L", "all", "abolished 15 Sept 1948", "L")])
canon("NJ-OLDSC", S["New Jersey"], "Supreme Court of New Jersey",
      [(0, 19480914, "Supreme Court of New Jersey (before 15 Sept 1948)", "A", "-",
        "doctrine §3.2 NJ: the old Supreme Court was not the court of last resort", "L")], id_era="A")
canon("NJ-SC", S["New Jersey"], "Supreme Court of New Jersey",
      [(19480915, D, "Supreme Court of New Jersey", "L", "all", "doctrine §3.2 NJ (est. 15 Sept 1948)", "L")], id_era="L")
canon("NJ-AD", S["New Jersey"], "New Jersey Superior Court, Appellate Division",
      [(0, D, "New Jersey Superior Court, Appellate Division", "A", "-", "doctrine S-NJ (1948)", "S")])
canon("NY-CORR", S["New York"], "New York Court for the Correction of Errors",
      [(0, D, "New York Court for the Trial of Impeachments and the Correction of Errors", "L", "all",
        "doctrine §3.2 NY (last resort 1777-1847)", "L")])
canon("NY-JUD", S["New York"], "New York Supreme Court of Judicature",
      [(0, D, "New York Supreme Court of Judicature", "A", "-",
        "doctrine §3.2 NY: below the Court for the Correction of Errors (v1 had L)", "L")])
canon("NY-GT", S["New York"], "New York Supreme Court, General Term",
      [(0, D, "New York Supreme Court, General Term", "A", "-", "doctrine §3.2 NY (intermediate 1847-1895)", "L")])
canon("NY-AD", S["New York"], "New York Supreme Court, Appellate Division",
      [(0, D, "New York Supreme Court, Appellate Division", "A", "-", "doctrine S-NY (since 1 Jan 1896)", "S")])
canon("NY-AT", S["New York"], "New York Supreme Court, Appellate Term",
      [(0, D, "New York Supreme Court, Appellate Term", "D", "-", "doctrine S-NY / §4.4 (Appellate Term)", "L")])
canon("NY-COMM", S["New York"], "New York Commission of Appeals",
      [(0, D, "New York Commission of Appeals", "S", "-", "doctrine §3.2 NY / H4 (1870-1875)", "U")])
canon("OK-CCA", S["Oklahoma"], "Oklahoma Court of Criminal Appeals",
      [(0, 19581231, "Criminal Court of Appeals of Oklahoma", "L", "criminal",
        "doctrine H2 (Okla. Const. art. VII §4; renamed 1959, day uncertain)", "L"),
       (19590101, D, "Oklahoma Court of Criminal Appeals", "L", "criminal", "doctrine H2", "S")])
canon("OK-SC", S["Oklahoma"], "Oklahoma Supreme Court",
      [(0, D, "Oklahoma Supreme Court", "L", "civil", "doctrine H2 (civil court of last resort)", "S")])
canon("OK-COCA", S["Oklahoma"], "Oklahoma Court of Civil Appeals",
      [(0, D, "Oklahoma Court of Civil Appeals", "A", "-", "doctrine §4.3 OK (4 divisions)", "L")])
canon("IND-TERR", S["Indian Territory"], "Court of Appeals of Indian Territory",
      [(0, D, "Court of Appeals of Indian Territory", "L", "all",
        "highest court of Indian Territory (1895-1907); v1 had A", "L")])
canon("SC-OLDCOA", S["South Carolina"], None,
      [(0, D, "South Carolina Court of Appeals (1824-1868, court of last resort)", "L", "all",
        "SC Court of Appeals before 1868 was the court of last resort (v1 merged it with the 1983 IAC)", "L")])
canon("SC-COA", S["South Carolina"], "South Carolina Court of Appeals",
      [(0, D, "South Carolina Court of Appeals", "A", "-", "doctrine §4.3 SC (1983)", "L")])
canon("TN-CCA", S["Tennessee"], "Tennessee Court of Criminal Appeals",
      [(0, D, "Tennessee Court of Criminal Appeals", "A", "-", "audit §5 mis-tiered T; doctrine §4.3 TN (1967)", "L")])
canon("TN-COA", S["Tennessee"], "Tennessee Court of Appeals",
      [(0, D, "Tennessee Court of Appeals", "A", "-", "doctrine §4.3 TN (1925)", "L")])
canon("TX-SC", S["Texas"], "Supreme Court of Texas",
      [(0, D, "Supreme Court of Texas", "L", "civil", "doctrine H2 (Tex. Const. art. V §3)", "S")])
canon("TX-CCA", S["Texas"], "Texas Court of Criminal Appeals",
      [(0, 18910731, "Texas Court of Appeals (1876-1891)", "L", "criminal",
        "doctrine H2: the CCA was the Court of Appeals 1876-1891 (criminal and some civil)", "L"),
       (18910801, D, "Texas Court of Criminal Appeals", "L", "criminal", "doctrine H2 (Tex. Const. art. V §5)", "S")])
canon("TX-COA", S["Texas"], "Texas Courts of Appeals",
      [(0, 19810831, "Texas Courts of Civil Appeals", "A", "-",
        "audit §5 mis-tiered T; doctrine S-TX (Courts of Civil Appeals until 1 Sept 1981)", "L"),
       (19810901, D, "Texas Courts of Appeals", "A", "-", "doctrine S-TX (renamed 1 Sept 1981, criminal jurisdiction added)",
        "L")])
canon("TX-COMM", S["Texas"], "Texas Commission of Appeals",
      [(0, D, "Texas Commission of Appeals", "S", "-",
        "doctrine §3.2 TX / H4 (1879-1892, 1918-1945; adopted opinions carry Supreme Court authority)", "S")])
canon("VA-SC", S["Virginia"], "Supreme Court of Appeals of Virginia",
      [(0, 18301231, "Court of Appeals of Virginia (court of last resort, to 1830)", "L", "all",
        "renamed Supreme Court of Appeals under the 1830 constitution (date uncertain)", "U"),
       (18310101, 19710630, "Supreme Court of Appeals of Virginia", "L", "all", "doctrine §3.2 VA", "L"),
       (19710701, D, "Supreme Court of Virginia", "L", "all", "doctrine §3.2 VA (renamed 1 July 1971)", "L")])
canon("VA-COA", S["Virginia"], "Court of Appeals of Virginia",
      [(19850101, D, "Court of Appeals of Virginia", "A", "-", "doctrine §4.3 VA (1985)", "L")], id_era="A")
canon("VA-SPEC", S["Virginia"], "Special Court of Appeals of Virginia",
      [(0, D, "Special Court of Appeals of Virginia", "L", "all",
        "temporary court sitting with Supreme Court of Appeals authority (1870s-1920s)", "U")])
canon("WV-ICA", S["West Virginia"], None,
      [(0, D, "Intermediate Court of Appeals of West Virginia", "A", "-",
        "doctrine §4.3 WV (1 July 2022; no decisions in the data)", "L")])
canon("KS-OLDCOA", S["Kansas"], None,
      [(0, D, "Kansas Court of Appeals (1895-1901)", "A", "-", "doctrine §4.3 KS (earlier court 1895-1901)", "L")])
canon("KS-COA", S["Kansas"], "Kansas Court of Appeals",
      [(0, D, "Kansas Court of Appeals", "A", "-", "doctrine §4.3 KS (1977)", "L")])
canon("CO-OLDCOA", S["Colorado"], None,
      [(0, D, "Colorado Court of Appeals (1891-1905, 1913-1917)", "A", "-", "doctrine §4.3 CO (earlier courts)", "L")])
canon("CO-COA", S["Colorado"], "Colorado Court of Appeals",
      [(0, D, "Colorado Court of Appeals", "A", "-", "doctrine §4.3 CO (1970)", "L")])
canon("IN-COA", S["Indiana"], "Court of Appeals of Indiana",
      [(0, 19711231, "Appellate Court of Indiana", "A", "-", "doctrine §4.3 IN (Appellate Court; renamed 1971)", "L"),
       (19720101, D, "Court of Appeals of Indiana", "A", "-", "doctrine §4.3 IN (rename date approximate)", "U")])
canon("MO-COA", S["Missouri"], "Missouri Court of Appeals",
      [(0, 19711231, "Missouri Courts of Appeals (St. Louis, Kansas City, Springfield)", "A", "-",
        "doctrine S-MO (separate courts before 1972)", "L"),
       (19720101, D, "Missouri Court of Appeals", "A", "-", "doctrine S-MO (unified 1 Jan 1972)", "L")])
canon("FL-DCA", S["Florida"], "Florida District Court of Appeal",
      [(0, D, "Florida District Courts of Appeal", "A", "-", "doctrine S-FL", "S")])
canon("CA-COA", S["California"], "Court of Appeal of the State of California",
      [(0, 19661107, "District Court of Appeal of the State of California", "A", "-",
        "doctrine S-CA (Courts of Appeal 1905; 'District Courts of Appeal' until the 1966 revision)", "L"),
       (19661108, D, "Court of Appeal of the State of California", "A", "-", "doctrine S-CA (rename date approximate)", "U")])
canon("CA-APPDIV", S["California"], "Appellate Division of the Superior Court of the State of California",
      [(0, D, "Appellate Division of the Superior Court of the State of California", "D", "-", "doctrine S-CA / §4.4", "S")])
canon("LA-COA", S["Louisiana"], "Louisiana Court of Appeal",
      [(0, D, "Louisiana Courts of Appeal", "A", "-", "doctrine S-LA (circuits)", "S")])
canon("OH-COA", S["Ohio"], "Ohio Court of Appeals",
      [(0, D, "Ohio Courts of Appeals", "A", "-", "doctrine S-OH (12 districts)", "S")])
canon("IL-APP", S["Illinois"], "Illinois Appellate Court",
      [(0, D, "Illinois Appellate Court", "A", "-", "doctrine S-IL (districts)", "S")])
canon("WA-COA", S["Washington"], "Washington Court of Appeals",
      [(0, D, "Washington Court of Appeals", "A", "-", "doctrine S-WA (3 divisions, 1969)", "S")])
canon("AZ-COA", S["Arizona"], "Arizona Court of Appeals",
      [(0, D, "Arizona Court of Appeals", "A", "-", "doctrine S-AZ (Divisions One and Two, 1965)", "S")])
canon("PR-TA", S["Puerto Rico"], "Puerto Rico Circuit Court of Appeals",
      [(0, 20030630, "Tribunal de Circuito de Apelaciones de Puerto Rico", "A", "-",
        "doctrine §4.3 PR (1992); v1 had federal T", "U"),
       (20030701, D, "Tribunal de Apelaciones de Puerto Rico", "A", "-", "doctrine §4.3 PR (renamed 2003)", "U")])
canon("VI-SC", S["Virgin Islands"], "Supreme Court of the Virgin Islands",
      [(0, D, "Supreme Court of the Virgin Islands", "L", "all", "doctrine §3.2 VI (first sat Jan 2007); v1 had T", "L")])
canon("AS-HC", S["American Samoa"], "High Court of American Samoa",
      [(0, D, "High Court of American Samoa", "L", "all",
        "doctrine §3.2 AS (its Appellate Division is last resort; name mixes trial and appellate divisions)", "U")])
canon("NMI-SC", S["Northern Mariana Islands"], "Commonwealth of the Northern Mariana Islands Supreme Court",
      [(0, D, "Commonwealth of the Northern Mariana Islands Supreme Court", "L", "all", "doctrine §3.2 NMI (1989); v1 had T",
        "L")])
canon("DAK-SC", S["Dakota Territory"], "Supreme Court of Dakota",
      [(0, D, "Supreme Court of Dakota Territory", "L", "all", "doctrine §3.2 ND (Dakota Territory, 1861-1889); v1 had T",
        "L")])
canon("NAV-SC", 61, "Navajo Nation Supreme Court",
      [(0, D, "Navajo Nation Supreme Court", "L", "all", "doctrine §3.2 tribal (separate system)", "L")])
canon("NAV-COA", 61, "Navajo Nation Court of Appeals",
      [(0, D, "Navajo Nation Court of Appeals", "L", "all", "predecessor of the Navajo Nation Supreme Court (1985)", "L")])
canon("WV-SCA", S["West Virginia"], "Supreme Court of Appeals of West Virginia",
      [(0, D, "Supreme Court of Appeals of West Virginia", "L", "all", "doctrine §3.2 WV", "L")])

# units of intermediate courts (and the old Fifth Circuit's administrative units): key -> [(unit, name, from, src, tag)]
TXC = ["Houston [1st Dist.] (Galveston before 1957)", "Fort Worth", "Austin", "San Antonio", "Dallas", "Texarkana",
       "Amarillo", "El Paso", "Beaumont", "Waco", "Eastland", "Tyler", "Corpus Christi-Edinburg", "Houston [14th Dist.]",
       "Fifteenth Court of Appeals (statewide)"]
TXY = [18920101, 18920101, 18920101, 18920101, 18930101, 19070101, 19110101, 19110101, 19150101, 19230101, 19250101,
       19630101, 19630101, 19670101, 20240901]
UNITS = {
    "FL-DCA": [(k, "District Court of Appeal of Florida, %s District" % w, f, "doctrine S-FL", "L" if k < 6 else "L")
               for k, w, f in ((1, "First", 19570701), (2, "Second", 19570701), (3, "Third", 19570701),
                               (4, "Fourth", 19650701), (5, "Fifth", 19790701), (6, "Sixth", 20230101))],
    "TX-COA": [(k + 1, "Court of Appeals of Texas, " + TXC[k], TXY[k], "doctrine S-TX (seats from memory)", "L")
               for k in range(15)],
    "CA-COA": [(k, "Court of Appeal of California, %s Appellate District" % w, f, "doctrine S-CA", "L")
               for k, w, f in ((1, "First", 19050101), (2, "Second", 19050101), (3, "Third", 19050101),
                               (4, "Fourth", 19290101), (5, "Fifth", 19610101), (6, "Sixth", 19840101))],
    "NY-AD": [(k, "Appellate Division, %s Department" % w, 18960101, "doctrine S-NY", "S")
              for k, w in ((1, "First"), (2, "Second"), (3, "Third"), (4, "Fourth"))],
    "NY-AT": [(k, "Appellate Term, %s Department" % w, 18960101, "doctrine S-NY (Appellate Term by department)", "L")
              for k, w in ((1, "First"), (2, "Second"))],
    "LA-COA": [(k, "Court of Appeal of Louisiana, %s Circuit" % w, f, "doctrine S-LA", "L")
               for k, w, f in ((1, "First", 19600701), (2, "Second", 19600701), (3, "Third", 19600701),
                               (4, "Fourth", 19600701), (5, "Fifth", 19820101))],
    "OH-COA": [(k, "Court of Appeals of Ohio, %s District" % w, 19130101, "doctrine S-OH (creation dates of districts "
                "10-12 not verified)", "U" if k >= 10 else "L")
               for k, w in enumerate("First Second Third Fourth Fifth Sixth Seventh Eighth Ninth Tenth Eleventh Twelfth"
                                     .split(), 1)],
    "IL-APP": [(k, "Illinois Appellate Court, %s District" % w, 18770101 if k <= 4 else 19640101, "doctrine S-IL", "L")
               for k, w in enumerate("First Second Third Fourth Fifth".split(), 1)],
    "MO-COA": [(1, "Missouri Court of Appeals, Eastern District (St. Louis Court of Appeals before 1972)", 18750101,
                "doctrine S-MO", "L"),
               (2, "Missouri Court of Appeals, Western District (Kansas City Court of Appeals before 1972)", 18840101,
                "doctrine S-MO", "L"),
               (3, "Missouri Court of Appeals, Southern District (Springfield Court of Appeals before 1972)", 19090101,
                "doctrine S-MO", "L")],
    "WA-COA": [(k, "Washington Court of Appeals, Division %s" % w, 19690801, "doctrine S-WA", "L")
               for k, w in ((1, "One"), (2, "Two"), (3, "Three"))],
    "AZ-COA": [(k, "Arizona Court of Appeals, Division %s" % w, 19650101, "doctrine S-AZ", "S")
               for k, w in ((1, "One"), (2, "Two"))],
    "IN-COA": [(k, "Court of Appeals of Indiana, %s District" % w, 19720101, "doctrine §4.3 IN (5 districts; dates not "
                "verified)", "U") for k, w in enumerate("First Second Third Fourth Fifth".split(), 1)],
    "OK-COCA": [(k, "Oklahoma Court of Civil Appeals, Division %d" % k, 19700101, "doctrine §4.3 OK (4 divisions)", "L")
                for k in (1, 2, 3, 4)],
    "TN-COA": [(k, "Tennessee Court of Appeals, %s Section" % w, 19250101, "grand divisions (no precedential effect: "
                "TN horizontal strong statewide)", "L") for k, w in ((1, "Eastern"), (2, "Middle"), (3, "Western"))],
    "TN-CCA": [(k, "Tennessee Court of Criminal Appeals, %s Section" % w, 19670101, "grand divisions", "L")
               for k, w in ((1, "Eastern"), (2, "Middle"), (3, "Western"))],
    "CA5": [(1, "Former Fifth Circuit, Unit A", 19801001, "doctrine F10 (administrative units in the last year)", "L"),
            (2, "Former Fifth Circuit, Unit B", 19801001, "doctrine F10 (Unit B decisions bind the 11th Cir.)", "L")],
}
UNIT_TO = {("CA5", 1): 19811231, ("CA5", 2): 19821231, ("TX-COA", 15): D}

# ------------------------------------------------------------------------------------------------ name routing


def ordnum(w):
    return ORDN.get(w) or ORDN.get(w.capitalize())


def name_unit(name, key):
    """The unit given by a court name (0 if none)."""
    if key == "TX-COA":
        for k, c in enumerate(["Houston (1st", "Fort Worth", "Austin", "San Antonio", "Dallas", "Texarkana", "Amarillo",
                               "El Paso", "Beaumont", "Waco", "Eastland", "Tyler", "Corpus Christi", "Houston (14th"]):
            if c in name:
                return k + 1
        return 0
    if key in ("TN-COA", "TN-CCA"):
        for k, c in ((1, "KNOXVILLE"), (2, "NASHVILLE"), (3, "JACKSON")):
            if c in name.upper():
                return k
        return 0
    m = re.search(r"\b(%s) (?:Appellate )?(?:District|Department|Circuit)\b" % "|".join(ORDN), name)
    if m and key in ("FL-DCA", "CA-COA", "NY-AD", "NY-AT", "LA-COA", "OH-COA", "IL-APP", "IN-COA"):
        return ordnum(m.group(1))
    if key == "MO-COA":
        for k, c in ((1, "Eastern"), (2, "Western"), (3, "Southern")):
            if c in name:
                return k
    if key in ("WA-COA", "AZ-COA", "OK-COCA"):
        m = re.search(r"Division(?: No\.)? (\w+)", name)
        if m:
            return ordnum(m.group(1)) or 0
    return 0


def route(name, sysid, tier, rule, years):
    """[(from, to, key, unit, src)] for one v1 court name; key None = keep the v1 court (default)."""
    n = name
    st = STATES[sysid - 1] if 0 < sysid <= len(STATES) else None

    def one(key, src):
        return [(0, D, key, name_unit(n, key), src)]
    if sysid == 0:
        if re.search(r"^United States Court of Appeals for the Six Circuit$", n):
            return one("CA6", "alias:name-typo")
        if re.search(r"^United States Court of Appeals for the Ninth$", n):
            return one("CA9", "alias:name-truncated")
        if n == "United States Court of Appeals for the Fifth Circuit":
            return one("CA5", "canonical")
        if re.search(r"^(United States )?Court of Appeals (for|of) the District of Columbia( Circuit)?$", n):
            return one("CADC", "alias:dc-circuit-names")
        if n == "United States Court of Appeals for the Federal Circuit":
            return one("CAFC", "canonical")
        if re.search(r"Court of Customs and Patent Appeals", n):
            return one("CCPA", "alias")
        if n == "United States Court of Claims":
            return one("CTCL", "canonical")
        if n == "United States Claims Court":
            return [(0, 19820930, "CTCL", 0, "alias:pre-1982 'Claims Court' = Court of Claims"),
                    (19821001, D, "CFC", 0, "alias")]
        if n == "United States Court of Federal Claims":
            return one("CFC", "canonical")
        if n in ("United States Customs Court", "United States Court of International Trade"):
            return one("CIT", "alias")
        if n in ("United States Board of Tax Appeals", "United States Tax Court"):
            return one("TAX", "alias")
        if n in ("United States Court of Military Appeals", "United States Court of Appeals for the Armed Forces"):
            return one("CAAF", "alias")
        for svc, pat in (("ARMY", "Army"), ("AF", "Air Force"), ("NMC", "Navy-Marine Corps"), ("CG", "Coast Guard")):
            if re.search(r"^United States %s Court of (Military Review|Criminal Appeals)$" % pat, n):
                return one("CCA-" + svc, "alias")
        if n in ("United States Court of Veterans Appeals", "United States Court of Appeals for Veterans Claims"):
            return one("CAVC", "alias")
        if n == "United States Supreme Court of the District of Columbia":
            return one("SCDC", "fix:audit §5 (v1 mapped to SCOTUS rule)")
        return [(0, D, None, 0, "")]
    if n in ("Court of Appeals of the District of Columbia",):
        return [(0, 19621231, "CADC", 0, "alias:federal Court of Appeals of D.C. (1893-)"),
                (19630101, D, "DCCA", 0, "alias")]
    if n == "District of Columbia Court of Appeals":
        return [(0, 19411231, "CADC", 0, "alias:pre-1942 decisions under this name are the federal Court of Appeals of D.C."),
                (19420101, D, "DCCA", 0, "canonical")]
    if n == "District of Columbia Municipal Court of Appeals":
        return one("DCCA", "alias")
    if n == "Supreme Court of the District of Columbia":
        return one("SCDC", "canonical")
    if st == "Alabama":
        if re.search(r"Court of Criminal Appeals", n):
            return one("AL-CRIM", "alias")
        if re.search(r"Court of Civil Appeals", n):
            return one("AL-CIV", "alias")
        if n == "Alabama Court of Appeals":
            return one("AL-COA", "canonical")
    if st == "Connecticut" and re.search(r"^(Connecticut Supreme Court|Supreme Court of Errors of the State of "
                                         r"Connecticut|Supreme Court of Connecticut)$", n):
        return one("CT-SC", "alias")
    if st == "Delaware":
        if n == "Delaware Court of Errors and Appeals":
            return one("DE-CEA", "canonical")
        if n in ("Delaware Supreme Court", "Supreme Court of Delaware"):
            return one("DE-SC", "alias")
    if st == "Hawaii":
        if n == "Supreme Court of the Territory of Hawaii":
            return one("HI-TERR", "fix:tier")
        if n == "Supreme Court of the Republic of Hawaii":
            return one("HI-REP", "fix:tier")
    if st == "Kentucky" and re.search(r"^(Kentucky Court of Appeals|Court of Appeals of Kentucky)$", n):
        return [(0, 19751231, "KY-OLDCOA", 0, "era:doctrine §3.2 KY"), (19760101, D, "KY-COA", 0, "era:doctrine §3.2 KY")]
    if st == "Maryland":
        if n in ("Court of Appeals of Maryland", "Maryland Court of Appeals", "Supreme Court of Maryland"):
            return one("MD-COA", "alias")
        if n in ("Court of Special Appeals of Maryland", "Maryland Court of Special Appeals", "Maryland Appellate Reports",
                 "Appellate Court of Maryland"):
            return one("MD-CSA", "alias" + (":audit §5 reporter name used as a court" if "Reports" in n else ""))
    if st == "Massachusetts":
        if n == "Superior Court of Judicature of the Province of Massachusetts Bay":
            return one("MA-PROV", "fix:tier")
        if re.search(r"^(Massachusetts Appeals Court|Appeals Court of Massachusetts)$", n):
            return one("MA-APP", "fix:audit §5 mis-tiered")
        if re.search(r"^Massachusetts Appellate (Division|Decisions)$", n):
            return one("MA-APPDIV", "fix:tier D")
    if st == "New Jersey":
        if n == "New Jersey Court of Errors and Appeals":
            return one("NJ-CEA", "canonical")
        if n in ("Supreme Court of New Jersey", "New Jersey Supreme Court"):
            return [(0, 19480914, "NJ-OLDSC", 0, "era:doctrine §3.2 NJ (15 Sept 1948)"),
                    (19480915, D, "NJ-SC", 0, "era:doctrine §3.2 NJ (15 Sept 1948)")]
        if re.search(r"Superior Court,? Appellate Division|Superior Court of New Jersey, Appellate Division", n):
            return one("NJ-AD", "alias")
    if st == "New York":
        if n in ("New York Court for the Correction of Errors", "New York Court of Errors"):
            return one("NY-CORR", "alias")
        if n == "New York Supreme Court of Judicature":
            return one("NY-JUD", "fix:tier (doctrine §3.2 NY)")
        if re.search(r"^New York Supreme Court,? General Term$", n):
            return one("NY-GT", "alias")
        if re.search(r"Appellate Division", n) and not re.search(r"Superior|City|County", n):
            return one("NY-AD", "alias")
        if re.search(r"Appellate Term", n):
            return one("NY-AT", "alias")
        if n == "New York Commission of Appeals":
            return one("NY-COMM", "canonical")
    if st == "Oklahoma" or n == "Court of Appeals of Indian Territory":
        if re.search(r"Court of Criminal Appeals|Criminal Court of Appeals", n):
            return one("OK-CCA", "alias")
        if n in ("Oklahoma Supreme Court", "Supreme Court of Oklahoma"):
            return one("OK-SC", "canonical")
        if re.search(r"Court of Civil Appeals|^Court of Appeals of Oklahoma$", n):
            return one("OK-COCA", "alias")
        if n == "Court of Appeals of Indian Territory":
            return one("IND-TERR", "fix:tier")
    if st == "South Carolina" and re.search(r"^(South Carolina Court of Appeals|Court of Appeals of South Carolina)$", n):
        return [(0, 19821231, "SC-OLDCOA", 0, "era:pre-1868 Court of Appeals (last resort)"),
                (19830101, D, "SC-COA", 0, "era:IAC (1983)")]
    if st == "Tennessee":
        if re.search(r"Court of Criminal Appeals", n):
            return one("TN-CCA", "alias")
        if re.search(r"^(Tennessee Court of Appeals|Court of Appeals of Tennessee.*)$", n):
            return one("TN-COA", "alias")
    if st == "Texas":
        if n in ("Supreme Court of Texas", "Texas Supreme Court"):
            return one("TX-SC", "canonical")
        if re.search(r"Court of Criminal Appeals", n):
            return one("TX-CCA", "alias")
        if n == "Texas Courts of Appeals":
            return [(0, 18910731, "TX-CCA", 0, "era:doctrine H2 (Court of Appeals 1876-1891 = CCA predecessor)"),
                    (18910801, D, "TX-COA", 0, "canonical")]
        if re.search(r"^Texas Courts? of (Civil )?Appeals$|^Court of Appeals of Texas", n):
            return one("TX-COA", "alias")
        if n == "Texas Commission of Appeals":
            return one("TX-COMM", "canonical")
    if st == "Virginia":
        if n in ("Supreme Court of Appeals of Virginia", "Supreme Court of Virginia"):
            return one("VA-SC", "alias")
        if n == "Court of Appeals of Virginia" or re.search(r"^Court of Appeals of Virginia, ", n):
            return [(0, 19841231, "VA-SC", 0, "era:old Court of Appeals of Virginia (last resort)"),
                    (19850101, D, "VA-COA", 0, "era:IAC (1985)")]
        if n == "Special Court of Appeals of Virginia":
            return one("VA-SPEC", "fix:tier")
    if st == "West Virginia" and n == "Supreme Court of Appeals of West Virginia":
        return one("WV-SCA", "canonical")
    if st == "Kansas" and re.search(r"^(Kansas Court of Appeals|Court of Appeals of Kansas)$", n):
        return [(0, 19761231, "KS-OLDCOA", 0, "era:1895-1901 court"), (19770101, D, "KS-COA", 0, "era:1977 court")]
    if st == "Colorado" and re.search(r"^Colorado Court of Appeals(, Div)?", n):
        return [(0, 19691231, "CO-OLDCOA", 0, "era:pre-1970 courts"), (19700101, D, "CO-COA", 0, "era:1970 court")]
    if st == "Indiana" and n in ("Appellate Court of Indiana", "Court of Appeals of Indiana", "Indiana Court of Appeals"):
        return one("IN-COA", "alias")
    if st == "Missouri" or n == "Kansas City Court of Appeals":
        if n == "St. Louis Court of Appeals":
            return [(0, D, "MO-COA", 1, "alias:unit 1 (Eastern)")]
        if n == "Kansas City Court of Appeals":
            return [(0, D, "MO-COA", 2, "alias:unit 2 (Western); fix system (v1 had Kansas)")]
        if n == "Springfield Court of Appeals":
            return [(0, D, "MO-COA", 3, "alias:unit 3 (Southern)")]
        if re.search(r"^Missouri Court of Appeals", n):
            return one("MO-COA", "alias")
    if st == "Florida":
        if re.search(r"^(Florida District Court of Appeal|District Court of Appeal of Florida)", n):
            return one("FL-DCA", "alias")
    if st == "California":
        if re.search(r"^(Court of Appeal of the State of California|District Court of Appeal of the State of California|"
                     r"California Court of Appeal|Court of Appeal, \w+ District)", n):
            return one("CA-COA", "alias")
        if n == "Appellate Division of the Superior Court of the State of California":
            return one("CA-APPDIV", "fix:tier D")
    if st == "Louisiana" and re.search(r"^(Louisiana Court of Appeal|Court of Appeal of Louisiana)", n):
        return one("LA-COA", "alias")
    if st == "Ohio" and (re.search(r"^(Ohio Court of Appeals|Court of Appeals of Ohio)", n) or
                         n == "Hamilton County Court of Appeals"):
        return [(0, D, "OH-COA", name_unit(n, "OH-COA") or (1 if n.startswith("Hamilton") else 0), "alias")]
    if st == "Illinois" and re.search(r"^(Illinois Appellate Court|Appellate Court of Illinois)", n):
        return one("IL-APP", "alias")
    if st == "Washington" and re.search(r"^(Washington Court of Appeals|Court of Appeals of Washington)", n):
        return one("WA-COA", "alias")
    if st == "Arizona" and re.search(r"^(Arizona Court of Appeals|Court of Appeals of Arizona)", n):
        return one("AZ-COA", "alias")
    if st == "Puerto Rico" and re.search(r"Circuit Court of Appeals|Tribunal de (Circuito de )?Apelaciones", n):
        return one("PR-TA", "fix:system+tier")
    if st == "Virgin Islands" and n == "Supreme Court of the Virgin Islands":
        return one("VI-SC", "fix:tier")
    if st == "American Samoa" and n == "High Court of American Samoa":
        return one("AS-HC", "fix:tier")
    if st == "Northern Mariana Islands" and re.search(r"Supreme Court", n):
        return one("NMI-SC", "fix:tier")
    if st == "Dakota Territory" or n == "Supreme Court of Dakota":
        return one("DAK-SC", "fix:tier")
    if n == "Navajo Nation Supreme Court":
        return one("NAV-SC", "fix:tier")
    if n == "Navajo Nation Court of Appeals":
        return one("NAV-COA", "fix:tier")
    return [(0, D, None, 0, "")]


MERGE_KEYS = {"supreme court", "court of appeals", "intermediate court of appeals", "appellate court", "court of appeal",
              "supreme judicial court", "court of criminal appeals", "court of civil appeals", "commonwealth court",
              "superior court", "supreme court of appeals", "court of special appeals", "court of chancery",
              "court of claims", "tax court", "workers compensation commission", "court of common pleas"}


def norm_name(name, sysid):
    """Normalised court name used to merge spellings of one court (None when the name is not a plain court name)."""
    st = STATES[sysid - 1]
    n = name
    if st == "New York" and re.search(r"Supreme Court", n, re.I):
        return None
    n = re.sub(r",\s*(?:DIVISION|Division|Div\.)\s*\w+\.?$", "", n)
    n = re.sub(r"\b(?:of )?(?:the )?(?:State|Commonwealth) of\b", " ", n)
    n = re.sub(r"\b" + re.escape(st) + r"\b", " ", n)
    n = re.sub(r"[^A-Za-z ]", " ", n).lower()
    n = re.sub(r"\b(of|the|for)\b", " ", n)
    n = " ".join(n.split())
    n = {"supreme court appeals": "supreme court of appeals", "court appeals": "court of appeals",
         "intermediate court appeals": "intermediate court of appeals", "court appeal": "court of appeal",
         "court criminal appeals": "court of criminal appeals", "court civil appeals": "court of civil appeals",
         "court special appeals": "court of special appeals", "court chancery": "court of chancery",
         "court claims": "court of claims", "court common pleas": "court of common pleas"}.get(n, n)
    return n if n in MERGE_KEYS else None


GENERIC_APPEAL = re.compile(r"\bCourt of (?:Civil |Criminal )?Appeals?\b|\bAppeals Court\b|\bAppellate Court\b")
NOT_APPEAL = re.compile(r"Commission|Board|Tax|Claims|Workers|Industrial|Bankruptcy|Tribal|Discipl|Judicial Conduct|"
                        r"Compensation|Municipal|County|City|Parish|District Court\b")
SPECIAL_SYSTEMS = {S["Indian Territory"], S["Dakota Territory"], S["Hawaiian Kingdom"], S["Navajo Nation"], 61}


def main():
    names = {}
    for line in open(os.path.join(WORK, "graph/courts.tsv"), encoding="utf-8"):
        i, n, c, lo, hi = line.rstrip("\n").split("\t")
        names[i] = (n, int(c), int(lo), int(hi))
    rep = collections.defaultdict(collections.Counter)
    with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 4)
            rep[p[3]][p[1]] += 1
    v1 = []  # v1 id -> (graph idx, name, lo, hi, sys, tier, circ, rule)
    for line in open(os.path.join(WORK, "graph/court_table.tsv"), encoding="utf-8"):
        cid, name, lo, hi, sysid, sysname, tier, circ, rule = line.rstrip("\n").split("\t")
        v1.append((cid, name, int(lo), int(hi), int(sysid), T1[tier], int(circ), rule))
    unmapped = [line.rstrip("\n").split("\t")[1] for line in open(os.path.join(WORK, "graph/court_unmapped.tsv"),
                                                                     encoding="utf-8")]
    gidx = {n: i for i, (n, *_r) in names.items()}

    # fix systems from the repo (state courts whose name holds another state's name, e.g. "Delaware County ...")
    fixes = []
    sysfix = {}
    for vid, (cid, name, lo, hi, sysid, tier, circ, rule) in enumerate(v1):
        top = rep[cid].most_common(1)
        rs = repo_state(top[0][0]) if top else None
        if rs is None:
            continue
        if sysid == 0 and rule in ("national-court", "district") and tier == "S":
            sysfix[vid] = (SYS[rs], "fix:state court mapped federal (repo %s)" % top[0][0])
        elif sysid == 0 and name == "Puerto Rico Circuit Court of Appeals":
            sysfix[vid] = (SYS[rs], "fix:PR state court mapped federal")
        elif sysid not in (0,) and sysid not in SPECIAL_SYSTEMS and SYS[rs] != sysid and name != "Court of Appeals of Indian Territory":
            sysfix[vid] = (SYS[rs], "fix:system from repo %s (v1 read %s from the name)" % (top[0][0], STATES[sysid - 1]))

    # canonical ids
    by_name = collections.defaultdict(list)
    for vid, r in enumerate(v1):
        by_name[r[1]].append(vid)
    next_id = [10000]
    cid_of = {}
    for key, c in CANON.items():
        vid = None
        if c["id_name"] and c["id_name"] in by_name:
            ids = by_name[c["id_name"]]
            if len(ids) == 1:
                vid = ids[0]
            else:
                vid = ids[0] if c["id_era"] == v1[ids[0]][5] else ids[1]
        if vid is None:
            vid = next_id[0]
            next_id[0] += 1
        cid_of[key] = vid

    # per v1 court: segments
    rows = {}  # court2 id -> epochs list
    alias = []  # (v1 id, graph idx, name, from, to, court2 id, unit, src)
    default_epoch = {}
    retier_n = collections.Counter()
    pending = collections.defaultdict(list)
    for vid, (cid, name, lo, hi, sysid, tier, circ, rule) in enumerate(v1):
        if vid in sysfix:
            sysid, why = sysfix[vid]
            fixes.append((vid, name, why))
            if circ and sysid:
                circ = 0
        segs = route(name, sysid, tier, rule, (lo, hi))
        era = len(by_name[name]) == 2
        for a, b, key, unit, src in segs:
            if era and key is None:
                a, b = (0, hi * 10000 + 1231) if hi < 9999 else (lo * 10000 + 101, D)
            if key is None:
                t2 = tier
                lrf = "all" if t2 == "L" else "-"
                tag = "-"
                s2 = "v1:" + rule
                if rule == "bap":
                    t2 = "B"
                    s2 = "v1:bap; doctrine F13 (tier B)"
                if sysid > 0 and t2 in "TS" and GENERIC_APPEAL.search(name) and not NOT_APPEAL.search(name):
                    t2, s2, tag = "A", "fix:mis-tiered appeals court (audit §5, generic)", "L"
                    retier_n[name] += names[cid][1]
                if sysid > 0 and rule in ("ny-appellate",) and re.search(r"General Term|Appellate Term", name) and \
                        re.search(r"City|Superior|Common Pleas|Marine", name):
                    t2, s2, tag = "D", "fix:general term of a trial court (doctrine §4.4)", "L"
                if sysid == 0 and re.search(r"Court of Criminal Appeals|Court of Military Review", name):
                    t2, s2, tag = "S", "fix:military intermediate court (v1 had T)", "L"
                if sysid > 0:
                    circ = 0
                gk = norm_name(name, sysid) if (sysid > 0 and sysid not in SPECIAL_SYSTEMS and not era) else None
                if gk in ("supreme court", "supreme judicial court", "supreme court of appeals") and t2 != "L":
                    t2, lrf, s2, tag = "L", "all", "fix:state supreme court mapped %s in v1" % t2, "L"
                ep = (a, b, name, sysid, t2, lrf, circ, 0, s2, tag)
                if gk:
                    pending[(sysid, t2, gk)].append((names[cid][1], vid, cid, name, ep))
                else:
                    rows.setdefault(vid, []).append(ep)
                    alias.append((vid, cid, name, a, b, vid, 0, "self"))
            else:
                alias.append((vid, cid, name, a, b, cid_of[key], unit, src))
                if src.startswith("fix") or "mis-tiered" in CANON[key]["epochs"][0][5]:
                    retier_n[name] += names[cid][1] if tier in "TS" and CANON[key]["epochs"][-1][3] in "AL" else 0
    # name variants of one court (same system, tier and normalised name) share the id of the most frequent name
    merged = 0
    for (sysid, t2, gk), mem in pending.items():
        mem.sort(reverse=True)
        cnt, cvid, ccid, cname, cep = mem[0]
        rows.setdefault(cvid, []).append(cep)
        for cnt2, vid, cid, name, ep in mem:
            u = 0
            if len(mem) > 1 and vid != cvid:
                merged += 1
            alias.append((vid, cid, name, ep[0], ep[1], cvid, u,
                          "self" if vid == cvid else "alias:name variant of '%s'" % cname))
    print("name variants merged", merged)
    # unmapped names (court id 3160 in v1) that can be placed
    UNM = {"Court of Customs and Patent Appeals": ("CCPA", None),
           "Judicial Council of the Ninth Circuit": (None, (0, "S", 9)),
           "Judicial Council of the Eighth Circuit": (None, (0, "S", 8)),
           "Judicial Council of the Second Circuit": (None, (0, "S", 2)),
           "Judicial Council of the Seventh Circuit": (None, (0, "S", 7)),
           "Judicial Council of the Third Circuit": (None, (0, "S", 3)),
           "Judicial Council of the Tenth Circuit": (None, (0, "S", 10)),
           "Judicial Council of the Sixth Circuit": (None, (0, "S", 6)),
           "Judicial Council of the Fifth Circuit": (None, (0, "S", 5)),
           "Court of Appeals in Cases of Capture": (None, (0, "S", 0)),
           "Special Court, Regional Rail Reorganization Act": (None, (0, "S", 0))}
    for nm in unmapped:
        g = gidx.get(nm)
        if nm in UNM:
            key, spec = UNM[nm]
            if key:
                alias.append((3160, g, nm, 0, D, cid_of[key], 0, "fix:unmapped name (audit §5)"))
                continue
            sysid, t2, circ = spec
        elif re.search(r"Tribe|Tribal|Nation|Mohegan|Hopi|Navajo|Salish|Grand Ronde|Cherokee|Fort Peck|Window Rock|"
                       r"Crownpoint|Shiprock|Chinle|Elders", nm):
            sysid, t2, circ = 61, "S", 0
        else:
            alias.append((3160, g, nm, 0, D, 3160, 0, "unmapped"))
            continue
        vid = next_id[0]
        next_id[0] += 1
        rows[vid] = [(0, D, nm, sysid, t2, "-", circ, 0, "fix:unmapped name (audit §5)", "-")]
        alias.append((3160, g, nm, 0, D, vid, 0, "fix:unmapped name"))
    rows[3160] = [(0, D, "(unmapped court)", 999, "T", "-", 0, 0, "v1:unmapped", "-")]

    # canonical epochs
    for key, c in CANON.items():
        vid = cid_of[key]
        rows[vid] = [(a, b, nm, c["system"], t, lrf, c["circuit"], 0, src, tag) for a, b, nm, t, lrf, src, tag in c["epochs"]]
    # unit rows
    unit_id = {}
    for key, us in UNITS.items():
        par = cid_of[key]
        sysid = CANON[key]["system"]
        tier = CANON[key]["epochs"][-1][3]
        for u, nm, frm, src, tag in us:
            vid = next_id[0]
            next_id[0] += 1
            unit_id[(key, u)] = vid
            to = UNIT_TO.get((key, u), D)
            rows[vid] = [(frm, to, nm, sysid, tier, "-", CANON[key]["circuit"], u, "unit-of:%d; %s" % (par, src), tag)]
    # the old Missouri courts as unit rows of their own (succession to the 1972 districts)
    extra = {}
    for k, nm, frm in ((1, "St. Louis Court of Appeals", 18750101), (2, "Kansas City Court of Appeals", 18840101),
                       (3, "Springfield Court of Appeals", 19090101)):
        vid = next_id[0]
        next_id[0] += 1
        extra[("MO-OLD", k)] = vid
        rows[vid] = [(frm, 19711231, nm, S["Missouri"], "A", "-", 0, k,
                      "unit-of:%d; doctrine S-MO (separate court before 1 Jan 1972)" % cid_of["MO-COA"], "L")]
    # Missouri district unit rows start 1972
    for k in (1, 2, 3):
        vid = unit_id[("MO-COA", k)]
        a, b, nm, sy, t, lrf, ci, u, src, tag = rows[vid][0]
        rows[vid] = [(19720101, b, nm.split(" (")[0], sy, t, lrf, ci, u, src, tag)]

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "courts2.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for vid in sorted(rows):
            eps = sorted(rows[vid])
            for a, b, nm, sy, t, lrf, ci, u, src, tag in eps:
                if t == "L" and lrf == "-":
                    lrf = "all"
                f.write("\t".join(str(x) for x in (vid, a, b, nm, sy, t, lrf, ci, u, src, tag)) + "\n")
    with open(os.path.join(OUT, "court_alias.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for r in alias:
            f.write("\t".join(str(x) for x in r) + "\n")
    ids = {"cid_of": cid_of, "unit_id": {"%s|%d" % k: v for k, v in unit_id.items()},
           "mo_old": {"%s|%d" % k: v for k, v in extra.items()}}
    import json
    with open(os.path.join(OUT, "..", "work", "courts", "court_keys.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(ids, f, indent=1)
    print("courts2 rows", sum(len(v) for v in rows.values()), "courts", len(rows), "alias rows", len(alias),
          "system fixes", len(fixes))
    for vid, name, why in fixes[:50]:
        print("  sysfix", vid, name, "|", why)
    print("re-tiered (generic, decisions):", sum(retier_n.values()))
    for n, c in retier_n.most_common(60):
        print("  ", c, n)


if __name__ == "__main__":
    main()
