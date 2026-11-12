import LegalProofs.USCaseLaw.StatuteText

/-!
# Watch lists: tell a user when a section they depend on changes

A user watches a section of the US Code, or one subsection of it, from a day `d` (the day they last read it, or the
day a decision applied it). Read on day `t`, the watch raises an alert for each law that came into force after `d`
and by `t` and changed the words watched: the subsection's words (`SVersion.sub`) or, for a whole section, the
section's (`SVersion.text`). A version made by an edition of the Code (a reprint, an editorial change) never raises an
alert; if it changes the words, it is an edition notice, reported apart.

Each version is compared with the one before it. Before a section's first version nothing is in force: `origin`, whose
words are `0` (the runner gives `0` to "no text", so a section added or repealed by a law changes its words).

Proved:
* `alerts_mono`, `alert_mono`: an earlier `d` gives every alert a later one gives, and possibly more;
* `alert_byLaw`, `alert_mem_lawChanges`, `no_law_no_alert`: every alert is a law in `lawChangesBetween`; with only
  editions in between there is none;
* `no_alert_same_words`: with no alert and no edition notice, the words watched in force on `t` are those in force on
  `d`; `no_alert_subDiffers`, `no_alert_wordsDiffer` state it with `StatuteText`'s `subDiffers` and `wordsDiffer`.
  So "no alert" means: the words are the same, or only an edition changed them (and the notice says so).
-/

namespace Legal.USCaseLaw.Watch

open Legal.USCaseLaw

/-- The words a watch follows: the whole section's, or the watched subsection's. -/
def wkey (whole : Bool) (v : SVersion) : Nat := if whole then v.text else v.sub

/-- Before the first version: nothing in force, no words. -/
def origin : SVersion := ⟨0, false, 0, 0⟩

/-- Each version with the version before it. -/
def steps : SVersion → List SVersion → List (SVersion × SVersion)
  | _, [] => []
  | p, v :: r => (p, v) :: steps v r

def inWindow (d t : Nat) (v : SVersion) : Bool := d < v.from_ && v.from_ ≤ t

def changesWords (whole : Bool) (s : SVersion × SVersion) : Bool := wkey whole s.1 != wkey whole s.2

/-- A law, in force after `d` and by `t`, that changed the words watched. -/
def isAlert (whole : Bool) (d t : Nat) (s : SVersion × SVersion) : Bool :=
  s.2.byLaw && inWindow d t s.2 && changesWords whole s

/-- An edition, in force after `d` and by `t`, that changed the words watched: reported, never an alert. -/
def isNotice (whole : Bool) (d t : Nat) (s : SVersion × SVersion) : Bool :=
  !s.2.byLaw && inWindow d t s.2 && changesWords whole s

def alerts (whole : Bool) (h : List SVersion) (d t : Nat) : List (SVersion × SVersion) :=
  (steps origin h).filter (isAlert whole d t)

def notices (whole : Bool) (h : List SVersion) (d t : Nat) : List (SVersion × SVersion) :=
  (steps origin h).filter (isNotice whole d t)

def alert (whole : Bool) (h : List SVersion) (d t : Nat) : Bool := !(alerts whole h d t).isEmpty

/-- The words watched in force on `x` (`0`: none). -/
def wordsOn (whole : Bool) (h : List SVersion) (x : Nat) : Nat := ((sInForceOn h x).map (wkey whole)).getD 0

/-! ## Monotone in the day watched from -/

theorem filter_sublist_imp {α} (l : List α) (p q : α → Bool) (hpq : ∀ x, p x = true → q x = true) :
    List.Sublist (l.filter p) (l.filter q) := by
  induction l with
  | nil => simp
  | cons a r ih =>
    by_cases hp : p a = true
    · have hq := hpq a hp
      simp only [List.filter_cons, hp, hq, ite_true]
      exact ih.cons_cons a
    · simp only [List.filter_cons, hp]
      by_cases hq : q a = true
      · simp only [hq, ite_true, Bool.false_eq_true, ite_false]; exact ih.cons a
      · simp only [hq, Bool.false_eq_true, ite_false]; exact ih

/-- Watching from an earlier day `d' ≤ d` gives every alert watching from `d` gives. -/
theorem alerts_mono (whole : Bool) (h : List SVersion) (d d' t : Nat) (hle : d' ≤ d) :
    List.Sublist (alerts whole h d t) (alerts whole h d' t) := by
  apply filter_sublist_imp
  intro s hs
  simp only [isAlert, inWindow, Bool.and_eq_true, decide_eq_true_eq] at hs ⊢
  obtain ⟨⟨hb, h1, h2⟩, hc⟩ := hs
  exact ⟨⟨hb, by omega, h2⟩, hc⟩

theorem alerts_mono_length (whole : Bool) (h : List SVersion) (d d' t : Nat) (hle : d' ≤ d) :
    (alerts whole h d t).length ≤ (alerts whole h d' t).length :=
  (alerts_mono whole h d d' t hle).length_le

theorem alert_mono (whole : Bool) (h : List SVersion) (d d' t : Nat) (hle : d' ≤ d)
    (ha : alert whole h d t = true) : alert whole h d' t = true := by
  have := alerts_mono_length whole h d d' t hle
  unfold alert at *
  cases e : alerts whole h d t with
  | nil => simp [e] at ha
  | cons x r =>
    rw [e] at this
    cases e' : alerts whole h d' t with
    | nil => rw [e'] at this; simp at this
    | cons y r' => simp

/-! ## Editions never alert -/

theorem mem_steps (p : SVersion) (h : List SVersion) (s : SVersion × SVersion) (hs : s ∈ steps p h) : s.2 ∈ h := by
  induction h generalizing p with
  | nil => simp [steps] at hs
  | cons v r ih =>
    simp only [steps, List.mem_cons] at hs
    rcases hs with rfl | hs
    · simp
    · exact List.mem_cons_of_mem _ (ih v hs)

theorem alert_byLaw (whole : Bool) (h : List SVersion) (d t : Nat) (s : SVersion × SVersion)
    (hs : s ∈ alerts whole h d t) : s.2.byLaw = true := by
  simp only [alerts, List.mem_filter, isAlert, Bool.and_eq_true] at hs
  exact hs.2.1.1

/-- Every alert is one of `StatuteText`'s law changes between `d` and `t`. -/
theorem alert_mem_lawChanges (whole : Bool) (h : List SVersion) (d t : Nat) (s : SVersion × SVersion)
    (hs : s ∈ alerts whole h d t) : s.2 ∈ lawChangesBetween h d t := by
  simp only [alerts, List.mem_filter, isAlert, inWindow, Bool.and_eq_true] at hs
  obtain ⟨hm, ⟨hb, hw⟩, _⟩ := hs
  simp only [lawChangesBetween, sChangesBetween, List.mem_filter, Bool.and_eq_true]
  exact ⟨⟨mem_steps _ _ _ hm, hw⟩, hb⟩

/-- With only editions between `d` and `t` (no law changed the section), there is no alert, whatever they changed. -/
theorem no_law_no_alert (whole : Bool) (h : List SVersion) (d t : Nat) (hn : lawChangesBetween h d t = []) :
    alerts whole h d t = [] := by
  cases e : alerts whole h d t with
  | nil => rfl
  | cons s r =>
    have := alert_mem_lawChanges whole h d t s (by rw [e]; simp)
    rw [hn] at this
    simp at this

/-! ## No alert: the same words -/

/-- The version in force on `x`, given that `p` was in force before the versions `h`. -/
def at_ (p : SVersion) : List SVersion → Nat → SVersion
  | [], _ => p
  | v :: r, x => if v.from_ ≤ x then at_ v r x else p

def Sorted (h : List SVersion) : Prop := h.Pairwise (fun a b => a.from_ ≤ b.from_)

theorem sInForce_at (p : SVersion) (h : List SVersion) (x : Nat) (hs : Sorted h) :
    (sInForceOn h x).getD p = at_ p h x := by
  induction h generalizing p with
  | nil => simp [sInForceOn, at_]
  | cons v r ih =>
    have hr : Sorted r := (List.pairwise_cons.mp hs).2
    have hv := (List.pairwise_cons.mp hs).1
    by_cases hx : v.from_ ≤ x
    · have := ih v hr
      simp only [sInForceOn] at this ⊢
      have hf : (v :: r).filter (fun w => decide (w.from_ ≤ x)) = v :: r.filter (fun w => decide (w.from_ ≤ x)) := by
        simp [hx]
      rw [hf, List.getLast?_cons]
      simp only [at_, hx, ite_true, Option.getD_some]
      exact this
    · have hnil : r.filter (fun w => decide (w.from_ ≤ x)) = [] := by
        rw [List.filter_eq_nil_iff]
        intro w hw
        have := hv w hw
        simp; omega
      simp [sInForceOn, hx, at_, hnil]

theorem at_first (v : SVersion) (r : List SVersion) (d : Nat) (hs : Sorted (v :: r)) (hd : d < v.from_) :
    at_ v r d = v := by
  cases r with
  | nil => rfl
  | cons w r' =>
    have := (List.pairwise_cons.mp hs).1 w (by simp)
    have : ¬ w.from_ ≤ d := by omega
    simp [at_, this]

theorem at_same (whole : Bool) (d t : Nat) (hle : d ≤ t) (p : SVersion) (h : List SVersion) (hs : Sorted h)
    (hno : ∀ s ∈ steps p h, inWindow d t s.2 = true → wkey whole s.1 = wkey whole s.2) :
    wkey whole (at_ p h d) = wkey whole (at_ p h t) := by
  induction h generalizing p with
  | nil => rfl
  | cons v r ih =>
    have hr : Sorted r := (List.pairwise_cons.mp hs).2
    have hrest : ∀ s ∈ steps v r, inWindow d t s.2 = true → wkey whole s.1 = wkey whole s.2 :=
      fun s hm hw => hno s (by simp [steps, hm]) hw
    by_cases h1 : v.from_ ≤ d
    · have h2 : v.from_ ≤ t := by omega
      simp only [at_, h1, h2, ite_true]
      exact ih v hr hrest
    · by_cases h2 : v.from_ ≤ t
      · have hw : inWindow d t v = true := by simp [inWindow]; omega
        have hpv := hno (p, v) (by simp [steps]) hw
        simp only [at_, h1, h2, ite_true, ite_false]
        rw [hpv, ← ih v hr hrest, at_first v r d hs (by omega)]
      · simp [at_, h1, h2]

/-- No alert and no edition notice: the words watched in force on `t` are those in force on `d`. -/
theorem no_alert_same_words (whole : Bool) (h : List SVersion) (d t : Nat) (hs : Sorted h) (hle : d ≤ t)
    (ha : alerts whole h d t = []) (hn : notices whole h d t = []) :
    wordsOn whole h d = wordsOn whole h t := by
  have key : ∀ x, wordsOn whole h x = wkey whole (at_ origin h x) := by
    intro x
    rw [← sInForce_at origin h x hs]
    unfold wordsOn
    cases sInForceOn h x <;> simp [origin, wkey]
  rw [key, key]
  apply at_same whole d t hle origin h hs
  intro s hm hw
  rw [alerts, List.filter_eq_nil_iff] at ha
  rw [notices, List.filter_eq_nil_iff] at hn
  have a := ha s hm
  have b := hn s hm
  simp only [isAlert, isNotice, hw, changesWords, Bool.and_true] at a b
  cases hb : s.2.byLaw <;> simp_all

theorem inForce_later (h : List SVersion) (d t : Nat) (hle : d ≤ t) (hd : (sInForceOn h d).isSome = true) :
    (sInForceOn h t).isSome = true := by
  unfold sInForceOn at *
  cases e : (h.filter (fun v => decide (v.from_ ≤ t))).getLast? with
  | some _ => rfl
  | none =>
    exfalso
    rw [List.getLast?_eq_none_iff, List.filter_eq_nil_iff] at e
    cases e2 : (h.filter (fun v => decide (v.from_ ≤ d))).getLast? with
    | none => rw [e2] at hd; simp at hd
    | some v =>
      have hm := List.mem_of_getLast? e2
      simp only [List.mem_filter, decide_eq_true_eq] at hm
      have := e v hm.1
      simp at this; omega

/-- The same in `StatuteText`'s terms, for a section in force on `d`: the subsection watched does not read
differently. -/
theorem no_alert_subDiffers (h : List SVersion) (d t : Nat) (hs : Sorted h) (hle : d ≤ t)
    (hd : (sInForceOn h d).isSome = true)
    (ha : alerts false h d t = []) (hn : notices false h d t = []) : subDiffers h d t = false := by
  have e := no_alert_same_words false h d t hs hle ha hn
  have ht := inForce_later h d t hle hd
  unfold wordsOn at e
  unfold subDiffers
  cases h1 : sInForceOn h d <;> cases h2 : sInForceOn h t <;> simp_all [wkey]

theorem no_alert_wordsDiffer (h : List SVersion) (d t : Nat) (hs : Sorted h) (hle : d ≤ t)
    (hd : (sInForceOn h d).isSome = true)
    (ha : alerts true h d t = []) (hn : notices true h d t = []) : wordsDiffer h d t = false := by
  have e := no_alert_same_words true h d t hs hle ha hn
  have ht := inForce_later h d t hle hd
  unfold wordsOn at e
  unfold wordsDiffer
  cases h1 : sInForceOn h d <;> cases h2 : sInForceOn h t <;> simp_all [wkey]

-- Example: 18 U.S.C. § 924, watched at (c) from 2006. A law of 2018 rewrites (c); an edition of 2019 reprints (c)
-- with a corrected reference; a law of 2022 amends (d) only.
section
private def h924 : List SVersion :=
  [⟨19950105, true, 1, 1⟩, ⟨20181221, true, 2, 2⟩, ⟨20190103, false, 3, 3⟩, ⟨20220625, true, 4, 3⟩]
#guard (alerts false h924 20060101 20261112).map (·.2.from_) == [20181221]   -- (c): the First Step Act
#guard (notices false h924 20060101 20261112).map (·.2.from_) == [20190103]  -- the edition: a notice
#guard (alerts true h924 20060101 20261112).length == 2                      -- the whole section: two laws
#guard alert false h924 20190101 20261112 == false                           -- from 2019: (c) unchanged by any law
#guard (alerts false h924 20190101 20261112).length ≤ (alerts false h924 20060101 20261112).length
#guard (alerts true [⟨19950105, false, 1, 1⟩, ⟨20200101, true, 0, 0⟩] 20100101 20261112).length == 1  -- repealed
end

end Legal.USCaseLaw.Watch
