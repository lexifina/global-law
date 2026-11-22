import TaxCode.Individual.B.Properties
import TaxCode.Individual.B.Forms

/-! Axiom audit for group B's main theorems: each should list only `propext`, `Classical.choice`, `Quot.sound`
(or none). -/

namespace TaxCode.Individual.B

/-- Two seniors on a joint return face 12% combined: at MAGI $200,000 each $6,000 is cut by 6% of $50,000. -/
theorem senior_two_at_200k :
    seniorDeduction { filing := .mfj, head := { age := 70 }, spouse := some { age := 67 } } 200000 = 6000 := by decide

#print axioms salt_step_300
#print axioms salt_floor
#print axioms salt_mfs_step_150
#print axioms salt_split_ge_joint
#print axioms itemized_salt_step
#print axioms senior_rate
#print axioms seniorDeduction_step
#print axioms senior_within_63f
#print axioms tips_antitone
#print axioms tips_average
#print axioms car_gone
#print axioms medical_exceeds_expenses
#print axioms taxableBeforeQbi_mono
#print axioms taxableBeforeQbi_step
#print axioms qbiPhase_antitone
#print axioms qbi_net_mono
#print axioms taxableIncome_mono
#print axioms notch_qbi
#print axioms scheduleASalt_eq
#print axioms sched1aCar_eq
#print axioms pub501_dep_ex4
#print axioms qbiPhase_midpoint
#print axioms sstbShare_midpoint

end TaxCode.Individual.B
