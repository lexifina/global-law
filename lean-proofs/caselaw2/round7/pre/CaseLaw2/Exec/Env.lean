import LegalProofs.CaseLaw2.Exec.Index
import LegalProofs.CaseLaw2.Spec.AuthorityThms
import LegalProofs.CaseLaw2.Spec.Status

/-!
# Exec: hash-indexed lookups, proved equal to the Spec's list scans

`ExecEnv.build` indexes the court epochs, successions, adoptions and rule rows by key; `ExecRecord.build` indexes the
admitted events by target. The runner calls the Spec's `force`, `canChangeStatus` and `statusOf` through these
indexed lookups. The refinement theorems say that this computes exactly what the Spec defines:

* `exec_lookups_eq_spec`, `exec_eventLookups_eq_spec`: the indexed lookups equal the list scans;
* `exec_force_eq_spec`, `exec_canChangeStatus_eq_spec`, `exec_status_eq_spec`: hence every verdict equals the Spec's.
-/

namespace CaseLaw2.Exec
open CaseLaw2 CaseLaw2.Spec Std

structure ExecEnv where
  epochs : HashMap Nat (List CourtEpoch)
  successions : HashMap Nat (List Succession)
  adoptions : HashMap Nat (List Adoption)
  rules : HashMap String (List RuleRow)

def ExecEnv.build (e : Env) : ExecEnv :=
  { epochs := index (·.court) e.epochs, successions := index (·.old) e.successions,
    adoptions := index (·.source) e.adoptions, rules := index (fun r => ruleKey r.rule r.key) e.rules }

def ExecEnv.lookups (x : ExecEnv) : Lookups :=
  { epochAt := fun c d => (x.epochs.getD c []).find? (epochCovers c d)
    adoptionsFrom := fun c => x.adoptions.getD c []
    successorsOf := fun c => x.successions.getD c []
    rules := Rules.ofLookup (fun k => x.rules.getD k []) }

theorem exec_lookups_eq_spec (e : Env) : (ExecEnv.build e).lookups = e.lookups := by
  simp only [ExecEnv.lookups, ExecEnv.build, Env.lookups, index_getD]
  congr
  funext c d
  rw [List.find?_filter]
  congr
  funext x
  simp only [epochCovers, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq]
  by_cases h1 : x.court = c <;> by_cases h2 : x.dateFrom ≤ d <;> by_cases h3 : d ≤ x.dateTo <;> simp [h1, h2, h3]

/-- The runner's force equals the Spec's. -/
theorem exec_force_eq_spec (e : Env) (x : Decision) (h : Holding) (p : Bool) (q : Query) :
    force (ExecEnv.build e).lookups x h p q = force e.lookups x h p q := by
  rw [exec_lookups_eq_spec]

/-- The runner's force on a court as it ordinarily sits (H6) equals the Spec's. -/
theorem exec_forceDiv_eq_spec (e : Env) (x : Decision) (h : Holding) (p : Bool) (q : Query) :
    forceDiv (ExecEnv.build e).lookups x h p q = forceDiv e.lookups x h p q := by
  rw [exec_lookups_eq_spec]

theorem exec_canChangeStatus_eq_spec (e : Env) (b x : Decision) (dom : Option Domain) :
    canChangeStatus (ExecEnv.build e).lookups b x dom = canChangeStatus e.lookups b x dom := by
  rw [exec_lookups_eq_spec]

structure ExecRecord where
  hist : HashMap Nat (List HEvent)
  treat : HashMap Nat (List TEvent)
  supers : HashMap Nat (List SEvent)

def ExecRecord.build (r : Record) : ExecRecord :=
  { hist := index (·.target) r.hist, treat := index (·.target) r.treat, supers := index (·.target) r.supers }

def ExecRecord.lookups (x : ExecRecord) : EventLookups :=
  { histOf := fun n => x.hist.getD n [], treatOf := fun n => x.treat.getD n [],
    supersOf := fun n => x.supers.getD n [] }

theorem exec_eventLookups_eq_spec (r : Record) : (ExecRecord.build r).lookups = recordLookups r := by
  simp [ExecRecord.lookups, ExecRecord.build, recordLookups, index_getD]

/-- The runner's status equals the Spec's (both the court data and the events through hash indexes). -/
theorem exec_status_eq_spec (e : Env) (r : Record) (x k t u : Nat) :
    status (effectsOf (ExecEnv.build e).lookups (ExecRecord.build r).lookups r.dec x) k t u =
      statusOf e.lookups r x k t u := by
  rw [exec_lookups_eq_spec, exec_eventLookups_eq_spec]; rfl

end CaseLaw2.Exec
