"""Hunt H3b, checked in round 2 (agent courts): the dated `horizontal` rows of Ohio and Louisiana (rerunnable).

    python -X utf8 rule_dates_fix.py [system_rules.tsv] [--install]

`horizontal` rows are keyed by the precedent's date (and, for `panelDepartsWithoutEnBanc`, the treating date as
well), so a row must not start before the court had the rule (HUNT.md section 3).

The script replaces every `horizontal` row of systems 35 and 18 by the rows below, whatever state the file is in
(the undated originals, the round 1 dates, or these rows), so it can be run again. Without --install it rewrites
the file named; with --install it writes <file>.tmp, keeps the file once as system_rules.pre_round2.tsv and renames.

Ohio (system 35). Sources read in the corpus (primary):
- State v. George, 50 Ohio App.2d 297, 362 N.E.2d 1223, 1231 (1975): a court of appeals is not bound by its own
  earlier rule. McFadden v. Cleveland State Univ., 170 Ohio App.3d 142, 2007-Ohio-939 (10th Dist.): a panel
  "specifically overruled" an earlier panel and held en banc proceedings unconstitutional. So `soft` before.
- McFadden v. Cleveland State Univ., 120 Ohio St.3d 54, 2008-Ohio-4914, decided 2 Oct 2008 (node 5369328), paras
  15, 19-21: en banc proceedings are constitutional; court of appeals decisions are precedent until formally
  overruled; judges who find that two decisions of their court conflict "must convene en banc to resolve the
  conflict"; no rule is needed for that. In re J.J., 111 Ohio St.3d 205, 2006-Ohio-5484 (8 Nov 2006), syllabus
  para 2, had said appellate courts are "duty-bound" to resolve intradistrict conflicts en banc, in a district with
  a local rule; the Tenth District then held the procedure unconstitutional, which McFadden reversed.
- App.R. 26(A)(2) (en banc consideration) is the procedure, in force 1 July 2010 (amendment history of Rule 26;
  Staff Note: "designed to address" McFadden). It is not the start of the duty.
  => the within-district row starts on 2 Oct 2008 (was 1 July 2010, from memory).

Louisiana (system 18). No 1997 source exists: Orillion v. Allstate, 690 So.2d 846 (La. App. 1 Cir. 14 Feb 1997),
says only that sister circuits are not binding. The within-circuit "law of the circuit" rule is judge-made and has
no enactment date. Statements found in the corpus: Shewmake v. Alejaudro, 466 So.2d 711 (La. App. 4 Cir. 12 Mar
1985) (an earlier panel's decision "is controlling" under the doctrine); State v. Wolfe, 630 So.2d 872 (La. App. 4
Cir. 1993) ("this panel is bound"); Graves v. Businelle Towing Corp., 673 So.2d 311, 315 (La. App. 1 Cir. 30 Apr
1996) ("requires that we follow prior decisions of our own circuit"). Wilson v. A-1 Industries, 451 So.2d 1251,
1253 (La. App. 4 Cir. 1984) uses the name for the across-circuit half only. No internal rule or Uniform Rule
requiring an en banc court to overrule a panel was found.
  => the row keeps its start, 1 Jan 1997, and is tagged U (was S): no source gives that date. Moving the start to
  12 Mar 1985 (the earliest statement found) was tried on a private copy: 15 status rows were lost, Louisiana
  decisions of 1985-1990 overruled by an en banc court whose unit does not match the precedent's in the data (unit
  recovery is incomplete), so the within-unit rule denied the power. The earlier date needs the units first.

The federal courts of appeals are handled in the engines (`enBancStatuteDate`, 1 Sept 1948), not here, so that older
circuit precedent keeps its horizontal force.
"""
import os
import sys

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
INSTALL = "--install" in sys.argv[1:]
P = ARGS[0] if ARGS else os.path.expanduser(
    "~/Documents/us-caselaw-lean-work/caselaw-lean-2/data/system_rules.tsv")

OH_START = 20081002
LA_START = 19970101
NEW = {
    "35": [
        ["35", "horizontal", "soft", "0", str(OH_START - 1),
         "doctrine S-OH: State v. George, 362 N.E.2d 1223, 1231 (Ohio App. 1975) (a court of appeals is not bound by "
         "its own earlier rule); a 10th Dist. panel still overruled an earlier panel in 2007 (McFadden, 2007-Ohio-939); "
         "hunt H3b; round2 courts", "S"],
        ["35", "horizontal", "withinUnitOnly", str(OH_START), "99991231",
         "McFadden v. Cleveland State Univ., 120 Ohio St.3d 54, 2008-Ohio-4914 (decided 2 Oct 2008), paras 15, 19-21: "
         "decisions of a court of appeals are precedent until formally overruled; judges who find an intradistrict "
         "conflict must convene en banc; no rule needed (In re J.J., 2006-Ohio-5484, syllabus 2, earlier). App.R. "
         "26(A)(2), in force 1 July 2010, is the procedure. Date read in the opinion (corpus node 5369328); hunt H3b; "
         "round2 courts", "S"],
    ],
    "18": [
        ["18", "horizontal", "withinUnitOnly", str(LA_START), "99991231",
         "doctrine S-LA 'law of the circuit'. Within a circuit: Shewmake v. Alejaudro, 466 So.2d 711 (La. App. 4 Cir. "
         "12 Mar 1985); State v. Wolfe, 630 So.2d 872 (La. App. 4 Cir. 1993); Graves v. Businelle Towing, 673 So.2d "
         "311, 315 (La. App. 1 Cir. 1996). Across circuits: Orillion v. Allstate, 690 So.2d 846, 849 (La. App. 1 Cir. "
         "1997). Judge-made, no enactment date; the 1997 start is the round 1 date and no source gives it (statements "
         "go back to 1985); 2d, 3d and 5th Circuits not shown; hunt H3b; round2 courts", "U"],
    ],
}

with open(P, encoding="utf-8", newline="\n") as f:
    rows = [l.rstrip("\n").split("\t") for l in f if l.strip("\n")]
out, done, n_old = [], set(), 0
for r in rows:
    if r[1] == "horizontal" and r[0] in NEW:
        n_old += 1
        if r[0] not in done:
            done.add(r[0])
            out.extend(NEW[r[0]])
        continue
    out.append(r)
missing = [s for s in NEW if s not in done]
if missing:
    sys.exit("rule_dates_fix: no horizontal row found for system(s) %s in %s" % (",".join(missing), P))
changed = out != rows
if INSTALL:
    backup = os.path.join(os.path.dirname(P), "system_rules.pre_round2.tsv")
    if not os.path.exists(backup):
        with open(P, "rb") as f, open(backup + ".tmp", "wb") as g:
            g.write(f.read())
        os.replace(backup + ".tmp", backup)
with open(P + ".tmp", "w", encoding="utf-8", newline="\n") as f:
    for r in out:
        f.write("\t".join(r) + "\n")
os.replace(P + ".tmp", P)
print("rule_dates_fix: %d horizontal rows of systems %s replaced by %d in %s (%s)" % (
    n_old, ",".join(sorted(NEW)), sum(len(v) for v in NEW.values()), P, "changed" if changed else "no change"))
