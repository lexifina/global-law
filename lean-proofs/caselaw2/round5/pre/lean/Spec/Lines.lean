import LegalProofs.CaseLaw2.Spec.Status
import LegalProofs.CaseLaw2.Spec.Splits
import LegalProofs.CaseLaw2.Spec.Horty

/-!
# Spec: status per line of authority, everywhere (round 2; DEVIATIONS 74–78)

Hunt H4 made status after an adoption cut-off relative to the court asking (`Reach`, `statusFor`), for citation
findings. This module carries the same reading to the other places a status is read:

* **status rows per line** (`Line`, `linesOf`, `lineStatus`): for a decision with a line-limited effect, the status in
  each pure line (the original line; each heir). `lineStatus_heir_agrees` / `lineStatus_orig_agrees`: a court standing
  in that line gets exactly that row's status. `lineStatus_all`, `linesOf_all`: with no line-limited effect there is
  one status and no extra row.
* **splits and conflicts** (`goodVia`, `goodIn`, `Held`, `heldVia`, `heldIn`): the holdings that count at a court are
  those good law in its line. `heldIn_ignores_unreaching`, `conflict_in_line_ignores_unreaching`: an overruling that
  does not reach the line changes nothing there. `heldIn_all`: with no line-limited effect it is the old (union) test.
* **Horty bases** (`lineBase`): the binding base of a court holds a precedent iff it binds there and is good law in the
  court's line (`mem_lineBase_iff`). The union base is inside every line's base (`unionBase_sub_lineBase`), so an
  inconsistency among precedents good everywhere is one in every line (`lineBase_consistent_union`).

The union status (`status`, every effect) is what `status.tsv` reports; `statusFor_le_status` shows it is an upper
bound for every line.
-/

namespace CaseLaw2.Spec
open CaseLaw2

/-! ## Pure lines -/

/-- A pure line of authority of a decision: the original line (a court in no heir's line), or one heir's. -/
inductive Line where
  | orig
  | heir (a : Nat)
  deriving Repr, DecidableEq, Inhabited

/-- The line as a view: which adopters' lines a court standing in it is in. -/
def Line.view : Line → Nat → Bool
  | .orig => fun _ => false
  | .heir a => fun b => b == a

/-- The effect does not reach every line. -/
def Effect.limited (e : Effect) : Bool := e.reach != .all

/-- The heir adopters an effect's reach names. -/
def Effect.adopters (e : Effect) : List Nat :=
  match e.reach with
  | .all => []
  | .lines _ reached unreached => reached ++ unreached

def lineLimited (effs : List Effect) : Bool := effs.any (·.limited)

/-- The pure lines of a decision: none unless some effect is line-limited; then the original line and every heir
its effects name. -/
def linesOf (effs : List Effect) : List Line :=
  if lineLimited effs then .orig :: ((effs.flatMap (·.adopters)).eraseDups.map .heir) else []

/-- **The status row of a line**: the status a court standing in exactly that line reads. -/
def lineStatus (ln : Line) (effs : List Effect) (k : Nat) (t u : Date) : Status := statusFor ln.view effs k t u

/-! ## Congruence: only which effects reach matters -/

theorem filter_congr_mem {α : Type} (l : List α) (p q : α → Bool) (h : ∀ x ∈ l, p x = q x) :
    l.filter p = l.filter q := by
  induction l with
  | nil => rfl
  | cons x l ih =>
    simp only [List.filter_cons]
    rw [h x (by simp), ih (fun y hy => h y (by simp [hy]))]

theorem any_congr_mem {α : Type} (l : List α) (p q : α → Bool) (h : ∀ x ∈ l, p x = q x) : l.any p = l.any q := by
  induction l with
  | nil => rfl
  | cons x l ih =>
    simp only [List.any_cons]
    rw [h x (by simp), ih (fun y hy => h y (by simp [hy]))]

/-- Two views that agree on the adopters an effect names are reached by it alike. -/
theorem reaches_congr (p q : Nat → Bool) (e : Effect) (h : ∀ b ∈ e.adopters, p b = q b) :
    e.reaches p = e.reaches q := by
  unfold Effect.reaches
  unfold Effect.adopters at h
  revert h
  cases e.reach with
  | all => intro _; rfl
  | lines o r un =>
    intro h
    have h1 : r.any p = r.any q := any_congr_mem r p q (fun x hx => h x (List.mem_append_left _ hx))
    have h2 : un.any p = un.any q := any_congr_mem un p q (fun x hx => h x (List.mem_append_right _ hx))
    show (r.any p || (o && !un.any p)) = (r.any q || (o && !un.any q))
    rw [h1, h2]

/-- Status in a line depends only on which effects reach the court. -/
theorem statusFor_congr (p q : Nat → Bool) (l : List Effect) (k : Nat) (t u : Date)
    (h : ∀ e ∈ l, e.reaches p = e.reaches q) : statusFor p l k t u = statusFor q l k t u := by
  have hf : heirEffects p l = heirEffects q l := filter_congr_mem l _ _ h
  unfold statusFor
  rw [hf]

/-- **Per-heir status rows agree with `statusFor`**: a court that is in adopter `a`'s line and in no other line the
effects name reads the status of row `heir a` (the Eleventh Circuit and its district courts read the Eleventh's
row). -/
theorem lineStatus_heir_agrees (inLine : Nat → Bool) (a : Nat) (l : List Effect) (k : Nat) (t u : Date)
    (h : ∀ e ∈ l, ∀ b ∈ e.adopters, inLine b = (b == a)) :
    statusFor inLine l k t u = lineStatus (.heir a) l k t u :=
  statusFor_congr inLine (Line.view (.heir a)) l k t u
    (fun e he => reaches_congr inLine (Line.view (.heir a)) e (fun b hb => h e he b hb))

/-- A court in no heir's line reads the original line's row. -/
theorem lineStatus_orig_agrees (inLine : Nat → Bool) (l : List Effect) (k : Nat) (t u : Date)
    (h : ∀ e ∈ l, ∀ b ∈ e.adopters, inLine b = false) :
    statusFor inLine l k t u = lineStatus .orig l k t u :=
  statusFor_congr inLine (Line.view .orig) l k t u
    (fun e he => reaches_congr inLine (Line.view .orig) e (fun b hb => h e he b hb))

/-- With no line-limited effect every line's row is the union status. -/
theorem lineStatus_all (ln : Line) (l : List Effect) (k : Nat) (t u : Date) (h : ∀ e ∈ l, e.reach = .all) :
    lineStatus ln l k t u = status l k t u :=
  statusFor_all ln.view l k t u h

/-- With no line-limited effect a decision has no per-line rows (its `status.tsv` rows are all there is). -/
theorem linesOf_all (l : List Effect) (h : ∀ e ∈ l, e.reach = .all) : linesOf l = [] := by
  have hl : lineLimited l = false := by
    unfold lineLimited
    rw [List.any_eq_false]
    intro e he
    simp [Effect.limited, h e he]
  simp [linesOf, hl]

/-! ## The union status bounds every line -/

theorem status_filter_le (p : Effect → Bool) (l : List Effect) (k : Nat) (t u : Date) :
    (status (l.filter p) k t u).rank ≤ (status l k t u).rank := by
  induction l with
  | nil => simp [status]
  | cons e l ih =>
    rw [List.filter_cons]
    split
    · rw [status_cons, status_cons]
      simp only [Status.rank_join]
      omega
    · rw [status_cons]
      simp only [Status.rank_join]
      omega

/-- The union status (`status.tsv`) is at least as severe as the status in any line. -/
theorem statusFor_le_status (inLine : Nat → Bool) (l : List Effect) (k : Nat) (t u : Date) :
    (statusFor inLine l k t u).rank ≤ (status l k t u).rank :=
  status_filter_le _ l k t u

/-- Good law in the union is good law in every line. -/
theorem good_in_every_line (inLine : Nat → Bool) (l : List Effect) (k : Nat) (t u : Date)
    (h : status l k t u = .good) : statusFor inLine l k t u = .good := by
  have hm := statusFor_le_status inLine l k t u
  rw [h] at hm
  exact (Status.rank_zero_iff _).mp (Nat.le_zero.mp hm)

/-! ## Good law as a court sees it -/

/-- Good law on date `t` (question date = conduct date) as a court sees it: `view` selects the effects that reach
the court (`heirEffects (inLine …)`; every effect when the court's line is unknown: `effectsFor`). -/
def goodVia (view : List Effect → List Effect) (effs : List Effect) (k : Nat) (t : Date) : Bool :=
  status (view effs) k t t == .good

/-- Good law in a line. -/
def goodIn (inLine : Nat → Bool) (effs : List Effect) (k : Nat) (t : Date) : Bool :=
  goodVia (heirEffects inLine) effs k t

/-- A decision that is good law in at least one of its pure lines (with no line-limited effect: good law). -/
def liveSomewhere (effs : List Effect) (k : Nat) (t : Date) : Bool :=
  if lineLimited effs then (linesOf effs).any (fun ln => lineStatus ln effs k t t == .good)
  else goodLaw effs k t t

/-- An overruling that does not reach a line leaves good law in that line as it was. -/
theorem goodIn_ignores_unreaching (inLine : Nat → Bool) (e : Effect) (l : List Effect) (k : Nat) (t : Date)
    (h : e.reaches inLine = false) : goodIn inLine (e :: l) k t = goodIn inLine l k t := by
  simp [goodIn, goodVia, heirEffects, List.filter, h]

/-- With no line-limited effect, good law in a line is good law. -/
theorem goodIn_all (inLine : Nat → Bool) (l : List Effect) (k : Nat) (t : Date) (h : ∀ e ∈ l, e.reach = .all) :
    goodIn inLine l k t = goodLaw l k t t := by
  unfold goodIn goodVia goodLaw
  rw [show status (heirEffects inLine l) k t t = status l k t t from statusFor_all inLine l k t t h]

/-- A court whose line is known reads a decision through `inLine`. -/
theorem effectsFor_known (L : Lookups) (c : Decision) (effs : List Effect) (hd : c.date ≠ 0)
    (he : (L.epochAt c.court c.date).isSome = true) : effectsFor L c effs = heirEffects (inLine L c) effs := by
  unfold effectsFor
  cases h : L.epochAt c.court c.date with
  | none => simp [h] at he
  | some E => simp [hd]

/-! ## Holdings that count at a court (splits, conflicts, Horty bases) -/

/-- A holding (or precedent) with what a court needs to know to count it: the issue, the effects on its decision,
and whether its force at the court asked is at least bindingAbsentConflict. -/
structure Held (α : Type) where
  item : α
  issue : Nat
  effs : List Effect
  binds : Bool := true

/-- The items that count at a court: binding there and good law as the court sees it. -/
def heldVia {α : Type} (view : List Effect → List Effect) (t : Date) (hs : List (Held α)) : List α :=
  (hs.filter fun h => h.binds && goodVia view h.effs h.issue t).map (·.item)

/-- The items that count in a line. -/
def heldIn {α : Type} (inLine : Nat → Bool) (t : Date) (hs : List (Held α)) : List α :=
  heldVia (heirEffects inLine) t hs

/-- The union version (every effect reaches): the old test. -/
def heldUnion {α : Type} (t : Date) (hs : List (Held α)) : List α :=
  (hs.filter fun h => h.binds && goodLaw h.effs h.issue t t).map (·.item)

theorem mem_heldIn_iff {α : Type} (inLine : Nat → Bool) (t : Date) (hs : List (Held α)) (x : α) :
    x ∈ heldIn inLine t hs ↔
      ∃ h ∈ hs, h.item = x ∧ h.binds = true ∧ statusFor inLine h.effs h.issue t t = .good := by
  unfold heldIn heldVia goodVia
  constructor
  · intro hx
    obtain ⟨h, hm, rfl⟩ := List.mem_map.mp hx
    obtain ⟨hin, hc⟩ := List.mem_filter.mp hm
    simp only [Bool.and_eq_true, beq_iff_eq] at hc
    exact ⟨h, hin, rfl, hc.1, hc.2⟩
  · rintro ⟨h, hin, rfl, hb, hg⟩
    refine List.mem_map.mpr ⟨h, List.mem_filter.mpr ⟨hin, ?_⟩, rfl⟩
    simp only [Bool.and_eq_true, beq_iff_eq]
    exact ⟨hb, hg⟩

/-- **A split or conflict judged in a line ignores overrulings that do not reach that line**: adding such an
overruling to any holding's decision leaves the holdings that count there unchanged. -/
theorem heldIn_ignores_unreaching {α : Type} (inLine : Nat → Bool) (t : Date) (pre post : List (Held α))
    (h : Held α) (e : Effect) (hr : e.reaches inLine = false) :
    heldIn inLine t (pre ++ { h with effs := e :: h.effs } :: post) = heldIn inLine t (pre ++ h :: post) := by
  have hg : goodVia (heirEffects inLine) (e :: h.effs) h.issue t = goodVia (heirEffects inLine) h.effs h.issue t :=
    goodIn_ignores_unreaching inLine e h.effs h.issue t hr
  unfold heldIn heldVia
  simp only [List.filter_append, List.map_append, List.filter_cons]
  rw [hg]
  by_cases hc : (h.binds && goodVia (heirEffects inLine) h.effs h.issue t) = true <;> simp [hc]

/-- The resolver's answer at a court (the conflict test) is unchanged by an overruling that does not reach its line
(a decision the Fifth Circuit alone overruled still counts for an Eleventh Circuit conflict). -/
theorem conflict_in_line_ignores_unreaching (inLine : Nat → Bool) (t : Date) (f : Bool) (s : Option TrialScope)
    (pre post : List (Held Cand)) (h : Held Cand) (e : Effect) (hr : e.reaches inLine = false) :
    resolve f s (heldIn inLine t (pre ++ { h with effs := e :: h.effs } :: post)) =
      resolve f s (heldIn inLine t (pre ++ h :: post)) := by
  rw [heldIn_ignores_unreaching inLine t pre post h e hr]

/-- **With no line-limited effect the line test is the old (union) test**: nothing changes for decisions without
heirs. -/
theorem heldIn_all {α : Type} (inLine : Nat → Bool) (t : Date) (hs : List (Held α))
    (hall : ∀ h ∈ hs, ∀ e ∈ h.effs, e.reach = .all) : heldIn inLine t hs = heldUnion t hs := by
  unfold heldIn heldVia heldUnion
  rw [filter_congr_mem hs _ _ (fun h hh => by
    rw [show goodVia (heirEffects inLine) h.effs h.issue t = goodLaw h.effs h.issue t t from
      goodIn_all inLine h.effs h.issue t (hall h hh)])]

/-- What counts in the union counts in every line. -/
theorem heldUnion_sub_heldIn {α : Type} (inLine : Nat → Bool) (t : Date) (hs : List (Held α)) :
    ∀ x ∈ heldUnion t hs, x ∈ heldIn inLine t hs := by
  intro x hx
  obtain ⟨h, hm, rfl⟩ := List.mem_map.mp hx
  obtain ⟨hin, hc⟩ := List.mem_filter.mp hm
  simp only [Bool.and_eq_true, goodLaw, beq_iff_eq] at hc
  exact (mem_heldIn_iff inLine t hs h.item).mpr
    ⟨h, hin, rfl, hc.1, good_in_every_line inLine h.effs h.issue t t hc.2⟩

/-! ## Horty bases in a line -/

/-- The binding case base of a court in a line (Horty): the precedents that bind there and are good law in the
court's line. -/
def lineBase (inLine : Nat → Bool) (t : Date) (hs : List (Held Horty.FCase)) : List Horty.FCase := heldIn inLine t hs

/-- **A Horty base in a line contains exactly the precedents good in that line** (and binding there). -/
theorem mem_lineBase_iff (inLine : Nat → Bool) (t : Date) (hs : List (Held Horty.FCase)) (c : Horty.FCase) :
    c ∈ lineBase inLine t hs ↔
      ∃ h ∈ hs, h.item = c ∧ h.binds = true ∧ statusFor inLine h.effs h.issue t t = .good :=
  mem_heldIn_iff inLine t hs c

/-- With no line-limited effect a line's base is the old (union) base. -/
theorem lineBase_all (inLine : Nat → Bool) (t : Date) (hs : List (Held Horty.FCase))
    (hall : ∀ h ∈ hs, ∀ e ∈ h.effs, e.reach = .all) : lineBase inLine t hs = heldUnion t hs :=
  heldIn_all inLine t hs hall

/-- The union base is inside every line's base. -/
theorem unionBase_sub_lineBase (inLine : Nat → Bool) (t : Date) (hs : List (Held Horty.FCase)) :
    ∀ c ∈ heldUnion t hs, c ∈ lineBase inLine t hs :=
  heldUnion_sub_heldIn inLine t hs

/-- A consistent base in some line makes the union base consistent: an inconsistency among precedents that are good
law everywhere is an inconsistency in every line. -/
theorem lineBase_consistent_union (inLine : Nat → Bool) (t : Date) (hs : List (Held Horty.FCase))
    (h : Horty.consistent (lineBase inLine t hs) = true) : Horty.consistent (heldUnion t hs) = true :=
  Horty.consistent_sublist (unionBase_sub_lineBase inLine t hs) h

end CaseLaw2.Spec
