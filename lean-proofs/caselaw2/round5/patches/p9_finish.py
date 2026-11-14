"""Round 5 finish: process table, PROGRESS, LOG, report generator tweaks, short doc notes."""
import json
import os

C2 = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2"
R5 = os.path.join(C2, "round5")


def w(p, s):
    open(p, "w", encoding="utf-8", newline="\n").write(s)


def r(p):
    return open(p, encoding="utf-8").read()


# 1. process table
p = os.path.join(R5, "report", "processes.json")
ps = json.load(open(p, encoding="utf-8"))
for x in ps:
    if x["work"].startswith("Lean expansion"):
        x["state"] = "Done"
        x["note"] = ("Recognised overrulings are in the frozen build (6,161 rows admitted by the checker; blind audit 94-97% right). "
                     "Operative words were built and audited at 79% / 27% and are not installed. 175 theorems locked, 34 mutants killed, "
                     "round-4 output reproduced byte for byte.")
    if x["work"].startswith("Sealed test"):
        x["state"] = "Done"
        x["note"] = ("Run once at 14:06 after the freeze record: lenient 46.5% -> 60.6% [51.9, 68.7] on 127 pairs; strict unchanged at 25.2% "
                     "(by design). The open half moved by the same amount.")
    if x["work"].startswith("Blog wording"):
        x["state"] = "Done"
        x["note"] = "Proposals are in the last section of this page. The post was not edited."
json.dump(ps, open(p, "w", encoding="utf-8", newline="\n"), indent=2, ensure_ascii=False)

# 2. PROGRESS
p = os.path.join(R5, "PROGRESS.md")
s = r(p)
i = s.index("## State")
w(p, s[:i] + """## State (final, 14:20)
| item | state |
|---|---|
| Design (`DESIGN5.md`) | final; rulings in section 9 |
| Lean | 175 theorems locked and checked (0 problems), 34 mutants killed, no sorry / new axiom / native_decide; round-4 output reproduced byte for byte |
| Python reference | round-5 rules implemented from the design alone; regression set 0 disagreements; new universes: status 0 of 55,055 keys |
| Recognised class | read (2,902 passages by the main model, 2,347 pre-screened), certified, blind-audited (94-97% right), **installed in the frozen build** |
| Operative-words class | read (2,179 passages), certified (665 rows), blind-audited at 79% (part) and 27% (whole): **not installed** |
| Frozen build | `round5/stage/final` + `round5/out/final`; `FREEZE.md` written 14:05 |
| Sealed test | run once, 14:06: lenient 46.5% -> 60.6%; strict 25.2% unchanged |
| Round report | `ROUND5.md`; page `~/Documents/html-reports/overturned.html` |
| Not done | fuzzer extension; scope and reader-recall fixes from the dev diagnosis; decoys in the audits; install over `data/`; fix of the date-0 power lookup |

## How to rebuild a variant
`python round5/stage.py <name> --delta ... ` -> `wsl/r5_run.sh <name> [ref]` (inside WSL) -> `bash round5/score_all.sh <name>`
-> `python round5/report/make_overturned.py`. The frozen build's command line is in `round5/stage/final/MANIFEST.txt`.
""")

# 3. LOG
p = os.path.join(R5, "LOG.md")
w(p, r(p) + """
## 8. Frozen build and the sealed half (14:05-14:07)

`final` = `it2` without the operative-words rows. Open half: strict 50 = 30.3%; overruled from a later court's date
30; lenient 108 = 65.5% [57.9, 72.3] (it2 was 66.7%: the two points were operative rows). Held-out notes: pool
13.9%, also-in-feed 35.3%, held-out-only 5.5%; recognised rows confirmed 170/181 = 93.9%. Leak check 0. Behaviour:
recognised whole case 0.78 (0.50-0.91), n = 207; part 0.85 (0.75-0.95), n = 957.

Theorem lock: 175 theorems, `audit.py check` 0 problems (exit 0), full build with the lock's guards green.
Second sweep on the frozen code (seeds 74000-74299): status 0 of 55,055 keys; 13 universes differ on one
certificate verdict each (the date-0 cause). Real data: 2 of 6,163 recognised rows differ (successor courts).

`FREEZE.md` written 14:05 (hashes of Lean sources, cue table, reference, readers, data, output). Then the sealed
half, once: 127 pairs; strict 32 = 25.2% [18.4, 33.4] (unchanged, by design); overruled from a later court's date
25; lenient 77 = 60.6% [51.9, 68.7] (round 4: 46.5% [38.0, 55.1]); implied pairs 5 of 21 (1 before); outside the
Constitution Annotated 3 of 8 (2 before). The open half had moved by 13.3 points, the sealed half by 14.1. Nothing
was changed after the run.

Final operative-words audit (all four auditors): part 63/80 = 78.8% [68.6, 86.3]; whole 11/41 = 26.8% [15.7, 41.9];
control 20/20.
""")

# 4. report generator: contents links and the sealed table
p = os.path.join(R5, "report", "make_overturned.py")
s = r(p)
a = """'<a href="#tests">The other tests</a><a href="#scores">Scores so far</a><a href="#sealed">Sealed half</a>'"""
b = """'<a href="#tests">The other tests</a><a href="#scores">Scores so far</a><a href="#sealed">Sealed half</a>'
                 '<a href="#model">What changed</a><a href="#results">Results</a><a href="#cases">Worked cases</a>'
                 '<a href="#limits">Limits</a><a href="#blog">Blog wording</a>'"""
if a in s and "#results" not in s:
    s = s.replace(a, b)
a = """        h.append('<tr><td colspan="3">%d runs are logged on the sealed half; the expanded build’s figure is in the results section '
                 'once the lead has written it.</td></tr>' % len(log))"""
b = """        ft = read(os.path.join(R5, 'results', 'final', 'fresh_test.txt'))
        fr = fresh_row(ft, 'all', 'all') if ft else None
        if fr:
            h.append('<tr><td>Frozen build (recognised class), the single run after the freeze record</td>'
                     '<td>%s <span class="muted">%s</span> (%d)</td><td><b>%s</b> <span class="muted">%s</span> (%d of %d; %d of them '
                     'overruled by the listed case from a later court’s date)</td></tr>' % (
                         pct(fr['strict']), esc(fr['sci']), fr['a'], pct(fr['lenient']), esc(fr['lci']),
                         fr['a'] + fr['ad'] + fr['b'] + fr['c'], fr['n'], fr['ad']))
        else:
            h.append('<tr><td colspan="3">%d runs are logged on the sealed half.</td></tr>' % len(log))"""
if a in s:
    s = s.replace(a, b)
w(p, s)

# 5. short notes in the standing documents
p = os.path.join(C2, "DEVIATIONS.md")
w(p, r(p).rstrip("\n") + """

## Round 5 (13 Nov 2026): recognised overrulings and operative words (`round5/DESIGN5.md`)

87. **A status may change on a later court's words.** Rounds 1-4: only the overruling court's own words. Round 5: a
    later decision W of a court with power over X, stating in a certified majority sentence naming X and Y that X
    was overruled by Y, makes X `unknown:recognisedLater` from date(Y) and negative from date(W)
    (`Spec.recogEffects`, `Cert.checkRecognised`). The model never backdates the negative to date(Y). No revival of a
    recognised effect after Y or W is reinstated (conservative).
88. **Cue lists for the round-5 text modes** (`recognised`, `disqualify_recognised`, `operative`, `operative_whole`,
    `operative_limit`, `disqualify_operative`, `self_announced`) are data in the one cue table. Substring matching
    means a disqualifier can refuse a true statement (for instance "declining" in a neighbouring clause); never the
    reverse.
89. **Operative words are checked strictly only where a row claims the class.** Rows of rounds 2-3 with such wording
    keep their effect and are only classified `operativeWords`. The rows of this round failed their blind audit
    (79% / 27%) and are not installed.
90. **Class of a row** (`Cert.classOf`) is computed from the verdict, the explicit flag and the quote; `oclass` on a
    status row is the least class among the treatment effects that make the status (history and statutes have none).
91. **Open, found by the round-5 generator, not fixed:** an unknown date (0) is read as a real day in the power
    lookup (`powerAnyDomain`, `powerOn`, the `citesLaterNegated` test): Lean can give or refuse power to an undated
    decision where the reference says unknown (13 of 300 generated universes, no status key). And
    `canChangeStatus` gives a successor court its predecessor's power only between courts of last resort; 2 real
    recognised rows (New Jersey) are refused by Lean and admitted by the reference.
""")
p = os.path.join(C2, "LEAN.md")
w(p, r(p).rstrip("\n") + """

## Round 5 (13 Nov 2026)

175 theorems (141 + 34), 34 mutants x 35 properties, locked (`audit.py lock`, `check`: 0 problems). New:
`Spec/Recognised.lean` (recognised overrulings: never negative before the later court's date, never without its
power, order independence, agreement with an explicit row from that date, never weakens; demoted scope never
negative), the round-5 section of `Certificate.lean` (`Mode`, `checkRecognised`, `checkOperative`, `classOf`,
`recogOf`), `Findings.citedRecognisedLater`, `Examples.plessy_timeline`, mutants M28-M34. Runner: optional
`treatment_class.tsv` turns on round-5 output (`classes.tsv`, `oclass` columns); without it the output is round 4's
byte for byte (`wsl/r5_base.sh`). Details: `round5/DESIGN5.md`, `round5/ROUND5.md`.
""")
p = os.path.join(C2, "TRUST.md")
w(p, r(p).rstrip("\n") + """

## Round 5 addendum (13 Nov 2026)

- Proved: the 34 round-5 theorems (list in `round5/ROUND5.md` and the report). Certificate-checked: every recognised
  row (the later court's quote, both names in it, its power). Tested: Lean against the reference on 118 regression
  universes (0), 600 new universes (status 0; one old cause differs on verdicts) and the real data (2 rows).
- Assumed, new: the opinion-part map's "majority" label for the later court's sentence; the reader's judgment that a
  sentence states the overruling as fact; the scope it assigns. Measured by blind audit at 94-97% right.
- Not covered: the fuzzer does not yet generate `treatment_class.tsv`.
""")
print("finished")
