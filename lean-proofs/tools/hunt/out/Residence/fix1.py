p='LegalProofs/USTax/Hunt/Residence.lean'
s=open(p,encoding='utf-8',newline='').read()
a="""  if days ≥ 183 && !((List.range n).all fun i => !bit s.mask i || bit s.homeMask i) then none else"""
b="""  let fp := firstSegBelow n s.mask n
  let lp := lastSeg n s.mask
  if days ≥ 183 && !((List.range n).all fun i => bit s.homeMask i || i < fp || i > lp) then none else"""
assert a in s; s=s.replace(a,b)
a="""* "tax home" and "closer connection" are one fact, changed by `relocate`. To keep the fact honest, a year with 183
  or more US days requires the tax home to be in the US on every segment the person is present (§911(d)(3) second
  sentence: no foreign tax home while the abode is in the US);"""
b="""* "tax home" and "closer connection" are one fact, changed by `relocate`. To keep the fact honest, in a year with
  183 or more US days the tax home may be foreign only before the first day or after the last day of presence
  (§911(d)(3) second sentence: no foreign tax home while the abode is in the US);"""
assert a in s; s=s.replace(a,b)
open(p,'w',encoding='utf-8',newline='').write(s)
g='tools/hunt/out/Residence/gen.py'
t=open(g,encoding='utf-8').read()
for x,y in [("'D_citizen_us_fine_h2': \"search base citizen\"","'D_citizen_us_coarse_h2': \"search { base with grid := coarse } citizen\""),
            ("'E_gc9_us_fine_h2': \"search base greenCard9\"","'E_gc9_us_coarse_h2': \"search { base with grid := coarse } greenCard9\""),
            ("'E2_gc3_us_fine_h2': \"search base greenCard3\"","'E2_gc3_us_coarse_h2': \"search { base with grid := coarse } greenCard3\""),
            ("'H_visa_realty_fine_h2': \"search { base with asset := .usRealty } visaHolder\"","'H_visa_realty_coarse_h2': \"search { base with grid := coarse, asset := .usRealty } visaHolder\""),
            ("#eval search base visaHolder","/-- Recorded runs")]:
    assert x in t, x; t=t.replace(x,y)
t=t.replace("'A0':0,","")
t=t.replace("sc={","sc={\n 'A_visa_us_fine_h2': \"search base visaHolder\",")
open(g,'w',encoding='utf-8').write(t)
