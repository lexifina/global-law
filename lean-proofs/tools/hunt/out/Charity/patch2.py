import io
p='LegalProofs/USTax/Hunt/Charity.lean'
s=io.open(p,encoding='utf-8',newline='').read()
i=s.index("def giftsOnly"); j=s.index("end Legal.USTax.Hunt.Charity")
s=s[:i]+'''/-- D: as A but under 70 1/2: no IRA distributions, no QCD. -/
def pD : P := ⟨200000, 0, 20000, 25, 36000, 0, 0, 150, 220⟩
/-- E: as B, with two adult children who pay tax and a C corporation earning $2M a year. -/
def pE : P := ⟨1200000, 100000, 60000, 25, 300000, 2, 2000000, 238, 370⟩

def gifts (c : Nat) : Bool := c < 7
def withTrust (c : Nat) : Bool := c < 7 || (8 ≤ c && c ≤ 10)
def withCrat (c : Nat) : Bool := c < 7 || c == 11 || c == 12
def withCorp (c : Nat) : Bool := c < 7 || c == 13
#eval run "A: moderate income; gifts, SGO, QCD" pA (s0 1000000 500000 1000000 0) gifts 6
#eval run "A: + children's trust" pA (s0 1000000 500000 1000000 0) withTrust
#eval run "A: + annuity trust" pA (s0 1000000 500000 1000000 0) withCrat
#eval run "D: no IRA; gifts, SGO" pD (s0 1000000 500000 0 0) gifts 6
#eval run "D: + children's trust" pD (s0 1000000 500000 0 0) withTrust
#eval run "B: high income; gifts, SGO, QCD" pB (s0 3000000 3000000 2500000 0) gifts 6
#eval run "B: + children's trust" pB (s0 3000000 3000000 2500000 0) withTrust
#eval run "B: + annuity trust" pB (s0 3000000 3000000 2500000 0) withCrat
#eval run "E: B + adult children + corporation" pE (s0 3000000 3000000 2500000 5000000) withCorp
#eval run "C: gifts above the percentage limits" pC (s0 1000000 3000000 1250000 0) gifts 6
#eval run "C: + children's trust" pC (s0 1000000 3000000 1250000 0) withTrust

'''+s[j:]
io.open(p,'w',encoding='utf-8',newline='').write(s)
