# Round 2, agent `courts`: court epochs and the three rule dates

2026-11-12. Installed in `data/`: `courts2.tsv`, `system_rules.tsv`, `succession.tsv`, `adoption.tsv` (tmp + rename;
originals kept as `data/*.pre_round2.tsv`). `court_alias.tsv` and `decisions2.tsv` were not touched.

Scripts (lean-proofs `tools/caselaw2/`): `epochs_fix.py` (new), `rule_dates_fix.py` (rewritten). Both can be rerun
(`--install` writes into `data/`). Docs: two "Round 2" sections appended to `data/COURTS.md`, § 7 appended to
`data/courts_validation.md`. Work files: `work/round2/courts/`.

## Task 1: court epochs

### How both engines read epochs
- A row covers date d when from ≤ d ≤ to (reference `Engine.epoch`; Lean `epochCovers`). `epoch_to = 0` is read as
  open by both (`Run.lean` `epochOf`; reference `Epoch.__init__`). The file keeps 99991231 for open.
- A date that no row covers gives no epoch. Then: a decision of that court dated there has unknown force
  (`srcEpoch`, Lean `sourceEpoch = none`) and no power (`canChangeStatus = none`); a question at that court is
  unknown (`dstEpoch`); an adopter does not hold (`adoptedForce = .none`; reference `holders` skips it); the court is
  skipped as a split or conflict destination; in `reachOf` "the original court has no epoch" becomes true, so an
  adopter's overruling reaches the original line; in the reference `holders`, a split court that is gone no longer
  keeps its own decisions (the successors hold them).
- Representation chosen: bounds on the first and last row of a court; internal rename boundaries unchanged
  (a rename with old = new was already two rows meeting at the date); decisions dated after a firm end get separate
  "cluster rows" so that no decision is outside its court's rows.

### Rules (full text in `epochs_fix.py` and COURTS.md)
- S/L succession dates (and a short `KNOWN_START` / `KNOWN_END` table, plus the U.S. circuit courts, abolished
  1912-01-01, L) are bounds. replace, absorb and rename (old ≠ new) end the old court; a split ends it only when
  under 5% of its decisions are dated on or after the date.
- U dates are not used as bounds: the bound is taken from the data.
- Data-derived bounds are year edges (1 Jan of the first-decision year, 31 Dec of the last-decision year), src
  `data:first-decision` / `data:last-decision`. Start = min(first decision, anchor). Without an anchor a court gets
  a start only when its first decision is 25 or more years after its system's start, and never an end.
- Decisions after an S/L end (misrouted or misdated) get cluster rows (date gap ≤ 366 days, exact dates,
  src `data:decision-cluster`).
- Bound sources are appended to src (`| from:…[tag]`, `| to:…[tag]`); the row tag is unchanged.

### Counts
| | before | after |
|---|---|---|
| rows | 3,019 | 3,106 |
| court ids with a non-zero first from | 86 | 2,671 |
| court ids with a closed last to | 7 | 168 |
| decisions dated outside their court's rows | 0 | 0 |

No existing multi-epoch row violated the rule. No decision is undated.

By source. from: succession S 4, succession L 7, known S 1, known L 4, data:first-decision 2,576. to: succession S
4, succession L 10, known L 135 (133 circuit courts, Commerce Court, old NJ Supreme Court), data:last-decision 17.
Cluster rows: 88 (47 courts, 839 decisions; `work/round2/courts/epoch_clusters.tsv`).

Examples: Federal Circuit from 1982-10-01 (S); Eleventh Circuit from 1981-10-01 (S); Tenth Circuit from 1929-02-28
(L); Alabama Court of Appeals 1911-01-01 to 1969-09-30 (S) plus 6 cluster rows (21 decisions, 1978–2003); CCPA and
Court of Claims to 1982-09-30 (S; Court of Claims plus 4 cluster rows, 486 decisions to 1992); Kentucky 913 to
1975-12-31, 914 and 917 from 1976-01-01 (S); New Jersey 1094/1095 to 1948-09-14, 1096/1099/1222 from 1948-09-15 (L);
D.C. Court of Appeals from 1942-01-01 (data).

Other table changes: `succession.tsv` 655→520 and 654→520 L → S, and `adoption.tsv` 520←655 L → S (*South Corp. v.
United States*, 690 F.2d 1368, 1369 (Fed. Cir. 1982) (in banc), read in the corpus: "established October 1, 1982");
`succession.tsv` 1→3 kind `split` → `rename` (Lean agent's note; Act No. 987: the Court of Appeals became the Court
of Criminal Appeals, as the row's src already said). The Alabama adoption rows were not touched.

## Task 2: three dates

4 of 8 web searches used. The decisions were read in the local corpus (primary sources).

| item | result | tag | source |
|---|---|---|---|
| Ohio within-district rule | start moved 2010-07-01 → **2008-10-02**; soft before | S (was L) | *McFadden v. Cleveland State Univ.*, 120 Ohio St.3d 54, 2008-Ohio-4914 (decided 2008-10-02), ¶¶ 15, 19–21 (node 5369328). App.R. 26(A)(2), in force 2010-07-01, is only the procedure (Staff Note). *In re J.J.*, 2006-Ohio-5484, said it earlier for a district with a local rule |
| Louisiana within-circuit rule | date kept at 1997-01-01, tag **S → U** | U | No source gives 1997 (*Orillion* is about sister circuits). Within-circuit statements: 4th Cir. 1985-03-12 (*Shewmake*, 466 So.2d 711), 4th Cir. 1993 (*Wolfe*), 1st Cir. 1996 (*Graves*, 673 So.2d 311, 315). No internal rule found. A 1985 start was tried and lost 15 status rows (en banc overrulings whose unit does not match the precedent's unit in the data), so it was not installed |
| Federal en banc date 1948-09-01 | **confirmed, unchanged** | S (was L) | *Ex parte Collett*, 337 U.S. 55 (1949): "September 1, 1948, the effective date of the present Judicial Code"; *Western Pacific R. Corp.*, 345 U.S. 247 (1953): § 46(c) "is but a legislative ratification of *Textile Mills*" |

Meaning of the federal constant: from *Textile Mills* (1941-12-08) a circuit could sit en banc if it had a rule for
it (the Third had; the Ninth had held it could not). From 1948-09-01 every circuit has an en banc court by statute.
The constant is the first day a panel of any circuit had an en banc court to go to. It is a floor for
`panelDepartsWithoutEnBanc`, not the start of each circuit's prior-panel rule.

Caveat (Ohio): the date is confirmed; the value `withinUnitOnly` is the hunt's reading (*McFadden* leaves discretion
on whether a conflict exists; App.R. 26(A)(2)(a) says "may order").

## Reference run, before and after

One frozen copy of `precedent_ref.py` (22:10, md5 7cfa6a50…) on one snapshot of `data/` (21:52), my four tables
swapped in. Outputs: `work/round2/courts/out_b` (before), `out_a` (epochs only), `out_final` (installed tables).

| file | before | after | changed rows |
|---|---|---|---|
| status.tsv | 69,256 | 69,256 | 0 |
| status_lines.tsv | 105 | 110 | +5 |
| findings.tsv | 141,049 | 140,939 | 165 gone, 55 new |
| splits.tsv / splits_asof.tsv | 393 / 332 | 393 / 332 | 0 |
| conflicts_asof.tsv | 107 | 107 | 48 rows with another destination id |
| certs.tsv, horty.tsv | 346,832 / 44 | same | 0 |

Triage of the changed findings (all rows read by cause; lists in `work/round2/courts/diff_*_findings.tsv`):
- **113 `atRisk citesLaterNegated` gone (epochs).** The citing court had ended before the negating decision's date,
  and the rule asks "does the negating court bind the citing court on the negating date". By citing court: U.S.
  circuit courts 25, Court of Claims 33, NJ Court of Chancery 11, Texas Commission of Appeals 11, Kansas Court of
  Appeals 7, Colorado Court of Appeals 6, Alabama Court of Appeals 6, CCPA 3. Looks wrong for the successor case;
  see "For the Lean owner" 1. The other 11 are federal district courts of Alabama and Florida citing Fifth Circuit
  decisions that the Fifth Circuit negated before 1981: their rows carry circuit 11 at every date, and the Eleventh
  Circuit (through which the old Fifth bound them) now starts in 1981. This is a data gap in `courts2.tsv`, not
  fixed: those district rows need a circuit-5 epoch before 1981-10-01 (same for Tenth Circuit districts before
  1929). See "Next round".
- **1 `citesOverruled` new (epochs).** Alabama Supreme Court (1985-09-27, node 58405) cites an Alabama Court of
  Appeals decision of 1929 (80815) that the Court of Criminal Appeals overruled en banc on 1985-03-12 (116047). The
  original court is gone, so the overruling now reaches the original line. This is the intended effect
  (DEVIATIONS 69, limit a).
- **48 conflict rows.** The trial destination was the first trial row in file order, an abolished U.S. circuit
  court (e.g. 374, 242); it is now the first living one (390, 257). Intended.
- **52 findings firm 1 → 0 (rules).** Louisiana: 48 `citesLaterNegated`, 1 `claim`, 3 `panelDepartsWithoutEnBanc`;
  the Louisiana row is now U.
- **2 `citesLaterNegated` new (rules).** Ohio, the 2008-10-02 to 2010-06-30 window.
- `eval/score.py` was not run: status, splits and certs are identical.

## For the Lean owner

1. **`citesLaterNegated` and ended courts** (`Run.lean` `lateNeg` / `bindsCiting`, `cAt := { ci with date :=
   ad.date }`). When the citing court has no epoch on the negating decision's date, `forceOn` is `none` and the
   finding is dropped. The reference lost 102 such rows; the Lean should lose the same. Suggested reading: ask at
   the citing court's epoch on the citing date, or at its successors and binding adopters, when it has no epoch on
   the negating date. Both sides must change together.
2. **Date 0.** `epochAt c 0` now finds nothing for most courts (first from > 0). The reference returns the single
   row of a one-row court for date 0. No real decision is undated; generated tests may hit it.
3. **Cluster rows.** A dead court has an epoch on the dates of its stray decisions (e.g. court 1 on 2003-06-13 to
   12-12), so "the original court has no epoch" is false on those days.
4. **Split destinations** now skip ended courts; `conflicts_asof` changed 48 destination ids in the reference.
5. **Alabama 1→3 is now `rename`.** `reachOf` treats a non-split successor as reaching the original line. DEVIATIONS
   73 (split successor without a firm adoption row) now concerns 1→2 only.
6. **`enBancStatuteDate` = 19480901 is confirmed. Do not change it.** Doc changes:
   - `Basic.lean` doc comment: "The Judicial Code of 1948 (Act of June 25, 1948, ch. 646; 28 U.S.C. § 46(c)) took
     effect on 1 Sept 1948 (*Ex parte Collett*, 337 U.S. 55 (1949)) and gave every court of appeals an en banc court
     by statute; it ratified *Textile Mills*, 314 U.S. 326 (1941) (*Western Pacific R. Corp.*, 345 U.S. 247 (1953)),
     under which a circuit could sit en banc only if it had provided for it by rule. Before this date no
     `panelDepartsWithoutEnBanc` (hunt H3b). Tag S."
   - DEVIATIONS 71: "(`enBancStatuteDate`, 28 U.S.C. § 46(c); tag L)" → "(…; tag S: *Ex parte Collett*; *Western
     Pacific*)". Last sentence → "Ohio is soft before 2 October 2008 (*McFadden*, 2008-Ohio-4914; tag S). Louisiana
     is within-circuit from 1997 (tag U: no source gives the date; statements go back to 1985)."
   - DEVIATIONS 69, limit (a) → "court epochs now have ends (round 2, `epochs_fix.py`): after Alabama 1969 a
     successor's overruling reaches the original line, except on the dates of cluster rows."
   - TRUST.md line 149: the federal date and the Ohio date are S; the Louisiana row is U.
   - LEAN.md line 506: "Ohio and Louisiana rows dated in the data" → add "(Ohio 2008-10-02, S; Louisiana 1997, U)".
   - SCHEMA.md, courts2: "epoch_from / epoch_to bound the court's existence; 0 / 99991231 = open; bound sources in
     src".

## Next round

- Re-route the 839 stray decisions (cluster rows) in `court_alias.tsv` and `decisions2.tsv`, then drop cluster rows.
  Largest: Court of Claims 1982–1992 (486, → Claims Court 656), Republic of Hawaii 2017–2019 (88), Kansas Court of
  Appeals 1919–1971 (80, probably the Kansas City Court of Appeals), NJ Court of Chancery (17), Alabama (21).
- Give the district courts of the Eleventh Circuit states a circuit-5 epoch before 1981-10-01 (and Tenth Circuit
  districts a circuit-8 epoch before 1929-02-28); 11 `citesLaterNegated` rows were lost for this reason.
- 17 courts start too early because of decisions dated before their creation (list in COURTS.md).
- Louisiana: recover units, then move the row's start to the evidence (1985) or to per-circuit rows.
- Ohio: check whether `withinUnitOnly` or `soft` is the better value after 2008.
- Unverified L dates: Tenth Circuit 1929-02-28, the 1912 circuit-court abolition, the Commerce Court, New Jersey
  1948-09-15, Claims Court 1982-10-01 (654→656).
- Fix 1 above (102 findings).
