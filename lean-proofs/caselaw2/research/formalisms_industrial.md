# caselaw-lean-2: industrial and legal formal-specification methodology (2026-11-12)

Scope: how industrial verification projects (AWS Cedar/Zelkova/SymCert, SampCert, LNSym; seL4, CompCert, CakeML) and
legal formalisms (Catala, Mlang, L4, Blawx/s(CASP), Logical English, OpenFisca, PolicyEngine, Dutch RegelSpraak, NZ
Better Rules) structure **spec vs checker vs implementation**, state their **trusted base**, **test against independent
oracles**, and win the trust of domain experts. It also covers the **untrusted solver + small verified checker** pattern
at data scale. It ends with ranked lessons for caselaw-lean-2.

It complements `prior_art.md` §5, which introduces Catala, L4, Blawx, LegalRuleML and the certificate idea. This file
goes deeper on methodology and does not repeat those summaries.

Source tags:
- **[fetched]** I read the full text, or substantial parts of it, in this pass.
- **[abs]** I read only the abstract or landing page.
- **[2nd]** Secondary summary only.
- **[mem]** From memory, not re-verified in this pass. Treat as unverified.

---

## 1. AWS: Cedar, SymCert, Zelkova, and Lean at AWS

### 1.1 Cedar and verification-guided development (VGD)

**Sources.**
- Disselkoen et al., "How We Built Cedar: A Verification-Guided Approach", FSE 2024 Companion. arXiv 2407.01688 [fetched].
- Cutler et al., "Cedar: A New Language for Expressive, Fast, Safe, and Analyzable Authorization", OOPSLA 2024. arXiv 2403.04651 [abs].
- The OOPSLA venue is [mem]. The arXiv page does not state it.

**Process.** VGD has three parts:
1. An executable **model** written in Lean 4, with mechanised proofs of properties about the model.
2. A production implementation in Rust, checked against the model by **differential random testing (DRT)**.
3. **Property-based testing (PBT)** for the parts the model does not cover, such as parser and formatter round-trips and
   parser safety on random bytes.

**Size (their Table 1).**

| Component | Lines |
|---|---|
| Lean model | about 1.7k (evaluator/authorizer about 0.9k, validator about 0.5k, custom sets/maps about 0.2k) |
| Lean proofs | about 5.7k |
| Rust production code | about 15.7k |
| Rust tests | about 20.5k |

- The model is roughly **an order of magnitude smaller** than the production code. It leaves out optimisations,
  diagnostics and error messages.
- All proofs and models check in about **3 minutes**.

**Proved properties.**
- forbid trumps permit;
- default deny;
- explicit allow;
- order independence of policies;
- sound policy slicing;
- termination;
- **validation soundness**: well-typed policies do not hit type errors at evaluation. The paper calls this the hardest
  proof.

**Bugs found.**
- The proofs found **4** validator bugs, including a non-termination bug that testing would probably not have found.
- DRT and PBT found **21** more bugs. Examples:
  - Rust and the model counted string length differently (bytes, code points or graphemes). The team dropped the
    feature rather than pick one.
  - Rust accepted octal IPv4 octets.
  - The model wrongly rejected `::` in IPv6 addresses.
  - The validator ignored some namespaces.
- Testing **missed** three bugs: the non-termination bug, a parser crash on malformed input, and acceptance of invalid
  JSON schemas.

**DRT mechanics.**
- Generators run under cargo-fuzz / libFuzzer.
  - **Type-directed:** schema, then entities, then policies and requests that conform to the schema.
  - **ABAC with arbitrary conditions.**
  - **RBAC.**
  - **Expressions.**
- Targets run nightly, about 6 hours each, on 4 vCPU.
- **Minimised corpora are saved per release and replayed in CI.**

**Lessons they draw.**
- Coverage alone misleads. Many random inputs exercised only error paths, so they wrote generators aimed at the core
  logic. The expression generator cut trivially-boolean literals from 35.5% to 9.7%.
- Generators that produce only well-formed inputs miss malformed-input bugs.

**Readability.**
- The models should "favor simplicity and understandability". The authorizer is a short declarative function.
- Lean's termination requirements forced custom set and map types. Their invariants live in separate theorems, so the
  model stays clean.
- The spec is public (cedar-spec) and serves as the reference semantics.

**What is not verified, by their own account.**
- The parser has no Lean model.
- Rust code outside the modelled components is covered by testing only.
- The paper says nothing about trusting the Lean toolchain, rustc, or the harness between Rust and Lean.

**Relevance.** Cedar is the closest analogue to v2: a small, readable Lean spec plus an untrusted fast implementation
(our reader and data pipeline), linked by testing. The difference is that our "implementation" is an LLM. We cannot
test it against the spec on random inputs, but we can **check each of its outputs** (§4).

### 1.2 SymCert: verified SMT-based policy analyses (FMCAD 2026)

**Source.** E. Torlak, "SymCert: Verifying SMT-Based Policy Analyses", FMCAD 2026 [fetched].

**What is verified.** A Lean framework with:
- a symbolic compiler (Cedar to SMT terms);
- a symbolic authorizer;
- a **hierarchy enforcer**, which adds well-formedness (acyclicity, transitivity) constraints so that SMT models
  correspond to legal inputs;
- a **counterexample extractor**, which turns an infinite SMT model into a finite, well-formed Cedar input.

**What is trusted.** The `solve` function, that is, the SMT solver (cvc5) and the term encoding. Their architecture
figure colours verified parts green and trusted parts grey. The soundness and completeness theorems are stated
**"assuming the trusted solve function is correct"**.

**Proof architecture lesson.**
- A first attempt in Dafny, a direct induction on compiler correctness, took about **8,000 lines for a subset**. It was
  fragile and its lemmas could not be reused.
- The fix was to factor correctness into two general properties:
  - *reducibility*: the compiler partially evaluates literal inputs;
  - *interpretability*: compilation commutes with SMT evaluation.
- Every term is built through small factory functions, each proved once. The top-level compiler-correctness theorem is
  then about 4 lines.
- Results:
  - Five production analyses were modelled and proved in **one work day** (about 550 lines).
  - Language extensions cost **4 to 8 days** each.
  - Overall: about 2.2k lines of model and about 21.7k lines of proof, about 500 person-hours. Proof-to-model is about
    10:1, which is consistent with Cedar.
- The Lean models were fast enough that service developers prototyped on them. They then ported the models to Rust for
  production and kept the Lean as the DRT oracle.

**Relevance to v2.**
- (a) **Factor proofs through generic lemmas.** For example, prove "status is a fold over events" and "the fold commutes
  with same-day reordering" once. Then each new treatment kind is a small obligation, not a new induction. Expect the
  doctrine to change, just as Cedar's language changes by RFC.
- (b) The **counterexample direction matters for completeness.** When the checker rejects, v2 should emit a concrete,
  typed reason, the analogue of `cex`, not just `false`.
- (c) The well-formedness enforcer corresponds to our court-table invariants: succession is acyclic and epochs do not
  overlap. These should be checked properties of the data, not assumptions.

### 1.3 Zelkova (IAM policies, SMT)

**Sources.**
- Backes et al., "Semantic-based Automated Reasoning for AWS Access Policies using SMT", FMCAD 2018 [mem].
- Rungta, "A Billion SMT Queries a Day", CAV 2022 [mem]. The scale is confirmed in SymCert's related work [fetched].

**Facts.**
- Zelkova compiles IAM policies to SMT (strings, regexes, bitvectors). It answers questions such as "can anyone outside
  my account reach this bucket?"
- It runs about a billion times a day.
- SymCert notes its encoding is **sound but not complete**, and is not formally verified.

**Practices [mem, unverified].**
- A portfolio of solvers.
- Regression corpora replayed on every solver upgrade.
- Results reported as *findings* that a human resolves.
- Abstraction is used to make the analysis tractable.

**Relevance.** It is an industrial precedent for **three-valued answers**: proved, refuted with a witness, or unknown.
It is also an example of being explicit that a sound-but-incomplete analysis means "no finding" is not "no problem". For
v2: *no admitted negative treatment* is not the same as *good law*.

### 1.4 SampCert and LNSym

**SampCert** (de Medeiros, Tristan et al., "Verified Foundations for Differential Privacy", PLDI 2025) [abs].
- A Lean library with a generic DP framework and verified Laplace and Gaussian samplers. It has over 12k lines of
  proof.
- It is used in AWS Clean Rooms.
- Lesson: they verified the *sampling code itself*, not an idealised source of randomness. That is, verify the
  component everyone else assumes.
- Whether the production code is extracted from Lean or ported is [mem, unverified].

**LNSym** (AWS): an Armv8 native-code symbolic simulator in Lean, for verifying cryptographic assembly [mem].
- Its relevance here is the tactic it drove into core Lean: **`bv_decide`** (Lean 4.12, Oct 2024) [fetched release
  notes and docs].
  - Bitvector goals are bit-blasted to an AIG and then to CNF.
  - The **untrusted** CaDiCaL solver (bundled with Lean) returns an **LRAT** proof.
  - The proof is checked by an **LRAT checker proved sound in Lean**. The checker came from Josh Clune's AWS
    internship; Henrik Boving at the Lean FRO did the bit-blaster [2nd: de Moura, CADE 2025 slides].
- **`bv_check`** replays an LRAT file stored on disk without calling a solver. That is the "certificate shipped with
  the data" workflow.
- The docs state the trust cost plainly: proofs use the reduce-Bool axiom, so **the Lean compiler joins the trusted
  base**.

---

## 2. seL4, CompCert, CakeML: refinement and the trusted base

### 2.1 seL4

**Sources.**
- Klein et al., SOSP 2009 [mem].
- seL4 "proof assumptions" page [fetched].

**Layering [mem].**
- **Abstract specification** (Isabelle/HOL, nondeterministic, says *what*).
- **Executable specification**, generated from a **Haskell prototype** the OS developers wrote and could run against a
  simulator.
- **C implementation**, imported into Isabelle by a C parser.
- **Binary**: Sewell et al. (PLDI 2013) translation-validate gcc output against the C semantics using SONOLAR/Z3 plus
  Isabelle and HOL4. This removes the compiler from the trusted base on supported platforms [fetched].

**Effort [mem].**
- The original proof was about 8.7k lines of C and about 200k lines of Isabelle.
- It took on the order of 20 person-years including tool building.
- **Most of the effort went into invariants**, not into the refinement steps themselves.

**How the assumptions are reported** [fetched]. A short public page lists each assumption in plain prose:
- about 340 lines of hand-reviewed assembly;
- the hardware behaves as its formal model says;
- cache, TLB and cache-colouring management are correct;
- boot code (about 1,200 lines) is outside the proof;
- no unverified DMA;
- timing channels are out of scope for the confidentiality proof;
- the compiler and linker are trusted *only* on platforms without binary verification;
- HOL is consistent and the prover checks correctly.

It ranks these as more and less likely to fail. It also flags one honest subtlety: for virtual memory, the
**completeness of the stated conditions depends on human checking**, not on the proof.

**Relevance.**
- seL4's three levels map onto v2:
  - **Spec**: precedent doctrine as Props;
  - **executable checker**: decidable Bool functions;
  - **data/pipeline**: untrusted.
- The Haskell prototype is the counterpart of our *runnable* Lean model, which lawyers and engineers can query before
  anything is proved.
- The assumptions page is the reporting model to copy.

### 2.2 CompCert

**Sources.**
- CompCert manual, ch. 1 [fetched].
- Leroy CACM 2009; Rideau & Leroy 2010; Yang et al., Csmith, PLDI 2011 [mem].

**What is guaranteed.** Semantic preservation: if compilation succeeds, the compiled code's observable behaviour is one
of the source program's allowed behaviours. The manual says about 90% of the compiler, including all optimisations, is
proved in Rocq/Coq.

**What is not verified.**
- preprocessing;
- elaboration and type-checking (only the parser is proved);
- assembling and linking (AbsInt's Valex offers a-posteriori validation);
- [mem] Coq extraction and the OCaml runtime.

**Verified validators [mem].** Several passes, notably register allocation, are done by **untrusted OCaml heuristics
whose output is checked by a Coq-verified validator**. If validation fails, compilation fails. This is exactly the
certificate-checker pattern, used *inside* a verified compiler, because proving the heuristic correct would be harder
than checking its answer.

**Csmith result [mem, widely cited].** Random differential testing of C compilers found many bugs in gcc and LLVM. In
CompCert it found bugs only in the **unverified front end**, and none in the verified middle end.

**Lesson.** Bugs concentrate exactly at the edge of the trusted base. For v2 that edge is the TSV parser, text
normalisation, offset arithmetic and hashing.

### 2.3 CakeML and verified checkers

**Sources.**
- CakeML (HOL4) [mem].
- cake_lpr: Tan, Heule & Myreen, TACAS 2021 and STTT 2023 [abs].
- SAT Competition checker docs [abs].

**CakeML [mem].**
- A verified ML compiler, bootstrapped *inside the logic*, so the compiler binary itself is verified.
- Proof-producing translation from HOL functions to CakeML.

**cake_lpr [abs].**
- An LRAT/LPR proof checker built on CakeML and **verified down to x64 machine code**.
- It checks the **SAT Competition**'s UNSAT proofs; it was first used for this in 2020.
- It is the standard example of a *small verified checker auditing an untrusted, highly optimised producer*.
- The STTT version adds a compositional format for **parallel** checking of split proofs.

**Empty hexagon (ITP 2024; Subercaseaux, Nawrocki, Gallicchio, Codel, Carneiro, Heule) [abs/2nd].** The proof that 30
points in general position always contain an empty convex hexagon has two halves:
- **the encoding is verified in Lean** (a geometric statement holds if and only if a CNF formula is UNSAT, including
  symmetry breaking);
- the UNSAT result comes from CaDiCaL (about 17k CPU hours) and is checked by **cake_lpr**.

Proving the encoding correct and checking the answer are separate jobs, and both are needed.

---

## 3. Legal formalisms in depth

### 3.1 Catala

**Sources.**
- Merigoux, Chataing & Protzenko, ICFP 2021, arXiv 2103.03198 [fetched].
- Goutagny, Fromherz & Monat, CUTECat, arXiv 2410.18212 [abs].
- Cnaf press release of 8 June 2026 [fetched].
- Pantheon-Sorbonne interview [fetched].

**Default calculus [fetched].** A default term has a list of exceptions, a justification, and a consequence. Its
semantics:
1. Every exception is evaluated.
2. If **two or more** apply, a **conflict error** is raised. This is fatal and aborts.
3. If exactly one applies, its value is the result.
4. If none applies and the justification is true, the result is the consequence.
5. Otherwise the result is an **empty** value. An empty value can be caught by an enclosing default, so the next level
   up can supply a value.

**Labels.**
- Each definition and exception carries a label.
- Each exception names the label it overrides, so exceptions to exceptions form a priority **tree**.
- Several unlabelled definitions of one variable are read as mutually exclusive exceptions with no base case.
- Conflict and empty errors point to the source locations of the competing definitions.
- The compilation from the scope language to the default calculus and on to a lambda calculus is proved in F*.

The logic follows Lawsky's prioritised default logic for statutes [mem].

**Process.**
- The paper recommends **pair programming**: a Catala expert transcribes while a legal expert reads and explains. Their
  lawyer collaboration ran as four 2-hour sessions [2nd: search snippet of the paper].
- The interview states the rule as "nothing is coded without the legal expert's approval".
- The interpreter logs each step of a hand-written test case, so a lawyer can follow the execution.
- The **literate** layout puts each article's text directly above its code.
- Unclear provisions are flagged with notes and sources rather than silently resolved.

**Testing against independent implementations [fetched].**
- French family benefits were compared with the official simulator mes-droits-sociaux.gouv.fr. There were no
  mismatches, but one case was missing: a child in the custody of social services was not in the official simulator,
  so it could not be compared.
- Reading the **OpenFisca** code found a real discrepancy. Article L755-12 of the Social Security Code says the income
  cap does not apply to one-child families overseas. OpenFisca missed it and fixed it after the report.
- So differential comparison found an error in the *oracle*, not in Catala. Any oracle comparison needs two-way triage.

**Scale and effort.**
- The French housing-benefit (aides logement) code was replicated in about **1.5 to 2 person-months** [2nd: Merigoux
  slides]. The production engine it mirrors is Cnaf's CRISTAL/Oracle system.
- **CUTECat** runs concolic (concrete plus SMT) testing over default logic. It generated hundreds of thousands of tests
  covering every branch of the housing-benefit code and of US IRC §132, with heuristics to keep the tests readable for
  lawyers [abs].

**Adoption.**
- On 8 June 2026 **Cnaf** (the family-allowance fund, which pays about EUR 110 bn a year to 13.6 m households) announced
  a partnership with Inria, after an evaluation that began in 2024. It chose Catala as a **foundation technology** for
  future calculation engines [fetched].
- The release does **not** say Catala is in production yet.
- I found no primary source for DGFiP running Catala in production. The DGFiP work I could verify is **Mlang** (§3.2).
  Treat "Catala at DGFiP" as **unverified**.

**Dates [mem, via a 2026 citing paper].** Monat, Fromherz & Merigoux, ESOP 2024, formalised legal **date arithmetic**
and statically detected its ambiguities. For example, "date + 1 month" from 31 January has no single answer, and the
rounding direction matters. This is relevant to v2's yyyymmdd integers and to `0 = unknown`.

### 3.2 Mlang: the DGFiP legacy tax engine

**Sources.**
- Merigoux, Monat & Protzenko, "A Modern Compiler for the French Tax Code", CC 2021, arXiv 2011.07966 [abs].
- Merigoux's thesis (HAL 02320347) [abs].

**The legacy system.** The DGFiP income-tax engine is about 100k lines of a 1990 DSL called **M**, plus handwritten C
workarounds.

**What Mlang did.**
- Reverse-engineered a formal semantics of M.
- Built a compiler on that semantics, removing the C workarounds and emitting Python and other targets.
- **Validated it against DGFiP's private test suite.**
- The DGFiP announced it was "officially transitioning to Mlang" for production.
- [mem] They also used fuzzing to grow the test set beyond the official cases.

A third-party fork notes a limit: passing the tests shows the compiler is faithful to M. It does not show that M is
faithful to the law.

**Lesson.** Separate *implementation fidelity* (does our checker compute what our spec says?) from *legal fidelity*
(does our spec say what the law says?). They need different evidence: tests and proofs for the first, lawyer review and
external oracles for the second.

### 3.3 L4 / Legalese

**Source.** legalese.com, "From vibes to verification", April 2026 [fetched]; see also prior_art §5.2.

**What it is now.**
- A DSL that reads like the legal text, with GIVEN / DECIDE clauses.
- `#EVAL`, `#CHECK` and `#ASSERT` directives act as "unit tests for legislation". They return a yes/no answer with a
  trace of the conditions that held.
- Rules are deployed as REST and MCP endpoints, so AI agents *execute* the rules instead of interpreting them.
- LLMs draft L4 from English and humans audit the result.
- Formal verification for contradictions and gaps is still "in active development".

**Lesson.** Here the LLM writes the formalisation, with no checker. v2 inverts this: the LLM *reads* and Lean *checks*
each claim. That is the safer direction.

### 3.4 Blawx and s(CASP); Logical English

**Sources.**
- Morris, PROLALA 2023 [abs].
- Morris, "Using OpenFisca to Power Expert Systems in the Canadian Public Service" (2022) [fetched].
- Logical English: Kowalski & Datoo, AI & Law 2022 [mem]; Sartor et al., ICLP 2023 and CEUR 3437 [abs].

**Blawx.**
- Blockly blocks over **s(CASP)**, a goal-directed answer-set programming system with negation as failure.
- Each answer comes with a **justification tree**, rendered in English through `#pred` templates.
- A CEUR paper reports significant use inside the Canadian federal government [abs].

**Morris's OpenFisca lessons** [fetched]. From encoding the Old Age Security Act:
- OpenFisca **fills missing inputs with defaults**: 0, false, "", or 1 Jan 1970. It therefore cannot tell *zero* from
  *unknown*. Workaround "_known" shadow variables made the code complex and bug-prone.
- The imperative formulas cannot reason backward from a conclusion. "Can X ever happen?" could only be explored by
  sampling, never proved impossible.
- The code was about 4 times longer than a declarative encoding, and opaque to policy experts.
- Explanations had to be rebuilt from execution traces.
- Morris concludes that declarative encodings that mirror the structure of the source are easier for subject experts to
  verify.

**Logical English (LE).**
- A controlled natural language meant to be readable by English speakers without training. It compiles to Prolog and
  s(CASP).
- It has been used on the Italy–France double-taxation convention, using the s(CASP) explanation module [abs].
- LE2 narrows the language to its robust core [abs].

**Lesson.**
- Explanations as *derivation trees in the domain's own words* are what lawyers trust.
- Do not let "unknown" collapse into a default value.

### 3.5 OpenFisca and PolicyEngine: tests as legal fixtures

**OpenFisca** [mem].
- Parameters are YAML files with dated values and a **reference** (a legal citation or URL) per value.
- Formulas are Python and vectorised.
- **YAML tests** fix a period, inputs and expected outputs. They are often transcribed from official worked examples
  or simulators.
- This is the "test suite as legal fixture" pattern: each test is a small, citable, dated legal fact that a lawyer can
  read.

**PolicyEngine-US** [abs].
- Contributor rules require reference, publication date and effective dates in parameter metadata.
- YAML tests are run by `policyengine-core test`.
- It has been **cross-validated against NBER TAXSIM** on thousands of CPS households since 2021, with a
  policyengine-taxsim emulator.
- A 2024 Manifold market on fully matching TAXSIM35 resolved NO. Agreement between independent calculators is hard,
  and the residual disagreements are where the interesting legal questions are.
- PSL Tax-Calculator keeps a similar TAXSIM35 validation folder.

**Lesson.**
- An independent oracle is valuable even when imperfect.
- Publish the disagreement table and classify each disagreement.

### 3.6 Government rules-as-code: Netherlands and New Zealand

**Netherlands (Belastingdienst)** [abs: BRCommunity, HAN CNL 2021, UvA assessment, JetBrains case study].
- **RegelSpraak** is a controlled natural language based on RuleSpeak.
- **ALEF** is the toolchain (built on JetBrains MPS) that compiles it to FICO Blaze rules running on the mainframe.
- About 2,300 to 3,000 rules were migrated from Excel. The sources disagree on the count.
- Domain experts edit, refactor and test the rules directly.
- An expert review found it adequate for what was tested, but could not say whether it can express *all* tax law.
- There is no authoritative public reference for the language yet. The tax office wants a standard independent of its
  own implementation.
- [mem] **Wetsanalyse** (the JRM legal-analysis method) is a separate, upstream step: the law text is annotated with
  typed juridical classes (legal subject, legal fact, condition, derivation rule, and so on) *before* anyone writes
  rules. That keeps a traceable link from every rule to the words it came from.
- [mem] The Belastingdienst also models tax law with **deep, layered exception structures**, as Catala does.

**New Zealand (Better Rules, 2018 onward)** [mem; OECD "Cracking the Code" in prior_art §5.5].
- Multidisciplinary teams of policy, legal, service-design and dev people co-drafted *concept models and decision trees
  before code*.
- They prototyped with OpenFisca (for example the Rates Rebate).
- The main lesson reported: the value was in the **shared model forcing ambiguities to the surface early**, not in the
  code.

**What made these trusted by lawyers (synthesis).**
1. Text and rule side by side, with a link from every rule to its source words: Catala literate files, Wetsanalyse
   annotations, OpenFisca references.
2. Lawyers sign off rule by rule, in pair or group sessions.
3. Explanations as derivations in domain vocabulary: s(CASP), LE, L4 traces, Catala logs.
4. Ambiguity is flagged and sourced, never silently resolved.
5. Worked examples become permanent regression tests that lawyers can read.
6. Independent oracles, with discrepancies triaged in both directions.
7. Open source.

---

## 4. Certificate checking at data scale

**The pattern** (Necula's proof-carrying code; certifying algorithms; DRAT/LRAT): an **untrusted, optimised producer**
emits a **witness**, and a **small, verified checker** accepts or rejects it. Soundness rests only on the checker and
the spec it is proved against. A wrong producer costs completeness, never soundness.

**Instances.**

| Instance | Producer (untrusted) | Witness | Checker (trusted or verified) | Notes |
|---|---|---|---|---|
| SAT Competition | any SAT solver | DRAT, converted to LRAT | cake_lpr (verified to x64) | parallel and compositional checking for huge proofs |
| Lean `bv_decide` / `bv_check` | CaDiCaL | LRAT, can be stored on disk | LRAT checker proved in Lean | trusts the Lean compiler (native evaluation) |
| CompCert register allocation [mem] | OCaml heuristic | the allocation | Coq-verified validator | failed validation means compile error |
| Empty hexagon | CaDiCaL (17k CPU h) | LRAT | cake_lpr, *plus* the encoding verified in Lean | verifying the encoding and checking the answer are both needed |
| Equational Theories Project (Tao et al., 2024–25) [2nd] | Vampire, Mace4, humans, scripts | Lean proof terms or finite counter-models | Lean kernel, lean4checker | about 22 m implications; only a generating set of about 10.7k positive and about 587k negative results was formalised, with **transitivity and duality closure done by external programs**, which are outside the kernel |
| q-ary covering codes (2026) [abs] | search code | "proof-carrying database" of bound traces | Lean replay of each trace | the database itself carries its proofs |
| SymCert | cvc5 | SMT model, or UNSAT | the extractor is verified; the UNSAT answer is **trusted** | one-sided: a counterexample is checked, a "proof" is trusted |

**Lean specifics** [2nd: Lean Zulip and papers].
- `decide` / `decide +kernel` evaluates in the kernel: no extra axioms, but slow on large strings and lists.
- `native_decide` compiles the check and trusts the compiler.
  - Historically this showed up as `Lean.ofReduceBool` and `Lean.trustCompiler` in `#print axioms`.
  - A **Feb 2026 change (lean4#12217)** replaces this with a generated axiom per use, so axiom *names* in reports
    depend on the Lean version.
- Mathlib discourages `native_decide`; a linter has been proposed. Practice in recent papers is to state the trust cost
  per theorem. One game-theory paper reports 145 of 2,627 theorems needing `native_decide`.
- `lean4checker` re-checks compiled `.olean` environments independently.

**Applied to v2 (our reader is the producer).** The SCHEMA already makes the reader emit CERT columns. Three gaps
against the pattern:
1. **The checker's correctness theorem is missing.** The pattern needs `checkCert c = true → Warranted c`, where
   `Warranted` is a *Prop in the spec layer*. For example: a quote occurs at the given offsets; the span lies in a
   majority part; it contains a cue of kind K with no disqualifier in the window; the target is resolved. Then the
   checker is a decision procedure for a stated property, not just a filter. A `Decidable` instance gives both
   directions for free.
2. **Steps outside Lean.**
   - The SHA check and the normalisation function are the analogue of the ETP's external closure scripts.
   - Either move them in, with a pure-Lean SHA over the *window* checked by `decide` on the audit sample, or list them
     in the trusted base.
3. **One-sidedness**, as in SymCert.
   - An *admitted* edge has a checked witness.
   - A *missing* edge has none. "No overruling found" is a statement about the reader's recall, not a theorem.
   - Status should therefore be three-valued per (holding, date): `negativeAdmitted`, `noAdmittedNegative`,
     `unknown`.

---

## 5. Lessons for caselaw-lean-2 (ranked)

### 1. Make the checker a proved decision procedure for a readable spec (layering)

Adopt the seL4/Cedar three-layer split, with an explicit proof link between the top two layers:

**Spec** (`CaseLaw2/Spec/*.lean`)
- Small, declarative, `Prop`-valued inductive relations: `Binds c d t`, `MayOverrule`, `Warranted cert`,
  `GoodLawOn h t`, `Split q t`.
- No performance concerns.
- Each constructor has a docstring with the doctrine.md rule id and its S/L/U tag.
- Target: Cedar-scale, a few hundred to about 2k lines. Most of the bulk belongs in proofs, not the spec.

**Exec** (`CaseLaw2/Exec/*.lean`)
- `Bool` functions over arrays and hash maps: `force`, `status`, `checkCert`, the split finder.
- Proved `exec = true ↔ spec` and packaged as `Decidable` instances.
- The corpus theorems are `decide`/`native_decide` facts about Exec, which the bridge theorem turns into Spec facts.

**Data/reader**
- Fully untrusted. Every admitted fact is either a checked certificate or a tagged parameter row.

**Proof factoring.** Use SymCert's strategy:
- Prove generic lemmas once: status is a left fold over events; same-day events commute; partial overruling removes
  only the named issues; prospective events do not touch conduct before their effective date.
- Then a new treatment kind or a new system rule costs days, not a rewrite.
- Avoid one monolithic induction. That is the Dafny failure mode SymCert reports.

### 2. Certificate-gated admission, with the soundness theorem and the counterexample side

- Every treatment and history edge is admitted only via `checkCert`.
- Prove `checkCert_sound : checkCert c = true → Warranted c`.
- Make the checker return a **typed rejection reason**, not `false`: `quoteMismatch`, `notMajority`, `cueAbsent`,
  `disqualifier "objection"`, `targetUnresolved`, `noAuthority`. Rejection histograms are a headline result, the
  analogue of SymCert's counterexample extractor.
- Ship certificates as files next to the data, so anyone can re-check without the reader, as `bv_check` replays LRAT.
- Shard the checking (the cake_lpr compositional idea). Each shard's theorem is independent, and a top-level theorem
  only conjoins them.
- Keep the honesty line already in prior_art §5.6. A passing certificate proves *the words support the claim at this
  place in this court's majority opinion*, not that the legal reading is right.

### 3. Write down the trusted base and report it like seL4

Publish a `TRUST.md` and a matching section in the HTML report. List each item, how likely it is to fail, and how it
is mitigated:

| Item | Mitigation |
|---|---|
| Lean kernel | `lean4checker` re-check |
| Lean compiler (only for `native_decide` theorems) | re-prove a stratified random sample with `decide +kernel`; list per theorem which mode was used |
| TSV parsing, Unicode normalisation, offset arithmetic | **CompCert/Csmith lesson: bugs live here.** Add parse/print round-trip tests and fuzzing as in Cedar, and keep the parser tiny |
| SHA and audit-copy consistency | outside Lean unless moved in |
| Doctrine parameter tables | the analogue of seL4's hardware model: each row carries S/L/U, and theorems quantify over any table satisfying named well-formedness props (succession acyclic, epochs disjoint, adoption dates consistent), instantiated to ours |
| Court and decision metadata from CAP/CourtListener | (no mitigation stated) |

Rules for the Lean side:
- Doctrine must **not** be encoded as Lean `axiom`s. Make it **structure fields or hypotheses**, so that
  `#print axioms` stays at {propext, Classical.choice, Quot.sound} plus the compiler axiom where stated.
- Print the `#print axioms` output for every headline theorem in the report. Note the Lean version, since the axiom
  names changed in Feb 2026.

### 4. Differential testing against independent oracles, with two-way triage

- Run the Lean Exec layer as the **oracle for the Python/TSV pipeline**, Cedar-style. Generate random court tables and
  event sequences, and compare Python's derived status columns with Lean's `status`, nightly or per build. This catches
  pipeline bugs before Lean even runs.
- Keep the external gold strictly held out, as SCHEMA already says: later-court notes, SCDB `precedentAlteration`,
  the CRS/Congress.gov table of overruled decisions, Christiansen–Eskridge and Hasen.
- Score against **each oracle separately**.
- **Triage every disagreement into one of:** reader wrong / checker too strict / oracle wrong / genuinely ambiguous.
  Catala's comparison found a bug in OpenFisca, not in Catala, and PolicyEngine and TAXSIM still disagree after years.
  Expect SCDB and editorial notes to be wrong sometimes, and publish the table.
- Follow Cedar's generator lessons. Coverage is not enough, so build **adversarial generators and seeds** for the known
  failure modes:
  - "objection ... overruled";
  - "we decline to overrule";
  - dissent text;
  - parentheticals reporting another court's act;
  - en banc versus panel;
  - same-case reversal versus overruling.
- Keep the **minimised failing cases as a permanent regression corpus** (`gold/regress/`), replayed on every reader or
  checker change.
- Treat the two models (gpt-5.4-mini and gpt-6-sol) as **N-version producers** only, never as an oracle for each other.
  Their errors are correlated.
- Validate parameter tables against doctrine.md's [S] rows using legal-fixture YAML/TSV tests, OpenFisca-style. Each
  test is a dated, cited fact such as "on 1981-10-01 the 11th Cir. is bound by 5th Cir. decisions before 1981-09-30".

### 5. Use Catala's default calculus for rules with exceptions, and make "conflict" a finding

- Encode authority and Marks as **labelled default trees**.
- Each node carries its source (doctrine rule id or decision), date range and tag.
- Semantics as in Catala, with one deliberate change: **a conflict returns `Finset` of the competing answers plus a
  `conflict` marker instead of aborting.** This matches doctrine.md §9 item 24, where the result is a set of
  permissible holdings. In doctrine, a conflict is data: a split, or a choice-of-law rule that is itself missing.

Sketches:

```
force(src, issue, dst, t):
  default: persuasive
  ├─ exception [vertical]  same system, higher court, issue in its domain   → binding
  │    └─ exception [unpub]  src unpublished ∧ unpubForce(...) < binding   → unpubForce
  ├─ exception [scotusFed] src = SCOTUS ∧ issue federal                     → binding
  ├─ exception [erie]      dst federal ∧ issue = stateLaw s ∧ src = s's court of last resort → binding
  │    └─ (no exception: a state intermediate court's view is persuasiveStrong, as "data", not binding)
  └─ exception [vacated]   src vacated before t                             → none     (overrides all; label priority)

holdingOf(plurality decision, issue):
  default: none (no majority holding)
  └─ exception [marks]  curated marksHolding exists                        → narrowest-ground proposition
       └─ exception [marksNoCommonDenominator] the circuit holds Marks inapplicable → none (court-relative)
```

- Generate tests over **every branch** of each tree, CUTECat-style, and render them for a lawyer to review. This is
  where the "unknown" and "conflict" leaves surface.
- **Dates.** SCHEMA's `0 = unknown` is the OpenFisca default trap (Morris). In Lean, lift it to
  `Option Date` / `DatePrecision` at parse time and never compare a raw 0. Following Monat et al. (ESOP 2024), make
  every date comparison on month- or year-precision dates return `unknown` when the precision cannot decide it.

### 6. Make it readable for lawyers through the rendered layer, not the Lean source

- **Literate spec.** Each Spec constructor or default-tree node is rendered in HTML next to:
  - the doctrine.md paragraph it encodes;
  - its sources;
  - its S/L/U tag;
  - a one-sentence plain-English statement.

  This is Catala's article-above-code layout, generated from docstrings.
- **Justification trees for every admitted fact and every status verdict**, s(CASP)/LE-style, with `#pred`-like
  English templates:

  > *Holding H of X is not good law in the 9th Cir. on 2015-03-01 because: Y (9th Cir. en banc, 2012) overruled it
  > ("we overrule X to the extent ...", majority part, chars 18,204–18,262); an en banc court may overrule a panel
  > (rule 1.2.3 [S]).*

- **Lawyer review sessions on the rendered spec**, as Catala's pair programming did. Track sign-off per node. Show the
  branch-coverage tests from lesson 5 as worked examples.
- Keep the Spec short and declarative (Cedar). Put efficiency only in Exec.

### 7. Report assumptions and claims honestly, in fixed categories

Every headline claim in the report is labelled with exactly one of:
- **proved** (kernel only);
- **proved by computation** (trusts the compiler);
- **checked by certificate** (states what the certificate does and does not establish);
- **tested** (DRT or oracle agreement with numbers);
- **assumed** (a parameter row; tag S/L, never U as a premise).

Further rules:
- Add a seL4-style plain-prose assumptions list, including the subtle ones:
  - the parameter tables may be *incomplete*, and only humans can check completeness, as seL4 says about its
    virtual-memory conditions;
  - reader recall bounds every "no negative treatment" statement.
- Separate **implementation fidelity** (proved or tested) from **legal fidelity** (lawyer review plus oracles), as the
  Mlang caveat shows.
- Phrase novelty as "we found no prior ...".

### 8. Smaller items

- Make the runnable Lean model a **queryable tool before proofs are finished**, as seL4's Haskell prototype and
  SymCert's prototyping use were. Lawyers and the eval agent can poke it early.
- Version the doctrine like Cedar RFCs. A change to a parameter table or rule is a reviewed PR with its proof deltas.
  Measure the cost per change to check that the proof factoring is working.
- Prove the encoding *and* check the answers, as in the empty-hexagon work. For example, prove that the TSV-to-Lean
  import preserves the meaning of rows (a round-trip theorem on the parser model), not only that the imported facts
  check.

---

## Sources

**Fetched**
- arXiv 2407.01688 (How We Built Cedar, FSE'24 Companion)
- SymCert FMCAD 2026 PDF (cdn.amazon.science)
- seL4 proof-assumptions page (sel4.systems/Verification/assumptions.html)
- CompCert manual ch. 1 (compcert.org/man/manual001.html)
- arXiv 2103.03198 (Catala, ICFP'21) full text
- Cnaf/Inria press release, 8 June 2026 (caf.fr)
- Pantheon-Sorbonne observatory interview with Merigoux and Huttner
- Morris, "Using OpenFisca to Power Expert Systems ..." (gauntlet173.github.io, 2022)
- Legalese, "From vibes to verification" (2026)

**Abstract, landing page or snippet**
- arXiv 2403.04651 (Cedar)
- arXiv 2412.01671 (SampCert, PLDI'25)
- Lean 4.12.0 release notes and BVDecide API docs
- cake_lpr (TACAS'21, STTT'23; cakeml.org/checkers.html)
- arXiv 2403.17370 (empty hexagon, ITP'24)
- arXiv 2011.07966 (Mlang, CC'21)
- arXiv 2410.18212 (CUTECat)
- PolicyEngine-TAXSIM pages
- RegelSpraak/ALEF sources (BRCommunity, HAN, UvA, JetBrains case study)
- Logical English / s(CASP) (CEUR 3193, 3437; ICLP 2023)
- Blawx (PROLALA 2023)
- arXiv 2606.09600 (q-ary covering codes)
- Lean Zulip threads on native_decide and lean4#12217
- arXiv 2607.23500 (flag algebras)
- arXiv 2607.08692 (card-game case study)

**Secondary**
- Equational Theories Project summaries
- de Moura CADE 2025 slides (via search snippet)
- Merigoux slides on aides logement effort

**Memory, unverified this pass**
- Zelkova (FMCAD'18) and "A billion SMT queries a day" (CAV'22) practices
- LNSym details
- seL4 effort figures and Haskell executable spec
- CompCert verified validators and the Csmith result
- CakeML bootstrapping
- OpenFisca YAML conventions
- Wetsanalyse/JRM
- NZ Better Rules
- Monat–Fromherz–Merigoux ESOP 2024
- Lawsky's default logic
- Catala at DGFiP (not found)
