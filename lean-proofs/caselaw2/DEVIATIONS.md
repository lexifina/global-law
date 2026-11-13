# caselaw-lean-2: where the Lean departs from doctrine.md (DESIGN D6)

Every place the Lean rules (lean-proofs `LegalProofs/CaseLaw2/`) differ from `research/doctrine.md`: simplifications,
fallbacks for unknown data, and states the model does not represent.

Each fallback for unknown data is a named `RuleId.assume*` label, so it appears in the justification path of every
verdict that used it. None of them is silent (D5). Doctrine tables enter only as `Rules` parameters. Every theorem
quantifies over all `Rules`, so U rows are never premises (D2).

## Fallbacks for unknown data (each recorded in the path)

| Label | When | Fallback | Why this direction |
|---|---|---|---|
| `assumeHomeDomain` | holding's domain unknown (incl. the anonymous issue ⊤) | the source court's home domain: federal → `federalGeneral`, state → `stateLaw sys` (§8.2) | the only way to run before issue extraction |
| `assumePublished` | publication unknown | published | an unknown channel is usually the official reporter |
| `assumeFullForm` | form unknown | full opinion | |
| `assumeUnpubPersuasive` | unpublished, no `unpubForce` row | persuasive | FRAP 32.1 default |
| `assumeHorizontalSoft` | no `horizontal` row, *force* | soft (`persuasiveStrong`) | does not claim a binding force the tables don't give |
| `assumeStrongForPower` | no `horizontal` row, *power* | strong (en banc needed) | does not admit an overruling the tables don't support |
| `assumeStatewide` | no `trialScope` row | statewide | the majority rule (§4.3) |
| `assumePanel` | bench unknown, *power* | panel | conservative |
| `assumeRetroactive` | treatment temporal `unknown` | retroactive (*Harper*) | TM2 default for federal law |

`horizontal` uses one fallback for force and the opposite one for power. Both are the conservative direction for what
they decide.

## Simplifications

1. **Case kind.** Civil vs criminal is not modelled (no column).
   - The dual courts of last resort (TX, OK, H2) each bind every lower court of their system.
   - Two different last-resort courts of one system never bind each other (`H2dual`).
2. **Swift era (E1).** Before 25 Apr 1938, federal decisions on state law are `persuasive` in federal courts. The
   *Swift* "local law" exception (binding) is not modelled, since local and general law cannot be told apart.
3. **E1 *West v. AT&T*.** Intermediate state decisions are `persuasiveStrong` in federal courts; state trial
   decisions are `persuasive` (*King*).
4. **Erie predictions.** A federal panel's departure from a circuit *Erie* prediction after a new state-high-court
   decision is not specially licensed. Power follows the circuit's horizontal rule.
5. **Marks (F6).** A plurality holding with no `marks.tsv` row is `persuasive`. The doctrine's separate grade
   `resultOnly` (binding on the result only) is folded into `persuasive`.
6. **Summary affirmances (F2)** are `binding`, without the narrow-issue scope.
7. **Equally divided (F5)** → `none`. **Memorandum** → `persuasive`.
   - **Data (2026-11-12, limit 13):** form `memorandum` now also covers 643,590 short dispositive orders outside
     SCOTUS (order language in under 1,500 characters of opinion text; SCHEMA has no `order` value), so they are
     `persuasive` rather than `assumeFullForm`. Oklahoma and Minnesota "MEMORANDUM OPINION"s are full published
     opinions and are no longer `memorandum` (limit 10).
   - Not modelled: Georgia "physical precedent" (concurrence-count test), WV memorandum weight, and Tax Court
     memorandum vs division opinions (except through `form = memorandum`).
8. **Commission opinions (H4)** are not distinguished (no column).
9. **Golsen (F12).** Handled only through the optional `decisions2_extra.tsv` `appeal_venue` (the bound decision's
   circuit). Without it, the Tax Court is a national special court.
10. **BAP** decisions are `persuasive` everywhere (F13, contested). A special court's own precedent is
    `persuasiveStrong` (F12 stare decisis).
11. **Unit B (F10).** The `unitB` adoption filter matches decisions whose `unit` is 2; the courts table must mark
    Unit B decisions that way.
12. **Adoption across systems** (*M.A.P. v. Ryan*, D.C.) is allowed. This is why the *Erie* theorem is stated
    "absent adoption"; `Examples.lean` shows the adoption case.
13. **SCOTUS** is not bound by itself (`H1self`, `persuasiveStrong`), like every court of last resort. `H1self`
    needs the two courts to be in the same system.
14. **AEDPA** (only SCOTUS holdings count on federal habeas) is not modelled.
15. **Abrogation by intervening higher authority (F14)** changes status only when a court states it in an admitted,
    explicit treatment row.
    - An inferred abrogation (`explicit = 0`) feeds `atRisk` only.
    - The split resolver ranks a SCOTUS holding first, but does not derive implicit abrogations of the lower holdings.
16. **Revival (T3).** An overruling lapses when the overruling decision is vacated, withdrawn, substituted, or
    reversed on every issue.
    - Overruling the overruler does not revive automatically, because the later court may adopt a third rule.
17. **Vacated** opinions have no force. The [U] view that some courts cite them as persuasive is not modelled.
18. **Withdrawal** takes effect from its date, not *ab initio* (TM3).
19. **California review granted (S-CA).** This is the approved `reviewGrantedForce` system rule.
    - Its force is ≤ `notCitable` → status `depublished`; otherwise status `reviewPending` (a `persuasive` cap).
    - The effect lasts until review is dismissed or the case is decided (affirmed, reversed, modified).
    - Not modelled: the 2021 "transfer with directions to vacate" and the 2021 administrative order. No row → a
      grant has no effect (as with cert. granted elsewhere).
20. **En banc grant (F8).** If no `enBancGrantVacatesPanel` row covers the court, the panel opinion's status is
    `unknown:enBancRuleUnknown`, not good law.
21. **Texas writ/pet. refused (S-TX-3)** promotes the opinion to last-resort tier for force. Not distinguished:
    "writ ref'd n.r.e.", which the data must not label `writRefused`. **Data (2026-11-12, limit 9):** `history.tsv`
    labels `writRefused` only for the Texas Supreme Court's "writ refused" / "writ ref'd" (1 row); "n.r.e.", "writ
    denied" and "writ dismissed" are never `writRefused`. The 2,287 former rows were the Louisiana Supreme Court's
    "Writ refused." on court-of-appeal judgments (a refusal to review); they are now kind `other` (src
    `relabel:other(...)`), which cannot be certified (item 52) and changes no status.
22. **"On other grounds" and unknown scope.** `otherGrounds`, `partialUnknown` and history scope `unknown` all reach
    "some issue". For a named holding, and for the anonymous issue ⊤, that is `unknown:partialScope`, not negative.
23. **Power over same-case history (`histPower`).** The deciding court is the same court (any bench: withdrawal,
    substitution, rehearing), its successor, a higher court of the system, or SCOTUS. If the deciding court is
    unknown, the row is admitted as `okUnverifiedBy`.
24. **Federal circuits** change the status only of decisions of their own circuit (v1).
25. **Certificates.**
    - The target check is the *presence* of the citation (spacing and case ignored) or of every name token (≥ 3
      characters) in the quote or window. Since the five-limits pass, a `cite:` evidence must also resolve through
      the citation index to the row's target when `cite_index.tsv` is supplied (item 64).
    - Window hashes are re-checked in Lean when `window_sha.tsv` is supplied (item 65).
    - Cue and disqualifier phrases are fixed lists in `Certificate.lean`.
26. **Holdings' certificates** are checked for hash and quote-at-offset only. The role column stands in for the part.
27. **Findings.**
    - `appliesSupersededHolding` in the citation pass uses the citing date as the conduct date (an upper bound on the
      real conduct date).
    - `citesUnpublishedAsBinding` needs an admitted `followed` treatment, since a bare citation does not say how it
      was used.
    - `citesOverruled` no longer needs the negating decision to bind the citing court: v1's condition was dropped in
      D4 triage, since status is not relative to the citing court (§5.1B, T1). See item 53.
28. **Splits.**
    - Examined at the `asOf` date.
    - `split` rows follow DESIGN layer 5 (D4 triage): two holdings on the question with opposite answers, both good
      law on `asOf`, by courts (court, unit) neither of which binds the other (force known and below
      `bindingAbsentConflict` both ways), with no good-law holding of a non-trial court binding both. This test is in
      the runner glue; the Spec's resolver-based `split` and `scotus_resolves_split` now back only `conflict` rows.
    - `conflict` rows: the bound courts are every (court, unit) that holds on the issue, plus one trial court per
      system/circuit involved. Opposite permissible answers within one bound court are a `conflict`.
29. **Horty consistency** is checked only where `factors.tsv` gives reasons. The checked base is the candidates with
    force `binding` after resolution.

## Readings chosen in differential testing (D4, 2026-11-12; DIFFTEST.md)

Each item below is a place where the Lean and the Python reference differed and both now follow the reading given
here. (c) marks a choice where doctrine.md leaves the answer open; (a) marks a Lean correction against doctrine, listed
because it changes what the Lean computes. The reference records the same list in REF_NOTES.md (R-numbers in
brackets).

30. **Supersession by enactment, issue `-`** (a). A `supersessions.tsv` row with issue `-` reaches the target's
    admitted holdings whose issue cites the amended block: `issues.usc` equal to the law change's `usc_block`, or one
    a subsection of the other. With none, it reaches some issue, unknown which (`someIssue`). `SEvent` now carries a
    `Scope` (§7 AB1: issue-limited).
31. **`retroactive_to = 1`** (SCHEMA, 2026-11-12). The law governs cases pending on its effective date, whatever the
    conduct date. Pending-ness is not in the data, so this is **approximated** as: the supersession is known from the
    effective date (question date t >= effective) and reaches all conduct. A case decided after the effective date that
    was not pending on it is over-reached. [R30]
32. **Supersession evidence** (a). A row whose evidence is `laterCourtSays:<tid>` is admitted only when that treatment
    row's text certificate passes. (c) A `supersededByEnactment` *treatment* alone changes no status: without the law
    change there is no effective date, retroactivity or amended block (AB1). [R27]
33. **Inferred rows** (§9.26). An `explicit = 0` treatment or supersession never changes status; it is atRisk only.
    [R26]
34. **Power with an unknown issue domain** (a, D5). Power is decided per issue reached: a named holding on its own
    domain; ⊤, or an issue of unknown domain, on every domain it could have (each court's home domain, federal law,
    patent law when the Federal Circuit is involved). Disagreeing domains, or an unknown court epoch, admit the row
    unverified with the effect `unknown powerUnknown` (a new `Unk` reason; `TEvent.powerKnown`). A `someIssue`
    treatment is narrowed to the holdings the court has power over (`Scope.someOf`).
35. **Fallbacks for unknown attributes** (c). An unknown publication is read as published, an unknown form as a full
    opinion, a missing `trialScope` row as statewide, a missing `horizontal` row as soft for force and strong for power,
    an unknown bench as a panel, a missing circulation row as not en banc, and an unknown (0) unit as not the own unit
    (for an appellate division over a trial court: no power). These are the Lean's existing `assume*` labels; the
    reference adopted them in place of enumerating the values. [R1, R31]
36. **Partial reach on ⊤** (c). Any event, negative or unknown, that reaches only part of a decision makes ⊤ `unknown
    partialScope` (§8.2 "partiallyNegative"). An unknown whole-decision event ranks above it. [R32]
37. **Revival** (c). An overruling lapses while the overruling decision is withdrawn, substituted, vacated (also by an
    en banc grant that vacates under the court's rule), depublished, or reversed, each over the whole decision. It
    revives if that decision is reinstated (§5.1A). A partial event, review granted, an unknown en banc rule, or the
    overruler being overruled leaves the overruling standing: revival is not automatic (T3). [R15]
38. **Reinstatement** (a). `reinstated` also ends a depublication and a pending review (§5.1A "restores status").
39. **Same-case power** (a). A history row is decided by the target's own court, a successor, a higher court of its
    system that reviews it (federal: its own circuit, or the Federal Circuit), or SCOTUS. The Court of Federal Claims
    reviews no one. [R25]
40. **Trial courts** (a, F13). A trial court or appellate division has no power over its own decisions.
41. **Adoption** (a). An adopter may change the status of an adopted decision only from at least the decision's dated
    tier (Kentucky 1976), and then under its own horizontal rule (*Bonner*). An adopted decision belongs to no unit of
    the adopter.
42. **Federal Circuit** (a, F11(b)). It has power over district courts on patent issues. From 1 Oct 1982 a regional
    circuit's patent law no longer binds its district courts.
43. **Plurality decisions** (c, HD6). A majority or per curiam holding of a plurality decision binds. An equally
    divided decision caps at none, whatever role the reader gave the holding.
44. **Another state's law** (c). A state court's ruling on a third system's law binds the system's own lower courts
    (vertical stare decisis), as on federal law.
45. **SCOTUS on state law** (F1, "on federal questions only"): persuasive everywhere. The Lean already did this; the
    reference was corrected. [R10]
46. **Pre-*Erie*** (c, DEVIATIONS 2). Federal decisions on state law before 25 Apr 1938 are persuasive in federal
    courts, the deciding circuit included. State high courts are persuasive in federal courts before *Erie*.
47. **E3 `stateFollowsCircuit`** (a). Applies only to the court of appeals of the circuit the state lies in (28 U.S.C.
    § 41). The runner gives each state system its circuit from its courts' names (majority vote).
48. **Temporal scope unknown** (c, TM2). Retroactive, for state law too: retroactivity is the general rule, and a
    prospective overruling must say so. [R14]
49. **California review granted** (c, S-CA). Read only from the approved `reviewGrantedForce` rule. **Data note:**
    `data/system_rules.tsv` has no such row yet, so S-CA review grants have no effect on the real data. [R16]
50. **Court of last resort and the system `horizontal` row** (c). A system-level row describes the intermediate
    courts; a court of last resort is bound by its own precedent only through a court-level row. **Data note:** the
    D.C. Court of Appeals' divisional rule (*M.A.P. v. Ryan*) needs a court-level row. [R23]
51. **Holdings** (a). Admitted only through their own certificate (hash, quote at offset, role).
52. **History certificates** (c). A quote from the target's own text needs no target evidence
    (`Cert.Input.selfText`). History kind `other` has no cue and cannot be certified. [R21, R28]
53. **Findings** (a/c).
    - Citation findings are not made when every live effect behind the cited status is the citing decision's own.
    - Per-holding findings only when the citing decision holds on that issue, or holds on nothing and every holding of
      the cited decision is negative (HD4), and only when the whole decision is not already negative.
    - `reversed` is a `citesVacated` (§5.1A). [R29]
    - Treatment findings read only rows whose text certificate passed (and, in the reference, that are not earlier
      than their target).
    - `panelDepartsWithoutEnBanc`: status-changing kinds only, any bench short of en banc, only from good law.
    - `pluralityTreatedAsBinding`: a plurality decision with no Marks row that would bind the citing court as a
      majority opinion on every domain its issue could have.
    - `citesUnpublishedAsBinding`: below `bindingAbsentConflict` on every domain the issue could have, ignoring the
      cited decision's status (which has findings of its own).
    - `atRisk inferredRejection`: power not shown absent, and the target not already wholly negative.
    - `firm` (D2) is the same verdict with the S/L tables: the D5 class and the negative kind, not the unknown reason.
54. **Texas writ/pet. refused** (a, S-TX-3). The notation promotes only a state intermediate court's opinion. On any
    other court it is a data error and changes nothing (it had demoted a circuit's binding force on its own district
    courts). [R24] Narrowed by item 62.
55. **Certificate target evidence** (D4 real data). The target may be named in the quote or in any well-formed window
    covering it. Citations compare as lowercase letters and digits (SCHEMA's normalised `cite:`); names compare as
    whole words of at least 3 characters. Only well-formed windows (text length = end0 − start0) are used.
56. **Cues and disqualifiers.** One cue table (`Cert.cues`, widened for "declines/refuse to follow", "reject",
    "certiorari granted"). Disqualifiers are phrases only (procedural rulings, reported history, refusals to
    overrule). A mention of a dissent is not a dissent's words; the `part` column decides that.
57. **Firm.** Only `U`-tagged rows are infirm; untagged (`-`) v1 rows are data and firm.
58. **BAP** (F13). A BAP changes no status. Same-case history: a BAP reviews its circuit's bankruptcy courts; in the
    federal system otherwise only a court of appeals reviews.
59. **Holdings windows** are read from `holdings_cert_text.tsv` as well as `cert_text.tsv`.
60. **Open (c):** a court whose tier changed (the D.C. Court of Appeals, intermediate to 1971, then last resort) acting
    on its own pre-change decisions. The Lean treats the later bench as a higher court; the reference treats it as
    the same court under its horizontal rule. 40 real residual rows; DIFFTEST.md §5.

## Five limits (2026-11-12, second D4 pass; DIFFTEST.md §7)

61. **Firm, by any route** (c, DIFFTEST seed 30984). A citation finding is firm when the S/L-only tables make the same
    finding (the same kind on the same status) by any route: the whole decision, or holding by holding. Before, the
    whole-decision row's firm flag read only the whole-decision status. This is the reference's reading; the
    regression fixture is `fixtures/regress/gen120-30984`. `atRisk citesLaterNegated` had `firm = 1` hard-coded; it
    is now computed.
62. **Texas writ and petition notations** (a, S-TX-3, F3). A `writRefused` row promotes the target only when:
    - the target is a Texas intermediate decision (the system is found from court names, as for E3);
    - the wording is "writ ref'd"/"writ refused" dated before 1 Sept 1997, or "pet. ref'd"/"petition refused" from
      then on, and never "n.r.e.";
    - the case is civil: a known refusing decision must be the civil court of last resort's; when it is unknown, only
      a writ-era notation counts (the writ of error was civil only; a petition-era "pet. ref'd" may be a criminal PDR
      refusal).
    It is read from the certified quote in the runner (`Run.writPromotes`, `HEvent.promotes`). The 2,142 Louisiana
    "Writ refused." rows of snap4 no longer promote anything (the data agent has since relabelled them `other`).
    [REF L5]
63. **Commission opinions** (H4, §3.2 TX). `commission.tsv` (optional) gives each decision its notation, and the
    `adoption.tsv` filters for the Texas Commission of Appeals are now read:
    - `opinionAdopted` takes "Opinion adopted", "Opinion approved" and "adopted as the opinion of the court";
      `holdingApproved` and `judgmentAdopted` take their notations;
    - `none` takes a decision with no notation row, one whose wording the data could not classify (`other`), and every
      decision when `commission.tsv` is absent: an adoption that is not shown is no adoption (c);
    - `resultOnly` is read as persuasive (the force scale has no result-only grade, and every compared output cuts at
      bindingAbsentConflict);
    - a "Judgment adopted" notation on any court's decision (a commissioner opinion of the CCA or of Missouri) caps it
      at persuasive. The runner glue reads it as a memorandum form, because the locked `scotus_binds_federal` fixes the
      caps inside `force`;
    - an adopted decision ranks in the resolver as its adopter's (the Supreme Court of Texas: 3).
    **Not modelled:** power over an adopted commission opinion is still judged on the commission's own (special) tier.
64. **Citation index** (SCHEMA addition: optional `cite_index.tsv`, normalised citation → node, derived from
    `graph/cite_index.tsv` restricted to the cited evidence by `tools/caselaw2/cite_index_build.py`). When it is
    supplied, a `cite:` evidence passes only if the citation occurs in the quote or a usable window **and** the index
    maps its compact form to the row's target (`checkCert_cite_index`). A compact key that two nodes share is left
    out: it is ambiguous and resolves to nothing (the real index has none). History rows whose quote is the target's
    own text still need no evidence. Name evidence keeps its rule.
65. **Window hashes** (SCHEMA addition: optional `window_sha.tsv` with text_sha, start0, end0, sha1, src; written by
    `tools/caselaw2/window_sha.py` from the corpus text at git HEAD, after checking each file's SHA-1 against
    `text_sha`). When it is supplied, a window is usable only if its key has a recorded digest and the checker's own
    SHA-1 of the window text equals it; otherwise the row fails with `windowHash` (`checkCert_window_hash`). The
    SHA-1 is pure Lean (`Sha1.hex`, with `#guard` vectors from `hashlib`). Each window's digest is computed once per
    run, as a `Thunk` pinned to `Sha1.hex text` by `Window.digest_eq`.
66. **New finding kinds on both sides** (c). Readings settled in D4:
    - `ignoresBindingInUnit` (§9 item 27): a trial-level state court with no power over the precedent declines to
      follow, or claims to overrule, a good-law precedent that binds it through its own unit (`VownUnit`,
      `appDivBinds`) on every domain the issue could have. The Lean's earlier, wider reading (also `hWithinUnit` and
      `hStrong`, which are panel departures) is dropped; those cases are `panelDepartsWithoutEnBanc`. A decision
      promoted by a writ or petition notation binds as the court of last resort's, not through the unit rule.
    - `atRisk citesLaterNegated`: the cited decision is wholly negative on asOf but not on the citing date, and a live
      negative effect comes from a decision whose court binds the citing court on that decision's date, on every
      domain. Supersessions, unknown deciding decisions and the citing decision itself do not count.
    - `atRisk soft` (limited, questioned, criticized, declinedToFollow) and `atRisk claim` (a status-changing kind by
      a court shown to lack power, T2): only for rows whose target is not later than the treating decision (T1), and
      not already wholly negative.
    - `atRisk contraryBinding` (F14): the earliest later contrary holding of a non-trial court that binds the
      holder's court on its date, on the issue's domain or on every domain an unknown one could have. The search stops
      when the holder is no longer good law.
67. **Conflict resolution** (c, §1.2 F7, §4.1 V). For `conflict` rows the runner prepares the candidates before the
    Spec's `resolve`:
    - a candidate whose deciding court another candidate binds, without binding it back, is displaced; a decision
      held by binding adoption is displaced only by one that also binds its adopter;
    - first-in-time is the rule of the source court whose panels conflict, not of the bound court;
    - the trial-scope rule is the intermediate court's (a court-level `trialScope` row overrides the system row) and
      is already in the candidates' force, so `resolve`'s own-unit step is not used;
    - a good-law holding whose force is unknown leaves the bound court undecided (no row, D5);
    - only holdings dated by asOf, and plurality holdings with a Marks row, count (the split filter); the firm run
      reads only S/L Marks rows;
    - answers are written as a set.

## Hunt fixes and the WSL verification run (2026-11-12, evening; HUNT.md "What to fix", DIFFTEST.md §8)

68. **Divisions of a court of last resort** (H6, §3.2/§4 DC; *M.A.P. v. Ryan*, 285 A.2d 310 (D.C. 1971)). A court of
    last resort with a court-level `horizontal` row (`system = -court_id`) is read as sitting in divisions. A
    division is bound by the court's own decisions as that row says (`divisionRelation`, `forceDiv`), and only an
    en banc–equivalent bench overrules them (`lastResortBench`). The court itself, en banc, is still not bound
    (`relation`'s H1self), so `nothing_binds_last_resort` holds as locked: it speaks of the court, not of a division.
    Every force the runner computes is for the court as it ordinarily sits (`forceDiv`); `forceDiv_eq_force` proves
    this changes nothing for any court that is not a court of last resort. A system-level row does not make a court
    of last resort a divisional court. Decisions of the court's earlier, intermediate era fall to the higher-court
    rule (any bench), on both sides.
69. **Status after an adoption cut-off is per heir** (H4, F10; `Reach`, `reachOf`, `inLine`, `statusFor`). Heirs are
    binding adoptions with filter `all` or `unitB`; persuasive adoptions and notation filters make none. A
    status-changing treatment reaches: every line if it is SCOTUS's; the original line if it is by the decision's own
    court, a court that replaced it (a succession other than a split), a higher court of its system, or an adopter
    once the original court has no epoch; an heir if the treating court is that heir, or stands above it, or the
    original line overruled on or before the heir's cut-off. A citing court is in an heir's line when it is the heir
    or a court below it (same system, lower tier; under a federal court of appeals, its circuit). Limits: (a) court
    epochs in `courts2.tsv` rarely end, so "the original court is gone" almost never fires: after a split that
    ended the old court (Alabama 1969), a successor's overruling reaches only its own line; (b) per-heir status is
    applied to the citation findings (`cites*`, `citesLaterNegated`, `supersededConductUnknown`) only. `status.tsv`,
    the treatment-level families, splits, conflicts and Horty bases still read the union status (negative if negative
    in any line).
70. **Superseded holdings need a conduct date and a holding-level match** (H2, §7 AB1). SCHEMA carries no conduct
    date for a citing decision, and its own date is not one. `appliesSupersededHolding` therefore needs
    `statusAtConduct = some …` and is never emitted from the present data. The low-confidence family
    `atRisk supersededConductUnknown:<issue>` is emitted instead when (a) the cited holding is superseded for the
    latest conduct the citing decision could concern (its own date), and (b) the citing decision has a holding on the
    same issue, or on an issue whose US Code block is the block the superseding law rewrote. The old fallback (a
    citing decision with no holdings citing a decision all of whose holdings are negative) does not apply to it.
71. **Panel departures** (H3b, F7). `panelDepartsWithoutEnBanc` needs a bench known to be a panel or a division (an
    unknown bench and an opinion circulated to the full court make no finding, whatever the circulation rule), and
    a strong or within-unit rule covering both the precedent's date and the treating date. A missing row makes no
    finding. A federal court of appeals makes none before 1 September 1948 (`enBancStatuteDate`, 28 U.S.C. § 46(c);
    tag L). Power is unchanged (a missing row still needs an en banc bench, R31), so status is unchanged.
    `horizontal` rows stay keyed by the precedent's date: dating a rule's start also ends the binding force of older
    decisions on the court's own panels, which is why the federal date is a constant and not a row date. Ohio
    (soft before 1 July 2010) and Louisiana (within-circuit from 1997) are dated in `system_rules.tsv`
    (`tools/caselaw2/rule_dates_fix.py`); those two dates are from memory (tag L) and need the courts agent's check.
72. **Texas notations that add no approval** (a, sweep seed 51925). `writPromotes` now also excludes "denied",
    "dism.", "w.o.j." and the criminal "PDR" wordings, as the reference does.
73. **Closed (c): a split successor without a firm adoption row** (round 2). Reading, on both sides: **a `split`
    succession row never by itself makes the new court hold the old court's decisions. Only an adoption row does,
    and each run (all tables; S/L tables) reads its own adoption rows.** `rename`, `replace` and `absorb` rows are
    unchanged. Grounds: a court made by dividing another does not take the old court's precedent by the division
    alone. The Eleventh Circuit took the former Fifth's by its own en banc decision (*Bonner v. City of Prichard*,
    661 F.2d 1206, 1209 (11th Cir. 1981)); the Tenth Circuit, made from the Eighth in 1929, did not take the
    Eighth's (*Estate of McMorris*, 243 F.3d 1254, 1258 (10th Cir. 2001); doctrine F10). Alabama, Act No. 987 of
    1969 (eff. 1 Oct 1969):
    - the Court of Appeals **continued as the Court of Criminal Appeals** (same court, same three judges): *Coalite,
      Inc. v. Aldridge* (Ala. Civ. App. 1969) says the case "was transferred from the Court of Appeals, now the
      Court of Criminal Appeals, to this, the Court of Civil Appeals, on October 1, 1969, pursuant to Act 987". A
      continued court holds its own decisions (H3). The court acts on that footing: "We overrule Willis, supra, so
      far as it might restrain us from acting ex mero motu" (Ala. Crim. App., 17 Aug 1971, node 110729, of a 1964
      Court of Appeals decision). The adoption row `3 <- 1` is therefore verified and its tag moved **U to S** in
      `data/adoption.tsv` (round 2, one row; the original is `adoption.pre_round2.tsv`);
    - the **Court of Civil Appeals** was a new court. No decision or statute adopting the old court's decisions as
      its own was found in four searches. Its practice treats them as its precedent (it overruled *Colquitt*, a 1964
      Court of Appeals decision, in 2007, node 106047), but that is practice, not an adoption shown. The row
      `2 <- 1` stays U, so findings that rest on it are `firm = 0` on both sides.
    The Lean already read inheritance only from adoption rows. The reference's firm run let the successor hold the
    old court's decisions through the S-tagged succession row; it now reads a split as the Lean does. Expected on
    the 11 real `firm` flags: the 10 Court of Criminal Appeals keys become firm on both sides (data), the 1 Court
    of Civil Appeals key becomes not firm on both sides (reading).

## Round 2: status per line of authority everywhere (2026-11-12, night; closes limit (b) of 69)

These entries are the whole reading. The reference was written from them alone.

74. **Lines and views.** Terms used below.
    - The **effects** of a decision X are as before (history, admitted status-changing treatments, supersessions).
      Each treatment effect has a **reach** (69): `all`, or `lines(orig, reached, unreached)` where `orig` says
      whether the original line is reached and `reached` / `unreached` are lists of heir adopter court ids. History
      and supersession effects reach `all`. An effect is **line-limited** when its reach is not `all`.
    - A **view** is a yes/no function `v` on adopter court ids ("is the asking court in this adopter's line?"). An
      effect with reach `all` reaches every view. An effect with reach `lines(orig, reached, unreached)` reaches
      view `v` iff `v(a)` for some `a` in `reached`, or (`orig` and `v(a)` for no `a` in `unreached`).
    - The **status of X in view v** on (t, u) is the ordinary status computed from only the effects that reach `v`
      (same join, same scope rules, same dates).
    - The **view of a court asked on a date** (court c, optional unit, date d; for a citing or treating decision
      its own court and date): if d = 0 or c has no epoch on d, the court's line is unknown and **every effect
      reaches it** (the union status, as before). Otherwise `v(a)` = "c on d is in adopter a's line" as in 69:
      a has an epoch on d, and c is a, or c is in a's system on a lower line tier (last 4 > appellate 3 > BAP,
      special 2 > appellate division of a trial court 1 > trial 0) and, when a is a federal court of appeals, in
      a's circuit. The unit plays no part.
    - The two kinds of **pure view** of a decision: `orig` (v is false everywhere: a court in no heir's line) and
      `heir a` (v is true of adopter a only).
    - **Union status** = the status from all effects (what `status.tsv` has always shown).
    - Facts that follow and are proved or tested: with no line-limited effect every view gives the union status;
      a view's status is never more severe than the union status.
    - **Original court gone, and dates outside an epoch** (69, restated because court epochs are now dated in
      `courts2.tsv`). Reach is computed with the treating decision B and its date bd, and X with its date. If X's
      court has no epoch on X's date, or B's court has none on bd, the reach is `all`. The original line is
      reached when B's court is X's court; or a non-split successor of it; or a court of X's system on a higher line
      tier than X's court (tiers read on bd for B and on X's date for X); or B's court is an heir adopter and X's
      court has **no epoch on bd** (the original court is gone: the adopter speaks for the original line too). An
      heir a is reached when a is B's court; or the original line is reached and bd <= a's cut-off; or a has an
      epoch on bd, in B's system, on a lower line tier than B's court. An adopter with no epoch on the asking date
      has nobody in its line on that date.
75. **`status_lines.tsv`** (new output file; `status.tsv` is unchanged byte for byte and stays the union status).
    For every decision X at least one of whose effects **in the all-tables run** is line-limited, one block of
    rows per pure view: `orig`, then each adopter id that occurs in a `reached` or `unreached` list of X's
    all-run effects. A block is what `status.tsv` would hold for X if only the effects reaching that view
    existed, over the same issues (the anonymous issue and each admitted holding), with one more, last column
    `line` = `orig` or the adopter's court id. `firm` compares, as in `status.tsv`, with the S/L run's status **in
    the same view** (the S/L run's own effects and reaches; an adopter that is no heir in the S/L run names
    nobody's line there, so that view is then the S/L `orig` view). Decisions with no line-limited effect have no
    rows. It is a separate file because six tools read `status.tsv` by position and would take a line's row for
    the union row.
76. **Treatment-level families read the treating court's line.** For a treatment row (B treats X) the status of X
    that these findings test is X's status **in the view of B's court on B's date** (74), on the anonymous issue,
    at (B's date, B's date): `panelDepartsWithoutEnBanc` and `ignoresBindingInUnit` ("still good law on the
    treating date"), `atRisk soft:` and `atRisk claim:` ("not already wholly negative"), and
    `atRisk inferredRejection` ("not already negative"). For `atRisk contraryBinding` (holder X in court c with
    unit n, later contrary holding Y dated t): "X is still good law" and "Y is good law" are both read **in the view
    of court c on date t**. `citesUnpublishedAsBinding` and `pluralityTreatedAsBinding` do not read status.
    Citation findings already read the citing court's view (69).
77. **Conflicts and splits read the line of the court asked about.**
    - **Conflict** at a bound court (court c, unit n) on asOf: the good-law holdings are those good **in the view
      of c on asOf**. Everything else (67) is unchanged.
    - **Split** between two holdings (Xa of court A, Xb of court B, opposite answers), on asOf:
      - each side counts only if its holding is good law **in the view of its own court on asOf** (court gone on
        asOf: the union status, by 74);
      - "A's holding does not bind B" is now: its force at B is known and below bindingAbsentConflict (as
        before), **or its force at B is known and the holding is not good law in the view of B on asOf**; likewise
        for B's holding at A. A force that is unknown still blocks the split;
      - a resolving holding (non-trial court, dated by asOf, binding both courts) must be good law **in the views
        of both A and B** on asOf.
      A decision overruled only in the Fifth Circuit's line still counts for an Eleventh Circuit conflict, and a
      pre-split decision the Eleventh Circuit overruled en banc no longer prevents a Fifth/Eleventh split.
    - With no line-limited effect all of these are the old tests.
78. **Horty bases read the line of the court asked about.**
    - A **case** is an admitted holding with at least one `factors.tsv` row (holding_id, factor id, side
      `pi`|other = delta, inReason 0/1) whose decision is dated in (0, asOf]. Its family key and outcome come
      from `factor_cases.tsv` (11 columns; column 0 holding id, column 3 family key, column 4 `yes`|`no`; a later
      row for the same holding replaces an earlier one; a row with another outcome is ignored), else from the
      holding's own issue key and yes/no answer (no answer: no case). Outcome yes = pi, no = delta. Facts = all
      its factor rows as (id, side); reason = those with inReason 1. Two cases **conflict** when their outcomes
      differ and each one's reason is contained in the other's facts (as sets of (id, side)). A base is
      **consistent** when no two of its cases conflict.
    - A case is **live** when its holding is good law at (asOf, asOf) in at least one pure view of its decision
      (`orig`, or `heir a` for an adopter named in the reaches of its effects). With no line-limited effect that
      is: good law.
    - **Examined courts** of a family, from its live cases: (i) each live case's (court, unit); (ii) for each
      (system, circuit) of a live case's court epoch on its decision date, the first row of `courts2.tsv` that is
      a trial court of that system (for the federal system: of that circuit as well) with an epoch covering asOf,
      crossed with every unit seen in (i) (including "no unit"); (iii) if any such system is federal, the first
      row of `courts2.tsv` that is a federal appellate court with circuit 1..12 and an epoch covering asOf, no
      unit.
    - The **binding base at an examined court** (court c, unit n) is the live cases whose holding (a) is good law
      **in the view of c on asOf** and (b) has force at (c, n) on asOf of at least bindingAbsentConflict. A base
      with fewer than two cases is skipped. Equal bases (same set of holding ids) are reported once.
    - New output `horty.tsv`: `family, court, verdict (consistent|inconsistent), cases, firm`, one row per
      distinct base of a family; `cases` is the holding ids sorted as strings and joined by commas; `court` is one
      examined court with that base. The comparison key is (family, cases) and the compared value is the verdict.
      `court` and `firm` are not compared (which of several courts with one base is named depends on iteration
      order). The `findings.tsv` rows `inconsistentBindingBase` / `hortyConsistentBase` are written as before
      from the same bases. `hortySelfInconsistent` (a holder court's own cases, informational) reads the holder
      court's view too.
79. **Generator.** The hunt layer of `ref/gen.py` (own random stream; earlier universes unchanged with
    `--no-hunt`) also draws, around the two adoptions it already has: dated epochs for the source court that
    **end** at the cut-off in some universes (the original court is gone) and adopter epochs that start the day
    after; decisions dated outside their court's epoch; yes/no holdings on shared question issues by pre-cut-off
    source decisions, the source court after the cut-off, the adopter and its lower court, with overrulings by
    the source court (before and after the cut-off), the adopter and SCOTUS, so that splits and conflicts differ
    by line; and `factors.tsv` / `factor_cases.tsv` rows for some of those holdings, so that Horty bases differ by
    line.

## Round 3: a ceased deciding court among conflict candidates (2026-11-12, late night; closes the open class of DIFFTEST §9.4)

80. **Displacement of a ceased court's decision** (*Bonner v. City of Prichard*, 661 F.2d 1206, 1209-11). In the
    conflict resolver at a bound court on asOf (67, 77), a counting candidate gives way to another counting
    candidate that binds its deciding court (and every binding adopter in whose line the bound court stands)
    without being bound in turn. The force on the deciding court was read on asOf. If that court has no epoch on
    asOf (it has ceased), the force was unknown, so nothing displaced its decisions. Now a deciding court with no
    epoch on asOf is asked **as it last sat**: in its last epoch that ended before asOf, with the candidate's unit,
    that epoch's circuit, date asOf. A court that never sat before asOf stays unknown. Only the displacement test
    uses this; force, status, findings, splits and Horty bases are unchanged. A holding that bound the old court
    and binds the adopter therefore prevails over the inherited decision (a Supreme Court holding over an old
    Fifth Circuit decision held by the Eleventh Circuit). Lean: `Exec.lastEpoch`, `Exec.forceOnAs`, and `bindsAt`
    in `Run.lean`. Reference: `last_epoch`, `authority(dep_as=)` (R3-80). No theorem changed and none was added.
    Before: sweep `drt9`, 17 of 4,977 conflict keys in 8 of 500 universes, all only in the reference (the
    reference already let the binding holding prevail by another route, and so reported the remaining pair). After:
    those 8 universes 0 (`r3_fail8`); the figures of the final sweep are in `ROUND3.md`. None on real data,
    before or after.
81. **SCDB precision is measured against a narrower definition.** `score.py` counts every Supreme Court decision
    with an admitted status-changing row on a Supreme Court target, including supersession by rule, disapproval of
    language and disavowal of dicta. SCDB's precedent-alteration flag is narrower. A blind audit of the 12
    unflagged decisions (round 3, `round3/scdbaudit.md`) found 11 real acts and 1 reader error (removed).
82. **A writ-refused decision ranks as the court of last resort's among conflict candidates (round 4).** Lean's
    `candFor` gave a Texas court of appeals decision promoted by "writ refused" the precedence of its own tier (2),
    although `forceOn` already treated it as the Supreme Court of Texas's (S-TX-3). Next to an adopted Commission
    of Appeals decision (precedence 3, the adopter's tier) the resolver dropped it; the reference reported both
    answers. Doctrine gives both Supreme Court value, so the reference was right. `Exec/Verdicts.lean` `candFor`
    now reads the tier as last resort when the force path has `TXpromoted`. No theorem statement names `candFor`.
    Before: 3 of 500 universes (seeds 62003, 62350, 62391), 10 conflict keys, reference only. The three universes
    are in `fixtures/regress/r4-*`. Log: `round4/sweep.md`.
83. **Witness rows: an implicit overruling stated by a later court (round 4).** A treatments row listed in
    `data/treatment_witness.tsv` says "X was overruled / abrogated by Y" in the words of a later decision W
    (format: `round3/implicit_schema.md`, SCHEMA). The row names Y; the hash, offsets, quote and window are W's.
    Both checkers (`Cert.checkWitness`; reference `check_witness`) require: W known, `explicit = 0`, a
    status-changing kind; every text check on W's window with X as target; Y named in the quote or window (a
    citation resolves through the index); date X ≤ Y ≤ W; W's court is X's court or has power to overrule X; then
    Y's power over X. Two deliberate differences from the format note: standing does not walk successions
    separately (a successor court has power over its predecessor's decisions already), and a row failing only
    X ≤ Y is reported `targetLater` by Lean and counted as a passed certificate with no finding by the reference,
    as for every other row. A witness row never changes a status (`Spec.inferred_treatment_no_effect`,
    `Examples.witness_row_no_effect`). It yields one finding, `atRisk X Y inferredRejection`, and no panel, unit
    or claim finding. The 13 round-2 rows that named W as the by-decision and cite Y in the window were converted;
    8 stay in the old format (by-decision = the stating court).
84. **`panelDepartsWithoutEnBanc` needs the panel's own overruling words (round 4).** The finding is emitted only
    when the certified quote contains `overrul`, `disapprov`, or `recede(s/d/ing) from`. A blind read of 20 of the
    334 findings added in round 3 found 1 sound (Wilson 1–24%): in 18 the panel says its circuit's precedent "is
    no longer good law" after an intervening Supreme Court or state high court decision, the recognised exception
    to the prior-panel rule. The status rows are unchanged; only the finding is restricted, in both engines
    (`Run.panelOwnWords`; reference `PANEL_OWN_WORDS`). The precision of the findings that remain was not measured.
85. **One cue table (round 4).** The cue phrases and disqualifiers are in `tools/caselaw2/cues/cue_table.json`.
    `gen_cues.py` writes them into `LegalProofs/CaseLaw2/CueTable.lean`, `ref/cue_table.py` and
    `reader/cue_table.py` (`--check` fails if a copy is stale). The shared table is the reader's: against the old
    checker table, `supersededByEnactment` gains "abrogat" and `questioned` gains "no longer". 41 rows that failed
    `noCue` now pass their text check (29 of round 3 and 12 older model-read rows; neither kind changes status).
86. **Same court, one decision promoted by "writ refused" (round 4).** After 82, the final sweep found the mirror
    case in the reference (seed 63322, 3 conflict keys): a writ-refused decision and a later unpromoted decision
    of the same Texas court of appeals bind each other, and the reference had no precedence step, so it reported
    both answers. Lean keeps the writ-refused decision (precedence 3 over 2), which is the doctrine of S-TX-3.
    The reference's `_resolve.binds` now refuses to let the unpromoted decision displace or equal the promoted one
    (R4-86). The universe is `fixtures/regress/r4-63322`. Real-data conflict rows did not change (92, 0 differ).
