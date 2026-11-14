import sys
p = 'LegalProofs/USTax/Hunt/Accounts.lean'
t = open(p, encoding='utf-8').read()


def rep(old, new):
    global t
    assert t.count(old) >= 1, old
    t = t.replace(old, new)


rep("  hasTA : Bool := false         -- a Trump account was established for the person before 18\n",
    "  hasTA : Bool := false         -- a Trump account was established for the person before 18\n"
    "  dependent : Bool := false     -- a §151 deduction for the person is allowable to another taxpayer, §223(b)(6)\n")
rep("  qcdYr : Nat := 0\n", "  qcdYr : Nat := 0\n  qcdExclYr : Nat := 0  -- excluded under §408(d)(8) so far this year\n")
rep("  | empRothB (a : Nat)      -- §402A(a)(3)\n",
    "  | empRothB (a : Nat)      -- §402A(a)(3)\n"
    "  | taRollIn (a : Nat)      -- §408(d)(3)(A)(ii), (H), from the Trump account to the employer plan\n")
rep("addB := 0, empBYr := 0, qcdYr := 0, ableYr := 0 }", "addB := 0, empBYr := 0, qcdYr := 0, qcdExclYr := 0, ableYr := 0 }")
old = '''      if c.iraDeductible then
        some { s with deducted := s.deducted + a, ded70 := s.ded70 + (if age c s ≥ 71 then a else 0) }
      else some { s with iraB := s.iraB + a }'''
new = '''      if c.iraDeductible then
        -- §408(d)(8)(A), second sentence: deductions for years ending on or after 70½ cut the exclusion, whichever
        -- comes first within the year
        let d := if age c s ≥ 71 then a else 0
        let red := min d s.qcdExclYr
        some { s with deducted := s.deducted + a, ded70 := s.ded70 + (d - red), qcdExclYr := s.qcdExclYr - red,
                      taxed := s.taxed + red }
      else some { s with iraB := s.iraB + a }'''
rep(old, new)
old = '''      if c.iraDeductible then
        some { s with deducted := s.deducted + a, ded70 := s.ded70 + (if age c s ≥ 71 then a else 0) }
      else some { s with taB := s.taB + a }'''
rep(old, new.replace("iraB := s.iraB + a", "taB := s.taB + a"))
rep('''        { s' with pledge := s'.pledge - a, qcdYr := s'.qcdYr + a, ded70 := s'.ded70 - red,
                  taxed := s'.taxed + red }''', '''        { s' with pledge := s'.pledge - a, qcdYr := s'.qcdYr + a, ded70 := s'.ded70 - red,
                  qcdExclYr := s'.qcdExclYr + (a - red), taxed := s'.taxed + red }''')
rep("    if age c s < 65 ∧ 0 < a ∧ a ≤ s.cash ∧ s.hsaYr + a ≤ cv.lastMonthLimit (hsaCu c s) then",
    "    if !c.dependent ∧ age c s < 65 ∧ 0 < a ∧ a ≤ s.cash ∧ s.hsaYr + a ≤ cv.lastMonthLimit (hsaCu c s) then")
rep("    -- §223(a), (b)(1)–(3), (b)(7), (b)(8)(A)\n", "    -- §223(a), (b)(1)–(3), (b)(6), (b)(7), (b)(8)(A)\n")
rep("    if age c s < 65 ∧ (s.qhfdN = 0 ∨ second)", "    if !c.dependent ∧ age c s < 65 ∧ (s.qhfdN = 0 ∨ second)")
rep("    -- extent otherwise includible, counted against the HSA limit and not deductible (§223(b)(4)(C))\n",
    "    -- extent otherwise includible, counted against the HSA limit and not deductible (§223(b)(4)(C)).\n"
    "    -- Conservative: closed to a dependent, although §223(b)(6) only denies \"deduction\" (see FINDINGS).\n")
old = '''      some { s with cash := s.cash - a, planRoth := s.planRoth + a, empBYr := s.empBYr + a, addB := s.addB + a }
    else none
'''
rep(old, old + '''  | .taRollIn a =>
    -- §408(d)(3)(A)(ii): only the part that would be includible may be rolled to an employer plan; §408(d)(3)(H):
    -- it is taken from the includible part first. The Trump account is an IRA for this purpose from the year of
    -- the 18th birthday (§530A(a), (h)(1)).
    if c.hasTA ∧ c.has401k ∧ age c s ≥ 18 ∧ 0 < a ∧ a ≤ s.ta - s.taB then
      some { s with ta := s.ta - a, planPre := s.planPre + a }
    else none
''')
rep("  | .afterTaxB _ => 30 | .rothRollB _ => 31 | .empPreB _ => 32 | .empRothB _ => 33",
    "  | .afterTaxB _ => 30 | .rothRollB _ => 31 | .empPreB _ => 32 | .empRothB _ => 33 | .taRollIn _ => 34")
rep('''  | .empRothB a => s!"employer Roth contribution, second employer ${a}"''',
    '''  | .empRothB a => s!"employer Roth contribution, second employer ${a}"
  | .taRollIn a => s!"roll ${a} of the Trump account into the employer plan"''')
rep('''   "employer Roth contrib (2nd)"]''', '''   "employer Roth contrib (2nd)", "Trump acct->employer plan"]''')
rep("(List.range 34)", "(List.range 35)")
rep("     .empPreB (min s.cash bRoom), .empRothB (min s.cash bRoom)]",
    "     .empPreB (min s.cash bRoom), .empRothB (min s.cash bRoom), .taRollIn preT]")
i = t.index('-- S2. Age 72')
j = t.index('-- S5. A 23-year-old')
t = t[:i] + '''-- S2. Age 72, still working, gives $10,000 a year to charity, IRA with basis.
#eval report "S2 age 72, IRA $30,000 with $20,000 basis, $10,000 pledge a year, deductible IRA contributions"
  { age0 := 72, years := 2, comp := 30000, iraDeductible := true, rNow := 32 }
  { cash := 40000, ira := 30000, iraB := 20000, pledge := 20000 } 8
  (isK [0, 1, 3, 4, 15, 17]) (isK [0, 1, 17])

-- S3. A 17-year-old with a Trump account used as intended so far ($40,000 contributed, $20,000 of growth), a
-- summer job, taxed at the child's own 10% rate.
#eval report "S3 Trump account, age 17 -> 19, child's own 10% rate"
  { age0 := 17, years := 3, comp := 6000, rothOK := true, hasTA := true, rNow := 10 }
  { cash := 30000, ta := 60000, taB := 40000 } 9
  (isK [0, 1, 2, 3, 6, 7, 8, 9]) (isK [0, 2, 6])

-- S3b. The same child, eligible for an ABLE account.
#eval report "S3b the same, ABLE-eligible"
  { age0 := 17, years := 3, comp := 6000, rothOK := true, hasTA := true, rNow := 10, disabled := true }
  { cash := 30000, ta := 60000, taB := 40000 } 9
  (isK [0, 2, 6, 7, 8, 9, 10]) (isK [0, 2, 6])

-- S3k. The same child, but income is taxed at the parents' 35% (section 1(g)); not a dependent; covered by the
-- parents' family HDHP; a job whose plan takes roll-ins; little spare cash.
#eval report "S3k Trump account, age 18 -> 19, parents' 35% rate, family HDHP, employer plan, $8,000 cash"
  { age0 := 18, years := 2, comp := 6000, rothOK := true, hasTA := true, rNow := 35, cov := [.family],
    has401k := true }
  { cash := 8000, ta := 60000, taB := 40000 } 8
  (isK [0, 2, 7, 8, 9, 11, 13, 34]) (isK [0, 2, 11])

-- S3m. As S3k, but a dependent (so no HSA moves) and no employer plan.
#eval report "S3m as S3k but a dependent, no employer plan"
  { age0 := 18, years := 2, comp := 6000, rothOK := true, hasTA := true, rNow := 35, cov := [.family],
    dependent := true }
  { cash := 8000, ta := 60000, taB := 40000 } 8
  (isK [0, 2, 7, 8, 9, 11, 13, 34]) (isK [0, 2, 11])

-- S4. An adult high earner who still has the (empty) Trump account from childhood and a large rollover IRA.
#eval report "S4 adult, age 30, high earner, empty Trump account + $100,000 rollover IRA, 2 years"
  { age0 := 30, years := 2, comp := 300000, hasTA := true }
  { cash := 30000, ira := 100000 } 7
  (isK [0, 1, 3, 7, 8]) (isK [0, 1, 3])

-- S4b. The same adult without the Trump account.
#eval report "S4b the same adult with no Trump account"
  { age0 := 30, years := 2, comp := 300000 }
  { cash := 30000, ira := 100000 } 7
  (isK [0, 1, 3, 7, 8]) (isK [0, 1, 3])

''' + t[j:]
open(p, 'w', encoding='utf-8', newline='\n').write(t)
