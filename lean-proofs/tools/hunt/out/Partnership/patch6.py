p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a))
    s=s.replace(a,b)
rep("""        let amt := a.big - a.adj[q]!
        s := modP s q (fun Q => recG a.kind amt { Q with outside := max 0 (Q.outside + amt) })""",
"""        let amt := a.big - a.adj[q]!
        -- §704(c)(1)(B)(ii) treats it as a sale by the partnership to the distributee, so §707(b)(1)(A), (b)(3)
        -- denies a loss when the distributee owns, directly or through family, more than half (T.D. 8642)
        let tot := (caps s).foldl (· + ·) 0
        let his := (List.range s.persons.size).foldl (fun acc i =>
          if i == p ∨ cfg.related p i then acc + s.persons[i]!.cap else acc) (0 : Int)
        let allowed := amt > 0 ∨ his * 2 ≤ tot
        s := modP s q (fun Q => (if allowed then recG a.kind amt else id) { Q with outside := max 0 (Q.outside + amt) })""")
# fourth goal
rep("""/-- Goal 3: every asset has been sold for cash (the cash may still be inside a continuing partnership). -/""",
"""/-- Goal 4: nothing has been sold and the family holds, directly or through an all-family partnership, every asset
it held or had contributed at the start. -/
def goalKeep (cfg : Cfg) (s0 s : State) : Bool :=
  s.assets.size == s0.assets.size ∧ (List.range s0.assets.size).all (fun i =>
    let a0 := s0.assets[i]!
    let a := s.assets[i]!
    let mine := match a0.holder with
      | .person p => cfg.fam p
      | .pship => (a0.contrib.map cfg.fam).getD false
      | .sold => false
    !mine ∨ (match a.holder with | .person p => cfg.fam p | _ => false))

/-- Goal 3: every asset has been sold for cash (the cash may still be inside a continuing partnership). -/""")
rep("let mut hits : Array (Std.HashMap Nat Hit) := #[{}, {}, {}]","let mut hits : Array (Std.HashMap Nat Hit) := #[{}, {}, {}, {}]")
rep("let gs := [goalOut cfg s0 s', goalCash cfg s0 s', goalSold s']","let gs := [goalOut cfg s0 s', goalCash cfg s0 s', goalSold s', goalKeep cfg s0 s' && famTax cfg s' < 0]")
rep("for k in [0:3] do\n                  if gs[k]! then","for k in [0:4] do\n                  if gs[k]! then")
rep("""  let names := ["X sold out of the family for cash, Y kept", "cash in hand, X and Y kept", "every asset sold"]
  for k in [0:3] do""","""  let names := ["X sold out of the family for cash, Y kept", "cash in hand, X and Y kept", "every asset sold",
                "a loss taken while the family keeps every asset"]
  for k in [0:4] do""")
a=s.index("def simple : Move → Bool")
b=s.index("end Legal.USTax.Hunt.Partnership")
s=s[:a]+'''/-- S8. A partnership formed three years ago: A put in 1,000 of cash, B (related to A) put in Y (1,000, basis
1,600), C (unrelated) put in 2,000 of cash. The family holds exactly half. -/
def start8 : State :=
  { year := 3, pcash := 3000, elect := false, everNonInv := true, carry := 0,
    assets := #[held 1 .capital 1000 1600 1],
    persons := #[{ partner0 0 1000 1000 with cashYr := some 0 }, partner0 0 1600 1000,
                 { partner0 0 2000 2000 with cashYr := some 0 }, person0 2000] }

/-- S8b. The same, but C put in 1,000, so the family holds two thirds. -/
def start8b : State :=
  { start8 with pcash := 2000,
                persons := #[{ partner0 0 1000 1000 with cashYr := some 0 }, partner0 0 1600 1000,
                             { partner0 0 1000 1000 with cashYr := some 0 }, person0 2000] }

def simple : Move → Bool
  | .borrow .. => false | .repay .. => false | .buy .. => false | .contribCash .. => false | .sellInt .. => false
  | .contribute .. => false | _ => true

def propOnly : Move → Bool
  | .dist _ none _ => false | .dist _ (some _) c => c == 0 | m => simple m

#eval search "S1 X 1000/100, Y 1000/1000" cfg1 6 start1 (fun _ => true) 4
#eval search "S1s X 300/60, Y 300/300" cfg1s 5 start1s (fun _ => true) 2
#eval search "S2 Y built-in loss 1000/1600" cfg1 6 start2 (fun _ => true) 8
#eval search "S3 C holds securities Z 1000/400" cfg1 5 start3 (fun _ => true) 3
#eval search "S4 Y inventory 1000/400" cfg1 6 start4 noD 4
#eval search "S5 as S1, debt-financed exception on" { cfg1 with debtFin := true } 5 start1 noD 3
#eval search "S6 existing partnership, parcels under $250k" cfg6 6 start6 propOnly 4
#eval search "S6b same, single pieces over $250k" cfg6 4 start6b propOnly 4
#eval search "S7 existing partnership with loss asset and securities" cfg1 4 start7 (fun _ => true) 6
#eval search "S8 loss asset, family holds half" cfg1 3 start8 simple 4
#eval search "S8b loss asset, family holds two thirds" cfg1 3 start8b simple 4

'''+s[b:]
open(p,'w',encoding='utf-8',newline='').write(s)
