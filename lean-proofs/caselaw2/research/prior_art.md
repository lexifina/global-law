# caselaw-lean-2: prior art

Survey for v2 (holdings, partial overruling, richer authority, statute abrogation, in-Lean certificates, rule-like
holdings, circuit splits). Written 2026-11-12 after about 38 web searches and fetches. Everything below is paraphrased.

**How sure each entry is.**
- **[abs]**: I read only the abstract, a publisher or index record, or a summary by someone else.
- **[full]**: I read the paper itself, or the parts of it I cite.
- **[mem]**: from background knowledge, not re-checked in this pass. Verify these before citing them in the write-up.

v1 baseline (`LegalProofs/USCaseLaw/{Courts,Precedent}.lean`):
- Courts are (system, tier, circuit) with `binds` and `mayOverrule`.
- An overruling event is a whole-decision pair (by, target). It is valid when the overruling court has power over the
  target's court and the target is not later.
- `overruledOn` is monotone, with no revival.
- Per-decision findings: `citesLater`, `invalidOverrulings`, `citesOverruled`.

Nothing in v1 knows *why* a case was decided, so none of the precedent-constraint literature has been used yet.

---

## 1. Formal theories of precedent

### 1.1 Horty: result model and reason model

**Sources.**
- J. F. Horty, "The result model of precedent", *Legal Theory* 10 (2004) 19–31 [mem].
- J. F. Horty, "Rules and reasons in the theory of precedent", *Legal Theory* 17(1) (2011) 1–33.
  https://www.cambridge.org/core/journals/legal-theory/article/rules-and-reasons-in-the-theory-of-precedent/3B7697D8BD95470F3A814ACA72C5A2F9 [abs]
- J. F. Horty & T. Bench-Capon, "A factor-based definition of precedential constraint", *AI and Law* 20(2) (2012)
  181–214, doi:10.1007/s10506-012-9125-8. https://link.springer.com/doi/10.1007/s10506-012-9125-8 [abs; definitions mem]
- Horty, *Reasons as Defaults* (OUP 2012) [mem].
- Horty, *The Logic of Precedent: Constraint and Freedom in Common Law Reasoning* (CUP).
  https://resolve.cambridge.org/core/books/logic-of-precedent/6C39AEE563BFD32769406F866E3833CE [abs]

**What it formalises.** How an earlier decision constrains a later court, on a base of *factors*. A factor is a
binary, legally relevant feature of a fact situation. Each factor favours one of two sides, π (plaintiff) or δ
(defendant).

**Key definitions (paraphrased).**
- **Fact situation:** a set X of factors. X^s is the subset of factors that favour side s.
- **Case:** a triple c = ⟨X, r, s⟩. X is the fact situation, s is the outcome, and r ⊆ X^s is the *reason* (the
  rule's premise) the court gave for s. The case is read as a defeasible rule r → s.
- **Priority induced by a case:** the court has ruled that r outweighs every set of opposing factors present in the
  case. So for every Y ⊆ X^{s̄}, Y <_c r. The relation is lifted to supersets (if r ⊆ r′, then r′ is at least as
  strong).
- **Case base:** Γ, a set of cases. Its derived ordering <_Γ is the union of the case orderings, closed under the
  superset lifting.
- **Consistency:** Γ is *inconsistent* if some pair of reasons is ordered both ways (Y <_Γ Z and Z <_Γ Y).
  Otherwise it is consistent.
- **Reason model:**
  - A decision for s on new facts with reason r′ is *permitted* iff Γ plus the new case is still consistent.
  - A decision for s is *forced* iff every decision for s̄ would be inconsistent.
  - A later court may *distinguish* a precedent: it points to factors in the new situation for s̄ that were absent
    from the precedent. Doing so refines, but never contradicts, the earlier ordering.
- **Result model:** the special case where the reason is all of X^s, i.e. the strongest possible reading. The
  precedent controls a new case F only *a fortiori*: F has at least the precedent's pro-s factors and at most its
  con-s factors. This is more conservative than the reason model.
- **Horty 2011 equivalence:** the reason model is extensionally equivalent to a rule model in which later courts may
  *narrow* earlier rules (by adding exceptions) consistently with all earlier outcomes. Precedent therefore
  constrains like defeasible rules.
- **Horty & Bench-Capon 2012:** the same theory in factor terms. It also discusses how to represent precedents whose
  ratio can be read more than one way.

**Limits.**
- Factors are given in advance and are binary. Dimensions are a later extension (Horty 2019, Rigoni 2015/2018, below).
- Single-step: no intermediate issues. Later work adds hierarchy.
- No court hierarchy. There is one case base and one court.
- No time, no overruling and no statute.
- A precedent's reason must be supplied, and in real opinions it is exactly what courts disagree about.

**Take for v2.**
- *Holding = (reason r, outcome s) over a factor vocabulary scoped to an issue.* It is a finite-set structure:
  `Finset Factor`, decidable `<_Γ`, decidable consistency.
- The predicates *permitted*, *forced* and *a fortiori* are cheap, decidable and provable in Lean.
- "Overruling" removes a case (or one holding) from Γ, and "partial overruling" removes some holdings of a decision.
  Then **removal can only shrink <_Γ**, so overruling preserves consistency. That is a one-line monotonicity theorem
  and a nice structural result for v2.
- Use the result model as the conservative default whenever the reader cannot extract a reason. Use the reason model
  only when the certificate quotes a stated rule.

### 1.2 Prakken (2019–2021) and the dimension models

**Sources.**
- H. Prakken, "Comparing alternative factor- and precedent-based accounts of precedential constraint", JURIX 2019,
  73–82 [abs].
- H. Prakken, "A formal analysis of some factor- and precedent-based accounts of precedential constraint", *AI and
  Law* 29(4) (2021) 559–585, doi:10.1007/s10506-021-09284-6. Open copy:
  https://webspace.science.uu.nl/~prakk101/pubs/cbrailj20.pdf [abs]
- Related dimension work [mem]:
  - Horty, "Reasoning with dimensions and magnitudes", *AI and Law* 27 (2019).
  - A. Rigoni, "An improved factor based approach to precedential constraint", *AI and Law* 23 (2015).
  - A. Rigoni, "Representing dimensions within the reason model of precedent", *AI and Law* 26 (2018).

**What it formalises.** A critical comparison of the reason and result models with dimension-based versions
(Horty's, Rigoni's), plus an alternative.

**Key definitions.**
- Prakken gives simple *syntactic* criteria, both factor-based and dimension-based, for when a decision is forced. In
  effect, the new case must be at least as strong for the outcome on every factor or dimension as a precedent that
  had that outcome.
- His alternative is less expressive than the reason model but, in his words, easier to apply in practice.
- The JURIX version embeds these models in Dung-style abstract argumentation, so "forced" becomes "justified in the
  grounded extension".

**Limits.** Still flat (one issue, one court). Dimensions need an ordering on values for each dimension, which an LLM
reader would have to supply.

**Take for v2.**
- Prakken's syntactic a fortiori criterion is the most implementation-friendly definition of "this holding controls
  that case". It is a pointwise comparison and decidable by `decide` over small sets.
- Use it as the core of a `controls : Holding → Situation → Bool` and prove that it implies Horty's *forced* under
  the result-model reading.

### 1.3 Canavotto, Horty, Mullins, van Woerkom et al.

**Sources.**
- I. Canavotto, "Precedential constraint derived from inconsistent case bases", JURIX 2022, FAIA 362,
  doi:10.3233/FAIA220445. https://ebooks.iospress.nl/pdf/doi/10.3233/FAIA220445 [abs]
  - Horty had only sketched constraint for inconsistent case bases. Canavotto develops and checks it.
- I. Canavotto & J. Horty, "The importance of intermediate factors", JURIX 2023.
  https://ebooks.iospress.nl/pdf/doi/10.3233/FAIA230941 [abs]
  - Reasoning goes base factors → decisions on intermediate issues → outcome by logic.
- Canavotto & Horty, "Reasoning with hierarchies of open-textured predicates" (2023).
  https://researchr.org/publication/CanavottoH23 [record only]
- W. van Woerkom, D. Grossi, H. Prakken, B. Verheij:
  - "Hierarchical precedential constraint", ICAIL 2023, 333–342, doi:10.1145/3594536.3595154.
    https://webspace.science.uu.nl/~woerk003/hpc.pdf [abs]
  - "Hierarchical a fortiori reasoning with dimensions", JURIX 2023, doi:10.3233/FAIA230944 [abs]
  - Journal version "Hierarchical models of precedential constraint", *AI and Law* (2026): four models (with and
    without dimensions and incomplete information). The authors prove these are **monotonic** under added precedents
    and added facts [abs].
  - "Justification in case-based reasoning" (ArgXAI, CEUR 3209) [abs].
  - "Landmarks in case-based reasoning: from theory to data" (HHAI 2022) [mem]. It measures consistency of real
    datasets used as case bases.
  - van Woerkom's PhD thesis, *A Fortiori Case-Based Reasoning* (Utrecht 2025).
    https://webspace.science.uu.nl/~woerk003/proefschriftweb.pdf [abs]
- R. Mullins, "Two factor-based models of precedential constraint: a comparison and proposal", *AI and Law* 31
  (2023) 703–738, doi:10.1007/s10506-022-09335-6 [abs]
  - Combines the reason model (precedents *rebut*) with an exclusionary model (precedents *undercut* opposing reasons).
  - Uses the undercut/rebut distinction to model **strict (binding) versus persuasive** precedent.
  - Mullins also has "Weight and authority in formal models of precedential constraint" (*Jurisprudence*, 2025)
    [record only].

**Take for v2.**
- **Inconsistent case bases (Canavotto):** the US system *as a whole* is an inconsistent case base. Circuits
  disagree. Constraint must be computed per court, over the *binding* sub-base only. That is exactly v1's `binds`
  relation, lifted to case bases.
- **Hierarchy (Canavotto–Horty, van Woerkom):** a decision's holdings resolve intermediate *issues*, and the outcome
  follows by rule. This is the right shape for "decision = set of holdings, one per issue": partial overruling
  removes one issue-holding while the others stand.
- **Monotonicity theorems (van Woerkom):** these are the kind of meta-results v2 should prove in Lean. Adding facts
  or precedents never un-forces a decision. Removing precedents (overruling) never creates inconsistency.
- **Mullins:** gives a principled way to type the v2 `Authority` relation as *binding* (exclusionary/undercutting)
  versus *persuasive* (rebutting weight). It is a better rationale than an ad hoc enum.

### 1.4 Lamond's constraint account

**Source.** G. Lamond, "Do precedents create rules?", *Legal Theory* 11(1) (2005) 1–26.
https://api.philpapers.org/rec/LAMDPC [abs]

**What it formalises (informal theory).**
- Precedents do not lay down rules. They create a special kind of reason: the earlier court's *assessment of the
  balance of reasons on its facts* binds later courts.
- A later court may distinguish only on facts that the earlier assessment did not already cover. Distinguishing is
  therefore constrained, not free.
- Lamond's motivating problem is that distinguishing is hard to square with orthodox (Razian) accounts of rules.
- Horty's reason model is widely read as the formalisation of this idea [abs, via Horty & Bench-Capon].

**Take for v2.** The legal justification for modelling holdings as priority constraints rather than as statutes. The
write-up should cite Lamond, then Horty, as the theory being formalised. There is nothing extra to encode.

### 1.5 Prakken & Sartor: argumentation-based precedent

**Sources.**
- H. Prakken & G. Sartor, "Modelling reasoning with precedents in a formal dialogue game", *AI and Law* 6 (1998)
  231–287 [abs; volume and pages mem].
  - Precedents become pro and con rules over factors, plus a priority between them.
  - New cases are argued in a dialogue game for argumentation with prioritised defeasible rules.
- Bench-Capon & Sartor, "A model of legal reasoning with cases incorporating theories and values", *AIJ* 150 (2003)
  97–143 [mem]. Theories are built from cases. Rule priorities are explained by preferences over values.
- Prakken, Wyner, Bench-Capon & Atkinson, "A formalization of argumentation schemes for legal case-based reasoning in
  ASPIC+", *J. Logic and Computation* 25 (2015) [mem].

**Take for v2.**
- The rule-plus-priority representation is what Lean should store.
- Argumentation semantics (grounded extension) are the natural way to compute "status of a proposition" when holdings
  conflict. They are computable on a finite argument graph and are a candidate for a decidable checker.
- Value-based priorities are *out of scope*: they are not observable in text.

### 1.6 HYPO, CATO, IBP (Ashley, Aleven, Brüninghaus)

**Sources [mem].**
- K. Ashley, *Modeling Legal Argument: Reasoning with Cases and Hypotheticals* (MIT Press 1990). HYPO covers trade
  secrets, uses dimensions, and builds claim lattices.
- V. Aleven, "Using background knowledge in case-based legal reasoning", *AIJ* 150 (2003) 183–237. CATO has 26 base
  factors under a factor hierarchy of abstract issues, with downplaying and emphasising moves.
- S. Brüninghaus & K. Ashley, ICAIL 2003. IBP is issue-based prediction, about 91% on the CATO cases.
- K. Ashley, *Artificial Intelligence and Legal Analytics* (CUP 2017).

**Key ideas.**
- *On-point* cases share factors. *Most on-point* cases are maximal in the claim lattice under set inclusion of
  shared factors.
- *Counterexamples* and *distinctions* are defined over sets of factors.
- CATO's factor hierarchy is the ancestor of the "intermediate factor / issue" hierarchies above.

**Limits.** Hand-built factor vocabularies for one doctrine (trade secrets). There is no notion of court hierarchy or
time.

**Take for v2.**
- The claim lattice is a neat, decidable notion of "closest precedent". It is useful for picking *which* binding
  holding a citing court is applying.
- Main lesson: factor vocabularies are per-issue and hand-made. A 6.9M-decision run cannot have them for every issue.
  Restrict factor-level modelling to a pilot domain, or build vocabularies per US Code section for statutory issues.

### 1.7 ANGELIC (Al-Abdulkarim, Atkinson, Bench-Capon)

**Sources.**
- L. Al-Abdulkarim, K. Atkinson, T. Bench-Capon, "A methodology for designing systems to reason with legal cases
  using Abstract Dialectical Frameworks", *AI and Law* 24 (2016), doi:10.1007/s10506-016-9190-5.
  https://link.springer.com/article/10.1007/s10506-016-9190-5 [abs]
- JURIX 2017 fielded application (noise-induced hearing loss claims, with Weightmans LLP).
  https://cgi.csc.liv.ac.uk/~katie/jurix17a.pdf [abs]
- K. Atkinson & T. Bench-Capon, "ANGELIC II", ICAIL 2023.
  https://intranet.csc.liv.ac.uk/~tbc/publications/ICAIL2023_Angelic2.pdf [abs]
- Bench-Capon & Atkinson, "Precedential constraint: the role of issues", ICAIL 2021.
  https://cgi.csc.liv.ac.uk/~katie/icail21b.pdf [record]

**What it formalises.** A domain as an Abstract Dialectical Framework: a tree from the outcome through issues and
abstract factors down to base factors. Each node has an *acceptance condition*: an ordered list of
accept/reject conditions over its children, tried in order. The tree is built from the precedents.

**Limits.** Knowledge-engineered for each domain. Its accuracy claims are on small, curated case sets (CATO-style).

**Take for v2.**
- Acceptance conditions as **ordered exception lists** have the same shape as Catala's default logic (§5.1). They are
  a simple, decidable structure for a "rule-like holding": a holding on an issue = an ordered list of
  (condition → result) with a default.
- Recommend this as the encoding of rule-like holdings, with each clause traced to the decision that added it. That
  supports partial overruling: delete that clause.

### 1.8 What could be encoded in Lean, and what "consistency of a case base" means

Encodable directly (all finite and decidable):
- `Factor` (per-issue vocabulary, with a side), `Situation := Finset Factor`, `Holding := {issue, reason : Finset
  Factor, outcome : Side}`.
- The derived priority <_Γ, a fortiori control, *permitted*, *forced*, and the claim-lattice "most on-point".
- Acceptance-condition lists (ANGELIC/Catala-style rule-like holdings).
- Binding sub-base: Γ_b(court, date) = holdings of decisions that `binds` the court, decided before the date, not
  overruled on the date (v1 machinery).

Consistency notions v2 can check, from weakest to strongest:
1. *Outcome consistency (result model):*
   - Statement: no two cases in one binding sub-base where one is a fortiori for an outcome and the other has the
     opposite outcome.
   - Needs only factors and outcomes.
2. *Reason consistency (Horty):* <_Γ has no 2-cycles over the stated reasons.
3. *Hierarchical consistency (van Woerkom):* consistency at each issue node, plus correct outcome derivation from
   issue decisions.

A consistency violation within one binding sub-base is a *finding*. Either the reader misread a holding, or there is an
implicit overruling or an unacknowledged conflict. Across sub-bases that do not bind each other, a violation is a
*split* (§6, recommendation 4).

---

## 2. Formal and computational treatment of authority and hierarchy

### 2.1 Citation-network authority

**Sources.**
- J. H. Fowler, T. R. Johnson, J. F. Spriggs II, S. Jeon, P. J. Wahlbeck, "Network analysis and the law: measuring
  the legal importance of precedents at the U.S. Supreme Court", *Political Analysis* 15(3) (2007) 324–346.
  https://www.cambridge.org/core/journals/political-analysis/article/network-analysis-and-the-law-measuring-the-legal-importance-of-precedents-at-the-us-supreme-court/D9B2F13BE2594E1527780AAFDD6BF164
  Copy: https://pdodds.w3.uvm.edu/files/papers/others/everything/fowler2007a.pdf [abs]
  - Kleinberg HITS on 26,681 majority opinions (1791–2005).
  - *Authority* score: many citations from good hubs. *Hub* score: cites many good authorities.
  - Rankings matched expert judgment and landmark lists.
- Fowler & Jeon, "The authority of Supreme Court precedent", *Social Networks* 30 (2008) [abs; 30,288 opinions,
  1754–2002].
- M. Bommarito, D. M. Katz, J. Zelner, "Law as a seamless web?", 2009.
  https://papers.ssrn.com/abstract=1419525 [abs]
- Bommarito, Katz, Zelner, Fowler, "Distance measures for dynamic citation networks", *Physica A* (2010),
  arXiv:0909.1819. https://pdf.arxiv.org/pdf/0909.1819 [abs]
- Later work: Schmid et al., "Generative dynamics of Supreme Court citations" (*Political Analysis* 2021). The Ukrainian
  100M-decision citation graph (arXiv 2605.15362) shows the scale is routine [abs].

**Limits.**
- Importance is not authority. HITS is blind to binding/persuasive status, to negative treatment and to time order.
- Scores are for SCOTUS only. No replication files were found in this pass.

**Take for v2.**
- Not a Lean concept. Use it as an *auxiliary ranking* to pick which decisions get expensive holdings extraction:
  high-authority targets first.
- Report it alongside Lean's binding-reach count (the number of later decisions bound by a holding, computed from
  `binds`). The contrast "authority score vs formal binding reach" is a cheap, interesting figure.

### 2.2 Formal models of stare decisis hierarchy and "good law"

- I found no prior proof-assistant model of court hierarchy or good-law status. The Lean Zulip "Legal and Lean"
  thread has no substantive answer.
  https://leanprover-community.github.io/archive/stream/236449-Program-verification/topic/Legal.20and.20Lean.html
  v1 appears to be novel in this respect, and v2's Authority layer extends ground nobody has formalised.
- The closest formal analogue is the AI-and-law work above (Mullins's strict vs persuasive; Canavotto's inconsistent
  bases), but it has no courts in it.
- The **Free Law Project citator roadmap** plans "court authority" relationships (which court can overrule which) and
  full appellate chains. https://free.law/2025/05/01/citator/ [full]
  This is the same thing v1 `mayOverrule` encodes. If they publish a court-authority table, v2 should diff its own
  court table against it.
- **Westlaw "Overruling Risk"** (§3.1) is the only commercial notion of *derived* bad law: a case relies on an
  overruled one. It corresponds to v1 `citesOverruled`, lifted to holdings.

---

## 3. Citators and treatment taxonomies

### 3.1 Shepard's and KeyCite (public descriptions)

**Shepard's (LexisNexis).**
- Sources:
  - https://www.lexisnexis.com/en-us/support/lexis/faqs/shepards-signal-indicators.page
  - https://www.lexisnexis.com/pdf/lexis-advance/Shepards-Signal-Indicators-and-analysis-phrases-Final.pdf [abs]
- Signals:
  - *Warning* (red): strong negative treatment, e.g. overruled by, reversed by.
  - *Questioned* (orange): precedential value questioned.
  - *Caution* (yellow): possible negative treatment, e.g. limited, criticized, distinguished.
  - *Positive* (green).
  - *Neutral / analysis available* (blue): e.g. explained.
- Under the signals is a list of *analysis phrases* [mem]: overruled by, overruled in part by, superseded by statute
  as stated in, abrogated by / as stated in, reversed, vacated, questioned by, limited by, criticized by, distinguished
  by, followed by, explained by, and others.

**KeyCite (Thomson Reuters).**
- Sources:
  - https://www.thomsonreuters.com/en-us/help/drafting-assistant/westcheck/keycite-status-flags
  - https://thomsonreuters.ca/en/westlaw-edge/features/keycite-overruling-risk.html [abs]
- Flags:
  - Red flag: no longer good law for at least one point (reversed or overruled).
  - Red-striped: overruled in part.
  - Yellow: some negative history.
  - Blue-striped: appeal pending.
  - Orange **Overruling Risk** (Westlaw Edge): a point of law may be implicitly undermined because it relies on a
    decision that was overruled or otherwise invalidated. It is AI-generated, not editor-assigned.
- KeyCite also grades *depth of treatment* (examined / discussed / cited / mentioned) [mem].

**Take for v2.** The treatment enum in DESIGN.md (overrules, overrules-in-part, abrogates, receded-from, disapproves,
limits, questions, distinguishes, follows, plus same-case history) matches these phrase sets well. Add:
- `supersededByStatute` (a court *acknowledges* statutory abrogation; distinct from v2's own computed abrogation);
- `explains`;
- `criticizes`;
- a separate `history` type (reversed, vacated, affirmed, modified) that is *never* conflated with overruling;
- a *derived* `atRisk` status. A holding whose stated reason depends on an overruled holding is computed, never
  extracted. It is Overruling Risk done as a proof rather than as AI.

### 3.2 Measured accuracy of commercial citators

**Source.** P. Hellyer, "Evaluating Shepard's, KeyCite, and BCite for case validation accuracy", *Law Library
Journal* 110(4) (2018) 449–476. https://scholarship.law.wm.edu/libpubs/131 [abs]

**Findings.**
- Sample: 357 citing relationships flagged negative by at least one citator, starting from 73 Ninth Circuit decisions
  of January 1984.
- Shepard's and KeyCite each missed or mislabelled about a third of the negative relationships. BCite missed over two
  thirds.
- All three agreed on negative treatment only 53 times. In 85% of the relationships, they did not agree.
- Errors propagate through to other citing relationships.
- Earlier: Taylor (2000), cited by Demir & Canbaz [mem].

**Validity of Shepard's as research data.**
- Spriggs & Hansford, "Measuring legal change: the reliability and validity of Shepard's Citations", *Political
  Research Quarterly* (2000).
  https://sites.ucmerced.edu/hansford/publications/measuring-legal-change-reliability-and-validity-shepards-citations
  [abs]
- Shepard's treatment coding is fairly reliable overall, but reliability varies by category.

**Take for v2.**
- Commercial citators are *not* ground truth. On negative treatment, about one in three relationships is wrong per
  tool.
- v2's evaluation should never use a single citator as the gold standard. Report three-way agreement where available,
  and lean on courts' own statements and curated lists (CRS, SCDB).
- This also strengthens the case for certificates: a treatment that comes with its quoted words is auditable in a
  way that a flag is not.

### 3.3 CourtListener / Free Law Project

**Sources.**
- Citation APIs: https://wiki.free.law/c/courtlistener/help/api/rest/v4/citations
- Bulk data: https://wiki.free.law/c/courtlistener/help/api/bulk-data
- Citation depth: https://free.law/2020/03/05/citation-depth-data/ [abs]

**What exists.**
- Opinion→opinion citation graph with `depth`, the number of times the cited opinion is cited in the citing opinion.
  It is exported quarterly in bulk.
- Parentheticals, available in bulk.
- eyecite, the open-source citation extractor.
- **No published treatment labels yet.**

**FLP AI citator experiment (2025).** https://free.law/2025/05/01/citator/ [full]
- Task: binary overruled / not overruled.
- Data: 149 confirmed overruled opinions *from the Congress.gov decisions-overruled table*, plus random CourtListener
  negatives, about 1,000 records at a 15:100 ratio.
- Context: eyecite locates each citation, and the six sentences on either side are sent to the model.
- Only thresholds were published:
  - Claude 3.5 Sonnet was the only model with recall above 90% (F1 above 80%).
  - Mistral Large was the only model with precision above 80%.
- Plans: court-authority relationships, appellate chains, and open-sourcing the citator.

**Take for v2.**
- Use eyecite-style span offsets as the certificate anchor.
- Parentheticals are a cheap, high-yield source of *other courts' descriptions* of a decision's holding and
  treatment, e.g. "(overruled in part on other grounds by …)". Use them as held-back evaluation, or as weak labels.
- FLP uses the same CRS table we have, so our numbers are comparable to theirs.

### 3.4 Harvard Caselaw Access Project (CAP)

**Sources.**
- https://lil.law.harvard.edu/our-work/caselaw-access-project
- Transitions post (restrictions lifted March 2024):
  https://lil.law.harvard.edu/blog/2024/03/26/transitions-for-the-caselaw-access-project [abs]

**What it has.**
- About 6.5–6.7M decisions (1658 to 2018), now unrestricted, distributed under CC0 (HF mirror).
- Static bulk at static.case.law [mem] with per-case `cites_to` [mem; not confirmed in this pass].
- It is already our source corpus with CourtListener.

**Take for v2.** CAP has no treatment data. Its value is the per-reporter page and offset structure, which gives
stable certificate anchors (volume, page, offset).

### 3.5 Automated citators, ML and "bad law bots"

**Casetext.**
- Launched a negative-treatment citator alongside CARA, and later SmartCite with richer than three-colour categories.
  https://www.lexblog.com/?p=669455 [abs]
- No precision or recall figures found. Casetext also *supplied* the attorney-labelled overruling sentences behind the
  CaseHOLD paper's Overruling task (§6.1).

**"Bad Law Bot"** (Stanford student, open source, 2017).
https://law.com/therecorder/2017/10/27/could-this-open-source-tool-tell-you-when-good-law-goes-bad [abs]
- Reported 89% precision on flagged negative treatments.
- Missed about 18% of negative treatments, i.e. about 82% recall.
- Could not handle nuanced treatment.

**Keyword patents.** A USPTO patent (US 7,529,756 / 8,600,974 family) describes stem matching on "overrul" near a
citation [abs]. This is essentially v1's candidate regex, and it misses implicit treatment.

**Demir & Canbaz.** "Validate your authority: benchmarking LLMs on multi-label precedent treatment classification",
NLLP 2025, 172–183. https://aclanthology.org/2025.nllp-1.13/ and arXiv 2605.17691 [abs]
- Expert-annotated set of 239 citations (one arXiv version: 329 high-confidence relationships).
- Multi-label treatment, with an *Average Severity Error* metric that penalises confusing "overruled" with "followed"
  more than near-misses.
- I did not retrieve its tables.

**Galgani & Hoffmann.** LEXA (2010), knowledge engineering plus ML for citation classes (Australian) [abs via Demir &
Canbaz].

**Shulayeva, Siddharthan, Wyner.** "Recognizing cited facts and principles in legal judgements", *AI and Law* 25
(2017), doi:10.1007/s10506-017-9197-6. https://link.springer.com/article/10.1007/s10506-017-9197-6 [abs]
- Per-class precision and recall of about 0.79–0.89 for cited fact / principle sentences.
- Relevant to locating the *holding* sentences that a citing court relies on.

**Take for v2.**
- Severity-weighted error is the right headline metric for a treatment reader. A missed "overruled" is far worse
  than "limited" read as "distinguished". Adopt it.
- Expected reader quality from published work:

  | Task | Precision | Recall |
  |---|---|---|
  | Express overruling | 0.8–0.9 | 0.8–0.9 |
  | Implicit or partial treatment | much worse (no robust public numbers) | much worse |

---

## 4. Datasets of overrulings and treatments

| Dataset | What | Treatment / overruling content | Access |
|---|---|---|---|
| **SCDB** (Spaeth et al.) | Every SCOTUS decision: legacy 1791–1945 and modern 1946–present, case- and justice-centred | `precedentAlteration` (Spaeth ALT_PREC): 1 if the majority opinion says it overrules, or effectively overrules, one or more of the Court's own precedents (including "disapproved" or "no longer good law"). It is a flag only: the *altered* precedents are not identified, and one row may alter several. Also: `lawType`/`lawSupp` (the statute at issue), `splitVote`, `certReason` (cert reason codes include intercircuit conflict). | https://scdb.la.psu.edu (codebook https://scdb.la.psu.edu/online-codebook). Free download (CSV/SAV), a few MB per release. Licence: free with citation [mem; check terms]. |
| **CRS / Congress.gov "Table of Supreme Court decisions overruled by subsequent decisions"** | Pairs (overruling decision → overruled decisions) | Express and implicit SCOTUS-by-SCOTUS overrulings, curated by CRS | https://constitution.congress.gov/resources/decisions-overruled/ ; public domain (US government work). We hold the 2016 CONAN edition (`crs/crs2016.tsv`, 236 rows). Refresh from the live site: it has rows after 2016 (Dobbs, Loper Bright …). |
| **Hansford & Spriggs, *The Politics of Precedent on the U.S. Supreme Court*** (Princeton UP 2006) | Shepard's treatment of SCOTUS precedents by later SCOTUS majority opinions, 1946–1999 era | Positive and negative interpretation counts per precedent per term | Not publicly posted (found no replication link). Derived from Shepard's, so redistribution is likely restricted. https://sites.ucmerced.edu/hansford/publications |
| **Cape & Kastellec** (working paper) | Extends the Spriggs Shepard's data on SCOTUS majority opinions, 1953–2023, with a focus on negative treatment | Yes, Shepard's categories | https://jkastellec.scholar.princeton.edu/document/166 [abs]; ask the authors. |
| **Songer U.S. Courts of Appeals Database** (+ Kuersten–Haire update 1997–2002) | About 30 sampled published decisions per circuit per year, 1925–2002, weighted | **En banc yes**: codes en banc after one panel, after several panels, with no prior panel, or after SCOTUS remand. More than 3 judges is treated as en banc. Treatment-of-precedent variables not confirmed in this pass. | https://artsandsciences.sc.edu/poli/juri/appct.htm ; codebook https://artsandsciences.sc.edu/poli/juri/KH_update_codebook.pdf ; ICPSR 2086. Free. About 20k cases [mem]. |
| **Sapiro-Gheiler & Kastellec, LLM-coded Courts of Appeals database** (working paper, June 2026) | About 440k published appellate opinions, 1892–2025 | Metadata, issue, litigants and direction. About 85–90% agreement with human coders on key variables and about 80% on direction. | https://jkastellec.scholar.princeton.edu/publications/appealing-large-language-model-judge-comprehensive-machine-coded-database-us-courts [abs]; release status unknown. |
| **CaselawQA** (LawMA, ICLR 2025) | 260 annotation tasks derived from SCDB and Songer variables | Indirect (uses Songer/SCDB codes as labels) | https://proceedings.iclr.cc/paper_files/paper/2025/file/56e5719d297fc1a778b0ec77cb6278d7-Paper-Conference.pdf [abs] |
| **Brace–Hall State Supreme Court Data Project** | Every state supreme court decision 1995–1998, all 50 states, more than 200 variables. Extended to 1995–2010 ("New data on state supreme court cases", *SPPQ* 2021). | No overruling or precedent-treatment variable found | https://artsandsciences.sc.edu/poli/juri/databases.htm ; extension: https://resolve.cambridge.org/core/journals/state-politics-and-policy-quarterly/article/new-data-on-state-supreme-court-cases/9844B659308AE7FC1ED66F7BBB016B28 [abs] |
| **Circuit splits** | Beim & Rader, *JELS* 2019: original dataset of splits 2005–2013. About a third were resolved by SCOTUS, more likely when disagreement is contemporaneous and growing. Also "Setting the Supreme Court's policy agenda" (Cambridge, 119 intercircuit splits), the Yale "Evolution of conflict" paper, and a 1986–87 cert-petition dataset (Duke). | Hand-coded split lists | Beim & Rader: https://zendy.io/title/10.1111/jels.12224 ; Yale: https://Law.yale.edu/sites/default/files/documents/pdf/Intellectual_Life/EvolutionofConflict.pdf [abs]. **No public machine-readable split dataset found.** Caveats: SCDB codes a split only when the Court says so, so it undercounts (Bruhl, via SCOTUSblog). SCOTUSblog and Bloomberg Law publish circuit-split roundups [mem] that could be scraped as weak labels, subject to their terms. |
| **Congressional overrides** | Christiansen & Eskridge, "Congressional overrides of Supreme Court statutory interpretation decisions, 1967–2011", *Texas L. Rev.* 92 (2014) | About 275 overrides, with statute and decision [mem] | Appendix tables in the article; already named in DESIGN.md. |
| **Holdings datasets** | CaseHOLD: 53,137 multiple-choice (citing context, 5 candidate holdings), from the Harvard case-law corpus (3.4M decisions, 1965 on). LePaRD: millions of (citing context → quoted precedent passage) pairs from US federal courts, 1.8M target passages. | Holding *statements* as written by later courts in parentheticals. LePaRD is *quoted passages*, a proxy for the operative language. | CaseHOLD: https://github.com/reglab/casehold , HF `casehold/casehold` [licence: check, mem Apache-2.0]. LePaRD: https://github.com/rmahari/LePaRD , HF `rmahari/LePaRD` (CC BY-NC-SA 4.0 per a third party; check). |

**Take for v2.**
- Use SCDB `precedentAlteration` as a *decision-level recall check*. Every SCOTUS decision flagged 1 must have at
  least one admitted overruling or partial-overruling event with a passing certificate. Every SCOTUS overruling event
  v2 admits should be in a flagged decision (precision check).
- Use CRS as the pair-level check. v1 found 70 of 236 express. v2's implicit and partial events should raise that,
  and each CRS pair v2 still misses should be classified.
- SCDB `lawType`/`lawSupp` join SCOTUS decisions to the statute at issue. That gives a ready seed for the statute
  join and for the Christiansen–Eskridge override check.
- Songer's en banc codes validate the v2 panel/en banc attribute and the prior-panel rule (only en banc overrules
  circuit precedent).

---

## 5. Formal verification and legal code

### 5.1 Catala

**Source.** D. Merigoux, N. Chataing, J. Protzenko, "Catala: a programming language for the law", *PACMPL* 5 (ICFP
2021). arXiv:2103.03198. https://arxiv.org/abs/2103.03198 [abs]

**What it formalises.**
- Statutes as *prioritised default logic*: a base rule plus exceptions with explicit precedence. This is the logic
  Lawsky argued fits statutes.
- Literate programming interleaves law text and code.
- Compiles to a lambda calculus. The compilation scheme is proved correct in F*.
- Used on US IRC §121 and French family benefits, where it found a bug in the official implementation.
- Follow-ups: CUTECat, concolic testing of Catala programs (arXiv 2410.18212) [abs].

**Limits.** Statutes only. No case law, no time-indexed versions of the rules themselves, and no court hierarchy.

**Take for v2.**
- The default/exception structure, with a precedence edge per exception, is the right encoding for a *rule-like
  holding* that narrows a statute: "§X applies, except where [holding]". Each exception carries its source decision.
  Abrogation by statute *removes* or *overrides* an exception at an effective date.
- The literate-code pattern (code next to the quoted text) is the presentation model for certificates.

### 5.2 L4 (SMU CCLAW / Legalese)

**Sources.**
- https://cclaw.smu.edu.sg/about
- https://l4-documentation.readthedocs.io [abs]
- Watt, Goodenough & Wong, JURIX 2023, executable semantics for deontic, time-bound contract terms, in Maude.
  https://ebooks.iospress.nl/pdf/doi/10.3233/FAIA230954 [abs]
- Legalese 2026 post on verification ("From vibes to verification").
  https://legalese.com/posts/2026-04-01-from-vibes-to-verification [abs]

**What it is.**
- A DSL for statutes and contracts with natural-language generation, transpilation to rule engines, and formal
  verification aimed at detecting contradictions and gaps.
- The verification layer is self-described as early.

**Take for v2.** Their stated goal, automated detection of contradictions and gaps in rule sets, is the statutory
analogue of case-base consistency checking. There is no precedent model to borrow, so cite it as context only.

### 5.3 Blawx, LegalRuleML

**Blawx** (J. Morris, Lexpedite).
- Sources: https://www.github.com/Lexpedite/blawx ; PROLALA 2023 paper
  https://popl23.sigplan.org/details/prolala-2023-papers/12/Blawx-User-friendly-Goal-Directed-Answer-Set-Programming-for-Rules-as-Code
  [abs]
- A block-based rules-as-code front end on **s(CASP)**, goal-directed answer-set programming in SWI-Prolog.
- s(CASP) returns a *justification tree* for each answer: the rules, facts, and absence of contrary evidence used.
  `#pred` templates render it in English.
- **Take:** s(CASP) justifications are the closest existing thing to a human-readable "certificate for a legal claim".
  v2's certificate renderer should produce the same shape (claim ← rule ← facts with quotes), with Lean doing the
  checking instead of a Prolog engine.

**LegalRuleML** (OASIS standard, 2021) [mem].
- XML for legal rules: deontic operators, defeasibility, temporal parameters, and *legal sources/authority* metadata
  (jurisdiction, authority, temporal validity of the rule versus the source).
- **Take:** borrow its vocabulary for v2's metadata fields (`authority`, `jurisdiction`, `inForce` versus `efficacy`
  time). Do not borrow the XML.

### 5.4 Law in proof assistants

- **Lean: "Correct computational law" (Microsoft Research).** Protzenko and collaborators, MSR Summit 2022 talk.
  https://www.microsoft.com/en-us/research/video/research-talk-correct-computational-law-and-civil-procedure-with-the-lean-proof-assistant/
  [abs]
  - Formalised French tax and benefits and Washington State legal financial obligations, and found bugs.
  - Used Lean to show a path through **US federal civil pleading** that meets the main procedural requirements.
  - This is the only Lean-on-US-law work found. It is procedure, not precedent.
- **Isabelle/HOL, LogiKEy** (Benzmüller, Fuenmayor, Lomfeld).
  https://fis.uni-bamberg.de/bitstreams/42a55a70-999e-4fb5-9062-5feae2e7552d/download [abs]
  - Value-oriented legal reasoning, with *case-based* tests on the classic wild-animal property cases (Pierson v.
    Post and similar).
  - Norms are context-dependent preferences in a shallow embedding of a logic in HOL.
  - **This is the nearest thing to precedent in a proof assistant**: a handful of cases, hand-encoded.
- **Coq.** A thesis formalising an EU regulation ontology [abs]. Nothing on precedent.
- **Methodology.** Novotná & Libal (2022) on evaluating legal formalisations: expert assessment is the right
  criterion [abs].
- **Conclusion.** No prior proof-assistant formalisation of a precedent *system* (hierarchy plus overruling plus
  holdings), and nothing at corpus scale. v1/v2 is new on both counts. That should be stated carefully in the
  write-up, as "we found no prior …", not as a claim to be first.

### 5.5 Rules as code (OECD)

**Source.** J. Mohun & A. Roberts, *Cracking the Code: Rulemaking for Humans and Machines*, OECD Working Papers on
Public Governance No. 42 (Oct 2020). https://oecd-opsi.org/publications/cracking-the-code/ [abs]

**What it says.** A machine-consumable version of certain rules should be created *alongside* the natural-language
text. Case studies: NZ Better Rules, France, Canada.

**Take for v2.** It is the framing for "Lean beside the opinion text". Note the report is about *making* rules, while
v2 *reads* existing case law: v2 is rules-as-code applied retrospectively.

### 5.6 What a "certificate" for a legal claim could look like

Prior art to borrow from:
- *Proof-carrying code* (Necula 1997) and *certifying algorithms* (McConnell, Mehlhorn, Näher & Schweitzer, *Computer
  Science Review* 5, 2011) [mem]. An untrusted producer emits a witness, and a small trusted checker verifies it. The
  checker is simpler than the producer.
- SAT-solver proof logs (DRAT/LRAT) [mem]: the solver is untrusted, the proof checker is verified.
- s(CASP) justification trees (§5.3): human-readable derivations.

Proposed v2 certificate for a treatment edge (holding H of decision B treats holding G of decision A as kind K):
1. **Text binding.** Decision id, SHA-256 of the normalised opinion text, and a character span [i, j).
   - The hash is checked outside Lean against the corpus (audit). Lean receives the quoted substring and the span.
   - Optionally Lean receives the whole opinion text for decisions in a small "certificate pack", so that
     `text.extract i j = quote` is checked by `decide` in the kernel.
2. **Opinion part.** The span lies inside a majority or plurality section, with section boundaries given as spans.
   The checked conditions are containment and section type.
3. **Lexical warrant.** The quote contains a treatment cue from the cue table for K. The table is a Lean `List String`
   per kind, e.g. overrule/overruled/overruling, recede, disapprove, abrogate.
   - It also has *no disqualifier*: not "objection … overruled", not "assignment of error … overruled", not "we
     decline to overrule", not "the dissent would overrule", not a quoted parenthetical of another court's act unless
     K is `acknowledges`.
   - Each of these is a decidable string predicate.
4. **Target binding.** The quote, or a sentence-adjacent span, contains a citation that resolves to A (reporter,
   volume, page), or case-name tokens that match A's name.
5. **Authority.** `mayOverrule court(B) court(A)` (v1), and date(A) ≤ date(B). For partial treatment, there must be an
   issue match between H and G.
6. Steps 1–5 are a `Bool` that Lean checks. Admission of an edge requires `check cert = true`, proved by
   `decide`/`native_decide` per shard.

Be honest about the trust base:
- `native_decide` trusts the compiler. Plain `decide` is kernel-only but slow on big strings, so use it on the audit
  sample.
- The hash check is outside Lean.
- What Lean guarantees is *"the reader's claim is warranted by these words, at this place, in this court's majority
  opinion"*, not that the reading is legally correct. That is still a large step beyond citators (§3.2).

---

## 6. LLM-based legal information extraction

### 6.1 Holding extraction and overruling classification

**CaseHOLD.** L. Zheng, N. Guha, B. Anderson, P. Henderson, D. E. Ho, "When does pretraining help? Assessing
self-supervised learning for law and the CaseHOLD dataset of 53,000+ legal holdings", ICAIL 2021,
doi:10.1145/3462757.3466088. arXiv:2104.08671. https://ar5iv.labs.arxiv.org/html/2104.08671 [full, results table]
- **CaseHOLD:** 53,137 multiple-choice questions. Each is a citing context with 5 candidate holding statements (the
  real one comes from the citing court's parenthetical). Macro-F1 is 0.613 for BERT and 0.695 for custom-vocabulary
  Legal-BERT.
- **Overruling task:** 2,400 sentences. Positives are attorney-labelled overruling sentences from Casetext; negatives
  are random Casetext sentences. Fewer than 1% of cases overrule another. F1 is 0.958 for BERT and 0.974 for
  Legal-BERT.
  - Note that this measures *sentence-level* "is this an overruling sentence" on clean positives. It is near the
    ceiling and says little about target resolution or partial scope.

**LegalBench.** N. Guha et al., "LegalBench: a collaboratively built benchmark for measuring legal reasoning in large
language models", NeurIPS 2023 Datasets & Benchmarks, arXiv:2308.11462. https://arxiv.org/pdf/2308.11462 [abs]
- 162 tasks.
- Includes `overruling` (the same 2,400 items; https://hazyresearch.stanford.edu/legalbench/tasks/overruling.html).
- Includes rule-recall, rule-application and interpretation tasks, and the CaseHOLD-derived holding tasks.

### 6.2 Hallucination and pitfalls

**Dahl, Magesh, Suzgun & Ho.** "Large legal fictions: profiling legal hallucinations in large language models",
*Journal of Legal Analysis* 16 (2024), doi:10.1093/jla/laae003. arXiv:2401.01301. [abs]
- Hallucination on verifiable questions about real federal cases:
  - at least 58% (published version);
  - 69–88% in the preprint, by model.
- Models often fail to correct a user's false legal premise and cannot predict their own hallucinations.
- Their task set includes questions on whether a case was overruled [mem].

**Magesh et al.** "Hallucination-free? Assessing the reliability of leading AI legal research tools" (Stanford
RegLab 2024; *JELS* 2025) [mem]. Even retrieval-grounded commercial tools hallucinated on about 17–33% of queries.

**Pitfalls seen in practice (and in v1's audits):**
- *"Overruled" that is not precedent overruling.* "Objection overruled"; "motion … overruled"; in Ohio and Texas
  practice, "the assignment of error / point of error is overruled".
  Fix: a disqualifier list in the certificate (§5.6 step 3).
- *Reporting another court's act.* "X, overruled on other grounds by Y" in a citation string. The citing court is
  *reporting* history, not acting. This is the single most common false positive.
  Fix: a separate `acknowledges` kind. It is useful as held-out evaluation, but it is not an event.
- *Dissents and concurrences* saying "the majority overrules" or "I would overrule".
  Fix: the opinion-part check.
- *Negations and hedges.* "We need not overrule", "we decline to overrule", "to the extent inconsistent, X is
  disapproved" (the last one is partial, and real).
- *Same-case history versus overruling.* Reversed, vacated or affirmed on appeal is history.
- *Jurisdiction-specific verbs.* "Recede from" (Florida), "disapprove" (California), "abrogate", "repudiate", "no
  longer good law".
- *Target hallucination.* The model names a plausible but wrong case.
  Fix: target binding by citation resolution, never by the model's free text.
- *Scope inflation.* A partial overruling read as a whole one.
  Fix: require the issue or holding to be named in the quote, or default to whole-decision only when the quote has
  no limiting language.

**Expected numbers.**
- Sentence-level express overruling: about 0.95 F1 (CaseHOLD paper).
- Full treatment extraction with target and authority: about 0.8–0.9 precision and recall (FLP, Bad Law Bot).
- Implicit or partial treatment: substantially lower, with no reliable public figure.
- Commercial citators: about a third of negative relationships missed or mislabelled (Hellyer).

---

## 7. Design recommendations for v2

### 7.1 Ranked ideas

1. **Certificate-gated admission, with the disqualifier list inside Lean** (§5.6, §6.2).
   - Each treatment edge is admitted only if Lean's decidable checker accepts it:
     - span and quote;
     - majority-part containment;
     - cue present with no disqualifier;
     - target resolved by citation;
     - `mayOverrule`.
   - This turns the most common LLM errors (objection-overruled, reported history, dissents, hallucinated targets)
     into checkable rejections. It also directly addresses the one-in-three citator error rate.
2. **Holdings as reason-model cases over per-issue factor sets** (Horty 2011; Horty & Bench-Capon 2012), with the
   **result model as the fallback** when no reason is quoted.
   - Gives decidable `permitted`, `forced` and `controls` (Prakken's a fortiori test, §1.2).
   - Prove `controls → forced` and that the result model is never stricter than the reason model.
3. **Binding sub-base per (court, date)** = holdings of `binds`-decisions, not overruled on the date (v1 machinery
   lifted to holdings).
   - The whole system is an inconsistent case base (Canavotto 2022). Constraint and consistency are defined only on
     binding sub-bases.
   - This reconciles the AI-and-law theory with v1's court hierarchy. That combination is new.
4. **Circuit split := two binding sub-bases, neither binding the other, each consistent, whose union is
   inconsistent on one issue** (statutory issues keyed by US Code subsection).
   - Theorem: a later binding SCOTUS holding on the issue makes every lower court's sub-base consistent on that issue
     ("resolves the split").
   - Validate on the Beim–Rader splits and on SCDB `certReason` = conflict.
5. **Partial overruling = removing one holding (issue node) of a decision**, as in hierarchical models (van Woerkom et
   al.; Canavotto–Horty intermediate factors).
   - Prove: removal preserves consistency (monotonicity), and other holdings' status is unchanged.
   - Default scope is the whole decision only when the certificate has no limiting language.
6. **Rule-like holdings as prioritised default/exception lists** (Catala default logic; ANGELIC acceptance
   conditions).
   - Each exception carries its source decision and date.
   - Statute abrogation and partial overruling become *deleting or overriding one clause at an effective date*.
   - Join to the US Code version record: an exception keyed to §X(y) dies when that subsection's text is rewritten,
     prospectively only.
7. **Derived "at risk" status (provable Overruling Risk).** A holding whose quoted reason cites a holding that is
   overruled on the date is `atRisk`. It is computed, never extracted, and is the formal counterpart of Westlaw's AI
   flag. Report counts of atRisk-but-unflagged holdings as a headline finding.
8. **Typed authority: binding = exclusionary, persuasive = weight only** (Mullins 2023). Add Erie (state law),
   prior-panel/en banc, unpublished, vacated, and Marks rules as in DESIGN.md. Each rule cites its doctrinal source.
9. **Severity-weighted evaluation** (Demir & Canbaz's Average Severity Error).
   - Never use a single citator as gold.
   - Report SCDB decision-level recall and precision, CRS pair-level recall, and parenthetical-acknowledgement
     agreement, all held out from the reader.
10. **Separate kinds for `history` (reversed, vacated, affirmed), `acknowledges` (reported treatment, a parenthetical)
    and `act`** (the court's own treatment). Only `act` edges are events. `acknowledges` edges are the evaluation set.
11. **Restrict factor-level modelling to pilots** (lesson of HYPO, CATO and ANGELIC: factor vocabularies are
    hand-made per domain). Run whole-corpus v2 at the holding/issue level (result-model, outcome-only consistency).
    Do full reason-model factors for:
    - SCOTUS plus a statutory pilot (e.g. one US Code title with many splits);
    - optionally the CATO trade-secret factors as a sanity check against the literature.
12. **Literate certificates rendered like s(CASP) justifications.** The claim, the rule (Lean theorem name) and the
    quoted facts appear side by side, the way Catala interleaves text and code. This is the presentation layer for
    the write-up and the audit HTML.
13. **Citation-network authority (HITS) only as a prioritiser** for which decisions get expensive holdings extraction,
    and as a contrast figure against formal binding reach.
14. **Use SCDB `lawType`/`lawSupp` plus Christiansen–Eskridge overrides** to seed and validate the statute-abrogation
    join before the corpus-wide join.
15. **Be careful with novelty claims.**
    - No prior proof-assistant model of a precedent system or of good-law status was found. LogiKEy (Isabelle) does a
      few hand-encoded property cases. MSR's Lean work covers procedure and benefits.
    - State it as "we found no prior …".

### 7.2 External datasets we can actually download for validation

| Dataset | URL | Licence | Size | Use |
|---|---|---|---|---|
| SCDB (modern + legacy, case-centred CSV) | https://scdb.la.psu.edu | Free with citation (check the site's terms) [mem] | A few MB; about 29k decisions in the legacy file [mem] | `precedentAlteration` decision-level check; `lawType`/`lawSupp` statute join; `certReason` conflicts |
| Congress.gov decisions-overruled table | https://constitution.congress.gov/resources/decisions-overruled/ | Public domain (US government) | About 240+ rows (236 in our 2016 copy) | Pair-level overruling recall; refresh past 2016 |
| CourtListener bulk: citation map, parentheticals, opinions | https://wiki.free.law/c/courtlistener/help/api/bulk-data | Free; court texts are public domain (check FLP terms per file) [mem] | Citation map: millions of edges, GB-scale; opinions: tens of GB compressed [mem] | Parentheticals as held-out acknowledgements; `depth`; cross-check of our citation graph |
| Caselaw Access Project | https://static.case.law (via https://case.law) | CC0 (restrictions lifted 2024) | About 6.5–6.7M decisions | Already our source; page and offset anchors for certificates |
| Songer CoA DB + Kuersten–Haire update | https://artsandsciences.sc.edu/poli/juri/appct.htm ; ICPSR 2086 | Free (academic) | About 20k coded cases, 1925–2002 [mem] | En banc / panel attribute check |
| CaseHOLD | https://github.com/reglab/casehold ; HF `casehold/casehold` | Check (Apache-2.0 per mem) | 53,137 items | Holding-statement extraction benchmark for our reader |
| LegalBench `overruling` | https://hazyresearch.stanford.edu/legalbench/ ; HF `nguha/legalbench` | Per-task (check) | 2,400 sentences | Sentence-level cue classifier sanity check (expect ≥ 0.95 F1) |
| LePaRD | https://github.com/rmahari/LePaRD ; HF `rmahari/LePaRD` | CC BY-NC-SA 4.0 (unverified) | Millions of pairs; 1.8M target passages | Proxy for "operative holding passage" of a decision; picks the span holdings extraction should read |
| Demir & Canbaz treatment set | https://aclanthology.org/2025.nllp-1.13/ | Check paper or repo | 239 (or 329) expert-labelled citations | Multi-label, severity-weighted treatment evaluation |
| Brace–Hall state supreme courts (1995–1998; extension 1995–2010) | https://artsandsciences.sc.edu/poli/juri/databases.htm | Free (academic) | All state high-court decisions in those years | Court table and publication checks for state systems (no treatment data) |
| Christiansen–Eskridge overrides 1967–2011 | *Texas L. Rev.* 92:1317 appendix | Article appendix (fair use for research) | About 275 overrides [mem] | Statute-abrogation join validation |

**Not downloadable or restricted:**
- Shepard's/KeyCite data, and the Hansford–Spriggs and Cape–Kastellec Shepard's-derived sets (ask the authors).
- Beim–Rader splits (check the JELS replication materials).
- Sapiro-Gheiler–Kastellec LLM CoA database (working paper; release unknown).

---

## Source list (searched or fetched in this pass)

**Precedent theory.**
- https://www.cambridge.org/core/journals/legal-theory/article/rules-and-reasons-in-the-theory-of-precedent/3B7697D8BD95470F3A814ACA72C5A2F9
- https://link.springer.com/doi/10.1007/s10506-012-9125-8
- https://webspace.science.uu.nl/~prakk101/pubs/cbrailj20.pdf
- https://ebooks.iospress.nl/pdf/doi/10.3233/FAIA220445
- https://ebooks.iospress.nl/pdf/doi/10.3233/FAIA230941
- https://webspace.science.uu.nl/~woerk003/hpc.pdf
- https://research-portal.uu.nl/en/publications/hierarchical-models-of-precedential-constraint/
- https://webspace.science.uu.nl/~woerk003/proefschriftweb.pdf
- https://springerlink.bibliotecabuap.elogim.com/content/pdf/10.1007/s10506-022-09335-6.pdf
- https://api.philpapers.org/rec/LAMDPC
- https://research-portal.uu.nl/en/publications/moddeling-reasoning-with-precedents-in-a-formal-dialoque-game/
- https://link.springer.com/article/10.1007/s10506-016-9190-5
- https://intranet.csc.liv.ac.uk/~tbc/publications/ICAIL2023_Angelic2.pdf

**Authority and citation networks.**
- https://www.cambridge.org/core/journals/political-analysis/article/network-analysis-and-the-law-measuring-the-legal-importance-of-precedents-at-the-us-supreme-court/D9B2F13BE2594E1527780AAFDD6BF164
- https://papers.ssrn.com/abstract=1419525
- https://pdf.arxiv.org/pdf/0909.1819

**Citators and treatment.**
- https://www.lexisnexis.com/en-us/support/lexis/faqs/shepards-signal-indicators.page
- https://www.thomsonreuters.com/en-us/help/drafting-assistant/westcheck/keycite-status-flags
- https://thomsonreuters.ca/en/westlaw-edge/features/keycite-overruling-risk.html
- https://scholarship.law.wm.edu/libpubs/131
- https://free.law/2025/05/01/citator/
- https://wiki.free.law/c/courtlistener/help/api/rest/v4/citations
- https://lil.law.harvard.edu/blog/2024/03/26/transitions-for-the-caselaw-access-project
- https://law.com/therecorder/2017/10/27/could-this-open-source-tool-tell-you-when-good-law-goes-bad
- https://aclanthology.org/2025.nllp-1.13/
- https://link.springer.com/article/10.1007/s10506-017-9197-6

**Datasets.**
- https://scdb.la.psu.edu/online-codebook
- https://sites.ucmerced.edu/hansford/publications/measuring-legal-change-reliability-and-validity-shepards-citations
- https://jkastellec.scholar.princeton.edu/document/166
- https://artsandsciences.sc.edu/poli/juri/KH_update_codebook.pdf
- https://jkastellec.scholar.princeton.edu/publications/appealing-large-language-model-judge-comprehensive-machine-coded-database-us-courts
- https://Law.yale.edu/sites/default/files/documents/pdf/Intellectual_Life/EvolutionofConflict.pdf
- https://artsandsciences.sc.edu/poli/juri/databases.htm

**Legal code and verification.**
- https://arxiv.org/abs/2103.03198
- https://cclaw.smu.edu.sg/about
- https://popl23.sigplan.org/details/prolala-2023-papers/12/Blawx-User-friendly-Goal-Directed-Answer-Set-Programming-for-Rules-as-Code
- https://www.microsoft.com/en-us/research/video/research-talk-correct-computational-law-and-civil-procedure-with-the-lean-proof-assistant/
- https://oecd-opsi.org/publications/cracking-the-code/

**LLM extraction.**
- https://ar5iv.labs.arxiv.org/html/2104.08671
- https://arxiv.org/pdf/2308.11462
- https://hazyresearch.stanford.edu/legalbench/tasks/overruling.html
- https://arxiv.org/abs/2401.01301v1
- https://arxiv.org/html/2311.09356v3
