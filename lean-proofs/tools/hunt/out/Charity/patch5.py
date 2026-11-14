import io
p='LegalProofs/USTax/Hunt/Charity.lean'
s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert a in s, a[:50]
    s=s.replace(a,b)
rep("""  corpCo : Nat
  deriving BEq, Hashable, Repr""","""  corpCo : Nat
  sgoIra : Nat   -- paid this year by the IRA trustee straight to a scholarship granting organization
  deriving BEq, Hashable, Repr""")
rep("""  | corpCash (a : Nat)   -- the corporation gives cash: §170(b)(2)
""","""  | corpCash (a : Nat)   -- the corporation gives cash: §170(b)(2)
  | iraSgo (a : Nat)     -- the IRA trustee pays a scholarship granting organization direct: §408(d)(8), §25F
""")
rep("""  let forced := p.rmd - min p.rmd s.qcd                 -- §408(d)(8): a QCD counts toward the RMD and is excluded
  let gain :=""","""  -- An IRA payment to a scholarship granting organization for which the §25F credit is allowed is "not taken into
  -- account as a charitable contribution for purposes of section 170" (§25F(e)); so a §170 deduction "for the entire
  -- distribution" is not allowable and none of it is a QCD (§408(d)(8)(C)): all of it is income. What exceeds the
  -- credit is an ordinary cash gift.
  let cap := if s.yr ≥ 1 then 1700 * (1 + p.kids) else 0
  let sx := s.sgo + s.sgoIra - min cap (s.sgo + s.sgoIra)
  let forced := p.rmd - min p.rmd (s.qcd + s.sgoIra)    -- §408(d)(8): a QCD counts toward the RMD and is excluded
  let gain :=""")
rep("let b := p.ord + forced + gain ","let b := p.ord + forced + s.sgoIra + gain ")
rep("let gT := s.gCash + s.gDaf + s.coG","let gT := s.gCash + s.gDaf + sx + s.coG")
rep("let anyX := s.gCash + s.gDaf > gA","let anyX := s.gCash + s.gDaf + sx > gA")
rep("let credit := if s.yr ≥ 1 then min (1700 * (1 + p.kids)) s.sgo else 0  -- §25F(a),(b)(1): per taxpayer",
    "let credit := min cap (s.sgo + s.sgoIra)              -- §25F(a),(b)(1): per taxpayer; nonrefundable")
rep("""  | .close =>
    if s.yr ≥ 3 then none else""","""  | .iraSgo a => if 0 < a ∧ a ≤ s.ira ∧ s.yr ≥ 1 ∧ s.qcd + s.sgoIra + a ≤ qcdCap then
      some { s with ira := s.ira - a, sgoIra := s.sgoIra + a, given := s.given + a } else none
  | .close =>
    if s.yr ≥ 3 then none else""")
rep("""    let forced := p.rmd - min p.rmd s.qcd
    let f := min forced s.ira""","""    let forced := p.rmd - min p.rmd (s.qcd + s.sgoIra)
    let f := min forced s.ira""")
rep("corp := s.corp + cSave, corpGift := 0, corpCo := cCo }","corp := s.corp + cSave, corpGift := 0, corpCo := cCo, sgoIra := 0 }")
rep("def nChan : Nat := 14","def nChan : Nat := 15")
rep("| .corpCash _ => 13 | .close => 14","| .corpCash _ => 13 | .iraSgo _ => 14 | .close => 15")
rep("""  | 13 => "corpCash" | _ => "close\"""","""  | 13 => "corpCash" | 14 => "IRA->SGO" | _ => "close\"""")
rep("""  | _ => .corpCash a
def amt""","""  | 13 => .corpCash a | _ => .iraSgo a
def amt""")
rep("| .fundTrust a | .trustSell a | .trustPay a | .fundCrat5 a | .fundCrat45 a | .corpCash a => a",
    "| .fundTrust a | .trustSell a | .trustPay a | .fundCrat5 a | .fundCrat45 a | .corpCash a | .iraSgo a => a")
rep("    | 13 => [u, rem, p.corpTI / 10, p.corpTI / 100]","    | 13 => [u, rem, p.corpTI / 10, p.corpTI / 100]\n    | 14 => [1700, u]")
rep("| 8 | 9 | 10 => 5 | 11 | 12 => 6 | _ => 7","| 8 | 9 | 10 => 5 | 11 | 12 => 6 | 13 => 7 | _ => 8")
rep("""  | 6 => "CRAT" | _ => "corporate gift\"""","""  | 6 => "CRAT" | 7 => "corporate gift" | _ => "IRA->SGO\"""")
rep("((List.range 8).filter","((List.range 9).filter")
rep("0, 0, 0, 0, 0, 0, 0, corp, 0, 0⟩","0, 0, 0, 0, 0, 0, 0, corp, 0, 0, 0⟩")
i=s.index("def sel (l"); j=s.index("end Legal.USTax.Hunt.Charity")
s=s[:i]+'''def sel (l : List Nat) (c : Nat) : Bool := l.contains c

-- Round 1: gifts, the credit, IRA distributions
#eval run "A: moderate income; gifts, SGO, QCD" pA (s0 1000000 500000 1000000 0) gifts 6
#eval run "A: + IRA paid straight to an SGO" pA (s0 1000000 500000 1000000 0) (sel [0, 3, 5, 6, 14])
#eval run "D: no IRA; gifts, SGO" pD (s0 1000000 500000 0 0) gifts 6
#eval run "B: high income; gifts, SGO, QCD" pB (s0 3000000 3000000 2500000 0) gifts 6
-- Round 2: trusts and the corporation
#eval run "D: + children's trust" pD (s0 1000000 500000 0 0) (sel [0, 3, 5, 8, 9, 10])
#eval run "B: + annuity trust" pB (s0 3000000 3000000 2500000 0) withCrat
#eval run "E: B + adult children + corporation" pE (s0 3000000 3000000 2500000 5000000) withCorp
-- Slower (41 s and 59 s), output kept in tools/hunt/out/Charity/run2.txt:
-- #eval run "A: + children's trust" pA (s0 1000000 500000 1000000 0) withTrust
-- #eval run "B: + children's trust" pB (s0 3000000 3000000 2500000 0) withTrust
-- Round 3: gifts larger than the percentage limits
#eval run "C: cash, stock to public charity, SGO, QCD" pC (s0 1000000 3000000 1250000 0) (sel [0, 3, 5, 6])
#eval run "C: stock to either, QCD" pC (s0 1000000 3000000 1250000 0) (sel [3, 4, 6])
#eval run "C: stock, QCD, children's trust" pC (s0 1000000 3000000 1250000 0) (sel [3, 6, 8, 9, 10])
#eval run "F: cash, stock to public charity, SGO, QCD" pF (s0 1000000 3000000 1250000 0) (sel [0, 3, 5, 6])
#eval run "F: stock to either, no QCD" pF (s0 1000000 3000000 1250000 0) (sel [3, 4])
#eval run "F: stock, children's trust" pF (s0 1000000 3000000 1250000 0) (sel [3, 8, 9, 10])

'''+s[j:]
io.open(p,'w',encoding='utf-8',newline='').write(s)
