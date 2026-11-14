import io
p='LegalProofs/USTax/Hunt/Charity.lean'
s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert a in s, a[:50]
    s=s.replace(a,b)
rep("let base := [u, 2 * u, 3 * u, p.target, rem, 30 * b0 / 100, 60 * b0 / 100]",
    "let base := [u, 2 * u, 3 * u, p.target, rem, 30 * b0 / 100, 60 * b0 / 100, b0 / 200]")
rep("| 8 => [rem * 100 / g, u * 100 / g]                       -- stock whose gain is what is left / one unit",
    "| 8 => [rem * 100 / g, p.target / 3 * 100 / g]            -- stock whose gain is what is left / a third of the target")
rep("| 10 => [min rem (s.tGain - s.tPaid), u]","| 10 => [min rem (s.tGain - s.tPaid)]")
i=s.index("def gifts (c"); j=s.index("end Legal.USTax.Hunt.Charity")
s=s[:i]+'''/-- F: AGI $500k, gives 30% of it in each year. -/
def pF : P := ⟨450000, 50000, 30000, 25, 450000, 0, 0, 238, 350⟩

def gifts (c : Nat) : Bool := c < 7
def withTrust (c : Nat) : Bool := c < 7 || (8 ≤ c && c ≤ 10)
def withCrat (c : Nat) : Bool := c < 7 || c == 11 || c == 12
def withCorp (c : Nat) : Bool := c < 7 || c == 13
#eval run "C: gifts above the percentage limits" pC (s0 1000000 3000000 1250000 0) gifts 6
#eval run "C: + children's trust" pC (s0 1000000 3000000 1250000 0) withTrust
#eval run "F: gifts at the 30% limit" pF (s0 1000000 3000000 1250000 0) gifts 6
#eval run "F: no QCD" pF (s0 1000000 3000000 1250000 0) (fun c => c < 6) 6

'''+s[j:]
io.open(p,'w',encoding='utf-8',newline='').write(s)
