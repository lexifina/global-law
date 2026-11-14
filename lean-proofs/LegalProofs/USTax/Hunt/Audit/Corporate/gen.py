# Red-team generator: builds Red*.lean from a verbatim copy of Corporate.lean lines 1-532 plus patches.
import io, sys
src = io.open('../../Corporate.lean', encoding='utf-8', newline='').read().replace('\r\n', '\n').split('\n')
base = '\n'.join(src[:532]) + '\n'
assert base.rstrip().endswith('end Legal.USTax.Hunt.Corporate')

def rep(t, old, new):
    assert t.count(old) == 1, (t.count(old), old[:60])
    return t.replace(old, new)

OPEN = '\nnamespace Legal.USTax.Hunt.Corporate\ndef plain : List Move := [.sellAsset, .dividend 33700]\ndef all : Move → Bool := fun _ => true\n'
CLOSE = '\nend Legal.USTax.Hunt.Corporate\n'

SELLP_OLD = """      let (j, t) := exchGain cfg s.age { ind0 with sh := 1, basis := s.pBasisA, cash := s.a.cash, q := s.pq } price s.pBasisA
      some { s with a := { s.a with cash := j.cash }, pAlive := false, oSh := s.oSh + s.pSh, pSh := 0, pCash := 0,
                    pBasisA := 0, pBasisC := 0, tax := s.tax + t }"""

def strict(t):
    # T1: (h)(4)(B) cap always applied; §351 "immediately after" proxied by a year end between contribution and sale
    t = rep(t, "  pq : Bool          -- A's P stock is treated as qualified small business stock (§1202(h)(4)(A))\n",
               "  pq : Bool\n  pCapGain : Nat := 0   -- RED: §1202(h)(4)(B) gain built in at the transfer\n")
    t = rep(t, "pAffil := false, pq := pq }", "pAffil := false, pq := pq,\n                    pCapGain := s.pCapGain + (n * (s.cash + s.aFmv) / outSh s - bPart) }")
    t = rep(t, "if s.pAlive ∧ (s.pSh > 0 ∨ s.pCash > 0) ∧ s.pPend = 0 ∧ s.pDivYr = 0 ∧ s.pDist = 0 then\n      let price",
               "if s.pAlive ∧ (s.pSh > 0 ∨ s.pCash > 0) ∧ s.pPend = 0 ∧ s.pDivYr = 0 ∧ s.pDist = 0 ∧ (s.pSh = 0 ∨ s.pAffil) then\n      let price")
    t = rep(t, SELLP_OLD, """      let gain := price - s.pBasisA
      let elig := min gain s.pCapGain
      let amt1 := min price (s.pBasisA + elig)
      let (j, t) := exchGain cfg s.age { ind0 with sh := 1, basis := s.pBasisA, cash := s.a.cash, q := s.pq } amt1 s.pBasisA
      let t2 := bp (gain - elig) rLT
      some { s with a := { s.a with cash := j.cash + (price - amt1) - t2 }, pAlive := false, oSh := s.oSh + s.pSh, pSh := 0, pCash := 0,
                    pBasisA := 0, pBasisC := 0, tax := s.tax + t + t2 }""")
    return t

def closed(t):
    # T2: (h)(4) stock treated as issued by the corporation that issued the exchanged stock, for §1202(b)
    return rep(t, SELLP_OLD, """      let (j, t) := exchGain cfg s.age { s.a with basis := s.pBasisA, q := s.pq } price s.pBasisA
      some { s with a := { j with basis := s.a.basis }, pAlive := false, oSh := s.oSh + s.pSh, pSh := 0, pCash := 0,
                    pBasisA := 0, pBasisC := 0, tax := s.tax + t }""")

def write(name, text):
    io.open(name, 'w', encoding='utf-8', newline='\n').write(text)

Q = "  let q := { cfg0 with post2025 := true }\n"
S2 = '  search "{l}" {c} {d} (start true {age} 10000 0 0) true {al} plain 8 false\n'

write('RedT1.lean', strict(base) + OPEN + "#eval do\n" + Q +
  S2.format(l="T1 strict: (h)(4)(B) cap always, sale of P only after a year end", c="q", d=4, age=5, al="all") +
  '  search "T1 strict, not QSBS control" cfg0 4 (start false 10 10000 0 0) true all plain 3\n' + CLOSE)

write('RedT2.lean', closed(base) + OPEN + "#eval do\n" + Q +
  S2.format(l="T2 closed gap: QSBS full exit, money to A", c="q", d=4, age=5, al="all") +
  '  search "T2 closed gap: money to family" q 4 (start true 5 10000 0 0) true all plain 6\n' +
  '  search "T2 closed gap: not QSBS" cfg0 4 (start false 10 10000 0 0) true all plain 3\n' + CLOSE)

T3 = OPEN + """def noSell : Move → Bool | .sellOut _ _ => false | _ => true
def noContrib : Move → Bool | .contribP _ => false | _ => true
def noSellP : Move → Bool | .sellP => false | _ => true
def onlyPlanKinds : Move → Bool | .sellOut .A _ | .contribP _ | .sellP => true | _ => false
def onlyPlanMoves : Move → Bool | .sellOut .A 5 | .contribP 1 | .sellP => true | _ => false
#eval do
""" + Q + ''.join(S2.format(l=l, c="q", d=4, age=5, al=a) for l, a in [
  ("T3 without sellOut", "noSell"), ("T3 without contribP", "noContrib"), ("T3 without sellP", "noSellP"),
  ("T3 only the plan's kinds of move", "onlyPlanKinds"), ("T3 only the plan's three moves", "onlyPlanMoves")]) + CLOSE
write('RedT3.lean', base + T3)

T4 = OPEN + "#eval do\n" + Q + \
  S2.format(l="T4 pre-July-2025 text ($10m, 5 years, no tiers), stock 6 years old", c="cfg0", d=4, age=6, al="all") + \
  S2.format(l="T4 post-2025 text, stock 3 years old (50% tier)", c="q", d=4, age=3, al="all") + \
  S2.format(l="T4 post-2025 text, stock 4 years old (75% tier)", c="q", d=4, age=4, al="all") + \
  '  search "T4 no section 1202 (pre-1993): stock not qualified" cfg0 4 (start false 10 10000 0 0) true all plain 3 false\n' + CLOSE
write('RedT4.lean', base + T4)
print('ok')
