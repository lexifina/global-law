p='core.lean'
s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n, (s.count(a),a)
    s=s.replace(a,b)
rep("""  s.lots.foldl (fun s x => if x.long then settleDivs s x (t + 200) else (settleLieu sc s x (t + 400)).1) s""",
"""  -- and the §263(h) period on a short still open runs out only if nothing held suspends it
  s.lots.foldl (fun s x =>
    if x.long then settleDivs s x (t + 200)
    else if s.lots.any (fun n => n.long && (sc.regs || (sc.world[n.inst]!).cls == (sc.world[x.inst]!).cls)) then s
    else (settleLieu sc s x (t + 400)).1) s""")
# header
i=s.index("/-!\n# Financial instruments")
j=s.index("namespace Legal.USTax.Hunt.Instruments")
s=s[:i]+'''/-!
# Financial instruments: timing and character of investment gain (2025 rates)

Part A writes down what the Code does to an individual investor's positions in actively traded property: when gain
or loss is taken into account, and whether it is short-term, long-term, 60/40 or ordinary. Part B is a blind search
over every sequence of trades that keeps the investor's market exposure on a prescribed schedule, so the pre-tax
result of every plan is the same and only the tax differs. Part C holds the worlds and scenarios that are run.

Nothing in Part A names a technique. Each rule cites its provision. Findings: `Instruments.FINDINGS.md`.

    lake env lean LegalProofs/USTax/Hunt/Instruments.lean

Simplifications, each stated once:
* positions are single units of one exposure; every instrument in a world has the same total-return path (a switch
  between instruments leaves the pre-tax result unchanged; real substitutes track less than perfectly);
* no transaction costs, no interest on cash or margin, no borrow fees;
* an individual in the top brackets: ordinary 37% (§1(j)), net capital gain and qualified dividends 20%
  (§1(h)(1)(D), (11)), §1411 3.8% on all of it; the §1211(b) $3,000 is deducted at 37%;
* "substantially identical" is decided by an instrument's class; an index future is treated as a contract to acquire
  the fund of its class (the conservative reading of §1091(a) and §1259(c)(1)(C));
* any long and any short position in the same world are offsetting positions (§1092(c)(2), (d)(3)(A)(i)) and are
  "substantially similar or related property" (§246(c)(4)(C)); again the conservative reading;
* `regs = true` adds Temp. Reg. §1.1092(b)-1T(c) and -2T (holding period and loss character in straddles), which
  §1092(b)(1) directs, and assumes regulations under §263(h)(4)(B); `regs = false` is the statute alone;
* not encoded: identified straddles (§1092(a)(2)), the mixed-straddle elections (§§1092(b)(2), 1256(d)), §263(g),
  §475(f), §1260, options, the 5% preferred threshold and the aggregation rules of §1059(c).
-/

'''+s[j:]
open(p,'w',encoding='utf-8',newline='\n').write(s)
s=open('scen.lean',encoding='utf-8').read()
s+='''
/-- FundA held. Dates: the day before GainFund goes ex, the ex-date, the day after, year end, end. -/
def exDate (g : Int) (nm : String) : Sc :=
  { name := nm, world := distWorld1, days := #[129, 130, 131, 364, 729],
    px := #[k 100, k 100, k 100, k 100, k 105], expo := #[[1], [1], [1], [1], [1]],
    start := [held 5 (k 100)], gST := [g, g], gLT := [0, 0], maxLots := 2 }

/-- `lieuScen1` with fewer dates. -/
def lieuScen2 (regs : Bool) (nm : String) : Sc :=
  { lieuScen1 regs nm with days := #[120, 130, 364, 729], px := #[k 100, k 100, k 100, k 105],
                           expo := #[[1], [1], [1], [1]] }
'''
open('scen.lean','w',encoding='utf-8',newline='\n').write(s)
print('ok')
