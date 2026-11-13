# caselaw-lean-2: lessons from "Formalizing CPython" and comparable large formalisms (2026-11-12)

Target: David Andrews and Chao Zhang, *Formalizing CPython: A Lean Model of CPython 3.15.2*,
write-up at broyojo.com/python-formalization (dated 10 Nov 2026, corrected the same day), code at
github.com/Broyojo/python-formalization (page numbers are from commit 344c8e06; I read a shallow
clone of HEAD 7d5a5ed, 10 Nov 2026). This is the project that inspired our "Formalizing the US tax
code" experiment.

Method for this note: I read the whole write-up, the README, `AGENTS.md`, `CONTRIBUTING.md`,
`coverage/REVIEW_PROMPT.md`, `lean/Audit.lean`, `lean/DiffMain.lean`, `lean/PyLean/{Core,Registry,DiffCore}.lean`,
`difftest/common.py`, `scripts/check_coverage.py`, `sky/*`, `reports/{LAUNCH,x_post,discourse_post,prelaunch_review}.md`,
sample inventory, review and bug files, and counted things in the clone. Discussion: the Hacker News
thread (item 50435105, 135 points, 56 comments, 10 Nov 2026), the discuss.python.org thread the
authors opened, and the julia-in-lean Discourse post it builds on. Tags: **[verified]** read in a
primary source this pass; **[summary]** taken from a fetched-page summary, not read line by line;
**[unverified]** from memory or a fragment, not checked this pass.

---

## Part A. Formalizing CPython in depth

### A1. What exactly was formalised

- **Not a language semantics.** Not the language reference, and not a whole-interpreter operational
  semantics. It is a **function-by-function mirror of CPython 3.15.2's source**: C functions, bytecode
  instructions (`Python/bytecodes.c`), PEG grammar rules (`Grammar/python.gram`) and pure-Python
  standard-library functions. Each Lean function copies one source function "line by line": same branch
  order, check order, error messages and integer overflow. Each step cites file and line in the pinned
  source. [verified]
- **Proof assistant:** Lean 4 (toolchain 4.35.0), no Mathlib dependency visible in the lakefile. [verified]
- **Inventory and scope:**
  - Every function, opcode and grammar rule is a row in `coverage/methods/<file>.tsv` (1,052 files).
    Columns: file, line, endline, name, signature, status, entry, note.
  - The denominator is 28,393 functions "worth checking"; 4,071 (14.3%) are accepted by review.
  - By area: grammar 100%, built-in types 35%, parser 31%, C modules 19%, interpreter core 10%,
    stdlib 8%.
  - In my count of the clone: 4,780 rows claim `modelled` (an author's claim), 5,192 are `excluded`
    with typed reasons, and 23,613 are `todo`.
  - Exclusion reasons: test-support 1,812, platform 1,445, no-behaviour 619, vendored 501, generated
    475, internal-bootstrap 174, trivial 153, deprecated 13.
  - Out of scope: multithreading, a heap model, finalisation (`__del__` on last reference), and
    metaclasses that override `__eq__`/`__hash__`/`__repr__`. These are stated scope limits.
  [verified]
- **Size** (page numbers, consistent with my count):
  - 613,318 lines of Lean in 1,539 files (I count 613,495 in 1,543 files at HEAD).
  - 18,898 theorems and lemmas.
  - 4,516 registered top-level properties: 3,834 proven, 588 refuted, 94 open.
  - A rough regex count gives about 25.6k `def`/`abbrev` declarations. The page gives no definition
    count.
  - 418 bug records reproduce on 3.15.2.
  - About 2,393 commits, almost all by one account, between repo creation (2 Nov) and 10 Nov. The
    project started on 29 Oct.
  [verified]

### A2. How the spec was written

- **Entirely by LLM agents, directed by one person.** The page says agents wrote everything. The
  Discourse post names Claude Opus 5.5 as the main model, with GPT-6.1 Sol in Codex helping in the
  final review of the bug reports. David Andrews "directed it and reviewed the results". [verified]
- **Copy the code, not the docs.** This is the central methodological claim. A model written from
  documentation agrees with the documentation, and bugs live where code and docs disagree. [verified]
- **Agent playbook (`AGENTS.md`).** One directory per CPython area, with one agent per module in its
  own worktree. Shared files (`Core.lean`, `DiffCore.lean`, `Registry.lean`, `DiffMain.lean`,
  `Audit.lean`, `scripts/`) are frozen. An agent that needs a new helper defines it locally and reports
  it. "Reference modules" (`Datetime`, `RangeSlice`, `Accel`, `Binary64`, `Fractions`, `StrSearch`) are
  finished exemplars that agents copy patterns from. [verified]
- **Modelling conventions** (`Core.lean`, `AGENTS.md`):
  - Exceptions are values (`Py α := Except PyExc α`), with the source's exact message. A leading `~`
    marks a message that embeds formatted objects, which the diff then compares by class only.
  - Python `int` maps to `Int`/`Nat`. C narrowing to `Py_ssize_t` and unsigned wraparound is explicit.
  - Floats use an exact binary64 model, because Lean's `Float` is opaque to proofs and `decide`.
  - Loops take explicit **fuel**. Running out of fuel returns `PyExc.modelFuel`, which "never
    corresponds to Python behaviour".
  - User callbacks (`__eq__`, `__index__`, iterators) are fallible, stateful and re-entrant. The
    interpreter core uses `EStateM` over a runtime state.
  - Generic functions are modelled over an abstract element type with explicit assumptions, such as
    "if `__lt__` is a strict weak order", not by picking `int`.
  [verified]

### A3. Validation against the real implementation

- **Differential testing before any proof.**
  - Each area has `difftest/<key>_diff.py`. It generates edge-heavy cases: 0, ±1, every `if`
    boundary, `sys.maxsize`, ±2^63, ±2^64, empty inputs and huge ints.
  - Cases are piped as JSON lines into `pydiff`, a compiled Lean executable whose per-module handlers
    run the model. They are compared with the same call on real `python3` 3.15.2.
  - Results compare as JSON. An exception compares on class name, and also on message unless the
    model marks it `~`.
  - The bar is 100% agreement on at least 50,000 cases across several seeds. A mismatch "is a model
    bug until proven otherwise". Deleting a generator case to get to 100% is forbidden.
  - Twin disagreement (the C and pure-Python implementations of the same module) is a finding, not a
    model bug.
  [verified]
- **No conformance-suite or code-coverage numbers.** The project does not use CPython's own test
  suite as an oracle, and reports no line or branch coverage of the C code reached by its difftests. I
  found no gcov or settrace tooling. The only "coverage" is inventory coverage. [verified, absence]
- **Proved statements are re-run against the real interpreter.** A valid proof about a wrong model is
  "the most misleading result you can get". Four such cases are described:
  - JSON indentation "proved" possible at 16 TB because allocation could not fail in the model.
  - A pickle depth bound broke in a fresh process because of a lazily loaded codec, which the harness
    had preloaded.
  - Three models checked exact exception names instead of subclass families.
  - A set model assumed freed addresses never come back. Fixing it turned an accepted proof into a
    real memory bug.
  [verified]
- **Bug records** (`bugs/*.yaml`, 418 that reproduce):
  - Each record has a plain-Python reproducer that must print `REPRODUCED <id>` on 3.15.2. It is also
    run on CPython main: 402 reproduce there, 16 do not, and 18 are "gone in 3.15".
  - Each record also has the cause with line numbers, a logged duplicate search,
    `priority`/`kind`/`likelihood`, `maybe_intended` and `promised_by`.
  - `scripts/check_bugs.py` re-runs all of them.
  - By type: twin disagreement 129, other 122, wrong result 56, crash 28, memory corruption 27, docs
    mismatch 26, wrong error 18, missing check 12. About 55 are serious.
  - Six were filed upstream at launch, after human reading. A pre-launch technical review re-ran 108
    reproducer blocks on both interpreters and matched them by code SHA-256.
  [verified]

### A4. Keeping statements honest

- **Registry plus audit (statement locking).**
  - Every property is one `Entry` in a per-module registry.
  - Entry fields: id, file, `pyFns` (every function it covers), an English `statement`, a `source`
    (docstring, docs line or "invariant"), `status ∈ {proven, refuted, open}`, `prop : Name`,
    `thm : Option Name`, `bug` and `notes`.
  - `lake env lean Audit.lean` iterates the registry in a `CommandElabM` `#eval`. For each entry it
    checks:
    - the theorem's type is **syntactically exactly** `prop` (proven) or `¬ prop` (refuted);
    - `collectAxioms` returns only `propext`, `Classical.choice` and `Quot.sound`, so `sorryAx` fails
      the audit;
    - every refutation names a bug id;
    - no id is duplicated.
  - `sorry`, `admit`, `native_decide`, `bv_decide`, `ofReduceBool`, new axioms, `implemented_by` and
    `@[extern]` are banned.
  - This locks statements to names. Changing a prop's body is still possible, so review must catch
    drift.
  [verified]
- **Refute, never weaken.** A false property is proved false (`thm : ¬P`) and recorded with a
  counterexample, never weakened with extra hypotheses until it becomes provable. Hard properties stay
  `.open` with a note. Every hypothesis must be a documented precondition or type invariant. [verified]
- **Independent review is the only thing that counts.**
  - `coverage/REVIEW_PROMPT.md` (adapted from julia-in-lean) gives a fresh agent a fixed rubric. The
    reviewer reads source and proofs but does not run them. It answers three questions:
    - MIRROR: does the prop use a Lean function that mirrors this function's body, with correct
      citations?
    - PROPERTY: is it quantified over all allowed inputs, with only documented hypotheses?
    - SETTLED: is it proven or refuted, with a bug file for a refutation?
  - Excluded rows get a single question: does the exclusion reason really apply?
  - The verdict is FAITHFUL only if every answer is yes, otherwise HOLLOW ("when unsure, answer no").
  - Verdicts go to `coverage/review/<file>.tsv` with a one-sentence reason per `no`. Across the 85
    reviewed files: 5,322 FAITHFUL, 295 HOLLOW. Earlier reviews are archived.
  [verified]
- **The "broken version" test.** Each theorem is checked by asking which wrong function would also
  satisfy it. If `fun _ => .error` or "always take the first" passes, the theorem pins nothing.
  - Other HOLLOW causes listed in the playbook: `rfl` on one-line definitions, single-example
    instances, `bind_ok` steps that discard the mirror, listing a name in `pyFns` without unfolding its
    body, and forcing `Bool` where Python returns an object.
  [verified]
- **History of the failure.** The first brief asked for breadth, "at least one property per
  function". Review then found fewer than half of the checked rows held up, and 21% in `functools.py`.
  - Per-file acceptance climbs over 2 to 9 review rounds, and sometimes falls. `typeobject.c` went
    0/142 → 135/142 over five rounds. `enum.py` went up and down across nine rounds. When an accepted
    proof turns out wrong about real Python, everything relying on it is withdrawn.
  [verified]
- **Version re-pinning as an honesty mechanism.** The project started on 3.14.7 and moved to 3.15.2.
  - `scripts/repin.py` compared bodies. Changed rows went back to `todo` with a `changed-in-3.15:`
    note. Deleting that note is an explicit claim that the model matches the new body.
  - Stale citations are tagged `@3.14.7:line`. Reviews of changed rows were archived and no longer
    count.
  [verified]

### A5. Tooling built

- **Inventory:** `list_python_functions.py`.
- **Coverage:** `check_coverage.py`. It validates rows against `registry.tsv`, which `Report.lean`
  exports from the Lean registry. `--prefill` settles rows only on a unique name match; ambiguous
  matches become `candidates:` notes.
- **Re-pinning:** `repin.py`, plus `recite.py` and `fix_bare_citations.py` for citation hygiene.
- **Proof checking and testing:** `Audit.lean`, `pydiff` and `difftest/common.py`.
- **Bug pipeline:** `check_bugs.py`, `gen_findings.py` (which writes FINDINGS.md), `reports/`
  (triage TSV, draft issues, `check_drafts.py`, `file_issues.py`) and a launch log.
- **Write-up:** a site generator (`site/build.py`). "Every number and chart on this page is generated
  from the project's repository" at a stated commit.
- **Compute:** SkyPilot `builder.yaml` (64 CPUs, 512 GB RAM pod on their own Kubernetes cluster),
  `scripts/r` (syncs the worktree and runs on the pod) and `watchdog.sh`. The watchdog kills any Lean
  or pydiff process above 64 GB RSS, stops builds when disk falls below 30 GB, and idles the pod down.
[verified]

### A6. Code structure

- **Layers:**
  - `Core` defines the vocabulary: `PyExc`, `Py α`, `ssize` bounds and bit helpers.
  - `DiffCore` holds the JSON helpers and `Handler` type.
  - Each area `PyLean/<Area>/` has `Model.lean` (the mirror), `*.lean` property and proof files, and
    `Diff.lean` (the executable handler).
  - `PyLean/<Area>.lean` holds the registry entries.
  - `All.lean` imports everything, and `Audit.lean` and `DiffMain.lean` sit on top.
  [verified]
- **Trusted base.** For proofs, the Lean kernel plus the three standard axioms. `native_decide` and
  `implemented_by` are banned, so the compiler is not trusted for any theorem.
  - The difftest does run compiled code, so the compiler is trusted for testing only. That is
    acceptable because tests are evidence, not proof.
  - The real trusted base is the **model–source correspondence**, which nothing mechanical checks. It
    rests on difftests plus reviewer reading. The authors say so explicitly ("A checked proof
    guarantees that a statement follows from the copy. It doesn't guarantee the copy matches real
    Python").
  [verified]
- **Executable vs propositional.** Models are **executable `def`s**: total, fuelled and returning
  `Py α`. The same definitions are run by `pydiff` and unfolded in proofs. Properties are separate
  `Prop`s quantified over all inputs; there are no inductive relational semantics. [verified]
- **Decidability and `#eval`.**
  - `decide` appears about 8,000 times as a tactic, for finite cases and concrete counterexamples.
    There are about 1,400 `Decidable` mentions, and `DecidableEq (Py α)` is hand-written.
  - `#eval` appears only twice. Testing goes through the compiled executable, not `#eval`.
  - Refutations are typically a concrete input plus `decide` or `simp`, run through the model.
  [verified, counts by grep]

### A7. Scale and performance

- A full build needs 64 GB of RAM or more; the saved build log reports 3,084 jobs. The lakefile caps
  each file at 8 GB (`-M8000`) so that runaway elaboration fails locally. 53 files raise
  `maxRecDepth`, and some set `maxHeartbeats 0` or 8M. [verified]
- All heavy work runs off the workstation on a shared pod, with a rule to kill your own processes by
  PID only. There is a known pitfall: a failed `lake build` leaves `Audit.lean` reporting on the
  stale build, so commands must be chained with `&&`. [verified]
- No build times, token counts or dollar costs are published. [verified, absence] julia-in-lean
  reported about $5,000 of API-equivalent usage for its effort. [summary]

### A8. Failure modes and lessons (theirs, plus the critics')

1. **Hollow theorems** (the dominant failure). True and machine-checked, but satisfied by broken
   functions. In julia-in-lean, 128 of 130 quick in-bounds proofs had assumed the index in bounds.
   [verified, summary for the Julia figure]
2. **Model–reality gaps where the difftest cannot reach.** Examples: allocation failure, process
   state, subclass families and address reuse. The fix was to make the model more realistic, not the
   theorem weaker. [verified]
3. **A wrong denominator.**
   - All of idlelib, tkinter and turtle were excluded as "GUI". A CPython core developer (the IDLE
     maintainer) pointed out on Discourse that much of it is not GUI code. Another LLM checker had
     found about 70 idlelib issues.
   - Coverage was corrected from 15.7% to 14.3%, with a dated correction on the page.
   - The authors also clarified that "excluded" means "never modelled", not "clean".
   [verified]
4. **Report flood risk.** A core developer welcomed the work but warned that a flood of issues would
   overwhelm the team, and asked for real-world-impact prioritisation and finished fixes. The authors
   filed 6 of 418 and held the rest pending maintainer preference. [summary]
5. **HN critiques.**
   - The bug classes are mostly "fuzzing, not proofs": twin disagreement and "other" are more than
     half the bugs.
   - The examples look cherry-picked toward pure functions; how is impure C translated?
   - Why not verify the real C with Frama-C/ACSL instead of an AI translation?
   - Models will drift from the code over time.
   - How are "properties that should hold" chosen? Answer from the playbook: in order of preference,
     (a) the implementation disagreeing with itself, (b) undisputed invariants, (c) explicit doc
     sentences read in context.
   - Some readers refused to read an AI-written write-up.
   [verified]
6. **The authors' own list.** Pin one version. Enumerate everything first. Copy code, not docs. Let
   user code misbehave. Test before proving. Keep counterexamples. Check proved statements against
   the real thing. Count only what an independent reviewer accepts. [verified]
7. **Where the bugs were** (`AGENTS.md`). "The C arithmetic is usually right." Findings came from
   parsers, missing error checks after conversions, NUL-terminator assumptions, validation in the
   wrong order, and above all re-entrancy: user code mutating a container mid-operation. [verified]

### A9. Agent workflow and costs

- One modelling agent per module (worktree), then a separate review agent per file with a fixed
  prompt. Rounds repeat until rows are FAITHFUL.
- Triage is read-only: agents may search the CPython tracker but "NEVER create, comment on, or react
  to" issues. A human reads everything before filing, and related findings go upstream as one issue.
- Rough throughput: about 12 days from start to 613k lines and about 2.4k commits, on a 64-CPU/512 GB
  pod.
- Costs are not disclosed. [verified; cost unknown]

---

## Part B. Comparable "formalise a large real artefact" projects

1. **julia-in-lean** (Miles Cranmer, 2026), the direct ancestor. [summary]
   - Same mirror → difftest → prove/refute → rubric-review pipeline over Julia Base (parts of about 90
     `base/` files and some stdlib).
   - Exhaustive differential checks where the domain is small: all 656,896 Int8/UInt8 cases, and
     236,954 Float64 operations.
   - Results: about 400 bugs found, 75 filed by hand. Bugs are YAML records with reproducers and a
     `maybe_intended` field. Cost was about $5k API-equivalent.
   - Its 128/130 hollow in-bounds proofs produced the rubric that CPython adopted.
   - The thread raised code/model drift (proposals: `test/lean/` folders in CI, or turning properties
     into property-based tests).
2. **AWS Cedar, verification-guided development** (Disselkoen et al., arXiv 2407.01688, FSE 2024).
   [verified]
   - A Lean executable model is the spec and the oracle. Production code stays in Rust. Nightly
     differential random testing (DRT) and property-based testing compare the two: 6 hours per
     target on ECS, millions of inputs, with type-directed generators.
   - Sizes in Table 1:
     - Lean: 1,673 lines of model, 5,714 lines of proof.
     - Rust: 15,693 lines of production code, 20,458 lines of tests.
     - The text's "13.4:1" proof ratio does not match the table.
   - Seven properties proved: forbid trumps permit, default deny, validation soundness, termination,
     and others.
   - Proofs found 4 bugs, including a non-termination bug that testing would hardly find. DRT and PBT
     found 21. Nine bugs that were missed are catalogued, mostly because generators did not reach
     them.
   - Lessons:
     - Keep the model about 10x smaller than the implementation. Omit the parser, diagnostics and
       optimisations.
     - Custom set and map types plus separate invariant theorems are needed for well-founded
       recursion.
     - Code coverage is not input diversity.
     - Don't ship Lean-compiled code into production.
     - Testing can feed back into language design.
3. **WebAssembly: WasmCert and SpecTec** (Watt CPP 2018; Youn et al. PLDI 2024).
   - Hand mechanisation in Isabelle/Coq found errata in the official spec. [unverified detail]
   - SpecTec, adopted by the Wasm CG in March 2025, inverts the flow. One DSL source generates the
     typeset spec, prose pseudocode, a meta-interpreter and Coq definitions. The meta-interpreter
     passes 100% of the applicable official Wasm 2.0 test suite and surfaced historical spec errors.
     This replaces "eyeball correspondence" between prose and mechanisation with generation.
     [verified via search summaries]
4. **JavaScript: JSCert/JSRef and ESMeta.**
   - JSCert (POPL 2014) is a Coq ES5 spec kept "line-by-line close" to the standard. JSRef is an
     interpreter extracted from Coq, proved correct against JSCert, and run on test262. Its failures
     exposed bugs in browsers, the standard and test262 itself. Pass counts were not verified this
     pass.
   - ESMeta mechanically extracts an executable model from ECMA-262's own `spec.html`. It runs test262
     against it and type-checks every spec pull request in CI. Its predecessor JEST found 44 engine
     bugs and 27 spec bugs in ES11 via N+1-version differential testing.
   - Lesson: when the source text is structured enough, **extract** rather than re-author, and make
     the conformance suite plus the spec check part of the upstream workflow.
   [verified via search summaries; numbers for JEST, not ESMeta]
5. **ISA semantics in Lean: Sail → Lean and AWS LNSym (Armv8).**
   - Sail has an experimental Lean backend. A Lean RISC-V model extracted from Sail is used by SP1's
     zkVM proofs, and Lean-MLIR has a bit-blastable RISC-V mechanisation claimed equivalent to the Sail
     model.
   - LNSym formalises AArch64 in Lean with a `cosim` target that runs random instruction tests
     against real Arm hardware (default 20 per instruction class).
   - Lesson: generate from the vendor's own machine-readable spec where one exists, and co-simulate
     against silicon.
   [verified via search summaries; depth unverified]
6. **AWS TLA+ and P** (Brooker and Desai, CACM 2025, "Systems Correctness Practices at AWS"), briefly.
   [unverified detail]
   - Design-level models: P state machines, PObserve checking production logs against P specs, and
     deterministic simulation.
   - Relevant mainly as **runtime conformance**: checking real traces against the spec after the fact
     is the closest analogue to checking our model against later courts' notes.
7. Also cited by the CPython page: **PTX in Lean** (arXiv 2611.04447, Nov 2026), which proves GPU
   kernels correct. The abstract does not say whether LLMs helped or how the model was validated.
   [verified, abstract only]

---

## Part C. How CPython's situation differs from ours

| | CPython | caselaw-lean-2 |
|---|---|---|
| Thing mirrored | source code, unambiguous | opinion text, ambiguous natural language |
| Oracle | total and executable: run `python3` on any generated input | sparse, partial and noisy: later courts' notes, SCDB, CRS, override lists; cannot be queried on new inputs |
| Inputs | generated freely (50k+ per function) | fixed corpus; no generation of "new decisions" |
| Ground truth for a mismatch | interpreter wins; the model is wrong unless twins disagree | no single winner; model, reader, oracle and court can each be wrong |
| Twins | C vs pure-Python implementations | independent sources for the same fact: CAP vs CourtListener metadata, SCDB vs CRS, head matter vs body, citing court's parenthetical vs its own text |
| Unit of coverage | function in a pinned source tree | decision, holding or treatment-candidate in a pinned corpus snapshot |

So their differential test is a *conformance* test. Ours can only be an *agreement-on-the-oracle's-support*
measurement with precision and recall, and every disagreement needs triage into four buckets: model,
reader, oracle, or the court itself.

---

## Lessons for caselaw-lean-2

Ranked by expected value. Each is concrete enough to put into SCHEMA.md, LEAN.md or the agent briefs.

### Architecture and trusted base

1. **Split the trusted base explicitly into (a) kernel-checked general theorems and (b) a verified
   executable checker run over data.**
   - CPython bans `native_decide`, so every theorem is kernel-only. Our certificate checking over
     millions of decisions cannot run in the kernel (`decide` on string search over opinion texts will
     not scale).
   - Write `Certificate.check : Cert → Corpus → Bool`. Prove once, in the kernel,
     `check c = true → Valid c`. Then run the compiled checker over the shards.
   - State in LEAN.md and the report that per-record admission trusts the Lean compiler and the
     loaded data, exactly as CPython's and Cedar's differential tests trust compiled code. The general
     theorems (monotonicity, partial overruling, Erie, split resolution) stay kernel-only.
   - Do **not** let shard runs use `native_decide` to "prove" corpus-wide statements and then present
     them as theorems.
2. **Executable models, separate `Prop`s.** As in CPython and Cedar:
   - `status`, `authority`, `binds` and `split` are total `def`s, with fuel or well-founded recursion
     on dates and event lists.
   - They are run by the shard runner and unfolded in proofs. Theorems are separate `Prop`s
     quantified over all court tables, event lists and dates.
   - Keep the model far smaller than the data pipeline (Cedar: about 10x smaller than the
     implementation). Parsing and extraction stay outside Lean.
3. **Freeze a small shared core plus a contract, with one directory per agent.**
   - Our six-agent split matches CPython's structure.
   - Add a frozen `CaseLaw2/Core.lean` (types for Court, Decision, Holding, Event, Date, Cert) and a
     JSON-lines handler interface (CPython's `Handler` + `pydiff`). Every layer's output can then be
     run and diffed.
   - Agents never edit the core. A new helper is defined locally and reported.
4. **Per-file memory and heartbeat caps from day one** (`-M8000` per file, a watchdog, no
   `maxHeartbeats 0` in committed code). Data never goes into `.lean` files as giant literals; load it
   at run time in the executable.

### Statement honesty

5. **A registry of every theorem, plus an audit that locks statements.**
   - Copy CPython's `Entry`/`Audit.lean` almost verbatim. Each entry has: id; doctrinal `source`
     (doctrine.md section, leading case cite and confidence tag); English `statement`;
     `status ∈ {proven, refuted, open}`; `prop`; `thm`; and a `counterexample` field for refutations.
   - The audit fails on: a type mismatch with the registered prop; axioms beyond the standard three;
     `sorry`, `native_decide`, `implemented_by` or `@[extern]` in any registered theorem; a refutation
     without a recorded counterexample.
   - Generate the report's theorem table from the registry, never by hand.
6. **Refute, never weaken, especially for doctrine.**
   - doctrine.md tags many rules with jurisdiction-dependent exceptions. Examples: "unpublished never
     binds" is false in some states, and the prior-panel rule has intervening-authority exceptions.
   - When a universal rule fails, state the refutation with the concrete court or decision as the
     counterexample. Then add a separately registered narrowed theorem whose extra hypothesis is a
     **named, sourced doctrinal exception**. This mirrors the `Accel` pattern: a broad statement
     refuted, a narrowed one proven, every excluded case on record.
   - Never add an anonymous hypothesis.
7. **Make the "would a broken version pass?" test mechanical: a mutation kill matrix.** This is the
   single most useful upgrade over CPython, whose version is an LLM reviewer reading.
   - We have a small set of core functions, so write about 15 deliberately broken variants: `status`
     always good law; ignores dates; ignores partial scope; ignores en banc; treats dissents as
     majority; treats `acknowledges` edges as acts; statute abrogation retroactive; and so on.
   - Every registered theorem must be *false* for at least one mutant. CI checks this by re-proving
     the negation, or by evaluating a counterexample, for each mutant.
   - A theorem that kills no mutant is HOLLOW automatically. Publish the matrix.
8. **Independent review with a fixed rubric; only reviewed rows count.**
   - Adapt `REVIEW_PROMPT.md` into three questions per layer row. MIRROR: does the model follow
     doctrine.md's rule and cite it? PROPERTY: is it quantified, with documented hypotheses only?
     SETTLED: proven or refuted, with counterexample?
   - For certificates and treatments, the reviewer reads the quoted span in the opinion and answers:
     is it a treatment *act* by the majority, of the asserted kind, on this target?
   - Verdicts go to TSV files with one-line reasons. "When unsure, answer no." Accepted counts may
     fall between rounds; withdraw dependents.
   - The reviewer is a different agent, and ideally a different model, from the writer.

### Validation against an independent oracle

9. **Hold the oracle back, then use it CPython-style: every disagreement is a model bug until triaged
   otherwise.**
   - The reader never sees later-court notes (already in DESIGN.md). Every pair where they disagree
     goes into a triage file with four outcomes: `model-wrong`, `reader-wrong`, `oracle-wrong` (note
     or SCDB error, with evidence) or `genuinely-contested`. Each outcome gets a quoted reproducer:
     the span and the note.
   - `oracle-wrong` records are our "bug reports". Citator and note errors are a headline finding,
     like CPython's 418. Prior_art.md §3.2 already says citators are wrong about a third of the time.
10. **Treat twin disagreement as the highest-yield finding class.**
    - In CPython, 129 of 418 findings were C vs Python twins disagreeing.
    - Our twins:
      - CAP vs CourtListener for court, date and publication status;
      - SCDB `precedentAlteration` vs CRS lists vs Christiansen–Eskridge;
      - a decision's head-matter history vs the citing court's own text;
      - a court's parenthetical about a holding vs that holding's own status.
    - Build a cross-source agreement pass early and record every disagreement as a finding with both
      sources.
11. **Check proved theorems against the data, not only against the model.** CPython's "valid proof,
    wrong about Python" cases came from model idealisations. For each general theorem, write a data
    query for its observable consequence and report violations. Two examples:
    - "SCOTUS resolves the split": find lower-court decisions after the SCOTUS date that still follow
      the old side without distinguishing it.
    - "Vacated never binds": find citing courts that treat a vacated decision as binding.
    Each violation is either a model idealisation to fix or a real-world anomaly to report.
12. **Model the misbehaving input.** CPython's worst bugs came from user code that throws or
    re-enters mid-operation. Our analogue is adversarial text: dissents quoting "overruled", "your
    objection is overruled", reported history, parentheticals, "overruled on other grounds",
    superseded rules, and same-day events. Each needs its own generator of hard negatives in the gold
    set and its own row in the certificate disqualifier list (prior_art §7.1 item 1).

### Test-suite design

13. **Pin and enumerate everything up front.**
    - Pin the corpus snapshot (CAP/CourtListener bulk date plus content SHA per decision), the US Code
      release point and the doctrine.md commit.
    - Build `coverage/inventory/*.tsv`: one row per decision in scope, per holding, and per
      treatment-candidate span. Status is one of `todo`, `modelled`, `excluded:<typed reason>` or
      `accepted`.
    - Re-pinning follows CPython's `repin.py`: changed text sends rows back to `todo`, stale offsets
      are tagged, and old reviews are archived.
14. **Differential tests per layer, with exhaustive checks where the domain is small.**
    - Court-pair authority is finite: about 1–3k courts squared times a few date epochs. Enumerate it
      completely against doctrine.md's tables, as julia-in-lean did for all Int8 cases.
    - Treatment and status: diff against every oracle-bearing pair (the analogue of 50k cases), and
      report agreement per court system and decade, not one global number.
    - A fixed set of seeded hard cases (CPython's "edge-heavy generation") forms the regression suite.
15. **Every finding has a re-runnable reproducer and a gold label kept in git.** Use
    `findings/*.yaml` with fields: id, kind, source A, source B, quoted spans with SHA and offsets,
    `maybe_intended` (doctrinally arguable), confidence, and the mechanism that found it. A
    `check_findings` script re-verifies every quote against the pinned corpus.

### Agent workflow

16. **Breadth-first produced junk in both Lean-mirror projects; go depth-first per layer.** Do not
    brief agents with "one theorem per rule" or "extract every treatment". A layer is finished when
    its rows would survive review.
17. **Read-only toward the outside world, with a human gate.** If we ever publish "the court's note is
    wrong" or "citator X misses this overruling", a human reads every item first, and related items go
    out batched. Discourse showed maintainers fear floods.
18. **Shared compute discipline.** Use one build host with a wrapper. Kill your own processes by PID.
    Chain build `&&` audit, because a failed build silently leaves a stale audit. This already matches
    our memory rules.

### Presenting coverage honestly

19. **Three-state coverage bars per area against the full denominator**: accepted / written but not
    accepted / not started, by court system and layer. Typed exclusions are listed separately and are
    themselves reviewed ("does the reason really apply?").
    - CPython's 15.7% → 14.3% correction came from an unreviewed blanket exclusion.
    - Publish corrections with a date. Say "excluded = never modelled, not clean".
20. **Attribute every finding to the mechanism that found it.** HN's sharpest critique was that most
    CPython findings came from differential comparison, not proofs. Cedar handled this well (4 bugs
    from proof vs 21 from testing). For each finding, record whether it came from Lean refutation,
    certificate rejection, oracle disagreement, twin disagreement or human audit, and show the split.
21. **Generate every number in the report from a commit** (CPython's `site/build.py` approach). Show
    the per-round acceptance curves, including drops, and the HOLLOW counts. Show the hollow-theorem
    and mutation-kill statistics; they are what makes the theorem count credible.
22. **State the model–reality gap in one sentence near the top.** For example: "a Lean proof shows a
    status follows from our encoding of doctrine and the admitted treatments; it does not show the
    encoding matches what courts do, which is what the held-out evaluation measures." CPython's page
    does this, and it pre-empts the "AI translation" critique.

### Unverified or open points from this pass

- No cost, token or time-per-function figures exist for the CPython project.
- The X thread (x.com/broyojo42/status/2119846041214206286) was not read.
- julia-in-lean figures come from a fetched-page summary.
- Comparables 3–6 are from search summaries or memory, not full papers. In particular: WasmCert errata,
  JSCert test262 pass counts, the depth of LNSym's co-simulation, and the CACM 2025 content.
- My grep counts of declarations are approximate (regex, not elaborated).
