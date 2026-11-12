"""The court table: every court name in US case law mapped to a system, a tier and (federal) a circuit.

    python tools/caselaw/courts_map.py <graph-dir>      -> <graph-dir>/court_table.tsv, court_unmapped.tsv

A court whose rank changed is split by era (ERAS): the Kentucky Court of Appeals was the state's court of last resort
until the Kentucky Supreme Court was created in 1976, for example. Each row: name, era start year, era end year,
system (0 = federal, else the state/territory index), system name, tier (last/appellate/trial/special), circuit, rule.
"""
import os, re, sys

STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
          "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
          "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
          "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
          "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
          "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
          "District of Columbia", "Puerto Rico", "Guam", "Virgin Islands", "American Samoa", "Northern Mariana Islands",
          "Dakota Territory", "Navajo Nation", "Indian Territory", "Hawaiian Kingdom"]
SYS = {s: i + 1 for i, s in enumerate(STATES)}
# federal district courts: state -> circuit
CIRCUIT_OF = {}
for c, sts in {1: ["Maine", "Massachusetts", "New Hampshire", "Rhode Island", "Puerto Rico"],
               2: ["Connecticut", "New York", "Vermont"],
               3: ["Delaware", "New Jersey", "Pennsylvania", "Virgin Islands"],
               4: ["Maryland", "North Carolina", "South Carolina", "Virginia", "West Virginia"],
               5: ["Louisiana", "Mississippi", "Texas"],
               6: ["Kentucky", "Michigan", "Ohio", "Tennessee"],
               7: ["Illinois", "Indiana", "Wisconsin"],
               8: ["Arkansas", "Iowa", "Minnesota", "Missouri", "Nebraska", "North Dakota", "South Dakota"],
               9: ["Alaska", "Arizona", "California", "Hawaii", "Idaho", "Montana", "Nevada", "Oregon", "Washington",
                   "Guam", "Northern Mariana Islands"],
               10: ["Colorado", "Kansas", "New Mexico", "Oklahoma", "Utah", "Wyoming"],
               11: ["Alabama", "Florida", "Georgia"],
               12: ["District of Columbia"]}.items():
    for s in sts:
        CIRCUIT_OF[s] = c
ORD = {"First": 1, "Second": 2, "Third": 3, "Fourth": 4, "Fifth": 5, "Sixth": 6, "Seventh": 7, "Eighth": 8,
       "Ninth": 9, "Tenth": 10, "Eleventh": 11, "District of Columbia": 12, "Federal": 13}

# State courts of last resort whose name does not say "Supreme Court of <state>".
LAST = [r"New York Court of Appeals", r"Court of Appeals of New York", r"Court of Appeals of Maryland",
        r"Maryland Court of Appeals", r"Supreme Court of Maryland", r"Massachusetts Supreme Judicial Court",
        r"Supreme Judicial Court", r"Texas Court of Criminal Appeals", r"Court of Criminal Appeals of Texas",
        r"Oklahoma Court of Criminal Appeals", r"Court of Criminal Appeals of Oklahoma",
        r"Supreme Court of Appeals", r"District of Columbia Court of Appeals", r"Supreme Court of Errors",
        r"Court of Errors and Appeals", r"Court for the Correction of Errors", r"Court of Errors",
        r"High Court of Errors and Appeals", r"Supreme Court of Judicature"]
# era splits: (name regex, until year inclusive, tier before, tier after)
ERAS = [(r"^Kentucky Court of Appeals$", 1975, "last", "appellate"),
        (r"^Court of Appeals of Kentucky$", 1975, "last", "appellate"),
        (r"^Supreme Court of New Jersey$", 1947, "appellate", "last"),
        (r"^New Jersey Supreme Court$", 1947, "appellate", "last"),
        (r"^Court of Appeals of Virginia$", 1984, "last", "appellate"),
        (r"^Court of Appeals of West Virginia$", 1999, "last", "appellate")]
SPECIAL = [r"Bankruptcy", r"Tax Court", r"Board of Tax Appeals", r"Court of Federal Claims", r"Court of Claims",
           r"Claims Court", r"Court of International Trade", r"Customs Court", r"Board of General Appraisers",
           r"Workers'? Compensation", r"Industrial", r"Juvenile", r"Family Court", r"Surrogate", r"Probate",
           r"Orphans", r"Attorney General", r"Board", r"Commission", r"Tribal", r"Military", r"Armed Forces",
           r"Veterans", r"Court-Martial", r"Judicial Panel", r"Land Court", r"Housing Court", r"Water Court",
           r"Court of Chancery", r"Chancery", r"Commerce Court", r"Emergency Court of Appeals"]


def state_in(name):
    best = None
    for s in sorted(STATES, key=len, reverse=True):
        if re.search(r"\b" + re.escape(s) + r"\b", name):
            if s == "Virginia" and "West Virginia" in name:
                continue
            best = s
            break
    if best is None and re.search(r"\bN\.?Y\.?\b", name):
        best = "New York"
    return best


def repo_state(repo):
    """The state a repo of US case law belongs to (None for federal repos)."""
    r = re.sub(r"-(appellate|other-courts|district)(-\d{4}-\d{4})?$|-\d{4}-\d{4}$", "", repo)
    words = r.replace("-", " ").title()
    for s in STATES:
        if s.lower() == words.lower():
            return s
    return None


def classify(name, repo=None):
    """(system name, tier, circuit, rule) or None."""
    n = name.strip()
    if re.search(r"Supreme Court of the United States|United States Supreme Court|^U\.?S\.? Supreme Court", n):
        return "federal", "last", 0, "scotus"
    federal = bool(re.search(r"United States|U\.S\.|Federal|Circuit Court of Appeals|Court of Appeals for the .* Circuit"
                             r"|District Court for|Court of Claims|Court of Federal Claims|Court of International Trade"
                             r"|Customs Court|Judicial Panel|Commerce Court|Emergency Court of Appeals|Armed Forces"
                             r"|Court of Military Appeals|Veterans Claims|Bankruptcy Appellate Panel|Tax Court"
                             r"|Board of Tax Appeals", n))
    if re.search(r"Navajo|Tribal|Nation\b|Band of|Pueblo", n) and "United States" not in n:
        return "tribal", "special", 0, "tribal"
    st = state_in(n)
    if federal and not re.search(r"^(Supreme|Superior|Circuit|District|County|Court of Appeals?) .*\b(of|for) (the )?State\b", n):
        m = re.search(r"Court of Appeals for the (.+?) Circuit|(\w+) Circuit Court of Appeals|Circuit Court of Appeals,? (\w+) Circuit", n)
        if m:
            key = next(g for g in m.groups() if g)
            key = key.replace("the ", "")
            c = ORD.get(key)
            if c:
                return "federal", "appellate", c, "circuit"
        if re.search(r"Court of Appeals for the Federal Circuit|Court of Customs and Patent Appeals", n):
            return "federal", "appellate", 13, "federal-circuit"
        if re.search(r"Court of Appeals for the District of Columbia|Court of Appeals of the District of Columbia"
                     r"|Court of Appeals for D\.?C|D\.?C\.? Circuit", n):
            return "federal", "appellate", 12, "dc-circuit"
        if re.search(r"Court of Federal Claims|Court of Claims|Claims Court|Court of International Trade|Customs Court", n):
            return "federal", "special", 13, "national-court"
        if re.search(r"Bankruptcy Appellate Panel", n):
            m2 = re.search(r"(\w+) Circuit", n)
            return "federal", "special", ORD.get(m2.group(1), 0) if m2 else 0, "bap"
        if st:
            tier = "special" if any(re.search(p, n) for p in SPECIAL) else "trial"
            return "federal", tier, CIRCUIT_OF.get(st, 0), "district"
        if any(re.search(p, n) for p in SPECIAL):
            return "federal", "special", 0, "federal-special"
        return "federal", "trial", 0, "federal-other"
    if st:
        for rx, until, before, after in ERAS:
            if re.search(rx, n):
                return st, f"era:{until}:{before}:{after}", 0, "era"
        if any(re.search(p, n) for p in LAST):
            return st, "last", 0, "last-named"
        if re.search(r"^Supreme Court of (the State of )?" + re.escape(st) + r"$|^" + re.escape(st) + r" Supreme Court$", n):
            if st == "New York":
                return st, "trial", 0, "ny-supreme"
            return st, "last", 0, "supreme"
        if st == "New York" and re.search(r"Appellate Division|Appellate Term|General Term", n):
            return st, "appellate", 0, "ny-appellate"
        if re.search(r"Court of Appeals?|Appellate|Superior Court of Pennsylvania|Commonwealth Court|District Court of Appeal"
                     r"|Court of Special Appeals|Appellate Court|Court of Civil Appeals|Intermediate", n):
            return st, "appellate", 0, "appellate"
        if any(re.search(p, n) for p in SPECIAL):
            return st, "special", 0, "state-special"
        return st, "trial", 0, "trial"
    rst = repo_state(repo) if repo else None
    if rst:
        if re.search(r"Court of Appeals?|Appellate|Superior Court of Pennsylvania|Commonwealth Court", n) and not re.search(r"County|City|Municipal", n):
            return rst, "appellate", 0, "repo-state-appellate"
        if any(re.search(p, n) for p in SPECIAL):
            return rst, "special", 0, "repo-state-special"
        return rst, "trial", 0, "repo-state-trial"
    return None


def main(gdir):
    import collections
    rows, un = [], []
    repo_of = collections.defaultdict(collections.Counter)
    for line in open(os.path.join(gdir, "nodes.tsv"), encoding="utf-8"):
        f = line.split("\t", 4)
        repo_of[f[3]][f[1]] += 1
    for line in open(os.path.join(gdir, "courts.tsv"), encoding="utf-8"):
        cid, name, n, lo, hi = line.rstrip("\n").split("\t")
        top = repo_of[cid].most_common(1)
        c = classify(name, top[0][0] if top else None)
        if c is None:
            un.append((int(n), name))
            continue
        sysname, tier, circ, rule = c
        sysid = 0 if sysname == "federal" else (len(STATES) + 1 if sysname == "tribal" else SYS[sysname])
        if tier.startswith("era:"):
            _, until, before, after = tier.split(":")
            rows.append((cid, name, 0, int(until), sysid, sysname, before, circ, rule))
            rows.append((cid, name, int(until) + 1, 9999, sysid, sysname, after, circ, rule))
        else:
            rows.append((cid, name, 0, 9999, sysid, sysname, tier, circ, rule))
    with open(os.path.join(gdir, "court_table.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    with open(os.path.join(gdir, "court_unmapped.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for n, name in sorted(un, reverse=True):
            f.write(f"{n}\t{name}\n")
    tot = sum(int(l.split('\t')[2]) for l in open(os.path.join(gdir, "courts.tsv"), encoding="utf-8"))
    print("courts", len(rows), "unmapped", len(un), "unmapped decisions", sum(n for n, _ in un), "of", tot)


if __name__ == "__main__":
    main(sys.argv[1])
