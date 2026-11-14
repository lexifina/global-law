p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a))
    s=s.replace(a,b)
# a. 704(c)(1)(B) net of 743(b)
rep("""      if q != p ∧ s.year < a.yr + 7 ∧ a.big != 0 then
        s := modP s q (fun Q => recG a.kind a.big { Q with outside := max 0 (Q.outside + a.big) })
        s := modA s i (fun a => { a with basis := a.basis + a.big, big := 0 })""",
"""      if q != p ∧ s.year < a.yr + 7 ∧ a.big != 0 then
        -- the amount he would have been allocated on a sale, so net of his own §743(b) adjustment
        let amt := a.big - a.adj[q]!
        s := modP s q (fun Q => recG a.kind amt { Q with outside := max 0 (Q.outside + amt) })
        s := modA s i (fun a => { a with basis := a.basis + a.big, big := 0, adj := a.adj.set! q 0 })""")
rep("some b.id != ai then acc + b.big else acc) 0)","some b.id != ai then acc + b.big - b.adj[p]! else acc) 0)")
rep("""        let x := min left b.big
        s := modP s p (fun P => recG b.kind x { P with outside := P.outside + x })""",
"""        let x := min left (b.big - b.adj[p]!)
        s := modP s p (fun P => recG b.kind x { P with outside := P.outside + x })""")
rep("∧ some b.id != ai ∧ b.big > 0 then","∧ some b.id != ai ∧ b.big - b.adj[p]! > 0 then")
# c. reorder
a=s.index("  -- a partner who has left: §704(c)(1)(C)")
b=s.index("  -- 8. §734(b)")
c=s.index("  -- 9. §751(b)")
cleanup='''  -- a partner who has left: his §704(c)(1)(C) built-in loss is no longer anyone's (the others' basis is the value
  -- at contribution); his built-in gain is shared by those who remain
  if liq then
    for j in [0:s.assets.size] do
      let b := s.assets[j]!
      if b.holder == .pship ∧ b.succ == some p then
        let cut := if b.big < 0 then min (-b.big) (max 0 (b.basis - b.fmv)) else 0
        s := modA s j (fun b => { b with succ := none, basis := b.basis - cut, big := 0 })
      s := modA s j (fun b => { b with adj := b.adj.set! p 0 })
'''
s=s[:a]+s[b:c]+cleanup+s[c:]
# d. termination
a=s.index("/-- Sale of a whole interest for its value.")
term='''/-- Make a list of bases add up to `target`: §732(c)(2) for an increase (first to appreciated property in
proportion to appreciation, then by value), §732(c)(3) for a decrease (first to depreciated property in proportion
to depreciation, then by basis). Items are (basis, value). -/
def fitBasis (items : Array (Int × Int)) (target : Int) : Array Int := Id.run do
  let bases := items.map (·.1)
  let diff := target - bases.foldl (· + ·) 0
  if diff ≥ 0 then
    let app := items.map (fun (b, f) => max 0 (f - b))
    let d1 := min diff (app.foldl (· + ·) 0)
    let x1 := spread app d1
    let x2 := spread (items.map (·.2)) (diff - d1)
    return (List.range items.size).toArray.map (fun i => bases[i]! + x1[i]! + x2[i]!)
  else
    let m := -diff
    let dep := items.map (fun (b, f) => max 0 (b - f))
    let d1 := min m (dep.foldl (· + ·) 0)
    let x1 := spread dep d1
    let b1 := (List.range items.size).toArray.map (fun i => bases[i]! - x1[i]!)
    let x2 := spread b1 (min (m - d1) (b1.foldl (· + ·) 0))
    return (List.range items.size).toArray.map (fun i => b1[i]! - x2[i]!)

def partners (s : State) : List Nat := (List.range s.persons.size).filter (fun i => s.persons[i]!.cap > 0)

/-- §708(b)(1): when only one partner is left, nothing is carried on "in a partnership"; it has terminated and he
holds the property. §731(a): gain if the money exceeds his interest basis; loss only if he receives nothing but
money and inventory. §732(b), (c): his interest basis less money becomes the basis of the property, inventory
first and never above the partnership's basis. He takes over the liabilities (§752(a) and (b) offset). -/
def terminate (s : State) : State := Id.run do
  match partners s with
  | [p] =>
    let P := s.persons[p]!
    let gain := max 0 (s.pcash - P.outside)
    let rem := max 0 (P.outside - s.pcash)
    let held (inv : Bool) (a : Asset) : Bool := a.holder == .pship ∧ (a.kind == .inventory) == inv
    let item (a : Asset) : Int × Int := (a.basis + a.adj[p]!, a.fmv)
    let invIdx := (List.range s.assets.size).filter (fun i => held true s.assets[i]!)
    let capIdx := (List.range s.assets.size).filter (fun i => held false s.assets[i]!)
    let invItems := invIdx.toArray.map (fun i => item s.assets[i]!)
    let invTot := invItems.foldl (fun acc x => acc + x.1) 0
    let invB := if rem < invTot then fitBasis invItems rem else invItems.map (·.1)
    let rem2 := max 0 (rem - invTot)
    let capItems := capIdx.toArray.map (fun i => item s.assets[i]!)
    let capB := fitBasis capItems rem2
    let loss := if capIdx.isEmpty then rem2 else 0
    let mut s := s
    let setB (s : State) (i : Nat) (b : Int) : State :=
      modA s i (fun a => { a with basis := b, holder := .person p, contrib := none, succ := none, big := 0,
                                  adj := zeroAdj s.persons.size })
    for k in [0:invIdx.length] do s := setB s invIdx[k]! invB[k]!
    for k in [0:capIdx.length] do s := setB s capIdx[k]! capB[k]!
    s := modP s p (fun P => { P with cash := P.cash + s.pcash - P.liab, outside := 0, cap := 0, liab := 0, susp := 0,
                                     capGain := P.capGain + gain - loss, cashYr := none, nonInv := false })
    return { s with pcash := 0, elect := false, everNonInv := false, carry := 0 }
  | _ => return s

'''
s=s[:a]+term+s[a:]
rep("  | .dist p a cash => distribute cfg s p a cash\n  | .sellInt p q => sellInt cfg s p q",
    "  | .dist p a cash => (distribute cfg s p a cash).map terminate\n  | .sellInt p q => (sellInt cfg s p q).map terminate")
rep("  | .borrow g amt => borrow s g amt","  | .borrow g amt => if (partners s).length < 2 then none else borrow s g amt")
rep("  | .pSell a => pSell s a","  | .pSell a => if (partners s).length < 2 then none else pSell s a")
rep("  | .buy amt => buy s amt","  | .buy amt => if (partners s).length < 2 then none else buy s amt")
rep("  | .elect => if s.elect then none","  | .elect => if s.elect ∨ (partners s).length < 2 then none")
# g amounts
rep("for c in [min s.pcash P.cap, min s.pcash P.outside, min s.pcash cfg.unit].eraseDups do",
    "for c in [min s.pcash P.cap, min s.pcash P.outside, min s.pcash cfg.unit, min s.pcash (P.cap * 9 / 10)].eraseDups do")
# f ranking
rep("""structure Hit where
  taxNow : Int""","""structure Hit where
  taxNow : Int      -- the family's tax so far, plus any tax so far of the unrelated partners (their losses not credited)
  others : Int      -- the unrelated partners' tax so far (negative: losses)""")
rep("let h : Hit := ⟨totalTax s', totalTax (windup s'), s'.year, d, path', s'⟩",
    "let oth := totalTax s' - famTax s'\n                let h : Hit := ⟨famTax s' + max 0 oth, oth, totalTax (windup s'), s'.year, d, path', s'⟩")
rep("""IO.println s!"  tax now ${h.taxNow}  tax if all later sold and wound up ${h.taxAll}  year {h.year}  [{sigName (sigOf h.path)}]\"""",
    """IO.println s!"  family tax now ${h.taxNow}  (unrelated partners now ${h.others})  everyone, once all is sold and wound up ${h.taxAll}  year {h.year}  [{sigName (sigOf h.path)}]\"""")
open(p,'w',encoding='utf-8',newline='').write(s)
