p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a))
    s=s.replace(a,b)
# propYr
rep("  cashYr : Option Nat       -- year of the last contribution of money\n",
    "  cashYr : Option Nat       -- year of the last contribution of money\n  propYr : Option Nat       -- year of the last contribution of property\n")
rep("nonInv := P.nonInv || a.kind != .security })","nonInv := P.nonInv || a.kind != .security,\n             propYr := some s.year })")
rep("  let recentCash := match P0.cashYr with | some y => s0.year < y + 2 | none => false\n  guard (!(a0?.isSome && !own && (recentProp || recentCash)))",
    "  let recentCash := match P0.cashYr with | some y => s0.year < y + 2 | none => false\n  let recentAny := match P0.propYr with | some y => s0.year < y + 2 | none => false\n  guard (!(a0?.isSome && !own && (recentAny || recentCash)))")
rep("capGain := P.capGain + gain - loss, cashYr := none, nonInv := false })","capGain := P.capGain + gain - loss, cashYr := none, propYr := none,\n                                     nonInv := false })")
rep("def person0 (cash : Int) : Person := ⟨cash, 0, 0, 0, 0, 0, 0, none, false⟩","def person0 (cash : Int) : Person := ⟨cash, 0, 0, 0, 0, 0, 0, none, none, false⟩")
# disguised sale at a loss
rep("""          let gain := max 0 (t' * (z.fmv - z.basis) / z.fmv)
          if gain > 0 then
            s := modP s p (fun P => recG z.kind gain { P with outside := P.outside + gain })
            s := modA s j (fun z => { z with basis := z.basis + gain, big := z.big - gain })
          break""",
"""          let gain := t' * (z.fmv - z.basis) / z.fmv
          -- §707(b)(1)(A), (b)(3): a loss on a sale to the partnership is not allowed to a person who owns,
          -- directly or through family (§267(c)), more than half of it
          let tot := (caps s).foldl (· + ·) 0
          let mine := (List.range s.persons.size).foldl (fun acc i =>
            if i == p ∨ cfg.related p i then acc + s.persons[i]!.cap else acc) (0 : Int)
          let allowed := gain > 0 ∨ mine * 2 ≤ tot
          if gain != 0 then
            s := modP s p (fun P => (if allowed then recG z.kind gain else id)
              { P with outside := max 0 (P.outside + gain) })
            s := modA s j (fun z => { z with basis := z.basis + gain, big := z.big - gain })
          break""")
rep("  wait (toYear : Nat)               -- let a clock run (2 years, 7 years)","  | wait (toYear : Nat)               -- let a clock run (2 years, 7 years)",0) if False else None
# goalCash
a=s.index("/-- Goal 2: the family has X's value")
b=s.index("def showPerson")
s=s[:a]+'''/-- Goal 2: the family has nine tenths of X's value in new cash in hand while it still holds both X and Y, directly
or through a partnership in which no unrelated person has capital. -/
def goalCash (cfg : Cfg) (s0 s : State) : Bool :=
  s.persons[0]!.cash + s.persons[1]!.cash ≥ s0.persons[0]!.cash + s0.persons[1]!.cash + cfg.unit * 9 / 10 ∧
  famHolds s 0 ∧ famHolds s 1

'''+s[b:]
# scenarios
a=s.index("#eval search \"S1 X")
b=s.index("end Legal.USTax.Hunt.Partnership")
s=s[:a]+'''#eval search "S1 X 1000/100, Y 1000/1000" cfg1 6 start1 (fun _ => true)
#eval search "S1s X 300/60, Y 300/300" cfg1s 5 start1s (fun _ => true) 4
#eval search "S2 Y built-in loss 1000/1600" cfg1 6 start2 (fun _ => true) 12
#eval search "S3 C holds securities Z 1000/400" cfg1 5 start3 (fun _ => true)
#eval search "S4 Y inventory 1000/400" cfg1 6 start4 noD
#eval search "S5 as S1, debt-financed exception on" { cfg1 with debtFin := true } 5 start1 noD 4

'''+s[b:]
open(p,'w',encoding='utf-8',newline='').write(s)
