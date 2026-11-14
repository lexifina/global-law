"""Red-team generator: copies the Rules part of the original Residence.lean (read-only) and applies named patches.
Every patch is an exact-string replacement that must match exactly once. Writes Red*.lean in this folder from
Red*.body (the test-specific tail)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'Residence.lean')
src = open(SRC, encoding='utf-8', newline='').read().replace('\r\n', '\n')
rules = src[:src.index("/-! ## Search -/")]
tail_defs = src[src.index("structure Start where"):src.index("def allMoves")] \
    + src[src.index("def tagNames"):src.index("structure Best where")] \
    + src[src.index("/-- The fine grid"):src.index("/-! Recorded runs -/")]


def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a)
    return s.replace(a, b)


r = rules.replace("namespace Legal.USTax.Hunt.Residence", "namespace Legal.USTax.Hunt.Audit.ResidenceRed")
# --- switches (all default to the original behaviour) ---
r = rep(r, "  endInUS : Bool        -- search filter: count only plans with 183 or more US days in the last year\n",
        "  endInUS : Bool        -- search filter: count only plans with 183 or more US days in the last year\n"
        "  fixA : Bool := false      -- T2: §877A(a)(3) denied if resident for the calendar year after the expatriation year\n"
        "  fixC : Bool := false      -- T2: §877A(a)(3) denied if covered solely by §877(a)(2)(C)\n"
        "  pre2008 : Bool := false   -- T4: law before the HEART Act (no §877A; §877(b) for covered expatriates)\n"
        "  noSeg0Exit : Bool := false -- T1: no expatriation on 1 January of year 0 (deemed sale would fall in the prior year)\n"
        "  ira : Nat := 0            -- T1: balance of a specified tax deferred account, §877A(e)(1)\n"
        "  exclusion : Nat := 890000 -- §877A(a)(3)\n")
r = rep(r, "  resPrev : Bool    -- resident at any time during the preceding year\n  deriving BEq, Hashable, Repr\n",
        "  resPrev : Bool    -- resident at any time during the preceding year\n"
        "  cov : Bool := false   -- RED: covered expatriate at year end (used only when pre2008)\n  deriving BEq, Hashable, Repr\n")
r = rep(r, "          g877 := if p.asset == .usStock || usSource then bp ltcgBp sale else 0\n",
        "          g877 := if p.asset == .usStock || usSource then bp ltcgBp sale else 0\n"
        "          -- RED T4: pre-2008 §877(a)(1): the §877(b) tax if greater than the §871 tax\n"
        "          if p.pre2008 && pd.cov then g871 := max g871 g877\n")
r = rep(r, "  tags : Nat\n  deriving BEq, Hashable, Repr, Inhabited\n",
        "  tags : Nat\n  exitYr : Nat := 99        -- RED: year of the expatriation\n"
        "  exclAmt : Nat := 0       -- RED: gain removed by §877A(a)(3)\n"
        "  resAfter : Bool := false -- RED: resident for the calendar year after the expatriation year\n"
        "  exits : Nat := 0\n  deriving BEq, Hashable, Repr, Inhabited\n")
r = rep(r, "  let s := { s with usTax := s.usTax + t.us, forTax := s.forTax + t.foreign, gainTax := s.gainTax + t.gainTax,\n"
           "                    tags := s.tags ||| t.tags }\n",
        "  let s := { s with usTax := s.usTax + t.us, forTax := s.forTax + t.foreign, gainTax := s.gainTax + t.gainTax,\n"
        "                    tags := s.tags ||| t.tags }\n"
        "  -- RED: was the person a resident for the calendar year following the year of expatriation?\n"
        "  let after := s.exitYr != 99 && y == s.exitYr + 1 && t.resAny\n"
        "  let claw := if after && p.fixA then bp (ltcgBp + niitBp) s.exclAmt else 0\n"
        "  let s := { s with resAfter := s.resAfter || after, usTax := s.usTax + claw, gainTax := s.gainTax + claw }\n")
r = rep(r, "citUntil := s.citUntil, lprUntil := s.lprUntil, d1 := s.d1, d2 := s.d2, resPrev := s.resPrev }",
        "citUntil := s.citUntil, lprUntil := s.lprUntil, d1 := s.d1, d2 := s.d2, resPrev := s.resPrev, cov := s.covExpat }")
r = rep(r, """  if expat && (p.covered || !certify) then
    let g := if s.held then s.gainLeft - min s.gainLeft exitExclusion else 0
    let t := bp (ltcgBp + niitBp) g
    { s with usTax := s.usTax + t, gainTax := s.gainTax + t, gainLeft := 0, covExpat := true,
             tags := s.tags ||| tMTM ||| tExpat }
""", """  if expat && (p.covered || !certify) then
    if p.pre2008 then { s with covExpat := true, tags := s.tags ||| tExpat, exitYr := s.yr, exits := s.exits + 1 } else
    let ex := if p.fixC && !p.covered then 0 else p.exclusion
    let exU := if s.held then min s.gainLeft ex else 0
    let g := if s.held then s.gainLeft - exU else 0
    let t := bp (ltcgBp + niitBp) g + bp ordBp p.ira
    { s with usTax := s.usTax + t, gainTax := s.gainTax + t, gainLeft := 0, covExpat := true,
             tags := s.tags ||| tMTM ||| tExpat, exitYr := s.yr, exclAmt := s.exclAmt + exU, exits := s.exits + 1 }
""")
r = rep(r, "    if s.isCit && s.saleSeg != s.seg then some",
        "    if s.isCit && s.saleSeg != s.seg && !(p.noSeg0Exit && s.yr == 0 && s.seg == 0) then some")
r = rep(r, "    if s.isLPR && s.saleSeg != s.seg then\n",
        "    if s.isLPR && s.saleSeg != s.seg && !(p.noSeg0Exit && s.yr == 0 && s.seg == 0) then\n")

search = open(os.path.join(HERE, 'red_search.leanpart'), encoding='utf-8').read()
core = r + tail_defs + search
END = "\nend Legal.USTax.Hunt.Audit.ResidenceRed\n"
for name in sys.argv[1:]:
    body = open(os.path.join(HERE, name + '.body'), encoding='utf-8').read()
    with_search = core if '-- NOSEARCH' not in body else r + tail_defs
    open(os.path.join(HERE, name + '.lean'), 'w', encoding='utf-8', newline='\n').write(with_search + body + END)
    print('wrote', name)
