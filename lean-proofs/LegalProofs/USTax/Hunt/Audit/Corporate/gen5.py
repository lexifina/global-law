import io
exec(io.open('gen.py', encoding='utf-8').read().split("def write(name, text):")[0])
def write(name, text): io.open(name, 'w', encoding='utf-8', newline='\n').write(text)
T5 = OPEN + r"""
/-- Everything the family owns plus all tax paid: cash in hand, P's cash, the family's and P's share of C at value. -/
def wealth (s : St) : Int :=
  let o := outSh s
  let fam := s.a.sh + s.k.sh + s.s.sh + s.pSh
  s.a.cash + s.k.cash + s.s.cash + (s.tax : Int) + (if s.pAlive then (s.pCash : Int) else 0)
    + (if s.alive && o > 0 then ((s.cash + s.aFmv) * fam / o : Nat) else 0)

structure Stats where
  n : Nat := 0
  wMax : Int := 0
  wMin : Int := 1000000
  wMaxPath : List Move := []
  wMinPath : List Move := []
  famMax : Int := 0
  minTaxFull : Nat := 1000000
  minTaxPath : List Move := []
  minTaxA : Nat := 1000000        -- full exit with all proceeds in A's hands
  minTaxAPath : List Move := []
  capBreak : Nat := 0             -- positions where a holder's excluded gain this year exceeds max(dollar limit, 10 x basis)
  totBreak : Nat := 0             -- positions where A's excluded gain over all years exceeds 15,000 + 10 x 1,000
  aTakenMax : Nat := 0
  basisBreak : Nat := 0           -- C corporation positions where stock basis in the family's hands exceeds the 1,000 paid
  negCash : Nat := 0
  up : Nat := 0
  upPath : List Move := []
  down : Nat := 0
  downMax : Int := 0
  downPath : List Move := []

def explore (cfg : Cfg) (depth : Nat) (s0 : St) (basis0 : Nat) : IO Stats := do
  let mut frontier : Array (St × List Move) := #[(s0, [])]
  let mut seen : Std.HashSet St := {}
  seen := seen.insert s0
  let mut st : Stats := {}
  for _ in [0:depth] do
    let mut next : Array (St × List Move) := #[]
    for (s, path) in frontier do
      for m in moves s do
        match step cfg s m with
        | none => pure ()
        | some s' =>
          if !seen.contains s' then
            seen := seen.insert s'
            let p := m :: path
            next := next.push (s', p)
            let w := wealth s'
            -- conservation per move: wealth + tax never rises, except by the corporate tax that falls on outside holders
            let o := outSh s
            let allow : Int := match m with
              | .sellAsset | .liquidate => if o > 0 then ((bp (s.aFmv - s.aBasis) rCorp * s.oSh / o + 1 : Nat) : Int) else 0
              | _ => 0
            let dlt := w - wealth s
            if dlt > allow then st := { st with up := st.up + 1, upPath := p }
            if dlt < -3 && !(s.oSh > 0) then st := { st with down := st.down + 1, downPath := p, downMax := max st.downMax (-dlt) }
            if w > st.wMax then st := { st with wMax := w, wMaxPath := p }
            if w < st.wMin then st := { st with wMin := w, wMinPath := p }
            let bad (i : Ind) : Bool := i.takenYr > max (qCap cfg - min (qCap cfg) i.usedPrior) (10 * i.basisYr) || i.takenYr > i.gainYr
            if bad s'.a || bad s'.k || bad s'.s then st := { st with capBreak := st.capBreak + 1 }
            if s'.a.usedPrior + s'.a.takenYr > qCap cfg + 10 * basis0 then st := { st with totBreak := st.totBreak + 1 }
            if s'.a.usedPrior + s'.a.takenYr > st.aTakenMax then st := { st with aTakenMax := s'.a.usedPrior + s'.a.takenYr }
            if !s'.isS && s'.a.basis + s'.k.basis + s'.s.basis + s'.pBasisA > basis0 then st := { st with basisBreak := st.basisBreak + 1 }
            match evaluate cfg true s' with
            | none => pure ()
            | some (fam, ao, tx) =>
              if fam > st.famMax then st := { st with famMax := fam }
              if tx < st.minTaxFull then st := { st with minTaxFull := tx, minTaxPath := p }
              if ao == fam && tx < st.minTaxA then st := { st with minTaxA := tx, minTaxAPath := p }
              if ao < 0 then st := { st with negCash := st.negCash + 1 }
    frontier := next
  return { st with n := seen.size }

def report (label : String) (st : Stats) : IO Unit := do
  IO.println s!"== {label}: {st.n} positions"
  IO.println s!"   wealth+tax: max {st.wMax} [{"; ".intercalate (st.wMaxPath.reverse.map showMove)}]"
  IO.println s!"               min {st.wMin} [{"; ".intercalate (st.wMinPath.reverse.map showMove)}]"
  IO.println s!"   best family money on full exit {st.famMax}; least tax on full exit {st.minTaxFull} [{"; ".intercalate (st.minTaxPath.reverse.map showMove)}]"
  IO.println s!"   least tax on full exit, all money to A: {st.minTaxA} [{"; ".intercalate (st.minTaxAPath.reverse.map showMove)}]"
  IO.println s!"   moves that raise wealth+tax: {st.up} [{"; ".intercalate (st.upPath.reverse.map showMove)}]; moves (no outside holders) that lose more than 3: {st.down}, worst {st.downMax} [{"; ".intercalate (st.downPath.reverse.map showMove)}]"
  IO.println s!"   yearly limit exceeded: {st.capBreak}; A lifetime bound exceeded: {st.totBreak}; A's largest excluded gain on C stock {st.aTakenMax}; basis created: {st.basisBreak}; negative A on full exit: {st.negCash}"

#eval do
  let q := { cfg0 with post2025 := true }
  report "T5 original rules, QSBS" (← explore q 4 (start true 5 10000 0 0) 1000)
  report "T5 original rules, not QSBS" (← explore cfg0 4 (start false 10 10000 0 0) 1000)
  report "T5 original rules, P deficit, literal 535(c)(2)" (← explore { cfg0 with aetLiteral := true } 4 (start false 10 10000 (-8000) 8000) 9000)
"""
write('RedT5.lean', base + T5 + CLOSE)
write('RedT5closed.lean', closed(base) + T5.replace('T5 original rules', 'T5 closed-gap rules') + CLOSE)
