# Courts and decisions (agent: courts)

These files are the "Courts and decisions" part of `SCHEMA.md`:
- court epochs;
- successions;
- adoptions;
- system rules;
- one row per decision.

All files are UTF-8 with LF line endings, tab-separated, with no header line. Dates are yyyymmdd integers: 0 means unknown or "from the beginning", and 99991231 means open-ended.

Scripts are in `~\Documents\global-law-lean\lean-proofs\tools\caselaw2\`. Work files are in `../work/courts/`.

## Id space

- **court_id is the v1 id of `lean-in-v3/courts.tsv`.** That id is the row index of `graph/court_table.tsv`, one per court name and v1 era. SCOTUS is 2906. 3160 is the unmapped court (system 999).
- **It is not the court index in column 4 of `graph/nodes.tsv`.** That is the name index of `graph/courts.tsv`, and the two drift apart after id 633 (SCOTUS is 2916 there).
- **Translation.** Decisions are translated explicitly: `court_alias.tsv` maps (graph name index, date) to court_id.
- **Checks** (`tools/caselaw2/report.py`, results in `courts_validation.md` §3):
  - all 384,140 SCOTUS decisions get 2906;
  - the 360,174 decisions whose court_id differs from `lean-in-v3/decisions.tsv` are all explained by `court_alias.tsv`.
- **One canonical id per court.** A court known under several names keeps the v1 id of its main name. The other names are aliases: they are listed in `court_alias.tsv`, and no decision points at them.
- **New ids from 10000 up** are used for:
  - courts that v1 did not separate (for example the South Carolina Court of Appeals of 1824–1868, which was the court of last resort);
  - names that v1 left unmapped (tribal courts, circuit Judicial Councils);
  - the West Virginia Intermediate Court of Appeals (created 2022, no decisions in the data);
  - **unit rows**, one per district, division or department, plus the three pre-1972 Missouri Courts of Appeals.

## courts2.tsv (3,019 rows, 2,991 court ids)

Columns: court_id, epoch_from, epoch_to, name, system, tier, last_resort_for, circuit, unit, src, tag.

- **Epochs.** There is one row per epoch. Each court's epochs tile 0–99991231, and a decision takes the epoch containing its date. Historical creation and abolition dates are given in src and in `succession.tsv`; the epochs mark role and name changes.
- **system** follows the v1 indices (`courts_map.STATES`): 0 federal, 1–50 states alphabetically, 51 DC, 52 PR, 53 Guam, 54 VI, 55 American Samoa, 56 NMI, 57 Dakota Territory, 59 Indian Territory, 999 unknown. v1's lumped tribal system 61 is no longer used: each tribe's judiciary is its own system from 1000 up (see "Tribal systems" below).
- **tier** is L, A, B, T, S or D. B (bankruptcy appellate panels) and D (appellate divisions or terms of trial courts) are new in v2.
- **last_resort_for** is all, civil, criminal or -.
- **circuit** is 1–13 for federal courts and 0 otherwise.
- **unit** is 0 on whole courts and k on unit rows.
- **tag** is `-` for rows that only restate the v1 mechanical mapping. Doctrine rows are tagged L 148, S 30, U 16.

**Dated roles** encoded as epochs or separate ids:

| court | dated role |
|---|---|
| Kentucky Court of Appeals | Before 1976-01-01: v1 id 913, L (last resort for all cases). From then on: v1 id 914, A. Both name spellings route by date. |
| Supreme Court of New Jersey | Before 1948-09-15: 1095, A. From that date: 1096, L. This corrects v1's year boundary. The Court of Errors and Appeals (1094) is L until then. |
| D.C. Court of Appeals (627) | Municipal Court of Appeals, A, to 1962-12-31. D.C. Court of Appeals, A, from 1963-01-01 (Pub. L. 87-873; date computed from its 60-day clause, U). L from 1971-02-01. Pre-1942 decisions under the D.C. names go to the federal D.C. Circuit (514), which has three name epochs (1934, 1948). |
| Texas | Supreme Court 2927: L civil. Court of Criminal Appeals 2928: L criminal, with the 1876–1891 Court of Appeals as its first epoch. |
| Oklahoma | Supreme Court 2574: L civil. Court of Criminal Appeals 2571: L criminal, renamed from "Criminal Court of Appeals" on 1959-03-11 (20 O.S. § 31.1, Laws 1959 p. 107, emergency clause; L: statutory history note, session law not seen). |
| Maryland | Court of Appeals → Supreme Court of Maryland, and Court of Special Appeals → Appellate Court of Maryland, both on 2022-12-14 (S, verified). There is no data after 2019. |
| Connecticut | Supreme Court of Errors → Supreme Court on 1965-12-30, when the governor proclaimed the 1965 constitution (art. XIV; S). |
| Delaware | Court of Errors and Appeals (609) to the 1897 constitution (its decisions end in 1897; day not verified, U). Supreme Court (610): the 1897-constitution court of last resort, then the separate Supreme Court from 1951-05-14 (Del. Const. art. IV § 35, 48 Del. Laws c. 109; S). |
| Virginia | Court of Appeals → Supreme Court of Appeals → Supreme Court (1830, 1971-07-01). The 1985 Court of Appeals is separate (3018). |
| California | District Courts of Appeal → Courts of Appeal by Prop. 1-a, adopted at the 1966-11-08 election (effective day not confirmed, U). |
| Indiana | Appellate Court → constitutional Court of Appeals on 1972-01-01 (amendment ratified 1970-11-03; in.gov court history, S). Same id 880. |
| Missouri Court of Appeals | Before 1972 it is the three separate courts; unified from 1972-01-01. |
| Puerto Rico | Tribunal de Circuito de Apelaciones → Tribunal de Apelaciones on 2003-11-20 (Ley 201-2003 art. 9.004: 90 days after its approval on 2003-08-22; S). Ley 201-2003 is itself replaced by Ley 222-2026 (approved 2026-11-03, in force about 2027-03-03); there is no data after 2010. |
| Federal special courts | Customs Court → CIT; Board of Tax Appeals → Tax Court; Claims Court → Court of Federal Claims; CMA → CAAF; Courts of Military Review → Courts of Criminal Appeals; CVA → CAVC. |

**Re-tiering and system fixes.**
- **Mis-tiered appeals courts → A:** the Texas Courts of (Civil) Appeals, the Alabama and Tennessee Courts of Criminal Appeals, and the Massachusetts Appeals Court. Counts are in `courts_validation.md` §3.
- **Territorial high courts → L:** Hawaii (territory and republic), the Virgin Islands, American Samoa, Dakota, the Northern Mariana Islands and Indian Territory.
- **The NY Supreme Court of Judicature (L → A).**
- **Appellate terms and divisions of trial courts → D.**
- **Systems taken from the repo** where v1 read a county name as a state: 48 courts, e.g. "Delaware County", "Washington County", Kansas City Court of Appeals → Missouri.
- **State courts of claims and tax courts → their state** (v1 had them as federal).
- **Puerto Rico Court of Appeals → state A** (v1 had it as federal trial).
- **Federal fixes:** the "Six Circuit" and "Ninth" name typos; CCPA (unmapped spelling); "United States Supreme Court of the District of Columbia" → the D.C. trial court.
- **Name variants merged:** 30 by normalised name (for example "Court of Appeals of Iowa" and "Iowa Court of Appeals").

**Units.** Units are numbered within their court. A unit is identified by (court_id, unit), and its row (id ≥ 10000) has src `unit-of:<court_id>`.

| court | units |
|---|---|
| Florida DCA (688) | 1–6; the 6th from 2023-01-01 |
| Texas Courts of Appeals (2951) | 1–15, by number (1 Houston/Galveston … 14 Houston [14th]); the 15th from 2024-09-01 |
| California Courts of Appeal | districts 1–6 |
| NY Appellate Division | departments 1–4 |
| NY Appellate Term | departments 1–2 |
| Louisiana | circuits 1–5 |
| Ohio | districts 1–12 |
| Illinois | districts 1–5 |
| Missouri | 1 Eastern / St. Louis, 2 Western / Kansas City, 3 Southern / Springfield |
| Washington | divisions 1–3 |
| Arizona | divisions 1–2 |
| Indiana | districts 1–5 |
| Oklahoma Court of Civil Appeals | divisions 1–4 |
| Tennessee CoA and CCA | grand divisions 1 E, 2 M, 3 W |
| Fifth Circuit (346) | 1 = Unit A, 2 = Unit B (see below) |

**Tribal systems** (`limits_fix.py`, 2026-11-12). Tribal courts are separate sovereign systems (doctrine §3.2 tribal: "Model as separate systems"). There is one system per tribe, not per court id, so that a tribe's appellate court and its trial courts share a system:

| system | tribe | court ids |
|---|---|---|
| 1000 | Navajo Nation | 2973–2977, 10007 Window Rock, 10015 Crownpoint, 10017 Shiprock, 10022 Chinle |
| 1001 | Eastern Band of Cherokee Indians | 2953, 2959, 2960, 10023 |
| 1002 | Cherokee Nation | 2954, 2955 |
| 1003 | Cheyenne River Sioux Tribe | 2956 |
| 1004 | Colville Confederated Tribes | 2957 |
| 1005 | Coquille Indian Tribe | 2958 |
| 1006 | Fort McDowell Yavapai Nation | 2961, 2962 |
| 1007 | Fort Peck Assiniboine and Sioux Tribes | 2963, 10004 |
| 1008 | Grand Traverse Band of Ottawa and Chippewa Indians | 2964, 2965 |
| 1009 | Ho-Chunk Nation | 2966, 2967 |
| 1010 | Leech Lake Band of Ojibwe | 2968 |
| 1011 | Little River Band of Ottawa Indians | 2969, 2970 |
| 1012 | Mohegan Tribe | 2971, 2972, 10005, 10011, 10025 |
| 1013 | Oneida Nation | 2978, 2979 |
| 1014 | Sac and Fox Nation | 2980, 2981 |
| 1015 | Eastern Shoshone and Northern Arapaho (Wind River) | 2982 |
| 1016 | Swinomish Indian Tribal Community | 2983, 2984 |
| 1017 | Little Traverse Bay Bands of Odawa Indians | 2985 |
| 1018 | Confederated Tribes of the Grand Ronde Community | 2986, 10010 |
| 1019 | Tulalip Tribes | 2987 |
| 1020 | White Earth Band of Chippewa | 2988 |
| 1021 | Hopi Tribe | 10006 |
| 1022 | Confederated Salish and Kootenai Tribes | 10008 |

Tiers are unchanged (S, except the Navajo Nation Supreme Court and Court of Appeals, L). Pueblo County District Court (579), which v1 had in the tribal system, is a Colorado state trial court (system 6, tier T; 7 decisions, 1883–1901).

**Military courts.** `adoption.tsv` has CAAF (650) → binding on each service Court of Criminal Appeals (Army 639, Navy-Marine Corps 673, Air Force 636, Coast Guard 646) and on the older Navy Court of Military Review (671) and the collective "Courts of Military Review" (661), up to 99991231 (10 U.S.C. §§ 866–867: CAAF reviews their decisions). The courts stay tier S in system 0. Because an adopter may act on adopted decisions under its own horizontal rule (DEVIATIONS 41), a CCA en banc treatment row could in principle reach a CAAF decision; no such row exists.

## court_alias.tsv (3,233 rows)

Columns: v1_id, graph_court_index, name, date_from, date_to, court_id, unit_from_name, route.

This is how decisions get their court. route is one of:
- self;
- alias;
- canonical;
- era:… (a date split);
- fix:… (a corrected mapping);
- unmapped.

## succession.tsv (63 rows)

Columns: old_court, new_court, date, kind (rename|replace|split|absorb), src, tag. Tags: L 31, S 11, U 21.

- **A rename that keeps its id** is written with old = new, for example (934, 934, 20221214, rename).
- **Covered:**
  - federal: 5th → 11th Circuit (1981-10-01); 8th → 10th (1929); CCPA and the Court of Claims → Federal Circuit / Claims Court (1982-10-01); the federal special-court renames;
  - states: Kentucky, New Jersey, D.C., Alabama (1969-10-01, verified), Connecticut, Delaware, Hawaii, Maryland, Massachusetts, Mississippi, Missouri, NY (1847, 1896), Oklahoma, Indian Territory, Dakota (one-to-many split), South Carolina, Tennessee, Texas, Indiana, California, Virginia, Puerto Rico, the Virgin Islands, Navajo Nation, the Florida DCA unit splits (2d → 6th on 2023-01-01).
- Unit rows appear as old and new where units split or absorb.

## adoption.tsv (41 rows)

Columns: adopter_court, source_court, up_to_date, filter, force, src, tag. Tags: S 7, L 13, U 21.

- **filter values:**
  - `all`;
  - `unitB`: decisions of the source with unit = 2;
  - `notTrialDivision`: Court of Claims; not separable in the data;
  - `opinionAdopted`, `holdingApproved`, `judgmentAdopted`, `none`: the notation on a Texas Commission of Appeals decision (see `commission.tsv`);
  - `issue:localLaw`: the source binds only on local-law issues.
- **force** uses doctrine's scale: binding, persuasiveStrong, persuasive, resultOnly, …
- **Key rows:**
  - 11th Circuit ← 5th up to 1981-09-30 (Bonner, S); 11th ← 5th `unitB` to 1982-12-31;
  - Federal Circuit ← CCPA and Court of Claims up to 1982-09-30;
  - 10th ← 8th up to 1929, persuasive only (McMorris);
  - D.C. Court of Appeals ← D.C. Circuit up to 1971-01-31 (M.A.P. v. Ryan, S);
  - new Kentucky Court of Appeals and Kentucky Supreme Court ← old Court of Appeals (SCR 1.030(8)(a), S);
  - Texas Supreme Court ← Commission of Appeals by notation (McKenzie, S; others U);
  - 6th DCA ← 2d DCA, persuasive (U);
  - Puerto Rico ← 1st Circuit, Guam ← 9th Circuit (to 2004-10-29: Pub. L. 108-378, approved 2004-10-30), Northern Mariana Islands ← 9th Circuit (to 2004-05-01: the 15-year sunset of 48 U.S.C. § 1824(a); day uncertain), Virgin Islands ← 3d Circuit, all on local law (U, S for VI);
  - each service Court of Criminal Appeals ← CAAF, binding (10 U.S.C. §§ 866–867, L; see Military courts above).

## system_rules.tsv (307 rows)

Columns: system, rule, value, from, to, src, tag. Tags: S 133, L 99, U 75.

- **Systems covered:** all 50 states, DC, PR, GU, VI, AS and MP (56 systems), plus the federal system.
- **Court-level rows** use system = -court_id. These cover:
  - each of the 13 circuits (horizontal, firstInTimeControls, circulationCountsAsEnBanc, enBancGrantVacatesPanel, unpubForce);
  - SCOTUS;
  - the five bankruptcy appellate panels;
  - the Pennsylvania Commonwealth Court;
  - the Tax Court.
- **Per state:**
  - horizontal and trialScope (doctrine §4.3). Where doctrine marks a "?", the row is our best reading, tagged U;
  - unpubForce, as dated rows;
  - stateFollowsCircuit: binding, tagged U, for ME, NH, SD and NE (Walker); persuasiveStrong, tagged U, for SC and TN; persuasive elsewhere (E3);
  - states with no intermediate appellate court get `horizontal none` (trial courts).
- **Date-keyed rows:**
  - Michigan horizontal: soft before 1990-11-01, strong after. It is keyed on the precedent's date.
  - Nebraska trialScope has a gap from 1996-02-19 to 2007-09-20 (Metro Renovation to Nelson). No row covers it, because the contract's value set has no "none".
  - unpubForce cutoffs: 5th Cir. 1996; D.C. Cir. 2002; FRAP 32.1 2007; IL 2021; PA 2008/2019; MD 2023; IN 2023; WA 2013; AZ 2015; NV 2016; WI 2009; MA 2008; AR 2009-07-01 (2009 Ark. 330, per curiam of 2009-05-28; S); OH 2002-05-01 (Rep.Op.R. 4, renumbered 3.4 in 2012; L, secondary sources).
- **unpubForce values:** a bare Force applies to publication ∈ {unpublished, table, summaryOrder}. `memorandum:<Force>` applies to publication = memorandum only (TX civil memorandum opinions are binding, the Tax Court's are persuasive, and so on).

## decisions2.tsv (6,892,454 rows; every node once, in node order)

Columns: node, court_id, date, unit, bench, publication, form, text_sha, src.

- **text_sha** is the sha1 of the decision file's bytes at HEAD. It is present for every node.
- **src** is `c:<court route>;u:<unit source>;b:<bench evidence>;p:<publication evidence>;f:<form evidence>`.

**Header region.** The body without front matter, up to max(2,500 characters, end of head matter (at most 4,000) + 1,500), plus the last 1,000 characters (the tail). CAP prints footnotes, "do not publish" and commission notations at the end.

### Field rules

**unit** (`u:`). Only the intermediate-court families above get a unit; everything else is 0. Sources, in order:
1. `name`: from the court name.
2. `docket`: FL `nD…`; TX `NN-YY-…-CR/CV`; CA letter A–H (1980+); IL `n-YY-` (1965+); IN `n-…A…` / `…A0n-`; MO `ED/WD/SD`; WA `-I/-II/-III`; AZ `n CA-`; LA circuit formats.
3. `county`: county or parish of origin. NY counties → departments (judicial-district table); OH counties (full table from 1976, core counties always); LA parishes from 1960 (5th Circuit parishes → 4th before 1982); WA counties; the largest CA counties with district start dates; Cook County → IL 1st.
4. `judges`: the bootstrap described in `courts_validation.md`.

A unit dated before that unit existed is dropped.

**Fifth Circuit units (coordinator convention).** A 5th Circuit decision dated 1980-10-01 to 1982-12-31 whose header names "Unit A" or "Unit B" gets unit 1 (Unit A) or unit 2 (Unit B). There are 822 and 730 such decisions. The `unitB` adoption filter matches unit = 2. The range runs past 1981-09-30 so that Unit B decisions issued after the split, which also bind the 11th Circuit (Stein v. Reynolds), are covered.

**bench**:
- **enBanc:** en banc only from the header region:
  - front-matter `judges` says en banc;
  - a federal circuit "Before" line lists 7 or more judges;
  - a strong caption line ("Argued and Submitted En Banc", "EN BANC", "sitting en banc", "Before the Court en banc", "…Court, En Banc.");
  - strict self-referring prose ("On rehearing en banc", "this case … heard en banc").
  The rule rejects orders granting or denying rehearing en banc, amendment lines, citations and lower tribunals sitting en banc.
- **limitedEnBanc:** en banc in the 9th Circuit on or after 1980.
- **circulated:** "this opinion … circulated to all active judges", 7th Cir. R. 40(e), the Irons footnote. Petitions for rehearing are excluded.
- **conflictPanel:** Michigan MCR 7.215(J) special panels.
- **division:** a "Division/Department N" caption, or an Arkansas/Colorado division in the name.
- **wholeCourt:** SCOTUS and CCPA by rule, otherwise "this case … heard by the whole court".
- **Defaults:** panel for tiers A, B and D; unknown for L, T and S.
- **Re-read of overruling decisions** (`labels_fix2.py`, `b:fix2:<evidence>+was:<old value>`): for the 15,690 decisions that overrule, disapprove or recede (treatments.tsv, hunt/data/p3_panel.tsv), a bench of panel or unknown is re-decided from the whole text. 900 changed.
  - enBanc: the judges lines, the first or last 1,500 characters, or self-referring prose anywhere say en banc / in banc / before the full court; "All the Judges concur" in a state intermediate court; or the judges lines name at least 5 judges in a court that sits in panels of three (federal circuits, FL, TX, OH, PA, KY, NC, D.C.), at least 7 elsewhere. Courts of last resort: only a caption or judges line.
  - circulated (federal circuits): the opinion, not a rehearing petition, was circulated to all active judges or the full court; the Irons footnote; 7th Cir. R. 40(e); "mini en banc"; "approved by the full court". A circulation footnote wins over en banc words in prose.

**publication** (first match wins):
1. "certified for partial publication" → published.
2. 2d Cir. "SUMMARY ORDER" → summaryOrder.
3. A non-publication banner or rule note in the header or tail → unpublished. These include NOT FOR PUBLICATION, DO NOT PUBLISH, NONPRECEDENTIAL, UNPUBLISHED, "this opinion is not designated for publication", 5th Cir. R. 47.5, 9th Cir. R. 36-3, Ill. R. 23, Mass. R. 1:28, …
4. Front matter `precedential_status: nonprecedential` → unpublished.
5. F. App'x citation → unpublished.
6. Table citation, or a short opinion with "Table … / Decision without published opinion" → table.
7. A Florida DCA per curiam with under 300 characters of opinion (a PCA) → table.
8. A Hawaii summary disposition order → unpublished.
9. A memorandum channel in a state appellate court or the Tax Court → memorandum. Not in Oklahoma or Minnesota, whose "MEMORANDUM OPINION"s are full published opinions: there the rule is skipped and the next rules decide (1,648 decisions, now published; `p:<rule>+okmn-memo-heading`).
10. Front matter `published`/`precedential`, a "FOR PUBLICATION"/"PUBLISHED" banner, or an official reporter citation → published.
11. Otherwise unknown.
12. Reporter check (`labels_fix2.py`, `p:reporter2:<reporter>+was:<old value>/<old evidence>`): a decision that rules 2–9 made non-published, but that is cited in a reporter of published opinions, becomes published. 7,342 decisions.
    - Reporters that count: official state reports, the regional reporters, F./F.2d/F.3d/F.4th, F. Supp., F.R.D., B.R., U.S., T.C. and the other federal courts' reports. Not F. App'x, T.C. Memo., N.Y.S., A.D., Misc., Cal. Rptr. alone, Ill. Dec., trial-court reporters, neutral or database citations.
    - Federal courts: always published, unless the row is `table` and its own heading is a table entry.
    - State courts: the old value is kept when the decision says so itself (NOT FOR PUBLICATION, "Not to be published in full", UNPUBLISHED OPINION / MEMORANDUM / Disposition, SUMMARY DISPOSITION ORDER, decision without published opinion, Mo. Rule 84.16(b), Ind. App. R. 65(D), "no precedential value") and no order published it in whole or part; or when it has under 600 characters of opinion text (an entry, not an opinion). A `table` row from a "(table)" citation in the text becomes published at any length.
    - Florida PCAs without opinion (rule 7) are never candidates.

**form** (first match wins):
1. equallyDivided: this court's own affirmance by an equally/evenly divided court, in a short opinion or the opening of the opinion; quorum affirmances (28 U.S.C. § 2109) are excluded.
2. certifiedAnswer: a state court of last resort answering a question certified by a federal court; acceptance-only orders are excluded.
3. plurality: "X announced the judgment … and delivered an opinion" or "opinion announcing the judgment", with no opinion of the Court for any part; or a `## Plurality` section.
4. summaryAffirmance: SCOTUS, under 600 characters of opinion, "judgment affirmed" or "want of a substantial federal question", and not a memorandum order.
5. perCuriam: the section title or the opening says "Per Curiam", or the SCOTUS `decision_type` is per curiam.
6. memorandum: a MEMORANDUM (OPINION/DECISION) heading, T.C. Memo., or the SCOTUS `decision_type` "memorandum order". In Oklahoma and Minnesota the heading does not count when the opinion has at least 600 characters (1,567 decisions are full, `f:len+okmn-memo-heading`).
7. full: at least 600 characters of opinion.
8. memorandum (`f:order-lt1500`): outside SCOTUS, a short dispositive order — under 1,500 characters of opinion text (head matter excluded; in practice every such decision has under 600, or rule 7 applies) with order language: "it is ordered", ORDER/ORDERED, "… affirmed/reversed/dismissed/denied/granted/vacated/remanded/quashed/refused", "writ … denied/refused/granted" (`orders_scan.py`, `ORDER_RX`). SCHEMA has no `order` value, so these are memorandum. 643,590 decisions; 100% (50/50) in review.
9. Otherwise unknown.

The rare classes (plurality, equallyDivided, certifiedAnswer) were re-read from git and re-tested by `refine.py`; failures fall back to perCuriam, full or unknown (`f:refine:…-rejected`).

## commission.tsv (15,567 rows; extra file, not in the contract)

Columns: node, court_id, notation, evidence. These are adoption notations found at the end of decisions:
- Texas Commission of Appeals: "Opinion adopted", "Holding approved", "Judgment adopted";
- Texas Court of Criminal Appeals commissioner opinions: "Opinion approved by the Court";
- Missouri commissioner opinions: "…is adopted as the opinion of the court".

notation is one of opinionAdopted (2,731), opinionApproved (3,327), judgmentAdopted (9), adoptedAsOpinionOfCourt (10) or other (9,490). "other" is mostly the Missouri per curiam adoption formula, whose evidence text was cut short. The `adoption.tsv` filters for Texas key on this file's notation.

## Scripts (tools/caselaw2)

| script | does |
|---|---|
| `prep_inputs.py` | splits `nodes.tsv` per repo |
| `scan.py` | one git pass per repo: sha1 and header signals; no text is written |
| `run_scan.py --detach` | 10 processes, detached with no console window, resumable (skips repos already done); log in `work/courts/logs/scan.log` |
| `courts2_build.py` | courts2.tsv, court_alias.tsv |
| `tables_build.py` | succession.tsv, adoption.tsv, system_rules.tsv |
| `decisions_build.py stage2` / `stage3` | per-repo labels, then the judge bootstrap and the concatenation into decisions2.tsv and commission.tsv |
| `refine.py` | the second look at the rare form classes |
| `report.py` | counts and id checks |
| `orders_scan.py` | reads the opinion text of every decision whose form is still unknown (outside SCOTUS) and marks short orders → `work/courts/orders.tsv` (966,109 decisions in 115 s, 10 processes) |
| `limits_fix.py` | the limit fixes of 2026-11-12 (`courts_validation.md` §5): dated sources, tribal systems, CAAF rows, unmapped courts, OK/MN memorandum, short orders, writ refused; reads the `*.pre_fix.tsv` backups, so it can be rerun |
| `labels_fix2.py scan` / `apply` | label fix 2 (`courts_validation.md` §6). `scan` re-reads from git (8 processes, about 50 s) the 15,364 non-published decisions cited in a reporter of published opinions and the 15,690 overruling decisions → `work/courts/pub2.tsv`, `bench2.tsv`. `apply` rewrites decisions2.tsv (`.tmp`, then rename), keeps the input as `decisions2.pre_pubfix.tsv`, and is idempotent |
| `sample_validate.py`, `precision.py` | validation samples and precision |
| `peek.py`, `show.py` | read headers from git |

Rebuild order: courts2_build → tables_build → decisions_build stage2 → refine → decisions_build stage3 → (reader) → orders_scan → limits_fix → labels_fix2 scan → labels_fix2 apply. After a full rebuild, delete the `*.pre_fix.tsv` backups first so that limits_fix reads the new files.

## Known gaps

- **bench**
  - It is unknown for 3.19M decisions, mostly state courts of last resort, because there is no header cue. They are not assumed to be whole-court.
  - About 1 in 5 enBanc labels is still an order on a rehearing petition rather than a decision of the en banc court.
  - The en banc / circulated re-read (`labels_fix2.py`) covers only the 15,690 decisions that overrule, disapprove or recede. Even there about one in four en banc decisions is still `panel`: three-judge courts where the panel was the whole court, Alabama's appellate courts (always a full court), Louisiana five-judge benches, and decisions with no judges line. A court-size rule would be needed.
  - conflictPanel has only 5 samples (60%).
- **Units**
  - Not recovered for about 38% of the decisions of unit-structured intermediate courts. The weakest are TX (45%), CA (55%), IN (56%) and NY AD (61%), mostly pre-1980 decisions with bare numeric dockets and no judge match.
  - NY Appellate Term, the OK Court of Civil Appeals and Tennessee are almost unrecovered.
  - Re-fetching CAP `head_matter` (which carries the court line) would close most of this gap; that was not attempted here.
  - County tables are the current ones:
    - Ohio: districts 11 and 12 are applied only from 1976.
    - Louisiana: applied from 1960.
    - Florida and Texas: no county tables are used, because their county-to-district maps changed or overlap.
- **Recall is not measured.** The precision figures say nothing about recall. Header-only en banc and plurality detection misses en banc or plurality decisions whose header says nothing. Plurality is especially conservative: 199 decisions.
- **Publication**
  - published relies on CAP's near-constant `precedential_status`. A reported state decision that a later court depublished is still "published": depublication is a same-case event and belongs in history.tsv.
  - Reporter check (`labels_fix2.py`): 8,022 reporter-cited decisions stay non-published because they say so themselves or are entries under 600 characters. A Florida per curiam of under 300 characters that cites an authority is still `table`.
  - The hunt's figure of 77,575 mislabelled decisions was too high: 50,512 are Florida PCAs without opinion and about 11,600 are T.C. Memo. / Summary Opinions, both correctly non-published. 7,342 were wrong and are fixed.
- **Form**
  - SCOTUS memorandum orders (272,740) and short orders elsewhere (643,590) are form = memorandum. 371,105 stubs stay unknown: 48,586 at SCOTUS and 322,519 elsewhere (162,692 of those have no opinion text; the rest have no order language).
- **Doctrine tables**
  - Rows marked U in doctrine.md stay U. The best readings are tagged U and are data, not premises.
  - Still uncertain: the California 1966 effective day; the Oklahoma 1959-03-11 date rests on a statutory history note (L); the end of the Delaware Court of Errors and Appeals in 1897 (day); TRAP 41.3's start (believed 2008-09-01, not confirmed; no row depends on it); the Ohio 2002 rule (secondary sources); the CNMI 2004 end of Ninth Circuit review (1 or 2 May).
- **Military courts** stay tier S; CAAF binds the service Courts of Criminal Appeals through `adoption.tsv`.
- **Tribal courts** are one system per tribe (1000–1022); their tiers are v1's (S), except Navajo (L), so a tribal appellate court does not yet bind its trial courts.
- **Unmapped:** none. The 8 former 3160 decisions: 6 Department of the Interior land-office decisions → 10109 (federal, S); 1 Salina land-office register → 10110 (federal, S); *Ex parte Rhodes* (1816, "Judge's Chambers") → 10111, system 999 (state not identified; U).
- **Web checks (2026-11-12, limit 8):** 19 of 25 searches; results above and in `courts_validation.md` §5. Earlier, 3 of the allowed 10 searches were used. They verified:
  - the Maryland 2022-12-14 renames;
  - Alabama Act No. 987, effective 1969-10-01;
  - D.C. Pub. L. 87-873, approved 1962-10-23 (effective date computed).
- 2026-11-12 coordinator: added system_rules rows for CA reviewGrantedForce (system 5) and D.C. Court of Appeals court-level horizontal strong (court 627), the two data gaps DIFFTEST found.

## Round 2 (agent courts, 2026-11-12): court epochs have a start and an end

This section replaces the "Epochs" bullet under `courts2.tsv` above ("each court's epochs tile 0–99991231"). Script: `tools/caselaw2/epochs_fix.py` (rerunnable; reads `courts2.pre_round2.tsv`). Log: `round2/courts.md`.

**What a bound means.** Both engines read a row as covering date d when epoch_from ≤ d ≤ epoch_to (reference `Engine.epoch`, Lean `epochCovers`). epoch_to = 0 is read as open by both; the file keeps writing 99991231. On a date that no row of a court covers, the court has no epoch:
- a decision of that court dated there has unknown force and changes no status;
- the court is not a destination (a question about it is unknown; split and conflict destinations skip it);
- an adopter does not yet hold the decisions it adopts (the Federal Circuit before 1982-10-01);
- after a split that ended the old court, only the successors hold its decisions, and an adopter's overruling reaches the original line (DEVIATIONS 69, limit a).

**Rules** (G = 366 days; an anchor is a dated creation or end):
1. End anchors: `succession.tsv` rows with old ≠ new. replace, absorb and rename end the old court the day before the date. A split ends it only when the court has decisions and under 5% of them are dated on or after the date (ended: Alabama Court of Appeals, Court of Claims, Dakota Territory; not ended: Fifth and Eighth Circuits, Florida 2d DCA). Plus the script's `KNOWN_END` table and the U.S. circuit courts (abolished 1912-01-01, Judicial Code of 1911 § 289; tag L).
2. Start anchors: `succession.tsv` rows with new = the court (the earliest), plus `KNOWN_START`. A known S/L date goes before a U succession date.
3. Start = min(first decision, anchor). An S or L anchor with no earlier decision is the start. If decisions are dated before the anchor, or the anchor is U, the start is 1 January of the year of the first decision (src `data:first-decision`).
4. End: an S or L anchor is the end. A U anchor is not used: the end is 31 December of the year of the last decision before the anchor, or of the last decision reached from the anchor through gaps of at most G days (src `data:last-decision`).
5. No anchor: start = 1 January of the year of the first decision, only when that year is 25 or more years after the start of the court's system (earliest 1st-percentile decision year among the system's courts with ≥ 100 decisions; 1789 for the federal system); else 0. No end: a court that is thin in the corpus is not ended.
6. Data-derived bounds are year edges and are never tighter than the decisions. Internal boundaries (renames and role changes with the same id) are unchanged. Rows wholly outside the new bounds are dropped (one row: the post-1948 row of the New Jersey Court of Errors and Appeals).
7. Decisions dated after an S/L end. Round 2 gave them cluster rows (src `data:decision-cluster`). Round 3 replaced that: the 839 stray decisions were re-routed to the court that decided them (804, the court column of `decisions2.tsv`: Court of Claims → Claims Court, Hawaii ICA → Supreme Court, US circuit courts → the district court, and others) or kept as dated exception rows (35 decisions, 7 rows, 5 courts). No `data:decision-cluster` row remains; `courts2.tsv` has 3,025 rows. No decision is dated outside its court's rows. Do not re-run `epochs_fix.py` from `courts2.pre_round2.tsv` without `work/round3/epochs/apply.py` after it: it would recreate the cluster rows. Not installed (round 3 trial, dropped in round 4): circuit-parent epochs for the Eleventh Circuit districts before 1981 and the Tenth before 1929 (`round3/epochs.md`).

**Where the source is written.** The row's src gets ` | from:<source>[<tag>]` and ` | to:<source>[<tag>]`. Sources: `succession <old>-><new> <date> <kind>`, `known: …`, `data:first-decision(<date>…)`, `data:last-decision(<date>…)`. Data-derived bounds have tag `-`. The row's own tag column is unchanged (it decides whether the firm run keeps the row).

**Counts** (3,019 → 3,106 rows; 2,991 court ids):

| | before | after |
|---|---|---|
| court ids whose first row starts after 0 | 86 | 2,671 |
| court ids whose last row is closed | 7 | 168 |
| decisions dated outside their court's rows | 0 | 0 |

| bound | source | n |
|---|---|---|
| from | succession, S | 4 |
| from | succession, L | 7 |
| from | known, S (Kentucky Court of Appeals 1976) | 1 |
| from | known, L (NJ Appellate Division and Chancery Division 1948, Court of Appeals of Virginia 1985, Commerce Court, Emergency Court of Appeals) | 4 |
| from | data:first-decision | 2,576 |
| to | succession, S | 4 |
| to | succession, L | 10 |
| to | known, L (133 U.S. circuit courts, Commerce Court, old NJ Supreme Court) | 135 |
| to | data:last-decision (U anchors) | 17 |
| cluster rows | data:decision-cluster | 88 rows, 47 courts, 839 decisions |

**The examples of DIFFTEST §8.5.**
- Federal Circuit from 1982-10-01 (S: *South Corp. v. United States*, 690 F.2d 1368, 1369, read in the corpus).
- Eleventh Circuit from 1981-10-01 (S). Tenth Circuit from 1929-02-28 (L).
- Alabama Court of Appeals 1911-01-01 to 1969-09-30 (S), with 6 cluster rows for 21 decisions dated 1978–2003. Court of Civil Appeals from 1969-10-01 (S). Court of Criminal Appeals from 1969-01-01 (data: one decision is dated 1969-08-19).
- CCPA to 1982-09-30 (S). Court of Claims to 1982-09-30 (S), with 4 cluster rows for 486 decisions dated 1982-10-07 to 1992-04-28 (Claims Court decisions under the old name).
- Kentucky: old Court of Appeals to 1975-12-31; Supreme Court and new Court of Appeals from 1976-01-01 (S).
- New Jersey: Court of Errors and Appeals and old Supreme Court to 1948-09-14; the new courts from 1948-09-15 (L).
- D.C. Court of Appeals (627) from 1942-01-01 (data).

**Limits.**
- A start can be too early where decisions are misdated or the id also covers an earlier court. 17 courts have decisions before their succession date, e.g. New York Appellate Division (1714), New York Court of Appeals (1800), Supreme Court of Hawaii (1847). This has no effect on the successor logic.
- Cluster rows keep a dead court alive on the dates of its stray decisions (Alabama Court of Appeals on 1978-10-03, 1983-04-27, 1986-03-26, 1994-06-17 to 1995-01-13, 1999-04-16 to 07-16 and 2003-06-13 to 12-12). The real fix is the court id of those 839 decisions (`court_alias.tsv` and `decisions2.tsv`). It was not done in round 2, because `decisions2.tsv` was being rewritten by another agent.
- `court_alias.tsv` is unchanged.
- `succession.tsv`: two rows L → S (655 → 520 and 654 → 520, *South Corp.*); row 1 → 3 (Alabama Court of Appeals → Court of Criminal Appeals) is now kind `rename`, not `split`: by Act No. 987 the old court continued as the Court of Criminal Appeals (the row's own src; Lean agent's note). `adoption.tsv`: one row L → S (520 ← 655).

## Round 2 (agent courts): the three dates of DEVIATIONS 71

Script: `tools/caselaw2/rule_dates_fix.py` (rerunnable: it replaces the `horizontal` rows of systems 35 and 18 whatever their state). 4 of 8 web searches used; the decisive sources were read in the corpus.

| item | was | now | tag | source |
|---|---|---|---|---|
| Ohio, within-district rule starts | 2010-07-01, L | **2008-10-02** | S | *McFadden v. Cleveland State Univ.*, 120 Ohio St.3d 54, 2008-Ohio-4914 (decided 2008-10-02), ¶¶ 15, 19–21: decisions of a court of appeals are precedent until formally overruled; judges who find an intradistrict conflict "must convene en banc"; no rule is needed. *In re J.J.*, 2006-Ohio-5484, syllabus ¶ 2, said so earlier for a district with a local rule. App.R. 26(A)(2), in force 2010-07-01, is the procedure (Staff Note: "designed to address" *McFadden*) |
| Ohio before | soft to 2010-06-30, S | soft to 2008-10-01 | S | *State v. George*, 362 N.E.2d 1223, 1231 (Ohio App. 1975); a Tenth District panel "specifically overruled" an earlier panel in 2007 (*McFadden*, 2007-Ohio-939) |
| Louisiana, within-circuit rule starts | 1997-01-01, S | 1997-01-01 (kept) | **U** | No source gives 1997: *Orillion* (La. App. 1 Cir. 1997-02-14) says only that sister circuits do not bind. The rule is judge-made and has no enactment date. Within-circuit statements found: *Shewmake v. Alejaudro*, 466 So.2d 711 (La. App. 4 Cir. 1985-03-12); *State v. Wolfe*, 630 So.2d 872 (4 Cir. 1993); *Graves v. Businelle Towing*, 673 So.2d 311, 315 (1 Cir. 1996). 2d, 3d and 5th Circuits not shown; no internal rule requiring en banc found. A start of 1985-03-12 was tried on a private copy and lost 15 status rows (en banc overrulings whose unit does not match the precedent's, because units are not fully recovered), so the date was not moved |
| Federal en banc date (`enBancStatuteDate`, a constant in both engines) | 1948-09-01, L | unchanged | S | Act of June 25, 1948, ch. 646 (28 U.S.C. § 46(c)); "September 1, 1948, the effective date of the present Judicial Code" (*Ex parte Collett*, 337 U.S. 55 (1949)); § 46(c) "is but a legislative ratification of *Textile Mills*" (*Western Pacific R. Corp. v. Western Pacific R. Co.*, 345 U.S. 247 (1953)) |

**What the federal constant means.** From *Textile Mills* (314 U.S. 326, decided 1941-12-08) a court of appeals had the power to sit en banc, but only where it had provided for it by rule (the Third Circuit's Rule 4(1); the Ninth Circuit had held it could not, *Lang's Estate v. Commissioner*, 97 F.2d 867 (1938)). From 1948-09-01 every circuit has an en banc court by statute. The constant is that date: the first day on which a panel of any circuit had an en banc court to go to. It is a floor for the finding `panelDepartsWithoutEnBanc`, not the start of the law-of-the-circuit rule in each circuit.

**Caveats.** Ohio: the date is confirmed; the value `withinUnitOnly` is the hunt's reading. *McFadden* leaves the court discretion to decide whether a conflict exists, and App.R. 26(A)(2)(a) says the en banc court "may order" en banc consideration. Louisiana: the row is now U, so the firm run has no Louisiana `horizontal` row.

## Bench by court size (agent enbanc, round 2, 2026-11-12)

Script: `tools/caselaw2/bench_size_fix.py` (`scan1`, `table`, `decide`, `install-table`, `apply`). Validation: `courts_validation.md` §8.

### court_size.tsv (23,399 rows; extra file, not in the contract)

Columns: court_id, from, to, judges, src, tag. The number of regular sitting judges of a court between two dates (yyyymmdd, inclusive).

- **court_id** is the unit row of `courts2.tsv` (id ≥ 10000) where the court has units, else the court id. Tiers L and A only; not SCOTUS.
- **Coverage:** 218 courts, 17,474 court-years with sampled judges. Tags: U 22,485, S 818, L 96.
- **Source.** A sample of up to 60 decisions per court, unit and year, evenly spaced by date (939,751 decisions with the overruling decisions; re-read from git, 16 processes, 3 minutes; `work/courts/bench3.tsv`). Judges come from the front-matter `judges` lines, else a "Before" line in the head, else a concurrence line in the last 1,500 characters, plus the authors in the section titles.
- **Regular judge of a year:** named, not as visiting and not as out, in at least max(2, 30% of the third most frequent judge's count) sampled decisions; or named once in a year next to one in which he is regular. Visiting: senior, district, special, pro tem, retired, by designation or assignment. Out: not participating, recused, took no part, absent.
- **Size at a date:** the number of regular judges whose span of appearances covers the date. Spans join over gaps of up to 400 days and are widened by 30 days. Near the start or end of the court's data (365 days) a judge is taken to sit to that edge.
- **src:** `data:regular=<n>,n=<sampled decisions in the range>,full=<0|1>`. `full=1` marks a year in which at least 60% of the sampled decisions with 2 or more names show every regular judge: the court sits as a full court.
- **Federal courts of appeals:** judges is the authorised number of judgeships from memory (`mem:authorised=`), with the data median and range beside it. Tag S where the data size equals it on at least half the days of the range, L where not.
- **State courts of last resort:** tag S where the data size equals the remembered present size for a range after 1990, else U. All other rows are U (data only).

### Rule (`b:size:<sitting>[+<k>out]/<size>[+u<unit>]+was:<old value>/<old evidence>`)

- Only rows with bench panel or unknown, tiers L and A, never SCOTUS. circulated, limitedEnBanc, conflictPanel, division and enBanc rows are not touched.
- sitting = the decision's names that are regular judges of the court at the date, not visiting, not out. out = regular judges the line names as not participating.
- Whole court: sitting ≥ 2, sitting > size / 2, sitting + out ≥ size, and the year's sample has at least 5 decisions naming 2 or more regular judges.
- Value: wholeCourt for tier L, for size ≤ 3 and for a `full` year; enBanc for another intermediate court. An order on a rehearing petition is not relabelled enBanc.
- A decision with fewer than 2 names (no line, or only the author) is never relabelled.
- A decision without unit in a court that has units at that date is matched to the one unit whose regular judges include at least 2 of its names; otherwise it is left.
- Left out: Arizona, Washington, the Oklahoma Court of Civil Appeals, Indiana and Tennessee. Their units are divisions of one court, so a division's judges are not the whole court.
- **Scope:** the 19,478 decisions of tiers L and A that overrule, disapprove, recede from or decline to follow (by-nodes of `treatments.tsv`, citing decisions of `hunt/data/p3_panel.tsv`). The bulk pass over small or always-full intermediate courts (`scan3`) is written but was not run.
- **Result:** 3,817 changed: panel → wholeCourt 172, panel → enBanc 40, unknown → wholeCourt 3,605. The input is kept as `decisions2.pre_round2.tsv`. `apply` is idempotent.

Values after the fix: panel 3,292,250 · unknown 3,182,649 · wholeCourt 403,778 · enBanc 11,324 · limitedEnBanc 815 · division 1,334 · circulated 204 · conflictPanel 100.

Rebuild order: … labels_fix2 apply → bench_size_fix scan1 → table → decide → install-table → apply.

### Known gaps: bench by size

- Decisions with no judges line stay as they were (most pre-1950 opinions name only the author). This is the largest remaining group.
- A Louisiana five-judge panel of a larger circuit is a panel under this rule.
- OCR variants of a name (DUFFY / DUEEY) count as separate judges and raise the size; a retired judge who still sits without a title does the same. Both make the rule miss, not mislabel.
- Federal sizes are authorised judgeships from memory; a vacancy makes the rule miss (Tenth Circuit 1968, six of seven).
- bench is still unknown for 3.18M decisions: only overruling decisions were read.
