import io
exec(io.open('gen.py', encoding='utf-8').read().split("def write(name, text):")[0])
def write(name, text): io.open(name, 'w', encoding='utf-8', newline='\n').write(text)
a = base.index("def step (cfg : Cfg) (s : St) : Move → Option St")
b = base.index("/-! ## Part 2. Search -/")
stepC = closed(base[a:b]).replace("def step (cfg : Cfg)", "/-- RED: `step` with the one closed-gap edit in `sellP`; every other line identical. -/\ndef stepClosed (cfg : Cfg)")
T6 = OPEN + stepC + r"""
def q : Cfg := { cfg0 with post2025 := true }
def s0 : St := start true 5 10000 0 0
def run (f : Cfg → St → Move → Option St) (cfg : Cfg) (s : St) (ms : List Move) : Option St :=
  ms.foldl (fun o m => o.bind (fun s => f cfg s m)) (some s)
def thePlan : List Move := [.sellOut .A 5, .contribP 1, .sellP]
def oneIssuer : List Move := [.contribP 1, .sellP]
def direct : List Move := [.sellOut .A 1]
/-- tax, A's money, and the eligible gain recorded against A's limit for C stock -/
def out (o : Option St) : Option (Nat × Int × Nat) := o.map fun s => (s.tax, s.a.cash, s.a.takenYr)
def outFinal (cfg : Cfg) (o : Option St) : Option (Int × Int × Nat) := o.bind (evaluate cfg true)

/-! ### Replays through the kernel (no compiled code) -/
theorem plan_original : out (run step q s0 thePlan) = some (3855, 36145, 7800) := by decide +kernel
theorem plan_original_final : outFinal q (run step q s0 thePlan) = some (36145, 36145, 3855) := by decide +kernel
theorem oneIssuer_original : out (run step q s0 oneIssuer) = some (5712, 34288, 0) := by decide +kernel
theorem direct_original : out (run step q s0 direct) = some (5712, 34288, 15000) := by decide +kernel
theorem plain_original : outFinal q (run step q s0 plain) = some (25680, 25680, 14320) := by decide +kernel
theorem plan_closed : out (run stepClosed q s0 thePlan) = some (5712, 34288, 15000) := by decide +kernel
theorem oneIssuer_closed : out (run stepClosed q s0 oneIssuer) = some (5712, 34288, 15000) := by decide +kernel
theorem plain_closed : (run stepClosed q s0 plain).bind (fun s => (settle q s).map (·.tax)) = some 14320 := by decide +kernel

/-! ### Every sequence of up to four of the plan's kinds of move, checked in the kernel -/
def alphabet : List Move := [.sellOut .A 1, .sellOut .A 2, .sellOut .A 4, .sellOut .A 5, .contribP 1, .contribP 2, .contribP 4, .sellP]
/-- least tax over every sequence of at most `d` further moves that leaves A with no C or P stock -/
def leastTax (f : Cfg → St → Move → Option St) (cfg : Cfg) : Nat → St → Nat
  | 0, s => if s.a.sh = 0 ∧ s.pSh = 0 then s.tax else 1000000
  | d + 1, s =>
    let here := if s.a.sh = 0 ∧ s.pSh = 0 then s.tax else 1000000
    alphabet.foldl (fun acc m => match f cfg s m with
      | none => acc
      | some s' => min acc (leastTax f cfg d s')) here
theorem least_original : leastTax step q 4 s0 = 3855 := by decide +kernel
theorem least_closed : leastTax stepClosed q 4 s0 = 5710 := by decide +kernel

/-! ### All sequences, any length: under the closed-gap rule the gain A excludes in a year on C stock and on the
holding-company stock together never passes 15,000 (cut down to the plan's three kinds of move, any holder, any
fraction; no year end, so one taxable year). -/
inductive PM where
  | sell (h : Who) (f : Nat) | contrib (f : Nat) | sellP
def PM.toMove : PM → Move
  | .sell h f => .sellOut h f | .contrib f => .contribP f | .sellP => .sellP

def Inv (s : St) : Prop := s.a.usedPrior = 0 ∧ s.a.takenYr ≤ 15000 ∧ s.a.basisYr + s.a.basis + s.pBasisA ≤ 1000

theorem part_le (b n sh : Nat) (h : n ≤ sh) : b * n / sh ≤ b := by
  rcases Nat.eq_zero_or_pos sh with h0 | hp
  · subst h0; simp
  · exact Nat.div_le_of_le_mul (by rw [Nat.mul_comm sh b]; exact Nat.mul_le_mul_left b h)

theorem exch_inv (age : Nat) (i : Ind) (amt b : Nat) (hu : i.usedPrior = 0) (ht : i.takenYr ≤ 15000)
    (hb : i.basisYr + b ≤ 1000) :
    let j := (exchGain q age i amt b).1
    j.usedPrior = 0 ∧ j.takenYr ≤ 15000 ∧ j.basisYr ≤ i.basisYr + b ∧ j.basis = i.basis := by
  unfold exchGain
  by_cases hc : (i.q && decide (qPct q age > 0) && true) = true
  · simp only [hc, ite_true]
    refine ⟨hu, ?_, Nat.le_refl _, trivial⟩
    simp only [q, cfg0, qCap, ite_true, hu]
    simp only [Nat.max_def, Nat.min_def]
    repeat' split
    all_goals omega
  · simp only [hc]
    exact ⟨hu, ht, by simp, rfl⟩

theorem step_inv (s s' : St) (m : PM) (hI : Inv s) (h : stepClosed q s m.toMove = some s') : Inv s' := by
  obtain ⟨hu, ht, hb⟩ := hI
  cases m with
  | sell who f =>
    simp only [PM.toMove, stepClosed] at h
    split at h
    · rename_i hc
      have hn : (getI s who).sh / f ≤ (getI s who).sh := Nat.div_le_self _ _
      have hp := part_le (getI s who).basis _ _ hn
      cases who with
      | A =>
        simp only [getI] at hp h
        have hx := exch_inv s.age s.a ((s.a.sh / f) * (s.cash + s.aFmv) / outSh s) (s.a.basis * (s.a.sh / f) / s.a.sh) hu ht (by omega)
        simp only [setI, Option.some.injEq] at h
        subst h
        obtain ⟨h1, h2, h3, h4⟩ := hx
        refine ⟨h1, h2, ?_⟩
        simp only
        omega
      | K => simp only [setI, Option.some.injEq] at h; subst h; exact ⟨hu, ht, hb⟩
      | S => simp only [setI, Option.some.injEq] at h; subst h; exact ⟨hu, ht, hb⟩
    · cases h
  | contrib f =>
    simp only [PM.toMove, stepClosed] at h
    split at h
    · have hp := part_le s.a.basis _ _ (Nat.div_le_self s.a.sh f)
      simp only [Option.some.injEq] at h
      subst h
      refine ⟨hu, ht, ?_⟩
      simp only
      omega
    · cases h
  | sellP =>
    simp only [PM.toMove, stepClosed] at h
    split at h
    · have hx := exch_inv s.age { s.a with basis := s.pBasisA, q := s.pq }
        (s.pCash + (if s.pSh = 0 then 0 else s.pSh * (s.cash + s.aFmv) / outSh s)) s.pBasisA hu ht (by simp only; omega)
      simp only [Option.some.injEq] at h
      subst h
      obtain ⟨h1, h2, h3, h4⟩ := hx
      refine ⟨h1, h2, ?_⟩
      simp only at h3 ⊢
      omega
    · cases h

def runPM (s : St) : List PM → Option St
  | [] => some s
  | m :: ms => (stepClosed q s m.toMove).bind (fun s' => runPM s' ms)

theorem run_inv : ∀ (ms : List PM) (s s' : St), Inv s → runPM s ms = some s' → Inv s'
  | [], s, s', hI, h => by simp only [runPM, Option.some.injEq] at h; subst h; exact hI
  | m :: ms, s, s', hI, h => by
    simp only [runPM] at h
    cases hs : stepClosed q s m.toMove with
    | none => rw [hs] at h; cases h
    | some s1 => rw [hs] at h; exact run_inv ms s1 s' (step_inv s s1 m hI hs) h

theorem inv_start : Inv s0 := by unfold Inv; decide +kernel

/-- Closed-gap rule: whatever A does with these moves, in whatever order and number, the eligible gain taken into
account for A in the year, P stock included, is at most 15,000. -/
theorem closed_no_second_limit (ms : List PM) (s' : St) (h : runPM s0 ms = some s') : s'.a.takenYr ≤ 15000 :=
  (run_inv ms s0 s' inv_start h).2.1

#print axioms plan_original
#print axioms plan_original_final
#print axioms oneIssuer_original
#print axioms direct_original
#print axioms plain_original
#print axioms plan_closed
#print axioms oneIssuer_closed
#print axioms plain_closed
#print axioms least_original
#print axioms least_closed
#print axioms closed_no_second_limit
"""
write('RedT6.lean', base + T6 + CLOSE)
