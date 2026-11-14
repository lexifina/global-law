"""Builds self-contained Red*.lean files: a copy of ../../Instruments.lean (rules + search) with audit knobs
(all default to the original behaviour), plus a per-test tail (tail_<X>.lean -> Red<X>.lean).
Never writes outside this folder."""
import io, os
here = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(here, '..', '..', 'Instruments.lean'), encoding='utf-8', newline='').read().replace('\r\n', '\n')
head, _ = src.split("/-! ### Runs -/")


def rep(a, b, n=1):
    global head
    assert head.count(a) == n, (a, head.count(a))
    head = head.replace(a, b)


rep("namespace Legal.USTax.Hunt.Instruments", "namespace Legal.USTax.Hunt.Audit.InstrumentsRed")
# knobs
rep("  maxTrades : Nat := 2\n", """  maxTrades : Nat := 2
  -- audit knobs (defaults = original behaviour)
  taintFix : Bool := false   -- T2: the §852(b)(4)(A) amount follows the §1091(d) basis into the replacement
  noWash : Bool := false     -- ablation: §1091(a) off for long sales
  noBasis : Bool := false    -- ablation: §1091(d) off (loss disallowed, basis not adjusted)
  noTack : Bool := false     -- ablation: §1223(3) off
  cgdOrd : Bool := false     -- ablation: §852(b)(3)(B) off (capital gain dividend taxed as ordinary dividend)
  no852b4 : Bool := false    -- ablation: §852(b)(4)(A) off
  six : Int := 183           -- §852(b)(4) period ("6 months or less"); 30 = the pre-1984 "less than 31 days"
  ban : List String := []    -- kinds of trade removed from the search
  oneLot : Bool := false     -- ablation: no second lot of an instrument already held long
  clearBy : Option (Nat × Nat) := none  -- (inst, date index): no lot of inst may be held on leaving that date or later
  strict : Bool := false     -- T1: §852(b)(4)(C)(ii) day cap; §1.1091-1(d) earliest-acquisition matching
""")
rep("  hedgeSI : List (Nat × Nat) := []     -- periods in which substantially identical property was held, §263(h)(4)(A)\n",
    "  hedgeSI : List (Nat × Nat) := []     -- periods in which substantially identical property was held, §263(h)(4)(A)\n"
    "  taint : Int := 0                     -- audit (T2): §852(b)(4)(A) amount inherited through §1091(d)\n")
rep("  final : Bool\n  deriving", "  final : Bool\n  taint : Int := 0\n  deriving")
rep("def settleDivs (s : St) (l : Lot) (t : Nat) : St :=", "def settleDivs (sc : Sc) (s : St) (l : Lot) (t : Nat) : St :=")
rep("    | .cgd => book s (yearOf ex) a .lt        -- §852(b)(3)(B)",
    "    | .cgd => if sc.cgdOrd then { s with yrs := modAt s.yrs (yearOf ex) fun y => { y with ord := y.ord + a } }\n"
    "              else book s (yearOf ex) a .lt        -- §852(b)(3)(B)")
rep("settleDivs (dropLot s k) k t", "settleDivs sc (dropLot s k) k t")
rep("(settleDivs (dropLot s l) l t,", "(settleDivs sc (dropLot s l) l t,")
rep("if x.long then settleDivs s x (t + 200)", "if x.long then settleDivs sc s x (t + 200)")
rep("def lossParts (l : Lot) (t : Nat) (amt : Int) (ch : Ch) : List (Int × Ch) :=\n  let short6 := heldAtRisk l t ≤ 183",
    "def lossParts (sc : Sc) (l : Lot) (t : Nat) (amt : Int) (ch : Ch) : List (Int × Ch) :=\n  let short6 := heldAtRisk l t ≤ sc.six")
rep("  let short6 := heldAtRisk l t ≤ sc.six", "  let tt : Nat := if sc.strict then l.divs.foldl (fun a d => min a (d.1 + 183)) t else t\n  let short6 := heldAtRisk l tt ≤ sc.six")
rep("      s.buys.find? fun (i, c, d) => c == I.cls", "      (if sc.strict then s.buys.reverse else s.buys).find? fun (i, c, d) => c == I.cls")
rep("  let cg := if short6 then sumK (fun d => d.2.2 == DK.cgd) else 0",
    "  let cg := if short6 && !sc.no852b4 then sumK (fun d => d.2.2 == DK.cgd) + (if sc.taintFix then l.taint else 0) else 0")
rep("  let parts := if isShort then [(amt0, ch)] else lossParts closed t amt0 ch",
    "  let parts := if isShort then [(amt0, ch)] else lossParts sc closed t amt0 ch\n"
    "  let tn : Int := if sc.taintFix && ch == Ch.st then parts.foldl (fun a q => if q.2 == Ch.lt then a - q.1 else a) 0 else 0")
rep("  let prior := if I.security && !isShort then", "  let prior := if I.security && !isShort && !sc.noWash then")
rep("""               { x with basis := x.basis - amt, hp := if x.noHP then x.hp else x.hp - held,
                        mixed := x.mixed || ch == Ch.split } else x }""",
    """               { x with basis := if sc.noBasis then x.basis else x.basis - amt,
                        hp := if x.noHP || sc.noTack then x.hp else x.hp - held,
                        taint := x.taint + tn,
                        mixed := x.mixed || ch == Ch.split } else x }""")
rep("washA := I.security && !isShort, washE := I.security && isShort, final := false } : PL)) ++ s.pls }",
    "washA := I.security && !isShort, washE := I.security && isShort, final := false,\n"
    "                       taint := if sc.taintFix && ch == Ch.st && c == Ch.lt then -a else 0 } : PL)) ++ s.pls }")
rep("  let pend := if J.acq then s.pls.find? fun q => q.washA && q.cls == J.cls && q.day + 30 ≥ t else none",
    "  let pend := if J.acq && !sc.noWash then s.pls.find? fun q => q.washA && q.cls == J.cls && q.day + 30 ≥ t else none")
rep("""    let lot := { lot with basis := p - tot, hp := if noHP then lot.hp else lot.hp - q.held,
                          mixed := lot.mixed || q.ch == Ch.split }""",
    """    let lot := { lot with basis := if sc.noBasis then p else p - tot,
                          hp := if noHP || sc.noTack then lot.hp else lot.hp - q.held,
                          taint := (s.pls.filter same).foldl (fun a r => a + r.taint) 0,
                          mixed := lot.mixed || q.ch == Ch.split }""")
rep("    (if room && !hasToday true && !opp true then",
    "    (if room && !hasToday true && !opp true && !(sc.oneLot && s.lots.any fun x => x.inst == j && x.long) then")
rep("  opens ++ closes\n", "  (opens ++ closes).filter fun x => !sc.ban.contains x.1.1\n")
rep("      if (sc.expo[i]!).contains (exposure s) then\n        let s' := advance sc s",
    "      if (sc.expo[i]!).contains (exposure s) &&\n"
    "         (match sc.clearBy with | some (j, d) => !(i ≥ d && s.lots.any fun x => x.inst == j) | none => true) then\n"
    "        let s' := advance sc s")
rep("    if !(sc.expo[i]!).contains (exposure s) then return none\n",
    "    if !(sc.expo[i]!).contains (exposure s) then return none\n"
    "    if (match sc.clearBy with | some (j, d) => i ≥ d && s.lots.any fun x => x.inst == j | none => false) then return none\n")

COMMON = io.open(os.path.join(here, 'common.lean'), encoding='utf-8').read()


def emit(name, tail):
    io.open(os.path.join(here, name), 'w', encoding='utf-8', newline='\n').write(
        head + COMMON + tail + "\nend Legal.USTax.Hunt.Audit.InstrumentsRed\n")


for f in sorted(os.listdir(here)):
    if f.startswith('tail_') and f.endswith('.lean'):
        emit('Red' + f[5:], io.open(os.path.join(here, f), encoding='utf-8').read())
        print('wrote', 'Red' + f[5:])
