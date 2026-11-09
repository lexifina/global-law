import LegalProofs.Basic

/-!
# Provisions built from a corpus history

The corpora record every change to a provision as a dated commit. A `History` is that record, newest first: each entry
says from which date the provision existed (`true`) or did not (`false`: deleted, or only a "(repealed)" placeholder).
`tools/gen_facts.py` writes these histories straight from the corpora, so the facts below are not typed by hand.
-/

namespace Legal

/-- A provision's record, newest first: `(from, exists)`. -/
abbrev History := List (Date × Bool)

/-- Whether the provision exists on `d`: the newest entry dated on or before `d` decides. -/
def History.at : History → Date → Bool
  | [], _ => false
  | (t, v) :: older, d => if t ≤ d then v else History.at older d

/-- The provision a history describes (its text is not needed for these rules, only whether it exists). -/
def History.toProvision (h : History) : Provision := fun d => if h.at d then some "" else none

/-- If the newest entry says "gone from `r`", the provision is gone on every date from `r` on. -/
theorem History.gone_from (r : Date) (older : History) :
    repealedFrom (History.toProvision ((r, false) :: older)) r := by
  intro d hd
  simp [History.toProvision, History.at, hd]

/-- If the newest entry says "exists from `t`", the provision exists on every date from `t` on. -/
theorem History.exists_from (t : Date) (older : History) :
    ∀ d, t ≤ d → (History.toProvision ((t, true) :: older) d).isSome = true := by
  intro d hd
  simp [History.toProvision, History.at, hd]

/-! ## Reference flags

A flag says: provision `citing` refers to provision `target` of the same act. -/

structure RefFlag where
  citing : History
  target : History

def RefFlag.rule (f : RefFlag) : BlanketRule := { rule := f.citing.toProvision, pointsAt := f.target.toProvision }

/-- The date the target has been gone since, if its record ends with it gone. -/
def RefFlag.deadFrom (f : RefFlag) : Option Date :=
  match f.target with
  | (r, false) :: _ => some r
  | _ => none

/-- A flag is **certified** on `today` when the target's record ends with it gone (on or before `today`) and the citing
provision still exists on `today`. Computable, so Lean checks it for every flag. -/
def RefFlag.certified (f : RefFlag) (today : Date) : Bool :=
  match f.target with
  | (r, false) :: _ => decide (r ≤ today) && f.citing.at today
  | _ => false

/-- The citing provision was itself rewritten after the target had gone: the legislature touched it and kept the dead
reference. -/
def RefFlag.reenacted (f : RefFlag) : Bool :=
  match f.target, f.citing with
  | (r, false) :: _, (t, true) :: _ => decide (r < t)
  | _, _ => false

/-- **Soundness of certificates.** If a flag is certified, the citing rule cannot apply on any date from the target's
removal on, although the citing provision is still on the statute book today. -/
theorem RefFlag.certified_sound (f : RefFlag) (today : Date) (h : f.certified today = true) :
    ∃ r, r ≤ today ∧ f.citing.at today = true ∧ ∀ d, r ≤ d → f.rule.applicable d = false := by
  unfold RefFlag.certified at h
  split at h
  · rename_i r older heq
    simp at h
    refine ⟨r, h.1, h.2, ?_⟩
    have hg : repealedFrom f.target.toProvision r := by rw [heq]; exact History.gone_from r older
    exact dead_reference f.rule r hg
  · simp at h

end Legal
