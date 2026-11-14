p='LegalProofs/USTax/Hunt/Residence.lean'
s=open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert a in s, a
    s=s.replace(a,b)
# moves with certification
rep("""  | renounce     -- relinquish citizenship, §877A(g)(4)
  | abandon      -- cease to be a lawful permanent resident, §7701(b)(6)""",
"""  | renounce (certify : Bool)   -- relinquish citizenship, §877A(g)(4); certify 5 years' compliance or not, §877(a)(2)(C)
  | abandon (certify : Bool)    -- cease to be a lawful permanent resident, §7701(b)(6); same certification""")
rep("""def exitTax (p : Params) (s : St) (expat : Bool) : St :=
  if expat && p.covered then""","""def exitTax (p : Params) (s : St) (expat certify : Bool) : St :=
  -- §877A(g)(1)(A), §877(a)(2): covered if the tax or net-worth test is met, or if compliance is not certified
  if expat && (p.covered || !certify) then""")
rep("""  | .renounce =>
    -- §877A(g)(2)(A): any citizen who relinquishes citizenship is an expatriate
    if s.isCit then some (exitTax p { s with isCit := false, citUntil := s.seg } true) else none
  | .abandon =>
    -- §877A(g)(2)(B), §877(e)(2): only a long-term resident (permanent resident in 8 of the last 15 taxable years)
    if s.isLPR then some (exitTax p { s with isLPR := false, lprUntil := s.seg } (s.lprYears + 1 ≥ 8)) else none""",
"""  | .renounce c =>
    -- §877A(g)(2)(A): any citizen who relinquishes citizenship is an expatriate. A sale earlier the same day was
    -- made as a citizen; the model keeps one order (status change, then sale) per day.
    if s.isCit && s.saleSeg != s.seg then some (exitTax p { s with isCit := false, citUntil := s.seg } true c) else none
  | .abandon c =>
    -- §877A(g)(2)(B), §877(e)(2): only a long-term resident (permanent resident in 8 of the last 15 taxable years)
    if s.isLPR && s.saleSeg != s.seg then
      some (exitTax p { s with isLPR := false, lprUntil := s.seg } (s.lprYears + 1 ≥ 8) c)
    else none""")
rep("def allMoves : List Move := [.present, .absent, .relocate, .sell, .renounce, .abandon, .giftUS, .giftNRA]",
    "def allMoves : List Move :=\n  [.present, .absent, .relocate, .sell, .renounce true, .renounce false, .abandon true, .abandon false, .giftUS, .giftNRA]")
rep("""    | .renounce => cur := cur ++ " RENOUNCE"
    | .abandon => cur := cur ++ " ABANDON-LPR\"""","""    | .renounce c => cur := cur ++ (if c then " RENOUNCE" else " RENOUNCE(no certification)")
    | .abandon c => cur := cur ++ (if c then " ABANDON-LPR" else " ABANDON-LPR(no certification)")""")
# home at year start
rep("  home : Bool        -- tax home (and closer connection) in the US now\n","  home : Bool        -- tax home (and closer connection) in the US now\n  homeY0 : Bool      -- tax home in the US when the year began\n")
rep("""  if days ≥ 183 && !((List.range n).all fun i => bit s.homeMask i || i < fp || i > lp) then none else""",
    """  if days ≥ 183 && !((List.range n).all fun i => bit s.homeMask i || (i < fp && !s.homeY0) || i > lp) then none else""")
rep("heldY0 := s.held, citUntil := if s.isCit then n else 0,","heldY0 := s.held, homeY0 := s.home, citUntil := if s.isCit then n else 0,")
rep("{ yr := 0, seg := 0, mask := 0, home := b.homeUS, homeMask := 0,","{ yr := 0, seg := 0, mask := 0, home := b.homeUS, homeY0 := b.homeUS, homeMask := 0,")
rep("""183 or more US days the tax home may be foreign only before the first day or after the last day of presence
  (§911(d)(3) second sentence: no foreign tax home while the abode is in the US);""",
"""183 or more US days the tax home may be foreign only after the last day of presence, or before the first day if
  the year began with a foreign tax home (§911(d)(3) second sentence: no foreign tax home while the abode is in
  the US);""")
# baseline by direct simulation
rep("""  let maxDays := 365 * p.horizon
  match front.get? maxDays with
  | some x => IO.println s!"baseline (in the US every day): tax on the gain ${x.gainTax}, all US tax ${x.us}"
  | none => IO.println "baseline: none\"""",
"""  let maxDays := 365 * p.horizon
  -- baseline: sell on day 1, be in the US every day, change nothing
  let plain := (List.replicate (p.horizon * p.grid.size) Move.present).foldl
    (fun (o : Option St) m => o.bind fun s => step p s m) (step p (initSt p b) .sell)
  match plain with
  | some x => IO.println s!"baseline (sell, in the US every day, no other move): tax on the gain ${x.gainTax}, all US tax ${x.usTax}"
  | none => IO.println "baseline: none\"""")
open(p,'w',encoding='utf-8',newline='').write(s)
g='tools/hunt/out/Residence/gen.py'
t=open(g,encoding='utf-8').read()
t=t.replace("sc={","""sc={
 'M_gc9_realty_covered_coarse_h2': "search { base with grid := coarse, asset := .usRealty } greenCard9",
 'M2_gc9_realty_notcovered_coarse_h2': "search { base with grid := coarse, asset := .usRealty, covered := false } greenCard9",
 'M3_gc9_us_notcovered_coarse_h2': "search { base with grid := coarse, covered := false } greenCard9",
 'D2_citizen_us_notcovered_coarse_h2': "search { base with grid := coarse, covered := false } citizen",""",1)
open(g,'w',encoding='utf-8').write(t)
