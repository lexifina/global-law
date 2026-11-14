import os
D = os.path.dirname(os.path.abspath(__file__)) + os.sep
b = open(D + 'RedKernel.body', encoding='utf-8').read()
i = b.index("/-! ### Every move sequence, unbounded")
j = b.index("#print axioms baseline_238000")
kern = b[:i] + "end Legal.USTax.Hunt.Audit.ResidenceRed\nnamespace Legal.USTax.Hunt.Audit.ResidenceRed\n\n" \
    + b[j:b.index("#print axioms settle_fields")]
old = kern[kern.index("/-- closed gap A: over EVERY"):kern.index("/-- and fix A leaves")]
new = '''/-- closed gap A: over EVERY sequence of these moves, a finished plan by a covered expatriate who is a resident for
the calendar year after the expatriation year pays at least the baseline $238,000 -/
theorem fixA_all_whole :
    ((reach { w2 with fixA := true } mv 7 (initSt w2 greenCard9)).all fun s =>
      s.yr == 2 && (s.held || !(s.covExpat && s.resAfter) || s.gainTax ≥ 238000)) = true := by decide +kernel

/-- what fix A leaves in the model: expatriate on 1 January of the LAST year, stay that year (730 US days); the model
then assumes absence after the horizon, so this is a leaver with a one-year delay, not a stayer -/
theorem fixA_last_year_exit_whole :
    ((reach { w2 with fixA := true } mv 7 (initSt w2 greenCard9)).any fun s =>
      s.yr == 2 && !s.held && s.usDays == 730 && s.exitYr == 1 && s.gainTax == 26180) = true := by decide +kernel

/-- and with fix A every 730-day finished plan below the baseline expatriated in the last year -/
theorem fixA_full_only_last_year_whole :
    ((reach { w2 with fixA := true } mv 7 (initSt w2 greenCard9)).all fun s =>
      s.held || s.usDays != 730 || s.gainTax ≥ 238000 || s.exitYr == 1) = true := by decide +kernel

'''
kern = kern.replace(old, new) + "#print axioms fixA_last_year_exit_whole\n#print axioms fixA_full_only_last_year_whole\n"
open(D + 'RedKernel.body', 'w', encoding='utf-8', newline='\n').write(kern)
