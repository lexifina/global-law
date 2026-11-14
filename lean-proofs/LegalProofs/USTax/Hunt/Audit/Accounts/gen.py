# Red-team generator: builds self-contained Lean files from a copy of the rules (RedRules.txt = lines 1-639 of the
# original Accounts.lean, unedited).  Never touches the original.
import io
rules = open('RedRules.txt', encoding='utf8').read()
orig_all = open('../../Accounts.lean', encoding='utf8').read()
scen = orig_all.split('/-! ### Scenarios -/')[1].rsplit('end Legal.USTax.Hunt.Accounts', 1)[0]
NS = '\nnamespace Legal.USTax.Hunt.Accounts\n'
END = '\nend Legal.USTax.Hunt.Accounts\n'


def w(name, body):
    io.open(name, 'w', encoding='utf8', newline='\n').write(body)


def rep(t, old, new):
    assert t.count(old) == 1, (t.count(old), old[:60])
    return t.replace(old, new)


# ---------- closed-gap rule (T2): (h)(4) limited to years before the year of the 18th birthday ----------
closed = rules
closed = rep(closed, "def setFirst (s : St) : St :=", '''/-- RED closed-gap rule.  §530A(h)(4) read as: "For any taxable year beginning before the first day of the calendar
year in which the account beneficiary attains age 18, section 408(d)(2) shall be applied separately ...".  From that
year on, §408(d)(2)(A) treats the Trump account and the other IRAs as one contract. -/
def aggTake (c : Cfg) (s : St) (src : Src) (a : Nat) : Nat × St :=
  if c.hasTA && age c s ≥ 18 then
    let B := s.iraB + s.taB
    let T := s.ira + s.ta
    let n := a * B / T
    let ira' := match src with | .ira => s.ira - a | .ta => s.ira
    let ta' := match src with | .ira => s.ta | .ta => s.ta - a
    let B' := B - n
    let taB' := min ta' (match src with | .ta => s.taB - min n s.taB | .ira => s.taB)
    let iraB' := min ira' (B' - taB')
    (n, { s with ira := ira', ta := ta', iraB := iraB', taB := B' - iraB' })
  else match src with
    | .ira => let n := a * s.iraB / s.ira
              (n, { s with ira := s.ira - a, iraB := s.iraB - n })
    | .ta => let n := a * s.taB / s.ta
             (n, { s with ta := s.ta - a, taB := s.taB - n })

def setFirst (s : St) : St :=''')
closed = rep(closed, '''      let n := a * s.iraB / s.ira
      some (setFirst { s with ira := s.ira - a, iraB := s.iraB - n, cvT := s.cvT + (a - n), cvN := s.cvN + n,
                              cvYr := s.yr, taxed := s.taxed + (a - n) })''',
'''      let (n, s) := aggTake c s .ira a
      some (setFirst { s with cvT := s.cvT + (a - n), cvN := s.cvN + n, cvYr := s.yr, taxed := s.taxed + (a - n) })''')
closed = rep(closed, '''      let n := a * s.iraB / s.ira
      some { s with ira := s.ira - a, iraB := s.iraB - n, cash := s.cash + a, taxed := s.taxed + (a - n),
                    penalty := s.penalty + (if age c s < 60 then (a - n) / 10 else 0) }''',
'''      let (n, s) := aggTake c s .ira a
      some { s with cash := s.cash + a, taxed := s.taxed + (a - n),
                    penalty := s.penalty + (if age c s < 60 then (a - n) / 10 else 0) }''')
closed = rep(closed, '''      let n := a * s.taB / s.ta
      some (setFirst { s with ta := s.ta - a, taB := s.taB - n, cvT := s.cvT + (a - n), cvN := s.cvN + n,
                              cvYr := s.yr, taxed := s.taxed + (a - n) })''',
'''      let (n, s) := aggTake c s .ta a
      some (setFirst { s with cvT := s.cvT + (a - n), cvN := s.cvN + n, cvYr := s.yr, taxed := s.taxed + (a - n) })''')
closed = rep(closed, '''      let n := a * s.taB / s.ta
      some { s with ta := s.ta - a, taB := s.taB - n, cash := s.cash + a, taxed := s.taxed + (a - n),
                    penalty := s.penalty + (if age c s < 60 then (a - n) / 10 else 0) }''',
'''      let (n, s) := aggTake c s .ta a
      some { s with cash := s.cash + a, taxed := s.taxed + (a - n),
                    penalty := s.penalty + (if age c s < 60 then (a - n) / 10 else 0) }''')
w('RedClosedRules.txt', closed)

# ---------- earlier law (T4): the Code without §530A: no Trump-account move exists ----------
early = rep(rules, "def step (c : Cfg) (s : St) : Move → Option St", "def step0 (c : Cfg) (s : St) : Move → Option St")
early = rep(early, "/-- The moves tried from a position.", '''/-- RED earlier law: before Pub. L. 119-21 there is no §530A, so no Trump-account move is defined. -/
def step (c : Cfg) (s : St) (m : Move) : Option St :=
  if [6, 7, 8, 9, 10, 13, 16, 34].contains (kind m) then none else step0 c s m

/-- The moves tried from a position.''')


def s4(title, allowed, plain='(isK [0, 1, 3])', cfg=None, st=None, depth=7):
    c = cfg or '{ age0 := 30, years := 2, comp := 300000, hasTA := true }'
    s = st or '{ cash := 30000, ira := 100000 }'
    return f'#eval report "{title}"\n  {c}\n  {s} {depth}\n  {allowed} {plain}\n'


# T2: every scenario under the closed rule (diff against the original output)
w('RedT2.lean', closed + NS + scen + END)

# T3 ablation + T1 fact variants, on the unmodified rules
A = '(isK [0, 1, 3, 7, 8])'
t3 = NS
t3 += s4('T3-A original S4', A)
t3 += s4('T3-B without 7 (Trump acct contrib 18+)', '(isK [0, 1, 3, 8])')
t3 += s4('T3-C without 8 (Trump acct->Roth conversion)', '(isK [0, 1, 3, 7])')
t3 += s4('T3-D without 0 (next year)', '(isK [1, 3, 7, 8])')
t3 += s4('T3-E only the moves the plan uses [0,7,8]', '(isK [0, 7, 8])')
t3 += s4('T3-F every move kind allowed (depth 6)', '(fun _ => true)', depth=6)
t3 += s4('T1-a Trump account holds 5,000 of seed money and growth, no basis', A,
         st='{ cash := 30000, ira := 100000, ta := 5000 }')
t3 += s4('T1-b Trump account 60,000 with 40,000 basis', A,
         st='{ cash := 30000, ira := 100000, ta := 60000, taB := 40000 }')
t3 += s4('T1-c Trump account 70,000, no basis', A, st='{ cash := 30000, ira := 100000, ta := 70000 }')
t3 += s4('T1-d no growth premium (beta 0)', A,
         cfg='{ age0 := 30, years := 2, comp := 300000, hasTA := true, beta := 0 }')
t3 += s4('T1-e IRA contributions deductible (no employer plan, s219(g) does not bite)', A,
         cfg='{ age0 := 30, years := 2, comp := 300000, hasTA := true, iraDeductible := true }')
t3 += s4('T1-f the 100,000 already rolled into the employer plan (known isolation)', A,
         st='{ cash := 30000, planPre := 100000 }')
t3 += s4('T1-g rLater 35 (same rate now and later)', A,
         cfg='{ age0 := 30, years := 2, comp := 300000, hasTA := true, rLater := 35 }')
t3 += s4('T1-h age 17 at start (minor year, then adult year)', '(isK [0, 1, 3, 6, 7, 8])',
         cfg='{ age0 := 17, years := 2, comp := 300000, hasTA := true }')
w('RedT3.lean', rules + t3 + END)

# T4
t4 = NS + s4('T4-A S4 under the Code without s530A, S4 move set', A) \
        + s4('T4-B S4 under the Code without s530A, every move kind (depth 6)', '(fun _ => true)', depth=6)
w('RedT4.lean', early + t4 + END)

# T5 free lunch / conservation on the unmodified rules
t5 = NS + open('t5_body.txt', encoding='utf8').read() + scen.replace('#eval report ', '#eval check ')
w('RedT5.lean', rules + t5 + END)

# T6 kernel replays
w('RedT6open.lean', rules + NS + open('t6_open.txt', encoding='utf8').read() + END)
w('RedT6closed.lean', closed + NS + open('t6_closed.txt', encoding='utf8').read() + END)
print('ok')
