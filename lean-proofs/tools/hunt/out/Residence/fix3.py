p='LegalProofs/USTax/Hunt/Residence.lean'
s=open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert a in s, a
    s=s.replace(a,b)
rep("  basis : Nat           -- adjusted basis of the asset (value = basis + gain)\n",
    "  basis : Nat           -- adjusted basis of the asset (value = basis + gain)\n  endInUS : Bool        -- search filter: count only plans with 183 or more US days in the last year\n")
rep("      if !s.held then\n        terminals","      if !s.held && (!p.endInUS || s.d1 ≥ 183 || p.student) then\n        terminals")
rep("student := false, horizon := 2, maxReloc := 2, gifts := false, basis := 500000 }","student := false, horizon := 2, maxReloc := 2, gifts := false, basis := 500000, endInUS := false }")
rep("/-- Whole years. -/\ndef whole : Array Nat := #[365]","/-- Whole years. -/\ndef whole : Array Nat := #[365]\n/-- One cut after day 183: the last 182 days of the year. -/\ndef arrival : Array Nat := #[183, 182]")
i=s.index("/-! Recorded runs -/")
s=s[:i]+'''/-! Recorded runs -/

/-!
The searches below run in about a minute together. Other recorded runs (output in `tools/hunt/out/Residence/`):
the fine grid over two years for the visa holder, the newcomer and the student; citizen and green-card holders with
and without the §877(a)(2) wealth test; US realty; gifts; foreign tax 25% / 15%; whole-year grid over six years.
-/

-- foreign-corporation stock, three years: the year of absence and the return
#eval search { base with grid := coarse, asset := .foreignStock, horizon := 3 } visaHolder
-- the same with domestic stock
#eval search { base with grid := coarse, horizon := 3 } visaHolder
-- long-term green-card holder below the wealth test, US realty
#eval search { base with grid := coarse, asset := .usRealty, covered := false } greenCard9
-- long-term green-card holder above the wealth test, domestic stock
#eval search { base with grid := coarse } greenCard9
-- arriving
#eval search { base with grid := arrival } newcomer
#eval search { base with grid := arrival, student := true } student
-- six whole years, plans that end back in the US
#eval search { base with grid := whole, horizon := 6, maxReloc := 4, endInUS := true } visaHolder

end Legal.USTax.Hunt.Residence
'''
open(p,'w',encoding='utf-8',newline='').write(s)
g='tools/hunt/out/Residence/gen.py'
t=open(g,encoding='utf-8').read()
t=t.replace("sc={","""sc={
 'J3_visa_us_whole_h6_endInUS': "search { base with grid := whole, horizon := 6, maxReloc := 4, endInUS := true } visaHolder",
 'N_newcomer_arrival_h2': "search { base with grid := arrival } newcomer",
 'N2_student_arrival_h2': "search { base with grid := arrival, student := true } student",""",1)
open(g,'w',encoding='utf-8').write(t)
