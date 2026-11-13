# caselaw-lean-2: differential testing (DESIGN D4)

The Lean runner (`runner/`, the Spec through the Exec layer) was compared with an independent Python reference
(`lean-proofs/tools/caselaw2/ref/precedent_ref.py`, written from doctrine.md). The comparison ran on:
- the fixtures;
- about 55,000 generated universes;
- the real data that has landed so far.

Every disagreement was triaged into one of four classes:
- **(a)** the Lean is wrong against doctrine.md;
- **(b)** the reference is wrong;
- **(c)** doctrine.md leaves the point open: one reading was chosen and recorded in both DEVIATIONS.md (items 30–54)
  and REF_NOTES.md ("Revisions after differential testing");
- **(d)** a data or fixture error.

Both sides were then fixed until they agreed.

**Headline, final (12 Nov, evening; §8).** Run under Linux Lean 4.35.0 in WSL, after the fuzz fixes and the hunt
fixes (H2, H3b, H4, H6):
- **Generated sweep:** 1,000 fresh universes (seeds 53000–53999, with the new hunt layer) give **zero
  disagreements** over 344,828 compared keys.
- **Regression set:** 111 kept counterexamples, all agreeing.
- **Real data** (fresh snapshot with the corrected bench and publication labels; 6,892,454 decisions, 48,318,876
  edges): certs 0 of 346,832, splits 0 of 329, conflicts 0 of 107; status 5 of 394,963 (0.0013%) and findings 6 of
  133,588 (0.0045%), **all eleven of them `firm` flags only**, one open class (§8.4).
- `lake build LegalProofs.CaseLaw2` green; `audit.py check`: 114 theorems, 0 statement changes, 0 problems.

**Headline, first pass (12 Nov, afternoon).**
- **Final sweep:** 5,000 fresh universes (seeds 20000–24999) give **zero disagreements** over 881,886 compared keys.
- **Stress sweep:** 2,000 universes twice the size (seeds 30000–31999) give 2 firm-flag-only differences over 737,019 keys, explained in §4.
- **Regression set:** 110 kept counterexamples, all agreeing.
- **Real data** (snapshot of 12 Nov 18:00, with reader and interim holdings files): certs 0 of 218,200, status 17 of
  78,615 (0.022%), findings 27 of 83,686 (0.032%). Splits are 0 of 0 because the holdings windows are malformed
  (d6). See "Real data".
- **Errors found:** 71 classes. 26 were Lean errors, 17 were reference errors, 24 were open points settled
  with one reading (c), and 4 were data or contract problems (d). Comparison-layer artifacts are listed separately.
- **Statement lock:** no theorem statement changed. `lake build LegalProofs.CaseLaw2` is green, and
  `audit/audit.py check` reports 84 theorems, 0 statement changes and 0 problems. No `sorry`, `axiom` or
  `native_decide`.

## 1. Canonical comparison form (step 1)

The two sides did not share an output format. The Lean writes status only on the diagonal (asOf t = conduct u),
with inclusive intervals and the D5 classes `noneAdmitted / negativeAdmitted / unknown`. The reference writes
asOf × conduct pieces with exclusive intervals, as `none / negative / unknown` with finer event kinds.

`diff.py` was rewritten to read **either** format into one canonical form; the label map is `ref/labels.json`. The
map only renames: it never changes a verdict. The canonical form is:

- **status:** for each (node, holding), the status at every breakpoint either side uses, for t ≤ asOf, read on the
  diagonal t = u.
  - The class is `none | negative | partial | unknown`. `partial` is §8.2's "partiallyNegative" on ⊤: the Lean's
    `unknown:partialScope` on holding `-`, or the reference's `...:partial` kinds.
  - A negative kind is mapped to the Lean `Neg` vocabulary: overruled ← overruled, disapproved or recededFrom;
    superseded ← supersededByEnactment; withdrawn ← withdrawn or substitutedBy; vacated ← vacated or
    rehearingEnBancGranted; reviewPending ← reviewGranted; and so on.
  - `firm` is compared too.
  - Breakpoints are normalised to calendar days. The Lean's `yyyymmdd + 1` for "the day after" (19980229) and the
    reference's next day (19980301) are the same point.
- **findings:** compared in three groups.
  - `cites`: (citing, cited, canonical kind of the cited status), from the citation-edge findings.
  - Pair findings: (kind, citing, cited).
  - `atRisk`: (family, subject, source). The Lean writes `inferredRejection` as (target, treating) and
    `inferredSupersession` as (target, 0); the reference writes (treating, target) and (lc:id, target).
  - Kinds only one side defines are counted as *uncompared*, not as disagreements: Lean `ignoresBindingInUnit`,
    `inconsistentBindingBase`, `atRisk:citesLaterNegated` and force-based `citesNotCitable`; reference `atRisk:soft`,
    `atRisk:claim` and `atRisk:contraryBinding`.
- **certs:** passed or rejected *as text*. Lean `noAuthority` and `targetLater` follow every text check, and the
  reference makes those decisions in the status layer, so both count as passed. Different rejection reasons are
  reported but not scored.
- **splits:** (issue, {court1, court2}) of the splits that exist on asOf, with units dropped. The reference gained a
  `splits_asof.tsv` output for this. Lean `conflict` rows have no reference counterpart and are uncompared.

Comparison-layer artifacts fixed along the way (not counted as errors of either side):
- the 2-D against diagonal segmentation;
- `to` inclusive against exclusive;
- an invalid date as a breakpoint;
- `firm` as row identity in the reference against a per-point verdict in the Lean (both now use the same verdict:
  D5 class and negative kind, cut where the firm run changes);
- the orientation of `atRisk` rows;
- citesNotCitable's detail column;
- tuple identity for finding `firm`.

## 2. Rounds run

| Sweep | Seeds | Universes | Purpose |
|---|---|---|---|
| fixtures | — | 1 | the 13 SCHEMA files, every output kind |
| initial | 1–40 (original generator) | 80 | first classes; kept as `fixtures/regress/orig-*` |
| triage iterations | 1–200 | ≈ 3,200 (16 × 200) | the bulk of the class-by-class triage |
| triage iterations | 1000–1999 | ≈ 8,000 (8 × 1,000) | |
| triage iterations | 10000–12999 | ≈ 15,000 (5 × 3,000) | |
| final, fresh seeds | 20000–24999 | 5,000 per run, 25,000 in all | residual measurement after the last fix: 5,000 rounds, 0 with a disagreement (status 0/316,963, findings 0/51,793, certs 0/465,023, splits 0/48,107 keys) |
| stress (n = 120) | 30000–31999 | 2,000 per run, 6,000 in all | larger universes: 2,000 rounds, 1 with a disagreement: two `firm`-only differences on `cites:vacated` (seed 30984), and no verdict differences (status 0/253,453, findings 2/40,926 firm only, certs 0/372,157, splits 0/70,483) |
| **total** | ≈ 11,200 distinct seeds | **≈ 57,000** | |

Each universe has 60 decisions (120 in the stress sweep) and is generated by `gen.py`. It contains:
- every court family: SCOTUS, circuits with a split and adoption, the Federal Circuit, CFC, the Tax Court, Maine,
  California with units, Kentucky epochs, and the Texas dual high courts;
- dated S/L/U rules;
- every treatment, history, scope and temporal kind;
- corrupted certificates;
- supersessions, including `retroactive_to = 1` (added for the new SCHEMA convention);
- `reviewGrantedForce` rows (added).

Run: `python gen.py --seed S --rounds N [--n 60] --out DIR --ref --lean --diff` (8 at a time, compiled runner).

## 3. Disagreement classes, triage and fix

"First seen" is the number of rounds out of 200 in the first iteration (seeds 1–200) in which the class appeared,
where it was measured. Fixes are in `LegalProofs/CaseLaw2/` (Lean) and `tools/caselaw2/ref/` (reference).

### Lean wrong (a): 26 classes

| # | Class | First seen | Fix |
|---|---|---|---|
| a1 | Every reader history and treatment row was rejected as a bad row: the ids are strings (`t:<by>:<target>:<start>`), but `Data.lean` parsed them as `Nat`. This blocked all real-data use. | 200/200 | `Data.lean`: ids are `String`; `Run.lean` uses the row index internally and writes the string id |
| a2 | Diagonal rows missed the breakpoints where an effect starts reaching conduct; firm breakpoints were missed too | 40/40 | `Run.lean`: dates include `conductFrom` and the firm run's dates |
| a3 | A supersession with issue `-` applied to the whole decision. AB1 says supersession is issue-limited. | 35/40 | `SEvent.scope`; `-` means the holdings on the amended USC block, else `someIssue` |
| a4 | Holdings were used without their certificate | 25/200 | holdings admitted only when their certificate passes |
| a5 | `laterCourtSays` supersession evidence was not certificate-checked | — | requires the treatment's text certificate |
| a6 | Treatment findings were emitted for rows whose certificate failed | 83/200 | findings read only text-certified rows |
| a7 | Per-holding citation findings were emitted for issues the citing decision does not cite (HD4) and only for two kinds; a decision citing what it itself overruled was flagged; per-holding rows were emitted when the whole decision was negative | 30/40 | DEVIATIONS 53 |
| a8 | `histPower`: any higher federal court, or the CFC, could reverse a district decision | 20/40 | own circuit or the Federal Circuit only |
| a9 | An unknown issue domain was silently read as the home domain for power (none-admitted instead of unknown, D5); power was decided once per treatment instead of per issue | 96/200 | per-issue power, `Unk.powerUnknown`, `TEvent.powerKnown`, `Scope.someOf` |
| a10 | An appellate division had power over trial courts of other units | — | same unit required |
| a11 | A trial court could overrule its own decisions (under the IAC's horizontal rule) | 4/200 | F13: no power |
| a12 | An adopter could overrule decisions of a higher dated tier (the new Kentucky CoA over the old court of last resort); its bench rule ignored its own horizontal rule; adopted decisions kept a unit | 11/200 | DEVIATIONS 41 |
| a13 | The Federal Circuit had no power over district courts on patent issues; a regional circuit's patent law bound its districts after 1982 | 13/1000 | F11(b) in `canChangeStatus` and `fedHier` |
| a14 | E3 `stateFollowsCircuit` applied to every circuit, not the state's own | — | the runner derives each state system's circuit (28 U.S.C. § 41) |
| a15 | `reinstated` did not end a depublication or a pending review | 13/200 | `histEffect` lapses |
| a16 | An overruling did not revive when the overruler was reinstated, and did not lapse when an en banc grant vacated the overruler | — | `treatEffects`, `vacatingGrants` |
| a17 | The split test was resolver-based: courts whose own law does not bind them (CA districts, state high courts) never split. DESIGN layer 5 defines a split by holdings. | 129/200 | layer-5 pairwise test in the runner; `conflict` kept |
| a18 | `pluralityTreatedAsBinding` did not ask whether the plurality would bind as a majority opinion | 80/200 | binding as a majority on every candidate domain |
| a19 | `atRisk inferredRejection` required verified power, and ignored a target that was already negative | 48/200 | power not shown absent; target not wholly negative |
| a20 | `panelDepartsWithoutEnBanc` ignored division benches and already-negated targets | 23/200 | DEVIATIONS 53 |
| a21 | A Texas writ-refused notation on a federal decision demoted the circuit's binding force | 3/5000 | promote only state intermediate courts |
| a22 | `Status.partially`: an unknown event reaching part of a decision showed as `partialScope` | 21/200 | the unknown reason is kept (later settled as c6) |
| a23 | A history quote from the target's own text needed target evidence | 25/200 | `Cert.Input.selfText` (with c18) |
| a24 | Firm glue: `pluralityTreatedAsBinding` hard-coded `firm = 1`; the firm run's targets were not computed; per-holding firm ignored the all-holdings condition; firm for cites findings did not require the same status; an empty domain list made a vacuous `all` | 1–16 / 1000 | `Run.lean` |
| a25 | `withinUnitOnly` required a known unit for force but not for power | 5/1000 | both unitless is the same unit |
| a26 | The anonymous issue under a partial and an unknown-power event was ranked unknown | 2/1000 | `partially` maps any change to `partialScope` |

### Reference wrong (b): 17 classes

| # | Class | First seen | Fix |
|---|---|---|---|
| b1 | Same-case history was admitted without asking who decided it (a CoA "vacating" a SCOTUS opinion) | 20/40 | R25 same-case power |
| b2 | Inferred (`explicit = 0`) rows gave `unknown:inferred`; §9.26 says they never prove status | 33/40 | R26: no status effect |
| b3 | SCOTUS on state law was binding on lower federal courts; F1 says "on federal questions only" | 26/200 (splits) | R10 |
| b4 | Power over a multi-issue treatment was judged on one domain; an ambiguous domain gave `unknown` | 1/200 | per-issue power |
| b5 | Restorers did not close `unknownScope:`/`otherGrounds:` effects or unknown en banc grants; `reinstated` did not close `reversed` | 5/1000 | `CLOSES` |
| b6 | A destination unit of 0 was read as a real unit, not as unknown | 1/1000 | the court's unit |
| b7 | The overruler's lapse dates were not breakpoints of the target timeline | 1/3000 | added |
| b8 | A panel departure was flagged for a treatment earlier than its target, or by a court with power by another route | 23/200 | T1, power check |
| b9 | Treatment findings did not check date order | 12/200 | added |
| b10 | Issue-level citation findings were only made under a partial whole-decision status; the self-citation test used only the reported effect | 9/1000 | R-revisions |
| b11 | An unknown force lost its bound, e.g. "unknown, but at most persuasive", which hid definite findings and splits | 28/200 | `upper()` bound in `fmin`/`agree` |
| b12 | `possiblySuperseded` was emitted on evidence that failed its certificate | 3/1000 | added |
| b13 | A pre-*Erie* circuit decision on state law kept horizontal binding force in its own circuit | 7/1000 | R-pre-Erie |
| b14 | Writ-refused promotion applied to federal decisions (SCOTUS-like force) | 3/5000 | R24 narrowed |
| b15 | Firm was row/tuple identity (finding detail, segment ends) | many | per-verdict firm |
| b16 | The CFC counted as a reviewing court (introduced while fixing b1, then caught) | 2/200 | appellate tier only |
| b17 | The `reviewGranted` effect for California was keyed on the court's name, not the approved D9 rule | 41/200 | R16 (with c10) |

### Doctrine ambiguous (c): 24 readings chosen

Recorded in DEVIATIONS 30–54 and REF_NOTES "Readings settled".

| # | Point | Reading |
|---|---|---|
| c1 | unknown publication / form / trialScope / horizontal / bench / circulation / unit | the Lean's `assume*` fallbacks; the reference stopped enumerating these (domain is still enumerated) |
| c2 | unknown temporal scope, state law | retroactive (*Harper* is the general rule) |
| c3 | revival when the overruler is overruled, partly vacated, under review or of unknown status | the overruling stands (T3: not automatic) |
| c4 | which kind is reported among simultaneous effects | the most severe |
| c5 | partial against unknown on ⊤ | an unknown whole-decision event ranks above a partial one |
| c6 | an unknown event that reaches part of a decision | ⊤ is `partial` |
| c7 | a `supersededByEnactment` treatment without a law-change row | no status effect (AB1 needs the law) |
| c8 | `reversed` as a finding | `citesVacated` |
| c9 | the self-citation finding | not made |
| c10 | CA review granted | only from `reviewGrantedForce` (D9) |
| c11 | system `horizontal` row and courts of last resort | court-level rows only |
| c12 | SCOTUS-level H1 | unchanged |
| c13 | plurality decisions (HD6) | majority/per curiam parts bind; F5 caps whatever the role |
| c14 | a state court on a third system's law | binds its own lower courts |
| c15 | pre-*Erie* | persuasive (DEVIATIONS 2) |
| c16 | memorandum form | capped at persuasive |
| c17 | Tax Court with no case venue | persuasive |
| c18 | history `other` | cannot be certified |
| c19 | citation findings | issue-attributed only via the citing decision's holdings (HD4) |
| c20 | v1 `citesOverruled` binding condition | dropped (status is absolute, T1) |
| c21 | `panelDeparts` | status-changing kinds only |
| c22 | `citesUnpublishedAsBinding` | below `bindingAbsentConflict` |
| c23 | `pluralityTreatedAsBinding` | every candidate domain |
| c24 | `retroactive_to = 1` | **approximated** as asOf ≥ effective, all conduct (DEVIATIONS 31, REF_NOTES R30) |

### Data or contract (d): 4

- **d1.** SCHEMA did not type the history and treatment `id`. The reader writes strings, and the Lean expected
  numbers (fixed on the Lean side as a1).
- **d2.** `data/system_rules.tsv` has **no `reviewGrantedForce` row**, so California review grants have no effect
  on the real data. This is for the courts agent.
- **d3.** There is no court-level `horizontal` row for the **D.C. Court of Appeals**, so *M.A.P. v. Ryan*'s
  divisional rule is not applied. This is for the courts agent.
- **d4.** `stateFollowsCircuit` rows name no circuit. The Lean now derives the circuit from court names, as the
  reference does.

### Which side was wrong how often

Of the ≈ 71 classes:
- the Lean was wrong in **26** (37%);
- the reference in **17** (24%);
- **24** (34%) were open points of doctrine, now settled one way on both sides;
- **4** (6%) were data or contract problems.

The Lean errors were mostly in the unverified glue (`Run.lean`: ids, segmentation, admission, findings, splits,
firm), 15 of 26. The other 11 were in the trusted Spec:
- `canChangeStatus`: trial self-power, appellate divisions, adoption, the Federal Circuit;
- `fedHier`: F11(b);
- `relation`: E3;
- `histEffect` / `lapseOfDecision`: reinstatement and revival;
- supersession scope;
- `formCap`: HD6;
- `horizontalForce`: units.

In every case the change stayed inside the existing theorem statements. Two proofs (`no_overrule_of_binding_superior`
and `only_scotus_changes_scotus`) needed one extra `simp` hypothesis.

## 4. Residuals

- **Generated data, final sweep (seeds 20000–24999):** 5,000 rounds, 0 with a disagreement (status 0/316,963, findings 0/51,793, certs 0/465,023, splits 0/48,107 keys).
- **Stress sweep (n = 120, seeds 30000–31999):** 2,000 rounds, 1 with a disagreement: two `firm`-only differences on `cites:vacated` (seed 30984), and no verdict differences (status 0/253,453, findings 2/40,926 firm only, certs 0/372,157, splits 0/70,483).
- **Regression set:** `fixtures/regress/`, 110 universes. These are the 40 original counterexamples, plus the
  generator seeds behind every class triaged after the first iterations. `python regress.py` passes: 110 universes, 0 disagreeing.
- **Fixtures:** status 0/14, findings 0/3, certs 0/13, splits 0/1 (2 reason-only cert differences: Lean `disqualified` against reference `noTarget`, both rejecting).

The one open residual, seed 30984 (n = 120), is a **`firm` flag only**. The finding is the same on both sides. The
cited decision is wholly vacated under all the tables, but under the S/L-only tables (with a U-tagged en banc row
removed) only through its single holding. The reference's firm run reaches the same finding through the
"all holdings negative" route and marks it firm. The Lean computes the firm flag of the whole-decision row only from
the whole-decision status, so it marks it not firm. Triage: (c), a convention: is a finding firm when the S/L tables
reach the same finding by another route? Not yet unified, because it occurred in 1 of 57,000 universes. The
reference's reading is the natural one; the fix belongs in the Lean glue.

Uncompared kinds (only one side defines them) are not residuals, but they are coverage gaps for the reference:
- Lean `ignoresBindingInUnit` and `atRisk:citesLaterNegated`;
- reference `atRisk:soft/claim/contraryBinding`;
- Lean `conflict` split rows.

## 5. Real data

### Inputs and runs

- **Snapshot.** The reader rewrote `data/` during a run at 17:58, and runs that read the files at different moments
  disagreed only for that reason. Every final run therefore reads one snapshot, `difftest/snap1/`, copied at
  18:00 on 12 Nov. It holds:
  - 6,892,454 decisions;
  - 31,841 treatments, 54,940 history rows and 80,571 cert_text windows;
  - the interim holdings: 131,422 holdings, issues, marks and `holdings_cert_text.tsv`;
  - lawchanges, 13,977 supersessions, and the courts tables.
- **Command:** `difftest/run_real.sh <run> difftest/snap1`.
- **Final run:** `difftest/real11/`. The Lean outputs are in `difftest/real11/lean/`. Lean: 8 shards over 48M
  citation edges, about 70 s. The reference takes about 30 s.

Runs `real3` to `real11` were the iterations. `real3` is the coordinator's first run.

### Disagreement before and after

| File | real3 (first) | real4 | real5 | real6 | real8 (snapshot) | **real11 (final)** |
|---|---|---|---|---|---|---|
| certs | 43,623 / 87,748 (49.7%) | 3.7% | 0.27% | 0.06% | 0 / 218,200 | **0 / 218,200 (0%)** |
| status | 19,740 / 46,017 (42.9%) | 7.0% | 0.54% | 0.22% | 0.13% | **17 / 78,615 (0.022%)** |
| findings | 56,819 / 69,704 (81.5%) | 41.3% | 0.81% | 0.31% | 0.21% | **27 / 83,686 (0.032%)** |
| splits | 0 / 0 | 0 / 0 | | | 0 / 0 | **0 / 0** (see d6) |

The final residual per rule (`difftest/real11/rates.tsv`) is:

| File | Class | Keys |
|---|---|---|
| findings | onlyB panelDepartsWithoutEnBanc | 17 |
| status | partial/none (partialScope) | 16 |
| findings | firm panelDepartsWithoutEnBanc | 7 |
| findings | onlyA cites:overruled | 2 |
| status | negative/none overruled | 1 |
| status | none/negative vacated | 1 |
| findings | onlyB cites:vacated | 1 |

### Real-data classes, triage and fix (real3 → real11)

| Class (real3 keys) | Triage | Fix |
|---|---|---|
| Certificate target evidence, history ok/noTarget (20,121) and treatment (2,052): the reader names the target in the caption or citation next to the quoted sentence, inside the cert_text window, not in the quote | (c), with (b) on the reference side | The target is named in the quote **or in any well-formed window covering it** (SCHEMA ships the window for exactly this check). Both sides; R21 revised, DEVIATIONS 55 |
| Target evidence, history targetUnresolved/ok (11,198) and treatment (7,725): `cite:575 f3d 432` against "575 F.3d 432". The Lean dropped only spaces. | (a) | `Cert.compact` keeps lowercase letters and digits only, as SCHEMA's normalised citation. Names are whole words of ≥ 3 characters on both sides |
| Cues, treatment noCue/ok (1,726): "declines to follow" missed the Lean cue "decline to follow"; history `reviewGranted` "certiorari granted" | (a) | One cue table for both sides (the Lean's, widened: `declin`, `not follow`, `refuse to follow`, `reject`, `not persuaded`; `granted`). R20 revised |
| Disqualifiers, disqualified/ok (≈ 770): "dissent" or "concurring" anywhere in a majority quote ("for the reasons in the dissent below, we reverse"); "objection … overruled" in genuine overrulings | (a) Lean too coarse, and (c) on which list | The `part` column decides dissents. Only phrase disqualifiers stay (procedural rulings, reported history, refusals to overrule), the same table on both sides (R33) |
| Holding and history quoteMismatch/ok (3,533 + 1,269): the Lean used the first window covering the quote even when malformed | (a) | `coveringWindow` takes only well-formed windows (text length = end0 − start0) |
| `holdings_cert_text.tsv` not read | (a) and (b) | Both sides read it |
| Findings and status `firm` (33,419 + 2,649): untagged rows (`-`, the 2,823 v1 court epochs) counted as U in the Lean, so the firm run had almost no courts | (a) | `Tag.firmStr`: only `U` is infirm |
| Data rewritten mid-run, ok/missing (≈ 2,800) | (d) | Snapshot runs |
| History: a BAP reversing a bankruptcy court, and an Arizona CoA overruling the Arizona Tax Court, rejected by the reference | (b) | A BAP reviews its circuit's bankruptcy courts; a state special court is trial-level for vertical review and force |
| History: a bankruptcy court "vacating" a district court decision, admitted by the reference | (b) | Only a court of appeals reviews in the federal system (and a BAP its bankruptcy courts) |
| Treatment: a BAP "disapproving" a decision in another circuit, admitted by the Lean | (a) | A BAP changes no status (F13: BAP persuasive) |
| Splits 0/0 | (d) | See d6 |

### Triage of the final residual

All 45 remaining rows were triaged, a census rather than a sample; `difftest/real11/sample.tsv` holds all of them.
The 100-row stratified samples of real4–real9 (`difftest/real*/sample.tsv`) are what drove the fixes above. Every
class in them was resolved, so they leave no residual.

- **40 of 45: one pattern, D.C. Court of Appeals decisions from its intermediate era (1963–1971, a U-tagged epoch)
  treated by the same court after it became the court of last resort (1 Feb 1971).** It covers 16 status,
  17 + 7 `panelDepartsWithoutEnBanc` and part of the cites rows.
  - The Lean reads the later court-of-last-resort bench as a higher court of the system, so the overruling is
    admitted.
  - The reference reads the same court id at another tier as "the same court" for the panel-departure test, and
    finds a panel departure under the court-level `strong` row (*M.A.P. v. Ryan*).
  - Triage: **(c)**, open. Can a court overrule its own pre-promotion decisions with a panel? M.A.P. bears on D.C.
    Circuit precedent, not on this case. Left unresolved; it needs a doctrine decision.
- **5 of 45:** citation findings that follow from statuses in the same pattern (2 + 1 + 1), and one
  `none/negative vacated` row from the same D.C. epoch overlap: (c), same pattern.

### Data notes for the agents (d)

- **d5.** The reader rewrites `data/` in place, so consumers must snapshot.
- **d6. Holdings windows.** `holdings_cert_text.tsv` has start0/end0 equal to the quote's span, but the window text is
  the ±400-character context. 127,941 of 131,422 holdings therefore fail their certificate on both sides (the 3,481
  that pass also have a well-formed window in `cert_text.tsv`). SCHEMA says the window is the text from start0 to
  end0. **The holdings agent should write start0 = start − 400 (clamped) and end0 = end + 400, or trim the text.**
  Until then, holdings, and with them splits, are almost empty on the real data.
- d2 and d3 (no `reviewGrantedForce` rows; no D.C. court-level horizontal row) still stand.

### Checks after the real-data fixes

- Lean: `lake build LegalProofs.CaseLaw2` green; `audit.py check`: 84 theorems, 0 statement changes, 0 problems.
- Regression set: 110 universes, 0 disagreeing.
- A fresh generated sweep (seeds 40000–41999): 2,000 rounds with 0 disagreements over 352,787 keys
  (`difftest/drt_post_real_40000-41999.txt`).

## 6. Files

- **Lean** (lean-proofs, `LegalProofs/CaseLaw2/`):
  - Spec: `Events`, `Spec/Status`, `Spec/Authority`, `Spec/AuthorityThms` (proofs only), `Spec/Findings`;
  - checker: `Certificate`;
  - Exec: `Exec/Verdicts`;
  - glue: `Data`, `Run`;
  - tests: `Examples`, `Mutants` (SEvent field).
- **Reference and comparison** (`lean-proofs/tools/caselaw2/ref/`): `precedent_ref.py`, `diff.py`, `labels.json`,
  `gen.py`, `regress.py`, `drt_show.py`, `real_report.py`, `REF_NOTES.md`.
- **Work** (`caselaw-lean-2/`):
  - this file, `DEVIATIONS.md` (30–54), `LEAN.md`, `TRUST.md`, `STATEMENTS.log`;
  - `fixtures/regress/`;
  - `difftest/`: the final sweep reports and diffs, `real1/` and `real2/`, `run_real.sh`.

## 7. Five limits (12 Nov, second pass)

What changed is in LEAN.md "Five limits", DEVIATIONS 61–67 and REF_NOTES "Revisions: five limits" (reference written
from doctrine.md by a separate agent, L1–L7) plus "Revisions after the five-limits differential run".

**Now compared** (nothing is uncompared except the Lean's Horty `inconsistentBindingBase` and force-based
`citesNotCitable`): `ignoresBindingInUnit`; `atRisk` `citesLaterNegated`, `soft`, `claim`, `contraryBinding`;
`conflict` rows (new `conflicts` heading; the reference writes `conflicts_asof.tsv`); certificate reason `windowHash`.
The generator (`gen.py`) now also writes `cite_index.tsv`, `window_sha.tsv` (in about 2/3 of universes),
`commission.tsv`, Texas writ/petition rows of every wording, era and court, and intra-court conflicts, from a separate
random stream: `--legacy` reproduces old universes byte for byte. Driver: `ref/drt.py` (batched interpreted Lean,
because Application Control blocks `caselaw2.exe`).

**Generated sweeps, seeds 50000– (n = 60):**

| Run | Rounds | With a disagreement | status | findings | certs | splits | conflicts |
|---|---|---|---|---|---|---|---|
| drt5a (first) | 100 | 98 | 0/8,503 | 242/3,941 | 0/12,115 | 7/1,136 | 239/397 |
| drt5c | 100 | 39 | 0 | 1/3,710 | 0 | 2/1,131 | 87/362 |
| drt5g | 100 | 6 | 0 | 1/3,710 | 0 | 2/1,131 | 12/310 |
| drt5i | 300 | 2 | 0/25,518 | 2/11,083 | 0/36,328 | 0/3,431 | 4/976 |

Classes triaged on the way (a = Lean, b = reference, c = reading settled on both sides):
- (b) soft/claim rows for a target later than the treating decision (T1); (c) `ignoresBindingInUnit` narrowed in the
  Lean to §9 item 27 (trial court, ownUnit rule), not promoted decisions in the reference;
- (c) `citesLaterNegated`: the negating decision must bind the citing court on its own date on every domain;
  supersessions, unknown deciders and the citing decision itself excluded (the Lean counted history and statutes and
  asked at asOf on the assumed domain);
- (a) `contraryBinding` on an unknown issue domain: binding on every domain (D5);
- (a) conflict answers written per candidate, not as a set; (a) first-in-time keyed on the bound court, not on the
  court whose panels conflict; (a) the resolver's own-unit step keyed on the bound court's system, overriding the
  intermediate court's court-level `trialScope`; (a) court-level `trialScope` rows ignored; (a) adopted decisions
  ranked as appellate (2) instead of as their adopter; (a) a candidate with unknown force silently dropped instead of
  leaving the court undecided; (a, c) vertical displacement between candidates; (b) displacement ignoring adoption and
  dated tiers (Kentucky 1976);
- (c) `judgmentAdopted` caps any court's commissioner opinion; unclassified or absent notations are no adoption;
  special courts' own precedent is persuasiveStrong on both sides;
- (a) the firm run used U-tagged Marks rows (the last drt5i class, fixed in `Run.lean` but **not yet re-run**: see
  below).

**Done since, under WSL: see §8.** What follows is the state at 19:32.

**Not yet done, blocked:** at 19:32 Windows Application Control started blocking the toolchain's unsigned `lean.exe`
(CodeIntegrity event 3077), after it had blocked `caselaw2.exe` and the elan proxies. The last `Run.lean` edit (firm
Marks) is therefore not compiled, and the ≥ 1,000-round sweep, the regression set (now 111 with `gen120-30984`), the
fresh real snapshot run (`difftest/snap5`, taken 19:07, with `cite_index.tsv` and `window_sha.tsv`) and the final
`lake build LegalProofs.CaseLaw2` / `audit.py check` are still to run. Commands, once `lean.exe` may run:

    cd lean-proofs && lake build LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run && python ../../us-caselaw-lean-work/caselaw-lean-2/audit/audit.py check
    python tools/caselaw2/ref/drt.py --seed 51000 --rounds 1000 --out <work>/difftest/drt5k --jobs 14 --batches 10
    python tools/caselaw2/ref/drt.py --dirs <each fixtures/regress/*> --out <work>/difftest/regress5
    cd <work> && bash difftest/run_real.sh real13 difftest/snap5

The interpreted real run is slow: the first attempt on snap5 (old code) was still loading after 70 minutes and was
stopped when the code changed.

### 7.1 Queued behind the block

Written after 19:32, also uncompiled: the nine FUZZ_BUGS fixes (FUZZ_BUGS.md, each marked) with the reference's
FB-L5 match (`read_tsv` `dec=`/`flag=`), and the Horty runner needs (LEAN.md). To run when `lean.exe` may run, in this
order: build and `audit.py lock` (for `checkCert_quote_nonempty`) then `check`; the regression set and a 1,000-round
sweep (`ref/drt.py`); the fuzzer's 5,000 cases (`python -X utf8 fuzz.py run --dir ~/AppData/Local/Temp/claude/fz/big`
then `fuzz.py check --dir` the same); `factors/horty_py.py` against the fixture and the overlay; a fresh snapshot and
`difftest/run_real.sh`.

## 8. Verification under WSL, and the hunt fixes (12 Nov, evening)

Windows Application Control blocks the Windows toolchain, so everything queued in §7 ran under Linux Lean 4.35.0 in
WSL Ubuntu (`run_lean_wsl.sh`, `wsl/verify.sh`; LEAN.md "Running under WSL"). The compiled Linux runner did the real
run and the fixtures; `drt.py` drives the batched runner for generated universes, as before. Summaries copied to
`difftest/wsl/` and `difftest/real17/`; the full outputs of the final runs (`real17`, `drt6d`, `regress8`, the fuzz cases) stay in `~/caselaw2/` in WSL; the
intermediate ones were deleted to keep the mirror small.

### 8.1 The pending commands of §7, as first run (code of 19:46 plus compile fixes)

| Check | Result |
|---|---|
| `lake build LegalProofs.CaseLaw2` + `Run` | green after three compile fixes (LEAN.md "First compile") |
| `audit.py check`, then `lock` for `checkCert_quote_nonempty` | 91 theorems, 0 problems |
| Fixtures | 0 disagreements (status 23, findings 4, certs 19, splits 1, conflicts 6 keys) |
| Regression set, 111 universes | 0 disagreements (7,359 status, 2,911 findings, 10,739 certs, 1,131 splits, 50 conflicts) |
| Sweep, seeds 51000–51999, n = 60 | 1 disagreeing universe of 1,000: 1 of 36,795 findings (status 0/84,993, certs 0/121,453, splits 0/11,495, conflicts 0/3,405) |
| Fuzzer, 5,000 cases, seed 7 | P1–P4 clean; P5 only the documented 64-bit deviation (FUZZ.md run B) |
| Real data, snapshot of 20:22 (`real14`) | certs 0/346,832, splits 0/335, conflicts 0/107, **status 30/394,537, findings 119/134,193** |

The first full real run with holdings (260,054 admitted; in §5 they were almost all rejected, d6) took 2.5 minutes
for 8 shards over 48.3M edges; the reference took 47 s.

### 8.2 Triage of that residue

| Class | Keys | Triage | Fix |
|---|---|---|---|
| Sweep 51925: `ignoresBindingInUnit`, reference only. A Texas "pet. ref'd (PDR)" notation promoted the opinion in the Lean | 1 | (a) | `writPromotes` excludes PDR, denied, dismissed and w.o.j. wordings (DEVIATIONS 72) |
| Real: D.C. Court of Appeals decisions (after 1971) "overruled" by a later bench of the same court whose bench is unknown or a division. The Lean let any bench of a court of last resort overrule itself; the reference read the court-level `-627 horizontal strong` row (*M.A.P. v. Ryan*). 30 status rows, 17 `atRisk claim`, 17 `panelDepartsWithoutEnBanc`, 2 `cites:overruled`, 15 `citesLaterNegated` | 81 | (a) | H6: `divisionRelation`, `lastResortBench`, `forceDiv` (DEVIATIONS 68). This is also the D.C. pattern left open in §5: with the court-level row now in the data, the reference was right |
| Real: `citesLaterNegated`, reference only, CCPA decisions. The reference made a Federal Circuit holder bind every circuit-13 court, the CCPA included, at dates before the Federal Circuit existed (the adopter's epoch starts at 0) | 56 | (b), with (d) | b2: `F11b.reach` binds lower courts only. Data note: epochs of courts created later should not start at 0 |
| Real: `citesLaterNegated`, Lean only, pre-*Erie* federal reversals. The reference added the adopter's system (Guam, the Virgin Islands, D.C.) to the candidate domains of an unextracted issue asked at an unrelated court, where the reversal is then only persuasive | 4 | (b) | b1: candidate domains from own and succession holders and the destination |
| Real: a New York Surrogate's Court "vacating" a New York Supreme Court decision, admitted by the reference | 2 | (b) | b3: a state special court reviews no court |
| Real: `panelDepartsWithoutEnBanc` `firm` flags, Alabama | 7 | (c), open | §8.4 |

### 8.3 Hunt fixes on both sides (HUNT.md "What to fix")

Made in the Lean (LEAN.md "Hunt fixes", DEVIATIONS 68–71) and, by a separate agent from the written reading, in the
reference (REF_NOTES "Revisions: hunt fixes"): H2 (`appliesSupersededHolding` needs a conduct date and a
holding-level match; `atRisk supersededConductUnknown` instead), H3b (a known panel, a rule in force on both dates,
no federal finding before 1 Sept 1948), H4 (status after an adoption cut-off per heir, on the citation findings), H6
(divisions). The generator gained a hunt layer on its own random stream (`gen.py`, `--no-hunt` reproduces old
universes): D.C. Circuit / D.C. Court of Appeals / Ohio courts, a binding adoption with a cut-off, overrulings by the
source court, the adopter and SCOTUS with citers from every line, benches of every kind around dated rule rows, and
supersessions with citers on the same issue, the same US Code block, another issue or none.

The first sweep with that layer (seeds 52000–52999) disagreed in 86 universes (status 103/117,265, findings
234/54,988, splits 56/18,873, conflicts 106/7,118). Three classes, all about a court of last resort that holds
decisions by adoption:

| Class | Triage | Fix |
|---|---|---|
| A court of last resort (no court-level row) overruling a decision it adopted: the Lean asked for an en banc bench, the reference let any bench (H1) | (a) | `adoptedLastResortBench`: free unless the court sits in divisions |
| The divisional row for an adopted decision keyed on the precedent's date: *M.A.P.* binds the divisions to pre-1971 D.C. Circuit decisions, which a row dated 1971 does not cover | (c), both sides | Keyed on the question or treating date for adopted decisions |
| Conflict displacement: "a decision held by binding adoption is displaced only by a holding that also binds its adopter" applied at a court outside the adopter's line (a California Supreme Court holding could not displace a D.C. Circuit reading of California law at the federal district court) | (b), and the Lean reached the right answer only through precedence | b4: only an adopter in whose line the destination stands (both sides) |

After these: 300 universes (52000–52299) 0 disagreements but the b4 class (5 universes), then the final sweep below.

### 8.4 Final state (code of 21:18, data snapshot of 21:16)

| Check | Result |
|---|---|
| Build, `audit.py check` | green; 114 theorems, 4 with no axioms, 0 statement changes, 0 problems |
| Regression set, 111 universes | **0 disagreements** (7,359 status, 2,822 findings, 10,739 certs, 1,131 splits, 50 conflicts) |
| Sweep, seeds 53000–53999, n = 60, hunt layer on | **0 of 1,000 universes disagree**: status 0/117,224, findings 0/55,142, certs 0/147,692, splits 0/17,931, conflicts 0/6,839 |
| Real data (`real17`) | certs **0/346,832**, splits **0/329**, conflicts **0/107**, status **5/394,963**, findings **6/133,588** |

- **Real residue: 11 keys, all `firm` flags, one class, open (c).** The Lean writes firm = 0 and the reference firm =
  1 on 4 `panelDepartsWithoutEnBanc` rows, 2 `cites:overruled` rows and 5 status rows, all Alabama: decisions of the
  old Court of Appeals treated by the Court of Civil or Criminal Appeals. The succession rows (split, 1969) are
  S-tagged and the adoption rows U-tagged. With S/L tables only, the reference lets the successor hold the old
  court's decisions through the succession row (H3); the Lean reads inheritance only from adoption rows, so its firm
  run finds no power question. The verdicts with all tables agree. It needs a decision on whether a split successor
  inherits without an adoption row (DEVIATIONS 73).
- **Uncompared, Lean only:** `citesNotCitable` on a not-citable force (5,683 rows; 35,053 before the publication
  labels were corrected), and the Horty rows (43 `hortyConsistentBase`, 1 `inconsistentBindingBase`, 1
  `hortySelfInconsistent`). The reference has no Horty check; `horty_py.py` is its independent recomputation.
- **Horty on the real factors:** 44 binding bases examined, 43 consistent, 1 inconsistent: `horty:preemption_express`
  (pair `H5955906.0,H6088866.2`). `horty_py.py`: 51 sub-family bases, 50 consistent, all 51 agree with the runner.
  As expected, only express preemption.
- **Counts of the final run:** 486,448 status rows; 149,812 finding rows (atRisk 62,133; citesOverruled 39,575;
  citesVacated 36,020; citesNotCitable 5,701; citesWithdrawn 5,642; panelDepartsWithoutEnBanc 696);
  `bad_edges` 0 of 48,318,876.
- **Effect of the hunt fixes and the label fix on the findings** (first WSL run → final): `panelDepartsWithoutEnBanc`
  1,960 → 696; `appliesSupersededHolding` 26 → 0 (no conduct date in the data); `citesNotCitable` 35,071 → 5,701.

### 8.5 Which side was wrong, this pass

Lean (a): 3 (Texas notations; last-resort divisions; last-resort adopters). Reference (b): 4 (b1 domains, b2
Federal Circuit reach, b3 special-court review, b4 displacement). Reading settled on both sides (c): 1 (date key for
adopted decisions). Open (c): 1 (split successor without a firm adoption row). Data (d): court epochs that start at
0 for courts created later (the Federal Circuit, the Eleventh Circuit) and never end for courts that ceased
(Alabama Court of Appeals, CCPA, Court of Claims).

## 9. Round 2: status per line of authority everywhere (12 Nov, night)

Readings: DEVIATIONS 73–79. Lean: LEAN.md "Round 2". Reference: REF_NOTES "Revisions: round 2", written by a separate
agent from DEVIATIONS 73–79 alone (it did not read the Lean). All Lean jobs ran in WSL on 24 cores
(`wsl/r2_verify.sh`). The coordinator time-boxed this pass: the 500-round sweep and the final real-data diff are left
to the integration run; the commands are in `round2/lean.md`.

### 9.1 What is compared now

`diff.py` compares two more files, and skips them silently when either side lacks one (old output directories still
diff):

| File | Key | Value |
|---|---|---|
| `status_lines.tsv` (reported as `lines`) | (node, holding, line), as a timeline like `status.tsv` | class, negative kind, firm |
| `horty.tsv` (reported as `horty`) | (family, sorted holding ids of the base) | `consistent` / `inconsistent` |

The reference had no Horty check before; it now computes the binding bases itself. `court` and `firm` of `horty.tsv`
are not compared (DEVIATIONS 78). `gen.LEAN_HEADERS` and `drt.py` know the two new Lean files; the Lean runner always
writes them.

The generator has a fourth layer on its own stream (`lines`, DEVIATIONS 79; `--no-lines` reproduces earlier
universes byte for byte): Alabama-style courts (a Court of Appeals that ends at a cut-off, two adopters, a trial
court, a court of last resort), a Fifth Circuit that ends with a reorganised successor, decisions dated outside their
court's epoch, yes/no holdings and factor rows on shared issues, and overrulings by the source court, each adopter
and SCOTUS.

### 9.2 Results

| Check | Result |
|---|---|
| Build, `audit.py check` after `lock` | green; **137 theorems**, 4 with no axioms, 0 statement changes, 0 problems |
| Fixtures (with the new per-line case, nodes 20–24) | **0 disagreements** (status 27, findings 4, certs 22, splits 1, conflicts 6, lines 4, horty 3 keys) |
| Regression set, 111 universes (`regress9`) | **0 disagreements** (7,359 status, 2,822 findings, 10,739 certs, 1,131 splits, 50 conflicts, 52 lines keys) |
| Sweep, seeds 54000–54099, n = 60, all layers on (`drt7a`) | **8 of 100 universes disagree**: status 5/15,047, findings 3/7,235, certs 0/17,803, splits 1/1,924, conflicts 3/859, lines 3/1,409, horty 0/298 |
| Sweep after the reference fix b5 (`drt7b`) | **3 of 100 universes disagree**: status 0/15,047, findings 0/7,235, certs 0/17,803, lines 0/1,409, horty 0/298, splits 1/1,924, conflicts 3/859. Regression set again 0 (`regress10`), fixtures 0 |
| Real data, Lean only (`real18pre`, data snapshot 22:09) | against the Lean output of `real17`: `status.tsv` identical but for the 5 Alabama `firm` flags (0 → 1); findings: the 5 Court of Criminal Appeals `firm` flags (0 → 1) and one new row; splits identical; 546 per-line rows for 41 decisions; 44 Horty bases |
| Real data, reference only, before and after its edits (no edges) | `status.tsv`, certs, splits, conflicts identical; findings: the Court of Civil Appeals `firm` flag (1 → 0) and the same new row |

- **The per-line rows on the real data** (41 decisions): 34 held by the Eleventh Circuit (*Bonner*), 3 by the D.C.
  Court of Appeals (*M.A.P.*), 3 by the two Alabama courts, 1 by the New York Court of Appeals.
- **The one new real finding:** `atRisk 2874534 948665 soft:declinedToFollow`. The target is negative in the union and
  not in the treating court's line (DEVIATIONS 76). Both sides make it.
- **The `firm` residue of §8.4 (11 keys)** is expected to be 0 in the integration run: the Lean now writes firm = 1
  on the 10 Court of Criminal Appeals keys (adoption row tagged S) and the reference writes firm = 0 on the Court of
  Civil Appeals key (a split alone transfers nothing). Seen on each side separately; the two-sided real diff was
  not run in this pass.

### 9.3 Triage of the sweep residue (`drt7a`)

All eight universes involve the new layer's courts whose epoch ended.

| Class | Keys | Triage | State |
|---|---|---|---|
| SCOTUS overrules a decision of a state court that has since ceased, issue domain unknown. The Lean: `unknown:powerUnknown` on the anonymous issue (state law or federal law: the candidates disagree, D5), overruled on a federal holding. The reference: negative. It had dropped the deciding court's own system from the candidate domains once the court had no later epoch and only adopters held the decision. Also behind 2 `atRisk claim`, 1 `atRisk soft` and 3 `lines` keys | 5 status, 3 findings, 3 lines | (b) reference | b5: the target's own court on its own date always gives a candidate domain. Fixed; the rerun has 0 status, findings and lines disagreements |
| A conflict at an adopter (the Court of Civil Appeals, the Alabama circuit court) between a decision of the ceased court, good law only in that adopter's line, and SCOTUS holdings the other way. The reference reports both answers; the Lean lets the SCOTUS holdings prevail by precedence | 2 conflicts (+1) | open | Next round |
| A split Eleventh Circuit / E.D. La. that only the reference reports, in a universe where the Fifth Circuit's epoch ended and a reorganised court took its place | 1 split | open | Next round |

Which side was wrong, this pass: Lean (a) 0 so far; reference (b) 1 (b5); open 2.

### 9.4 After the coordinator's 500-round sweep (`drt8`, seeds 56000-56499: 15 universes)

| Class | Rounds in `drt8` | Triage | State |
|---|---|---|---|
| `firm` flags on status (4) and findings (3): SCOTUS, or another court with power, acting on a decision of a court whose epoch ended by a split, where the adoption row is U. The reference's firm run left such a decision with no holder (power unknown), so firm = 0; the Lean reads the deciding court on the decision's own date, so firm = 1 | 7 | (b) reference | b6, fixed: a court whose only successors are splits stays the holder of its own decisions (dated tier), with or without an epoch on the question date |
| Horty base only in the Lean (the cases of a ceased court had no force in the reference) | 3 | (b) reference | b6, fixed |
| Split only in the reference (Eleventh Circuit / E.D. La.) | 1 | (b) reference | b6, fixed (none in `drt9`) |
| Conflict only in the reference, at an adopter or a trial court below it, between a ceased court's decision good law in that line and holdings the other way | 7 | open, not triaged | Next round |

Final runs (code of 22:50): regression set `regress13` **0 disagreements** (111 universes). Sweep `drt9`, seeds
57000-57499, n = 60, all layers: **8 of 500 universes disagree, conflicts 17/4,977 only**; status 0/75,511, findings
0/35,566, certs 0/89,748, splits 0/10,939, lines 0/7,332, horty 0/1,450.

Which side was wrong, round 2: Lean (a) 0; reference (b) 2 (b5 candidate domains, b6 holder of a ceased court); open 1
(conflict at an adopter of a ceased court). Not changed in the reference: after a rename, replace or absorb the
successor holds, as before.

## 10. Round 3: the conflict class at an adopter of a ceased court (12 Nov, late night)

The open class of §9.4 (conflict rows only in the reference, at an adopter of a ceased court or a trial court below
it; `drt9`: 17 of 4,977 conflict keys, 8 universes) had one root on both sides. The displacement test among conflict
candidates read the force on the deciding court on asOf. A ceased court has no epoch on asOf, so that force was
unknown and nothing displaced its decisions. Both engines now ask a ceased deciding court as it last sat
(DEVIATIONS 80). Triage: a reading both sides lacked; changed on both sides; no locked statement touched.

| Run (code of 22:50, both sides) | Result |
|---|---|
| The 8 disagreeing universes of `drt9` (`r3_fail8`) | 0 disagreements; conflicts 0/78 |
| Regression set, 114 universes (111 + 3 kept from `drt9`: `r3-ceased-57420`, `-57295`, `-57433`) (`r3_regress1`, again `r3_regress2` at 23:05) | 0 disagreements |
| Sweep, seeds 61000-61239, 240 universes (`r3_drt1`) | 0 disagreements; conflicts 0/2,182 |
| Final sweep, seeds 62000-62499, 500 universes, all layers (`r3_drt2`) | 3 universes disagree (62003, 62350, 62391), conflicts only: 10 of 4,668 keys. Status 0/75,045, findings 0/34,862, certs 0/89,479, splits 0/11,053, lines 0/7,149, horty 0/1,396 |

**Residue of `r3_drt2` (open, not triaged).** All 10 keys are conflict rows that only the reference reports, on the
generator's state issue `tx.a`, at the adopter court (102, whose epoch starts the day after the adoption cut-off) or a
court under it. In the two universes looked at, the reference's candidates include a holding whose force on one
candidate's deciding court is `unknown: dstEpoch` (a court with no epoch on asOf and, it seems, none before it, so
"as it last sat" does not apply). Which side is right was not decided. The three universes were not added to the
regression set. None on real data.

Which side was wrong, round 3: a reading missing on both sides 1 (DEVIATIONS 80); open 1.

## 11. Round 4: witness rows, one cue table, and the last sweep residue (12 Nov, 23:15–23:35)

Code changed on both sides: witness rows (`Cert.checkWitness`; reference `check_witness`; DEVIATIONS 83), one
generated cue table (85), the panel finding's own-words test (84), and the two writ-refused precedence fixes (82:
Lean was wrong; 86: the reference was wrong). The first real-data run of the round showed 170 certificate keys and
145 findings that differed: one reference bug (the by-evidence copy of the certificate was built with integer
offsets and failed its own offset parse). Fixed in the reference; class: reference wrong.

### 11.1 Final state (code of 23:32, data snapshot of 23:25)

| Check | Result |
|---|---|
| Build, `audit.py check` | green; 141 theorems, 4 with no axioms, 0 statement changes, 0 problems |
| Regression set, 118 universes (`r4_regress2`) | **0 disagreements** (8,406 status, 3,311 findings, 12,023 certs, 1,241 splits, 138 conflicts, 144 per-line rows, 23 Horty) |
| Sweep, seeds 63000–63499, 500 universes, all layers (`r4_drt2`) | **0 of 500 universes disagree**: status 0/75,396, findings 0/35,295, certs 0/89,464, splits 0/10,602, conflicts 0/4,603, per-line rows 0/7,228, Horty 0/1,377 |
| Real data (`real20`) | certs **0/350,651**, splits **0/360**, conflicts **0/92**, status **0/398,482**, findings **0/168,276** |

- The sweep before the reference fix 86 (`r4_drt`): 1 universe, 3 of 4,606 conflict keys. The generator writes no
  witness rows: the witness checker is compared on the real data only (179 rows) and by `#guard`s in `Examples`.
- The four universes of 82 and 86 are in the regression set (`r4-62003`, `r4-62350`, `r4-62391`, `r4-63322`).
