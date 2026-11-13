"""Fixes for the validated data limits 8, 9, 10, 11 and 13 (courts_validation.md §5), applied to the built data files.

    python -X utf8 limits_fix.py            (after decisions_build stage3 and the reader's certify step)

Reads each file's `<name>.pre_fix.tsv` backup when present (made on the first run), so a rerun gives the same result.
Every output is written to `<name>.tsv.tmp` and renamed over `<name>.tsv`.

- 8  uncertain dates: DATE_FIXES below (primary sources in src, tag S where confirmed).
- 9  history.tsv: `writRefused` only for the Texas Supreme Court's "writ refused"/"writ ref'd" notation. Rows from other
     systems (the Louisiana Supreme Court's "Writ refused." on a court-of-appeal judgment) become kind `other` with a
     src note; "n.r.e." rows are dropped. The reader (reader/scan.py, resolve.py) applies the same rule on a rerun.
- 10 Oklahoma (36) and Minnesota (23): a "MEMORANDUM OPINION" heading is not a publication channel there (the opinions
     are full, published opinions), so publication falls through to the next rule, and form is `full` at >= 600 chars.
- 11 courts: the 8 unmapped decisions get courts; tribal courts get one system per tribe (from 1000); Pueblo County
     District Court (579) is a Colorado trial court; CAAF binds the service Courts of Criminal Appeals (adoption.tsv).
- 13 form `unknown` outside SCOTUS + order language in under 1,500 characters of opinion text (orders_scan.py,
     work/courts/orders.tsv) -> `memorandum` (SCHEMA has no `order` value).
"""
import collections, os, re, shutil

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
L2 = os.path.join(WORK, "caselaw-lean-2")
DATA = os.path.join(L2, "data")
WD = os.path.join(L2, "work", "courts")
SCOTUS = 2906
UNMAPPED = 3160
OK, MN, TX, CO = 36, 23, 43, 6

# ------------------------------------------------------------------ 11: courts
TRIBES = [  # system id, tribe, court ids (v1 ids and the 100xx ids from the unmapped-name fix)
    (1000, "Navajo Nation", [2973, 2974, 2975, 2976, 2977, 10007, 10015, 10017, 10022]),
    (1001, "Eastern Band of Cherokee Indians", [2953, 2959, 2960, 10023]),
    (1002, "Cherokee Nation", [2954, 2955]),
    (1003, "Cheyenne River Sioux Tribe", [2956]),
    (1004, "Confederated Tribes of the Colville Reservation", [2957]),
    (1005, "Coquille Indian Tribe", [2958]),
    (1006, "Fort McDowell Yavapai Nation", [2961, 2962]),
    (1007, "Assiniboine and Sioux Tribes of the Fort Peck Reservation", [2963, 10004]),
    (1008, "Grand Traverse Band of Ottawa and Chippewa Indians", [2964, 2965]),
    (1009, "Ho-Chunk Nation", [2966, 2967]),
    (1010, "Leech Lake Band of Ojibwe", [2968]),
    (1011, "Little River Band of Ottawa Indians", [2969, 2970]),
    (1012, "Mohegan Tribe", [2971, 2972, 10005, 10011, 10025]),
    (1013, "Oneida Nation (Wisconsin)", [2978, 2979]),
    (1014, "Sac and Fox Nation", [2980, 2981]),
    (1015, "Eastern Shoshone and Northern Arapaho Tribes (Wind River)", [2982]),
    (1016, "Swinomish Indian Tribal Community", [2983, 2984]),
    (1017, "Little Traverse Bay Bands of Odawa Indians", [2985]),
    (1018, "Confederated Tribes of the Grand Ronde Community", [2986, 10010]),
    (1019, "Tulalip Tribes", [2987]),
    (1020, "White Earth Band of Chippewa", [2988]),
    (1021, "Hopi Tribe", [10006]),
    (1022, "Confederated Salish and Kootenai Tribes", [10008]),
]
TRIBE_SYS = {c: s for s, _, cs in TRIBES for c in cs}
NEW_COURTS = [  # court id, name, system, tier, src, tag; graph name index of the unmapped name
    (10109, "Department of the Interior (General Land Office appeals)", 0, "S",
     "fix:unmapped name 'Department of Interior' (Secretary/Commissioner land-office decisions, 1 Colo. L. Rep.)", "-",
     "635"),
    (10110, "Register and Receiver, U.S. Land Office, Salina", 0, "S",
     "fix:unmapped name 'Salina Register and Receiver' (federal land office)", "-", "647"),
    (10111, None, None, None, None, None, "636"),  # Judge's Chambers: filled from JUDGES_CHAMBERS
]
# Ex parte Rhodes, 2 Wheel. Cr. Cas. 559 (1816), heard at chambers on habeas corpus
JUDGES_CHAMBERS = dict(name="Judge's Chambers (habeas corpus at chambers; Ex parte Rhodes, 1816)", system=999,
                       tier="T", src="fix:unmapped name 'Judge's Chambers'; state not identified", tag="U")
PUEBLO = 579
MILITARY_CCA = [(639, "the Army Court of Criminal Appeals"), (673, "the Navy-Marine Corps Court of Criminal Appeals"),
                (636, "the Air Force Court of Criminal Appeals"), (646, "the Coast Guard Court of Criminal Appeals"),
                (671, "the Navy Court of Military Review (predecessor of the Navy-Marine Corps court)"),
                (661, "the Courts of Military Review (collective name)")]
CAAF = 650

# ------------------------------------------------------------------ 8: dates
# (file, {column: value} identifying exactly one row, {column: new value}); src/tag are replaced whole.
# courts2: 1 from, 2 to, 3 name, 9 src, 10 tag · succession: 2 date, 4 src, 5 tag · adoption: 2 up_to, 5 src, 6 tag ·
# system_rules: 3 from, 4 to, 5 src, 6 tag
CT = ("Conn. Const. (1965) art. XIV: in force on approval by the people and proclamation by the governor; "
      "'Referendum December 14, 1965. Proclaimed by the governor December 30, 1965.' (cga.ct.gov constitution text)")
DE51 = ("Del. Const. art. IV §§ 1, 35 (48 Del. Laws c. 109, approved 9 May 1951): cases 'pending on May 14, 1951' pass "
        "to the 'newly established Supreme Court' (delcode.delaware.gov)")
DE97 = ("Del. Const. 1897 abolished the Court of Errors and Appeals; the Supreme Court (judges of the other courts) was "
        "the court of last resort 1897-1951 (Delaware Public Archives); day of the 1897 constitution not verified")
OK59 = ("20 O.S. § 31.1 (Laws 1959, p. 107, § 1; emergency clause, effective 11 Mar 1959; statutory history note, "
        "session-law page not seen)")
IN72 = ("in.gov/courts/appeals/about/history: the Appellate Court was abolished and the constitutional Court of Appeals "
        "'came into existence on January 1, 1972' (Ind. Const. art. 7 amendment ratified 3 Nov 1970); same id kept")
CA66 = ("Prop. 1-a (constitutional revision) adopted at the 8 Nov 1966 general election (UC Law SF ballot repository); "
        "effective day not confirmed")
PR03 = ("Ley Núm. 201 de 22 de agosto de 2003 (Ley de la Judicatura), Art. 9.004: in force 90 days after approval "
        "= 20 Nov 2003; Art. 9.002 repeals the Tribunal de Circuito de Apelaciones (OGP official text, "
        "bvirtualogp.pr.gov 201-2003.pdf)")
AR09 = ("In re Ark. Sup. Ct. & Ct. App. Rule 5-2, 2009 Ark. 330 (per curiam, 28 May 2009): opinions issued after "
        "1 July 2009 are precedent and may be cited")
OH02 = ("Ohio Rep.Op.R. 4 (eff. 1 May 2002; renumbered 3.4 in 2012): the controlling/persuasive distinction for "
        "unreported court-of-appeals opinions abolished (law-library sources; rule text not fetched)")
FRAP24 = ("FRAP 35 transferred to restyled FRAP 40 eff. 1 Dec 2024 (S. Ct. order of 2 Apr 2024, "
          "supremecourt.gov/orders/courtorders/frap24_g204.pdf)")
GU04 = ("Pub. L. 108-378 § 2, 118 Stat. 2206 (approved 30 Oct 2004, no separate effective date): strikes the Ninth "
        "Circuit certiorari proviso of 48 U.S.C. § 1424-2; review by SCOTUS from then")
DATE_FIXES = [
    # 8 renames
    ("courts2.tsv", {0: "599", 1: "19651230"}, {9: "rename: " + CT, 10: "S"}),
    ("succession.tsv", {0: "599", 1: "599", 3: "rename"}, {4: CT, 5: "S"}),
    ("courts2.tsv", {0: "609", 1: "0"}, {9: DE97, 10: "L"}),
    ("courts2.tsv", {0: "610", 1: "0"}, {2: "19510513", 3: "Supreme Court of Delaware (1897 constitution)",
                                         9: DE97 + "; until " + DE51, 10: "L"}),
    ("courts2.tsv", {0: "610", 1: "19510101"}, {1: "19510514", 9: DE51, 10: "S"}),
    ("succession.tsv", {0: "609", 1: "610"}, {2: "18970610", 4: DE97 + " (date: believed 10 June 1897)", 5: "U"}),
    ("adoption.tsv", {0: "610", 1: "609"}, {2: "18970609", 5: "doctrine H3 (successor court of last resort; " + DE97 + ")",
                                            6: "L"}),
    ("courts2.tsv", {0: "2571", 1: "0"}, {2: "19590310", 9: "doctrine H2 (Okla. Const. art. VII §4); renamed: " + OK59,
                                          10: "L"}),
    ("courts2.tsv", {0: "2571", 1: "19590101"}, {1: "19590311", 9: "doctrine H2; " + OK59}),
    ("succession.tsv", {0: "2571", 1: "2571"}, {2: "19590311", 4: "doctrine H2 (Criminal Court of Appeals -> Court of "
                                                                  "Criminal Appeals): " + OK59, 5: "L"}),
    ("courts2.tsv", {0: "880", 1: "19720101"}, {9: IN72, 10: "S"}),
    ("succession.tsv", {0: "880", 1: "880"}, {4: IN72, 5: "S"}),
    ("courts2.tsv", {0: "533", 1: "19661108"}, {9: "doctrine S-CA; " + CA66}),
    ("succession.tsv", {0: "533", 1: "533"}, {4: "doctrine S-CA (District Courts of Appeal -> Courts of Appeal); " + CA66}),
    ("courts2.tsv", {0: "2887", 1: "0"}, {2: "20031119", 9: "doctrine §4.3 PR (1992); v1 had federal T; abolished by "
                                                          + PR03}),
    ("courts2.tsv", {0: "2887", 1: "20030701"}, {1: "20031120", 9: PR03, 10: "S"}),
    ("succession.tsv", {0: "2887", 1: "2887"}, {2: "20031120", 4: PR03, 5: "S"}),
    # 8 rules
    ("system_rules.tsv", {0: "4", 1: "unpubForce", 2: "notCitable"}, {5: "Ark. Sup. Ct. R. 5-2 (before " + AR09 + ")",
                                                                      6: "S"}),
    ("system_rules.tsv", {0: "4", 1: "unpubForce", 2: "binding"}, {5: AR09, 6: "S"}),
    ("system_rules.tsv", {0: "35", 1: "unpubForce", 2: "persuasive"}, {5: "doctrine S-OH (weight of unreported opinions "
                                                                          "before 2002 varied); end date: " + OH02,
                                                                       6: "U"}),
    ("system_rules.tsv", {0: "35", 1: "unpubForce", 2: "binding"}, {5: OH02, 6: "L"}),
    ("system_rules.tsv", {0: "-373", 1: "enBancGrantVacatesPanel"}, {5: "6th Cir. R. 35(b); " + FRAP24}),
    ("system_rules.tsv", {0: "43", 1: "horizontal"}, {5: "doctrine S-TX: Owen v. Jim Allee Imports (2012); TRAP 41.3 "
                                                         "transfer (added in the 2008 TRAP amendments; effective day, "
                                                         "believed 1 Sept 2008, not confirmed)"}),
    ("adoption.tsv", {0: "865", 1: "479"}, {5: "doctrine §3.2 GU (9th Cir. certiorari over the Supreme Court of Guam "
                                               "ends: " + GU04 + "); weight uncertain"}),
]
EXTRA_ROWS = [
    ("succession.tsv", ["610", "610", "19510514", "rename", DE51 + " (separate Supreme Court replaces the 1897 court)",
                        "S"]),
    ("adoption.tsv", ["1964", "479", "20040501", "issue:localLaw", "persuasive",
                      "48 U.S.C. § 1824(a): 9th Cir. review of the CNMI Supreme Court for the first 15 years after its "
                      "establishment (2 May 1989; Pub. L. 108-378 does not cover the CNMI); end day uncertain "
                      "(1 or 2 May 2004); weight uncertain", "U"]),
]


def path(name):
    return os.path.join(DATA, name)


def src_of(name):
    b = path(name.replace(".tsv", ".pre_fix.tsv"))
    return b if os.path.exists(b) else path(name)


def commit(name, write_rows):
    """write <name>.tmp, keep the first original as <name>.pre_fix.tsv (hard link), rename tmp over <name>"""
    p = path(name)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fo:
        write_rows(fo)
    b = path(name.replace(".tsv", ".pre_fix.tsv"))
    if not os.path.exists(b):
        try:
            os.link(p, b)
        except OSError:
            shutil.copy2(p, b)
    os.replace(tmp, p)


def read(name):
    return [l.rstrip("\n").split("\t") for l in open(src_of(name), encoding="utf-8")]


def apply_date_fixes(name, rows, stats):
    for fname, key, new in DATE_FIXES:
        if fname != name:
            continue
        hit = [r for r in rows if all(r[i] == v for i, v in key.items())]
        assert len(hit) == 1, (name, key, len(hit))
        for i, v in new.items():
            hit[0][i] = v
        stats["dates:" + name] += 1
    for fname, row in EXTRA_ROWS:
        if fname == name and row not in rows:
            rows.append(list(row))
            stats["dates-added:" + name] += 1


def tables(stats):
    # courts2
    rows = read("courts2.tsv")
    apply_date_fixes("courts2.tsv", rows, stats)
    for r in rows:
        c = int(r[0])
        if c in TRIBE_SYS:
            assert r[4] == "61", r
            r[4] = str(TRIBE_SYS[c])
            r[9] = r[9] + "; system %d (one system per tribe, split from v1 tribal 61)" % TRIBE_SYS[c]
            stats["courts2:tribal-system"] += 1
        elif c == PUEBLO:
            r[4], r[5] = str(CO), "T"
            r[9] = "fix: Colorado state district court (Pueblo County, Colo.; 1883-1901 Colo. reporters); v1 read it as tribal"
            stats["courts2:pueblo"] += 1
    left = [r for r in rows if r[4] == "61"]
    assert not left, left
    have = {int(r[0]) for r in rows}
    for cid, nm, sy, ti, sr, tg, _ in NEW_COURTS:
        if cid == 10111:
            nm, sy, ti, sr, tg = (JUDGES_CHAMBERS[k] for k in ("name", "system", "tier", "src", "tag"))
        if cid not in have:
            rows.append([str(cid), "0", "99991231", nm, str(sy), ti, "-", "0", "0", sr, tg])
            stats["courts2:new"] += 1
    commit("courts2.tsv", lambda fo: fo.writelines("\t".join(r) + "\n" for r in rows))
    # court_alias: the three unmapped names now route to their courts
    al = read("court_alias.tsv")
    g2c = {g: cid for cid, *_, g in NEW_COURTS}
    for r in al:
        if r[7] == "unmapped" and r[1] in g2c:
            r[5], r[7] = str(g2c[r[1]]), "fix:unmapped name (limit 11)"
            stats["alias:unmapped"] += 1
    commit("court_alias.tsv", lambda fo: fo.writelines("\t".join(r) + "\n" for r in al))
    # succession, system_rules: dates
    for name in ("succession.tsv", "system_rules.tsv"):
        rs = read(name)
        apply_date_fixes(name, rs, stats)
        commit(name, lambda fo, rs=rs: fo.writelines("\t".join(r) + "\n" for r in rs))
    # adoption: CAAF binds the service Courts of Criminal Appeals
    ad = read("adoption.tsv")
    apply_date_fixes("adoption.tsv", ad, stats)
    ad = [r for r in ad if not (r[1] == str(CAAF) and r[6] == "L" and r[5].startswith("10 U.S.C."))]
    have = {(r[0], r[1]) for r in ad}
    for cca, svc in MILITARY_CCA:
        if (str(cca), str(CAAF)) not in have:
            ad.append([str(cca), str(CAAF), "99991231", "all", "binding",
                       "10 U.S.C. §§ 866-867: CAAF (Court of Military Appeals to 1994) reviews decisions of %s;"
                       " its precedent binds that court (vertical)" % svc, "L"])
            stats["adoption:caaf"] += 1
    commit("adoption.tsv", lambda fo: fo.writelines("\t".join(r) + "\n" for r in ad))


def history(stats):
    sysof = {}
    for l in open(path("courts2.tsv"), encoding="utf-8"):
        p = l.split("\t")
        sysof.setdefault(int(p[0]), int(p[4]))
    rows = read("history.tsv")
    need = {int(r[2]) for r in rows if r[4] == "writRefused"}
    court = {}
    with open(path("decisions2.tsv"), encoding="utf-8") as f:
        for line in f:
            n, c, _ = line.split("\t", 2)
            if int(n) in need:
                court[int(n)] = int(c)
    out = []
    for r in rows:
        if r[4] == "writRefused":
            if re.search(r"n\.\s?r\.\s?e\b|no reversible error", r[9], re.I):
                stats["history:writ-nre-dropped"] += 1
                continue
            if sysof.get(court.get(int(r[2]), -1), -1) != TX:
                r[0] = re.sub(r":writRefused$", ":other", r[0])
                r[4] = "other"
                r[12] += ";relabel:other(writ refused by a non-Texas court: Louisiana Supreme Court refusal to review; not S-TX-3)"
                stats["history:writRefused->other"] += 1
            else:
                stats["history:writRefused-kept(Texas)"] += 1
        out.append(r)
    commit("history.tsv", lambda fo: fo.writelines("\t".join(r) + "\n" for r in out))


def decisions(stats):
    sysof = {}
    for l in open(path("courts2.tsv"), encoding="utf-8"):
        p = l.split("\t")
        sysof.setdefault(int(p[0]), int(p[4]))
    orders = {}
    for line in open(os.path.join(WD, "orders.tsv"), encoding="utf-8"):
        n, ln, code, _ = line.rstrip("\n").split("\t")
        if code == "order":
            orders[n] = int(ln)
    sig = {}  # OK/MN scan signals: node -> (op_len, fm status, pub codes)
    for repo in ("oklahoma", "oklahoma-appellate", "minnesota", "minnesota-appellate"):
        for line in open(os.path.join(WD, "out", repo + ".tsv"), encoding="utf-8"):
            c = line.rstrip("\n").split("\t")
            sig[c[0]] = (int(c[3]), c[5], c[8])
    unm = {}  # graph name index of each unmapped node -> new court
    g2c = {g: cid for cid, *_, g in NEW_COURTS}
    with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 5)
            if p[3] in g2c:
                unm[p[0]] = g2c[p[3]]

    def write(fo):
        with open(src_of("decisions2.tsv"), encoding="utf-8") as f:
            for line in f:
                r = line.rstrip("\n").split("\t")
                n, c = r[0], int(r[1])
                s = r[8]
                if c == UNMAPPED and n in unm:
                    r[1] = str(unm[n])
                    s = s.replace("c:unmapped;", "c:fix;")
                    stats["dec:unmapped->court"] += 1
                    c = unm[n]
                sy = sysof.get(c, -1)
                if sy in (OK, MN) and n in sig:
                    oplen, fmst, pub = sig[n]
                    if r[5] == "memorandum" and ";p:memo;" in s:
                        if fmst in ("published", "precedential"):
                            pv, ps = "published", "fm:" + fmst
                        elif re.search(r"(?:^|\|)pubpos=", pub):
                            pv, ps = "published", "banner"
                        else:
                            pv, ps = "unknown", "-"
                        r[5] = pv
                        s = s.replace(";p:memo;", ";p:%s+okmn-memo-heading;" % ps)
                        stats["dec:okmn-pub memorandum->" + pv] += 1
                    if r[6] == "memorandum" and s.endswith(";f:memo") and oplen >= 600:
                        r[6] = "full"
                        s = s[:-len("memo")] + "len+okmn-memo-heading"
                        stats["dec:okmn-form memorandum->full"] += 1
                if r[6] == "unknown" and c != SCOTUS and n in orders:
                    r[6] = "memorandum"
                    s = re.sub(r";f:[^;]*$", ";f:order-lt1500", s)
                    stats["dec:form unknown->memorandum(order)"] += 1
                r[8] = s
                stats["dec:rows"] += 1
                fo.write("\t".join(r) + "\n")
    commit("decisions2.tsv", write)


def main():
    stats = collections.Counter()
    tables(stats)
    history(stats)
    decisions(stats)
    for k, v in sorted(stats.items()):
        print("%s\t%d" % (k, v))


if __name__ == "__main__":
    main()
