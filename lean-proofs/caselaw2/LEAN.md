# caselaw-lean-2: the Lean core

Lean 4.35, no Mathlib, in lean-proofs `LegalProofs/CaseLaw2/` (namespace `CaseLaw2`). It is built on the revised design
in DESIGN.md (D1–D9).
- The trusted base and what is proved, computed, certified, tested or assumed: `TRUST.md`.
- Every departure from doctrine.md: `DEVIATIONS.md`.
- Statement changes: `STATEMENTS.log`.

    lake build LegalProofs.CaseLaw2            # model + proofs + examples + mutation matrix + statement lock
    python audit/audit.py check                # statement lock, axioms within {propext, Classical.choice, Quot.sound}, no sorry
    ./run_lean.sh <shards> [data] [edges] [out] [asOf]   # the runner (compiled; falls back to the interpreter)
    ./run_lean_wsl.sh build | audit | run ...  # the same under Linux Lean in WSL (see "Running under WSL")

**Where it runs.** Windows Application Control blocks the Windows Lean toolchain (`lean.exe`, `lake.exe`) and the
compiled `caselaw2.exe` on this machine. Since 12 Nov (evening) everything below was built, audited and run under
Linux Lean 4.35.0 in WSL Ubuntu, with the runner compiled as a native Linux executable.

## Counts

- **Lean:** 8,461 lines in 27 files (1,643 of them the generated `Registry` and `Audit`; `CueTable` is generated too).
- **Theorems:** **141**, all registered and locked (4 for witness rows in round 4, 91 after the fuzz fix, 9 for the hunt fixes, 14 in `Hunt`, 23 in
  `Spec/Lines` for round 2). 4 use no axioms; the rest use only propext, Quot.sound and Classical.choice.
- **`#guard` checks:** 223 (145 real-case replays in `Examples`, 12 of them witness rows, 44 in `Hunt`, 16 SHA-1 vectors, 14 Horty, 3
  mutation-matrix guards, 1 registry count).
- **Mutation:** 27 properties against 27 mutants, all killed (M27 "witness row may be explicit or lack standing" with round 4; M21 "status global after adoption cut-off", M22
  "divisions overrule the court" added with the hunt fixes; M23–M26 with round 2).
- **No `sorry`, `axiom` or `native_decide`** anywhere (checked by `audit.py`).

## Layers (DESIGN D1) and modules

| Layer | Module | Contents |
|---|---|---|
| types | `Basic` | `Date` (yyyymmdd), the ordered `Force` scale (none < notCitable < citableNoWeight < persuasive < persuasiveStrong < bindingAbsentConflict < binding), every SCHEMA enumeration with a parser that returns `none` for unknown strings, `optNat` (TSV 0 = none) |
| types | `Courts` | `CourtEpoch` (dated tier, system, circuit, unit), `Succession`, `Adoption` (+ `unitB` filter), the abstract parameter structure `Rules`, `RuleRow` -> `Rules.ofLookup`, `Env`, `Env.firm` (S/L rows only), the Spec lookups `Env.lookups` (list scans) |
| types | `Holdings` | `Decision` (+ optional appeal venue, TRAP 41.3 transferor), `Holding` (interned issue, 0 = anonymous issue; role; answer; Marks flag) |
| types | `Events` | `Scope`, `HKind`, `TKind` (+ `changesStatus`), `Temporal` (Sunburst), `HEvent`, `TEvent`, `SEvent`, `Record` |
| Spec | `Spec/RuleId` | the labels of the default trees, each with the doctrine.md rule it implements; `assume*` labels for every fallback |
| Spec | `Spec/Authority` | Catala-style default trees: `relation` (H1self, F1, E1/E3, federal hierarchy F7/F11/F12/F13, state hierarchy H1/H2/§4.1 H/§4.1 V/§4.4); `force` (adoption raise, then F9/F5/F6 caps; Texas promotion); `canChangeStatus` (cLater, F1abrogate, higherCourt, lastResortSelf, same-court bench rule, adoptedEnBanc) |
| Spec | `Spec/AuthorityThms` | §9 22(a)–(d) and the power theorems |
| Spec | `Spec/Status` | `Status` (good / unknown r / neg n), `Effect`, `status` = fold of `join` over effects, `goodLaw`; compiling admitted events to effects (`histEffect`, `treatEffect`, `superEffect`, lapse = revival); `statusOf` (two dates: asOf t, conduct u); theorems |
| Spec | `Spec/Splits` | candidates, `resolve` (binding sub-base, then top precedence, then first-in-time / own unit / choice; returns a set), `split`; theorems |
| Spec | `Spec/Findings` | the finding predicates (Bool): citesOverruled, citesVacated, citesWithdrawn, citesNotCitable, citesUnpublishedAsBinding, appliesSupersededHolding, panelDepartsWithoutEnBanc, pluralityTreatedAsBinding, ignoresBindingInUnit, atRisk |
| Spec | `Spec/Lines` | round 2: status per line of authority everywhere. `Line`, `linesOf`, `lineStatus` (the per-line status rows); `goodVia`, `goodIn`, `liveSomewhere`; `Held`, `heldVia`, `heldIn`, `heldUnion` (the holdings that count at a court: splits, conflicts); `lineBase` (Horty); 23 theorems |
| Spec | `Spec/Horty` | Horty's reason model (factors, cases, pair-form consistency, permitted, forcedBy, result model, answer embedding) |
| Exec | `Exec/Index` | `index` (group by key into a HashMap) and `index_getD` (= the Spec's filter) |
| Exec | `Exec/Env` | `ExecEnv`, `ExecRecord` (hash-indexed lookups) and the refinement theorems `exec_*_eq_spec` |
| Exec | `Exec/Verdicts` | `queryFor`, `forceOn`, `witness`, `negByBinding`, `citeFacts`, `candFor`, `histPower`: the glue the runner and Examples share |
| checker | `Certificate` | `Cert.check` (decidable, reason codes), cue and disqualifier tables, `checkCert_sound` |
| tests | `Examples` | real-case replays (`#guard`) |
| tests | `Mutants` | `Impl`, 22 properties, 22 mutants, the kill matrix |
| lock | `Registry`, `Audit` | generated by `audit/audit.py lock`: every theorem, and `#guard_msgs` on each statement and axiom list |
| I/O | `Tsv`, `Data`, `Run` | streaming TSV readers, raw SCHEMA rows, the runner |
| | `Core` | imports every model module; `LegalProofs/CaseLaw2.lean` = Core + Registry + Audit |

## Theorems (the registry; statements are locked in `audit/statements.lock`)

Generated by `python audit/theorem_table.py`.

| Theorem | Module | Statement (doc, or the locked statement abbreviated) |
|---|---|---|
| `Cert.Window.digest_eq` | Certificate | `∀ (self : Window), self.digest.get = Sha1.hex self.text` |
| `Cert.checkCert_cite_index` | Certificate | Citation-index resolution: — `∀ (c : Input), (check c).admitted = true → c.selfText = false → c.evidence.startsWith "cite:" = true → ∀ (m : Std.HashMap String Nat), c.citeIndex = some m → m.get? (comp…` |
| `Cert.checkCert_quote_nonempty` | Certificate | Non-empty quote (FB-L2): — `∀ (c : Input), (check c).admitted = true → c.quote ≠ "" ∧ c.start < c.stop` |
| `Cert.checkCert_sound` | Certificate | Certificate soundness: — `∀ (c : Input), (check c).admitted = true → shaOk c = true ∧ (∃ w, coveringWindow c = some w ∧ quoteAt c w = true) ∧ hasCue c = true ∧ disqualified c = false ∧ resolves c …` |
| `Cert.checkCert_window_hash` | Certificate | Window hash (TRUST.md): — `∀ (c : Input), (check c).admitted = true → ∃ w, coveringWindow c = some w ∧ quoteAt c w = true ∧ wellFormed c w = true ∧ (∀ (s : String), w.hash = some s → Sha1.hex w.tex…` |
| `Cert.check_fail_reason` | Certificate | Each rejection names the first failing condition: — `∀ (c : Input) (r : Reason), check c = Result.fail r → (r = Reason.shaUnknown ↔ shaOk c = false)` |
| `Exec.exec_canChangeStatus_eq_spec` | Exec.Env | `∀ (e : Env) (b x : Decision) (dom : Option Domain), canChangeStatus (ExecEnv.build e).lookups b x dom = canChangeStatus e.lookups b x dom` |
| `Exec.exec_eventLookups_eq_spec` | Exec.Env | `∀ (r : Record), (ExecRecord.build r).lookups = recordLookups r` |
| `Exec.exec_forceDiv_eq_spec` | Exec.Env | The runner's force on a court as it ordinarily sits (H6) equals the Spec's. — `∀ (e : Env) (x : Decision) (h : Holding) (p : Bool) (q : Query), forceDiv (ExecEnv.build e).lookups x h p q = forceDiv e.lookups x h p q` |
| `Exec.exec_force_eq_spec` | Exec.Env | The runner's force equals the Spec's. — `∀ (e : Env) (x : Decision) (h : Holding) (p : Bool) (q : Query), force (ExecEnv.build e).lookups x h p q = force e.lookups x h p q` |
| `Exec.exec_lookups_eq_spec` | Exec.Env | `∀ (e : Env), (ExecEnv.build e).lookups = e.lookups` |
| `Exec.exec_status_eq_spec` | Exec.Env | The runner's status equals the Spec's (both the court data and the events through hash indexes). — `∀ (e : Env) (r : Record) (x k t u : Nat), status (effectsOf (ExecEnv.build e).lookups (ExecRecord.build r).lookups r.dec x) k t u = statusOf e.lookups r x k t u` |
| `Exec.index_getD` | Exec.Index | `∀ {α : Type u_1} {K : Type u_2} [inst : BEq K] [inst_1 : Hashable K] [LawfulBEq K] [LawfulHashable K] (key : α → K) (l : List α) (k : K), (index key l).getD k [] = List.f…` |
| `Force.le_binding` | Basic | `∀ (a : Force), a.rank ≤ Force.binding.rank` |
| `Force.rank_inj` | Basic | `∀ {a b : Force}, a.rank = b.rank → a = b` |
| `Force.rank_max` | Basic | `∀ (a b : Force), (a.max b).rank = max a.rank b.rank` |
| `Force.rank_min` | Basic | `∀ (a b : Force), (a.min b).rank = min a.rank b.rank` |
| `Hunt.acknowledged_never_zombie` | Hunt | `∀ (s : Status) (u : Hunt.Use), u.acknowledges = true → Hunt.zombie s u = false` |
| `Hunt.corrected_implies_first` | Hunt | `∀ (pub : Publication) (pr : Bool) (f : Force) (b s : Bool), Hunt.unpublishedAsBinding' pub pr f b s = true → Hunt.unpublishedAsBinding pub f b s = true` |
| `Hunt.earlier_conduct_no_error` | Hunt | Prospectivity (the reader-side mirror of `Spec.supersession_prospective`): — `∀ (d u : Nat) (a n : Bool), u < d → Hunt.twoDateError d u a n = false` |
| `Hunt.enBanc_never` | Hunt | `∀ (d : Hunt.Departure), d.panel = false → Hunt.panelOverrulesPanel d = false` |
| `Hunt.erase_keeps_consistent` | Hunt | Overruling a case never creates an inconsistency (from `Horty.consistent_erase`). — `∀ (Γ : List FCase) (c : FCase), Hunt.inconsistentBase Γ = false → Hunt.inconsistentBase (Γ.erase c) = false` |
| `Hunt.forumDependent_symm` | Hunt | `∀ (a b : Force), Hunt.forumDependent a b = Hunt.forumDependent b a` |
| `Hunt.good_law_never_zombie` | Hunt | `∀ (u : Hunt.Use), Hunt.zombie Status.good u = false` |
| `Hunt.no_conflict_with_power` | Hunt | `∀ (c k : Force) (a b : Answer) (p : Bool), Hunt.dualHighCourtConflict c k a b true p = false` |
| `Hunt.panelOverrulesPanel_needs` | Hunt | `∀ (d : Hunt.Departure), Hunt.panelOverrulesPanel d = true → d.panel = true ∧ d.strongRule = true ∧ d.exception = none` |
| `Hunt.same_notation_same_force` | Hunt | `∀ (n m : Hunt.Notation), n = m → Hunt.commissionForce n = Hunt.commissionForce m` |
| `Hunt.twoDateError_dates` | Hunt | `∀ (d u : Nat) (a n : Bool), Hunt.twoDateError d u a n = true → d ≤ u` |
| `Hunt.unpublishedAsBinding_spec` | Hunt | The Spec's version with `followed` read from the opinion. — `∀ (c : CiteFacts) (f : Force) (p : List RuleId) (pub : Publication), c.pub = some pub → c.force = some (f, p) → c.followed = true → Hunt.unpublishedAsBinding pub f true f…` |
| `Hunt.winning_side_never` | Hunt | `∀ (s c : Nat) (a : Answer) (r n : Bool), Hunt.losingSideAfterResolution s c a a r n = false` |
| `Hunt.zombie_is_spec_finding` | Hunt | The Spec's own findings are the candidate set: — `∀ (c : CiteFacts) (u : Hunt.Use), Hunt.zombie c.status u = true → (citesOverruled c ∣∣ citesVacated c ∣∣ citesWithdrawn c) = true` |
| `Lookups.succeeds_refl` | Courts | `∀ (L : Lookups) (f c : Nat), L.succeeds f c c = true` |
| `Spec.Horty.FCase.wf_iff` | Spec.Horty | `∀ (c : FCase), c.wf = true ↔ ∀ (f : Factor), f ∈ c.reason → f ∈ c.facts ∧ f.side = c.outcome` |
| `Spec.Horty.Side.ne_opp` | Spec.Horty | `∀ (s : Side), s ≠ s.opp` |
| `Spec.Horty.Side.opp_ne` | Spec.Horty | `∀ (s : Side), s.opp ≠ s` |
| `Spec.Horty.answerCase_conflict` | Spec.Horty | `∀ (a b : Bool), conflict (answerCase a) (answerCase b) = !a == b` |
| `Spec.Horty.answers_consistent_iff` | Spec.Horty | Yes/no holdings are the degenerate fact-free case: — `∀ (as : List Bool), consistent (List.map answerCase as) = true ↔ ∀ (a : Bool), a ∈ as → ∀ (b : Bool), b ∈ as → a = b` |
| `Spec.Horty.consistent_erase` | Spec.Horty | Overruling one case preserves consistency. — `∀ {Γ : List FCase} (c : FCase), consistent Γ = true → consistent (Γ.erase c) = true` |
| `Spec.Horty.consistent_filter` | Spec.Horty | Overruling every case matching a predicate preserves consistency. — `∀ {Γ : List FCase} (p : FCase → Bool), consistent Γ = true → consistent (List.filter p Γ) = true` |
| `Spec.Horty.consistent_iff` | Spec.Horty | `∀ (Γ : List FCase), consistent Γ = true ↔ ∀ (c1 : FCase), c1 ∈ Γ → ∀ (c2 : FCase), c2 ∈ Γ → conflict c1 c2 = false` |
| `Spec.Horty.consistent_of_same_outcome` | Spec.Horty | A base whose cases all share one outcome is consistent. — `∀ {Γ : List FCase} {s : Side}, (∀ (c : FCase), c ∈ Γ → c.outcome = s) → consistent Γ = true` |
| `Spec.Horty.consistent_sublist` | Spec.Horty | Overruling = removing holdings preserves consistency. — `∀ {Γ Γ' : List FCase}, (∀ (x : FCase), x ∈ Γ' → x ∈ Γ) → consistent Γ = true → consistent Γ' = true` |
| `Spec.Horty.forcedBy_iff` | Spec.Horty | `∀ (c : FCase) (X : List Factor), forcedBy c X = true ↔ (∀ (f : Factor), f ∈ c.reason → f ∈ X) ∧ ∀ (f : Factor), f ∈ X → f.side = c.outcome.opp → f ∈ c.facts` |
| `Spec.Horty.forced_blocks_opposite` | Spec.Horty | If a precedent forces its outcome on `X`, every decision for the other side on `X` (with any reason made of present, other-side factors) is inconsistent with the case base. — `∀ {Γ : List FCase} {c : FCase} {X : List Factor}, c ∈ Γ → forcedBy c X = true → ∀ (r : List Factor), sub r X = true → (∀ (f : Factor), f ∈ r → f.side = c.outcome.opp) → c…` |
| `Spec.Horty.permitted_of_consistent_same_outcome` | Spec.Horty | If every case in a consistent base has outcome `s`, any well-formed case with outcome `s` is permitted. — `∀ {Γ : List FCase} {s : Side} {c : FCase}, consistent Γ = true → (∀ (d : FCase), d ∈ Γ → d.outcome = s) → c.wf = true → c.outcome = s → permitted Γ c = true` |
| `Spec.Horty.result_not_stricter` | Spec.Horty | The result model never forces where the reason model does not. — `∀ {c : FCase} {X : List Factor}, c.wf = true → forcedBy (resultCase c) X = true → forcedBy c X = true` |
| `Spec.Horty.sub_iff` | Spec.Horty | `∀ (a b : List Factor), sub a b = true ↔ ∀ (x : Factor), x ∈ a → x ∈ b` |
| `Spec.Status.good_join` | Spec.Status | `∀ (a : Status), Status.good.join a = a` |
| `Spec.Status.isNeg_iff` | Spec.Status | `∀ (a : Status), 10 ≤ a.rank ↔ ∃ n, a = Status.neg n` |
| `Spec.Status.join_assoc` | Spec.Status | `∀ (a b c : Status), (a.join b).join c = a.join (b.join c)` |
| `Spec.Status.join_comm` | Spec.Status | `∀ (a b : Status), a.join b = b.join a` |
| `Spec.Status.join_good` | Spec.Status | `∀ (a : Status), a.join Status.good = a` |
| `Spec.Status.rank_inj` | Spec.Status | `∀ {a b : Status}, a.rank = b.rank → a = b` |
| `Spec.Status.rank_join` | Spec.Status | `∀ (a b : Status), (a.join b).rank = max a.rank b.rank` |
| `Spec.Status.rank_zero_iff` | Spec.Status | `∀ (a : Status), a.rank = 0 ↔ a = Status.good` |
| `Spec.adopted_status_per_heir` | Spec.Status | Status after an adoption cut-off is per heir (hunt H4; *Bonner*): — `∀ (inLine : Nat → Bool) (e : Effect) (l : List Effect) (k t u : Nat) (orig : Bool) (reached unreached : List Nat) (a : Nat), e.reach = Reach.lines orig reached unreached …` |
| `Spec.any_congr_mem` | Spec.Lines | `∀ {α : Type} (l : List α) (p q : α → Bool), (∀ (x : α), x ∈ l → p x = q x) → l.any p = l.any q` |
| `Spec.appliesSuperseded_needs_conduct` | Spec.Findings | Hunt H2: — `∀ (c : CiteFacts), appliesSupersededHolding c = true → c.statusAtConduct = some (Status.neg Neg.superseded) ∧ c.holdingMatch = true` |
| `Spec.before_start_no_effect` | Spec.Status | Nor does any effect reach a question date before it starts. — `∀ (e : Effect) (l : List Effect) (k t u : Nat), t < e.start → status (e :: l) k t u = status l k t u` |
| `Spec.claimRisk_needs_no_power` | Spec.Findings | A claim is only reported when the treating court is shown to lack power (T2). — `∀ (r : TreatRisk), claimRisk r = true → r.power = some false ∧ r.kind.changesStatus = true` |
| `Spec.conductUnknown_not_finding` | Spec.Findings | With an unknown conduct date the finding is never made; the low-confidence family is disjoint from it. — `∀ (c : CiteFacts), c.statusAtConduct = none → appliesSupersededHolding c = false` |
| `Spec.conflict_in_line_ignores_unreaching` | Spec.Lines | The resolver's answer at a court (the conflict test) is unchanged by an overruling that does not reach its line (a decision the Fifth Circuit alone overruled still counts for an Eleventh Circuit conflict). — `∀ (inLine : Nat → Bool) (t : Nat) (f : Bool) (s : Option TrialScope) (pre post : List (Held Cand)) (h : Held Cand) (e : Effect), Effect.reaches inLine e = false → resolve…` |
| `Spec.contraryBinding_needs_binding` | Spec.Findings | A contrary-binding risk needs a later holding that binds the holder's court and is good law. — `∀ (f : ContraryFacts), contraryBinding f = true → f.binds = true ∧ f.later = true ∧ f.contraryGood = true` |
| `Spec.division_cannot_overrule` | Spec.AuthorityThms | Hunt H6, *M.A.P. — `∀ (L : Lookups) (X B : CourtEpoch) (b x : Decision), B.court = X.court → L.rules.horizontalCourt X.court x.date = some HRule.strong → b.bench = some Bench.panel ∨ b.bench…` |
| `Spec.effectsFor_known` | Spec.Lines | A court whose line is known reads a decision through `inLine`. — `∀ (L : Lookups) (c : Decision) (effs : List Effect), c.date ≠ 0 → (L.epochAt c.court c.date).isSome = true → effectsFor L c effs = heirEffects (inLine L c) effs` |
| `Spec.erie_one_directional` | Spec.AuthorityThms | §9 22(c), *Erie* one-directional: — `∀ (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query) (S : CourtEpoch), sourceEpoch L x p = some S → adoptionsOf L x = [] → ∀ (r : Force × List RuleId), for…` |
| `Spec.filter_congr_mem` | Spec.Lines | `∀ {α : Type} (l : List α) (p q : α → Bool), (∀ (x : α), x ∈ l → p x = q x) → List.filter p l = List.filter q l` |
| `Spec.foldl_join` | Spec.Status | `∀ (l : List Effect) (k t u : Nat) (s : Status), List.foldl (fun s e => s.join (e.contrib k t u)) s l = s.join (status l k t u)` |
| `Spec.foldl_max_ge` | Spec.Splits | `∀ (cs : List Cand) (m : Nat) (c : Cand), c ∈ cs → c.prec ≤ List.foldl (fun m c => max m c.prec) m cs` |
| `Spec.foldl_max_ge_init` | Spec.Splits | `∀ (cs : List Cand) (m : Nat), m ≤ List.foldl (fun m c => max m c.prec) m cs` |
| `Spec.foldl_max_le` | Spec.Splits | `∀ (cs : List Cand) (n m : Nat), m ≤ n → (∀ (c : Cand), c ∈ cs → c.prec ≤ n) → List.foldl (fun m c => max m c.prec) m cs ≤ n` |
| `Spec.foldl_max_rank_le` | Spec.AuthorityThms | `∀ {α : Type u_1} (g : α → Force) (n : Nat) (l : List α) (init : Force), init.rank ≤ n → (∀ (a : α), a ∈ l → (g a).rank ≤ n) → (List.foldl (fun f a => f.max (g a)) init l)…` |
| `Spec.forceDiv_eq_force` | Spec.AuthorityThms | Hunt H6: — `∀ (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query), q.dst.tier ≠ Tier.last → forceDiv L x h p q = force L x h p q` |
| `Spec.force_le_relation_noAdopt` | Spec.AuthorityThms | With no adoption, the force is at most the relation. — `∀ (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query) (S : CourtEpoch), sourceEpoch L x p = some S → adoptionsOf L x = [] → ∀ (r : Force × List RuleId), for…` |
| `Spec.force_rank_le` | Spec.AuthorityThms | If the relation is bounded on every court, the force is bounded (adoption and caps cannot lift it). — `∀ (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query) (n : Nat), (∀ (S : CourtEpoch), (relation L S x (h.domain.getD ((Option.map CourtEpoch.home (sourceEpo…` |
| `Spec.goodIn_all` | Spec.Lines | With no line-limited effect, good law in a line is good law. — `∀ (inLine : Nat → Bool) (l : List Effect) (k t : Nat), (∀ (e : Effect), e ∈ l → e.reach = Reach.all) → goodIn inLine l k t = goodLaw l k t t` |
| `Spec.goodIn_ignores_unreaching` | Spec.Lines | An overruling that does not reach a line leaves good law in that line as it was. — `∀ (inLine : Nat → Bool) (e : Effect) (l : List Effect) (k t : Nat), Effect.reaches inLine e = false → goodIn inLine (e :: l) k t = goodIn inLine l k t` |
| `Spec.goodLaw_antitone` | Spec.Status | `∀ (l : List Effect) (k u t t' : Nat), t ≤ t' → (∀ (e : Effect), e ∈ l → e.lapse = none) → goodLaw l k t' u = true → goodLaw l k t u = true` |
| `Spec.good_cites_clean` | Spec.Findings | A cited holding that is good law is never reported as overruled, vacated or withdrawn. — `∀ (c : CiteFacts), c.status = Status.good → citesOverruled c = false ∧ citesVacated c = false ∧ citesWithdrawn c = false` |
| `Spec.good_in_every_line` | Spec.Lines | Good law in the union is good law in every line. — `∀ (inLine : Nat → Bool) (l : List Effect) (k t u : Nat), status l k t u = Status.good → statusFor inLine l k t u = Status.good` |
| `Spec.heir_overruling_stays_in_line` | Spec.Status | An heir's own overruling stays in its line: — `∀ (inLine : Nat → Bool) (e : Effect) (l : List Effect) (k t u : Nat) (reached unreached : List Nat), e.reach = Reach.lines false reached unreached → reached.any inLine = …` |
| `Spec.heldIn_all` | Spec.Lines | With no line-limited effect the line test is the old (union) test: — `∀ {α : Type} (inLine : Nat → Bool) (t : Nat) (hs : List (Held α)), (∀ (h : Held α), h ∈ hs → ∀ (e : Effect), e ∈ h.effs → e.reach = Reach.all) → heldIn inLine t hs = held…` |
| `Spec.heldIn_ignores_unreaching` | Spec.Lines | A split or conflict judged in a line ignores overrulings that do not reach that line: — `∀ {α : Type} (inLine : Nat → Bool) (t : Nat) (pre post : List (Held α)) (h : Held α) (e : Effect), Effect.reaches inLine e = false → heldIn inLine t (pre ++ { item := h.i…` |
| `Spec.heldUnion_sub_heldIn` | Spec.Lines | What counts in the union counts in every line. — `∀ {α : Type} (inLine : Nat → Bool) (t : Nat) (hs : List (Held α)) (x : α), x ∈ heldUnion t hs → x ∈ heldIn inLine t hs` |
| `Spec.inferred_treatment_no_effect` | Spec.Status | Inferred treatments never change status (§9 item 26). — `∀ (byHist : List HEvent) (tr : TEvent), tr.explicit = false → treatEffect byHist tr = none` |
| `Spec.lineBase_all` | Spec.Lines | With no line-limited effect a line's base is the old (union) base. — `∀ (inLine : Nat → Bool) (t : Nat) (hs : List (Held FCase)), (∀ (h : Held FCase), h ∈ hs → ∀ (e : Effect), e ∈ h.effs → e.reach = Reach.all) → lineBase inLine t hs = heldU…` |
| `Spec.lineBase_consistent_union` | Spec.Lines | A consistent base in some line makes the union base consistent: — `∀ (inLine : Nat → Bool) (t : Nat) (hs : List (Held FCase)), consistent (lineBase inLine t hs) = true → consistent (heldUnion t hs) = true` |
| `Spec.lineStatus_all` | Spec.Lines | With no line-limited effect every line's row is the union status. — `∀ (ln : Line) (l : List Effect) (k t u : Nat), (∀ (e : Effect), e ∈ l → e.reach = Reach.all) → lineStatus ln l k t u = status l k t u` |
| `Spec.lineStatus_heir_agrees` | Spec.Lines | Per-heir status rows agree with `statusFor`: — `∀ (inLine : Nat → Bool) (a : Nat) (l : List Effect) (k t u : Nat), (∀ (e : Effect), e ∈ l → ∀ (b : Nat), b ∈ e.adopters → inLine b = (b == a)) → statusFor inLine l k t u …` |
| `Spec.lineStatus_orig_agrees` | Spec.Lines | A court in no heir's line reads the original line's row. — `∀ (inLine : Nat → Bool) (l : List Effect) (k t u : Nat), (∀ (e : Effect), e ∈ l → ∀ (b : Nat), b ∈ e.adopters → inLine b = false) → statusFor inLine l k t u = lineStatus …` |
| `Spec.linesOf_all` | Spec.Lines | With no line-limited effect a decision has no per-line rows (its `status.tsv` rows are all there is). — `∀ (l : List Effect), (∀ (e : Effect), e ∈ l → e.reach = Reach.all) → linesOf l = []` |
| `Spec.mem_heldIn_iff` | Spec.Lines | `∀ {α : Type} (inLine : Nat → Bool) (t : Nat) (hs : List (Held α)) (x : α), x ∈ heldIn inLine t hs ↔ ∃ h, h ∈ hs ∧ h.item = x ∧ h.binds = true ∧ statusFor inLine h.effs h.…` |
| `Spec.mem_lineBase_iff` | Spec.Lines | A Horty base in a line contains exactly the precedents good in that line (and binding there). — `∀ (inLine : Nat → Bool) (t : Nat) (hs : List (Held FCase)) (c : FCase), c ∈ lineBase inLine t hs ↔ ∃ h, h ∈ hs ∧ h.item = c ∧ h.binds = true ∧ statusFor inLine h.effs h.i…` |
| `Spec.minDate_attained` | Spec.Splits | `∀ (rest : List Cand) (c : Cand), ∃ d, d ∈ c :: rest ∧ d.date = minDate (c :: rest)` |
| `Spec.neg_stays_neg` | Spec.Status | Without lapse, once negative, always negative; and good law on a later date was good law earlier. — `∀ (l : List Effect) (k u t t' : Nat), t ≤ t' → (∀ (e : Effect), e ∈ l → e.lapse = none) → ∀ (n : Neg), status l k t u = Status.neg n → ∃ n', status l k t' u = Status.neg …` |
| `Spec.no_cross_system` | Spec.AuthorityThms | No cross-system power, absent adoption, except SCOTUS on federal law. — `∀ (L : Lookups) (b x : Decision) (dom : Option Domain) (B X : CourtEpoch), L.epochAt b.court b.date = some B → L.epochAt x.court x.date = some X → B.system ≠ X.system → B…` |
| `Spec.no_overrule_of_binding_superior` | Spec.AuthorityThms | v1 `no_overrule_of_binding_superior`, lifted: — `∀ (L : Lookups) (b x : Decision) (dom : Option Domain) (B X : CourtEpoch), L.epochAt b.court b.date = some B → L.epochAt x.court x.date = some X → B.tier.rank < X.tier.ra…` |
| `Spec.no_panel_overrules_panel_in_strong` | Spec.AuthorityThms | §9 item 23, F7: — `∀ (L : Lookups) (b x : Decision) (dom : Option Domain) (B X : CourtEpoch), L.epochAt b.court b.date = some B → L.epochAt x.court x.date = some X → B.court = X.court → B.t…` |
| `Spec.no_power_over_later` | Spec.AuthorityThms | A decision never has power over a later one. — `∀ (L : Lookups) (b x : Decision) (dom : Option Domain) (B X : CourtEpoch), L.epochAt b.court b.date = some B → L.epochAt x.court x.date = some X → b.date < x.date → canCh…` |
| `Spec.nothing_binds_last_resort` | Spec.AuthorityThms | §9 22(b): — `∀ (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query), q.dst.tier = Tier.last → q.dst.system ≠ 0 → h.domain = some (Domain.stateLaw q.dst.system) → ∀ (r : F…` |
| `Spec.only_scotus_changes_scotus` | Spec.AuthorityThms | Only SCOTUS (or the same court) changes the status of a SCOTUS decision, absent adoption. — `∀ (L : Lookups) (b x : Decision) (dom : Option Domain) (B X : CourtEpoch), L.epochAt b.court b.date = some B → L.epochAt x.court x.date = some X → X.scotus = true → ((ado…` |
| `Spec.panelDeparts_needs_enBanc` | Spec.Findings | A panel departure is only reported when the power check failed for want of an en banc bench. — `∀ (f : TreatFacts), panelDepartsWithoutEnBanc f = true → ∃ r, f.power = some (false, r) ∧ (r = RuleId.strongNeedsEnBanc ∨ r = RuleId.withinUnitEnBanc ∨ r = RuleId.adopted…` |
| `Spec.panelDeparts_needs_panel_and_rule` | Spec.Findings | Hunt H3b: — `∀ (f : TreatFacts), panelDepartsWithoutEnBanc f = true → f.panel = true ∧ f.ruleAtDeparture = true` |
| `Spec.partial_overruling_preserves` | Spec.Status | Partial overruling preserves the other holdings: — `∀ (byHist : List HEvent) (tr : TEvent) (e : Effect), treatEffect byHist tr = some e → ∀ (ks : List Nat), tr.scope = Scope.issues ks → ∀ (l : List Effect) (k : Nat), ¬k ∈ …` |
| `Spec.partial_touches_only` | Spec.Status | Partial events touch only their holdings: — `∀ (e : Effect) (l : List Effect) (k t u : Nat) (ks : List Nat), e.scope = Scope.issues ks → ¬k ∈ ks → k ≠ anonIssue → status (e :: l) k t u = status l k t u` |
| `Spec.prospective_no_effect` | Spec.Status | Prospectivity: — `∀ (e : Effect) (l : List Effect) (k t u : Nat), u < e.conductFrom → status (e :: l) k t u = status l k t u` |
| `Spec.reaches_congr` | Spec.Lines | Two views that agree on the adopters an effect names are reached by it alike. — `∀ (p q : Nat → Bool) (e : Effect), (∀ (b : Nat), b ∈ e.adopters → p b = q b) → Effect.reaches p e = Effect.reaches q e` |
| `Spec.relation_fed_on_state` | Spec.AuthorityThms | `∀ (L : Lookups) (S : CourtEpoch) (x : Decision) (s : Nat) (q : Query), S.system = 0 → q.dst.system ≠ 0 → (relation L S x (Domain.stateLaw s) q).fst = Force.persuasive` |
| `Spec.relation_lastResort_own_law` | Spec.AuthorityThms | `∀ (L : Lookups) (S : CourtEpoch) (x : Decision) (q : Query), q.dst.tier = Tier.last → q.dst.system ≠ 0 → (relation L S x (Domain.stateLaw q.dst.system) q).fst.rank ≤ Forc…` |
| `Spec.relation_scotus_federal` | Spec.AuthorityThms | `∀ (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query), S.scotus = true → dom.federal = true → q.dst.tier ≠ Tier.last → relation L S x dom q = (Force.…` |
| `Spec.relation_state_on_federal` | Spec.AuthorityThms | `∀ (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query), S.system ≠ 0 → dom.federal = true → q.dst.system = 0 → relation L S x dom q = (Force.persuasiv…` |
| `Spec.relation_trial` | Spec.AuthorityThms | `∀ (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query), S.tier = Tier.trial → (relation L S x dom q).fst.rank ≤ Force.persuasive.rank` |
| `Spec.resolve_agree` | Spec.Splits | If the binding sub-base agrees, the resolver returns it unchanged (no choice is needed). — `∀ (f : Bool) (s : Option TrialScope) (cs : List Cand), agree (top cs) = true → resolve f s cs = top cs` |
| `Spec.resolve_nonempty` | Spec.Splits | With some binding candidate, the resolver is never empty. — `∀ (f : Bool) (s : Option TrialScope) (cs : List Cand), (∃ c, c ∈ cs ∧ c.counts = true) → resolve f s cs ≠ []` |
| `Spec.resolve_sound` | Spec.Splits | The resolver only returns candidates it was given, and only binding-sub-base ones. — `∀ (f : Bool) (s : Option TrialScope) (cs : List Cand) (c : Cand), c ∈ resolve f s cs → c ∈ cs ∧ c.counts = true` |
| `Spec.resolve_sub_top` | Spec.Splits | `∀ (f : Bool) (s : Option TrialScope) (cs : List Cand) (c : Cand), c ∈ resolve f s cs → c ∈ top cs` |
| `Spec.revival_counterexample` | Spec.Status | Revival refutes unrestricted monotonicity (T3): — `∃ l k u t t', t ≤ t' ∧ status l k t u = Status.neg Neg.overruled ∧ status l k t' u = Status.good` |
| `Spec.same_day_events_commute` | Spec.Status | Two events (e.g. — `∀ (l₁ l₂ : List Effect) (e₁ e₂ : Effect) (k t u : Nat), status (l₁ ++ e₁ :: e₂ :: l₂) k t u = status (l₁ ++ e₂ :: e₁ :: l₂) k t u` |
| `Spec.scotus_binds_federal` | Spec.AuthorityThms | §9 22(a): — `∀ (L : Lookups) (x : Decision) (h : Holding) (q : Query) (S : CourtEpoch), L.epochAt x.court x.date = some S → S.scotus = true → (∀ (d : Domain), h.domain = some d → d.fe…` |
| `Spec.scotus_resolves` | Spec.Splits | A binding SCOTUS holding resolves the issue for every court it binds: — `∀ (f : Bool) (s : Option TrialScope) (cs : List Cand) (a : Answer), (∃ c, c ∈ cs ∧ c.prec = scotusPrec ∧ c.force = Force.binding ∧ c.answer = a) → (∀ (c : Cand), c ∈ cs →…` |
| `Spec.scotus_resolves_split` | Spec.Splits | A later binding SCOTUS holding resolves any split among the courts it binds. — `∀ (f₁ f₂ : Bool) (s₁ s₂ : Option TrialScope) (cs₁ cs₂ : List Cand) (a : Answer) (b : Bool), (∃ c, c ∈ cs₁ ∧ c.prec = scotusPrec ∧ c.force = Force.binding ∧ c.answer = a) …` |
| `Spec.soft_claim_disjoint` | Spec.Findings | Soft and claim risks never coincide: — `∀ (r : TreatRisk), (!decide ((softRisk r && claimRisk r) = true)) = true` |
| `Spec.soft_treatment_no_effect` | Spec.Status | Soft treatments never change status (§5.2 T1). — `∀ (byHist : List HEvent) (tr : TEvent), tr.kind.changesStatus = false → treatEffect byHist tr = none` |
| `Spec.statusFor_all` | Spec.Status | Where every effect reaches every line (no heir, or only history, statutes and SCOTUS), status does not depend on the court asking. — `∀ (inLine : Nat → Bool) (l : List Effect) (k t u : Nat), (∀ (e : Effect), e ∈ l → e.reach = Reach.all) → statusFor inLine l k t u = status l k t u` |
| `Spec.statusFor_congr` | Spec.Lines | Status in a line depends only on which effects reach the court. — `∀ (p q : Nat → Bool) (l : List Effect) (k t u : Nat), (∀ (e : Effect), e ∈ l → Effect.reaches p e = Effect.reaches q e) → statusFor p l k t u = statusFor q l k t u` |
| `Spec.statusFor_le_status` | Spec.Lines | The union status (`status.tsv`) is at least as severe as the status in any line. — `∀ (inLine : Nat → Bool) (l : List Effect) (k t u : Nat), (statusFor inLine l k t u).rank ≤ (status l k t u).rank` |
| `Spec.status_cons` | Spec.Status | `∀ (e : Effect) (l : List Effect) (k t u : Nat), status (e :: l) k t u = (e.contrib k t u).join (status l k t u)` |
| `Spec.status_cons_good` | Spec.Status | An effect that contributes nothing leaves the status unchanged. — `∀ (e : Effect) (l : List Effect) (k t u : Nat), e.contrib k t u = Status.good → status (e :: l) k t u = status l k t u` |
| `Spec.status_filter_le` | Spec.Lines | `∀ (p : Effect → Bool) (l : List Effect) (k t u : Nat), (status (List.filter p l) k t u).rank ≤ (status l k t u).rank` |
| `Spec.status_mono` | Spec.Status | Monotonicity (§9 22(e), generalising v1 `overruledOn_mono`): — `∀ (l : List Effect) (k u t t' : Nat), t ≤ t' → (∀ (e : Effect), e ∈ l → e.lapse = none) → (status l k t u).rank ≤ (status l k t' u).rank` |
| `Spec.status_mono_conduct` | Spec.Status | Status only worsens as the conduct date advances (every effect reaches later conduct if it reaches earlier). — `∀ (l : List Effect) (k t u u' : Nat), u ≤ u' → (status l k t u).rank ≤ (status l k t u').rank` |
| `Spec.status_perm` | Spec.Status | Status does not depend on the order of the events. — `∀ {l₁ l₂ : List Effect}, l₁.Perm l₂ → ∀ (k t u : Nat), status l₁ k t u = status l₂ k t u` |
| `Spec.status_rank_mono_of` | Spec.Status | `∀ (l : List Effect) (k t u t' u' : Nat), (∀ (e : Effect), e ∈ l → (e.contrib k t u).rank ≤ (e.contrib k t' u').rank) → (status l k t u).rank ≤ (status l k t' u').rank` |
| `Spec.supersession_prospective` | Spec.Status | Supersession is prospective (§7 AB1): — `∀ (s : SEvent) (e : Effect), superEffect s = some e → ∀ (l : List Effect) (k t u : Nat), u < s.retroactiveTo.getD s.effective → status (e :: l) k t u = status l k t u` |
| `Spec.top_sub` | Spec.Splits | `∀ (cs : List Cand) (c : Cand), c ∈ top cs → c ∈ cs ∧ c.counts = true` |
| `Spec.trial_never_binding` | Spec.AuthorityThms | §9 22(d), F13/§4.4: — `∀ (L : Lookups) (x : Decision) (h : Holding) (q : Query) (S : CourtEpoch), L.epochAt x.court x.date = some S → S.tier = Tier.trial → adoptionsOf L x = [] → ∀ (r : Force ×…` |
| `Spec.unionBase_sub_lineBase` | Spec.Lines | The union base is inside every line's base. — `∀ (inLine : Nat → Bool) (t : Nat) (hs : List (Held FCase)) (c : FCase), c ∈ heldUnion t hs → c ∈ lineBase inLine t hs` |

## Known episodes replayed (`Examples.lean`)

- *Betts*/*Gideon* and *Bowers*/*Lawrence* (status by date, power, H1 self); a district court citing *Bowers* in 2005
  (`citesOverruled`).
- **Kentucky 1976.** A 1970 old Court of Appeals decision binds the new Court of Appeals in 1990, which cannot
  overrule it; the Supreme Court of Kentucky can (`lastResortSelf`).
- **Bonner.** Pre-split 5th Cir. law binds the 11th; post-split law is persuasive; panel no, en banc yes.
- **South Corp.** CCPA law binds the Federal Circuit, and district courts on patent law only.
- ***M.A.P. v. Ryan*.** Cross-system adoption: pre-1971 D.C. Cir. law binds D.C. courts; later law does not.
- ***Erie*** both ways and on both sides of 1938.
- **California Court of Appeal conflict.** The superior court gets both answers (choice); under an own-unit rule it
  follows its district; a SCOTUS holding ends the conflict.
- **Georgia partial overruling.** Notice falls, venue stands, the anonymous issue is `unknown:partialScope`.
- ***Ledbetter*.** Superseded for conduct from 28 May 2007, known from 29 Jan 2009.
- **The 5th Cir. 1996 unpublished cut-off.**
- **A *Sunburst* prospective overruling.**
- **Revival.**
- **En banc grant under an unknown rule** -> `unknown`.
- **Status per line (round 2).** The *Salinas* / *Adamson* decision has two status rows, `orig` overruled and the
  Eleventh Circuit's good; a conflict between it and a later Eleventh Circuit panel exists in the Eleventh Circuit
  and not in the Fifth; a Horty base holding both is inconsistent in the Eleventh's line and consistent in the
  Fifth's. A pre-1971 D.C. Circuit decision that court later overruled en banc is still good law for the D.C. Court
  of Appeals and the Superior Court (*M.A.P.*). The Federal Circuit en banc reaches every line of a CCPA decision
  (the original court is gone).
- **Certificates.** Gideon's own words are admitted; a wrong offset, a dissent, a wrong target, no power, a procedural
  "point of error is overruled" and a reported "overruled by" are all rejected.

## Mutation results (DESIGN D3; `Mutants.lean`, `#eval killMatrix`)

| Property (registered theorem family) | Killed by |
|---|---|
| scotus_binds_federal | M11 SCOTUS persuasive |
| nothing_binds_last_resort | M1 Erie both ways, M10 trial courts bind, M12 intermediate binds last resort |
| erie_one_directional | M1 Erie both ways |
| trial_never_binding | M10 trial courts bind |
| no_panel_overrules_panel_in_strong | M2 panel overrules panel, M15 no power check |
| only_scotus_changes_scotus | M15 no power check |
| status_perm | M13 order-dependent status |
| partial_touches_only | M4 ignore partial scope |
| supersession_prospective | M5 supersession retroactive |
| status_mono / dated effect | M17 effects before their date |
| revival (lapse honoured) | M6 revival ignored |
| soft_treatment_no_effect | M14 soft treatments count |
| checkCert_sound: part | M7 cert accepts dissents |
| checkCert_sound: disqualifier | M8 cert without disqualifiers |
| checkCert_sound: quote at offset | M9 cert without quote check |
| checkCert_sound: admits Gideon | M18 cert off-by-one offsets |
| unpublished cap (F9) | M3 ignore unpublished |
| scotus_resolves_split | M16 resolver ignores precedence |
| checkCert_window_hash | M19 cert trusts window text |
| checkCert_cite_index | M20 cert ignores citation index |
| adopted_status_per_heir (Bonner) | M21 status global after adoption cut-off |
| division_cannot_overrule (M.A.P.) | M2, M15, M22 divisions overrule the court |
| lineStatus_heir_agrees (Bonner rows) | M23 line rows report the union status |
| heldIn_ignores_unreaching (Salinas conflict) | M24 splits and conflicts on the union status |
| mem_lineBase_iff (Horty base in a line) | M25 Horty base keeps precedents overruled in the line |
| lineStatus_all / heldIn_all (no heir: union) | M26 heir rows drop effects that reach every line |

Every property holds of the Spec, and every mutant is caught (`#guard`s in `Mutants.lean`).

## Statement lock (DESIGN D2)

- `audit/audit.py check` lists every theorem from the Lean environment (`audit/ListTheorems.lean`). It then
  elaborates `#check @thm` and `#print axioms thm` (`lean --json`) and compares each with `audit/statements.lock`.
  It also checks that the axioms are within {propext, Classical.choice, Quot.sound}, and that no CaseLaw2 source
  contains sorry, admit, native_decide or an axiom declaration. Exit 1 on any problem.
- `audit/audit.py lock --reason "..."` accepts the current statements. It rewrites `statements.lock`, `Registry.lean`
  and `Audit.lean`, and appends every new, changed or removed statement to `STATEMENTS.log`.
- **Policy:**
  - a weakened statement is escalated as a probable spec or data bug;
  - a false property is refuted (its counterexample kept, as with `revival_counterexample`), never weakened.
- `Audit.lean` is part of `lake build LegalProofs.CaseLaw2`, so a changed statement fails the build itself.

## Runner

    ./run_lean.sh <shards> [data-dir] [edges-dir] [out-dir] [asOf]
      defaults: data = caselaw-lean-2/data, edges = ../lean-in-v3 (v1's edges-00..15.tsv, citing -> cited),
                out = caselaw-lean-2/out, asOf = 20261112
    ./run_lean.sh 2 fixtures/data fixtures/edges fixtures/out      # fixtures (python fixtures/make_fixtures.py)
    INTERP=1 ./run_lean.sh ...                                       # force the interpreter

**How it runs:**
- **Build and fallback.** It builds the compiled runner (`runner/`, a Lake package that requires lean-proofs by
  path; lean_exe `caselaw2`, root `Main`, which imports `LegalProofs.CaseLaw2.Run`). If Windows Application Control
  blocks the .exe, it falls back to `lake env lean --run LegalProofs/CaseLaw2/Run.lean` with the same results.
- **Sharding.** It runs N shards, 8 at a time. Shard k reads every `edges-j.tsv` with j % N = k, and handles
  status for nodes with node % N = k, certs and treatment findings for rows with id % N = k, and splits for issues
  with index % N = k.
- **Output.** Merged files go in `out/`, each with a header line.

**Measured, compiled, at full scale** (6.89M decision rows, synthetic SCHEMA decisions2): load 35 s, then 6.04M
citations in 10 s on one process. A 16-file run at 8-way is about 1 minute; interpreted it is about 8 minutes.

**Inputs** (SCHEMA.md, exactly):
- `courts2`, `succession`, `adoption`, `system_rules`, `decisions2`, `history`, `treatments`, `cert_text`, `issues`,
  `holdings`, `marks`, `lawchanges`, `supersessions`.
- Approved optional files:
  - `decisions2_extra.tsv`: node, appeal_venue, transfer_from (0 = none);
  - `factors.tsv`: holding_id, factor (Nat), side (pi|delta), inReason (0/1).
- The approved system rule `reviewGrantedForce` (value: a Force), court- or system-level.
- A missing file loads as empty; bad rows are counted in `summary.tsv`.

### Output formats (for the differential tester, D4)

Each row's **justification path** (D8) is a `>`-joined list of `RuleId` labels (Spec/RuleId.lean).

**firm** (D2) is 1 when the S/L-only tables give the same verdict as the tables with U rows.

**Classes** (D5):
- `negativeAdmitted` = `neg:*`;
- `noneAdmitted` = `good`;
- `unknown` = `unknown:partialScope`, `unknown:enBancRuleUnknown` or `unknown:powerUnknown` (D4: an explicit
  treatment whose power the data leave open).

`out/status.tsv` has these columns:

| Column | Meaning |
|---|---|
| node | decision node id |
| issue | issue key; `-` is the anonymous issue |
| holding | holding id or `-` |
| from, to | the interval of question dates, with t = u (conduct = question date); rows break wherever an effect starts, lapses or starts reaching conduct, in either rule instance |
| status | `good`, `neg:{reviewPending,superseded,abrogated,overruled,reversed,depublished,vacated,withdrawn}`, or `unknown:{partialScope,enBancRuleUnknown,powerUnknown}` |
| class | as above |
| firm | as above |
| witness_row | the reader's row id (history/treatment/supersession; strings, e.g. `t:<by>:<target>:<start>`) of the most severe live effect |
| actor | the decision that caused it |
| path | the witness effect's rule: `history`, `treatment`, `prospective` or `supersession` |

Rows cover every node with an admitted event or an extracted holding. `status.tsv` is the **union status**: negative
if negative in any line of authority. It is unchanged by round 2.

`out/status_lines.tsv` (round 2, DEVIATIONS 75) has the same eleven columns and a twelfth:

| Column | Meaning |
|---|---|
| line | `orig` (a court in no heir's line) or the court id of an heir (a binding adopter) |

It holds rows only for decisions with a **line-limited effect** in the all-tables run (an overruling that reaches
some lines of authority and not others, DEVIATIONS 69): one block per pure line, each block being what `status.tsv`
would hold if only the effects reaching that line existed (`Spec.lineStatus`). `firm` compares with the S/L run's
status in the same line. A court in several heirs' lines reads the more severe of their rows. Decisions without an
heir have no rows here.

`out/findings.tsv` has these columns:

| Column | Meaning |
|---|---|
| finding | one of the kinds below |
| citing | citing node |
| cited | cited node |
| issue | `-` = whole decision |
| detail | the cited status, force or kind |
| firm | as above |
| path | force path, plus power rule for treatment findings |

Finding kinds:
- `citesOverruled`, `citesVacated`, `citesWithdrawn`, `citesNotCitable` and `appliesSupersededHolding` (also per
  holding, issue-aware) come from the 48M citation edges.
- `citesUnpublishedAsBinding`, `pluralityTreatedAsBinding`, `panelDepartsWithoutEnBanc` and `ignoresBindingInUnit`
  come from treatment rows.
- `atRisk` has three sources:
  - `inferredRejection` (the citing column holds the target, the cited column the treating decision);
  - `inferredSupersession`;
  - `citesLaterNegated:<status>`: the citing decision cites a decision that has since been negated by a court that
    binds it.
- `inconsistentBindingBase` (Horty, with factors.tsv).

`out/certs.tsv` has these columns:

| Column | Meaning |
|---|---|
| table | treatment, history or holding |
| id | row id |
| result_all | result with the full tables |
| result_firm | result with the firm tables |

Results:
- treatment and history rows: `ok`, `okUnverifiedBy`, or one of `shaUnknown`, `noWindow`, `quoteMismatch`, `noCue`,
  `disqualified`, `targetUnresolved`, `partNotMajority`, `targetLater`, `noAuthority`, `badRow`;
- holdings: `ok`, `shaUnknown`, `quoteMismatch` or `badRole`.

`out/splits.tsv` has these columns:

| Column | Meaning |
|---|---|
| kind | `split` (DESIGN layer 5: two good-law holdings with opposite answers by courts neither of which binds the other, not resolved by a holding binding both; D4) or `conflict` (one bound court whose permissible answers include both) |
| issue | issue key |
| court1, court2 | `court[/unit]` |
| answers1, answers2 | the resolved answers |
| holdings1, holdings2 | the holdings behind them |
| asOf | the date examined |
| firm | as above |

`out/horty.tsv` (round 2, DEVIATIONS 78; header only when there is no `factors.tsv`) has these columns:

| Column | Meaning |
|---|---|
| family | the family issue key |
| court | one examined court whose binding base this is |
| verdict | `consistent` or `inconsistent` |
| cases | the base: holding ids, sorted, comma-joined |
| firm | as above |

One row per distinct binding base of a family, the same bases as the `inconsistentBindingBase` /
`hortyConsistentBase` rows of `findings.tsv`. A base holds the precedents that bind the court and are good law in
its line.

`out/summary.tsv` holds per-shard counters: rows admitted and rejected, status rows, per-line status rows
(`status_line_rows`), findings, splits, edges, timings, and bad input rows.

## SCHEMA additions used (all approved in D9; SCHEMA.md itself not edited)

- Optional `decisions2_extra.tsv` (node, appeal_venue, transfer_from).
- Optional `factors.tsv` (holding_id, factor, side, inReason).
- The system rule `reviewGrantedForce`.
- **New conventions to confirm** (these are interpretations of the schema, not new files):
  - the `unitB` adoption filter = decisions whose `unit` is 2;
  - `epoch_to`/`upTo`/rule `to` = 0 is read as open-ended;
  - `prospectiveFrom:yyyymmdd` dates are parsed from the temporal column.

## Differential testing (D4, 2026-11-12)

The runner was diffed against the independent Python reference (`tools/caselaw2/ref/`) on the fixtures, on 15,000+
generated universes and on the real data: see `DIFFTEST.md`. Changes it made here:
- **Glue:** string row ids for history and treatments (the reader's ids); holdings admitted only through their
  certificate; per-issue power for treatments; the layer-5 split test; finding rules (DEVIATIONS 53); state circuits
  for E3; `retroactive_to = 1`.
- **Spec:** `Scope.someOf`, `SEvent.scope`, `TEvent.powerKnown`, `Unk.powerUnknown`, `Status.partially`,
  `treatEffects` (revival on reinstatement), `vacatingGrants`, and refinements to `canChangeStatus`, `fedHier`,
  `relation`, `formCap`, `horizontalForce`, `lapseOfDecision`, `histEffect`,
  `citesOverruled` and `histPower`.
- **Locks:** no theorem statement changed. Two proofs in `Spec/AuthorityThms` now use their no-adoption hypothesis
  directly. `revival_counterexample` now also uses `propext` (logged in STATEMENTS.log).

## Five limits (2026-11-12)

| Limit | Lean change |
|---|---|
| 1. firm by another route (seed 30984) | `Run.lean`: citation rows are computed per rules instance by both routes (whole decision, holding by holding); a row is firm when the S/L run makes the same finding on the same status by any route. `citesLaterNegated` firm computed (was hard-coded 1). DEVIATIONS 61 |
| 2. one-sided finding kinds | `Spec/Findings`: `TKind.softNegative`, `TreatRisk`, `softRisk`, `claimRisk`, `ContraryFacts`, `contraryBinding`; `ignoresBindingInUnit` narrowed to §9 item 27 (`VownUnit`/`appDivBinds`, no power). `Run.lean` emits `atRisk soft:/claim:/contraryBinding:` (source, subject). Conflict candidates prepared as DEVIATIONS 67; `Exec/Verdicts.candFor` ranks adopted decisions as their adopter. DEVIATIONS 66–67 |
| 3. certificates resolve the target | `Certificate`: `Input.target`, `Input.citeIndex` (compact citation → node), `citeResolves`; `Run.lean` loads `cite_index.tsv` (`buildCiteIndex`, ambiguous keys dropped). DEVIATIONS 64 |
| 4. window hashes in Lean | new `Sha1.lean` (pure SHA-1, 16 `#guard` vectors); `Certificate`: `Window.hash`, cached `Window.digest` with `digest_eq`, `wellFormed`/`hashOk`/`usable`, reason `windowHash`; `Run.lean` loads `window_sha.tsv`. DEVIATIONS 65 |
| 5. commission opinions | `Courts`: `Notation`, `AdoptFilter` gains `opinionAdopted/holdingApproved/judgmentAdopted/noNotation`, `admits` reads the notation; `Holdings`: `Decision.commission`; `Rules.trialScope` keyed by court as well (court-level rows); `Events`: `HEvent.promotes`; `Spec/Status.promotedAt` honours it; `Run.lean`: `commission.tsv`, `forceOrResultOnly`, `texasSystems`, `writPromotes`. DEVIATIONS 62–63 |

New theorems (registered and locked, `STATEMENTS.log` 19:07): `Cert.checkCert_window_hash`, `Cert.checkCert_cite_index`,
`Cert.Window.digest_eq`, `Spec.claimRisk_needs_no_power`, `Spec.soft_claim_disjoint`, `Spec.contraryBinding_needs_binding`.
New `#guard`s: 16 SHA-1 vectors (`Sha1.lean`), 8 certificate replays (hash ok / wrong / missing / tampered; index ok /
wrong target / missing key / name evidence) in `Examples.lean`.

## Fuzz fixes and Horty runner needs (2026-11-12; compiled and verified under WSL the same evening)

- **FUZZ_BUGS FB-L1–L8, FB-R1:** `Data.lean` (exactly 9 decision fields; `explicit` 0/1, `confidence`/`score` must
  parse), `Certificate.lean` (`quoteAt` needs a non-empty quote at a non-empty span; `coveringWindow` = first usable
  window that carries the quote, so the verdict does not depend on window order), `Run.lean` (holdings check their
  certificate's `part`; bad edge lines counted as `bad_edges`), `Events.lean` (`prospectiveFrom:` digits only),
  `run_lean.sh` (node count ignores non-digit and > 8-digit ids), `reader/certify.py` (`clean()` maps CR).
- **New theorem** (registered and locked, STATEMENTS.log 20:38): `Cert.checkCert_quote_nonempty` — an admitted row has
  `quote ≠ ""` and `start < stop`. No existing statement changes; `checkCert_sound`'s proof gains one case split.
- **Horty (FACTORS_NEEDS.md):** the runner reads the optional `factor_cases.tsv` (holding → family issue, outcome); a
  holding with factor rows enters its family's base (else its own issue's, with its yes/no answer). Bases are checked
  at every holder court, one trial court per system/circuit, and the first federal court of appeals when a federal
  court holds (so SCOTUS-only bases are examined); a base is the good-law cases whose force there is at least
  bindingAbsentConflict (`Cand.counts`). Findings: `inconsistentBindingBase` (detail = the first conflicting pair
  `h1,h2`), `hortyConsistentBase` (detail = `N cases`), one row per distinct base; and, informational,
  `hortySelfInconsistent` per holder court's own base. `summary.tsv` counts `horty_bases`, `horty_inconsistent`,
  `horty_self_bases`, `horty_self_inconsistent`. Factors stay data, never premises: no new theorem.

**First compile (WSL).** Three things did not compile or run as written: `checkCert_sound`'s proof (one stale
`simp only` line after the FB-L3 `coveringWindow`), the `FCase` literal in the Horty block, and the
`factor_cases.tsv` loader, which asked for 10 columns where the file has 11 (every row would have been a bad row).
No locked statement changed. On the fixtures the Horty block gives `inconsistentBindingBase 346 fx.hortyA hA1,hA3`,
`hortyConsistentBase 346 fx.hortyB 2 cases` and `hortySelfInconsistent 2906 fx.hortyA hA1,hA3`. The real factors are
in DIFFTEST.md §8.

## Running under WSL (2026-11-12)

    ./run_lean_wsl.sh sync [code|data|all]     # copy the Windows tree (source of truth) into ~/caselaw2 in WSL
    ./run_lean_wsl.sh build                    # lake build LegalProofs.CaseLaw2 + Run, and the native runner
    ./run_lean_wsl.sh audit [check|lock]       # audit/audit.py; lock, Registry, Audit and the log are copied back
    ./run_lean_wsl.sh run 8 data ../lean-in-v3 out   # run_lean.sh in the mirror; out/*.tsv copied back to Windows
    ./run_lean_wsl.sh sh '<command>'           # anything else, in the mirror's caselaw-lean-2/

- **Setup, once:** in WSL Ubuntu, the official elan installer, non-interactive
  (`curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain
  leanprover/lean4:v4.35.0`). `docker-desktop` is the default distro, so every call passes `-d Ubuntu`.
- **Mirror:** `wsl/sync.sh` rsyncs `lean-proofs/` (without `.lake`, `data`, `video`) to `~/caselaw2/lean-proofs`, and
  `runner/`, `audit/`, `fixtures/`, `data/*.tsv`, the edge shards and the node count under
  `~/caselaw2/us-caselaw-lean-work/`, the same relative layout as on Windows (`~/Documents` in WSL is a link to
  `~/caselaw2`, so the tools' paths hold). Edits are made on Windows and re-synced; nothing is edited in WSL.
- **`run_lean.sh` is the same script on both systems:** it finds lean-proofs beside the work tree, drops the `.exe`
  suffix on Linux, reads `graph/nodes.count` when `nodes.tsv` is not there, and takes `PAR` (parallel shards).
- **Verification driver:** `wsl/verify.sh fixtures|regress|sweep|fuzz|real` (DIFFTEST.md §8); `wsl/collect.sh` copies
  the final outputs back.
- **Quoting:** `wsl.exe -- bash -lc '<inline>'` re-parses the line in an outer shell (`$(…)` and `$VAR` are
  mangled), so every command is a script file run with `bash -l <file>`; Git Bash needs `MSYS_NO_PATHCONV=1`.
- **The VM stops when no `wsl.exe` session is attached.** A job must stay attached to its `wsl.exe` call (or a
  keep-alive session must be open); `nohup … &` inside a call that returns is killed.
- **Measured (24 cores):** clean build of `LegalProofs.CaseLaw2` and the runner about 35 s; `audit.py check` about
  20 s; the full real run (6,892,454 decisions, 48,318,876 citation edges, 8 shards) 1.5 to 2.7 minutes depending on
  what else is running; the reference 47 to 66 s.

## Hunt fixes (2026-11-12, evening; HUNT.md "What to fix")

| Item | Lean change |
|---|---|
| H2 `appliesSupersededHolding` (0 of 20 right) | `Spec/Findings`: `CiteFacts.statusAtConduct` is an `Option` (no conduct date in SCHEMA: `none`), `holdingMatch`; the finding needs both; new `supersededConductUnknown`. `Run.lean` emits `atRisk supersededConductUnknown:<issue>` on a holding-level match (same issue, or the US Code block the law rewrote). DEVIATIONS 70 |
| H3b `panelDepartsWithoutEnBanc` | `TreatFacts.panel` = a known panel or division; `ruleAtDeparture` (`Exec.strongRuleAt`): the rule covers the treating date too; no finding for a federal court of appeals before 1 Sept 1948 (`enBancStatuteDate`). Ohio and Louisiana rows dated in the data. DEVIATIONS 71 |
| H4 status after an adoption cut-off | `Spec/Status`: `Reach`, `Effect.reach`, `heirsOf`, `reachOf`, `inLine`, `effectsFor`, `statusFor`; `effectsOf` stamps each treatment effect with the lines it reaches; `Exec.citeFacts` and the citation pass read the cited decision through the citing court's line. DEVIATIONS 69 |
| H6 D.C. Court of Appeals divisions | `Courts`: `Rules.horizontalCourt` (the court-level row alone); `Spec/Authority`: `divisionRelation`, `relationDiv`, `forceDiv`, `lastResortBench`, `adoptedLastResortBench`; `Exec.forceOn` uses `forceDiv`. `nothing_binds_last_resort` is unchanged and still proved. DEVIATIONS 68 |
| Hunt module | `Hunt.lean` imported by `Core`; its 14 theorems registered |

New theorems (locked, STATEMENTS.log 21:05): `Spec.forceDiv_eq_force`, `Spec.division_cannot_overrule`,
`Exec.exec_forceDiv_eq_spec`, `Spec.adopted_status_per_heir`, `Spec.heir_overruling_stays_in_line`,
`Spec.statusFor_all`, `Spec.appliesSuperseded_needs_conduct`, `Spec.conductUnknown_not_finding`,
`Spec.panelDeparts_needs_panel_and_rule`, and the 14 of `Hunt`.

New `#guard`s (`Examples.lean`): the *Salinas* / *Adamson* pattern (a 1983 Fifth Circuit en banc overruling of a
pre-split decision is `good` for the Eleventh Circuit and its district courts, `overruled` for the Fifth, its
district courts and an outside court; the reverse for an Eleventh Circuit en banc overruling; an overruling before
the cut-off and a SCOTUS overruling reach every line); *M.A.P. v. Ryan* (a D.C. Court of Appeals division is bound
by, and cannot overrule, the court's decision; the court en banc can; the Spec's `force` on the court itself stays
persuasiveStrong); the Ledbetter supersession with and without a conduct date and a holding match.

New output rows: `findings.tsv` `atRisk <citing> <cited> <issue> supersededConductUnknown:<issue>`;
`hortyConsistentBase`, `hortySelfInconsistent`; `summary.tsv` `bad_edges`, `horty_bases`, `horty_inconsistent`,
`horty_self_bases`, `horty_self_inconsistent`. `status.tsv` is unchanged in form: it reports the union status
(negative if negative in any line of authority); the per-heir reading is applied to the citation findings. (Round 2, below, carries it to the rest and adds `status_lines.tsv`.)

## Round 2: status per line of authority everywhere (2026-11-12, night; DEVIATIONS 73–79)

H4 applied per-heir status to the citation findings only (DEVIATIONS 69 limit (b)). Round 2 carries it to every
place a status is read.

| Where | Lean change |
|---|---|
| Status rows | `Spec/Lines`: `Line` (`orig`, `heir a`), `linesOf`, `lineStatus`. `Run.lean` writes `status_lines.tsv` for decisions with a line-limited effect; `status.tsv` is byte for byte what it was. DEVIATIONS 75 |
| Treatment-level families | `Run.lean`: `panelDepartsWithoutEnBanc`, `ignoresBindingInUnit`, `atRisk soft:/claim:/inferredRejection` read the target's status through `effectsFor` for the treating decision; `contraryBinding` reads holder and contrary holding in the holder court's line on the contrary holding's date. DEVIATIONS 76 |
| Conflicts | `Run.lean`: the good-law holdings at a bound court are `heldVia (effectsFor L court)`. DEVIATIONS 77 |
| Splits | `Run.lean`: each side good law in its own court's line; "does not bind" also when the holding is not good law in the other court's line; a resolver must be good law in both lines. DEVIATIONS 77 |
| Horty bases | `Run.lean`: a case is live when good law in some pure line (`liveSomewhere`); the base at a court is `heldVia (effectsFor L court)` over the live cases; new `horty.tsv`. DEVIATIONS 78 |
| Split successors | no Lean change: inheritance was already read from adoption rows only. The Alabama Court of Criminal Appeals row is now tagged S. DEVIATIONS 73 |

`effectsFor` is unchanged: a court with no epoch on the date, or an undated decision, reads every effect (the union).
`effectsFor_known` proves it is `heirEffects (inLine L c)` otherwise, which is what the theorems speak of.

**New theorems** (23, `Spec/Lines`, locked, STATEMENTS.log 22:08):
- per-line rows agree with `statusFor`: `lineStatus_heir_agrees`, `lineStatus_orig_agrees` (through `statusFor_congr`,
  `reaches_congr`, `filter_congr_mem`, `any_congr_mem`);
- a split or conflict judged in a line ignores overrulings that do not reach it: `goodIn_ignores_unreaching`,
  `heldIn_ignores_unreaching`, `conflict_in_line_ignores_unreaching`, with `mem_heldIn_iff`;
- a Horty base in a line contains exactly the precedents good in that line: `mem_lineBase_iff`;
- with no line-limited effect everything is the old (union) definition: `lineStatus_all`, `linesOf_all` (no extra
  rows), `goodIn_all`, `heldIn_all`, `lineBase_all`;
- the union bounds every line: `status_filter_le`, `statusFor_le_status`, `good_in_every_line`,
  `heldUnion_sub_heldIn`, `unionBase_sub_lineBase`, `lineBase_consistent_union` (an inconsistency among precedents good
  everywhere is one in every line);
- `effectsFor_known`.

**New mutants and properties** (`Mutants.lean`): M23 line rows report the union status; M24 splits and conflicts on
the union status; M25 a Horty base that keeps precedents overruled in the line; M26 heir rows that drop effects
reaching every line. Four new properties, one killed by each. The matrix is 26 × 26 and complete.

**New `#guard`s** (35, `Examples.lean`): the per-line rows of the *Salinas* decision and of the Eleventh Circuit's
own en banc overruling; no rows for a decision without heirs; *M.A.P.* (the pre-1971 D.C. Circuit decision, good for
the D.C. Court of Appeals and the Superior Court, overruled for the D.C. Circuit); the Federal Circuit en banc on a
CCPA decision (original court gone) and decisions dated outside their court's epoch (reach `all`); the holdings that
count in the Eleventh Circuit, the Northern District of Georgia, the Fifth Circuit and the Northern District of Texas;
a court with no epoch reads the union; the conflict that exists only in the Eleventh Circuit; the Horty base that is
inconsistent only there.

`run_lean.sh` merges the two new per-shard files (`status_lines`, `horty`).

## Round 3: a ceased deciding court among conflict candidates (2026-11-12, late night; DEVIATIONS 80)

- `Exec/Verdicts.lean`: `lastEpoch` (the last epoch of a court that ended before a date) and `forceOnAs` (`forceDiv`
  on a court asked in a given epoch). `Run.lean`: the resolver's `bindsAt` asks a deciding court with no epoch on asOf
  as it last sat. Only the displacement test among conflict candidates changed.
- No theorem was added and no statement changed: 137 theorems, 26 × 26 mutants, as in round 2. The two new
  definitions are runner glue and are not covered by a theorem.
- The implicit-overruling witness format (`round3/implicit_schema.md`) is specified but not implemented in
  `Certificate.lean` or the reference. No data row uses it.

## Round 4: witness rows, the generated cue table, two findings fixes (2026-11-12, 23:15–23:35; DEVIATIONS 82–86)

- `CueTable.lean` (generated by `tools/caselaw2/cues/gen_cues.py` from `cue_table.json`): `treatCues`, `histCues`,
  `treatDisqualifiers`, `histDisqualifiers`. `Cert.cues` and `Cert.disqualifiers` keep their types and read it.
- `Certificate.lean`: `Witness`, `byResolves`, `textCheck`, `witnessTail`, `checkWitness`, `WResult`. Theorems:
  `witnessTail_sound`, `checkWitness_sound`, `checkWitness_inferred`; in `Examples`, `witness_row_no_effect` (with
  `Spec.inferred_treatment_no_effect`: the event of an admitted witness row has no status effect) and 12 `#guard`s.
- `Data.lean`: `WitnessRow`, optional `treatment_witness.tsv`; W's node is loaded for its hash, court and date.
- `Run.lean`: a treatments row with a witness line is checked by `checkWitness` on W's text; it yields only
  `atRisk X Y inferredRejection`. `panelOwnWords`: the panel finding needs the panel's own overruling words.
- `Exec/Verdicts.lean` `candFor`: a writ-refused decision ranks as the court of last resort's.
- `Mutants.lean`: property "checkWitness_sound / witness_row_no_effect", mutant M27. Matrix 27 × 27.
- No locked statement changed. 141 theorems; no `sorry`, `axiom` or `native_decide`.

## Round 5 (13 Nov 2026)

175 theorems (141 + 34), 34 mutants x 35 properties, locked (`audit.py lock`, `check`: 0 problems). New:
`Spec/Recognised.lean` (recognised overrulings: never negative before the later court's date, never without its
power, order independence, agreement with an explicit row from that date, never weakens; demoted scope never
negative), the round-5 section of `Certificate.lean` (`Mode`, `checkRecognised`, `checkOperative`, `classOf`,
`recogOf`), `Findings.citedRecognisedLater`, `Examples.plessy_timeline`, mutants M28-M34. Runner: optional
`treatment_class.tsv` turns on round-5 output (`classes.tsv`, `oclass` columns); without it the output is round 4's
byte for byte (`wsl/r5_base.sh`). Details: `round5/DESIGN5.md`, `round5/ROUND5.md`.

## Round 6: anchored history rows (13 Nov 2026; `round6/history/DESIGN6.md` §4, `round6/history/LEAN6.md`)

183 theorems (175 + 8), 40 mutants x 41 properties, locked (`audit.py check`: 0 changes, 0 problems; the lock
shows additions only). `Certificate.lean`: `Anchor`, `checkAnchored`, `checkHistory`, five reason codes
(`anchorMismatch`, `anchorNoCue`, `anchorDisqualified`, `anchorUnresolved`, `anchorPart`); theorems
`checkAnchored_sound`, `_disposition`, `_cite_index`, `_window_hash`, `_quote_nonempty`, `_admitted_iff`,
`checkHistory_no_anchor`, `checkHistory_anchored`. Cue table keys `anchor`, `disqualify_anchor`. `Data.lean`: optional
`history_anchor.tsv`. `Run.lean`: the history loop calls `Cert.checkHistory`; anchor counters in `summary.tsv` only
when the file has a line. Mutants M35-M40, 31 new `#guard`s. Without the table (absent or empty) the output is
byte-identical to round 5 (`round5/out/final`) and round 4 (`difftest/real20`) (`wsl/r6_lean_base.sh`). Fixture:
`round6/history/fixtures/anchor/` (`wsl/r6_anchor_fixture.sh`). Backup: `round6/history/pre/`.
